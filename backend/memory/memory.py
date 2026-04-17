# backend/memory/memory.py
# Identical behaviour to base_pipeline/memory_manager.py.

class MemoryManager:
    def __init__(self):
        self.prev_query = None
        self.prev_answer = None
        self.prev_embedding = None

    def update(self, query: str, answer: str, embedding):
        self.prev_query = query
        self.prev_answer = answer
        self.prev_embedding = embedding

    def get(self):
        return self.prev_query, self.prev_answer, self.prev_embedding
