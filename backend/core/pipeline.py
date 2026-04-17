# backend/core/pipeline.py
# Orchestrates the full RAG flow:
#   User Query → Retrieval → Context → Prompt → LLM → Answer → Memory Update

from backend.retrieval.retriever import Retriever
from backend.memory.memory import MemoryManager
from backend.memory.relation import RelationClassifier
from backend.memory.processor import MemoryProcessor
from backend.prompting.prompt_builder import PromptBuilder
from backend.llm.llm_service import LLMService
from backend.utils.formatter import format_context, format_visuals


class RAGPipeline:
    def __init__(self, pdf1: str, pdf2: str = None, extract_visuals: bool = True):
        """
        pdf1            - path to first (or only) PDF
        pdf2            - optional path to second PDF for dual-document comparison
        extract_visuals - whether to extract images/tables and attach to chunks
        """
        self.retriever1 = Retriever(pdf1, extract_visuals=extract_visuals)
        self.retriever2 = Retriever(pdf2, extract_visuals=extract_visuals) if pdf2 else None

        self.memory = MemoryManager()
        self.classifier = RelationClassifier(self.retriever1.embed_model)
        self.processor = MemoryProcessor()
        self.prompt_builder = PromptBuilder()
        self.llm = LLMService()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def query(self, user_query: str) -> dict:
        """
        Run a single query through the full pipeline.

        Returns a dict with:
            answer      - LLM response string
            context     - formatted context string used in prompt
            visuals     - formatted visual summary (images + tables)
            similarity  - float, embedding similarity to previous query
            relation    - "HIGH" | "MEDIUM" | "LOW"
        """
        # Step 1: memory
        prev_q, prev_ans, _ = self.memory.get()

        # Step 2: relation classification
        relation_level, similarity = self.classifier.classify(prev_q, user_query)

        # Step 3: key-point extraction from previous answer
        key_points = None
        if relation_level in ("HIGH", "MEDIUM") and prev_ans:
            key_points = self.processor.extract_key_points(prev_ans)

        # Step 4: retrieval
        if self.retriever2:
            chunks_a = self.retriever1.retrieve(user_query)
            chunks_b = self.retriever2.retrieve(user_query)
            context_a = format_context(chunks_a)
            context_b = format_context(chunks_b)
            merged_context = f"--- DOCUMENT 1 ---\n{context_a}\n\n--- DOCUMENT 2 ---\n{context_b}"
            all_chunks = chunks_a + chunks_b
        else:
            chunks = self.retriever1.retrieve(user_query)
            merged_context = format_context(chunks)
            context_a = context_b = None
            all_chunks = chunks

        # Step 5: visuals summary (printed, not sent to LLM)
        visuals_summary = format_visuals(all_chunks)

        # Step 6: build prompt
        if self.retriever2:
            prompt = self.prompt_builder.build_dual(user_query, context_a, context_b, key_points)
        else:
            prompt = self.prompt_builder.build_single(user_query, merged_context, key_points)

        # Step 7: LLM
        answer = self.llm.run(prompt)

        # Step 8: update memory
        curr_emb = self.retriever1.embed_query(user_query)
        self.memory.update(user_query, answer, curr_emb)

        return {
            "answer": answer,
            "context": merged_context,
            "visuals": visuals_summary,
            "similarity": similarity,
            "relation": relation_level,
        }
