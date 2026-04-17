# # main.py

# from retrieval_wrapper import RetrievalWrapper
# from memory_manager import MemoryManager
# from relation_classifier import RelationClassifier
# from memory_processor import MemoryProcessor
# from prompt_builder import PromptBuilder
# from llm_chain import LLMChainWrapper
# from utils import format_context

# # FILE_PATH = input("Enter PDF path: ")

# # retriever = RetrievalWrapper(FILE_PATH)

# pdf1 = input("Enter first PDF path: ").strip()
# pdf2 = input("Enter second PDF path (or press Enter to skip): ").strip()

# retriever1 = RetrievalWrapper(pdf1)
# retriever2 = RetrievalWrapper(pdf2) if pdf2 else None

# memory = MemoryManager()
# classifier = RelationClassifier(retriever.embed_model)
# processor = MemoryProcessor()
# prompt_builder = PromptBuilder()
# llm = LLMChainWrapper()

# print("\nSystem Ready. Type 'exit' to quit.\n")

# while True:
#     query = input("💬 Query: ").strip()
#     if query.lower() == "exit":
#         break

#     # prev_q, prev_ans = memory.get()
#     prev_q, prev_ans, prev_emb = memory.get()

#     # Step 1: classify relation
#     # relation = classifier.classify(prev_q, query)
#     relation_level, similarity = classifier.classify(prev_q, query)
#     # print(f"\n🔗 Relation: {relation}")
#     print(f"\n🔗 Similarity: {similarity:.3f} | Level: {relation_level}")

#     # Step 2: retrieve context
#     context_chunks = retriever.retrieve(query)
#     context = format_context(context_chunks)

#     # Step 3: process memory
#     key_points = None
#     # if relation != "UNRELATED" and prev_ans:
#     #     key_points = processor.extract_key_points(prev_ans)
#     if relation_level in ["HIGH", "MEDIUM"] and prev_ans:
#         key_points = processor.extract_key_points(prev_ans)
#     else:
#         key_points = None

#     # Step 4: build prompt
#     prompt = prompt_builder.build(query, context, key_points)

#     # Step 5: LLM answer
#     answer = llm.run(prompt)

#     print("\n🤖 Answer:\n", answer)

#     # Step 6: update memory
#     memory.update(query, answer)





# main.py

from retrieval_wrapper import RetrievalWrapper
from memory_manager import MemoryManager
from relation_classifier import RelationClassifier
from memory_processor import MemoryProcessor
from prompt_builder import PromptBuilder
from llm_chain import LLMChainWrapper
from utils import format_context

# -------------------------------
# Input PDFs
# -------------------------------
pdf1 = input("Enter first PDF path: ").strip()
pdf2 = input("Enter second PDF path (or press Enter to skip): ").strip()

retriever1 = RetrievalWrapper(pdf1)
retriever2 = RetrievalWrapper(pdf2) if pdf2 else None

# -------------------------------
# Initialize components
# -------------------------------
memory = MemoryManager()
classifier = RelationClassifier(retriever1.embed_model)  # ✅ FIXED
processor = MemoryProcessor()
prompt_builder = PromptBuilder()
llm = LLMChainWrapper()

print("\nSystem Ready. Type 'exit' to quit.\n")

# -------------------------------
# Query Loop
# -------------------------------
while True:
    query = input("💬 Query: ").strip()
    if query.lower() == "exit":
        break

    # Step 1: Get memory
    prev_q, prev_ans, prev_emb = memory.get()

    # Step 2: relation (embedding-based)
    relation_level, similarity = classifier.classify(prev_q, query)
    print(f"\n🔗 Similarity: {similarity:.3f} | Level: {relation_level}")

    # Step 3: process memory
    key_points = None
    if relation_level in ["HIGH", "MEDIUM"] and prev_ans:
        key_points = processor.extract_key_points(prev_ans)

    # -------------------------------
    # Step 4: Retrieval
    # -------------------------------
    if retriever2:
        context_a_chunks = retriever1.retrieve(query)
        context_b_chunks = retriever2.retrieve(query)

        context_a = format_context(context_a_chunks)
        context_b = format_context(context_b_chunks)

        merged_context = f"""
--- DOCUMENT 1 ---
{context_a}

--- DOCUMENT 2 ---
{context_b}
"""
    else:
        context_chunks = retriever1.retrieve(query)
        merged_context = format_context(context_chunks)

    # -------------------------------
    # Step 5: Prompt (FIXED)
    # -------------------------------
    if retriever2:
        prompt = prompt_builder.build_dual(
            query,
            context_a,
            context_b,
            key_points
        )
    else:
        prompt = prompt_builder.build_single(
            query,
            merged_context,
            key_points
        )

    # -------------------------------
    # Step 6: LLM
    # -------------------------------
    answer = llm.run(prompt)

    print("\n🤖 Answer:\n")
    print(answer)
    print("\n" + "=" * 60)

    # -------------------------------
    # Step 7: Update memory
    # -------------------------------
    curr_emb = retriever1.embed_query(query)
    memory.update(query, answer, curr_emb)