# backend/memory/relation.py
# Identical behaviour to base_pipeline/relation_classifier.py.

import numpy as np


class RelationClassifier:
    def __init__(self, embed_model, high_threshold: float = 0.6, low_threshold: float = 0.4):
        self.embed_model = embed_model
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold

    def _cosine_sim(self, a, b) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

    def classify(self, prev_q, curr_q):
        """
        Returns ("HIGH"|"MEDIUM"|"LOW", similarity_float)
        """
        if not prev_q:
            return "LOW", 0.0

        prev_emb = self.embed_model.encode([prev_q])[0]
        curr_emb = self.embed_model.encode([curr_q])[0]
        sim = self._cosine_sim(prev_emb, curr_emb)

        if sim >= self.high_threshold:
            return "HIGH", sim
        elif sim >= self.low_threshold:
            return "MEDIUM", sim
        else:
            return "LOW", sim
