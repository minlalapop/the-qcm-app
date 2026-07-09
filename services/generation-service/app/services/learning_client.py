import httpx

from app.core.config import settings


async def fetch_prompt_context(task_type: str, teacher_id: str, query: str, token: str) -> dict:
    if not settings.LEARNING_SERVICE_URL:
        return {}

    url = f"{settings.LEARNING_SERVICE_URL}/learning/prompt-context"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "task_type": task_type,
        "teacher_id": teacher_id,
        "query": query,
        "top_k": 3,
    }

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, params=params, headers=headers)
    except httpx.HTTPError:
        return {}

    if response.status_code >= 400:
        return {}
    return response.json()
