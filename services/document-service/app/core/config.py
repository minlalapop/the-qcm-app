from pathlib import Path

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "QCM Document Service"
    APP_ENV: str = "development"

    DATABASE_URL: str = "postgresql+psycopg://qcm_user:qcm_password@localhost:5432/qcm_app"
    DB_SCHEMA: str = "documents"

    JWT_SECRET_KEY: str = "dev-only-jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"

    STORAGE_ROOT: Path = Path("/app/storage")
    PDF_STORAGE_DIR: str = "pdfs"
    EXTRACTED_IMAGES_DIR: str = "extracted-images"
    TEMP_STORAGE_DIR: str = "temp"

    CHUNK_MAX_CHARS: int = 1200
    CHUNK_OVERLAP_CHARS: int = 180

    CORS_ORIGINS: list[AnyHttpUrl] | list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def pdf_storage_path(self) -> Path:
        return self.STORAGE_ROOT / self.PDF_STORAGE_DIR

    @property
    def extracted_images_path(self) -> Path:
        return self.STORAGE_ROOT / self.EXTRACTED_IMAGES_DIR

    @property
    def temp_storage_path(self) -> Path:
        return self.STORAGE_ROOT / self.TEMP_STORAGE_DIR


settings = Settings()
