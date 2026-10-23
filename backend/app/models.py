import datetime as dt

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class InvalidSessionTimesError(Exception):
    """Raised when a session plan ends at or before it starts."""


class ArchivedDrillError(Exception):
    """Raised when an archived drill is newly added to a session plan."""


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
    location: Mapped[str] = mapped_column(String(200), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    date: Mapped[dt.date]
    start_time: Mapped[dt.time]
    end_time: Mapped[dt.time]

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
            if drill.archived and drill.id not in already_in_plan:
                raise ArchivedDrillError(f"Drill {drill.id} is archived")
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
