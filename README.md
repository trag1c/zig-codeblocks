[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

# zig-codeblocks

`zig-codeblocks` is a CPython 3.10+ library for adding syntax highlighting to
Zig code blocks in Markdown files through ANSI escape codes.
Originally intended for patching the lack of syntax highlighting for Zig on
Discord.


## Installation
`zig-codeblocks` is available on PyPI:
```sh
pip install zig-codeblocks
```
You can also install it from source:
```sh
pip install git+https://github.com/trag1c/zig-codeblocks.git
```


## API Reference

### `extract_codeblocks`
```py
def extract_codeblocks(source: str | bytes) -> Iterator[CodeBlock]
```
Yields [`CodeBlock`](#codeblock)s from a Markdown source.
Assumes UTF-8 if source is `bytes`.

**Example usage:**
```py
from pathlib import Path

from zig_codeblocks import extract_codeblocks

source = Path("examples/riiz.md").read_text()
for codeblock in extract_codeblocks(source):
    print(f"Language: {codeblock.lang}")
    print(f"Body:\n{codeblock.body}")
```
```
Language: py
Body:
print("Hello, World!")

Language: zig
Body:
const std = @import("std");
pub fn main() !void {
    std.debug.print("Hello, World!\n", .{});
}
```


### `highlight_zig_code`
```py
def highlight_zig_code(source: str | bytes, theme: Theme = DEFAULT_THEME) -> str
```
Returns an ANSI syntax-highlighted version of the given Zig source code.
Assumes UTF-8 if source is `bytes`.
An optional [`Theme`](#theme) can be supplied (defaults to
[`DEFAULT_THEME`](#default_theme)).

**Example usage:**
```py
from pathlib import Path

from zig_codeblocks import DEFAULT_THEME, Color, Style, highlight_zig_code

source = Path("examples/hello_world.zig").read_text()

theme = DEFAULT_THEME.copy()
theme.builtin_identifiers = Style(Color.ORANGE, underline=True)
theme.strings = Style(Color.CYAN)
theme.types = None

print(
    highlight_zig_code(source),
    highlight_zig_code(source, theme),
    sep="\n\n",
)
```
<img src="examples/highlighted-zig-code.png" width="65%">


### `process_markdown`
```py
def process_markdown(
    source: str | bytes,
    theme: Theme = DEFAULT_THEME,
    *,
    only_code: bool = False,
) -> str
```
Returns a Markdown source with Zig code blocks syntax-highlighted.
Assumes UTF-8 if source is `bytes`.
An optional [`Theme`](#theme) can be supplied (defaults to
[`DEFAULT_THEME`](#default_theme)).
If `only_code` is True, only processed Zig code blocks will be returned.

**Example usage:**
```py
from pathlib import Path

from zig_codeblocks import process_markdown

source = Path("examples/riiz.md").read_text()
print(process_markdown(source))
```
<img src="examples/processed-markdown.png" width="85%">


### `CodeBlock`
```py
class CodeBlock(NamedTuple):
    lang: str
    body: str
```
A code block extracted from a Markdown source.


### `Color`
```py
class Color(Enum):
    GRAY = "30"
    RED = "31"
    GREEN = "32"
    ORANGE = "33"
    BLUE = "34"
    MAGENTA = "35"
    CYAN = "36"
    WHITE = "37"  # Black for light mode
```
An enumeration of 3-bit ANSI colors.
Some names were adjusted to match Discord's style.


### `Style`
```py
@dataclass(slots=True, frozen=True)
class Style:
    color: Color
    _: KW_ONLY
    bold: bool = False
    underline: bool = False
```
A style for syntax highlighting.
Takes a [`Color`](#color) and can optionally be bold and/or underlined.
Immutable.
Produces an SGR sequence when converted to a string.


### `Theme`
```py
class Theme(TypedDict, total=False):
    builtin_identifiers: Style
    calls: Style
    comments: Style
    identifiers: Style
    keywords: Style
    numeric: Style
    strings: Style
    primitive_values: Style
    types: Style
```
A theme dict for syntax highlighting Zig code.
Each key is optional and can be provided a [`Style`](#style) to apply to the
corresponding token type.
Can be instantiated with a dict literal or with a `Theme` call:
```py
from zig_codeblocks import Color, Style, Theme

theme_foo = Theme(
    numeric=Style(Color.BLUE),
    strings=Style(Color.GREEN),
)

theme_bar: Theme = {
    "numeric": Style(Color.BLUE),
    "strings": Style(Color.GREEN),
}

assert theme_foo == theme_bar
```


### `DEFAULT_THEME`
The default theme used for highlighting, defined as follows:
```py
DEFAULT_THEME = Theme(
    builtin_identifiers=Style(Color.BLUE, bold=True),
    calls=Style(Color.BLUE),
    comments=Style(Color.GRAY),
    keywords=Style(Color.MAGENTA),
    numeric=Style(Color.CYAN),
    primitive_values=Style(Color.CYAN),
    strings=Style(Color.GREEN),
    types=Style(Color.ORANGE),
)
```


## License
`zig-codeblocks` is licensed under the [MIT License].  
© [trag1c], 2025

[MIT License]: https://opensource.org/license/mit/
[trag1c]: https://github.com/trag1c/
