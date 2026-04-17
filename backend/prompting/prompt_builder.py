# backend/prompting/prompt_builder.py

class PromptBuilder:

    def build_single(self, query: str, context: str, previous_summary: str = None) -> str:
        prev_block = f"""
Previous context (for reference, use only if relevant):
{previous_summary}
""" if previous_summary else ""

        return f"""You are a research assistant.

Rules:
- Answer ONLY using the provided context.
- Do NOT add external knowledge.
- Only answer using the provided context. If insufficient information is available, provide the best possible answer based strictly on the given context without explicitly stating that information is missing.
- Be clear and concise.
{prev_block}
Context:
{context}

Question:
{query}

Answer:"""

    def build_dual(self, query: str, context_a: str, context_b: str, previous_summary: str = None) -> str:
        prev_block = f"""
Previous context (for reference, use only if relevant):
{previous_summary}
""" if previous_summary else ""

        return f"""You are a research assistant working with TWO separate documents.

Rules:
- Treat both documents independently.
- Do NOT mix information between documents.
- Use ONLY the given context.
- Do NOT add external knowledge.
- Only answer using the provided context. If insufficient information is available, provide the best possible answer based strictly on the given context without explicitly stating that information is missing.
{prev_block}
--- DOCUMENT 1 ---
{context_a}

--- DOCUMENT 2 ---
{context_b}

Question:
{query}

Answer in this exact format:

[Doc1 Answer]
<answer using only Document 1>

[Doc2 Answer]
<answer using only Document 2>

[Comparison]
<similarities, differences, which is more detailed>"""
