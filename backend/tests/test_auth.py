"""Authentication: the real login-token check, with tokens we sign ourselves.

Supabase signs real tokens with its private key. Here we make our own key pair and point the
app at our public key, so we can create good tokens and every kind of bad one.
"""

import time
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec

from app import auth, settings
from app.auth import get_current_user
from app.main import app

PROJECT = "https://test-project.supabase.co"
OUR_KEY = ec.generate_private_key(ec.SECP256R1())  # The same kind of key Supabase uses (ES256).
OTHER_KEY = ec.generate_private_key(ec.SECP256R1())
USER_ID = uuid.uuid4()


@pytest.fixture
def real_auth(client, monkeypatch):
    """Use the real get_current_user, trusting our test key instead of downloading Supabase's."""
    del app.dependency_overrides[get_current_user]
    monkeypatch.setattr(settings, "SUPABASE_URL", PROJECT)
    monkeypatch.setattr(auth, "signing_key", lambda token: OUR_KEY.public_key())
    return client


def make_token(key=OUR_KEY, algorithm="ES256", **changes) -> str:
    claims = {
        "sub": str(USER_ID),
        "email": "coach@example.com",
        "aud": "authenticated",
        "iss": f"{PROJECT}/auth/v1",
        "exp": int(time.time()) + 3600,
    }
    claims.update(changes)
    claims = {name: value for name, value in claims.items() if value is not None}  # None = leave it out.
    return jwt.encode(claims, key, algorithm=algorithm)


def get_drills(client, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return client.get("/drills", headers=headers)


def test_valid_token_lets_you_in(real_auth):
    response = get_drills(real_auth, make_token())

    assert response.status_code == 200


def test_new_teams_belong_to_the_logged_in_user(real_auth):
    headers = {"Authorization": f"Bearer {make_token()}"}
    team = real_auth.post("/teams", json={"name": "U12 Eagles"}, headers=headers).json()

    other_user = {"Authorization": f"Bearer {make_token(sub=str(uuid.uuid4()))}"}
    assert real_auth.get(f"/teams/{team['id']}", headers=headers).status_code == 200
    assert real_auth.get(f"/teams/{team['id']}", headers=other_user).status_code == 404


def test_no_token_is_401(real_auth):
    response = get_drills(real_auth)

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "token",
    [
        pytest.param("not-a-token", id="garbage"),
        pytest.param(make_token(exp=int(time.time()) - 60), id="expired"),
        pytest.param(make_token(key=OTHER_KEY), id="signed by someone else"),
        pytest.param(make_token(aud="anon"), id="wrong audience"),
        pytest.param(make_token(iss="https://other-project.supabase.co/auth/v1"), id="other project"),
        pytest.param(make_token(exp=None), id="no expiry"),
        pytest.param(make_token(sub=None), id="no user id"),
        pytest.param(make_token(sub="not-a-uuid"), id="bad user id"),
        # Classic attack: sign with a shared secret and hope the server accepts any algorithm.
        pytest.param(make_token(key="guessed-secret-guessed-secret-123", algorithm="HS256"), id="HS256 shared secret"),
    ],
)
def test_bad_tokens_are_401(real_auth, token):
    assert get_drills(real_auth, token).status_code == 401


def test_health_check_needs_no_login(real_auth):
    assert real_auth.get("/health").status_code == 200
