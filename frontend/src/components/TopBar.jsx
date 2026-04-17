import { useShallow } from 'zustand/react/shallow';
import useAppStore from '../store/useAppStore';
import '../styles/TopBar.css';

export default function TopBar() {
  const selectChat      = useAppStore((s) => s.selectChat);
  const selectedGroupId = useAppStore((s) => s.users[s.user?.username]?.selectedGroupId ?? null);
  const selectedChatId  = useAppStore((s) => s.users[s.user?.username]?.selectedChatId  ?? null);

  const groups = useAppStore(
    useShallow((s) => s.users[s.user?.username]?.groups ?? [])
  );
  const chats = useAppStore(
    useShallow((s) => s.users[s.user?.username]?.chats ?? [])
  );

  const group      = groups.find((g) => g.id === selectedGroupId) ?? null;
  const groupChats = chats.filter((c) => c.groupId === selectedGroupId);

  return (
    <header className="topbar">
      <div className="topbar-left">
        {group
          ? <span className="topbar-group-name">📁 {group.name}</span>
          : <span className="topbar-placeholder">Select a group to see chats</span>}
      </div>
      <div className="topbar-chats">
        {groupChats.map((chat) => (
          <button
            key={chat.id}
            className={`topbar-chat-tab ${selectedChatId === chat.id ? 'active' : ''}`}
            onClick={() => selectChat(chat.id)}
          >
            {chat.name}
          </button>
        ))}
      </div>
    </header>
  );
}
