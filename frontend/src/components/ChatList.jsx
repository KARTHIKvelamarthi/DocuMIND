import { useState } from 'react';
import { useShallow } from 'zustand/react/shallow';
import useAppStore from '../store/useAppStore';

export default function ChatList({ groupId }) {
  const selectedChatId = useAppStore((s) => s.users[s.user?.username]?.selectedChatId ?? null);

  const groupChats = useAppStore(
    useShallow((s) => (s.users[s.user?.username]?.chats ?? []).filter((c) => c.groupId === groupId))
  );

  const selectChat = useAppStore((s) => s.selectChat);
  const renameChat = useAppStore((s) => s.renameChat);
  const deleteChat = useAppStore((s) => s.deleteChat);

  const [editingId, setEditingId] = useState(null);
  const [editName, setEditName]   = useState('');

  const startEdit = (e, chat) => {
    e.stopPropagation();
    setEditingId(chat.id);
    setEditName(chat.name);
  };

  const commitEdit = (chatId) => {
    if (editName.trim()) renameChat(chatId, editName.trim());
    setEditingId(null);
  };

  if (groupChats.length === 0) return <p className="empty-hint indent">No chats yet.</p>;

  return (
    <div className="chat-list">
      {groupChats.map((chat) => (
        <div
          key={chat.id}
          className={`chat-item ${selectedChatId === chat.id ? 'active' : ''}`}
          onClick={() => selectChat(chat.id)}
        >
          <span className="chat-icon">💬</span>

          {editingId === chat.id ? (
            <input
              className="inline-edit"
              value={editName}
              autoFocus
              onChange={(e) => setEditName(e.target.value)}
              onBlur={() => commitEdit(chat.id)}
              onKeyDown={(e) => e.key === 'Enter' && commitEdit(chat.id)}
              onClick={(e) => e.stopPropagation()}
            />
          ) : (
            <span className="chat-name">{chat.name}</span>
          )}

          <div className="chat-actions">
            <button className="icon-btn sm" onClick={(e) => startEdit(e, chat)}>✏️</button>
            <button className="icon-btn sm danger"
              onClick={(e) => { e.stopPropagation(); deleteChat(chat.id); }}>🗑</button>
          </div>
        </div>
      ))}
    </div>
  );
}
