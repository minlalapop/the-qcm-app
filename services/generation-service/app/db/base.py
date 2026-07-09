from sqlalchemy import MetaData, text
from sqlalchemy.orm import declarative_base

from app.core.config import settings
from app.db.session import engine


metadata = MetaData(schema=settings.DB_SCHEMA)
Base = declarative_base(metadata=metadata)


def init_db() -> None:
    from app import models  # noqa: F401

    with engine.begin() as connection:
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA}"))

    Base.metadata.create_all(bind=engine)
