"""
Business logic for vote events.
"""
import logging
import json
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from src.models import VoteEvent, Candidate, EventStatus
from src.schemas.vote_events import VoteEventCreate, VoteEventDetailResponse
from src.exceptions import EventNotFoundException, InvalidEventStateException
from src.electionguard_service.manifest_builder import build_manifest
from src.electionguard_service.key_ceremony import perform_key_ceremony

logger = logging.getLogger(__name__)


async def create_vote_event(
    db: AsyncSession,
    event_data: VoteEventCreate
) -> VoteEvent:
    """
    Create a new vote event with ElectionGuard setup.

    Steps:
    1. Validate input and create event record
    2. Create candidate records
    3. Build ElectionGuard manifest
    4. Perform key ceremony
    5. Store cryptographic materials

    Args:
        db: Database session
        event_data: Vote event creation data

    Returns:
        Created VoteEvent with candidates

    Raises:
        Exception: If event creation fails
    """
    logger.info(f"# CREATE | Starting event creation: {event_data.name}")

    try:
        # Step 1: Create event record
        event = VoteEvent(
            name=event_data.name,
            from_date=event_data.from_date,
            to_date=event_data.to_date,
            status=EventStatus.INVOTING,
            allow_vote_candidate_num=event_data.allow_vote_candidate_num,
        )
        db.add(event)
        await db.flush()  # Get event.id

        logger.info(f"Event {event.id} # CREATE | Event record created")

        # Step 2: Create candidate records
        candidates = []
        for idx, candidate_name in enumerate(event_data.candidate_names):
            candidate = Candidate(
                event_id=event.id,
                name=candidate_name,
                vote_count=0,
                vote_percentage=0.0
            )
            candidates.append(candidate)
            db.add(candidate)

        await db.flush()
        logger.info(f"Event {event.id} # CREATE | Created {len(candidates)} candidates: {[c.name for c in candidates]}")

        # Step 3: Build ElectionGuard manifest
        manifest = build_manifest(
            event_id=event.id,
            event_name=event.name,
            candidate_names=event_data.candidate_names,
            allow_vote_candidate_num=event_data.allow_vote_candidate_num,
            start_date=event_data.from_date,
            end_date=event_data.to_date
        )

        # Store manifest as JSON
        from electionguard.serialize import to_raw
        event.election_manifest = to_raw(manifest)  # to_raw already returns JSON string
        logger.info(f"Event {event.id} # CREATE | ElectionGuard manifest created")

        # Step 4: Perform key ceremony
        guardian_keypair, context = perform_key_ceremony(manifest)

        # Store cryptographic materials (in production, secure storage is essential)
        event.joint_public_key = guardian_keypair.key_pair.public_key.to_hex()

        # Extract polynomial coefficients (they are Coefficient objects with value and commitment)
        polynomial_coefficients = [coeff.value.to_hex() for coeff in guardian_keypair.polynomial.coefficients]

        event.crypto_context = json.dumps({
            'guardian_id': guardian_keypair.owner_id,
            'sequence_order': guardian_keypair.sequence_order,
            'guardian_secret_key': guardian_keypair.key_pair.secret_key.to_hex(),
            'elgamal_public_key': context.elgamal_public_key.to_hex(),
            'polynomial_coefficients': polynomial_coefficients,
            'crypto_base_hash': context.crypto_base_hash.to_hex(),
            'crypto_extended_base_hash': context.crypto_extended_base_hash.to_hex(),
            'commitment_hash': context.commitment_hash.to_hex(),
            'manifest_hash': context.manifest_hash.to_hex(),
            'number_of_guardians': context.number_of_guardians,
            'quorum': context.quorum,
        })

        logger.info(f"Event {event.id} # CREATE | Key ceremony completed (Guardian: {guardian_keypair.owner_id})")

        await db.commit()
        await db.refresh(event)

        logger.info(f"Event {event.id} # CREATE | ✓ Event created successfully")
        return event

    except Exception as e:
        await db.rollback()
        logger.error(f"# CREATE | ✗ Failed to create event: {str(e)}")
        raise


async def get_vote_events(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> tuple[List[VoteEvent], int]:
    """
    Get list of vote events with pagination.

    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records to return

    Returns:
        Tuple of (events list, total count)
    """
    # Get total count
    count_query = select(func.count(VoteEvent.id))
    total = await db.scalar(count_query)

    # Get events
    query = select(VoteEvent).offset(skip).limit(limit).order_by(VoteEvent.id.desc())
    result = await db.execute(query)
    events = result.scalars().all()

    return list(events), total or 0


async def get_vote_event_detail(
    db: AsyncSession,
    event_id: int
) -> VoteEvent:
    """
    Get detailed vote event information including candidates.

    Args:
        db: Database session
        event_id: Event ID

    Returns:
        VoteEvent with candidates loaded

    Raises:
        EventNotFoundException: If event not found
    """
    query = select(VoteEvent).where(VoteEvent.id == event_id).options(
        selectinload(VoteEvent.candidates)
    )
    result = await db.execute(query)
    event = result.scalar_one_or_none()

    if not event:
        raise EventNotFoundException(f"Event with ID {event_id} not found")

    return event


async def end_voting(
    db: AsyncSession,
    event_id: int
) -> VoteEvent:
    """
    End voting for an event and perform tally.

    This will:
    1. Change event status to ENDED
    2. Trigger tally computation (handled separately by tally endpoint)

    Args:
        db: Database session
        event_id: Event ID

    Returns:
        Updated VoteEvent

    Raises:
        EventNotFoundException: If event not found
        InvalidEventStateException: If event not in INVOTING state
    """
    event = await get_vote_event_detail(db, event_id)

    if event.status != EventStatus.INVOTING:
        raise InvalidEventStateException(
            f"Cannot end voting for event in {event.status} state"
        )

    event.status = EventStatus.END
    event.end_at = datetime.utcnow()
    await db.commit()
    await db.refresh(event)

    logger.info(f"Event {event_id} # END_VOTING | ✓ Voting ended")
    return event


async def execute_tally(
    db: AsyncSession,
    event_id: int
) -> VoteEvent:
    """
    Execute tally ceremony for an event.

    This performs ElectionGuard homomorphic tally and decryption:
    1. Get all encrypted ballots for the event
    2. Perform homomorphic aggregation
    3. Decrypt aggregated tally using guardian keypair
    4. Update candidate vote counts and percentages
    5. Update event status to END

    Args:
        db: Database session
        event_id: Event ID

    Returns:
        Updated VoteEvent with tally results

    Raises:
        EventNotFoundException: If event not found
        InvalidEventStateException: If event not in valid state for tally
    """
    from src.models import CustomerVote
    from dacite import from_dict, Config
    from electionguard.serialize import from_raw
    from electionguard.manifest import Manifest, SpecVersion, ElectionType, ReportingUnitType, VoteVariationType
    from src.electionguard_service.tally_ceremony import perform_full_tally
    from src.services.votes_service import _deserialize_manifest, _deserialize_context, _deserialize_guardian_keypair

    logger.info(f"Event {event_id} # TALLY | Starting tally ceremony")

    # Get event with candidates
    event = await get_vote_event_detail(db, event_id)

    # Get all votes for this event
    votes_query = select(CustomerVote).where(CustomerVote.event_id == event_id)
    votes_result = await db.execute(votes_query)
    votes = votes_result.scalars().all()

    if not votes:
        logger.warning(f"Event {event_id} # TALLY | No votes found")
        event.status = EventStatus.END
        event.end_at = datetime.utcnow()
        event.total_votes = 0
        await db.commit()
        await db.refresh(event)
        return event

    logger.info(f"Event {event_id} # TALLY | Processing {len(votes)} encrypted ballots")

    # Deserialize ElectionGuard materials
    manifest = _deserialize_manifest(event.election_manifest)
    context = _deserialize_context(event.crypto_context, manifest)
    guardian_keypair = _deserialize_guardian_keypair(event.crypto_context)

    logger.info(f"Event {event_id} # TALLY | Cryptographic materials loaded (Guardian: {guardian_keypair.owner_id})")

    # Deserialize encrypted ballots
    from electionguard.ballot import CiphertextBallot
    encrypted_ballots = []
    for vote in votes:
        ballot_data = json.loads(vote.encrypted_ballot)
        ciphertext_ballot = from_raw(CiphertextBallot, ballot_data)
        encrypted_ballots.append(ciphertext_ballot)

    logger.info(f"Event {event_id} # TALLY | Performing homomorphic aggregation and decryption")

    # Perform tally ceremony
    vote_counts = perform_full_tally(
        encrypted_ballots=encrypted_ballots,
        manifest=manifest,
        context=context,
        guardian_keypair=guardian_keypair
    )

    # Map selection IDs to candidate IDs
    # ElectionGuard uses object_id like "candidate-1-0", "candidate-1-1", etc.
    # Extract the index from "candidate-1-INDEX" and match to candidate order
    candidate_counts = {}
    for selection_id, count in vote_counts.items():
        # Parse "candidate-1-INDEX" to get candidate index
        parts = selection_id.split('-')
        if len(parts) == 3:
            candidate_index = int(parts[2])
            if candidate_index < len(event.candidates):
                candidate = event.candidates[candidate_index]
                candidate_counts[candidate.id] = count

    # Calculate total votes
    total_votes = sum(candidate_counts.values())

    # Update candidate vote counts and percentages
    for candidate in event.candidates:
        candidate.vote_count = candidate_counts.get(candidate.id, 0)
        candidate.vote_percentage = (
            (candidate.vote_count / total_votes * 100) if total_votes > 0 else 0.0
        )

    # Update event
    event.total_votes = total_votes
    event.status = EventStatus.END
    event.end_at = datetime.utcnow()

    await db.commit()
    await db.refresh(event)

    # Log final results
    results_str = ", ".join([f"{c.name}: {c.vote_count}" for c in event.candidates])
    logger.info(f"Event {event_id} # TALLY | ✓ Tally completed | Total: {total_votes} votes | Results: {results_str}")
    return event
