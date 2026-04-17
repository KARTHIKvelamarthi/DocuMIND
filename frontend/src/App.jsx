import { Component } from 'react';
import useAppStore from './store/useAppStore';
import LoginModal from './components/LoginModal';
import MainPage from './pages/MainPage';
import './styles/global.css';

// Error boundary catches render crashes and shows a readable message
class ErrorBoundary extends Component {
  state = { error: null };
  static getDerivedStateFromError(error) { return { error }; }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 40, fontFamily: 'monospace', color: '#dc2626', background: '#fdf2f2', minHeight: '100vh' }}>
          <h2>Something went wrong</h2>
          <pre style={{ marginTop: 16, whiteSpace: 'pre-wrap' }}>{this.state.error.message}</pre>
          <button
            style={{ marginTop: 24, padding: '8px 16px', cursor: 'pointer' }}
            onClick={() => { localStorage.removeItem('documind-storage'); window.location.reload(); }}
          >
            Clear storage &amp; reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function AppInner() {
  const user = useAppStore((s) => s.user);
  return (
    <>
      {!user && <LoginModal />}
      <MainPage />
    </>
  );
}

export default function App() {
  return (
    <ErrorBoundary>
      <AppInner />
    </ErrorBoundary>
  );
}
