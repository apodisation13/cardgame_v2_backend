import os
from urllib.parse import urljoin


APP_PORT_OUTSIDE = os.environ.get("APP_PORT_OUTSIDE")


def build_image_url(
    base_url: str,
    image_path: str,
) -> str:
    """
    Вот тут конечно костыль...
    При запуске через локальный докер, обычно указываю порт в переменной APP_PORT_OUTSIDE
    nginx его проксирует наружу: "${APP_PORT_OUTSIDE}:80"
    то есть внутри сети контейнеров порта-то нет (80), а снаружи есть
    так вот и ссылку на картинки надо будет с этим портом тоже делать
    """
    if APP_PORT_OUTSIDE:
        base_url = f"{base_url.rstrip('/')}:{APP_PORT_OUTSIDE}"
    return urljoin(base_url, f"media/{image_path}")
