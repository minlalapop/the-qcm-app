from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_bearer_token, get_current_user_context
from app.db.session import get_db
from app.models.export import Export
from app.models.export_job import ExportJob
from app.schemas.export import ExportJobPublic, ExportOptions, ExportPublic, UserContext
from app.services.exporter import create_job, export_mindmap, export_qcm, export_summary
from app.services.generation_client import GenerationClient
from app.services.storage import absolute_storage_path


router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("/qcms/{qcm_id}/pdf", response_model=ExportPublic, status_code=status.HTTP_201_CREATED)
async def export_qcm_pdf_endpoint(
    qcm_id: str,
    options: ExportOptions = Body(default_factory=ExportOptions),
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> ExportPublic:
    return await _export_qcm(qcm_id, "pdf", options, db, current_user, token)


@router.post("/qcms/{qcm_id}/docx", response_model=ExportPublic, status_code=status.HTTP_201_CREATED)
async def export_qcm_docx_endpoint(
    qcm_id: str,
    options: ExportOptions = Body(default_factory=ExportOptions),
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> ExportPublic:
    return await _export_qcm(qcm_id, "docx", options, db, current_user, token)


@router.post("/qcms/{qcm_id}/xlsx", response_model=ExportPublic, status_code=status.HTTP_201_CREATED)
async def export_qcm_xlsx_endpoint(
    qcm_id: str,
    options: ExportOptions = Body(default_factory=ExportOptions),
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> ExportPublic:
    return await _export_qcm(qcm_id, "xlsx", options, db, current_user, token)


@router.post("/summaries/{summary_id}/pdf", response_model=ExportPublic, status_code=status.HTTP_201_CREATED)
async def export_summary_pdf_endpoint(
    summary_id: str,
    options: ExportOptions = Body(default_factory=ExportOptions),
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> ExportPublic:
    return await _export_summary(summary_id, "pdf", options, db, current_user, token)


@router.post("/summaries/{summary_id}/docx", response_model=ExportPublic, status_code=status.HTTP_201_CREATED)
async def export_summary_docx_endpoint(
    summary_id: str,
    options: ExportOptions = Body(default_factory=ExportOptions),
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> ExportPublic:
    return await _export_summary(summary_id, "docx", options, db, current_user, token)


@router.post("/mindmaps/{mindmap_id}/png", response_model=ExportPublic, status_code=status.HTTP_201_CREATED)
async def export_mindmap_png_endpoint(
    mindmap_id: str,
    options: ExportOptions = Body(default_factory=ExportOptions),
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> ExportPublic:
    return await _export_mindmap(mindmap_id, "png", options, db, current_user, token)


@router.post("/mindmaps/{mindmap_id}/mermaid", response_model=ExportPublic, status_code=status.HTTP_201_CREATED)
async def export_mindmap_mermaid_endpoint(
    mindmap_id: str,
    options: ExportOptions = Body(default_factory=ExportOptions),
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> ExportPublic:
    return await _export_mindmap(mindmap_id, "mermaid", options, db, current_user, token)


@router.get("", response_model=list[ExportPublic])
def list_exports(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    resource_type: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[ExportPublic]:
    query = db.query(Export).filter(Export.owner_id == current_user.id)
    if resource_type:
        query = query.filter(Export.resource_type == resource_type)
    return query.order_by(Export.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/jobs", response_model=list[ExportJobPublic])
def list_export_jobs(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    resource_type: str | None = Query(default=None),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[ExportJobPublic]:
    query = db.query(ExportJob).filter(ExportJob.owner_id == current_user.id)
    if resource_type:
        query = query.filter(ExportJob.resource_type == resource_type)
    return query.order_by(ExportJob.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/jobs/{job_id}", response_model=ExportJobPublic)
def get_export_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> ExportJobPublic:
    job = db.query(ExportJob).filter(ExportJob.id == job_id, ExportJob.owner_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export job not found")
    return job


@router.get("/{export_id}", response_model=ExportPublic)
def get_export(
    export_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> ExportPublic:
    return _get_export_for_owner(db, export_id, current_user.id)


@router.get("/{export_id}/download")
def download_export(
    export_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> FileResponse:
    export = _get_export_for_owner(db, export_id, current_user.id)
    path = absolute_storage_path(export.file_path)
    if not path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export file not found")
    return FileResponse(path, media_type=export.mime_type, filename=path.name)


async def _export_qcm(
    qcm_id: str,
    export_format: str,
    options: ExportOptions,
    db: Session,
    current_user: UserContext,
    token: str,
) -> ExportPublic:
    job = create_job(db, current_user, "qcm", qcm_id, export_format)
    try:
        qcm = await GenerationClient(token).get_qcm(qcm_id)
        return export_qcm(db, current_user, qcm, export_format, options, job)
    except Exception as exc:
        _mark_failed(db, job, exc)
        raise


async def _export_summary(
    summary_id: str,
    export_format: str,
    options: ExportOptions,
    db: Session,
    current_user: UserContext,
    token: str,
) -> ExportPublic:
    job = create_job(db, current_user, "summary", summary_id, export_format)
    try:
        summary = await GenerationClient(token).get_summary(summary_id)
        return export_summary(db, current_user, summary, export_format, options, job)
    except Exception as exc:
        _mark_failed(db, job, exc)
        raise


async def _export_mindmap(
    mindmap_id: str,
    export_format: str,
    options: ExportOptions,
    db: Session,
    current_user: UserContext,
    token: str,
) -> ExportPublic:
    job = create_job(db, current_user, "mindmap", mindmap_id, export_format)
    try:
        mindmap = await GenerationClient(token).get_mindmap(mindmap_id)
        return export_mindmap(db, current_user, mindmap, export_format, options, job)
    except Exception as exc:
        _mark_failed(db, job, exc)
        raise


def _get_export_for_owner(db: Session, export_id: str, owner_id: str) -> Export:
    export = db.query(Export).filter(Export.id == export_id, Export.owner_id == owner_id).first()
    if not export:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")
    return export


def _mark_failed(db: Session, job, exc: Exception) -> None:
    job.status = "failed"
    job.error_message = str(exc)[:1000]
    job.finished_at = datetime.now(timezone.utc)
    db.commit()
