from enum import Enum
from typing import TypedDict

class CodeBlock:
    lang: str | None
    body: str

    def __init__(self, lang: str | None, body: str) -> None: ...

class Color(Enum):
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
    color: Color
    bold: bool
    underline: bool

    def __init__(
        self, color: Color, *, bold: bool = False, underline: bool = False
    ) -> None: ...

class Theme(TypedDict, total=False):
    BuiltinIdentifier: Style
    Call: Style
    Comment: Style
    Identifier: Style
    Keyword: Style
    Numeric: Style
    String: Style
    PrimitiveValue: Style
    Type: Style

def highlight_zig_code(source: str | bytes, theme: Theme = ...) -> str: ...
def process_markdown(
    source: str | bytes, theme: Theme = ..., *, only_code: bool = False
) -> str: ...
def extract_codeblocks(source: str | bytes) -> list[CodeBlock]: ...
