import json
from pathlib import Path

import pytest

from zig_codeblocks.formatting import process_markdown

SOURCE_DIR = Path(__file__).parent / "sources"


def read_expected_styling(test_name: str) -> str:
    return "".join(
        json.loads(
            (SOURCE_DIR / "formatting_results" / f"{test_name}.json").read_bytes()
        )
    )


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
    expected_styling = f"```ansi\n{read_expected_styling(test_name)}\n```"
    assert process_markdown(f"```zig\n{source}```", only_code=True) == expected_styling
