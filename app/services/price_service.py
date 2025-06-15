import json
import uuid
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime

from app.models.price import RawMarketData, ProcessedPrice, MovingAverage, PollingJob
from app.services.market_data import get_provider
from app.services.kafka.producer import PriceEventProducer
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class PriceService:
    """Service class for handling price-related operations"""
    
    def __init__(self):
        self.producer = PriceEventProducer()
    
    async def get_latest_price(
        self, 
        db: Session, 
        symbol: str, 
        provider_name: Optional[str] = None
    ) -> dict:
        """Get the latest price for a symbol"""
        try:
            # Use default provider if not specified
            if not provider_name:
                provider_name = settings.default_provider
            
            # Get API key for provider if needed
            api_key = None
            if provider_name == "alpha_vantage":
                api_key = settings.alpha_vantage_api_key
            elif provider_name == "finnhub":
                api_key = settings.finnhub_api_key
            
            # Get the provider
            provider = get_provider(provider_name, api_key)
            
            # Fetch price data
            price_data = await provider.get_latest_price(symbol)
            
            # Store raw response
            raw_data = RawMarketData(
                symbol=symbol.upper(),
                provider=provider_name,
                raw_response=json.dumps(price_data.get("raw_response", {}))
            )
            db.add(raw_data)
            db.commit()
            db.refresh(raw_data)
            
            # Add raw_response_id to price_data for Kafka message
            price_data["raw_response_id"] = raw_data.id
            
            # Produce to Kafka for processing
            await self.producer.produce_price_event(price_data)
            
            # Return API response
            return {
                "symbol": price_data["symbol"],
                "price": price_data["price"],
                "timestamp": price_data["timestamp"],
                "provider": price_data["provider"]
            }
            
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            raise
    
    async def create_polling_job(
        self, 
        db: Session, 
        symbols: List[str], 
        interval: int, 
        provider_name: Optional[str] = None
    ) -> dict:
        """Create a new polling job"""
        try:
            # Use default provider if not specified
            if not provider_name:
                provider_name = settings.default_provider
            
            # Generate job ID
            job_id = f"poll_{uuid.uuid4().hex[:8]}"
            
            # Create job record
            job = PollingJob(
                job_id=job_id,
                symbols=json.dumps(symbols),
                interval=interval,
                provider=provider_name,
                status="accepted"
            )
            db.add(job)
            db.commit()
            
            # TODO: In a real implementation, you'd add this job to a task queue
            # For now, we'll just return the accepted response
            
            return {
                "job_id": job_id,
                "status": "accepted",
                "config": {
                    "symbols": symbols,
                    "interval": interval,
                    "provider": provider_name
                }
            }
            
        except Exception as e:
            logger.error(f"Error creating polling job: {e}")
            raise
    
    def get_moving_average(
        self, 
        db: Session, 
        symbol: str, 
        window_size: Optional[int] = None
    ) -> Optional[dict]:
        """Get the latest moving average for a symbol"""
        try:
            if not window_size:
                window_size = settings.moving_average_window
            
            # Get the latest moving average
            ma = db.query(MovingAverage).filter(
                MovingAverage.symbol == symbol.upper(),
                MovingAverage.window_size == window_size
            ).order_by(desc(MovingAverage.timestamp)).first()
            
            if not ma:
                return None
            
            return {
                "symbol": ma.symbol,
                "window_size": ma.window_size,
                "value": ma.value,
                "timestamp": ma.timestamp.isoformat() + "Z"
            }
            
        except Exception as e:
            logger.error(f"Error getting moving average for {symbol}: {e}")
            raise