"""
Pydantic schemas for votes API.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class VoteSubmitRequest(BaseModel):
    """Schema for submitting a vote."""
    event_id: int = Field(..., gt=0, description="Vote event ID")
    customer_secret: str = Field(..., min_length=1, description="Customer secret token")
    selected_candidate_ids: List[int] = Field(
        ...,
        min_items=1,
        description="List of selected candidate IDs"
    )

    @validator('selected_candidate_ids')
    def validate_no_duplicates(cls, selected_candidate_ids):
        """Ensure no duplicate candidate IDs."""
        if len(selected_candidate_ids) != len(set(selected_candidate_ids)):
            raise ValueError('Cannot vote for the same candidate multiple times')
        return selected_candidate_ids


class VoteSubmitResponse(BaseModel):
    """Schema for vote submission response."""
    vote_secret: str = Field(
        ...,
        description="Secret token for vote verification"
    )
    verification_code: str = Field(
        ...,
        description="Human-readable verification code (ballot tracking code)"
    )
    message: str = Field(
        default="Vote submitted successfully",
        description="Success message"
    )
    # Additional fields for UI table updates
    event_id: int = Field(..., description="Vote event ID")
    customer_id: int = Field(..., description="Customer ID who voted")
    vote_at: datetime = Field(..., description="Timestamp when vote was cast")
    selected_candidate_ids: List[int] = Field(..., description="List of selected candidate IDs")


class VoteVerifyRequest(BaseModel):
    """Schema for verifying a vote."""
    vote_secret: str = Field(..., min_length=1, description="Vote secret token")


class VoteVerifyResponse(BaseModel):
    """Schema for vote verification response."""
    event_id: int
    event_name: str
    selected_candidates: List[str] = Field(..., description="Names of selected candidates")
    verification_code: str = Field(..., description="Ballot verification code")
    is_counted: bool = Field(
        default=True,
        description="Whether the vote has been counted in the tally"
    )

    class Config:
        orm_mode = True


class VoteListItem(BaseModel):
    """Schema for a single vote in the event votes list."""
    id: int
    customer_id: int
    customer_unique_id: str = Field(..., description="Customer's unique ID (email/student ID)")
    vote_at: datetime = Field(..., description="Timestamp when vote was cast")
    verification_code: str = Field(..., description="Ballot verification code")
    vote_secret: str = Field(..., description="Vote secret for verification")
    selected_candidate_ids: List[int] = Field(..., description="IDs of selected candidates")
    selected_candidate_names: List[str] = Field(..., description="Names of selected candidates")

    class Config:
        orm_mode = True


class VoteListResponse(BaseModel):
    """Schema for list of votes for an event."""
    votes: List[VoteListItem]
    total: int


class VoteDecodeRequest(BaseModel):
    """Schema for decoding a vote (Level 1: code only, Level 2: code + secret)."""
    verification_code: str = Field(..., min_length=1, description="Verification code")
    vote_secret: Optional[str] = Field(None, description="Vote secret (optional, for Level 2 decode)")


class VoteDecodeResponse(BaseModel):
    """Schema for vote decode response."""
    vote_id: int
    event_id: int
    event_name: str
    vote_at: datetime = Field(..., description="Timestamp when vote was cast")
    selected_candidates: List[str] = Field(..., description="Names of selected candidates")
    verification_code: str = Field(..., description="Ballot verification code")
    # Level 2 info (only if vote_secret was provided and correct)
    customer_unique_id: Optional[str] = Field(None, description="Customer's unique ID (only for Level 2)")
    customer_id: Optional[int] = Field(None, description="Customer ID (only for Level 2)")

    class Config:
        orm_mode = True
