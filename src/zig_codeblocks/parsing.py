import re
from collections.abc import Iterator
from itertools import chain
from typing import NamedTuple

import tree_sitter as ts
import tree_sitter_zig

CODE_BLOCK_PATTERN = re.compile(
    r"```(?:([A-Za-z0-9\-_\+\.#]+)(?:\r?\n)+([^\r\n].+?)|(.*?))```", re.DOTALL
)

ZIG_PARSER = ts.Parser(ts.Language(tree_sitter_zig.language()))


class Token(NamedTuple):
    kind: str
    value: bytes
    byte_range: range


class CodeBlock(NamedTuple):
    """A code block extracted from a Markdown source."""

    lang: str | None
    body: str


def extract_codeblocks(source: str | bytes) -> Iterator[CodeBlock]:
    """Yield CodeBlocks from a Markdown source. Assumes UTF-8 if source is `bytes`."""
    if isinstance(source, bytes):
        source = source.decode()
    for m in CODE_BLOCK_PATTERN.finditer(source):
        lang, body, no_lang_body = m.groups()
        yield (
            CodeBlock(lang, body=body.strip("\r\n"))
            if lang
            else CodeBlock(lang=None, body=no_lang_body.strip("\r\n"))
        )


def tokenize_zig(src: bytes) -> Iterator[Token]:
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
