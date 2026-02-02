from pathlib import Path

from lib.utils.config.env_types import EnvType
from services.rest.app.config import Config, get_config


BASE_DIR = Path(__file__).resolve().parent.parent


config: Config = get_config()

SECRET_KEY = config.DJANGO_SECRET_KEY

# ALLOWED_HOSTS = []
# ALLOWED_HOSTS = [
#     "localhost",
#     "127.0.0.1",
#     "rest",
#     "nginx",
# ]
#
# # Настройте CSRF
# CSRF_TRUSTED_ORIGINS = [
#     "http://localhost:8001",
#     "http://127.0.0.1:8001",
#     "http://localhost:8002",
#     "http://127.0.0.1:8002",
# ]
ALLOWED_HOSTS = ["*"]

if config.ENV_TYPE in EnvType.docker_development():
    CSRF_TRUSTED_ORIGINS = config.CSRF_TRUSTED_ORIGINS
else:
    CSRF_TRUSTED_ORIGINS = ["*"]

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Для продакшена
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTH_USER_MODEL = "accounts.DjangoAuthUser"
