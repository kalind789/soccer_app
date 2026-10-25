"""team staff, age group and invite link

A team now has a staff (team_members) instead of one owner: each team's owner becomes its head coach.
Teams also get an age group and an invite link.

Revision ID: ec9f76f942c3
Revises: dabd8f706a33
Create Date: 2026-10-25 10:43:11.678631

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ec9f76f942c3'
down_revision: Union[str, Sequence[str], None] = 'dabd8f706a33'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Same placeholder owner as the owner_id migration, for the downgrade.
NOBODY = "0" * 32


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('team_members',
    sa.Column('team_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('email', sa.String(length=320), nullable=False),
    sa.Column('joined_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('team_id', 'user_id')
    )
    with op.batch_alter_table('team_members', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_team_members_user_id'), ['user_id'], unique=False)

    # Every team's owner becomes its head coach. Names fill in the next time they list their teams.
    op.execute("""
        INSERT INTO team_members (team_id, user_id, role, name, email)
        SELECT id, owner_id, 'head_coach', '', '' FROM teams
    """)

    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('age_group', sa.String(length=20), nullable=True))
        batch_op.add_column(sa.Column('invite_token', sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column('invite_expires_at', sa.DateTime(), nullable=True))
        batch_op.drop_index(batch_op.f('ix_teams_owner_id'))
        batch_op.create_unique_constraint('uq_teams_invite_token', ['invite_token'])
        batch_op.drop_column('owner_id')

    # Like every table: block Supabase's public Data API (see the row level security migration).
    if op.get_bind().dialect.name == "postgresql":
        op.execute("ALTER TABLE team_members ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    """Downgrade schema. Each team goes back to one owner: its first head coach. Other coaches lose access."""
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_id', sa.Uuid(), nullable=False, server_default=NOBODY))
        batch_op.drop_constraint('uq_teams_invite_token', type_='unique')
        batch_op.create_index(batch_op.f('ix_teams_owner_id'), ['owner_id'], unique=False)
        batch_op.drop_column('invite_expires_at')
        batch_op.drop_column('invite_token')
        batch_op.drop_column('age_group')
    with op.batch_alter_table('teams', schema=None) as batch_op:
        batch_op.alter_column('owner_id', server_default=None)
    op.execute("""
        UPDATE teams SET owner_id = (
            SELECT user_id FROM team_members m
            WHERE m.team_id = teams.id AND m.role = 'head_coach'
            ORDER BY m.joined_at LIMIT 1
        )
        WHERE EXISTS (SELECT 1 FROM team_members m WHERE m.team_id = teams.id AND m.role = 'head_coach')
    """)

    with op.batch_alter_table('team_members', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_team_members_user_id'))
    op.drop_table('team_members')
