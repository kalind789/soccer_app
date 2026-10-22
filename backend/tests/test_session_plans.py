PRESSING = {
    "title": "Pressing",
    "focus": "Win the ball back high",
    "date": "2026-11-03",
    "start_time": "18:00",
    "end_time": "19:30",
}


def create_plan(client, **overrides):
    response = client.post("/session-plans", json={**PRESSING, **overrides})
    assert response.status_code == 201
    return response.json()


def test_create_plan(client):
    plan = create_plan(client)

    assert plan["id"] == 1
    assert plan["title"] == "Pressing"
    assert plan["start_time"] == "18:00:00"
    assert plan["notes"] == ""


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


def set_drills(client, plan_id, drill_ids):
    return client.put(f"/session-plans/{plan_id}/drills", json={"drill_ids": drill_ids})


def test_new_plan_has_no_drills(client):
    assert create_plan(client)["drills"] == []


def test_set_drills_keeps_order(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    shooting = create_drill(client, "Shooting")

    response = set_drills(client, plan["id"], [shooting["id"], rondo["id"]])

    assert response.status_code == 200
    assert [d["name"] for d in response.json()["drills"]] == ["Shooting", "Rondo"]
    saved = client.get(f"/session-plans/{plan['id']}").json()
    assert [d["name"] for d in saved["drills"]] == ["Shooting", "Rondo"]


def test_set_drills_replaces_previous_list(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    shooting = create_drill(client, "Shooting")
    set_drills(client, plan["id"], [rondo["id"], shooting["id"]])

    response = set_drills(client, plan["id"], [shooting["id"]])

    assert [d["name"] for d in response.json()["drills"]] == ["Shooting"]


def test_set_drills_allows_repeats(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    shooting = create_drill(client, "Shooting")

    response = set_drills(client, plan["id"], [rondo["id"], shooting["id"], rondo["id"]])

    assert [d["name"] for d in response.json()["drills"]] == ["Rondo", "Shooting", "Rondo"]


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
    assert response.json()["drills"][0]["archived"] is True


def test_editing_a_drill_shows_up_in_plans(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    set_drills(client, plan["id"], [rondo["id"]])

    client.patch(f"/drills/{rondo['id']}", json={"name": "Rondo 5v2"})

    saved = client.get(f"/session-plans/{plan['id']}").json()
    assert saved["drills"][0]["name"] == "Rondo 5v2"


def test_deleting_plan_keeps_its_drills(client):
    plan = create_plan(client)
    rondo = create_drill(client, "Rondo")
    set_drills(client, plan["id"], [rondo["id"]])

    client.delete(f"/session-plans/{plan['id']}")

    assert client.get(f"/drills/{rondo['id']}").status_code == 200
