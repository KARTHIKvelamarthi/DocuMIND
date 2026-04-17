import '../styles/MessageBubble.css';

const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

// Render a 2-D array as an HTML table. First row is treated as header.
function TableView({ rows }) {
  if (!rows || rows.length === 0) return null;
  const [head, ...body] = rows;
  return (
    <table className="extracted-table">
      <thead>
        <tr>
          {head.map((cell, i) => (
            <th key={i}>{cell ?? ''}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {body.map((row, ri) => (
          <tr key={ri}>
            {row.map((cell, ci) => (
              <td key={ci}>{cell ?? ''}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  const isDual = !isUser && (message.doc1_answer || message.doc2_answer);

  return (
    <div className={`bubble-row ${isUser ? 'user' : 'assistant'}`}>
      <div className="bubble-avatar">{isUser ? '👤' : '🧠'}</div>

      <div className={`bubble ${isUser ? 'bubble-user' : 'bubble-assistant'}`}>

        {/* ── Dual-doc structured answer ── */}
        {isDual ? (
          <div className="dual-answer">
            {message.doc1_answer && (
              <div className="dual-section">
                <span className="dual-label">Doc 1</span>
                <p className="bubble-text">{message.doc1_answer}</p>
              </div>
            )}
            {message.doc2_answer && (
              <div className="dual-section">
                <span className="dual-label">Doc 2</span>
                <p className="bubble-text">{message.doc2_answer}</p>
              </div>
            )}
            {message.comparison && (
              <div className="dual-section comparison">
                <span className="dual-label">Comparison</span>
                <p className="bubble-text">{message.comparison}</p>
              </div>
            )}
          </div>
        ) : (
          <p className="bubble-text">{message.content}</p>
        )}

        {/* ── Images ── */}
        {message.images?.length > 0 && (
          <div className="bubble-images">
            <p className="visuals-label">🖼️ Extracted Images</p>
            <div className="image-grid">
              {message.images.map((imgPath, i) => {
                const filename = imgPath.replace(/\\/g, '/').split('/').pop();
                const src = `${BASE_URL}/assets/images/${filename}`;
                return (
                  <a key={i} href={src} target="_blank" rel="noreferrer">
                    <img src={src} alt={`extracted-${i}`} className="extracted-img" />
                  </a>
                );
              })}
            </div>
          </div>
        )}

        {/* ── Tables ── */}
        {message.tables?.length > 0 && (
          <div className="bubble-tables">
            <p className="visuals-label">📊 Extracted Tables</p>
            {message.tables.map((rows, i) => (
              <div key={i} className="table-wrapper">
                <TableView rows={rows} />
              </div>
            ))}
          </div>
        )}

        <span className="bubble-time">
          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
}
