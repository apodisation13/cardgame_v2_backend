from lib.utils.models import BaseModel, TimestampMixin
from sqlalchemy import Boolean, ForeignKey, Integer, UniqueConstraint, String
from sqlalchemy.orm import Mapped, mapped_column


class Leaderboard(BaseModel, TimestampMixin):
    __tablename__ = "leaderboard"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "leader_id",
            "mode",
            name="uq_leaderboard_user_leader_mode",
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
    )
    leader_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("leaders.id", ondelete="RESTRICT"),
    )
    mode: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
    )
    max_kills: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
    )


class UserStats(BaseModel, TimestampMixin):
    __tablename__ = "user_stats"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "faction_id",
            "type",
            name="uq_userstats_user_faction_type",
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
    )
    faction_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("factions.id", ondelete="RESTRICT"),
    )
    type: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
    )
    count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="1",
    )
