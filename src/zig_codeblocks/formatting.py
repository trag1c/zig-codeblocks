from __future__ import annotations

from itertools import tee
from typing import TYPE_CHECKING, TypeVar

from zig_codeblocks.parsing import extract_codeblocks, tokenize_zig
from zig_codeblocks.styling import Color, Reset, Style

if TYPE_CHECKING:
    from collections.abc import Iterator

    from zig_codeblocks.parsing import Token

Body = list[str | Style | Reset]
T = TypeVar("T")

ZIG_KEYWORDS = frozenset(
    {
        "addrspace",
        "align",
        "allowzero",
        "and",
        "anyframe",
        "anytype",
        "asm",
        "async",
        "await",
        "break",
        "callconv",
        "catch",
        "comptime",
        "const",
        "continue",
        "defer",
        "else",
        "enum",
        "errdefer",
        "error",
        "export",
        "extern",
        "fn",
        "for",
        "if",
        "inline",
        "linksection",
        "noalias",
        "noinline",
        "nosuspend",
        "opaque",
        "or",
        "orelse",
        "packed",
        "pub",
        "resume",
        "return",
        "struct",
        "suspend",
        "switch",
        "test",
        "threadlocal",
        "try",
        "union",
        "unreachable",
        "usingnamespace",
        "var",
        "volatile",
        "while",
    }
)
ZIG_TYPE_TOKENS = frozenset({"builtin_type", "f64"})
ZIG_NUMERIC_TOKENS = frozenset({"integer", "float"})
ZIG_STRING_TOKENS = frozenset(
    {"string_content", "multiline_string", '"', "'", "character_content"}
)

_KIND_MAPPINGS = {
    "comment": Style(Color.GRAY),
    "builtin_identifier": Style(Color.BLUE, bold=True),
}
_GROUP_KIND_MAPPINGS: tuple[tuple[frozenset[str], Style], ...] = (
    (ZIG_STRING_TOKENS, Style(Color.GREEN)),
    (ZIG_KEYWORDS, Style(Color.ORANGE)),
    (ZIG_NUMERIC_TOKENS, Style(Color.CYAN)),
    (ZIG_TYPE_TOKENS, Style(Color.MAGENTA)),
)


def _get_style(kind: str) -> Style | None:
    return next(
        (style for options, style in _GROUP_KIND_MAPPINGS if kind in options),
        None,
    ) or _KIND_MAPPINGS.get(kind)


def _peek(iterator: Iterator[T]) -> T:
    return next(tee(iterator, 1)[0])


def _last_applied_style(body: Body) -> Style | Reset | None:
    return next((item for item in body[::-1] if not isinstance(item, str)), None)


def _adjust_reset(body: Body) -> None:
    last_style = _last_applied_style(body)
    if last_style is Reset.BOLD:
        body[~body[::-1].index(Reset.BOLD)] = Reset.FULL
    elif last_style is not Reset.FULL:
        body.append(Reset.FULL)


def _adjust_string_idents(body: Body, token: Token) -> None:
    # Special case for `whatever.@"something here"`,
    # which is an identifier, so should have no string highlighting
    if (
        token.kind == '"'
        and _last_applied_style(body) == Style(Color.GREEN)
        and len(body) > 3
        and body[-4] == "@"
    ):
        del body[-3]


def _process_zig_tokens(source: bytes, tokens: Iterator[Token]) -> str:
    body: Body = []
    pointer = 0
    token = next(tokens)

    def skip_to_token() -> None:
        nonlocal pointer
        filler = source[pointer : token.byte_range.start]
        if not filler.isspace():
            _adjust_reset(body)
        body.append(filler.decode())
        pointer = token.byte_range.start

    while pointer < len(source):
        if token.byte_range.start > pointer:
            skip_to_token()
            continue

        style = (
            Style(Color.BLUE)  # Special case for function calls
            if token.kind == "identifier" and _peek(tokens).kind == "("
            else _get_style(token.kind)
        )
        if style is None:
            _adjust_reset(body)
        elif _last_applied_style(body) is not style:
            body.append(style)

        _adjust_string_idents(body, token)

        body.append(token.value.decode())

        match style:
            case Style(bold=True):
                body.append(Reset.BOLD)
            case Style(underline=True):
                body.append(Reset.UNDERLINE)

        pointer = token.byte_range.stop
        try:
            token = next(tokens)
        except StopIteration:
            break
    return "".join(map(str, body))


def highlight_zig_code(source: str) -> str:
    """Return an ANSI syntax-highlighted version of the given Zig source code."""
    return _process_zig_tokens(source.encode(), tokenize_zig(source))


def process_markdown(source: str, *, only_code: bool = False) -> str:
    """
    Return a Markdown source with Zig code blocks syntax-highlighted.
    If `only_code` is True, only processed Zig code blocks will be returned.
    """
    zig_codeblocks = (
        block.body for block in extract_codeblocks(source) if block.lang == "zig"
    )
    if only_code:
        return "\n".join(
            f"```ansi\n{highlight_zig_code(code)}\n```" for code in zig_codeblocks
        )
    for codeblock in zig_codeblocks:
        original_source = f"```zig\n{codeblock}```"
        highlighted_source = f"```ansi\n{highlight_zig_code(codeblock)}\n```"
        source = source.replace(original_source, highlighted_source)
    return source
