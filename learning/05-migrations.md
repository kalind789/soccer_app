# Step 7: Alembic migrations

- **Schema:** the *shape* of the database: which tables, which columns, which types. (Different from a Pydantic schema, sadly the same word.)
- **Migration:** a small Python file that changes the schema one step: "add the `location` column". Kept in git, so every database (yours, a teammate's, production) goes through the same steps.
- **Why not `create_all`?** It only creates tables that are *missing*. It never adds a column to a table that already exists, so a new model field would quietly never reach your real database.
- **Alembic:** SQLAlchemy's migration tool. Its files live in `backend/migrations/`.
- **Revision:** one migration. Each has an id (`9dafdd2eaa37`) and points at the one before it (`down_revision`), forming a chain.
- **Head:** the newest revision. `alembic upgrade head` means "apply every step I haven't applied yet".
- **`alembic_version` table:** Alembic stores which revision the database is at here. That's how it knows what to run next.
- **`upgrade()` / `downgrade()`:** do the change, and undo it.
- **Autogenerate:** `alembic revision --autogenerate` compares your models to the database and writes the migration for you. Always read the file it writes, because it can guess wrong (for example a rename looks like "drop + add", which loses data).
- **Stamp:** `alembic stamp head` says "this database is already up to date" without running anything. We used it once, for the `planner.db` that `create_all` had made.
- **Batch mode:** SQLite can't change most columns in place, so Alembic copies the table to a new one. `render_as_batch=True` in `env.py` turns it on.
- **Guard test:** `test_migrations_match_models` builds a database from migrations and checks it matches the models. Forget a migration and it fails.

The new-field workflow from now on:
1. Change the model in `app/models.py`.
2. `uv run alembic revision --autogenerate -m "add equipment to drills"`
3. Read the new file in `migrations/versions/`.
4. `uv run alembic upgrade head`
5. `uv run pytest`

My notes:
