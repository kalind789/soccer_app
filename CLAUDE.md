# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Roster: a learning project

The mentoring behavior (hint levels, review format, tone) lives in the output style at `.claude/output-styles/mentor.md`, enabled by `"outputStyle": "Mentor"` in `.claude/settings.json`. The rules below are the short version that always applies.

## Who I am and why this exists

I'm learning software engineering fundamentals so I can eventually build a full TeamSnap-style soccer app (roster, practices, RSVPs, team chat) on my own, with no guidance. This repo is a series of small, instructional projects. **I write the code myself.** Claude's job is to teach, guide, and review, not to implement.

## Teaching rules (always apply)

- Do not write implementation code in `src/` or `tests/` for me. Explain concepts, ask guiding questions, and give hints.
- Claude may edit `CLAUDE.md` (keep "Current status" accurate after each step) and files under `.claude/`. Everything else, including `pyproject.toml`, I edit myself after Claude shows and explains the snippet.
- Do not use em dashes.
- When I ask for a review, say what's good, then list issues in priority order with hints, not finished fixes.
- Always explain *why* a practice matters, and connect it to the bigger soccer app when relevant.
- If I explicitly say "show me the code", you may show it, then ask me to explain it back.
- Keep me in the habit of: small commits, running tests, running ruff.

## Roadmap

1. **Command-line roster manager (pure Python).** Add, remove, list players, saved to JSON. Skills: functions, classes, file I/O, first pytest tests, uv, ruff. **(current)**
2. **Same roster with a database.** Swap JSON for SQLite via SQLAlchemy. Add an Alembic migration (jersey number column). Skills: data modeling, migrations.
3. **Roster API with FastAPI.** Endpoints, Pydantic schemas, status codes, testing via `/docs`.
4. **Deploy it.** Render or Railway, GitHub Actions running tests first. Switch to Postgres and Docker around here.
5. **Small React frontend.** List and add players from the deployed API. React basics, fetch, CORS.
6. **Login.** Register/login, hashed passwords, protected endpoints.
7. **Practice scheduler with RSVPs.** Events and attendance, table relationships, permission rules.
8. **Simple chat room.** Standalone FastAPI WebSocket demo, then fold into the app.

## Design decisions for project 1

- **Scope:** model `Player` and `Team` only. No `Event` until project 7.
- **Layers, one job each:**
  - `src/soccer_app/models.py`: what things are and the rules. Imports nothing from the other files.
  - `src/soccer_app/storage.py`: save/load a Team to JSON. No rules. This is the only file rewritten in project 2.
  - `src/soccer_app/cli.py`: parse commands with argparse, call models and storage, print results, turn errors into friendly messages.
  - Dependency direction: cli -> storage -> models. Never the reverse.
- **Player** is a `@dataclass` with an `id: int`. Players are identified by id, not name.
- **Team** contains a list of players (composition, not inheriting from list). Rules live in Team: no duplicate ids, removing a missing id raises a clear error.
- **Models return data, they don't print.** Printing is the CLI's job.
- **No jersey number yet.** It gets added in project 2 as the first migration.
- **Tests:** `tests/test_models.py` and `tests/test_storage.py`. Use pytest's `tmp_path` for storage tests. CLI stays thin and is not tested at first.

## Tooling

- Created with `uv init --package` (src layout, git repo, entry point). Package is `soccer_app`; the console script `soccer-app` points at `soccer_app:main` in `src/soccer_app/__init__.py` (still the uv placeholder until step 6).
- Python >= 3.13 (pinned in `.python-version`). Dev tools: `uv add --dev pytest ruff`.
- Run tests: `uv run pytest`. Single file: `uv run pytest tests/test_models.py`. Single test: `uv run pytest tests/test_models.py::test_name`.
- Lint and format: `uv run ruff check` and `uv run ruff format`
- Run the app: `uv run soccer-app <command>`
- Commit `uv.lock` and `.python-version`. Never commit `.venv/`.

## Step plan for project 1

1. Set up project with uv, first commit. **(done)**
2. Write `models.py`. **(in progress)**
3. Write `tests/test_models.py`, run pytest, commit.
4. Write `storage.py` (dataclass <-> dict <-> JSON).
5. Write `tests/test_storage.py`, commit.
6. Write `cli.py` with argparse (`add`, `remove`, `list`), point the `soccer-app` script in `pyproject.toml` at it.
7. Run ruff, fix issues, commit.

## Current status

Third draft of `models.py` (uncommitted). `Team.players` is now a `dict[int, Player]` keyed by id. `Player` has `id`, `name`, `position`.

Done: duplicate ids rejected, `remove_player(player_id: int)`, `list_players` returns a new list (no outside mutation).

Still open:
1. The `__main__` demo calls `remove_player(player1)` with a `Player`, which crashes with `TypeError: unhashable type: 'Player'`. Type hints aren't enforced at runtime.
2. Errors are built-in `ValueError`/`KeyError` with generic messages. Consider a custom exception (so the CLI can catch "roster rule" errors specifically) and include the id in the message.
3. Move the `__main__` manual checks into `tests/test_models.py` (step 3).
4. Ruff: import sorting and blank lines; run `uv run ruff check --fix` and `uv run ruff format`.
5. Decided: `position` is optional. Learner is making that change.

Learner has never written tests before; step 3 is their first pytest experience.

Update (step 3 in progress): `position` is now optional and `PlayerDoesNotExistException` was added. `tests/test_models.py` has 4 tests, but 3 lack the `test_` prefix so pytest only runs 1. `models.py` regressed: the `if ... raise` checks were replaced with `try/except` blocks that never trigger (dict assignment overwrites silently, `pop` raises `KeyError`). Learner confused raising (models) with catching (cli); `raise` vs `try/except` needs reinforcing.

Update: `models.py` fixed (raises `PlayerAlreadyExistsException` / `PlayerDoesNotExistsException`). Claude showed the remaining tests on request ("show me the code" rule); learner pasting them. Explain-back: solid on test design; shaky on references vs copies (aliasing) and thought dicts have no `len`. Revisit aliasing in storage.py work.

Step 3 essentially done (7 tests once `new_team_has_no_players` gets its `test_` prefix). Next: step 4, `storage.py`. Learner says aliasing now makes sense.

JSON format decided: `{"name": "Falcons", "players": [{"id": 1, "name": "Sam", "position": "MF"}, {"id": 2, "name": "Na", "position": null}]}`. Players are an array of objects with named fields (matches `dataclasses.asdict`); missing position is written as `null`. Learner is writing `save` next.

Update (step 4 in progress): models + tests committed (3125aec). First `save_team` draft exists, but learner moved `asdict` into `Team.add_player` (Team now stores dicts, `list_players` returns dicts) and edited `test_models.py` asserts to match. Pushed back: serialization belongs in storage.py, and tests shouldn't be changed to fit code. Still open in storage: hard-coded `storage_data.json` path (test writes a real file in repo root), `test_save_team` has no assert, `indent=True`, ruff errors.

Update: fixed. `asdict` moved into `save_team` (list comprehension), path parameter added, model tests restored. Remaining: test passes `tmp_path` (the folder) instead of `path`, causing `IsADirectoryError`; test builds its expected value with the same `asdict` comprehension (mirrors the implementation, so write it by hand); unused `asdict` import and `__main__` block back in `models.py`; ruff errors. Then `load_team`.

Open design questions:
- What fields should a player have besides id and name?
- Can one player belong to more than one team? (Affects project 2's database design.)
