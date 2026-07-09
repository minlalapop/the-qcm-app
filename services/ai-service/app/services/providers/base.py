from abc import ABC, abstractmethod

from app.schemas.ai import LLMGeneration, LLMMessage


class BaseLLMProvider(ABC):
    name: str

    @abstractmethod
    async def generate(
        self,
        messages: list[LLMMessage],
        model: str | None,
        temperature: float,
        top_p: float,
        max_tokens: int,
    ) -> LLMGeneration:
        raise NotImplementedError
