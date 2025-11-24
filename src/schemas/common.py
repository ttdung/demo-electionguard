"""
Common schemas.
"""
from datetime import datetime
from pydantic import BaseModel, Field


class HealthCheckResponse(BaseModel):
    """Health check response schema."""
    status: str = Field(..., description="Health status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(..., description="Current timestamp")
