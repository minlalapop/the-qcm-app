import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.knowledge import DocumentPage


async def fetch_document_pages(document_id: str, token: str) -> list[DocumentPage]:
    url = f"{settings.DOCUMENT_SERVICE_URL}/documents/{document_id}/pages"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url, headers=headers)

    if response.status_code == status.HTTP_404_NOT_FOUND:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    if response.status_code >= 400:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Document Service error: {response.text}",
        )

    return [DocumentPage(**item) for item in response.json()]
