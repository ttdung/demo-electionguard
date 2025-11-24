"""FastAPI application entry point."""
import logging
import os
from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uuid

from src.config import get_settings
from src.database import init_db
from src.logging_config import setup_logging
from src.schemas import HealthCheckResponse
from src.exceptions import (
    DomainException,
    EventNotFoundException,
    CustomerNotFoundException,
    InvalidCustomerSecretException,
    AlreadyVotedException,
    InvalidSelectionCountException,
    EventNotActiveException,
    VoteNotFoundException,
    DuplicateCustomerException,
    InvalidCandidatesException,
)

# Import routers
from src.api import vote_events_router, customers_router, votes_router


settings = get_settings()

# Setup logging BEFORE creating the app (before uvicorn takes over)
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting ElectionGuard Demo API")
    await init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down ElectionGuard Demo API")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="ElectionGuard end-to-end verifiable voting demonstration",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For MVP - restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID to each request."""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


# Exception handlers
@app.exception_handler(EventNotFoundException)
async def event_not_found_handler(request: Request, exc: EventNotFoundException):
    """Handle event not found errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "EVENT_NOT_FOUND",
            "message": str(exc) or "Event not found"
        }
    )


@app.exception_handler(VoteNotFoundException)
async def vote_not_found_handler(request: Request, exc: VoteNotFoundException):
    """Handle vote not found errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "VOTE_NOT_FOUND",
            "message": str(exc) or "Vote not found"
        }
    )


@app.exception_handler(CustomerNotFoundException)
async def customer_not_found_handler(request: Request, exc: CustomerNotFoundException):
    """Handle customer not found errors."""
    return JSONResponse(
        status_code=404,
        content={
            "error": "CUSTOMER_NOT_FOUND",
            "message": str(exc) or "Customer not found"
        }
    )


@app.exception_handler(InvalidCustomerSecretException)
async def invalid_customer_secret_handler(request: Request, exc: InvalidCustomerSecretException):
    """Handle invalid customer secret errors."""
    return JSONResponse(
        status_code=401,
        content={
            "error": "INVALID_CUSTOMER_SECRET",
            "message": str(exc) or "Customer not found or invalid secret"
        }
    )


@app.exception_handler(AlreadyVotedException)
async def already_voted_handler(request: Request, exc: AlreadyVotedException):
    """Handle already voted errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "ALREADY_VOTED",
            "message": str(exc) or "Customer has already voted in this event"
        }
    )


@app.exception_handler(InvalidSelectionCountException)
async def invalid_selection_count_handler(request: Request, exc: InvalidSelectionCountException):
    """Handle invalid selection count errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "INVALID_SELECTION_COUNT",
            "message": str(exc)
        }
    )


@app.exception_handler(EventNotActiveException)
async def event_not_active_handler(request: Request, exc: EventNotActiveException):
    """Handle event not active errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "EVENT_NOT_ACTIVE",
            "message": str(exc)
        }
    )


@app.exception_handler(DuplicateCustomerException)
async def duplicate_customer_handler(request: Request, exc: DuplicateCustomerException):
    """Handle duplicate customer errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "DUPLICATE_CUSTOMER",
            "message": str(exc) or "Customer with this unique_id already exists"
        }
    )


@app.exception_handler(InvalidCandidatesException)
async def invalid_candidates_handler(request: Request, exc: InvalidCandidatesException):
    """Handle invalid candidates errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "INVALID_CANDIDATES",
            "message": str(exc)
        }
    )


@app.exception_handler(DomainException)
async def domain_exception_handler(request: Request, exc: DomainException):
    """Handle generic domain errors."""
    return JSONResponse(
        status_code=400,
        content={
            "error": exc.__class__.__name__.replace("Exception", "").upper(),
            "message": str(exc)
        }
    )


# Health check endpoint
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version="1.0.0",
        timestamp=datetime.utcnow()
    )


# Include routers
app.include_router(vote_events_router, prefix=settings.api_v1_prefix)
app.include_router(customers_router, prefix=settings.api_v1_prefix)
app.include_router(votes_router, prefix=settings.api_v1_prefix)


# Mount static files for frontend (only if directory exists)
# In Docker, frontend is served by separate nginx container
if os.path.exists("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
