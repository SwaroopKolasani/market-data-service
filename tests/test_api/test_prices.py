import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

def test_health_check(client: TestClient):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_root_endpoint(client: TestClient):
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data

@patch('app.services.price_service.PriceService.get_latest_price')
async def test_get_latest_price_success(mock_get_price, client: TestClient):
    """Test successful price retrieval"""
    # Mock the price service response
    mock_get_price.return_value = {
        "symbol": "AAPL",
        "price": 150.25,
        "timestamp": "2024-03-20T10:30:00Z",
        "provider": "yahoo_finance"
    }
    
    response = client.get("/api/v1/prices/latest?symbol=AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["price"] == 150.25

def test_get_latest_price_missing_symbol(client: TestClient):
    """Test price endpoint without symbol parameter"""
    response = client.get("/api/v1/prices/latest")
    assert response.status_code == 422  # Validation error

def test_create_poll_job_success(client: TestClient):
    """Test successful poll job creation"""
    request_data = {
        "symbols": ["AAPL", "MSFT"],
        "interval": 60,
        "provider": "yahoo_finance"
    }
    
    with patch('app.services.price_service.PriceService.create_polling_job') as mock_create_job:
        mock_create_job.return_value = {
            "job_id": "poll_12345",
            "status": "accepted",
            "config": request_data
        }
        
        response = client.post("/api/v1/prices/poll", json=request_data)
        assert response.status_code == 202
        data = response.json()
        assert data["status"] == "accepted"
        assert "job_id" in data

def test_create_poll_job_invalid_interval(client: TestClient):
    """Test poll job creation with invalid interval"""
    request_data = {
        "symbols": ["AAPL"],
        "interval": 30,  # Too short
        "provider": "yahoo_finance"
    }
    
    response = client.post("/api/v1/prices/poll", json=request_data)
    assert response.status_code == 422  # Validation error