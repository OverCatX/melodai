# Automated tests (Django)

Backend tests live in **`backend/songs/tests/`** (e.g. `test_api.py`). They use Django’s test runner, a **temporary SQLite database** (no need for `db.sqlite3` while testing), and **do not** call Google or Suno in production mode — Google `id_token` verification is **mocked**; generation uses the **Mock** strategy.

## Run all tests

From `backend/` with the project venv:

```bash
cd backend
source venv/bin/activate    # Windows: venv\Scripts\activate
python manage.py test songs
```

## Useful options

| Command                                                                                                   | What it does                  |
| --------------------------------------------------------------------------------------------------------- | ----------------------------- |
| `python manage.py test songs -v 2`                                                                        | Verbose: print each test name |
| `python manage.py test songs.tests.test_api.MockGenerationRunTests`                                       | Run one test class only       |
| `python manage.py test songs.tests.test_api.AuthGoogleTests.test_valid_id_token_returns_user_and_session` | Run a single test method      |

## What is covered (high level)

| Area           | What the tests check                                                                                                                    |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| **Auth**       | `GET /api/auth/config/`, `GET /api/auth/google/login/` → Google → `GET /api/auth/google/callback/`; `POST /api/auth/google/` (mocked verify) |
| **Users**      | `POST /api/users/get-or-create/` when allowed vs forbidden; `GET /api/users/{id}/songs/` Bearer scoping (403 for another user’s id)     |
| **Generation** | `GET/POST /api/generation-config/`; full **Mock** path: create user → song → prompt → `generation-request` → `…/run/` until `COMPLETED` |
| **Models**     | Light sanity (e.g. `User` string)                                                                                                       |

## Frontend

There is no automated UI test in this repo yet; exercise the Vite app manually (see the main [README](../README.md), **Testing Guide → Option 2 — Web UI**) or add something like Vitest/Playwright separately if you need it.
