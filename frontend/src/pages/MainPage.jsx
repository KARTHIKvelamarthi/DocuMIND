import { useShallow } from 'zustand/react/shallow';
import useAppStore from '../store/useAppStore';
import Sidebar from '../components/Sidebar';
import TopBar from '../components/TopBar';
import ChatArea from '../components/ChatArea';
import PdfSelector from '../components/PdfSelector';
import NoChatState from '../components/NoChatState';
import '../styles/MainPage.css';

export default function MainPage() {
  const chat = useAppStore(
    useShallow((s) => {
      const u  = s.user?.username;
      const id = s.users[u]?.selectedChatId;
      return s.users[u]?.chats?.find((c) => c.id === id) ?? null;
    })
  );

  const hasChat = !!chat;

  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-center">
        <TopBar />
        {hasChat ? <ChatArea /> : <NoChatState />}
      </div>
      {/* Floating PDF panel — only shown when a chat is active */}
      {hasChat && <PdfSelector />}
    </div>
  );
}
