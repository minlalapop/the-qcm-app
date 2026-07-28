import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy.orm import Session

from app.models.export import Export
from app.models.export_job import ExportJob
from app.schemas.export import ExportOptions, UserContext
from app.services.renderers import (
    render_mermaid_code,
    render_mermaid_png,
    render_qcm_docx,
    render_qcm_pdf,
    render_qcm_xlsx,
    render_summary_docx,
    render_summary_pdf,
)
from app.services.storage import ensure_export_storage, relative_export_path, safe_filename


MIME_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "mermaid": "text/vnd.mermaid",
    "png": "image/png",
}


def create_job(db: Session, current_user: UserContext, resource_type: str, resource_id: str, export_format: str) -> ExportJob:
    job = ExportJob(
        owner_id=current_user.id,
        resource_type=resource_type,
        resource_id=resource_id,
        export_format=export_format,
        status="running",
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def export_qcm(
    db: Session,
    current_user: UserContext,
    qcm: dict[str, Any],
    export_format: str,
    options: ExportOptions,
    job: ExportJob,
) -> Export:
    title = options.title or qcm.get("title") or "QCM"
    path = _build_output_path("qcm", qcm["id"], title, export_format)
    if export_format == "pdf":
        render_qcm_pdf(qcm, path, options)
    elif export_format == "docx":
        render_qcm_docx(qcm, path, options)
    elif export_format == "xlsx":
        render_qcm_xlsx(qcm, path, options)
    else:
        raise ValueError(f"Unsupported QCM export format: {export_format}")
    return _save_export(db, current_user, "qcm", qcm["id"], export_format, title, path, job, options)


def export_summary(
    db: Session,
    current_user: UserContext,
    summary: dict[str, Any],
    export_format: str,
    options: ExportOptions,
    job: ExportJob,
) -> Export:
    title = options.title or summary.get("title") or "Summary"
    path = _build_output_path("summary", summary["id"], title, export_format)
    if export_format == "pdf":
        render_summary_pdf(summary, path, options)
    elif export_format == "docx":
        render_summary_docx(summary, path, options)
    else:
        raise ValueError(f"Unsupported summary export format: {export_format}")
    return _save_export(db, current_user, "summary", summary["id"], export_format, title, path, job, options)


def export_mindmap(
    db: Session,
    current_user: UserContext,
    mindmap: dict[str, Any],
    export_format: str,
    options: ExportOptions,
    job: ExportJob,
) -> Export:
    title = options.title or mindmap.get("title") or "MindMap"
    extension = "mmd" if export_format == "mermaid" else export_format
    path = _build_output_path("mindmap", mindmap["id"], title, extension)
    if export_format == "png":
        render_mermaid_png(mindmap, path)
    elif export_format == "mermaid":
        render_mermaid_code(mindmap, path)
    else:
        raise ValueError(f"Unsupported mindmap export format: {export_format}")
    return _save_export(db, current_user, "mindmap", mindmap["id"], export_format, title, path, job, options)


def _build_output_path(resource_type: str, resource_id: str, title: str, extension: str) -> Path:
    ensure_export_storage()
    filename = f"{safe_filename(f'{resource_type}-{title}-{resource_id}')}-{uuid.uuid4().hex[:10]}.{extension}"
    return ensure_path(filename)


def ensure_path(filename: str) -> Path:
    from app.core.config import settings

    return settings.export_storage_path / filename


def _save_export(
    db: Session,
    current_user: UserContext,
    resource_type: str,
    resource_id: str,
    export_format: str,
    title: str,
    absolute_path: Path,
    job: ExportJob,
    options: ExportOptions,
) -> Export:
    relative_path = relative_export_path(absolute_path.name)
    export = Export(
        owner_id=current_user.id,
        resource_type=resource_type,
        resource_id=resource_id,
        export_format=export_format,
        title=title,
        file_path=relative_path,
        mime_type=MIME_TYPES[export_format],
        status="completed",
        details=options.model_dump(),
    )
    db.add(export)
    db.flush()
    job.export_id = export.id
    job.status = "completed"
    job.finished_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(export)
    return export
