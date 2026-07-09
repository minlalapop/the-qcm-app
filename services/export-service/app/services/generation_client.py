from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings


class GenerationClient:
    def __init__(self, token: str):
        self.token = token

    async def _get(self, path: str) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.token}"}
        url = f"{settings.GENERATION_SERVICE_URL.rstrip('/')}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)

        if response.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generation resource not found")
        if response.status_code >= 400:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=response.text)
        return response.json()

    async def get_qcm(self, qcm_id: str) -> dict[str, Any]:
        return await self._get(f"/generation/qcms/{qcm_id}")

    async def get_summary(self, summary_id: str) -> dict[str, Any]:
        return await self._get(f"/generation/summaries/{summary_id}")

    async def get_mindmap(self, mindmap_id: str) -> dict[str, Any]:
        return await self._get(f"/generation/mindmaps/{mindmap_id}")
