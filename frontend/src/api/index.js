// api/index.js
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

function authHeaders(token) {
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function _post(path, body, token) {
  const res = await fetch(`${BASE_URL}${path}`, {
    method:  'POST',
    headers: { 'Content-Type': 'application/json', ...authHeaders(token) },
    body:    JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({ detail: res.statusText }));
  if (!res.ok) throw new Error(data.detail ?? 'Request failed');
  return data;
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export async function login(username, password) {
  // returns { username, token }
  return _post('/login', { username, password });
}

export async function register(username, password) {
  // returns { message }
  return _post('/register', { username, password });
}

// ── PDF Upload ────────────────────────────────────────────────────────────────
export async function uploadPdf(file, chatId, token) {
  const form = new FormData();
  form.append('file', file);

  const res = await fetch(
    `${BASE_URL}/upload?chat_id=${encodeURIComponent(chatId)}`,
    { method: 'POST', headers: authHeaders(token), body: form }
  );
  const data = await res.json().catch(() => ({ detail: res.statusText }));
  if (!res.ok) throw new Error(data.detail ?? 'Upload failed');
  return data; // { id, name, path }
}

// ── Query ─────────────────────────────────────────────────────────────────────
export async function sendQuery(query, selectedPdfs, chatId, token) {
  return _post('/query', {
    query,
    pdfs:    selectedPdfs.map((p) => p.path),
    chat_id: chatId,
  }, token);
}
