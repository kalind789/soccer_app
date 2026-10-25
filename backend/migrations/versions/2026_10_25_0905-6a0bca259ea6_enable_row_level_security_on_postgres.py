"""enable row level security on postgres

Revision ID: 6a0bca259ea6
Revises: f9cc8839a08b
Create Date: 2026-10-25 09:05:26.765864

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6a0bca259ea6'
down_revision: Union[str, Sequence[str], None] = 'f9cc8839a08b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Supabase puts a public web API (PostgREST) in front of every table in the "public" schema.
# With row level security on and no policies, that API can't read or write anything.
# Our backend connects as the table owner, which RLS doesn't apply to, so the app is unaffected.
# SQLite has no RLS, so this does nothing there. New tables need the same treatment.
TABLES = ["drills", "session_plans", "session_drills", "alembic_version"]


def upgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    if op.get_bind().dialect.name != "postgresql":
        return
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY")
