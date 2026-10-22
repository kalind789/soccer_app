# Learning notes

Terms from each step. Add your own notes under each one, in your own words.

## Step 1: Skeleton

- **Dependency:** a package the code needs. Listed in `backend/pyproject.toml`.
- **Dev dependency:** only needed while developing (pytest), not by the running app. Listed under `[dependency-groups] dev`.
- **Lockfile (`uv.lock`):** the exact version of every installed package. `pyproject.toml` gives the allowed range, and `uv.lock` pins the exact choice. Commit it.
- **Virtual environment (`.venv`):** a private folder of installed packages for this project only. uv creates and uses it for you. Never commit it.
- **Endpoint / route:** HTTP method + path (`GET /health`) connected to a Python function.
- **Health check:** an endpoint that only answers "I'm alive". Used by hosting services to see if the app is up.
- **TestClient:** sends fake HTTP requests to the app inside the test, with no real server needed.

My notes:

## Step 2: Database plumbing

- **SQLAlchemy:** a Python library for talking to SQL databases. The same code works on SQLite and Postgres.
- **Engine:** knows *how* and *where* to connect. Made once, when the app starts.
- **Database session:** one short conversation with the database: open, read/write, close. One per request.
- **Dependency injection:** a function *asks for* what it needs (`Depends(get_db)`) instead of making it itself. FastAPI provides it, and tests can swap in a different one.
- **Dependency override:** in tests, `app.dependency_overrides[get_db] = ...` swaps the real database for a throwaway one.
- **Fixture:** a pytest function that sets something up for a test (`client`). A test asks for it by naming it as a parameter.
- **Environment variable:** a setting from outside the code. `DATABASE_URL` decides which database to use.
- **`yield` / `try` / `finally`:** hand something over, wait until the caller is done, then always clean up, even if there was an error.

My notes:

## Steps 3 to 5: Drills, session plans, drills in sessions

- **Model (`app/models.py`):** a Python class that *is* a database table. One object = one row. Holds the rules (`archive()`, `check_times()`, `set_drills()`).
- **Schema (`app/schemas.py`):** a Pydantic class describing what the API *accepts* or *returns*. It validates incoming JSON before your code runs.
- **Why both?** The table and the API are different things that change for different reasons. For example, `archived` is returned but never accepted on create, and `duration_minutes` is returned but never stored.
- **Router:** a group of related endpoints (`/drills/...`), plugged into the app with `include_router`.
- **CRUD:** Create, Read, Update, Delete. These are the four basic operations, which map to POST, GET, PATCH, DELETE.
- **PATCH vs PUT:** PATCH changes only the fields you send. PUT replaces the whole thing (our drill list).
- **Status codes we use:** 200 OK, 201 Created, 204 No Content (deleted), 404 Not Found, 405 Method Not Allowed, 422 Unprocessable (bad data or a broken rule).
- **Primary key:** the column that uniquely identifies a row (`id`).
- **Foreign key:** a column that points at another table's primary key (`session_drills.drill_id` → `drills.id`).
- **Link table / many-to-many:** a plan has many drills and a drill is in many plans. `session_drills` sits in between, with an extra `position` column.
- **Relationship:** SQLAlchemy's way of letting you write `plan.slots` or `slot.drill` instead of writing the SQL join yourself.
- **Cascade:** "when the parent is deleted, delete these too". Deleting a plan deletes its slots, but not the drills.
- **Commit / rollback:** commit saves the changes in a database session for good. Rollback throws them away.
- **Custom exception:** `ArchivedDrillError`. The model raises it, and the router turns it into an HTTP 422. The model knows nothing about HTTP.

My notes:
