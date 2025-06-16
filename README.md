<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

</head>
<body>
<h1>🏦 Market Data Service</h1>
    <img src="https://github.com/SwaroopKolasani/market-data-service/blob/main/docs/docker-image.png" alt="Architecture Diagram" width="500"/>
<p>A production-ready microservice that fetches real-time market data from Finnhub API, processes it through a Kafka streaming pipeline, and serves it via REST APIs with automated 5-point moving average calculations.</p>
<h2>🚀 Key Features</h2>
<ul>
  <li>📊 Real-time Market Data: Live stock prices from Finnhub API (60 calls/minute)</li>
  <li>🔄 Streaming Pipeline: Apache Kafka for real-time data processing</li>
  <li>📈 Moving Averages: Automated 5-point moving average calculations</li>
  <li>⚡ High-Performance API: FastAPI with async/await and automatic OpenAPI docs</li>
  <li>📂 Persistent Storage: PostgreSQL with optimized indexes and Alembic migrations</li>
  <li>🐳 Containerized: Complete Docker Compose setup for easy deployment</li>
  <li>📝 Production Logging: Structured logging with comprehensive error handling</li>
  <li>🔧 Professional Architecture: Clean code, dependency injection, service layers</li>
</ul>
<h2>🏗️ System Architecture</h2>
<img src="https://github.com/SwaroopKolasani/market-data-service/blob/main/docs/system-architecture.png" alt="Architecture Diagram" width="500"/>

<h2>📋 Quick Start</h2>
<h3>Prerequisites</h3>
<ul>
  <li>Docker & Docker Compose</li>
  <li>Python 3.11+ (for local development)</li>
  <li>Finnhub API key (free at finnhub.io)</li>
</ul>

<h3>1. Clone Repository</h3>
<pre><code>git clone https://github.com/yourusername/market-data-service.git
cd market-data-service</code></pre>

<h3>2. Configure Environment</h3>
<pre><code>cp .env.example .env
# Edit .env with your Finnhub API key</code></pre>

<h3>3. Start Services</h3>
<pre><code>docker-compose -f docker/docker-compose.yml up -d
docker-compose -f docker/docker-compose.yml ps
docker-compose -f docker/docker-compose.yml logs -f api</code></pre>

<h3>4. Test the API</h3>
<pre><code>curl http://localhost:8000/health
curl "http://localhost:8000/api/v1/prices/latest?symbol=AAPL"
curl -X POST "http://localhost:8000/api/v1/prices/poll" -H "Content-Type: application/json" -d '{"symbols": ["AAPL", "MSFT"], "interval": 60}'
curl "http://localhost:8000/api/v1/prices/moving-average?symbol=AAPL"
open http://localhost:8000/docs</code></pre>

<h2>📖 API Documentation</h2>
<p>Base URL: <code>http://localhost:8000/api/v1</code></p>
<h3>📊 Get Latest Price</h3>
<pre><code>GET /prices/latest?symbol=AAPL</code></pre>

<h3>🔄 Create Polling Job</h3>
<pre><code>POST /prices/poll</code></pre>

<h3>📈 Get Moving Average</h3>
<pre><code>GET /prices/moving-average?symbol=AAPL</code></pre>

<h2>🐳 Docker Services</h2>
<ul>
  <li><strong>api</strong> - FastAPI application (port 8000)</li>
  <li><strong>postgres</strong> - PostgreSQL (port 5432)</li>
  <li><strong>redis</strong> - Redis cache (port 6379)</li>
  <li><strong>kafka</strong> - Apache Kafka (port 9092)</li>
  <li><strong>zookeeper</strong> - Kafka coordination (port 2181)</li>
  <li><strong>consumer</strong> - Moving average processor</li>
  <li><strong>adminer</strong> - Database admin UI (port 8080)</li>
</ul>

<h2>📊 Database Schema</h2>
<pre><code>CREATE TABLE raw_market_data (...);
CREATE TABLE processed_prices (...);
CREATE TABLE moving_averages (...);
CREATE TABLE polling_jobs (...);</code></pre>

<h2>🔄 Data Flow</h2>
<ol>
  <li>Client Request → API receives price request</li>
  <li>External API Call → Fetch from Finnhub API</li>
  <li>Raw Storage → Store in PostgreSQL</li>
  <li>Event Publishing → Send to Kafka</li>
  <li>Stream Processing → Consumer calculates average</li>
  <li>Processed Storage → Save result in DB</li>
</ol>

<h3>Moving Average Algorithm</h3>
<pre><code>def calculate_moving_average(symbol: str, new_price: float) -> float:
    recent_prices = get_recent_prices(symbol, limit=4)
    all_prices = [new_price] + recent_prices
    return sum(all_prices) / len(all_prices)</code></pre>

<h2>🛠️ Local Development</h2>
<pre><code>python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements/dev.txt
export DATABASE_URL=...
uvicorn app.main:app --reload
python scripts/run_consumer.py</code></pre>

<h3>Linting and Format</h3>
<pre><code>black app
isort app
flake8 app
mypy app</code></pre>

<h2>📈 Performance & Monitoring</h2>
<ul>
  <li>Response Time: &lt; 200ms</li>
  <li>Throughput: 1000+ reqs/min</li>
  <li>Monitoring via logs, Adminer, Swagger</li>
</ul>

<h2>🔧 Configuration</h2>
<pre><code>DATABASE_URL=...
KAFKA_BOOTSTRAP_SERVERS=...
FINNHUB_API_KEY=...
MOVING_AVERAGE_WINDOW=5</code></pre>

<h2>🚨 Troubleshooting</h2>
<pre><code>docker-compose ps
docker-compose logs api
psql -U user -d market_data -c "SELECT 1"
kafka-topics --list --bootstrap-server localhost:9092</code></pre>

<h2>🧰 Testing</h2>
<pre><code>curl http://localhost:8000/health
curl http://localhost:8000/api/v1/prices/latest?symbol=AAPL</code></pre>

<h2>📚 Project Structure</h2>
<pre><code>market-data-service/
├── app/
├── docker/
├── scripts/
├── requirements/
├── .env.example
├── README.md
└── LICENSE</code></pre>

<h2>🔐 Security</h2>
<ul>
  <li>Input validation</li>
  <li>Rate limiting</li>
  <li>No sensitive logs</li>
  <li>Non-root Docker user</li>
</ul>
</body>
</html>
