from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_bearer_token, get_current_user_context
from app.db.session import get_db
from app.models.feedback_example import FeedbackExample
from app.models.learned_rule import LearnedRule
from app.models.teacher_preference import TeacherPreference
from app.schemas.learning import (
    AnalyzeQCMRequest,
    FeedbackExampleCreate,
    FeedbackExamplePublic,
    LearnedRulePublic,
    LearningAnalysisPublic,
    PromptContextResponse,
    SimilarFeedbackRequest,
    SimilarFeedbackResult,
    TeacherPreferencePublic,
    UserContext,
)
from app.services.evaluation_client import fetch_qcm_feedback, fetch_qcm_metrics
from app.services.learning import (
    active_preferences,
    active_rules,
    analyze_feedback,
    create_feedback_example,
    search_similar_examples,
)


router = APIRouter(prefix="/learning", tags=["learning"])


@router.post("/qcms/{qcm_id}/analyze", response_model=LearningAnalysisPublic)
async def analyze_qcm_feedback(
    qcm_id: str,
    payload: AnalyzeQCMRequest,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> LearningAnalysisPublic:
    feedbacks = await fetch_qcm_feedback(qcm_id, token)
    metrics = await fetch_qcm_metrics(qcm_id, token)
    teacher_id = payload.teacher_id or current_user.id
    return analyze_feedback(
        db=db,
        qcm_id=qcm_id,
        metrics=metrics,
        feedbacks=feedbacks,
        teacher_id=teacher_id,
        create_new_prompt_version=payload.create_prompt_version,
        index_validated_examples=payload.index_validated_examples,
    )


@router.get("/rules", response_model=list[LearnedRulePublic])
def list_rules(
    db: Session = Depends(get_db),
    _: UserContext = Depends(get_current_user_context),
    task_type: str = Query(default="qcm"),
    teacher_id: str | None = None,
) -> list[LearnedRulePublic]:
    return active_rules(db, task_type=task_type, teacher_id=teacher_id)


@router.get("/preferences", response_model=list[TeacherPreferencePublic])
def list_preferences(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    teacher_id: str | None = None,
    task_type: str = Query(default="qcm"),
) -> list[TeacherPreferencePublic]:
    return active_preferences(db, teacher_id=teacher_id or current_user.id, task_type=task_type)


@router.post("/feedback-examples", response_model=FeedbackExamplePublic)
def add_feedback_example(
    payload: FeedbackExampleCreate,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> FeedbackExamplePublic:
    return create_feedback_example(db, current_user, payload)


@router.get("/feedback-examples", response_model=list[FeedbackExamplePublic])
def list_feedback_examples(
    db: Session = Depends(get_db),
    _: UserContext = Depends(get_current_user_context),
    teacher_id: str | None = None,
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[FeedbackExamplePublic]:
    query = db.query(FeedbackExample)
    if teacher_id:
        query = query.filter(FeedbackExample.teacher_id == teacher_id)
    return query.order_by(FeedbackExample.created_at.desc()).offset(offset).limit(limit).all()


@router.post("/feedback-examples/search", response_model=list[SimilarFeedbackResult])
def search_feedback_examples(
    payload: SimilarFeedbackRequest,
    db: Session = Depends(get_db),
    _: UserContext = Depends(get_current_user_context),
) -> list[SimilarFeedbackResult]:
    return search_similar_examples(db, payload.query, payload.top_k, teacher_id=payload.teacher_id)


@router.get("/prompt-context", response_model=PromptContextResponse)
def get_prompt_context(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    task_type: str = Query(default="qcm"),
    teacher_id: str | None = None,
    query: str = Query(default="QCM medical pedagogique avec distracteurs plausibles"),
    top_k: int = Query(default=3, ge=0, le=10),
) -> PromptContextResponse:
    selected_teacher_id = teacher_id or current_user.id
    return PromptContextResponse(
        task_type=task_type,
        teacher_id=selected_teacher_id,
        learned_rules=active_rules(db, task_type=task_type, teacher_id=selected_teacher_id),
        teacher_preferences=active_preferences(db, teacher_id=selected_teacher_id, task_type=task_type),
        similar_examples=search_similar_examples(db, query, top_k, teacher_id=selected_teacher_id) if top_k else [],
    )
