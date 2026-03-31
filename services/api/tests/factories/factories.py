import factory
from lib.tests.factories import BaseModelFactory, TimeStampMixinFactory, UserFactory
from lib.utils.models import (
    Ability,
    Card,
    CardDeck,
    Color,
    Deathwish,
    Deck,
    Enemy,
    EnemyLeader,
    EnemyLeaderAbility,
    EnemyPassiveAbility,
    Faction,
    GameConstants,
    Leader,
    Leaderboard,
    Level,
    LevelEnemy,
    LevelRelatedLevels,
    Move,
    PassiveAbility,
    Season,
    SeasonRelatedSeasons,
    Type,
    UserCard,
    UserDeck,
    UserLeader,
    UserLevel,
    UserPreferences,
    UserResource,
    UserSeason,
    UserStats,
)
from lib.utils.schemas.game import (
    DEFAULT_CARDS_PRICES,
    DEFAULT_KEY_REWARDS,
    DEFAULT_RESOURCES_TRANSITIONS,
    DEFAULT_START_LEVEL_PRICES,
    DEFAULT_WIN_LEVEL_REWARDS,
    LeaderboardGameMode,
    LevelDifficulty,
    UserStatsRecordType,
)
from services.api.app.apps.preferences.schemas import DEFAULT_PREFERENCES


class FactionFactory(BaseModelFactory):
    class Meta:
        model = Faction

    name = factory.Sequence(lambda n: f"Faction {n}")


class ColorFactory(BaseModelFactory):
    class Meta:
        model = Color

    name = factory.Sequence(lambda n: f"Color {n}")


class GameConstantsFactory(BaseModelFactory):
    class Meta:
        model = GameConstants

    data = {
        "hand_size": 6,
        "number_of_cards_in_deck": 12,
        "resources_transitions": DEFAULT_RESOURCES_TRANSITIONS,
        "key_rewards": DEFAULT_KEY_REWARDS,
        "win_level_rewards": DEFAULT_WIN_LEVEL_REWARDS,
        "start_level_prices": DEFAULT_START_LEVEL_PRICES,
        "cards_resources_prices": DEFAULT_CARDS_PRICES,
    }


class TypeFactory(BaseModelFactory):
    class Meta:
        model = Type

    name = factory.Sequence(lambda n: f"Type {n}")


class AbilityFactory(BaseModelFactory):
    class Meta:
        model = Ability

    name = factory.Sequence(lambda n: f"Ability {n}")
    description = factory.Faker("sentence")


class PassiveAbilityFactory(BaseModelFactory):
    class Meta:
        model = PassiveAbility

    name = factory.Sequence(lambda n: f"Passive Ability {n}")
    description = factory.Faker("sentence")


class LeaderFactory(BaseModelFactory):
    class Meta:
        model = Leader

    name = factory.Sequence(lambda n: f"Leader {n + 1}")
    image_original = "image_url"
    image_tablet = "image_url"
    image_phone = "image_url"
    unlocked = False
    faction_id = factory.SubFactory(FactionFactory)
    ability_id = factory.SubFactory(AbilityFactory)
    hp = 0
    damage = 0
    charges = 1
    heal = 0
    armor = 0
    has_passive = False
    passive_ability_id = None
    value = 0
    timer = 0
    default_timer = 0
    reset_timer = False
    newly_added = False
    data = {}


class CardFactory(BaseModelFactory):
    class Meta:
        model = Card

    name = factory.Sequence(lambda n: f"Card {n + 1}")
    image_original = "image_url"
    image_tablet = "image_url"
    image_phone = "image_url"
    unlocked = False
    faction_id = factory.SubFactory(FactionFactory)
    color_id = factory.SubFactory(ColorFactory)
    type_id = factory.SubFactory(TypeFactory)
    ability_id = factory.SubFactory(AbilityFactory)
    damage = 0
    charges = 1
    hp = 0
    heal = 0
    armor = 0
    has_passive = False
    has_passive_in_hand = False
    has_passive_in_deck = False
    has_passive_in_grave = False
    passive_ability_id = None
    value = 0
    timer = 0
    default_timer = 0
    reset_timer = False
    each_tick = False
    newly_added = False
    data = {}


class DeckFactory(BaseModelFactory, TimeStampMixinFactory):
    class Meta:
        model = Deck

    name = factory.Sequence(lambda n: f"Deck {n}")
    leader_id = factory.SubFactory(LeaderFactory)


class CardDeckFactory(BaseModelFactory, TimeStampMixinFactory):
    class Meta:
        model = CardDeck

    deck_id = factory.SubFactory(DeckFactory)
    card_id = factory.SubFactory(CardFactory)


class MoveFactory(BaseModelFactory):
    class Meta:
        model = Move

    name = factory.Sequence(lambda n: f"Move {n}")
    description = factory.Faker("sentence")


class EnemyPassiveAbilityFactory(BaseModelFactory):
    class Meta:
        model = EnemyPassiveAbility

    name = factory.Sequence(lambda n: f"Enemy Passive {n}")
    description = factory.Faker("sentence")


class EnemyLeaderAbilityFactory(BaseModelFactory):
    class Meta:
        model = EnemyLeaderAbility

    name = factory.Sequence(lambda n: f"Enemy Leader Ability {n}")
    description = factory.Faker("sentence")


class DeathwishFactory(BaseModelFactory):
    class Meta:
        model = Deathwish

    name = factory.Sequence(lambda n: f"Deathwish {n}")
    description = factory.Faker("sentence")


class EnemyFactory(BaseModelFactory):
    class Meta:
        model = Enemy

    name = factory.Sequence(lambda n: f"Enemy {n + 1}")
    image_original = "image_url"
    image_tablet = "image_url"
    image_phone = "image_url"
    faction_id = factory.SubFactory(FactionFactory)
    color_id = factory.SubFactory(ColorFactory)
    move_id = factory.SubFactory(MoveFactory)
    damage = 0
    hp = 10
    base_hp = 10
    shield = False
    has_passive = False
    has_passive_in_field = False
    has_passive_in_deck = False
    has_passive_in_grave = False
    passive_ability_id = None
    value = 0
    timer = 0
    default_timer = 0
    reset_timer = False
    each_tick = False
    has_deathwish = False
    deathwish_id = None
    deathwish_value = 0
    data = {}


class EnemyLeaderFactory(BaseModelFactory):
    class Meta:
        model = EnemyLeader

    name = factory.Sequence(lambda n: f"Enemy Leader {n + 1}")
    image_original = "image_url"
    image_tablet = "image_url"
    image_phone = "image_url"
    faction_id = factory.SubFactory(FactionFactory)
    hp = 100
    base_hp = 100
    ability_id = factory.SubFactory(EnemyLeaderAbilityFactory)
    has_passive = False
    passive_ability_id = None
    value = 0
    timer = 0
    default_timer = 0
    reset_timer = False
    each_tick = False
    data = {}


class SeasonFactory(BaseModelFactory):
    class Meta:
        model = Season

    name = factory.Sequence(lambda n: f"Season {n}")
    description = factory.Faker("paragraph")
    unlocked = False
    x = 0
    y = 0


class LevelFactory(BaseModelFactory):
    class Meta:
        model = Level

    name = factory.Sequence(lambda n: f"Level {n}")
    starting_enemies_number = 3
    difficulty = LevelDifficulty.EASY
    unlocked = False
    x = 0
    y = 0
    season_id = factory.SubFactory(SeasonFactory)
    enemy_leader_id = factory.SubFactory(EnemyLeaderFactory)


class LevelRelatedLevelsFactory(BaseModelFactory):
    class Meta:
        model = LevelRelatedLevels

    level_id = factory.SubFactory(LevelFactory)
    related_level_id = factory.SubFactory(LevelFactory)
    line = "right"
    connection = "1-2"


class SeasonRelatedSeasonsFactory(BaseModelFactory):
    class Meta:
        model = SeasonRelatedSeasons

    season_id = factory.SubFactory(SeasonFactory)
    related_season_id = factory.SubFactory(SeasonFactory)
    line = "right"
    connection = "1-2"


class LevelEnemyFactory(BaseModelFactory):
    class Meta:
        model = LevelEnemy

    level_id = factory.SubFactory(LevelFactory)
    enemy_id = factory.SubFactory(EnemyFactory)


class UserResourceFactory(BaseModelFactory):
    class Meta:
        model = UserResource

    id = factory.SubFactory(UserFactory)
    scraps = 1000
    raw_bronze = 0
    raw_silver = 0
    raw_gold = 0
    bronze_ingots = 0
    silver_ingots = 0
    gold_ingots = 0
    crops = 1000
    wood = 1000
    silk = 0
    kegs = 3
    big_kegs = 1
    chests = 0
    keys = 3
    rare_gem = 0
    money = 2000


class UserCardFactory(BaseModelFactory):
    class Meta:
        model = UserCard

    user_id = factory.SubFactory(UserFactory)
    card_id = factory.SubFactory(CardFactory)
    count = 1


class UserLeaderFactory(BaseModelFactory):
    class Meta:
        model = UserLeader

    user_id = factory.SubFactory(UserFactory)
    leader_id = factory.SubFactory(LeaderFactory)
    count = 1


class UserDeckFactory(BaseModelFactory):
    class Meta:
        model = UserDeck

    user_id = factory.SubFactory(UserFactory)
    deck_id = factory.SubFactory(DeckFactory)


class UserLevelFactory(BaseModelFactory):
    class Meta:
        model = UserLevel

    user_id = factory.SubFactory(UserFactory)
    level_id = factory.SubFactory(LevelFactory)
    finished = False


class UserSeasonFactory(BaseModelFactory):
    class Meta:
        model = UserSeason

    user_id = factory.SubFactory(UserFactory)
    season_id = factory.SubFactory(SeasonFactory)
    finished = False


class UserPreferenceFactory(BaseModelFactory):
    class Meta:
        model = UserPreferences

    id = factory.SubFactory(UserFactory)
    data = DEFAULT_PREFERENCES


class LeaderboardFactory(BaseModelFactory, TimeStampMixinFactory):
    class Meta:
        model = Leaderboard

    user_id = factory.SubFactory(UserFactory)
    leader_id = factory.SubFactory(LeaderFactory)
    mode = LeaderboardGameMode.SEASON
    max_kills = 1


class UserStatsFactory(BaseModelFactory, TimeStampMixinFactory):
    class Meta:
        model = UserStats

    user_id = factory.SubFactory(UserFactory)
    faction_id = factory.SubFactory(FactionFactory)
    type = UserStatsRecordType.PLAY
    count = 1
