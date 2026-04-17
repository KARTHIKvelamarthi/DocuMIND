# backend/retrieval/retriever.py
# Wraps the retrieval pipeline. Identical behaviour to base_pipeline/retrieval_wrapper.py.

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from ut import query_pipeline
from backend.ingestion.parser import parse_and_index
from backend.ingestion.visual_extractor import enrich_chunks_with_visuals


class Retriever:
    def __init__(self, file_path: str, extract_visuals: bool = True):
        self.file_path = file_path
        self.chunks, self.faiss, self.bm25, self.embed_model, self.reranker = parse_and_index(file_path)

        if extract_visuals:
            enrich_chunks_with_visuals(file_path, self.chunks)

    def retrieve(self, query: str):
        return query_pipeline(
            query,
            self.chunks,
            self.faiss,
            self.bm25,
            self.embed_model,
            self.reranker,
        )

    def embed_query(self, query: str):
        return self.embed_model.encode([query])[0]
