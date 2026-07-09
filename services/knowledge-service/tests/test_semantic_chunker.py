from app.schemas.knowledge import DocumentPage
from app.services.semantic_chunker import split_sentences


def test_split_sentences() -> None:
    page = DocumentPage(id="page-1", page_number=1, text_content="First idea. Second idea? Third idea!")

    sentences = split_sentences(page.text_content)

    assert sentences == ["First idea.", "Second idea?", "Third idea!"]
