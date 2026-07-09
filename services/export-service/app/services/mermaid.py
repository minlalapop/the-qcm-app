from typing import Any


def mindmap_to_mermaid(mindmap: dict[str, Any]) -> str:
    content = mindmap.get("mermaid_content")
    if content:
        return str(content).strip()

    title = mindmap.get("title") or "MindMap"
    payload = mindmap.get("json_content") or {}
    lines = ["mindmap", f"  root(({_clean_node(title)}))"]

    def walk(node: Any, depth: int) -> None:
        if isinstance(node, dict):
            label = node.get("label") or node.get("title") or node.get("name")
            if label:
                lines.append(f"{'  ' * depth}{_clean_node(str(label))}")
            children = node.get("children") or node.get("nodes") or []
            for child in children:
                walk(child, depth + 1)
        elif isinstance(node, list):
            for child in node:
                walk(child, depth)

    walk(payload.get("children") or payload.get("nodes") or [], 2)
    return "\n".join(lines)


def _clean_node(value: str) -> str:
    return value.replace("\n", " ").replace("\r", " ").strip()[:120] or "item"
