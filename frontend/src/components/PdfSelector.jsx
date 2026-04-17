import { useRef, useState } from 'react';
import useAppStore from '../store/useAppStore';
import { uploadPdf } from '../api';
import '../styles/PdfSelector.css';

export default function PdfSelector() {
  const selectedChatId     = useAppStore((s) => s.selectedChatId);
  const chats              = useAppStore((s) => s.chats);
  const addPdf             = useAppStore((s) => s.addPdf);
  const removePdf          = useAppStore((s) => s.removePdf);
  const togglePdfSelection = useAppStore((s) => s.togglePdfSelection);

  // Derive directly — no function selector
  const chat = chats.find((c) => c.id === selectedChatId) ?? null;

  const fileRef = useRef();
  const [uploading, setUploading]     = useState(false);
  const [uploadError, setUploadError] = useState('');

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    e.target.value = '';
    if (!file || !selectedChatId) return;

    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadError('Only PDF files are accepted.');
      return;
    }

    setUploadError('');
    setUploading(true);
    try {
      const pdf = await uploadPdf(file);   // { id, name, path }
      addPdf(selectedChatId, pdf);
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const canUpload = chat && chat.pdfs.length < 2 && !uploading;

  return (
    <aside className="pdf-selector">
      <div className="pdf-selector-header">
        <span className="pdf-selector-title">📎 Documents</span>
      </div>

      {!chat ? (
        <p className="pdf-hint">Open a chat to manage PDFs.</p>
      ) : (
        <>
          {/* ── Upload button ── */}
          <div className="pdf-upload-area">
            <input
              ref={fileRef}
              type="file"
              accept=".pdf"
              style={{ display: 'none' }}
              onChange={handleUpload}
            />
            <button
              className="upload-btn"
              onClick={() => { setUploadError(''); fileRef.current.click(); }}
              disabled={!canUpload}
              title={canUpload ? 'Upload a PDF (max 2)' : 'Max 2 PDFs per chat'}
            >
              {uploading ? '⏳ Uploading…' : '＋ Upload PDF'}
            </button>
            {uploadError && <p className="pdf-error">{uploadError}</p>}
            {!canUpload && !uploading && chat.pdfs.length >= 2 && (
              <p className="pdf-hint">Max 2 PDFs per chat.</p>
            )}
          </div>

          {/* ── PDF list ── */}
          <div className="pdf-list">
            {chat.pdfs.length === 0 ? (
              <p className="pdf-hint">No PDFs uploaded yet.</p>
            ) : (
              chat.pdfs.map((pdf) => {
                const selected = chat.selectedPdfIds.includes(pdf.id);
                return (
                  <div key={pdf.id} className={`pdf-item ${selected ? 'pdf-selected' : ''}`}>
                    <label className="pdf-label">
                      <input
                        type="checkbox"
                        checked={selected}
                        onChange={() => togglePdfSelection(selectedChatId, pdf.id)}
                      />
                      <span className="pdf-icon">📄</span>
                      <span className="pdf-name" title={pdf.name}>{pdf.name}</span>
                    </label>
                    <button
                      className="icon-btn sm danger"
                      onClick={() => removePdf(selectedChatId, pdf.id)}
                      title="Remove"
                    >✕</button>
                  </div>
                );
              })
            )}
          </div>

          {/* ── Mode badge ── */}
          <div className="pdf-mode-badge">
            {chat.selectedPdfIds.length === 0 && <span className="badge badge-off">No PDF selected</span>}
            {chat.selectedPdfIds.length === 1 && <span className="badge badge-single">Single mode</span>}
            {chat.selectedPdfIds.length === 2 && <span className="badge badge-dual">Dual compare mode</span>}
          </div>
        </>
      )}
    </aside>
  );
}
