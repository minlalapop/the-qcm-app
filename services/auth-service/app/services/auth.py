from datetime import UTC, datetime, timedelta

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.refresh_token import RefreshToken
from app.models.role import Role
from app.models.user import User
from app.services.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)


def get_or_create_role(db: Session, name: str) -> Role:
    role = db.query(Role).filter(Role.name == name).first()
    if role:
        return role

    role = Role(name=name, description=f"{name.capitalize()} role")
    db.add(role)
    db.flush()
    return role


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def register_user(db: Session, email: str, password: str, full_name: str | None, role_name: str) -> User:
    role = get_or_create_role(db, role_name)
    user = User(
        email=email.lower(),
        password_hash=hash_password(password),
        full_name=full_name,
        role_id=role.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User | None:
    user = get_user_by_email(db, email)
    if not user or not user.is_active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def create_token_pair(db: Session, user: User) -> tuple[str, str]:
    raw_refresh_token = generate_refresh_token()
    refresh_token = RefreshToken(
        user_id=user.id,
        token_hash=hash_refresh_token(raw_refresh_token),
        expires_at=datetime.now(UTC) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_token)
    db.commit()

    access_token = create_access_token(subject=user.id, email=user.email, role=user.role.name)
    return access_token, raw_refresh_token


def refresh_token_pair(db: Session, raw_refresh_token: str) -> tuple[User, str, str] | None:
    stored_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_refresh_token(raw_refresh_token))
        .first()
    )
    if not stored_token or stored_token.revoked_at or stored_token.expires_at <= datetime.now(UTC):
        return None
    if not stored_token.user.is_active:
        return None

    stored_token.revoked_at = datetime.now(UTC)
    access_token, new_refresh_token = create_token_pair(db, stored_token.user)
    db.commit()
    return stored_token.user, access_token, new_refresh_token


def revoke_refresh_token(db: Session, raw_refresh_token: str) -> bool:
    stored_token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == hash_refresh_token(raw_refresh_token))
        .first()
    )
    if not stored_token or stored_token.revoked_at:
        return False

    stored_token.revoked_at = datetime.now(UTC)
    db.commit()
    return True
