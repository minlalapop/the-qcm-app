from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile
from app.schemas.user import UserContext, UserProfileUpdate


def get_profile_by_auth_user_id(db: Session, auth_user_id: str) -> UserProfile | None:
    return db.query(UserProfile).filter(UserProfile.auth_user_id == auth_user_id).first()


def get_or_create_profile(db: Session, user_context: UserContext) -> UserProfile:
    profile = get_profile_by_auth_user_id(db, user_context.id)
    if profile:
        return profile

    profile = UserProfile(
        auth_user_id=user_context.id,
        email=str(user_context.email).lower(),
        role=user_context.role,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile


def update_profile(db: Session, profile: UserProfile, payload: UserProfileUpdate) -> UserProfile:
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile


def list_profiles(db: Session, offset: int = 0, limit: int = 50) -> list[UserProfile]:
    return db.query(UserProfile).order_by(UserProfile.created_at.desc()).offset(offset).limit(limit).all()
