from conftest import ALICE, BOB

PLAN = {"title": "Pressing", "date": "2026-11-03", "start_time": "18:00", "end_time": "19:30"}


def create_team(client, name="U12 Eagles"):
    response = client.post("/teams", json={"name": name})
    assert response.status_code == 201
    return response.json()


def create_plan(client, team_id, title="Pressing"):
    return client.post("/session-plans", json={**PLAN, "title": title, "team_id": team_id}).json()


def test_create_team(client):
    team = create_team(client)

    assert team["name"] == "U12 Eagles"
    assert team["plan_count"] == 0


def test_team_needs_a_name(client):
    assert client.post("/teams", json={"name": ""}).status_code == 422
    assert client.post("/teams", json={}).status_code == 422


def test_a_coach_can_run_several_teams_sorted_by_name(client):
    create_team(client, "U12 Eagles 2026")
    create_team(client, "U10 Hawks")
    create_team(client, "U12 Eagles 2027")

    teams = client.get("/teams").json()

    assert [t["name"] for t in teams] == ["U10 Hawks", "U12 Eagles 2026", "U12 Eagles 2027"]


def test_a_new_team_starts_empty_even_with_the_same_name(client):
    last_year = create_team(client, "U12 Eagles")
    create_plan(client, last_year["id"])

    this_year = create_team(client, "U12 Eagles")

    assert this_year["id"] != last_year["id"]
    assert this_year["plan_count"] == 0


def test_rename_team(client):
    team = create_team(client)

    response = client.patch(f"/teams/{team['id']}", json={"name": "U12 Eagles Blue"})

    assert response.json()["name"] == "U12 Eagles Blue"


def test_delete_empty_team(client):
    team = create_team(client)

    assert client.delete(f"/teams/{team['id']}").status_code == 204
    assert client.get(f"/teams/{team['id']}").status_code == 404


def test_cant_delete_a_team_with_plans(client):
    team = create_team(client)
    create_plan(client, team["id"])

    response = client.delete(f"/teams/{team['id']}")

    assert response.status_code == 409
    assert client.get(f"/teams/{team['id']}").status_code == 200


def test_someone_elses_team_looks_missing(client, login_as):
    team = create_team(client)
    login_as(BOB)

    assert client.get("/teams").json() == []
    assert client.get(f"/teams/{team['id']}").status_code == 404
    assert client.patch(f"/teams/{team['id']}", json={"name": "Hacked"}).status_code == 404
    assert client.delete(f"/teams/{team['id']}").status_code == 404


def test_plan_needs_a_team(client):
    assert client.post("/session-plans", json=PLAN).status_code == 422


def test_cant_add_a_plan_to_someone_elses_team(client, login_as):
    alices = create_team(client)
    login_as(BOB)

    response = client.post("/session-plans", json={**PLAN, "team_id": alices["id"]})

    assert response.status_code == 404


def test_plans_show_their_team(client):
    team = create_team(client, "U12 Eagles")
    plan = create_plan(client, team["id"])

    assert plan["team"] == {"id": team["id"], "name": "U12 Eagles"}
    assert client.get("/session-plans").json()[0]["team"]["name"] == "U12 Eagles"


def test_list_plans_for_one_team(client):
    eagles = create_team(client, "U12 Eagles")
    hawks = create_team(client, "U10 Hawks")
    create_plan(client, eagles["id"], "Eagles session")
    create_plan(client, hawks["id"], "Hawks session")

    plans = client.get("/session-plans", params={"team_id": hawks["id"]}).json()

    assert [p["title"] for p in plans] == ["Hawks session"]


def test_move_a_plan_to_another_team(client):
    eagles = create_team(client, "U12 Eagles")
    hawks = create_team(client, "U10 Hawks")
    plan = create_plan(client, eagles["id"])

    response = client.patch(f"/session-plans/{plan['id']}", json={"team_id": hawks["id"]})

    assert response.json()["team"]["name"] == "U10 Hawks"


def test_cant_move_a_plan_to_someone_elses_team(client, login_as):
    login_as(BOB)
    bobs_team = create_team(client)
    login_as(ALICE)
    plan = create_plan(client, create_team(client)["id"])

    response = client.patch(f"/session-plans/{plan['id']}", json={"team_id": bobs_team["id"]})

    assert response.status_code == 404


def test_deleting_a_team_deletes_its_drills(client):
    team = create_team(client)
    drill = client.post(f"/teams/{team['id']}/drills", json={"name": "Rondo"}).json()

    client.delete(f"/teams/{team['id']}")

    assert client.get(f"/drills/{drill['id']}").status_code == 404
