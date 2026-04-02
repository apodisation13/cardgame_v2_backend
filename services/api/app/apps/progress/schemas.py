from lib.utils.schemas import Base
from lib.utils.schemas.game import CardActionSubtype, LevelDifficulty, ResourceActionSubtype
from services.api.app.apps.cards.schemas import Card, Deck, Enemy, EnemyLeader, Leader, DeckV2


class UserResources(Base):
    scraps: int
    raw_bronze: int
    raw_silver: int
    raw_gold: int
    bronze_ingots: int
    silver_ingots: int
    gold_ingots: int
    crops: int
    wood: int
    silk: int
    kegs: int
    big_kegs: int
    chests: int
    keys: int
    rare_gem: int
    money: int

    @staticmethod
    def get_one(
        row: dict,
    ) -> "UserResources":
        return UserResources(
            scraps=row["scraps"],
            raw_bronze=row["raw_bronze"],
            raw_silver=row["raw_silver"],
            raw_gold=row["raw_gold"],
            bronze_ingots=row["bronze_ingots"],
            silver_ingots=row["silver_ingots"],
            gold_ingots=row["gold_ingots"],
            crops=row["crops"],
            wood=row["wood"],
            silk=row["silk"],
            kegs=row["kegs"],
            big_kegs=row["big_kegs"],
            chests=row["chests"],
            keys=row["keys"],
            rare_gem=row["rare_gem"],
            money=row["money"],
        )


class UserCard(Base):
    id: int | None = None
    count: int = 0
    card: Card


class UserLeader(Base):
    id: int | None = None
    count: int = 0
    card: Leader


class UserDeck(Base):
    id: int
    deck: Deck


class UserDatabase(Base):
    cards: list[UserCard]
    leaders: list[UserLeader]
    decks: list[UserDeck]


class LevelRelatedLevel(Base):
    related_level_id: int | None
    line: str | None
    connection: str | None


class Level(Base):
    id: int
    name: str
    starting_enemies_number: int
    difficulty: LevelDifficulty
    x: int
    y: int
    enemy_leader: EnemyLeader
    enemies: list[Enemy]
    children: list[LevelRelatedLevel]


class LevelV2(Base):
    id: int
    name: str
    starting_enemies_number: int
    difficulty: LevelDifficulty
    x: int
    y: int
    enemy_leader: int
    enemies: list[int]
    children: list[LevelRelatedLevel]


class UserLevel(Base):
    id: int | None
    unlocked: bool
    finished: bool | None
    level: Level


class UserLevelV2(Base):
    id: int | None
    unlocked: bool
    finished: bool | None
    level: LevelV2


class SeasonRelatedSeason(Base):
    related_season_id: int | None
    line: str | None
    connection: str | None


class Season(Base):
    id: int
    name: str
    description: str
    x: int
    y: int
    levels: list[UserLevel]
    children: list[SeasonRelatedSeason]


class SeasonV2(Base):
    id: int
    name: str
    description: str
    x: int
    y: int
    levels: list[UserLevelV2]
    children: list[SeasonRelatedSeason]


class Stats(Base):
    total_levels: int
    finished_levels: int = 0
    unlocked_levels: int = 0
    easy_levels: int = 0
    normal_levels: int = 0
    hard_levels: int = 0


class UserSeason(Base):
    id: int | None
    finished: bool | None
    season: Season
    stats: Stats


class UserSeasonV2(Base):
    id: int | None
    finished: bool | None
    season: SeasonV2
    stats: Stats


class UserProgressResponse(Base):
    user_database: UserDatabase
    seasons: list[UserSeason]
    resources: UserResources
    enemies: list[Enemy]
    enemy_leaders: list[EnemyLeader]
    game_const: dict


class UserCardV2(Base):
    user_card_id: int
    count: int


class UserLeaderV2(Base):
    user_leader_id: int
    count: int


class UserDeckV2(Base):
    user_deck_id: int
    deck: DeckV2


class UserProgressResponseV2(Base):
    user_resources: UserResources
    user_cards: dict[int, UserCardV2]
    user_leaders: dict[int, UserLeaderV2]
    user_decks: list[UserDeckV2]
    user_seasons: list[UserSeasonV2]


class CreateDeckRequest(Base):
    deck_name: str
    leader_id: int
    cards: list[int]


class ListDecksResponse(Base):
    decks: list[UserDeck]


class ResourcesRequest(Base):
    subtype: ResourceActionSubtype
    data: dict


class CardCraftMillRequest(Base):
    subtype: CardActionSubtype
    recipe: dict | None = None


class CardCraftMillResponse(Base):
    cards: list[UserCard] | list[UserLeader]
    resources: UserResources


class OpenRelatedLevelsResponse(Base):
    seasons: list[UserSeason]


class CardCraftBonusRequest(Base):
    cards_ids: list[int]


class CardCraftBonusResponse(Base):
    cards: list[UserCard]
