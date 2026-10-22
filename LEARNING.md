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
