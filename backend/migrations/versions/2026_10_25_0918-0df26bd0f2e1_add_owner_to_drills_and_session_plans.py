"""add owner to drills and session plans

Revision ID: 0df26bd0f2e1
Revises: 6a0bca259ea6
Create Date: 2026-10-25 09:18:56.555532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0df26bd0f2e1'
down_revision: Union[str, Sequence[str], None] = '6a0bca259ea6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Rows that exist before login did belong to nobody. They get the all-zeros id, which no real user
# has, so they're hidden from everyone rather than shown to the wrong person. Written as 32 hex
# digits, a form both Postgres and SQLite (where Uuid is stored as text) accept.
NOBODY = "0" * 32


def upgrade() -> None:
    for table in ("drills", "session_plans"):
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.add_column(sa.Column("owner_id", sa.Uuid(), nullable=False, server_default=NOBODY))
            batch_op.create_index(batch_op.f(f"ix_{table}_owner_id"), ["owner_id"], unique=False)
        # Remove the default afterward: new rows must always say who owns them.
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.alter_column("owner_id", server_default=None)


def downgrade() -> None:
    for table in ("session_plans", "drills"):
        with op.batch_alter_table(table, schema=None) as batch_op:
            batch_op.drop_index(batch_op.f(f"ix_{table}_owner_id"))
            batch_op.drop_column("owner_id")
