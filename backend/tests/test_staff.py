"""Several coaches per team: invite links, roles, and the staff list."""

import datetime as dt

from conftest import ALICE, BOB, CARLA

from app.auth import User, display_name
from app.models import Team

PLAN = {"title": "Pressing", "date": "2026-11-03", "start_time": "18:00", "end_time": "19:30"}


def create_team(client):
    return client.post("/teams", json={"name": "U12 Eagles", "age_group": "u11-u12"}).json()


def invite(client, team):
    response = client.post(f"/teams/{team['id']}/invite-link")
    assert response.status_code == 200
    return response.json()["token"]


def join_as(client, login_as, user, token):
    login_as(user)
    return client.post(f"/invites/{token}/accept")


def staff(team):
    return [(m["name"], m["role"]) for m in team["members"]]


def test_whoever_makes_a_team_is_its_head_coach(client):
    team = create_team(client)

    assert staff(team) == [("Alice Smith", "head_coach")]
    assert team["members"][0]["email"] == "alice@example.com"
    assert team["my_role"] == "head_coach"


def test_join_with_an_invite_link(client, login_as):
    team = create_team(client)
    token = invite(client, team)
    login_as(BOB)

    preview = client.get(f"/invites/{token}").json()
    joined = client.post(f"/invites/{token}/accept").json()

    assert preview == {
        "team_id": team["id"],
        "team_name": "U12 Eagles",
        "age_group": "u11-u12",
        "head_coach": "Alice Smith",
        "already_member": False,
    }
    assert joined["my_role"] == "coach"
    assert staff(joined) == [("Alice Smith", "head_coach"), ("Bob Jones", "coach")]
    assert [t["name"] for t in client.get("/teams").json()] == ["U12 Eagles"]


def test_coaches_share_the_teams_plans_and_drills(client, login_as):
    team = create_team(client)
    plan = client.post("/session-plans", json={**PLAN, "team_id": team["id"]}).json()
    drill = client.post(f"/teams/{team['id']}/drills", json={"name": "Rondo"}).json()
    join_as(client, login_as, BOB, invite(client, team))

    assert client.get(f"/session-plans/{plan['id']}").status_code == 200
    assert client.patch(f"/drills/{drill['id']}", json={"name": "Rondo 5v2"}).status_code == 200
    assert client.post("/session-plans", json={**PLAN, "team_id": team["id"]}).status_code == 201
    login_as(ALICE)
    assert len(client.get("/session-plans").json()) == 2  # Alice sees the plan Bob made.


def test_joining_twice_changes_nothing(client, login_as):
    team = create_team(client)
    token = invite(client, team)

    join_as(client, login_as, BOB, token)
    again = client.post(f"/invites/{token}/accept").json()
    login_as(ALICE)
    own_link = client.post(f"/invites/{token}/accept").json()

    assert staff(again) == [("Alice Smith", "head_coach"), ("Bob Jones", "coach")]
    assert own_link["my_role"] == "head_coach"  # Still in charge.


def test_a_wrong_link_is_404(client, login_as):
    login_as(BOB)

    assert client.get("/invites/not-a-real-token").status_code == 404
    assert client.post("/invites/not-a-real-token/accept").status_code == 404


def test_an_expired_link_is_404(client, login_as, TestingSession):
    team = create_team(client)
    token = invite(client, team)
    with TestingSession() as db:
        db.get(Team, team["id"]).invite_expires_at = dt.datetime(2020, 1, 1)
        db.commit()

    response = join_as(client, login_as, BOB, token)

    assert response.status_code == 404
    assert "expired" in response.json()["detail"]


def test_a_new_link_replaces_the_old_one(client, login_as):
    team = create_team(client)
    old = invite(client, team)
    new = invite(client, team)

    assert join_as(client, login_as, BOB, old).status_code == 404
    assert join_as(client, login_as, BOB, new).status_code == 200


def test_turning_the_link_off(client, login_as):
    team = create_team(client)
    token = invite(client, team)

    assert client.delete(f"/teams/{team['id']}/invite-link").status_code == 204
    assert client.get(f"/teams/{team['id']}/invite-link").json() is None
    assert join_as(client, login_as, BOB, token).status_code == 404


def test_only_the_head_coach_manages_the_team(client, login_as):
    team = create_team(client)
    join_as(client, login_as, BOB, invite(client, team))
    login_as(ALICE)
    join_as(client, login_as, CARLA, invite(client, team))
    login_as(BOB)

    assert client.patch(f"/teams/{team['id']}", json={"name": "Bob's team"}).status_code == 403
    assert client.delete(f"/teams/{team['id']}").status_code == 403
    assert client.get(f"/teams/{team['id']}/invite-link").status_code == 403
    assert client.post(f"/teams/{team['id']}/invite-link").status_code == 403
    assert client.delete(f"/teams/{team['id']}/members/{CARLA.id}").status_code == 403


def test_outsiders_cant_see_the_invite_link(client, login_as):
    team = create_team(client)
    invite(client, team)
    login_as(BOB)

    assert client.get(f"/teams/{team['id']}/invite-link").status_code == 404


def test_head_coach_can_remove_a_coach(client, login_as):
    team = create_team(client)
    join_as(client, login_as, BOB, invite(client, team))
    login_as(ALICE)

    assert client.delete(f"/teams/{team['id']}/members/{BOB.id}").status_code == 204
    login_as(BOB)
    assert client.get(f"/teams/{team['id']}").status_code == 404


def test_a_coach_can_leave(client, login_as):
    team = create_team(client)
    join_as(client, login_as, BOB, invite(client, team))

    assert client.delete(f"/teams/{team['id']}/members/{BOB.id}").status_code == 204
    assert client.get("/teams").json() == []


def test_the_head_coach_cant_leave(client):
    team = create_team(client)

    response = client.delete(f"/teams/{team['id']}/members/{ALICE.id}")

    assert response.status_code == 409


def test_staff_names_follow_the_login(client, login_as):
    team = create_team(client)
    login_as(User(id=ALICE.id, email="alice@example.com", name="Coach Alice"))

    [listed] = client.get("/teams").json()

    assert staff(listed) == [("Coach Alice", "head_coach")]
    assert listed["id"] == team["id"]


def test_display_name_comes_from_the_login():
    assert display_name({"user_metadata": {"full_name": "Alice Smith"}, "email": "a@x.com"}) == "Alice Smith"
    assert display_name({"user_metadata": {"name": "Bob"}, "email": "b@x.com"}) == "Bob"
    assert display_name({"user_metadata": {}, "email": "carla.diaz@x.com"}) == "carla.diaz"  # No name given.
