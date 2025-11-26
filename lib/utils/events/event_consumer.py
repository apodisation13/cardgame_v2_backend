import json
import logging

from aiokafka import AIOKafkaConsumer

from lib.utils.config.base import BaseConfig
from lib.utils.db.pool import Database
from lib.utils.events.event_processor import EventProcessor
from lib.utils.schemas.events import EventMessage

logger = logging.getLogger(__name__)


class EventConsumer:
    def __init__(
        self,
        config: BaseConfig,
    ):
        self.config = config

        self.consumer = None
        self.running = False
        self.db = None

    async def start_consuming(self) -> None:
        """Запуск потребителя событий"""
        db = Database(self.config)
        await db.connect()
        self.db = db

        logger.info("Starting event consumer...")

        self.consumer = AIOKafkaConsumer(
            self.config.KAFKA_TOPIC,
            bootstrap_servers=self.config.KAFKA_BOOTSTRAP_SERVERS,
            group_id="event-processor",
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest'
        )

        await self.consumer.start()
        self.running = True

        try:
            async for message in self.consumer:
                if not self.running:
                    break

                try:
                    message_value: dict = message.value
                    print("STR51", type(message_value), message_value)
                    event_message = EventMessage(
                        id=message_value['id'],
                        event_type=message_value['event_type'],
                        payload=message_value['payload'],
                    )
                    await self.process_message(event_message)
                    logger.info(f"Processed event: {event_message.event_type}")

                except Exception as e:
                    logger.error(f"Error processing message: {e}")

        except Exception as e:
            logger.error(f"Consumer error: {e}")
        finally:
            await self.stop()

    async def process_message(
        self,
        event_message: EventMessage,
    ):
        """Обработка одного сообщения"""
        processor = EventProcessor(
            db=self.db,
            config=self.config,
        )

        try:
            await processor.process_event(event_message=event_message)

        except Exception as e:
            logger.error(f"Error processing event: {e}")
        finally:
            await self.db.disconnect()

    async def stop(self):
        """Остановка потребителя"""
        self.running = False
        if self.consumer:
            await self.consumer.stop()
