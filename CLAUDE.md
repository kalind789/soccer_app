# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A practice planner for soccer coaches: a reusable drill library, plus session plans that put drills in order. v1 is single-user with no login. The user is learning while Claude builds. Work in batches of small, per-step commits, then walk through the code and ask check questions. New terms go in `learning/`, one file per step (index in `learning/README.md`).

## Stack

- **Backend:** FastAPI + SQLAlchemy 2.0 + Pydantic, in `backend/`. Python >= 3.13, managed with uv. Tests use pytest. No linter.
- **Frontend:** React, in `frontend/` (not created yet).
- **Storage:** SQLite (`backend/planner.db`, gitignored). Set `DATABASE_URL` to change it. Tables are created at startup by `create_all`.

## Backend layout

- `app/database.py`: engine (from `DATABASE_URL`), `Base`, `get_db`, and the `DbSession` type for endpoints.
- `app/models.py`: SQLAlchemy tables plus the domain rules: `Drill`, `SessionPlan`, `SessionDrill` (an ordered link table, repeats allowed). Rules raise custom exceptions and know nothing about HTTP.
- `app/schemas.py`: Pydantic request and response shapes, kept separate from the models.
- `app/routers/`: `drills.py`, `session_plans.py`. They turn model exceptions into HTTP errors (404/422).
- `tests/conftest.py`: the `client` fixture gives each test a fresh in-memory database by overriding `get_db`.

## Domain rules

- Drills are archived, never deleted. Archived drills are hidden from `GET /drills` unless `?include_archived=true`. Editing a drill changes it in every plan that uses it.
- A session plan's `end_time` must be after `start_time`. `duration_minutes` is calculated, never stored.
- `PUT /session-plans/{id}/drills` replaces the ordered list. An archived drill can't be newly added, but one already in the plan can stay.

## Commands (run from `backend/`)

- Run tests: `uv run pytest`. One file: `uv run pytest tests/test_drills.py`. One test: `uv run pytest tests/test_drills.py::test_create_drill`.
- Run the server: `uv run fastapi dev app/main.py`, then open http://127.0.0.1:8000/docs
- Add a dependency: `uv add <package>` (dev: `uv add --dev <package>`)

## Current status

Backend v1 is done (steps 1 to 5), plus drill name search (`GET /drills?search=`), with 34 tests passing. Waiting on the user's walkthrough questions.

Next, in order: Alembic migrations (replacing `create_all`), the React frontend in `frontend/` (with CORS), then Supabase Postgres with auth, teams and email invites.
