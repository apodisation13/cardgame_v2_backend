from .security import *
from .apps import *
from .middleware import *
from .templates import *
from .database import *
from .localization import *
from .static import *
# from .urls import *

# Базовые настройки
ROOT_URLCONF = 'settings.urls'
WSGI_APPLICATION = 'settings.wsgi.application'
ASGI_APPLICATION = 'settings.asgi.application'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
