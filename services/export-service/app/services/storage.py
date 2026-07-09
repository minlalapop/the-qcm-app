import re
from pathlib import Path

from app.core.config import settings


def ensure_export_storage() -> None:
    settings.export_storage_path.mkdir(parents=True, exist_ok=True)


def safe_filename(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]+", "-", value.strip()).strip("-")
    return cleaned[:120] or "export"


def relative_export_path(filename: str) -> str:
    return f"{settings.EXPORT_DIR_NAME}/{filename}"


def absolute_storage_path(relative_path: str) -> Path:
    return settings.STORAGE_ROOT / relative_path
