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

## Testing

Run the test suite from `backend/` (with the project venv activated):

```bash
cd backend
source venv/bin/activate    # Windows: venv\Scripts\activate
python manage.py test songs
```

**Full guide** — automated tests (coverage), **curl / Postman** walkthrough, **web UI**, **browsable API**, and **`demo_generation`**: **[docs/testing-guide.md](docs/testing-guide.md)**.

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

Central place for diagrams and the long **testing** guide. Each row links to a page under `docs/` (figures live in `docs/images/` where noted).

| Document | What it contains |
|----------|------------------|
| [Testing guide](docs/testing-guide.md) | **Automated tests** (`manage.py test`) + **curl** / Postman + web UI + browsable API + `demo_generation` |
| [Domain model](docs/domain-model.md) | Overview image (`docs/images/domain_model.png`), Mermaid `erDiagram` vs `songs/models/` |
| [Class diagram (UML)](docs/classdiagram.md) | **Mermaid** `classDiagram` blocks in the doc (source of truth) |
| [Sequence — song generation](docs/Sequence-diagram.md) | Generation use case — `docs/images/sequence -diagram.png` |
| [MVT architecture](docs/mvt-diagram.md) | Model–View–Template for this REST + React app — `docs/images/mvt-diagram.png` |
