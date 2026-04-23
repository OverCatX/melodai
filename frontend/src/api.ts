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
  google_id: string;
  email: string;
  display_name: string;
  session_token: string;
}) {
  return apiFetch<{ id: number; user_id: string; display_name: string }>('/users/get-or-create/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

// --- Songs ---
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

export function getSong(id: number) {
  return apiFetch<{
    id: number; song_id: string; title: string;
    audio_file_url: string | null; generation_status: string;
    created_at: string; is_favorite: boolean; is_draft: boolean;
  }>(`/songs/${id}/`);
}

export function listSongs() {
  return apiFetch<Array<{
    id: number; song_id: string; title: string;
    audio_file_url: string | null; generation_status: string;
    created_at: string; is_favorite: boolean; is_draft: boolean;
  }>>('/songs/');
}

export function updateSong(id: number, payload: Partial<{ is_favorite: boolean; is_draft: boolean }>) {
  return apiFetch<{ id: number }>(`/songs/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  });
}

export function deleteSong(id: number) {
  return fetch(`${BASE_URL}/songs/${id}/`, { method: 'DELETE' });
}

export function syncSongStatus(id: number) {
  return apiFetch<{
    id: number; song_id: string; title: string;
    audio_file_url: string | null; generation_status: string;
    created_at: string; is_favorite: boolean; is_draft: boolean;
  }>(`/songs/${id}/sync-status/`, { method: 'POST' });
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
  return apiFetch<{ id: number; status: string; external_task_id: string }>('/generation-requests/', {
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
  return apiFetch<{ id: number; status: string; external_task_id: string; external_status: string }>(
    `/generation-requests/${req_id}/run/`,
    { method: 'POST', body: JSON.stringify({}) }
  );
}

export function pollGeneration(req_id: number) {
  return apiFetch<{ id: number; status: string; external_task_id: string; external_status: string }>(
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
