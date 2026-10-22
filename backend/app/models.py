from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


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
