from enum import StrEnum
import uuid

from pydantic import BaseModel, ConfigDict


class Base(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )


class StrEnumChoices(StrEnum):
    @classmethod
    def choices(cls) -> list[tuple]:
        return [(item, item) for item in cls]


def generate_uuid4_str() -> str:
    return str(uuid.uuid4())
