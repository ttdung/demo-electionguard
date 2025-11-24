"""
ElectionGuard Key Ceremony.

Performs the key ceremony to generate cryptographic keys for the election.
For MVP, implements a simplified single-guardian setup.
"""
import logging
from typing import Tuple
from electionguard.manifest import Manifest, InternalManifest
from electionguard.election import CiphertextElectionContext, make_ciphertext_election_context
from electionguard.key_ceremony import ElectionKeyPair, generate_election_key_pair
from electionguard.group import ElementModQ

logger = logging.getLogger(__name__)


def perform_key_ceremony(
    manifest: Manifest,
    number_of_guardians: int = 1,
    quorum: int = 1
) -> Tuple[ElectionKeyPair, CiphertextElectionContext]:
    """
    Perform a simplified key ceremony for the election.

    For MVP, this creates a single guardian (trustee) who holds the election key.
    In production, multiple guardians would participate in a distributed key ceremony.

    Args:
        manifest: ElectionGuard Manifest defining the election
        number_of_guardians: Total number of guardians (default: 1 for MVP)
        quorum: Minimum guardians needed to decrypt (default: 1 for MVP)

    Returns:
        Tuple containing:
            - ElectionKeyPair: The guardian's election keypair (proper 1.4.0 type)
            - CiphertextElectionContext: Cryptographic context with joint public key

    Raises:
        Exception: If key ceremony fails

    Note:
        The secret key must be stored securely for tally decryption.
        For MVP, we'll store it in memory (not production-safe).
    """
    logger.info(f"Starting key ceremony for election: {manifest.election_scope_id}")
    logger.info(f"Guardians: {number_of_guardians}, Quorum: {quorum}")

    try:
        # Step 1: Generate election keypair for the guardian
        # ElectionKeyPair is the proper 1.4.0 type for guardian keys
        guardian_keypair = generate_election_key_pair(
            guardian_id="guardian-1",
            sequence_order=0,
            quorum=quorum
        )

        logger.info(f"Guardian election keypair generated")
        logger.info(f"Guardian ID: {guardian_keypair.owner_id}")
        logger.info(f"Public key: {guardian_keypair.key_pair.public_key.to_hex()[:32]}...")

        # Step 2: Create internal manifest
        internal_manifest = InternalManifest(manifest)

        # Step 3: Build the election context with the public key
        # For single guardian, the joint public key is just the guardian's public key
        # Generate commitment hash from guardian's public keys
        from electionguard.hash import hash_elems
        commitment_hash = hash_elems(guardian_keypair.key_pair.public_key)

        context = make_ciphertext_election_context(
            number_of_guardians=number_of_guardians,
            quorum=quorum,
            elgamal_public_key=guardian_keypair.key_pair.public_key,
            commitment_hash=commitment_hash,
            manifest_hash=internal_manifest.manifest_hash,
        )

        if context is None:
            raise Exception("Failed to build election context")

        logger.info(f"Election context created successfully")
        logger.info(f"Joint public key: {context.elgamal_public_key.to_hex()[:32]}...")
        logger.info(f"Crypto base hash: {context.crypto_base_hash.to_hex()[:32]}...")

        return guardian_keypair, context

    except Exception as e:
        logger.error(f"Key ceremony failed: {str(e)}")
        raise


def get_secret_key_from_keypair(keypair: ElectionKeyPair) -> ElementModQ:
    """
    Extract the secret key from an election keypair.

    Args:
        keypair: ElectionKeyPair containing the guardian's secret key

    Returns:
        ElementModQ: The secret key

    Note:
        This is used during tally decryption. Keep this key secure!
    """
    return keypair.key_pair.secret_key
