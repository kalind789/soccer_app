"""add teams and move session plans into them

Revision ID: 7d71dfb0b2d0
Revises: 0df26bd0f2e1
Create Date: 2026-10-25 09:26:36.571718

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d71dfb0b2d0'
down_revision: Union[str, Sequence[str], None] = '0df26bd0f2e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Plans that already exist each go into a "My team" for their owner, so no plan is left without a team.
EXISTING_TEAM_NAME = "My team"
EXISTING_TEAM_SEASON = "2026"


def upgrade() -> None:
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("season", sa.String(length=20), nullable=False),
        sa.Column("previous_team_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["previous_team_id"], ["teams.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_teams_owner_id"), "teams", ["owner_id"], unique=False)

    # 1. Add team_id, empty for now.
    with op.batch_alter_table("session_plans", schema=None) as batch_op:
        batch_op.add_column(sa.Column("team_id", sa.Integer(), nullable=True))

    # 2. Fill it: one "My team" per owner who has plans, then point each plan at its owner's team.
    #    (The teams table is brand new, so each owner has exactly one team at this point.)
    conn = op.get_bind()
    conn.execute(
        sa.text("INSERT INTO teams (owner_id, name, season) SELECT DISTINCT owner_id, :name, :season FROM session_plans"),
        {"name": EXISTING_TEAM_NAME, "season": EXISTING_TEAM_SEASON},
    )
    conn.execute(
        sa.text("UPDATE session_plans SET team_id = (SELECT teams.id FROM teams WHERE teams.owner_id = session_plans.owner_id)")
    )

    # 3. Now every plan has a team: make it required, and drop the plan's own owner (the team has it).
    with op.batch_alter_table("session_plans", schema=None) as batch_op:
        batch_op.alter_column("team_id", nullable=False)
        batch_op.create_index(batch_op.f("ix_session_plans_team_id"), ["team_id"], unique=False)
        batch_op.create_foreign_key("fk_session_plans_team_id_teams", "teams", ["team_id"], ["id"])
        batch_op.drop_index(batch_op.f("ix_session_plans_owner_id"))
        batch_op.drop_column("owner_id")

    # Like every table: block Supabase's public Data API (see the row level security migration).
    if conn.dialect.name == "postgresql":
        op.execute("ALTER TABLE teams ENABLE ROW LEVEL SECURITY")


def downgrade() -> None:
    # Give plans their owner back (from their team), then remove teams.
    with op.batch_alter_table("session_plans", schema=None) as batch_op:
        batch_op.add_column(sa.Column("owner_id", sa.Uuid(), nullable=True))
    op.get_bind().execute(
        sa.text("UPDATE session_plans SET owner_id = (SELECT teams.owner_id FROM teams WHERE teams.id = session_plans.team_id)")
    )
    with op.batch_alter_table("session_plans", schema=None) as batch_op:
        batch_op.alter_column("owner_id", nullable=False)
        batch_op.create_index(batch_op.f("ix_session_plans_owner_id"), ["owner_id"], unique=False)
        batch_op.drop_constraint("fk_session_plans_team_id_teams", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_session_plans_team_id"))
        batch_op.drop_column("team_id")
    op.drop_index(op.f("ix_teams_owner_id"), table_name="teams")
    op.drop_table("teams")
