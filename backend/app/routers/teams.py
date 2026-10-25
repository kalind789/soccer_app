from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.orm import selectinload

from app.auth import CurrentUser, User
from app.database import DbSession
from app.models import (
    AGE_GROUPS,
    Drill,
    LastHeadCoachError,
    SessionDrill,
    SessionPlan,
    Team,
    TeamMember,
    TeamNotEmptyError,
    utcnow,
)
from app.schemas import (
    DrillCreate,
    DrillRead,
    DrillSuggestions,
    InviteLink,
    TeamCreate,
    TeamRead,
    TeamUpdate,
    UsedDrill,
)

router = APIRouter(prefix="/teams", tags=["teams"])


def get_team_or_404(db: DbSession, team_id: int, user: User) -> Team:
    """The one place that decides who may use a team (and so its plans and drills): its staff."""
    team = db.get(Team, team_id)
    # Not on staff gets the same 404 as a missing team, so ids don't reveal what exists.
    if team is None or team.member(user.id) is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, f"Team {team_id} not found")
    return team


def get_managed_team(db: DbSession, team_id: int, user: User) -> Team:
    """For changes only the head coach may make. Other coaches can see the team, so a 403 is honest."""
    team = get_team_or_404(db, team_id, user)
    if team.member(user.id).role != "head_coach":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the head coach can do that")
    return team


def team_read(team: Team, user: User) -> TeamRead:
    member = team.member(user.id)
    return TeamRead.model_validate(team).model_copy(update={"my_role": member.role if member else None})


@router.post("", status_code=status.HTTP_201_CREATED)
def create_team(data: TeamCreate, db: DbSession, user: CurrentUser) -> TeamRead:
    team = Team(**data.model_dump())
    team.add_member(user.id, user.name, user.email or "", role="head_coach")  # Whoever makes it runs it.
    db.add(team)
    db.commit()
    db.refresh(team)
    return team_read(team, user)


@router.get("")
def list_teams(db: DbSession, user: CurrentUser) -> list[TeamRead]:
    # Keep the name teammates see up to date with the login (it can change, e.g. a Google profile).
    db.execute(
        update(TeamMember).where(TeamMember.user_id == user.id).values(name=user.name, email=user.email or "")
    )
    db.commit()
    query = (
        select(Team)
        .join(TeamMember)
        .where(TeamMember.user_id == user.id)
        .options(selectinload(Team.plans), selectinload(Team.members))  # Two extra queries, not one per team.
        .order_by(Team.name)
    )
    return [team_read(team, user) for team in db.scalars(query)]


@router.get("/{team_id}")
def get_team(team_id: int, db: DbSession, user: CurrentUser) -> TeamRead:
    return team_read(get_team_or_404(db, team_id, user), user)


@router.patch("/{team_id}")
def update_team(team_id: int, data: TeamUpdate, db: DbSession, user: CurrentUser) -> TeamRead:
    team = get_managed_team(db, team_id, user)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(team, field, value)
    db.commit()
    return team_read(team, user)


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(team_id: int, db: DbSession, user: CurrentUser) -> None:
    team = get_managed_team(db, team_id, user)
    try:
        team.check_can_delete()
    except TeamNotEmptyError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error))
    db.delete(team)
    db.commit()


# --- Staff ---


@router.delete("/{team_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_member(team_id: int, user_id: UUID, db: DbSession, user: CurrentUser) -> None:
    """The head coach can remove anyone; any coach can remove themselves (leave the team)."""
    team = get_team_or_404(db, team_id, user)
    member = team.member(user_id)
    if member is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "That coach isn't on this team")
    if user_id != user.id and team.member(user.id).role != "head_coach":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Only the head coach can remove coaches")
    try:
        team.remove_member(member)
    except LastHeadCoachError as error:
        raise HTTPException(status.HTTP_409_CONFLICT, str(error))
    db.commit()


@router.get("/{team_id}/invite-link")
def get_invite_link(team_id: int, db: DbSession, user: CurrentUser) -> InviteLink | None:
    team = get_managed_team(db, team_id, user)
    if team.invite_token is None or team.invite_expires_at < utcnow():
        return None  # Off, or expired.
    return InviteLink(token=team.invite_token, expires_at=team.invite_expires_at)


@router.post("/{team_id}/invite-link")
def create_invite_link(team_id: int, db: DbSession, user: CurrentUser) -> InviteLink:
    """Make a new link. The old one, if any, stops working."""
    team = get_managed_team(db, team_id, user)
    team.new_invite(utcnow())
    db.commit()
    return InviteLink(token=team.invite_token, expires_at=team.invite_expires_at)


@router.delete("/{team_id}/invite-link", status_code=status.HTTP_204_NO_CONTENT)
def turn_off_invite_link(team_id: int, db: DbSession, user: CurrentUser) -> None:
    team = get_managed_team(db, team_id, user)
    team.turn_off_invite()
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
    # Ideas for the team's age group; without one, the fundamentals (ideas tagged for every age).
    # Only a few dozen ideas, so filter in Python.
    ideas = db.scalars(select(Drill).where(Drill.team_id.is_(None), Drill.archived.is_(False)).order_by(Drill.name))
    wanted = {team.age_group} if team.age_group else set(AGE_GROUPS)
    recommended = [d for d in ideas if wanted <= set(d.age_groups) and d.id not in used_ids]
    # Fundamentals (every age) first, then the rest by name. Eight is plenty for a short list.
    recommended.sort(key=lambda d: (not set(AGE_GROUPS) <= set(d.age_groups), d.name))
    recommended = recommended[:8]
    return DrillSuggestions(
        used_before=[UsedDrill(**DrillRead.model_validate(d).model_dump(), times_used=n) for d, n in used],
        recommended=[DrillRead.model_validate(d) for d in recommended],
    )
