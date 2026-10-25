"""team drills, tags and drill ideas

Drills now belong to a team (team_id). A drill with no team is a drill idea: a starter library
that ships with the app, added below. Both kinds get age group and goal tags.

Revision ID: dabd8f706a33
Revises: 79e40007d35a
Create Date: 2026-10-25 10:27:13.678872

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dabd8f706a33'
down_revision: Union[str, Sequence[str], None] = '79e40007d35a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Same placeholder owner as the owner_id migration.
NOBODY = "0" * 32

ALL_AGES = ["u6-u8", "u9-u10", "u11-u12", "u13+"]


def idea(name, age_groups, goals, objective, setup, how, coaching):
    description = f"Setup: {setup}\n\nHow it works: {how}\n\nCoaching points: {coaching}"
    return {"name": name, "description": description, "objective": objective, "archived": False,
            "team_id": None, "age_groups": age_groups, "goals": goals}


# The starter library. Age groups follow U.S. Soccer's game formats (4v4 for U6–U8, 7v7 for U9–U10,
# 9v9 for U11–U12, 11v11 from U13). Goals follow its moments of the game: attacking, defending and
# the transitions between them (transitions from U11), plus warm-ups, possession and finishing.
# Ideas tagged with every age group are the fundamentals the app recommends to every team.
IDEAS = [
    idea("Ball Mastery", ALL_AGES, ["warm-up"],
         "Comfort on the ball with both feet.",
         "Every player has a ball in a 20x20 yard area.",
         "On the coach's call, players do toe taps, sole rolls, inside-outside touches, pull-backs and turns, 30–45 seconds per move with short rests. Count touches and try to beat your score.",
         "Small touches, ball close, eyes up between touches, use both feet."),
    idea("Red Light, Green Light", ["u6-u8"], ["warm-up"],
         "Dribbling with control and stopping on command.",
         "Players with a ball on one line, the coach facing them about 25 yards away.",
         "Green light: dribble toward the coach. Yellow: slow down. Red: stop the ball with the sole. If your ball keeps rolling, go back a few steps. Add \"Turn around!\" for a quick turn.",
         "Ball close all the time, stop it with the sole, look up to see and hear the next call."),
    idea("Gates Dribbling", ["u6-u8", "u9-u10", "u11-u12"], ["warm-up", "attacking"],
         "Dribbling with the head up and changing direction.",
         "10–15 small cone gates (2 yards wide) spread around a 25x25 area. Every player has a ball.",
         "Dribble through as many different gates as you can in 60 seconds. Then try weaker foot only, add a defender who steals balls, or pass through the gates in pairs.",
         "Eyes up to find an open gate, speed up after each gate, use different parts of the foot."),
    idea("Sharks and Minnows", ["u6-u8", "u9-u10"], ["warm-up", "attacking"],
         "Dribbling under pressure and shielding the ball.",
         "A 20x30 area. Minnows each have a ball on one end line; one or two sharks wait in the middle without a ball.",
         "Minnows dribble to the far line without a shark kicking their ball out. Caught minnows become sharks. The last minnow wins.",
         "Shield the ball with your body, change speed and direction to escape, keep the ball close in traffic."),
    idea("Passing Pairs with Movement", ALL_AGES, ["warm-up", "possession"],
         "Accurate passing and a good first touch on the move.",
         "Pairs with one ball, moving freely around a 25x25 area.",
         "Partners pass while moving around the space and the other pairs. Then try two touches only, or pass and move to a new spot every time.",
         "Pass with the inside of the foot, first touch away from traffic, move into open space after you pass, talk to your partner."),
    idea("Pass Through the Gates", ["u6-u8", "u9-u10"], ["possession"],
         "Passing to a teammate and moving to receive.",
         "6–8 cone gates in a 25x25 area. Pairs with one ball.",
         "Pairs score a point each time they pass to each other through a gate. Most points in 90 seconds wins. Add one or two defenders who try to intercept.",
         "The receiver gets to the gate early and calls for the ball; pass softly enough that your partner can keep moving."),
    idea("Rondo 4v1", ["u9-u10", "u11-u12"], ["possession"],
         "Keeping the ball under pressure.",
         "A 10x10 square: four players on the outside, one defender inside.",
         "The outside players keep the ball away from the defender. If the defender touches it, the player who lost it swaps in. Count passes and try to reach 10.",
         "Open your body to see both options, receive across your body, pass to the far foot, move along the line to give an angle."),
    idea("Rondo 5v2", ["u11-u12", "u13+"], ["possession", "transition"],
         "Moving the ball quickly, and winning it back as a pair.",
         "A 12x12 square: five attackers, two defenders.",
         "Attackers keep possession; a pass that splits the two defenders scores a bonus point. When the defenders win it, they try to pass to a coach outside the square before the attackers win it back.",
         "One- and two-touch passing, look for the split pass. Defenders press together: one presses, one covers."),
    idea("4v4+3 Possession", ["u11-u12", "u13+"], ["possession", "transition"],
         "Keeping the ball as a team, and reacting the moment possession changes.",
         "A 30x30 area: two teams of four, plus three neutral players in a third color who play with whichever team has the ball.",
         "The team with the ball plays 7v4 with the neutrals and scores a point for 6 passes in a row. When the ball is lost, the other team attacks straight away.",
         "Spread out to make the field big, support at angles, press right away when you lose the ball."),
    idea("End Zone Game", ["u9-u10", "u11-u12", "u13+"], ["possession", "attacking"],
         "Playing forward, and keeping the ball until a forward chance appears.",
         "A 30x25 field with a 5-yard end zone at each end. Teams of 3 to 5, no goalkeepers.",
         "Score by dribbling into the other team's end zone, or (for older players) by receiving a pass inside it.",
         "Look forward first, support the player on the ball, time your run so you receive while moving."),
    idea("4v4 to Small Goals", ALL_AGES, ["attacking", "defending"],
         "Lots of touches and decisions in a real game.",
         "A 25x35 field (bigger for older players) with small goals or cone gates at each end, no goalkeepers.",
         "Play 4v4 with kick-ins or dribble-ins from the sideline. Rotate teams every 4–5 minutes. It's U.S. Soccer's game format for U6–U8, and older players get far more touches than in a big game.",
         "Attack with width and depth, encourage 1v1 moves. Defend by pressing the ball and staying close together."),
    idea("Scrimmage in Your Game Format", ALL_AGES, ["attacking", "defending", "transition"],
         "Using today's topic in the real game.",
         "Your age group's game: 4v4 (U6–U8), 7v7 (U9–U10), 9v9 (U11–U12) or 11v11 (U13+).",
         "Start and end practice with it, as in U.S. Soccer's Play–Practice–Play. Keep the coaching light: let them play, and ask a question or two at water breaks about today's topic.",
         "Watch for today's practice goal showing up in the game, and praise it when it does."),
    idea("1v1 to Goal", ALL_AGES, ["attacking", "defending"],
         "Beating a player 1v1, and defending 1v1.",
         "A 15x20 area with a small goal at each end. Two lines of players, one beside each goal; the coach stands at the side with the balls.",
         "The coach plays a ball in and the first player from each line battles: attack the far goal, defend your own. The next pair goes after a goal or 30 seconds.",
         "Attack the defender at speed, use a move and burst away. Defender: close down quickly, get low, push them to one side."),
    idea("2v1 to Goal", ["u9-u10", "u11-u12", "u13+"], ["attacking"],
         "Using an extra player: when to pass and when to dribble.",
         "A 20x25 area with a goal and goalkeeper. Two attackers start at the halfway line, one defender near the goal.",
         "The attackers try to score. If the defender wins the ball, they score by dribbling over the halfway line. Switch roles every few turns.",
         "The dribbler draws the defender in, then passes (or keeps going if the defender stays back). The other attacker stays wide. Shoot early."),
    idea("3v2 to Goal with Counter", ["u11-u12", "u13+"], ["attacking", "defending", "transition"],
         "Making the extra player count, then reacting when the ball is lost.",
         "Half a field: a big goal with a goalkeeper, and two small goals at the halfway line.",
         "Three attackers play against two defenders. If the defenders or the goalkeeper win the ball, they score through either small goal.",
         "Attackers: stay wide, decide quickly, shoot early. Defenders: one presses, one covers, delay until help arrives, and play forward fast once you win it."),
    idea("Crossing and Finishing", ["u11-u12", "u13+"], ["attacking", "finishing"],
         "Getting the ball wide and turning crosses into goals.",
         "A goal with a goalkeeper. A wide player on each side about 30 yards out, two strikers in the middle.",
         "A wide player dribbles down the line and crosses (start with low, driven crosses). The strikers run to the near post and the far post. Then add one or two defenders.",
         "Cross early or from near the end line. Strikers arrive late and split the posts, and finish first time."),
    idea("Build Out from the Back", ["u9-u10", "u11-u12", "u13+"], ["possession", "attacking"],
         "Playing out from the goalkeeper under pressure.",
         "Half a field (use the build-out line for U9–U10). A goalkeeper and three defenders against two attackers, with cone gates at the halfway line.",
         "The goalkeeper starts with the ball. The defending team scores by dribbling or passing through a gate. If the attackers win the ball, they shoot on goal.",
         "Defenders spread wide, use the goalkeeper as an extra passer, find the free player. Be brave, not careless."),
    idea("Everybody Shoots (World Cup)", ["u6-u8", "u9-u10"], ["finishing", "attacking"],
         "Shooting with confidence in a busy, game-like area.",
         "One goal with a coach or goalkeeper in a 25x30 area. Players in teams of 2 or 3, each in a team color.",
         "The coach rolls one ball in and every team tries to score. A team that scores moves on to the next round; the last team each round does a quick fun challenge and jumps back in.",
         "Shoot whenever you get a chance, aim low for the corners, follow up for rebounds."),
    idea("Turn and Shoot", ["u9-u10", "u11-u12", "u13+"], ["finishing"],
         "Receiving, turning and finishing quickly.",
         "A goal with a goalkeeper. A server about 25 yards out, a striker 18–20 yards from goal facing the server.",
         "The server passes into the striker, who turns and shoots within two touches. Then add a passive defender behind the striker, then an active one.",
         "Check away, then toward the ball. Open your body to turn, look at the goal before the ball arrives, strike through the middle of the ball."),
    idea("Shooting Circuit (Pass, Receive, Shoot)", ["u11-u12", "u13+"], ["finishing"],
         "Finishing from a combination.",
         "A goal with a goalkeeper, a line of players 30 yards out, and a layoff player at the top of the box.",
         "Pass into the layoff player, run onto their layoff and finish. Rotate: shooter becomes the layoff player, then back to the line.",
         "Pass firmly, first touch toward goal, pick a corner, land on your shooting foot."),
    idea("1v1 Defending: Jockey and Channel", ALL_AGES, ["defending"],
         "Stopping an attacker 1v1.",
         "A 10x20 channel with a gate on each end line. An attacker at one end, a defender at the other.",
         "The defender passes to the attacker and closes them down; the attacker tries to dribble through the defender's gate. If the defender wins the ball, they score through the attacker's gate.",
         "Close down fast, then slow down. Stand side-on, low and on your toes, push the attacker to one side, tackle when their touch is heavy."),
    idea("Pressure and Cover 2v2", ["u11-u12", "u13+"], ["defending"],
         "Defending together: one presses, one covers.",
         "A 20x25 area. Two attackers start at one end line, two defenders at the other.",
         "The attackers try to dribble over the defenders' end line. The defenders work together to stop them, and if they win the ball, they counter to the other line.",
         "The first defender pressures the ball; the second covers at an angle behind them. Swap roles whenever the ball is passed."),
    idea("Win It Back in 5 Seconds", ["u11-u12", "u13+"], ["transition", "defending"],
         "Reacting the moment the ball is lost.",
         "A 30x30 grid with two teams of five.",
         "Teams keep possession. A team that loses the ball gets a bonus point if it wins it back within 5 seconds (the coach counts out loud).",
         "The nearest player presses right away, the others cut off passing lanes. If you can't win it quickly, drop back into shape."),
    idea("3v3 Waves", ["u9-u10", "u11-u12", "u13+"], ["transition", "attacking"],
         "Switching between attacking and defending fast.",
         "A 25x35 field with small goals. Extra teams of three wait behind each end line.",
         "Play 3v3. When a goal is scored or the ball goes out, the team that just defended leaves, and a new team of three rushes on with a ball and attacks straight away.",
         "Attack quickly before the defense is set. Defenders recover goal-side first."),
]

drills = sa.table(
    "drills",
    sa.column("name", sa.String), sa.column("description", sa.Text), sa.column("objective", sa.Text),
    sa.column("archived", sa.Boolean), sa.column("team_id", sa.Integer),
    sa.column("age_groups", sa.JSON), sa.column("goals", sa.JSON),
)


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('drills', schema=None) as batch_op:
        batch_op.add_column(sa.Column('team_id', sa.Integer(), nullable=True))
        # Existing rows start with no tags; the default only fills them in and is then dropped.
        batch_op.add_column(sa.Column('age_groups', sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
        batch_op.add_column(sa.Column('goals', sa.JSON(), nullable=False, server_default=sa.text("'[]'")))
        batch_op.create_index(batch_op.f('ix_drills_team_id'), ['team_id'], unique=False)
        batch_op.create_foreign_key('fk_drills_team_id_teams', 'teams', ['team_id'], ['id'])
    with op.batch_alter_table('drills', schema=None) as batch_op:
        batch_op.alter_column('age_groups', server_default=None)
        batch_op.alter_column('goals', server_default=None)

    connection = op.get_bind()
    # Each existing drill moves to the team of the first plan that uses it.
    connection.execute(sa.text("""
        UPDATE drills SET team_id = (
            SELECT p.team_id FROM session_drills s JOIN session_plans p ON p.id = s.session_plan_id
            WHERE s.drill_id = drills.id ORDER BY p.id LIMIT 1
        )
    """))
    # Unused drills go to the first team, or to a new ownerless "My team" if there are no teams.
    # Otherwise they'd have no team and turn into drill ideas.
    if connection.execute(sa.text("SELECT count(*) FROM drills WHERE team_id IS NULL")).scalar():
        team_id = connection.execute(sa.text("SELECT min(id) FROM teams")).scalar()
        if team_id is None:
            team_id = connection.execute(
                sa.text("INSERT INTO teams (owner_id, name) VALUES (:owner, 'My team') RETURNING id"),
                {"owner": NOBODY},
            ).scalar()
        connection.execute(sa.text("UPDATE drills SET team_id = :team WHERE team_id IS NULL"), {"team": team_id})

    op.bulk_insert(drills, IDEAS)


def downgrade() -> None:
    """Downgrade schema. Drill ideas, and plans' uses of them, are removed; team drills stay."""
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM session_drills WHERE drill_id IN (SELECT id FROM drills WHERE team_id IS NULL)"))
    connection.execute(sa.text("DELETE FROM drills WHERE team_id IS NULL"))
    with op.batch_alter_table('drills', schema=None) as batch_op:
        batch_op.drop_constraint('fk_drills_team_id_teams', type_='foreignkey')
        batch_op.drop_index(batch_op.f('ix_drills_team_id'))
        batch_op.drop_column('goals')
        batch_op.drop_column('age_groups')
        batch_op.drop_column('team_id')
