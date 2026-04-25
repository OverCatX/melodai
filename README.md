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
│   │   │   ├── song_generation_request.py  # Request dataclass
│   │   │   ├── song_generation_result.py   # Result dataclass
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

If your folder is **not** named `melodai` (e.g. a fork or a different clone path), that is fine — use whatever directory contains **`backend/`** and **`frontend/`**.

All commands below are run from this **project root** (that folder), unless noted.

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
cp .env.example .env   # Windows: copy .env.example .env — then set VITE_GOOGLE_CLIENT_ID (same as backend GOOGLE_OAUTH_CLIENT_ID) for Google Sign-In
npm install
npm run dev
```

If you are still inside `backend/` from step 2, use `cd ../frontend` instead of `cd frontend`.

Open **`http://localhost:5173`** in your browser. The **Login** page needs **Google OAuth** to be configured — if the Google button is missing or sign-in fails, set `GOOGLE_OAUTH_CLIENT_ID` in `backend/.env` and `VITE_GOOGLE_CLIENT_ID` in `frontend/.env` (see [Environment variables](#environment-variables)), then restart **both** the API and `npm run dev`.

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

# Google Sign-In (required for the web app)
# GOOGLE_OAUTH_CLIENT_ID=...client-id...apps.googleusercontent.com

# Optional: allow POST /api/users/get-or-create/ for curl/Postman (default: off, Google-only API)
# ALLOW_DISPLAY_NAME_GET_OR_CREATE=true
```

**Web app sign-in** is **Google only**. Set `GOOGLE_OAUTH_CLIENT_ID` in `backend/.env` and run the API — the login page uses **`GET /api/auth/config/`** (or `VITE_GOOGLE_CLIENT_ID` at build time if you set `frontend/.env`).

### Google OAuth (required for the web UI)

1. In [Google Cloud Console](https://console.cloud.google.com/apis/credentials), create an **OAuth 2.0 Client ID** of type **Web application**.
2. Add **Authorized JavaScript origins**: `http://localhost:5173` (and your production origin if needed).
3. Put the **Client ID** in `backend/.env` as `GOOGLE_OAUTH_CLIENT_ID` (used to verify `id_token` and to serve `GET /api/auth/config/`).
4. `POST /api/auth/google/` with body `{"id_token":"<JWT>"}` returns a `session_token`. The app stores it and sends `Authorization: Bearer <session_token>`. The legacy **`POST /api/users/get-or-create/`** is **disabled** unless you set `ALLOW_DISPLAY_NAME_GET_OR_CREATE=true` (for curl testing only).

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

### Automated tests (Django)

Backend tests live in **`backend/songs/tests/`** (e.g. `test_api.py`). They use Django’s test runner, a **temporary SQLite database** (no need for `db.sqlite3` while testing), and **do not** call Google or Suno in production mode — Google `id_token` verification is **mocked**; generation uses the **Mock** strategy.

**Run all tests** from `backend/` with the project venv:

```bash
cd backend
source venv/bin/activate    # Windows: venv\Scripts\activate
python manage.py test songs
```

**Useful options:**

| Command | What it does |
|--------|----------------|
| `python manage.py test songs -v 2` | Verbose: print each test name |
| `python manage.py test songs.tests.test_api.MockGenerationRunTests` | Run one test class only |
| `python manage.py test songs.tests.test_api.AuthGoogleTests.test_valid_id_token_returns_user_and_session` | Run a single test method |

**What is covered (high level):**

| Area | What the tests check |
|------|----------------------|
| **Auth** | `GET /api/auth/config/`, `POST /api/auth/google/` (503 / 400 / 200 with mocked verify) |
| **Users** | `POST /api/users/get-or-create/` when allowed vs forbidden; `GET /api/users/{id}/songs/` Bearer scoping (403 for another user’s id) |
| **Generation** | `GET/POST /api/generation-config/`; full **Mock** path: create user → song → prompt → `generation-request` → `…/run/` until `COMPLETED` |
| **Models** | Light sanity (e.g. `User` string) |

**Frontend:** there is no automated UI test in this repo yet; exercise the Vite app manually (see **Option 2** below) or add something like Vitest/Playwright separately if you need it.

---

**Manual / integration checks below** — start the backend at `http://127.0.0.1:8000` first. **Option order:** full **curl** walkthrough, then the **web UI** and **browsable API**, and the **management command** last (quickest, Mock only).

### Option 1 — curl / Postman (Advanced)

Run each step in order. Copy the `id` from each response and export it before the next step.

```bash
export BASE=http://127.0.0.1:8000/api
```

---

**Step 1 — Create a user (or obtain a session)**

By default, **`POST /api/users/get-or-create/` is disabled**. For this curl walkthrough, add to `backend/.env`:

`ALLOW_DISPLAY_NAME_GET_OR_CREATE=true` — then restart the server.

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
  "display_name": "testuser",
  "email": "",
  "session_token": "..."
}
```

```bash
export USER_ID=<id from response above>   # use the number (e.g. 15), NOT the UUID
export TOKEN=<session_token from response>   # optional: use Authorization: Bearer for scoped routes
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
2. Open `http://localhost:5173` and log in (Google — see **Environment Variables** if the Login page is empty)
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
| `/api/users/get-or-create/`           | POST   | Create or retrieve user by `username` — **only if** `ALLOW_DISPLAY_NAME_GET_OR_CREATE=true` (default: off)       |
| `/api/generation-requests/{id}/run/`  | POST   | Execute generation; optional `?stream=1` streams poll lines (`text/plain`, last line JSON; use `curl -N`) |
| `/api/generation-requests/{id}/poll/` | POST   | Poll Suno task status (`record-info`)                                                                     |
| `/api/songs/{id}/sync-status/`        | POST   | Re-sync song status from latest generation request                                                        |
| `/api/songs/{id}/download/`           | GET    | Stream download; requires `?user_id=` (song owner), same as other song detail routes                      |
| `/api/generation-config/`             | GET    | View current strategy + source + suno key status                                                          |
| `/api/generation-config/`             | POST   | Switch strategy or clear runtime override                                                                 |

### Authentication (Google)

| Endpoint                | Method | Description                                                                                    |
| ----------------------- | ------ | ---------------------------------------------------------------------------------------------- |
| `/api/auth/config/`     | GET    | Public: `{"google_client_id":"..."}` for the Login page (empty if OAuth is not configured)  |
| `/api/auth/google/`     | POST   | Body `{"id_token":"..."}` — verify Google JWT; returns user + `session_token` for `Authorization: Bearer` (requires `GOOGLE_OAUTH_CLIENT_ID`) |

---

## System documentation

Central place for model and diagram write-ups. Each row links to a page under `docs/` (figures are embedded there).

| Document | What it contains |
|----------|------------------|
| [Domain model](docs/domain-model.md) | Overview image (`docs/images/domain_model.png`), Mermaid `erDiagram` vs `songs/models/` |
| [Class diagram (UML)](docs/classdiagram.md) | **Mermaid** `classDiagram` in the doc + optional `docs/images/class-diagram.png` |
| [Sequence — song generation](docs/Sequence-diagram.md) | Generation use case — `docs/images/sequence -diagram.png` |
| [MVT architecture](docs/mvt-diagram.md) | Model–View–Template for this REST + React app — `docs/images/mvt-diagram.png` |
