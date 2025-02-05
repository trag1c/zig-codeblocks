from collections.abc import Iterator
from itertools import chain
from typing import NamedTuple, cast

import marko
import tree_sitter as ts
import tree_sitter_zig


class Token(NamedTuple):
    kind: str
    value: bytes
    byte_range: range


ZIG_PARSER = ts.Parser(ts.Language(tree_sitter_zig.language()))


class CodeBlock(NamedTuple):
    """A code block extracted from a Markdown source."""

    lang: str
    body: str


def extract_codeblocks(source: str) -> Iterator[CodeBlock]:
    """Yield CodeBlocks from a Markdown source."""
    for element in marko.parse(source).children:
        if not isinstance(element, marko.block.FencedCode):
            continue
        body = cast(marko.parser.inline.RawText, element.children[0])  # type: ignore[name-defined]
        yield CodeBlock(element.lang, body.children)


def tokenize_zig(source: str) -> Iterator[Token]:
    src = source.encode()
    tree = ZIG_PARSER.parse(src)
    return _traverse(tree.root_node, src)


def _traverse(node: ts.Node, src: bytes) -> Iterator[Token]:
    if node.child_count == 0:
        yield Token(
            node.type,
            src[node.start_byte : node.end_byte],
            range(node.start_byte, node.end_byte),
        )
    else:
        yield from chain.from_iterable(_traverse(child, src) for child in node.children)
