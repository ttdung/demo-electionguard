# ElectionGuard Demo - Implementation Task List

**Project**: ElectionGuard Voting Demo with FastAPI
**Status**: In Progress
**Last Updated**: 2025-11-13

---

## Progress Overview

- [x] Phase 0: Planning & Documentation
- [ ] Phase 1: Project Setup
- [ ] Phase 2: Database Layer
- [ ] Phase 3: ElectionGuard Service
- [ ] Phase 4: API Implementation
- [ ] Phase 5: Frontend
- [ ] Phase 6: Testing & Documentation

---

## Phase 0: Planning & Documentation ✅

- [x] Review original requirements
- [x] Read ElectionGuard business terms documentation
- [x] Read ElectionGuard technical workflow documentation
- [x] Read FastAPI best practices
- [x] Create comprehensive requirements-v2.md with:
  - [x] System architecture diagrams
  - [x] User flows and scenarios
  - [x] API specifications with examples
  - [x] Database schema design
  - [x] Frontend specifications
  - [x] Success criteria and test scenarios
- [x] Create task list file for session continuity

---

## Phase 1: Project Setup

### 1.1 Python Project Initialization
- [ ] Create `.env` file from `.env.example`
- [ ] Initialize uv project: `uv init` (if needed)
- [ ] Install dependencies: `uv sync`
- [ ] Verify ElectionGuard SDK installation
- [ ] Test basic imports

**Files to verify**:
- `pyproject.toml` ✅ (already created)
- `.env.example` ✅ (already created)
- `.gitignore` ✅ (already created)
- `.env` (to create from example)

### 1.2 Project Structure
Create the following directory structure:
```
src/
├── __init__.py ✅
├── main.py
├── config.py ✅
├── database.py ✅
├── logging_config.py ✅
├── models.py
├── schemas.py
├── exceptions.py
├── vote_events/
│   ├── __init__.py
│   ├── router.py
│   ├── service.py
│   └── schemas.py
├── customers/
│   ├── __init__.py
│   ├── router.py
│   ├── service.py
│   └── schemas.py
├── votes/
│   ├── __init__.py
│   ├── router.py
│   ├── service.py
│   └── schemas.py
└── electionguard_service/
    ├── __init__.py
    ├── manifest_builder.py
    ├── key_ceremony.py
    ├── ballot_encryptor.py
    └── tally_ceremony.py
```

**Tasks**:
- [ ] Create main.py with FastAPI app initialization
- [ ] Create domain folders (vote_events, customers, votes)
- [ ] Create electionguard_service module
- [ ] Create __init__.py files for all packages

---

## Phase 2: Database Layer

### 2.1 Database Models
- [ ] Complete `src/models.py` with SQLAlchemy models:
  - [ ] VoteEvent model
  - [ ] Candidate model
  - [ ] Customer model
  - [ ] CustomerVote model
  - [ ] Add proper indexes and constraints
  - [ ] Add relationships between models

### 2.2 Pydantic Schemas
- [ ] Create `src/schemas.py` with base schemas:
  - [ ] Custom BaseModel with common config
  - [ ] EventStatus enum
  - [ ] Common response models

- [ ] Create `src/vote_events/schemas.py`:
  - [ ] CreateVoteEventRequest
  - [ ] VoteEventResponse
  - [ ] CandidateResponse
  - [ ] TallyResponse
  - [ ] VoteStatisticResponse

- [ ] Create `src/customers/schemas.py`:
  - [ ] CreateCustomerRequest
  - [ ] CustomerResponse

- [ ] Create `src/votes/schemas.py`:
  - [ ] CastVoteRequest
  - [ ] CastVoteResponse
  - [ ] VerifyVoteResponse
  - [ ] SelectedCandidateRequest

### 2.3 Database Initialization
- [ ] Create database init script
- [ ] Test database creation
- [ ] Add sample data seed script (optional for testing)

---

## Phase 3: ElectionGuard Service Layer

### 3.1 Manifest Builder
File: `src/electionguard_service/manifest_builder.py`

- [ ] Create function to build ElectionGuard Manifest from event
- [ ] Define geopolitical unit
- [ ] Create contest with candidates
- [ ] Create ballot style
- [ ] Return complete Manifest object
- [ ] Add logging for manifest creation

### 3.2 Key Ceremony
File: `src/electionguard_service/key_ceremony.py`

- [ ] Implement simplified key ceremony (single guardian for MVP)
- [ ] Generate guardian keypair
- [ ] Create CeremonyDetails
- [ ] Generate joint election key
- [ ] Create CryptoContext
- [ ] Return public key and context
- [ ] Add logging for key ceremony steps

### 3.3 Ballot Encryptor
File: `src/electionguard_service/ballot_encryptor.py`

- [ ] Create PlaintextBallot from customer selections
- [ ] Implement ballot encryption using joint public key
- [ ] Generate CiphertextBallot
- [ ] Create zero-knowledge proofs (Chaum-Pedersen)
- [ ] Generate verification code (ballot hash)
- [ ] Return encrypted ballot, proofs, and verification code
- [ ] Add comprehensive logging for encryption steps

### 3.4 Tally Ceremony
File: `src/electionguard_service/tally_ceremony.py`

- [ ] Implement homomorphic ballot aggregation
- [ ] Create encrypted tally from all cast ballots
- [ ] Perform tally ceremony (decryption)
- [ ] Generate partial decryptions (guardian)
- [ ] Combine partial decryptions to plaintext tally
- [ ] Extract vote counts per candidate
- [ ] Add logging for tally process

### 3.5 Integration & Testing
- [ ] Create unit tests for manifest builder
- [ ] Create unit tests for key ceremony
- [ ] Create unit tests for ballot encryption
- [ ] Create unit tests for tally ceremony
- [ ] Test complete ElectionGuard flow end-to-end

---

## Phase 4: API Implementation

### 4.1 Exception Handling
File: `src/exceptions.py`

- [ ] Create base DomainException
- [ ] Create specific exceptions:
  - [ ] EventNotFoundException
  - [ ] CustomerNotFoundException
  - [ ] InvalidCustomerSecretException
  - [ ] AlreadyVotedException
  - [ ] InvalidSelectionCountException
  - [ ] EventNotActiveException
  - [ ] VoteNotFoundException
- [ ] Create global exception handlers in main.py

### 4.2 Vote Events Module
Files: `src/vote_events/`

- [ ] **router.py**: Create API endpoints
  - [ ] POST /vote-events (create event)
  - [ ] POST /execute-tally-election/:event_id (tally)
  - [ ] GET /vote_events/:event_id (get results)

- [ ] **service.py**: Business logic
  - [ ] create_vote_event():
    - [ ] Validate input
    - [ ] Create ElectionGuard manifest
    - [ ] Perform key ceremony
    - [ ] Save event to database
    - [ ] Create candidates
    - [ ] Log operation
  - [ ] execute_tally():
    - [ ] Validate event exists
    - [ ] Update status to TALLING
    - [ ] Fetch all encrypted ballots
    - [ ] Call ElectionGuard tally service
    - [ ] Calculate statistics and winner
    - [ ] Update event with results
    - [ ] Update status to END
    - [ ] Log operation
  - [ ] get_event_results():
    - [ ] Fetch event with candidates
    - [ ] Format response with statistics
    - [ ] Return results

### 4.3 Customers Module
Files: `src/customers/`

- [ ] **router.py**: Create API endpoints
  - [ ] POST /gen-customer-fake-token (register customer)

- [ ] **service.py**: Business logic
  - [ ] create_customer():
    - [ ] Validate unique_id is unique
    - [ ] Generate UUID as customer_secret
    - [ ] Save to database
    - [ ] Return customer with secret

### 4.4 Votes Module
Files: `src/votes/`

- [ ] **router.py**: Create API endpoints
  - [ ] POST /customer-vote (cast vote)
  - [ ] POST /verify-customer-vote/:vote_secret (verify vote)

- [ ] **service.py**: Business logic
  - [ ] cast_vote():
    - [ ] Validate customer_secret (authentication)
    - [ ] Validate event exists and status is INVOTING
    - [ ] Validate event is within date range
    - [ ] Validate candidates belong to event
    - [ ] Validate selection count matches allow_vote_candidate_num
    - [ ] Check idempotency (customer hasn't voted)
    - [ ] Create plaintext ballot from selections
    - [ ] Call ElectionGuard encryption service
    - [ ] Save encrypted ballot to database
    - [ ] Log operation
    - [ ] Return vote_secret and details
  - [ ] verify_vote():
    - [ ] Lookup vote by vote_secret
    - [ ] Join with customer and event data
    - [ ] Parse selected candidates
    - [ ] Return vote details

### 4.5 Main Application
File: `src/main.py`

- [ ] Initialize FastAPI app
- [ ] Configure CORS middleware
- [ ] Add request ID middleware
- [ ] Set up logging
- [ ] Register exception handlers
- [ ] Include routers with API prefix
- [ ] Add startup event for database init
- [ ] Add health check endpoint
- [ ] Configure static files (for frontend)

### 4.6 Dependencies
- [ ] Create dependency for database session (already in database.py)
- [ ] Create dependency for ElectionGuard services
- [ ] Add request logging middleware

---

## Phase 5: Frontend Development

### 5.1 HTML Structure
File: `frontend/index.html`

- [ ] Create HTML boilerplate
- [ ] Add meta tags and title
- [ ] Include Tailwind CSS or shadcn UI via CDN
- [ ] Create main layout container
- [ ] Add section for event creation
- [ ] Add two-column layout for voting and results
- [ ] Add footer with attribution

### 5.2 Section 1: Create Event
- [ ] Create event form with inputs:
  - [ ] Event name input
  - [ ] From date/time input
  - [ ] To date/time input
  - [ ] Candidates list with add/remove
  - [ ] Allow vote candidate number input
  - [ ] Submit button
- [ ] Add form validation
- [ ] Implement API call to POST /vote-events
- [ ] Display created event details
- [ ] Handle errors and show messages

### 5.3 Section 2.1: Create Customer
- [ ] Create customer form:
  - [ ] Unique ID input
  - [ ] Create button
- [ ] Implement API call to POST /gen-customer-fake-token
- [ ] Add row to customers table
- [ ] Display customer secret (for testing)
- [ ] Handle errors

### 5.4 Section 2.2: Cast Vote
- [ ] Create vote form:
  - [ ] Customer dropdown (populated from table)
  - [ ] Candidate multi-select (from event)
  - [ ] Vote button
- [ ] Implement API call to POST /customer-vote
- [ ] Add row to customer votes table
- [ ] Display vote_secret
- [ ] Handle errors and validation

### 5.5 Section 2.3: Customer Votes Table
- [ ] Create table with columns:
  - [ ] Customer name
  - [ ] Selected candidates
  - [ ] Verify button
- [ ] Implement verify button click handler
- [ ] Call API POST /verify-customer-vote/:vote_secret
- [ ] Display vote details in modal or alert
- [ ] Handle errors

### 5.6 Section 3: Vote Results
- [ ] Create tally button
- [ ] Implement API call to POST /execute-tally-election
- [ ] Create refresh button
- [ ] Implement API call to GET /vote_events/:event_id
- [ ] Display winner section with highlight
- [ ] Create statistics table:
  - [ ] Candidate name
  - [ ] Vote count
  - [ ] Percentage
- [ ] Sort by vote count descending
- [ ] Handle loading states
- [ ] Handle errors

### 5.7 JavaScript Implementation
- [ ] Create API client functions (fetch wrapper)
- [ ] Implement state management (simple object)
- [ ] Add loading spinners for async operations
- [ ] Add toast/notification system for feedback
- [ ] Implement form validation
- [ ] Add error handling and display
- [ ] Test all user interactions

### 5.8 Styling
- [ ] Apply consistent styling with Tailwind/shadcn
- [ ] Make responsive (mobile-friendly)
- [ ] Add button states (hover, active, disabled)
- [ ] Style tables
- [ ] Style forms
- [ ] Add loading states
- [ ] Polish winner section (highlight/card)

---

## Phase 6: Testing & Documentation

### 6.1 Backend Testing
- [ ] Test API endpoint: Create vote event
- [ ] Test API endpoint: Generate customer token
- [ ] Test API endpoint: Cast vote
- [ ] Test API endpoint: Verify vote
- [ ] Test API endpoint: Execute tally
- [ ] Test API endpoint: Get event results
- [ ] Test idempotency (duplicate vote)
- [ ] Test validation errors
- [ ] Test event date range validation
- [ ] Test candidate selection validation
- [ ] Test tally accuracy with multiple votes
- [ ] Test ElectionGuard integration logging

### 6.2 Integration Testing
- [ ] Run complete voting flow (Test Scenario 1)
- [ ] Test idempotency protection (Test Scenario 2)
- [ ] Test event time validation (Test Scenario 3)
- [ ] Test candidate selection validation (Test Scenario 4)
- [ ] Test invalid customer secret (Test Scenario 5)
- [ ] Test vote verification (Test Scenario 6)
- [ ] Test tally accuracy (Test Scenario 7)
- [ ] Test ElectionGuard encryption (Test Scenario 8)

### 6.3 Frontend Testing
- [ ] Test create event form
- [ ] Test create customer form
- [ ] Test cast vote form
- [ ] Test verify button functionality
- [ ] Test tally button
- [ ] Test refresh button
- [ ] Test error message display
- [ ] Test loading states
- [ ] Test responsive design
- [ ] Cross-browser testing (Chrome, Firefox, Safari)

### 6.4 Documentation
- [ ] Create README.md with:
  - [ ] Project overview
  - [ ] Installation instructions
  - [ ] Running the application
  - [ ] API documentation reference
  - [ ] Testing guide
- [ ] Create SETUP.md with detailed setup steps
- [ ] Create API_GUIDE.md with curl examples
- [ ] Add code comments for complex logic
- [ ] Document ElectionGuard integration points
- [ ] Create troubleshooting guide

### 6.5 Deployment Preparation (Optional)
- [ ] Create requirements.txt (if not using uv)
- [ ] Create Dockerfile (optional)
- [ ] Create docker-compose.yml (optional)
- [ ] Add production configuration
- [ ] Add health check endpoint
- [ ] Configure logging for production
- [ ] Security audit (input validation, secrets)

---

## Current Session Progress

**Phase**: 0 - Planning & Documentation ✅
**Next Phase**: 1 - Project Setup
**Next Task**: Initialize uv project and install dependencies

**Files Created This Session**:
- [x] pyproject.toml
- [x] .env.example
- [x] .gitignore
- [x] src/config.py
- [x] src/database.py
- [x] src/logging_config.py
- [x] docs/requirements-v2.md
- [x] docs/TASK_LIST.md

**Ready to Start**: Phase 1 - Project Setup

---

## Notes for Next Session

### Quick Start Commands
```bash
# Install dependencies
uv sync

# Copy environment file
cp .env.example .env

# Run development server
uv run uvicorn src.main:app --reload

# Run tests
uv run pytest
```

### Key Context
- Using ElectionGuard SDK for cryptographic operations
- FastAPI with async/await pattern
- SQLite for MVP (easy setup, no external dependencies)
- Single guardian setup (simplified key ceremony)
- Single HTML frontend with CDN dependencies

### Important References
- Requirements: `docs/requirements-v2.md`
- ElectionGuard docs: `docs/election-guard--business-terms.md`, `docs/election-guard--how-vote-work.md`
- FastAPI best practices: `docs/fast-api-best-practices.md`

### Session Continuity
To continue from where you left off:
1. Check this task list for current phase
2. Review "Current Session Progress" section
3. Start with next unchecked task in current phase
4. Update checkboxes as you complete tasks
5. Update "Current Session Progress" when moving to new phase

---

**Last Updated**: 2025-11-13
**Total Tasks**: ~150+
**Completed**: ~15 (Phase 0)
**Remaining**: ~135+
