# ⚽ Practice Planner

[![CI](https://github.com/kalind789/soccer_app/actions/workflows/ci.yml/badge.svg)](https://github.com/kalind789/soccer_app/actions/workflows/ci.yml)

A full-stack web app for youth soccer coaching staffs. Coaches plan **practice sessions** for each team, drill by drill. Each team keeps its own **drill library**, and a built-in set of **drill ideas** is organized by U.S. Soccer age group and practice goal.

**Stack:** Python · FastAPI · SQLAlchemy 2.0 · Pydantic · Alembic · PostgreSQL (Supabase) · Supabase Auth (JWT) · React 19 · TypeScript · Vite · pytest · GitHub Actions

## Features

- **Teams and coaching staff:** a coach can run several teams, and a team can have several coaches. The head coach invites assistants with a shareable link that expires after 7 days and can be replaced or turned off.
- **Session plans:** date, time, location, goal and notes. Drag drills into order, with time set per session: the same drill can run 15 minutes on Monday and 20 on Thursday. The plan warns when the drill times add up to more than the session.
- **Drill library per team**, tagged by age group (U6–U8 through U13+) and goal (possession, attacking, defending, transition, and more).
- **Drill ideas:** 24 starter drills built on U.S. Soccer's game formats and moments of the game, filterable by age and goal.
- **Suggestions while planning:** the drills a team uses most, plus recommended ideas for the team's age group.
- **Accounts:** email + password or Google sign-in through Supabase Auth.

## Design decisions

- **Authorization in one place.** Every request carries a Supabase access token. The backend checks its signature against Supabase's published public keys (ES256 only, so a forged HS256 token fails), so the backend holds no secret. Who can touch a team is decided in one function, `get_team_or_404`, which checks the team's staff list. Someone else's team returns 404, not 403, so ids don't reveal what exists.
- **Time lives on the link, not the drill.** `SessionDrill` is an ordered link table (plan ↔ drill) with its own `minutes` and `position`. Drills stay reusable, and the same drill can appear twice in one plan.
- **One table, two kinds of drill.** A drill with a `team_id` belongs to that team. A drill with none is a read-only drill idea that every team can use. Plans point at either one the same way.
- **Domain rules live in the models; HTTP lives in the routers.** Models raise custom exceptions (`ArchivedDrillError`, `InvalidInviteError`, `LastHeadCoachError`, ...) and know nothing about HTTP. Routers turn them into 403/404/409/422 responses.
- **Schema changes are migrations.** Alembic is the only thing that creates or changes tables, including data migrations (one team owner → a staff of coaches). Every migration was tested both ways, on SQLite and Postgres, with data already in it. Row level security is on for every table, so Supabase's public API can't reach the data.
- **One typed API client.** Every frontend call goes through `src/api.ts`, whose TypeScript types mirror the Pydantic schemas.

## Testing

- **102 backend tests** (pytest). Each test gets a fresh in-memory database and a fake login through dependency injection, so no test touches real data or needs secrets.
- **Security cases are tested:** forged and expired tokens, the wrong algorithm, another coach's data, expired or revoked invite links, and coaches trying head-coach actions.
- **A guard test** builds a database from the migrations and fails if it doesn't match the models, which catches a forgotten migration.
- **CI** (GitHub Actions) runs the tests, the frontend lint and the TypeScript build on every push and pull request.

## Run it locally

You need a free [Supabase](https://supabase.com) project for the database and logins.

```bash
# Backend: http://127.0.0.1:8000/docs
cd backend
cp .env.example .env          # then fill in DATABASE_URL and SUPABASE_URL
uv run alembic upgrade head
uv run fastapi dev app/main.py

# Frontend: http://localhost:5173
cd frontend
# create .env.local with VITE_SUPABASE_URL and VITE_SUPABASE_PUBLISHABLE_KEY
npm install
npm run dev
```

Tests (no Supabase needed): `cd backend && uv run pytest`

## Roadmap

See [`tickets/`](tickets/README.md): deployment, drag-and-drop drill diagrams, and practice schedules with a calendar.

## Project layout

```
backend/   FastAPI app (models, schemas, routers, auth), Alembic migrations, pytest suite
frontend/  React + TypeScript pages, components, and typed API client
tickets/   Planned work, one ticket per feature
learning/  My notes on the concepts behind each step
```
