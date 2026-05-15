from enum import StrEnum

from lib.utils.schemas.base import StrEnumChoices


class LevelDifficulty(StrEnumChoices):
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"


class ResourceType(StrEnum):
    SCRAPS = "scraps"
    RAW_BRONZE = "raw_bronze"
    RAW_SILVER = "raw_silver"
    RAW_GOLD = "raw_gold"
    BRONZE_INGOTS = "bronze_ingots"
    SILVER_INGOTS = "silver_ingots"
    GOLD_INGOTS = "gold_ingots"
    CROPS = "crops"
    WOOD = "wood"
    SILK = "silk"
    KEGS = "kegs"
    BIG_KEGS = "big_kegs"
    CHESTS = "chests"
    RARE_GEM = "rare_gem"
    KEYS = "keys"
    MONEY = "money"


class ResourceActionSubtype(StrEnum):
    START_SEASON_LEVEL = "start_season_level"
    WIN_SEASON_LEVEL = "win_season_level"
    OPEN_BONUS_RESOURCE = "open_bonus_resource"
    ACCEPT_KEY_REWARD = "accept_key_reward"
    RESOURCE_TRANSITION = "resource_transition"


class CardActionSubtype(StrEnum):
    CRAFT_CARD = "craft_card"
    CRAFT_LEADER = "craft_leader"
    MILL_CARD = "mill_card"
    MILL_LEADER = "mill_leader"


class CardColorName(StrEnum):
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"


class ResourceTransitionActionType(StrEnum):
    CRAFT = "craft"
    MILL = "mill"
    BUY = "buy"
    SELL = "sell"

    @classmethod
    def to_increase_resources(cls) -> set:
        return {cls.BUY, cls.CRAFT}

    @classmethod
    def to_decrease_resources(cls) -> set:
        return {cls.SELL, cls.MILL}


DEFAULT_RESOURCES_TRANSITIONS = {
    ResourceType.BRONZE_INGOTS: {
        ResourceTransitionActionType.BUY: [{ResourceType.MONEY: -2000}],
        ResourceTransitionActionType.SELL: [{ResourceType.MONEY: 200}],
        ResourceTransitionActionType.CRAFT: [{ResourceType.RAW_BRONZE: -50, ResourceType.MONEY: -200}],
        ResourceTransitionActionType.MILL: [{ResourceType.RAW_BRONZE: 25, ResourceType.MONEY: -100}],
        "step": 1,
        "index": 1,
    },
    ResourceType.SILVER_INGOTS: {
        ResourceTransitionActionType.BUY: [{ResourceType.MONEY: -4000}],
        ResourceTransitionActionType.SELL: [{ResourceType.MONEY: 400}],
        ResourceTransitionActionType.CRAFT: [{ResourceType.RAW_SILVER: -50, ResourceType.MONEY: -400}],
        ResourceTransitionActionType.MILL: [{ResourceType.RAW_SILVER: 25, ResourceType.MONEY: -100}],
        "step": 1,
        "index": 2,
    },
    ResourceType.GOLD_INGOTS: {
        ResourceTransitionActionType.BUY: [{ResourceType.MONEY: -8000}],
        ResourceTransitionActionType.SELL: [{ResourceType.MONEY: 800}],
        ResourceTransitionActionType.CRAFT: [{ResourceType.RAW_GOLD: -50, ResourceType.MONEY: -1000}],
        ResourceTransitionActionType.MILL: [{ResourceType.RAW_GOLD: 25, ResourceType.MONEY: -200}],
        "step": 1,
        "index": 3,
    },
    ResourceType.CROPS: {
        ResourceTransitionActionType.BUY: [{ResourceType.MONEY: -200}],
        ResourceTransitionActionType.SELL: [{ResourceType.MONEY: 20}],
        "step": 100,
        "index": 4,
    },
    ResourceType.WOOD: {
        ResourceTransitionActionType.BUY: [{ResourceType.MONEY: -400}],
        ResourceTransitionActionType.SELL: [{ResourceType.MONEY: 40}],
        "step": 100,
        "index": 5,
    },
    ResourceType.SILK: {
        ResourceTransitionActionType.BUY: [{ResourceType.MONEY: -1000}],
        ResourceTransitionActionType.SELL: [{ResourceType.MONEY: 100}],
        ResourceTransitionActionType.CRAFT: [
            {ResourceType.SCRAPS: -1000, ResourceType.RAW_GOLD: -2, ResourceType.MONEY: -1000},
        ],
        ResourceTransitionActionType.MILL: [
            {ResourceType.SCRAPS: 100, ResourceType.RAW_GOLD: 1, ResourceType.MONEY: -1000},
        ],
        "step": 1,
        "index": 6,
    },
    ResourceType.KEGS: {
        ResourceTransitionActionType.BUY: [{ResourceType.MONEY: -10000}],
        ResourceTransitionActionType.SELL: [{ResourceType.MONEY: 1000}],
        ResourceTransitionActionType.CRAFT: [
            {ResourceType.CROPS: -100, ResourceType.WOOD: -100, ResourceType.MONEY: -1000},
            {ResourceType.CROPS: -100, ResourceType.RAW_BRONZE: -60, ResourceType.MONEY: -1000},
            {ResourceType.CROPS: -100, ResourceType.BRONZE_INGOTS: -10, ResourceType.MONEY: -1000},
        ],
        "step": 1,
        "index": 7,
    },
    ResourceType.BIG_KEGS: {
        ResourceTransitionActionType.BUY: [{ResourceType.MONEY: -20000}],
        ResourceTransitionActionType.SELL: [{ResourceType.MONEY: 2000}],
        ResourceTransitionActionType.CRAFT: [
            {ResourceType.CROPS: -200, ResourceType.WOOD: -200, ResourceType.MONEY: -2000},
            {ResourceType.CROPS: -200, ResourceType.RAW_SILVER: -160, ResourceType.MONEY: -2000},
            {ResourceType.CROPS: -200, ResourceType.SILVER_INGOTS: -10, ResourceType.MONEY: -2000},
        ],
        "step": 1,
        "index": 8,
    },
    ResourceType.SCRAPS: {
        ResourceTransitionActionType.BUY: [{ResourceType.MONEY: -1000}],
        ResourceTransitionActionType.SELL: [{ResourceType.MONEY: 100}],
        "step": 100,
        "index": 9,
    },
    ResourceType.CHESTS: {
        ResourceTransitionActionType.BUY: [{ResourceType.MONEY: -100000}],
        ResourceTransitionActionType.SELL: [{ResourceType.MONEY: 5000}],
        ResourceTransitionActionType.CRAFT: [
            {ResourceType.WOOD: -2000, ResourceType.RAW_GOLD: -5, ResourceType.SILK: -5, ResourceType.MONEY: -20000},
            {ResourceType.WOOD: -2000, ResourceType.GOLD_INGOTS: -5, ResourceType.MONEY: -20000},
        ],
        "step": 1,
        "index": 10,
    },
}

DEFAULT_KEY_REWARDS = {
    ResourceType.SCRAPS: {
        "min": 100,
        "max": 200,
        "probability": 17,
        "type": "diapason",
    },
    ResourceType.RAW_BRONZE: {
        "min": 30,
        "max": 50,
        "probability": 6,
        "type": "diapason",
    },
    ResourceType.RAW_SILVER: {
        "min": 25,
        "max": 50,
        "probability": 4,
        "type": "diapason",
    },
    ResourceType.RAW_GOLD: {
        "min": 15,
        "max": 30,
        "probability": 3,
        "type": "diapason",
    },
    ResourceType.BRONZE_INGOTS: {
        "min": 1,
        "max": 3,
        "probability": 5,
        "type": "diapason",
    },
    ResourceType.SILVER_INGOTS: {
        "min": 1,
        "max": 3,
        "probability": 4,
        "type": "diapason",
    },
    ResourceType.GOLD_INGOTS: {
        "min": 1,
        "max": 2,
        "probability": 3,
        "type": "diapason",
    },
    ResourceType.CROPS: {
        "min": 175,
        "max": 275,
        "probability": 17,
        "type": "diapason",
    },
    ResourceType.WOOD: {
        "min": 150,
        "max": 250,
        "probability": 17,
        "type": "diapason",
    },
    ResourceType.SILK: {
        "min": 2,
        "max": 3,
        "probability": 2,
        "type": "diapason",
    },
    ResourceType.KEGS: {
        "value": 1,
        "probability": 1,
        "type": "simple",
    },
    ResourceType.BIG_KEGS: {
        "value": 1,
        "probability": 0.5,
        "type": "simple",
    },
    ResourceType.CHESTS: {
        "value": 1,
        "probability": 0.3,
        "type": "simple",
    },
    ResourceType.RARE_GEM: {
        "value": 1,
        "probability": 0.2,
        "type": "simple",
    },
    ResourceType.MONEY: {
        "min": 1000,
        "max": 2000,
        "probability": 20,
        "type": "diapason",
    },
}

DEFAULT_WIN_LEVEL_REWARDS = {
    LevelDifficulty.EASY: {
        ResourceType.CROPS: {
            "min": 200,
            "max": 300,
            "type": "diapason",
        },
        ResourceType.MONEY: {
            "min": 1400,
            "max": 1600,
            "type": "diapason",
        },
        ResourceType.SCRAPS: {
            "min": 100,
            "max": 200,
            "type": "diapason",
        },
        ResourceType.KEGS: {
            "value": 1,
            "type": "simple",
            "probability": 1,
        },
        ResourceType.BIG_KEGS: {
            "value": 1,
            "type": "simple",
            "probability": 0.5,
        },
    },
    LevelDifficulty.NORMAL: {
        ResourceType.CROPS: {
            "min": 400,
            "max": 500,
            "type": "diapason",
        },
        ResourceType.WOOD: {
            "min": 200,
            "max": 300,
            "type": "diapason",
        },
        ResourceType.MONEY: {
            "min": 2500,
            "max": 3100,
            "type": "diapason",
        },
        ResourceType.SCRAPS: {
            "min": 150,
            "max": 250,
            "type": "diapason",
        },
        ResourceType.KEGS: {
            "value": 1,
            "type": "simple",
            "probability": 1,
        },
        ResourceType.BIG_KEGS: {
            "value": 1,
            "type": "simple",
            "probability": 0.5,
        },
    },
    LevelDifficulty.HARD: {
        ResourceType.CROPS: {
            "min": 1000,
            "max": 1150,
            "type": "diapason",
        },
        ResourceType.WOOD: {
            "min": 400,
            "max": 500,
            "type": "diapason",
        },
        ResourceType.MONEY: {
            "min": 4000,
            "max": 4300,
            "type": "diapason",
        },
        ResourceType.SCRAPS: {
            "min": 300,
            "max": 450,
            "type": "diapason",
        },
        ResourceType.SILK: {
            "min": 3,
            "max": 5,
            "type": "diapason",
        },
        ResourceType.KEGS: {
            "value": 1,
            "type": "simple",
            "probability": 2,
        },
        ResourceType.BIG_KEGS: {
            "value": 1,
            "type": "simple",
            "probability": 1,
        },
    },
}

DEFAULT_START_LEVEL_PRICES = {
    "levels_difficulty_values": {
        LevelDifficulty.EASY: {
            ResourceType.CROPS: {
                "value": -50,
                "type": "simple",
            },
            ResourceType.MONEY: {
                "value": -200,
                "type": "simple",
            },
        },
        LevelDifficulty.NORMAL: {
            ResourceType.CROPS: {
                "value": -100,
                "type": "simple",
            },
            ResourceType.WOOD: {
                "value": -50,
                "type": "simple",
            },
            ResourceType.MONEY: {
                "value": -500,
                "type": "simple",
            },
        },
        LevelDifficulty.HARD: {
            ResourceType.CROPS: {
                "value": -200,
                "type": "simple",
            },
            ResourceType.WOOD: {
                "value": -100,
                "type": "simple",
            },
            ResourceType.MONEY: {
                "value": -1000,
                "type": "simple",
            },
            ResourceType.SILK: {
                "value": -1,
                "type": "simple",
            },
        },
    },
    "player_cards_values": {
        "bronze": {
            ResourceType.CROPS: -1,
            ResourceType.WOOD: -1,
            ResourceType.MONEY: -10,
        },
        "silver": {
            ResourceType.CROPS: -2,
            ResourceType.WOOD: -2,
            ResourceType.MONEY: -20,
        },
        "gold": {
            ResourceType.CROPS: -3,
            ResourceType.WOOD: -3,
            ResourceType.MONEY: -30,
        },
    },
}

DEFAULT_CARDS_PRICES = {
    CardColorName.BRONZE: {
        CardActionSubtype.CRAFT_CARD: [
            {
                ResourceType.SCRAPS: -250,
                ResourceType.RAW_BRONZE: -50,
                ResourceType.MONEY: -500,
            },
            {
                ResourceType.SCRAPS: -250,
                ResourceType.BRONZE_INGOTS: -3,
                ResourceType.MONEY: -500,
            },
            {
                ResourceType.RARE_GEM: -1,
            },
        ],
        CardActionSubtype.MILL_CARD: [
            {
                ResourceType.SCRAPS: 100,
                ResourceType.BRONZE_INGOTS: 1,
                ResourceType.MONEY: -200,
            },
        ],
    },
    CardColorName.SILVER: {
        CardActionSubtype.CRAFT_CARD: [
            {
                ResourceType.SCRAPS: -1000,
                ResourceType.RAW_SILVER: -50,
                ResourceType.MONEY: -1000,
            },
            {
                ResourceType.SCRAPS: -1000,
                ResourceType.SILVER_INGOTS: -3,
                ResourceType.MONEY: -1000,
            },
            {
                ResourceType.RARE_GEM: -1,
            },
        ],
        CardActionSubtype.MILL_CARD: [
            {
                ResourceType.SCRAPS: 250,
                ResourceType.SILVER_INGOTS: 1,
                ResourceType.MONEY: -200,
            },
        ],
    },
    CardColorName.GOLD: {
        CardActionSubtype.CRAFT_CARD: [
            {
                ResourceType.SCRAPS: -2000,
                ResourceType.RAW_GOLD: -50,
                ResourceType.MONEY: -2000,
            },
            {
                ResourceType.SCRAPS: -2000,
                ResourceType.GOLD_INGOTS: -3,
                ResourceType.MONEY: -2000,
            },
            {
                ResourceType.RARE_GEM: -1,
            },
        ],
        CardActionSubtype.MILL_CARD: [
            {
                ResourceType.SCRAPS: 500,
                ResourceType.GOLD_INGOTS: 1,
                ResourceType.MONEY: -200,
            },
        ],
    },
    "leader": {
        CardActionSubtype.CRAFT_LEADER: [
            {
                ResourceType.SCRAPS: -1000,
                ResourceType.BRONZE_INGOTS: -1,
                ResourceType.SILVER_INGOTS: -1,
                ResourceType.GOLD_INGOTS: -1,
                ResourceType.MONEY: -2000,
            },
            {
                ResourceType.SCRAPS: -1000,
                ResourceType.RAW_BRONZE: -15,
                ResourceType.RAW_SILVER: -15,
                ResourceType.RAW_GOLD: -15,
                ResourceType.MONEY: -2000,
            },
            {
                ResourceType.RARE_GEM: -1,
            },
        ],
        CardActionSubtype.MILL_LEADER: [
            {
                ResourceType.SCRAPS: 500,
                ResourceType.MONEY: -200,
            },
        ],
    },
}


class LeaderboardGameMode(StrEnum):
    RANDOM = "random"
    RANDOM_N = "random_n"
    SEASON = "season"
    ARENA = "arena"


class UserStatsRecordType(StrEnum):
    PLAY = "play"
    WIN = "win"


class UpgradeType(StrEnum):
    RESOURCES = "resources"
    SETTINGS = "settings"
    GAME = "game"


class UpgradeSubtype(StrEnum):
    MAX_CARDS_IN_DECK = "max_cards_in_deck"
    HAND_SIZE = "hand_size"
    MAX_ARMOR = "max_armor"
    MAX_HP = "max_hp"
    MAX_DECKS = "max_decks"

    AVATAR = "avatar"
    THEME = "theme"

    MONEY = "money"
    SCRAPS = "scraps"
    KEGS = "kegs"
    SILK = "silk"
    RARE_GEMS = "rare_gems"
    WOOD = "wood"
    INGOTS = "ingots"
    RAW = "raw"


DEFAULT_USER_UPGRADES = {
    UpgradeType.RESOURCES: {
        UpgradeSubtype.MAX_CARDS_IN_DECK: 0,
        UpgradeSubtype.HAND_SIZE: 0,
        UpgradeSubtype.MAX_ARMOR: 0,
        UpgradeSubtype.MAX_HP: 0,
        UpgradeSubtype.MAX_DECKS: 0,
    },
    UpgradeType.SETTINGS: {
        UpgradeSubtype.AVATAR: 0,
        UpgradeSubtype.THEME: 0,
    },
    UpgradeType.GAME: {
        UpgradeSubtype.MONEY: 0,
        UpgradeSubtype.SCRAPS: 0,
        UpgradeSubtype.RARE_GEMS: 0,
        UpgradeSubtype.WOOD: 0,
        UpgradeSubtype.INGOTS: 0,
        UpgradeSubtype.RAW: 0,
        UpgradeSubtype.SILK: 0,
        UpgradeSubtype.KEGS: 0,
    }
}
