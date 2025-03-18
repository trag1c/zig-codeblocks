from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from zig_codeblocks import Color, Style, highlight_zig_code, process_markdown

if TYPE_CHECKING:
    from zig_codeblocks._core import Theme

SOURCE_DIR = Path(__file__).parent / "sources"


def read_expected_styling(test_name: str) -> str:
    expected_style: list[str] = []
    for line in json.loads(
        (SOURCE_DIR / "formatting_results" / f"{test_name}.json").read_bytes()
    ):
        style, _, content = line.partition(":")
        expected_style.append(f"\x1b[{style}m{content}")
    return "".join(expected_style)


@pytest.mark.parametrize("only_code", [True, False])
@pytest.mark.parametrize(
    "test_name",
    [
        "assign_undefined",
        "comments",
        "emoji",
        "global_assembly",
        "hello_again",
        "identifiers",
    ],
)
def test_zig_highlighting(test_name: str, only_code: bool) -> None:
    source = (
        (SOURCE_DIR / "zig_inputs" / f"{test_name}.zig")
        .read_bytes()
        .replace(b"\r\n", b"\n")
        .decode()
    )
    source = f"```zig\n{source}```"
    expected_styling = f"```ansi\n{read_expected_styling(test_name)}\n```"
    assert process_markdown(source, only_code=only_code) == expected_styling
    assert process_markdown(source.encode(), only_code=only_code) == expected_styling


@pytest.mark.parametrize(
    "theme",
    [
        {"Identifier": Style(Color.Red)},
        {"Identifier": Style(Color.Red), "String": Style(Color.Green)},
    ],
)
def test_highlighting_backtrack_identifier_case(theme: Theme) -> None:
    source = 'const @"identifier with spaces in it" = 0xff;'
    expected_highlighting = (
        'const @\033[31m"identifier with spaces in it" \033[0m= 0xff;'
    )
    assert highlight_zig_code(source, theme) == expected_highlighting


def test_reset_optimization() -> None:
    source = " const x = 0xff;"
    theme: Theme = {
        "Identifier": (red := Style(Color.Red)),
        "Keyword": (blue_u := Style(Color.Blue, underline=True)),
    }
    expected_highlighting = f" {blue_u}const\033[0m {red}x \033[0m= 0xff;"
    assert highlight_zig_code(source, theme) == expected_highlighting


def test_safe_peek() -> None:
    src = "just_an_identifier"
    assert highlight_zig_code(src) == src

    theme: Theme = {"Identifier": (red := Style(Color.Red))}
    assert highlight_zig_code(src, theme) == f"{red}{src}"
