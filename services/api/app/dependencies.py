from fastapi import Depends, FastAPI
from lib.utils.db.pool import Database
from services.api.app.apps.auth.service import AuthService
from services.api.app.apps.cards.service import CardsService
from services.api.app.apps.game_const.service import GameConstService
from services.api.app.apps.news.service import NewsService
from services.api.app.apps.preferences.service import PreferencesService
from services.api.app.apps.progress.service import UserProgressService
from services.api.app.apps.purchases.service import PurchasesService
from services.api.app.apps.stats.service import StatsService
from services.api.app.apps.upgrades.service import UpgradesService
from services.api.app.config import Config


# Глобальная переменная для доступа к app
_app: FastAPI = None


def set_global_app(
    app: FastAPI,
) -> None:
    global _app
    _app = app


async def get_config() -> Config:
    return _app.state.config


async def get_db() -> Database:
    return _app.state.db


async def get_auth_service(
    db_pool: Database = Depends(get_db),
    config: Config = Depends(get_config),
) -> AuthService:
    return AuthService(
        db_pool=db_pool,
        config=config,
    )


async def get_cards_service(
    db_pool: Database = Depends(get_db),
    config: Config = Depends(get_config),
) -> CardsService:
    return CardsService(
        db_pool=db_pool,
        config=config,
    )


async def get_news_service(
    db_pool: Database = Depends(get_db),
    config: Config = Depends(get_config),
) -> NewsService:
    return NewsService(
        db_pool=db_pool,
        config=config,
    )


async def get_game_const_service(
    db_pool: Database = Depends(get_db),
    config: Config = Depends(get_config),
) -> GameConstService:
    return GameConstService(
        db_pool=db_pool,
        config=config,
    )


async def get_preferences_service(
    db_pool: Database = Depends(get_db),
    config: Config = Depends(get_config),
) -> PreferencesService:
    return PreferencesService(
        db_pool=db_pool,
        config=config,
    )


async def get_user_progress_service(
    db_pool: Database = Depends(get_db),
    config: Config = Depends(get_config),
) -> UserProgressService:
    return UserProgressService(
        db_pool=db_pool,
        config=config,
    )


async def get_stats_service(
    db_pool: Database = Depends(get_db),
    config: Config = Depends(get_config),
) -> StatsService:
    return StatsService(
        db_pool=db_pool,
        config=config,
    )


async def get_purchase_service(
    db_pool: Database = Depends(get_db),
    config: Config = Depends(get_config),
) -> PurchasesService:
    return PurchasesService(
        db_pool=db_pool,
        config=config,
    )


async def get_upgrades_service(
    db_pool: Database = Depends(get_db),
    config: Config = Depends(get_config),
) -> UpgradesService:
    return UpgradesService(
        db_pool=db_pool,
        config=config,
    )
