# Step 11: Logins and ownership (backend)

- **Authentication vs authorization:** authentication = proving who you are (the login token). Authorization = what you're allowed to touch (only your own drills and plans).
- **JWT (JSON Web Token):** a signed note from Supabase that says "this is user 1234, valid until 7:30". Three parts separated by dots: header, claims, signature. Anyone can *read* it; only Supabase can *sign* it.
- **Claims we check:** `sub` (the user id), `exp` (expiry), `aud` = `authenticated` (it's a logged-in user's token), `iss` = our project (not another Supabase project's).
- **Public/private keys (asymmetric, ES256):** Supabase signs with a private key only it has. We check with the matching public key, which anyone may download (the JWKS URL). So the backend holds no secret at all.
- **Algorithm confusion attack:** a forged token that says "HS256, signed with this password". We only accept ES256/RS256, so it fails. One of our tests tries exactly this.
- **Bearer token:** sent as the header `Authorization: Bearer <token>`. "Bearer" means whoever holds it gets in, so it must stay secret in transit (HTTPS).
- **401 vs 403 vs 404:** 401 = not logged in. 403 = logged in but not allowed. We return 404 for someone else's things, so ids don't reveal what exists.
- **Dependency override for login:** tests swap `get_current_user` for "it's Alice", just like `get_db` is swapped for a test database. `login_as(BOB)` switches users mid-test.
- **`@pytest.mark.parametrize`:** run one test many times with different inputs, here 9 kinds of bad tokens.
- **Shell variable beats `.env`:** `DATABASE_URL=sqlite:///... uv run alembic ...` works on a scratch file instead of Supabase, because `load_dotenv` never overrides what's already set.

My notes:
