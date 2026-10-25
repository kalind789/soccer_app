from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.auth import CurrentUser
from app.database import DbSession
from app.models import InvalidInviteError, Team, utcnow
from app.routers.teams import team_read
from app.schemas import InvitePreview, TeamRead

# Opening an invite link: /join/<token> in the app calls these.
router = APIRouter(prefix="/invites", tags=["teams"])


def get_invited_team(db: DbSession, token: str) -> Team:
    team = db.scalar(select(Team).where(Team.invite_token == token))
    try:
        if team is None:
            raise InvalidInviteError("This invite link isn't valid anymore")
        team.check_invite(token, utcnow())
    except InvalidInviteError as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error))
    return team


@router.get("/{token}")
def preview_invite(token: str, db: DbSession, user: CurrentUser) -> InvitePreview:
    team = get_invited_team(db, token)
    head_coach = next((m.name for m in team.members if m.role == "head_coach"), "")
    return InvitePreview(
        team_id=team.id,
        team_name=team.name,
        age_group=team.age_group,
        head_coach=head_coach,
        already_member=team.member(user.id) is not None,
    )


@router.post("/{token}/accept")
def accept_invite(token: str, db: DbSession, user: CurrentUser) -> TeamRead:
    team = get_invited_team(db, token)
    team.add_member(user.id, user.name, user.email or "")  # Joins as a coach.
    db.commit()
    return team_read(team, user)
