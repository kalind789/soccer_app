# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A practice planner for soccer coaches: a reusable drill library, plus session plans that put drills in order. v1 is single-user with no login. The user is learning while Claude builds. Work in batches of small, per-step commits, then walk through the code and ask check questions. New terms go in `learning/`, one file per step (index in `learning/README.md`).

## Stack

- **Backend:** FastAPI + SQLAlchemy 2.0 + Pydantic, in `backend/`. Python >= 3.13, managed with uv. Tests use pytest. No linter.
- **Frontend:** React 19 + TypeScript + Vite, in `frontend/`. Lint with oxlint (`npm run lint`). No frontend tests yet.
- **Storage:** Supabase Postgres when `backend/.env` sets `DATABASE_URL` (template: `backend/.env.example`; `.env` is gitignored and holds the password). Without it, local SQLite (`backend/planner.db`, gitignored). Driver: psycopg 3; `normalize_url` in `database.py` turns Supabase's `postgresql://` into `postgresql+psycopg://`. Tables are created and changed only by Alembic migrations (`backend/migrations/`), never at startup. Tests still use `create_all` on their in-memory database, for speed.

## Backend layout

- `app/settings.py`: loads `backend/.env` and holds every setting: `DATABASE_URL` (+ `normalize_url`), `FRONTEND_ORIGIN`, `SUPABASE_URL`.
- `app/database.py`: engine, `Base`, `get_db`, and the `DbSession` type for endpoints.
- `app/auth.py`: `get_current_user` verifies the Supabase access token (`Authorization: Bearer`) against the project's public JWKS keys (ES256; asymmetric algorithms only; audience `authenticated`, issuer `<SUPABASE_URL>/auth/v1`). `CurrentUser` is the endpoint shortcut. No secret is needed in the backend.
- `app/models.py`: SQLAlchemy tables plus the domain rules: `Drill`, `Team`, `SessionPlan`, `SessionDrill` (an ordered link table, repeats allowed). Rules raise custom exceptions and know nothing about HTTP.
- `app/schemas.py`: Pydantic request and response shapes, kept separate from the models.
- `app/routers/`: `drills.py`, `session_plans.py`, `teams.py`. They turn model exceptions into HTTP errors (404/422).
- `migrations/`: Alembic. `env.py` reads `DATABASE_URL` and `Base.metadata`; one file per change in `versions/`. Every new table must get `ENABLE ROW LEVEL SECURITY` on Postgres (see the RLS migration): otherwise Supabase's public Data API can read and write it.
- `tests/conftest.py`: the `client` fixture gives each test a fresh in-memory database by overriding `get_db`, and fakes the login as `ALICE`; `login_as(BOB)` switches users. `tests/test_auth.py` tests the real token check with a locally generated ES256 key.
- `tests/test_migrations.py`: fails if a model changes without a matching migration.

## Frontend layout

- `src/api.ts`: the only place that calls the backend. Its types mirror the Pydantic schemas in `backend/app/schemas.py`, so keep them in sync by hand. `VITE_API_URL` overrides the API address (default `http://127.0.0.1:8000`).
- `src/App.tsx`: header nav, toast provider, team provider, and React Router routes: `/plans`, `/plans/:planId`, `/drills`, `/teams` (`/` redirects to `/plans`).
- `src/pages/`: one file per route. `PlansPage` (upcoming/past cards with progress), `PlanPage` (hero, edit/delete in modals, drill editor), `DrillsPage` (card grid, search, archive with undo, create/edit in modals), `TeamsPage` (grouped by season, edit, start next season, delete).
- `src/components/`: `SlotEditor` (a plan's drills: drag to reorder with dnd-kit, −/+ minute steppers, autosave after 600 ms, flushes pending changes on unmount), `DrillPicker` (searchable click-to-add panel), `Timeline` (colored bar of drill minutes vs session length), `Modal` (native `<dialog>`), `Toast`, `DateTile`, `DrillForm`, `PlanForm` and `TeamForm` (create and edit), `TeamProvider` + `TeamSwitcher` (the header's team picker; the selected team is remembered in localStorage).
- `src/toast.ts`: `useToast()` hook and context. `src/teamContext.ts`: `useTeams()`. `src/colors.ts`: a stable color per drill or team id. `src/format.ts`: display helpers.
- `src/index.css`: all styles, "clean and bright" light theme (the user chose it). Design tokens are CSS variables on `:root`. Font: Plus Jakarta Sans (Google Fonts, loaded in `index.html`).
- The UI labels drill `objective` and plan `focus` as "Goal". The user chose to keep the field names and only relabel them.
- The backend's CORS allows only `FRONTEND_ORIGIN` (default `http://localhost:5173`), so open the app at `localhost`, not `127.0.0.1`.

## Domain rules

- Drills and teams have an `owner_id` (the Supabase user id). A session plan belongs to a team (`team_id`, required) and is owned through it. The drill library is per coach, shared across their teams.
- A team is one season ("U12 Eagles", "2026"). Next season is a new team with `previous_team_id` pointing back, so old plans stay with the old season. A team with plans can't be deleted (409).
- Every endpoint except `/health` and `/version` needs a login (401 otherwise) and only touches the user's own rows. Someone else's id is a 404, never a 403. Pre-login rows were given the all-zeros owner, so nobody sees them.
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

Backend: v1 plus drill search, Alembic, CORS, per-slot minutes, logins and teams, with 77 tests passing. Runs on Supabase Postgres (free tier, us-east-1) through the **session pooler** (`aws-0-us-east-1.pooler.supabase.com:5432`). The direct `db.<ref>.supabase.co` host is IPv6-only and unreachable from the user's network. Frontend: session plans, drill library and teams pages, with editing. No frontend tests yet.

The user often runs their own dev servers on 8000 and 5173 against the real `planner.db`. Verify on other ports with a scratch `DATABASE_URL`.

Ticket 002 is in progress: steps 1 to 3 are done (Supabase Postgres, owners, backend login check). The frontend has no login yet, so it gets 401s until step 4 is done. Planned work is in `tickets/` (index in `tickets/README.md`): 001 drill diagram editor, 002 users and auth (Supabase), 003 shared teams and invites (teams themselves exist; 003 adds more coaches per team), 004 practice schedules and calendar. 