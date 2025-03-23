import re

import pytest

from zig_codeblocks._core import Color, Style


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("Gray", Color.Gray),
        ("gray", Color.Gray),
        ("GRAY", Color.Gray),
        ("magenta", Color.Magenta),
    ],
)
def test_color_from_string(string: str, expected: Color) -> None:
    assert Color.from_string(string) == expected


def test_color_from_string_fail() -> None:
    with pytest.raises(ValueError, match=re.escape('Invalid color: "blurple"')):
        Color.from_string("blurple")


@pytest.mark.parametrize(
    ("color", "bold", "underline", "expected_sgr"),
    [
        ("White", False, False, "\033[37m"),
        ("Blue", True, False, "\033[34;1m"),
        ("Orange", False, False, "\033[33m"),
        ("Red", True, False, "\033[31;1m"),
        ("Blue", True, True, "\033[34;1;4m"),
        ("Magenta", False, True, "\033[35;4m"),
        ("White", True, True, "\033[37;1;4m"),
        ("Cyan", True, True, "\033[36;1;4m"),
        ("Magenta", True, True, "\033[35;1;4m"),
        ("Gray", False, False, "\033[30m"),
    ],
)
def test_style(color: str, bold: bool, underline: bool, expected_sgr: str) -> None:
    style = Style(Color.from_string(color), bold=bold, underline=underline)
    assert str(style) == expected_sgr
    assert eval(repr(style)) == style  # noqa: S307


@pytest.mark.parametrize(
    ("string", "expected"),
    [
        ("red", Style(Color.Red)),
        ("blue+bold", Style(Color.Blue, bold=True)),
        ("oRange+BOLD", Style(Color.Orange, bold=True)),
        ("green+underline", Style(Color.Green, underline=True)),
        ("bold+cyan+underline", Style(Color.Cyan, bold=True, underline=True)),
        ("bold+underline+magenta", Style(Color.Magenta, bold=True, underline=True)),
    ],
)
def test_style_from_string(string: str, expected: Style) -> None:
    assert Style.from_string(string) == expected


@pytest.mark.parametrize(
    ("string", "err_msg"),
    [
        ("underline+bold", "Missing color in input string"),
        ("black+bold+underline", 'Invalid color "black"'),
        ("red+cyan", "Multiple colors found: Red and Cyan"),
    ],
)
def test_style_from_string_fail(string: str, err_msg: str) -> None:
    with pytest.raises(ValueError, match=re.escape(err_msg)):
        Style.from_string(string)
