from pathlib import Path

import faiss
import numpy as np

from app.core.config import settings


def ensure_vector_store_dirs() -> None:
    settings.document_vector_path.mkdir(parents=True, exist_ok=True)


def document_index_path(document_id: str) -> Path:
    return settings.document_vector_path / f"{document_id}.faiss"


def write_document_index(document_id: str, embeddings: np.ndarray) -> Path:
    ensure_vector_store_dirs()
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    path = document_index_path(document_id)
    faiss.write_index(index, str(path))
    return path


def read_document_index(path: str | Path) -> faiss.Index:
    return faiss.read_index(str(path))


def search_index(path: str | Path, query_embedding: np.ndarray, top_k: int) -> tuple[np.ndarray, np.ndarray]:
    index = read_document_index(path)
    return index.search(query_embedding, top_k)
