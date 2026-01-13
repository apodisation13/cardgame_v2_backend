from lib.utils.models import BaseModel
from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column


class UserResource(BaseModel):
    __tablename__ = "user_resources"

    id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        primary_key=True,
    )
    scraps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1000",
    )
    wood: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1000",
    )
    kegs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="3",
    )
    big_kegs: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
    )
    chests: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )
    keys: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="3",
    )


class UserCard(BaseModel):
    __tablename__ = "user_cards"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "card_id",
            name="uq_user_card",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    card_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("cards.id", ondelete="RESTRICT"),
        nullable=False,
    )
    count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )


class UserLeader(BaseModel):
    __tablename__ = "user_leaders"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "leader_id",
            name="uq_user_leader",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    leader_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("leaders.id", ondelete="RESTRICT"),
        nullable=False,
    )
    count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )


class UserDeck(BaseModel):
    __tablename__ = "user_decks"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "deck_id",
            name="uq_user_deck",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    deck_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("decks.id", ondelete="RESTRICT"),
        nullable=False,
    )


class UserLevel(BaseModel):
    __tablename__ = "user_levels"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "level_id",
            name="uq_user_level",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    level_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("levels.id", ondelete="RESTRICT"),
        nullable=False,
    )
    finished: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="false",
    )
