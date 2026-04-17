# # retrieval_wrapper.py

# from ut import build_pipeline, query_pipeline

# class RetrievalWrapper:
#     def __init__(self, file_path):
#         self.chunks, self.faiss, self.bm25, self.embed_model, self.reranker = build_pipeline(file_path)

#     def retrieve(self, query):
#         return query_pipeline(
#             query,
#             self.chunks,
#             self.faiss,
#             self.bm25,
#             self.embed_model,
#             self.reranker
#         )



# retrieval_wrapper.py

from ut import build_pipeline, query_pipeline

class RetrievalWrapper:
    def __init__(self, file_path):
        self.chunks, self.faiss, self.bm25, self.embed_model, self.reranker = build_pipeline(file_path)

    def retrieve(self, query):
        return query_pipeline(
            query,
            self.chunks,
            self.faiss,
            self.bm25,
            self.embed_model,
            self.reranker
        )

    def embed_query(self, query):
        return self.embed_model.encode([query])[0]