# Melodai Ai Song Generation

A Django REST API for AI-powered song generation, implementing the **Strategy Pattern** to support multiple interchangeable generation backends — **Mock** (offline, instant) and **Suno** (real external API).

---

## Project Structure

After `git clone`, your root folder is usually **`melodai/`** (this README uses that name; a ZIP may use a different folder name as long as it contains the folders below).

```
melodai/
├── backend/                        # Django REST API
│   ├── config/                     # Project settings & URLs
│   ├── songs/
│   │   ├── generation/
│   │   │   ├── base.py             # Strategy interface (ABC)
│   │   │   ├── factory.py          # Strategy factory + runtime override
│   │   │   ├── service.py          # run_generation / refresh_generation_status
│   │   │   ├── types.py            # SongGenerationRequest / Result dataclasses
│   │   │   └── strategies/
│   │   │       ├── mock.py         # MockSongGeneratorStrategy
│   │   │       └── suno.py         # SunoSongGeneratorStrategy
│   │   ├── models/                 # Domain models
│   │   ├── serializers/
│   │   ├── views/
│   │   └── management/commands/    # seed, demo_generation
│   ├── .env.example
│   └── requirements.txt
└── frontend/                       # React + Vite (Create Music, My Library)
```

---

## Setup

**What you need:** [Git](https://git-scm.com/), **Python 3.11+**, **Node.js 18+** (and npm), and two terminal windows (one for the API, one for the web app).

### 1. Get the project

Clone the repository and go into the project folder (the folder name is `melodai` with the default clone command):

```bash
git clone https://github.com/OverCatX/melodai.git
cd melodai
```

If you already downloaded the project as a ZIP, unzip it, then `cd` into the root folder that contains `backend/` and `frontend/`.

All commands below are run from this **project root** (`melodai/`), unless noted.

### 2. Backend (Django API)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # copy then edit; see [Environment variables](#environment-variables) below
python3 manage.py migrate
python3 manage.py seed            # optional: sample data
python3 manage.py runserver
```

Keep this terminal open. The API will be at:

| URL                            | Purpose                                                |
| ------------------------------ | ------------------------------------------------------ |
| `http://127.0.0.1:8000/api/`   | JSON REST API                                          |
| `http://127.0.0.1:8000/admin/` | Django Admin (create a superuser first if you need it) |

### 3. Frontend (Vite + React)

Open a **second** terminal. If you are at the project root (`melodai/`):

```bash
cd frontend
npm install
npm run dev
```

If you are still inside `backend/` from step 2, use `cd ../frontend` instead of `cd frontend`.

Open **`http://localhost:5173`** in your browser.

The frontend connects to the backend at `http://127.0.0.1:8000`. It has two pages:

- **Create Music** — fill in a prompt, generate a song (Mock or Suno), play it, and download the audio file when ready
- **My Library** — view all generated songs, play, download, toggle favorites, delete

The active generation strategy is shown in the top-right corner of the nav bar. Click it to toggle between Mock and Suno without restarting the server.

---

## Environment Variables

Copy `.env.example` to `.env` and configure the values. **Never commit `.env`** — it is gitignored.

```env
# Generation strategy: mock (default) | suno
GENERATOR_STRATEGY=mock

# Required only when GENERATOR_STRATEGY=suno
SUNO_API_KEY=your_bearer_token_here

```

---

## Strategy Pattern Overview

The generation layer uses the **Strategy Pattern** so that generation behavior can be swapped without changing any other part of the system.

| Component          | File                                  | Role                                                                            |
| ------------------ | ------------------------------------- | ------------------------------------------------------------------------------- |
| Strategy Interface | `songs/generation/base.py`            | `SongGenerationStrategy` (ABC) with `generate()` + `fetch_status()`             |
| Mock Strategy      | `songs/generation/strategies/mock.py` | Offline, deterministic, completes instantly                                     |
| Suno Strategy      | `songs/generation/strategies/suno.py` | Calls Suno API, returns a `taskId` for polling                                  |
| Factory            | `songs/generation/factory.py`         | Reads `GENERATOR_STRATEGY` from env/settings, instantiates the correct strategy |
| Service            | `songs/generation/service.py`         | Orchestrates `run_generation()` and `refresh_generation_status()`               |

**Strategy is selected via environment variable — selection is centralized in `factory.py` with no scattered `if/else` across the codebase.**

---

## Testing Guide

Make sure the backend is running at `http://127.0.0.1:8000` before you start. **Option order here:** full **curl** walkthrough first, then the **web UI** and **browsable API**, and the **management command** last (quickest, Mock only).

---

### Option 1 — curl / Postman (Advanced)

Run each step in order. Copy the `id` from each response and export it before the next step.

```bash
export BASE=http://127.0.0.1:8000/api
```

---

**Step 1 — Create a user**

```bash
curl -s -X POST "$BASE/users/get-or-create/" \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser"}' \
  | python3 -m json.tool
```

```json
{
  "id": 15,
  "user_id": "b86846ae-...",
  "username": "testuser",
  "display_name": "testuser"
}
```

```bash
export USER_ID=<id from response above>   # use the number (e.g. 15), NOT the UUID
```

---

**Step 2 — Create a song**

```bash
curl -s -X POST "$BASE/songs/" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\":$USER_ID,\"title\":\"My Song\",\"generation_status\":\"DRAFT\",\"is_draft\":true}" \
  | python3 -m json.tool
```

```bash
export SONG_ID=<id from response above>   # use the number, NOT song_id UUID
```

---

**Step 3 — Create a prompt**

```bash
curl -s -X POST "$BASE/song-prompts/" \
  -H "Content-Type: application/json" \
  -d "{\"song_id\":$SONG_ID,\"title\":\"Birthday Song\",\"occasion\":\"BIRTHDAY\",\"mood_and_tone\":\"HAPPY\",\"singer_tone\":\"NEUTRAL\",\"description\":\"\"}" \
  | python3 -m json.tool
```

Valid values — `occasion`: BIRTHDAY · WEDDING · ANNIVERSARY · GRADUATION · GENERAL | `mood_and_tone`: HAPPY · SAD · ROMANTIC · ENERGETIC · CALM | `singer_tone`: MALE_DEEP · MALE_LIGHT · FEMALE_DEEP · FEMALE_LIGHT · NEUTRAL

```bash
export PROMPT_ID=<id from response above>   # use the number, NOT prompt_id UUID
```

---

**Step 4 — Create a generation request**

```bash
curl -s -X POST "$BASE/generation-requests/" \
  -H "Content-Type: application/json" \
  -d "{\"prompt_id\":$PROMPT_ID}" \
  | python3 -m json.tool
```

> If you get `409 Conflict`, the request already exists — use the `id` from the response.

```bash
export REQ_ID=<id from response above>   # use the number (e.g. 29), NOT request_id UUID
```

---

**Step 5 — Switch strategy, then run generation**

**For Mock** (no API key needed):

```bash
# Switch to mock
curl -s -X POST "$BASE/generation-config/" \
  -H "Content-Type: application/json" \
  -d '{"generator_strategy":"mock"}' | python3 -m json.tool

# Run — completes immediately
curl -s -X POST "$BASE/generation-requests/$REQ_ID/run/" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
```

Expected: `"status": "COMPLETED"`, `"external_task_id": "mock-..."`

---

**For Suno** (requires `SUNO_API_KEY` in `.env`):

```bash
# Switch to suno
curl -s -X POST "$BASE/generation-config/" \
  -H "Content-Type: application/json" \
  -d '{"generator_strategy":"suno"}' | python3 -m json.tool
```

**Run with live poll lines in the terminal (one command, no shell script)** — add `?stream=1` and use `curl -N` (`--no-buffer`) so each `[poll] …` line appears as the server updates (waits up to 60×5s, same as the web UI). The **last line** is the same JSON a normal `run` would return; grab it with `tail -1`:

```bash
curl -N -s -X POST "$BASE/generation-requests/$REQ_ID/run/?stream=1" \
  -H "Content-Type: application/json" \
  -d '{}'
# [stream] …  →  [poll] 1/60 …  →  last line: full JSON
# Only the JSON:  … | tail -1 | python3 -m json.tool
```

**Or** run and poll by hand (each call returns once):

```bash
# Run — returns IN_PROGRESS with a taskId
curl -s -X POST "$BASE/generation-requests/$REQ_ID/run/" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool

# Poll until status = COMPLETED (repeat every few seconds)
curl -s -X POST "$BASE/generation-requests/$REQ_ID/poll/" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
# PENDING → TEXT_SUCCESS → FIRST_SUCCESS → SUCCESS
```

**Step 6 — Download the MP3**

Wait until `run` / `stream` finishes with `status: COMPLETED`, then download.

| Value           | Where to get it                                                                                                 |
| --------------- | --------------------------------------------------------------------------------------------------------------- |
| `**SONG_ID`\*\* | The `song_id` field in the last JSON line (**not** the generation request’s `"id"`), or the song id from Step 2 |
| `**USER_ID`\*\* | Your user’s numeric `id` from Step 1 (same account that owns the song)                                          |

**Web UI:** use Download — the app adds `?user_id` for you.  
`**curl`:** you must add `?user_id=$USER_ID` or the server returns **404\*\*.

```bash
export USER_ID=<from Step 1>
export SONG_ID=<from Step 2 or song_id in JSON>
curl -fSL -o "my-song.mp3" "$BASE/songs/$SONG_ID/download/?user_id=$USER_ID"
```

The file is saved in the directory where you run `curl` (often `~`); or use e.g. `-o "$HOME/Downloads/my-song.mp3"`.

**Switch strategy at runtime (no restart):**

| Action                 | Request                                                           |
| ---------------------- | ----------------------------------------------------------------- |
| Check current strategy | `GET /api/generation-config/`                                     |
| Switch to Mock         | `POST /api/generation-config/` `{"generator_strategy": "mock"}`   |
| Switch to Suno         | `POST /api/generation-config/` `{"generator_strategy": "suno"}`   |
| Revert to `.env`       | `POST /api/generation-config/` `{"clear_runtime_override": true}` |

---

### Option 2 — Web UI (Recommended for full flow)

The frontend supports both Mock and Suno with no extra setup.

1. Start both servers (backend + frontend)
2. Open `http://localhost:5173` and log in
3. Click the **Mock / Suno badge** in the top-right to switch strategy
4. Go to **Create Music**, fill in the form, and click **Generate**
5. Check **My Library** to see the result — use the 🔄 button to sync status if needed
6. **Download** — use **Download audio** on the result screen or the ⬇ action in **My Library**; the app attaches `user_id` and streams the file through the backend from the song’s `audio_file_url`

---

### Option 3 — Browsable API (No curl needed)

Django REST Framework provides a built-in web interface for every endpoint.

Open any of these in your browser:

| URL                                                        | What you can do                                         |
| ---------------------------------------------------------- | ------------------------------------------------------- |
| `http://127.0.0.1:8000/api/`                               | Browse all endpoints                                    |
| `http://127.0.0.1:8000/api/generation-config/`             | Check/switch strategy                                   |
| `http://127.0.0.1:8000/api/generation-requests/`           | List or create requests                                 |
| `http://127.0.0.1:8000/api/generation-requests/{id}/run/`  | Trigger generation                                      |
| `http://127.0.0.1:8000/api/generation-requests/{id}/poll/` | Poll status                                             |
| `http://127.0.0.1:8000/api/songs/{id}/download/?user_id=`  | Download audio (GET; set `user_id` to the song’s owner) |

Download is a **GET** that returns a binary file — see **Option 1, Step 6** for a `curl` example. Most other links in the table are POST and show an HTML form in DRF.

---

### Option 4 — Management Command (Easiest, Mock only)

One command. No full curl walkthrough needed.

```bash
cd backend
python3 manage.py demo_generation
```

Expected output:

```
Active strategy: MockSongGeneratorStrategy
external_task_id='mock-xxxxxxxxxxxxxxxx'
external_status='SUCCESS'
ai_status=COMPLETED
song.generation_status=COMPLETED
song.audio_file_url='https://...'
```

---

## REST API Reference

### Resources

| Endpoint                    | Resource            | Methods                                                                                                                                       |
| --------------------------- | ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `/api/users/`               | User                | GET, POST, PUT, PATCH, DELETE                                                                                                                 |
| `/api/songs/`               | Song                | GET, POST, PUT, PATCH, DELETE (list/detail for reads & mutations use `?user_id=<owner>`; `GET /api/users/{id}/songs/` lists one user’s songs) |
| `/api/libraries/`           | Library             | GET, POST, PUT, PATCH, DELETE                                                                                                                 |
| `/api/song-prompts/`        | SongPrompt          | GET, POST, PUT, PATCH, DELETE                                                                                                                 |
| `/api/generation-requests/` | AIGenerationRequest | GET, POST, PUT, PATCH, DELETE                                                                                                                 |
| `/api/shared-songs/`        | SharedSong          | GET, POST, PUT, PATCH, DELETE                                                                                                                 |
| `/api/playback-sessions/`   | PlaybackSession     | GET, POST, PUT, PATCH, DELETE                                                                                                                 |
| `/api/drafts/`              | Draft               | GET, POST, PUT, PATCH, DELETE                                                                                                                 |

### Generation Actions

| Endpoint                              | Method | Description                                                                                               |
| ------------------------------------- | ------ | --------------------------------------------------------------------------------------------------------- |
| `/api/users/get-or-create/`           | POST   | Create or retrieve user by `username`                                                                     |
| `/api/generation-requests/{id}/run/`  | POST   | Execute generation; optional `?stream=1` streams poll lines (`text/plain`, last line JSON; use `curl -N`) |
| `/api/generation-requests/{id}/poll/` | POST   | Poll Suno task status (`record-info`)                                                                     |
| `/api/songs/{id}/sync-status/`        | POST   | Re-sync song status from latest generation request                                                        |
| `/api/songs/{id}/download/`           | GET    | Stream download; requires `?user_id=` (song owner), same as other song detail routes                      |
| `/api/generation-config/`             | GET    | View current strategy + source + suno key status                                                          |
| `/api/generation-config/`             | POST   | Switch strategy or clear runtime override                                                                 |

---

## Domain Model

![MeloDAI domain model](domain_model.png)

Full field definitions and relationships are in `backend/songs/models/`.
