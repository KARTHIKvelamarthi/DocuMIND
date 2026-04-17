# backend/services/rag_service.py
# Manages per-chat RAGPipeline instances.
# Each chat_id gets its own pipeline keyed by the sorted tuple of PDF paths,
# so switching PDFs rebuilds the pipeline while re-using it for the same PDFs.

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.core.pipeline import RAGPipeline

# { chat_id: { "key": (pdf1, pdf2|None), "pipeline": RAGPipeline } }
_sessions: dict = {}


def _session_key(pdf_paths: list[str]) -> tuple:
    """Stable key regardless of selection order."""
    return tuple(sorted(pdf_paths))


def get_or_create_pipeline(chat_id: str, pdf_paths: list[str]) -> RAGPipeline:
    key = _session_key(pdf_paths)
    session = _sessions.get(chat_id)

    if session and session["key"] == key:
        return session["pipeline"]

    # Build new pipeline
    pdf1 = pdf_paths[0]
    pdf2 = pdf_paths[1] if len(pdf_paths) == 2 else None
    pipeline = RAGPipeline(pdf1, pdf2, extract_visuals=True)

    _sessions[chat_id] = {"key": key, "pipeline": pipeline}
    return pipeline


def run_query(chat_id: str, query: str, pdf_paths: list[str]) -> dict:
    pipeline = get_or_create_pipeline(chat_id, pdf_paths)
    return pipeline.query(query)
