from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.price_service import PriceService
from fastapi import Depends


def get_price_service() -> PriceService:
    """Dependency to get price service"""
    return PriceService()
