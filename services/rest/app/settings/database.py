from pathlib import Path

from services.rest.app.config import Config, get_config


BASE_DIR = Path(__file__).resolve().parent.parent

config: Config = get_config()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config.DB_NAME,
        "USER": config.DB_USER,
        "PASSWORD": config.DB_PASSWORD,
        "HOST": config.DB_HOST,
        "PORT": config.DB_PORT,
    },
}
