"""add minutes to session drills

Revision ID: f9cc8839a08b
Revises: 9dafdd2eaa37
Create Date: 2026-10-23 10:35:56.841779

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9cc8839a08b'
down_revision: Union[str, Sequence[str], None] = '9dafdd2eaa37'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Slots that already exist need some value, so they start at 10 minutes.
    # The default is removed afterward: new slots must always say how long they run.
    with op.batch_alter_table('session_drills', schema=None) as batch_op:
        batch_op.add_column(sa.Column('minutes', sa.Integer(), nullable=False, server_default='10'))
    with op.batch_alter_table('session_drills', schema=None) as batch_op:
        batch_op.alter_column('minutes', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('session_drills', schema=None) as batch_op:
        batch_op.drop_column('minutes')
