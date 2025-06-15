import json
import logging
from typing import Dict, Any
from confluent_kafka import Producer
from app.core.config import settings

logger = logging.getLogger(__name__)


class PriceEventProducer:
    """Kafka producer for price events"""

    def __init__(self):
        self.config = {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "client.id": "market-data-producer",
            "acks": "all",  # Wait for all replicas
            "retries": 3,
            "batch.size": 16384,
            "linger.ms": 5,
            "compression.type": "snappy",
        }
        self.producer = Producer(self.config)
        self.topic = settings.kafka_topic_price_events

    def delivery_callback(self, err, msg):
        """Callback for message delivery confirmation"""
        if err:
            logger.error(f"Message delivery failed: {err}")
        else:
            logger.debug(f"Message delivered to {msg.topic()} [{msg.partition()}]")

    async def produce_price_event(self, price_data: Dict[str, Any]):
        """Produce a price event to Kafka"""
        try:
            # Create the message payload
            message = {
                "symbol": price_data["symbol"],
                "price": price_data["price"],
                "timestamp": price_data["timestamp"],
                "source": price_data["provider"],
                "raw_response_id": str(price_data.get("raw_response_id", "")),
            }

            # Serialize to JSON
            value = json.dumps(message).encode("utf-8")

            # Produce the message
            self.producer.produce(
                topic=self.topic, key=price_data["symbol"].encode("utf-8"), value=value, callback=self.delivery_callback
            )

            # Trigger delivery report callbacks
            self.producer.poll(0)

            logger.info(f"Produced price event for {price_data['symbol']}")

        except Exception as e:
            logger.error(f"Failed to produce price event: {e}")
            raise

    def flush(self, timeout: float = 10.0):
        """Flush pending messages"""
        self.producer.flush(timeout)

    def close(self):
        """Close the producer"""
        self.producer.flush()
