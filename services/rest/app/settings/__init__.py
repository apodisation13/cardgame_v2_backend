from .apps import *  # noqa 403
from .database import *  # noqa 403
from .localization import *  # noqa 403
from .middleware import *  # noqa 403
from .security import *  # noqa 403
from .static import *  # noqa 403
from .templates import *  # noqa 403


# Базовые настройки
ROOT_URLCONF = "settings.urls"
WSGI_APPLICATION = "settings.wsgi.application"
ASGI_APPLICATION = "settings.asgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
