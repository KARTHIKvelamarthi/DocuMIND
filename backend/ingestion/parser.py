# backend/ingestion/parser.py
# Wraps ut.py's build_structured_chunks + embed_chunks + index builders.
# All chunking logic lives in ut.py — this module only orchestrates it.

import sys
import os

# Allow importing from project root (where ut.py lives)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ut import (
    build_structured_chunks,
    embed_chunks,
    build_faiss_index,
    build_bm25_index,
    link_heading_spans,
    print_tree,
)
from sentence_transformers import SentenceTransformer, CrossEncoder


def parse_and_index(file_path: str):
    """
    Full ingestion pipeline for a single PDF.

    Returns:
        chunks      - list of chunk dicts (with embeddings)
        faiss_index - FAISS IndexFlatIP
        bm25_index  - BM25Okapi
        embed_model - SentenceTransformer
        reranker    - CrossEncoder
    """
    raw_chunks = build_structured_chunks(file_path)

    print("\n🧠 Loading embedding model...")
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")

    print("\n🧠 Loading cross-encoder re-ranker...")
    reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

    print("\n🔢 Embedding chunks...")
    chunks = embed_chunks(raw_chunks, embed_model)

    print("\n🔗 Linking heading spans...")
    link_heading_spans(chunks)

    print_tree(chunks, limit=100)

    print("\n📦 Building FAISS index...")
    faiss_index = build_faiss_index(chunks)

    print("\n📦 Building BM25 index...")
    bm25_index = build_bm25_index(chunks)

    return chunks, faiss_index, bm25_index, embed_model, reranker
