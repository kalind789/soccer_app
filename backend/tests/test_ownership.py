"""Authorization: a team's plans and drills are only for its coach. Drill ideas are for everyone."""

from conftest import BOB

PLAN = {"title": "Pressing", "date": "2026-11-03", "start_time": "18:00", "end_time": "19:30"}


def create_plan(client):
    team = client.post("/teams", json={"name": "U12 Eagles"}).json()
    return client.post("/session-plans", json={**PLAN, "team_id": team["id"]}).json()


def test_someone_elses_team_drills_look_missing(client, login_as):
    team = client.post("/teams", json={"name": "U12 Eagles"}).json()
    drill = client.post(f"/teams/{team['id']}/drills", json={"name": "Alice's rondo"}).json()
    login_as(BOB)

    assert client.get(f"/teams/{team['id']}/drills").status_code == 404
    assert client.post(f"/teams/{team['id']}/drills", json={"name": "Sneaky"}).status_code == 404
    assert client.get(f"/teams/{team['id']}/drill-suggestions").status_code == 404
    assert client.get(f"/drills/{drill['id']}").status_code == 404
    assert client.patch(f"/drills/{drill['id']}", json={"name": "Hacked"}).status_code == 404
    assert client.post(f"/drills/{drill['id']}/archive").status_code == 404


def test_plan_lists_only_show_your_own(client, login_as):
    create_plan(client)
    login_as(BOB)

    assert client.get("/session-plans").json() == []


def test_someone_elses_plan_looks_missing(client, login_as):
    plan = create_plan(client)
    login_as(BOB)

    assert client.get(f"/session-plans/{plan['id']}").status_code == 404
    assert client.patch(f"/session-plans/{plan['id']}", json={"title": "Hacked"}).status_code == 404
    assert client.put(f"/session-plans/{plan['id']}/drills", json={"drills": []}).status_code == 404
    assert client.delete(f"/session-plans/{plan['id']}").status_code == 404


def test_cant_put_someone_elses_drill_in_your_plan(client, login_as):
    team = client.post("/teams", json={"name": "U12 Eagles"}).json()
    alices_drill = client.post(f"/teams/{team['id']}/drills", json={"name": "Alice's rondo"}).json()
    login_as(BOB)
    bobs_plan = create_plan(client)

    response = client.put(
        f"/session-plans/{bobs_plan['id']}/drills",
        json={"drills": [{"drill_id": alices_drill["id"], "minutes": 15}]},
    )

    assert response.status_code == 404
