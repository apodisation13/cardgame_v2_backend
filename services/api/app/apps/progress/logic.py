import logging

import asyncpg

from lib.utils.schemas.game import LevelDifficulty
from services.api.app.apps.cards.schemas import Card, CardForDeck, Deck, Enemy, EnemyLeader, Leader
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


logger = logging.getLogger(__name__)


async def process_enemies(
    connection: asyncpg.Connection,
    user_id: int,
    base_url: str,
) -> tuple[list[Enemy], list[EnemyLeader], list[UserSeason]]:
    # 1. собираем список врагов просто в единый список
    enemies: list[Enemy] = await get_enemies(
        connection=connection,
        base_url=base_url,
    )

    # 2. а тут собираем словарь из них: {enemy_id: весь_враг}
    enemies_dict = {}
    for enemy in enemies:
        enemies_dict[enemy.id] = enemy

    # 3. собираем список лидеров врагов просто в единый список
    enemy_leaders: list[EnemyLeader] = await get_enemy_leaders(
        connection=connection,
        base_url=base_url,
    )

    # 4. аналогично собираем словарь из них: {enemy_leader_id: весь_лидер_врага}
    enemy_leaders_dict = {}
    for enemy_leader in enemy_leaders:
        enemy_leaders_dict[enemy_leader.id] = enemy_leader

    # 5. список всех сезонов с уровнями
    seasons: list = await get_seasons(
        connection=connection,
        user_id=user_id,
    )

    # 6. из него выбираем список уникальных id уровней, множество id типа {1,2,3,4...etc}
    level_ids = {row["level_id"] for row in seasons}

    # 7. для всех уровней ищем всех их связи, даже если их нет
    # на выходе словарь: {level_id: [список связей]}
    level_related_levels: dict[int, list[LevelRelatedLevel]] = await get_level_related_levels(
        connection=connection,
        level_ids=level_ids,
    )

    # 8. из сезонов теперь так же выбираем уникальные id самих сезонов, множество id типа {1,2,3...}
    season_ids = {row["season_id"] for row in seasons}

    # 9. для всех сезонов ищем все их связи, даже если их нет
    # на выходе словарь: {season_id: [список связей]}
    season_related_seasons: dict[int, list[SeasonRelatedSeason]] = await get_season_related_seasons(
        connection=connection,
        season_ids=season_ids,
    )

    # 10. финал - собираем их всех этих данных единую структуру
    user_seasons: list[UserSeason] = await construct_seasons(
        seasons=seasons,
        enemies_dict=enemies_dict,
        enemy_leaders_dict=enemy_leaders_dict,
        level_related_levels=level_related_levels,
        season_related_seasons=season_related_seasons,
    )

    return enemies, enemy_leaders, user_seasons


async def get_enemies(
    connection: asyncpg.Connection,
    base_url: str,
) -> list[Enemy]:
    enemies = await connection.fetch(
        """
            SELECT
                enemies.id,
                enemies.name,
                enemies.image_original AS image,
                factions.name AS faction_name,
                colors.name AS color_name,
                moves.name AS move_name,
                moves.description AS move_description,
                enemies.damage,
                enemies.hp,
                enemies.base_hp,
                enemies.shield,
                enemies.has_passive,
                enemies.has_passive_in_field,
                enemies.has_passive_in_grave,
                enemies.has_passive_in_deck,
                enemy_passive_abilities.name AS passive_ability_name,
                enemy_passive_abilities.description AS passive_ability_description,
                enemies.value,
                enemies.timer,
                enemies.default_timer,
                enemies.reset_timer,
                enemies.each_tick,
                enemies.has_deathwish,
                deathwishes.name AS deathwish_name,
                deathwishes.description AS deathwish_description,
                enemies.deathwish_value,
                enemies.data
            FROM
                enemies
            JOIN
                factions ON enemies.faction_id = factions.id
            JOIN
                colors ON enemies.color_id = colors.id
            JOIN
                moves ON enemies.move_id = moves.id
            LEFT JOIN
                deathwishes ON enemies.deathwish_id = deathwishes.id
            LEFT JOIN
                enemy_passive_abilities ON enemies.passive_ability_id = enemy_passive_abilities.id
        """,
    )
    return [Enemy.get_one(row, base_url) for row in enemies]


async def get_enemy_leaders(
    connection: asyncpg.Connection,
    base_url: str,
) -> list[EnemyLeader]:
    enemy_leaders = await connection.fetch(
        """
            SELECT
                enemy_leaders.id,
                enemy_leaders.name,
                enemy_leaders.image_original AS image,
                factions.name AS faction_name,
                enemy_leaders.hp,
                enemy_leaders.base_hp,
                enemy_leader_abilities.name AS ability_name,
                enemy_leader_abilities.description AS ability_description,
                enemy_leaders.has_passive,
                enemy_passive_abilities.name AS passive_ability_name,
                enemy_passive_abilities.description AS passive_ability_description,
                enemy_leaders.value,
                enemy_leaders.timer,
                enemy_leaders.default_timer,
                enemy_leaders.reset_timer,
                enemy_leaders.each_tick,
                enemy_leaders.data
            FROM
                enemy_leaders
            JOIN
                factions ON enemy_leaders.faction_id = factions.id
            LEFT JOIN
                enemy_leader_abilities ON enemy_leaders.ability_id = enemy_leader_abilities.id
            LEFT JOIN
                enemy_passive_abilities ON enemy_leaders.passive_ability_id = enemy_passive_abilities.id
        """,
    )
    return [EnemyLeader.get_one(row, base_url) for row in enemy_leaders]


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
    seasons: list,
    enemies_dict: dict,
    enemy_leaders_dict: dict,
    level_related_levels: dict[int, list[LevelRelatedLevel]],
    season_related_seasons: dict[int, list[SeasonRelatedSeason]],
) -> list[UserSeason]:
    user_seasons_dict = {}
    levels_dict = {}

    # 1. тут мы идем по всем записям сезоны+уровни+враги и вначале набираем врагов в уровень!
    for row in seasons:
        enemy_id: int = row["enemy_id"]  # достаем только id врага
        enemy: Enemy = enemies_dict[enemy_id]  # а отсюда берем по id врага весь объект врага

        level_id = row["level_id"]  # достаем id уровня

        # если уровня нет в суммарном словаре
        if level_id not in levels_dict:
            # лидера врага надо положить в принципе только 1 раз
            enemy_leader_id: int = row["enemy_leader_id"]  # берем id лидера врагов
            enemy_leader: EnemyLeader = enemy_leaders_dict[enemy_leader_id]  # и сам объект лидера врагов

            # собираем объект уровня, а в список его врагов кладем пока что первого по счету врага
            # детей этого уровня - берем из словаря всех связей по id самогО уровня level_id
            level = Level(
                id=row["level_id"],
                name=row["level_name"],
                difficulty=row["difficulty"],
                starting_enemies_number=row["starting_enemies_number"],
                x=row["x"],
                y=row["y"],
                enemy_leader=enemy_leader,
                enemies=[enemy],
                children=level_related_levels[level_id],
            )
            levels_dict[level_id] = level  # и так же положили в итоговый словарь весь объект уровня
        else:
            # попали в уровень, который уже есть в итоговом словаре, достаточно просто добавить туда нового врага
            level: Level = levels_dict[level_id]
            level.enemies.append(enemy)

    # 2. а вот тут идем еще раз по общему списку и уже собираем сезоны+уровни, ведь враги и связи уровней уже собраны
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


async def process_cards(
    connection: asyncpg.Connection,
    user_id: int,
    base_url: str,
) -> tuple[list[UserCard], list[UserLeader], list[UserDeck]]:
    user_cards: list[UserCard] = await get_user_cards(
        connection=connection,
        user_id=user_id,
        base_url=base_url,
    )

    users_card_dict = {}
    for card in user_cards:
        users_card_dict[card.card.id] = card.card

    user_leaders: list[UserLeader] = await get_user_leaders(
        connection=connection,
        user_id=user_id,
        base_url=base_url,
    )

    users_leaders_dict = {}
    for leader in user_leaders:
        users_leaders_dict[leader.card.id] = leader.card

    user_decks: list[UserDeck] = await construct_user_decks(
        connection=connection,
        user_id=user_id,
        users_card_dict=users_card_dict,
        users_leaders_dict=users_leaders_dict,
    )

    return user_cards, user_leaders, user_decks


async def get_user_cards(
    connection: asyncpg.Connection,
    user_id: int,
    base_url: str,
) -> list[UserCard]:
    user_cards: list[dict] = await connection.fetch(
        """
            SELECT
                cards.id,
                cards.name,
                cards.image_original AS image,
                cards.unlocked,
                factions.name AS faction_name,
                colors.name AS color_name,
                types.name AS type_name,
                abilities.name AS ability_name,
                abilities.description AS ability_description,
                cards.damage,
                cards.charges,
                cards.hp,
                cards.heal,
                cards.armor,
                cards.has_passive,
                cards.has_passive_in_hand,
                cards.has_passive_in_deck,
                cards.has_passive_in_grave,
                passive_abilities.name AS passive_ability_name,
                passive_abilities.description AS passive_ability_description,
                cards.value,
                cards.timer,
                cards.default_timer,
                cards.reset_timer,
                cards.each_tick,
                cards.newly_added,
                cards.data,
                COALESCE(user_cards.count, 0) AS user_card_count,
                user_cards.id AS user_card_id
            FROM
                cards
            LEFT JOIN
                user_cards ON cards.id = user_cards.card_id AND user_cards.user_id = $1
            JOIN
                factions ON cards.faction_id = factions.id
            JOIN
                colors ON cards.color_id = colors.id
            JOIN
                types ON cards.type_id = types.id
            JOIN
                abilities ON cards.ability_id = abilities.id
            LEFT JOIN
                passive_abilities ON cards.passive_ability_id = passive_abilities.id
            ORDER BY
                cards.color_id DESC,
                cards.damage DESC,
                cards.hp DESC,
                cards.charges DESC
        """,
        user_id,
    )

    return [
        UserCard(
            id=user_card["user_card_id"],
            count=user_card["user_card_count"],
            card=Card.get_one(user_card, base_url),
        )
        for user_card in user_cards
    ]


async def get_user_leaders(
    connection: asyncpg.Connection,
    user_id: int,
    base_url: str,
) -> list[UserLeader]:
    user_leaders: list[dict] = await connection.fetch(
        """
            SELECT
                leaders.id,
                leaders.name,
                leaders.image_original AS image,
                leaders.unlocked,
                factions.name AS faction_name,
                abilities.name AS ability_name,
                abilities.description AS ability_description,
                leaders.hp,
                leaders.damage,
                leaders.charges,
                leaders.heal,
                leaders.armor,
                leaders.has_passive,
                passive_abilities.name AS passive_ability_name,
                passive_abilities.description AS passive_ability_description,
                leaders.value,
                leaders.timer,
                leaders.default_timer,
                leaders.reset_timer,
                leaders.newly_added,
                leaders.data,
                COALESCE(user_leaders.count, 0) AS user_leader_count,
                user_leaders.id AS user_leader_id
            FROM
                leaders
            LEFT JOIN
                user_leaders ON leaders.id = user_leaders.leader_id AND user_leaders.user_id = $1
            JOIN
                factions ON leaders.faction_id = factions.id
            JOIN
                abilities ON leaders.ability_id = abilities.id
            LEFT JOIN
                passive_abilities ON leaders.passive_ability_id = passive_abilities.id
            ORDER BY
                leaders.faction_id,
                leaders.hp DESC,
                leaders.charges DESC
        """,
        user_id,
    )
    return [
        UserLeader(
            id=user_leader["user_leader_id"],
            count=user_leader["user_leader_count"],
            card=Leader.get_one(user_leader, base_url),
        )
        for user_leader in user_leaders
    ]


async def construct_user_decks(
    connection: asyncpg.Connection,
    user_id: int,
    users_card_dict: dict,
    users_leaders_dict: dict,
) -> list[UserDeck]:
    user_decks: list[dict] = await connection.fetch(
        """
            SELECT
                user_decks.id AS user_deck_id,
                decks.id AS deck_id,
                decks.name AS deck_name,
                decks.leader_id AS leader_id,
                card_decks.card_id AS card_id
            FROM
                user_decks
            JOIN decks ON user_decks.deck_id = decks.id
            JOIN card_decks ON decks.id = card_decks.deck_id
            WHERE
                user_decks.user_id = $1
            ORDER BY decks.updated_at DESC;
        """,
        user_id,
    )

    user_decs_dict = {}

    for row in user_decks:
        user_deck_id = row["user_deck_id"]

        card_id: int = row["card_id"]
        card: Card = users_card_dict[card_id]
        hp = card.hp
        card_for_deck = CardForDeck(card=card)

        if user_deck_id not in user_decs_dict:
            deck_id: int = row["deck_id"]
            deck_name: str = row["deck_name"]
            leader_id: int = row["leader_id"]
            leader: Leader = users_leaders_dict[leader_id]

            user_decs_dict[user_deck_id] = UserDeck(
                id=user_deck_id,
                deck=Deck(
                    id=deck_id,
                    name=deck_name,
                    leader=leader,
                    health=hp + leader.hp,  # при первом заходе сюда добавляем сразу и жизни лидера, и первой карты
                    cards=[card_for_deck],
                ),
            )
        else:
            user_deck: UserDeck = user_decs_dict[user_deck_id]
            user_deck.deck.cards.append(card_for_deck)
            user_deck.deck.health += hp

    # user_decks_model = []
    # for _, user_deck in user_decs_dict.items():
    #     user_decks_model.append(user_deck)

    return list(user_decs_dict.values())


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
                money
            FROM user_resources
            WHERE id = $1
        """,
        user_id,
    )
    return UserResources.get_one(user_resources)


async def get_game_constants(
    connection: asyncpg.Connection,
) -> dict:
    game_constants: dict = await connection.fetchval("""SELECT data::jsonb FROM game_constants""")
    return game_constants


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
