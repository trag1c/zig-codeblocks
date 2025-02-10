from __future__ import annotations

from dataclasses import KW_ONLY, dataclass, replace
from enum import Enum
from itertools import compress


def _to_sgr(*args: str) -> str:
    return f"\033[{';'.join(args)}m"


RESET = _to_sgr("0")


class Color(Enum):
    """
    An enumeration of 3-bit ANSI colors.
    Some names were adjusted to match Discord's style.
    """

    GRAY = "30"
    RED = "31"
    GREEN = "32"
    ORANGE = "33"
    BLUE = "34"
    MAGENTA = "35"
    CYAN = "36"
    WHITE = "37"  # Black for light mode


@dataclass(slots=True, frozen=True)
class Style:
    """
    A style for syntax highlighting.
    Takes a `Color` and can optionally be bold and/or underlined.
    Produces an SGR sequence when converted to a string.
    """

    color: Color
    _: KW_ONLY
    bold: bool = False
    underline: bool = False

    def __str__(self) -> str:
        modifiers = compress(("1", "4"), (self.bold, self.underline))
        return _to_sgr(self.color.value, *modifiers)


@dataclass(slots=True, kw_only=True)
class Theme:
    """A theme for syntax highlighting Zig code."""

    builtin_identifiers: Style | None = None
    calls: Style | None = None
    comments: Style | None = None
    identifiers: Style | None = None
    keywords: Style | None = None
    numeric: Style | None = None
    strings: Style | None = None
    primitive_values: Style | None = None
    types: Style | None = None

    def copy(self) -> Theme:
        """Create a copy of the `Theme`."""
        return replace(self)
