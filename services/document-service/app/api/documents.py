from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user_context
from app.db.session import get_db
from app.schemas.document import (
    DocumentCachePublic,
    DocumentDetail,
    DocumentPagePublic,
    DocumentSummary,
    UserContext,
)
from app.services.documents import (
    build_document_detail,
    delete_document,
    get_document_cache,
    get_document_for_owner,
    list_documents_for_owner,
    render_document_page_previews,
    upload_and_extract_document,
)
from app.services.storage import document_page_previews_dir


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentDetail, status_code=status.HTTP_201_CREATED)
async def upload_pdf(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> DocumentDetail:
    document = await upload_and_extract_document(db, file, current_user)
    return build_document_detail(db, document)


@router.get("", response_model=list[DocumentSummary])
def list_pdfs(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[DocumentSummary]:
    return list_documents_for_owner(db, current_user.id, offset=offset, limit=limit)


@router.get("/{document_id}", response_model=DocumentDetail)
def get_pdf(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> DocumentDetail:
    document = get_document_for_owner(db, document_id, current_user.id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return build_document_detail(db, document)


@router.get("/{document_id}/file")
def stream_pdf_file(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> FileResponse:
    document = get_document_for_owner(db, document_id, current_user.id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    pdf_path = Path(document.storage_path)
    if not pdf_path.exists() or not pdf_path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF file not found")

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=document.original_filename,
        content_disposition_type="inline",
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_pdf(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> None:
    document = get_document_for_owner(db, document_id, current_user.id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    delete_document(db, document)


@router.get("/{document_id}/pages", response_model=list[DocumentPagePublic])
def list_pdf_pages(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> list[DocumentPagePublic]:
    document = get_document_for_owner(db, document_id, current_user.id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return sorted(document.pages, key=lambda page: page.page_number)


@router.get("/{document_id}/page-images")
def list_pdf_page_images(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> list[dict]:
    document = get_document_for_owner(db, document_id, current_user.id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return render_document_page_previews(document)


@router.get("/{document_id}/page-images/{page_number}")
def get_pdf_page_image(
    document_id: str,
    page_number: int,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> FileResponse:
    document = get_document_for_owner(db, document_id, current_user.id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    render_document_page_previews(document, max_pages=max(page_number, 1))
    image_path = document_page_previews_dir(document.id) / f"page-{page_number}.png"
    if not image_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PDF page image not found")
    return FileResponse(image_path, media_type="image/png")


@router.get("/{document_id}/cache", response_model=list[DocumentCachePublic])
def list_pdf_cache(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> list[DocumentCachePublic]:
    document = get_document_for_owner(db, document_id, current_user.id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return get_document_cache(db, document)
