import hashlib
import shutil
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


def ensure_storage_dirs() -> None:
    settings.pdf_storage_path.mkdir(parents=True, exist_ok=True)
    settings.extracted_images_path.mkdir(parents=True, exist_ok=True)
    settings.temp_storage_path.mkdir(parents=True, exist_ok=True)


def document_pdf_path(owner_id: str, pdf_hash: str) -> Path:
    return settings.pdf_storage_path / owner_id / f"{pdf_hash}.pdf"


def document_images_dir(document_id: str) -> Path:
    return settings.extracted_images_path / document_id


def document_page_previews_dir(document_id: str) -> Path:
    return settings.extracted_images_path / document_id / "page-previews"


async def save_uploaded_pdf(upload_file: UploadFile, owner_id: str) -> tuple[str, Path, int]:
    ensure_storage_dirs()
    temp_path = settings.temp_storage_path / f"{owner_id}-{upload_file.filename}.upload"
    pdf_hash = hashlib.sha256()
    file_size = 0

    with temp_path.open("wb") as output:
        while chunk := await upload_file.read(1024 * 1024):
            file_size += len(chunk)
            pdf_hash.update(chunk)
            output.write(chunk)

    digest = pdf_hash.hexdigest()
    final_path = document_pdf_path(owner_id, digest)
    final_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(temp_path), final_path)
    return digest, final_path, file_size


def delete_file_if_exists(path: str | Path) -> None:
    file_path = Path(path)
    if file_path.exists() and file_path.is_file():
        file_path.unlink()


def delete_directory_if_exists(path: str | Path) -> None:
    directory = Path(path)
    if directory.exists() and directory.is_dir():
        shutil.rmtree(directory)
