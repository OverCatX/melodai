# Strategy pattern overview

The generation layer uses the **Strategy Pattern** so that generation behavior can be swapped without changing any other part of the system.

| Component          | File                                  | Role                                                                            |
| ------------------ | ------------------------------------- | ------------------------------------------------------------------------------- |
| Strategy Interface | `songs/generation/base.py`            | `SongGenerationStrategy` (ABC) with `generate()` + `fetch_status()`             |
| Mock Strategy      | `songs/generation/strategies/mock.py` | Offline, deterministic, completes instantly                                     |
| Suno Strategy      | `songs/generation/strategies/suno.py` | Calls Suno API, returns a `taskId` for polling                                |
| Factory            | `songs/generation/factory.py`         | Reads `GENERATOR_STRATEGY` from env/settings, instantiates the correct strategy |
| Service            | `songs/generation/service.py`         | Orchestrates `run_generation()` and `refresh_generation_status()`               |

**Strategy is selected via environment variable** — selection is centralized in `factory.py` with no scattered `if/else` across the codebase.

For diagrams, see [Class diagram (UML)](classdiagram.md) (generation package) and the main [README](../README.md) for runtime strategy switching via `/api/generation-config/`.
