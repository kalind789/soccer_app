"""Every setting the app reads from the environment, in one place."""

import os

from dotenv import load_dotenv

# Copy settings from backend/.env (if it exists) into the environment. The file is gitignored,
# because it holds the database password. A variable already set in the shell wins over the file.
load_dotenv()


def normalize_url(url: str) -> str:
    """Supabase gives "postgresql://..."; SQLAlchemy needs to be told to use the psycopg driver."""
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url.removeprefix(prefix)
    return url


# Without a .env file, everything stays on the local SQLite file, so the app works offline.
DATABASE_URL = normalize_url(os.environ.get("DATABASE_URL", "sqlite:///./planner.db"))

# The address the React app runs at. Browsers block it from calling this API unless it's allowed.
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "http://localhost:5173")

# Your Supabase project, e.g. https://abcd1234.supabase.co. Used to check login tokens.
SUPABASE_URL = os.environ.get("SUPABASE_URL", "").rstrip("/")
