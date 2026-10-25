from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth import CurrentUser, User
from app.database import DbSession
from app.models import ArchivedDrillError, InvalidSessionTimesError, OtherTeamDrillError, SessionPlan, Team
from app.routers.drills import get_drill_or_404
from app.routers.teams import get_team_or_404
from app.schemas import (
    SessionDrillsUpdate,
    SessionPlanCreate,
    SessionPlanRead,
    SessionPlanSummary,
    SessionPlanUpdate,
)

router = APIRouter(prefix="/session-plans", tags=["session plans"])


def get_plan_or_404(db: DbSession, plan_id: int, user: User) -> SessionPlan:
    plan = db.get(SessionPlan, plan_id)
    # A plan is yours if its team is yours. Someone else's plan gets the same 404 as a missing one.
    if plan is None or plan.team.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Session plan {plan_id} not found")
    return plan


def check_times_or_422(db: DbSession, plan: SessionPlan) -> None:
    try:
        plan.check_times()
    except InvalidSessionTimesError as error:
        db.rollback()  # throw away the unsaved changes
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error))


@router.post("", status_code=status.HTTP_201_CREATED)
def create_plan(data: SessionPlanCreate, db: DbSession, user: CurrentUser) -> SessionPlanRead:
    get_team_or_404(db, data.team_id, user)  # Can only add plans to your own teams.
    plan = SessionPlan(**data.model_dump())
    check_times_or_422(db, plan)
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return SessionPlanRead.model_validate(plan)


@router.get("")
def list_plans(db: DbSession, user: CurrentUser, team_id: int | None = None) -> list[SessionPlanSummary]:
    # Only plans whose team belongs to this user. The join lets the database do that filtering.
    query = (
        select(SessionPlan)
        .join(SessionPlan.team)
        .where(Team.owner_id == user.id)
        # Load every plan's slots and team in extra queries, instead of one per plan (the "N+1" problem).
        .options(selectinload(SessionPlan.slots), selectinload(SessionPlan.team))
        .order_by(SessionPlan.date, SessionPlan.start_time)
    )
    if team_id is not None:
        query = query.where(SessionPlan.team_id == team_id)
    return [SessionPlanSummary.model_validate(plan) for plan in db.scalars(query)]


@router.get("/{plan_id}")
def get_plan(plan_id: int, db: DbSession, user: CurrentUser) -> SessionPlanRead:
    return SessionPlanRead.model_validate(get_plan_or_404(db, plan_id, user))


@router.patch("/{plan_id}")
def update_plan(plan_id: int, data: SessionPlanUpdate, db: DbSession, user: CurrentUser) -> SessionPlanRead:
    plan = get_plan_or_404(db, plan_id, user)
    if data.team_id is not None:
        get_team_or_404(db, data.team_id, user)  # Can only move a plan to another of your own teams.
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(plan, field, value)
    # Check after merging, so changing only end_time is still compared to the saved start_time.
    check_times_or_422(db, plan)
    db.commit()
    return SessionPlanRead.model_validate(plan)


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_plan(plan_id: int, db: DbSession, user: CurrentUser) -> None:
    db.delete(get_plan_or_404(db, plan_id, user))
    db.commit()


@router.put("/{plan_id}/drills")
def set_plan_drills(plan_id: int, data: SessionDrillsUpdate, db: DbSession, user: CurrentUser) -> SessionPlanRead:
    plan = get_plan_or_404(db, plan_id, user)
    drills = [(get_drill_or_404(db, entry.drill_id, user), entry.minutes) for entry in data.drills]
    try:
        plan.set_drills(drills)
    except ArchivedDrillError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(error))
    except OtherTeamDrillError as error:
        # Each team has its own drills. Another team's drill looks missing, like someone else's.
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error))
    db.commit()
    return SessionPlanRead.model_validate(plan)
