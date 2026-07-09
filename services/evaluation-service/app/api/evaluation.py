from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_context
from app.db.session import get_db
from app.models.evaluation import Evaluation
from app.models.hallucination_report import HallucinationReport
from app.models.question_feedback import QuestionFeedback
from app.schemas.evaluation import (
    CreateEvaluationRequest,
    CreateHallucinationReportRequest,
    CreateQuestionFeedbackRequest,
    EvaluationPublic,
    HallucinationReportPublic,
    QualityMetricPublic,
    QuestionFeedbackPublic,
    UpdateHallucinationReportRequest,
    UserContext,
)
from app.services.evaluation import (
    create_evaluation,
    create_hallucination_report,
    create_question_feedback,
    update_hallucination_report,
)
from app.services.metrics import compute_quality_metrics


router = APIRouter(prefix="/evaluation", tags=["evaluation"])


@router.post("/qcms/{qcm_id}/reviews", response_model=EvaluationPublic, status_code=status.HTTP_201_CREATED)
def review_qcm(
    qcm_id: str,
    payload: CreateEvaluationRequest,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> EvaluationPublic:
    return create_evaluation(db, qcm_id, current_user, payload)


@router.get("/qcms/{qcm_id}/reviews", response_model=list[EvaluationPublic])
def list_qcm_reviews(
    qcm_id: str,
    db: Session = Depends(get_db),
    _: UserContext = Depends(get_current_user_context),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[EvaluationPublic]:
    return (
        db.query(Evaluation)
        .filter(Evaluation.qcm_id == qcm_id)
        .order_by(Evaluation.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/reviews", response_model=list[EvaluationPublic])
def list_my_reviews(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[EvaluationPublic]:
    return (
        db.query(Evaluation)
        .filter(Evaluation.reviewer_id == current_user.id)
        .order_by(Evaluation.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.post(
    "/qcms/{qcm_id}/questions/{question_id}/feedback",
    response_model=QuestionFeedbackPublic,
    status_code=status.HTTP_201_CREATED,
)
def add_question_feedback(
    qcm_id: str,
    question_id: str,
    payload: CreateQuestionFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> QuestionFeedbackPublic:
    return create_question_feedback(db, qcm_id, question_id, current_user, payload)


@router.get("/qcms/{qcm_id}/questions/feedback", response_model=list[QuestionFeedbackPublic])
def list_qcm_question_feedback(
    qcm_id: str,
    db: Session = Depends(get_db),
    _: UserContext = Depends(get_current_user_context),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=200),
) -> list[QuestionFeedbackPublic]:
    return (
        db.query(QuestionFeedback)
        .filter(QuestionFeedback.qcm_id == qcm_id)
        .order_by(QuestionFeedback.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.post(
    "/qcms/{qcm_id}/hallucination-reports",
    response_model=HallucinationReportPublic,
    status_code=status.HTTP_201_CREATED,
)
def report_hallucination(
    qcm_id: str,
    payload: CreateHallucinationReportRequest,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> HallucinationReportPublic:
    return create_hallucination_report(db, qcm_id, current_user, payload)


@router.patch("/hallucination-reports/{report_id}", response_model=HallucinationReportPublic)
def patch_hallucination_report(
    report_id: str,
    payload: UpdateHallucinationReportRequest,
    db: Session = Depends(get_db),
    _: UserContext = Depends(get_current_user_context),
) -> HallucinationReportPublic:
    report = db.query(HallucinationReport).filter(HallucinationReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hallucination report not found")
    return update_hallucination_report(db, report, payload)


@router.get("/qcms/{qcm_id}/hallucination-reports", response_model=list[HallucinationReportPublic])
def list_hallucination_reports(
    qcm_id: str,
    db: Session = Depends(get_db),
    _: UserContext = Depends(get_current_user_context),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[HallucinationReportPublic]:
    return (
        db.query(HallucinationReport)
        .filter(HallucinationReport.qcm_id == qcm_id)
        .order_by(HallucinationReport.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/qcms/{qcm_id}/metrics", response_model=QualityMetricPublic)
def get_qcm_metrics(
    qcm_id: str,
    db: Session = Depends(get_db),
    _: UserContext = Depends(get_current_user_context),
) -> QualityMetricPublic:
    return compute_quality_metrics(db, qcm_id)
