from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_context, require_admin
from app.db.session import get_db
from app.schemas.user import UserContext, UserProfilePublic, UserProfileUpdate
from app.services.users import get_or_create_profile, get_profile_by_auth_user_id, list_profiles, update_profile


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfilePublic)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> UserProfilePublic:
    return get_or_create_profile(db, current_user)


@router.patch("/me", response_model=UserProfilePublic)
def update_my_profile(
    payload: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> UserProfilePublic:
    profile = get_or_create_profile(db, current_user)
    return update_profile(db, profile, payload)


@router.get("/{auth_user_id}", response_model=UserProfilePublic)
def get_user_profile(
    auth_user_id: str,
    db: Session = Depends(get_db),
    _: UserContext = Depends(get_current_user_context),
) -> UserProfilePublic:
    profile = get_profile_by_auth_user_id(db, auth_user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")
    return profile


@router.get("", response_model=list[UserProfilePublic])
def get_user_profiles(
    db: Session = Depends(get_db),
    _: UserContext = Depends(require_admin),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[UserProfilePublic]:
    return list_profiles(db, offset=offset, limit=limit)
