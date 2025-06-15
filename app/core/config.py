from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    app_name: str = "Market Data Service"
    debug: bool = False
    api_v1_str: str = "/api/v1"

    # Database - Use container name in Docker
    database_url: str = "postgresql://user:password@postgres:5432/market_data"

    # Redis Cache
    redis_url: str = "redis://redis:6379/0"

    # Kafka - Use container name in Docker
    kafka_bootstrap_servers: str = "kafka:9092"
    kafka_topic_price_events: str = "price-events"
    kafka_group_id: str = "market-data-consumers"

    # Market Data Provider - Now using Finnhub
    default_provider: str = "finnhub"
    finnhub_api_key: Optional[str] = "demo"  # Free demo key

    rate_limit_per_minute: int = 60
    moving_average_window: int = 5

    class Config:
        env_file = ".env"


settings = Settings()
