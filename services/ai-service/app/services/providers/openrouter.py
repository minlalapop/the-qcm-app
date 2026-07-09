import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.ai import LLMGeneration, LLMMessage
from app.services.providers.base import BaseLLMProvider


class OpenRouterProvider(BaseLLMProvider):
    name = "openrouter"
    auto_router_model = "openrouter/auto"

    async def generate(
        self,
        messages: list[LLMMessage],
        model: str | None,
        temperature: float,
        top_p: float,
        max_tokens: int,
    ) -> LLMGeneration:
        if not settings.OPENROUTER_API_KEY:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="OPENROUTER_API_KEY is not configured",
            )

        routed_model = model or self.auto_router_model
        payload = {
            "model": routed_model,
            "messages": [message.model_dump() for message in messages],
            "temperature": temperature,
            "top_p": top_p,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": settings.OPENROUTER_HTTP_REFERER,
            "X-Title": settings.OPENROUTER_APP_TITLE,
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{settings.OPENROUTER_BASE_URL}/chat/completions",
                json=payload,
                headers=headers,
            )

        if response.status_code >= 400:
            error_detail = build_openrouter_error_detail(response)
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=error_detail,
            )

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return LLMGeneration(
            content=content,
            model=data.get("model", routed_model),
            provider=self.name,
            usage=data.get("usage") or {},
            raw=data,
        )


def build_openrouter_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
        message = str(payload.get("error", {}).get("message") or payload.get("message") or response.text)
    except ValueError:
        message = response.text

    if "Insufficient credits" in message:
        return "OpenRouter refuse la generation: le compte lie a cette cle API n'a pas de credits disponibles."

    if "User not found" in message:
        return "OpenRouter refuse la generation: la cle API ne correspond a aucun compte OpenRouter valide. Verifie OPENROUTER_API_KEY dans .env."

    return f"OpenRouter error: {message}"
