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
    Level,
    LevelEnemy,
    LevelRelatedLevels,
    Move,
    PassiveAbility,
    Season,
    Type,
    UserCard,
    UserDeck,
    UserLeader,
    UserLevel,
    UserResource,
)


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
        "mill_gold": 200,
        "craft_gold": -2000,
        "mill_bronze": 20,
        "mill_leader": 300,
        "mill_silver": 100,
        "craft_bronze": -200,
        "craft_leader": -3000,
        "craft_silver": -1000,
        "pay_for_kegs": -200,
        "pay_for_chests": -2000,
        "win_level_easy": 125,
        "win_level_hard": 500,
        "play_level_easy": -50,
        "play_level_hard": -200,
        "pay_for_big_kegs": -400,
        "win_level_normal": 275,
        "play_level_normal": -100,
        "number_of_cards_in_deck": 12,
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

    name = factory.Sequence(lambda n: f"Leader {n}")
    image_original = factory.Faker("image_url")
    image_tablet = factory.Faker("image_url")
    image_phone = factory.Faker("image_url")
    unlocked = False
    faction_id = factory.SubFactory(FactionFactory)
    ability_id = factory.SubFactory(AbilityFactory)
    damage = 0
    charges = 1
    heal = 0
    has_passive = False
    passive_ability_id = None
    value = 0
    timer = 0
    default_timer = 0
    reset_timer = False


class CardFactory(BaseModelFactory):
    class Meta:
        model = Card

    name = factory.Sequence(lambda n: f"Card {n}")
    image_original = factory.Faker("image_url")
    image_tablet = factory.Faker("image_url")
    image_phone = factory.Faker("image_url")
    unlocked = False
    faction_id = factory.SubFactory(FactionFactory)
    color_id = factory.SubFactory(ColorFactory)
    type_id = factory.SubFactory(TypeFactory)
    ability_id = factory.SubFactory(AbilityFactory)
    damage = 0
    charges = 1
    hp = 0
    heal = 0
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

    name = factory.Sequence(lambda n: f"Enemy {n}")
    image_original = factory.Faker("image_url")
    image_tablet = factory.Faker("image_url")
    image_phone = factory.Faker("image_url")
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


class EnemyLeaderFactory(BaseModelFactory):
    class Meta:
        model = EnemyLeader

    name = factory.Sequence(lambda n: f"Enemy Leader {n}")
    image_original = factory.Faker("image_url")
    image_tablet = factory.Faker("image_url")
    image_phone = factory.Faker("image_url")
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


class SeasonFactory(BaseModelFactory):
    class Meta:
        model = Season

    name = factory.Sequence(lambda n: f"Season {n}")
    description = factory.Faker("paragraph")
    unlocked = False


class LevelFactory(BaseModelFactory):
    class Meta:
        model = Level

    name = factory.Sequence(lambda n: f"Level {n}")
    starting_enemies_number = 3
    difficulty = "NORMAL"
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
    wood = 1000
    kegs = 3
    big_kegs = 1
    chests = 0
    keys = 3


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
