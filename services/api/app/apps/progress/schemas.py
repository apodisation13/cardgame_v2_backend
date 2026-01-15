from lib.utils.schemas import Base
from lib.utils.schemas.game import LevelDifficulty, ResourceActionSubtype, CardActionSubtype
from services.api.app.apps.cards.schemas import Card, Deck, Enemy, EnemyLeader, Leader


class UserResources(Base):
    scraps: int
    kegs: int
    big_kegs: int
    chests: int
    wood: int
    keys: int


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


class UserLevel(Base):
    id: int | None
    unlocked: bool
    finished: bool | None
    level: Level


class Season(Base):
    id: int
    name: str
    description: str
    unlocked: bool
    levels: list[UserLevel]


class UserProgressResponse(Base):
    user_database: UserDatabase
    seasons: list[Season]
    resources: UserResources
    enemies: list[Enemy]
    enemy_leaders: list[EnemyLeader]
    game_const: dict


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


class CardCraftMillResponse(Base):
    cards: list[UserCard] | list[UserLeader]
    resources: UserResources


class OpenRelatedLevelsResponse(Base):
    seasons: list[Season]


class CardCraftBonusRequest(Base):
    cards_ids: list[int]


class CardCraftBonusResponse(Base):
    cards: list[UserCard]
