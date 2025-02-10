from __future__ import annotations

from itertools import tee
from typing import TYPE_CHECKING, TypeVar, cast

from zig_codeblocks import consts
from zig_codeblocks.parsing import extract_codeblocks, tokenize_zig
from zig_codeblocks.styling import RESET, Style, Theme

if TYPE_CHECKING:
    from collections.abc import Iterator

    from zig_codeblocks.parsing import Token

Body = list[str | Style]
T = TypeVar("T")


def _get_style(kind: str, theme: Theme) -> Style | None:
    for options, style in (
        (consts.IDENTIFIERS, theme.identifiers),
        (consts.KEYWORDS, theme.keywords),
        (consts.NUMERIC_LITERALS, theme.numeric),
        (consts.PRIMITIVE_VALUES, theme.primitive_values),
        (consts.STRINGLIKE, theme.strings),
        (consts.TYPES, theme.types),
    ):
        if kind in options:
            return style
    if kind == "comment":
        return theme.comments
    if kind == "builtin_identifier":
        return theme.builtin_identifiers
    return None


def _peek(iterator: Iterator[T]) -> T:
    return next(tee(iterator, 1)[0])


def _last_applied_style(body: Body) -> Style | str | None:
    return next(
        (item for item in body[::-1] if not isinstance(item, str) or item == RESET),
        None,
    )


def _adjust_string_idents(body: Body, token: Token, theme: Theme) -> None:
    # Special case for `whatever.@"something here"`,
    # which is an identifier, so should have no string highlighting
    if not ((theme.identifiers or theme.strings) and token.kind == '"'):
        return
    if not theme.strings:
        if len(body) > 2 and body[-3] == "@":
            body.insert(-2, cast(Style, theme.identifiers))
        return
    if _last_applied_style(body) == theme.strings and len(body) > 3 and body[-4] == "@":
        if theme.identifiers:
            body[-3] = theme.identifiers
        else:
            del body[-3]


def _process_zig_tokens(
    source: bytes, tokens: Iterator[Token], theme: Theme = consts.DEFAULT_THEME
) -> str:
    body: Body = []
    pointer = 0
    token = next(tokens)

    def skip_to_token() -> None:
        nonlocal pointer
        filler = source[pointer : token.byte_range.start]
        match filler.isspace(), _last_applied_style(body):
            case (_, None):
                pass
            case (True, Style(underline=True) | Style(bold=True)):
                body.append(RESET)
            case (False, Style()):
                body.append(RESET)
        body.append(filler.decode())
        pointer = token.byte_range.start

    while pointer < len(source):
        if token.byte_range.start > pointer:
            skip_to_token()
            continue

        style = (
            theme.calls
            if token.kind == "identifier" and _peek(tokens).kind == "("
            else _get_style(token.kind, theme)
        )
        if style is None:
            if _last_applied_style(body) not in (RESET, None):
                body.append(RESET)
        elif _last_applied_style(body) is not style:
            body.append(style)

        _adjust_string_idents(body, token, theme)

        body.append(token.value.decode())

        pointer = token.byte_range.stop
        try:
            token = next(tokens)
        except StopIteration:
            break
    return "".join(map(str, body))


def highlight_zig_code(source: str | bytes, theme: Theme = consts.DEFAULT_THEME) -> str:
    """
    Return an ANSI syntax-highlighted version of the given Zig source code.
    Assumes UTF-8 if source is `bytes`.
    """
    if isinstance(source, str):
        source = source.encode()
    return _process_zig_tokens(source, tokenize_zig(source), theme)


def process_markdown(
    source: str | bytes, theme: Theme = consts.DEFAULT_THEME, *, only_code: bool = False
) -> str:
    """
    Return a Markdown source with Zig code blocks syntax-highlighted.
    If `only_code` is True, only processed Zig code blocks will be returned.
    Assumes UTF-8 if source is `bytes`.
    """
    if isinstance(source, bytes):
        source = source.decode()
    zig_codeblocks = (
        block.body for block in extract_codeblocks(source) if block.lang == "zig"
    )
    if only_code:
        return "\n".join(
            f"```ansi\n{highlight_zig_code(code, theme)}\n```"
            for code in zig_codeblocks
        )
    for codeblock in zig_codeblocks:
        original_source = f"```zig\n{codeblock}```"
        highlighted_source = f"```ansi\n{highlight_zig_code(codeblock, theme)}\n```"
        source = source.replace(original_source, highlighted_source)
    return source
