import logging

from lib.utils.db.pool import Database
from services.api.app.apps.cards import logic
from services.api.app.apps.cards.schemas import CardsResponse
from services.api.app.config import Config

logger = logging.getLogger(__name__)


class CardsService:
    def __init__(
        self,
        db_pool: Database,
        config: Config,
    ):
        self.db_pool = db_pool
        self.config = config

    async def get_cards(
        self,
        base_url: str,
    ) -> CardsResponse:
        async with self.db_pool.connection() as connection:
            return CardsResponse(
                cards=await logic.get_cards(connection, base_url),
                leaders=await logic.get_leaders(connection, base_url),
                enemies=await logic.get_enemies(connection, base_url),
                enemy_leaders=await logic.get_enemy_leaders(connection, base_url),
            )
