from lib.utils.models import BaseModel
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column


class Type(BaseModel):
    __tablename__ = "types"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Type(id={self.id}, name='{self.name}')>"


class Ability(BaseModel):
    __tablename__ = "abilities"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(32),
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

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    name: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<Passive ability(id={self.id}, name='{self.name}')>"
