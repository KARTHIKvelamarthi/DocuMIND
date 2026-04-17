import { useState } from 'react';
import { login, register } from '../api';
import useAppStore from '../store/useAppStore';
import '../styles/LoginModal.css';

export default function LoginModal() {
  const setUser = useAppStore((s) => s.login);  // login(username, token)

  // 'login' | 'register'
  const [mode, setMode]         = useState('login');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [success, setSuccess]   = useState('');
  const [loading, setLoading]   = useState(false);

  const switchMode = (m) => {
    setMode(m);
    setError('');
    setSuccess('');
    setUsername('');
    setPassword('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      if (mode === 'login') {
        const res = await login(username, password);
        setUser(res.username, res.token);
      } else {
        await register(username, password);
        setSuccess('Account created! You can now log in.');
        switchMode('login');
      }
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

        <div className="auth-tabs">
          <button
            className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
            onClick={() => switchMode('login')}
            type="button"
          >Login</button>
          <button
            className={`auth-tab ${mode === 'register' ? 'active' : ''}`}
            onClick={() => switchMode('register')}
            type="button"
          >Register</button>
        </div>

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

          {error   && <p className="login-error">{error}</p>}
          {success && <p className="login-success">{success}</p>}

          <button type="submit" disabled={loading}>
            {loading
              ? (mode === 'login' ? 'Signing in…' : 'Creating account…')
              : (mode === 'login' ? 'Login' : 'Create Account')}
          </button>
        </form>
      </div>
    </div>
  );
}
