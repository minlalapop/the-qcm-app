from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings
from app.services.security import user_context_from_token


def test_user_context_from_access_token() -> None:
    token = jwt.encode(
        {
            "sub": "user-1",
            "email": "teacher@example.com",
            "role": "teacher",
            "type": "access",
            "exp": datetime.now(UTC) + timedelta(minutes=5),
        },
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )

    user_context = user_context_from_token(token)

    assert user_context.id == "user-1"
    assert user_context.email == "teacher@example.com"
    assert user_context.role == "teacher"
