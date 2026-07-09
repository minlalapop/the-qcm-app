from pathlib import Path

import faiss
import numpy as np

from app.core.config import settings


def ensure_vector_store_dirs() -> None:
    settings.feedback_vector_path.mkdir(parents=True, exist_ok=True)


def feedback_index_path() -> Path:
    return settings.feedback_vector_path / "feedback_examples.faiss"


def write_feedback_index(embeddings: np.ndarray) -> Path:
    ensure_vector_store_dirs()
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    path = feedback_index_path()
    faiss.write_index(index, str(path))
    return path


def read_feedback_index() -> faiss.Index | None:
    path = feedback_index_path()
    if not path.exists():
        return None
    return faiss.read_index(str(path))


def search_feedback_index(query_embedding: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray] | None:
    index = read_feedback_index()
    if index is None:
        return None
    return index.search(query_embedding, top_k)
