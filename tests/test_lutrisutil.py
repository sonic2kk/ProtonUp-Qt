from collections.abc import Generator
import pytest

from pupgui2.datastructures import LutrisGame
from pupgui2.lutrisutil import is_lutris_game_using_runner


def make_lutris_game(name: str = '', slug: str = '', runner: str = '', installer_slug: str = '', installed_at: int = -1, install_loc: dict[str, str] | None = None) -> LutrisGame:

    lutris_game: LutrisGame = LutrisGame()

    lutris_game.name = name
    lutris_game.slug = slug
    lutris_game.runner = runner
    lutris_game.installer_slug = installer_slug
    lutris_game.installed_at = installed_at
    lutris_game.install_loc = install_loc

    return lutris_game


@pytest.mark.parametrize(
    'game, runner, expected', [
        pytest.param(make_lutris_game(runner = 'wine'), 'wine', True),
        pytest.param(make_lutris_game(runner = 'legendary'), 'legendary', True),
        pytest.param(make_lutris_game(), 'nile', False),
        pytest.param(make_lutris_game(runner = None), 'wine', False),
        pytest.param(make_lutris_game(runner = None), '', False),
        pytest.param(make_lutris_game(runner = None), None, False),
    ]
)
def test_is_lutris_game_using_runner(game: LutrisGame, runner: str, expected: bool) -> None:

    """
    Given a LutrisGame object and a known runner string,
    When the runner matches the LutrisGame object's runner,
    Then it should return True.
    """

    result: bool = is_lutris_game_using_runner(game, runner)

    assert result == expected
