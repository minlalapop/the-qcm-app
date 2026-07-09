from pathlib import Path

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.knowledge_index import KnowledgeIndex
from app.models.retrieval_log import RetrievalLog
from app.schemas.knowledge import DocumentPage, RetrievalResult, UserContext
from app.services.embedder import embedder
from app.services.semantic_chunker import chunk_pages
from app.services.vector_store import search_index, write_document_index


def get_index(db: Session, owner_id: str, document_id: str) -> KnowledgeIndex | None:
    return (
        db.query(KnowledgeIndex)
        .filter(KnowledgeIndex.owner_id == owner_id, KnowledgeIndex.document_id == document_id)
        .first()
    )


def list_indexes(db: Session, owner_id: str, offset: int = 0, limit: int = 50) -> list[KnowledgeIndex]:
    return (
        db.query(KnowledgeIndex)
        .filter(KnowledgeIndex.owner_id == owner_id)
        .order_by(KnowledgeIndex.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


def list_chunks(db: Session, index: KnowledgeIndex) -> list[KnowledgeChunk]:
    return db.query(KnowledgeChunk).filter(KnowledgeChunk.index_id == index.id).order_by(KnowledgeChunk.chunk_index).all()


def index_document_pages(
    db: Session,
    user: UserContext,
    document_id: str,
    pages: list[DocumentPage],
    force_reindex: bool = False,
) -> KnowledgeIndex:
    existing_index = get_index(db, user.id, document_id)
    if existing_index and existing_index.status == "ready" and not force_reindex:
        return existing_index

    if existing_index and force_reindex:
        db.delete(existing_index)
        db.commit()

    chunks = chunk_pages(pages)
    if not chunks:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No text chunks generated")

    chunk_texts = [chunk["content"] for chunk in chunks]
    embeddings = embedder.encode(chunk_texts)
    vector_store_path = write_document_index(document_id, embeddings)

    knowledge_index = KnowledgeIndex(
        owner_id=user.id,
        document_id=document_id,
        embedding_model=settings.EMBEDDING_MODEL_NAME,
        vector_store_type="faiss",
        vector_store_path=str(vector_store_path),
        dimension=embeddings.shape[1],
        chunks_count=len(chunks),
        status="ready",
    )
    db.add(knowledge_index)
    db.flush()

    for vector_id, chunk in enumerate(chunks):
        db.add(
            KnowledgeChunk(
                index_id=knowledge_index.id,
                owner_id=user.id,
                document_id=document_id,
                source_page_number=chunk["source_page_number"],
                chunk_index=chunk["chunk_index"],
                vector_id=vector_id,
                content=chunk["content"],
                content_hash=chunk["content_hash"],
                chunk_metadata=chunk["chunk_metadata"],
            )
        )

    db.commit()
    db.refresh(knowledge_index)
    return knowledge_index


def retrieve(
    db: Session,
    user: UserContext,
    query: str,
    top_k: int,
    document_id: str | None = None,
    page_numbers: list[int] | None = None,
    chunk_ids: list[str] | None = None,
) -> list[RetrievalResult]:
    indexes = [get_index(db, user.id, document_id)] if document_id else list_indexes(db, user.id, limit=100)
    indexes = [index for index in indexes if index and index.status == "ready" and Path(index.vector_store_path).exists()]
    if not indexes:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No ready knowledge index found")

    query_embedding = embedder.encode([query])
    all_results: list[RetrievalResult] = []
    selected_pages = set(page_numbers or [])
    selected_chunk_ids = set(chunk_ids or [])
    candidate_k = min(max(top_k * 5, top_k), 100) if selected_pages or selected_chunk_ids else top_k

    for index in indexes:
        distances, vector_ids = search_index(index.vector_store_path, query_embedding, candidate_k)
        chunks_by_vector_id = {chunk.vector_id: chunk for chunk in list_chunks(db, index)}

        for score, vector_id in zip(distances[0].tolist(), vector_ids[0].tolist(), strict=False):
            if vector_id < 0 or vector_id not in chunks_by_vector_id:
                continue
            chunk = chunks_by_vector_id[vector_id]
            if selected_pages and chunk.source_page_number not in selected_pages:
                continue
            if selected_chunk_ids and chunk.id not in selected_chunk_ids:
                continue
            all_results.append(
                RetrievalResult(
                    document_id=chunk.document_id,
                    chunk_id=chunk.id,
                    chunk_index=chunk.chunk_index,
                    source_page_number=chunk.source_page_number,
                    score=float(score),
                    content=chunk.content,
                    metadata=chunk.chunk_metadata,
                )
            )

    all_results.sort(key=lambda item: item.score, reverse=True)
    selected_results = all_results[:top_k]

    db.add(
        RetrievalLog(
            owner_id=user.id,
            document_id=document_id,
            query=query,
            top_k=top_k,
            results={
                "items": [result.model_dump() for result in selected_results],
                "filters": {
                    "page_numbers": sorted(selected_pages),
                    "chunk_ids": sorted(selected_chunk_ids),
                },
            },
        )
    )
    db.commit()
    return selected_results
