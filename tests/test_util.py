from pupgui2.util import *

from pupgui2.datastructures import SteamApp, LutrisGame, HeroicGame


def test_get_random_game_name() -> None:

    """ Test whether get_random_game_name returns a valid game name for each launcher game type. """

    names: list[str] = ["game", "A super cool game", "A game with a very long name that is very long", "0123456789"]

    steam_app: list[SteamApp] = [SteamApp() for _ in range(len(names))]
    lutris_game: list[LutrisGame] = [LutrisGame() for _ in range(len(names))]
    heroic_game: list[HeroicGame] = [HeroicGame() for _ in range(len(names))]

    for i, name in enumerate(names):
        steam_app[i].game_name = name
        lutris_game[i].name = name
        heroic_game[i].title = name

    for i in range(10):
        assert get_random_game_name(steam_app) in names
        assert get_random_game_name(lutris_game) in names
        assert get_random_game_name(heroic_game) in names
