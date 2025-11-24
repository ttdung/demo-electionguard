"""
ElectionGuard Ballot Encryptor.

Encrypts voter ballots using homomorphic encryption and generates zero-knowledge proofs.
"""
import logging
import hashlib
from typing import List, Tuple, Dict
from electionguard.manifest import Manifest, InternalManifest
from electionguard.ballot import PlaintextBallot, PlaintextBallotContest, PlaintextBallotSelection
from electionguard.encrypt import encrypt_ballot, EncryptionDevice, EncryptionMediator
from electionguard.election import CiphertextElectionContext
from electionguard.ballot import CiphertextBallot

logger = logging.getLogger(__name__)


def create_plaintext_ballot(
    event_id: int,
    customer_id: int,
    selected_candidate_indices: List[int],
    manifest: Manifest
) -> PlaintextBallot:
    """
    Create a PlaintextBallot from voter selections.

    Args:
        event_id: Voting event ID
        customer_id: Customer (voter) ID
        selected_candidate_indices: List of selected candidate indices
        manifest: ElectionGuard Manifest

    Returns:
        PlaintextBallot: Unencrypted ballot with selections

    Example:
        If candidates are ["Alice", "Bob", "Carol"] and voter selects Bob (index 1):
        selected_candidate_indices = [1]
        This creates: [0, 1, 0] where 1 = selected, 0 = not selected
    """
    ballot_id = f"ballot-{event_id}-{customer_id}"

    # Get the contest from manifest (we only have one contest per event)
    contest = manifest.contests[0]

    # Create selections: 1 for selected, 0 for not selected
    selections = []
    for idx, selection_desc in enumerate(contest.ballot_selections):
        is_selected = idx in selected_candidate_indices
        selection = PlaintextBallotSelection(
            object_id=selection_desc.object_id,
            vote=1 if is_selected else 0,
            is_placeholder_selection=False
        )
        selections.append(selection)

    logger.info(f"Created {len(selections)} selections, {len(selected_candidate_indices)} selected")

    # Create contest
    plaintext_contest = PlaintextBallotContest(
        object_id=contest.object_id,
        ballot_selections=selections
    )

    # Create ballot
    ballot_style_id = manifest.ballot_styles[0].object_id
    plaintext_ballot = PlaintextBallot(
        object_id=ballot_id,
        style_id=ballot_style_id,  # Correct parameter name for 1.4.0
        contests=[plaintext_contest]
    )

    logger.info(f"PlaintextBallot created: {ballot_id}")
    return plaintext_ballot


def encrypt_vote_ballot(
    plaintext_ballot: PlaintextBallot,
    manifest: Manifest,
    context: CiphertextElectionContext,
    device_id: str = "device-001"
) -> Tuple[CiphertextBallot, str]:
    """
    Encrypt a plaintext ballot using ElectionGuard.

    This performs:
    1. Homomorphic encryption of each selection using the joint public key
    2. Generation of zero-knowledge proofs (Chaum-Pedersen proofs)
    3. Creation of a verification code (ballot hash)

    Args:
        plaintext_ballot: Unencrypted ballot with voter selections
        manifest: ElectionGuard Manifest
        context: Cryptographic context with public key
        device_id: Identifier for the voting device (for tracking)

    Returns:
        Tuple containing:
            - CiphertextBallot: Encrypted ballot with proofs
            - str: Verification code (ballot tracking code)

    Raises:
        Exception: If encryption fails
    """
    logger.info(f"# ENCRYPT | Starting ballot encryption: {plaintext_ballot.object_id}")

    try:
        # Create encryption device
        logger.info(f"# ENCRYPT | SDK Step 1: Creating encryption device ({device_id})")
        device = EncryptionDevice(
            device_id=device_id,
            session_id=1,
            launch_code=1,
            location="demo-location"
        )

        # Create internal manifest (required by EncryptionMediator in 1.4.0)
        logger.info("# ENCRYPT | SDK Step 2: Creating internal manifest")
        internal_manifest = InternalManifest(manifest)

        # Create encryption mediator
        logger.info("# ENCRYPT | SDK Step 3: Initializing encryption mediator with public key")
        mediator = EncryptionMediator(internal_manifest, context, device)

        # Encrypt the ballot
        logger.info("# ENCRYPT | SDK Step 4: Performing homomorphic encryption with zero-knowledge proofs")
        ciphertext_ballot = mediator.encrypt(plaintext_ballot)

        if ciphertext_ballot is None:
            raise Exception("Ballot encryption returned None")

        logger.info("# ENCRYPT | SDK Step 5: Encryption complete, generating verification code")

        # Generate verification code from ballot hash
        # This is the code voters use to verify their ballot was counted
        ballot_hash = ciphertext_ballot.crypto_hash.to_hex()
        verification_code = generate_verification_code(ballot_hash)

        logger.info(f"# ENCRYPT | ✓ Ballot encrypted successfully (Code: {verification_code}, Hash: {ballot_hash[:16]}...)")

        return ciphertext_ballot, verification_code

    except Exception as e:
        logger.error(f"# ENCRYPT | ✗ Encryption failed: {str(e)}")
        raise


def generate_verification_code(ballot_hash: str) -> str:
    """
    Generate a human-readable verification code from ballot hash.

    Converts the cryptographic hash into a format like: "COOK-7HMCG-NOTION-9329D"
    This code is given to the voter to verify their ballot later.

    Args:
        ballot_hash: Hexadecimal hash of the encrypted ballot

    Returns:
        str: Formatted verification code

    Example:
        >>> generate_verification_code("a1b2c3d4...")
        "COOK-7HMCG-NOTION-9329D"
    """
    # Take first 16 characters of hash for uniqueness
    hash_prefix = ballot_hash[:16].upper()

    # Format as readable groups
    # For MVP, just format the hex nicely
    # In production, might use word lists like BIP39
    code = '-'.join([
        hash_prefix[i:i+4] for i in range(0, len(hash_prefix), 4)
    ])

    return code


def validate_ballot_selections(
    selected_candidate_indices: List[int],
    num_candidates: int,
    allow_vote_candidate_num: int
) -> Tuple[bool, str]:
    """
    Validate that ballot selections follow election rules.

    Args:
        selected_candidate_indices: Indices of selected candidates
        num_candidates: Total number of candidates
        allow_vote_candidate_num: Number of candidates voter can select

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> validate_ballot_selections([0, 2], 5, 2)
        (True, "")
        >>> validate_ballot_selections([0], 5, 2)
        (False, "Must select exactly 2 candidate(s)")
    """
    # Check selection count
    if len(selected_candidate_indices) != allow_vote_candidate_num:
        return False, f"Must select exactly {allow_vote_candidate_num} candidate(s)"

    # Check for duplicates
    if len(selected_candidate_indices) != len(set(selected_candidate_indices)):
        return False, "Cannot select the same candidate multiple times"

    # Check indices are valid
    for idx in selected_candidate_indices:
        if idx < 0 or idx >= num_candidates:
            return False, f"Invalid candidate index: {idx}"

    return True, ""
