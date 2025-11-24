#!/bin/bash
set -e

echo "Initializing database..."
python -c "
import asyncio
from src.database import init_db

async def main():
    await init_db()
    print('Database tables created successfully')

asyncio.run(main())
"

echo "Starting application..."
exec python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
