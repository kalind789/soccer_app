from conftest import ALICE, BOB

PLAN = {"title": "Pressing", "date": "2026-11-03", "start_time": "18:00", "end_time": "19:30"}


def create_team(client, name="U12 Eagles", season="2026", **extra):
    response = client.post("/teams", json={"name": name, "season": season, **extra})
    assert response.status_code == 201
    return response.json()


def create_plan(client, team_id, title="Pressing"):
    return client.post("/session-plans", json={**PLAN, "title": title, "team_id": team_id}).json()


def test_create_team(client):
    team = create_team(client)

    assert team["name"] == "U12 Eagles"
    assert team["season"] == "2026"
    assert team["previous_team_id"] is None
    assert team["plan_count"] == 0


def test_team_needs_a_name_and_season(client):
    assert client.post("/teams", json={"name": "", "season": "2026"}).status_code == 422
    assert client.post("/teams", json={"name": "U12 Eagles"}).status_code == 422


def test_a_coach_can_run_several_teams_newest_season_first(client):
    create_team(client, "U12 Eagles", "2026")
    create_team(client, "U10 Hawks", "2027")
    create_team(client, "U14 Owls", "2027")

    teams = client.get("/teams").json()

    assert [(t["name"], t["season"]) for t in teams] == [("U10 Hawks", "2027"), ("U14 Owls", "2027"), ("U12 Eagles", "2026")]


def test_next_season_is_a_new_team_linked_to_last_year(client):
    this_year = create_team(client, "U12 Eagles", "2026")
    create_plan(client, this_year["id"])

    next_year = create_team(client, "U12 Eagles", "2027", previous_team_id=this_year["id"])

    assert next_year["previous_team_id"] == this_year["id"]
    assert next_year["plan_count"] == 0  # A fresh start: last year's plans stay with last year's team.
    assert client.get(f"/teams/{this_year['id']}").json()["plan_count"] == 1


def test_cant_continue_someone_elses_team(client, login_as):
    alices = create_team(client)
    login_as(BOB)

    response = client.post("/teams", json={"name": "Mine now", "season": "2027", "previous_team_id": alices["id"]})

    assert response.status_code == 404


def test_rename_team(client):
    team = create_team(client)

    response = client.patch(f"/teams/{team['id']}", json={"name": "U12 Eagles Blue"})

    assert response.json()["name"] == "U12 Eagles Blue"
    assert response.json()["season"] == "2026"


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


def test_deleting_last_years_team_unlinks_next_year(client):
    this_year = create_team(client, season="2026")
    next_year = create_team(client, season="2027", previous_team_id=this_year["id"])

    client.delete(f"/teams/{this_year['id']}")

    assert client.get(f"/teams/{next_year['id']}").json()["previous_team_id"] is None


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
    team = create_team(client, "U12 Eagles", "2026")
    plan = create_plan(client, team["id"])

    assert plan["team"] == {"id": team["id"], "name": "U12 Eagles", "season": "2026"}
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
