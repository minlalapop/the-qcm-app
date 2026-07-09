import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.ai import RetrievalResult


async def retrieve_context(
    document_id: str,
    query: str,
    top_k: int,
    token: str,
    page_numbers: list[int] | None = None,
    chunk_ids: list[str] | None = None,
) -> list[RetrievalResult]:
    url = f"{settings.KNOWLEDGE_SERVICE_URL}/knowledge/retrieve"
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "document_id": document_id,
        "query": query,
        "top_k": top_k,
        "page_numbers": page_numbers or [],
        "chunk_ids": chunk_ids or [],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(url, json=payload, headers=headers)

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Knowledge index not found. Index the document before using AI Service.",
        )
    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Knowledge Service error: {response.text}",
        )

    data = response.json()
    return [RetrievalResult(**item) for item in data.get("results", [])]
