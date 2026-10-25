from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.auth import CurrentUser, User
from app.database import DbSession
from app.models import Team, TeamNotEmptyError
from app.schemas import TeamCreate, TeamRead, TeamUpdate

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
