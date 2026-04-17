import { useState } from 'react';
import '../styles/InputBar.css';

export default function InputBar({ onSend, disabled, loading }) {
  const [text, setText] = useState('');

  const handleSend = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled || loading) return;
    onSend(trimmed);
    setText('');
  };

  const handleKey = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="inputbar-wrapper">
      <div className={`inputbar ${disabled ? 'inputbar-disabled' : ''}`}>
        <textarea
          className="inputbar-textarea"
          placeholder={disabled ? 'Select at least one PDF to start chatting…' : 'Ask anything about your documents…'}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKey}
          disabled={disabled || loading}
          rows={1}
        />
        <button
          className="send-btn"
          onClick={handleSend}
          disabled={disabled || loading || !text.trim()}
          title="Send"
        >
          {loading ? '⏳' : '➤'}
        </button>
      </div>
      {disabled && (
        <p className="inputbar-hint">Upload and select PDFs in the right panel to enable chat.</p>
      )}
    </div>
  );
}
