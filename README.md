# ElectionGuard Voting Demo

A complete web-based demonstration application showcasing ElectionGuard's end-to-end verifiable voting technology with an event-centric interface.

## 🌟 Features

### **Core Voting Features**
- ✅ Create and manage voting events with multiple candidates
- ✅ Event-specific voter registration
- ✅ Homomorphic encryption using ElectionGuard
- ✅ End-to-end verifiable voting
- ✅ Two-level vote decoding (public vs authenticated)
- ✅ Real-time tally computation
- ✅ Comprehensive vote tracking and audit trail

### **Security & Privacy**
- **Encrypted Ballots**: All votes are homomorphically encrypted using ElectionGuard
- **Zero-Knowledge Proofs**: Cryptographic proofs ensure vote validity without revealing content
- **Two-Level Verification**:
  - **Level 1 (Public)**: Verification code → See what was voted for
  - **Level 2 (Authenticated)**: Verification code + vote secret → See who voted
- **Masked Secrets**: All sensitive tokens are blurred by default

### **User Interface**
- **Event-Centric Workflow**: All voting activities organized by event
- **Real-Time Updates**: Tables auto-refresh after actions
- **Inline Decode**: Vote details expand within table rows
- **Responsive Design**: Works on desktop and mobile devices

## 📋 Requirements

- **Python 3.10.x** (Required - ElectionGuard 1.4.0 is not compatible with Python 3.11+)
- **Docker & Docker Compose** (for containerized deployment)
- **uv package manager** (recommended) or pip

## 🚀 Quick Start

### Option 1: Docker Deployment (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd demo-electionguard

# Copy environment file
cp .env.example .env

# Start with Docker Compose
docker-compose up --build -d

# Check container status
docker ps

# View logs
docker logs electionguard-api
docker logs electionguard-frontend
```

**Access the application:**
- **Frontend**: http://localhost:8089
- **API**: http://localhost:8088
- **API Documentation**: http://localhost:8089/docs

# Sample input
seal: 73c457ba10a3ca651f6d58af20241ac344ae75a4c85d29db862ecf36d8f419a16d2efd711c8f382af116509c9f334f622ebc206f8c8254d8529ec8cf12a598b6b7a3f9eb0f1eef2699d7079614efbef31d95cae4793909ef4ea90b74bfc7759a170cae7d2327c229d5e4f94c94f5c4de2371c9d26c93b682d2502ed86c10f9403af3c2092b621cdd802d4bf42a9e0f3db98c243743c11b9e2fe3f4bd7c44a48545b3feff2cf26b2ca7eca2b5b3777ce21b50b9b6f20e2b546914ca5f7ebfee50c3d0c4a7132368a23f4155e5a7aec6abcd61e3a26a3722c6f31e19adfb582ba2d081d00e0137d0aefefe6b68c7630d4f4564517cf151f5b2d57a42042051337250499738

journal:
000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000654000000000000000396139646530323734333434313164353865353235353264643362663731633262373562323735303332363332393339363237616664383565343031306238341e00000001e90300000000000000000000000000000100000000000000000000000000000000000000000000000000000000000000000000

journal_abi:
4000000000000000396139646530323734333434313164353865353235353264643362663731633262373562323735303332363332393339363237616664383565343031306238341e00000001e90300000000000000000000000000000100000000000000

image_id:
43706d1c05d8ab2375026a165aca9e5d2cf2123ff77a40438580c47e6f968861

### Option 2: Local Development

```bash
# Create virtual environment with Python 3.10
python3.10 -m venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install uv (fast Python package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install -e .

# Copy environment file
cp .env.example .env

# Run development server
python -m uvicorn src.main:app --reload

# Visit
http://localhost:8000
```

## 🐳 Docker Configuration

### Port Configuration

Default ports (can be customized via `.env`):
- **API Server**: `8088` (maps to container port 8000)
- **Frontend**: `8089` (maps to container port 80)

To use custom ports, create a `.env` file:
```bash
API_PORT=8088
FRONTEND_PORT=8089
```

### Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild after code changes
docker-compose up --build -d

# View logs
docker-compose logs -f

# View API logs only
docker logs -f electionguard-api

# View frontend logs only
docker logs -f electionguard-frontend

# Check health status
docker ps
```

### Volume Mounts

- **Database**: `./data` → `/app/data` (persists vote data)
- **Frontend**: `./frontend` → `/usr/share/nginx/html` (hot-reload frontend changes)
- **Nginx Config**: `./nginx.conf` → `/etc/nginx/conf.d/default.conf`

## 📁 Project Structure

```
demo-electionguard/
├── src/
│   ├── main.py                      # FastAPI application entry point
│   ├── config.py                    # Configuration management
│   ├── database.py                  # Database setup & initialization
│   ├── models.py                    # SQLAlchemy models
│   ├── exceptions.py                # Custom exceptions
│   │
│   ├── api/                         # API endpoints
│   │   ├── vote_events.py           # Event management & tally endpoints
│   │   ├── customers.py             # Customer registration endpoints
│   │   └── votes.py                 # Vote submission & verification endpoints
│   │
│   ├── schemas/                     # Pydantic schemas
│   │   ├── vote_events.py           # Event & tally schemas
│   │   ├── customers.py             # Customer & registration schemas
│   │   ├── votes.py                 # Vote & decode schemas
│   │   └── common.py                # Shared schemas
│   │
│   ├── services/                    # Business logic layer
│   │   ├── vote_events_service.py   # Event & tally operations
│   │   ├── customers_service.py     # Customer management
│   │   └── votes_service.py         # Vote processing
│   │
│   └── electionguard_service/       # ElectionGuard integration
│       ├── manifest_builder.py      # Election manifest creation
│       ├── key_ceremony.py          # Guardian key generation
│       ├── ballot_encryptor.py      # Vote encryption
│       └── tally_ceremony.py        # Homomorphic tally & decryption
│
├── frontend/
│   └── index.html                   # Event-centric single-page app
│
├── docker-compose.yml               # Docker orchestration
├── Dockerfile                       # API container definition
├── Dockerfile.frontend              # Frontend container definition
├── nginx.conf                       # Nginx reverse proxy config
├── docker-entrypoint.sh             # Database initialization script
│
├── .env.example                     # Environment template
├── .gitignore                       # Git ignore rules
├── pyproject.toml                   # Python dependencies (uv)
├── uv.lock                          # Locked dependency versions
└── README.md                        # This file
```

## 🎯 Usage Guide

### 1. Create a Voting Event

1. Navigate to the **"Create Event"** tab
2. Fill in event details:
   - Event name (e.g., "2024 Student Council Election")
   - Start and end dates
   - Number of candidates voters can select
   - Comma-separated candidate names
3. Click **"Create Event"**

The system automatically:
- Creates the ElectionGuard election manifest
- Performs the guardian key ceremony
- Generates encryption keys
- Initializes the cryptographic context

### 2. Register Voters

1. Click on an event from the **"Events List"**
2. In the **"Register Voter"** section:
   - Enter unique ID (email or student ID)
   - Click **"Register"**
3. Save the generated **customer secret** (needed for voting)

**Customer Table** shows:
- Customer ID
- Customer Secret (masked, click eye icon to reveal)
- Registration Date
- Voting Status (Voted / Not Voted)

### 3. Submit Votes

In the **"Submit Vote"** section:
1. Enter your **customer secret**
2. Select candidates (max limit enforced)
3. Click **"Submit Vote"**
4. Save your **verification code** and **vote secret**

The vote is:
- Encrypted using ElectionGuard
- Proven valid with zero-knowledge proofs
- Given a unique verification code

### 4. Decode Votes

In the **"Votes Cast"** table, each vote has two decode buttons:

**"Detail" (Level 1 - Public)**
- Uses verification code only
- Shows: Event name, vote time, selected candidates
- Click again to collapse

**"Full Vote Info" (Level 2 - Authenticated)**
- Uses verification code + vote secret
- Shows: All Level 1 info + voter identity
- Demonstrates voter can prove their vote

### 5. Tally Results

1. Click **"Tally Now"** to compute results
   - Performs homomorphic aggregation of encrypted ballots
   - Decrypts only the aggregated tally (not individual votes)
   - Updates candidate vote counts and percentages

2. View results in the **"Tally Results"** section

**Note**: You can tally votes without ending the event!

## 🔧 API Endpoints

### Vote Events
```
POST   /app/v1/vote-events                          # Create event
GET    /app/v1/vote-events                          # List events
GET    /app/v1/vote-events/{event_id}               # Get event details
POST   /app/v1/vote-events/{event_id}/end-voting    # End voting
POST   /app/v1/vote-events/{event_id}/tally         # Execute tally
```

### Customer Registration
```
POST   /app/v1/vote-events/{event_id}/customers/register    # Register for event
GET    /app/v1/vote-events/{event_id}/customers             # List event customers
POST   /app/v1/customers/register                           # Global registration (deprecated)
```

### Voting
```
POST   /app/v1/votes/submit       # Submit encrypted vote
POST   /app/v1/votes/verify       # Verify vote with secret
POST   /app/v1/votes/decode       # Decode vote (2 levels)
GET    /app/v1/vote-events/{event_id}/votes    # List event votes
```

### Health & Docs
```
GET    /health                    # Health check
GET    /docs                      # Interactive API documentation
GET    /openapi.json              # OpenAPI schema
```

## 🗄️ Database Schema

**VoteEvent** - Voting events
- Event details (name, dates, status)
- ElectionGuard manifest, keys, context
- Tally results (encrypted & plaintext)

**Candidate** - Event candidates
- Name, vote count, percentage
- Links to event

**Customer** - Registered voters
- Unique ID, customer secret
- Global across events

**EventCustomer** - Event-specific registrations
- Links customers to specific events
- Registration timestamp

**CustomerVote** - Encrypted ballots
- Encrypted ballot & proofs
- Verification code & vote secret
- Selected candidates (for verification)
- Links to event & customer

## 🛠️ Development

### Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_vote_events.py
```

### Database Migrations

The database is automatically initialized on startup. To reset:

```bash
# Local development
rm election_demo.db

# Docker
docker-compose down -v
docker-compose up -d
```

### Hot Reload

**Local Development:**
- API auto-reloads on code changes (uvicorn --reload)
- Frontend reloads on browser refresh

**Docker:**
- API: Requires container rebuild (`docker-compose up --build -d`)
- Frontend: Hot-reloads via volume mount (just edit `frontend/index.html`)

## 🔐 Security Considerations

### For Production Use

1. **Change default secrets**: Generate unique guardian keys per event
2. **Use HTTPS**: Enable SSL/TLS for all communications
3. **Restrict CORS**: Set specific allowed origins
4. **Add authentication**: Implement proper user authentication
5. **Secure database**: Use PostgreSQL with encryption
6. **Rate limiting**: Add API rate limits
7. **Input validation**: Enhanced validation on all inputs
8. **Audit logging**: Log all sensitive operations
9. **Key management**: Use hardware security modules (HSMs) for guardian keys

### Current Security Features

- ✅ Homomorphic encryption (ElectionGuard)
- ✅ Zero-knowledge proofs
- ✅ Vote verification without revealing content
- ✅ Masked secrets in UI
- ✅ Event-specific voter registration
- ⚠️ Single guardian (use 3-5 guardians in production)
- ⚠️ SQLite (use PostgreSQL in production)
- ⚠️ No authentication (add OAuth2/JWT in production)

## 📚 ElectionGuard Resources

- [ElectionGuard Official Website](https://www.electionguard.vote/)
- [ElectionGuard Python SDK](https://github.com/microsoft/electionguard-python)
- [ElectionGuard Specification](https://www.electionguard.vote/spec/)

## 🐛 Troubleshooting

### Docker Issues

**Containers not starting:**
```bash
# Check logs
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose up --build
```

**Port already in use:**
```bash
# Change ports in .env
API_PORT=9088
FRONTEND_PORT=9089

# Restart
docker-compose down
docker-compose up -d
```

**Database not initialized:**
```bash
# Check API logs
docker logs electionguard-api | grep "Database"

# Should see: "Database tables created successfully"
```

### Local Development Issues

**ImportError for ElectionGuard:**
```bash
# Ensure Python 3.10.x
python --version

# Reinstall dependencies
uv pip install --force-reinstall electionguard
```

**Database errors:**
```bash
# Remove and recreate
rm election_demo.db
python -m uvicorn src.main:app --reload
```

## 📝 License

MIT License - For demonstration and educational purposes

## 🙏 Acknowledgments

- Microsoft ElectionGuard Team
- FastAPI Framework
- Tailwind CSS
- Docker Community
