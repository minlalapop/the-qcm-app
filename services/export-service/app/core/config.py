from pathlib import Path

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "QCM Export Service"
    APP_ENV: str = "development"

    DATABASE_URL: str = "postgresql+psycopg://qcm_user:qcm_password@localhost:5432/qcm_app"
    DB_SCHEMA: str = "export"

    JWT_SECRET_KEY: str = "dev-only-jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"

    GENERATION_SERVICE_URL: str = "http://generation-service:8000"
    STORAGE_ROOT: Path = Path("/app/storage")
    EXPORT_DIR_NAME: str = "exports"

    CORS_ORIGINS: list[AnyHttpUrl] | list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def export_storage_path(self) -> Path:
        return self.STORAGE_ROOT / self.EXPORT_DIR_NAME


settings = Settings()
