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


class SessionPlanCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    focus: str = Field(default="", max_length=200)
    notes: str = ""
    date: dt.date
    start_time: dt.time
    end_time: dt.time


class SessionPlanUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    focus: str | None = Field(default=None, max_length=200)
    notes: str | None = None
    date: dt.date | None = None
    start_time: dt.time | None = None
    end_time: dt.time | None = None


class SessionPlanSummary(BaseModel):
    """The short version, used in lists."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    focus: str
    date: dt.date
    start_time: dt.time
    end_time: dt.time
    duration_minutes: int


class SessionPlanRead(SessionPlanSummary):
    """The full version, used when showing one session plan."""

    notes: str
    drills: list[DrillRead]


class SessionDrillsUpdate(BaseModel):
    """The full, ordered list of drill ids. It replaces the plan's current list."""

    drill_ids: list[int]
