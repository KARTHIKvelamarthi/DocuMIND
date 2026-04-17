# backend/main.py — FastAPI server entry point
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.routes import router

app = FastAPI(title="DocuMind API", version="1.0.0")

# Allow the Vite dev server (port 5173) and any localhost origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve extracted images as static files at /assets/images/<filename>
ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "images")
os.makedirs(ASSETS_DIR, exist_ok=True)
app.mount("/assets/images", StaticFiles(directory=ASSETS_DIR), name="images")

app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok"}
