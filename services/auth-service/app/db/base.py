from sqlalchemy import MetaData, text
from sqlalchemy.orm import declarative_base

from app.core.config import settings
from app.db.session import SessionLocal, engine


metadata = MetaData(schema=settings.DB_SCHEMA)
Base = declarative_base(metadata=metadata)


def init_db() -> None:
    from app import models  # noqa: F401

    with engine.begin() as connection:
        connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {settings.DB_SCHEMA}"))

    Base.metadata.create_all(bind=engine)
    seed_default_admin()


def seed_default_admin() -> None:
    if not settings.ENABLE_DEFAULT_ADMIN or settings.APP_ENV == "production":
        return

    from app.models.role import Role
    from app.models.user import User
    from app.services.security import hash_password

    db = SessionLocal()
    try:
        admin_role = db.query(Role).filter(Role.name == "admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Development admin role")
            db.add(admin_role)
            db.flush()

        existing_admin = db.query(User).filter(User.email == settings.DEFAULT_ADMIN_EMAIL.lower()).first()
        if existing_admin:
            existing_admin.password_hash = hash_password(settings.DEFAULT_ADMIN_PASSWORD)
            existing_admin.full_name = settings.DEFAULT_ADMIN_FULL_NAME
            existing_admin.role_id = admin_role.id
            existing_admin.is_active = True
            existing_admin.is_verified = True
            db.commit()
            return

        db.add(
            User(
                email=settings.DEFAULT_ADMIN_EMAIL.lower(),
                password_hash=hash_password(settings.DEFAULT_ADMIN_PASSWORD),
                full_name=settings.DEFAULT_ADMIN_FULL_NAME,
                role_id=admin_role.id,
                is_active=True,
                is_verified=True,
            )
        )
        db.commit()
    finally:
        db.close()
