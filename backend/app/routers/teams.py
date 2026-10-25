from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.auth import CurrentUser, User
from app.database import DbSession
from app.models import AGE_GROUPS, Drill, SessionDrill, SessionPlan, Team, TeamNotEmptyError
from app.schemas import DrillCreate, DrillRead, DrillSuggestions, TeamCreate, TeamRead, TeamUpdate, UsedDrill

router = APIRouter(prefix="/teams", tags=["teams"])


def get_team_or_404(db: DbSession, team_id: int, user: User) -> Team:
    """The one place that decides who may use a team (and so its session plans)."""
    team = db.get(Team, team_id)
    # Someone else's team gets the same 404 as a missing one, so ids don't reveal what exists.
    if team is None or team.owner_id != user.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Team {team_id} not found")
    return team


@router.post("", status_code=status.HTTP_201_CREATED)
def create_team(data: TeamCreate, db: DbSession, user: CurrentUser) -> TeamRead:
    team = Team(**data.model_dump(), owner_id=user.id)
    db.add(team)
    db.commit()
    db.refresh(team)
    return TeamRead.model_validate(team)


@router.get("")
def list_teams(db: DbSession, user: CurrentUser) -> list[TeamRead]:
    query = (
        select(Team)
        .where(Team.owner_id == user.id)
        .options(selectinload(Team.plans))  # For plan_count, in one extra query.
        .order_by(Team.name)
    )
    return [TeamRead.model_validate(team) for team in db.scalars(query)]


@router.get("/{team_id}")
def get_team(team_id: int, db: DbSession, user: CurrentUser) -> TeamRead:
    return TeamRead.model_validate(get_team_or_404(db, team_id, user))


@router.patch("/{team_id}")
def update_team(team_id: int, data: TeamUpdate, db: DbSession, user: CurrentUser) -> TeamRead:
    team = get_team_or_404(db, team_id, user)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(team, field, value)
    db.commit()
    return TeamRead.model_validate(team)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, db: DbSession, user: CurrentUser) -> None:
    team = get_team_or_404(db, team_id, user)
    try:
        team.check_can_delete()
    except TeamNotEmptyError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error))
    db.delete(team)
    db.commit()


# --- A team's drill library ---


@router.post("/{team_id}/drills", status_code=status.HTTP_201_CREATED)
def create_team_drill(team_id: int, data: DrillCreate, db: DbSession, user: CurrentUser) -> DrillRead:
    team = get_team_or_404(db, team_id, user)
    drill = Drill(**data.model_dump(), team=team)
    db.add(drill)
    db.commit()
    return DrillRead.model_validate(drill)


@router.get("/{team_id}/drills")
def list_team_drills(
    team_id: int, db: DbSession, user: CurrentUser, include_archived: bool = False, search: str | None = None
) -> list[DrillRead]:
    team = get_team_or_404(db, team_id, user)
    query = select(Drill).where(Drill.team_id == team.id).order_by(Drill.name)
    if not include_archived:
        query = query.where(Drill.archived.is_(False))
    if search is not None:
        query = query.where(Drill.name.ilike(f"%{search}%"))
    return [DrillRead.model_validate(drill) for drill in db.scalars(query)]


@router.get("/{team_id}/drill-suggestions")
def suggest_drills(team_id: int, db: DbSession, user: CurrentUser) -> DrillSuggestions:
    team = get_team_or_404(db, team_id, user)
    # How often each drill (the team's own, or an idea) appears in this team's plans, most used first.
    times_used = func.count(SessionDrill.id).label("times_used")
    used = db.execute(
        select(Drill, times_used)
        .join(SessionDrill, SessionDrill.drill_id == Drill.id)
        .join(SessionPlan, SessionPlan.id == SessionDrill.session_plan_id)
        .where(SessionPlan.team_id == team.id, Drill.archived.is_(False))
        .group_by(Drill.id)
        .order_by(times_used.desc(), Drill.name)
        .limit(10)
    ).all()
    used_ids = {drill.id for drill, _ in used}
    # "Fundamental" = an idea tagged for every age group. Only a few dozen ideas, so filter in Python.
    ideas = db.scalars(select(Drill).where(Drill.team_id.is_(None), Drill.archived.is_(False)).order_by(Drill.name))
    recommended = [d for d in ideas if set(d.age_groups) == set(AGE_GROUPS) and d.id not in used_ids]
    return DrillSuggestions(
        used_before=[UsedDrill(**DrillRead.model_validate(d).model_dump(), times_used=n) for d, n in used],
        recommended=[DrillRead.model_validate(d) for d in recommended],
    )
