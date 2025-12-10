from elasticapm import get_client
import os
from elasticapm.contrib.starlette import make_apm_client

from lib.utils.config.base import BaseConfig


class ElasticTracerManager:
    _instance = None
    _initialized = False
    _apm_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        config: BaseConfig,
        service_name: str,
        environment: str = "development",
    ) -> bool:
        # Проверяем, есть ли уже глобальный клиент (избегаем дублирования)
        existing_client = get_client()
        if existing_client is not None:
            print("APM: reusing existing client")
            self._apm_client = existing_client
            self._initialized = True
            return False

        if self._initialized:
            print("APM: already initialized by this manager")
            return False

        # # Читаем из стандартных переменных elastic-apm
        # apm_enabled = os.getenv("ELASTIC_APM_ENABLED", "true").lower() == "true"
        #
        # if not apm_enabled:
        #     print("APM disabled")
        #     self._initialized = True
        #     return True

        # Получаем настройки из переменных окружения
        apm_server_url = config.ELASTIC_APM_SERVER_URL

        config = {
            "SERVICE_NAME": service_name,
            "SERVER_URL": apm_server_url,
            "ENVIRONMENT": environment,

            # Аутентификация
            "SECRET_TOKEN": config.ELASTIC_APM_SECRET_TOKEN,

            # Настройки трейсинга
            "CAPTURE_BODY": "all",  # off, errors, transactions, all
            "CAPTURE_HEADERS": True,
            "TRANSACTION_SAMPLE_RATE": 1.0,  # 1.0 = 100% транзакций

            # Производительность
            "SPAN_COMPRESSION_ENABLED": True,
            "SPAN_COMPRESSION_EXACT_MATCH_MAX_DURATION": "50ms",
            "SPAN_COMPRESSION_SAME_KIND_MAX_DURATION": "5ms",

            # Логирование самого APM
            "DEBUG": os.getenv("APM_DEBUG", "false").lower() == "true",
        }

        try:
            self._apm_client = make_apm_client(config)
            self._initialized = True
            print(f"APM initialized: {service_name} -> {apm_server_url}")
            return True
        except Exception as e:
            print(f"Failed to initialize APM: {e}")
            return False

    @property
    def client(self):
        return self._apm_client

    @property
    def is_initialized(self) -> bool:
        return self._initialized
