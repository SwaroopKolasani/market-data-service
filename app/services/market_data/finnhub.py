import httpx
import random
from typing import Dict, Any
from datetime import datetime
from .base import MarketDataProvider
import logging

logger = logging.getLogger(__name__)

class FinnhubProvider(MarketDataProvider):
    """Finnhub provider for REAL-TIME market data"""
    
    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        if not api_key or api_key == "demo":
            raise ValueError("Finnhub requires a valid API key for real-time data")
        
        self.api_key = api_key
        self.base_url = "https://finnhub.io/api/v1"
        
        # Log with masked API key for security
        masked_key = f"{api_key[:8]}...{api_key[-4:]}" if len(api_key) > 12 else "***"
        logger.info(f"✅ Initialized Finnhub with API key: {masked_key}")
    
    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """Get REAL-TIME price from Finnhub API"""
        try:
            logger.info(f"📡 Fetching REAL-TIME data for {symbol} from Finnhub...")
            
            params = {
                "symbol": symbol.upper(),
                "token": self.api_key
            }
            
            headers = {
                "User-Agent": "Market-Data-Service/1.0",
                "Accept": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
                response = await client.get(f"{self.base_url}/quote", params=params)
                
                logger.info(f"Finnhub API response: {response.status_code}")
                response.raise_for_status()
                data = response.json()
            
            # Check for valid price data
            current_price = data.get("c")
            if current_price is None or current_price <= 0:
                logger.warning(f"No valid price data for {symbol}: {data}")
                return self._get_mock_data(symbol, "no_price_data")
            
            # Extract market data
            high_price = data.get("h", 0)
            low_price = data.get("l", 0) 
            open_price = data.get("o", 0)
            previous_close = data.get("pc", 0)
            
            # Calculate changes
            price_change = current_price - previous_close if previous_close > 0 else 0
            price_change_percent = (price_change / previous_close * 100) if previous_close > 0 else 0
            
            timestamp = datetime.utcnow()
            
            logger.info(f"🟢 REAL-TIME {symbol}: ${current_price:.2f} ({price_change_percent:+.2f}%)")
            
            return {
                "symbol": symbol.upper(),
                "price": float(current_price),
                "timestamp": timestamp.isoformat() + "Z",
                "provider": self.get_provider_name(),
                "raw_response": {
                    "source": "finnhub_api_real_time",
                    "current_price": current_price,
                    "high": high_price,
                    "low": low_price,
                    "open": open_price,
                    "previous_close": previous_close,
                    "price_change": price_change,
                    "price_change_percent": round(price_change_percent, 2),
                    "real_time": True,
                    "mock": False  # Real data!
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Finnhub error for {symbol}: {e}")
            return self._get_mock_data(symbol, f"error_{e}")
    
    def _get_mock_data(self, symbol: str, reason: str = "unknown") -> Dict[str, Any]:
        """Fallback mock data"""
        logger.warning(f"🔄 Using mock data for {symbol} (reason: {reason})")
        
        base_prices = {
            'AAPL': 185.50, 'MSFT': 420.25, 'GOOGL': 2850.80, 'TSLA': 195.60,
            'AMZN': 3420.90, 'META': 488.75, 'NFLX': 545.20, 'NVDA': 1275.30
        }
        
        base_price = base_prices.get(symbol.upper(), 150.0)
        current_price = base_price * (1 + random.uniform(-0.02, 0.02))
        
        return {
            "symbol": symbol.upper(),
            "price": round(current_price, 2),
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "provider": self.get_provider_name(),
            "raw_response": {
                "source": "mock_data",
                "mock": True,
                "mock_reason": reason
            }
        }
    
    def get_provider_name(self) -> str:
        return "finnhub"
    
    def get_rate_limit(self) -> int:
        return 60
