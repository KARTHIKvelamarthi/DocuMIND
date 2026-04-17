# backend/api/routes.py
import os, shutil, uuid
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
import bcrypt

from backend.auth.jwt_handler import create_token, get_current_user
from backend.services.rag_service import run_query, preload_retriever
from backend.db.database import get_db, User

router = APIRouter()

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── /register ─────────────────────────────────────────────────────────────────
class AuthRequest(BaseModel):
    username: str
    password: str


@router.post("/register", status_code=201)
def register(req: AuthRequest, db: Session = Depends(get_db)):
    if not req.username.strip() or not req.password:
        raise HTTPException(400, "Username and password are required.")
    if db.query(User).filter(User.username == req.username.strip()).first():
        raise HTTPException(409, "Username already taken.")
    hashed = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    db.add(User(username=req.username.strip(), password_hash=hashed))
    db.commit()
    return {"message": "Account created successfully."}


# ── /login ────────────────────────────────────────────────────────────────────
@router.post("/login")
def login(req: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username.strip()).first()
    if not user or not bcrypt.checkpw(req.password.encode(), user.password_hash.encode()):
        raise HTTPException(401, "Invalid username or password.")
    token = create_token(user.id, user.username)
    return {"username": user.username, "token": token}


# ── /upload ───────────────────────────────────────────────────────────────────
@router.post("/upload")
async def upload_pdf(
    file:    UploadFile = File(...),
    chat_id: str = "default",
    current_user: dict = Depends(get_current_user),
):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Only PDF files are accepted.")

    file_id   = str(uuid.uuid4())
    safe_name = f"{file_id}_{file.filename}"
    dest      = os.path.join(UPLOAD_DIR, safe_name)

    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        preload_retriever(current_user["user_id"], chat_id, dest)
    except Exception as e:
        print(f"[upload] Preload warning: {e}")

    return {"id": file_id, "name": file.filename, "path": dest}


# ── /query ────────────────────────────────────────────────────────────────────
class QueryRequest(BaseModel):
    query:   str
    pdfs:    List[str]
    chat_id: str


@router.post("/query")
async def query_endpoint(
    req: QueryRequest,
    current_user: dict = Depends(get_current_user),
):
    if not req.pdfs:
        raise HTTPException(400, "At least one PDF path is required.")
    if len(req.pdfs) > 2:
        raise HTTPException(400, "Maximum 2 PDFs supported.")
    for p in req.pdfs:
        if not os.path.isfile(p):
            raise HTTPException(404, f"PDF not found on server: {p}")

    try:
        result = run_query(current_user["user_id"], req.chat_id, req.query, req.pdfs)
    except Exception as e:
        raise HTTPException(500, str(e))

    answer      = result.get("answer", "")
    doc1_answer = doc2_answer = comparison = ""

    if len(req.pdfs) == 2:
        doc1_answer = _extract_section(answer, "[Doc1 Answer]", "[Doc2 Answer]")
        doc2_answer = _extract_section(answer, "[Doc2 Answer]", "[Comparison]")
        comparison  = _extract_section(answer, "[Comparison]", None)

    images, tables = _collect_visuals(result.get("visuals", ""), result.get("raw_tables", []))

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


def _collect_visuals(visuals_text: str, raw_tables: list):
    """Extract image paths from visuals text; use raw_tables for structured data."""
    images = []
    for line in visuals_text.splitlines():
        line = line.strip()
        if line.startswith("📷 Image:"):
            images.append(line.replace("📷 Image:", "").strip())
    # raw_tables is already List[List[List[str]]] — pass through directly
    return images, raw_tables
