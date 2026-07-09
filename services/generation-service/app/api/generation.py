from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_bearer_token, get_current_user_context
from app.db.session import get_db
from app.models.mindmap import MindMap
from app.models.summary import Summary
from app.schemas.generation import (
    GenerateMindMapRequest,
    GenerateQCMRequest,
    GenerateSummaryRequest,
    MindMapPublic,
    MindMapUpdate,
    QCMPublic,
    QCMUpdate,
    QuestionPublic,
    QuestionUpdate,
    SummaryPublic,
    SummaryUpdate,
    UserContext,
)
from app.services.generation import (
    generate_mindmap,
    generate_qcm,
    generate_summary,
    get_qcm_for_owner,
    get_question_for_owner,
    list_qcms_for_owner,
    update_qcm,
    update_question,
)


router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/qcms", response_model=QCMPublic, status_code=status.HTTP_201_CREATED)
async def create_qcm(
    payload: GenerateQCMRequest,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> QCMPublic:
    return await generate_qcm(db, current_user, token, payload)


@router.get("/qcms", response_model=list[QCMPublic])
def list_qcms(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[QCMPublic]:
    return list_qcms_for_owner(db, current_user.id, offset=offset, limit=limit)


@router.get("/qcms/{qcm_id}", response_model=QCMPublic)
def get_qcm(
    qcm_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> QCMPublic:
    qcm = get_qcm_for_owner(db, qcm_id, current_user.id)
    if not qcm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QCM not found")
    return qcm


@router.patch("/qcms/{qcm_id}", response_model=QCMPublic)
def patch_qcm(
    qcm_id: str,
    payload: QCMUpdate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> QCMPublic:
    qcm = get_qcm_for_owner(db, qcm_id, current_user.id)
    if not qcm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QCM not found")
    return update_qcm(db, qcm, payload)


@router.delete("/qcms/{qcm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_qcm(
    qcm_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> None:
    qcm = get_qcm_for_owner(db, qcm_id, current_user.id)
    if not qcm:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="QCM not found")
    db.delete(qcm)
    db.commit()


@router.patch("/qcms/{qcm_id}/questions/{question_id}", response_model=QuestionPublic)
def patch_question(
    qcm_id: str,
    question_id: str,
    payload: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> QuestionPublic:
    question = get_question_for_owner(db, qcm_id, question_id, current_user.id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return update_question(db, question, payload)


@router.delete("/qcms/{qcm_id}/questions/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(
    qcm_id: str,
    question_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> None:
    question = get_question_for_owner(db, qcm_id, question_id, current_user.id)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    db.delete(question)
    db.commit()


@router.post("/summaries", response_model=SummaryPublic, status_code=status.HTTP_201_CREATED)
async def create_summary(
    payload: GenerateSummaryRequest,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> SummaryPublic:
    return await generate_summary(db, current_user, token, payload)


@router.get("/summaries", response_model=list[SummaryPublic])
def list_summaries(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[SummaryPublic]:
    return (
        db.query(Summary)
        .filter(Summary.owner_id == current_user.id)
        .order_by(Summary.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/summaries/{summary_id}", response_model=SummaryPublic)
def get_summary(
    summary_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> SummaryPublic:
    summary = db.query(Summary).filter(Summary.id == summary_id, Summary.owner_id == current_user.id).first()
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")
    return summary


@router.patch("/summaries/{summary_id}", response_model=SummaryPublic)
def patch_summary(
    summary_id: str,
    payload: SummaryUpdate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> SummaryPublic:
    summary = db.query(Summary).filter(Summary.id == summary_id, Summary.owner_id == current_user.id).first()
    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Summary not found")
    if payload.title is not None:
        summary.title = payload.title
        if isinstance(summary.structured_payload, dict):
            summary.structured_payload = {**summary.structured_payload, "title": payload.title}
    db.commit()
    db.refresh(summary)
    return summary


@router.post("/mindmaps", response_model=MindMapPublic, status_code=status.HTTP_201_CREATED)
async def create_mindmap(
    payload: GenerateMindMapRequest,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> MindMapPublic:
    return await generate_mindmap(db, current_user, token, payload)


@router.get("/mindmaps", response_model=list[MindMapPublic])
def list_mindmaps(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[MindMapPublic]:
    return (
        db.query(MindMap)
        .filter(MindMap.owner_id == current_user.id)
        .order_by(MindMap.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/mindmaps/{mindmap_id}", response_model=MindMapPublic)
def get_mindmap(
    mindmap_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> MindMapPublic:
    mindmap = db.query(MindMap).filter(MindMap.id == mindmap_id, MindMap.owner_id == current_user.id).first()
    if not mindmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MindMap not found")
    return mindmap


@router.patch("/mindmaps/{mindmap_id}", response_model=MindMapPublic)
def patch_mindmap(
    mindmap_id: str,
    payload: MindMapUpdate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> MindMapPublic:
    mindmap = db.query(MindMap).filter(MindMap.id == mindmap_id, MindMap.owner_id == current_user.id).first()
    if not mindmap:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="MindMap not found")
    if payload.title is not None:
        mindmap.title = payload.title
        if isinstance(mindmap.json_content, dict) and mindmap.json_content.get("root"):
            mindmap.json_content = {**mindmap.json_content, "root": payload.title}
    db.commit()
    db.refresh(mindmap)
    return mindmap
