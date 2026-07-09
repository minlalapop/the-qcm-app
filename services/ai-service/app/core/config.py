from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "QCM AI Service"
    APP_ENV: str = "development"

    DATABASE_URL: str = "postgresql+psycopg://qcm_user:qcm_password@localhost:5432/qcm_app"
    DB_SCHEMA: str = "ai"

    JWT_SECRET_KEY: str = "dev-only-jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"

    KNOWLEDGE_SERVICE_URL: str = "http://knowledge-service:8000"

    DEFAULT_LLM_PROVIDER: str = "openrouter"
    OPENROUTER_API_KEY: str | None = None
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_APP_TITLE: str = "The QCM App"
    OPENROUTER_HTTP_REFERER: str = "http://localhost:8005"
    DEFAULT_TOP_K: int = 6
    DEFAULT_TEMPERATURE: float = 0.2
    DEFAULT_TOP_P: float = 0.9
    DEFAULT_MAX_TOKENS: int = 1800

    CORS_ORIGINS: list[AnyHttpUrl] | list[str] = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()
