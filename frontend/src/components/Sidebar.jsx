import { useShallow } from 'zustand/react/shallow';
import useAppStore from '../store/useAppStore';
import GroupList from './GroupList';
import '../styles/Sidebar.css';

export default function Sidebar() {
  const user            = useAppStore((s) => s.user);
  const logout          = useAppStore((s) => s.logout);
  const createGroup     = useAppStore((s) => s.createGroup);
  const createChat      = useAppStore((s) => s.createChat);
  const selectedGroupId = useAppStore((s) => s.users[s.user?.username]?.selectedGroupId ?? null);

  const groups = useAppStore(
    useShallow((s) => s.users[s.user?.username]?.groups ?? [])
  );

  const handleNewChat = () => {
    if (groups.length === 0) {
      const gid = createGroup('Default');
      createChat(gid);
    } else {
      createChat(selectedGroupId ?? groups[0].id);
    }
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="sidebar-brand">
          <span className="brand-icon">🧠</span>
          <span className="brand-name">DocuMind</span>
        </div>
        <button className="new-chat-btn" onClick={handleNewChat}>＋ New Chat</button>
      </div>
      <div className="sidebar-body"><GroupList /></div>
      <div className="sidebar-footer">
        <span className="user-badge">👤 {user?.username}</span>
        <button className="logout-btn" onClick={logout}>Logout</button>
      </div>
    </aside>
  );
}
