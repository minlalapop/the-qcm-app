import json
import re
from typing import Any


def strip_markdown_fence(content: str) -> str:
    clean_content = content.strip()
    fence_match = re.match(r"^```(?:json|mermaid)?\s*(.*?)\s*```$", clean_content, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()
    return clean_content


def parse_json_response(content: str) -> dict[str, Any]:
    clean_content = strip_markdown_fence(content)
    try:
        parsed = json.loads(clean_content)
        return parsed if isinstance(parsed, dict) else {"items": parsed}
    except json.JSONDecodeError:
        start = clean_content.find("{")
        end = clean_content.rfind("}")
        if start >= 0 and end > start:
            parsed = json.loads(clean_content[start : end + 1])
            return parsed if isinstance(parsed, dict) else {"items": parsed}
        raise


def parse_mermaid_response(content: str) -> dict[str, str]:
    clean_content = strip_markdown_fence(content)
    return {"mermaid": clean_content}


def parse_ai_response(task_type: str, content: str, output_format: str | None = None) -> tuple[str, dict[str, Any]]:
    if task_type == "qcm":
        return "json", parse_json_response(content)
    if task_type == "summary":
        try:
            return "json", parse_json_response(content)
        except json.JSONDecodeError:
            clean_content = strip_markdown_fence(content)
            return (
                "text_fallback",
                {
                    "title": "Summary",
                    "sections": [{"heading": "Summary", "content": clean_content, "sources": []}],
                    "key_points": [],
                },
            )
    if task_type == "mindmap" and output_format == "json":
        return "json", parse_json_response(content)
    if task_type == "mindmap":
        return "mermaid", parse_mermaid_response(content)
    return "raw", {"content": content}
