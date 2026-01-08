DJANGO_DEFAULT_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

SERVICE_APPS = [
    "django_json_widget",
]

APPS = [
    "apps.accounts.apps.AccountsConfig",
    "apps.cards.apps.CardsConfig",
    "apps.core.apps.CoreConfig",
    "apps.cron.apps.CronConfig",
    "apps.enemies.apps.EnemiesConfig",
    "apps.events.apps.EventsConfig",
    "apps.news.apps.NewsConfig",
    "apps.seasons.apps.SeasonsConfig",
]


INSTALLED_APPS = DJANGO_DEFAULT_APPS + SERVICE_APPS + APPS
