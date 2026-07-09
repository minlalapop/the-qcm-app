from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "QCM Evaluation Service"
    APP_ENV: str = "development"

    DATABASE_URL: str = "postgresql+psycopg://qcm_user:qcm_password@localhost:5432/qcm_app"
    DB_SCHEMA: str = "evaluation"

    JWT_SECRET_KEY: str = "dev-only-jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"

    CORS_ORIGINS: list[AnyHttpUrl] | list[str] = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()
