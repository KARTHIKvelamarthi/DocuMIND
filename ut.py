import re
import numpy as np
from collections import Counter

import pdfplumber
import faiss
import nltk
from nltk.tokenize import sent_tokenize

from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi

nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)


# -----------------------------------------------------------------------
# CONFIG — tweak these for your document
# -----------------------------------------------------------------------
CHUNK_SIZE      = 200    # max words per content chunk
OVERLAP         = 50     # word overlap between chunks
HYBRID_TOP_K    = 15     # candidates from hybrid retrieval
RERANK_TOP_K    = 5      # kept after cross-encoder
CONTEXT_SIZE    = 6      # final assembled context window
ALPHA           = 0.6    # 0=pure BM25, 1=pure semantic (0.6 favors semantic)

# Heading detection: % of words that must be capitalized for a short line to be a heading
# Raise this if too many content lines are classified as headings
HEADING_CAP_RATIO = 0.5

# Minimum font-size DELTA above median to be classified as heading
# (e.g. 1.5 means the font must be 1.5pt larger than median body text)
HEADING_SIZE_DELTA = 1.5


# -----------------------------------------------------------------------
# Step 1: Font-aware extraction with pdfplumber
# -----------------------------------------------------------------------
def extract_structured_blocks(file_path):
    blocks = []
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            words = page.extract_words(extra_attrs=["size", "fontname"])
            if not words:
                continue

            # Group words into lines by y-position
            lines = {}
            for word in words:
                y = round(word["top"], 1)
                lines.setdefault(y, []).append(word)

            for y in sorted(lines.keys()):
                line_words = lines[y]
                text = " ".join(w["text"] for w in line_words).strip()
                avg_size = sum(w["size"] for w in line_words) / len(line_words)
                font = line_words[0]["fontname"]

                if text:
                    blocks.append({
                        "text": text,
                        "size": round(avg_size, 2),
                        "font": font,
                        "page": page_num + 1,
                    })
    return blocks


def get_body_font_size(blocks):
    """
    Body text is the MOST COMMON font size in the document.
    Much more reliable than percentile-based thresholding.
    """
    size_counter = Counter(round(b["size"], 1) for b in blocks)
    body_size = size_counter.most_common(1)[0][0]
    print(f"   Detected body font size: {body_size}pt")
    return body_size


# -----------------------------------------------------------------------
# Step 2: Reliable heading classification
# Uses BOTH font size delta AND capitalization ratio
# -----------------------------------------------------------------------
def classify_block(block, body_size):
    text = block["text"].strip()
    words = text.split()

    if not words:
        return "content"

    # Bullet detection
    if text[0] in ("•", "-", "–", "▪", "*"):
        return "bullet"

    size_delta = block["size"] - body_size
    word_count = len(words)

    # Strong heading signal: significantly larger font
    if size_delta >= HEADING_SIZE_DELTA:
        return "heading"

    # Weak heading signal: same size but short + mostly capitalized
    # (e.g. bold section titles rendered at same size)
    if word_count <= 10 and not text.endswith("."):
        cap_ratio = sum(1 for w in words if w[0].isupper()) / word_count
        if cap_ratio >= HEADING_CAP_RATIO and size_delta >= 0:
            return "heading"

    return "content"


# -----------------------------------------------------------------------
# Step 3: Noise filtering
# -----------------------------------------------------------------------
def is_noise(text):
    t = text.lower().strip()
    if re.match(r"^page \d+", t):          return True
    if "pg." in t and len(t.split()) <= 4: return True
    if len(t.split()) <= 2:                return True
    if re.match(r"^[\d\s\.\,\-]+$", t):   return True
    return False


# -----------------------------------------------------------------------
# Step 4: Sentence-aware chunking
# -----------------------------------------------------------------------
def sentence_aware_chunk(text, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    sentences = sent_tokenize(text)
    chunks = []
    current_words = []

    for sentence in sentences:
        words = sentence.split()
        if len(current_words) + len(words) > chunk_size and current_words:
            chunks.append(" ".join(current_words))
            current_words = (current_words[-overlap:] if len(current_words) > overlap else current_words[:]) + words
        else:
            current_words.extend(words)

    if current_words:
        chunks.append(" ".join(current_words))

    return chunks


# -----------------------------------------------------------------------
# Step 5: Build structured chunks
# -----------------------------------------------------------------------
def build_structured_chunks(file_path):
    print("\n📄 Extracting structured blocks from PDF...")
    blocks = extract_structured_blocks(file_path)
    print(f"   Raw line-blocks extracted: {len(blocks)}")

    body_size = get_body_font_size(blocks)

    # Deduplicate repeated lines (headers/footers)
    normalized_texts = [re.sub(r"\s+", " ", b["text"].lower()) for b in blocks]
    counts = Counter(normalized_texts)

    # ---- Merge consecutive same-type lines into paragraphs ----
    merged = []
    current_para = None

    for block, norm in zip(blocks, normalized_texts):
        if counts[norm] > 2 or is_noise(block["text"]):
            continue

        btype = classify_block(block, body_size)

        if current_para is None:
            current_para = {"text": block["text"], "size": block["size"],
                            "font": block["font"], "page": block["page"], "type": btype}
        elif btype == current_para["type"] and btype != "heading":
            # Merge consecutive content/bullet lines into one paragraph
            current_para["text"] += " " + block["text"]
        else:
            merged.append(current_para)
            current_para = {"text": block["text"], "size": block["size"],
                            "font": block["font"], "page": block["page"], "type": btype}

    if current_para:
        merged.append(current_para)

    print(f"   Merged paragraph blocks: {len(merged)}")

    # ---- Chunk merged paragraphs ----
    raw_chunks = []
    current_heading = None
    heading_count = sum(1 for m in merged if m["type"] == "heading")
    content_count  = sum(1 for m in merged if m["type"] != "heading")
    print(f"   Headings: {heading_count} | Content/Bullet blocks: {content_count}")

    for block in merged:
        if block["type"] == "heading":
            current_heading = block["text"].strip()
            raw_chunks.append({
                "text": current_heading,
                "type": "heading",
                "page": block["page"],
                "heading": current_heading,
            })
        else:
            sub_chunks = sentence_aware_chunk(block["text"])
            for sub in sub_chunks:
                raw_chunks.append({
                    "text": sub,
                    "type": block["type"],
                    "page": block["page"],
                    "heading": current_heading,
                })

    heading_final  = sum(1 for c in raw_chunks if c["type"] == "heading")
    content_final  = sum(1 for c in raw_chunks if c["type"] != "heading")
    print(f"   Final chunks → headings: {heading_final} | content+bullet: {content_final}")

    if heading_final > content_final:
        print("\n⚠️  WARNING: More headings than content chunks detected!")
        print("   → Increase HEADING_SIZE_DELTA or HEADING_CAP_RATIO in CONFIG.")
        print("   → Run diagnose_fonts.py to inspect your document's font sizes.\n")

    return raw_chunks


# -----------------------------------------------------------------------
# Step 6: Embed chunks
# -----------------------------------------------------------------------
def embed_chunks(raw_chunks, model):
    texts = [c["text"] for c in raw_chunks]
    embeddings = model.encode(texts, show_progress_bar=True, batch_size=64)

    chunks = []
    for i, (chunk, emb) in enumerate(zip(raw_chunks, embeddings)):
        chunks.append({
            "id":      i,
            "text":    chunk["text"],
            "type":    chunk["type"],
            "page":    chunk["page"],
            "heading": chunk.get("heading"),
            "embedding": emb.astype("float32"),
            "length":  len(chunk["text"].split()),
            "links":   [],
        })
    return chunks


# -----------------------------------------------------------------------
# Step 7: FAISS index
# -----------------------------------------------------------------------
def build_faiss_index(chunks):
    embeddings = np.array([c["embedding"] for c in chunks]).astype("float32")
    faiss.normalize_L2(embeddings)
    index = faiss.IndexFlatIP(embeddings.shape[1])
    index.add(embeddings)
    print(f"   FAISS index: {index.ntotal} vectors (dim={embeddings.shape[1]})")
    return index


# -----------------------------------------------------------------------
# Step 8: BM25 index
# -----------------------------------------------------------------------
def build_bm25_index(chunks):
    tokenized = [c["text"].lower().split() for c in chunks]
    print(f"   BM25 index: {len(tokenized)} chunks")
    return BM25Okapi(tokenized)


# -----------------------------------------------------------------------
# Step 9: Heading-span linking
# -----------------------------------------------------------------------
def link_heading_spans(chunks):
    current_heading_idx = None
    linked = 0
    for i, chunk in enumerate(chunks):
        if chunk["type"] == "heading":
            current_heading_idx = i
        elif current_heading_idx is not None:
            chunks[current_heading_idx]["links"].append({"id": i, "score": 1.0})
            chunks[i]["links"].append({"id": current_heading_idx, "score": 1.0})
            linked += 1
    print(f"   Heading-span links created: {linked}")


# -----------------------------------------------------------------------
# Step 10: Hybrid retrieval (semantic + BM25)
# Headings are EXCLUDED from retrieval — they exist only for context assembly
# -----------------------------------------------------------------------
def hybrid_retrieve(query, chunks, bm25, faiss_index, model,
                    top_k=HYBRID_TOP_K, alpha=ALPHA):
    n = len(chunks)

    # BM25
    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_norm   = bm25_scores / (bm25_scores.max() + 1e-9)

    # Semantic
    query_emb = model.encode([query]).astype("float32")
    faiss.normalize_L2(query_emb)
    raw_scores, indices = faiss_index.search(query_emb, n)

    sem_norm = np.zeros(n)
    for rank in range(len(indices[0])):
        idx = indices[0][rank]
        if 0 <= idx < n:
            sem_norm[idx] = raw_scores[0][rank]

    combined = alpha * sem_norm + (1 - alpha) * bm25_norm

    # ---- KEY FIX: penalize headings so content chunks surface ----
    for i, chunk in enumerate(chunks):
        if chunk["type"] == "heading":
            combined[i] *= 0.3   # 70% score penalty on headings

    top_indices = np.argsort(combined)[::-1][:top_k]

    print(f"\n🔀 Hybrid top-{top_k} (α={alpha}, headings penalized):")
    for idx in top_indices:
        c = chunks[idx]
        print(f"   ID {c['id']:3d} | {c['type']:8s} | "
              f"sem={sem_norm[idx]:.3f} bm25={bm25_norm[idx]:.3f} "
              f"fused={combined[idx]:.3f} | pg {c['page']}")

    return [chunks[i] for i in top_indices]


# -----------------------------------------------------------------------
# Step 11: Cross-encoder re-ranking
# -----------------------------------------------------------------------
def rerank_candidates(query, candidates, reranker):
    pairs  = [(query, c["text"]) for c in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, candidates), key=lambda x: x[0], reverse=True)

    print(f"\n🏆 Re-ranked:")
    for score, c in ranked:
        print(f"   ID {c['id']:3d} | {c['type']:8s} | "
              f"rerank={score:6.3f} | pg {c['page']}"
              + (f" | under: '{c['heading'][:40]}'" if c.get("heading") and c["type"] != "heading" else ""))

    return [c for _, c in ranked]


# -------------------------------
# Section-level grouping
# -------------------------------
def group_by_heading(chunks):
    sections = {}

    for c in chunks:
        heading = c.get("heading") or "NO_HEADING"

        if heading not in sections:
            sections[heading] = []

        sections[heading].append(c)

    return sections


# -------------------------------
# Section scoring (using reranker)
# -------------------------------
def score_section(section_chunks, query, reranker):
    pairs = [(query, c["text"]) for c in section_chunks]
    scores = reranker.predict(pairs)

    return sum(scores) / len(scores)


# -------------------------------
# Select best section
# -------------------------------
def select_best_section(reranked_chunks, query, reranker):
    sections = group_by_heading(reranked_chunks)

    best_section = None
    best_score = float("-inf")

    print("\n📊 Section Scores:\n")

    for heading, chunks in sections.items():
        score = score_section(chunks, query, reranker)

        print(f"→ {heading[:50]} | score={score:.3f}")

        if score > best_score:
            best_score = score
            best_section = (heading, chunks)

    return best_section


# -----------------------------------------------------------------------
# Step 12: Context assembly
# Pull in parent heading + sibling content around each top chunk
# -----------------------------------------------------------------------
def assemble_context(top_chunks, chunks, max_chunks=CONTEXT_SIZE):
    seen_ids = set()
    context  = []

    for chunk in top_chunks:
        if len(context) >= max_chunks:
            break

        # Add heading first (for labeling)
        for link in chunk["links"]:
            linked = chunks[link["id"]]
            if linked["type"] == "heading" and linked["id"] not in seen_ids:
                context.append(linked)
                seen_ids.add(linked["id"])

        # Add the content chunk itself
        if chunk["id"] not in seen_ids:
            context.append(chunk)
            seen_ids.add(chunk["id"])

        # Add adjacent content siblings (same heading)
        for link in chunk["links"]:
            if len(context) >= max_chunks:
                break
            linked = chunks[link["id"]]
            if linked["type"] in ("content", "bullet") and linked["id"] not in seen_ids:
                context.append(linked)
                seen_ids.add(linked["id"])

    # Sort final context by document order (chunk ID = document order)
    context.sort(key=lambda c: c["id"])
    return context


# -----------------------------------------------------------------------
# Pipeline builders
# -----------------------------------------------------------------------
def build_pipeline(file_path):
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


def query_pipeline(query, chunks, faiss_index, bm25_index, embed_model, reranker):
    print(f"\n💬 Query: {query}")

    candidates = hybrid_retrieve(query, chunks, bm25_index, faiss_index, embed_model)
    reranked   = rerank_candidates(query, candidates, reranker)
    # top_chunks = reranked[:RERANK_TOP_K]
    # context    = assemble_context(top_chunks, chunks)
    # return context
    heading, best_chunks = select_best_section(reranked, query, reranker)

    print(f"\n🏆 Selected Section: {heading}\n")

    context = assemble_context(best_chunks, chunks)

    return context




def print_tree(chunks, limit=None):
    print("\n🌳 DOCUMENT TREE STRUCTURE:\n")

    tree = {}
    
    # Group chunks by heading
    for c in chunks:
        heading = c.get("heading") or "ROOT"

        if heading not in tree:
            tree[heading] = []

        tree[heading].append(c)

    count = 0

    for heading, items in tree.items():
        print(f"\n📂 {heading}\n")

        for c in items:
            if c["type"] == "heading":
                continue

            prefix = "   ├──"
            if c["type"] == "bullet":
                prefix = "   •"

            print(f"{prefix} [ID {c['id']}] ({c['type']}) {c['text'][:100]}")

            count += 1
            if limit and count >= limit:
                return

# -----------------------------------------------------------------------
# Entry point
# -----------------------------------------------------------------------
if __name__ == "__main__":
    file_path = r"C:\Users\karth\Downloads\j0_endgame_merged.pdf"

    chunks, faiss_index, bm25_index, embed_model, reranker = build_pipeline(file_path)

    print("\n" + "=" * 60)
    print("RAG Pipeline Ready. Type 'exit' to quit.")
    print("=" * 60)

    while True:
        query = input("\n💬 Enter query: ").strip()
        if query.lower() in ("exit", "quit", "q"):
            print("👋 Exiting.")
            break
        if not query:
            continue

        context = query_pipeline(query, chunks, faiss_index, bm25_index, embed_model, reranker)

        print("\n📦 RETRIEVED CONTEXT:\n" + "=" * 60)
        for c in context:
            label = f"[ID {c['id']}] [{c['type'].upper()}] [Page {c['page']}]"
            if c.get("heading") and c["type"] != "heading":
                label += f" ← '{c['heading'][:50]}'"
            print(label)
            print(c["text"][:500])
            print("-" * 60)

        print("\n✅ Done.")