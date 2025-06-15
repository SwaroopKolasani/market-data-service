"""Kafka services for streaming data processing"""

from .producer import PriceEventProducer
from .consumer import MovingAverageConsumer

__all__ = ["PriceEventProducer", "MovingAverageConsumer"]
