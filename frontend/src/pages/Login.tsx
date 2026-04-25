import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google';
import { Music, Loader2 } from 'lucide-react';
import { authGoogle, getAuthConfig } from '../api';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [googleClientId, setGoogleClientId] = useState(
    (import.meta.env.VITE_GOOGLE_CLIENT_ID as string) || ''
  );
  const [authConfigLoading, setAuthConfigLoading] = useState(
    !((import.meta.env.VITE_GOOGLE_CLIENT_ID as string) || '')
  );

  const saveSession = (u: {
    username: string;
    id: number;
    session_token: string;
    display_name: string;
    email?: string;
  }) => {
    localStorage.setItem(
      'user',
      JSON.stringify({
        username: u.username,
        id: u.id,
        session_token: u.session_token,
        display_name: u.display_name,
        ...(u.email ? { email: u.email } : {}),
      })
    );
  };

  useEffect(() => {
    const fromEnv = (import.meta.env.VITE_GOOGLE_CLIENT_ID as string) || '';
    if (fromEnv) {
      setAuthConfigLoading(false);
      return;
    }
    let cancelled = false;
    (async () => {
      try {
        const cfg = await getAuthConfig();
        if (!cancelled && cfg.google_client_id) {
          setGoogleClientId(cfg.google_client_id);
        }
      } catch {
        /* backend offline or CORS */
      } finally {
        if (!cancelled) setAuthConfigLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

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

        {!authConfigLoading && !googleClientId && (
          <p
            style={{
              width: '100%',
              textAlign: 'center',
              fontSize: '0.875rem',
              color: 'var(--error-color)',
              lineHeight: 1.5,
            }}
          >
            Google Sign-In is not configured. Set <code>GOOGLE_OAUTH_CLIENT_ID</code> in{' '}
            <code>backend/.env</code>, run the API, then refresh this page.
          </p>
        )}

        {googleClientId && (
          <div
            style={{
              width: '100%',
              display: 'flex',
              justifyContent: 'center',
            }}
          >
            <GoogleOAuthProvider clientId={googleClientId}>
              <GoogleLogin
                onSuccess={async (cred) => {
                  if (!cred.credential) return;
                  setIsLoading(true);
                  setError('');
                  try {
                    const user = await authGoogle(cred.credential);
                    saveSession(user);
                    navigate('/generate');
                  } catch (err: any) {
                    setError(
                      err.message ||
                        'Google sign-in failed. Check GOOGLE_OAUTH_CLIENT_ID in backend .env.'
                    );
                  } finally {
                    setIsLoading(false);
                  }
                }}
                onError={() => setError('Google sign-in was cancelled or failed.')}
              />
            </GoogleOAuthProvider>
          </div>
        )}

        {isLoading && (
          <p
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              marginTop: '1rem',
              color: 'var(--text-secondary)',
            }}
          >
            <Loader2 size={16} style={{ animation: 'spin 1s linear infinite' }} />
            Signing in…
          </p>
        )}

        <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </div>
    </div>
  );
};

export default Login;
