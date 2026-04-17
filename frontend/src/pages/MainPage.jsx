import Sidebar from '../components/Sidebar';
import TopBar from '../components/TopBar';
import ChatArea from '../components/ChatArea';
import PdfSelector from '../components/PdfSelector';
import '../styles/MainPage.css';

export default function MainPage() {
  return (
    <div className="app-layout">
      <Sidebar />
      <div className="app-center">
        <TopBar />
        <ChatArea />
      </div>
      <PdfSelector />
    </div>
  );
}
