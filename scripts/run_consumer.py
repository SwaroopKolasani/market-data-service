#!/usr/bin/env python3
"""
Standalone script to run the Kafka consumer for moving averages
"""
import asyncio
import logging
import sys
import os

# Add the app directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.kafka.consumer import MovingAverageConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Main function to run the consumer"""
    consumer = MovingAverageConsumer()
    
    try:
        logger.info("Starting Moving Average Consumer...")
        await consumer.start_consuming()
    except KeyboardInterrupt:
        logger.info("Shutting down consumer...")
        consumer.stop()
    except Exception as e:
        logger.error(f"Consumer error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())