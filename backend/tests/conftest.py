from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.auth import User, get_current_user
from app.database import Base, get_db
from app.main import app
from app.models import Drill

# Two pretend coaches. Tests run as Alice unless they switch with `login_as(BOB)`.
ALICE = User(id=UUID(int=1), email="alice@example.com")
BOB = User(id=UUID(int=2), email="bob@example.com")


@pytest.fixture
def current_user():
    """Who the fake login says is making requests. A dict, so `login_as` can change it mid-test."""
    return {"user": ALICE}


@pytest.fixture
def login_as(current_user):
    def switch(user: User) -> None:
        current_user["user"] = user

    return switch


@pytest.fixture
def TestingSession():
    # A fresh in-memory database for every test. StaticPool keeps it on one
    # connection so it doesn't vanish between requests.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


@pytest.fixture
def add_idea(TestingSession):
    """Drill ideas come from a migration, and tests skip migrations, so tests add their own."""

    def add(name: str, age_groups: list[str] = [], goals: list[str] = []) -> int:
        with TestingSession() as db:
            idea = Drill(name=name, age_groups=age_groups, goals=goals)
            db.add(idea)
            db.commit()
            return idea.id

    return add


@pytest.fixture
def client(current_user, TestingSession):
    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    # Skip real token checking (tests/test_auth.py covers that) and just say who's logged in.
    app.dependency_overrides[get_current_user] = lambda: current_user["user"]
    yield TestClient(app)
    app.dependency_overrides.clear()
