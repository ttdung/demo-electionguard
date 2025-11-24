"""
Votes API endpoints.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.models import EventStatus
from src.schemas.votes import (
    VoteSubmitRequest,
    VoteSubmitResponse,
    VoteVerifyRequest,
    VoteVerifyResponse,
    VoteDecodeRequest,
    VoteDecodeResponse,
)
from src.services import votes_service
from src.exceptions import (
    CustomerNotFoundException,
    EventNotFoundException,
    InvalidEventStateException,
    AlreadyVotedException,
    InvalidVoteSelectionException,
    VoteNotFoundException,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/votes", tags=["votes"])


@router.post(
    "/submit",
    response_model=VoteSubmitResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a vote",
    description="Submits an encrypted vote for a voting event using ElectionGuard"
)
async def submit_vote(
    vote_data: VoteSubmitRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Submit an encrypted vote.

    The vote is:
    1. Validated against election rules
    2. Encrypted using ElectionGuard homomorphic encryption
    3. Stored with zero-knowledge proofs
    4. Given a verification code for later verification

    Args:
        vote_data: Vote submission data including customer_secret and selected candidates

    Returns:
        Vote secret and verification code
    """
    try:
        logger.info(f"Event {vote_data.event_id} # VOTE_API | Request to submit vote")
        vote_secret, verification_code, customer_vote = await votes_service.submit_vote(db, vote_data)
        logger.info(f"Event {vote_data.event_id} # VOTE_API | ✓ Vote submitted successfully (Code: {verification_code})")
        return VoteSubmitResponse(
            vote_secret=vote_secret,
            verification_code=verification_code,
            message="Vote submitted successfully. Keep your verification code to verify your vote was counted.",
            event_id=customer_vote.event_id,
            customer_id=customer_vote.customer_id,
            vote_at=customer_vote.vote_at,
            selected_candidate_ids=vote_data.selected_candidate_ids
        )
    except CustomerNotFoundException as e:
        logger.error(f"Event {vote_data.event_id} # VOTE_API | ✗ Customer not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except EventNotFoundException as e:
        logger.error(f"Event {vote_data.event_id} # VOTE_API | ✗ Event not found: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except AlreadyVotedException as e:
        logger.error(f"Event {vote_data.event_id} # VOTE_API | ✗ Already voted: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidVoteSelectionException as e:
        logger.error(f"Event {vote_data.event_id} # VOTE_API | ✗ Invalid selection: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except InvalidEventStateException as e:
        logger.error(f"Event {vote_data.event_id} # VOTE_API | ✗ Invalid event state: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Event {vote_data.event_id} # VOTE_API | ✗ Failed to submit vote: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to submit vote: {str(e)}"
        )


@router.post(
    "/verify",
    response_model=VoteVerifyResponse,
    summary="Verify a vote",
    description="Verifies a vote using the vote secret and returns details about what was voted for"
)
async def verify_vote(
    verify_data: VoteVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a vote using the vote secret.

    Returns details about:
    - The event voted in
    - The candidates selected
    - The verification code (ballot tracking code)

    This allows voters to confirm their vote was recorded correctly.
    """
    try:
        event, selected_candidates, verification_code = await votes_service.verify_vote(
            db,
            verify_data.vote_secret
        )

        return VoteVerifyResponse(
            event_id=event.id,
            event_name=event.name,
            selected_candidates=[c.name for c in selected_candidates],
            verification_code=verification_code,
            is_counted=event.status == EventStatus.TALLIED
        )
    except VoteNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to verify vote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to verify vote: {str(e)}"
        )


@router.post(
    "/decode",
    response_model=VoteDecodeResponse,
    summary="Decode a vote",
    description="Decode a vote using verification code (Level 1) or verification code + vote secret (Level 2)"
)
async def decode_vote(
    decode_data: VoteDecodeRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Decode a vote with 2 security levels.

    Level 1 (verification code only):
    - Shows selected candidates and timestamp
    - Public information

    Level 2 (verification code + vote secret):
    - Shows all Level 1 info PLUS voter identity
    - Requires both verification code and vote secret

    This allows transparent verification while maintaining voter privacy.
    """
    try:
        vote_data = await votes_service.decode_vote(
            db,
            decode_data.verification_code,
            decode_data.vote_secret
        )

        return VoteDecodeResponse(**vote_data)
    except VoteNotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except InvalidVoteSelectionException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to decode vote: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to decode vote: {str(e)}"
        )
