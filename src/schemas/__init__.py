"""
Pydantic schemas for API request/response models.
"""
from .common import HealthCheckResponse
from .vote_events import (
    VoteEventCreate,
    VoteEventResponse,
    VoteEventListResponse,
    VoteEventDetailResponse,
)
from .customers import (
    CustomerRegisterRequest,
    CustomerRegisterResponse,
)
from .votes import (
    VoteSubmitRequest,
    VoteSubmitResponse,
    VoteVerifyRequest,
    VoteVerifyResponse,
)

__all__ = [
    # Common
    "HealthCheckResponse",
    # Vote Events
    "VoteEventCreate",
    "VoteEventResponse",
    "VoteEventListResponse",
    "VoteEventDetailResponse",
    # Customers
    "CustomerRegisterRequest",
    "CustomerRegisterResponse",
    # Votes
    "VoteSubmitRequest",
    "VoteSubmitResponse",
    "VoteVerifyRequest",
    "VoteVerifyResponse",
]
