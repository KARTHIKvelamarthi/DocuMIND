# # relation_classifier.py

# from langchain_community.llms import Ollama

# class RelationClassifier:
#     def __init__(self, model_name="mistral"):
#         self.llm = Ollama(model=model_name)

#     def classify(self, prev_q, curr_q):
#         if not prev_q:
#             return "UNRELATED"

# #         prompt = f"""
# # Classify the relation between two queries:

# # Q1: {prev_q}
# # Q2: {curr_q}

# # Return ONLY one word:
# # SAME, EXPAND, CONTRAST, DEPENDENT, UNRELATED
# # """
#         prompt = f"""
# Classify the relationship BETWEEN queries AND their direction:

# Q1: {prev_q}
# Q2: {curr_q}

# Consider:
# - Is Q2 asking for explanation of Q1? → EXPAND
# - Is Q2 asking for limitations of Q1? → CONTRAST
# - Is Q2 switching topic? → UNRELATED
# - Is Q2 reversing perspective? → DEPENDENT

# Return ONLY one:
# SAME, EXPAND, CONTRAST, DEPENDENT, UNRELATED
# """

#         result = self.llm.invoke(prompt).strip().upper()

#         valid = {"SAME", "EXPAND", "CONTRAST", "DEPENDENT", "UNRELATED"}
#         return result if result in valid else "UNRELATED"





# relation_classifier.py

import numpy as np


class RelationClassifier:
    def __init__(self, embed_model, high_threshold=0.6, low_threshold=0.4):
        """
        embed_model: reuse the embedding model from your pipeline
        high_threshold: strong relation
        low_threshold: weak relation
        """
        self.embed_model = embed_model
        self.high_threshold = high_threshold
        self.low_threshold = low_threshold

    def cosine_sim(self, a, b):
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

    def classify(self, prev_q, curr_q):
        """
        Returns:
        - "HIGH"    → strongly related (use full memory)
        - "MEDIUM"  → somewhat related (use compressed memory)
        - "LOW"     → unrelated (ignore memory)
        """

        if not prev_q:
            return "LOW", 0.0

        prev_emb = self.embed_model.encode([prev_q])[0]
        curr_emb = self.embed_model.encode([curr_q])[0]

        sim = self.cosine_sim(prev_emb, curr_emb)

        if sim >= self.high_threshold:
            return "HIGH", sim
        elif sim >= self.low_threshold:
            return "MEDIUM", sim
        else:
            return "LOW", sim