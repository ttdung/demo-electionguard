# API Server Dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including MPFR and MPC for gmpy2)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgmp-dev \
    libmpfr-dev \
    libmpc-dev \
    curl \
    python3-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package installer)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy dependency files and source (needed for editable install)
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY .env.example .env
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

# Install Python dependencies using uv
# Use pip install --system for Docker (no venv needed in container)
RUN uv pip install --system --no-cache -e .

# Create data directory for SQLite database
RUN mkdir -p /app/data

# Make entrypoint script executable
RUN chmod +x /app/docker-entrypoint.sh

# Expose port (will be configurable via docker-compose)
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL=sqlite+aiosqlite:////app/data/election_demo.db

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the application with database initialization
CMD ["/app/docker-entrypoint.sh"]
