from enum import StrEnum

from lib.utils.schemas.base import StrEnumChoices


class LevelDifficulty(StrEnumChoices):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"


class ResourceType(StrEnum):
    WOOD = "wood"
    SCRAPS = "scraps"
    KEGS = "kegs"
    BIG_KEGS = "big_kegs"
    CHESTS = "chests"
    KEYS = "keys"


class ResourceActionSubtype(StrEnum):
    START_SEASON_LEVEL = "start_season_level"
    WIN_SEASON_LEVEL = "win_season_level"
    BONUS_REWARD = "bonus_reward"


class CardActionSubtype(StrEnum):
    CRAFT_CARD = "craft_card"
    CRAFT_LEADER = "craft_leader"
    MILL_CARD = "mill_card"
    MILL_LEADER = "mill_leader"


class CardColorName(StrEnum):
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"
