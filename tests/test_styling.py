import pytest

from zig_codeblocks.styling import Color, Reset, Style


@pytest.mark.parametrize(
    ("color", "bold", "underline", "expected_sgr"),
    [
        ("WHITE", False, False, "\033[37m"),
        ("BLUE", True, False, "\033[34;1m"),
        ("ORANGE", False, False, "\033[33m"),
        ("RED", True, False, "\033[31;1m"),
        ("BLUE", True, True, "\033[34;1;4m"),
        ("MAGENTA", False, True, "\033[35;4m"),
        ("WHITE", True, True, "\033[37;1;4m"),
        ("CYAN", True, True, "\033[36;1;4m"),
        ("MAGENTA", True, True, "\033[35;1;4m"),
        ("GRAY", False, False, "\033[30m"),
    ],
)
def test_style(color: str, bold: bool, underline: bool, expected_sgr: str) -> None:
    style = Style(Color[color], bold=bold, underline=underline)
    assert str(style) == expected_sgr


@pytest.mark.parametrize(
    ("reset_type", "expected_sgr"),
    [("FULL", "\033[0m"), ("BOLD", "\033[21m"), ("UNDERLINE", "\033[24m")],
)
def test_reset(reset_type: str, expected_sgr: str) -> None:
    assert str(Reset[reset_type]) == expected_sgr
