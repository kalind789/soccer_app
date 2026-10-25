from collections.abc import Iterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.settings import DATABASE_URL

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
