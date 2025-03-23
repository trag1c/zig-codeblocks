import sys
from pathlib import Path
from typing import Annotated, Optional, Union, cast

import zig_codeblocks as zc

try:
    import typer
except ModuleNotFoundError:
    sys.exit(
        "Cannot launch the CLI (failed to import typer)."
        " Make sure you have the [cli] extra installed."
    )

PATH_HELP_TEXT = "Path to read the {} source from. Reads from STDIN if omitted."
THEME_OPTION = typer.Option(
    "-t",
    "--theme",
    metavar="THEME",
    help="An optional custom theme to use for Zig highlighting.",
)
THEME_OVERRIDE_OPTION = typer.Option(
    "-o",
    "--theme-override",
    metavar="THEME",
    help="Optional changes to apply to the default theme for Zig highlighting.",
)

app = typer.Typer()


def read_in(path: Optional[Path]) -> str:
    if path is None:
        return sys.stdin.read()
    return path.read_text()


def parse_theme_config(config: str) -> dict[str, Union[str, zc.Style]]:
    theme = {}
    for token_type, style in (item.split(":") for item in config.split(",")):
        if token_type not in zc.Theme.__optional_keys__:
            msg = f"invalid token type: {token_type!r}"
            raise ValueError(msg)
        theme[token_type] = style if style == "none" else zc.Style.from_string(style)
    return theme


def resolve_theme(theme: Optional[str], theme_overrides: Optional[str]) -> zc.Theme:
    if theme is None:
        if theme_overrides is None:
            return zc.DEFAULT_THEME
        new_theme = zc.DEFAULT_THEME.copy()
        for k, v in parse_theme_config(theme_overrides).items():
            if v == "none":
                del new_theme[k]  # type: ignore[misc]
            else:
                new_theme[k] = v  # type: ignore[literal-required]
        return new_theme
    if theme_overrides is None:
        return cast(zc.Theme, parse_theme_config(theme))
    msg = "can't provide --theme and --theme-overrides at once"
    raise ValueError(msg)


@app.command(name="zig")
def process_zig(
    path: Annotated[
        Optional[Path],
        typer.Argument(help=PATH_HELP_TEXT.format("Zig")),
    ] = None,
    theme: Annotated[Optional[str], THEME_OPTION] = None,
    theme_overrides: Annotated[Optional[str], THEME_OVERRIDE_OPTION] = None,
) -> None:
    print(zc.highlight_zig_code(read_in(path), resolve_theme(theme, theme_overrides)))


@app.command(name="markdown")
def process_markdown(
    path: Annotated[
        Optional[Path],
        typer.Argument(help=PATH_HELP_TEXT.format("Markdown")),
    ] = None,
    only_code: Annotated[
        bool,
        typer.Option(
            "-c",
            "--only-code",
            help="If true, only Zig codeblocks will be included in the output.",
        ),
    ] = False,
    theme: Annotated[Optional[str], THEME_OPTION] = None,
    theme_overrides: Annotated[Optional[str], THEME_OVERRIDE_OPTION] = None,
) -> None:
    theme_ = resolve_theme(theme, theme_overrides)
    print(zc.process_markdown(read_in(path), theme_, only_code=only_code))


@app.command(name="codeblocks")
def extract_codeblocks(
    path: Annotated[
        Optional[Path],
        typer.Argument(help=PATH_HELP_TEXT.format("Markdown")),
    ] = None,
    langs: Annotated[
        Optional[str],
        typer.Option(
            "-l",
            "--langs",
            metavar="LANGS",
            help=(
                "A comma-separated list of languages to include."
                " Includes all if unspecified."
            ),
        ),
    ] = None,
) -> None:
    allowed_langs = set((langs or "").split(","))
    for cb in zc.extract_codeblocks(read_in(path)):
        if langs is None:
            print(cb)
            continue
        if cb.lang in allowed_langs:
            print(cb)


if __name__ == "__main__":
    app()
