import useAppStore from '../store/useAppStore';
import { useShallow } from 'zustand/react/shallow';
import '../styles/NoChatState.css';

export default function NoChatState() {
  const createGroup = useAppStore((s) => s.createGroup);
  const createChat  = useAppStore((s) => s.createChat);
  const groups      = useAppStore(useShallow((s) => s.users[s.user?.username]?.groups ?? []));

  const handleNewChat = () => {
    if (groups.length === 0) {
      const gid = createGroup('Default');
      createChat(gid);
    } else {
      createChat(groups[0].id);
    }
  };

  return (
    <div className="no-chat-state">
      <div className="no-chat-inner">
        <span className="no-chat-icon">🧠</span>
        <h2 className="no-chat-title">Welcome to DocuMind</h2>
        <p className="no-chat-sub">
          Create a new chat or open an existing one to continue
        </p>
        <button className="no-chat-btn" onClick={handleNewChat}>
          ＋ New Chat
        </button>
      </div>
    </div>
  );
}
