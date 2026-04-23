import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  LogOut, 
  Wand2, 
  CheckCircle2, 
  CircleDashed, 
  Music, 
  Loader2, 
  Play, 
} from 'lucide-react';

type Step = 'idle' | 'requesting' | 'generating' | 'processing' | 'done';

const timelineSteps = [
  { id: 'requesting', label: 'Analyzing Prompt', description: 'Understanding your music request' },
  { id: 'generating', label: 'Composing Music', description: 'AI is composing melodies and beats' },
  { id: 'processing', label: 'Processing Audio', description: 'Mixing and finalizing the track' },
  { id: 'done', label: 'Ready', description: 'Your song is ready to play' },
];

const Generate: React.FC = () => {
  const navigate = useNavigate();
  
  // Form State matching backend AIGenerationRequest / SongPrompt
  const [title, setTitle] = useState('');
  const [occasion, setOccasion] = useState('GENERAL');
  const [moodTone, setMoodTone] = useState('HAPPY');
  const [singerTone, setSingerTone] = useState('NEUTRAL');
  const [description, setDescription] = useState('');
  
  const [currentStep, setCurrentStep] = useState<Step>('idle');
  const [user, setUser] = useState<{username: string} | null>(null);
  
  useEffect(() => {
    const userData = localStorage.getItem('user');
    if (!userData) {
      navigate('/login');
    } else {
      setUser(JSON.parse(userData));
    }
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('user');
    navigate('/login');
  };

  const handleGenerate = () => {
    if (!title.trim() || currentStep !== 'idle') return;
    
    // In a real app, this is where we POST to /api/generation-requests/
    setCurrentStep('requesting');
    
    setTimeout(() => {
      setCurrentStep('generating');
      setTimeout(() => {
        setCurrentStep('processing');
        setTimeout(() => {
          setCurrentStep('done');
        }, 2000);
      }, 3000);
    }, 1500);
  };

  const resetGeneration = () => {
    setCurrentStep('idle');
    setTitle('');
    setOccasion('GENERAL');
    setMoodTone('HAPPY');
    setSingerTone('NEUTRAL');
    setDescription('');
  };

  const renderForm = () => (
    <div className="glass-panel animate-fade-in" style={{ padding: '2.5rem' }}>
      <h2 style={{ fontSize: '1.75rem', marginBottom: '1rem' }}>Create New Music</h2>
      <p style={{ marginBottom: '2rem' }}>Fill in the details below to generate a new AI song.</p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '2rem' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Song Title</label>
          <input
            className="input-field"
            type="text"
            placeholder="e.g. Summer Breeze"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Occasion</label>
            <select className="input-field" value={occasion} onChange={(e) => setOccasion(e.target.value)}>
              <option value="BIRTHDAY">Birthday</option>
              <option value="WEDDING">Wedding</option>
              <option value="ANNIVERSARY">Anniversary</option>
              <option value="GRADUATION">Graduation</option>
              <option value="GENERAL">General</option>
            </select>
          </div>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Mood and Tone</label>
            <select className="input-field" value={moodTone} onChange={(e) => setMoodTone(e.target.value)}>
              <option value="HAPPY">Happy</option>
              <option value="SAD">Sad</option>
              <option value="ROMANTIC">Romantic</option>
              <option value="ENERGETIC">Energetic</option>
              <option value="CALM">Calm</option>
            </select>
          </div>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Singer Tone</label>
          <select className="input-field" value={singerTone} onChange={(e) => setSingerTone(e.target.value)}>
            <option value="MALE_DEEP">Male Deep</option>
            <option value="MALE_LIGHT">Male Light</option>
            <option value="FEMALE_DEEP">Female Deep</option>
            <option value="FEMALE_LIGHT">Female Light</option>
            <option value="NEUTRAL">Neutral</option>
          </select>
        </div>

        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Description (Optional)</label>
          <textarea
            className="input-field"
            placeholder="A short description of the song..."
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            style={{ resize: 'none' }}
          />
        </div>
      </div>
      
      <button 
        className="btn-primary" 
        style={{ width: '100%', padding: '1rem' }}
        onClick={handleGenerate}
        disabled={!title.trim()}
      >
        <Wand2 size={20} />
        Generate Music
      </button>
    </div>
  );

  const renderTimeline = () => {
    if (currentStep === 'idle') return null;
    const currentIndex = timelineSteps.findIndex(s => s.id === currentStep);
    return (
      <div className="glass-panel animate-fade-in" style={{ padding: '2rem', marginTop: '2rem' }}>
        <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Loader2 className="animate-pulse-glow" style={{ animation: 'spin 2s linear infinite' }} size={20} />
          Generation Status
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {timelineSteps.map((step, index) => {
            const isCompleted = currentStep === 'done' || index < currentIndex;
            const isCurrent = currentStep !== 'done' && index === currentIndex;
            const isPending = !isCompleted && !isCurrent;
            return (
              <div key={step.id} style={{ display: 'flex', gap: '1rem', opacity: isPending ? 0.4 : 1, transition: 'all 0.3s ease' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
                  <div style={{
                    width: '32px', height: '32px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    backgroundColor: isCompleted ? 'var(--success-color)' : isCurrent ? 'var(--accent-color)' : 'var(--bg-secondary)',
                    boxShadow: isCurrent ? '0 0 15px var(--accent-glow)' : 'none', transition: 'all 0.3s ease'
                  }}>
                    {isCompleted ? <CheckCircle2 size={18} color="white" /> : 
                     isCurrent ? <Loader2 size={18} color="white" style={{ animation: 'spin 2s linear infinite' }} /> :
                     <CircleDashed size={18} color="var(--text-secondary)" />}
                  </div>
                  {index < timelineSteps.length - 1 && (
                    <div style={{ width: '2px', height: '100%', backgroundColor: isCompleted ? 'var(--success-color)' : 'var(--border-color)', flexGrow: 1, minHeight: '2rem' }} />
                  )}
                </div>
                <div style={{ paddingBottom: '1rem' }}>
                  <h4 style={{ margin: 0, color: isCurrent ? 'var(--accent-color)' : 'var(--text-primary)' }}>{step.label}</h4>
                  <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{step.description}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderResult = () => {
    if (currentStep !== 'done') return null;
    return (
      <div className="glass-panel animate-fade-in" style={{ padding: '2rem', marginTop: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.5rem' }}>
        <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--success-color), #059669)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 8px 16px rgba(16, 185, 129, 0.3)' }}>
          <Music size={40} color="white" />
        </div>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>"{title}" is Ready</h2>
          <p style={{ color: 'var(--text-secondary)' }}>{occasion} • {moodTone} • {singerTone}</p>
        </div>
        <div style={{ width: '100%', padding: '1rem', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <button style={{ width: '40px', height: '40px', borderRadius: '50%', backgroundColor: 'var(--accent-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
            <Play size={20} fill="currentColor" />
          </button>
          <div style={{ flexGrow: 1 }}>
            <div style={{ width: '100%', height: '4px', backgroundColor: 'var(--border-color)', borderRadius: '2px', position: 'relative' }}>
              <div style={{ width: '30%', height: '100%', backgroundColor: 'var(--accent-color)', borderRadius: '2px' }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
              <span>0:00</span><span>3:24</span>
            </div>
          </div>
        </div>
        <button onClick={resetGeneration} className="btn-primary" style={{ width: '100%', marginTop: '1rem', backgroundColor: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-primary)', boxShadow: 'none' }}>
          Generate Another Song
        </button>
      </div>
    );
  };

  return (
    <div style={{ minHeight: '100vh', padding: '2rem' }} className="container">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'linear-gradient(135deg, var(--accent-color), #4f46e5)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Music size={20} color="white" />
          </div>
          <h1 style={{ fontSize: '1.25rem', margin: 0 }}>AI Music Studio</h1>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Hello, {user?.username}</span>
          <button onClick={handleLogout} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-secondary)', padding: '0.5rem 1rem', borderRadius: 'var(--radius-pill)', border: '1px solid var(--border-color)' }}>
            <LogOut size={16} />
            <span style={{ fontSize: '0.875rem' }}>Logout</span>
          </button>
        </div>
      </header>

      <main style={{ maxWidth: '600px', margin: '0 auto' }}>
        {currentStep === 'idle' ? renderForm() : (
          <div>
            {renderTimeline()}
            {renderResult()}
          </div>
        )}
      </main>
      
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default Generate;
