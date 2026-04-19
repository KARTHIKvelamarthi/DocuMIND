# 🧠 DocuMind

An advanced, full-stack Retrieval-Augmented Generation (RAG) platform that empowers users to query, analyze, and compare multiple PDF documents simultaneously. It features conversational memory, hybrid retrieval (Dense + Sparse), and intelligent visual extraction for a comprehensive document analysis experience.

---

## ✨ Features

* **Advanced PDF Querying:** Chat natively with complex PDF documents to extract relevant answers quickly.
* **Dual Document Comparison:** Upload and query two documents side-by-side, prompting explicit comparative analyses.
* **Visual & Tabular Extraction:** Automatically extract relevant images, charts, and tables from PDFs to supplement text-based context.
* **Conversational Memory:** Maintains context across chat turns using relational embeddings, classifying the similarity between queries to fetch context intelligently.
* **Per-Chat Indexing:** Embeddings and indices are created dynamically on a per-chat basis, ensuring context isolation and efficiency.
* **Hybrid Retrieval Engine:** Combines FAISS (dense vector semantic search) and BM25 (sparse keyword search), optimized with a Cross-Encoder reranker.

---

## 🏛️ Architecture Overview

The system flow separates concerns cleanly between user interface, routing, and deep AI logic:

**Frontend (React UI)** ➔ **FastAPI Server** ➔ **RAG Pipeline (`rag_service`)** ➔ **LLM (Ollama/Mistral)**

1. User interacts with the **Frontend** and uploads PDFs.
2. The **FastAPI Server** handles authentication, saves the files, and orchestrates the AI service calls.
3. The **RAG Pipeline** chunks, embeds, and indexes the documents, running a hybrid search against the user's query.
4. **Ollama (Mistral)** receives the tailored prompt and returns the generated answer, which is streamed or sent back to the frontend.

---

## 📂 Project Structure

The repository is modularly split into specific feature sets:

* **`base_pipeline/`**: The core, standalone RAG engine logic. Contains underlying mechanics like chunking (`ut.py`), dual-prompts (`prompt_builder.py`), cross-encoder reranking, and BM25 setups. Kept pristine to ensure AI mechanics can be tested independently of the web API.
* **`backend/`**:
  * **`api/`**: RESTful API endpoints and routers tying the frontend to the backend (`routes.py`).
  * **`auth/`**: JWT-based authentication system.
  * **`db/`**: SQLite database session and schema models for user management.
  * **`ingestion/`**: Logic for parsing PDFs (`parser.py`) and extracting visuals and tables (`visual_extractor.py`).
  * **`memory/`**: Manages conversational history, utilizing `RelationClassifier` to determine context drift.
  * **`retrieval/`**: Wrappers for the core retrieval capabilities in the pipeline.
  * **`services/`**: High-level orchestrators (like `rag_service.py`) that stitch ingestion, memory, and LLMs together.
* **`frontend/`**: The Vite + React web application, utilizing Zustand for global state management.

---

## ⚙️ How It Works

1. **PDF Upload & Preload:** When a PDF is uploaded, `base_pipeline` tools use `pdfplumber` to chunk the document sentence-by-sentence, aware of headings and font sizes.
2. **Chunking & Indexing:** A fast `SentenceTransformer` embeds textual chunks and creates a FAISS index, paired with a BM25 index. Visual and tabular data via `PyMuPDF` is linked by page.
3. **Retrieval:** User queries are matched via hybrid FAISS + BM25 scores (with headings penalized so core content surfaces). 
4. **Memory Injection:** A `RelationClassifier` injects key points from previous conversational turns into the current context based on similarity scores.
5. **LLM Generation:** The context is formatted into a system prompt. For dual PDFs, it fetches from two separate indices and requests explicit comparisons. The prompt maps to Ollama running Mistral.

---

## 🚀 Setup Instructions

### Prerequisites
* Python 3.10+
* Node.js v18+

### 1. Running Ollama (Mistral)
The pipeline assumes a local LLM running via Ollama.
```bash
# Install Ollama (https://ollama.com/)
ollama pull mistral
ollama run mistral
```

### 2. Backend Setup
```bash
# Create and activate virtual environment
python -m venv venv
# On Windows: venv\Scripts\activate
# On Mac/Linux: source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Run the FastAPI server
uvicorn backend.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install

# Start the Vite dev server
npm run dev
```

---

## 💻 Tech Stack

* **Frontend:** React, Vite, Zustand
* **Backend:** FastAPI, SQLite, Pydantic, Passlib/Bcrypt (JWT Auth)
* **AI & Retrieval Engine:** 
  * FAISS (Dense Search)
  * BM25 (Sparse Keyword Search)
  * Sentence-Transformers & Cross-Encoders
* **Data Processing:** PyMuPDF (`fitz`), `pdfplumber`
* **LLM Orchestration:** LangChain (Community), Ollama

---

## 🏗️ Key Design Decisions

* **Isolated `base_pipeline/`:** By decoupling the actual retrieval and AI orchestration logic from the web server code, the pipeline remains fully testable via CLI (like `ut.py`) without needing to mock HTTP endpoints.
* **Hybrid Retrieval:** Dense embeddings (FAISS) capture semantic meaning, while sparse embeddings (BM25) ensure exact keyword matches (vital for jargon-heavy documents). Reranking refines the final candidate list.
* **Per-Chat Indexing:** Each chat initializes its own distinct vector spaces and indices. This ensures no data bleeding between documents across different sessions and keeps retrieval fast and perfectly relevant.

---

## 🔮 Future Improvements

* Allow users to select different underlying local/remote LLMs (e.g., LLaMA-3, OpenAI).
* Support for a wider variety of file formats like `.docx`, `.csv`, and `.txt`.
* Advanced visual Q&A by passing extracted images to multimodal LLMs (like LLaVa).

---

## ⚠️ Notes

* Directories such as `assets/` and `uploads/` are explicitly ignored by version control.
* Indices, uploaded PDFs, and extracted visual assets are generated organically at runtime and persisted locally.
