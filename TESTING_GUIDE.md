# ElectionGuard Voting Demo - Testing Guide

## Quick Start

### 1. Start the Server

```bash
# Navigate to project directory
cd /Users/uyenzen/Documents/self-learning/demo-electionguard

# Activate virtual environment
source .venv/bin/activate

# Start the server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2. Access the Application

**Frontend UI:** Open your browser and navigate to:
```
http://localhost:8000/
```

**API Documentation:** Interactive API docs available at:
```
http://localhost:8000/docs
```

**Alternative API docs:**
```
http://localhost:8000/redoc
```

---

## Testing via Web Interface (Recommended)

### Test Scenario: Complete Voting Flow

#### Step 1: Create a Voting Event

1. Click on the **"Create Event"** tab
2. Fill in the form:
   - **Event Name:** `2024 Student Council Election`
   - **Start Date:** Choose a past date (e.g., yesterday)
   - **End Date:** Choose a future date (e.g., next week)
   - **Number of Candidates to Vote For:** `1`
   - **Candidates:** Enter one per line:
     ```
     Alice Johnson
     Bob Smith
     Carol Williams
     ```
3. Click **"Create Event"**
4. Wait for ElectionGuard setup (takes 1-2 seconds)
5. You'll see a success message

**What happens behind the scenes:**
- ElectionGuard Manifest is created
- Key ceremony is performed
- Guardian keypair generated
- Cryptographic context stored

#### Step 2: Register as a Voter

1. Click on the **"Register"** tab
2. Enter a unique ID:
   ```
   student123@university.edu
   ```
3. Click **"Register"**
4. **IMPORTANT:** Copy and save your customer secret (64-character hex string)
   - Example: `f5766338ae0abce3f0a1146c5f514a2960323c3b4315a21ada1bebd9d72a3e99`
   - You'll need this to vote!

#### Step 3: View Events

1. Click on the **"Events"** tab
2. You'll see your created event with status badge
3. Click **"View Details →"** to see:
   - Event dates
   - Candidates list
   - Total votes (initially 0)

#### Step 4: Submit a Vote

1. Click on the **"Vote"** tab
2. Paste your **customer secret** from Step 2
3. Select the **event** from the dropdown
4. The candidates will load automatically
5. **Select one candidate** (e.g., Bob Smith)
6. Click **"Submit Vote"**

**What happens:**
- Your ballot is encrypted using ElectionGuard homomorphic encryption
- Zero-knowledge proofs are generated
- Ballot is stored encrypted (never decrypted)
- You receive:
  - **Vote Secret** (64 chars) - for verification
  - **Verification Code** (format: XXXX-XXXX-XXXX-XXXX)

7. **Save both** the vote secret and verification code

#### Step 5: Verify Your Vote

1. Click on the **"Verify Vote"** tab
2. Paste your **vote secret** from Step 4
3. Click **"Verify Vote"**
4. You'll see:
   - Event name
   - Your selected candidate
   - Verification code
   - Counted status

---

## Testing via API (Command Line)

### Test Scenario: Complete Voting Flow via curl

#### 1. Create Event

```bash
curl -X POST http://localhost:8000/app/v1/vote-events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "2024 Student Council Election",
    "from_date": "2024-11-01T00:00:00Z",
    "to_date": "2024-12-01T23:59:59Z",
    "allow_vote_candidate_num": 1,
    "candidate_names": ["Alice Johnson", "Bob Smith", "Carol Williams"]
  }'
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "2024 Student Council Election",
  "from_date": "2024-11-01T00:00:00",
  "to_date": "2024-12-01T23:59:59",
  "status": "INVOTING",
  "allow_vote_candidate_num": 1
}
```

#### 2. Get Event Details (with Candidates)

```bash
curl http://localhost:8000/app/v1/vote-events/1
```

**Expected Response:**
```json
{
  "id": 1,
  "name": "2024 Student Council Election",
  "status": "INVOTING",
  "candidates": [
    {"id": 1, "name": "Alice Johnson", "vote_count": 0},
    {"id": 2, "name": "Bob Smith", "vote_count": 0},
    {"id": 3, "name": "Carol Williams", "vote_count": 0}
  ],
  "total_votes": 0
}
```

#### 3. Register Customer

```bash
curl -X POST http://localhost:8000/app/v1/customers/register \
  -H "Content-Type: application/json" \
  -d '{"unique_id": "student@university.edu"}'
```

**Expected Response:**
```json
{
  "id": 1,
  "unique_id": "student@university.edu",
  "customer_secret": "f5766338ae0abce3f0a1146c5f514a2960323c3b4315a21ada1bebd9d72a3e99"
}
```

**Save the `customer_secret`!**

#### 4. Submit Vote

```bash
# Replace customer_secret with your actual secret from step 3
# Replace candidate ID (2 = Bob Smith in this example)

curl -X POST http://localhost:8000/app/v1/votes/submit \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "customer_secret": "f5766338ae0abce3f0a1146c5f514a2960323c3b4315a21ada1bebd9d72a3e99",
    "selected_candidate_ids": [2]
  }'
```

**Expected Response:**
```json
{
  "vote_secret": "18971f35d223fb79527fb8e025f53b971a375603231db27fb2049d3926e7b44b",
  "verification_code": "27F5-2542-7372-D3C6",
  "message": "Vote submitted successfully. Keep your verification code to verify your vote was counted."
}
```

**Save the `vote_secret`!**

#### 5. Verify Vote

```bash
# Replace vote_secret with your actual secret from step 4

curl -X POST http://localhost:8000/app/v1/votes/verify \
  -H "Content-Type: application/json" \
  -d '{
    "vote_secret": "18971f35d223fb79527fb8e025f53b971a375603231db27fb2049d3926e7b44b"
  }'
```

**Expected Response:**
```json
{
  "event_id": 1,
  "event_name": "2024 Student Council Election",
  "selected_candidates": ["Bob Smith"],
  "verification_code": "27F5-2542-7372-D3C6",
  "is_counted": false
}
```

---

## Testing Multiple Voters

### Simulate 3 Voters Voting for Different Candidates

```bash
# Voter 1: Register and vote for Alice
curl -X POST http://localhost:8000/app/v1/customers/register \
  -H "Content-Type: application/json" \
  -d '{"unique_id": "voter1@test.com"}' | jq -r '.customer_secret' > voter1_secret.txt

VOTER1_SECRET=$(cat voter1_secret.txt)

curl -X POST http://localhost:8000/app/v1/votes/submit \
  -H "Content-Type: application/json" \
  -d "{\"event_id\": 1, \"customer_secret\": \"$VOTER1_SECRET\", \"selected_candidate_ids\": [1]}"

# Voter 2: Register and vote for Bob
curl -X POST http://localhost:8000/app/v1/customers/register \
  -H "Content-Type: application/json" \
  -d '{"unique_id": "voter2@test.com"}' | jq -r '.customer_secret' > voter2_secret.txt

VOTER2_SECRET=$(cat voter2_secret.txt)

curl -X POST http://localhost:8000/app/v1/votes/submit \
  -H "Content-Type: application/json" \
  -d "{\"event_id\": 1, \"customer_secret\": \"$VOTER2_SECRET\", \"selected_candidate_ids\": [2]}"

# Voter 3: Register and vote for Bob
curl -X POST http://localhost:8000/app/v1/customers/register \
  -H "Content-Type: application/json" \
  -d '{"unique_id": "voter3@test.com"}' | jq -r '.customer_secret' > voter3_secret.txt

VOTER3_SECRET=$(cat voter3_secret.txt)

curl -X POST http://localhost:8000/app/v1/votes/submit \
  -H "Content-Type: application/json" \
  -d "{\"event_id\": 1, \"customer_secret\": \"$VOTER3_SECRET\", \"selected_candidate_ids\": [2]}"

# Check event - should show 3 total votes
curl http://localhost:8000/app/v1/vote-events/1 | jq
```

---

## Verification Tests

### 1. Test Duplicate Vote Prevention

```bash
# Try to vote twice with same customer secret
# This should FAIL with error

curl -X POST http://localhost:8000/app/v1/votes/submit \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "customer_secret": "YOUR_SECRET_FROM_STEP_3",
    "selected_candidate_ids": [1]
  }'
```

**Expected:** Error `400 Bad Request` - "Customer has already voted in this event"

### 2. Test Invalid Customer Secret

```bash
curl -X POST http://localhost:8000/app/v1/votes/submit \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "customer_secret": "invalid_secret_123",
    "selected_candidate_ids": [1]
  }'
```

**Expected:** Error `401 Unauthorized` - "Invalid customer secret"

### 3. Test Invalid Candidate Selection

```bash
curl -X POST http://localhost:8000/app/v1/votes/submit \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "customer_secret": "YOUR_VALID_SECRET",
    "selected_candidate_ids": [999]
  }'
```

**Expected:** Error `400 Bad Request` - "Invalid candidate ID: 999"

### 4. Test Vote Verification with Invalid Secret

```bash
curl -X POST http://localhost:8000/app/v1/votes/verify \
  -H "Content-Type: application/json" \
  -d '{"vote_secret": "invalid_vote_secret_123"}'
```

**Expected:** Error `404 Not Found` - "Invalid vote secret"

---

## Checking Logs

### View ElectionGuard Encryption Process

When you submit a vote, you'll see detailed ElectionGuard logs:

```
INFO: Processing vote submission for event 1
INFO: Vote validated for customer 1
INFO: encrypt: objectId: ballot-1-1
INFO: manifest_hash : D6C11AA5C4814EA272937A0B88926864...
INFO: encryption_seed : 5F9C5945137547230E819C21415C96D0...
INFO: encrypt_selection: for candidate-1-0 hash: 969420753B16B53D...
INFO: elgamal_encrypt: publicKey: ADABF0C56211CEE2E689BCFF...
INFO: Vote recorded for customer 1 in event 1
```

This confirms:
- ElectionGuard encryption is working
- Zero-knowledge proofs are generated
- Homomorphic properties preserved

---

## Database Inspection

### Check Database Contents

```bash
# View all events
sqlite3 election_demo.db "SELECT id, name, status, total_votes FROM vote_events;"

# View all candidates
sqlite3 election_demo.db "SELECT id, event_id, name, vote_count FROM candidates;"

# View all customers (WITHOUT secrets for security)
sqlite3 election_demo.db "SELECT id, unique_id, created_at FROM customers;"

# View vote count per event
sqlite3 election_demo.db "SELECT event_id, COUNT(*) as votes FROM customer_votes GROUP BY event_id;"

# Check encrypted ballots are stored
sqlite3 election_demo.db "SELECT id, event_id, customer_id, LENGTH(encrypted_ballot) as ballot_size FROM customer_votes;"
```

---

## Performance Testing

### Test Event Creation Time

```bash
time curl -X POST http://localhost:8000/app/v1/vote-events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Performance Test Event",
    "from_date": "2024-11-01T00:00:00Z",
    "to_date": "2024-12-01T23:59:59Z",
    "allow_vote_candidate_num": 1,
    "candidate_names": ["Candidate A", "Candidate B", "Candidate C"]
  }'
```

**Expected:** 1-2 seconds (includes key ceremony)

### Test Vote Submission Time

```bash
time curl -X POST http://localhost:8000/app/v1/votes/submit \
  -H "Content-Type: application/json" \
  -d '{
    "event_id": 1,
    "customer_secret": "YOUR_SECRET",
    "selected_candidate_ids": [1]
  }'
```

**Expected:** < 1 second (includes ElectionGuard encryption)

---

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Then restart server
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Database Issues

```bash
# Delete and recreate database
rm election_demo.db
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### Module Import Errors

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Verify packages installed
pip list | grep -E "electionguard|fastapi|sqlalchemy"
```

### CORS Errors in Browser

The API allows all origins by default (for development). If you see CORS errors:
1. Check that the server is running on port 8000
2. Clear browser cache
3. Try incognito/private browsing mode

---

## Next Steps

After testing the basic flow:

1. **Test Tally Ceremony** (Phase 6)
   - End voting period
   - Aggregate encrypted ballots
   - Decrypt tally
   - Verify results

2. **Test with Multiple Events**
   - Create multiple concurrent events
   - Test voter participation across events

3. **Test Edge Cases**
   - Event dates (past, future, invalid ranges)
   - Maximum candidates
   - Maximum vote selections
   - Concurrent vote submissions

4. **Security Testing**
   - Test with invalid tokens
   - Test SQL injection attempts
   - Test XSS attempts in event names

---

## API Endpoints Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/app/v1/vote-events` | Create voting event |
| GET | `/app/v1/vote-events` | List all events (paginated) |
| GET | `/app/v1/vote-events/{id}` | Get event details |
| POST | `/app/v1/vote-events/{id}/end-voting` | End voting period |
| POST | `/app/v1/customers/register` | Register customer |
| POST | `/app/v1/votes/submit` | Submit encrypted vote |
| POST | `/app/v1/votes/verify` | Verify vote |

Full API documentation available at: `http://localhost:8000/docs`
