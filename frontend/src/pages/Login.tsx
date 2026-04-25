import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Music, ArrowRight, Loader2 } from 'lucide-react';
import { getOrCreateUser } from '../api';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) return;
    setIsLoading(true);
    setError('');

    try {
      const user = await getOrCreateUser({ username: username.trim() });
      localStorage.setItem(
        'user',
        JSON.stringify({ username: user.username, id: user.id })
      );
      navigate('/generate');
    } catch (err: any) {
      setError(err.message || 'Could not connect to the server. Make sure the backend is running at http://127.0.0.1:8000');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      minHeight: '100vh', padding: '1.5rem', position: 'relative', overflow: 'hidden'
    }}>
      <div style={{
        position: 'absolute', width: '600px', height: '600px',
        background: 'radial-gradient(circle, var(--accent-glow) 0%, transparent 70%)',
        top: '50%', left: '50%', transform: 'translate(-50%, -50%)',
        zIndex: 0, pointerEvents: 'none', opacity: 0.5
      }} />

      <div className="glass-panel animate-fade-in" style={{
        width: '100%', maxWidth: '400px', padding: '3rem 2rem',
        position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center'
      }}>
        <div style={{
          width: '64px', height: '64px', borderRadius: '20px',
          background: 'linear-gradient(135deg, var(--accent-color), #ea580c)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          marginBottom: '2rem', boxShadow: '0 8px 16px var(--accent-glow)'
        }}>
          <Music size={32} color="white" />
        </div>

        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Welcome</h1>
        <p style={{ textAlign: 'center', marginBottom: '2.5rem', color: 'var(--text-secondary)' }}>
          Sign in to start creating AI-generated music.
        </p>

        {error && (
          <div style={{
            width: '100%', padding: '0.75rem', marginBottom: '1rem',
            backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)',
            borderRadius: 'var(--radius-md)', color: 'var(--error-color)', fontSize: '0.875rem'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} style={{ width: '100%', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              Display Name
            </label>
            <input
              type="text"
              className="input-field"
              placeholder="Enter your name"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            className="btn-primary"
            style={{ width: '100%', padding: '0.875rem', marginTop: '0.5rem' }}
            disabled={isLoading || !username.trim()}
          >
            {isLoading
              ? <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
              : <ArrowRight size={18} />
            }
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    </div>
  );
};

export default Login;
