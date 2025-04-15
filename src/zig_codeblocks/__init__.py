from __future__ import annotations

from typing import TypedDict

from zig_codeblocks._core import (
    CodeBlock,
    Color,
    Style,
    extract_codeblocks,
    highlight_zig_code,
    process_markdown,
)


class Theme(TypedDict, total=False):
    """A theme for syntax highlighting Zig code."""

    BuiltinIdentifier: Style
    Call: Style
    Comment: Style
    Identifier: Style
    Keyword: Style
    Numeric: Style
    PrimitiveValue: Style
    String: Style
    Type: Style


DEFAULT_THEME: Theme = {
    "BuiltinIdentifier": Style(Color.Blue, bold=True),
    "Call": Style(Color.Blue),
    "Comment": Style(Color.Gray),
    "Keyword": Style(Color.Magenta),
    "Numeric": Style(Color.Cyan),
    "PrimitiveValue": Style(Color.Cyan),
    "String": Style(Color.Green),
    "Type": Style(Color.Orange),
}

__all__ = (
    "DEFAULT_THEME",
    "CodeBlock",
    "Color",
    "Style",
    "Theme",
    "extract_codeblocks",
    "highlight_zig_code",
    "process_markdown",
)
