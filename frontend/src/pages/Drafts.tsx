import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Edit2, Trash2, RefreshCw } from 'lucide-react';
import { listDrafts, deleteDraft } from '../api';

const Drafts: React.FC = () => {
  const navigate = useNavigate();
  const [drafts, setDrafts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDrafts = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await listDrafts();
      setDrafts(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchDrafts(); }, []);

  const handleDelete = async (id: number) => {
    if (!window.confirm('Delete this draft?')) return;
    await deleteDraft(id);
    setDrafts(drafts.filter(d => d.id !== id));
  };

  return (
    <div style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '2rem' }}>
        <div>
          <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Drafts</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Unfinished song prompts ready to be generated.</p>
        </div>
        <button onClick={fetchDrafts} style={{ padding: '0.75rem', borderRadius: 'var(--radius-md)', backgroundColor: 'var(--bg-secondary)', color: 'var(--text-secondary)', border: '1px solid var(--border-color)' }}>
          <RefreshCw size={18} />
        </button>
      </div>

      {error && <div style={{ padding: '1rem', marginBottom: '1rem', backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-md)', color: 'var(--error-color)', fontSize: '0.875rem' }}>{error}</div>}

      {loading ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>Loading...</div>
      ) : drafts.length === 0 ? (
        <div className="glass-panel" style={{ padding: '3rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          No drafts yet. Save a song prompt as a draft from the Create Music page.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
          {drafts.map(draft => (
            <div key={draft.id} className="glass-panel" style={{ padding: '1.5rem' }}>
              <h3 style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>Draft #{draft.id}</h3>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', opacity: 0.7, marginBottom: '0.25rem', fontFamily: 'monospace' }}>{draft.draft_id}</p>
              {draft.saved_at && <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', opacity: 0.7, marginBottom: '1.5rem' }}>Saved: {new Date(draft.saved_at).toLocaleString()}</p>}
              <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <span style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem', borderRadius: 'var(--radius-pill)', border: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                  {draft.is_submitted ? 'Submitted' : 'Pending'}
                </span>
                {draft.retention_policy && (
                  <span style={{ fontSize: '0.75rem', padding: '0.25rem 0.5rem', borderRadius: 'var(--radius-pill)', border: '1px solid var(--border-color)', color: 'var(--text-secondary)' }}>
                    {draft.retention_policy}
                  </span>
                )}
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <button onClick={() => navigate('/generate')} className="btn-primary" style={{ flexGrow: 1, padding: '0.5rem', fontSize: '0.875rem' }}>
                  <Edit2 size={16} /> Continue
                </button>
                <button onClick={() => handleDelete(draft.id)} style={{ padding: '0.5rem 1rem', borderRadius: 'var(--radius-md)', backgroundColor: 'rgba(239, 68, 68, 0.1)', color: 'var(--error-color)', border: '1px solid rgba(239, 68, 68, 0.2)' }}>
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Drafts;
