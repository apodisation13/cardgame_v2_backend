from enum import StrEnum
from uuid import UUID, uuid4

from lib.utils.events.event_types import EventType
from lib.utils.schemas import Base
from pydantic import Field, model_serializer


class EventMessage(Base):
    id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    payload: dict

    @model_serializer
    def serialize_model(self) -> dict:
        return {
            "id": str(self.id),
            "event_type": self.event_type.value,
            "payload": self.payload,
        }


class ActionConfigData(Base):
    type: str
    conditions: bool | list[dict]
    receiver: str | None = None
    message: str | None = None


class ActionContext(Base):
    event_type: EventType
    payload: dict
    action_config: ActionConfigData


class AddResourcesSubtype(StrEnum):
    DIRECT = "direct"
    SUCCESS_PAYMENT = "success_payment"

    @classmethod
    def processable_subtypes(cls) -> set:
        return {cls.DIRECT, cls.SUCCESS_PAYMENT}
