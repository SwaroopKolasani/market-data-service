-- docker/init-db.sql
\echo 'Creating Market Data Service tables...'

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create all tables
CREATE TABLE IF NOT EXISTS raw_market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    raw_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS processed_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    provider VARCHAR(50) NOT NULL,
    raw_response_id UUID
);

CREATE TABLE IF NOT EXISTS moving_averages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    window_size INTEGER NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS polling_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id VARCHAR(100) UNIQUE NOT NULL,
    symbols TEXT NOT NULL,
    interval INTEGER NOT NULL,
    provider VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_run TIMESTAMP
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_raw_market_data_symbol_timestamp ON raw_market_data(symbol, timestamp);
CREATE INDEX IF NOT EXISTS idx_processed_prices_symbol_timestamp ON processed_prices(symbol, timestamp);

\echo 'Market Data Service tables created successfully!'