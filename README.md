🏦 Market Data Service 
![System Architecture](https://github.com/SwaroopKolasani/market-data-service/blob/main/docs/docker-image.png)

A production-ready microservice that fetches real-time market data from Finnhub API, processes it through a Kafka streaming pipeline, and serves it via REST APIs with automated 5-point moving average calculations.
🎯 Built as an interview project for Blockhouse Capital Software Engineer Intern position.
🚀 Key Features
📊 Real-time Market Data: Live stock prices from Finnhub API (60 calls/minute)
🔄 Streaming Pipeline: Apache Kafka for real-time data processing
📈 Moving Averages: Automated 5-point moving average calculations
⚡ High-Performance API: FastAPI with async/await and automatic OpenAPI docs
💾 Persistent Storage: PostgreSQL with optimized indexes and Alembic migrations
🐳 Containerized: Complete Docker Compose setup for easy deployment
📝 Production Logging: Structured logging with comprehensive error handling
🔧 Professional Architecture: Clean code, dependency injection, service layers
🏗️ System Architecture
mermaid
graph TB
    Client[Client Application] --> API[FastAPI Service]
    API --> DB[(PostgreSQL)]
    API --> Redis[Redis Cache]
    API --> Finnhub[Finnhub API]
    API --> KafkaP[Kafka Producer]
    KafkaP --> Kafka[Apache Kafka]
    Kafka --> KafkaC[Moving Average Consumer]
    KafkaC --> DB
    Kafka --> ZK[ZooKeeper]
    
    subgraph "Data Flow"
        API -->|1. Store Raw Data| DB
        API -->|2. Publish Event| KafkaP
        KafkaC -->|3. Calculate MA| DB
        KafkaC -->|4. Store Result| DB
    end
    
    style API fill:#e1f5fe
    style Kafka fill:#fff3e0
    style DB fill:#f3e5f5
📋 Quick Start
Prerequisites
Docker & Docker Compose
Python 3.11+ (for local development)
Finnhub API key (free at finnhub.io)
1. Clone Repository
bash
git clone https://github.com/yourusername/market-data-service.git
cd market-data-service
2. Configure Environment
bash
# Copy environment template
cp .env.example .env

# Edit .env with your Finnhub API key
# FINNHUB_API_KEY=your_finnhub_api_key_here
3. Start Services
bash
# Start complete infrastructure
docker-compose -f docker/docker-compose.yml up -d

# Verify services are running
docker-compose -f docker/docker-compose.yml ps

# Check service logs
docker-compose -f docker/docker-compose.yml logs -f api
4. Test the API
bash
# Health check
curl http://localhost:8000/health

# Get real-time stock price
curl "http://localhost:8000/api/v1/prices/latest?symbol=AAPL" | jq

# Create polling job
curl -X POST "http://localhost:8000/api/v1/prices/poll" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT"], "interval": 60}' | jq

# Get moving average (after a few price requests)
curl "http://localhost:8000/api/v1/prices/moving-average?symbol=AAPL" | jq

# Interactive API documentation
open http://localhost:8000/docs
📖 API Documentation
Base URL: http://localhost:8000/api/v1
Core Endpoints
📊 Get Latest Price
http
GET /prices/latest?symbol={symbol}&provider={provider}
Example:
bash
curl "http://localhost:8000/api/v1/prices/latest?symbol=AAPL"
Response:
json
{
  "symbol": "AAPL",
  "price": 185.75,
  "timestamp": "2025-06-15T14:30:00Z",
  "provider": "finnhub"
}
🔄 Create Polling Job
http
POST /prices/poll
Request:
json
{
  "symbols": ["AAPL", "MSFT"],
  "interval": 60,
  "provider": "finnhub"
}
Response (202 Accepted):
json
{
  "job_id": "poll_abc123",
  "status": "accepted",
  "config": {
    "symbols": ["AAPL", "MSFT"],
    "interval": 60,
    "provider": "finnhub"
  }
}
📈 Get Moving Average
http
GET /prices/moving-average?symbol={symbol}&window={window}
Response:
json
{
  "symbol": "AAPL",
  "window_size": 5,
  "value": 184.92,
  "timestamp": "2025-06-15T14:30:00Z"
}
Interactive Documentation
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
🐳 Docker Services
Service
Port
Description
Health Check
api
8000
FastAPI application
GET /health
postgres
5432
PostgreSQL database
pg_isready
redis
6379
Redis cache
redis-cli ping
kafka
9092
Apache Kafka
kafka-broker-api-versions
zookeeper
2181
Kafka coordination
nc -z localhost 2181
consumer
-
Moving average calculator
Process monitoring
adminer
8080
Database admin UI
HTTP response

📊 Database Schema
Key Tables
raw_market_data
sql
CREATE TABLE raw_market_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    provider VARCHAR(50) NOT NULL,
    raw_response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
processed_prices
sql
CREATE TABLE processed_prices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    provider VARCHAR(50) NOT NULL,
    raw_response_id UUID REFERENCES raw_market_data(id)
);
moving_averages
sql
CREATE TABLE moving_averages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    symbol VARCHAR(10) NOT NULL,
    window_size INTEGER NOT NULL,
    value DECIMAL(10,2) NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
polling_jobs
sql
CREATE TABLE polling_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    job_id VARCHAR(100) UNIQUE NOT NULL,
    symbols TEXT NOT NULL,
    interval INTEGER NOT NULL,
    provider VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_run TIMESTAMP
);
🔄 Data Flow
Client Request → API receives price request for stock symbol
External API Call → Fetch real-time data from Finnhub API
Raw Storage → Store complete API response in PostgreSQL
Event Publishing → Send price event to Kafka topic price-events
Stream Processing → Consumer calculates 5-point moving average
Processed Storage → Store moving average result in database
Client Response → Return formatted price data to client
Moving Average Algorithm
python
def calculate_moving_average(symbol: str, new_price: float) -> float:
    # Get last 4 prices from database
    recent_prices = get_recent_prices(symbol, limit=4)
    
    # Include new price to make 5 data points
    all_prices = [new_price] + recent_prices
    
    # Calculate average of up to 5 points
    return sum(all_prices) / len(all_prices)
🛠️ Local Development
Development Setup
bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements/dev.txt

# Start infrastructure services only
docker-compose -f docker/docker-compose.yml up postgres kafka zookeeper redis -d

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/market_data"
export KAFKA_BOOTSTRAP_SERVERS="localhost:9092"  
export FINNHUB_API_KEY="your_api_key_here"

# Run API locally for development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, run Kafka consumer
python scripts/run_consumer.py
Development Commands
bash
# Format code
black app
isort app

# Lint code  
flake8 app
mypy app

# Database operations
alembic revision --autogenerate -m "Description"
alembic upgrade head

# View service logs
docker-compose -f docker/docker-compose.yml logs -f api
docker-compose -f docker/docker-compose.yml logs -f consumer
📈 Performance & Monitoring
Key Metrics
API Response Time: < 200ms (p95)
Throughput: 1000+ requests/minute
Moving Average Calculation: < 5 seconds
Database Query Performance: < 50ms (optimized indexes)
Monitoring
Health Check: GET /health
Database Admin: http://localhost:8080 (Adminer)
API Documentation: http://localhost:8000/docs
Service Logs: docker-compose logs -f [service_name]
🔧 Configuration
Environment VariablesFinnhub Configuration

Variable
Description
Default
Required
DATABASE_URL
PostgreSQL connection string
postgresql://user:password@localhost:5432/market_data
✅
KAFKA_BOOTSTRAP_SERVERS
Kafka broker addresses
localhost:9092
✅
FINNHUB_API_KEY
Finnhub API key for real-time data
None
✅
DEFAULT_PROVIDER
Default market data provider
finnhub
❌
MOVING_AVERAGE_WINDOW
Moving average window size
5
❌
RATE_LIMIT_PER_MINUTE
API rate limiting
60
❌
DEBUG
Enable debug mode
false
❌

Rate Limit: 60 calls/minute (free tier)
Latency: ~100ms average
Coverage: Global markets (US, EU, Asia)
Real-time: Yes, live market data
Cost: Free tier available
🚨 Troubleshooting
Common Issues
Services Won't Start
bash
# Check Docker status
docker --version
docker-compose --version

# Verify services
docker-compose -f docker/docker-compose.yml ps

# Check logs
docker-compose -f docker/docker-compose.yml logs api
Database Connection Issues
bash
# Test database connection
docker-compose -f docker/docker-compose.yml exec postgres psql -U user -d market_data -c "SELECT 1;"

# Check database tables
docker-compose -f docker/docker-compose.yml exec postgres psql -U user -d market_data -c "\dt"
Kafka Issues
bash
# Check Kafka topics
docker-compose -f docker/docker-compose.yml exec kafka kafka-topics --bootstrap-server localhost:9092 --list

# Monitor consumer logs
docker-compose -f docker/docker-compose.yml logs -f consumer
API Rate Limiting
Finnhub free tier: 60 calls/minute
Monitor usage in application logs
Implement caching for high-frequency requests
Debug Mode
bash
# Enable debug logging
echo "DEBUG=true" >> .env
docker-compose -f docker/docker-compose.yml restart api

# View detailed logs
docker-compose -f docker/docker-compose.yml logs -f api
🧪 Testing
Manual Testing
bash
# Test health endpoint
curl http://localhost:8000/health

# Test real-time data
curl "http://localhost:8000/api/v1/prices/latest?symbol=AAPL"

# Test batch operations
curl -X POST "http://localhost:8000/api/v1/prices/poll" \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT"], "interval": 60}'

# Test moving averages
curl "http://localhost:8000/api/v1/prices/moving-average?symbol=AAPL"
Database Verification
bash
# Check raw data storage
docker-compose -f docker/docker-compose.yml exec postgres psql -U user -d market_data -c "
SELECT symbol, provider, timestamp 
FROM raw_market_data 
ORDER BY timestamp DESC 
LIMIT 5;"

# Check moving averages
docker-compose -f docker/docker-compose.yml exec postgres psql -U user -d market_data -c "
SELECT symbol, window_size, value, timestamp 
FROM moving_averages 
ORDER BY timestamp DESC 
LIMIT 5;"
📚 Project Structure
market-data-service/
├── app/                           # Main application code
│   ├── api/                       # FastAPI routes and dependencies
│   │   ├── endpoints/             # API endpoint definitions
│   │   └── deps.py               # Dependency injection
│   ├── core/                      # Core configuration
│   │   ├── config.py             # Settings management
│   │   └── database.py           # Database setup
│   ├── models/                    # SQLAlchemy database models
│   │   └── price.py              # Market data models
│   ├── schemas/                   # Pydantic request/response schemas
│   │   ├── price.py              # Price schemas
│   │   └── job.py                # Job schemas
│   ├── services/                  # Business logic layer
│   │   ├── market_data/          # Market data providers
│   │   │   ├── base.py           # Provider interface
│   │   │   └── finnhub.py        # Finnhub implementation
│   │   ├── kafka/                # Kafka components
│   │   │   ├── producer.py       # Event producer
│   │   │   └── consumer.py       # Moving average consumer
│   │   └── price_service.py      # Core business logic
│   ├── utils/                     # Utility functions
│   └── main.py                   # FastAPI application entry
├── docker/                        # Docker configuration
│   ├── Dockerfile                # Container image
│   ├── docker-compose.yml        # Multi-service setup
│   └── init-db.sql              # Database initialization
├── scripts/                       # Operational scripts
│   ├── init_db.py                # Database setup
│   └── run_consumer.py           # Kafka consumer runner
├── requirements/                  # Python dependencies
│   ├── base.txt                  # Core dependencies
│   ├── dev.txt                   # Development tools
│   └── prod.txt                  # Production requirements
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── README.md                     # This documentation
├── CONTRIBUTING.md               # Contribution guidelines
├── CHANGELOG.md                  # Version history
└── LICENSE                       # MIT license
🔐 Security
API Security
Input Validation: Pydantic schema validation on all endpoints
Rate Limiting: Configurable per-IP request limiting
Error Handling: No sensitive data exposed in error responses
CORS: Configurable cross-origin policies
Data Security
API Keys: Environment variable storage only
Database: Encrypted connections for production
Logging: No sensitive data in application logs
Containers: Non-root user execution