import datetime as dt

from pydantic import BaseModel, ConfigDict, Field


class DrillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str = ""
    objective: str = ""


class DrillUpdate(BaseModel):
    """Every field is optional: only the fields sent get changed."""

    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None
    objective: str | None = None


class DrillRead(BaseModel):
    # Lets Pydantic read values from a SQLAlchemy object (drill.name) instead of a dict.
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str
    objective: str
    archived: bool


class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    season: str = Field(min_length=1, max_length=20)
    # Set when starting next season's version of an existing team.
    previous_team_id: int | None = None


class TeamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    season: str | None = Field(default=None, min_length=1, max_length=20)


class TeamRef(BaseModel):
    """Just enough to show which team something belongs to."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    season: str


class TeamRead(TeamRef):
    previous_team_id: int | None
    plan_count: int


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
