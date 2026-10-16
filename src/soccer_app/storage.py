import dataclasses
import json
from soccer_app.models import Team, Player
from dataclasses import asdict

def save_team(team: Team, path) -> None:
    temp_dict = {"name": team.name}
    players_dict = team.list_players()

    temp_dict["players"] = [asdict(player) for player in players_dict]

    with open(path, 'w') as f:
        json.dump(temp_dict, f, indent=2, sort_keys=True)