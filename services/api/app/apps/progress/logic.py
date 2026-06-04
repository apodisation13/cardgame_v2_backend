import logging

import asyncpg

from lib.utils.schemas.game import LevelDifficulty, ResourceType, UpgradeSubtype, UpgradeType
from services.api.app.apps.cards.schemas import Deck
from services.api.app.apps.game_const import logic as game_const_logic
from services.api.app.apps.progress.schemas import (
    Level,
    LevelRelatedLevel,
    Season,
    SeasonRelatedSeason,
    Stats,
    UserCard,
    UserDeck,
    UserLeader,
    UserLevel,
    UserResources,
    UserSeason,
)
from services.api.app.exceptions.exceptions import NegativeResourcesError


logger = logging.getLogger(__name__)


async def get_seasons(
    connection: asyncpg.Connection,
    user_id: int,
) -> list:
    return await connection.fetch(
        """
            SELECT
                seasons.id AS season_id,
                seasons.name AS season_name,
                seasons.description AS season_description,
                seasons.unlocked AS season_unlocked,
                seasons.x AS season_x,
                seasons.y AS season_y,
                levels.id AS level_id,
                levels.name AS level_name,
                levels.difficulty,
                levels.starting_enemies_number,
                levels.x,
                levels.y,
                user_levels.id AS user_level_id,
                user_levels.finished AS user_level_finished,
                levels.enemy_leader_id AS enemy_leader_id,
                level_enemies.enemy_id AS enemy_id,
                user_seasons.id AS user_season_id,
                user_seasons.finished AS user_season_finished
            FROM seasons
            JOIN levels ON seasons.id = levels.season_id
            JOIN level_enemies ON levels.id = level_enemies.level_id
            LEFT JOIN user_levels ON levels.id = user_levels.level_id AND user_levels.user_id = $1
            LEFT JOIN user_seasons ON user_seasons.season_id = seasons.id AND user_seasons.user_id = $1
            ORDER BY seasons.id;
        """,
        user_id,
    )


async def get_level_related_levels(
    connection: asyncpg.Connection,
    level_ids: set[int],
) -> dict[int, list[LevelRelatedLevel]]:
    # возвращает словарь, где ключ это id уровня, значение - список его связей (даже если связей нет)
    all_related_levels = await connection.fetch(
        """
            SELECT
                levels.id,
                level_related_levels.related_level_id,
                level_related_levels.line,
                level_related_levels.connection
            FROM levels
            LEFT JOIN level_related_levels ON levels.id = level_related_levels.level_id
            WHERE levels.id = ANY ($1)
        """,
        level_ids,
    )

    level_ids_dict = {}
    for row in all_related_levels:
        level_id = row["id"]
        level_related_level = LevelRelatedLevel(
            line=row["line"],
            connection=row["connection"],
            related_level_id=row["related_level_id"],
        )
        if level_id not in level_ids_dict:
            level_ids_dict[level_id] = [level_related_level]
        else:
            level_ids_dict[level_id].append(level_related_level)

    return level_ids_dict


async def get_season_related_seasons(
    connection: asyncpg.Connection,
    season_ids: set[int],
) -> dict[int, list[SeasonRelatedSeason]]:
    # возвращает словарь, где ключ это id сезона, значение - список его связей (даже если связей нет)
    all_related_seasons = await connection.fetch(
        """
            SELECT
                seasons.id,
                season_related_seasons.related_season_id,
                season_related_seasons.line,
                season_related_seasons.connection
            FROM seasons
            LEFT JOIN season_related_seasons ON season_related_seasons.season_id = seasons.id
            WHERE seasons.id = ANY ($1)
        """,
        season_ids,
    )

    season_ids_dict = {}
    for row in all_related_seasons:
        season_id = row["id"]
        season_related_season = SeasonRelatedSeason(
            line=row["line"],
            connection=row["connection"],
            related_season_id=row["related_season_id"],
        )
        if season_id not in season_ids_dict:
            season_ids_dict[season_id] = [season_related_season]
        else:
            season_ids_dict[season_id].append(season_related_season)

    return season_ids_dict


async def construct_seasons(
    connection: asyncpg.Connection,
    user_id: int,
) -> list[UserSeason]:
    # 1. список всех сезонов с уровнями
    seasons: list = await get_seasons(
        connection=connection,
        user_id=user_id,
    )

    # 2. из него выбираем список уникальных id уровней, множество id типа {1,2,3,4...etc}
    level_ids = {row["level_id"] for row in seasons}

    # 3. для всех уровней ищем всех их связи, даже если их нет
    # на выходе словарь: {level_id: [список связей]}
    level_related_levels: dict[int, list[LevelRelatedLevel]] = await get_level_related_levels(
        connection=connection,
        level_ids=level_ids,
    )

    # 4. из сезонов теперь так же выбираем уникальные id самих сезонов, множество id типа {1,2,3...}
    season_ids = {row["season_id"] for row in seasons}

    # 5. для всех сезонов ищем все их связи, даже если их нет
    # на выходе словарь: {season_id: [список связей]}
    season_related_seasons: dict[int, list[SeasonRelatedSeason]] = await get_season_related_seasons(
        connection=connection,
        season_ids=season_ids,
    )

    user_seasons_dict = {}
    levels_dict = {}

    # 6. тут мы идем по всем записям сезоны+уровни+враги и вначале набираем врагов в уровень!
    for row in seasons:
        enemy_id: int = row["enemy_id"]  # достаем только id врага
        level_id = row["level_id"]  # достаем id уровня

        # если уровня нет в суммарном словаре
        if level_id not in levels_dict:
            # лидера врага надо положить в принципе только 1 раз
            enemy_leader_id: int = row["enemy_leader_id"]  # берем id лидера врагов

            # собираем объект уровня, а в список его врагов кладем пока что первого по счету врага
            # детей этого уровня - берем из словаря всех связей по id самогО уровня level_id
            level = Level(
                id=row["level_id"],
                name=row["level_name"],
                difficulty=row["difficulty"],
                starting_enemies_number=row["starting_enemies_number"],
                x=row["x"],
                y=row["y"],
                enemy_leader=enemy_leader_id,
                enemies=[enemy_id],
                children=level_related_levels[level_id],
            )
            levels_dict[level_id] = level  # и так же положили в итоговый словарь весь объект уровня
        else:
            # попали в уровень, который уже есть в итоговом словаре, достаточно просто добавить туда нового врага
            level: Level = levels_dict[level_id]
            level.enemies.append(enemy_id)

    # 7. а вот тут идем еще раз по общему списку и уже собираем сезоны+уровни, ведь враги и связи уровней уже собраны
    for row in seasons:
        season_id = row["season_id"]  # запоминаем id сезона

        level_id = row["level_id"]  # берем id уровня
        level: Level = levels_dict[level_id]  # и находим весь объект уровня в словаре, который выше собирали

        # составляем нужную структуру
        user_level = UserLevel(
            id=row["user_level_id"],  # это id в таблице user_levels.id. есть - уровень открыт, нет - закрыт
            level=level,
            finished=row["user_level_finished"],  # уровень может быть пройден или нет
            unlocked=True if row["user_level_id"] else False,
        )

        # тут мы берем какой-то сезон первый раз
        if season_id not in user_seasons_dict:
            # собираем статистику в зависимости от уровня и пройден ли он
            stats = Stats(
                total_levels=1,
                finished_levels=1 if user_level.finished else 0,
                unlocked_levels=1 if user_level.unlocked else 0,
                easy_levels=1 if level.difficulty == LevelDifficulty.EASY else 0,
                normal_levels=1 if level.difficulty == LevelDifficulty.NORMAL else 0,
                hard_levels=1 if level.difficulty == LevelDifficulty.HARD else 0,
            )
            # собираем объект сезона, уровень сезона при первом заходе кладем в список, связи тоже для сезона нашли
            season = Season(
                id=season_id,
                name=row["season_name"],
                description=row["season_description"],
                x=row["season_x"],
                y=row["season_y"],
                levels=[user_level],
                children=season_related_seasons[season_id],
            )
            user_season = UserSeason(
                id=row["user_season_id"],
                season=season,
                finished=row["user_season_finished"],
                stats=stats,
            )
            user_seasons_dict[season_id] = user_season
        else:
            # а здесь наполняем сезон разными уровнями и добавляем статистику
            season: Season = user_seasons_dict[season_id].season

            if user_level not in season.levels:
                stats: Stats = user_seasons_dict[season_id].stats
                stats.total_levels += 1
                stats.finished_levels += 1 if user_level.finished else 0
                stats.unlocked_levels += 1 if user_level.unlocked else 0
                stats.easy_levels += 1 if level.difficulty == LevelDifficulty.EASY else 0
                stats.normal_levels += 1 if level.difficulty == LevelDifficulty.NORMAL else 0
                stats.hard_levels += 1 if level.difficulty == LevelDifficulty.HARD else 0

                season.levels.append(user_level)

    return list(user_seasons_dict.values())


async def get_user_cards(
    connection: asyncpg.Connection,
    user_id: int,
) -> dict[int, UserCard]:
    user_cards: list[dict] = await connection.fetch(
        """
            SELECT
                user_cards.id AS user_card_id,
                user_cards.card_id,
                user_cards.count
            FROM
                user_cards
            WHERE
                user_cards.user_id = $1
        """,
        user_id,
    )

    return {
        row["card_id"]: UserCard(
            user_card_id=row["user_card_id"],
            count=row["count"],
        )
        for row in user_cards
    }


async def get_user_leaders(
    connection: asyncpg.Connection,
    user_id: int,
) -> dict[int, UserLeader]:
    user_leaders: list[dict] = await connection.fetch(
        """
            SELECT
                user_leaders.id AS user_leader_id,
                user_leaders.leader_id,
                user_leaders.count
            FROM
                user_leaders
            WHERE
                user_leaders.user_id = $1
        """,
        user_id,
    )

    return {
        row["leader_id"]: UserLeader(
            user_leader_id=row["user_leader_id"],
            count=row["count"],
        )
        for row in user_leaders
    }


async def construct_user_decks(
    connection: asyncpg.Connection,
    user_id: int,
) -> list[UserDeck]:
    user_decks: list[dict] = await connection.fetch(
        """
            SELECT
                user_decks.id AS user_deck_id,
                decks.id AS deck_id,
                decks.name AS deck_name,
                decks.leader_id AS leader_id,
                card_decks.card_id AS card_id,
                cards.data -> 'hp' AS card_hp,
                leaders.data -> 'hp' AS leader_hp
            FROM
                user_decks
            JOIN decks ON user_decks.deck_id = decks.id
            JOIN card_decks ON decks.id = card_decks.deck_id
            JOIN cards ON card_decks.card_id = cards.id
            JOIN leaders ON decks.leader_id = leaders.id
            WHERE
                user_decks.user_id = $1
            ORDER BY decks.updated_at DESC;
        """,
        user_id,
    )

    user_decks_dict = {}

    for row in user_decks:
        user_deck_id = row["user_deck_id"]

        card_id: int = row["card_id"]
        card_hp = row["card_hp"]

        if user_deck_id not in user_decks_dict:
            deck_id: int = row["deck_id"]
            deck_name: str = row["deck_name"]
            leader_id: int = row["leader_id"]
            leader_hp: int = row["leader_hp"]

            user_decks_dict[user_deck_id] = UserDeck(
                user_deck_id=user_deck_id,
                deck=Deck(
                    id=deck_id,
                    name=deck_name,
                    leader_id=leader_id,
                    health=card_hp + leader_hp,  # при первом заходе сюда добавляем сразу и жизни лидера, и первой карты
                    cards=[card_id],
                ),
            )
        else:
            user_deck: UserDeck = user_decks_dict[user_deck_id]
            user_deck.deck.cards.append(card_id)
            user_deck.deck.health += card_hp

    return list(user_decks_dict.values())


async def get_user_resources(
    user_id: int,
    connection: asyncpg.Connection,
) -> UserResources:
    user_resources = await connection.fetchrow(
        """
            SELECT
                scraps,
                raw_bronze,
                raw_silver,
                raw_gold,
                bronze_ingots,
                silver_ingots,
                gold_ingots,
                crops,
                wood,
                silk,
                kegs,
                big_kegs,
                chests,
                keys,
                rare_gem,
                money,
                flowers,
                first_aid_kits,
                shields
            FROM user_resources
            WHERE id = $1
        """,
        user_id,
    )
    return UserResources.get_one(user_resources)


async def change_resources(
    connection: asyncpg.Connection,
    user_id: int,
    resources_to_change: dict[ResourceType, int],
    scenario: str,
) -> UserResources:
    if any(delta > 0 for delta in resources_to_change.values()):
        current_resources: UserResources = await get_user_resources(
            connection=connection,
            user_id=user_id,
        )
        resources_to_change = await cap_resources_to_max(
            connection=connection,
            resources_to_change=resources_to_change,
            current_resources=current_resources,
            user_id=user_id,
        )

    set_parts = []
    query_params = [user_id]

    for i, (resource, delta) in enumerate(resources_to_change.items(), start=2):
        set_parts.append(f"{resource} = {resource} + ${i}")
        query_params.append(delta)

    set_parts.append("updated_at = NOW()")

    query = f"""
        UPDATE user_resources
        SET {", ".join(set_parts)}
        WHERE id = $1
        RETURNING *
    """  # noqa: S608

    result = await connection.fetchrow(query, *query_params)
    user_resources: UserResources = UserResources.get_one(result)

    await validate_non_negative_values(
        resources_to_change=resources_to_change,
        user_resources=user_resources,
        user_id=user_id,
        scenario=scenario,
    )

    return user_resources


async def validate_non_negative_values(
    resources_to_change: dict,
    user_resources: UserResources,
    user_id: int,
    scenario: str,
) -> None:
    for r in resources_to_change:
        actual_resource: int = getattr(user_resources, r)
        if actual_resource < 0:
            msg = "Scenario: %s, user_id: %s, resource: %s - insufficient resources (actual: %s)"
            logger.error(msg, scenario, user_id, r, actual_resource)
            raise NegativeResourcesError(
                msg % (scenario, user_id, r, actual_resource),
            )


async def cap_resources_to_max(
    connection: asyncpg.Connection,
    resources_to_change: dict[ResourceType, int],
    current_resources: UserResources,
    user_id: int,
) -> dict[ResourceType, int]:
    user_upgrades: dict = await connection.fetchval(
        """
            SELECT
                user_upgrades.data::jsonb
            FROM
                user_upgrades
            WHERE user_upgrades.id = $1
        """,
        user_id,
    )
    game_const: dict = await game_const_logic.get_game_constants(
        connection=connection,
    )
    upgrades_config: dict = game_const["upgrades"]

    adjusted = dict(resources_to_change)
    for resource_type, delta in resources_to_change.items():
        if delta <= 0 or resource_type == ResourceType.KEYS:
            continue

        if resource_type == ResourceType.MONEY:
            correct_upgrade_subtype = UpgradeSubtype.MONEY
        elif resource_type == ResourceType.SCRAPS:
            correct_upgrade_subtype = UpgradeSubtype.SCRAPS
        elif resource_type == ResourceType.SILK:
            correct_upgrade_subtype = UpgradeSubtype.SILK
        elif resource_type == ResourceType.RARE_GEM:
            correct_upgrade_subtype = UpgradeSubtype.RARE_GEMS
        elif resource_type in (ResourceType.CROPS, ResourceType.WOOD):
            correct_upgrade_subtype = UpgradeSubtype.WOOD
        elif resource_type in (ResourceType.BRONZE_INGOTS, ResourceType.SILVER_INGOTS, ResourceType.GOLD_INGOTS):
            correct_upgrade_subtype = UpgradeSubtype.INGOTS
        elif resource_type in (ResourceType.RAW_BRONZE, ResourceType.RAW_SILVER, ResourceType.RAW_GOLD):
            correct_upgrade_subtype = UpgradeSubtype.RAW
        elif resource_type in (ResourceType.KEGS, ResourceType.BIG_KEGS, ResourceType.CHESTS):
            correct_upgrade_subtype = UpgradeSubtype.KEGS
        elif resource_type == ResourceType.FLOWERS:
            correct_upgrade_subtype = UpgradeSubtype.FLOWERS
        elif resource_type == ResourceType.FIRST_AID_KITS:
            correct_upgrade_subtype = UpgradeSubtype.FIRST_AID_KITS
        elif resource_type == ResourceType.SHIELDS:
            correct_upgrade_subtype = UpgradeSubtype.SHIELDS
        else:
            raise ValueError(f"Unknown resource type for max cap: {resource_type}")

        user_upgrade_level: int = user_upgrades[UpgradeType.RESOURCES][correct_upgrade_subtype]
        level_data: dict = upgrades_config[UpgradeType.RESOURCES]["upgrades"][correct_upgrade_subtype]["upgrades"][
            str(user_upgrade_level)
        ]
        max_value: int = level_data["value"]

        current_value: int = getattr(current_resources, resource_type)
        adjusted[resource_type] = min(delta, max(0, max_value - current_value))

    return adjusted


async def open_default_content(
    connection: asyncpg.Connection,
    user_id: int,
):
    logger.info("Opening default content for user: %s", user_id)

    # 1. берем все открытые по умолчанию карты
    cards = await connection.fetch("""SELECT cards.id FROM cards WHERE cards.unlocked IS TRUE""")
    logger.info("Number of default cards to insert: %s", len(cards))

    # 2. инзертим их юзеру
    user_cards = await connection.fetch(
        """
            INSERT INTO user_cards (user_id, card_id, count)
            SELECT $1, s.card_id, 1
            FROM unnest($2::int[]) AS s(card_id)
            RETURNING id
        """,
        user_id,
        [card["id"] for card in cards],
    )
    logger.info("Number of user_cards inserted: %s", len(user_cards))

    if len(user_cards) != len(cards):
        msg = "Number of unlocked cards %s does not match number of inserted user_cards %"
        logger.error(msg, len(cards), len(user_cards))
        raise Exception(msg % (len(cards), len(user_cards)))

    # 3. берем всех открытых по умолчанию лидеров
    leaders = await connection.fetch("""SELECT leaders.id FROM leaders WHERE leaders.unlocked IS TRUE""")
    logger.info("Number of default leaders to insert: %s", len(leaders))

    # 4. инзертим их юзеру
    user_leaders = await connection.fetch(
        """
            INSERT INTO user_leaders (user_id, leader_id, count)
            SELECT $1, s.leader_id, 1
            FROM unnest($2::int[]) AS s(leader_id)
            RETURNING id
        """,
        user_id,
        [card["id"] for card in leaders],
    )
    logger.info("Number of user_leaders inserted: %s", len(user_leaders))

    if len(user_leaders) != len(leaders):
        msg = "Number of unlocked leaders %s does not match number of inserted user_leaders %s"
        logger.error(msg, len(leaders), len(user_leaders))
        raise Exception(msg % (len(leaders), len(user_leaders)))

    # 5. инзертим юзеру base-desk
    await connection.execute(
        """
            INSERT INTO user_decks
            (user_id, deck_id)
            VALUES ($1, 1)
        """,
        user_id,
    )
    logger.info("Inserted user_desk for base-deck")

    # 6. берем все открытые по умолчанию уровни
    levels = await connection.fetch("""SELECT levels.id FROM levels WHERE levels.unlocked IS TRUE""")
    logger.info("Number of default levels to insert: %s", len(levels))

    # 7. инзертим их юзеру
    user_levels = await connection.fetch(
        """
            INSERT INTO user_levels (user_id, level_id)
            SELECT $1, s.level_id
            FROM unnest($2::int[]) AS s(level_id)
            RETURNING id
        """,
        user_id,
        [level["id"] for level in levels],
    )
    logger.info("Number of user_levels inserted: %s", len(user_levels))

    if len(user_levels) != len(levels):
        msg = "Number of unlocked levels %s does not match number of inserted user_levels %s"
        logger.error(msg, len(levels), len(user_levels))
        raise Exception(msg % (len(levels), len(user_levels)))

    # 8. берем все открытые по умолчанию сезоны
    seasons = await connection.fetch("""SELECT seasons.id FROM seasons WHERE seasons.unlocked IS TRUE""")
    logger.info("Number of default seasons to insert: %s", len(seasons))

    # 9. инзертим их юзеру
    user_seasons = await connection.fetch(
        """
            INSERT INTO user_seasons (user_id, season_id)
            SELECT $1, s.season_id
            FROM unnest($2::int[]) AS s(season_id)
            RETURNING id
        """,
        user_id,
        [season["id"] for season in seasons],
    )
    logger.info("Number of user_seasons inserted: %s", len(user_seasons))

    if len(user_seasons) != len(seasons):
        msg = "Number of unlocked seasons %s does not match number of inserted user_seasons %s"
        logger.error(msg, len(seasons), len(user_seasons))
        raise Exception(msg % (len(seasons), len(user_seasons)))

    # 10. создаем юзеру дефолтные ресурсы - они указаны напрямую в БД
    await connection.execute("""INSERT INTO user_resources (id) VALUES ($1)""", user_id)

    logger.info("Finished creating user database for user %s", user_id)
