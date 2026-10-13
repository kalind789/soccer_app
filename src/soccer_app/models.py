from dataclasses import dataclass

class PlayerAlreadyExistsException(Exception):
    pass

class PlayerDoesNotExistsException(Exception):
    pass

@dataclass
class Player:
    id: int
    name: str
    position: str | None = None

class Team:
    def __init__(self, name: str):
        self.name = name
        self.players: dict[int, Player] = {}    # {id1: player, id2: player2}

    def add_player(self, player: Player) -> None:
        if player.id in self.players:
            raise PlayerAlreadyExistsException("This player id already exists in the data")

        self.players[player.id] = player

    def remove_player(self, player_id: int) -> None:
        if player_id not in self.players:
            raise PlayerDoesNotExistsException("This player does not exist in the data")
            
        self.players.pop(player_id)

    def list_players(self) -> list[Player]:
        return list(self.players.values())