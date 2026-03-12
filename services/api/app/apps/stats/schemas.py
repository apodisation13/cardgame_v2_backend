from typing import TypedDict

from lib.utils.schemas import Base
from lib.utils.schemas.game import UserStatsRecordType


class GameStats(Base):
    play: int
    win: int
    winrate: int | float


class CardsStats(TypedDict):
    total: int
    open: int


class LeadersStats(TypedDict):
    total: int
    open: int


class SeasonsStats(TypedDict):
    total: int
    finished: int


class LevelsStats(TypedDict):
    total: int
    finished: int


class GetStatsResponse(Base):
    stats: dict[str, GameStats]
    cards: CardsStats
    leaders: LeadersStats
    seasons: SeasonsStats
    levels: LevelsStats


class PostStatsRequest(Base):
    user_deck_id: int
    type: UserStatsRecordType
