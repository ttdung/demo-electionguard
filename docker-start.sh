#!/bin/bash

# ElectionGuard Docker Quick Start Script

echo "========================================"
echo "ElectionGuard Docker Deployment"
echo "========================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "ERROR: Docker is not installed"
    echo "Please install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "ERROR: Docker Compose is not installed"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Check if .env exists, if not copy from example
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo ""
    echo "You can edit .env to customize ports and configuration"
    echo ""
fi

# Create data directory if it doesn't exist
if [ ! -d "data" ]; then
    echo "Creating data directory..."
    mkdir -p data
    echo "✓ data directory created"
    echo ""
fi

# Stop any existing containers
echo "Stopping any existing containers..."
docker-compose down 2>/dev/null

# Build and start containers
echo ""
echo "Building Docker images..."
echo "This may take a few minutes on first run..."
echo ""
docker-compose build

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Docker build failed"
    echo "Please check the error messages above"
    exit 1
fi

echo ""
echo "Starting containers..."
docker-compose up -d

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to start containers"
    echo "Please check the error messages above"
    exit 1
fi

# Wait for containers to be healthy
echo ""
echo "Waiting for containers to be ready..."
sleep 5

# Check container status
echo ""
echo "Container Status:"
docker-compose ps

echo ""
echo "========================================"
echo "✓ ElectionGuard is now running!"
echo "========================================"
echo ""
echo "Access the application:"
echo "  Frontend:  http://localhost"
echo "  API Docs:  http://localhost/docs"
echo "  Health:    http://localhost/health"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f     # View logs"
echo "  docker-compose down        # Stop containers"
echo "  docker-compose restart     # Restart containers"
echo ""
echo "For help, see:"
echo "  DOCKER_README.md  - Quick start guide"
echo "  DOCKER_GUIDE.md   - Complete documentation"
echo ""
