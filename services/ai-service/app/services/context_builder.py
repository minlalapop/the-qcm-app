from app.schemas.ai import RetrievalResult


def build_context_block(chunks: list[RetrievalResult]) -> str:
    if not chunks:
        return "Aucun contexte documentaire trouve."

    context_parts: list[str] = []
    for index, chunk in enumerate(chunks, start=1):
        context_parts.append(
            "\n".join(
                [
                    f"[Source {index}]",
                    f"document_id: {chunk.document_id}",
                    f"chunk_id: {chunk.chunk_id}",
                    f"page: {chunk.source_page_number}",
                    f"score: {chunk.score:.4f}",
                    "content:",
                    chunk.content,
                ]
            )
        )

    return "\n\n---\n\n".join(context_parts)


def default_query_for_task(task_type: str) -> str:
    if task_type == "qcm":
        return "notions importantes, definitions, mecanismes, exceptions et points evaluables du cours"
    if task_type == "summary":
        return "idees principales, structure du cours, definitions importantes et synthese"
    if task_type == "mindmap":
        return "concepts centraux, relations hierarchiques, sous-themes et connexions du cours"
    return "contenu pertinent du document"
