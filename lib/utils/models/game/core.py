from typing import Any

from sqlalchemy.dialects.postgresql import JSONB

from lib.utils.models import BaseModel
from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Faction(BaseModel):
    __tablename__ = "factions"
    __table_args__ = (
        UniqueConstraint('name', name='uq_faction_name'),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    leaders: Mapped[list["Leader"]] = relationship(
        "Leader",
        back_populates="faction",
    )
    cards: Mapped[list["Card"]] = relationship(
        "Card",
        back_populates="faction",
    )
    enemies: Mapped[list["Enemy"]] = relationship(
        "Enemy",
        back_populates="faction",
    )
    enemy_leaders: Mapped[list["EnemyLeader"]] = relationship(
        "EnemyLeader",
        back_populates="faction",
    )

    def __repr__(self) -> str:
        return f"<Faction(id={self.id}, name='{self.name}')>"


class Color(BaseModel):
    __tablename__ = "colors"
    __table_args__ = (
        UniqueConstraint('name', name='uq_color_name'),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )

    cards: Mapped[list["Card"]] = relationship(
        "Card",
        back_populates="color",
    )
    enemies: Mapped[list["Enemy"]] = relationship(
        "Enemy",
        back_populates="color",
    )

    def __repr__(self) -> str:
        return f"<Color(id={self.id}, name='{self.name}')>"


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

    def __repr__(self) -> str:
        return f"<GameConstant(id={self.id})>"
