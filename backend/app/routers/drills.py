from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.auth import CurrentUser, User
from app.database import DbSession
from app.models import Drill
from app.schemas import DrillRead, DrillUpdate

# Creating and listing a team's drills lives in teams.py (/teams/{id}/drills).
router = APIRouter(prefix="/drills", tags=["drills"])
ideas_router = APIRouter(prefix="/drill-ideas", tags=["drills"])


def get_drill_or_404(db: DbSession, drill_id: int, user: User) -> Drill:
    """A drill idea, or a drill from a team the user coaches."""
    drill = db.get(Drill, drill_id)
    # Another team's drill gets the same 404 as a missing one, so ids don't reveal what exists.
    if drill is None or (drill.team is not None and drill.team.member(user.id) is None):
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Drill {drill_id} not found")
    return drill


def get_editable_drill(db: DbSession, drill_id: int, user: User) -> Drill:
    drill = get_drill_or_404(db, drill_id, user)
    if drill.is_idea:
        # Everyone can see ideas, so a 403 (not allowed) is honest here, unlike a 404.
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Drill ideas can't be changed")
    return drill


@ideas_router.get("")
def list_drill_ideas(db: DbSession, user: CurrentUser) -> list[DrillRead]:
    query = select(Drill).where(Drill.team_id.is_(None), Drill.archived.is_(False)).order_by(Drill.name)
    return [DrillRead.model_validate(drill) for drill in db.scalars(query)]


@router.get("/{drill_id}")
def get_drill(drill_id: int, db: DbSession, user: CurrentUser) -> DrillRead:
    return DrillRead.model_validate(get_drill_or_404(db, drill_id, user))


@router.patch("/{drill_id}")
def update_drill(drill_id: int, data: DrillUpdate, db: DbSession, user: CurrentUser) -> DrillRead:
    drill = get_editable_drill(db, drill_id, user)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(drill, field, value)
    db.commit()
    return DrillRead.model_validate(drill)


@router.post("/{drill_id}/archive")
def archive_drill(drill_id: int, db: DbSession, user: CurrentUser) -> DrillRead:
    drill = get_editable_drill(db, drill_id, user)
    drill.archive()
    db.commit()
    return DrillRead.model_validate(drill)


@router.post("/{drill_id}/unarchive")
def unarchive_drill(drill_id: int, db: DbSession, user: CurrentUser) -> DrillRead:
    drill = get_editable_drill(db, drill_id, user)
    drill.unarchive()
    db.commit()
    return DrillRead.model_validate(drill)
