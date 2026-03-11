from typing import Dict, TypedDict

from lib.utils.schemas import Base


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
    stats: Dict[str, GameStats]
    cards: CardsStats
    leaders: LeadersStats
    seasons: SeasonsStats
    levels: LevelsStats
