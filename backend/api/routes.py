# backend/api/routes.py
import os, shutil, uuid
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

from backend.services.rag_service import run_query

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── /upload ───────────────────────────────────────────────────────────────────
@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    file_id = str(uuid.uuid4())
    safe_name = f"{file_id}_{file.filename}"
    dest = os.path.join(UPLOAD_DIR, safe_name)

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    return {
        "id": file_id,
        "name": file.filename,
        "path": dest,
    }


# ── /query ────────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query: str
    pdfs: List[str]   # list of server-side file paths returned by /upload
    chat_id: str


@router.post("/query")
async def query_endpoint(req: QueryRequest):
    if not req.pdfs:
        raise HTTPException(status_code=400, detail="At least one PDF path is required.")
    if len(req.pdfs) > 2:
        raise HTTPException(status_code=400, detail="Maximum 2 PDFs supported.")

    # Validate paths exist
    for p in req.pdfs:
        if not os.path.isfile(p):
            raise HTTPException(status_code=404, detail=f"PDF not found on server: {p}")

    try:
        result = run_query(req.chat_id, req.query, req.pdfs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Parse dual-doc answer into structured fields
    answer = result.get("answer", "")
    doc1_answer = doc2_answer = comparison = ""

    if len(req.pdfs) == 2:
        doc1_answer = _extract_section(answer, "[Doc1 Answer]", "[Doc2 Answer]")
        doc2_answer = _extract_section(answer, "[Doc2 Answer]", "[Comparison]")
        comparison  = _extract_section(answer, "[Comparison]", None)

    # Collect structured visuals from chunks
    images, tables = _collect_visuals(result.get("visuals", ""))

    return {
        "answer":      answer,
        "doc1_answer": doc1_answer,
        "doc2_answer": doc2_answer,
        "comparison":  comparison,
        "visuals":     result.get("visuals", ""),
        "images":      images,
        "tables":      tables,
        "relation":    result.get("relation", ""),
        "similarity":  result.get("similarity", 0),
    }


# ── helpers ───────────────────────────────────────────────────────────────────
def _extract_section(text: str, start_tag: str, end_tag: str | None) -> str:
    try:
        s = text.index(start_tag) + len(start_tag)
        e = text.index(end_tag) if end_tag and end_tag in text else len(text)
        return text[s:e].strip()
    except ValueError:
        return ""


def _collect_visuals(visuals_text: str):
    """Parse the plain-text visuals summary into image paths and table rows."""
    images, tables = [], []
    for line in visuals_text.splitlines():
        line = line.strip()
        if line.startswith("📷 Image:"):
            images.append(line.replace("📷 Image:", "").strip())
        elif line.startswith("📊 Table"):
            tables.append(line)
    return images, tables
