# AI Song Domain – Exercise 3

Django domain layer implementation for an AI-powered song generation platform.

---

## Local Setup

### Prerequisites

- Python 3.11+

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/OverCatX/ai-song-domain.git
cd ai-song-domain

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply database migrations
python manage.py migrate

# 5. (Optional) Load sample data
python manage.py seed

# 6. Run the development server
python manage.py runserver
```

- API: http://127.0.0.1:8000/api/
- Admin panel: http://127.0.0.1:8000/admin/ (requires `python manage.py createsuperuser`)

---

## Domain Model

![Domain Model](domain_model.png)

### Entities

| Entity                | Description                                                                |
| --------------------- | -------------------------------------------------------------------------- |
| `User`                | A registered user who generates songs on the platform                      |
| `Song`                | A generated song owned by a user, carrying its generation lifecycle status |
| `Library`             | A personal collection of songs owned by a user (one per user)              |
| `SongPrompt`          | The creative input (occasion, mood, singer tone) that defines a song       |
| `AIGenerationRequest` | A record of the AI generation job triggered by a prompt                    |
| `SharedSong`          | A shareable link produced when a user shares a song publicly               |
| `PlaybackSession`     | Tracks playback state (position, loop points, equalizer) for a song        |
| `Draft`               | A saved draft snapshot of a song before final submission                   |

### Enumerations

| Enum               | Values                                                              |
| ------------------ | ------------------------------------------------------------------- |
| `GenerationStatus` | `IN_PROGRESS`, `COMPLETED`, `FAILED`, `DRAFT`                       |
| `Occasion`         | `BIRTHDAY`, `WEDDING`, `ANNIVERSARY`, `GRADUATION`, `GENERAL`       |
| `MoodTone`         | `HAPPY`, `SAD`, `ROMANTIC`, `ENERGETIC`, `CALM`                     |
| `SingerTone`       | `MALE_DEEP`, `MALE_LIGHT`, `FEMALE_DEEP`, `FEMALE_LIGHT`, `NEUTRAL` |

### Relationships

| Relationship                     | Type                                                  |
| -------------------------------- | ----------------------------------------------------- |
| User → Song                      | One-to-many (a user generates many songs)             |
| User → Library                   | One-to-one (a user owns exactly one library)          |
| Library → Song                   | Many-to-many (a library contains many songs)          |
| Song → SongPrompt                | One-to-one (a song is defined by one prompt)          |
| SongPrompt → AIGenerationRequest | One-to-one (a prompt triggers one generation request) |
| Song → SharedSong                | One-to-one (a song can be shared once)                |
| Song → PlaybackSession           | Many-to-one (many songs can be played in one session) |
| Song → Draft                     | One-to-many (a song can have multiple draft saves)    |

---

## CRUD Evidence

Full Create, Read, Update, and Delete operations are implemented as a JSON REST API for all 8 domain entities.

### API Endpoints

| Endpoint                    | Entity              |
| --------------------------- | ------------------- |
| `/api/users/`               | User                |
| `/api/songs/`               | Song                |
| `/api/libraries/`           | Library             |
| `/api/song-prompts/`        | SongPrompt          |
| `/api/generation-requests/` | AIGenerationRequest |
| `/api/shared-songs/`        | SharedSong          |
| `/api/playback-sessions/`   | PlaybackSession     |
| `/api/drafts/`              | Draft               |

Each endpoint supports:

- `GET /api/{entity}/` — list all records
- `POST /api/{entity}/` — create a new record
- `GET /api/{entity}/{id}/` — retrieve a single record
- `PATCH /api/{entity}/{id}/` — partially update a record
- `PUT /api/{entity}/{id}/` — fully replace a record
- `DELETE /api/{entity}/{id}/` — delete a record

### Example Operations

**Create a User**

```bash
curl -X POST http://127.0.0.1:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"google_id":"g_001","email":"alice@example.com","display_name":"Alice"}'
```

**Create a Song**

```bash
curl -X POST http://127.0.0.1:8000/api/songs/ \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"title":"Birthday Song","generation_status":"DRAFT"}'
```

**Update a Song's status**

```bash
curl -X PATCH http://127.0.0.1:8000/api/songs/1/ \
  -H "Content-Type: application/json" \
  -d '{"generation_status":"COMPLETED","is_draft":false}'
```

**Delete a Song**

```bash
curl -X DELETE http://127.0.0.1:8000/api/songs/1/
```

**Read all Songs for a User**

```bash
curl http://127.0.0.1:8000/api/users/1/songs/
```

### Running Tests

41 automated tests verify every entity's CRUD behaviour, relationships, and constraints:

```bash
python manage.py test songs --verbosity=2
# Ran 41 tests in 0.xxxs — OK
```
