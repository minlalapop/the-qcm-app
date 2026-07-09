from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.user import UserContext
from app.services.security import user_context_from_token


bearer_scheme = HTTPBearer()


def get_current_user_context(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> UserContext:
    return user_context_from_token(credentials.credentials)


def require_admin(user_context: UserContext = Depends(get_current_user_context)) -> UserContext:
    if user_context.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")
    return user_context
