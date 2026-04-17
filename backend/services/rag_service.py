# backend/services/rag_service.py
# Retriever cache is scoped by (user_id, chat_id, pdf_path).
# Same chat_id across different users never collides.

import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.retrieval.retriever import Retriever
from backend.memory.memory import MemoryManager
from backend.memory.relation import RelationClassifier
from backend.memory.processor import MemoryProcessor
from backend.prompting.prompt_builder import PromptBuilder
from backend.llm.llm_service import LLMService
from backend.utils.formatter import format_context, format_visuals

# ── Caches ────────────────────────────────────────────────────────────────────
# { user_id: { chat_id: { pdf_path: Retriever } } }
_retriever_cache: dict[int, dict[str, dict[str, Retriever]]] = {}

# { user_id: { chat_id: { memory, classifier, ... } } }
_chat_sessions: dict[int, dict[str, dict]] = {}

# ── "Not found" scrubber ──────────────────────────────────────────────────────
_NOT_FOUND_RE = re.compile(
    r"not found in (the|that) document[s]?\.?"
    r"|(?:the|that) document[s]? (?:does|do) not (?:contain|mention|include|provide)[^.]*\."
    r"|(?:no|the) (?:relevant |specific )?(?:information|answer|detail|content|data)"
      r" (?:is )?(?:available|found|present|provided) in (?:the|that) document[s]?\.?"
    r"|(?:this|the) (?:information|topic|question) is not"
      r" (?:covered|addressed|discussed) in (?:the|that) document[s]?\.?",
    flags=re.IGNORECASE,
)


def _clean(text: str) -> str:
    cleaned = _NOT_FOUND_RE.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_retriever(user_id: int, chat_id: str, pdf_path: str) -> Retriever:
    user_cache = _retriever_cache.setdefault(user_id, {})
    chat_cache = user_cache.setdefault(chat_id, {})
    if pdf_path not in chat_cache:
        print(f"[cache] BUILD  user={user_id} chat={chat_id} pdf={os.path.basename(pdf_path)}")
        chat_cache[pdf_path] = Retriever(pdf_path, extract_visuals=True)
    else:
        print(f"[cache] REUSE  user={user_id} chat={chat_id} pdf={os.path.basename(pdf_path)}")
    return chat_cache[pdf_path]


def _get_session(user_id: int, chat_id: str, embed_model) -> dict:
    user_sessions = _chat_sessions.setdefault(user_id, {})
    if chat_id not in user_sessions:
        user_sessions[chat_id] = {
            "memory":         MemoryManager(),
            "classifier":     RelationClassifier(embed_model),
            "processor":      MemoryProcessor(),
            "prompt_builder": PromptBuilder(),
            "llm":            LLMService(),
        }
    return user_sessions[chat_id]


# ── Public API ────────────────────────────────────────────────────────────────

def preload_retriever(user_id: int, chat_id: str, pdf_path: str) -> None:
    """Eagerly index on upload so first query is instant."""
    _get_retriever(user_id, chat_id, pdf_path)


def run_query(user_id: int, chat_id: str, query: str, pdf_paths: list[str]) -> dict:
    r1 = _get_retriever(user_id, chat_id, pdf_paths[0])
    r2 = _get_retriever(user_id, chat_id, pdf_paths[1]) if len(pdf_paths) == 2 else None

    sess          = _get_session(user_id, chat_id, r1.embed_model)
    memory        = sess["memory"]
    classifier    = sess["classifier"]
    processor     = sess["processor"]
    prompt_builder = sess["prompt_builder"]
    llm           = sess["llm"]

    prev_q, prev_ans, _ = memory.get()
    relation_level, similarity = classifier.classify(prev_q, query)

    key_points = None
    if relation_level in ("HIGH", "MEDIUM") and prev_ans:
        key_points = processor.extract_key_points(prev_ans)

    if r2:
        chunks_a  = r1.retrieve(query)
        chunks_b  = r2.retrieve(query)
        context_a = format_context(chunks_a)
        context_b = format_context(chunks_b)
        all_chunks = chunks_a + chunks_b
        prompt    = prompt_builder.build_dual(query, context_a, context_b, key_points)
        merged    = f"--- DOCUMENT 1 ---\n{context_a}\n\n--- DOCUMENT 2 ---\n{context_b}"
    else:
        chunks    = r1.retrieve(query)
        context_a = format_context(chunks)
        context_b = None
        all_chunks = chunks
        prompt    = prompt_builder.build_single(query, context_a, key_points)
        merged    = context_a

    visuals = format_visuals(all_chunks)
    answer  = _clean(llm.run(prompt))

    memory.update(query, answer, r1.embed_query(query))

    # Collect structured table data from retrieved chunks
    raw_tables = []
    for chunk in all_chunks:
        for tbl in chunk.get("tables", []):
            data = tbl.get("data")
            if data:
                raw_tables.append(data)

    return {
        "answer":     answer,
        "context":    merged,
        "visuals":    visuals,
        "raw_tables": raw_tables,
        "similarity": float(similarity),
        "relation":   relation_level,
    }
