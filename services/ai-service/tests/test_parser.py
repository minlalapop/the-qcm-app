from app.services.parser import parse_json_response, parse_mermaid_response


def test_parse_json_from_markdown_fence() -> None:
    parsed = parse_json_response('```json\n{"ok": true}\n```')

    assert parsed == {"ok": True}


def test_parse_mermaid_from_markdown_fence() -> None:
    parsed = parse_mermaid_response("```mermaid\nmindmap\n  root((Cours))\n```")

    assert parsed["mermaid"].startswith("mindmap")
