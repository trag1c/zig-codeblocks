from pathlib import Path

import pytest

from zig_codeblocks.parsing import CodeBlock, extract_codeblocks

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
    src = (SOURCE_DIR / "spacing" / file_name).read_text()
    assert list(extract_codeblocks(src)) == [
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
    print((source, expected))
    codeblocks = list(extract_codeblocks(f"```{source}```"))
    assert len(codeblocks) == 1
    assert codeblocks[0] == CodeBlock(*expected)
