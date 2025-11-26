import json

from aiokafka import AIOKafkaProducer

from lib.utils.config.base import BaseConfig
from lib.utils.db.pool import Database
from lib.utils.events.event_types import EventType, EventProcessingState
from lib.utils.schemas.events import EventMessage



class EventSender:
    def __init__(
        self,
        config: BaseConfig,
        db: Database,
    ):
        self.config = config
        self.db = db

        self._producer = None
        self._initialized = False


    async def _ensure_initialized(self) -> None:
        """Инициализирует producer если еще не инициализирован"""
        if not self._initialized:
            self._producer = AIOKafkaProducer(
                bootstrap_servers=self.config.KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self._producer.start()
            self._initialized = True

    async def send_event(
        self,
        event_type: EventType,
        payload: dict,
    ) -> None:
        """Отправка события в Kafka"""
        await self._ensure_initialized()

        message = EventMessage(
            event_type=event_type,
            payload=payload,
        )
        topic = self.config.KAFKA_TOPIC

        try:
            await self._producer.send_and_wait(topic, message.model_dump(mode="json"))
            await self._log_event(message=message, payload=payload)
        except Exception as e:
            # При ошибке сбрасываем состояние и пробуем переинициализировать при следующем вызове
            self._initialized = False
            if self._producer:
                await self._producer.stop()
                self._producer = None
            raise Exception(f"Failed to send event to Kafka: {e}")

    async def _log_event(
        self,
        message: EventMessage,
        payload: dict,
    ) -> None:
        async with self.db.connection() as connection:
            await connection.execute(
                """
                INSERT INTO event_log 
                (id, type, state, payload)
                VALUES ($1, $2, $3, $4)
                """,
                message.id,
                message.event_type,
                EventProcessingState.SENT,
                json.dumps(payload),
            )


# глобальный инстанс сендера
_event_sender: EventSender | None = None


async def get_event_sender(
    config: BaseConfig,
) -> EventSender:
    global _event_sender
    if _event_sender is None:
        db = Database()
        await db.connect()
        _event_sender = EventSender(
            config=config,
            db=db,
        )
    return _event_sender


async def create_event(
    event_type: EventType,
    payload: dict,
    config: BaseConfig,
) -> None:
    sender: EventSender = await get_event_sender(config)
    await sender.send_event(event_type=event_type, payload=payload)
