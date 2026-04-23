import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Share2, Copy, Play, RefreshCw } from 'lucide-react';
import { listSharedSongs } from '../api';

const Shared: React.FC = () => {
  const { setCurrentSong, setIsPlaying } = useOutletContext<any>();
  const [sharedSongs, setSharedSongs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchShared = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await listSharedSongs();
      setSharedSongs(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchShared(); }, []);

  const handleCopy = (url: string) => {
    navigator.clipboard.writeText(url).then(() => alert('Link copied to clipboard!'));
  };

  const handlePlay = (title: string) => {
    setCurrentSong(title);
    setIsPlaying(true);
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Shared Links</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Manage songs you have shared with others.</p>
        </div>
        <button onClick={fetchShared} style={{ padding: '0.75rem', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
          <RefreshCw size={18} />
        </button>
      </div>

      {error && <div style={{ padding: '1rem', marginBottom: '1rem', backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-md)', color: 'var(--error-color)', fontSize: '0.875rem' }}>{error}</div>}

      {loading ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading...</div>
      ) : sharedSongs.length === 0 ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          No shared songs yet. Share a song from your Library.
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          {sharedSongs.map(item => {
            const shareUrl = item.share_link || '';
            return (
              <div key={item.id} className="glass-panel" style={{ padding: '1.5rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                  <div style={{ width: '48px', height: '48px', borderRadius: '12px', backgroundColor: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Share2 size={24} color="var(--accent-color)" />
                  </div>
                  <div>
                    <h3 style={{ fontSize: '1.125rem', marginBottom: '0.25rem' }}>Song #{item.song_id}</h3>
                    <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                      Shared: {new Date(item.shared_at).toLocaleDateString()}
                      {shareUrl && <span> &bull; <a href={shareUrl} target="_blank" rel="noreferrer" style={{ color: 'var(--accent-color)' }}>{shareUrl}</a></span>}
                    </div>
                  </div>
                </div>
                <div style={{ display: 'flex', gap: '0.5rem' }}>
                  <button onClick={() => handlePlay(`Song #${item.song_id}`)} style={{ padding: '0.75rem', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border-color)' }}>
                    <Play size={18} />
                  </button>
                  {shareUrl && (
                    <button onClick={() => handleCopy(shareUrl)} style={{ padding: '0.75rem 1.25rem', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border-color)', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                      <Copy size={18} /> Copy Link
                    </button>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default Shared;
