from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class PriceResponse(BaseModel):
    """Response schema for price data"""

    symbol: str
    price: float
    timestamp: datetime
    provider: str

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z"}


class MovingAverageResponse(BaseModel):
    """Response schema for moving average data"""

    symbol: str
    window_size: int
    value: float
    timestamp: datetime

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat() + "Z"}
