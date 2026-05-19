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


class UpgradeType(StrEnumChoices):
    RESOURCES = "resources"
    SETTINGS = "settings"
    GAME = "game"


class UpgradeSubtype(StrEnumChoices):
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
    UpgradeType.GAME: {
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
    UpgradeType.RESOURCES: {
        UpgradeSubtype.MONEY: 0,
        UpgradeSubtype.SCRAPS: 0,
        UpgradeSubtype.RARE_GEMS: 0,
        UpgradeSubtype.WOOD: 0,  # WOOD + CROPS
        UpgradeSubtype.INGOTS: 0,  # all 3 ingots
        UpgradeSubtype.RAW: 0,  # all 3 raw
        UpgradeSubtype.SILK: 0,
        UpgradeSubtype.KEGS: 0,  # KEGS, BIG_KEGS, CHESTS
    },
}

DEFAULT_UPGRADES: dict[UpgradeType, dict] = {
    UpgradeType.GAME: {
        "ordering": 0,
        "title": "Игровые",
        "upgrades": {
            UpgradeSubtype.MAX_CARDS_IN_DECK: {
                "ordering": 1,
                "title": "Карт в колоде",
                "upgrades": {
                    0: {
                        "value": 10,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.RAW_BRONZE: -30,
                            ResourceType.RAW_SILVER: -10,
                            ResourceType.RAW_GOLD: -5,
                        },
                    },
                    1: {
                        "value": 11,
                        "next": {
                            ResourceType.MONEY: -2000,
                            ResourceType.RAW_BRONZE: -50,
                            ResourceType.RAW_SILVER: -30,
                            ResourceType.RAW_GOLD: -20,
                        },
                    },
                    2: {
                        "value": 12,
                        "next": {
                            ResourceType.MONEY: -3000,
                            ResourceType.RAW_BRONZE: -50,
                            ResourceType.RAW_SILVER: -30,
                            ResourceType.RAW_GOLD: -20,
                        },
                    },
                    3: {
                        "value": 13,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.RAW_BRONZE: -100,
                            ResourceType.RAW_SILVER: -50,
                            ResourceType.RAW_GOLD: -40,
                            ResourceType.BRONZE_INGOTS: -5,
                            ResourceType.SILVER_INGOTS: -3,
                            ResourceType.GOLD_INGOTS: -1,
                        },
                    },
                    4: {
                        "value": 14,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.RAW_BRONZE: -200,
                            ResourceType.RAW_SILVER: -80,
                            ResourceType.RAW_GOLD: -50,
                            ResourceType.BRONZE_INGOTS: -7,
                            ResourceType.SILVER_INGOTS: -5,
                            ResourceType.GOLD_INGOTS: -2,
                        },
                    },
                    5: {
                        "value": 15,
                        "next": {
                            ResourceType.MONEY: -6000,
                            ResourceType.RAW_BRONZE: -300,
                            ResourceType.RAW_SILVER: -100,
                            ResourceType.RAW_GOLD: -75,
                            ResourceType.BRONZE_INGOTS: -10,
                            ResourceType.SILVER_INGOTS: -8,
                            ResourceType.GOLD_INGOTS: -5,
                        },
                    },
                    6: {
                        "value": 16,
                        "next": {
                            ResourceType.MONEY: -8000,
                            ResourceType.RAW_BRONZE: -400,
                            ResourceType.RAW_SILVER: -100,
                            ResourceType.RAW_GOLD: -90,
                            ResourceType.BRONZE_INGOTS: -10,
                            ResourceType.SILVER_INGOTS: -8,
                            ResourceType.GOLD_INGOTS: -5,
                        },
                    },
                    7: {
                        "value": 17,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.RAW_BRONZE: -500,
                            ResourceType.RAW_SILVER: -250,
                            ResourceType.RAW_GOLD: -150,
                            ResourceType.BRONZE_INGOTS: -15,
                            ResourceType.SILVER_INGOTS: -10,
                            ResourceType.GOLD_INGOTS: -8,
                        },
                    },
                    8: {"value": 18, "next": None},
                },
            },
            UpgradeSubtype.HAND_SIZE: {
                "ordering": 2,
                "title": "Размер руки",
                "upgrades": {
                    0: {
                        "value": 5,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.SCRAPS: -1000,
                            ResourceType.RAW_BRONZE: -20,
                            ResourceType.RAW_SILVER: -10,
                            ResourceType.RAW_GOLD: -5,
                        },
                    },
                    1: {
                        "value": 6,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.SCRAPS: -2500,
                            ResourceType.RAW_BRONZE: -200,
                            ResourceType.RAW_SILVER: -100,
                            ResourceType.RAW_GOLD: -100,
                            ResourceType.BRONZE_INGOTS: 10,
                            ResourceType.SILVER_INGOTS: 8,
                            ResourceType.GOLD_INGOTS: 5,
                        },
                    },
                    2: {
                        "value": 7,
                        "next": {
                            ResourceType.MONEY: -15000,
                            ResourceType.SCRAPS: -7500,
                            ResourceType.RAW_BRONZE: -500,
                            ResourceType.RAW_SILVER: -300,
                            ResourceType.RAW_GOLD: -250,
                            ResourceType.BRONZE_INGOTS: 30,
                            ResourceType.SILVER_INGOTS: 20,
                            ResourceType.GOLD_INGOTS: 15,
                        },
                    },
                    3: {"value": 8, "next": None},
                },
            },
            UpgradeSubtype.MAX_ARMOR: {
                "ordering": 4,
                "title": "Броня лидера",
                "upgrades": {
                    0: {
                        "value": 0,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.WOOD: -500,
                            ResourceType.CROPS: -1000,
                        },
                    },
                    1: {
                        "value": 10,
                        "next": {
                            ResourceType.MONEY: -2000,
                            ResourceType.WOOD: -1000,
                            ResourceType.CROPS: -1500,
                        },
                    },
                    2: {
                        "value": 15,
                        "next": {
                            ResourceType.MONEY: -3000,
                            ResourceType.WOOD: -2000,
                            ResourceType.CROPS: -3000,
                            ResourceType.SILK: -1,
                        },
                    },
                    3: {
                        "value": 20,
                        "next": {
                            ResourceType.MONEY: -4000,
                            ResourceType.WOOD: -3000,
                            ResourceType.CROPS: -4000,
                            ResourceType.SILK: -3,
                        },
                    },
                    4: {
                        "value": 25,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.WOOD: -4000,
                            ResourceType.CROPS: -5000,
                            ResourceType.SILK: -5,
                        },
                    },
                    5: {
                        "value": 30,
                        "next": {
                            ResourceType.MONEY: -6000,
                            ResourceType.WOOD: -5000,
                            ResourceType.CROPS: -6000,
                            ResourceType.SILK: -7,
                        },
                    },
                    6: {
                        "value": 35,
                        "next": {
                            ResourceType.MONEY: -7000,
                            ResourceType.WOOD: -6000,
                            ResourceType.CROPS: -7000,
                            ResourceType.SILK: -10,
                        },
                    },
                    7: {
                        "value": 40,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.WOOD: -10000,
                            ResourceType.CROPS: -10000,
                            ResourceType.SILK: -20,
                        },
                    },
                    8: {"value": 100, "next": None},
                },
            },
            UpgradeSubtype.MAX_HP: {
                "ordering": 3,
                "title": "Здоровье колоды",
                "upgrades": {
                    0: {
                        "value": 100,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.SCRAPS: -300,
                            ResourceType.BRONZE_INGOTS: -2,
                        },
                    },
                    1: {
                        "value": 125,
                        "next": {
                            ResourceType.MONEY: -1500,
                            ResourceType.SCRAPS: -700,
                            ResourceType.BRONZE_INGOTS: -3,
                        },
                    },
                    2: {
                        "value": 150,
                        "next": {
                            ResourceType.MONEY: -2500,
                            ResourceType.SCRAPS: -1000,
                            ResourceType.BRONZE_INGOTS: -5,
                            ResourceType.SILVER_INGOTS: -2,
                        },
                    },
                    3: {
                        "value": 175,
                        "next": {
                            ResourceType.MONEY: -3000,
                            ResourceType.SCRAPS: -1500,
                            ResourceType.BRONZE_INGOTS: -6,
                            ResourceType.SILVER_INGOTS: -3,
                            ResourceType.GOLD_INGOTS: -2,
                        },
                    },
                    4: {
                        "value": 200,
                        "next": {
                            ResourceType.MONEY: -3500,
                            ResourceType.WOOD: -2000,
                            ResourceType.CROPS: -3000,
                            ResourceType.BRONZE_INGOTS: -8,
                            ResourceType.SILVER_INGOTS: -5,
                            ResourceType.GOLD_INGOTS: -3,
                        },
                    },
                    5: {
                        "value": 225,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.WOOD: -3000,
                            ResourceType.CROPS: -4000,
                            ResourceType.BRONZE_INGOTS: -10,
                            ResourceType.SILVER_INGOTS: -7,
                            ResourceType.GOLD_INGOTS: -5,
                        },
                    },
                    6: {
                        "value": 250,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.WOOD: -4000,
                            ResourceType.CROPS: -5000,
                            ResourceType.SILK: -10,
                            ResourceType.BRONZE_INGOTS: -10,
                            ResourceType.SILVER_INGOTS: -7,
                            ResourceType.GOLD_INGOTS: -5,
                        },
                    },
                    7: {
                        "value": 275,
                        "next": {
                            ResourceType.MONEY: -7000,
                            ResourceType.WOOD: -5000,
                            ResourceType.CROPS: -7000,
                            ResourceType.SILK: -15,
                            ResourceType.BRONZE_INGOTS: -15,
                            ResourceType.SILVER_INGOTS: -10,
                            ResourceType.GOLD_INGOTS: -7,
                        },
                    },
                    8: {"value": 300, "next": None},
                },
            },
            UpgradeSubtype.MAX_DECKS: {
                "ordering": 0,
                "title": "Количество колод",
                "upgrades": {
                    0: {
                        "value": 2,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.CROPS: -1000,
                        },
                    },
                    1: {
                        "value": 3,
                        "next": {
                            ResourceType.MONEY: -2000,
                            ResourceType.CROPS: -1500,
                            ResourceType.WOOD: -1000,
                        },
                    },
                    2: {
                        "value": 5,
                        "next": {
                            ResourceType.MONEY: -3000,
                            ResourceType.CROPS: -3000,
                            ResourceType.WOOD: -2000,
                            ResourceType.SILK: -5,
                        },
                    },
                    3: {
                        "value": 7,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.CROPS: -3000,
                            ResourceType.WOOD: -2000,
                            ResourceType.SILK: -5,
                            ResourceType.SILVER_INGOTS: -5,
                        },
                    },
                    4: {
                        "value": 8,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.CROPS: -5000,
                            ResourceType.WOOD: -4000,
                            ResourceType.SILK: -15,
                            ResourceType.BRONZE_INGOTS: -30,
                            ResourceType.SILVER_INGOTS: -15,
                            ResourceType.GOLD_INGOTS: -5,
                        },
                    },
                    5: {"value": 10, "next": None},
                },
            },
        },
    },
    UpgradeType.SETTINGS: {
        "ordering": 2,
        "title": "Настройки",
        "upgrades": {
            UpgradeSubtype.AVATAR: {
                "ordering": 0,
                "title": "Аватары",
                "upgrades": {
                    0: {
                        "value": False,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.CROPS: -5000,
                        },
                    },
                    1: {"value": True, "next": None},
                },
            },
            UpgradeSubtype.THEME: {
                "ordering": 1,
                "title": "Темы",
                "upgrades": {
                    0: {
                        "value": False,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.WOOD: -3000,
                            ResourceType.SCRAPS: -3000,
                        },
                    },
                    1: {"value": True, "next": None},
                },
            },
        },
    },
    UpgradeType.RESOURCES: {
        "ordering": 1,
        "title": "Ресурсы",
        "upgrades": {
            UpgradeSubtype.MONEY: {
                "ordering": 0,
                "title": "Запас монет",
                "upgrades": {
                    0: {
                        "value": 5000,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.CROPS: -500,
                            ResourceType.RAW_BRONZE: -30,
                        },
                    },
                    1: {
                        "value": 10000,
                        "next": {
                            ResourceType.MONEY: -2000,
                            ResourceType.CROPS: -1000,
                            ResourceType.RAW_BRONZE: -50,
                        },
                    },
                    2: {
                        "value": 15000,
                        "next": {
                            ResourceType.MONEY: -3000,
                            ResourceType.CROPS: -2000,
                            ResourceType.RAW_BRONZE: -100,
                            ResourceType.RAW_SILVER: -30,
                        },
                    },
                    3: {
                        "value": 20000,
                        "next": {
                            ResourceType.MONEY: -3000,
                            ResourceType.CROPS: -2000,
                            ResourceType.WOOD: -1000,
                            ResourceType.RAW_BRONZE: -150,
                            ResourceType.RAW_SILVER: -50,
                        },
                    },
                    4: {
                        "value": 30000,
                        "next": {
                            ResourceType.MONEY: -4000,
                            ResourceType.CROPS: -3000,
                            ResourceType.WOOD: -2000,
                            ResourceType.RAW_BRONZE: -200,
                            ResourceType.RAW_SILVER: -70,
                            ResourceType.RAW_GOLD: -30,
                        },
                    },
                    5: {
                        "value": 40000,
                        "next": {
                            ResourceType.MONEY: -4000,
                            ResourceType.CROPS: -3000,
                            ResourceType.WOOD: -2000,
                            ResourceType.SILK: -20,
                            ResourceType.RAW_BRONZE: -250,
                            ResourceType.RAW_SILVER: -100,
                            ResourceType.RAW_GOLD: -50,
                        },
                    },
                    6: {
                        "value": 50000,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.CROPS: -4000,
                            ResourceType.WOOD: -3000,
                            ResourceType.SILK: -30,
                            ResourceType.RAW_BRONZE: -300,
                            ResourceType.RAW_SILVER: -150,
                            ResourceType.RAW_GOLD: -100,
                        },
                    },
                    7: {
                        "value": 75000,
                        "next": {
                            ResourceType.MONEY: -7000,
                            ResourceType.CROPS: -3000,
                            ResourceType.WOOD: -2000,
                            ResourceType.SILK: -20,
                            ResourceType.BRONZE_INGOTS: -20,
                            ResourceType.SILVER_INGOTS: -15,
                            ResourceType.GOLD_INGOTS: -5,
                        },
                    },
                    8: {
                        "value": 100000,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.CROPS: -5000,
                            ResourceType.WOOD: -4000,
                            ResourceType.SILK: -50,
                            ResourceType.BRONZE_INGOTS: -40,
                            ResourceType.SILVER_INGOTS: -25,
                            ResourceType.GOLD_INGOTS: -15,
                        },
                    },
                    9: {
                        "value": 200000,
                        "next": {
                            ResourceType.MONEY: -20000,
                            ResourceType.CROPS: -7000,
                            ResourceType.WOOD: -7000,
                            ResourceType.SILK: -50,
                            ResourceType.BRONZE_INGOTS: -50,
                            ResourceType.SILVER_INGOTS: -50,
                            ResourceType.GOLD_INGOTS: -50,
                        },
                    },
                    10: {"value": 1000000, "next": None},
                },
            },
            UpgradeSubtype.SCRAPS: {
                "ordering": 4,
                "title": "Запас тряпок",
                "upgrades": {
                    0: {
                        "value": 2000,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.CROPS: -500,
                        },
                    },
                    1: {
                        "value": 3000,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.CROPS: -500,
                            ResourceType.WOOD: -200,
                        },
                    },
                    2: {
                        "value": 5000,
                        "next": {
                            ResourceType.MONEY: -2000,
                            ResourceType.CROPS: -1000,
                            ResourceType.WOOD: -500,
                        },
                    },
                    3: {
                        "value": 7500,
                        "next": {
                            ResourceType.MONEY: -3000,
                            ResourceType.CROPS: -1500,
                            ResourceType.WOOD: -750,
                            ResourceType.SILK: -5,
                        },
                    },
                    4: {
                        "value": 10000,
                        "next": {
                            ResourceType.MONEY: -4000,
                            ResourceType.CROPS: -2000,
                            ResourceType.WOOD: -1000,
                            ResourceType.SILK: -8,
                        },
                    },
                    5: {
                        "value": 15000,
                        "next": {
                            ResourceType.MONEY: -8000,
                            ResourceType.SILK: -10,
                            ResourceType.BRONZE_INGOTS: -8,
                            ResourceType.SILVER_INGOTS: -4,
                        },
                    },
                    6: {
                        "value": 20000,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.SILK: -15,
                            ResourceType.BRONZE_INGOTS: -13,
                            ResourceType.SILVER_INGOTS: -8,
                        },
                    },
                    7: {
                        "value": 30000,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.SILK: -15,
                            ResourceType.BRONZE_INGOTS: -20,
                            ResourceType.SILVER_INGOTS: -14,
                            ResourceType.GOLD_INGOTS: -4,
                        },
                    },
                    8: {
                        "value": 40000,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.SILK: -15,
                            ResourceType.BRONZE_INGOTS: -20,
                            ResourceType.SILVER_INGOTS: -15,
                            ResourceType.GOLD_INGOTS: -10,
                        },
                    },
                    9: {
                        "value": 50000,
                        "next": {
                            ResourceType.MONEY: -15000,
                            ResourceType.SILK: -20,
                            ResourceType.RAW_GOLD: -100,
                            ResourceType.GOLD_INGOTS: -20,
                        },
                    },
                    10: {"value": 100000, "next": None},
                },
            },
            UpgradeSubtype.KEGS: {
                "ordering": 1,
                "title": "Запас бочек/коробок",
                "upgrades": {
                    0: {
                        "value": 0,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.WOOD: -300,
                        },
                    },
                    1: {
                        "value": 1,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.WOOD: -500,
                        },
                    },
                    2: {
                        "value": 3,
                        "next": {
                            ResourceType.MONEY: -2000,
                            ResourceType.WOOD: -1000,
                            ResourceType.BRONZE_INGOTS: -5,
                        },
                    },
                    3: {
                        "value": 5,
                        "next": {
                            ResourceType.MONEY: -2500,
                            ResourceType.WOOD: -1500,
                            ResourceType.BRONZE_INGOTS: -8,
                            ResourceType.SILVER_INGOTS: -4,
                        },
                    },
                    4: {
                        "value": 7,
                        "next": {
                            ResourceType.MONEY: -3500,
                            ResourceType.WOOD: -2000,
                            ResourceType.BRONZE_INGOTS: -12,
                            ResourceType.SILVER_INGOTS: -6,
                        },
                    },
                    5: {
                        "value": 10,
                        "next": {
                            ResourceType.MONEY: -3500,
                            ResourceType.WOOD: -2500,
                            ResourceType.BRONZE_INGOTS: -15,
                            ResourceType.SILVER_INGOTS: -8,
                            ResourceType.GOLD_INGOTS: -3,
                        },
                    },
                    6: {
                        "value": 15,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.WOOD: -3000,
                            ResourceType.BRONZE_INGOTS: -15,
                            ResourceType.SILVER_INGOTS: -10,
                            ResourceType.GOLD_INGOTS: -5,
                        },
                    },
                    7: {
                        "value": 25,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.WOOD: -3000,
                            ResourceType.BRONZE_INGOTS: -15,
                            ResourceType.SILVER_INGOTS: -10,
                            ResourceType.GOLD_INGOTS: -5,
                            ResourceType.SILK: -10,
                        },
                    },
                    8: {
                        "value": 40,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.WOOD: -3000,
                            ResourceType.BRONZE_INGOTS: -15,
                            ResourceType.SILVER_INGOTS: -10,
                            ResourceType.GOLD_INGOTS: -5,
                            ResourceType.SILK: -20,
                        },
                    },
                    9: {"value": 100, "next": None},
                },
            },
            UpgradeSubtype.SILK: {
                "ordering": 6,
                "title": "Запас золотого шёлка",
                "upgrades": {
                    0: {
                        "value": 0,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.RAW_GOLD: -5,
                        },
                    },
                    1: {
                        "value": 3,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.RAW_GOLD: -8,
                        },
                    },
                    2: {
                        "value": 5,
                        "next": {
                            ResourceType.MONEY: -1500,
                            ResourceType.RAW_GOLD: -8,
                            ResourceType.GOLD_INGOTS: -2,
                        },
                    },
                    3: {
                        "value": 10,
                        "next": {
                            ResourceType.MONEY: -2500,
                            ResourceType.RAW_GOLD: -10,
                            ResourceType.GOLD_INGOTS: -4,
                        },
                    },
                    4: {
                        "value": 15,
                        "next": {
                            ResourceType.MONEY: -2500,
                            ResourceType.RAW_GOLD: -10,
                            ResourceType.GOLD_INGOTS: -4,
                            ResourceType.SILK: -5,
                        },
                    },
                    5: {
                        "value": 25,
                        "next": {
                            ResourceType.MONEY: -3500,
                            ResourceType.RAW_GOLD: -15,
                            ResourceType.GOLD_INGOTS: -8,
                            ResourceType.SILK: -8,
                        },
                    },
                    6: {
                        "value": 40,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.RAW_GOLD: -25,
                            ResourceType.GOLD_INGOTS: -10,
                            ResourceType.SILK: -10,
                        },
                    },
                    7: {
                        "value": 60,
                        "next": {
                            ResourceType.MONEY: -7000,
                            ResourceType.RAW_GOLD: -30,
                            ResourceType.GOLD_INGOTS: -14,
                            ResourceType.SILK: -14,
                        },
                    },
                    8: {
                        "value": 100,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.RAW_GOLD: -30,
                            ResourceType.GOLD_INGOTS: -15,
                            ResourceType.SILK: -20,
                        },
                    },
                    9: {"value": 200, "next": None},
                },
            },
            UpgradeSubtype.RARE_GEMS: {
                "ordering": 7,
                "title": "Запас редких камней",
                "upgrades": {
                    0: {"value": 0, "next": {ResourceType.MONEY: -2000}},
                    1: {"value": 1, "next": {ResourceType.MONEY: -3000}},
                    2: {"value": 3, "next": {ResourceType.MONEY: -5000}},
                    3: {"value": 5, "next": {ResourceType.MONEY: -10000}},
                    4: {"value": 7, "next": {ResourceType.MONEY: -10000}},
                    5: {"value": 10, "next": None},
                },
            },
            UpgradeSubtype.WOOD: {
                "ordering": 5,
                "title": "Запас соломы/дерева",
                "upgrades": {
                    0: {
                        "value": 3000,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.CROPS: -500,
                            ResourceType.WOOD: -200,
                        },
                    },
                    1: {
                        "value": 5000,
                        "next": {
                            ResourceType.MONEY: -1500,
                            ResourceType.CROPS: -700,
                            ResourceType.WOOD: -400,
                        },
                    },
                    2: {
                        "value": 7000,
                        "next": {
                            ResourceType.MONEY: -2000,
                            ResourceType.CROPS: -1000,
                            ResourceType.WOOD: -500,
                        },
                    },
                    3: {
                        "value": 1000,
                        "next": {
                            ResourceType.MONEY: -2500,
                            ResourceType.CROPS: -1200,
                            ResourceType.WOOD: -700,
                        },
                    },
                    4: {
                        "value": 15000,
                        "next": {
                            ResourceType.MONEY: -3000,
                            ResourceType.CROPS: -1500,
                            ResourceType.WOOD: -1000,
                        },
                    },
                    5: {
                        "value": 20000,
                        "next": {
                            ResourceType.MONEY: -3500,
                            ResourceType.CROPS: -2000,
                            ResourceType.WOOD: -1200,
                        },
                    },
                    6: {
                        "value": 25000,
                        "next": {
                            ResourceType.MONEY: -4000,
                            ResourceType.CROPS: -2500,
                            ResourceType.WOOD: -1500,
                            ResourceType.SILK: -5,
                        },
                    },
                    7: {
                        "value": 35000,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.CROPS: -3000,
                            ResourceType.WOOD: -2000,
                            ResourceType.SILK: -8,
                        },
                    },
                    8: {
                        "value": 50000,
                        "next": {
                            ResourceType.MONEY: -6000,
                            ResourceType.CROPS: -3500,
                            ResourceType.WOOD: -2500,
                            ResourceType.SILK: -10,
                        },
                    },
                    9: {
                        "value": 75000,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.CROPS: -5000,
                            ResourceType.WOOD: -3000,
                            ResourceType.SILK: -15,
                            ResourceType.GOLD_INGOTS: -10,
                        },
                    },
                    10: {"value": 100000, "next": None},
                },
            },
            UpgradeSubtype.INGOTS: {
                "ordering": 3,
                "title": "Запас слитков",
                "upgrades": {
                    0: {
                        "value": 0,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.CROPS: -1000,
                        },
                    },
                    1: {
                        "value": 5,
                        "next": {
                            ResourceType.MONEY: -1500,
                            ResourceType.RAW_BRONZE: -30,
                        },
                    },
                    2: {
                        "value": 10,
                        "next": {
                            ResourceType.MONEY: -2000,
                            ResourceType.RAW_BRONZE: -50,
                        },
                    },
                    3: {
                        "value": 15,
                        "next": {
                            ResourceType.MONEY: -2500,
                            ResourceType.RAW_BRONZE: -75,
                            ResourceType.RAW_SILVER: -20,
                        },
                    },
                    4: {
                        "value": 20,
                        "next": {
                            ResourceType.MONEY: -3000,
                            ResourceType.RAW_BRONZE: -100,
                            ResourceType.RAW_SILVER: -35,
                        },
                    },
                    5: {
                        "value": 30,
                        "next": {
                            ResourceType.MONEY: -3500,
                            ResourceType.RAW_BRONZE: -130,
                            ResourceType.RAW_SILVER: -50,
                            ResourceType.RAW_GOLD: -5,
                        },
                    },
                    6: {
                        "value": 40,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.RAW_BRONZE: -150,
                            ResourceType.RAW_SILVER: -75,
                            ResourceType.RAW_GOLD: -15,
                        },
                    },
                    7: {
                        "value": 50,
                        "next": {
                            ResourceType.MONEY: -6000,
                            ResourceType.RAW_BRONZE: -165,
                            ResourceType.RAW_SILVER: -80,
                            ResourceType.RAW_GOLD: -25,
                        },
                    },
                    8: {
                        "value": 70,
                        "next": {
                            ResourceType.MONEY: -7000,
                            ResourceType.RAW_BRONZE: -200,
                            ResourceType.RAW_SILVER: -100,
                            ResourceType.RAW_GOLD: -45,
                        },
                    },
                    9: {
                        "value": 90,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.RAW_BRONZE: -300,
                            ResourceType.RAW_SILVER: -150,
                            ResourceType.RAW_GOLD: -100,
                        },
                    },
                    10: {"value": 200, "next": None},
                },
            },
            UpgradeSubtype.RAW: {
                "ordering": 2,
                "title": "Запас чистых камней",
                "upgrades": {
                    0: {
                        "value": 50,
                        "next": {
                            ResourceType.MONEY: -1000,
                            ResourceType.CROPS: -500,
                        },
                    },
                    1: {
                        "value": 75,
                        "next": {
                            ResourceType.MONEY: -1500,
                            ResourceType.CROPS: -700,
                            ResourceType.WOOD: -400,
                        },
                    },
                    2: {
                        "value": 100,
                        "next": {
                            ResourceType.MONEY: -2000,
                            ResourceType.CROPS: -1000,
                            ResourceType.WOOD: -500,
                            ResourceType.SILK: -5,
                        },
                    },
                    3: {
                        "value": 150,
                        "next": {
                            ResourceType.MONEY: -2500,
                            ResourceType.CROPS: -1500,
                            ResourceType.WOOD: -700,
                            ResourceType.SILK: -8,
                        },
                    },
                    4: {
                        "value": 250,
                        "next": {
                            ResourceType.MONEY: -3000,
                            ResourceType.CROPS: -2000,
                            ResourceType.WOOD: -1200,
                            ResourceType.SILK: -10,
                        },
                    },
                    5: {
                        "value": 400,
                        "next": {
                            ResourceType.MONEY: -3500,
                            ResourceType.CROPS: -2400,
                            ResourceType.WOOD: -1500,
                            ResourceType.SILK: -12,
                        },
                    },
                    6: {
                        "value": 600,
                        "next": {
                            ResourceType.MONEY: -4000,
                            ResourceType.CROPS: -2900,
                            ResourceType.WOOD: -1700,
                            ResourceType.SILK: -15,
                        },
                    },
                    7: {
                        "value": 800,
                        "next": {
                            ResourceType.MONEY: -4500,
                            ResourceType.CROPS: -3300,
                            ResourceType.WOOD: -2200,
                            ResourceType.SILK: -18,
                        },
                    },
                    8: {
                        "value": 1000,
                        "next": {
                            ResourceType.MONEY: -5000,
                            ResourceType.CROPS: -5000,
                            ResourceType.WOOD: -3000,
                            ResourceType.SILK: -25,
                            ResourceType.RAW_GOLD: -50,
                        },
                    },
                    9: {
                        "value": 1500,
                        "next": {
                            ResourceType.MONEY: -10000,
                            ResourceType.CROPS: -10000,
                            ResourceType.WOOD: -5000,
                            ResourceType.SILK: -50,
                            ResourceType.RAW_GOLD: -100,
                        },
                    },
                    10: {"value": 5000, "next": None},
                },
            },
        },
    },
}
