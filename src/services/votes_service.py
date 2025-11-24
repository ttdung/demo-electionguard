"""
Business logic for votes.
"""
import logging
import secrets
import json
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from electionguard.serialize import from_raw
from electionguard.manifest import Manifest
from electionguard.election import CiphertextElectionContext
from electionguard.key_ceremony import ElectionKeyPair
from electionguard.elgamal import ElGamalKeyPair
from electionguard.group import int_to_q

from src.models import VoteEvent, CustomerVote, Candidate, EventStatus
from src.schemas.votes import VoteSubmitRequest
from src.exceptions import (
    EventNotFoundException,
    InvalidEventStateException,
    CustomerNotFoundException,
    AlreadyVotedException,
    InvalidVoteSelectionException,
    VoteNotFoundException,
)
from src.services.customers_service import get_customer_by_secret
from src.electionguard_service.ballot_encryptor import (
    create_plaintext_ballot,
    encrypt_vote_ballot,
    validate_ballot_selections,
)

logger = logging.getLogger(__name__)


def generate_vote_secret() -> str:
    """
    Generate a secure random secret token for vote verification.

    Returns:
        64-character hex string
    """
    return secrets.token_hex(32)


def _deserialize_manifest(manifest_json: str) -> Manifest:
    """Deserialize ElectionGuard Manifest from JSON."""
    from dacite import from_dict, Config
    from datetime import datetime
    from electionguard.manifest import (
        SpecVersion,
        ElectionType,
        ReportingUnitType,
        VoteVariationType
    )

    manifest_dict = json.loads(manifest_json)

    # Configure dacite to handle datetime strings and enums
    config = Config(
        type_hooks={
            datetime: datetime.fromisoformat
        },
        cast=[SpecVersion, ElectionType, ReportingUnitType, VoteVariationType]
    )

    return from_dict(Manifest, manifest_dict, config=config)


def _deserialize_context(
    crypto_context_json: str,
    manifest: Manifest
) -> CiphertextElectionContext:
    """Deserialize CiphertextElectionContext from stored JSON."""
    from electionguard.manifest import InternalManifest
    from electionguard.election import make_ciphertext_election_context
    from electionguard.group import hex_to_q, hex_to_p

    ctx_data = json.loads(crypto_context_json)

    context = make_ciphertext_election_context(
        number_of_guardians=ctx_data['number_of_guardians'],
        quorum=ctx_data['quorum'],
        elgamal_public_key=hex_to_p(ctx_data['elgamal_public_key']),
        commitment_hash=hex_to_q(ctx_data['commitment_hash']),
        manifest_hash=hex_to_q(ctx_data['manifest_hash']),
    )

    return context


def _deserialize_guardian_keypair(crypto_context_json: str) -> ElectionKeyPair:
    """Deserialize guardian keypair from stored JSON."""
    from electionguard.group import hex_to_q, hex_to_p
    from electionguard.elgamal import ElGamalKeyPair
    from electionguard.key_ceremony import ElectionKeyPair, ElectionPolynomial

    ctx_data = json.loads(crypto_context_json)

    # Reconstruct ElGamalKeyPair
    secret_key = hex_to_q(ctx_data['guardian_secret_key'])
    public_key = hex_to_p(ctx_data['elgamal_public_key'])
    elgamal_keypair = ElGamalKeyPair(secret_key, public_key)

    # Reconstruct polynomial
    polynomial_coefficients = [hex_to_q(coeff_hex) for coeff_hex in ctx_data['polynomial_coefficients']]
    polynomial = ElectionPolynomial(polynomial_coefficients)

    # Reconstruct ElectionKeyPair with all required components
    guardian_id = ctx_data['guardian_id']
    sequence_order = ctx_data.get('sequence_order', 0)
    election_keypair = ElectionKeyPair(
        owner_id=guardian_id,
        sequence_order=sequence_order,
        key_pair=elgamal_keypair,
        polynomial=polynomial
    )

    return election_keypair


async def submit_vote(
    db: AsyncSession,
    vote_data: VoteSubmitRequest
) -> tuple[str, str, CustomerVote]:
    """
    Submit an encrypted vote.

    Steps:
    1. Validate customer and event
    2. Check if customer already voted
    3. Validate candidate selections
    4. Build ElectionGuard plaintext ballot
    5. Encrypt ballot with ElectionGuard
    6. Store encrypted ballot and tracking information

    Args:
        db: Database session
        vote_data: Vote submission data

    Returns:
        Tuple of (vote_secret, verification_code, customer_vote)

    Raises:
        CustomerNotFoundException: If customer_secret invalid
        EventNotFoundException: If event not found
        InvalidEventStateException: If event not accepting votes
        AlreadyVotedException: If customer already voted
        InvalidVoteSelectionException: If selections invalid
    """
    logger.info(f"Event {vote_data.event_id} # VOTE | Processing vote submission")

    # Step 1: Validate customer
    customer = await get_customer_by_secret(db, vote_data.customer_secret)
    if not customer:
        raise CustomerNotFoundException("Invalid customer secret")

    # Step 2: Get event with candidates
    query = select(VoteEvent).where(VoteEvent.id == vote_data.event_id).options(
        selectinload(VoteEvent.candidates)
    )
    result = await db.execute(query)
    event = result.scalar_one_or_none()

    if not event:
        raise EventNotFoundException(f"Event with ID {vote_data.event_id} not found")

    if event.status != EventStatus.INVOTING:
        raise InvalidEventStateException(
            f"Event is not accepting votes (status: {event.status})"
        )

    # Step 3: Check if customer is registered for this event
    from src.models import EventCustomer
    event_customer_query = select(EventCustomer).where(
        EventCustomer.event_id == vote_data.event_id,
        EventCustomer.customer_id == customer.id
    )
    ec_result = await db.execute(event_customer_query)
    event_customer = ec_result.scalar_one_or_none()

    if not event_customer:
        raise CustomerNotFoundException(
            f"Customer is not registered for event {vote_data.event_id}"
        )

    # Step 4: Check if already voted
    existing_vote_query = select(CustomerVote).where(
        CustomerVote.event_id == vote_data.event_id,
        CustomerVote.customer_id == customer.id
    )
    result = await db.execute(existing_vote_query)
    if result.scalar_one_or_none():
        raise AlreadyVotedException(
            f"Customer has already voted in event {vote_data.event_id}"
        )

    # Step 4: Validate candidate selections
    logger.info(f"Event {vote_data.event_id} # VOTE | Validating candidate selections")
    candidate_ids_map = {c.id: idx for idx, c in enumerate(event.candidates)}
    selected_indices = []

    for candidate_id in vote_data.selected_candidate_ids:
        if candidate_id not in candidate_ids_map:
            logger.error(f"Event {vote_data.event_id} # VOTE | ✗ Invalid candidate ID: {candidate_id}")
            raise InvalidVoteSelectionException(
                f"Invalid candidate ID: {candidate_id}"
            )
        selected_indices.append(candidate_ids_map[candidate_id])

    # Validate selection rules
    is_valid, error_msg = validate_ballot_selections(
        selected_candidate_indices=selected_indices,
        num_candidates=len(event.candidates),
        allow_vote_candidate_num=event.allow_vote_candidate_num
    )

    if not is_valid:
        logger.error(f"Event {vote_data.event_id} # VOTE | ✗ Ballot validation failed: {error_msg}")
        raise InvalidVoteSelectionException(error_msg)

    # Get selected candidate names for logging
    selected_names = [event.candidates[idx].name for idx in selected_indices]
    logger.info(f"Event {event.id} # VOTE | Customer {customer.unique_id} | Selections validated: {selected_names}")

    # Step 5: Deserialize ElectionGuard materials
    manifest = _deserialize_manifest(event.election_manifest)
    context = _deserialize_context(event.crypto_context, manifest)

    # Step 6: Create and encrypt ballot
    plaintext_ballot = create_plaintext_ballot(
        event_id=event.id,
        customer_id=customer.id,
        selected_candidate_indices=selected_indices,
        manifest=manifest
    )

    ciphertext_ballot, verification_code = encrypt_vote_ballot(
        plaintext_ballot=plaintext_ballot,
        manifest=manifest,
        context=context
    )

    logger.info(f"Event {event.id} # VOTE | Customer {customer.unique_id} | Ballot encrypted (Code: {verification_code[:8]}...)")

    # Step 7: Generate vote secret and store
    vote_secret = generate_vote_secret()

    # Serialize encrypted ballot
    from electionguard.serialize import to_raw
    encrypted_ballot_json = json.dumps(to_raw(ciphertext_ballot))
    ballot_proofs_json = json.dumps({
        'ballot_hash': ciphertext_ballot.crypto_hash.to_hex(),
        'verification_code': verification_code,
    })

    # Store vote record
    customer_vote = CustomerVote(
        event_id=event.id,
        customer_id=customer.id,
        vote_secret=vote_secret,
        encrypted_ballot=encrypted_ballot_json,
        ballot_proofs=ballot_proofs_json,
        selected_candidate_ids=json.dumps(vote_data.selected_candidate_ids)
    )

    db.add(customer_vote)
    await db.commit()
    await db.refresh(customer_vote)

    logger.info(f"Event {event.id} # VOTE | Customer {customer.unique_id} | ✓ Vote recorded successfully")

    return vote_secret, verification_code, customer_vote


async def verify_vote(
    db: AsyncSession,
    vote_secret: str
) -> tuple[VoteEvent, List[Candidate], str]:
    """
    Verify a vote using the vote secret.

    Args:
        db: Database session
        vote_secret: Vote secret token

    Returns:
        Tuple of (event, selected_candidates, verification_code)

    Raises:
        VoteNotFoundException: If vote secret invalid
    """
    # Get vote record
    query = select(CustomerVote).where(CustomerVote.vote_secret == vote_secret).options(
        selectinload(CustomerVote.event).selectinload(VoteEvent.candidates)
    )
    result = await db.execute(query)
    vote = result.scalar_one_or_none()

    if not vote:
        raise VoteNotFoundException("Invalid vote secret")

    # Get selected candidates
    selected_ids = json.loads(vote.selected_candidate_ids)
    selected_candidates = [c for c in vote.event.candidates if c.id in selected_ids]

    # Get verification code
    proofs = json.loads(vote.ballot_proofs)
    verification_code = proofs['verification_code']

    return vote.event, selected_candidates, verification_code


async def get_event_votes(
    db: AsyncSession,
    event_id: int
) -> List[dict]:
    """
    Get all votes for a specific event.

    Args:
        db: AsyncSession
        event_id: Event ID

    Returns:
        List of vote dicts with customer and candidate info

    Raises:
        EventNotFoundException: If event not found
    """
    from src.models import Customer
    from src.exceptions import EventNotFoundException

    # Check if event exists
    event_query = select(VoteEvent).where(VoteEvent.id == event_id).options(
        selectinload(VoteEvent.candidates)
    )
    event_result = await db.execute(event_query)
    event = event_result.scalar_one_or_none()

    if not event:
        raise EventNotFoundException(f"Event with ID {event_id} not found")

    # Get all votes for this event with customer data
    query = select(CustomerVote, Customer).join(
        Customer, CustomerVote.customer_id == Customer.id
    ).where(CustomerVote.event_id == event_id).order_by(CustomerVote.vote_at.desc())

    result = await db.execute(query)
    votes = result.all()

    # Build candidate map for efficient lookup
    candidate_map = {c.id: c.name for c in event.candidates}

    # Build response
    votes_data = []
    for vote, customer in votes:
        # Get selected candidate IDs and names
        selected_ids = json.loads(vote.selected_candidate_ids)
        selected_names = [candidate_map[cid] for cid in selected_ids if cid in candidate_map]

        # Get verification code
        proofs = json.loads(vote.ballot_proofs)
        verification_code = proofs['verification_code']

        votes_data.append({
            'id': vote.id,
            'customer_id': customer.id,
            'customer_unique_id': customer.unique_id,
            'vote_at': vote.vote_at,
            'verification_code': verification_code,
            'vote_secret': vote.vote_secret,
            'selected_candidate_ids': selected_ids,
            'selected_candidate_names': selected_names
        })

    return votes_data


async def decode_vote(
    db: AsyncSession,
    verification_code: str,
    vote_secret: str = None
) -> dict:
    """
    Decode a vote using verification code (Level 1) or verification code + vote secret (Level 2).

    Level 1 (code only): Shows candidates and timestamp
    Level 2 (code + secret): Shows candidates, timestamp, and voter identity

    Args:
        db: Database session
        verification_code: Ballot verification code
        vote_secret: Optional vote secret for Level 2 decode

    Returns:
        Vote details dict (Level 1 or Level 2 based on vote_secret)

    Raises:
        VoteNotFoundException: If verification code not found
        InvalidVoteSelectionException: If vote_secret provided but doesn't match
    """
    from src.models import Customer

    decode_level = "Level 2" if vote_secret else "Level 1"
    logger.info(f"# DECODE | {decode_level} | Verification code: {verification_code[:8]}...")

    # Find vote by verification code
    query = select(CustomerVote).options(
        selectinload(CustomerVote.event).selectinload(VoteEvent.candidates),
        selectinload(CustomerVote.customer)
    )
    result = await db.execute(query)
    all_votes = result.scalars().all()

    # Search for matching verification code in proofs
    vote = None
    for v in all_votes:
        proofs = json.loads(v.ballot_proofs)
        if proofs['verification_code'] == verification_code:
            vote = v
            break

    if not vote:
        logger.warning(f"# DECODE | {decode_level} | ✗ Vote not found")
        raise VoteNotFoundException(f"Vote with verification code '{verification_code}' not found")

    # Get selected candidates
    selected_ids = json.loads(vote.selected_candidate_ids)
    selected_names = [c.name for c in vote.event.candidates if c.id in selected_ids]

    # Build base response (Level 1)
    response = {
        'vote_id': vote.id,
        'event_id': vote.event_id,
        'event_name': vote.event.name,
        'vote_at': vote.vote_at,
        'selected_candidates': selected_names,
        'verification_code': verification_code,
        'customer_unique_id': None,
        'customer_id': None
    }

    # Level 2: Add customer info if vote_secret provided and matches
    if vote_secret:
        if vote.vote_secret == vote_secret:
            response['customer_unique_id'] = vote.customer.unique_id
            response['customer_id'] = vote.customer_id
            logger.info(f"Event {vote.event_id} # DECODE | Level 2 | ✓ Vote decoded with voter identity: {vote.customer.unique_id}")
        else:
            logger.warning(f"Event {vote.event_id} # DECODE | Level 2 | ✗ Vote secret mismatch")
            from src.exceptions import InvalidVoteSelectionException
            raise InvalidVoteSelectionException("Vote secret does not match verification code")
    else:
        logger.info(f"Event {vote.event_id} # DECODE | Level 1 | ✓ Vote decoded (candidates only)")

    return response
