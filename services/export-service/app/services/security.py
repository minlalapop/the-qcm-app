import jwt
from fastapi import HTTPException, status
from jwt import InvalidTokenError

from app.core.config import settings
from app.schemas.export import UserContext


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])


def user_context_from_token(token: str) -> UserContext:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_access_token(token)
        if payload.get("type") != "access":
            raise credentials_error

        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role")
        if not user_id or not email or not role:
            raise credentials_error
    except InvalidTokenError as exc:
        raise credentials_error from exc

    return UserContext(id=user_id, email=email, role=role)
