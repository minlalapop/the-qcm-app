from app.schemas.generation import SourceSelection


def source_selection_to_prompt(selection: SourceSelection, custom_rules: dict | None = None) -> str:
    parts = [
        "Respecter strictement la selection de sources demandee par l'utilisateur.",
        f"Documents selectionnes: {', '.join(selection.document_ids)}.",
    ]
    if selection.page_numbers:
        parts.append(f"Pages a privilegier: {', '.join(str(page) for page in selection.page_numbers)}.")
    if selection.chunk_ids:
        parts.append(f"Chunks a privilegier: {', '.join(selection.chunk_ids)}.")
    if selection.focus_text:
        parts.append(f"Focus utilisateur: {selection.focus_text}.")
    if custom_rules:
        parts.append(f"Regles personnalisees: {custom_rules}.")
    return "\n".join(parts)


def distribute_questions(total_questions: int, document_count: int) -> list[int]:
    base = total_questions // document_count
    remainder = total_questions % document_count
    return [base + (1 if index < remainder else 0) for index in range(document_count)]
