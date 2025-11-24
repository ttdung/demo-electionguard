"""Common Pydantic schemas and base models."""
from datetime import datetime
from pydantic import BaseModel


class CustomBaseModel(BaseModel):
    """Base model with common configuration."""

    class Config:
        orm_mode = True
        validate_assignment = True
        anystr_strip_whitespace = True
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class HealthCheckResponse(CustomBaseModel):
    """Health check response model."""
    status: str
    version: str
    timestamp: datetime
