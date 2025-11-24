"""
Test ballot encryption with ElectionGuard.
"""
import sys
sys.path.insert(0, '/Users/uyenzen/Documents/self-learning/demo-electionguard')

from src.electionguard_service.manifest_builder import build_manifest
from src.electionguard_service.key_ceremony import perform_key_ceremony
from src.electionguard_service.ballot_encryptor import (
    create_plaintext_ballot,
    encrypt_vote_ballot,
    validate_ballot_selections
)

def test_ballot_encryption():
    """Test creating and encrypting a ballot."""
    print("=" * 60)
    print("Testing Ballot Encryption")
    print("=" * 60)

    # Step 1: Build manifest
    print("\n1. Building manifest...")
    event_id = 1
    event_name = "2024 Student Council Election"
    candidates = ["Alice Johnson", "Bob Smith", "Carol Williams"]

    manifest = build_manifest(
        event_id=event_id,
        event_name=event_name,
        candidate_names=candidates,
        allow_vote_candidate_num=1
    )
    print(f"✅ Manifest created with {len(candidates)} candidates")

    # Step 2: Perform key ceremony
    print("\n2. Performing key ceremony...")
    keypair, context = perform_key_ceremony(manifest)
    print(f"✅ Key ceremony complete")
    print(f"   Public key: {context.elgamal_public_key.to_hex()[:32]}...")

    # Step 3: Validate ballot selections
    print("\n3. Validating ballot selections...")
    customer_id = 101
    selected_indices = [1]  # Vote for Bob (index 1)

    is_valid, error_msg = validate_ballot_selections(
        selected_candidate_indices=selected_indices,
        num_candidates=len(candidates),
        allow_vote_candidate_num=1
    )

    if not is_valid:
        print(f"❌ Validation failed: {error_msg}")
        return False
    print(f"✅ Ballot selections valid")

    # Step 4: Create plaintext ballot
    print("\n4. Creating plaintext ballot...")
    plaintext_ballot = create_plaintext_ballot(
        event_id=event_id,
        customer_id=customer_id,
        selected_candidate_indices=selected_indices,
        manifest=manifest
    )
    print(f"✅ Plaintext ballot created: {plaintext_ballot.object_id}")

    # Verify ballot structure
    contest = plaintext_ballot.contests[0]
    print(f"   Contest: {contest.object_id}")
    print(f"   Selections:")
    for selection in contest.ballot_selections:
        print(f"     - {selection.object_id}: vote={selection.vote}")

    # Step 5: Encrypt ballot
    print("\n5. Encrypting ballot...")
    try:
        ciphertext_ballot, verification_code = encrypt_vote_ballot(
            plaintext_ballot=plaintext_ballot,
            manifest=manifest,
            context=context,
            device_id="test-device-001"
        )
        print(f"✅ Ballot encrypted successfully!")
        print(f"   Ballot ID: {ciphertext_ballot.object_id}")
        print(f"   Verification code: {verification_code}")
        print(f"   Crypto hash: {ciphertext_ballot.crypto_hash.to_hex()[:32]}...")

        # Verify encryption created proofs
        encrypted_contest = ciphertext_ballot.contests[0]
        print(f"\n   Encrypted contest: {encrypted_contest.object_id}")
        print(f"   Encrypted selections: {len(encrypted_contest.ballot_selections)}")

        for enc_selection in encrypted_contest.ballot_selections:
            print(f"     - {enc_selection.object_id}")
            print(f"       Has ciphertext: {enc_selection.ciphertext is not None}")
            print(f"       Has proof: {enc_selection.proof is not None}")

        print("\n" + "=" * 60)
        print("✨ Ballot encryption test PASSED!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n❌ Ballot encryption FAILED!")
        print(f"   Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_ballot_encryption()
    sys.exit(0 if success else 1)
