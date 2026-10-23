def preflight(client, origin):
    """What a browser sends before a cross-origin request, to ask if it's allowed."""
    return client.options(
        "/drills",
        headers={"Origin": origin, "Access-Control-Request-Method": "POST"},
    )


def test_frontend_origin_is_allowed(client):
    response = preflight(client, "http://localhost:5173")

    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"


def test_other_origins_are_not_allowed(client):
    response = preflight(client, "http://evil.example")

    assert "access-control-allow-origin" not in response.headers
