# main.py — new entry point
# Produces identical output to base_pipeline/main.py, with visual support added.

from backend.core.pipeline import RAGPipeline

# -------------------------------
# Input PDFs
# -------------------------------
pdf1 = input("Enter first PDF path: ").strip()
pdf2 = input("Enter second PDF path (or press Enter to skip): ").strip()

pipeline = RAGPipeline(pdf1, pdf2 if pdf2 else None, extract_visuals=True)

print("\nSystem Ready. Type 'exit' to quit.\n")

# -------------------------------
# Query Loop
# -------------------------------
while True:
    query = input("💬 Query: ").strip()
    if query.lower() == "exit":
        break
    if not query:
        continue

    result = pipeline.query(query)

    print(f"\n🔗 Similarity: {result['similarity']:.3f} | Level: {result['relation']}")
    print("\n🤖 Answer:\n")
    print(result["answer"])

    # Step 6: display visuals (images + tables) — no LLM interpretation
    if result["visuals"]:
        print("\n🖼️  Visuals found in retrieved chunks:")
        print(result["visuals"])

    print("\n" + "=" * 60)
