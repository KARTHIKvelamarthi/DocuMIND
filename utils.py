# utils.py

def format_context(chunks):
    lines = []

    for c in chunks:
        if c["type"] == "heading":
            lines.append(f"\n### {c['text']}\n")
        else:
            lines.append(c["text"])

    return "\n".join(lines)