import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Loader2, Music } from 'lucide-react';

const AuthCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [message, setMessage] = useState('Completing sign-in…');

  useEffect(() => {
    const err = searchParams.get('error');
    const detail = searchParams.get('detail');
    if (err) {
      setMessage(detail || err);
      return;
    }

    const sessionToken = searchParams.get('session_token');
    const idRaw = searchParams.get('id');
    const username = searchParams.get('username');
    const displayName = searchParams.get('display_name');
    const email = searchParams.get('email');

    if (!sessionToken || !idRaw || !username || !displayName) {
      setMessage('Sign-in response was incomplete. Try again from the login page.');
      return;
    }

    const id = parseInt(idRaw, 10);
    if (Number.isNaN(id) || id <= 0) {
      setMessage('Invalid user id from server.');
      return;
    }

    localStorage.setItem(
      'user',
      JSON.stringify({
        username,
        id,
        session_token: sessionToken,
        display_name: displayName,
        ...(email ? { email } : {}),
      })
    );
    navigate('/generate', { replace: true });
  }, [searchParams, navigate]);

  const isError =
    message !== 'Completing sign-in…' &&
    !message.startsWith('Redirecting');

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '1.5rem',
      }}
    >
      <div
        className="glass-panel animate-fade-in"
        style={{
          width: '100%',
          maxWidth: '400px',
          padding: '2rem',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: '1rem',
        }}
      >
        <div
          style={{
            width: '48px',
            height: '48px',
            borderRadius: '16px',
            background: 'linear-gradient(135deg, var(--accent-color), #ea580c)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Music size={24} color="white" />
        </div>
        {isError ? (
          <>
            <h1 style={{ fontSize: '1.125rem', textAlign: 'center' }}>Sign-in failed</h1>
            <p
              style={{
                textAlign: 'center',
                color: 'var(--text-secondary)',
                fontSize: '0.875rem',
                lineHeight: 1.5,
              }}
            >
              {message}
            </p>
            <button
              type="button"
              className="btn-primary"
              style={{ marginTop: '0.5rem' }}
              onClick={() => navigate('/login', { replace: true })}
            >
              Back to login
            </button>
          </>
        ) : (
          <p
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              color: 'var(--text-secondary)',
            }}
          >
            <Loader2 size={18} style={{ animation: 'spin 1s linear infinite' }} />
            {message}
          </p>
        )}
        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    </div>
  );
};

export default AuthCallback;
