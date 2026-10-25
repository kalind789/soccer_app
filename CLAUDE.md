# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A practice planner for soccer coaches: teams, each with session plans that put drills in order and its own drill library, plus a built-in library of drill ideas. Coaches log in with Supabase Auth (email + password). The user is learning while Claude builds. Work in batches of small, per-step commits, then walk through the code and ask check questions. New terms go in `learning/`, one file per step (index in `learning/README.md`).

## Stack

- **Backend:** FastAPI + SQLAlchemy 2.0 + Pydantic, in `backend/`. Python >= 3.13, managed with uv. Tests use pytest. No linter.
- **Frontend:** React 19 + TypeScript + Vite, in `frontend/`. Lint with oxlint (`npm run lint`). No frontend tests yet.
- **Storage:** Supabase Postgres when `backend/.env` sets `DATABASE_URL` (template: `backend/.env.example`; `.env` is gitignored and holds the password). Without it, local SQLite (`backend/planner.db`, gitignored). Driver: psycopg 3; `normalize_url` in `database.py` turns Supabase's `postgresql://` into `postgresql+psycopg://`. Tables are created and changed only by Alembic migrations (`backend/migrations/`), never at startup. Tests still use `create_all` on their in-memory database, for speed.

## Backend layout

- `app/settings.py`: loads `backend/.env` and holds every setting: `DATABASE_URL` (+ `normalize_url`), `FRONTEND_ORIGIN`, `SUPABASE_URL`.
- `app/database.py`: engine, `Base`, `get_db`, and the `DbSession` type for endpoints.
- `app/auth.py`: `get_current_user` verifies the Supabase access token (`Authorization: Bearer`) against the project's public JWKS keys (ES256; asymmetric algorithms only; audience `authenticated`, issuer `<SUPABASE_URL>/auth/v1`). `CurrentUser` is the endpoint shortcut. No secret is needed in the backend.
- `app/models.py`: SQLAlchemy tables plus the domain rules: `Drill`, `Team`, `SessionPlan`, `SessionDrill` (an ordered link table, repeats allowed), and the tag lists `AGE_GROUPS` and `GOALS` (also in `schemas.py` as `Literal`s and in `frontend/src/tags.ts`; keep all three in sync). Rules raise custom exceptions and know nothing about HTTP.
- `app/schemas.py`: Pydantic request and response shapes, kept separate from the models.
- `app/routers/`: `drills.py` (`/drills/{id}` read/edit/archive, plus `/drill-ideas`), `session_plans.py`, `teams.py` (also `/teams/{id}/drills` and `/teams/{id}/drill-suggestions`). They turn model exceptions into HTTP errors (403/404/409/422).
- The drill ideas (24, written from U.S. Soccer's game formats and moments of the game) are data inside the migration `dabd8f706a33_team_drills_tags_and_drill_ideas.py`. To change them, add a new migration.
- `migrations/`: Alembic. `env.py` reads `DATABASE_URL` and `Base.metadata`; one file per change in `versions/`. Every new table must get `ENABLE ROW LEVEL SECURITY` on Postgres (see the RLS migration): otherwise Supabase's public Data API can read and write it.
- `tests/conftest.py`: the `client` fixture gives each test a fresh in-memory database by overriding `get_db`, and fakes the login as `ALICE`; `login_as(BOB)` switches users. `add_idea(name, age_groups, goals)` inserts a drill idea (tests skip migrations, so they have none). `tests/test_auth.py` tests the real token check with a locally generated ES256 key.
- `tests/test_migrations.py`: fails if a model changes without a matching migration.

## Frontend layout

- `src/api.ts`: the only place that calls the backend. Its types mirror the Pydantic schemas in `backend/app/schemas.py`, so keep them in sync by hand. `VITE_API_URL` overrides the API address (default `http://127.0.0.1:8000`).
- `src/App.tsx`: header nav with log out, toast and auth providers, the login gate (`LoggedInOnly`: login page until there's a session), team provider (keyed by user id), and React Router routes: `/teams`, `/teams/:teamId` (Sessions tab), `/teams/:teamId/drills` (Drills tab), `/teams/:teamId/sessions/:planId`, `/ideas` (`/` redirects to `/teams`). Header nav: Teams, Drill ideas (the user chose this).
- `src/pages/`: `TeamsPage` (team cards: open, edit, delete), `TeamPage` (team header + tabs) showing `TeamSessions` (upcoming/past cards with progress) or `TeamDrills` (the team's drills: card grid, search, archive with undo, create/edit in modals), `PlanPage` (hero, edit/delete in modals, drill editor), `IdeasPage` (drill ideas filtered by age group and goal, read-only detail modal).
- `src/components/`: `SlotEditor` (a plan's drills: drag to reorder with dnd-kit, −/+ minute steppers, autosave after 600 ms, flushes pending changes on unmount), `DrillPicker` (click-to-add panel: Used before, Recommended for any age, the team's drills, Drill ideas; search + goal filter), `Timeline` (colored bar of drill minutes vs session length), `Modal` (native `<dialog>`), `Toast`, `DateTile`, `DrillForm`, `PlanForm` and `TeamForm` (create and edit), `TeamProvider` (loads the coach's teams once), `DrillTags` (tag chips), `TagPicker` (toggle chips in `DrillForm`).
- `src/supabase.ts`: the Supabase client, used only for login (needs `VITE_SUPABASE_URL` and `VITE_SUPABASE_PUBLISHABLE_KEY` in the gitignored `frontend/.env.local`). `src/authContext.ts`: `useSession()`; `components/AuthProvider.tsx` follows `onAuthStateChange`. `pages/LoginPage.tsx`: Log in / Sign up tabs, "Continue with Google" (`signInWithOAuth`, needs the Google provider enabled in Supabase), and email + password (sign-up asks for the password twice; email confirmation is on, so it shows "check your email").
- `src/api.ts` sends `Authorization: Bearer <access token>` on every call, and logs out on a 401.
- `src/toast.ts`: `useToast()` hook and context. `src/teamContext.ts`: `useTeams()`. `src/tags.ts`: age group and goal values, labels, `isForAllAges`. `src/colors.ts`: a stable color per drill or team id. `src/format.ts`: display helpers.
- `src/index.css`: all styles, "clean and bright" light theme (the user chose it). Design tokens are CSS variables on `:root`. Font: Plus Jakarta Sans (Google Fonts, loaded in `index.html`).
- The UI labels drill `objective` and plan `focus` as "Goal". The user chose to keep the field names and only relabel them.
- The backend's CORS allows only `FRONTEND_ORIGIN` (default `http://localhost:5173`), so open the app at `localhost`, not `127.0.0.1`.

## Domain rules

- **Drills belong to a team** (`team_id`): only that team's plans can newly add them, and only its coach can see or edit them. A drill with `team_id = NULL` is a **drill idea**: everyone can see it and use it in a plan, nobody can edit it (403). The user chose team libraries plus ideas over one shared library.
- **Tags:** `age_groups` (U.S. Soccer formats: `u6-u8` 4v4, `u9-u10` 7v7, `u11-u12` 9v9, `u13+` 11v11) and `goals` (`warm-up`, `possession`, `attacking`, `finishing`, `defending`, `transition`), stored as JSON lists. Filtering happens in the browser.
- **Suggestions** (`/teams/{id}/drill-suggestions`): `used_before` = drills in the team's plans, most used first (top 10); `recommended` = ideas tagged for every age group that the team hasn't used.
- A team is just a name ("U12 Eagles 2027") with an `owner_id` (the Supabase user id). No seasons and no links between teams: a new year is simply a new, unrelated team (the user chose this; keep teams simple). A team with plans can't be deleted (409); deleting a team deletes its drills.
- A session plan belongs to a team (`team_id`, required) and is owned through it.
- Every endpoint except `/health` and `/version` needs a login (401 otherwise). Someone else's team or plan is a 404, never a 403.
- Drills are archived, never deleted (except with their team). Archived drills are hidden from `GET /teams/{id}/drills` unless `?include_archived=true`. Editing a drill changes it in every plan that uses it.
- A session plan's `end_time` must be after `start_time`. `duration_minutes` is calculated, never stored.
- `PUT /session-plans/{id}/drills` replaces the ordered list with `{drill_id, minutes}` entries. An archived drill or another team's drill can't be newly added, but one already in the plan can stay.
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

Backend: v1 plus drill search, Alembic, CORS, per-slot minutes, logins and teams, team drill libraries, tags and drill ideas, with 86 tests passing. Runs on Supabase Postgres (free tier, us-east-1) through the **session pooler** (`aws-0-us-east-1.pooler.supabase.com:5432`). The direct `db.<ref>.supabase.co` host is IPv6-only and unreachable from the user's network. Frontend: teams (with Sessions and Drills tabs), session plans, drill ideas, login. No frontend tests yet.

The user often runs their own dev servers on 8000 and 5173 against the real `planner.db`. Verify on other ports with a scratch `DATABASE_URL`.

Ticket 002 is in progress: steps 1 to 4 are done (Supabase Postgres, owners, backend login check, frontend login). Left: the user tries a real sign-up, optional Google login, then hosting (step 5). Planned work is in `tickets/` (index in `tickets/README.md`): 001 drill diagram editor, 002 users and auth (Supabase), 003 shared teams and invites (teams themselves exist; 003 adds more coaches per team), 004 practice schedules and calendar. 