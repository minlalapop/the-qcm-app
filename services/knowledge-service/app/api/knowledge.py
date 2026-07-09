from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_bearer_token, get_current_user_context
from app.db.session import get_db
from app.schemas.knowledge import (
    IndexDocumentRequest,
    KnowledgeChunkPublic,
    KnowledgeIndexPublic,
    RetrieveRequest,
    RetrieveResponse,
    UserContext,
)
from app.services.document_client import fetch_document_pages
from app.services.knowledge import get_index, index_document_pages, list_chunks, list_indexes, retrieve


router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.post("/documents/{document_id}/index", response_model=KnowledgeIndexPublic)
async def index_document(
    document_id: str,
    payload: IndexDocumentRequest,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    token: str = Depends(get_bearer_token),
) -> KnowledgeIndexPublic:
    pages = await fetch_document_pages(document_id, token)
    return index_document_pages(db, current_user, document_id, pages, force_reindex=payload.force_reindex)


@router.get("/indexes", response_model=list[KnowledgeIndexPublic])
def get_indexes(
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=100),
) -> list[KnowledgeIndexPublic]:
    return list_indexes(db, current_user.id, offset=offset, limit=limit)


@router.get("/documents/{document_id}/chunks", response_model=list[KnowledgeChunkPublic])
def get_document_chunks(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> list[KnowledgeChunkPublic]:
    index = get_index(db, current_user.id, document_id)
    if not index:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Knowledge index not found")
    return list_chunks(db, index)


@router.post("/retrieve", response_model=RetrieveResponse)
def retrieve_chunks(
    payload: RetrieveRequest,
    db: Session = Depends(get_db),
    current_user: UserContext = Depends(get_current_user_context),
) -> RetrieveResponse:
    results = retrieve(
        db=db,
        user=current_user,
        query=payload.query,
        top_k=payload.top_k,
        document_id=payload.document_id,
        page_numbers=payload.page_numbers,
        chunk_ids=payload.chunk_ids,
    )
    return RetrieveResponse(query=payload.query, top_k=payload.top_k, results=results)
