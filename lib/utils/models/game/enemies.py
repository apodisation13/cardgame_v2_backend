from typing import Optional

from sqlalchemy import Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import mapped_column, Mapped, relationship

from lib.utils.models import BaseModel


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

    enemies: Mapped[list["Enemy"]] = relationship(
        "Enemy",
        back_populates="move",
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

    enemies: Mapped[list["Enemy"]] = relationship(
        "Enemy",
        back_populates="passive_ability",
    )
    enemy_leaders: Mapped[list["EnemyLeader"]] = relationship(
        "EnemyLeader",
        back_populates="passive_ability",
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

    enemy_leaders: Mapped[list["EnemyLeader"]] = relationship(
        "EnemyLeader",
        back_populates="ability",
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

    enemies: Mapped[list["Enemy"]] = relationship(
        "Enemy",
        back_populates="deathwish",
    )


class Enemy(BaseModel):
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
    image: Mapped[str] = mapped_column(
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
    damage: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    hp: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    base_hp: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    shield: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
    )
    has_passive: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
    )
    has_passive_in_field: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
    )
    has_passive_in_deck: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
    )
    has_passive_in_grave: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
    )
    passive_ability_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("enemy_passive_abilities.id", ondelete="RESTRICT"),
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
        server_default='false',
    )
    each_tick: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
    )
    has_deathwish: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
    )
    deathwish_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("deathwishes.id", ondelete="RESTRICT"),
        nullable=True,
    )
    deathwish_value: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )

    # Relationships
    faction: Mapped["Faction"] = relationship(
        "Faction",
        back_populates="enemies",
    )
    color: Mapped["Color"] = relationship(
        "Color",
        back_populates="enemies",
    )
    move: Mapped["Move"] = relationship(
        "Move",
        back_populates="enemies",
    )
    passive_ability: Mapped[Optional["EnemyPassiveAbility"]] = relationship(
        "EnemyPassiveAbility",
        back_populates="enemies",
    )
    deathwish: Mapped[Optional["Deathwish"]] = relationship(
        "Deathwish",
        back_populates="enemies",
    )

    def __repr__(self) -> str:
        return f"<Enemy(id={self.id}, name='{self.name}', damage={self.damage}, hp={self.hp})>"

    def __str__(self) -> str:
        return f'{self.id}:{self.name}, {self.faction}, {self.color}, damage {self.damage}, hp {self.hp}, move {self.move.name}, shield {self.shield}'


class EnemyLeader(BaseModel):
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
    image: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    faction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("factions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    hp: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    base_hp: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    ability_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("enemy_leader_abilities.id", ondelete="RESTRICT"),
        nullable=True,
    )
    has_passive: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
    )
    passive_ability_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("enemy_passive_abilities.id", ondelete="RESTRICT"),
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
        server_default='false',
    )
    each_tick: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default='false',
    )

    # Relationships
    faction: Mapped["Faction"] = relationship(
        "Faction",
        back_populates="enemy_leaders",
    )
    ability: Mapped[Optional["EnemyLeaderAbility"]] = relationship(
        "EnemyLeaderAbility",
        back_populates="enemy_leaders",
    )
    passive_ability: Mapped[Optional["EnemyPassiveAbility"]] = relationship(
        "EnemyPassiveAbility",
        back_populates="enemy_leaders",
    )

    def __repr__(self) -> str:
        return f"<EnemyLeader(id={self.id}, name='{self.name}', hp={self.hp})>"

    def __str__(self) -> str:
        return f'{self.id} - {self.name}, hp {self.hp}, passive {self.has_passive}, ability - {self.ability}, passive - {self.passive_ability}'
