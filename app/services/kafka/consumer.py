import json
import logging
from typing import List, Dict, Any
from confluent_kafka import Consumer, KafkaError
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import SessionLocal
from app.models.price import ProcessedPrice, MovingAverage
from app.core.config import settings
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class MovingAverageConsumer:
    """Kafka consumer for calculating moving averages"""
    
    def __init__(self):
        self.config = {
            'bootstrap.servers': settings.kafka_bootstrap_servers,
            'group.id': settings.kafka_group_id,
            'client.id': 'ma-consumer',
            'auto.offset.reset': 'latest',
            'enable.auto.commit': True,
            'auto.commit.interval.ms': 1000,
        }
        self.consumer = Consumer(self.config)
        self.topic = settings.kafka_topic_price_events
        self.window_size = settings.moving_average_window
        self.running = False
    
    def calculate_moving_average(self, db: Session, symbol: str, new_price: float) -> float:
        """Calculate 5-point moving average for a symbol"""
        try:
            # Get the last 4 prices (we'll add the new one to make 5)
            recent_prices = db.query(ProcessedPrice.price).filter(
                ProcessedPrice.symbol == symbol
            ).order_by(desc(ProcessedPrice.timestamp)).limit(self.window_size - 1).all()
            
            # Include the new price
            prices = [new_price] + [p.price for p in recent_prices]
            
            # If we don't have enough data points, return the average of what we have
            if len(prices) < self.window_size:
                return sum(prices) / len(prices)
            
            # Calculate moving average for exactly window_size points
            return sum(prices[:self.window_size]) / self.window_size
            
        except Exception as e:
            logger.error(f"Error calculating moving average for {symbol}: {e}")
            return new_price  # Fallback to current price
    
    def process_price_event(self, message_value: str):
        """Process a single price event message"""
        try:
            # Parse the message
            data = json.loads(message_value)
            symbol = data['symbol']
            price = data['price']
            timestamp_str = data['timestamp']
            source = data['source']
            
            # Parse timestamp
            if timestamp_str.endswith('Z'):
                timestamp_str = timestamp_str[:-1]
            timestamp = datetime.fromisoformat(timestamp_str)
            
            db = SessionLocal()
            try:
                # Store processed price
                processed_price = ProcessedPrice(
                    symbol=symbol,
                    price=price,
                    timestamp=timestamp,
                    provider=source
                )
                db.add(processed_price)
                db.commit()
                
                # Calculate and store moving average
                ma_value = self.calculate_moving_average(db, symbol, price)
                
                moving_avg = MovingAverage(
                    symbol=symbol,
                    window_size=self.window_size,
                    value=ma_value,
                    timestamp=datetime.utcnow()
                )
                db.add(moving_avg)
                db.commit()
                
                logger.info(f"Processed price event for {symbol}: price={price}, MA={ma_value:.2f}")
                
            finally:
                db.close()
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse message JSON: {e}")
        except Exception as e:
            logger.error(f"Error processing price event: {e}")
    
    async def start_consuming(self):
        """Start consuming messages"""
        self.consumer.subscribe([self.topic])
        self.running = True
        
        logger.info(f"Started consuming from topic: {self.topic}")
        
        try:
            while self.running:
                # Poll for messages
                msg = self.consumer.poll(timeout=1.0)
                
                if msg is None:
                    # No message available, continue polling
                    await asyncio.sleep(0.1)
                    continue
                
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        # End of partition - not an error
                        continue
                    else:
                        logger.error(f"Consumer error: {msg.error()}")
                        continue
                
                # Process the message
                try:
                    message_value = msg.value().decode('utf-8')
                    self.process_price_event(message_value)
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                
                await asyncio.sleep(0.01)  # Small delay to prevent CPU spinning
                
        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        finally:
            self.consumer.close()
            logger.info("Consumer closed")
    
    def stop(self):
        """Stop consuming messages"""
        self.running = False