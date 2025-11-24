# Docker Deployment Guide

## Overview

This guide explains how to deploy the ElectionGuard Voting Demo using Docker Compose with two containers:
1. **API Server** - FastAPI backend with ElectionGuard
2. **Frontend Server** - Nginx serving the HTML interface

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Quick Start

### 1. Create Environment File

Copy the example environment file and customize it:

```bash
cp .env.example .env
```

Edit `.env` to configure ports and paths (see Configuration section below).

### 2. Start the Application

```bash
# Build and start both containers
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 3. Access the Application

- **Frontend:** http://localhost (or configured FRONTEND_PORT)
- **API Docs:** http://localhost/docs
- **Health Check:** http://localhost/health

### 4. Stop the Application

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (deletes database!)
docker-compose down -v
```

---

## Configuration

### Environment Variables (.env)

All configuration is done via the `.env` file:

```bash
# ===========================================
# Port Configuration
# ===========================================

# API server port (default: 8000)
API_PORT=8000

# Frontend server port (default: 80)
FRONTEND_PORT=80

# ===========================================
# Database Configuration
# ===========================================

# Host path for database storage (default: ./data)
DATABASE_PATH=./data

# Database filename (default: election_demo.db)
DATABASE_NAME=election_demo.db

# ===========================================
# Frontend Configuration
# ===========================================

# Host path to frontend files (default: ./frontend)
FRONTEND_PATH=./frontend

# Custom nginx config (optional, default: ./nginx.conf)
NGINX_CONFIG_PATH=./nginx.conf

# ===========================================
# Application Settings
# ===========================================

# Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Debug mode (default: false)
DEBUG=false

# CORS origins (* for development, specific domains for production)
CORS_ORIGINS=*
```

### Common Configurations

#### Development Setup (Default)

```bash
API_PORT=8000
FRONTEND_PORT=80
DATABASE_PATH=./data
DEBUG=false
```

Access: http://localhost

#### Custom Ports

```bash
API_PORT=3000
FRONTEND_PORT=8080
```

Access: http://localhost:8080

#### Custom Database Location

```bash
# Store database in /var/data
DATABASE_PATH=/var/data
DATABASE_NAME=my_election.db
```

#### Custom Frontend Location

```bash
# Serve frontend from different directory
FRONTEND_PATH=/path/to/custom/frontend
```

---

## Volume Mounts

### API Container Volumes

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `${DATABASE_PATH}` | `/app/data` | SQLite database storage |
| `./.env` | `/app/.env` | Environment configuration (read-only) |

### Frontend Container Volumes

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `${FRONTEND_PATH}` | `/usr/share/nginx/html` | HTML files (read-only) |
| `${NGINX_CONFIG_PATH}` | `/etc/nginx/conf.d/default.conf` | Nginx config (read-only) |

---

## Docker Commands

### Building

```bash
# Build both containers
docker-compose build

# Build specific container
docker-compose build api
docker-compose build frontend

# Force rebuild (no cache)
docker-compose build --no-cache
```

### Running

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background (detached)
docker-compose up -d

# Start specific service
docker-compose up -d api
docker-compose up -d frontend

# Restart services
docker-compose restart
docker-compose restart api
```

### Logs

```bash
# View all logs
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# View specific service logs
docker-compose logs api
docker-compose logs frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Status and Inspection

```bash
# Check status
docker-compose ps

# View resource usage
docker stats

# Inspect container
docker inspect electionguard-api
docker inspect electionguard-frontend

# Execute command in container
docker-compose exec api bash
docker-compose exec frontend sh
```

### Cleanup

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (WARNING: deletes data!)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Full cleanup
docker-compose down -v --rmi all --remove-orphans
```

---

## Database Management

### Backup Database

```bash
# From host (if using default ./data path)
cp ./data/election_demo.db ./data/election_demo.db.backup

# From running container
docker-compose exec api cp /app/data/election_demo.db /app/data/backup.db
docker cp electionguard-api:/app/data/backup.db ./election_demo.db.backup
```

### Restore Database

```bash
# Stop services
docker-compose down

# Restore file
cp ./election_demo.db.backup ./data/election_demo.db

# Start services
docker-compose up -d
```

### Reset Database

```bash
# Stop services
docker-compose down

# Delete database
rm ./data/election_demo.db

# Start services (will create new database)
docker-compose up -d
```

---

## Custom Frontend

To use a custom frontend:

1. Create your custom HTML files in a directory (e.g., `./custom-frontend/`)
2. Update `.env`:
   ```bash
   FRONTEND_PATH=./custom-frontend
   ```
3. Restart:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

The frontend must make API calls to the relative paths (e.g., `/app/v1/vote-events`) as nginx proxies them to the API container.

---

## Custom Nginx Configuration

To customize nginx settings:

1. Edit `nginx.conf`
2. Restart frontend container:
   ```bash
   docker-compose restart frontend
   ```

Or use a different config file:

```bash
# .env
NGINX_CONFIG_PATH=./my-custom-nginx.conf
```

---

## Networking

### Container Communication

Both containers are on the same Docker network (`electionguard-network`):
- Frontend can reach API at `http://api:8000`
- API is isolated from external access (only accessible via frontend proxy)

### Port Mapping

```
Host:FRONTEND_PORT → Frontend Container:80 → Proxy → API Container:8000
```

### Access Patterns

- **Browser** → http://localhost:80 → **Frontend Container**
- **Browser** → http://localhost:80/app/v1/* → **Frontend** (nginx) → **API Container**
- **API Container** is NOT directly accessible from host (by design)

---

## Health Checks

Both containers include health checks:

### API Health Check
```bash
# Inside container
python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# From host (through frontend proxy)
curl http://localhost/health
```

### Frontend Health Check
```bash
# Inside container
wget --quiet --tries=1 --spider http://localhost:80/

# From host
curl http://localhost/
```

View health status:
```bash
docker-compose ps
```

---

## Troubleshooting

### Port Already in Use

```bash
# Check what's using the port
lsof -ti:80    # Frontend
lsof -ti:8000  # API

# Kill process
lsof -ti:80 | xargs kill -9

# Or change port in .env
FRONTEND_PORT=8080
```

### Container Won't Start

```bash
# Check logs
docker-compose logs api
docker-compose logs frontend

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Database Issues

```bash
# Check database file exists
ls -la ./data/

# Check permissions
chmod 755 ./data
chmod 644 ./data/election_demo.db

# Reset database
docker-compose down
rm ./data/election_demo.db
docker-compose up -d
```

### API Not Accessible

```bash
# Check API container is running
docker-compose ps

# Check API health directly
docker-compose exec api python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Check logs
docker-compose logs api
```

### Frontend Shows 502 Bad Gateway

This means nginx cannot reach the API container:

```bash
# Check API is running
docker-compose ps

# Check network connectivity
docker-compose exec frontend ping -c 3 api

# Restart services
docker-compose restart
```

---

## Production Deployment

### Security Checklist

1. **Environment Variables**
   ```bash
   DEBUG=false
   CORS_ORIGINS=https://yourdomain.com
   ```

2. **Use HTTPS**
   - Set up reverse proxy (e.g., nginx on host) with SSL certificates
   - Or use Traefik/Caddy as reverse proxy

3. **Database Backup**
   - Set up automated backups
   - Store backups securely off-server

4. **Update Regularly**
   ```bash
   git pull
   docker-compose build --no-cache
   docker-compose up -d
   ```

5. **Monitor Logs**
   ```bash
   docker-compose logs -f --tail=100
   ```

6. **Resource Limits**

   Edit `docker-compose.yml` to add resource limits:
   ```yaml
   services:
     api:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 1G
   ```

### Example Production Setup with HTTPS

1. Install Caddy on host
2. Configure Caddy:
   ```
   yourdomain.com {
       reverse_proxy localhost:80
   }
   ```
3. Update `.env`:
   ```bash
   FRONTEND_PORT=8080
   CORS_ORIGINS=https://yourdomain.com
   ```
4. Start application:
   ```bash
   docker-compose up -d
   ```

---

## Development Tips

### Live Reload (Development)

For development with live reload, mount source code:

```yaml
# Add to docker-compose.yml api service
volumes:
  - ./src:/app/src
```

Then rebuild and start with `--reload`:

```yaml
command: ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Access Container Shell

```bash
# API container (bash)
docker-compose exec api bash

# Frontend container (sh - alpine)
docker-compose exec frontend sh
```

### Run Commands in Container

```bash
# Run Python in API container
docker-compose exec api python

# Check database in container
docker-compose exec api ls -la /app/data

# View frontend files
docker-compose exec frontend ls -la /usr/share/nginx/html
```

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                         Host                            │
│                                                         │
│  ┌─────────────────────────────────────────────────┐  │
│  │          Docker Network (bridge)                │  │
│  │                                                  │  │
│  │  ┌──────────────────┐      ┌─────────────────┐ │  │
│  │  │  Frontend (nginx)│      │   API (FastAPI)  │ │  │
│  │  │  Port: 80        │─────▶│   Port: 8000     │ │  │
│  │  │  /usr/share/nginx│      │   /app           │ │  │
│  │  │                  │      │   /app/data (vol)│ │  │
│  │  └──────────────────┘      └─────────────────┘ │  │
│  │          ▲                          ▲           │  │
│  └──────────│──────────────────────────│───────────┘  │
│             │                          │              │
│      Port 80│                   Volume │              │
│             │                    ./data│              │
└─────────────┼──────────────────────────┼──────────────┘
              │                          │
         User Browser              SQLite Database
```

---

## Support

For issues:
- Check logs: `docker-compose logs -f`
- Review `TESTING_GUIDE.md` for testing procedures
- Check GitHub issues: https://github.com/anthropics/claude-code/issues
