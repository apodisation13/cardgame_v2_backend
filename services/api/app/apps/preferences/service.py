import logging

from lib.utils.db.pool import Database
from services.api.app.apps.preferences.schemas import UserPreferencesResponse, DEFAULT_PREFERENCES, \
    UpdateUserPreferencesRequest

from services.api.app.config import Config


logger = logging.getLogger(__name__)


class PreferencesService:
    def __init__(
        self,
        db_pool: Database,
        config: Config,
    ):
        self.db_pool = db_pool
        self.config = config

    async def get_user_preference(
        self,
        user_id: int,
    ) -> UserPreferencesResponse:
        async with self.db_pool.connection() as connection:
            preferences: dict = await connection.fetchval(
                """
                    SELECT
                        data::jsonb
                    FROM
                        user_preferences
                    WHERE id = $1
                """,
                user_id,
            )

            if not preferences:
                logger.info("User %s preferences not found, gotta insert new", user_id)
                preferences = await connection.fetchval(
                    """
                        INSERT INTO user_preferences 
                        (
                            id, 
                            data
                        )
                        VALUES ($1, $2)
                        RETURNING data::jsonb
                    """,
                    user_id,
                    DEFAULT_PREFERENCES,
                )

        return UserPreferencesResponse(data=preferences)

    async def update_user_preferences(
        self,
        user_id: int,
        preferences: UpdateUserPreferencesRequest,
    ) -> UserPreferencesResponse:
        print("STR61", preferences.data)
        async with self.db_pool.connection() as connection:
            preferences: dict = await connection.fetchval(
                """
                    UPDATE user_preferences 
                    SET
                        data = $2,
                        updated_at = NOW()
                    WHERE id = $1
                    RETURNING data::jsonb
                """,
                user_id,
                preferences.data,
            )

        return UserPreferencesResponse(data=preferences)
