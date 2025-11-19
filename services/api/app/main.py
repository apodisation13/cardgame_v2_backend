import logging.config
from contextlib import asynccontextmanager

from fastapi import FastAPI
from lib.utils.db.pool import Database
from services.api.app.apps.api_docs.routes import router as swagger_router

from services.api.app.apps.auth.routes import router as users_router
from services.api.app.config import get_config as get_app_settings
from services.api.app.dependencies import set_global_app
from services.api.app.exceptions.handlers import add_exceptions


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.config = get_app_settings()

    logger = logging.getLogger(__name__)
    logging.config.dictConfig(app.state.config.LOGGING)

    logger.info("Starting API")

    db = Database()
    await db.connect()
    app.state.db = db

    set_global_app(app)

    yield
    await db.disconnect()


app = FastAPI(
    title="Project API",
    lifespan=lifespan,
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/v1/openapi.json",
)

add_exceptions(app)


app.include_router(swagger_router, prefix="", tags=["swagger"])
app.include_router(users_router, prefix="/users", tags=["auth"])
