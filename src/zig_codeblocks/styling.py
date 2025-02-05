from dataclasses import KW_ONLY, dataclass
from enum import Enum
from itertools import compress


def _to_sgr(*args: str) -> str:
    return f"\033[{';'.join(args)}m"


class Reset(Enum):
    FULL = "0"
    BOLD = "21"
    UNDERLINE = "24"

    def __str__(self) -> str:
        return _to_sgr(self.value)


class Color(Enum):
    # Names adjusted to match Discord's style
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
    color: Color
    _: KW_ONLY
    bold: bool = False
    underline: bool = False

    def __str__(self) -> str:
        modifiers = compress(("1", "4"), (self.bold, self.underline))
        return _to_sgr(self.color.value, *modifiers)
