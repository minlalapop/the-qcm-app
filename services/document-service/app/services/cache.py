from sqlalchemy.orm import Session

from app.models.document_cache import DocumentCache


def get_cache(db: Session, pdf_hash: str, cache_type: str) -> DocumentCache | None:
    return (
        db.query(DocumentCache)
        .filter(DocumentCache.pdf_hash == pdf_hash, DocumentCache.cache_type == cache_type)
        .first()
    )


def upsert_cache(db: Session, pdf_hash: str, cache_type: str, payload: dict) -> DocumentCache:
    cache_entry = get_cache(db, pdf_hash, cache_type)
    if cache_entry:
        cache_entry.payload = payload
    else:
        cache_entry = DocumentCache(pdf_hash=pdf_hash, cache_type=cache_type, payload=payload)
        db.add(cache_entry)

    db.flush()
    return cache_entry


def list_cache_entries(db: Session, pdf_hash: str) -> list[DocumentCache]:
    return db.query(DocumentCache).filter(DocumentCache.pdf_hash == pdf_hash).all()
