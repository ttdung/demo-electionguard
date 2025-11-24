"""
Pydantic schemas for vote events API.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from src.models import EventStatus


class CandidateBase(BaseModel):
    """Base candidate schema."""
    name: str = Field(..., min_length=1, max_length=255, description="Candidate name")


class CandidateResponse(CandidateBase):
    """Candidate response schema."""
    id: int
    vote_count: int = 0
    vote_percentage: float = 0.0

    class Config:
        orm_mode = True


class VoteEventCreate(BaseModel):
    """Schema for creating a new vote event."""
    name: str = Field(..., min_length=1, max_length=255, description="Event name")
    from_date: datetime = Field(..., description="Event start date")
    to_date: datetime = Field(..., description="Event end date")
    allow_vote_candidate_num: int = Field(
        default=1,
        ge=1,
        description="Number of candidates voters can select"
    )
    candidate_names: List[str] = Field(
        ...,
        min_items=2,
        description="List of candidate names (minimum 2)"
    )

    @validator('to_date')
    def validate_dates(cls, to_date, values):
        """Ensure end date is after start date."""
        if 'from_date' in values and to_date <= values['from_date']:
            raise ValueError('to_date must be after from_date')
        return to_date

    @validator('allow_vote_candidate_num')
    def validate_candidate_num(cls, allow_vote_candidate_num, values):
        """Ensure allowed votes doesn't exceed number of candidates."""
        if 'candidate_names' in values:
            num_candidates = len(values['candidate_names'])
            if allow_vote_candidate_num > num_candidates:
                raise ValueError(
                    f'allow_vote_candidate_num ({allow_vote_candidate_num}) '
                    f'cannot exceed number of candidates ({num_candidates})'
                )
        return allow_vote_candidate_num


class VoteEventResponse(BaseModel):
    """Schema for vote event response."""
    id: int
    name: str
    from_date: datetime
    to_date: datetime
    status: EventStatus
    allow_vote_candidate_num: int

    class Config:
        orm_mode = True


class VoteEventListResponse(BaseModel):
    """Schema for list of vote events."""
    events: List[VoteEventResponse]
    total: int


class VoteEventDetailResponse(VoteEventResponse):
    """Schema for detailed vote event with candidates and results."""
    candidates: List[CandidateResponse]
    total_votes: int = 0

    class Config:
        orm_mode = True


class TallyResultItem(BaseModel):
    """Schema for a single candidate's tally result."""
    candidate_id: int
    candidate_name: str
    vote_count: int
    vote_percentage: float

    class Config:
        orm_mode = True


class TallyResultsResponse(BaseModel):
    """Schema for tally results of an event."""
    event_id: int
    event_name: str
    status: EventStatus
    total_votes: int
    results: List[TallyResultItem]

    class Config:
        orm_mode = True


class LogEntry(BaseModel):
    """Schema for a single log entry."""
    timestamp: str
    level: str
    logger: str
    message: str
    event_id: Optional[int] = None


class EventLogsResponse(BaseModel):
    """Schema for event logs response."""
    event_id: int
    logs: List[LogEntry]
    total_count: int
