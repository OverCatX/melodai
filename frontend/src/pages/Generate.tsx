import React, { useState } from 'react';
import { useOutletContext, useNavigate, Link } from 'react-router-dom';
import { Wand2, CheckCircle2, CircleDashed, Loader2, Play, Download, Save, AlertCircle, Library } from 'lucide-react';
import { createSong, getSong, createPrompt, createGenerationRequest, runGeneration, pollGeneration, downloadSongFile } from '../api';

type Step = 'idle' | 'creating' | 'generating' | 'polling' | 'done' | 'error';

const timelineSteps = [
  { id: 'creating', label: 'Creating Song', description: 'Setting up song and prompt in the database' },
  { id: 'generating', label: 'Starting Generation', description: 'Sending your request to the AI strategy' },
  { id: 'polling', label: 'Processing Audio', description: 'Suno is composing your song — usually 1 to 3 minutes' },
  { id: 'done', label: 'Ready', description: 'Your song has been generated' },
];

const Generate: React.FC = () => {
  const navigate = useNavigate();
  const { setCurrentSong, setIsPlaying } = useOutletContext<any>();

  const [title, setTitle] = useState('');
  const [occasion, setOccasion] = useState('GENERAL');
  const [moodTone, setMoodTone] = useState('HAPPY');
  const [singerTone, setSingerTone] = useState('NEUTRAL');
  const [description, setDescription] = useState('');

  const [currentStep, setCurrentStep] = useState<Step>('idle');
  const [errorMsg, setErrorMsg] = useState('');
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [generationStatus, setGenerationStatus] = useState('');
  const [activeGenReqId, setActiveGenReqId] = useState<number | null>(null);
  const [generatedSongId, setGeneratedSongId] = useState<number | null>(null);
  const [downloadBusy, setDownloadBusy] = useState(false);

  const getUser = (): { id: number; session_token: string } | null => {
    const data = localStorage.getItem('user');
    if (!data) return null;
    try {
      const o = JSON.parse(data) as { id?: number; session_token?: string };
      if (typeof o.id !== 'number' || o.id <= 0 || !o.session_token) return null;
      return { id: o.id, session_token: o.session_token };
    } catch {
      return null;
    }
  };

  const handleGenerate = async () => {
    const stored = getUser();
    if (!title.trim() || currentStep !== 'idle') return;
    if (!stored) {
      setErrorMsg('Please sign in with Google from the login page.');
      navigate('/login');
      return;
    }
    setCurrentStep('creating');
    setErrorMsg('');
    setGeneratedSongId(null);

    try {
      // Step 1: Create Song
      const song = await createSong({ user_id: stored.id, title, generation_status: 'DRAFT', is_draft: true });
      setGeneratedSongId(song.id);

      // Step 2: Create Prompt
      const prompt = await createPrompt({
        song_id: song.id, title, occasion, mood_and_tone: moodTone,
        singer_tone: singerTone, description,
      });

      // Step 3: Create Generation Request
      const genReq = await createGenerationRequest(prompt.id);
      setActiveGenReqId(genReq.id);
      setCurrentStep('generating');

      // Step 4: Run Generation
      const runResult = await runGeneration(genReq.id);
      setGenerationStatus(runResult.external_status || runResult.status);

      if (runResult.status === 'COMPLETED') {
        // Mock: done immediately
        setCurrentStep('done');
        setAudioUrl(song.audio_file_url || 'https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/audio/dummy-audio.mp3');
        return;
      }

      // Step 5: Poll until done (Suno async)
      // Suno can take 1-5 minutes — poll every 5s for up to 60 attempts (5 min)
      setCurrentStep('polling');
      let done = false;
      let attempts = 0;
      const MAX_ATTEMPTS = 60;   // 5 minutes
      const POLL_INTERVAL = 5000;

      while (!done && attempts < MAX_ATTEMPTS) {
        await new Promise(r => setTimeout(r, POLL_INTERVAL));
        const pollResult = await pollGeneration(genReq.id);
        // Show Suno's human-readable status in the timeline
        setGenerationStatus(pollResult.external_status || pollResult.status);
        if (pollResult.status === 'COMPLETED') {
          done = true;
          setCurrentStep('done');
          // Re-fetch song to get the audio_file_url that Suno populated
          const updatedSong = await getSong(song.id);
          setAudioUrl(updatedSong.audio_file_url || null);
        } else if (pollResult.status === 'FAILED') {
          throw new Error(`Generation failed: ${pollResult.external_status || 'unknown reason'}`);
        }
        attempts++;
      }

      if (!done) {
        // Soft timeout: Suno is likely still running. Let user resume polling.
        setErrorMsg('Still processing on Suno (>5 min). Click "Keep Waiting" to continue polling or check back later in My Library.');
        setCurrentStep('error');
      }
    } catch (err: any) {
      setErrorMsg(err.message || 'An unexpected error occurred.');
      setCurrentStep('error');
    }
  };

  // Resume polling for an already-running generation request
  const handleKeepWaiting = async () => {
    if (!activeGenReqId) return;
    setCurrentStep('polling');
    setErrorMsg('');
    let done = false;
    let attempts = 0;
    try {
      while (!done && attempts < 60) {
        await new Promise(r => setTimeout(r, 5000));
        const pollResult = await pollGeneration(activeGenReqId);
        setGenerationStatus(pollResult.external_status || pollResult.status);
        if (pollResult.status === 'COMPLETED') {
          done = true;
          setCurrentStep('done');
          if (generatedSongId != null) {
            const updated = await getSong(generatedSongId);
            setAudioUrl(updated.audio_file_url || null);
          }
        } else if (pollResult.status === 'FAILED') {
          throw new Error(`Generation failed: ${pollResult.external_status}`);
        }
        attempts++;
      }
      if (!done) {
        setErrorMsg('Still processing. Check My Library in a few minutes — Suno may have finished.');
        setCurrentStep('error');
      }
    } catch (err: any) {
      setErrorMsg(err.message);
      setCurrentStep('error');
    }
  };

  const handleSaveDraft = () => {
    alert(`Draft "${title}" saved! (Drafts saved via the backend will appear in the Drafts page).`);
    navigate('/drafts');
  };

  const handlePlaySong = () => {
    if (!audioUrl) return;
    setCurrentSong({ title, url: audioUrl });
    setIsPlaying(true);
  };

  const handleDownload = async () => {
    if (generatedSongId == null) return;
    setDownloadBusy(true);
    try {
      await downloadSongFile(generatedSongId, title);
    } catch (e: any) {
      alert(e?.message || 'Download failed');
    } finally {
      setDownloadBusy(false);
    }
  };

  const resetGeneration = () => {
    setCurrentStep('idle');
    setTitle('');
    setOccasion('GENERAL');
    setMoodTone('HAPPY');
    setSingerTone('NEUTRAL');
    setDescription('');
    setAudioUrl(null);
    setErrorMsg('');
    setGenerationStatus('');
    setActiveGenReqId(null);
    setGeneratedSongId(null);
  };

  const renderForm = () => (
    <div className="glass-panel animate-fade-in" style={{ padding: '2.5rem' }}>
      <h2 style={{ fontSize: '1.75rem', marginBottom: '1rem' }}>Create New Music</h2>
      <p style={{ marginBottom: '2rem' }}>Fill in the details below to generate a new AI song.</p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', marginBottom: '2rem' }}>
        <div>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Song Title</label>
          <input className="input-field" type="text" placeholder="e.g. Summer Breeze" value={title} onChange={(e) => setTitle(e.target.value)} />
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
          <textarea className="input-field" placeholder="A short description of the song..." rows={3}
            value={description} onChange={(e) => setDescription(e.target.value)} style={{ resize: 'none' }} />
        </div>
      </div>

      <div style={{ display: 'flex', gap: '1rem' }}>
        <button className="btn-primary" style={{ flexGrow: 1, padding: '1rem' }} onClick={handleGenerate} disabled={!title.trim()}>
          <Wand2 size={20} /> Generate Music
        </button>
        <button onClick={handleSaveDraft} disabled={!title.trim()} style={{
          padding: '1rem 1.5rem', borderRadius: 'var(--radius-pill)', border: '1px solid var(--border-color)',
          backgroundColor: 'transparent', color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '0.5rem',
          opacity: !title.trim() ? 0.5 : 1, cursor: !title.trim() ? 'not-allowed' : 'pointer'
        }}>
          <Save size={20} /> Draft
        </button>
      </div>
    </div>
  );

  const renderTimeline = () => {
    if (currentStep === 'idle') return null;
    const currentIndex = timelineSteps.findIndex(s => s.id === currentStep);

    return (
      <div className="glass-panel animate-fade-in" style={{ padding: '2rem', marginTop: '2rem' }}>
        <h3 style={{ marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          {currentStep === 'error'
            ? <AlertCircle size={20} color="var(--error-color)" />
            : <Loader2 size={20} style={{ animation: 'spin 2s linear infinite' }} />}
          Generation Status
          {generationStatus && (
            <span style={{
              fontSize: '0.7rem', marginLeft: 'auto', fontFamily: 'monospace',
              padding: '0.2rem 0.6rem', borderRadius: 'var(--radius-pill)',
              border: '1px solid var(--border-color)',
              backgroundColor: generationStatus === 'SUCCESS' ? 'rgba(16,185,129,0.1)' : 'var(--bg-secondary)',
              color: generationStatus === 'SUCCESS' ? 'var(--success-color)' : 'var(--text-secondary)',
            }}>
              {generationStatus}
            </span>
          )}
        </h3>

        {currentStep === 'error' && (
          <div style={{ marginBottom: '1.5rem', padding: '0.75rem 1rem', backgroundColor: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 'var(--radius-md)', color: 'var(--error-color)', fontSize: '0.875rem' }}>
            {errorMsg}
          </div>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', marginTop: '1.5rem' }}>
          {timelineSteps.map((step, index) => {
            const isCompleted = currentStep === 'done' || (currentStep !== 'error' && index < currentIndex);
            const isCurrent = currentStep !== 'done' && currentStep !== 'error' && index === currentIndex;
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

        {/* Waiting banner — shown while Suno is processing */}
        {currentStep === 'polling' && (
          <div style={{
            marginTop: '1.5rem', padding: '1rem 1.25rem',
            borderRadius: 'var(--radius-md)',
            border: '1px solid var(--border-color)',
            backgroundColor: 'var(--bg-secondary)',
            display: 'flex', flexDirection: 'column', gap: '0.75rem',
          }}>
            <p style={{ margin: 0, fontSize: '0.875rem', color: 'var(--text-secondary)', lineHeight: 1.6 }}>
              Suno is composing your song in the background.
              This usually takes <strong style={{ color: 'var(--text-primary)' }}>1 to 3 minutes</strong>.<br />
              You can stay here or go to <strong style={{ color: 'var(--text-primary)' }}>My Library</strong> — the song will appear there once it's ready.
            </p>
            <Link
              to="/library"
              style={{
                display: 'inline-flex', alignItems: 'center', gap: '0.5rem',
                padding: '0.5rem 1rem', borderRadius: 'var(--radius-pill)',
                border: '1px solid var(--border-color)', fontSize: '0.85rem',
                color: 'var(--text-secondary)', alignSelf: 'flex-start',
                backgroundColor: 'var(--bg-primary)',
              }}
            >
              <Library size={15} /> Go to My Library
            </Link>
          </div>
        )}

        {currentStep === 'error' && (
          <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {/* Keep Waiting: only shown when soft-timeout (activeGenReqId still alive) */}
            {activeGenReqId && errorMsg.includes('Still processing') && (
              <button onClick={handleKeepWaiting} className="btn-primary" style={{ width: '100%' }}>
                <Loader2 size={18} /> Keep Waiting
              </button>
            )}
            <button onClick={resetGeneration} style={{
              width: '100%', padding: '0.75rem', borderRadius: 'var(--radius-pill)',
              backgroundColor: 'transparent', border: '1px solid var(--border-color)',
              color: 'var(--text-secondary)', cursor: 'pointer'
            }}>
              Start Over
            </button>
          </div>
        )}
      </div>
    );
  };

  const renderResult = () => {
    if (currentStep !== 'done') return null;
    return (
      <div className="glass-panel animate-fade-in" style={{ padding: '2rem', marginTop: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.5rem' }}>
        <div style={{ width: '80px', height: '80px', borderRadius: '50%', background: 'linear-gradient(135deg, var(--success-color), #059669)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 8px 16px rgba(16, 185, 129, 0.3)' }}>
          <CheckCircle2 size={40} color="white" />
        </div>
        <div style={{ textAlign: 'center' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>"{title}" is Ready</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Saved to your Library automatically.</p>
        </div>
        {audioUrl && (
          <>
            <div style={{ width: '100%' }}>
              <audio controls style={{ width: '100%', borderRadius: 'var(--radius-md)' }} src={audioUrl}>
                Your browser does not support audio.
              </audio>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', width: '100%', gap: '0.75rem' }}>
              <button onClick={handlePlaySong} className="btn-primary" style={{ width: '100%' }}>
                <Play size={20} /> Play in Player
              </button>
              {generatedSongId != null && (
                <button
                  type="button"
                  onClick={handleDownload}
                  disabled={downloadBusy}
                  style={{
                    width: '100%',
                    padding: '0.85rem 1rem',
                    borderRadius: 'var(--radius-pill)',
                    border: '1px solid var(--border-color)',
                    backgroundColor: 'var(--bg-secondary)',
                    color: 'var(--text-primary)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '0.5rem',
                    cursor: downloadBusy ? 'wait' : 'pointer',
                    opacity: downloadBusy ? 0.7 : 1,
                  }}
                >
                  <Download size={20} />
                  {downloadBusy ? 'Downloading…' : 'Download audio file'}
                </button>
              )}
            </div>
          </>
        )}
        {!audioUrl && (
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            Audio URL not yet available — check <a href="/library" style={{ color: 'var(--accent-color)' }}>My Library</a> or use the sync button.
          </p>
        )}
        <button onClick={resetGeneration} style={{ width: '100%', padding: '0.75rem', backgroundColor: 'transparent', border: 'none', color: 'var(--text-secondary)' }}>
          Create Another Song
        </button>
      </div>
    );
  };

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      {currentStep === 'idle' ? renderForm() : (
        <div>{renderTimeline()}{renderResult()}</div>
      )}
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
    </div>
  );
};

export default Generate;
