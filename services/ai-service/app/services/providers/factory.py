from fastapi import HTTPException, status

from app.core.config import settings
from app.services.providers.base import BaseLLMProvider
from app.services.providers.openrouter import OpenRouterProvider


def get_llm_provider(provider_name: str | None = None) -> BaseLLMProvider:
    provider = provider_name or settings.DEFAULT_LLM_PROVIDER
    if provider == "openrouter":
        return OpenRouterProvider()

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown LLM provider: {provider}")
