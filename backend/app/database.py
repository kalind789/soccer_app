import os
from collections.abc import Iterator
from typing import Annotated

from dotenv import load_dotenv
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

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

# SQLite only: FastAPI may use a connection from a different thread than the one that opened it.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# pool_pre_ping: check a connection still works before using it. Hosted databases close idle connections.
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    """Parent class for every table model."""


def get_db() -> Iterator[Session]:
    """Give one database session to a request, and always close it afterward."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Shortcut for endpoint parameters: `db: DbSession` instead of the full Annotated form.
DbSession = Annotated[Session, Depends(get_db)]
