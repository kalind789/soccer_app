"""Who is making this request? Checks the Supabase login token sent with every request.

Authentication (who are you?) happens here. Authorization (what may you touch?) happens in the
routers, which only ever look at the current user's own drills and plans.
"""

from dataclasses import dataclass
from functools import cache
from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app import settings


@dataclass(frozen=True)
class User:
    id: UUID  # The same id as the user's row in Supabase's auth.users table.
    email: str | None


# Reads the "Authorization: Bearer <token>" header. auto_error=False so we can send our own 401.
bearer = HTTPBearer(auto_error=False)

# Supabase signs tokens with a private key and publishes the matching public keys (ES256 for this project).
# Only asymmetric algorithms are accepted, so a token signed with a guessed shared secret can't get in.
ALGORITHMS = ["ES256", "RS256"]


@cache
def _jwks_client() -> jwt.PyJWKClient:
    # Downloads the public keys once and keeps them for 10 minutes.
    return jwt.PyJWKClient(f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json", lifespan=600)


def signing_key(token: str):
    """The public key the token says it was signed with. Tests replace this with their own key."""
    return _jwks_client().get_signing_key_from_jwt(token).key


def decode_token(token: str) -> dict:
    """Return the token's claims, or raise jwt.PyJWTError if it's forged, expired, or not for us."""
    return jwt.decode(
        token,
        signing_key(token),
        algorithms=ALGORITHMS,
        audience="authenticated",  # Supabase's audience for logged-in users.
        issuer=f"{settings.SUPABASE_URL}/auth/v1",  # Made by *our* Supabase project, not another one.
        options={"require": ["exp", "sub"]},
    )


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)]) -> User:
    if credentials is None:
        raise _unauthorized("Not logged in")
    if not settings.SUPABASE_URL:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Login isn't set up: SUPABASE_URL is missing")
    try:
        claims = decode_token(credentials.credentials)
        return User(id=UUID(claims["sub"]), email=claims.get("email"))
    except (jwt.PyJWTError, ValueError):
        raise _unauthorized("Your login has expired or isn't valid. Please log in again.")


def _unauthorized(detail: str) -> HTTPException:
    # The WWW-Authenticate header tells the caller *how* to log in: with a bearer token.
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail, headers={"WWW-Authenticate": "Bearer"})


# Shortcut for endpoint parameters, like DbSession: `user: CurrentUser`.
CurrentUser = Annotated[User, Depends(get_current_user)]
