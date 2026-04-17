import { Component } from 'react';
import useAppStore from './store/useAppStore';
import LoginModal from './components/LoginModal';
import MainPage from './pages/MainPage';
import './styles/global.css';

function hardReset() {
  localStorage.clear();
  sessionStorage.clear();
  window.location.href = window.location.href; // force full reload
}

class ErrorBoundary extends Component {
  state = { error: null };
  static getDerivedStateFromError(error) { return { error }; }
  render() {
    if (this.state.error) {
      return (
        <div style={{
          padding: 40, fontFamily: 'monospace', color: '#dc2626',
          background: '#fdf2f2', minHeight: '100vh'
        }}>
          <h2>Something went wrong</h2>
          <pre style={{ marginTop: 16, whiteSpace: 'pre-wrap', fontSize: 13 }}>
            {this.state.error.message}
          </pre>
          <button
            style={{
              marginTop: 24, padding: '10px 20px', cursor: 'pointer',
              background: '#dc2626', color: '#fff', border: 'none',
              borderRadius: 8, fontSize: 14, fontWeight: 600
            }}
            onClick={hardReset}
          >
            Clear all data &amp; reload
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
