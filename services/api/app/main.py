from contextlib import asynccontextmanager
import logging.config

from fastapi import APIRouter, FastAPI
from lib.utils.db.pool import Database
from lib.utils.elk.elastic_logger import ElasticLoggerManager
from lib.utils.elk.elastic_tracer import ElasticTracerManager
from services.api.app.apps.api_docs.routes import router as swagger_router
from services.api.app.apps.auth.routes import router as users_router
from services.api.app.apps.news.routes import router as news_router
from services.api.app.apps.progress.routes import router as progress_router
from services.api.app.config import get_config as get_app_settings
from services.api.app.dependencies import set_global_app
from services.api.app.exceptions.handlers import add_exceptions
from services.api.app.middlewares import set_middlewares
from services.api.app.staticfiles import mount_static


apm_manager = ElasticTracerManager()
config = get_app_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.config = config

    logging.config.dictConfig(config.LOGGING)

    elastic_logger_manager = ElasticLoggerManager()
    elastic_logger_manager.initialize(
        config=config,
        service_name="fast-api",
        delay_seconds=5,
    )
    apm_manager.initialize(
        config=config,
        service_name="fast-api",
    )

    logger = logging.getLogger(__name__)

    logger.info("Starting API")

    db = Database(config)
    await db.connect()
    app.state.db = db

    set_global_app(app)

    yield
    await db.disconnect()


app = FastAPI(
    title="Gridways backend",
    lifespan=lifespan,
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

add_exceptions(app)
set_middlewares(app, config, apm_manager)
mount_static(app, config)


api_v1_router = APIRouter(prefix="/api/v1")

api_v1_router.include_router(swagger_router, prefix="", tags=["swagger"])
api_v1_router.include_router(users_router, prefix="/users", tags=["accounts"])
api_v1_router.include_router(news_router, prefix="/news", tags=["news"])
api_v1_router.include_router(progress_router, prefix="/user-progress", tags=["progress"])

app.include_router(api_v1_router)
