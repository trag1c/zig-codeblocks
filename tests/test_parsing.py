import json
from pathlib import Path

import pytest

from zig_codeblocks.parsing import CodeBlock, Token, extract_codeblocks, tokenize_zig

SOURCE_DIR = Path(__file__).parent / "sources"


@pytest.mark.parametrize(
    ("file_name"),
    [
        ("standard.md"),
        ("early_start.md"),
        ("squished.md"),
        ("no_gap.md"),
        ("squished_no_gap.md"),
    ],
)
def test_codeblock_spacing_scenarios(file_name: str) -> None:
    src = SOURCE_DIR / "spacing" / file_name
    for meth in (Path.read_text, Path.read_bytes):
        assert list(extract_codeblocks(meth(src))) == [
            CodeBlock(lang="py", body="print(1)"),
            CodeBlock(lang="zig", body='const std = @import("std");'),
        ]


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("rust", (None, "rust")),
        ("rust\n", (None, "rust")),
        ("rust\nfn", ("rust", "fn")),
        ("rust\n\n\n\n\n\n", (None, "rust")),
        ("ruśt\nfn", (None, "ruśt\nfn")),
        ("1+2\nfn", ("1+2", "fn")),
        ("1%2\nfn", (None, "1%2\nfn")),
    ],
)
def test_codeblock_with_language(source: str, expected: tuple[str | None, str]) -> None:
    codeblocks = list(extract_codeblocks(f"```{source}```"))
    assert len(codeblocks) == 1
    assert codeblocks[0] == CodeBlock(*expected)


def read_expected_tokens(test_name: str) -> list[Token]:
    return [
        Token(
            kind=t["kind"],
            value=(t.get("value") or t["kind"]).encode(),
            byte_range=range(t["start"], t["end"]),
        )
        for t in json.loads(
            (SOURCE_DIR / "zig_parsing" / f"result_{test_name}.json").read_text()
        )
    ]


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
def test_zig_parser(test_name: str) -> None:
    source = (SOURCE_DIR / "zig_parsing" / f"{test_name}.zig").read_bytes()
    assert list(tokenize_zig(source)) == read_expected_tokens(test_name)
