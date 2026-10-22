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
