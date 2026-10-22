# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A new app built from scratch (started 2026-10-21). What the app does is not decided yet. Claude writes the code.

## Stack

- **Backend:** FastAPI, in `backend/`. Python >= 3.13, managed with uv.
- **Frontend:** React, in `frontend/` (not created yet).
- **Storage:** a local SQLite file for now. The plan is to move to Postgres on Supabase later, so the code should keep database access in one place that's easy to swap.

The backend and frontend are separate projects with their own dependencies. They only talk to each other over HTTP.

## Commands

Run backend commands from `backend/`:

- Add a dependency: `uv add <package>`
- Run Python: `uv run <command>`

## Current status

The backend is a bare `uv init` and nothing else. There's no ruff, no pytest and no app code yet.
