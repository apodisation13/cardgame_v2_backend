from enum import StrEnum

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
