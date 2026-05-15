import logging

from lib.utils.db.pool import Database
from lib.utils.schemas.game import DEFAULT_USER_UPGRADES
from services.api.app.config import Config

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
    ):
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
                logger.info("User %s preferences not found, gotta insert new", user_id)
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
