from typing import Any, Optional

from lib.utils.models import BaseModel, TimestampMixin
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class Type(BaseModel):
    __tablename__ = "types"
    __table_args__ = (UniqueConstraint("name", name="uq_type_name"),)

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )


class Ability(BaseModel):
    __tablename__ = "abilities"
    __table_args__ = (UniqueConstraint("name", name="uq_ability_name"),)

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class PassiveAbility(BaseModel):
    __tablename__ = "passive_abilities"
    __table_args__ = (UniqueConstraint("name", name="uq_passive_ability_name"),)

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )


class Leader(BaseModel, TimestampMixin):
    __tablename__ = "leaders"
    __table_args__ = (UniqueConstraint("name", name="uq_leader_name"),)

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    image_original: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    unlocked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
    )
    faction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("factions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    ability_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("abilities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    passive_ability_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("passive_abilities.id", ondelete="RESTRICT"),
        nullable=True,
    )
    newly_added: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        server_default="{}",
        nullable=False,
    )


class Card(BaseModel, TimestampMixin):
    __tablename__ = "cards"

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
    unlocked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
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
    type_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    ability_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("abilities.id", ondelete="RESTRICT"),
        nullable=False,
    )
    passive_ability_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("passive_abilities.id", ondelete="RESTRICT"),
        nullable=True,
    )
    newly_added: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    data: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        server_default="{}",
        nullable=False,
    )


class Deck(BaseModel, TimestampMixin):
    __tablename__ = "decks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    leader_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("leaders.id", ondelete="RESTRICT"),
        nullable=False,
    )


class CardDeck(BaseModel, TimestampMixin):
    __tablename__ = "card_decks"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    deck_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("decks.id", ondelete="RESTRICT"),
        nullable=False,
    )
    card_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cards.id", ondelete="RESTRICT"),
        nullable=False,
    )
