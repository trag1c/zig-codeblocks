from __future__ import annotations

from pathlib import Path

import pytest

from zig_codeblocks._core import CodeBlock, extract_codeblocks

SOURCE_DIR = Path(__file__).parent / "sources"


@pytest.mark.parametrize(
    ("file_name"),
    [
        ("standard.md"),
        ("early_start.md"),
        ("squished.md"),
        ("no_gap.md"),
        ("squished_no_gap.md"),
        ("triple_in_double_inline.md"),
    ],
)
def test_codeblock_spacing_scenarios(file_name: str) -> None:
    src = SOURCE_DIR / "spacing" / file_name
    for meth in (Path.read_text, Path.read_bytes):
        code_blocks = extract_codeblocks(meth(src))
        assert len(code_blocks) == 2
        py_block, zig_block = code_blocks
        assert (py_block.lang, zig_block.lang) == ("py", "zig")
        assert py_block.body.strip("\r\n") == "print(1)"
        assert zig_block.body.strip("\r\n") == 'const std = @import("std");'


@pytest.mark.parametrize(
    ("source", "expected"),
    [
        ("rust", (None, "rust")),
        ("rust\n", (None, "rust\n")),
        ("rust\nfn", ("rust", "fn")),
        ("zig\na", ("zig", "a")),
        ("zig\naa", ("zig", "aa")),
        ("zig\na\n", ("zig", "a\n")),
        ("rust\n\n\n\n\n\n", (None, "rust\n\n\n\n\n\n")),
        ("ruśt\nfn", (None, "ruśt\nfn")),
        ("1+2\nfn", ("1+2", "fn")),
        ("1%2\nfn", (None, "1%2\nfn")),
    ],
)
def test_codeblock_with_language(source: str, expected: tuple[str | None, str]) -> None:
    codeblocks = extract_codeblocks(f"```{source}```")
    assert len(codeblocks) == 1
    assert codeblocks[0] == CodeBlock(*expected)


@pytest.mark.parametrize(
    "source",
    [
        '```zig\nconst std = @import("std");\n```',
        "```py\nprint(1)\n```\n```woah```",
        "```\n\n\nhi\n\n\n```",
        '```zig\nconst std = @import("std"); // this is `std`\n```',
    ],
)
def test_codeblocks_are_reproducible(source: str) -> None:
    codeblocks = extract_codeblocks(source)
    assert "\n".join(map(str, codeblocks)) == source
