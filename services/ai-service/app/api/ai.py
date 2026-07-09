from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_bearer_token, get_current_user_context
from app.db.session import get_db
from app.models.ai_request import AIRequest
from app.schemas.ai import (
    AIRequestLogPublic,
    AIResponsePublic,
    GenerateMindMapRequest,
    GenerateQCMRequest,
    GenerateSummaryRequest,
    UserContext,
)
from app.services.ai import run_ai_generation


router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/qcm", response_model=AIResponsePublic)
async def generate_qcm(
    payload: GenerateQCMRequest,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> AIResponsePublic:
    return await run_ai_generation(db, current_user, token, payload, task_type="qcm")


@router.post("/summary", response_model=AIResponsePublic)
async def generate_summary(
    payload: GenerateSummaryRequest,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> AIResponsePublic:
    return await run_ai_generation(db, current_user, token, payload, task_type="summary")


@router.post("/mindmap", response_model=AIResponsePublic)
async def generate_mindmap(
    payload: GenerateMindMapRequest,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> AIResponsePublic:
    return await run_ai_generation(db, current_user, token, payload, task_type="mindmap")


@router.get("/requests", response_model=list[AIRequestLogPublic])
def list_ai_requests(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[AIRequestLogPublic]:
    return (
        db.query(AIRequest)
        .filter(AIRequest.owner_id == current_user.id)
        .order_by(AIRequest.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
