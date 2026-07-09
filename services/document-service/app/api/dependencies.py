from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.schemas.document import UserContext
from app.services.security import user_context_from_token


bearer_scheme = HTTPBearer()


def get_current_user_context(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> UserContext:
    return user_context_from_token(credentials.credentials)
