# backend/utils/formatter.py
# Formats retrieved chunks into a plain-text context string for the prompt.

from typing import List


def format_context(chunks: List[dict]) -> str:
    lines = []
    for c in chunks:
        if c["type"] == "heading":
            lines.append(f"\n### {c['text']}\n")
        else:
            lines.append(c["text"])
    return "\n".join(lines)


def format_visuals(chunks: List[dict]) -> str:
    """Return a human-readable summary of images and tables attached to chunks."""
    lines = []
    for c in chunks:
        images = c.get("images", [])
        tables = c.get("tables", [])
        if images or tables:
            lines.append(f"\n[Page {c['page']} | Chunk ID {c['id']}]")
            for img in images:
                lines.append(f"  📷 Image: {img['path']}")
            for tbl in tables:
                lines.append(f"  📊 Table ({len(tbl['data'])} rows):")
                for row in tbl["data"][:5]:   # preview first 5 rows
                    lines.append(f"       {row}")
    return "\n".join(lines) if lines else ""
