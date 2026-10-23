from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.database import DbSession
from app.models import ArchivedDrillError, InvalidSessionTimesError, SessionPlan
from app.routers.drills import get_drill_or_404
from app.schemas import (
    SessionDrillsUpdate,
    SessionPlanCreate,
    SessionPlanRead,
    SessionPlanSummary,
    SessionPlanUpdate,
)

router = APIRouter(prefix="/session-plans", tags=["session plans"])


def get_plan_or_404(db: DbSession, plan_id: int) -> SessionPlan:
    plan = db.get(SessionPlan, plan_id)
    if plan is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Session plan {plan_id} not found")
    return plan


def check_times_or_422(db: DbSession, plan: SessionPlan) -> None:
    try:
        plan.check_times()
    except InvalidSessionTimesError as error:
        db.rollback()  # throw away the unsaved changes
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_plan(data: SessionPlanCreate, db: DbSession) -> SessionPlanRead:
    plan = SessionPlan(**data.model_dump())
    check_times_or_422(db, plan)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return SessionPlanRead.model_validate(plan)


@router.get("")
def list_plans(db: DbSession) -> list[SessionPlanSummary]:
    query = select(SessionPlan).order_by(SessionPlan.date, SessionPlan.start_time)
    return [SessionPlanSummary.model_validate(plan) for plan in db.scalars(query)]


@router.get("/{plan_id}")
def get_plan(plan_id: int, db: DbSession) -> SessionPlanRead:
    return SessionPlanRead.model_validate(get_plan_or_404(db, plan_id))


@router.patch("/{plan_id}")
def update_plan(plan_id: int, data: SessionPlanUpdate, db: DbSession) -> SessionPlanRead:
    plan = get_plan_or_404(db, plan_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(plan, field, value)
    # Check after merging, so changing only end_time is still compared to the saved start_time.
    check_times_or_422(db, plan)
    db.commit()
    return SessionPlanRead.model_validate(plan)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: DbSession) -> None:
    db.delete(get_plan_or_404(db, plan_id))
    db.commit()


@router.put("/{plan_id}/drills")
def set_plan_drills(plan_id: int, data: SessionDrillsUpdate, db: DbSession) -> SessionPlanRead:
    plan = get_plan_or_404(db, plan_id)
    drills = [(get_drill_or_404(db, entry.drill_id), entry.minutes) for entry in data.drills]
    try:
        plan.set_drills(drills)
    except ArchivedDrillError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error))
    db.commit()
    return SessionPlanRead.model_validate(plan)
