"""
Test complete ElectionGuard flow: manifest → keys → encrypt → tally.
"""
import sys
sys.path.insert(0, '/Users/uyenzen/Documents/self-learning/demo-electionguard')

from src.electionguard_service.manifest_builder import build_manifest
from src.electionguard_service.key_ceremony import perform_key_ceremony
from src.electionguard_service.ballot_encryptor import (
    create_plaintext_ballot,
    encrypt_vote_ballot
)
from src.electionguard_service.tally_ceremony import perform_full_tally

def test_full_electionguard_flow():
    """Test complete ElectionGuard workflow."""
    print("=" * 70)
    print("COMPLETE ELECTIONGUARD FLOW TEST")
    print("=" * 70)

    # Step 1: Build manifest
    print("\n📋 Step 1: Building election manifest...")
    event_id = 1
    event_name = "2024 Class President Election"
    candidates = ["Alice Johnson", "Bob Smith", "Carol Williams"]

    manifest = build_manifest(
        event_id=event_id,
        event_name=event_name,
        candidate_names=candidates,
        allow_vote_candidate_num=1
    )
    print(f"   ✅ Manifest created: {manifest.election_scope_id}")
    print(f"   Candidates: {', '.join(candidates)}")

    # Step 2: Perform key ceremony
    print("\n🔑 Step 2: Performing key ceremony...")
    guardian_keypair, context = perform_key_ceremony(manifest)
    print(f"   ✅ Key ceremony complete")
    print(f"   Guardian ID: {guardian_keypair.owner_id}")
    print(f"   Public key: {guardian_keypair.key_pair.public_key.to_hex()[:32]}...")

    # Step 3: Encrypt multiple ballots
    print("\n🗳️  Step 3: Encrypting ballots...")

    # Simulate 5 voters
    votes = [
        (101, [0]),  # Voter 101 votes for Alice (index 0)
        (102, [1]),  # Voter 102 votes for Bob (index 1)
        (103, [0]),  # Voter 103 votes for Alice
        (104, [2]),  # Voter 104 votes for Carol (index 2)
        (105, [0]),  # Voter 105 votes for Alice
    ]

    encrypted_ballots = []
    verification_codes = []

    for customer_id, selected_indices in votes:
        # Create plaintext ballot
        plaintext_ballot = create_plaintext_ballot(
            event_id=event_id,
            customer_id=customer_id,
            selected_candidate_indices=selected_indices,
            manifest=manifest
        )

        # Encrypt ballot
        ciphertext_ballot, verification_code = encrypt_vote_ballot(
            plaintext_ballot=plaintext_ballot,
            manifest=manifest,
            context=context
        )

        encrypted_ballots.append(ciphertext_ballot)
        verification_codes.append(verification_code)

        candidate_name = candidates[selected_indices[0]]
        print(f"   ✅ Voter {customer_id}: voted for {candidate_name} ({selected_indices[0]})")
        print(f"      Verification code: {verification_code}")

    print(f"\n   Total ballots encrypted: {len(encrypted_ballots)}")

    # Step 4: Perform tally ceremony
    print("\n📊 Step 4: Performing tally ceremony...")
    print("   (Homomorphic aggregation + decryption)")

    vote_counts = perform_full_tally(
        encrypted_ballots=encrypted_ballots,
        manifest=manifest,
        context=context,
        guardian_keypair=guardian_keypair
    )

    # Step 5: Display results
    print("\n🎯 Step 5: Election Results")
    print("   " + "=" * 50)

    total_votes = sum(vote_counts.values())

    for idx, candidate_name in enumerate(candidates):
        candidate_id = f"candidate-{event_id}-{idx}"
        count = vote_counts.get(candidate_id, 0)
        percentage = (count / total_votes * 100) if total_votes > 0 else 0
        print(f"   {candidate_name:20s}: {count:3d} votes ({percentage:5.1f}%)")

    print("   " + "=" * 50)
    print(f"   Total votes: {total_votes}")

    # Step 6: Verify correctness
    print("\n✅ Step 6: Verifying results...")
    expected_counts = {
        f"candidate-{event_id}-0": 3,  # Alice: 3 votes
        f"candidate-{event_id}-1": 1,  # Bob: 1 vote
        f"candidate-{event_id}-2": 1,  # Carol: 1 vote
    }

    all_correct = True
    for candidate_id, expected_count in expected_counts.items():
        actual_count = vote_counts.get(candidate_id, 0)
        if actual_count != expected_count:
            print(f"   ❌ {candidate_id}: expected {expected_count}, got {actual_count}")
            all_correct = False

    if all_correct:
        print("   ✅ All vote counts match expected values!")
        print("\n" + "=" * 70)
        print("🎉 COMPLETE ELECTIONGUARD FLOW TEST PASSED!")
        print("=" * 70)
        print("\n✨ Summary:")
        print("   - Manifest creation: ✅")
        print("   - Key ceremony: ✅")
        print("   - Ballot encryption: ✅")
        print("   - Homomorphic tally: ✅")
        print("   - Tally decryption: ✅")
        print("   - Vote counting: ✅")
        print("   - End-to-end verifiable voting: ✅")
        return True
    else:
        print("\n❌ VOTE COUNT MISMATCH!")
        return False

if __name__ == "__main__":
    success = test_full_electionguard_flow()
    sys.exit(0 if success else 1)
