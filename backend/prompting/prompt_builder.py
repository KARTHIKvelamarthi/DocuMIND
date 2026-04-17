# backend/prompting/prompt_builder.py
# Identical behaviour to base_pipeline/prompt_builder.py.

class PromptBuilder:

    def build_single(self, query: str, context: str, previous_summary: str = None) -> str:
        if previous_summary:
            return f"""
You are a research assistant.

You MUST follow these rules:
- Answer ONLY using the provided context
- Do NOT add external knowledge
- If the answer is not present, say "Not found in the document"

Context:
{context}

Previous context (for reference, may or may not be relevant):
{previous_summary}

Question:
{query}

Instructions:
- If the question asks for explanation → expand using context
- If it asks for drawbacks → identify limitations from context
- If it is a follow-up → use previous context only if relevant

Answer clearly and concisely.
"""
        return f"""
You are a research assistant.

You MUST follow these rules:
- Answer ONLY using the provided context
- Do NOT add external knowledge
- If the answer is not present, say "Not found in the document"

Context:
{context}

Question:
{query}

Answer clearly using only the context.
"""

    def build_dual(self, query: str, context_a: str, context_b: str, previous_summary: str = None) -> str:
        return f"""
You are a research assistant working with TWO separate documents.

You MUST follow these rules:
- Treat both documents independently
- Do NOT mix information between documents
- Use ONLY the given context
- Do NOT add external knowledge
- If a document does not contain the answer, say "Not found in that document"

--- DOCUMENT 1 ---
{context_a}

--- DOCUMENT 2 ---
{context_b}

Previous context (for reference, may or may not be relevant):
{previous_summary if previous_summary else "None"}

Question:
{query}

Instructions:
1. First, answer using ONLY Document 1 → label as [Doc1 Answer]
2. Then, answer using ONLY Document 2 → label as [Doc2 Answer]
3. Then compare both → label as [Comparison]

For comparison:
- mention similarities
- mention differences
- indicate which is more detailed (if applicable)

IMPORTANT:
- Do NOT use Document 2 content in Doc1 answer
- Do NOT use Document 1 content in Doc2 answer

Answer format:

[Doc1 Answer]
...

[Doc2 Answer]
...

[Comparison]
...
"""
