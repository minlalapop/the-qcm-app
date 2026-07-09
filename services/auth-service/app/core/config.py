from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    APP_NAME: str = "QCM Auth Service"
    APP_ENV: str = "development"

    DATABASE_URL: str = "postgresql+psycopg://qcm_user:qcm_password@localhost:5432/qcm_app"
    DB_SCHEMA: str = "auth"

    JWT_SECRET_KEY: str = "dev-only-jwt-secret-change-me"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENABLE_DEFAULT_ADMIN: bool = True
    DEFAULT_ADMIN_EMAIL: str = "admin@example.com"
    DEFAULT_ADMIN_PASSWORD: str = "admin1234"
    DEFAULT_ADMIN_FULL_NAME: str = "Admin Iktibar"

    CORS_ORIGINS: list[AnyHttpUrl] | list[str] = ["http://localhost:3000", "http://localhost:5173"]


settings = Settings()
