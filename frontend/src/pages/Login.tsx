import React, { useEffect, useState } from 'react';
import { Music } from 'lucide-react';
import { getAuthConfig } from '../api';

const Login: React.FC = () => {
  const [error, setError] = useState('');
  const [googleLoginUrl, setGoogleLoginUrl] = useState('');
  const [oauthReady, setOauthReady] = useState(false);
  const [authConfigLoading, setAuthConfigLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const cfg = await getAuthConfig();
        if (cancelled) return;
        setGoogleLoginUrl(cfg.google_login_url || '');
        setOauthReady(Boolean(cfg.google_oauth_ready));
        if (!cfg.google_client_id) {
          setError('');
        }
      } catch {
        if (!cancelled) {
          setError('Cannot reach the API. Start the Django server at http://127.0.0.1:8000 and refresh.');
        }
      } finally {
        if (!cancelled) setAuthConfigLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const startGoogleLogin = () => {
    if (!googleLoginUrl) return;
    window.location.href = googleLoginUrl;
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        padding: '1.5rem',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'absolute',
          width: '600px',
          height: '600px',
          background: 'radial-gradient(circle, var(--accent-glow) 0%, transparent 70%)',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          zIndex: 0,
          pointerEvents: 'none',
          opacity: 0.5,
        }}
      />

      <div
        className="glass-panel animate-fade-in"
        style={{
          width: '100%',
          maxWidth: '400px',
          padding: '3rem 2rem',
          position: 'relative',
          zIndex: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <div
          style={{
            width: '64px',
            height: '64px',
            borderRadius: '20px',
            background: 'linear-gradient(135deg, var(--accent-color), #ea580c)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '2rem',
            boxShadow: '0 8px 16px var(--accent-glow)',
          }}
        >
          <Music size={32} color="white" />
        </div>

        <h1 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Welcome</h1>
        <p
          style={{
            textAlign: 'center',
            marginBottom: '2rem',
            color: 'var(--text-secondary)',
          }}
        >
          Sign in with your Google account to create AI-generated music.
        </p>

        {error && (
          <div
            style={{
              width: '100%',
              padding: '0.75rem',
              marginBottom: '1rem',
              backgroundColor: 'rgba(239,68,68,0.1)',
              border: '1px solid rgba(239,68,68,0.2)',
              borderRadius: 'var(--radius-md)',
              color: 'var(--error-color)',
              fontSize: '0.875rem',
            }}
          >
            {error}
          </div>
        )}

        {authConfigLoading && (
          <p
            style={{
              width: '100%',
              textAlign: 'center',
              margin: '0 0 1rem',
              fontSize: '0.8rem',
              color: 'var(--text-secondary)',
            }}
          >
            Loading sign-in…
          </p>
        )}

        {!authConfigLoading && !oauthReady && (
          <p
            style={{
              width: '100%',
              textAlign: 'center',
              fontSize: '0.875rem',
              color: 'var(--error-color)',
              lineHeight: 1.5,
            }}
          >
            Google OAuth is not fully configured. Set <code>GOOGLE_OAUTH_CLIENT_ID</code> and{' '}
            <code>GOOGLE_OAUTH_CLIENT_SECRET</code> in <code>backend/.env</code>, add the backend
            callback URL in Google Cloud (see README), restart the API, then refresh.
          </p>
        )}

        {!authConfigLoading && oauthReady && googleLoginUrl && (
          <button
            type="button"
            onClick={startGoogleLogin}
            style={{
              width: '100%',
              maxWidth: '280px',
              padding: '0.75rem 1.25rem',
              borderRadius: 'var(--radius-md)',
              border: '1px solid rgba(255,255,255,0.12)',
              background: 'rgba(255,255,255,0.06)',
              color: 'var(--text-primary)',
              fontSize: '0.9375rem',
              fontWeight: 500,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '0.75rem',
            }}
          >
            <svg width="20" height="20" viewBox="0 0 48 48" aria-hidden>
              <path
                fill="#FFC107"
                d="M43.611 20.083H42V20H24v8h11.303c-1.649 4.657-6.08 8-11.303 8-6.627 0-12-5.373-12-12s5.373-12 12-12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 12.955 4 4 12.955 4 24s8.955 20 20 20 20-8.955 20-20c0-1.341-.138-2.65-.389-3.917z"
              />
              <path
                fill="#FF3D00"
                d="m6.306 14.691 6.571 4.819C14.655 15.108 18.961 12 24 12c3.059 0 5.842 1.154 7.961 3.039l5.657-5.657C34.046 6.053 29.268 4 24 4 16.318 4 9.656 8.337 6.306 14.691z"
              />
              <path
                fill="#4CAF50"
                d="M24 44c5.166 0 9.86-1.977 13.409-5.192l-6.19-5.238A11.91 11.91 0 0 1 24 36c-5.202 0-9.619-3.317-11.283-7.946l-6.522 5.025C9.505 39.556 16.227 44 24 44z"
              />
              <path
                fill="#1976D2"
                d="M43.611 20.083H42V20H24v8h11.303a12.04 12.04 0 0 1-4.087 5.571l.003-.002 6.19 5.238C36.971 39.205 44 34 44 24c0-1.341-.138-2.65-.389-3.917z"
              />
            </svg>
            Continue with Google
          </button>
        )}

        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    </div>
  );
};

export default Login;
