# Sequence diagram — song generation (use case)

This order matches **`frontend/src/pages/Generate.tsx`**, **`AIGenerationRequestViewSet.run` / `poll`**, and **`run_generation` / `refresh_generation_status`** in `songs/generation/service.py`. The client sends **`Authorization: Bearer`** after Google login. **Mock** finishes in one step with no network; **Suno** creates a task, then the browser **polls** `api.sunoapi.org` via `SunoSongGeneratorStrategy.fetch_status`.

![Sequence diagram — song generation](sequence%20-diagram.png)

*The `run` action inside the generation `ViewSet` can stream `text/plain` (`?stream=1` + `curl -N`); the DB updates from `run_generation` are the same as for non-streaming.*

← [Back to main README](../README.md#system-documentation)
