import logging
from typing import TYPE_CHECKING

from lib.utils.db.pool import Database
from lib.utils.schemas.game import DEFAULT_USER_UPGRADES, UpgradeSubtype, UpgradeType
from services.api.app.apps.game_const import logic as game_const_logic
from services.api.app.apps.progress import logic as progress_logic
from services.api.app.apps.upgrades.schemas import PostUpgradeResponse
from services.api.app.config import Config
from services.api.app.exceptions.exceptions import UpgradeMaxLevelReachedError


if TYPE_CHECKING:
    from services.api.app.apps.progress.schemas import UserResources


logger = logging.getLogger(__name__)


class UpgradesService:
    def __init__(
        self,
        db_pool: Database,
        config: Config,
    ):
        self.db_pool = db_pool
        self.config = config

    async def get_user_upgrades(
        self,
        user_id: int,
    ) -> dict:
        async with self.db_pool.connection() as connection:
            upgrades: dict | None = await connection.fetchval(
                """
                    SELECT
                        user_upgrades.data::jsonb
                    FROM
                        user_upgrades
                    WHERE user_upgrades.id = $1
                """,
                user_id,
            )

            if not upgrades:
                logger.info("User %s upgrades not found, gotta insert new", user_id)
                upgrades = await connection.fetchval(
                    """
                        INSERT INTO user_upgrades
                        (
                            id,
                            data
                        )
                        VALUES ($1, $2)
                        RETURNING data::jsonb
                    """,
                    user_id,
                    DEFAULT_USER_UPGRADES,
                )

        return upgrades

    async def post_user_upgrade(
        self,
        user_id: int,
        upgrade_type: UpgradeType,
        upgrade_subtype: UpgradeSubtype,
    ) -> PostUpgradeResponse:
        logger.info(
            "Upgrading for user %s: type %s, subtype %s",
            user_id,
            upgrade_type,
            upgrade_subtype,
        )

        async with self.db_pool.transaction() as connection:
            # 1. Берем игровые константы, где записан весь конфиг переходов
            game_const: dict = await game_const_logic.get_game_constants(connection=connection)
            upgrades: dict = game_const["upgrades"]

            # 2. Смотрим апгрейды юзера - они записаны в виде значения уровня апгрейда (числа)
            user_upgrades = await connection.fetchval(
                "SELECT data::jsonb FROM user_upgrades WHERE id = $1 FOR UPDATE",
                user_id,
            )

            # 3. Но что если в словари добавились новые ключи, позже чем юзеру создались апгрейды
            # тогда надо пройти по всем ключам словаря и добавить недостающие юзеру
            merged = dict(user_upgrades)
            changed = False
            for u_type, subtypes in DEFAULT_USER_UPGRADES.items():
                if u_type not in merged:
                    merged[u_type] = {}
                    changed = True
                for u_subtype, default_val in subtypes.items():
                    if u_subtype not in merged[u_type]:
                        merged[u_type][u_subtype] = default_val
                        changed = True
            if changed:
                logger.info("Migrating user_upgrades for user %s: adding missing keys", user_id)
                await connection.execute(
                    "UPDATE user_upgrades SET data = $2::jsonb WHERE id = $1",
                    user_id,
                    merged,
                )
            user_upgrades = merged

            # 4. Достаем текущий уровень апгрейда юзера по нужному типу
            current_level: int = user_upgrades[upgrade_type][upgrade_subtype]

            # 5. Смотрим, а какие ресурсы нужны для следующего уровня апгрейда
            level_data: dict = upgrades[upgrade_type]["upgrades"][upgrade_subtype]["upgrades"][str(current_level)]

            # 6. Если достигнут последний уровень, то мы не должны ничего апгрейдить
            # такая проверка есть на фронте, так что это скорее запрос из постмана
            if level_data["next"] is None:
                msg = "User %s already at max level for %s/%s"
                logger.error(msg, user_id, upgrade_type, upgrade_subtype)
                raise UpgradeMaxLevelReachedError(msg % (user_id, upgrade_type, upgrade_subtype))

            # 7. Смотрим, какие ресурсы надо списать для апгрейда и списываем их
            resources_to_change: dict = level_data["next"]
            user_resources: UserResources = await progress_logic.change_resources(
                connection=connection,
                user_id=user_id,
                resources_to_change=resources_to_change,
                scenario=f"Post upgrade: type {upgrade_type}, subtype {upgrade_subtype}",
            )

            # 8. Проставляем юзеру в его апгрейды следующий уровень апгрейда
            new_level = current_level + 1
            updated_upgrades: dict = await connection.fetchval(
                """
                UPDATE user_upgrades
                SET data = jsonb_set(data, $2::text[], to_jsonb($3::int))
                WHERE id = $1
                RETURNING data::jsonb
                """,
                user_id,
                [upgrade_type, upgrade_subtype],
                new_level,
            )

        return PostUpgradeResponse(
            resources=user_resources,
            upgrades=updated_upgrades,
        )
