from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.schemas.user import UserPublic
from app.services.auth import (
    authenticate_user,
    create_token_pair,
    get_user_by_email,
    refresh_token_pair,
    register_user,
    revoke_refresh_token,
)


router = APIRouter(prefix="/auth", tags=["auth"])


def build_user_public(user: User) -> UserPublic:
    return UserPublic(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        role=user.role.name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    if get_user_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    try:
        user = register_user(
            db=db,
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            role_name=payload.role,
        )
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered") from exc

    access_token, refresh_token = create_token_pair(db, user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=build_user_public(user),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = authenticate_user(db, payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token, refresh_token = create_token_pair(db, user)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=build_user_public(user),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token_pair = refresh_token_pair(db, payload.refresh_token)
    if not token_pair:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    user, access_token, refresh_token = token_pair
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=build_user_public(user),
    )


@router.post("/logout", response_model=MessageResponse)
def logout(payload: LogoutRequest, db: Session = Depends(get_db)) -> MessageResponse:
    revoke_refresh_token(db, payload.refresh_token)
    return MessageResponse(message="Logged out")


@router.get("/me", response_model=UserPublic)
def me(current_user: User = Depends(get_current_user)) -> UserPublic:
    return build_user_public(current_user)
