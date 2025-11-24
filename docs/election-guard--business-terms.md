# ElectionGuard Terminology Guide for Business Leaders

  A plain-language glossary to understand ElectionGuard voting technology.

## ⏺ ElectionGuard Terminology Tree

### ElectionGuard Voting System Terminology

  │
  ├── Core Concepts
  │   ├── ElectionGuard
  │   ├── End-to-End Verifiable (E2EV) Election
  │   └── Homomorphic Encryption
  │
  ├── People & Roles
  │   ├── Voter
  │   ├── Guardian (Trustee)
  │   ├── Election Administrator
  │   ├── Verifier (Auditor)
  │   └── Voting Device Vendor
  │
  ├── Pre-Election Setup
  │   ├── Election Manifest
  │   ├── Key Ceremony (Key Generation Ceremony)
  │   ├── Joint Election Key (Public Key)
  │   ├── Private Key Share (Secret Share)
  │   ├── Threshold (k-of-n)
  │   └── Backup Share
  │
  ├── Voting Process
  │   ├── Ballot Style
  │   ├── PlaintextBallot
  │   ├── CiphertextBallot (Encrypted Ballot)
  │   ├── Ballot Encryption
  │   ├── Verification Code (Tracking Code / Ballot ID)
  │   ├── Cast Ballot
  │   └── Challenge Ballot (Spoiled Ballot)
  │
  ├── Security Proofs (The Math Behind Trust)
  │   ├── Zero-Knowledge Proof
  │   ├── Chaum-Pedersen Proof
  │   ├── Range Proof (Correctness Proof)
  │   └── Ballot Chaining
  │
  ├── Post-Election
  │   ├── Tally
  │   ├── Encrypted Tally
  │   ├── Homomorphic Aggregation
  │   ├── Tally Ceremony (Decryption Ceremony)
  │   ├── Partial Decryption
  │   ├── Decryption Proof
  │   ├── PlaintextTally (Final Results)
  │   └── Lagrange Interpolation
  │
  ├── Published Data
  │   ├── Election Record
  │   ├── Submitted Ballot
  │   ├── Spoiled Ballot
  │   └── Guardian Record
  │
  ├── Verification
  │   ├── Individual Verification (Voter Verification)
  │   ├── Independent Verification (Universal Verification)
  │   ├── Verifier Software
  │   ├── Cast as Intended
  │   ├── Recorded as Cast
  │   └── Counted as Cast
  │
  ├── Technical Terms (Simplified)
  │   ├── Encryption
  │   ├── Decryption
  │   ├── Public Key
  │   ├── Private Key
  │   ├── Hash (Cryptographic Hash)
  │   ├── Nonce
  │   ├── ElGamal Encryption
  │   └── Commitment
  │
  ├── Data Formats & Files
  │   ├── JSON File
  │   ├── Manifest.json
  │   ├── Context.json
  │   ├── Tally.json
  │   └── Encrypted_tally.json
  │
  ├── Security Concepts
  │   ├── Verifiable
  │   ├── Cryptographic Proof
  │   ├── Tamper-Evidence
  │   ├── Ballot Secrecy (Voter Privacy)
  │   ├── Election Integrity
  │   └── Risk-Limiting Audit (RLA)
  │
  ├── Integration Terms
  │   ├── Voting System
  │   ├── Election Management System (EMS)
  │   ├── Ballot Marking Device (BMD)
  │   ├── Optical Scanner
  │   └── Cast Vote Record (CVR)
  │
  └── Business Benefits
      ├── Transparency
      ├── Auditability
      ├── Cost-Effective
      ├── Risk Mitigation
      ├── Vendor-Neutral
      └── Future-Proof

## Condensed View by Phase

  ElectionGuard Terms by Election Phase
  │
  ├── SETUP PHASE
  │   ├── Election Manifest
  │   ├── Key Ceremony
  │   │   ├── Guardian (Trustee)
  │   │   ├── Joint Election Key
  │   │   ├── Private Key Share
  │   │   ├── Threshold (k-of-n)
  │   │   └── Backup Share
  │   └── Election Management System (EMS)
  │
  ├── VOTING PHASE
  │   ├── Voter
  │   ├── Ballot Style
  │   ├── Voting Device
  │   │   ├── Ballot Marking Device (BMD)
  │   │   └── Optical Scanner
  │   │
  │   ├── Ballot Creation
  │   │   ├── PlaintextBallot
  │   │   ├── Ballot Encryption
  │   │   │   ├── ElGamal Encryption
  │   │   │   ├── Homomorphic Encryption
  │   │   │   ├── Public Key
  │   │   │   └── Nonce
  │   │   └── CiphertextBallot (Encrypted Ballot)
  │   │
  │   ├── Ballot Proofs
  │   │   ├── Zero-Knowledge Proof
  │   │   ├── Chaum-Pedersen Proof
  │   │   ├── Range Proof
  │   │   └── Ballot Chaining
  │   │
  │   ├── Verification Code (Tracking Code)
  │   │
  │   └── Ballot Submission
  │       ├── Cast Ballot
  │       └── Challenge Ballot (Spoiled Ballot)
  │
  ├── TALLYING PHASE
  │   ├── Tally Ceremony
  │   │   ├── Guardian (minimum k)
  │   │   ├── Partial Decryption
  │   │   ├── Private Key Share
  │   │   └── Lagrange Interpolation
  │   │
  │   ├── Aggregation
  │   │   ├── Homomorphic Aggregation
  │   │   ├── Encrypted Tally
  │   │   └── Decryption Proof
  │   │
  │   └── Final Results
  │       ├── PlaintextTally
  │       └── Tally
  │
  ├── PUBLICATION PHASE
  │   ├── Election Record
  │   │   ├── manifest.json
  │   │   ├── context.json
  │   │   ├── tally.json
  │   │   ├── encrypted_tally.json
  │   │   ├── Submitted Ballots
  │   │   ├── Spoiled Ballots
  │   │   └── Guardian Records
  │   │
  │   └── Data Properties
  │       ├── JSON File
  │       ├── Hash (Cryptographic Hash)
  │       └── Commitment
  │
  └── VERIFICATION PHASE
      ├── Voter Verification
      │   ├── Individual Verification
      │   ├── Verification Code lookup
      │   ├── Cast as Intended
      │   └── Recorded as Cast
      │
      └── Independent Verification
          ├── Verifier (Auditor)
          ├── Verifier Software
          ├── Universal Verification
          ├── Counted as Cast
          ├── Cryptographic Proof
          ├── Verifiable
          ├── Tamper-Evidence
          └── Risk-Limiting Audit (RLA)

## Relationship View

  Key Relationships Between Terms
  │
  ├── Encryption Hierarchy
  │   ├── Public Key (encrypts)
  │   │   └── Joint Election Key
  │   │       └── Created by combining Guardian public keys
  │   │
  │   ├── Private Key (decrypts)
  │   │   └── Private Key Share
  │   │       ├── Held by each Guardian
  │   │       └── Backup Share (emergency copy)
  │   │
  │   └── Threshold (k-of-n)
  │       └── Minimum Guardians needed to decrypt
  │
  ├── Ballot Lifecycle
  │   ├── PlaintextBallot (voter selections)
  │   │   └── Encrypted by →
  │   │       └── CiphertextBallot (encrypted selections)
  │   │           ├── With → Zero-Knowledge Proofs
  │   │           ├── Generates → Verification Code
  │   │           └── Becomes either →
  │   │               ├── Cast Ballot (counted)
  │   │               └── Challenge Ballot (audited, not counted)
  │   │
  │   └── All Cast Ballots →
  │       └── Homomorphic Aggregation →
  │           └── Encrypted Tally →
  │               └── Tally Ceremony (Guardian decryption) →
  │                   └── PlaintextTally (final results)
  │
  ├── Proof Chain
  │   ├── Zero-Knowledge Proof (generic concept)
  │   │   ├── Chaum-Pedersen Proof (proves 0 or 1)
  │   │   ├── Range Proof (proves correct sum)
  │   │   └── Decryption Proof (proves correct decryption)
  │   │
  │   └── Verification Uses
  │       ├── Cast as Intended (voter confidence)
  │       ├── Recorded as Cast (ballot stored correctly)
  │       └── Counted as Cast (tally computed correctly)
  │
  ├── Ceremony Relationships
  │   ├── Key Ceremony (before voting)
  │   │   ├── Creates → Joint Election Key
  │   │   ├── Creates → Private Key Shares
  │   │   └── Creates → Backup Shares
  │   │
  │   └── Tally Ceremony (after voting)
  │       ├── Uses → Private Key Shares
  │       ├── Creates → Partial Decryptions
  │       ├── Creates → Decryption Proofs
  │       └── Produces → PlaintextTally
  │
  └── Verification Hierarchy
      ├── Individual Verification (voters)
      │   └── Uses Verification Code
      │       └── Confirms Recorded as Cast
      │
      └── Independent Verification (third parties)
          └── Uses Election Record
              ├── Verifies → Cast as Intended (via proofs)
              ├── Verifies → Recorded as Cast (via hashes)
              └── Verifies → Counted as Cast (via tally proofs)

## Quick Reference Tree (Most Important Terms)

  Essential ElectionGuard Terms
  │
  ├── BEFORE VOTING
  │   ├── Guardian (holds key pieces)
  │   ├── Key Ceremony (creates encryption key)
  │   └── Election Manifest (ballot definition)
  │
  ├── DURING VOTING
  │   ├── Encryption (scrambles vote)
  │   ├── CiphertextBallot (encrypted vote)
  │   ├── Verification Code (voter's tracking number)
  │   ├── Cast Ballot (counted)
  │   └── Challenge Ballot (audited, not counted)
  │
  ├── AFTER VOTING
  │   ├── Tally Ceremony (decrypt results)
  │   ├── Election Record (published data)
  │   └── PlaintextTally (final results)
  │
  └── VERIFICATION
      ├── Individual Verification (voter checks their code)
      └── Independent Verification (anyone checks the math)

  These tree structures show how all the terminology fits together hierarchically and by relationships!

  ---

## Core Concepts

### ElectionGuard

  A free, open-source voting security system developed by Microsoft that makes elections verifiable using mathematics. Think of it as a
  tamper-evident seal for elections—anyone can verify votes were counted correctly without seeing how individuals voted.

### End-to-End Verifiable (E2EV) Election

  An election where voters can verify their own ballot was counted AND independent observers can verify the entire election was conducted
  correctly—all without revealing how anyone voted. Like tracking a package, but for your vote.

### Homomorphic Encryption

  Special math that lets you add numbers without seeing what they are. Imagine locked boxes where you can count what's inside without
  opening them. This allows tallying encrypted votes without decrypting individual ballots.

  ---

## People & Roles

### Voter

  The person casting a ballot. In ElectionGuard, voters get a special code to verify their ballot later.

### Guardian (also called "Trustee")

  Trusted community members who hold "keys" to decrypt election results. Like bank safety deposit boxes that need multiple keys—no single
  guardian can access results alone. Typically 5-10 people from different organizations (political parties, civic groups, universities).

### Election Administrator

  Officials who run the election (county clerks, election boards). They organize the guardians and publish results, but cannot decrypt
  votes alone.

### Verifier (also called "Auditor")

  Independent third parties (news organizations, political parties, watchdog groups, mathematicians) who check the election math to confirm
   accuracy.

### Voting Device Vendor

  Companies that make voting machines, scanners, or ballot-marking devices. ElectionGuard works with their existing equipment.

  ---

## Pre-Election Setup

### Election Manifest

  The complete definition of your election written in a standard format. Contains:

- All contests (races/questions)
- All candidates/choices
- Which ballots go to which voters
- Rules (how many selections allowed)

  Think of it as the blueprint for the election.

### Key Ceremony (also "Key Generation Ceremony")

  A formal meeting before the election where guardians create the encryption keys together. Like a bank vault that requires multiple people
   to open. Usually takes 1-2 hours with all guardians present.

### Joint Election Key (also "Public Key")

  The "master lock" created by combining all guardian keys. Every ballot is locked with this key. The public can use it to verify ballots,
  but only guardians together can unlock results.

### Private Key Share (also "Secret Share")

  Each guardian's secret piece of the master key. Like having 1 of 5 required keys to open a vault. Guardians never share these.

### Threshold (written as "k-of-n")

  The minimum number of guardians needed to decrypt results. Example: "3-of-5" means 5 total guardians, but any 3 can complete the tally.
  Protects against guardians being sick, unavailable, or compromised.

### Backup Share

  Encrypted copies of each guardian's key piece, split among other guardians. Insurance policy if a guardian becomes unavailable—others can
   compensate using their backup pieces.

  ---

## Voting Process

### Ballot Style

  The specific combination of contests a voter sees based on their address. A county voter might see county + state races, while a city
  voter sees county + state + city races.

### PlaintextBallot

  The voter's selections in readable form before encryption. Example: "Voter chose Candidate A in Race 1, Yes on Question 2." Exists
  briefly in the device's memory only.

### CiphertextBallot (also "Encrypted Ballot")

  The voter's ballot after encryption—looks like random numbers. Cannot be read without the guardians' keys, but can be mathematically
  verified as valid.

### Ballot Encryption

  The process of scrambling the ballot using the Joint Election Key so nobody can read it, but it can still be counted and verified. Takes
  a fraction of a second.

### Verification Code (also "Tracking Code" or "Ballot ID")

  A unique code generated for each ballot (example: COOK 7HMCG NOTION 9329D). Voter keeps this to later verify their ballot was counted.
  Like a package tracking number—doesn't reveal contents, just confirms delivery.

### Cast Ballot

  A ballot the voter accepted and wants counted in the election. Stored in encrypted form.

### Challenge Ballot (also "Spoiled Ballot")

  A ballot the voter chose to "challenge" by having it decrypted immediately to prove encryption worked correctly. NOT counted in results.
  Voter must start over with a new ballot. Used for random auditing.

  ---

## Security Proofs (The Math Behind Trust)

### Zero-Knowledge Proof

  Mathematical evidence that something is true without revealing the details. Like proving you know a password without saying it.
  ElectionGuard uses these to prove ballots are valid without revealing votes.

### Chaum-Pedersen Proof

  A specific type of zero-knowledge proof proving each encrypted selection is a valid 0 (not selected) or 1 (selected)—not 2, not -1, not
  any invalid number.

### Range Proof (also "Correctness Proof")

  Mathematical proof that a voter didn't overvote. Example: If you can select 2 candidates, proves the sum of selections equals exactly 2.

### Ballot Chaining

  Linking each ballot to the previous one using math, creating a chain. Makes it detectable if ballots are added, removed, or reordered
  after submission. Optional security feature.

  ---

## Post-Election

### Tally

  The counting of all votes to produce final results.

### Encrypted Tally

  The combined total of all encrypted ballots, still in encrypted form. You can verify the addition was done correctly, but can't read the
  numbers yet.

### Homomorphic Aggregation

  The process of combining encrypted ballots using special math to create the encrypted tally. Like adding numbers inside locked boxes
  without opening them.

### Tally Ceremony (also "Decryption Ceremony")

  A formal meeting after voting where guardians come together to decrypt the final tally. Similar to the Key Ceremony but in reverse. Takes
   1-2 hours.

### Partial Decryption

  Each guardian's contribution to unlocking the encrypted tally. Each guardian provides one piece; minimum threshold (k) pieces needed to
  complete.

### Decryption Proof

  Mathematical evidence that guardians correctly decrypted the tally without cheating or making mistakes.

### PlaintextTally (also "Final Results")

  The decrypted election results in readable form. Example: "Candidate A: 15,432 votes, Candidate B: 13,987 votes."

### Lagrange Interpolation

  Complex math used when guardians are missing. Allows remaining guardians to compensate using backup shares. Business takeaway: Election
  can still be completed even if some guardians are unavailable.

  ---

## Published Data

### Election Record

  The complete package of election data published online after voting. Contains:

- All encrypted ballots
- All proofs
- Encrypted tally
- Decrypted results
- Guardian information (public parts only)

  Anyone can download and verify. Typically 1-10 GB depending on election size.

### Submitted Ballot

  An encrypted cast ballot that was counted, stored in the published election record with its verification code.

### Spoiled Ballot

  A challenged ballot stored in decrypted form in the published record. Proves the encryption system works correctly.

### Guardian Record

  Public information about each guardian (name, organization, public key parts). Does NOT include their private keys.

  ---

## Verification

### Individual Verification (also "Voter Verification")

  When voters use their verification code to confirm their ballot appears in the published results. Can be done on a website or mobile app.
   Takes 30 seconds.

### Independent Verification (also "Universal Verification")

  When third parties download the election record and verify all the math:

- Every ballot is properly encrypted
- The tally adds up correctly
- Decryption was done correctly

## Requires specialized software but anyone can do it

### Verifier Software

  Computer programs that check election record math. Multiple organizations create different verifiers—all should reach the same conclusion
   if the election was conducted correctly.

### Cast as Intended

  Verification that the device correctly encrypted your selections. Voters gain confidence through challenge ballots—some voters randomly
  challenge their ballots to prove the system works.

### Recorded as Cast

  Verification that your encrypted ballot was stored and not altered. Voters check their verification code appears in the published record.

### Counted as Cast

  Verification that stored ballots were correctly tallied. Independent verifiers check the math of aggregation and decryption.

  ---

## Technical Terms (Simplified)

### Encryption

  Scrambling data so only authorized people can unscramble it. Like a combination lock on a diary.

### Decryption

  Unscrambling encrypted data back to readable form. Opening the combination lock.

### Public Key

  Information that can be shared publicly and used to encrypt data. Anyone can lock the box, but only private key holders can unlock it.

### Private Key

  Secret information used to decrypt data. Must be kept secure. In ElectionGuard, split among multiple guardians.

### Hash (also "Cryptographic Hash")

  A mathematical fingerprint of data. If even one letter changes, the fingerprint completely changes. Used to detect tampering. Cannot be
  reversed to get original data.

### Nonce

  A random number used once to make encryption unique. Ensures encrypting the same vote twice produces different ciphertexts, preventing
  pattern analysis.

### ElGamal Encryption

  The specific encryption method ElectionGuard uses. Chosen because it supports homomorphic addition (counting encrypted votes).

### Commitment

  A mathematical way to lock in a value without revealing it. Like putting a prediction in a sealed envelope—you can prove later what you
  predicted without being able to change it.

  ---

## Data Formats & Files

### JSON File

  A standard text file format for storing structured data. All ElectionGuard data is stored in JSON for transparency and compatibility.

### Manifest.json

  The file containing the election manifest (definition).

### Context.json

  The file containing cryptographic setup information (joint public key, election parameters).

### Tally.json

  The file containing final decrypted results.

### Encrypted_tally.json

  The file containing the encrypted combined total before decryption.

  ---

## Security Concepts

### Verifiable

  Can be checked and proven mathematically. Not based on trust, but on math anyone can verify.

### Cryptographic Proof

  Mathematical evidence that something was done correctly. Cannot be faked without being detected.

### Tamper-Evidence

  System design where any tampering leaves detectable traces. Like security tape that shows "VOID" if removed.

### Ballot Secrecy (also "Voter Privacy")

  The principle that individual votes remain private. ElectionGuard maintains this because individual ballots stay encrypted forever—only
  the combined total is decrypted.

### Election Integrity

  Confidence that election results accurately reflect voter intent, with no votes added, removed, or changed.

### Risk-Limiting Audit (RLA)

  A statistical audit method that provides strong evidence of correct outcomes. ElectionGuard's challenge ballots can support RLAs.

  ---

## Integration Terms

### Voting System

  The complete set of equipment and software used to conduct an election (ballot printers, scanners, tabulators, etc.).

### Election Management System (EMS)

  Software used by election officials to design ballots, program machines, and manage the election.

### Ballot Marking Device (BMD)

  A machine that helps voters mark paper ballots, often used for accessibility. ElectionGuard can add verification codes to BMD output.

### Optical Scanner

  A machine that reads paper ballots. Can be enhanced with ElectionGuard to encrypt votes as they're scanned.

### Cast Vote Record (CVR)

  A record of how a ballot was interpreted by voting equipment. ElectionGuard replaces traditional CVRs with encrypted verifiable versions.

  ---

### Business Benefits

### Transparency

  Everything is public and verifiable. Builds public confidence.

### Auditability

  Complete mathematical audit trail. Goes beyond traditional audits.

### Cost-Effective

  Free open-source software. Works with existing voting equipment.

### Risk Mitigation

  Multiple layers of security. No single point of failure.

### Vendor-Neutral

  Not tied to specific voting machine companies. Reduces vendor lock-in.

### Future-Proof

  Based on proven cryptographic standards. Designed for long-term security.

  ---

## Common Misconceptions - Clarified

  ❌ "Blockchain voting"✅ ElectionGuard does NOT use blockchain. Uses proven cryptographic techniques from academic research.

  ❌ "Online voting / Internet voting"✅ ElectionGuard is for in-person and mail voting with paper ballots, NOT internet voting.

  ❌ "Votes are stored in a database"✅ Encrypted ballots are published as files anyone can download, not locked in a proprietary database.

  ❌ "Requires new voting machines"✅ Works with existing voting equipment from multiple vendors.

  ❌ "Voters need technical knowledge"✅ Voter experience is nearly identical to current voting. Verification is optional and simple.

  ❌ "Guardians can see how people voted"✅ Guardians only decrypt the combined total, never individual ballots.

  ---

## Quick Reference: The 30-Second Explanation

  For executives:
  "ElectionGuard is like package tracking for votes. Voters get a code to verify their ballot was counted, and independent observers can
  verify the entire election using published mathematical proofs—all without revealing how anyone voted. It's free, open-source, and works
  with existing voting equipment."

  For board members:
  "ElectionGuard adds cryptographic verification to elections, allowing anyone to mathematically prove results are correct while
  maintaining voter privacy. Reduces election security risks, increases public trust, and costs significantly less than replacing voting
  equipment."

  For investors/funders:
  "Developed by Microsoft and endorsed by election security experts, ElectionGuard addresses the #1 concern in modern elections:
  verifiability. It's being piloted in multiple jurisdictions and offers a clear ROI through increased public confidence and reduced legal
  challenges."

  ---
  This glossary should help business stakeholders understand ElectionGuard without getting lost in technical details. The focus is on
  outcomes and benefits rather than cryptographic mathematics.
