import { useEffect, useRef, useState } from 'react';
import useAppStore from '../store/useAppStore';
import { sendQuery } from '../api';
import MessageBubble from './MessageBubble';
import InputBar from './InputBar';
import FeatureGrid from './FeatureGrid';
import '../styles/ChatArea.css';

export default function ChatArea() {
  const selectedChatId = useAppStore((s) => s.selectedChatId);
  const chats          = useAppStore((s) => s.chats);
  const addMessage     = useAppStore((s) => s.addMessage);

  // Derive active chat directly — no function call in selector
  const chat = chats.find((c) => c.id === selectedChatId) ?? null;

  const [loading, setLoading] = useState(false);
  const bottomRef = useRef();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chat?.messages?.length]);

  const handleSend = async (text) => {
    if (!chat || chat.selectedPdfIds.length === 0) return;

    const selectedPdfs = chat.pdfs.filter((p) => chat.selectedPdfIds.includes(p.id));

    addMessage(selectedChatId, {
      id:        crypto.randomUUID(),
      role:      'user',
      content:   text,
      timestamp: Date.now(),
    });

    setLoading(true);
    try {
      const result = await sendQuery(text, selectedPdfs, selectedChatId);
      addMessage(selectedChatId, {
        id:          crypto.randomUUID(),
        role:        'assistant',
        content:     result.answer,
        doc1_answer: result.doc1_answer || '',
        doc2_answer: result.doc2_answer || '',
        comparison:  result.comparison  || '',
        images:      result.images      || [],
        tables:      result.tables      || [],
        visuals:     result.visuals     || '',
        timestamp:   Date.now(),
      });
    } catch (err) {
      addMessage(selectedChatId, {
        id:        crypto.randomUUID(),
        role:      'assistant',
        content:   `⚠️ ${err.message}`,
        timestamp: Date.now(),
      });
    } finally {
      setLoading(false);
    }
  };

  const noChat        = !chat;
  const noPdfSelected = chat && chat.selectedPdfIds.length === 0;
  const isEmpty       = chat && chat.messages.length === 0;

  return (
    <main className="chat-area">
      <div className="chat-messages">
        {noChat || isEmpty ? (
          <FeatureGrid />
        ) : (
          chat.messages.map((msg) => (
            <MessageBubble key={msg.id} message={msg} />
          ))
        )}

        {loading && (
          <div className="bubble-row assistant">
            <div className="bubble-avatar">🧠</div>
            <div className="bubble bubble-assistant typing">
              <span className="dot" /><span className="dot" /><span className="dot" />
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <InputBar
        onSend={handleSend}
        disabled={noChat || noPdfSelected}
        loading={loading}
      />
    </main>
  );
}
