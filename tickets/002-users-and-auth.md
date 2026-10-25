# 002: Users, login, and authorization

**Status:** In progress (login works; hosting set up in `render.yaml` + `frontend/vercel.json`; Google login left) · **Size:** Large · **Depends on:** nothing. Blocks 003.

## Why

Right now anyone who opens the app sees and changes everything. Each coach needs their own account, and a coach should only see their own drills and plans.

## What

Accounts and login, with every drill and session plan belonging to an owner.

## Acceptance criteria

1. ✅ Move from SQLite to **Supabase Postgres**: `DATABASE_URL` points at it, and the Alembic migrations run cleanly on Postgres. (Done 2026-10-25: session pooler connection, RLS on every table.)
2. ✅ Sign up, log in, and log out (with Supabase Auth: email + password, and maybe Google). (Email + password done 2026-10-25. Google is optional, later.)
3. ✅ Drills and session plans get an `owner_id`, added by a migration. Existing rows are assigned to the first user. (Changed: they got an all-zeros "nobody" owner instead, because there were no users yet.)
4. ✅ **Authentication** (who are you?): every API request must include a valid login token, otherwise 401.
5. ✅ **Authorization** (what can you touch?): a user can only list, read, and edit their own drills and plans. Someone else's id returns 404, not 403, so it doesn't reveal that the item exists.
6. ✅ The frontend has login and sign-up pages, sends the token with every request, and redirects to login when it gets a 401.
7. ✅ Tests cover: no token → 401, my data → 200, someone else's data → 404.

## Out of scope

- Teams and sharing with other coaches (ticket 003)
- Password reset emails, if Supabase doesn't handle them for free

## Notes

- Learn the difference: **authentication** = proving who you are; **authorization** = what you're allowed to do.
- Set up the `get_current_user` dependency the same way as `get_db`, so tests can override it.
