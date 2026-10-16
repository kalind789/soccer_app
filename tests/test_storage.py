from soccer_app.storage import save_team
from soccer_app.models import Team, Player
from dataclasses import asdict
import json

def test_save_team(tmp_path):
    team1 = Team("Red Dragons")

    player1 = Player(0, "Red Man", "MF")
    player2 = Player(1, "Chhabi")

    team1.add_player(player1)
    team1.add_player(player2)

    path = tmp_path / "team.json" 
    save_team(team1, path)

    with open(path) as f:
        data = json.load(f)
    assert data == {
        "name": "Red Dragons",
        "players": [
            {"id": 0, "name": "Red Man", "position": "MF"},
            {"id": 1, "name": "Chhabi", "position": None}
        ],
    }