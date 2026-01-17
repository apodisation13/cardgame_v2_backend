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
import pytest_asyncio
from services.api.tests.factories.factories import (
    AbilityFactory,
    CardDeckFactory,
    CardFactory,
    ColorFactory,
    DeathwishFactory,
    DeckFactory,
    EnemyFactory,
    EnemyLeaderAbilityFactory,
    EnemyLeaderFactory,
    EnemyPassiveAbilityFactory,
    FactionFactory,
    GameConstantsFactory,
    LeaderFactory,
    LevelEnemyFactory,
    LevelFactory,
    LevelRelatedLevelsFactory,
    MoveFactory,
    PassiveAbilityFactory,
    SeasonFactory,
    TypeFactory,
    UserCardFactory,
    UserDeckFactory,
    UserLeaderFactory,
    UserLevelFactory,
    UserResourceFactory,
)


# Базовые модели
@pytest_asyncio.fixture
def faction_factory(db_connection):
    async def factory(**kwargs) -> Faction:
        return await FactionFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def color_factory(db_connection):
    async def factory(**kwargs) -> Color:
        return await ColorFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def game_constants_factory(db_connection):
    async def factory(**kwargs) -> GameConstants:
        return await GameConstantsFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def type_factory(db_connection):
    async def factory(**kwargs) -> Type:
        return await TypeFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def ability_factory(db_connection):
    async def factory(**kwargs) -> Ability:
        return await AbilityFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def passive_ability_factory(db_connection):
    async def factory(**kwargs) -> PassiveAbility:
        return await PassiveAbilityFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


# Игровые элементы
@pytest_asyncio.fixture
def leader_factory(db_connection):
    async def factory(**kwargs) -> Leader:
        return await LeaderFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def card_factory(db_connection):
    async def factory(**kwargs) -> Card:
        return await CardFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def deck_factory(db_connection):
    async def factory(**kwargs) -> Deck:
        return await DeckFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def card_deck_factory(db_connection):
    async def factory(**kwargs) -> CardDeck:
        return await CardDeckFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


# Вражеские элементы
@pytest_asyncio.fixture
def move_factory(db_connection):
    async def factory(**kwargs) -> Move:
        return await MoveFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def enemy_passive_ability_factory(db_connection):
    async def factory(**kwargs) -> EnemyPassiveAbility:
        return await EnemyPassiveAbilityFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def enemy_leader_ability_factory(db_connection):
    async def factory(**kwargs) -> EnemyLeaderAbility:
        return await EnemyLeaderAbilityFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def deathwish_factory(db_connection):
    async def factory(**kwargs) -> Deathwish:
        return await DeathwishFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def enemy_factory(db_connection):
    async def factory(**kwargs) -> Enemy:
        return await EnemyFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def enemy_leader_factory(db_connection):
    async def factory(**kwargs) -> EnemyLeader:
        return await EnemyLeaderFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


# Уровни и сезоны
@pytest_asyncio.fixture
def season_factory(db_connection):
    async def factory(**kwargs) -> Season:
        return await SeasonFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def level_factory(db_connection):
    async def factory(**kwargs) -> Level:
        return await LevelFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def level_related_levels_factory(db_connection):
    async def factory(**kwargs) -> LevelRelatedLevels:
        return await LevelRelatedLevelsFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def level_enemy_factory(db_connection):
    async def factory(**kwargs) -> LevelEnemy:
        return await LevelEnemyFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


# Пользовательские данные
@pytest_asyncio.fixture
def user_resource_factory(db_connection):
    async def factory(**kwargs) -> UserResource:
        return await UserResourceFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def user_card_factory(db_connection):
    async def factory(**kwargs) -> UserCard:
        return await UserCardFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def user_leader_factory(db_connection):
    async def factory(**kwargs) -> UserLeader:
        return await UserLeaderFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def user_deck_factory(db_connection):
    async def factory(**kwargs) -> UserDeck:
        return await UserDeckFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
def user_level_factory(db_connection):
    async def factory(**kwargs) -> UserLevel:
        return await UserLevelFactory.create_in_db(conn=db_connection, **kwargs)

    return factory


@pytest_asyncio.fixture
async def init_db_cards(
    faction_factory,
    color_factory,
    type_factory,
    ability_factory,
    passive_ability_factory,
    leader_factory,
    card_factory,
    deck_factory,
    card_deck_factory,
    move_factory,
    enemy_leader_ability_factory,
    enemy_passive_ability_factory,
    deathwish_factory,
    enemy_factory,
    enemy_leader_factory,
    season_factory,
    level_factory,
    level_related_levels_factory,
    level_enemy_factory,
):
    """
    Создаем тут по цепочке:
    - 2 фракции
    - 3 цвета
    - 2 типа
    - 1 абилка
    - 1 пассивная абилка
    - 1 лидера (открытый)
    - 3 карты (2 открыты, 1 нет)
    - base-deck в которой есть лидер и 3 карты (через связи card_decks)
    - 2 типа хода врагов
    - 1 пассивка лидера врагов, 1 пассивка врагов, 1 завещание
    - 1 лидер врагов
    - 3 врага
    - 1 сезон
    - 3 уровня (1 открыт, 2 нет)
    - связи между сезоном и уровнем, уровнем и его детьми, уровнем и врагами
    """
    f1 = await faction_factory(name="Neutrals")
    f2 = await faction_factory(name="Soldiers")
    c1 = await color_factory(name="Bronze")
    c2 = await color_factory(name="Silver")
    c3 = await color_factory(name="Gold")
    t1 = await type_factory(name="Unit")
    t2 = await type_factory(name="Special")
    a = await ability_factory(name="Damage one", description="Damage one")
    pa = await passive_ability_factory(name="Passive ability", description="Passive ability")

    leader_1 = await leader_factory(
        faction_id=f1.id,
        ability_id=a.id,
        unlocked=True,
    )
    card_1 = await card_factory(
        faction_id=f1.id,
        ability_id=a.id,
        color_id=c1.id,
        type_id=t1.id,
        unlocked=True,
    )
    card_2 = await card_factory(
        faction_id=f2.id,
        ability_id=a.id,
        color_id=c2.id,
        type_id=t2.id,
        unlocked=True,
    )
    card_3 = await card_factory(
        faction_id=f2.id,
        ability_id=a.id,
        color_id=c3.id,
        type_id=t2.id,
        has_passive=True,
        passive_ability_id=pa.id,
    )

    base_deck = await deck_factory(
        name="base-deck",
        leader_id=leader_1.id,
    )
    await card_deck_factory(
        deck_id=base_deck.id,
        card_id=card_1.id,
    )
    await card_deck_factory(
        deck_id=base_deck.id,
        card_id=card_2.id,
    )
    await card_deck_factory(
        deck_id=base_deck.id,
        card_id=card_3.id,
    )

    m1 = await move_factory(name="Down")
    m2 = await move_factory(name="Right")
    ela = await enemy_leader_ability_factory(name="Enemy leader ability", description="Enemy leader ability")
    epa = await enemy_passive_ability_factory(name="Passive passive ability", description="Passive passive ability")
    deathwish = await deathwish_factory(name="Deathwish", description="Deathwish")

    enemy_leader = await enemy_leader_factory(
        faction_id=f1.id,
        ability_id=ela.id,
    )
    enemy_1 = await enemy_factory(
        faction_id=f1.id,
        color_id=c1.id,
        move_id=m1.id,
        has_passive=True,
        passive_ability_id=epa.id,
        has_deathwish=True,
        deathwish_id=deathwish.id,
    )
    enemy_2 = await enemy_factory(
        faction_id=f2.id,
        color_id=c2.id,
        move_id=m2.id,
    )
    enemy_3 = await enemy_factory(
        faction_id=f2.id,
        color_id=c3.id,
        move_id=m2.id,
    )

    s1 = await season_factory(
        name="Season 1",
        description="Season 1",
        unlocked=True,
    )
    l1 = await level_factory(
        name="Level 1",
        season_id=s1.id,
        enemy_leader_id=enemy_leader.id,
        unlocked=True,
    )
    l2 = await level_factory(
        name="Level 2",
        season_id=s1.id,
        enemy_leader_id=enemy_leader.id,
    )
    l3 = await level_factory(
        name="Level 3",
        season_id=s1.id,
        enemy_leader_id=enemy_leader.id,
    )

    await level_related_levels_factory(
        level_id=l1.id,
        related_level_id=l2.id,
    )
    await level_related_levels_factory(
        level_id=l1.id,
        related_level_id=l3.id,
    )
    await level_related_levels_factory(
        level_id=l2.id,
        related_level_id=l3.id,
    )

    await level_enemy_factory(
        level_id=l1.id,
        enemy_id=enemy_1.id,
    )
    await level_enemy_factory(
        level_id=l2.id,
        enemy_id=enemy_1.id,
    )
    await level_enemy_factory(
        level_id=l2.id,
        enemy_id=enemy_2.id,
    )
    await level_enemy_factory(
        level_id=l3.id,
        enemy_id=enemy_1.id,
    )
    await level_enemy_factory(
        level_id=l3.id,
        enemy_id=enemy_2.id,
    )
    await level_enemy_factory(
        level_id=l3.id,
        enemy_id=enemy_3.id,
    )
