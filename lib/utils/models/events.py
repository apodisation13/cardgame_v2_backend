from typing import Any
from uuid import UUID

from lib.utils.models import BaseModel, TimestampMixin
from sqlalchemy import Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column


class Event(BaseModel):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(String(255), unique=True)
    processing: Mapped[list[dict[str, Any]]] = mapped_column(
        JSONB,
        server_default="[]",
        nullable=False,
    )


class EventLog(BaseModel, TimestampMixin):
    __tablename__ = "event_log"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
        nullable=False,
    )
    type: Mapped[str] = mapped_column(String(255))
    state: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        server_default="{}",
        nullable=False,
    )
