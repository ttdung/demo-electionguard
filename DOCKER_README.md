# Docker Deployment - Quick Start

## 🚀 Quick Start (3 Steps)

### 1. Setup Environment

```bash
# Copy environment template
cp .env.example .env

# (Optional) Edit .env to customize ports
nano .env
```

### 2. Start Application

```bash
# Build and start both containers
docker-compose up -d

# View logs (optional)
docker-compose logs -f
```

### 3. Access Application

- **Frontend:** http://localhost
- **API Docs:** http://localhost/docs
- **Health:** http://localhost/health

That's it! 🎉

---

## 📋 What Gets Created

### Two Docker Containers:

1. **electionguard-api** (FastAPI + ElectionGuard)
   - Port: 8000 (internal)
   - Database: `./data/election_demo.db` (persisted)
   - Environment: From `.env` file

2. **electionguard-frontend** (Nginx)
   - Port: 80 (external, configurable)
   - Serves: `./frontend/index.html`
   - Proxies API requests to backend

### Architecture:
```
Browser → http://localhost:80 → Frontend (Nginx) → API (FastAPI) → Database
                                       ↓
                                  Static HTML
```

---

## ⚙️ Configuration Options

Edit `.env` file to customize:

```bash
# Change frontend port (default: 80)
FRONTEND_PORT=8080

# Change API port (default: 8000, internal)
API_PORT=8000

# Change database location (default: ./data)
DATABASE_PATH=./data
DATABASE_NAME=election_demo.db

# Use custom frontend files
FRONTEND_PATH=./custom-frontend

# Debug mode
DEBUG=false
LOG_LEVEL=INFO
```

After changing `.env`:
```bash
docker-compose down
docker-compose up -d
```

---

## 🛠️ Common Commands

### Start/Stop

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart
```

### Logs

```bash
# View all logs
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# API logs only
docker-compose logs -f api

# Frontend logs only
docker-compose logs -f frontend
```

### Status

```bash
# Check status
docker-compose ps

# Check health
curl http://localhost/health
```

### Rebuild

```bash
# Rebuild after code changes
docker-compose build
docker-compose up -d

# Force rebuild (no cache)
docker-compose build --no-cache
docker-compose up -d
```

---

## 🗄️ Database Management

### Backup Database

```bash
# Database is in ./data/election_demo.db
cp ./data/election_demo.db ./data/backup_$(date +%Y%m%d).db
```

### Reset Database

```bash
docker-compose down
rm ./data/election_demo.db
docker-compose up -d
```

### Change Database Location

```bash
# Edit .env
DATABASE_PATH=/path/to/your/data
```

---

## 🧪 Testing

Once containers are running, test the complete workflow:

### Option 1: Web Interface
1. Open http://localhost
2. Go to "Create Event" tab
3. Create an event
4. Go to "Register" tab and register
5. Go to "Vote" tab and submit a vote
6. Go to "Verify Vote" tab to verify

### Option 2: API Testing

```bash
# Health check
curl http://localhost/health

# Create event
curl -X POST http://localhost/app/v1/vote-events \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Election",
    "from_date": "2024-11-01T00:00:00Z",
    "to_date": "2024-12-01T23:59:59Z",
    "allow_vote_candidate_num": 1,
    "candidate_names": ["Alice", "Bob", "Carol"]
  }'

# View API docs
open http://localhost/docs
```

---

## 🐛 Troubleshooting

### Port 80 already in use

```bash
# Option 1: Change port in .env
FRONTEND_PORT=8080

# Option 2: Kill process using port 80
lsof -ti:80 | xargs kill -9
```

### Container won't start

```bash
# Check logs
docker-compose logs

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Can't connect to API

```bash
# Check both containers are running
docker-compose ps

# Both should show "healthy" status
# If not, check logs:
docker-compose logs api
docker-compose logs frontend
```

### Reset everything

```bash
# Stop and remove everything (including database!)
docker-compose down -v

# Rebuild and start fresh
docker-compose build --no-cache
docker-compose up -d
```

---

## 📚 Full Documentation

For detailed documentation, see:
- **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** - Complete Docker reference
- **[TESTING_GUIDE.md](TESTING_GUIDE.md)** - Testing procedures
- **[.env.example](.env.example)** - Configuration options

---

## 🔒 Production Deployment

For production use:

1. **Set secure environment**
   ```bash
   DEBUG=false
   CORS_ORIGINS=https://yourdomain.com
   ```

2. **Use HTTPS** (add reverse proxy like Caddy/Traefik)

3. **Backup database regularly**

4. **Monitor logs**
   ```bash
   docker-compose logs -f --tail=100
   ```

5. **Keep updated**
   ```bash
   git pull
   docker-compose build --no-cache
   docker-compose up -d
   ```

See [DOCKER_GUIDE.md](DOCKER_GUIDE.md) for production best practices.

---

## 📞 Support

- GitHub Issues: [Report issues](https://github.com/anthropics/claude-code/issues)
- Documentation: See `DOCKER_GUIDE.md` and `TESTING_GUIDE.md`
- Logs: `docker-compose logs -f`
