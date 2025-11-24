"""
Pydantic schemas for customers API.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class CustomerRegisterRequest(BaseModel):
    """Schema for customer registration."""
    unique_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique identifier for the customer (e.g., email, student ID)"
    )


class CustomerRegisterResponse(BaseModel):
    """Schema for customer registration response."""
    id: int
    unique_id: str
    customer_secret: str = Field(
        ...,
        description="Secret token for voting authentication"
    )

    class Config:
        orm_mode = True


class EventCustomerRegisterRequest(BaseModel):
    """Schema for event-specific customer registration."""
    unique_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Unique identifier for the customer (e.g., email, student ID)"
    )


class EventCustomerRegisterResponse(BaseModel):
    """Schema for event-specific customer registration response."""
    id: int
    unique_id: str
    customer_secret: str = Field(..., description="Secret token for voting authentication")
    event_id: int
    registered_at: datetime

    class Config:
        orm_mode = True


class EventCustomerItem(BaseModel):
    """Schema for a single customer in the event customer list."""
    id: int
    customer_id: int
    unique_id: str = Field(..., description="Customer's unique ID (email/student ID)")
    customer_secret: str = Field(..., description="Secret token for voting")
    registered_at: datetime
    has_voted: bool = Field(..., description="Whether this customer has voted in this event")

    class Config:
        orm_mode = True


class EventCustomerListResponse(BaseModel):
    """Schema for list of customers for an event."""
    customers: List[EventCustomerItem]
    total: int
