from typing import Any

from lib.utils.models import BaseModel
from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class Faction(BaseModel):
    __tablename__ = "factions"
    __table_args__ = (UniqueConstraint("name", name="uq_faction_name"),)

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )


class Color(BaseModel):
    __tablename__ = "colors"
    __table_args__ = (UniqueConstraint("name", name="uq_color_name"),)

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )


class GameConstants(BaseModel):
    __tablename__ = "game_constants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        server_default="{}",
        nullable=False,
    )
