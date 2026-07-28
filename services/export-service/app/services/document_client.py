from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class DocumentClient:
    def __init__(self, token: str):
        self.token = token

    async def get_document(self, document_id: str) -> dict[str, Any] | None:
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{settings.DOCUMENT_SERVICE_URL.rstrip('/')}/documents/{document_id}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code == status.HTTP_404_NOT_FOUND:
            return None
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=response.text)
        return response.json()

    async def get_document_titles(self, document_ids: list[str]) -> dict[str, str]:
        titles: dict[str, str] = {}
        for document_id in document_ids:
            document = await self.get_document(document_id)
            if document:
                title = document.get("original_filename") or document.get("title")
                if title:
                    titles[document_id] = title
        return titles
