from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from uuid import UUID


class PollRequest(BaseModel):
    """Request schema for creating a polling job"""
    symbols: List[str] = Field(..., min_items=1, max_items=10, description="Stock symbols to poll")
    interval: int = Field(..., ge=60, le=3600, description="Polling interval in seconds (1 minute to 1 hour)")
    provider: Optional[str] = Field(None, description="Data provider (defaults to yahoo_finance)")

    class Config:
        schema_extra = {
            "example": {
                "symbols": ["AAPL", "MSFT"],
                "interval": 60,
                "provider": "yahoo_finance"
            }
        }


class PollResponse(BaseModel):
    """Response schema for polling job creation"""
    job_id: str
    status: str
    config: dict

    class Config:
        schema_extra = {
            "example": {
                "job_id": "poll_abc123",
                "status": "accepted",
                "config": {
                    "symbols": ["AAPL", "MSFT"],
                    "interval": 60,
                    "provider": "yahoo_finance"
                }
            }
        }


class JobConfig(BaseModel):
    """Configuration schema for polling jobs"""
    symbols: List[str]
    interval: int
    provider: str


class JobStatus(BaseModel):
    """Status schema for polling jobs"""
    job_id: str
    status: str
    config: JobConfig
    created_at: datetime
    last_run: Optional[datetime] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() + "Z"
        }
