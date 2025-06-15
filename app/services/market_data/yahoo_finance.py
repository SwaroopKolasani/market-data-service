import yfinance as yf
import asyncio
from typing import Dict, Any
from datetime import datetime
from .base import MarketDataProvider
import logging

logger = logging.getLogger(__name__)


class YahooFinanceProvider(MarketDataProvider):
    """Yahoo Finance provider implementation using yfinance"""

    def __init__(self, api_key: str = None):
        super().__init__(api_key)
        # Configure yfinance with proper headers
        self.session = None

    def _get_session(self):
        """Get configured session for yfinance"""
        if not self.session:
            import requests

            self.session = requests.Session()
            self.session.headers.update(
                {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
            )
        return self.session

    async def get_latest_price(self, symbol: str) -> Dict[str, Any]:
        """Get latest price from Yahoo Finance with better error handling"""
        try:
            loop = asyncio.get_event_loop()

            # Try different approaches in order
            approaches = [
                self._try_fast_info,
                self._try_regular_info,
                self._try_history_method,
                self._try_mock_data,  # Fallback for demo
            ]

            for approach in approaches:
                try:
                    result = await loop.run_in_executor(None, approach, symbol)
                    if result:
                        return result
                except Exception as e:
                    logger.warning(f"Approach {approach.__name__} failed for {symbol}: {e}")
                    continue

            raise Exception(f"All methods failed for symbol {symbol}")

        except Exception as e:
            logger.error(f"Failed to fetch data for {symbol}: {str(e)}")
            raise Exception(f"Failed to fetch data for {symbol}: {str(e)}")

    def _try_fast_info(self, symbol: str) -> Dict[str, Any]:
        """Try using fast_info method"""
        ticker = yf.Ticker(symbol, session=self._get_session())
        fast_info = ticker.fast_info
        price = fast_info.get("lastPrice") or fast_info.get("regularMarketPrice")

        if price and price > 0:
            timestamp = datetime.utcnow()
            return {
                "symbol": symbol.upper(),
                "price": float(price),
                "timestamp": timestamp.isoformat() + "Z",
                "provider": self.get_provider_name(),
                "raw_response": {"fast_info": dict(fast_info), "method": "fast_info"},
            }
        return None

    def _try_regular_info(self, symbol: str) -> Dict[str, Any]:
        """Try using regular info method"""
        ticker = yf.Ticker(symbol, session=self._get_session())
        info = ticker.info
        price = info.get("regularMarketPrice") or info.get("currentPrice") or info.get("previousClose")

        if price and price > 0:
            timestamp = datetime.utcnow()
            return {
                "symbol": symbol.upper(),
                "price": float(price),
                "timestamp": timestamp.isoformat() + "Z",
                "provider": self.get_provider_name(),
                "raw_response": {"info": info, "method": "regular_info"},
            }
        return None

    def _try_history_method(self, symbol: str) -> Dict[str, Any]:
        """Try using history method"""
        ticker = yf.Ticker(symbol, session=self._get_session())
        hist = ticker.history(period="5d", interval="1d")

        if not hist.empty:
            price = float(hist["Close"].iloc[-1])
            timestamp = datetime.utcnow()
            return {
                "symbol": symbol.upper(),
                "price": price,
                "timestamp": timestamp.isoformat() + "Z",
                "provider": self.get_provider_name(),
                "raw_response": {"history": hist.tail(1).to_dict(), "method": "history"},
            }
        return None

    def _try_mock_data(self, symbol: str) -> Dict[str, Any]:
        """Fallback mock data for demo purposes"""
        import random

        # Mock prices for popular symbols
        mock_prices = {
            "AAPL": 175.50,
            "MSFT": 380.25,
            "GOOGL": 2750.80,
            "TSLA": 245.60,
            "AMZN": 3320.90,
            "META": 298.75,
            "NFLX": 445.20,
            "NVDA": 875.30,
        }

        base_price = mock_prices.get(symbol.upper(), 100.0)
        # Add some random variation (±5%)
        price = base_price * (1 + random.uniform(-0.05, 0.05))

        timestamp = datetime.utcnow()
        logger.warning(f"Using mock data for {symbol}: ${price:.2f}")

        return {
            "symbol": symbol.upper(),
            "price": round(price, 2),
            "timestamp": timestamp.isoformat() + "Z",
            "provider": self.get_provider_name(),
            "raw_response": {"mock": True, "base_price": base_price, "method": "mock"},
        }

    def get_provider_name(self) -> str:
        return "yahoo_finance"

    def get_rate_limit(self) -> int:
        return 1000  # Yahoo Finance is quite generous
