"""
Customers API endpoints.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db
from src.schemas.customers import CustomerRegisterRequest, CustomerRegisterResponse
from src.services import customers_service
from src.exceptions import CustomerAlreadyExistsException

from pydantic import BaseModel
from src.utils import check_vote, VoteRequest as VoteRequestModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/customers", tags=["customers"])

class VoteRequest(BaseModel):
    seal: str
    journal: str
    journal_abi: str
    image_id: str
    nullifier: str
    age: int
    is_student: bool
    poll_id: int
    option_a: int
    option_b: int

# @router.post(
#     "/checkvoter",
#     response_model=CustomerRegisterResponse,
#     status_code=status.HTTP_201_CREATED,
#     summary="Register a new customer (auto from ZK proof)"
# )
# async def checkvote_endpoint(vote_request: VoteRequest, db: AsyncSession = Depends(get_db)):
#     try:
#         # Build the ZK input model (only these four are allowed)
#         vote_model = VoteRequestModel(
#             seal=vote_request.seal,
#             journal=vote_request.journal,
#             journal_abi=vote_request.journal_abi,
#             image_id=vote_request.image_id,
#         )

#         # Decode and verify vote
#         result = check_vote(vote_model)

#         # Generate unique_id based on nullifier + decoded poll_id
#         unique_id = f"{result.nullifier}{result.poll_id}"
#         print(f"Unique ID: {unique_id}")

#         # Check for existing customer
#         existing_customer = await customers_service.get_customer_by_unique_id(db, unique_id)
#         if existing_customer:
#             return CustomerRegisterResponse.from_orm(existing_customer)

#         # Register new customer
#         customer_data = CustomerRegisterRequest(unique_id=unique_id)
#         customer = await customers_service.register_customer(db, customer_data)

#         return CustomerRegisterResponse.from_orm(customer)

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.post("/checkvoter")
async def checkvote_endpoint(vote_request: VoteRequest):
    try:
        vote_model = VoteRequestModel(
            seal=vote_request.seal,
            journal=vote_request.journal,
            journal_abi=vote_request.journal_abi,
            image_id=vote_request.image_id,
            nullifier=vote_request.nullifier,
            age=vote_request.age,
            is_student=vote_request.is_student,
            poll_id=vote_request.poll_id,
            option_a=vote_request.option_a,
            option_b=vote_request.option_b,
        )
        result = check_vote(vote_model)
        # Convert dataclass to dict for JSON serialization
        result_dict = {
            "nullifier": result.nullifier,
            "age": result.age,
            "is_student": result.is_student,
            "poll_id": result.poll_id,
        }
        return {"status": "success", "result": result_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post(
    "/register",
    response_model=CustomerRegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new customer",
    description="Registers a new customer and returns a secret token for voting authentication"
)
async def register_customer(
    customer_data: CustomerRegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new customer.

    The customer will receive a `customer_secret` token that must be used
    when submitting votes. This token should be kept secure.

    Args:
        customer_data: Registration data containing unique_id

    Returns:
        Customer details with secret token
    """
    try:
        customer = await customers_service.register_customer(db, customer_data)
        return CustomerRegisterResponse.from_orm(customer)
    except CustomerAlreadyExistsException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Failed to register customer: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register customer: {str(e)}"
        )
