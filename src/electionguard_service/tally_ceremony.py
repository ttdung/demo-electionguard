"""
ElectionGuard Tally Ceremony.

Performs homomorphic aggregation of encrypted ballots and decrypts the tally.
"""
import logging
from typing import List, Dict
from electionguard.manifest import Manifest, InternalManifest
from electionguard.ballot import CiphertextBallot, SubmittedBallot
from electionguard.election import CiphertextElectionContext
from electionguard.tally import CiphertextTally, tally_ballots, PlaintextTally
from electionguard.data_store import DataStore
from electionguard.key_ceremony import ElectionKeyPair
from electionguard.decryption_share import DecryptionShare
from electionguard import compute_decryption_share, decrypt_tally, cast_ballot

logger = logging.getLogger(__name__)


def aggregate_ballots(
    encrypted_ballots: List[CiphertextBallot],
    manifest: Manifest,
    context: CiphertextElectionContext
) -> CiphertextTally:
    """
    Perform homomorphic aggregation of encrypted ballots.

    This adds all encrypted ballots together WITHOUT decrypting them.
    Uses the homomorphic property: E(a) × E(b) = E(a + b)

    Args:
        encrypted_ballots: List of encrypted ballots to aggregate
        manifest: ElectionGuard Manifest
        context: Cryptographic context

    Returns:
        CiphertextTally: Aggregated encrypted tally

    Raises:
        Exception: If aggregation fails
    """
    logger.info(f"# TALLY | Aggregating {len(encrypted_ballots)} encrypted ballots")

    try:
        # Cast ballots (mark them as CAST state for tallying)
        # In ElectionGuard 1.4.0, ballots must be cast before tallying
        cast_ballots = []
        for ballot in encrypted_ballots:
            submitted_ballot = cast_ballot(ballot)
            cast_ballots.append(submitted_ballot)

        logger.info(f"# TALLY | Cast {len(cast_ballots)} ballots for homomorphic addition")

        # Create DataStore from cast ballots
        store = DataStore()
        for ballot in cast_ballots:
            store.set(ballot.object_id, ballot)

        # Create internal manifest (required by tally_ballots in 1.4.0)
        internal_manifest = InternalManifest(manifest)

        # Perform homomorphic tally
        ciphertext_tally = tally_ballots(
            store=store,
            internal_manifest=internal_manifest,
            context=context
        )

        if ciphertext_tally is None:
            raise Exception("Ballot aggregation returned None")

        logger.info("# TALLY | ✓ Homomorphic aggregation completed (ballots still encrypted)")
        return ciphertext_tally

    except Exception as e:
        logger.error(f"# TALLY | ✗ Ballot aggregation failed: {str(e)}")
        raise


def decrypt_tally_with_secret(
    ciphertext_tally: CiphertextTally,
    guardian_keypair: ElectionKeyPair,
    context: CiphertextElectionContext,
    manifest: Manifest
) -> PlaintextTally:
    """
    Decrypt the aggregated tally using the guardian's keypair.

    In a full implementation, multiple guardians would provide partial decryptions.
    For MVP with single guardian, we compute the decryption share and decrypt.

    Args:
        ciphertext_tally: Encrypted aggregated tally
        guardian_keypair: Guardian's ElectionKeyPair (contains secret key)
        context: Cryptographic context
        manifest: Election manifest

    Returns:
        PlaintextTally: Decrypted vote counts

    Raises:
        Exception: If decryption fails
    """
    logger.info(f"# TALLY | Starting decryption ceremony (Guardian: {guardian_keypair.owner_id})")

    try:
        # Step 1: Compute decryption share from guardian's keypair
        logger.info("# TALLY | Computing decryption share from guardian's keypair...")
        decryption_share = compute_decryption_share(
            key_pair=guardian_keypair,
            tally=ciphertext_tally,
            context=context
        )

        if decryption_share is None:
            raise Exception("Failed to compute decryption share")

        logger.info(f"# TALLY | ✓ Decryption share computed (Guardian: {guardian_keypair.owner_id})")

        # Step 2: Decrypt tally with the decryption share
        # For single guardian, we only have one share
        shares = {guardian_keypair.owner_id: decryption_share}

        logger.info("# TALLY | Decrypting aggregated tally...")
        plaintext_tally = decrypt_tally(
            tally=ciphertext_tally,
            shares=shares,
            crypto_extended_base_hash=context.crypto_extended_base_hash,
            manifest=manifest
        )

        if plaintext_tally is None:
            raise Exception("Tally decryption returned None")

        logger.info("# TALLY | ✓ Tally decrypted successfully")
        return plaintext_tally

    except Exception as e:
        logger.error(f"# TALLY | ✗ Decryption failed: {str(e)}")
        raise


def extract_vote_counts(
    plaintext_tally: PlaintextTally,
    manifest: Manifest
) -> Dict[str, int]:
    """
    Extract vote counts per candidate from the decrypted tally.

    Args:
        plaintext_tally: Decrypted tally
        manifest: ElectionGuard Manifest

    Returns:
        Dict mapping candidate object_id to vote count

    Example:
        {
            "candidate-1-0": 75,   # Alice: 75 votes
            "candidate-1-1": 45,   # Bob: 45 votes
            "candidate-1-2": 30    # Carol: 30 votes
        }
    """
    logger.info("# TALLY | Extracting vote counts from plaintext tally")

    vote_counts = {}

    # Get the contest (we only have one per event)
    contest = manifest.contests[0]
    contest_tally = plaintext_tally.contests.get(contest.object_id)

    if contest_tally is None:
        logger.error(f"# TALLY | ✗ Contest {contest.object_id} not found in tally")
        return vote_counts

    # Extract counts for each selection (candidate)
    for selection_desc in contest.ballot_selections:
        selection_id = selection_desc.object_id
        selection_tally = contest_tally.selections.get(selection_id)

        if selection_tally:
            vote_count = selection_tally.tally
            vote_counts[selection_id] = vote_count
            logger.info(f"# TALLY |   {selection_id}: {vote_count} votes")
        else:
            logger.warning(f"# TALLY |   {selection_id}: No tally data")
            vote_counts[selection_id] = 0

    total_votes = sum(vote_counts.values())
    logger.info(f"# TALLY | ✓ Total votes counted: {total_votes}")

    return vote_counts


def perform_full_tally(
    encrypted_ballots: List[CiphertextBallot],
    manifest: Manifest,
    context: CiphertextElectionContext,
    guardian_keypair: ElectionKeyPair
) -> Dict[str, int]:
    """
    Perform complete tally ceremony: aggregate and decrypt.

    This is a convenience function that performs both steps:
    1. Homomorphic aggregation of encrypted ballots
    2. Decryption of the aggregated tally

    Args:
        encrypted_ballots: List of encrypted ballots
        manifest: ElectionGuard Manifest
        context: Cryptographic context
        guardian_keypair: Guardian's ElectionKeyPair for decryption

    Returns:
        Dict mapping candidate object_id to vote count

    Raises:
        Exception: If tally fails at any step
    """
    logger.info(f"# TALLY | ═══ Full Tally Ceremony Starting ═══")
    logger.info(f"# TALLY | Processing {len(encrypted_ballots)} encrypted ballots")

    # Step 1: Aggregate encrypted ballots (homomorphic tally)
    ciphertext_tally = aggregate_ballots(encrypted_ballots, manifest, context)

    # Step 2: Decrypt the aggregated tally
    plaintext_tally = decrypt_tally_with_secret(ciphertext_tally, guardian_keypair, context, manifest)

    # Step 3: Extract vote counts
    vote_counts = extract_vote_counts(plaintext_tally, manifest)

    logger.info("# TALLY | ═══ Full Tally Ceremony Completed ═══")
    return vote_counts
