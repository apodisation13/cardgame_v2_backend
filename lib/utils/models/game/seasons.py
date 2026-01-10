from typing import Optional

from lib.utils.models import BaseModel
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class Season(BaseModel):
    __tablename__ = "seasons"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    unlocked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
    )


class Level(BaseModel):
    __tablename__ = "levels"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )
    starting_enemies_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="3",
    )
    difficulty: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    unlocked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
    )
    x: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    y: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    season_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("seasons.id", ondelete="RESTRICT"),
        nullable=False,
    )
    enemy_leader_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("enemy_leaders.id", ondelete="RESTRICT"),
        nullable=False,
    )


class LevelRelatedLevels(BaseModel):
    __tablename__ = "level_related_levels"
    __table_args__ = (
        UniqueConstraint(
            'level_id',
            'related_level_id',
            name='uq_level_related_levels',
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    level_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("levels.id", ondelete="RESTRICT"),
        nullable=False,
    )
    related_level_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("levels.id", ondelete="RESTRICT"),
        nullable=False,
    )
    line: Mapped[Optional[str]] = mapped_column(
        String(16),
        nullable=True,
    )
    connection: Mapped[str] = mapped_column(
        String(16),
        nullable=True,
    )


class LevelEnemy(BaseModel):
    __tablename__ = "level_enemies"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    level_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("levels.id", ondelete="RESTRICT"),
        nullable=False,
    )
    enemy_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("enemies.id", ondelete="RESTRICT"),
        nullable=False,
    )
