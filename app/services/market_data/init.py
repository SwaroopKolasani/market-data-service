from .base import MarketDataProvider
from .yahoo_finance import YahooFinanceProvider
from typing import Dict, Type

# Simplified provider registry - only Yahoo Finance
PROVIDERS: Dict[str, Type[MarketDataProvider]] = {
    "yahoo_finance": YahooFinanceProvider,
}

# Default provider
DEFAULT_PROVIDER = "yahoo_finance"


def get_provider(provider_name: str = None, api_key: str = None) -> MarketDataProvider:
    """Factory function to get a market data provider"""
    # Use default if no provider specified
    if not provider_name:
        provider_name = DEFAULT_PROVIDER

    if provider_name not in PROVIDERS:
        available = ", ".join(PROVIDERS.keys())
        raise ValueError(f"Unknown provider: {provider_name}. Available: {available}")

    provider_class = PROVIDERS[provider_name]

    # Yahoo Finance doesn't need API key
    return provider_class()


def get_available_providers() -> list:
    """Get list of available providers"""
    return list(PROVIDERS.keys())
