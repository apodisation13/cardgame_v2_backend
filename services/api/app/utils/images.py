from urllib.parse import urljoin


def build_image_url(
    base_url: str,
    image_path: str,
) -> str:
    return urljoin(base_url, f"media/{image_path}")
