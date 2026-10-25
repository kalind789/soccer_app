import datetime as dt
import secrets
import uuid

from sqlalchemy import JSON, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


# Drill tags. Age groups follow U.S. Soccer's game formats: 4v4, 7v7, 9v9, then 11v11.
AGE_GROUPS = ("u6-u8", "u9-u10", "u11-u12", "u13+")
GOALS = ("warm-up", "possession", "attacking", "finishing", "defending", "transition")
# A team's staff. The head coach created the team (or was handed it) and manages it; coaches plan with them.
ROLES = ("head_coach", "coach")
INVITE_DAYS = 7


def utcnow() -> dt.datetime:
    """Now, in UTC, without a time zone attached: how invite expiry times are stored."""
    return dt.datetime.now(dt.UTC).replace(tzinfo=None)


class InvalidSessionTimesError(Exception):
    """Raised when a session plan ends at or before it starts."""


class ArchivedDrillError(Exception):
    """Raised when an archived drill is newly added to a session plan."""


class TeamNotEmptyError(Exception):
    """Raised when deleting a team that still has session plans."""


class OtherTeamDrillError(Exception):
    """Raised when another team's drill is newly added to a session plan."""


class InvalidInviteError(Exception):
    """Raised when an invite link is wrong, turned off, or expired."""


class LastHeadCoachError(Exception):
    """Raised when the only head coach tries to leave, which would leave the team with no one in charge."""


class Drill(Base):
    """A drill in one team's library, or a drill idea (no team) that every team can use.

    Drill ideas come with the app (a migration adds them), and nobody can edit them.
    """

    __tablename__ = "drills"

    id: Mapped[int] = mapped_column(primary_key=True)
    team_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, default="")
    objective: Mapped[str] = mapped_column(Text, default="")
    archived: Mapped[bool] = mapped_column(default=False)
    # Tags, as lists of the values in AGE_GROUPS and GOALS. A JSON list is enough: the lists are
    # short, and filtering happens in the browser.
    age_groups: Mapped[list[str]] = mapped_column(JSON, default=list)
    goals: Mapped[list[str]] = mapped_column(JSON, default=list)

    team: Mapped["Team | None"] = relationship(back_populates="drills")

    @property
    def is_idea(self) -> bool:
        return self.team_id is None

    def archive(self) -> None:
        self.archived = True

    def unarchive(self) -> None:
        self.archived = False


class Team(Base):
    """A team that session plans belong to, e.g. "U12 Eagles 2027". A new year is just a new team."""

    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    # One of AGE_GROUPS. Empty only for teams made before age groups existed.
    age_group: Mapped[str | None] = mapped_column(String(20))
    # The invite link's secret part. One link per team: a new link or "turn off" replaces it.
    invite_token: Mapped[str | None] = mapped_column(String(64), unique=True)
    invite_expires_at: Mapped[dt.datetime | None]

    members: Mapped[list["TeamMember"]] = relationship(
        back_populates="team", cascade="all, delete-orphan", order_by="TeamMember.joined_at"
    )

    plans: Mapped[list["SessionPlan"]] = relationship(back_populates="team")
    # The team's own drill library. Deleting a team (only possible with no plans) deletes its drills.
    drills: Mapped[list[Drill]] = relationship(back_populates="team", cascade="all, delete-orphan")

    @property
    def plan_count(self) -> int:
        return len(self.plans)

    def member(self, user_id: uuid.UUID) -> "TeamMember | None":
        return next((m for m in self.members if m.user_id == user_id), None)

    def new_invite(self, now: dt.datetime) -> None:
        # 128 random bits, unguessable. Anyone holding the link can join, like a group chat invite.
        self.invite_token = secrets.token_urlsafe(16)
        self.invite_expires_at = now + dt.timedelta(days=INVITE_DAYS)

    def turn_off_invite(self) -> None:
        self.invite_token = None
        self.invite_expires_at = None

    def check_invite(self, token: str, now: dt.datetime) -> None:
        # compare_digest takes the same time whether the first or last character is wrong,
        # so response times don't hint at the right token.
        if self.invite_token is None or not secrets.compare_digest(self.invite_token, token):
            raise InvalidInviteError("This invite link isn't valid anymore")
        if self.invite_expires_at is None or self.invite_expires_at < now:
            raise InvalidInviteError("This invite link has expired. Ask the head coach for a new one.")

    def add_member(self, user_id: uuid.UUID, name: str, email: str, role: str = "coach") -> "TeamMember":
        """Join the team. Joining twice is fine: you stay what you were."""
        existing = self.member(user_id)
        if existing:
            return existing
        member = TeamMember(user_id=user_id, name=name, email=email, role=role)
        self.members.append(member)
        return member

    def remove_member(self, member: "TeamMember") -> None:
        head_coaches = [m for m in self.members if m.role == "head_coach"]
        if head_coaches == [member]:
            raise LastHeadCoachError("The head coach can't leave. Delete the team instead.")
        self.members.remove(member)

    def check_can_delete(self) -> None:
        # Deleting a team would take its plans with it, so empty it first (move or delete the plans).
        if self.plans:
            raise TeamNotEmptyError(f"{self.name} still has {len(self.plans)} session plans")


class SessionPlan(Base):
    """One planned practice. Not called `Session`, which is SQLAlchemy's database session."""

    __tablename__ = "session_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Who can see a plan follows from its team, so a plan has no owner of its own.
    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), index=True)
    title: Mapped[str] = mapped_column(String(100))
    focus: Mapped[str] = mapped_column(String(200), default="")
    location: Mapped[str] = mapped_column(String(200), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    date: Mapped[dt.date]
    start_time: Mapped[dt.time]
    end_time: Mapped[dt.time]

    team: Mapped[Team] = relationship(back_populates="plans")

    # The ordered slots. Deleting a plan deletes its slots, but never the drills themselves.
    slots: Mapped[list["SessionDrill"]] = relationship(
        order_by="SessionDrill.position", cascade="all, delete-orphan"
    )

    @property
    def duration_minutes(self) -> int:
        start = dt.datetime.combine(self.date, self.start_time)
        end = dt.datetime.combine(self.date, self.end_time)
        return int((end - start).total_seconds() // 60)

    def check_times(self) -> None:
        if self.end_time <= self.start_time:
            raise InvalidSessionTimesError("end_time must be after start_time")

    @property
    def planned_minutes(self) -> int:
        """Total drill time. It can be more or less than duration_minutes; the coach decides."""
        return sum(slot.minutes for slot in self.slots)

    @property
    def drill_count(self) -> int:
        return len(self.slots)

    def set_drills(self, drills: list[tuple[Drill, int]]) -> None:
        """Replace the drill list with (drill, minutes) pairs.

        The list order becomes the session order, and repeats are allowed.
        """
        already_in_plan = {slot.drill_id for slot in self.slots}
        for drill, _ in drills:
            if drill.id in already_in_plan:
                continue  # Already there, so it can stay even if it's archived or from another team.
            if drill.archived:
                raise ArchivedDrillError(f"Drill {drill.id} is archived")
            if not drill.is_idea and drill.team_id != self.team_id:
                raise OtherTeamDrillError(f"Drill {drill.id} not found")
        self.slots = [
            SessionDrill(drill=drill, minutes=minutes, position=i)
            for i, (drill, minutes) in enumerate(drills)
        ]


class SessionDrill(Base):
    """One slot in a session plan: which drill, for how long, and where in the order.

    A link table between SessionPlan and Drill. It has its own id, so the same
    drill can appear in a plan more than once.
    """

    __tablename__ = "session_drills"

    id: Mapped[int] = mapped_column(primary_key=True)
    session_plan_id: Mapped[int] = mapped_column(ForeignKey("session_plans.id"))
    drill_id: Mapped[int] = mapped_column(ForeignKey("drills.id"))
    position: Mapped[int]
    # Lives on the slot, not the drill: the same drill can run 15 minutes in one plan and 20 in another.
    minutes: Mapped[int]

    drill: Mapped[Drill] = relationship()


class TeamMember(Base):
    """One coach on one team's staff. A coach can be on several teams, and a team has several coaches."""

    __tablename__ = "team_members"

    team_id: Mapped[int] = mapped_column(ForeignKey("teams.id"), primary_key=True)
    # Their Supabase user id. No foreign key to auth.users: that table belongs to Supabase,
    # and tests run on SQLite without it. Indexed, because "my teams" filters by it.
    user_id: Mapped[uuid.UUID] = mapped_column(primary_key=True, index=True)
    role: Mapped[str] = mapped_column(String(20))  # One of ROLES.
    # Copied from their login, so teammates can see who's on staff. Refreshed when they list their teams.
    name: Mapped[str] = mapped_column(String(200), default="")
    email: Mapped[str] = mapped_column(String(320), default="")
    joined_at: Mapped[dt.datetime] = mapped_column(server_default=func.now())

    team: Mapped[Team] = relationship(back_populates="members")
