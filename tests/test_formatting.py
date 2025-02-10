import json
from pathlib import Path

import pytest

from zig_codeblocks.formatting import highlight_zig_code, process_markdown
from zig_codeblocks.styling import Color, Style, Theme

SOURCE_DIR = Path(__file__).parent / "sources"


def read_expected_styling(test_name: str) -> str:
    expected_style: list[str] = []
    for line in json.loads(
        (SOURCE_DIR / "formatting_results" / f"{test_name}.json").read_bytes()
    ):
        style, _, content = line.partition(":")
        expected_style.append(f"\x1b[{style}m{content}")
    return "".join(expected_style)


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
def test_zig_highlighting(test_name: str) -> None:
    source = (
        (SOURCE_DIR / "zig_inputs" / f"{test_name}.zig")
        .read_bytes()
        .replace(b"\r\n", b"\n")
        .decode()
    )
    source = f"```zig\n{source}```"
    expected_styling = f"```ansi\n{read_expected_styling(test_name)}\n```"
    assert process_markdown(source, only_code=True) == expected_styling
    assert process_markdown(source.encode(), only_code=True) == expected_styling


@pytest.mark.parametrize(
    "theme",
    [
        Theme(identifiers=Style(Color.RED)),
        Theme(identifiers=Style(Color.RED), strings=Style(Color.GREEN)),
    ],
)
def test_highlighting_backtrack_identifier_case(theme: Theme) -> None:
    source = 'const @"identifier with spaces in it" = 0xff;'
    expected_highlighting = (
        'const @\033[31m"identifier with spaces in it" \033[0m= 0xff;'
    )
    assert highlight_zig_code(source, theme) == expected_highlighting
