from conftest import BOB

from app.models import Team

RONDO = {"name": "Rondo 5v2", "description": "Keep-away in a grid", "objective": "Quick passing"}
ALL_AGES = ["u6-u8", "u9-u10", "u11-u12", "u13+"]


def create_team(client, name="U12 Eagles"):
    return client.post("/teams", json={"name": name, "age_group": "u11-u12"}).json()


def create_drill(client, team_id=None, **overrides):
    """A drill in this team's library (a new team if none is given)."""
    team_id = team_id or create_team(client)["id"]
    response = client.post(f"/teams/{team_id}/drills", json={**RONDO, **overrides})
    assert response.status_code == 201
    return response.json()


def team_drills(client, team_id, **params):
    return client.get(f"/teams/{team_id}/drills", params=params).json()


def test_create_drill(client):
    team = create_team(client)

    drill = create_drill(client, team["id"])

    assert drill["name"] == "Rondo 5v2"
    assert drill["team_id"] == team["id"]
    assert drill["archived"] is False
    assert drill["age_groups"] == [] and drill["goals"] == []


def test_create_drill_only_name_required(client):
    team = create_team(client)

    response = client.post(f"/teams/{team['id']}/drills", json={"name": "Shooting"})

    assert response.status_code == 201
    assert response.json()["description"] == ""


def test_create_drill_rejects_empty_name(client):
    team = create_team(client)

    assert client.post(f"/teams/{team['id']}/drills", json={"name": ""}).status_code == 422


def test_get_drill(client):
    drill = create_drill(client)

    response = client.get(f"/drills/{drill['id']}")

    assert response.status_code == 200
    assert response.json() == drill


def test_get_missing_drill_returns_404(client):
    assert client.get("/drills/999").status_code == 404


def test_list_drills_sorted_by_name(client):
    team = create_team(client)
    create_drill(client, team["id"], name="Shooting")
    create_drill(client, team["id"], name="Passing")

    assert [d["name"] for d in team_drills(client, team["id"])] == ["Passing", "Shooting"]


def test_each_team_has_its_own_drills(client):
    eagles = create_team(client, "U12 Eagles")
    hawks = create_team(client, "U10 Hawks")
    create_drill(client, eagles["id"], name="Eagles rondo")
    create_drill(client, hawks["id"], name="Hawks shooting")

    assert [d["name"] for d in team_drills(client, hawks["id"])] == ["Hawks shooting"]


def test_update_drill_changes_only_sent_fields(client):
    drill = create_drill(client)

    response = client.patch(f"/drills/{drill['id']}", json={"objective": "One-touch passing"})

    assert response.status_code == 200
    assert response.json()["objective"] == "One-touch passing"
    assert response.json()["name"] == "Rondo 5v2"


def test_archived_drill_hidden_from_list_by_default(client):
    drill = create_drill(client)

    client.post(f"/drills/{drill['id']}/archive")

    assert team_drills(client, drill["team_id"]) == []
    assert len(team_drills(client, drill["team_id"], include_archived=True)) == 1


def test_search_drills_by_name(client):
    team = create_team(client)
    create_drill(client, team["id"], name="Rondo 4v1")
    create_drill(client, team["id"], name="Shooting")

    assert [d["name"] for d in team_drills(client, team["id"], search="rondo")] == ["Rondo 4v1"]


def test_search_drills_ignores_case(client):
    drill = create_drill(client, name="Rondo 4v1")

    assert len(team_drills(client, drill["team_id"], search="RONDO")) == 1


def test_search_drills_respects_include_archived(client):
    drill = create_drill(client, name="Rondo 4v1")
    client.post(f"/drills/{drill['id']}/archive")

    assert team_drills(client, drill["team_id"], search="rondo") == []
    assert len(team_drills(client, drill["team_id"], search="rondo", include_archived=True)) == 1


def test_unarchive_drill(client):
    drill = create_drill(client)
    client.post(f"/drills/{drill['id']}/archive")

    response = client.post(f"/drills/{drill['id']}/unarchive")

    assert response.json()["archived"] is False
    assert len(team_drills(client, drill["team_id"])) == 1


# --- Tags ---


def test_drills_have_age_group_and_goal_tags(client):
    drill = create_drill(client, age_groups=["u9-u10", "u11-u12"], goals=["possession"])

    response = client.patch(f"/drills/{drill['id']}", json={"goals": ["possession", "transition"]})

    assert response.json()["age_groups"] == ["u9-u10", "u11-u12"]
    assert response.json()["goals"] == ["possession", "transition"]


def test_unknown_tags_are_rejected(client):
    team = create_team(client)

    assert client.post(f"/teams/{team['id']}/drills", json={"name": "X", "goals": ["juggling"]}).status_code == 422
    assert client.post(f"/teams/{team['id']}/drills", json={"name": "X", "age_groups": ["u99"]}).status_code == 422


def test_repeated_tags_are_kept_once(client):
    drill = create_drill(client, goals=["attacking", "attacking", "finishing"])

    assert drill["goals"] == ["attacking", "finishing"]


# --- Drill ideas ---


def test_everyone_sees_the_drill_ideas(client, add_idea, login_as):
    add_idea("Rondo 4v1", age_groups=["u9-u10"], goals=["possession"])
    add_idea("Ball Mastery", age_groups=ALL_AGES, goals=["warm-up"])
    login_as(BOB)

    ideas = client.get("/drill-ideas").json()

    assert [i["name"] for i in ideas] == ["Ball Mastery", "Rondo 4v1"]
    assert ideas[1]["team_id"] is None
    assert ideas[1]["goals"] == ["possession"]


def test_drill_ideas_cant_be_changed(client, add_idea):
    idea_id = add_idea("Rondo 4v1")

    assert client.get(f"/drills/{idea_id}").status_code == 200
    assert client.patch(f"/drills/{idea_id}", json={"name": "Mine"}).status_code == 403
    assert client.post(f"/drills/{idea_id}/archive").status_code == 403


def test_team_drills_are_not_drill_ideas(client, add_idea):
    create_drill(client, name="Our rondo")

    assert client.get("/drill-ideas").json() == []


# --- Suggestions ---


def test_suggestions_recommend_ideas_for_the_teams_age_group(client, add_idea):
    add_idea("Ball Mastery", age_groups=ALL_AGES)
    add_idea("Rondo 5v2", age_groups=["u11-u12", "u13+"])
    add_idea("Red Light, Green Light", age_groups=["u6-u8"])
    team = create_team(client)  # U11–U12

    suggestions = client.get(f"/teams/{team['id']}/drill-suggestions").json()

    assert suggestions["used_before"] == []
    assert [d["name"] for d in suggestions["recommended"]] == ["Ball Mastery", "Rondo 5v2"]


def test_a_team_without_an_age_group_gets_the_fundamentals(client, add_idea, TestingSession):
    add_idea("Ball Mastery", age_groups=ALL_AGES)
    add_idea("Rondo 5v2", age_groups=["u11-u12", "u13+"])
    team = create_team(client)
    with TestingSession() as db:  # Teams made before age groups existed have none.
        db.get(Team, team["id"]).age_group = None
        db.commit()

    suggestions = client.get(f"/teams/{team['id']}/drill-suggestions").json()

    assert [d["name"] for d in suggestions["recommended"]] == ["Ball Mastery"]


def test_suggestions_put_the_most_used_drills_first(client, add_idea):
    ball_mastery = add_idea("Ball Mastery", age_groups=ALL_AGES)
    team = create_team(client)
    rondo = create_drill(client, team["id"], name="Rondo")
    shooting = create_drill(client, team["id"], name="Shooting")
    plan_fields = {"title": "P", "date": "2026-11-03", "start_time": "18:00", "end_time": "19:30", "team_id": team["id"]}
    for drill_ids in [[shooting["id"], ball_mastery], [shooting["id"]]]:
        plan = client.post("/session-plans", json=plan_fields).json()
        entries = [{"drill_id": drill_id, "minutes": 10} for drill_id in drill_ids]
        client.put(f"/session-plans/{plan['id']}/drills", json={"drills": entries})

    suggestions = client.get(f"/teams/{team['id']}/drill-suggestions").json()

    assert [(d["name"], d["times_used"]) for d in suggestions["used_before"]] == [("Shooting", 2), ("Ball Mastery", 1)]
    assert suggestions["recommended"] == []  # Ball Mastery was already used, so it's not recommended again.
    assert rondo["id"] not in [d["id"] for d in suggestions["used_before"]]  # Never used.
