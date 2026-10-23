# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A practice planner for soccer coaches: a reusable drill library, plus session plans that put drills in order. v1 is single-user with no login. The user is learning while Claude builds. Work in batches of small, per-step commits, then walk through the code and ask check questions. New terms go in `learning/`, one file per step (index in `learning/README.md`).

## Stack

- **Backend:** FastAPI + SQLAlchemy 2.0 + Pydantic, in `backend/`. Python >= 3.13, managed with uv. Tests use pytest. No linter.
- **Frontend:** React 19 + TypeScript + Vite, in `frontend/`. Lint with oxlint (`npm run lint`). No frontend tests yet.
- **Storage:** SQLite (`backend/planner.db`, gitignored). Set `DATABASE_URL` to change it. Tables are created and changed only by Alembic migrations (`backend/migrations/`), never at startup. Tests still use `create_all` on their in-memory database, for speed.

## Backend layout

- `app/database.py`: engine (from `DATABASE_URL`), `Base`, `get_db`, and the `DbSession` type for endpoints.
- `app/models.py`: SQLAlchemy tables plus the domain rules: `Drill`, `SessionPlan`, `SessionDrill` (an ordered link table, repeats allowed). Rules raise custom exceptions and know nothing about HTTP.
- `app/schemas.py`: Pydantic request and response shapes, kept separate from the models.
- `app/routers/`: `drills.py`, `session_plans.py`. They turn model exceptions into HTTP errors (404/422).
- `migrations/`: Alembic. `env.py` reads `DATABASE_URL` and `Base.metadata`; one file per change in `versions/`.
- `tests/conftest.py`: the `client` fixture gives each test a fresh in-memory database by overriding `get_db`.
- `tests/test_migrations.py`: fails if a model changes without a matching migration.

## Frontend layout

- `src/api.ts`: the only place that calls the backend. Its types mirror the Pydantic schemas in `backend/app/schemas.py`, so keep them in sync by hand. `VITE_API_URL` overrides the API address (default `http://127.0.0.1:8000`).
- `src/App.tsx`: header nav and React Router routes: `/plans`, `/plans/:planId`, `/drills` (`/` redirects to `/plans`).
- `src/pages/`: one file per route. `PlansPage` (list + create), `PlanPage` (details, edit, delete, drills), `DrillsPage` (search, archive, create, edit).
- `src/components/`: `DrillForm` and `PlanForm` (each used for both create and edit), `SlotEditor` (a plan's drills: minutes, reorder, remove, add, or create a new library drill inline; edits a draft until Save).
- `src/format.ts`: date, time and minutes display helpers.
- `src/index.css`: all styles; colors are CSS variables on `:root`, redefined for dark mode.
- The UI labels drill `objective` and plan `focus` as "Goal". The user chose to keep the field names and only relabel them.
- The backend's CORS allows only `FRONTEND_ORIGIN` (default `http://localhost:5173`), so open the app at `localhost`, not `127.0.0.1`.

## Domain rules

- Drills are archived, never deleted. Archived drills are hidden from `GET /drills` unless `?include_archived=true`. Editing a drill changes it in every plan that uses it.
- A session plan's `end_time` must be after `start_time`. `duration_minutes` is calculated, never stored.
- `PUT /session-plans/{id}/drills` replaces the ordered list with `{drill_id, minutes}` entries. An archived drill can't be newly added, but one already in the plan can stay.
- Minutes belong to the slot (`SessionDrill.minutes`), never to the drill: the same drill can run 15 min in one plan and 20 in another. Minutes must be > 0, with no upper limit. `planned_minutes` (sum of slots) may differ from `duration_minutes`; the UI warns when over but never blocks.

## Commands

Frontend (from `frontend/`): `npm run dev`, then open http://localhost:5173 (the backend must be running too). `npm run build` type-checks and builds.

Backend (from `backend/`):

- Run tests: `uv run pytest`. One file: `uv run pytest tests/test_drills.py`. One test: `uv run pytest tests/test_drills.py::test_create_drill`.
- Run the server: `uv run fastapi dev app/main.py`, then open http://127.0.0.1:8000/docs
- Add a dependency: `uv add <package>` (dev: `uv add --dev <package>`)
- Apply migrations: `uv run alembic upgrade head`. Do this before the first server run and after pulling new migrations.
- After changing a model: `uv run alembic revision --autogenerate -m "<what changed>"`, read the generated file, then `upgrade head`.

## Current status

Backend: v1 plus drill search, Alembic, CORS and per-slot minutes, with 42 tests passing. Frontend: session plans and drill library pages, with editing. No frontend tests yet.

The user often runs their own dev servers on 8000 and 5173 against the real `planner.db`. Verify on other ports with a scratch `DATABASE_URL`.

Planned work is in `tickets/` (index in `tickets/README.md`): 001 drill diagram editor, 002 users and auth (Supabase), 003 teams and invites, 004 practice schedules and calendar. Current work: a UI redesign in a "clean and bright" style (light, soft shadows, rounded cards, colorful accents).
