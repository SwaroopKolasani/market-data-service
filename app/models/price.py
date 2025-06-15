from sqlalchemy import Column, Integer, String, Float, DateTime, Index, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime


class RawMarketData(Base):
    __tablename__ = "raw_market_data"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    provider = Column(String(50), nullable=False)
    raw_response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('ix_raw_market_data_symbol_timestamp', 'symbol', 'timestamp'),
        Index('ix_raw_market_data_provider', 'provider'),
    )


class ProcessedPrice(Base):
    __tablename__ = "processed_prices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    provider = Column(String(50), nullable=False)
    raw_response_id = Column(UUID(as_uuid=True), nullable=True)
    
    __table_args__ = (
        Index('ix_processed_prices_symbol_timestamp', 'symbol', 'timestamp'),
        Index('ix_processed_prices_symbol_latest', 'symbol', 'timestamp'),
    )


class MovingAverage(Base):
    __tablename__ = "moving_averages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    symbol = Column(String(10), nullable=False)
    window_size = Column(Integer, nullable=False)
    value = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('ix_moving_averages_symbol_window', 'symbol', 'window_size', 'timestamp'),
    )


class PollingJob(Base):
    __tablename__ = "polling_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(String(100), unique=True, nullable=False)
    symbols = Column(Text, nullable=False)  # JSON array as string
    interval = Column(Integer, nullable=False)  # seconds
    provider = Column(String(50), nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active, paused, stopped
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_run = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('ix_polling_jobs_status', 'status'),
        Index('ix_polling_jobs_job_id', 'job_id'),
    )
