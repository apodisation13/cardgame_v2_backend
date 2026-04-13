from typing import Any, Optional

from lib.utils.models import BaseModel, TimestampMixin
from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class Move(BaseModel):
    __tablename__ = "moves"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class EnemyPassiveAbility(BaseModel):
    __tablename__ = "enemy_passive_abilities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class EnemyLeaderAbility(BaseModel):
    __tablename__ = "enemy_leader_abilities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class Deathwish(BaseModel):
    __tablename__ = "deathwishes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class Enemy(BaseModel, TimestampMixin):
    __tablename__ = "enemies"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
    )
    image_original: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    faction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("factions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    color_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("colors.id", ondelete="RESTRICT"),
        nullable=False,
    )
    move_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("moves.id", ondelete="RESTRICT"),
        nullable=False,
    )
    passive_ability_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("enemy_passive_abilities.id", ondelete="RESTRICT"),
        nullable=True,
    )
    deathwish_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("deathwishes.id", ondelete="RESTRICT"),
        nullable=True,
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        server_default="{}",
        nullable=False,
    )


class EnemyLeader(BaseModel, TimestampMixin):
    __tablename__ = "enemy_leaders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
    )
    image_original: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    faction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("factions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    ability_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("enemy_leader_abilities.id", ondelete="RESTRICT"),
        nullable=True,
    )
    passive_ability_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("enemy_passive_abilities.id", ondelete="RESTRICT"),
        nullable=True,
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        server_default="{}",
        nullable=False,
    )
