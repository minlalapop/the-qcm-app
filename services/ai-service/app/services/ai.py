import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.ai_request import AIRequest
from app.models.ai_response import AIResponse
from app.schemas.ai import (
    AIRequestBase,
    AIResponsePublic,
    GenerateMindMapRequest,
    GenerateQCMRequest,
    GenerateSummaryRequest,
    LLMMessage,
    RetrievalResult,
    UserContext,
)
from app.services.context_builder import default_query_for_task
from app.services.knowledge_client import retrieve_context
from app.services.parser import parse_ai_response
from app.services.prompt_builder import build_mindmap_messages, build_qcm_messages, build_summary_messages
from app.services.providers.factory import get_llm_provider


JSON_REPAIR_SYSTEM_PROMPT = """Tu es un reparateur JSON strict.
Tu dois retourner uniquement un objet JSON valide, sans Markdown, sans commentaire, sans texte autour."""


def get_usage_value(usage: dict, key: str) -> int | None:
    value = usage.get(key)
    return int(value) if value is not None else None


def create_request_log(
    db: Session,
    user: UserContext,
    payload: AIRequestBase,
    task_type: str,
    provider: str,
    model: str | None,
    prompt: str,
    context_chunks: list[RetrievalResult],
) -> AIRequest:
    request_log = AIRequest(
        owner_id=user.id,
        document_id=payload.document_id,
        provider=provider,
        model=model or "openrouter/auto",
        task_type=task_type,
        prompt=prompt,
        parameters={
            "top_k": payload.top_k,
            "page_numbers": payload.page_numbers,
            "chunk_ids": payload.chunk_ids,
            "max_tokens": payload.max_tokens,
            "extra_instructions": payload.extra_instructions,
        },
        context_payload={"chunks": [chunk.model_dump() for chunk in context_chunks]},
        temperature=payload.temperature,
        top_p=payload.top_p,
        status="pending",
    )
    db.add(request_log)
    db.commit()
    db.refresh(request_log)
    return request_log


async def parse_or_repair_response(
    provider,
    task_type: str,
    content: str,
    output_format: str,
    temperature: float,
    top_p: float,
    max_tokens: int,
) -> tuple[str, dict, str, dict]:
    try:
        parser_type, parsed_response = parse_ai_response(task_type, content, output_format=output_format)
        return parser_type, parsed_response, content, {}
    except json.JSONDecodeError as exc:
        if task_type not in {"qcm", "summary"}:
            raise exc

        schema_hint = (
            '{"questions":[{"question":"...","difficulty":"...","options":[{"label":"A","text":"...","is_correct":true}],'
            '"explanation":"...","source":{"page":1,"chunk_id":"...","citation":"..."}}]}'
            if task_type == "qcm"
            else '{"title":"...","sections":[{"heading":"...","content":"...","sources":[{"page":1}]}],"key_points":["..."]}'
        )
        repair_messages = [
            LLMMessage(role="system", content=JSON_REPAIR_SYSTEM_PROMPT),
            LLMMessage(
                role="user",
                content=(
                    "Corrige ce JSON invalide. Ne change pas le sens du contenu. "
                    f"Respecte exactement cette forme: {schema_hint}\n\nJSON invalide:\n{content}"
                ),
            ),
        ]
        repaired = await provider.generate(
            messages=repair_messages,
            model=None,
            temperature=0.0,
            top_p=top_p,
            max_tokens=max_tokens,
        )
        try:
            parser_type, parsed_response = parse_ai_response(task_type, repaired.content, output_format=output_format)
        except json.JSONDecodeError as repair_exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI returned invalid JSON twice. Please retry generation with fewer sources or fewer questions.",
            ) from repair_exc
        return f"{parser_type}_repaired", parsed_response, repaired.content, repaired.usage


async def run_ai_generation(
    db: Session,
    user: UserContext,
    token: str,
    payload: GenerateQCMRequest | GenerateSummaryRequest | GenerateMindMapRequest,
    task_type: str,
) -> AIResponsePublic:
    query = payload.query or default_query_for_task(task_type)
    context_chunks = await retrieve_context(
        payload.document_id,
        query,
        payload.top_k,
        token,
        page_numbers=payload.page_numbers,
        chunk_ids=payload.chunk_ids,
    )
    if not context_chunks:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No context chunks returned")

    if task_type == "qcm":
        messages = build_qcm_messages(payload, context_chunks)
        output_format = "json"
    elif task_type == "summary":
        messages = build_summary_messages(payload, context_chunks)
        output_format = "json"
    else:
        messages = build_mindmap_messages(payload, context_chunks)
        output_format = payload.output_format if isinstance(payload, GenerateMindMapRequest) else "mermaid"

    provider = get_llm_provider()
    model = None
    prompt = "\n\n".join(message.content for message in messages if isinstance(message, LLMMessage))
    request_log = create_request_log(db, user, payload, task_type, provider.name, model, prompt, context_chunks)

    try:
        generation = await provider.generate(
            messages=messages,
            model=model,
            temperature=payload.temperature,
            top_p=payload.top_p,
            max_tokens=payload.max_tokens,
        )
        parser_type, parsed_response, parsed_content, repair_usage = await parse_or_repair_response(
            provider,
            task_type,
            generation.content,
            output_format,
            payload.temperature,
            payload.top_p,
            payload.max_tokens,
        )

        request_log.status = "completed"
        request_log.prompt_tokens = get_usage_value(generation.usage, "prompt_tokens")
        request_log.completion_tokens = get_usage_value(generation.usage, "completion_tokens")
        request_log.total_tokens = get_usage_value(generation.usage, "total_tokens")
        response_log = AIResponse(
            request_id=request_log.id,
            raw_response=parsed_content,
            parsed_response=parsed_response,
            parser_type=parser_type,
        )
        db.add(response_log)
        db.commit()

        return AIResponsePublic(
            request_id=request_log.id,
            task_type=task_type,
            provider=generation.provider,
            model=generation.model,
            raw_response=parsed_content,
            parsed_response=parsed_response,
            parser_type=parser_type,
            context=context_chunks,
        )
    except Exception as exc:
        db.rollback()
        request_log = db.merge(request_log)
        request_log.status = "failed"
        request_log.error_message = str(exc)
        db.commit()
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"AI generation failed: {exc}") from exc
