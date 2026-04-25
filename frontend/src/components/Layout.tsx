import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  Music, Wand2, Library, LogOut, Play, Pause,
  SkipForward, Repeat, FlaskConical, Zap, X, CheckCircle2, AlertCircle, Volume2
} from 'lucide-react';
import { getGenerationConfig, setGenerationStrategy } from '../api';

// ── Strategy Switcher Modal ──────────────────────────────────────────────────

interface StrategyModalProps {
  current: 'mock' | 'suno';
  sunoConfigured: boolean;
  loading: boolean;
  onSelect: (s: 'mock' | 'suno') => void;
  onClose: () => void;
}

const StrategyModal: React.FC<StrategyModalProps> = ({ current, sunoConfigured, loading, onSelect, onClose }) => (
  <div
    onClick={onClose}
    style={{
      position: 'fixed', inset: 0, zIndex: 1000,
      backgroundColor: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
    }}
  >
    <div
      onClick={e => e.stopPropagation()}
      className="glass-panel animate-fade-in"
      style={{ width: '100%', maxWidth: '440px', padding: '2rem', position: 'relative' }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h2 style={{ fontSize: '1.25rem', margin: 0 }}>Generation Strategy</h2>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: '0.25rem 0 0' }}>
            Choose how songs are generated
          </p>
        </div>
        <button onClick={onClose} style={{ color: 'var(--text-secondary)', padding: '0.25rem' }}>
          <X size={20} />
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
        {/* Mock */}
        <button
          onClick={() => onSelect('mock')} disabled={loading}
          style={{
            width: '100%', padding: '1.25rem', borderRadius: 'var(--radius-md)',
            border: `2px solid ${current === 'mock' ? 'var(--accent-color)' : 'var(--border-color)'}`,
            backgroundColor: current === 'mock' ? 'rgba(249,115,22,0.08)' : 'var(--bg-secondary)',
            textAlign: 'left', cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1, transition: 'all 0.2s ease',
            display: 'flex', alignItems: 'center', gap: '1rem',
          }}
        >
          <div style={{
            width: '44px', height: '44px', borderRadius: '12px', flexShrink: 0,
            backgroundColor: current === 'mock' ? 'rgba(249,115,22,0.15)' : 'rgba(255,255,255,0.05)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: current === 'mock' ? '1px solid rgba(249,115,22,0.3)' : '1px solid var(--border-color)',
          }}>
            <FlaskConical size={22} color={current === 'mock' ? 'var(--accent-color)' : 'var(--text-secondary)'} />
          </div>
          <div style={{ flexGrow: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Mock</span>
              <span style={{ fontSize: '0.7rem', padding: '0.1rem 0.5rem', borderRadius: 'var(--radius-pill)', backgroundColor: 'rgba(16,185,129,0.15)', color: 'var(--success-color)', border: '1px solid rgba(16,185,129,0.3)' }}>
                Offline
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>Instant, no API key needed. Great for testing.</p>
          </div>
          {current === 'mock' && <CheckCircle2 size={20} color="var(--accent-color)" />}
        </button>

        {/* Suno */}
        <button
          onClick={() => onSelect('suno')} disabled={loading}
          style={{
            width: '100%', padding: '1.25rem', borderRadius: 'var(--radius-md)',
            border: `2px solid ${current === 'suno' ? 'var(--accent-color)' : 'var(--border-color)'}`,
            backgroundColor: current === 'suno' ? 'rgba(249,115,22,0.08)' : 'var(--bg-secondary)',
            textAlign: 'left', cursor: loading ? 'not-allowed' : 'pointer',
            opacity: loading ? 0.6 : 1, transition: 'all 0.2s ease',
            display: 'flex', alignItems: 'center', gap: '1rem',
          }}
        >
          <div style={{
            width: '44px', height: '44px', borderRadius: '12px', flexShrink: 0,
            backgroundColor: current === 'suno' ? 'rgba(249,115,22,0.15)' : 'rgba(255,255,255,0.05)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            border: current === 'suno' ? '1px solid rgba(249,115,22,0.3)' : '1px solid var(--border-color)',
          }}>
            <Zap size={22} color={current === 'suno' ? 'var(--accent-color)' : 'var(--text-secondary)'} />
          </div>
          <div style={{ flexGrow: 1 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.2rem' }}>
              <span style={{ fontWeight: 600, color: 'var(--text-primary)' }}>Suno</span>
              <span style={{ fontSize: '0.7rem', padding: '0.1rem 0.5rem', borderRadius: 'var(--radius-pill)', backgroundColor: 'rgba(249,115,22,0.12)', color: 'var(--accent-color)', border: '1px solid rgba(249,115,22,0.3)' }}>
                Live API
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0 }}>Real AI generation via Suno. Requires API key.</p>
            {!sunoConfigured && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', marginTop: '0.4rem', fontSize: '0.75rem', color: '#f59e0b' }}>
                <AlertCircle size={13} /> SUNO_API_KEY not configured on the server
              </div>
            )}
          </div>
          {current === 'suno' && <CheckCircle2 size={20} color="var(--accent-color)" />}
        </button>
      </div>
      {loading && <p style={{ textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '1rem' }}>Switching strategy…</p>}
    </div>
  </div>
);

// ── helpers ──────────────────────────────────────────────────────────────────

function fmt(secs: number) {
  if (!secs || isNaN(secs)) return '0:00';
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

// ── Layout ───────────────────────────────────────────────────────────────────

export interface NowPlaying { title: string; url: string }

const Layout: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [user, setUser] = useState<{ username: string } | null>(null);

  // ── strategy ──
  const [strategy, setStrategy] = useState<'mock' | 'suno'>('mock');
  const [sunoConfigured, setSunoConfigured] = useState(false);
  const [strategyLoading, setStrategyLoading] = useState(false);
  const [showStrategyModal, setShowStrategyModal] = useState(false);

  // ── player ──
  const audioRef = useRef<HTMLAudioElement>(null);
  const [nowPlaying, setNowPlaying] = useState<NowPlaying | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) { navigate('/login'); } else { setUser(JSON.parse(userData)); }
    getGenerationConfig()
      .then(cfg => { setStrategy(cfg.generator_strategy as 'mock' | 'suno'); setSunoConfigured(cfg.suno_api_configured); })
      .catch(() => {});
  }, [navigate]);

  // Load & autoplay when nowPlaying changes; stop and clear audio when player is closed
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;
    if (!nowPlaying?.url) {
      audio.pause();
      audio.removeAttribute("src");
      audio.load();
      setCurrentTime(0);
      setDuration(0);
      return;
    }
    audio.src = nowPlaying.url;
    audio.load();
    audio.play().catch(() => {});
    setIsPlaying(true);
  }, [nowPlaying]);

  // Play / pause
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio || !nowPlaying) return;
    if (isPlaying) { audio.play().catch(() => {}); }
    else { audio.pause(); }
  }, [isPlaying, nowPlaying]);

  const handleTimeUpdate = useCallback(() => {
    const audio = audioRef.current;
    if (audio) setCurrentTime(audio.currentTime);
  }, []);

  const handleLoadedMetadata = useCallback(() => {
    const audio = audioRef.current;
    if (audio) setDuration(audio.duration);
  }, []);

  const handleEnded = useCallback(() => setIsPlaying(false), []);

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current;
    const t = Number(e.target.value);
    if (audio) { audio.currentTime = t; setCurrentTime(t); }
  };

  // Context passed to child pages
  const setCurrentSong = useCallback((song: NowPlaying | null) => {
    if (!song) { setNowPlaying(null); setIsPlaying(false); return; }
    setNowPlaying(song);
  }, []);

  const handleLogout = () => { localStorage.removeItem('user'); navigate('/login'); };

  const handleSelectStrategy = async (next: 'mock' | 'suno') => {
    if (next === strategy) { setShowStrategyModal(false); return; }
    setStrategyLoading(true);
    try { await setGenerationStrategy(next); setStrategy(next); setShowStrategyModal(false); }
    catch (e: any) { alert(`Could not switch to ${next}: ${e.message}`); }
    finally { setStrategyLoading(false); }
  };

  const navItems = [
    { path: '/generate', label: 'Create Music', icon: <Wand2 size={18} /> },
    { path: '/library', label: 'My Library', icon: <Library size={18} /> },
  ];

  const progress = duration ? (currentTime / duration) * 100 : 0;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', paddingBottom: nowPlaying ? '88px' : '0' }}>

      {/* Hidden audio element */}
      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
        preload="metadata"
      />

      {showStrategyModal && (
        <StrategyModal
          current={strategy} sunoConfigured={sunoConfigured}
          loading={strategyLoading} onSelect={handleSelectStrategy}
          onClose={() => setShowStrategyModal(false)}
        />
      )}

      <header style={{
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: '1rem 2rem', borderBottom: '1px solid var(--border-color)',
        backgroundColor: 'var(--bg-glass)', backdropFilter: 'blur(12px)',
        position: 'sticky', top: 0, zIndex: 10,
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <Link to="/generate" style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: 'var(--text-primary)' }}>
            <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg, var(--accent-color), #ea580c)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Music size={18} color="white" />
            </div>
            <h1 style={{ fontSize: '1.25rem', margin: 0 }}>AI Music Studio</h1>
          </Link>
          <nav style={{ display: 'flex', gap: '0.25rem' }}>
            {navItems.map(item => (
              <Link key={item.path} to={item.path} style={{
                display: 'flex', alignItems: 'center', gap: '0.5rem',
                padding: '0.5rem 0.875rem', borderRadius: 'var(--radius-pill)',
                backgroundColor: location.pathname === item.path ? 'rgba(249,115,22,0.15)' : 'transparent',
                color: location.pathname === item.path ? 'var(--accent-color)' : 'var(--text-secondary)',
                fontWeight: location.pathname === item.path ? 600 : 400,
                fontSize: '0.875rem',
              }}>
                {item.icon}<span>{item.label}</span>
              </Link>
            ))}
          </nav>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button
            onClick={() => setShowStrategyModal(true)}
            style={{
              display: 'flex', alignItems: 'center', gap: '0.5rem',
              padding: '0.4rem 0.875rem', borderRadius: 'var(--radius-pill)',
              border: `1px solid ${strategy === 'suno' ? 'rgba(249,115,22,0.5)' : 'var(--border-color)'}`,
              backgroundColor: strategy === 'suno' ? 'rgba(249,115,22,0.12)' : 'var(--bg-secondary)',
              color: strategy === 'suno' ? 'var(--accent-color)' : 'var(--text-secondary)',
              fontSize: '0.8rem', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s ease',
            }}
          >
            {strategy === 'mock' ? <FlaskConical size={14} /> : <Zap size={14} />}
            {strategy === 'mock' ? 'Mock' : 'Suno'}
          </button>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Hello, {user?.username}</span>
          <button onClick={handleLogout} style={{
            display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)',
            padding: '0.5rem 1rem', borderRadius: 'var(--radius-pill)', border: '1px solid var(--border-color)',
          }}>
            <LogOut size={16} /><span style={{ fontSize: '0.875rem' }}>Logout</span>
          </button>
        </div>
      </header>

      <main style={{ flexGrow: 1, padding: '2rem' }}>
        <Outlet context={{ setCurrentSong, setIsPlaying }} />
      </main>

      {/* ── Mini Player ─────────────────────────────────────────────────── */}
      {nowPlaying && (
        <div style={{
          position: 'fixed', bottom: 0, left: 0, right: 0,
          backgroundColor: 'var(--bg-primary)', borderTop: '1px solid var(--border-color)',
          zIndex: 100, boxShadow: '0 -4px 20px rgba(0,0,0,0.3)',
        }}>
          {/* Progress bar — full width, sits on top */}
          <div
            style={{ position: 'relative', height: '3px', backgroundColor: 'var(--border-color)', cursor: 'pointer' }}
          >
            <div style={{ width: `${progress}%`, height: '100%', backgroundColor: 'var(--accent-color)', transition: 'width 0.25s linear' }} />
            <input
              type="range" min={0} max={duration || 1} step={0.5} value={currentTime}
              onChange={handleSeek}
              style={{
                position: 'absolute', inset: 0, width: '100%', opacity: 0,
                cursor: 'pointer', margin: 0, height: '100%',
              }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'center', padding: '0 2rem', height: '72px', gap: '2rem' }}>
            {/* Song info */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', minWidth: '200px', flexShrink: 0 }}>
              <div style={{ width: '44px', height: '44px', borderRadius: '8px', background: 'linear-gradient(135deg, var(--accent-color), #ea580c)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                <Music size={20} color="white" />
              </div>
              <div style={{ overflow: 'hidden' }}>
                <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{nowPlaying.title}</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>AI Generated</div>
              </div>
            </div>

            {/* Controls */}
            <div style={{ flexGrow: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '1.5rem' }}>
              <button
                onClick={() => setIsPlaying(!isPlaying)}
                style={{
                  width: '44px', height: '44px', borderRadius: '50%',
                  backgroundColor: 'var(--accent-color)', color: 'white',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  boxShadow: '0 0 12px var(--accent-glow)',
                }}
              >
                {isPlaying ? <Pause size={20} fill="currentColor" /> : <Play size={20} fill="currentColor" style={{ marginLeft: '2px' }} />}
              </button>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
                <Volume2 size={14} />
                <span>{fmt(currentTime)}</span>
                <span>/</span>
                <span>{fmt(duration)}</span>
              </div>
            </div>

            {/* Close */}
            <div style={{ display: 'flex', justifyContent: 'flex-end', minWidth: '120px' }}>
              <button
                onClick={() => { setNowPlaying(null); setIsPlaying(false); }}
                style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.8rem', color: 'var(--text-secondary)', padding: '0.4rem 0.75rem', borderRadius: 'var(--radius-pill)', border: '1px solid var(--border-color)' }}
              >
                <X size={14} /> Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Layout;
