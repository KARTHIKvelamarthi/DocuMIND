# backend/api/routes.py
# Future API endpoints — ready to be wrapped with FastAPI or Flask.
# Currently exposes the pipeline as callable functions with clear I/O contracts.

from backend.core.pipeline import RAGPipeline

_pipeline: RAGPipeline = None


def init_pipeline(pdf1: str, pdf2: str = None, extract_visuals: bool = True):
    """
    Initialize the global pipeline instance.
    Call once at startup before handling queries.
    """
    global _pipeline
    _pipeline = RAGPipeline(pdf1, pdf2, extract_visuals=extract_visuals)


def handle_query(user_query: str) -> dict:
    """
    Handle a single user query.

    Input:
        user_query: str

    Output:
        {
            "answer":     str,
            "context":    str,
            "visuals":    str,
            "similarity": float,
            "relation":   str,
        }
    """
    if _pipeline is None:
        raise RuntimeError("Pipeline not initialized. Call init_pipeline() first.")
    return _pipeline.query(user_query)
