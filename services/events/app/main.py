import asyncio
import logging.config
import os
import sys


# Добавляем корневую директорию проекта в Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from lib.utils.events.event_consumer import EventConsumer
from services.events.app.config import get_config


async def main():
    config = get_config()

    logger = logging.getLogger(__name__)
    logging.config.dictConfig(config.LOGGING)
    logging.getLogger('aiokafka').setLevel(logging.ERROR)

    logger.info("Starting Event Processor...")

    consumer = EventConsumer(config=config)
    await consumer.start_consuming()


if __name__ == "__main__":
    asyncio.run(main())
