import json
import logging

from aiokafka import AIOKafkaProducer
from lib.utils.config.base import BaseConfig
from lib.utils.db.pool import Database
from lib.utils.events.event_types import EventProcessingState, EventType
from lib.utils.schemas.events import EventMessage


logger = logging.getLogger(__name__)


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
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            await self._producer.start()
            self._initialized = True

    async def send_event(
        self,
        event_type: EventType,
        payload: dict,
        dedup_key: str | None = None,
    ) -> None:
        """Отправка события в Kafka"""
        logger.info("Sending event %s", event_type)

        message = EventMessage(
            event_type=event_type,
            payload=payload,
            dedup_key=dedup_key,
        )

        inserted = await self._log_event(message=message, payload=payload)
        if not inserted:
            logger.warning("Duplicate event skipped: %s dedup_key=%s", event_type, dedup_key)
            return

        await self._ensure_initialized()

        try:
            await self._producer.send_and_wait(self.config.KAFKA_TOPIC, message.model_dump(mode="json"))
            logger.info("Event %s has been sent", message)
        except Exception as e:
            self._initialized = False
            if self._producer:
                await self._producer.stop()
                self._producer = None
            raise Exception(f"Failed to send event to Kafka: {e}") from e

    async def _log_event(
        self,
        message: EventMessage,
        payload: dict,
    ) -> bool:
        """Возвращает True если запись вставлена, False если дубль по dedup_key"""
        async with self.db.connection() as connection:
            result = await connection.execute(
                """
                INSERT INTO event_log
                (id, type, state, payload, dedup_key)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT (dedup_key) DO NOTHING
                """,
                message.id,
                message.event_type,
                EventProcessingState.SENT,
                payload,
                message.dedup_key,
            )
        return result == "INSERT 0 1"


# глобальный инстанс сендера
_event_sender: EventSender | None = None


async def get_event_sender(
    config: BaseConfig,
) -> EventSender:
    global _event_sender
    if _event_sender is None:
        db = Database(config)
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
    dedup_key: str | None = None,
) -> None:
    sender: EventSender = await get_event_sender(config)
    await sender.send_event(event_type=event_type, payload=payload, dedup_key=dedup_key)
