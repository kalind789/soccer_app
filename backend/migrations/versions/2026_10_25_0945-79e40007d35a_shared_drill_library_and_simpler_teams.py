"""shared drill library and simpler teams

Drills belong to everyone now, so they lose owner_id. Teams are just a name: season and
previous_team_id go away (a new year is simply a new team).

Revision ID: 79e40007d35a
Revises: 7d71dfb0b2d0
Create Date: 2026-10-25 09:45:08.834646

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79e40007d35a'
down_revision: Union[str, Sequence[str], None] = '7d71dfb0b2d0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Same placeholder owner as the owner_id migration, for the downgrade.
NOBODY = "0" * 32


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('drills', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_drills_owner_id'))
        batch_op.drop_column('owner_id')

    # Dropping previous_team_id also drops its foreign key.
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.drop_column('previous_team_id')
        batch_op.drop_column('season')


def downgrade() -> None:
    """Downgrade schema. Seasons and links can't come back, so teams get "2026" and no link."""
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('season', sa.String(length=20), nullable=False, server_default="2026"))
        batch_op.add_column(sa.Column('previous_team_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'teams_previous_team_id_fkey', 'teams', ['previous_team_id'], ['id'], ondelete='SET NULL'
        )
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.alter_column('season', server_default=None)

    # Drill owners can't come back either, so every drill gets the nobody owner.
    with op.batch_alter_table('drills', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_id', sa.Uuid(), nullable=False, server_default=NOBODY))
        batch_op.create_index(batch_op.f('ix_drills_owner_id'), ['owner_id'], unique=False)
    with op.batch_alter_table('drills', schema=None) as batch_op:
        batch_op.alter_column('owner_id', server_default=None)
