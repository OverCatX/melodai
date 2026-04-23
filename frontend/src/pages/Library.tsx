import React, { useState, useEffect } from 'react';
import { useOutletContext } from 'react-router-dom';
import { Play, Heart, Trash2, RefreshCw, Search, Music } from 'lucide-react';
import { listSongs, updateSong, deleteSong, syncSongStatus } from '../api';

const Library: React.FC = () => {
  const { setCurrentSong, setIsPlaying } = useOutletContext<any>();
  const [songs, setSongs] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchSongs = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await listSongs();
      setSongs(data.filter(s => !s.is_draft));
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchSongs(); }, []);

  const handleToggleFavorite = async (id: number, isFav: boolean) => {
    await updateSong(id, { is_favorite: !isFav });
    setSongs(songs.map(s => s.id === id ? { ...s, is_favorite: !isFav } : s));
  };

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this song?')) return;
    await deleteSong(id);
    setSongs(songs.filter(s => s.id !== id));
  };

  const handlePlay = (song: any) => {
    if (!song.audio_file_url) return;
    setCurrentSong({ title: song.title, url: song.audio_file_url });
    setIsPlaying(true);
  };

  const handleSync = async (id: number) => {
    try {
      const updated = await syncSongStatus(id);
      setSongs(songs.map(s => s.id === id ? updated : s));
    } catch (e: any) {
      alert(`Sync failed: ${e.message}`);
    }
  };

  const filtered = songs.filter(s => s.title.toLowerCase().includes(search.toLowerCase()));

  const statusBadgeStyle = (status: string) => ({
    padding: '0.25rem 0.75rem',
    borderRadius: 'var(--radius-pill)',
    fontSize: '0.75rem',
    border: '1px solid var(--border-color)',
    backgroundColor: status === 'COMPLETED' ? 'rgba(16,185,129,0.1)' : 'var(--bg-primary)',
    color: status === 'COMPLETED' ? 'var(--success-color)' : status === 'FAILED' ? 'var(--error-color)' : 'var(--text-secondary)',
  });

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>My Library</h2>
          <p style={{ color: 'var(--text-secondary)' }}>All your generated songs.</p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <div style={{ position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
            <input type="text" className="input-field" placeholder="Search songs..." value={search} onChange={(e) => setSearch(e.target.value)} style={{ paddingLeft: '2.5rem', width: '220px' }} />
          </div>
          <button onClick={fetchSongs} style={{ padding: '0.75rem', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
            <RefreshCw size={18} />
          </button>
        </div>
      </div>

      {error && <div style={{ padding: '1rem', marginBottom: '1rem', backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-md)', color: 'var(--error-color)', fontSize: '0.875rem' }}>{error}</div>}

      <div className="glass-panel" style={{ overflow: 'hidden' }}>
        {loading ? (
          <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading...</div>
        ) : (
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
                <th style={{ padding: '1.25rem 1.5rem', fontWeight: 500, width: '40px' }}>#</th>
                <th style={{ padding: '1.25rem 1.5rem', fontWeight: 500 }}>Title</th>
                <th style={{ padding: '1.25rem 1.5rem', fontWeight: 500 }}>Status</th>
                <th style={{ padding: '1.25rem 1.5rem', fontWeight: 500, textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.length > 0 ? filtered.map((song, index) => (
                <tr key={song.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.03)' }}>
                  <td style={{ padding: '1rem 1.5rem', color: 'var(--text-secondary)' }}>{index + 1}</td>
                  <td style={{ padding: '1rem 1.5rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div style={{ width: '36px', height: '36px', borderRadius: '8px', backgroundColor: 'var(--bg-secondary)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        <Music size={18} color="var(--accent-color)" />
                      </div>
                      <div>
                        <div style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{song.title}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{new Date(song.created_at).toLocaleDateString()}</div>
                      </div>
                    </div>
                  </td>
                  <td style={{ padding: '1rem 1.5rem' }}>
                    <span style={statusBadgeStyle(song.generation_status)}>{song.generation_status}</span>
                  </td>
                  <td style={{ padding: '1rem 1.5rem', textAlign: 'right' }}>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                      <button onClick={() => handleToggleFavorite(song.id, song.is_favorite)} style={{ padding: '0.5rem', color: song.is_favorite ? 'var(--error-color)' : 'var(--text-secondary)' }}>
                        <Heart size={18} fill={song.is_favorite ? 'currentColor' : 'none'} />
                      </button>
                      {song.generation_status !== 'COMPLETED' && song.generation_status !== 'FAILED' && (
                        <button onClick={() => handleSync(song.id)} title="Sync status with AI provider" style={{ padding: '0.5rem', color: 'var(--accent-color)' }}>
                          <RefreshCw size={18} />
                        </button>
                      )}
                      {song.generation_status === 'COMPLETED' && (
                        <button onClick={() => handlePlay(song)} style={{ padding: '0.5rem', color: 'var(--text-secondary)' }}><Play size={18} /></button>
                      )}
                      <button onClick={() => handleDelete(song.id)} style={{ padding: '0.5rem', color: 'var(--error-color)' }}><Trash2 size={18} /></button>
                    </div>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={4} style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
                    No songs yet. Go generate your first song!
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default Library;
