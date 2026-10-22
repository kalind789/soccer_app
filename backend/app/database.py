import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Read from the environment so the same code can point at Supabase later.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./planner.db")

# SQLite only: FastAPI may use a connection from a different thread than the one that opened it.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
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
