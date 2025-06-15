import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.price_service import PriceService
from app.models.price import RawMarketData

@pytest.mark.asyncio
async def test_get_latest_price_yahoo_finance(test_db):
    """Test getting latest price from Yahoo Finance"""
    service = PriceService()
    
    with patch('app.services.market_data.get_provider') as mock_get_provider:
        # Mock provider
        mock_provider = AsyncMock()
        mock_provider.get_latest_price.return_value = {
            "symbol": "AAPL",
            "price": 150.25,
            "timestamp": "2024-03-20T10:30:00Z",
            "provider": "yahoo_finance",
            "raw_response": {"test": "data"}
        }
        mock_get_provider.return_value = mock_provider
        
        # Mock Kafka producer
        with patch.object(service, 'producer') as mock_producer:
            mock_producer.produce_price_event = AsyncMock()
            
            result = await service.get_latest_price(test_db, "AAPL")
            
            assert result["symbol"] == "AAPL"
            assert result["price"] == 150.25
            assert result["provider"] == "yahoo_finance"
            
            # Verify raw data was stored
            raw_data = test_db.query(RawMarketData).first()
            assert raw_data is not None
            assert raw_data.symbol == "AAPL"

@pytest.mark.asyncio
async def test_create_polling_job(test_db):
    """Test creating a polling job"""
    service = PriceService()
    
    result = await service.create_polling_job(
        test_db, 
        ["AAPL", "MSFT"], 
        60, 
        "yahoo_finance"
    )
    
    assert result["status"] == "accepted"
    assert "job_id" in result
    assert result["config"]["symbols"] == ["AAPL", "MSFT"]
    assert result["config"]["interval"] == 60
