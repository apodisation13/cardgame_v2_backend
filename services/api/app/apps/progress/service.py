import logging
from typing import TYPE_CHECKING

import asyncpg

from lib.utils.db.pool import Database
from lib.utils.schemas.game import (
    CardActionSubtype,
    CardColorName,
    LevelDifficulty,
    ResourceActionSubtype,
    ResourceType,
)
from services.api.app.apps.progress import logic
from services.api.app.apps.progress.schemas import (
    CardCraftBonusResponse,
    CardCraftMillResponse,
    CreateDeckRequest,
    ListDecksResponse,
    OpenRelatedLevelsResponse,
    ResourcesRequest,
    UserCard,
    UserDatabase,
    UserLeader,
    UserProgressResponse,
    UserResources,
)
from services.api.app.config import Config
from services.api.app.exceptions.exceptions import CraftMillCardProcessError, ManageResourcesProcessError


if TYPE_CHECKING:
    from services.api.app.apps.cards.schemas import Card


logger = logging.getLogger(__name__)


class UserProgressService:
    def __init__(
        self,
        db_pool: Database,
        config: Config,
    ):
        self.db_pool = db_pool
        self.config = config

    async def get_user_progress(
        self,
        user_id: int,
        base_url: str,
    ) -> UserProgressResponse:
        async with self.db_pool.connection() as connection:
            user_resources: UserResources = await logic.get_user_resources(
                connection=connection,
                user_id=user_id,
            )

            game_constants: dict = await logic.get_game_constants(
                connection=connection,
            )

            enemies, enemy_leaders, seasons = await logic.process_enemies(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )

            user_cards, user_leaders, user_decks = await logic.process_cards(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )

        return UserProgressResponse(
            user_database=UserDatabase(
                cards=user_cards,
                leaders=user_leaders,
                decks=user_decks,
            ),
            resources=user_resources,
            seasons=seasons,
            game_const=game_constants,
            enemies=enemies,
            enemy_leaders=enemy_leaders,
        )

    async def create_user_deck(
        self,
        user_id: int,
        deck: CreateDeckRequest,
        base_url: str,
    ) -> ListDecksResponse:
        async with self.db_pool.transaction() as connection:
            deck_id = await connection.fetchval(
                """
                    INSERT INTO decks
                    (name, leader_id)
                    VALUES ($1, $2)
                    RETURNING id
                """,
                deck.deck_name,
                deck.leader_id,
            )
            print("STR110", deck_id)

            card_decks: list[tuple[deck_id, Card.id]] = [(deck_id, card_id) for card_id in deck.cards]
            print("STR111", card_decks)

            await connection.executemany(
                """
                INSERT INTO card_decks
                (deck_id, card_id)
                VALUES ($1, $2)
                """,
                card_decks,
            )

            await connection.execute(
                """
                INSERT INTO user_decks
                (user_id, deck_id)
                VALUES ($1, $2)
                """,
                user_id,
                deck_id,
            )

            _, _, user_decks = await logic.process_cards(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )
            print("STR121", len(user_decks))

        return ListDecksResponse(
            decks=user_decks,
        )

    async def delete_user_deck(
        self,
        user_id: int,
        deck_id: int,
        base_url: str,
    ) -> ListDecksResponse:
        async with self.db_pool.transaction() as connection:
            await connection.execute(
                """
                DELETE FROM user_decks
                WHERE
                    user_decks.user_id = $1
                    AND user_decks.deck_id = $2
                """,
                user_id,
                deck_id,
            )
            await connection.execute(
                """
                DELETE FROM card_decks
                WHERE
                    card_decks.deck_id = $1
                """,
                deck_id,
            )
            await connection.execute(
                """
                DELETE FROM decks
                WHERE
                    decks.id = $1
                """,
                deck_id,
            )
            _, _, user_decks = await logic.process_cards(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )
            print("STR183", len(user_decks))

        return ListDecksResponse(
            decks=user_decks,
        )

    async def patch_user_deck(
        self,
        user_id: int,
        deck_id: int,
        deck: CreateDeckRequest,
        base_url: str,
    ) -> ListDecksResponse:
        async with self.db_pool.transaction() as connection:
            await connection.fetchrow(
                """
                    UPDATE decks
                    SET
                        name = $2,
                        leader_id = $3
                    WHERE
                        decks.id = $1
                """,
                deck_id,
                deck.deck_name,
                deck.leader_id,
            )

            await connection.execute(
                """
                    DELETE FROM card_decks
                    WHERE card_decks.deck_id = $1
                """,
                deck_id,
            )

            card_decks: list[tuple[deck_id, Card.id]] = [(deck_id, card_id) for card_id in deck.cards]
            print("STR220", card_decks)
            await connection.executemany(
                """
                INSERT INTO card_decks
                (deck_id, card_id)
                VALUES ($1, $2)
                """,
                card_decks,
            )

            _, _, user_decks = await logic.process_cards(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )
            print("STR235", len(user_decks))

        return ListDecksResponse(
            decks=user_decks,
        )

    async def manage_resources(
        self,
        user_id: int,
        resource_request: ResourcesRequest,
    ) -> UserResources:
        logger.info("Got here for user %s, resource request: %s", user_id, resource_request)
        subtype: ResourceActionSubtype = resource_request.subtype

        match subtype:
            case subtype.START_SEASON_LEVEL:
                """ { subtype: start_game, data: {level_id: int}} """
                level_id: int = resource_request.data["level_id"]

                async with self.db_pool.transaction() as connection:
                    difficulty: LevelDifficulty = await connection.fetchval(
                        """
                            SELECT difficulty
                            FROM levels
                            WHERE levels.id = $1
                        """,
                        level_id,
                    )

                    game_constants: dict = await logic.get_game_constants(
                        connection=connection,
                    )

                    if difficulty == LevelDifficulty.EASY:
                        pay_resources = {ResourceType.WOOD: game_constants["play_level_easy"]}
                    elif difficulty == LevelDifficulty.NORMAL:
                        pay_resources = {ResourceType.WOOD: game_constants["play_level_normal"]}
                    elif difficulty == LevelDifficulty.HARD:
                        pay_resources = {ResourceType.WOOD: game_constants["play_level_hard"]}
                    else:
                        raise TypeError(f"Invalid level difficulty {difficulty}")

                    user_resources: UserResources = await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=pay_resources,
                    )

                    if user_resources.wood < 0:
                        msg = "Can not change resources for user %s, seems to be negative value wood"
                        logger.error(msg, user_id)
                        raise ManageResourcesProcessError(msg, user_id)

                    return user_resources

            case subtype.WIN_SEASON_LEVEL:
                """
                data: { wood: 201, scraps: 185, etc }
                Тут придет словарь с ресурсами, которые нужно начислить
                """
                async with self.db_pool.connection() as connection:
                    return await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=resource_request.data,
                    )

            case subtype.BONUS_REWARD:
                """
                data: { wood: +-201, scraps: +-185, etc }
                Тут придет словарь с ресурсами, которые нужно списать или наоборот начислить
                Отличие от бонуса в том, что тут нужно проверять, не стало ли минус, и кинуть ошибку если стало
                """
                async with self.db_pool.transaction() as connection:
                    user_resources: UserResources = await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=resource_request.data,
                    )

                    for resource in resource_request.data:
                        if getattr(user_resources, resource) < 0:
                            msg = "Can not process bonus resources for user %s, seems to be negative value for %s"
                            logger.error(msg, user_id, resource)
                            raise ManageResourcesProcessError(msg, user_id)

                    return user_resources

            case _:
                raise TypeError(f"Invalid subtype {subtype}")

    async def _change_resources(
        self,
        connection: asyncpg.Connection,
        user_id: int,
        resources_to_change: dict[ResourceType:int],
    ) -> UserResources:
        set_parts = []
        query_params = [user_id]

        for i, (resource, delta) in enumerate(resources_to_change.items(), start=2):
            set_parts.append(f"{resource} = {resource} + ${i}")
            query_params.append(delta)

        query = f"""
            UPDATE user_resources
            SET {", ".join(set_parts)}
            WHERE id = $1
            RETURNING *
        """  # noqa: S608

        result = await connection.fetchrow(query, *query_params)
        return UserResources(
            wood=result["wood"],
            scraps=result["scraps"],
            kegs=result["kegs"],
            big_kegs=result["big_kegs"],
            chests=result["chests"],
            keys=result["keys"],
        )

    async def manage_craft_mill_process(
        self,
        user_id: int,
        card_id: int,
        subtype: CardActionSubtype,
        base_url: str,
    ) -> CardCraftMillResponse:
        logger.info("Got here for user %s trying (subtype %s) for card %s", user_id, subtype, card_id)
        match subtype:
            case subtype.CRAFT_CARD:
                async with self.db_pool.transaction() as connection:
                    # 1. Спишем ресурсы за созданную карту
                    # 1.1. Ищем цвет карты, чтобы понять, сколько за нее начислить
                    card_color: CardColorName = await connection.fetchval(
                        """
                            SELECT colors.name
                            FROM cards
                            JOIN colors ON cards.color_id = colors.id
                            WHERE cards.id = $1
                        """,
                        card_id,
                    )

                    # 1.2. В константах лежат параметры, сколько списать за крафт той или иной карты
                    game_constants: dict = await logic.get_game_constants(
                        connection=connection,
                    )

                    if card_color == CardColorName.BRONZE:
                        pay_resources = {ResourceType.SCRAPS: game_constants["craft_bronze"]}
                    elif card_color == CardColorName.SILVER:
                        pay_resources = {ResourceType.SCRAPS: game_constants["craft_silver"]}
                    elif card_color == CardColorName.GOLD:
                        pay_resources = {ResourceType.SCRAPS: game_constants["craft_gold"]}
                    else:
                        logger.error("Unknown color %s", card_color)
                        raise TypeError(f"Invalid card color {card_color}")

                    # 1.3. Попытались списать ресурсы
                    user_resources: UserResources = await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=pay_resources,
                    )

                    # 1.4. Если получилось, что ресурсов на списание не хватило, отменяем транзакцию!
                    if user_resources.scraps < 0:
                        msg = "Can not craft card %s for user %s, not enough scraps"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg, card_id, user_id)

                    # 2. Создаем юзеру карту
                    # 2.1. Крафтим карту - пытаемся сделать инзерт, а если такая уже есть, делаем count += 1
                    await connection.fetchrow(
                        """
                            INSERT INTO user_cards
                            (user_id, card_id, count)
                            VALUES ($1, $2, 1)
                            ON CONFLICT (user_id, card_id)
                            DO UPDATE
                            SET
                                count = user_cards.count + 1,
                                updated_at = NOW()
                        """,
                        user_id,
                        card_id,
                    )

                    # 2.2. После создания возвращаем на фронт весь список UserCard, чтобы обновить там карты
                    user_cards: list[UserCard] = await logic.get_user_cards(
                        connection=connection,
                        user_id=user_id,
                        base_url=base_url,
                    )

                    logger.info("Successfully crafted card %s for user %s", card_id, user_id)
                    return CardCraftMillResponse(
                        cards=user_cards,
                        resources=user_resources,
                    )

            case subtype.CRAFT_LEADER:
                async with self.db_pool.transaction() as connection:
                    # 1. Спишем ресурсы за карту лидера
                    # 1.1. Берем опять же игровые константы
                    game_constants: dict = await logic.get_game_constants(
                        connection=connection,
                    )
                    # 1.2. А тут проще - не нужно делать запрос, мы всегда знаем стоимость за крафт лидера
                    pay_resources = {ResourceType.SCRAPS: game_constants["craft_leader"]}

                    # 1.3. Попытались списать ресурсы
                    user_resources: UserResources = await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=pay_resources,
                    )

                    # 1.4. Если получилось, что ресурсов на списание не хватило, отменяем транзакцию!
                    if user_resources.scraps < 0:
                        msg = "Can not craft leader card %s for user %s, not enough scraps"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg, card_id, user_id)

                    # 2. Создаем юзеру карту лидера
                    # 2.1. Крафтим карту лидера - пытаемся сделать инзерт, а если такая уже есть, делаем count += 1
                    await connection.fetchrow(
                        """
                            INSERT INTO user_leaders
                            (user_id, leader_id, count)
                            VALUES ($1, $2, 1)
                            ON CONFLICT (user_id, leader_id)
                            DO UPDATE
                            SET
                                count = user_leaders.count + 1,
                                updated_at = NOW()
                        """,
                        user_id,
                        card_id,
                    )

                    # 2.2. После создания возвращаем на фронт весь список UserLeader, чтобы обновить там лидеров
                    user_leaders: list[UserLeader] = await logic.get_user_leaders(
                        connection=connection,
                        user_id=user_id,
                        base_url=base_url,
                    )

                    logger.info("Successfully crafted leader card %s for user %s", card_id, user_id)
                    return CardCraftMillResponse(
                        cards=user_leaders,
                        resources=user_resources,
                    )

            case subtype.MILL_CARD:
                async with self.db_pool.transaction() as connection:
                    # 1. А здесь делаем наоборот - вначале уничтожаем карту, потом начисляем ресурсы
                    # 1.1. Ищем, карта из дефолтного набора (unlocked) или нет + смотрим ее user_cards.count
                    user_card: dict = await connection.fetchrow(
                        """
                            SELECT
                                cards.unlocked,
                                user_cards.id,
                                user_cards.count
                            FROM user_cards
                            JOIN cards ON cards.id = user_cards.card_id
                            AND user_cards.user_id = $1
                            AND user_cards.card_id = $2
                        """,
                        user_id,
                        card_id,
                    )

                    if not user_card:
                        msg = "Cannot find such card %s for user %s"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg, card_id, user_id)

                    # 1.2. Если карта из дефолтного набора и ее у юзера 1, то ее нельзя миллить!
                    if user_card["unlocked"] and user_card["count"] <= 1:
                        msg = "Cannot mill default unlocked card %s for user %s"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg, card_id, user_id)

                    # 1.3. Если карта НЕ из дефолтного набора, то ее нельзя миллить если ее и так нету
                    if not user_card["unlocked"] and user_card["count"] <= 0:
                        msg = "Cannot mill card %s for user %s, seems user doesn't have it"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg, card_id, user_id)

                    # 1.4. Пытаемся уничтожить эту карту, поставив ей user_cards.count -= 1
                    card_count: int = await connection.fetchval(
                        """
                            UPDATE user_cards
                            SET
                                count = user_cards.count - 1,
                                updated_at = NOW()
                            WHERE user_cards.id = $1
                            RETURNING user_cards.count
                        """,
                        user_card["id"],
                    )

                    # 1.5. Если вдруг как-то карты стало отрицательное значение, отменяем транзакцию
                    if card_count < 0:
                        msg = "Cannot mill card %s for user %s, count seems to be negative value"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg, card_id, user_id)

                    # 2. А теперь начисляем ресурсы за униточженную карту
                    # 2.1. Ищем цвет карты, чтобы понять какие ресурсы за нее
                    card_color: CardColorName = await connection.fetchval(
                        """
                            SELECT
                                colors.name
                            FROM cards
                            JOIN colors ON cards.color_id = colors.id
                            WHERE cards.id = $1
                        """,
                        card_id,
                    )

                    # 2.2. Достаем игровые константы
                    game_constants: dict = await logic.get_game_constants(
                        connection=connection,
                    )

                    if card_color == CardColorName.BRONZE:
                        pay_resources = {ResourceType.SCRAPS: game_constants["mill_bronze"]}
                    elif card_color == CardColorName.SILVER:
                        pay_resources = {ResourceType.SCRAPS: game_constants["mill_silver"]}
                    elif card_color == CardColorName.GOLD:
                        pay_resources = {ResourceType.SCRAPS: game_constants["mill_gold"]}
                    else:
                        raise TypeError(f"Invalid card color {card_color}")

                    # 2.3. Добавляем тут юзеру ресурсы
                    user_resources: UserResources = await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=pay_resources,
                    )

                    # 3. Карту уничтожили, ресурсы добавили, можем собирать все карты юзера для ответа
                    user_cards: list[UserCard] = await logic.get_user_cards(
                        connection=connection,
                        user_id=user_id,
                        base_url=base_url,
                    )

                    logger.info("Successfully milled card %s for user %s", card_id, user_id)
                    return CardCraftMillResponse(
                        cards=user_cards,
                        resources=user_resources,
                    )

            case subtype.MILL_LEADER:
                async with self.db_pool.transaction() as connection:
                    # 1. А здесь делаем наоборот - вначале уничтожаем карту лидера, потом начисляем ресурсы
                    # 1.1. Ищем, карта лидера из дефолтного набора (unlocked) или нет + смотрим ее user_leaders.count
                    user_leader: dict = await connection.fetchrow(
                        """
                            SELECT
                                leaders.unlocked,
                                user_leaders.id,
                                user_leaders.count
                            FROM user_leaders
                            JOIN leaders ON leaders.id = user_leaders.leader_id
                            AND user_leaders.user_id = $1
                            AND user_leaders.leader_id = $2
                        """,
                        user_id,
                        card_id,
                    )

                    if not user_leader:
                        msg = "Cannot find such leader card %s for user %s"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg, card_id, user_id)

                    # 1.2. Если карта лидера из дефолтного набора и ее у юзера 1, то ее нельзя миллить!
                    if user_leader["unlocked"] and user_leader["count"] <= 1:
                        msg = "Cannot mill default unlocked leader card %s for user %s"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg, card_id, user_id)

                    # 1.3. Если карта лидера НЕ из дефолтного набора, то ее нельзя миллить если ее и так нету
                    if not user_leader["unlocked"] and user_leader["count"] <= 0:
                        msg = "Cannot mill leader card %s for user %s, seems user doesn't have it"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg, card_id, user_id)

                    # 1.4. Пытаемся уничтожить эту карту лидера, поставив ей user_leaders.count -= 1
                    await connection.fetchrow(
                        """
                            UPDATE user_leaders
                            SET
                                count = user_leaders.count - 1,
                                updated_at = NOW()
                            WHERE user_leaders.id = $1
                        """,
                        user_leader["id"],
                    )

                    # 2. А теперь начисляем ресурсы за униточженную карту лидера
                    # 2.1. С лидером проще - за него всегда одна и та же сумма
                    game_constants: dict = await logic.get_game_constants(
                        connection=connection,
                    )
                    pay_resources = {ResourceType.SCRAPS: game_constants["mill_leader"]}

                    # 2.2. Добавляем тут юзеру ресурсы
                    user_resources: UserResources = await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=pay_resources,
                    )

                    # 3. Карту лидера уничтожили, ресурсы добавили, можем собирать все карты лидера юзера для ответа

                    user_leaders: list[UserLeader] = await logic.get_user_leaders(
                        connection=connection,
                        user_id=user_id,
                        base_url=base_url,
                    )

                    logger.info("Successfully milled leader card %s for user %s", card_id, user_id)
                    return CardCraftMillResponse(
                        cards=user_leaders,
                        resources=user_resources,
                    )

            case _:
                msg = "Unknown subtype %s for craft/mill card process"
                logger.error(msg, subtype)
                raise CraftMillCardProcessError(msg, subtype)

    async def open_level_related_levels(
        self,
        user_id: int,
        user_level_id: int,
        base_url: str,
    ) -> OpenRelatedLevelsResponse:
        logger.info("Opening related_levels for user_level %s and user %s", user_level_id, user_id)

        # Ставим текущему user_levels.finished = true, уровень пройден
        async with self.db_pool.transaction() as connection:
            await connection.execute(
                """
                    UPDATE user_levels
                    SET
                        finished = TRUE,
                        updated_at = NOW()
                    FROM levels, level_related_levels
                    WHERE user_levels.level_id = levels.id
                      AND levels.id = level_related_levels.level_id
                      AND user_levels.id = $2
                      AND user_levels.user_id = $1;
                """,
                user_id,
                user_level_id,
            )

            # находим для этого уровня все его связанные related_level_id и инзертим их как user_levels
            level_related_levels = await connection.fetch(
                """
                    INSERT INTO user_levels (user_id, level_id)
                    SELECT $1, level_related_levels.related_level_id
                    FROM level_related_levels
                    JOIN user_levels ON level_related_levels.level_id = user_levels.level_id
                    WHERE user_levels.user_id = $1
                      AND user_levels.id = $2
                    ON CONFLICT (user_id, level_id) DO NOTHING
                    RETURNING user_levels.id, user_levels.level_id;
                """,
                user_id,
                user_level_id,
            )
            logger.info(
                "Successfully opened related levels: %s for user %s",
                [row["level_id"] for row in level_related_levels],
                user_id,
            )

            _, _, seasons = await logic.process_enemies(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )

        return OpenRelatedLevelsResponse(
            seasons=seasons,
        )

    async def craft_bonus_cards(
        self,
        user_id: int,
        cards_ids: list[int],
        base_url: str,
    ) -> CardCraftBonusResponse:
        logger.info("Crafting bonus cards %s for user %s", cards_ids, user_id)
        async with self.db_pool.transaction() as connection:
            r = await connection.fetch(
                """
                    WITH card_counts AS (
                        SELECT card_id, COUNT(*) as occurrence_count
                        FROM unnest($2::int[]) as card_id
                        GROUP BY card_id
                    )
                    INSERT INTO user_cards
                    (user_id, card_id, count)
                    SELECT $1, card_counts.card_id, card_counts.occurrence_count
                    FROM card_counts
                    ON CONFLICT (user_id, card_id)
                    DO UPDATE
                        SET
                            count = user_cards.count + EXCLUDED.count,
                            updated_at = NOW()
                    RETURNING user_cards.id;
                """,
                user_id,
                cards_ids,
            )
            print("STR720", r)

            user_cards = await logic.get_user_cards(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )

        return CardCraftBonusResponse(
            cards=user_cards,
        )
