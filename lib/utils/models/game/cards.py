from typing import Optional

from lib.utils.models import BaseModel
from sqlalchemy import Integer, String, Text, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class Type(BaseModel):
    __tablename__ = "types"
    __table_args__ = (
        UniqueConstraint('name', name='uq_type_name'),
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

    def __repr__(self) -> str:
        return f"<Type(id={self.id}, name='{self.name}')>"


class Ability(BaseModel):
    __tablename__ = "abilities"
    __table_args__ = (
        UniqueConstraint('name', name='uq_ability_name'),
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
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Ability(id={self.id}, name='{self.name}')>"


class PassiveAbility(BaseModel):
    __tablename__ = "passive_abilities"
    __table_args__ = (
        UniqueConstraint('name', name='uq_passive_ability_name'),
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
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Passive ability(id={self.id}, name='{self.name}')>"


class Leader(BaseModel):
    __tablename__ = "leaders"
    __table_args__ = (
        UniqueConstraint('name', name='uq_leader_name'),
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
    image_original: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    image_tablet: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    image_phone: Mapped[str] = mapped_column(
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
    damage: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0"
    )
    charges: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1"
    )
    heal: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    has_passive: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    passive_ability_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("passive_abilities.id", ondelete="RESTRICT"),
        nullable=True,
    )
    value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    timer: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    default_timer: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    reset_timer: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )

    def __repr__(self) -> str:
        return f"<Leader(id={self.id}, name='{self.name}', damage={self.damage}, charges={self.charges})>"

    def __str__(self) -> str:
        return f'{self.name}, ability {self.ability_id}, damage {self.damage} charges {self.charges}'


class Card(BaseModel):
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
    image_tablet: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    image_phone: Mapped[str] = mapped_column(
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
    damage: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    charges: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
    )
    hp: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    heal: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    has_passive: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    has_passive_in_hand: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    has_passive_in_deck: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    has_passive_in_grave: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    passive_ability_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("passive_abilities.id", ondelete="RESTRICT"),
        nullable=True,
    )
    value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    timer: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    default_timer: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    reset_timer: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
    each_tick: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )

    def __repr__(self) -> str:
        return f"<Card(id={self.id}, name='{self.name}', hp={self.hp}, damage={self.damage})>"

    def __str__(self) -> str:
        return f'{self.id} {self.name}, hp {self.hp}, ability {self.ability_id}, damage {self.damage}, heal {self.heal}'


class Deck(BaseModel):
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


class CardDeck(BaseModel):
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
