# # memory_manager.py

# class MemoryManager:
#     def __init__(self):
#         self.prev_query = None
#         self.prev_answer = None

#     def update(self, query, answer):
#         self.prev_query = query
#         self.prev_answer = answer

#     def get(self):
#         return self.prev_query, self.prev_answer




# memory_manager.py

class MemoryManager:
    def __init__(self):
        self.prev_query = None
        self.prev_answer = None
        self.prev_embedding = None

    def update(self, query, answer, embedding):
        self.prev_query = query
        self.prev_answer = answer
        self.prev_embedding = embedding

    def get(self):
        return self.prev_query, self.prev_answer, self.prev_embedding