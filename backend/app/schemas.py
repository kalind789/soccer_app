import datetime as dt
from typing import Annotated, Literal
from uuid import UUID

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

# Must match AGE_GROUPS and GOALS in models.py. Literal makes Pydantic reject anything else (422).
AgeGroup = Literal["u6-u8", "u9-u10", "u11-u12", "u13+"]
Goal = Literal["warm-up", "possession", "attacking", "finishing", "defending", "transition"]
Role = Literal["head_coach", "coach"]  # Must match ROLES in models.py.


def without_repeats(tags: list[str]) -> list[str]:
    return list(dict.fromkeys(tags))  # dict keys are unique and keep their order.


AgeGroups = Annotated[list[AgeGroup], AfterValidator(without_repeats)]
Goals = Annotated[list[Goal], AfterValidator(without_repeats)]


class DrillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""
    objective: str = ""
    age_groups: AgeGroups = []
    goals: Goals = []


class DrillUpdate(BaseModel):
    """Every field is optional: only the fields sent get changed."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    objective: str | None = None
    age_groups: AgeGroups | None = None
    goals: Goals | None = None


class DrillRead(BaseModel):
    # Lets Pydantic read values from a SQLAlchemy object (drill.name) instead of a dict.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    objective: str
    archived: bool
    team_id: int | None  # None for a drill idea.
    age_groups: list[str]
    goals: list[str]


class UsedDrill(DrillRead):
    times_used: int  # In this team's session plans.


class DrillSuggestions(BaseModel):
    used_before: list[UsedDrill]  # Most used first.
    recommended: list[DrillRead]  # Up to 8 unused drill ideas for the team's age group, fundamentals first.


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    age_group: AgeGroup


class TeamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    age_group: AgeGroup | None = None


class TeamRef(BaseModel):
    """Just enough to show which team something belongs to."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age_group: AgeGroup | None


class MemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    name: str
    email: str
    role: Role


class TeamRead(TeamRef):
    plan_count: int
    members: list[MemberRead]  # The staff, in the order they joined (so whoever made the team comes first).
    my_role: Role | None = None  # The logged-in coach's role, so the app knows what to show.


class InviteLink(BaseModel):
    """The secret part of the link. The app turns it into http://.../join/<token>."""

    token: str
    expires_at: dt.datetime


class InvitePreview(BaseModel):
    """What someone with the link sees before joining."""

    team_id: int
    team_name: str
    age_group: AgeGroup | None
    head_coach: str
    already_member: bool


class SessionPlanCreate(BaseModel):
    team_id: int
    title: str = Field(min_length=1, max_length=100)
    focus: str = Field(default="", max_length=200)
    location: str = Field(default="", max_length=200)
    notes: str = ""
    date: dt.date
    start_time: dt.time
    end_time: dt.time

class SessionPlanUpdate(BaseModel):
    team_id: int | None = None  # Move the plan to another of your teams.
    title: str | None = Field(default=None, min_length=1, max_length=100)
    focus: str | None = Field(default=None, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    notes: str | None = None
    date: dt.date | None = None
    start_time: dt.time | None = None
    end_time: dt.time | None = None

class SessionPlanSummary(BaseModel):
    """The short version, used in lists."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    team: TeamRef
    title: str
    focus: str
    location: str
    date: dt.date
    start_time: dt.time
    end_time: dt.time
    duration_minutes: int
    planned_minutes: int
    drill_count: int


class SessionDrillRead(BaseModel):
    """One slot in a plan: the drill, and how long it runs in this plan."""

    model_config = ConfigDict(from_attributes=True)

    drill: DrillRead
    minutes: int


class SessionPlanRead(SessionPlanSummary):
    """The full version, used when showing one session plan."""

    notes: str
    # Named `slots` to match the model: the same drill can appear more than once.
    slots: list[SessionDrillRead]


class SessionDrillEntry(BaseModel):
    drill_id: int
    # Any positive number of minutes. There's no upper limit: the coach decides.
    minutes: int = Field(gt=0)


class SessionDrillsUpdate(BaseModel):
    """The full, ordered list of drills with their minutes. It replaces the plan's current list."""

    drills: list[SessionDrillEntry]
