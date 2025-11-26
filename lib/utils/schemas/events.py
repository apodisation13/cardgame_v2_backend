from uuid import UUID, uuid4

from pydantic import Field, ConfigDict, model_serializer

from lib.utils.events.event_types import EventType
from lib.utils.schemas import Base


class EventMessage(Base):
    id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    payload: dict

    @model_serializer
    def serialize_model(self) -> dict:
        return {
            'id': str(self.id),
            'event_type': self.event_type.value,
            'payload': self.payload,
        }


class ActionConfigData(Base):
    type: str
    conditions: bool | list[dict]
    receiver: str | None
