import hashlib
import re
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.answer import Answer
from app.models.generation_history import GenerationHistory
from app.models.mindmap import MindMap
from app.models.qcm import QCM
from app.models.qcm_settings import QCMSettings
from app.models.question import Question
from app.models.summary import Summary
from app.schemas.generation import (
    GenerateMindMapRequest,
    GenerateQCMRequest,
    GenerateSummaryRequest,
    QCMUpdate,
    QuestionUpdate,
    UserContext,
)
from app.services.ai_client import call_ai
from app.services.learning_client import fetch_prompt_context
from app.services.source_selection import distribute_questions, source_selection_to_prompt


def hash_text(text: str) -> str:
    return hashlib.sha256(text.strip().lower().encode("utf-8")).hexdigest()


def get_qcm_for_owner(db: Session, qcm_id: str, owner_id: str) -> QCM | None:
    return db.query(QCM).filter(QCM.id == qcm_id, QCM.owner_id == owner_id).first()


def list_qcms_for_owner(db: Session, owner_id: str, offset: int = 0, limit: int = 50) -> list[QCM]:
    return db.query(QCM).filter(QCM.owner_id == owner_id).order_by(QCM.created_at.desc()).offset(offset).limit(limit).all()


def get_question_for_owner(db: Session, qcm_id: str, question_id: str, owner_id: str) -> Question | None:
    qcm = get_qcm_for_owner(db, qcm_id, owner_id)
    if not qcm:
        return None
    return db.query(Question).filter(Question.qcm_id == qcm_id, Question.id == question_id).first()


def build_ai_payload(document_id: str, payload, number_of_questions: int | None = None, learning_context: dict | None = None) -> dict:
    custom_rules = dict(payload.custom_rules or {})
    if learning_context:
        custom_rules["learning_context"] = learning_context
    extra_instructions = source_selection_to_prompt(payload.source_selection, custom_rules)
    ai_payload = {
        "document_id": document_id,
        "query": payload.source_selection.focus_text,
        "top_k": payload.top_k,
        "page_numbers": payload.source_selection.page_numbers,
        "chunk_ids": payload.source_selection.chunk_ids,
        "temperature": payload.temperature,
        "top_p": payload.top_p,
        "max_tokens": payload.max_tokens,
        "extra_instructions": extra_instructions,
    }
    if number_of_questions is not None:
        ai_payload["number_of_questions"] = number_of_questions
        ai_payload["number_of_options"] = payload.number_of_options
        ai_payload["difficulty"] = payload.difficulty
    return ai_payload


def extract_questions(ai_response: dict) -> list[dict[str, Any]]:
    parsed = ai_response.get("parsed_response") or {}
    questions = parsed.get("questions") or []
    if not isinstance(questions, list):
        return []
    return questions


def clean_summary_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r", "\n").strip()
    json_tail = re.search(r"(?im)^\s*summary\s*\n\s*\{", text)
    if json_tail:
        text = text[: json_tail.start()].strip()
    json_start = text.find("{")
    if json_start == 0:
        return ""
    if json_start > 0 and '"sections"' in text[json_start:]:
        text = text[:json_start].strip()

    cleaned_lines: list[str] = []
    for raw_line in text.splitlines():
        line = " ".join(raw_line.strip().split())
        if not line or line in {"*", "-", "•"}:
            continue
        if line.lower() == "summary":
            continue
        if line.startswith("```"):
            continue
        cleaned_lines.append(line)
    return "\n".join(cleaned_lines).strip()


def normalize_summary_section(section: dict[str, Any], fallback_heading: str) -> dict[str, Any] | None:
    heading = clean_summary_text(section.get("heading") or section.get("title") or fallback_heading).split("\n")[0]
    content = clean_summary_text(section.get("content") or section.get("summary") or section.get("text"))
    if len(content.split()) < 18:
        return None

    sources = []
    raw_sources = section.get("sources") or []
    if isinstance(raw_sources, dict):
        raw_sources = [raw_sources]
    if isinstance(raw_sources, list):
        for source in raw_sources:
            if isinstance(source, dict) and source.get("page"):
                sources.append({"page": source.get("page")})

    return {
        "heading": heading or fallback_heading,
        "content": content,
        "sources": sources,
    }


async def generate_qcm(db: Session, user: UserContext, token: str, payload: GenerateQCMRequest) -> QCM:
    document_ids = payload.source_selection.document_ids
    question_distribution = distribute_questions(payload.number_of_questions, len(document_ids))
    generated_questions: list[dict[str, Any]] = []
    ai_request_ids: list[str] = []
    raw_payloads: list[dict] = []
    learning_context = await fetch_prompt_context("qcm", user.id, payload.source_selection.focus_text or payload.title, token)

    for document_id, question_count in zip(document_ids, question_distribution, strict=True):
        if question_count <= 0:
            continue
        ai_response = await call_ai("/ai/qcm", build_ai_payload(document_id, payload, question_count, learning_context), token)
        ai_request_ids.append(ai_response["request_id"])
        raw_payloads.append(ai_response)
        for question in extract_questions(ai_response):
            question["source_document_id"] = document_id
            generated_questions.append(question)

    if not generated_questions:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No QCM questions generated")

    qcm = QCM(
        owner_id=user.id,
        title=payload.title,
        document_ids=document_ids,
        status="draft",
        difficulty=payload.difficulty,
        source_selection=payload.source_selection.model_dump(),
        ai_request_ids=ai_request_ids,
    )
    db.add(qcm)
    db.flush()

    qcm.settings = QCMSettings(
        qcm_id=qcm.id,
        number_of_questions=payload.number_of_questions,
        number_of_options=payload.number_of_options,
        difficulty=payload.difficulty,
        source_selection=payload.source_selection.model_dump(),
        duplication_check=payload.duplication_check,
        custom_rules=payload.custom_rules,
    )

    seen_hashes: set[str] = set()
    order_index = 1
    for question_payload in generated_questions:
        question_text = str(question_payload.get("question") or "").strip()
        if not question_text:
            continue
        question_hash = hash_text(question_text)
        if payload.duplication_check and question_hash in seen_hashes:
            continue
        seen_hashes.add(question_hash)

        source_payload = question_payload.get("source") or {}
        question = Question(
            qcm_id=qcm.id,
            order_index=order_index,
            question_text=question_text,
            explanation=question_payload.get("explanation"),
            difficulty=question_payload.get("difficulty") or payload.difficulty,
            source_document_id=question_payload.get("source_document_id"),
            source_page=source_payload.get("page"),
            source_chunk_id=source_payload.get("chunk_id"),
            citation=source_payload.get("citation"),
            question_hash=question_hash,
        )
        db.add(question)
        db.flush()

        options = question_payload.get("options") or []
        for answer_index, option in enumerate(options):
            is_correct = bool(option.get("is_correct"))
            db.add(
                Answer(
                    question_id=question.id,
                    order_index=answer_index,
                    label=str(option.get("label") or chr(65 + answer_index)),
                    answer_text=str(option.get("text") or ""),
                    is_correct=is_correct,
                    is_distractor=not is_correct,
                )
            )
        order_index += 1

    history = GenerationHistory(
        owner_id=user.id,
        resource_type="qcm",
        resource_id=qcm.id,
        document_ids=document_ids,
        ai_request_ids=ai_request_ids,
        model=None,
        parameters=payload.model_dump(),
        generated_payload={"ai_responses": raw_payloads},
    )
    db.add(history)
    db.commit()
    db.refresh(qcm)
    return qcm


async def generate_summary(db: Session, user: UserContext, token: str, payload: GenerateSummaryRequest) -> Summary:
    ai_request_ids: list[str] = []
    sections: list[dict] = []
    key_points: list[str] = []
    learning_context = await fetch_prompt_context("summary", user.id, payload.source_selection.focus_text or payload.title, token)

    for document_id in payload.source_selection.document_ids:
        ai_payload = build_ai_payload(document_id, payload, learning_context=learning_context)
        ai_payload["style"] = payload.style
        ai_payload["max_sections"] = max(1, payload.max_sections // len(payload.source_selection.document_ids))
        ai_response = await call_ai("/ai/summary", ai_payload, token)
        ai_request_ids.append(ai_response["request_id"])
        parsed = ai_response.get("parsed_response") or {}
        parsed_sections = parsed.get("sections") or []
        if isinstance(parsed_sections, list):
            for item in parsed_sections:
                if isinstance(item, dict):
                    normalized = normalize_summary_section(item, payload.title)
                    if normalized:
                        sections.append(normalized)
        elif isinstance(parsed_sections, dict):
            normalized = normalize_summary_section(parsed_sections, payload.title)
            if normalized:
                sections.append(normalized)
        elif parsed.get("content"):
            normalized = normalize_summary_section(
                {"heading": parsed.get("title") or payload.title, "content": parsed["content"], "sources": []},
                payload.title,
            )
            if normalized:
                sections.append(normalized)

        if not sections and ai_response.get("raw_response"):
            normalized = normalize_summary_section(
                {"heading": payload.title, "content": ai_response["raw_response"], "sources": []},
                payload.title,
            )
            if normalized:
                sections.append(normalized)

        parsed_key_points = parsed.get("key_points") or []
        if isinstance(parsed_key_points, list):
            key_points.extend(clean_summary_text(item) for item in parsed_key_points if clean_summary_text(item))

    if not sections:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="AI did not return a usable summary. Try again with fewer pages or a more precise instruction.",
        )

    structured_payload = {
        "title": payload.title,
        "sections": sections[: payload.max_sections],
        "key_points": key_points[:12],
    }
    content_parts = []
    for section in structured_payload["sections"]:
        heading = section.get("heading") or "Section"
        content = section.get("content") or ""
        content_parts.append(f"{heading}\n{content}".strip())

    summary = Summary(
        owner_id=user.id,
        title=payload.title,
        document_ids=payload.source_selection.document_ids,
        content="\n\n".join(content_parts),
        structured_payload=structured_payload,
        source_selection=payload.source_selection.model_dump(),
        ai_request_ids=ai_request_ids,
    )
    db.add(summary)
    db.flush()
    db.add(
        GenerationHistory(
            owner_id=user.id,
            resource_type="summary",
            resource_id=summary.id,
            document_ids=payload.source_selection.document_ids,
            ai_request_ids=ai_request_ids,
            model=None,
            parameters=payload.model_dump(),
            generated_payload=structured_payload,
        )
    )
    db.commit()
    db.refresh(summary)
    return summary


async def generate_mindmap(db: Session, user: UserContext, token: str, payload: GenerateMindMapRequest) -> MindMap:
    primary_document_id = payload.source_selection.document_ids[0]
    learning_context = await fetch_prompt_context("mindmap", user.id, payload.source_selection.focus_text or payload.title, token)
    ai_payload = build_ai_payload(primary_document_id, payload, learning_context=learning_context)
    ai_payload["output_format"] = payload.output_format
    ai_response = await call_ai("/ai/mindmap", ai_payload, token)
    parsed = ai_response.get("parsed_response") or {}

    mindmap = MindMap(
        owner_id=user.id,
        title=payload.title,
        document_ids=payload.source_selection.document_ids,
        output_format=payload.output_format,
        mermaid_content=parsed.get("mermaid"),
        json_content=parsed if payload.output_format == "json" else {},
        source_selection=payload.source_selection.model_dump(),
        ai_request_ids=[ai_response["request_id"]],
    )
    db.add(mindmap)
    db.flush()
    db.add(
        GenerationHistory(
            owner_id=user.id,
            resource_type="mindmap",
            resource_id=mindmap.id,
            document_ids=payload.source_selection.document_ids,
            ai_request_ids=[ai_response["request_id"]],
            model=None,
            parameters=payload.model_dump(),
            generated_payload=parsed,
        )
    )
    db.commit()
    db.refresh(mindmap)
    return mindmap


def update_qcm(db: Session, qcm: QCM, payload: QCMUpdate) -> QCM:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(qcm, field, value)
    db.commit()
    db.refresh(qcm)
    return qcm


def update_question(db: Session, question: Question, payload: QuestionUpdate) -> Question:
    update_data = payload.model_dump(exclude_unset=True)
    answers_payload = update_data.pop("answers", None)
    for field, value in update_data.items():
        setattr(question, field, value)
    if question.question_text:
        question.question_hash = hash_text(question.question_text)

    if answers_payload is not None:
        for answer, answer_payload in zip(sorted(question.answers, key=lambda item: item.order_index), answers_payload, strict=False):
            for field, value in answer_payload.items():
                if value is None:
                    continue
                if field == "answer_text":
                    answer.answer_text = value
                else:
                    setattr(answer, field, value)
            answer.is_distractor = not answer.is_correct

    db.commit()
    db.refresh(question)
    return question
