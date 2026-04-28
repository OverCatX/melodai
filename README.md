# Melodai Ai Song Generation

A Django REST API for AI-powered song generation, implementing the **Strategy Pattern** to support multiple interchangeable generation backends — **Mock** (offline, instant) and **Suno** (real external API).

---

## Setup

**Prerequisites:** [Git](https://git-scm.com/), **Python 3.11+**, **Node.js 18+** (npm), and **two terminals** (backend + frontend).

Work from the **repository root**: the folder that contains `**backend/`** and `**frontend/**` (often `melodai` after `git clone`). ZIP downloads: unzip, then `cd` into that same kind of folder.

### 1. Get the project

```bash
git clone https://github.com/OverCatX/melodai.git
cd melodai
```

### 2. Configure Google OAuth

The web app signs in **only with Google**. Flow in one line: **Login** → Django `**/api/auth/google/login/`** → Google → Django `**/api/auth/google/callback/**` → React `**/auth/callback**` (session stored in the browser).

Do this **before** you expect the Login button to work. In [Google Cloud Console](https://console.cloud.google.com/apis/credentials):

1. Pick or create a project.
2. **OAuth consent screen** → **Overview** → app name + user support email → **Save**. If the app is in **Testing**, add your Google account under **Test users**.
3. **Create credentials** → **OAuth client ID** → type **Web application**.
4. **Authorized JavaScript origins** (scheme + host + port, **no path**): add `http://localhost:5173`, `http://localhost`, and `http://127.0.0.1:5173` if you ever open the UI with that host (`localhost` and `127.0.0.1` are different to Google).
5. **Authorized redirect URIs**: add **exactly** (trailing slash included unless you change it everywhere):
  `http://127.0.0.1:8000/api/auth/google/callback/`
6. **Create** → copy the **Client ID** and **Client secret** into `**backend/.env`** (see [Environment variables](#environment-variables)).


| If something fails                   | What to check                                                                            |
| ------------------------------------ | ---------------------------------------------------------------------------------------- |
| `redirect_uri_mismatch`              | Same callback URL in Google Cloud and in `GOOGLE_OAUTH_REDIRECT_URI`.                    |
| Login stuck / “not fully configured” | Both `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` set; restart `runserver`. |
| Access blocked                       | Consent screen **Testing** → your Gmail must be a **Test user**.                         |


**Optional:** `POST /api/auth/google/` with `{"id_token":"..."}` for scripts or tests (no client secret).

### 3. Backend (Django)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env: Google keys, optional Suno (see Environment variables)
python3 manage.py migrate
python3 manage.py seed            # optional
python3 manage.py runserver
```


| URL                            | Purpose      |
| ------------------------------ | ------------ |
| `http://127.0.0.1:8000/api/`   | REST API     |
| `http://127.0.0.1:8000/admin/` | Django admin |


### 4. Frontend (React + Vite)

Second terminal, from the **repo root**:

```bash
cd frontend             # from repo root; or cd ../frontend if you are still in backend/
cp .env.example .env    # optional; frontend needs no Google secrets
npm install
npm run dev
```

Open `**http://localhost:5173**` and click **Continue with Google**. The hostname must match what you put under **JavaScript origins** in Google.

**In the app:** **Create Music** (generate, play, download) · **My Library**. The **Mock / Suno** badge in the nav switches strategy without restarting servers.

---

## Environment variables

Copy `**backend/.env.example`** → `**backend/.env**`. **Never commit `.env`.**

```env
GENERATOR_STRATEGY=mock
SUNO_API_KEY=                      # only if using suno

GOOGLE_OAUTH_CLIENT_ID=
GOOGLE_OAUTH_CLIENT_SECRET=
GOOGLE_OAUTH_REDIRECT_URI=http://127.0.0.1:8000/api/auth/google/callback/
GOOGLE_OAUTH_FRONTEND_BASE=http://localhost:5173

# ALLOW_DISPLAY_NAME_GET_OR_CREATE=true   # curl/Postman only; default off
```

After login, the UI sends `**Authorization: Bearer <session_token>**`. `**POST /api/users/get-or-create/**` stays disabled unless you set `ALLOW_DISPLAY_NAME_GET_OR_CREATE=true`.

---

## Testing Guide

**Further reading:** [Strategy pattern](docs/strategy-pattern.md) · [Automated tests (Django)](docs/automated-tests.md).

The sections below are **manual** checks: curl, web UI, browsable API, and management commands.

### Manual and integration

Start the backend at `http://127.0.0.1:8000` first. Suggested order: full **curl** walkthrough, then the **web UI** and **browsable API**, and the **management command** last (quickest, Mock only).

#### Option 1 — curl / Postman (Advanced)

Run each step in order. Copy the `id` from each response and export it before the next step.

```bash
export BASE=http://127.0.0.1:8000/api
```

---

**Step 1 — Create a user (or obtain a session)**

By default, `**POST /api/users/get-or-create/`** is disabled. For this curl walkthrough, add to `backend/.env`:

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


| Value       | Where to get it                                                                                                 |
| ----------- | --------------------------------------------------------------------------------------------------------------- |
| **SONG_ID** | The `song_id` field in the last JSON line (**not** the generation request’s `"id"`), or the song id from Step 2 |
| **USER_ID** | Your user’s numeric `id` from Step 1 (same account that owns the song)                                          |


**Web UI:** use Download — the app adds `?user_id` for you.  
**curl:** you must add `?user_id=$USER_ID` or the server returns **404**.

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

#### Option 2 — Web UI (Recommended for full flow)

The frontend supports both Mock and Suno with no extra setup.

1. Start both servers (backend + frontend)
2. Open `http://localhost:5173` and log in with Google (if the button is missing, see [Configure Google OAuth](#2-configure-google-oauth))
3. Click the **Mock / Suno badge** in the top-right to switch strategy
4. Go to **Create Music**, fill in the form, and click **Generate**
5. Check **My Library** to see the result — use the 🔄 button to sync status if needed
6. **Download** — use **Download audio** on the result screen or the ⬇ action in **My Library**; the app attaches `user_id` and streams the file through the backend from the song’s `audio_file_url`

---

#### Option 3 — Browsable API (No curl needed)

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

#### Option 4 — Management Command (Easiest, Mock only)

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


| Endpoint                              | Method | Description                                                                                                |
| ------------------------------------- | ------ | ---------------------------------------------------------------------------------------------------------- |
| `/api/users/get-or-create/`           | POST   | Create or retrieve user by `username` — **only if** `ALLOW_DISPLAY_NAME_GET_OR_CREATE=true` (default: off) |
| `/api/generation-requests/{id}/run/`  | POST   | Execute generation; optional `?stream=1` streams poll lines (`text/plain`, last line JSON; use `curl -N`)  |
| `/api/generation-requests/{id}/poll/` | POST   | Poll Suno task status (`record-info`)                                                                      |
| `/api/songs/{id}/sync-status/`        | POST   | Re-sync song status from latest generation request                                                         |
| `/api/songs/{id}/download/`           | GET    | Stream download; requires `?user_id=` (song owner), same as other song detail routes                       |
| `/api/generation-config/`             | GET    | View current strategy + source + suno key status                                                           |
| `/api/generation-config/`             | POST   | Switch strategy or clear runtime override                                                                  |


### Authentication (Google)


| Endpoint                     | Method | Description                                                                                                                            |
| ---------------------------- | ------ | -------------------------------------------------------------------------------------------------------------------------------------- |
| `/api/auth/config/`          | GET    | Public: `google_client_id`, `google_login_url`, `google_oauth_ready` (ID + secret set)                                                 |
| `/api/auth/google/login/`    | GET    | Redirect to Google consent (stores `state` in Django session); requires ID + secret + `GOOGLE_OAUTH_REDIRECT_URI`                      |
| `/api/auth/google/callback/` | GET    | OAuth redirect: exchange `code`, verify `id_token`, redirect to SPA `/auth/callback?session_token=...`                                 |
| `/api/auth/google/`          | POST   | Body `{"id_token":"..."}` — verify JWT; returns user + `session_token` (optional; tests / API clients; needs `GOOGLE_OAUTH_CLIENT_ID`) |


---

## System documentation

Central place for design and test notes under `docs/` (figures in `docs/images/` where noted). **Manual** testing (curl, UI, etc.) is in **[Testing Guide](#testing-guide)** above.


| Document                                               | What it contains                                                                        |
| ------------------------------------------------------ | --------------------------------------------------------------------------------------- |
| [Strategy pattern](docs/strategy-pattern.md)           | Mock/Suno strategy layout, factory, service                                             |
| [Automated tests (Django)](docs/automated-tests.md)    | `manage.py test`, coverage, no UI tests yet                                             |
| [Domain model](docs/domain-model.md)                   | Overview image (`docs/images/domain_model.png`), Mermaid `erDiagram` vs `songs/models/` |
| [Class diagram (UML)](docs/classdiagram.md)            | **Mermaid** `classDiagram` blocks in the doc (source of truth)                          |
| [Sequence — song generation](docs/Sequence-diagram.md) | Generation use case — `docs/images/sequence -diagram.png`                               |
| [MVT architecture](docs/mvt-diagram.md)                | Model–View–Template for this REST + React app — `docs/images/mvt-diagram.png`           |


