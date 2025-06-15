from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.api.deps import get_price_service
from app.core.database import get_db
from app.schemas.price import PriceResponse, MovingAverageResponse
from app.schemas.job import PollRequest, PollResponse

from app.services.price_service import PriceService

router = APIRouter()


@router.get("/latest", response_model=PriceResponse)
async def get_latest_price(
    symbol: str = Query(..., description="Stock symbol (e.g., AAPL)"),
    provider: Optional[str] = Query(None, description="Data provider"),
    db: Session = Depends(get_db),
    price_service: PriceService = Depends(get_price_service)
):
    """Get the latest price for a symbol"""
    try:
        price_data = await price_service.get_latest_price(db, symbol, provider)
        return PriceResponse(**price_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/poll", response_model=PollResponse, status_code=202)
async def create_poll_job(
    request: PollRequest,
    db: Session = Depends(get_db),
    price_service: PriceService = Depends(get_price_service)
):
    """Create a polling job for multiple symbols"""
    try:
        job_data = await price_service.create_polling_job(
            db, 
            request.symbols, 
            request.interval, 
            request.provider
        )
        return PollResponse(**job_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/moving-average", response_model=MovingAverageResponse)
async def get_moving_average(
    symbol: str = Query(..., description="Stock symbol (e.g., AAPL)"),
    window: Optional[int] = Query(None, description="Moving average window size"),
    db: Session = Depends(get_db),
    price_service: PriceService = Depends(get_price_service)
):
    """Get the latest moving average for a symbol"""
    try:
        ma_data = price_service.get_moving_average(db, symbol, window)
        if not ma_data:
            raise HTTPException(status_code=404, detail="Moving average not found")
        return MovingAverageResponse(**ma_data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
