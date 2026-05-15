from lib.utils.db.pool import Database
from services.api.app.apps.game_const import logic
from services.api.app.config import Config


class GameConstService:
    def __init__(
        self,
        db_pool: Database,
        config: Config,
    ):
        self.db_pool = db_pool
        self.config = config

    async def get_game_const(self) -> dict:
        async with self.db_pool.connection() as connection:
            game_const: dict | None = await logic.get_game_constants(connection=connection)

        if not game_const:
            return {}
        return game_const
