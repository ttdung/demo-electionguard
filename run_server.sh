#!/bin/bash

# ElectionGuard Demo Server Startup Script

echo "========================================"
echo "ElectionGuard Voting Demo"
echo "========================================"
echo ""

# Navigate to project directory
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Please run: python3.10 -m venv .venv && .venv/bin/pip install -r requirements.txt"
    exit 1
fi

# Kill any existing process on port 8000
echo "Checking for processes on port 8000..."
if lsof -ti:8000 > /dev/null 2>&1; then
    echo "Killing existing process on port 8000..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Start the server
echo ""
echo "Starting ElectionGuard Demo Server..."
echo "========================================"
echo ""
echo "Access the application at:"
echo "  Frontend: http://localhost:8000/"
echo "  API Docs: http://localhost:8000/docs"
echo ""
echo "Press CTRL+C to stop the server"
echo ""
echo "========================================"
echo ""

.venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
