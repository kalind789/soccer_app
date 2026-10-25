PRESSING = {
    "title": "Pressing",
    "focus": "Win the ball back high",
    "location": "field 3",
    "date": "2026-11-03",
    "start_time": "18:00",
    "end_time": "19:30",
}


def create_team(client, name="U12 Eagles", season="2026"):
    return client.post("/teams", json={"name": name, "season": season}).json()


def create_plan(client, **overrides):
    """Make a plan. Without a team_id, it goes in a new team."""
    if "team_id" not in overrides:
        overrides["team_id"] = create_team(client)["id"]
    response = client.post("/session-plans", json={**PRESSING, **overrides})
    assert response.status_code == 201
    return response.json()


def test_create_plan(client):
    plan = create_plan(client)

    assert plan["id"] == 1
    assert plan["title"] == "Pressing"
    assert plan["start_time"] == "18:00:00"
    assert plan["notes"] == ""



def test_create_plan_saves_location(client):
    plan = create_plan(client, location="Field 3")

    assert plan["location"] == "Field 3"
    assert client.get(f"/session-plans/{plan['id']}").json()["location"] == "Field 3"


def test_location_defaults_to_empty(client):
    without_location = {key: value for key, value in PRESSING.items() if key != "location"}

    response = client.post("/session-plans", json={**without_location, "team_id": create_team(client)["id"]})

    assert response.status_code == 201
    assert response.json()["location"] == ""

def test_duration_is_calculated(client):
    plan = create_plan(client)

    assert plan["duration_minutes"] == 90


def test_create_rejects_end_before_start(client):
    response = client.post("/session-plans", json={**PRESSING, "end_time": "17:00"})

    assert response.status_code == 422


def test_create_rejects_end_equal_to_start(client):
    response = client.post("/session-plans", json={**PRESSING, "end_time": "18:00"})

    assert response.status_code == 422


def test_get_missing_plan_returns_404(client):
    assert client.get("/session-plans/999").status_code == 404


def test_list_plans_sorted_by_date_then_time(client):
    create_plan(client, title="Later", date="2026-11-10")
    create_plan(client, title="Evening", start_time="19:00", end_time="20:00")
    create_plan(client, title="Earlier")

    titles = [p["title"] for p in client.get("/session-plans").json()]

    assert titles == ["Earlier", "Evening", "Later"]


def test_update_plan(client):
    plan = create_plan(client)

    response = client.patch(f"/session-plans/{plan['id']}", json={"end_time": "20:00"})

    assert response.status_code == 200
    assert response.json()["duration_minutes"] == 120


def test_update_rejects_end_before_saved_start(client):
    plan = create_plan(client)

    response = client.patch(f"/session-plans/{plan['id']}", json={"end_time": "17:00"})

    assert response.status_code == 422
    assert client.get(f"/session-plans/{plan['id']}").json()["end_time"] == "19:30:00"


def test_delete_plan(client):
    plan = create_plan(client)

    response = client.delete(f"/session-plans/{plan['id']}")

    assert response.status_code == 204
    assert client.get(f"/session-plans/{plan['id']}").status_code == 404


def create_drill(client, name):
    return client.post("/drills", json={"name": name}).json()


def set_drills(client, plan_id, drill_ids, minutes=10):
    """Put these drills in the plan, each for `minutes`."""
    entries = [{"drill_id": drill_id, "minutes": minutes} for drill_id in drill_ids]
    return client.put(f"/session-plans/{plan_id}/drills", json={"drills": entries})


def drill_names(plan):
    return [slot["drill"]["name"] for slot in plan["slots"]]


def test_new_plan_has_no_drills(client):
    assert create_plan(client)["slots"] == []


def test_set_drills_keeps_order(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    shooting = create_drill(client, "Shooting")

    response = set_drills(client, plan["id"], [shooting["id"], rondo["id"]])

    assert response.status_code == 200
    assert drill_names(response.json()) == ["Shooting", "Rondo"]
    saved = client.get(f"/session-plans/{plan['id']}").json()
    assert drill_names(saved) == ["Shooting", "Rondo"]


def test_set_drills_replaces_previous_list(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    shooting = create_drill(client, "Shooting")
    set_drills(client, plan["id"], [rondo["id"], shooting["id"]])

    response = set_drills(client, plan["id"], [shooting["id"]])

    assert drill_names(response.json()) == ["Shooting"]


def test_set_drills_allows_repeats(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    shooting = create_drill(client, "Shooting")

    response = set_drills(client, plan["id"], [rondo["id"], shooting["id"], rondo["id"]])

    assert drill_names(response.json()) == ["Rondo", "Shooting", "Rondo"]


def test_set_drills_unknown_drill_returns_404(client):
    plan = create_plan(client)

    assert set_drills(client, plan["id"], [999]).status_code == 404


def test_set_drills_rejects_newly_added_archived_drill(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    client.post(f"/drills/{rondo['id']}/archive")

    response = set_drills(client, plan["id"], [rondo["id"]])

    assert response.status_code == 422


def test_archived_drill_already_in_plan_can_stay(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    shooting = create_drill(client, "Shooting")
    set_drills(client, plan["id"], [rondo["id"]])
    client.post(f"/drills/{rondo['id']}/archive")

    response = set_drills(client, plan["id"], [rondo["id"], shooting["id"]])

    assert response.status_code == 200
    assert response.json()["slots"][0]["drill"]["archived"] is True


def test_editing_a_drill_shows_up_in_plans(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    set_drills(client, plan["id"], [rondo["id"]])

    client.patch(f"/drills/{rondo['id']}", json={"name": "Rondo 5v2"})

    saved = client.get(f"/session-plans/{plan['id']}").json()
    assert saved["slots"][0]["drill"]["name"] == "Rondo 5v2"


def test_deleting_plan_keeps_its_drills(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    set_drills(client, plan["id"], [rondo["id"]])

    client.delete(f"/session-plans/{plan['id']}")

    assert client.get(f"/drills/{rondo['id']}").status_code == 200


def test_each_slot_has_its_own_minutes(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    shooting = create_drill(client, "Shooting")
    entries = [{"drill_id": rondo["id"], "minutes": 15}, {"drill_id": shooting["id"], "minutes": 25}]

    response = client.put(f"/session-plans/{plan['id']}/drills", json={"drills": entries})

    assert [slot["minutes"] for slot in response.json()["slots"]] == [15, 25]
    assert response.json()["planned_minutes"] == 40


def test_same_drill_can_run_different_times_in_different_plans(client):
    monday = create_plan(client, title="Monday")
    thursday = create_plan(client, title="Thursday")
    rondo = create_drill(client, "Rondo 4v2")

    set_drills(client, monday["id"], [rondo["id"]], minutes=15)
    set_drills(client, thursday["id"], [rondo["id"]], minutes=20)

    assert client.get(f"/session-plans/{monday['id']}").json()["slots"][0]["minutes"] == 15
    assert client.get(f"/session-plans/{thursday['id']}").json()["slots"][0]["minutes"] == 20


def test_planned_minutes_can_be_more_than_the_session(client):
    plan = create_plan(client)  # 90 minutes long
    rondo = create_drill(client, "Rondo")

    response = set_drills(client, plan["id"], [rondo["id"]], minutes=120)

    assert response.status_code == 200
    assert response.json()["planned_minutes"] == 120


def test_minutes_must_be_positive(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")

    assert set_drills(client, plan["id"], [rondo["id"]], minutes=0).status_code == 422


def test_plan_list_shows_progress(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    set_drills(client, plan["id"], [rondo["id"], rondo["id"]], minutes=15)

    [summary] = client.get("/session-plans").json()

    assert summary["drill_count"] == 2
    assert summary["planned_minutes"] == 30
