import logging
import time
import sys
from datetime import datetime
import os
import threading
from typing import Optional

# КРИТИЧНО: Отключаем логи ДО импорта Elasticsearch!
logging.getLogger("elastic_transport").setLevel(logging.WARNING)
logging.getLogger("elastic_transport.transport").setLevel(logging.WARNING)
logging.getLogger("elasticsearch").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)

# Теперь импортируем
from elasticsearch import Elasticsearch


class ElasticsearchHandler(logging.Handler):
    """Хендлер для отправки логов в Elasticsearch"""

    # Список логгеров, которые нужно игнорировать
    IGNORED_LOGGERS = {
        'elasticsearch',
        'elastic_transport',
        'elastic_transport.transport',
        'urllib3',
        'urllib3.connectionpool',
        'urllib3.util',
        'urllib3.util.retry',
        'es_handler_'
    }

    def __init__(self, service_name="myapp", retry_count=3):
        super().__init__()
        self.service_name = service_name
        self.retry_count = retry_count
        self.es = None
        self._sending = threading.local()  # Для предотвращения рекурсии
        self._init_elasticsearch()

    def _init_elasticsearch(self):
        """Инициализация подключения к Elasticsearch"""
        try:
            self.es = Elasticsearch(
                ['http://elasticsearch:9200'],
                verify_certs=False,
                ssl_show_warn=False,
                request_timeout=30,
                max_retries=3,
                retry_on_timeout=True,
                basic_auth=("elastic", "YourStrongPassword123!"),
            )

            info = self.es.info()
            version = info['version']['number']
            print(f"✅ Подключение к Elasticsearch {version} установлено")

        except Exception as e:
            print(f"❌ Ошибка подключения к Elasticsearch: {e}")
            self.es = None

    def emit(self, record):
        """Отправка лога в Elasticsearch"""

        # КРИТИЧНО: Игнорируем логи от ES библиотек
        if any(record.name.startswith(ignored) for ignored in self.IGNORED_LOGGERS):
            return

        # Предотвращаем рекурсию
        if getattr(self._sending, 'in_progress', False):
            return

        if not self.es:
            return

        try:
            self._sending.in_progress = True

            # Формируем JSON
            log_data = {
                "@timestamp": datetime.now().isoformat() + "Z",
                "level": record.levelname,
                "message": record.getMessage(),
                "service": self.service_name,
                "logger": record.name,
                "hostname": os.getenv("HOSTNAME", "unknown"),
                "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            }

            # Добавляем exception если есть
            if record.exc_info:
                log_data["exception"] = self.format(record)

            # Добавляем extra поля
            for key, value in record.__dict__.items():
                if key not in {'name', 'msg', 'args', 'created', 'filename', 'funcName',
                               'levelname', 'levelno', 'lineno', 'module', 'msecs',
                               'pathname', 'process', 'processName', 'relativeCreated',
                               'thread', 'threadName', 'exc_info', 'exc_text', 'stack_info',
                               'getMessage', 'taskName'} and not key.startswith('_'):
                    try:
                        str(value)  # Проверка сериализации
                        log_data[key] = value
                    except:
                        pass

            # Отправляем в Elasticsearch БЕЗ логирования
            self.es.index(
                index=f"logs-{self.service_name}-{datetime.now().strftime('%Y.%m.%d')}",
                document=log_data,
                refresh=False
            )

        except Exception:
            pass  # Молча игнорируем ошибки
        finally:
            self._sending.in_progress = False


def setup_elastic_logging_global(service_name="fast-api", delay_seconds=5):
    """
    Настраивает Elasticsearch хендлер для ВСЕХ логгеров
    """

    # ВАЖНО: Отключаем логи ДО всего остального
    for logger_name in [
        'elasticsearch',
        'elasticsearch.trace',
        'elastic_transport',
        'elastic_transport.transport',
        'elastic_transport.node',
        'elastic_transport.node_pool',
        'urllib3',
        'urllib3.connectionpool',
        'urllib3.util',
        'urllib3.util.retry'
    ]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)
        logging.getLogger(logger_name).propagate = False

    if delay_seconds > 0:
        print(f"⏳ Ожидаем {delay_seconds} секунд перед подключением к Elasticsearch...")
        time.sleep(delay_seconds)

    root_logger = logging.getLogger()

    # Проверяем, не добавлен ли уже
    for handler in root_logger.handlers:
        if isinstance(handler, ElasticsearchHandler):
            print(f"⚠️ Elasticsearch handler уже добавлен")
            return root_logger

    # Создаем хендлер
    es_handler = ElasticsearchHandler(service_name=service_name)
    es_handler.setLevel(logging.INFO)

    # Создаем фильтр для исключения системных логов
    class SystemLogFilter(logging.Filter):
        def filter(self, record):
            # Исключаем системные логгеры
            return not any(record.name.startswith(ignored)
                           for ignored in ElasticsearchHandler.IGNORED_LOGGERS)

    es_handler.addFilter(SystemLogFilter())

    # Добавляем к корневому логгеру
    root_logger.addHandler(es_handler)

    print(f"✅ Elasticsearch хендлер добавлен глобально для сервиса '{service_name}'")
    return root_logger


# Синглтон для управления единственным экземпляром
class ElasticLoggerManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, service_name="fast-api", delay_seconds=5):
        """Инициализация Elasticsearch логирования (вызывать только один раз)"""
        if not self._initialized:
            setup_elastic_logging_global(service_name, delay_seconds)
            self._initialized = True
            return True
        return False

    def get_logger(self, name):
        """Получить логгер (будет автоматически писать в ES если инициализирован)"""
        return logging.getLogger(name)


# from elasticapm.contrib.starlette import make_apm_client

logger = logging.getLogger(__name__)
from elasticapm import Client, get_client

# class ElasticAPMManager:
#     """
#     Синглтон для управления Elastic APM (аналогично ElasticLoggerManager)
#     Инициализируется ОДИН раз при старте приложения
#     """
#     _instance = None
#     _initialized: bool = False
#     _apm_client = None
#
#     def __new__(cls):
#         if cls._instance is None:
#             cls._instance = super().__new__(cls)
#         return cls._instance
#
#     def initialize(
#         self,
#         service_name: str,
#         server_url: str = "http://apm-server:8200",
#         environment: str = "development",
#         secret_token: str = "",
#         capture_body: str = "all",
#         transaction_sample_rate: float = 1.0,
#         debug: bool = False
#     ) -> bool:
#         if self._initialized:
#             logger.warning("APM уже инициализирован ранее. Пропускаем повторную инициализацию.")
#             return False
#
#         try:
#             apm_config = {
#                 'SERVER_URL': server_url,
#                 'SERVICE_NAME': service_name,
#                 'ENVIRONMENT': environment,
#
#                 # Настройки трассировки
#                 'COLLECT_LOCAL_VARIABLES': 'all',
#                 'CAPTURE_BODY': capture_body,
#                 'TRANSACTION_SAMPLE_RATE': transaction_sample_rate,
#
#                 # Для отладки
#                 'DEBUG': debug,
#
#                 # Асинхронный режим (для FastAPI)
#                 'ASYNC_MODE': True,
#             }
#
#             # Добавляем секретный токен, если задан
#             if secret_token:
#                 apm_config['SECRET_TOKEN'] = secret_token
#                 logger.debug(f"APM использует секретный токен: {secret_token[:5]}...")
#
#             # Создаем APM клиент
#             self._apm_client = Client(apm_config)
#
#             self._initialized = True
#
#             logger.info(
#                 f"✅ Elastic APM инициализирован\n"
#                 f"   Сервис: {service_name}\n"
#                 f"   Окружение: {environment}\n"
#                 f"   APM Server: {server_url}\n"
#                 f"   Семплирование: {transaction_sample_rate * 100}%"
#             )
#             return True
#
#         except Exception as e:
#             logger.error(f"❌ Ошибка инициализации Elastic APM: {e}")
#             self._apm_client = None
#             self._initialized = False
#             return False
#
#     def close(self):
#         """Закрыть APM клиент (вызывать при завершении приложения)"""
#         if self._initialized and self._apm_client:
#             try:
#                 self._apm_client.close()
#                 logger.info("APM клиент закрыт")
#             except Exception as e:
#                 logger.error(f"Ошибка при закрытии APM клиента: {e}")
#
#             self._apm_client = None
#             self._initialized = False
#
#     @property
#     def client(self):
#         if not self._initialized:
#             logger.warning("APM клиент запрошен до инициализации. Сначала вызовите initialize()")
#         return self._apm_client


# app/core/apm.py

import os
from elasticapm.contrib.starlette import make_apm_client



class APMManager:
    _instance = None
    _initialized = False
    _apm_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(
        self,
        service_name: str = "fast-api",
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

        # Читаем из стандартных переменных elastic-apm
        apm_enabled = os.getenv("ELASTIC_APM_ENABLED", "true").lower() == "true"

        if not apm_enabled:
            print("APM disabled")
            self._initialized = True
            return True

        # Получаем настройки из переменных окружения
        apm_server_url = os.getenv("ELASTIC_APM_SERVER_URL", "http://apm-server:8200")
        apm_secret_token = os.getenv("ELASTIC_APM_SECRET_TOKEN", "some-secret-key")

        config = {
            "SERVICE_NAME": service_name,
            "SERVER_URL": apm_server_url,
            "ENVIRONMENT": environment,

            # Аутентификация
            "SECRET_TOKEN": apm_secret_token,

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
        """Получить APM клиент"""
        return self._apm_client

    @property
    def is_initialized(self) -> bool:
        return self._initialized
