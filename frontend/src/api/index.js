// api/index.js — real API calls to FastAPI backend

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// ── Auth (frontend-only, no backend auth yet) ─────────────────────────────────
export async function login(username, password) {
  if (!username || !password) throw new Error('Username and password required');
  return { username };
}

// ── PDF Upload ────────────────────────────────────────────────────────────────
export async function uploadPdf(file) {
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(`${BASE_URL}/upload`, { method: 'POST', body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? 'Upload failed');
  }
  // Returns { id, name, path }
  return res.json();
}

// ── Query ─────────────────────────────────────────────────────────────────────
export async function sendQuery(query, selectedPdfs, chatId) {
  const res = await fetch(`${BASE_URL}/query`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      query,
      pdfs: selectedPdfs.map((p) => p.path),   // server-side paths
      chat_id: chatId,
    }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? 'Query failed');
  }

  // Returns { answer, doc1_answer, doc2_answer, comparison, visuals, images, tables, relation, similarity }
  return res.json();
}
