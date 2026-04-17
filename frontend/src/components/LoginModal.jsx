import { useState } from 'react';
import { login } from '../api';
import useAppStore from '../store/useAppStore';
import '../styles/LoginModal.css';

export default function LoginModal() {
  const setUser = useAppStore((s) => s.login);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(username, password);
      setUser(user.username);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-overlay">
      <div className="login-box">
        <div className="login-logo">
          <span className="login-logo-icon">🧠</span>
          <h1>DocuMind</h1>
        </div>
        <p className="login-subtitle">Sign in to continue</p>

        <form onSubmit={handleSubmit} className="login-form">
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            autoFocus
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <p className="login-error">{error}</p>}
          <button type="submit" disabled={loading}>
            {loading ? 'Signing in…' : 'Login'}
          </button>
        </form>
      </div>
    </div>
  );
}
