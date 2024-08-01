# Type Aliases
from typing import TypeAlias

from pupgui2.datastructures import HeroicGame, LutrisGame, SteamApp


AnyGame: TypeAlias = SteamApp | LutrisGame | HeroicGame
JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None