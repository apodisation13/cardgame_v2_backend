from enum import StrEnum

from lib.utils.schemas.base import StrEnumChoices


class EventType(StrEnumChoices):
    EVENT_1 = "event_1"
    EVENT_2 = "event_2"

    @classmethod
    def choices(cls) -> list[tuple]:
        return [(item, item) for item in cls]


class EventProcessingState(StrEnum):
    SENT = "sent"
    IN_PROGRESS = "in_progress"
    SUCCESS = "success"
    FAILED = "failed"
