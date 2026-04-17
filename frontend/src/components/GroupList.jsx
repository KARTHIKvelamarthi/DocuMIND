import { useState } from 'react';
import { useShallow } from 'zustand/react/shallow';
import useAppStore from '../store/useAppStore';
import ChatList from './ChatList';

export default function GroupList() {
  const username = useAppStore((s) => s.user?.username);
  const selectedGroupId = useAppStore((s) => s.users[username]?.selectedGroupId ?? null);

  // useShallow prevents new-reference re-renders for arrays
  const groups = useAppStore(
    useShallow((s) => s.users[s.user?.username]?.groups ?? [])
  );

  const createGroup = useAppStore((s) => s.createGroup);
  const renameGroup = useAppStore((s) => s.renameGroup);
  const deleteGroup = useAppStore((s) => s.deleteGroup);
  const selectGroup = useAppStore((s) => s.selectGroup);
  const createChat  = useAppStore((s) => s.createChat);

  const [newGroupName, setNewGroupName] = useState('');
  const [editingId, setEditingId]       = useState(null);
  const [editName, setEditName]         = useState('');

  const handleCreate = () => {
    createGroup(newGroupName.trim() || 'New Group');
    setNewGroupName('');
  };

  const startEdit = (e, group) => {
    e.stopPropagation();
    setEditingId(group.id);
    setEditName(group.name);
  };

  const commitEdit = (groupId) => {
    if (editName.trim()) renameGroup(groupId, editName.trim());
    setEditingId(null);
  };

  return (
    <div className="group-list">
      <div className="new-group-row">
        <input
          placeholder="Group name…"
          value={newGroupName}
          onChange={(e) => setNewGroupName(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleCreate()}
        />
        <button className="icon-btn" onClick={handleCreate} title="Create group">＋</button>
      </div>

      {groups.length === 0 && <p className="empty-hint">No groups yet.</p>}

      {groups.map((group) => (
        <div key={group.id} className="group-item">
          <div
            className={`group-header ${selectedGroupId === group.id ? 'active' : ''}`}
            onClick={() => selectGroup(selectedGroupId === group.id ? null : group.id)}
          >
            <span className="group-icon">📁</span>

            {editingId === group.id ? (
              <input
                className="inline-edit"
                value={editName}
                autoFocus
                onChange={(e) => setEditName(e.target.value)}
                onBlur={() => commitEdit(group.id)}
                onKeyDown={(e) => e.key === 'Enter' && commitEdit(group.id)}
                onClick={(e) => e.stopPropagation()}
              />
            ) : (
              <span className="group-name">{group.name}</span>
            )}

            <div className="group-actions">
              <button className="icon-btn sm" onClick={(e) => startEdit(e, group)}>✏️</button>
              <button className="icon-btn sm danger"
                onClick={(e) => { e.stopPropagation(); deleteGroup(group.id); }}>🗑</button>
              <button className="icon-btn sm"
                onClick={(e) => { e.stopPropagation(); createChat(group.id); }}>💬</button>
            </div>
          </div>

          {selectedGroupId === group.id && <ChatList groupId={group.id} />}
        </div>
      ))}
    </div>
  );
}
