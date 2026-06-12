from contextlib import asynccontextmanager
import logging.config

from fastapi import FastAPI
from lib.utils.db.pool import Database
from lib.utils.elk.elastic_logger import ElasticLoggerManager
from services.ws.app.apps.matchmaking.routes import router as matchmaking_router
from services.ws.app.config import get_config


config = get_config()


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

    logger = logging.getLogger(__name__)

    logger.info("Starting WS")

    db = Database(config)
    await db.connect()
    app.state.db = db

    yield

    await db.disconnect()


app = FastAPI(
    title="Gridways WS",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
)

app.include_router(matchmaking_router)
