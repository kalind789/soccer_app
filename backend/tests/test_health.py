def test_health_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_version(client):
    response = client.get("/version")

    assert response.status_code == 200
    assert response.json() == {"version": "0.1.0"}
