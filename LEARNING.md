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
