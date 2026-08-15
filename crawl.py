from urllib.parse import urlsplit


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    full_path = f"{parts.netloc}{parts.path}"
    full_path = full_path.rstrip("/")
    return full_path.lower()
