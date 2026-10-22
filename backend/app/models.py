import datetime as dt

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class InvalidSessionTimesError(Exception):
    """Raised when a session plan ends at or before it starts."""


class Drill(Base):
    """A reusable drill in the coach's library."""

    __tablename__ = "drills"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text, default="")
    objective: Mapped[str] = mapped_column(Text, default="")
    archived: Mapped[bool] = mapped_column(default=False)

    def archive(self) -> None:
        self.archived = True

    def unarchive(self) -> None:
        self.archived = False


class SessionPlan(Base):
    """One planned practice. Not called `Session`, which is SQLAlchemy's database session."""

    __tablename__ = "session_plans"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    focus: Mapped[str] = mapped_column(String(200), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    date: Mapped[dt.date]
    start_time: Mapped[dt.time]
    end_time: Mapped[dt.time]

    @property
    def duration_minutes(self) -> int:
        start = dt.datetime.combine(self.date, self.start_time)
        end = dt.datetime.combine(self.date, self.end_time)
        return int((end - start).total_seconds() // 60)

    def check_times(self) -> None:
        if self.end_time <= self.start_time:
            raise InvalidSessionTimesError("end_time must be after start_time")
