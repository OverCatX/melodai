# Class diagram (UML)

**REST API + generation (Strategy pattern)** in `backend/songs/`. The diagram is easier to read in **three layers**:

| Layer | What it is |
|-------|------------|
| **1. ViewSet** | `ModelViewSet` per resource (user, song, library, …) |
| **2. Non-ViewSet routes** | `auth_config`, `auth_google`, `generation_config` — `@api_view` functions, not a `ViewSet` |
| **3. Generation** | `SongGenerationStrategy` (Mock / Suno) + `factory.py` + `service.py` |

Standard DRF `list` / `retrieve` / `create` / … map to HTTP as usual for each route.

---

## 1) All ViewSets

```mermaid
classDiagram
  direction TB
  class ModelViewSet {
    <<rest_framework ModelViewSet>>
  }
  class UserViewSet
  class SongViewSet
  class LibraryViewSet
  class SongPromptViewSet
  class AIGenerationRequestViewSet
  class SharedSongViewSet
  class PlaybackSessionViewSet
  class DraftViewSet
  ModelViewSet <|-- UserViewSet
  ModelViewSet <|-- SongViewSet
  ModelViewSet <|-- LibraryViewSet
  ModelViewSet <|-- SongPromptViewSet
  ModelViewSet <|-- AIGenerationRequestViewSet
  ModelViewSet <|-- SharedSongViewSet
  ModelViewSet <|-- PlaybackSessionViewSet
  ModelViewSet <|-- DraftViewSet
  note for AIGenerationRequestViewSet "actions: run, poll, stream"
  note for SongViewSet "e.g. sync_status calls service"
```

**In the repo:** `views/user.py`, `song.py`, `library.py`, `song_prompt.py`, `ai_generation_request.py`, `shared_song.py`, `playback_session.py`, `draft.py` — re-exported from `views/__init__.py`.

---

## 2) Function-based endpoints (not ViewSet)

```mermaid
classDiagram
  direction TB
  class auth_config
  class auth_google
  class generation_config
  note for auth_config "auth_google.py GET /api/auth/config/"
  note for auth_google "auth_google.py POST /api/auth/google/"
  note for generation_config "generation_config.py GET+POST /api/generation-config/"
```

---

## 3) Strategy + factory + service

- **`factory.py`** reads `GENERATOR_STRATEGY` and any **runtime** override (via `generation_config`) and instantiates **Mock** or **Suno**.
- **`service.py`** calls `get_song_generator_strategy()` then `generate` / updates **`Song`** and **`AIGenerationRequest`** — **strategies do not write the DB** themselves.
- **`SunoSongGeneratorStrategy`** calls the provider with **`requests`**.

```mermaid
classDiagram
  direction TB
  class SongGenerationStrategy {
    <<abstract>>
    +generate
    +fetch_status
  }
  class MockSongGeneratorStrategy
  class SunoSongGeneratorStrategy
  class serviceModule {
    <<module>>
  }
  class factoryModule {
    <<module>>
  }
  SongGenerationStrategy <|-- MockSongGeneratorStrategy
  SongGenerationStrategy <|-- SunoSongGeneratorStrategy
  factoryModule ..> MockSongGeneratorStrategy
  factoryModule ..> SunoSongGeneratorStrategy
  serviceModule --> factoryModule
  serviceModule --> SongGenerationStrategy
  note for MockSongGeneratorStrategy "offline fake task + URL"
  note for SunoSongGeneratorStrategy "POST generate, GET record-info"
  note for serviceModule "service.py run_generation refresh_status"
  note for factoryModule "factory.py get and create strategy"
```

**How this ties to ViewSets:** `AIGenerationRequestViewSet` (actions `run` / `poll`) and `SongViewSet` (e.g. `sync_status`) call into `service.py` — arrows to `service` are not duplicated in the diagrams above to avoid clutter; the **code imports `service` directly**.

---

## Notes

* **Domain entities / ERD:** [`domain-model.md`](domain-model.md)
* **Domain enum values** (`GenerationStatus`, etc.): `backend/songs/models/`

← [Back to main README](../README.md#system-documentation)
