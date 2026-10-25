# ⚽ Practice Planner

[![CI](https://github.com/kalind789/soccer_app/actions/workflows/ci.yml/badge.svg)](https://github.com/kalind789/soccer_app/actions/workflows/ci.yml)

A full-stack web app for soccer coaches. Build a reusable **drill library** and plan **practice sessions**: drills put in order, each with its own time for that session.

**Stack:** Python · FastAPI · SQLAlchemy 2.0 · Pydantic · Alembic · SQLite · React 19 · TypeScript · Vite · pytest

## Features

- **Drill library:** create, edit, search by name, and archive drills. Editing a drill updates it in every plan that uses it.
- **Session plans:** date, start/end time, location, goal and notes, with the length calculated from the times.
- **Per-session drill timing:** the same drill can run 15 minutes on Monday and 20 on Thursday. The plan shows planned time against session length and warns when it goes over.
- **Plan as you go:** create a new drill from inside a session plan, and it's saved to the library for reuse.

## Design decisions

- **Time lives on the link, not the drill.** `SessionDrill` is an ordered link table (plan ↔ drill) with its own `minutes` and `position`. That keeps drills reusable, with no fixed length, and allows the same drill to appear twice in one plan.
- **Domain rules live in the models; HTTP lives in the routers.** Models raise custom exceptions (`ArchivedDrillError`, `InvalidSessionTimesError`) and know nothing about HTTP. Routers turn them into 404/422 responses.
- **Separate database models and API schemas.** SQLAlchemy models describe the tables; Pydantic schemas describe what the API accepts and returns. For example, `duration_minutes` is returned but never stored.
- **Archive, don't delete.** Old plans keep pointing at real drills. An archived drill can stay in a plan but can't be newly added.
- **Schema changes are migrations.** Alembic is the only thing that creates or changes tables. Migrations were tested on databases that already had data in them.
- **One typed API client.** Every frontend call goes through `src/api.ts`, whose TypeScript types mirror the Pydantic schemas.

## Testing

- **42 backend tests** (pytest). Each test gets a fresh in-memory database through dependency injection, so no test touches real data.
- **A guard test** builds a database from the migrations and fails if it doesn't match the models, which catches a forgotten migration.
- **CORS tests** check that only the frontend's address is allowed to call the API.

## Run it locally

```bash
# Backend: http://127.0.0.1:8000/docs
cd backend
uv run alembic upgrade head
uv run fastapi dev app/main.py

# Frontend: http://localhost:5173
cd frontend
npm install
npm run dev
```

Tests: `cd backend && uv run pytest`

## Roadmap

See [`tickets/`](tickets/README.md): drag-and-drop drill diagrams, users and authorization, team invites, and practice schedules with a calendar.

## Project layout

```
backend/   FastAPI app (models, schemas, routers), Alembic migrations, pytest suite
frontend/  React + TypeScript pages, components, and typed API client
learning/  My notes on the concepts behind each step
```
