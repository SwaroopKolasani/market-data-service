"""Market data providers package"""

from .base import MarketDataProvider
from .yahoo_finance import YahooFinanceProvider
from .finnhub import FinnhubProvider

# Provider registry - Use Finnhub as default
PROVIDERS = {
    "yahoo_finance": YahooFinanceProvider,
    "finnhub": FinnhubProvider,
}

DEFAULT_PROVIDER = "finnhub"  # Switch to Finnhub for real-time data

def get_provider(provider_name: str = None, api_key: str = None) -> MarketDataProvider:
    """Factory function to get a market data provider"""
    if not provider_name:
        provider_name = DEFAULT_PROVIDER
    
    if provider_name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider: {provider_name}. Available: {available}")
    
    provider_class = PROVIDERS[provider_name]
    
    if provider_name == "finnhub":
        return provider_class(api_key or "demo")
    else:
        return provider_class()

def get_available_providers() -> list:
    return list(PROVIDERS.keys())

__all__ = [
    "MarketDataProvider", "YahooFinanceProvider", "FinnhubProvider", 
    "get_provider", "get_available_providers", "PROVIDERS", "DEFAULT_PROVIDER"
]
