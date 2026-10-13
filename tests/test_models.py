import pytest
from soccer_app.models import Player, Team, PlayerAlreadyExistsException, PlayerDoesNotExistsException

"""
1. A new team has no players.
2. Adding a player makes them appear in list_players().
3. Adding two players with the same id raises an error.
4. Removing a player by id makes them disappear from the list.
5. Removing an id that doesn't exist raises an error.
6. A player can be created without a position (once you make that change).
7. Changing the list that list_players() returns doesn't change the team. This one is harder; try it last.
"""

def test_new_team_has_no_players():
    team = Team(name="Falcons")

    assert len(team.list_players()) == 0 

def test_add_player_appears_in_list():
    team = Team(name="Falcons")
    player = Player(id=1, name="Sam", position="MF")

    team.add_player(player)

    assert team.list_players() == [player]

def test_adding_duplicate_id_causes_value_error():
    player1 = Player(id=1, name="Sam", position="MF")
    player2 = Player(id=1, name="Na", position="DF")

    team1 = Team(name="Falcons")
    team1.add_player(player1)

    with pytest.raises(PlayerAlreadyExistsException):
        team1.add_player(player2)

def test_cannot_remove_id_that_doesnt_exist():
    player1 = Player(id=1, name="Sam", position="MF")
    player2 = Player(id=2, name="Na")

    team1 = Team(name="Falcons")
    team1.add_player(player1)
    team1.add_player(player2)

    with pytest.raises(PlayerDoesNotExistsException):
        team1.remove_player(3)

def test_removed_player_disappears_from_list():
    team = Team(name="Falcons")
    player1 = Player(id=1, name="Sam", position="MF")
    player2 = Player(id=2, name="Na", position="DF")
    team.add_player(player1)
    team.add_player(player2)

    team.remove_player(1)

    assert team.list_players() == [player2]


def test_player_position_is_optional():
    player = Player(id=1, name="Sam")

    assert player.position is None


def test_changing_returned_list_does_not_change_team():
    team = Team(name="Falcons")
    team.add_player(Player(id=1, name="Sam"))

    players = team.list_players()
    players.append(Player(id=2, name="Na"))

    assert len(team.list_players()) == 1