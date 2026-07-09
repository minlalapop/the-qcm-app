import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.learning import QualityMetricSource, QuestionFeedbackSource


async def fetch_qcm_feedback(qcm_id: str, token: str) -> list[QuestionFeedbackSource]:
    url = f"{settings.EVALUATION_SERVICE_URL}/evaluation/qcms/{qcm_id}/questions/feedback"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url, headers=headers)

    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Evaluation Service error: {response.text}")

    return [QuestionFeedbackSource(**item) for item in response.json()]


async def fetch_qcm_metrics(qcm_id: str, token: str) -> QualityMetricSource:
    url = f"{settings.EVALUATION_SERVICE_URL}/evaluation/qcms/{qcm_id}/metrics"
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.get(url, headers=headers)

    if response.status_code >= 400:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Evaluation Service error: {response.text}")

    return QualityMetricSource(**response.json())
