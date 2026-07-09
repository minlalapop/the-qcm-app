import hashlib
import re

import numpy as np

from app.core.config import settings
from app.schemas.knowledge import DocumentPage
from app.services.embedder import embedder


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def split_sentences(text: str) -> list[str]:
    clean_text = normalize_text(text)
    if not clean_text:
        return []
    return [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", clean_text) if sentence.strip()]


def cosine_similarity(left: np.ndarray, right: np.ndarray) -> float:
    return float(np.dot(left, right))


def build_chunk(sentences: list[str], page_number: int, chunk_index: int, reasons: list[str]) -> dict:
    content = " ".join(sentences).strip()
    return {
        "source_page_number": page_number,
        "chunk_index": chunk_index,
        "content": content,
        "content_hash": hashlib.sha256(content.encode("utf-8")).hexdigest(),
        "chunk_metadata": {
            "strategy": "minilm-semantic-breakpoints",
            "sentence_count": len(sentences),
            "chars": len(content),
            "break_reasons": reasons,
        },
    }


def chunk_page(page: DocumentPage, start_index: int = 0) -> list[dict]:
    sentences = split_sentences(page.text_content)
    if not sentences:
        return []

    sentence_embeddings = embedder.encode(sentences)
    chunks: list[dict] = []
    current_sentences: list[str] = []
    current_reasons: list[str] = []
    current_chars = 0
    chunk_index = start_index

    for sentence_index, sentence in enumerate(sentences):
        sentence_chars = len(sentence)
        semantic_break = False
        similarity = 1.0

        if sentence_index > 0:
            similarity = cosine_similarity(sentence_embeddings[sentence_index - 1], sentence_embeddings[sentence_index])
            semantic_break = similarity < settings.SEMANTIC_BREAKPOINT_THRESHOLD

        exceeds_limit = current_sentences and current_chars + sentence_chars + 1 > settings.CHUNK_MAX_CHARS
        enough_context = current_chars >= settings.CHUNK_MIN_CHARS

        if current_sentences and (exceeds_limit or (semantic_break and enough_context)):
            reason = "size_limit" if exceeds_limit else f"semantic_break:{similarity:.3f}"
            current_reasons.append(reason)
            chunks.append(build_chunk(current_sentences, page.page_number, chunk_index, current_reasons))
            chunk_index += 1

            overlap = current_sentences[-settings.CHUNK_OVERLAP_SENTENCES :] if settings.CHUNK_OVERLAP_SENTENCES else []
            current_sentences = list(overlap)
            current_reasons = ["overlap"] if overlap else []
            current_chars = sum(len(item) + 1 for item in current_sentences)

        current_sentences.append(sentence)
        current_chars += sentence_chars + 1

    if current_sentences:
        chunks.append(build_chunk(current_sentences, page.page_number, chunk_index, current_reasons))

    return chunks


def chunk_pages(pages: list[DocumentPage]) -> list[dict]:
    all_chunks: list[dict] = []
    next_index = 0
    for page in sorted(pages, key=lambda item: item.page_number):
        page_chunks = chunk_page(page, start_index=next_index)
        all_chunks.extend(page_chunks)
        next_index += len(page_chunks)
    return all_chunks
