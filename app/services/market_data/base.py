from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime


class MarketDataProvider(ABC):
    """Base interface for market data providers"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    @abstractmethod
    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """Get the latest price for a symbol"""
        pass
    
    @abstractmethod
    def get_provider_name(self) -> str:
        """Get the provider name"""
        pass
    
    @abstractmethod
    def get_rate_limit(self) -> int:
        """Get rate limit per minute"""
        pass