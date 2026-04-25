const BASE_URL = 'http://127.0.0.1:8000/api';

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || JSON.stringify(data));
  return data as T;
}

// --- Users ---
/** Always returns a valid user — creates one or returns the existing one. */
export function getOrCreateUser(payload: {
  username: string;
  display_name?: string;
}) {
  return apiFetch<{ id: number; user_id: string; username: string; display_name: string }>('/users/get-or-create/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// --- Songs (scoped by user: DB already has user FK; API filters by `user_id`) ---

/** Current user’s numeric id (from localStorage, or get-or-create from username). */
export async function resolveUserId(): Promise<number> {
  const raw = localStorage.getItem('user');
  if (!raw) throw new Error('Not logged in');
  let u: { username?: string; id?: number };
  try {
    u = JSON.parse(raw);
  } catch {
    throw new Error('Invalid session');
  }
  if (typeof u.id === 'number' && u.id > 0) return u.id;
  if (!u.username) throw new Error('Not logged in');
  const fresh = await getOrCreateUser({ username: u.username });
  localStorage.setItem('user', JSON.stringify({ username: fresh.username, id: fresh.id }));
  return fresh.id;
}

function songsQuery(userId: number) {
  return `?user_id=${userId}`;
}

export function createSong(payload: {
  user_id: number;
  title: string;
  generation_status: string;
  is_draft: boolean;
}) {
  return apiFetch<{ id: number; song_id: string; audio_file_url: string | null; generation_status: string }>(
    '/songs/',
    { method: 'POST', body: JSON.stringify(payload) }
  );
}

export async function getSong(id: number) {
  const userId = await resolveUserId();
  return apiFetch<{
    id: number; song_id: string; title: string;
    audio_file_url: string | null; generation_status: string;
    created_at: string; is_favorite: boolean; is_draft: boolean;
  }>(`/songs/${id}/${songsQuery(userId)}`);
}

/** All songs for the logged-in user (via nested route). */
export async function listSongs() {
  const userId = await resolveUserId();
  return apiFetch<Array<{
    id: number; song_id: string; title: string;
    audio_file_url: string | null; generation_status: string;
    created_at: string; is_favorite: boolean; is_draft: boolean;
  }>>(`/users/${userId}/songs/`);
}

export async function updateSong(id: number, payload: Partial<{ is_favorite: boolean; is_draft: boolean }>) {
  const userId = await resolveUserId();
  return apiFetch<{ id: number }>(`/songs/${id}/${songsQuery(userId)}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export async function deleteSong(id: number) {
  const userId = await resolveUserId();
  const res = await fetch(`${BASE_URL}/songs/${id}/${songsQuery(userId)}`, { method: 'DELETE' });
  if (!res.ok) {
    const data = await res.json().catch(() => ({}));
    throw new Error((data as { detail?: string }).detail || `Delete failed (${res.status})`);
  }
}

export async function syncSongStatus(id: number) {
  const userId = await resolveUserId();
  return apiFetch<{
    id: number; song_id: string; title: string;
    audio_file_url: string | null; generation_status: string;
    created_at: string; is_favorite: boolean; is_draft: boolean;
  }>(`/songs/${id}/sync-status/${songsQuery(userId)}`, { method: 'POST' });
}

const SAFE_FILENAME = /[^\w\s\-._]/g;

function safeDownloadFilename(title: string, ext: string) {
  const base = (title || 'song')
    .trim()
    .replace(SAFE_FILENAME, '')
    .replace(/\s+/g, '_') || 'song';
  return `${base.slice(0, 200)}${ext.startsWith('.') ? ext : `.${ext}`}`;
}

/** Download audio via backend proxy (avoids CORS issues with Suno CDN). */
export async function downloadSongFile(songId: number, title: string) {
  const userId = await resolveUserId();
  const res = await fetch(
    `${BASE_URL}/songs/${songId}/download/${songsQuery(userId)}`,
    { method: 'GET' }
  );
  const contentType = res.headers.get('Content-Type') || '';
  let ext = '.mp3';
  if (contentType.includes('wav')) ext = '.wav';
  else if (contentType.includes('flac')) ext = '.flac';
  else if (contentType.includes('ogg') || contentType.includes('opus')) ext = '.ogg';

  if (!res.ok) {
    let detail = 'Download failed';
    try {
      const err = await res.json();
      detail = (err as { detail?: string }).detail || detail;
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }

  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = safeDownloadFilename(title, ext);
  a.rel = 'noopener';
  a.click();
  URL.revokeObjectURL(url);
}

// --- Song Prompts ---
export function createPrompt(payload: {
  song_id: number;
  title: string;
  occasion: string;
  mood_and_tone: string;
  singer_tone: string;
  description: string;
}) {
  return apiFetch<{ id: number; prompt_id: string }>('/song-prompts/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// --- Generation Requests ---
export function createGenerationRequest(prompt_id: number) {
  return apiFetch<{
    id: number;
    song_id: number;
    status: string;
    external_task_id: string;
  }>('/generation-requests/', {
    method: 'POST',
    body: JSON.stringify({ prompt_id }),
  });
}

export function getGenerationRequestForSong(songId: number) {
  // We'll need to find the prompt first, then the request. 
  // For simplicity, let's assume the backend can filter generation requests by song_id if we added it, 
  // but for now we'll just list them and filter client-side or add an endpoint.
  // Actually, let's just add an endpoint in the next step or use list with filter.
  return apiFetch<Array<{ id: number; status: string; prompt: { song: number } }>>(`/generation-requests/`);
}

export function runGeneration(req_id: number) {
  return apiFetch<{
    id: number;
    song_id: number;
    status: string;
    external_task_id: string;
    external_status: string;
  }>(
    `/generation-requests/${req_id}/run/`,
    { method: 'POST', body: JSON.stringify({}) }
  );
}

export function pollGeneration(req_id: number) {
  return apiFetch<{
    id: number;
    song_id: number;
    status: string;
    external_task_id: string;
    external_status: string;
  }>(
    `/generation-requests/${req_id}/poll/`,
    { method: 'POST', body: JSON.stringify({}) }
  );
}

// --- Generation Config (strategy) ---
export function getGenerationConfig() {
  return apiFetch<{ generator_strategy: string; strategy_source: string; suno_api_configured: boolean }>('/generation-config/');
}

export function setGenerationStrategy(strategy: 'mock' | 'suno') {
  return apiFetch<{ generator_strategy: string }>('/generation-config/', {
    method: 'POST',
    body: JSON.stringify({ generator_strategy: strategy }),
  });
}

// --- Drafts ---
export function listDrafts() {
  // DraftSerializer fields: id, draft_id, song_id, saved_at, is_submitted, retention_policy
  return apiFetch<Array<{ id: number; draft_id: string; song_id: number; saved_at: string; is_submitted: boolean; retention_policy: string }>>('/drafts/');
}

export function deleteDraft(id: number) {
  return fetch(`${BASE_URL}/drafts/${id}/`, { method: 'DELETE' });
}

// --- Shared Songs ---
export function listSharedSongs() {
  // SharedSongSerializer fields: id, share_id, song_id, share_link, shared_at, accessible_by_guest
  return apiFetch<Array<{ id: number; share_id: string; song_id: number; share_link: string; shared_at: string; accessible_by_guest: boolean }>>('/shared-songs/');
}
