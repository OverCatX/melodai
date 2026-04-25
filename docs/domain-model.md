# Domain model

Overview figure, **Mermaid ERD**, and **enumerations** — aligned 1:1 with `backend/songs/models/`.

**Conventions (Django):** Every `models.Model` has an autoincrement integer primary key **`id`** in the database (not shown in the diagram below). The UUID fields such as `user_id`, `song_id`, etc. are **additional** business identifiers (`unique=True`, `editable=False`) as in the source files.

![MeloDAI domain model](images/domain_model.png)

## Entity–relationship (Mermaid)

Relationships match ForeignKey / OneToOne / ManyToMany in code:

* **Library** — `user` = `OneToOneField` to **User** (each user at most one library record).
* **Song** — `user` = `ForeignKey` to **User**; `playback_session` = optional `ForeignKey` to **PlaybackSession** (`null=True`); a single **PlaybackSession** can be shared by many **Song** rows (`related_name="songs"`), or songs may leave it unset.
* **Library** ↔ **Song** — `ManyToManyField` `Library.songs` / `Song.libraries`.
* **SongPrompt** — `OneToOneField` to **Song** (`related_name="prompt"`).
* **AIGenerationRequest** — `OneToOneField` to **SongPrompt** (`related_name="generation_request"`).
* **Draft** — `ForeignKey` to **Song** (`related_name="drafts"`, 0..* drafts per song).
* **SharedSong** — `OneToOneField` to **Song** (`related_name="shared_song"`, 0 or 1 per song).

```mermaid
erDiagram
  User {
    uuid user_id
    string username
    string display_name
    string email
    string google_id
    string session_token
  }
  Library {
    string filter_criteria
    int total_count
  }
  Song {
    uuid song_id
    string title
    string audio_file_url
    string generation_status
    datetime created_at
    bool is_favorite
    bool is_draft
    string share_link
  }
  PlaybackSession {
    uuid session_id
    float current_position
    float loop_start
    float loop_end
    string equalizer_settings
  }
  SongPrompt {
    uuid prompt_id
    string title
    string occasion
    string mood_and_tone
    string singer_tone
    string description
  }
  AIGenerationRequest {
    uuid request_id
    datetime submitted_at
    string status
    string error_message
    string external_task_id
    string external_status
  }
  Draft {
    uuid draft_id
    datetime saved_at
    bool is_submitted
    string retention_policy
  }
  SharedSong {
    uuid share_id
    string share_link
    datetime shared_at
    bool accessible_by_guest
  }

  User ||--|| Library : "OneToOne library.user"
  User ||--o{ Song : "user FK"
  Library }o--o{ Song : "M2M songs"
  PlaybackSession ||--o{ Song : "nullable FK on song"
  Song ||--|| SongPrompt : "OneToOne prompt.song"
  SongPrompt ||--|| AIGenerationRequest : "OneToOne to prompt"
  Song ||--o{ Draft : "drafts"
  Song ||--o| SharedSong : "OneToOne shared_song"
```

**Field / type details (code parity):**

| Entity | Django notes |
|--------|----------------|
| **User** | `email` default `""`; `google_id` / `session_token` may be `NULL` in DB. |
| **Library** | `filter_criteria` `max_length=500`, blank; `total_count` `PositiveIntegerField`, default 0. |
| **Song** | `generation_status` uses **`GenerationStatus`** (see below); `share_link` / `audio_file_url` may be blank. |
| **PlaybackSession** | `loop_start` / `loop_end` nullable `FloatField`. |
| **SongPrompt** | `occasion` / `mood_and_tone` / `singer_tone` are `CharField` with **Occasion / MoodTone / SingerTone** choices. |
| **AIGenerationRequest** | `status` uses **`GenerationStatus`**; `error_message` / `external_*` may be blank. |
| **Draft** | `retention_policy` may be blank. |
| **SharedSong** | `share_link` `URLField` `unique=True`. |

## Enumerations (`TextChoices`)

Values below are the **database / API string values** (same as `backend/songs/models/*.py`).

| Enum | Values |
|------|--------|
| **GenerationStatus** | `IN_PROGRESS`, `COMPLETED`, `FAILED`, `DRAFT` — used on **Song** and **AIGenerationRequest**. |
| **Occasion** | `BIRTHDAY`, `WEDDING`, `ANNIVERSARY`, `GRADUATION`, `GENERAL` — **SongPrompt.occasion**. |
| **MoodTone** | `HAPPY`, `SAD`, `ROMANTIC`, `ENERGETIC`, `CALM` — **SongPrompt.mood_and_tone**. |
| **SingerTone** | `MALE_DEEP`, `MALE_LIGHT`, `FEMALE_DEEP`, `FEMALE_LIGHT`, `NEUTRAL` — **SongPrompt.singer_tone**. |

← [Back to main README](../README.md#system-documentation)
