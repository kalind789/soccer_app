from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.auth import CurrentUser, User
from app.database import DbSession
from app.models import Drill
from app.schemas import DrillCreate, DrillRead, DrillUpdate

router = APIRouter(prefix="/drills", tags=["drills"])


def get_drill_or_404(db: DbSession, drill_id: int, user: User) -> Drill:
    drill = db.get(Drill, drill_id)
    # Someone else's drill gets the same 404 as a missing one, so ids don't reveal what exists.
    if drill is None or drill.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Drill {drill_id} not found")
    return drill


@router.post("", status_code=status.HTTP_201_CREATED)
def create_drill(data: DrillCreate, db: DbSession, user: CurrentUser) -> DrillRead:
    drill = Drill(**data.model_dump(), owner_id=user.id)
    db.add(drill)
    db.commit()
    db.refresh(drill)
    return DrillRead.model_validate(drill)


@router.get("")
def list_drills(
    db: DbSession, user: CurrentUser, include_archived: bool = False, search: str | None = None
) -> list[DrillRead]:
    query = select(Drill).where(Drill.owner_id == user.id).order_by(Drill.name)
    if not include_archived:
        query = query.where(Drill.archived.is_(False))
    if search is not None:
        query = query.where(Drill.name.ilike(f"%{search}%"))
    return [DrillRead.model_validate(drill) for drill in db.scalars(query)]

@router.get("/{drill_id}")
def get_drill(drill_id: int, db: DbSession, user: CurrentUser) -> DrillRead:
    return DrillRead.model_validate(get_drill_or_404(db, drill_id, user))


@router.patch("/{drill_id}")
def update_drill(drill_id: int, data: DrillUpdate, db: DbSession, user: CurrentUser) -> DrillRead:
    drill = get_drill_or_404(db, drill_id, user)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(drill, field, value)
    db.commit()
    return DrillRead.model_validate(drill)


@router.post("/{drill_id}/archive")
def archive_drill(drill_id: int, db: DbSession, user: CurrentUser) -> DrillRead:
    drill = get_drill_or_404(db, drill_id, user)
    drill.archive()
    db.commit()
    return DrillRead.model_validate(drill)


@router.post("/{drill_id}/unarchive")
def unarchive_drill(drill_id: int, db: DbSession, user: CurrentUser) -> DrillRead:
    drill = get_drill_or_404(db, drill_id, user)
    drill.unarchive()
    db.commit()
    return DrillRead.model_validate(drill)
