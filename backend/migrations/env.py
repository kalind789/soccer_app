"""Alembic runs this file for every command (upgrade, revision, ...)."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

import app.models  # noqa: F401  Importing the models registers their tables on Base.metadata.
from app.database import Base
from app.settings import DATABASE_URL, normalize_url

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

# Use the app's DATABASE_URL, unless the caller (a test) set its own.
url = normalize_url(config.get_main_option("sqlalchemy.url") or DATABASE_URL)

with create_engine(url).connect() as connection:
    context.configure(
        connection=connection,
        # What the tables *should* look like. `revision --autogenerate` compares the database to this.
        target_metadata=Base.metadata,
        # SQLite can't change most columns in place, so Alembic copies the table instead.
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()
