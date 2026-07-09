from pathlib import Path

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "QCM Learning Service"
    APP_ENV: str = "development"

    DATABASE_URL: str = "postgresql+psycopg://qcm_user:qcm_password@localhost:5432/qcm_app"
    DB_SCHEMA: str = "learning"

    JWT_SECRET_KEY: str = "dev-only-jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"

    EVALUATION_SERVICE_URL: str = "http://evaluation-service:8000"
    VECTOR_STORE_ROOT: Path = Path("/app/vector_store")
    EMBEDDING_MODEL_NAME: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    MIN_RULE_CONFIDENCE: float = 0.55

    CORS_ORIGINS: list[AnyHttpUrl] | list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @property
    def feedback_vector_path(self) -> Path:
        return self.VECTOR_STORE_ROOT / "feedback"


settings = Settings()
