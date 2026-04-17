import useAppStore from '../store/useAppStore';
import '../styles/TopBar.css';

export default function TopBar() {
  const selectedGroupId = useAppStore((s) => s.selectedGroupId);
  const selectedChatId  = useAppStore((s) => s.selectedChatId);
  const groups          = useAppStore((s) => s.groups);
  const chats           = useAppStore((s) => s.chats);
  const selectChat      = useAppStore((s) => s.selectChat);

  const group      = groups.find((g) => g.id === selectedGroupId) ?? null;
  const groupChats = chats.filter((c) => c.groupId === selectedGroupId);

  return (
    <header className="topbar">
      <div className="topbar-left">
        {group
          ? <span className="topbar-group-name">📁 {group.name}</span>
          : <span className="topbar-placeholder">Select a group to see chats</span>
        }
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
