from enum import Enum
from typing import TypedDict

class CodeBlock:
    """A code block extracted from a Markdown source."""

    lang: str | None
    body: str

    def __init__(self, lang: str | None, body: str) -> None: ...

class Color(Enum):
    """
    An enumeration of 3-bit ANSI colors.
    Some names were adjusted to match Discord's style.
    """

    Gray = ...
    Red = ...
    Green = ...
    Orange = ...
    Blue = ...
    Magenta = ...
    Cyan = ...
    White = ...

    @staticmethod
    def from_string(color: str) -> Color: ...

class Style:
    """
    A style for syntax highlighting.
    Takes a `Color` and can optionally be bold and/or underlined.
    Produces an SGR sequence when converted to a string.
    """

    color: Color
    bold: bool
    underline: bool

    def __init__(
        self, color: Color, *, bold: bool = False, underline: bool = False
    ) -> None: ...
    @staticmethod
    def from_string(value: str) -> Style: ...

class Theme(TypedDict, total=False):
    BuiltinIdentifier: Style
    Call: Style
    Comment: Style
    Identifier: Style
    Keyword: Style
    Numeric: Style
    PrimitiveValue: Style
    String: Style
    Type: Style

def highlight_zig_code(source: str | bytes, theme: Theme = ...) -> str:
    """
    Return an ANSI syntax-highlighted version of the given Zig source code.
    Assumes UTF-8.
    """

def process_markdown(
    source: str | bytes, theme: Theme = ..., *, only_code: bool = False
) -> str:
    """
    Return a Markdown source with Zig code blocks syntax-highlighted.
    If `only_code` is True, only processed Zig code blocks will be returned.
    Assumes UTF-8.
    """

def extract_codeblocks(source: str | bytes) -> list[CodeBlock]:
    """Return CodeBlocks from a Markdown source. Assumes UTF-8."""
