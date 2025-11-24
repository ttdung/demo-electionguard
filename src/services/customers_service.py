"""
Business logic for customers.
"""
import logging
import secrets
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models import Customer, EventCustomer, VoteEvent, CustomerVote
from src.schemas.customers import CustomerRegisterRequest, EventCustomerRegisterRequest
from src.exceptions import CustomerAlreadyExistsException, EventNotFoundException

logger = logging.getLogger(__name__)


def generate_customer_secret() -> str:
    """
    Generate a secure random secret token for customer authentication.

    Returns:
        64-character hex string
    """
    return secrets.token_hex(32)


async def register_customer(
    db: AsyncSession,
    customer_data: CustomerRegisterRequest
) -> Customer:
    """
    Register a new customer.

    Generates a secure customer_secret token for voting authentication.

    Args:
        db: Database session
        customer_data: Customer registration data

    Returns:
        Created Customer with secret token

    Raises:
        CustomerAlreadyExistsException: If unique_id already registered
    """
    logger.info(f"Registering customer: {customer_data.unique_id}")

    # Check if customer already exists
    query = select(Customer).where(Customer.unique_id == customer_data.unique_id)
    result = await db.execute(query)
    existing_customer = result.scalar_one_or_none()

    if existing_customer:
        raise CustomerAlreadyExistsException(
            f"Customer with unique_id '{customer_data.unique_id}' already exists"
        )

    # Generate secure secret
    customer_secret = generate_customer_secret()

    # Create customer
    customer = Customer(
        unique_id=customer_data.unique_id,
        customer_secret=customer_secret
    )

    db.add(customer)
    await db.commit()
    await db.refresh(customer)

    logger.info(f"Customer registered with ID: {customer.id}")
    return customer


async def get_customer_by_secret(
    db: AsyncSession,
    customer_secret: str
) -> Customer | None:
    """
    Get customer by their secret token.

    Args:
        db: Database session
        customer_secret: Customer secret token

    Returns:
        Customer if found, None otherwise
    """
    query = select(Customer).where(Customer.customer_secret == customer_secret)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def register_customer_for_event(
    db: AsyncSession,
    event_id: int,
    customer_data: EventCustomerRegisterRequest
) -> tuple[Customer, EventCustomer]:
    """
    Register a customer for a specific event.

    If customer with unique_id doesn't exist, creates new customer.
    Links customer to event via EventCustomer junction table.

    Args:
        db: Database session
        event_id: Event ID to register for
        customer_data: Customer registration data

    Returns:
        Tuple of (Customer, EventCustomer)

    Raises:
        EventNotFoundException: If event not found
        CustomerAlreadyExistsException: If customer already registered for this event
    """
    logger.info(f"Event {event_id} # REGISTER | Registering customer: {customer_data.unique_id}")

    # Check if event exists
    event_query = select(VoteEvent).where(VoteEvent.id == event_id)
    event_result = await db.execute(event_query)
    event = event_result.scalar_one_or_none()

    if not event:
        raise EventNotFoundException(f"Event with ID {event_id} not found")

    # Check if customer already exists
    customer_query = select(Customer).where(Customer.unique_id == customer_data.unique_id)
    customer_result = await db.execute(customer_query)
    customer = customer_result.scalar_one_or_none()

    # Create customer if doesn't exist
    if not customer:
        customer_secret = generate_customer_secret()
        customer = Customer(
            unique_id=customer_data.unique_id,
            customer_secret=customer_secret
        )
        db.add(customer)
        await db.flush()
        logger.info(f"Event {event_id} # REGISTER | Created new customer (ID: {customer.id}, Secret: {customer_secret[:8]}...)")
    else:
        logger.info(f"Event {event_id} # REGISTER | Using existing customer (ID: {customer.id})")

    # Check if already registered for this event
    event_customer_query = select(EventCustomer).where(
        EventCustomer.event_id == event_id,
        EventCustomer.customer_id == customer.id
    )
    event_customer_result = await db.execute(event_customer_query)
    existing_registration = event_customer_result.scalar_one_or_none()

    if existing_registration:
        raise CustomerAlreadyExistsException(
            f"Customer '{customer_data.unique_id}' is already registered for event {event_id}"
        )

    # Create event-customer link
    event_customer = EventCustomer(
        event_id=event_id,
        customer_id=customer.id
    )
    db.add(event_customer)
    await db.commit()
    await db.refresh(customer)
    await db.refresh(event_customer)

    logger.info(f"Event {event_id} # REGISTER | ✓ Customer {customer.unique_id} registered successfully")
    return customer, event_customer


async def get_event_customers(
    db: AsyncSession,
    event_id: int
) -> List[dict]:
    """
    Get all customers registered for a specific event with voting status.

    Args:
        db: Database session
        event_id: Event ID

    Returns:
        List of customer dicts with voting status

    Raises:
        EventNotFoundException: If event not found
    """
    # Check if event exists
    event_query = select(VoteEvent).where(VoteEvent.id == event_id)
    event_result = await db.execute(event_query)
    event = event_result.scalar_one_or_none()

    if not event:
        raise EventNotFoundException(f"Event with ID {event_id} not found")

    # Get all event customers with their customer data
    query = select(EventCustomer, Customer).join(
        Customer, EventCustomer.customer_id == Customer.id
    ).where(EventCustomer.event_id == event_id).order_by(EventCustomer.registered_at.desc())

    result = await db.execute(query)
    event_customers = result.all()

    # Get all votes for this event to determine voting status
    votes_query = select(CustomerVote.customer_id).where(CustomerVote.event_id == event_id)
    votes_result = await db.execute(votes_query)
    voted_customer_ids = {row[0] for row in votes_result.all()}

    # Build response with voting status
    customers_data = []
    for event_customer, customer in event_customers:
        customers_data.append({
            'id': event_customer.id,
            'customer_id': customer.id,
            'unique_id': customer.unique_id,
            'customer_secret': customer.customer_secret,
            'registered_at': event_customer.registered_at,
            'has_voted': customer.id in voted_customer_ids
        })

    return customers_data
