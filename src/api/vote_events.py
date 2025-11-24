"""
Vote events API endpoints.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.vote_events import (
    VoteEventCreate,
    VoteEventResponse,
    VoteEventListResponse,
    VoteEventDetailResponse,
    CandidateResponse,
    TallyResultsResponse,
    TallyResultItem,
    EventLogsResponse,
    LogEntry,
)
from src.schemas.customers import (
    EventCustomerRegisterRequest,
    EventCustomerRegisterResponse,
    EventCustomerListResponse,
    EventCustomerItem,
)
from src.schemas.votes import (
    VoteListResponse,
    VoteListItem,
)
from src.services import vote_events_service, customers_service, votes_service
from src.exceptions import EventNotFoundException, InvalidEventStateException, CustomerAlreadyExistsException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vote-events", tags=["vote-events"])


@router.post(
    "",
    response_model=VoteEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new vote event",
    description="Creates a new voting event with candidates and initializes ElectionGuard cryptographic setup"
)
async def create_vote_event(
    event_data: VoteEventCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new vote event.

    This endpoint:
    - Creates the event and candidate records
    - Builds an ElectionGuard manifest
    - Performs the key ceremony
    - Stores cryptographic materials for the election

    Returns the created event details.
    """
    try:
        logger.info(f"# CREATE | Request to create event: {event_data.name}")
        event = await vote_events_service.create_vote_event(db, event_data)
        return VoteEventResponse.from_orm(event)
    except ValueError as e:
        # Validation errors
        logger.error(f"# CREATE | ✗ Validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Validation error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"# CREATE | ✗ Failed to create vote event: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create vote event: {str(e)}"
        )


@router.get(
    "",
    response_model=VoteEventListResponse,
    summary="Get list of vote events",
    description="Returns a paginated list of all vote events"
)
async def get_vote_events(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get list of vote events with pagination.

    Args:
        skip: Number of records to skip (default: 0)
        limit: Maximum number of records to return (default: 100, max: 100)
    """
    if limit > 100:
        limit = 100

    events, total = await vote_events_service.get_vote_events(db, skip, limit)
    return VoteEventListResponse(
        events=[VoteEventResponse.from_orm(e) for e in events],
        total=total
    )


@router.get(
    "/{event_id}",
    response_model=VoteEventDetailResponse,
    summary="Get vote event details",
    description="Returns detailed information about a specific vote event including candidates and results"
)
async def get_vote_event(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed information about a vote event.

    Includes:
    - Event details (name, dates, status)
    - List of candidates
    - Vote counts and percentages (if tally has been performed)
    """
    try:
        event = await vote_events_service.get_vote_event_detail(db, event_id)

        # Calculate total votes
        total_votes = sum(c.vote_count for c in event.candidates)

        return VoteEventDetailResponse(
            id=event.id,
            name=event.name,
            from_date=event.from_date,
            to_date=event.to_date,
            status=event.status,
            allow_vote_candidate_num=event.allow_vote_candidate_num,
            candidates=[CandidateResponse.from_orm(c) for c in event.candidates],
            total_votes=total_votes
        )
    except EventNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/{event_id}/end-voting",
    response_model=VoteEventResponse,
    summary="End voting for an event",
    description="Closes voting for an event, preventing new votes from being submitted"
)
async def end_voting(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    End voting for an event.

    Changes the event status to ENDED, preventing new votes.
    The tally must be performed separately using the tally endpoint.
    """
    try:
        event = await vote_events_service.end_voting(db, event_id)
        return VoteEventResponse.from_orm(event)
    except EventNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidEventStateException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/{event_id}/customers/register",
    response_model=EventCustomerRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register customer for event",
    description="Register a customer for a specific voting event"
)
async def register_customer_for_event(
    event_id: int,
    customer_data: EventCustomerRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a customer for a specific event.

    If customer doesn't exist, creates new customer.
    Links customer to event via event-customer registration.
    """
    try:
        customer, event_customer = await customers_service.register_customer_for_event(
            db, event_id, customer_data
        )
        return EventCustomerRegisterResponse(
            id=customer.id,
            unique_id=customer.unique_id,
            customer_secret=customer.customer_secret,
            event_id=event_id,
            registered_at=event_customer.registered_at
        )
    except EventNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except CustomerAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get(
    "/{event_id}/customers",
    response_model=EventCustomerListResponse,
    summary="Get customers for event",
    description="Returns list of all customers registered for this event with voting status"
)
async def get_event_customers(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all customers registered for a specific event.

    Includes voting status (whether they've voted or not).
    """
    try:
        customers_data = await customers_service.get_event_customers(db, event_id)
        return EventCustomerListResponse(
            customers=[EventCustomerItem(**c) for c in customers_data],
            total=len(customers_data)
        )
    except EventNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get(
    "/{event_id}/votes",
    response_model=VoteListResponse,
    summary="Get votes for event",
    description="Returns list of all votes cast in this event"
)
async def get_event_votes(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all votes for a specific event.

    Includes customer info, timestamp, verification code, and selected candidates.
    """
    try:
        votes_data = await votes_service.get_event_votes(db, event_id)
        return VoteListResponse(
            votes=[VoteListItem(**v) for v in votes_data],
            total=len(votes_data)
        )
    except EventNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post(
    "/{event_id}/tally",
    response_model=TallyResultsResponse,
    summary="Execute tally ceremony",
    description="Performs ElectionGuard tally ceremony and returns results"
)
async def execute_tally(
    event_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Execute tally ceremony for an event.

    Performs:
    - Homomorphic aggregation of encrypted ballots
    - Decryption of aggregated tally
    - Updates candidate vote counts
    - Changes event status to END

    Returns the tally results with vote counts per candidate.
    """
    try:
        logger.info(f"Event {event_id} # TALLY_API | Request to execute tally ceremony")
        event = await vote_events_service.execute_tally(db, event_id)

        results = [
            TallyResultItem(
                candidate_id=c.id,
                candidate_name=c.name,
                vote_count=c.vote_count,
                vote_percentage=c.vote_percentage
            )
            for c in event.candidates
        ]

        logger.info(f"Event {event_id} # TALLY_API | ✓ Tally ceremony completed successfully")
        return TallyResultsResponse(
            event_id=event.id,
            event_name=event.name,
            status=event.status,
            total_votes=event.total_votes,
            results=results
        )
    except EventNotFoundException as e:
        logger.error(f"Event {event_id} # TALLY_API | ✗ Event not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidEventStateException as e:
        logger.error(f"Event {event_id} # TALLY_API | ✗ Invalid event state: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Event {event_id} # TALLY_API | ✗ Tally ceremony failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tally ceremony failed: {str(e)}"
        )


@router.get(
    "/{event_id}/logs",
    response_model=EventLogsResponse,
    summary="Get event logs",
    description="Retrieves logs filtered by event ID"
)
async def get_event_logs(
    event_id: int,
    limit: int = 100,
    debug: bool = False
):
    """
    Get logs for a specific event.

    Returns logs filtered by event ID, most recent first.
    Useful for debugging and monitoring event operations.

    Set debug=true to see ALL logs without filtering (for troubleshooting).
    """
    from src.log_handler import get_log_handler

    try:
        # Get log handler
        log_handler = get_log_handler()

        # Debug mode: return ALL logs without filtering
        if debug:
            all_logs = list(log_handler.logs)[-limit:]
            log_entries = [
                LogEntry(
                    timestamp=log['timestamp'],
                    level=log['level'],
                    logger=log['logger'],
                    message=log['message'],
                    event_id=log['event_id']
                )
                for log in all_logs
            ]
            return EventLogsResponse(
                event_id=event_id,
                logs=log_entries,
                total_count=len(log_entries)
            )

        # Get filtered logs
        logs = log_handler.get_logs(event_id=event_id, limit=limit)

        # Convert to response format
        log_entries = [
            LogEntry(
                timestamp=log['timestamp'],
                level=log['level'],
                logger=log['logger'],
                message=log['message'],
                event_id=log['event_id']
            )
            for log in logs
        ]

        return EventLogsResponse(
            event_id=event_id,
            logs=log_entries,
            total_count=len(log_entries)
        )
    except Exception as e:
        logger.error(f"Failed to fetch logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch logs: {str(e)}"
        )
