from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # API Settings
    app_name: str = "Market Data Service"
    debug: bool = False
    api_v1_str: str = "/api/v1"
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/market_data"
    
    # Redis Cache (optional)
    redis_url: str = "redis://localhost:6379/0"
    
    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic_price_events: str = "price-events"
    kafka_group_id: str = "market-data-consumers"
    
    # Market Data Provider - Simplified to only Yahoo Finance
    default_provider: str = "yahoo_finance"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # Moving Average Settings
    moving_average_window: int = 5
    
    class Config:
        env_file = ".env"


settings = Settings()
