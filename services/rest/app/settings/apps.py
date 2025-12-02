DJANGO_DEFAULT_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

APPS = [
    "apps.accounts.apps.AccountsConfig",
    "apps.cron.apps.CronConfig",
    "apps.events.apps.EventsConfig",
]

SERVICE_APPS = [
    "django_json_widget",
]


INSTALLED_APPS = APPS + DJANGO_DEFAULT_APPS + SERVICE_APPS
