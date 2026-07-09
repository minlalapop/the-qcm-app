from datetime import UTC, datetime
from pathlib import Path

import fitz
from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_image import DocumentImage
from app.models.document_metadata import DocumentMetadata
from app.models.document_page import DocumentPage
from app.models.extraction_job import ExtractionJob
from app.schemas.document import DocumentDetail, UserContext
from app.services.cache import list_cache_entries, upsert_cache
from app.services.extractor import extract_pdf_elements
from app.services.storage import (
    delete_directory_if_exists,
    delete_file_if_exists,
    document_images_dir,
    document_page_previews_dir,
    save_uploaded_pdf,
)


def get_document_for_owner(db: Session, document_id: str, owner_id: str) -> Document | None:
    return db.query(Document).filter(Document.id == document_id, Document.owner_id == owner_id).first()


def list_documents_for_owner(db: Session, owner_id: str, offset: int = 0, limit: int = 50) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.owner_id == owner_id)
        .order_by(Document.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def build_document_detail(db: Session, document: Document) -> DocumentDetail:
    latest_job = (
        db.query(ExtractionJob)
        .filter(ExtractionJob.document_id == document.id)
        .order_by(ExtractionJob.created_at.desc())
        .first()
    )
    return DocumentDetail(
        id=document.id,
        owner_id=document.owner_id,
        original_filename=document.original_filename,
        mime_type=document.mime_type,
        file_size=document.file_size,
        pdf_hash=document.pdf_hash,
        status=document.status,
        page_count=document.page_count,
        created_at=document.created_at,
        updated_at=document.updated_at,
        metadata_record=document.metadata_record,
        pages_count=len(document.pages),
        images_count=len(document.images),
        latest_job=latest_job,
    )


async def upload_and_extract_document(db: Session, upload_file: UploadFile, user: UserContext) -> Document:
    if upload_file.content_type not in {"application/pdf", "application/octet-stream"}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only PDF files are accepted")
    if not upload_file.filename or not upload_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must have a .pdf extension")

    pdf_hash, storage_path, file_size = await save_uploaded_pdf(upload_file, user.id)
    existing_document = (
        db.query(Document)
        .filter(Document.owner_id == user.id, Document.pdf_hash == pdf_hash)
        .first()
    )
    if existing_document:
        return existing_document

    document = Document(
        owner_id=user.id,
        original_filename=upload_file.filename,
        storage_path=str(storage_path),
        mime_type="application/pdf",
        file_size=file_size,
        pdf_hash=pdf_hash,
        status="uploaded",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    extract_document(db, document)
    db.refresh(document)
    return document


def extract_document(db: Session, document: Document) -> None:
    job = ExtractionJob(document_id=document.id, status="running", started_at=datetime.now(UTC))
    document.status = "processing"
    db.add(job)
    db.commit()

    try:
        extracted = extract_pdf_elements(Path(document.storage_path), document.id)

        metadata_payload = extracted["metadata"]
        document.page_count = metadata_payload["page_count"]
        document.metadata_record = DocumentMetadata(document_id=document.id, **metadata_payload)

        for page_payload in extracted["pages"]:
            db.add(DocumentPage(document_id=document.id, **page_payload))

        for image_payload in extracted["images"]:
            db.add(DocumentImage(document_id=document.id, **image_payload))

        upsert_cache(db, document.pdf_hash, "metadata", metadata_payload)
        upsert_cache(db, document.pdf_hash, "pages", {"items": extracted["pages"]})
        upsert_cache(db, document.pdf_hash, "tables", {"items": extracted["tables"]})
        upsert_cache(db, document.pdf_hash, "ocr", extracted["ocr"])
        upsert_cache(db, document.pdf_hash, "knowledge", {"status": "not_indexed", "owner": "knowledge-service"})

        job.status = "completed"
        job.finished_at = datetime.now(UTC)
        document.status = "ready"
        db.commit()
    except Exception as exc:
        db.rollback()
        job = db.merge(job)
        document = db.merge(document)
        job.status = "failed"
        job.error_message = str(exc)
        job.finished_at = datetime.now(UTC)
        document.status = "failed"
        db.commit()
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"PDF extraction failed: {exc}") from exc


def delete_document(db: Session, document: Document) -> None:
    delete_file_if_exists(document.storage_path)
    delete_directory_if_exists(document_images_dir(document.id))
    db.delete(document)
    db.commit()


def get_document_cache(db: Session, document: Document) -> list:
    return list_cache_entries(db, document.pdf_hash)


def render_document_page_previews(document: Document, max_pages: int = 30) -> list[dict]:
    preview_dir = document_page_previews_dir(document.id)
    preview_dir.mkdir(parents=True, exist_ok=True)
    previews: list[dict] = []

    with fitz.open(document.storage_path) as pdf:
        page_limit = min(pdf.page_count, max_pages)
        for page_index in range(page_limit):
            page_number = page_index + 1
            image_path = preview_dir / f"page-{page_number}.png"
            if not image_path.exists():
                page = pdf.load_page(page_index)
                pixmap = page.get_pixmap(matrix=fitz.Matrix(1.4, 1.4), alpha=False)
                pixmap.save(image_path)
            previews.append(
                {
                    "page_number": page_number,
                    "image_url": f"/documents/{document.id}/page-images/{page_number}",
                }
            )

    return previews
