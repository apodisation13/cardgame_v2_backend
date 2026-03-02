import logging
from typing import TYPE_CHECKING

import asyncpg

from lib.utils.db.pool import Database
from lib.utils.schemas.game import (
    CardActionSubtype,
    CardColorName,
    ResourceActionSubtype,
    ResourceTransitionActionType,
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
        logger.info("Getting database for user %s", user_id)
        async with self.db_pool.connection() as connection:
            user_resources: UserResources = await logic.get_user_resources(
                connection=connection,
                user_id=user_id,
            )

            game_constants: dict = await logic.get_game_constants(
                connection=connection,
            )

            enemies, enemy_leaders, user_seasons = await logic.process_enemies(
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
            seasons=user_seasons,
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

            card_decks: list[tuple[deck_id, Card.id]] = [(deck_id, card_id) for card_id in deck.cards]

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
                        leader_id = $3,
                        updated_at = NOW()
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
            case subtype.WIN_SEASON_LEVEL | subtype.ACCEPT_KEY_REWARD:
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

            case subtype.RESOURCE_TRANSITION:
                """
                data: { action: craft, resource: wood, quantity: 3, recipe (за один): { wood: 100, scraps: 100} }
                Тут придет словарь с ресурсами, которые нужно списать или наоборот начислить
                """
                async with self.db_pool.transaction() as connection:
                    game_constants: dict = await logic.get_game_constants(
                        connection=connection,
                    )
                    resources_transitions: dict = game_constants["resources_transitions"]

                    action: ResourceTransitionActionType = resource_request.data["action"]

                    resource: ResourceType = resource_request.data["resource"]
                    quantity: int = resource_request.data["quantity"]
                    recipe = resource_request.data["recipe"]

                    # вот тут упадет для тех ресурсов, у кого нет переходов (keys, rare_gem, money)
                    step: int | None = resources_transitions.get(resource, {}).get("step")
                    if not step:
                        msg = "Can not process bonus resource %s (%s), action %s, recipe %s for user %s: no resource"
                        logger.error(msg, resource, quantity, action, recipe, user_id)
                        raise ManageResourcesProcessError(msg % (resource, quantity, action, recipe, user_id))

                    # это те ресурсы, которые из констант - цена милла/крафта итп
                    # они там с правильным знаком, плюс или минус, списать или начислить
                    resources_to_change = {}
                    all_recipes: list = resources_transitions[resource][action]
                    for r_ in all_recipes:
                        if r_ == recipe:
                            resources_to_change = r_

                    if not resources_to_change:
                        msg = "Can not process bonus resource %s (%s), action %s, recipe %s for user %s: no config"
                        logger.error(msg, resource, quantity, action, recipe, user_id)
                        raise ManageResourcesProcessError(msg % (resource, quantity, action, recipe, user_id))

                    # а это собственно сам тот ресурс, который надо крафтить/миллить
                    # но тут нужно понять, начислять и наоборот отнимать исходный ресурс
                    if action in ResourceTransitionActionType.to_decrease_resources():
                        resources_to_change[resource] = -step
                    elif action in ResourceTransitionActionType.to_increase_resources():
                        resources_to_change[resource] = step
                    else:
                        msg = "Unknown action %s for resource %s for user %s"
                        logger.error(msg, resource, action, user_id)
                        raise ManageResourcesProcessError(msg % (resource, action, user_id))

                    # а тут мы все ресурсы умножаем на количество, как в плюс, так и в минус
                    for key, value in resources_to_change.items():
                        resources_to_change[key] = value * quantity

                    logger.info("Resources to change: %s for user %s", resources_to_change, user_id)

                    user_resources: UserResources = await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=resources_to_change,
                    )

                    for r in resources_to_change:
                        actual_resource: int = getattr(user_resources, r)
                        if actual_resource < 0:
                            msg = "User %s, resource: %s (quantity: %s), action: %s (recipe %s), ACTUAL: %s %s"
                            logger.error(msg, user_id, resource, quantity, action, recipe, actual_resource, r)
                            raise ManageResourcesProcessError(
                                msg % (user_id, resource, quantity, action, recipe, actual_resource, r),
                            )

                return user_resources

            case subtype.START_SEASON_LEVEL | subtype.OPEN_BONUS_RESOURCE:
                """
                data: { kegs: -1 }, { wood: -40, crops: -200, etc }
                Тут придет словарь с ресурсами, которые нужно отнять
                """

                # на случай запросов из постмана с положительными ресурсами вместо отрицательных :)
                for resource, value in resource_request.data.items():
                    if value >= 0:
                        msg = "Can not process subtype %s for user %s, wrong value: %s %s"
                        logger.error(msg, subtype, user_id, value, resource)
                        raise ManageResourcesProcessError(msg % (subtype, user_id, value, resource))

                async with self.db_pool.transaction() as connection:
                    user_resources: UserResources = await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=resource_request.data,
                    )

                for resource in resource_request.data:
                    actual_resource: int = getattr(user_resources, resource)
                    if actual_resource < 0:
                        msg = "Can not process subtype %s for user %s, negative value: %s %s"
                        logger.error(msg, subtype, user_id, actual_resource, resource)
                        raise ManageResourcesProcessError(msg % (subtype, user_id, actual_resource, resource))

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

        set_parts.append("updated_at = NOW()")

        query = f"""
            UPDATE user_resources
            SET {", ".join(set_parts)}
            WHERE id = $1
            RETURNING *
        """  # noqa: S608

        result = await connection.fetchrow(query, *query_params)
        return UserResources.get_one(result)

    async def manage_craft_mill_process(
        self,
        user_id: int,
        card_id: int,
        subtype: CardActionSubtype,
        base_url: str,
        recipe: dict | None = None,
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

                    card_resources: dict = game_constants["cards_resources_prices"][card_color]
                    craft_card_recipes: list[dict] = card_resources[CardActionSubtype.CRAFT_CARD]

                    # 1.3. Тут ищем, какую конкретно формулу крафта выбрал юзер (пришла с фронта)
                    pay_resources = {}
                    for r in craft_card_recipes:
                        if r == recipe:
                            pay_resources = recipe

                    # 1.4. Если не нашлось, рейзим ошибку!
                    if not pay_resources:
                        msg = "Craft card error: no config for recipe %s for user %s"
                        logger.error(msg, recipe, user_id)
                        raise ManageResourcesProcessError(msg % (recipe, user_id))

                    # 1.5. Попытались списать ресурсы
                    user_resources: UserResources = await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=pay_resources,
                    )

                    # 1.6. Проверяем, если какого-то ресурса стало 0, рейзим ошибку!
                    for r in pay_resources:
                        actual_resource: int = getattr(user_resources, r)
                        if actual_resource < 0:
                            msg = "Craft card error: user %s, ACTUAL: %s %s"
                            logger.error(msg, user_id, actual_resource, r)
                            raise ManageResourcesProcessError(msg % (user_id, actual_resource, r))

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

                    # 1.2. Ищем цену на крафт лидера
                    leader_resources: dict = game_constants["cards_resources_prices"]["leader"]
                    craft_leader_recipes: list[dict] = leader_resources[CardActionSubtype.CRAFT_LEADER]

                    # 1.3. Тут ищем, какую конкретно формулу крафта выбрал юзер (пришла с фронта)
                    pay_resources = {}
                    for r in craft_leader_recipes:
                        if r == recipe:
                            pay_resources = recipe

                    # 1.4. Если не нашлось, рейзим ошибку!
                    if not pay_resources:
                        msg = "Craft leader error: no config for recipe %s for user %s"
                        logger.error(msg, recipe, user_id)
                        raise ManageResourcesProcessError(msg % (recipe, user_id))

                    # 1.5. Попытались списать ресурсы
                    user_resources: UserResources = await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=pay_resources,
                    )

                    # 1.6. Проверяем, если какого-то ресурса стало 0, рейзим ошибку!
                    for r in pay_resources:
                        actual_resource: int = getattr(user_resources, r)
                        if actual_resource < 0:
                            msg = "Craft leader error: user %s, ACTUAL: %s %s"
                            logger.error(msg, user_id, actual_resource, r)
                            raise ManageResourcesProcessError(msg % (user_id, actual_resource, r))

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
                        raise CraftMillCardProcessError(msg % (card_id, user_id))

                    # 1.2. Если карта из дефолтного набора и ее у юзера 1, то ее нельзя миллить!
                    if user_card["unlocked"] and user_card["count"] <= 1:
                        msg = "Cannot mill default unlocked card %s for user %s"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg % (card_id, user_id))

                    # 1.3. Если карта НЕ из дефолтного набора, то ее нельзя миллить если ее и так нету
                    if not user_card["unlocked"] and user_card["count"] <= 0:
                        msg = "Cannot mill card %s for user %s, seems user doesn't have it"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg % (card_id, user_id))

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
                        raise CraftMillCardProcessError(msg % (card_id, user_id))

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

                    # здесь для порядка список из 1 элемента, мы возьмем первый (единственный)
                    pay_resources = game_constants["cards_resources_prices"][card_color][CardActionSubtype.MILL_CARD]

                    # 2.3. Добавляем тут юзеру ресурсы
                    user_resources: UserResources = await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=pay_resources[0],
                    )

                    # 2.4. Проверяем, что ресурса не стало меньше 0
                    for r in pay_resources[0]:
                        actual_resource: int = getattr(user_resources, r)
                        if actual_resource < 0:
                            msg = "Mill card error: user %s, ACTUAL: %s %s"
                            logger.error(msg, user_id, actual_resource, r)
                            raise ManageResourcesProcessError(
                                msg % (user_id, actual_resource, r),
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
                        msg = "Cannot find such leader %s for user %s"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg % (card_id, user_id))

                    # 1.2. Если карта лидера из дефолтного набора и ее у юзера 1, то ее нельзя миллить!
                    if user_leader["unlocked"] and user_leader["count"] <= 1:
                        msg = "Cannot mill default unlocked leader %s for user %s"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg % (card_id, user_id))

                    # 1.3. Если карта лидера НЕ из дефолтного набора, то ее нельзя миллить если ее и так нету
                    if not user_leader["unlocked"] and user_leader["count"] <= 0:
                        msg = "Cannot mill leader %s for user %s, seems user doesn't have it"
                        logger.error(msg, card_id, user_id)
                        raise CraftMillCardProcessError(msg % (card_id, user_id))

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

                    # вот тут для порядка - список, но там только 1 элемент, его мы и возьмем
                    pay_resources = game_constants["cards_resources_prices"]["leader"][CardActionSubtype.MILL_LEADER]

                    # 2.2. Добавляем тут юзеру ресурсы
                    user_resources: UserResources = await self._change_resources(
                        connection=connection,
                        user_id=user_id,
                        resources_to_change=pay_resources[0],
                    )

                    # 2.3. Проверяем, что не стало меньше 0 каких-то ресурсов
                    for r in pay_resources[0]:
                        actual_resource: int = getattr(user_resources, r)
                        if actual_resource < 0:
                            msg = "Mill leader error: user %s, ACTUAL: %s %s"
                            logger.error(msg, user_id, actual_resource, r)
                            raise ManageResourcesProcessError(
                                msg % (user_id, actual_resource, r),
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
                raise CraftMillCardProcessError(msg % (subtype,))

    async def open_level_related_levels(
        self,
        user_id: int,
        user_level_id: int,
        base_url: str,
    ) -> OpenRelatedLevelsResponse:
        logger.info("Opening related_levels for user_level %s and user %s", user_level_id, user_id)

        # Ставим текущему user_levels.finished = true, уровень пройден
        async with self.db_pool.transaction() as connection:
            season_id: int = await connection.fetchval(
                """
                    UPDATE user_levels
                    SET
                        finished = TRUE,
                        updated_at = NOW()
                    FROM levels
                    WHERE user_levels.level_id = levels.id
                        AND user_levels.user_id = $1
                        AND user_levels.id = $2
                    RETURNING levels.season_id;
                """,
                user_id,
                user_level_id,
            )

            # TODO: если тут что-то хотя бы открылось, значит сезон еще точно НЕ пройден
            # если не открылось - ничего не значит, надо проверять тогда все остальные уровни сезона
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

            _, _, user_seasons = await logic.process_enemies(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )

        return OpenRelatedLevelsResponse(
            seasons=user_seasons,
        )

    async def craft_bonus_cards(
        self,
        user_id: int,
        cards_ids: list[int],
        base_url: str,
    ) -> CardCraftBonusResponse:
        logger.info("Crafting bonus cards %s for user %s", cards_ids, user_id)
        async with self.db_pool.transaction() as connection:
            await connection.fetch(
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

            user_cards = await logic.get_user_cards(
                connection=connection,
                user_id=user_id,
                base_url=base_url,
            )

        return CardCraftBonusResponse(
            cards=user_cards,
        )
