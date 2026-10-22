RONDO = {"name": "Rondo 5v2", "description": "Keep-away in a grid", "objective": "Quick passing"}


def create_drill(client, **overrides):
    response = client.post("/drills", json={**RONDO, **overrides})
    assert response.status_code == 201
    return response.json()


def test_create_drill(client):
    drill = create_drill(client)

    assert drill["id"] == 1
    assert drill["name"] == "Rondo 5v2"
    assert drill["archived"] is False


def test_create_drill_only_name_required(client):
    response = client.post("/drills", json={"name": "Shooting"})

    assert response.status_code == 201
    assert response.json()["description"] == ""


def test_create_drill_rejects_empty_name(client):
    response = client.post("/drills", json={"name": ""})

    assert response.status_code == 422


def test_get_drill(client):
    drill = create_drill(client)

    response = client.get(f"/drills/{drill['id']}")

    assert response.status_code == 200
    assert response.json() == drill


def test_get_missing_drill_returns_404(client):
    response = client.get("/drills/999")

    assert response.status_code == 404


def test_list_drills_sorted_by_name(client):
    create_drill(client, name="Shooting")
    create_drill(client, name="Passing")

    names = [d["name"] for d in client.get("/drills").json()]

    assert names == ["Passing", "Shooting"]


def test_update_drill_changes_only_sent_fields(client):
    drill = create_drill(client)

    response = client.patch(f"/drills/{drill['id']}", json={"objective": "One-touch passing"})

    assert response.status_code == 200
    assert response.json()["objective"] == "One-touch passing"
    assert response.json()["name"] == "Rondo 5v2"


def test_archived_drill_hidden_from_list_by_default(client):
    drill = create_drill(client)

    client.post(f"/drills/{drill['id']}/archive")

    assert client.get("/drills").json() == []
    assert len(client.get("/drills", params={"include_archived": True}).json()) == 1


def test_unarchive_drill(client):
    drill = create_drill(client)
    client.post(f"/drills/{drill['id']}/archive")

    response = client.post(f"/drills/{drill['id']}/unarchive")

    assert response.json()["archived"] is False
    assert len(client.get("/drills").json()) == 1
