# AI Song Domain

A Django REST API for AI-powered song generation, implementing the **Strategy Pattern** to support multiple interchangeable generation backends — **Mock** (offline, instant) and **Suno** (real external API).

---

## Project Structure

```
ai-song-domain/
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

**Requirements:** Python 3.11+, Node.js 18+

### Backend

```bash
cd backend
python3 -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                               # then fill in values
python manage.py migrate
python manage.py seed                              # optional: load sample data
python manage.py runserver
```

| URL                            | Purpose       |
| ------------------------------ | ------------- |
| `http://127.0.0.1:8000/api/`   | JSON REST API |
| `http://127.0.0.1:8000/admin/` | Django Admin  |

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

The frontend connects to the backend at `http://127.0.0.1:8000`. It has two pages:

- **Create Music** — fill in a prompt, generate a song (Mock or Suno), and play it
- **My Library** — view all generated songs, toggle favorites, delete

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

> **Prerequisites:** Backend server must be running at `http://127.0.0.1:8000`.
>
> Set a base URL for convenience:
>
> ```bash
> export BASE=http://127.0.0.1:8000/api
> ```

All examples below use `curl`. You can also use the **Django Admin** or tools like **Postman / HTTPie**.

### Step 0: Create the Required Data Chain

Both Mock and Suno require the same chain: **User → Song → SongPrompt → AIGenerationRequest**.
Run these once, then substitute the returned IDs.

**1. Create or retrieve a User**

Use the `get-or-create` endpoint — safe to call multiple times with the same `google_id`.

```bash
curl -s -X POST "$BASE/users/get-or-create/" \
  -H "Content-Type: application/json" \
  -d '{
    "google_id": "test_user_001",
    "email": "test@example.com",
    "display_name": "Test User",
    "session_token": "token123"
  }' | python3 -m json.tool
```

> Note the returned `"id"` → set `USER_ID=<id>`

**2. Create a Song**

```bash
curl -s -X POST "$BASE/songs/" \
  -H "Content-Type: application/json" \
  -d "{
    \"user_id\": $USER_ID,
    \"title\": \"My Test Song\",
    \"generation_status\": \"DRAFT\",
    \"is_draft\": true
  }" | python3 -m json.tool
```

> Note the returned `"id"` → set `SONG_ID=<id>`

**3. Create a Song Prompt**

Valid enum values:

- `occasion`: `BIRTHDAY` | `WEDDING` | `ANNIVERSARY` | `GRADUATION` | `GENERAL`
- `mood_and_tone`: `HAPPY` | `SAD` | `ROMANTIC` | `ENERGETIC` | `CALM`
- `singer_tone`: `MALE_DEEP` | `MALE_LIGHT` | `FEMALE_DEEP` | `FEMALE_LIGHT` | `NEUTRAL`

```bash
curl -s -X POST "$BASE/song-prompts/" \
  -H "Content-Type: application/json" \
  -d "{
    \"song_id\": $SONG_ID,
    \"title\": \"A Calm Birthday Song\",
    \"occasion\": \"BIRTHDAY\",
    \"mood_and_tone\": \"CALM\",
    \"singer_tone\": \"NEUTRAL\",
    \"description\": \"A relaxing birthday song for my friend\"
  }" | python3 -m json.tool
```

> Note the returned `"id"` → set `PROMPT_ID=<id>`

**4. Create an AIGenerationRequest**

```bash
curl -s -X POST "$BASE/generation-requests/" \
  -H "Content-Type: application/json" \
  -d "{\"prompt_id\": $PROMPT_ID}" | python3 -m json.tool
```

> Note the returned `"id"` → set `REQ_ID=<id>`
>
> WARNING: If you see `409 Conflict`, a request already exists for this prompt. Use the `"id"` from the response instead.

---

### Mock Mode (Offline)

**No API key needed. Completes instantly.**

**Step 1 — Set strategy to Mock**

```bash
# Option A: in .env
GENERATOR_STRATEGY=mock

# Option B: environment variable (then restart server)
export GENERATOR_STRATEGY=mock

# Option C: runtime override (no restart needed)
curl -s -X POST "$BASE/generation-config/" \
  -H "Content-Type: application/json" \
  -d '{"generator_strategy": "mock"}'
```

**Step 2 — Verify active strategy**

```bash
curl -s "$BASE/generation-config/" | python3 -m json.tool
```

Expected output:

```json
{
  "generator_strategy": "mock",
  "strategy_source": "environment",
  "suno_api_configured": false
}
```

**Step 3 — Run generation**

```bash
curl -s -X POST "$BASE/generation-requests/$REQ_ID/run/" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
```

Expected result:

- `"status": "COMPLETED"`
- `"external_task_id"` starts with `mock-`
- `"external_status": "SUCCESS"`

**Step 4 — (Optional) Quick demo via management command**

```bash
python manage.py demo_generation           # runs a full generation cycle
python manage.py demo_generation --skip-run  # only prints active strategy
```

---

### Suno Mode (Live API)

**Requires a real Suno API key and internet access.**

**Step 1 — Configure API key**

```bash
# In .env (recommended):
GENERATOR_STRATEGY=suno
SUNO_API_KEY=your_bearer_token_here
```

Then restart the server: `python manage.py runserver`

**Step 2 — Verify active strategy**

```bash
curl -s "$BASE/generation-config/" | python3 -m json.tool
```

Expected output:

```json
{
  "generator_strategy": "suno",
  "strategy_source": "environment",
  "suno_api_configured": true
}
```

**Step 3 — Start generation (creates Suno task)**

Use the same `REQ_ID` from Step 0, or create a new chain.

```bash
curl -s -X POST "$BASE/generation-requests/$REQ_ID/run/" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
```

Expected result:

- `"status": "IN_PROGRESS"`
- `"external_task_id"` — Suno's task ID (non-empty)
- `"external_status": "PENDING"`

**Step 4 — Poll for completion**

Repeat until `status` is `COMPLETED` or `FAILED`.

```bash
curl -s -X POST "$BASE/generation-requests/$REQ_ID/poll/" \
  -H "Content-Type: application/json" \
  -d '{}' | python3 -m json.tool
```

Suno status progression: `PENDING` → `TEXT_SUCCESS` → `FIRST_SUCCESS` → `SUCCESS`

When `SUCCESS`, the related song will have `audio_file_url` populated.

> **No key configured?** The `run` endpoint returns a clear 400 error — there is no silent fallback to Mock.

---

### Switching Strategy at Runtime

You can switch strategies **without restarting the server** using the config endpoint.

| Action                                     | Request                                                           |
| ------------------------------------------ | ----------------------------------------------------------------- |
| Check current strategy                     | `GET /api/generation-config/`                                     |
| Switch to Mock                             | `POST /api/generation-config/` `{"generator_strategy": "mock"}`   |
| Switch to Suno                             | `POST /api/generation-config/` `{"generator_strategy": "suno"}`   |
| Clear runtime override (revert to env var) | `POST /api/generation-config/` `{"clear_runtime_override": true}` |

---

## REST API Reference

### Resources

| Endpoint                    | Resource            | Methods                       |
| --------------------------- | ------------------- | ----------------------------- |
| `/api/users/`               | User                | GET, POST, PUT, PATCH, DELETE |
| `/api/songs/`               | Song                | GET, POST, PUT, PATCH, DELETE |
| `/api/libraries/`           | Library             | GET, POST, PUT, PATCH, DELETE |
| `/api/song-prompts/`        | SongPrompt          | GET, POST, PUT, PATCH, DELETE |
| `/api/generation-requests/` | AIGenerationRequest | GET, POST, PUT, PATCH, DELETE |
| `/api/shared-songs/`        | SharedSong          | GET, POST, PUT, PATCH, DELETE |
| `/api/playback-sessions/`   | PlaybackSession     | GET, POST, PUT, PATCH, DELETE |
| `/api/drafts/`              | Draft               | GET, POST, PUT, PATCH, DELETE |

### Generation Actions

| Endpoint                              | Method | Description                                    |
| ------------------------------------- | ------ | ---------------------------------------------- |
| `/api/generation-requests/{id}/run/`  | POST   | Execute generation with current strategy       |
| `/api/generation-requests/{id}/poll/` | POST   | Poll external task status (Suno `record-info`) |
| `/api/generation-config/`             | GET    | View current active strategy and its source    |
| `/api/generation-config/`             | POST   | Switch or clear strategy at runtime            |

---

## Domain Model

![Domain model](domain_model.png)

Full field definitions and relationships are in `backend/songs/models/`.
