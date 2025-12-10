from contextlib import asynccontextmanager
import logging.config

from elasticapm.contrib.starlette import ElasticAPM
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from lib.utils.config.env_types import EnvType
from lib.utils.db.pool import Database
from lib.utils.elk.elastic_logger import ElasticLoggerManager
from lib.utils.elk.elastic_tracer import ElasticTracerManager
from services.api.app.apps.api_docs.routes import router as swagger_router
from services.api.app.apps.auth.routes import router as users_router
from services.api.app.config import get_config as get_app_settings
from services.api.app.dependencies import set_global_app
from services.api.app.exceptions.handlers import add_exceptions


apm_manager = ElasticTracerManager()
elastic_logger_manager = ElasticLoggerManager()
config = get_app_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.config = config

    logging.config.dictConfig(config.LOGGING)

    if config.ENV_TYPE in EnvType.need_elastic():
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
    title="Project API",
    lifespan=lifespan,
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    openapi_url="/api/v1/openapi.json",
)

add_exceptions(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (только для разработки!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
if config.ENV_TYPE in EnvType.need_elastic():
    app.add_middleware(
        ElasticAPM,
        client=apm_manager.client,
    )


app.include_router(swagger_router, prefix="", tags=["swagger"])
app.include_router(users_router, prefix="/users", tags=["accounts"])
