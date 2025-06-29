# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [v0.3.2] - 2025-06-29

### Fixed
- Inline code blocks inside fenced code blocks are no longer removed
  (thanks [@00-kat](https://github.com/00-kat)!)

## [v0.3.1] - 2025-04-25

### Fixed
- Fixed ` ``` ` in inline code blocks being treated as a fenced code block
  starter

## [v0.3.0] - 2025-04-15

### Added
- A command-line interface
- Python 3.9 support
- `CodeBlock` objects now return the fenced Markdown code block form when
  converted to string
- `Style` objects can now be created from strings, e.g.
  `Style.from_string("cyan+bold")` is the same as `Style(Color.Cyan, bold=True)`

### Changed
- Most of the parsing/highlighting logic was moved to Rust, leading to
  significant speedups for both small (<300 lines) and large (>10k lines)
  inputs:
  - `highlight_zig_code` is 4–10x faster for small inputs and ~300x faster for
    large inputs
  - `process_markdown(only_code=False)` is 3–6x faster for small inputs and ~50x
    faster for large inputs
  - `process_markdown(only_code=True)` is ~4x faster for all inputs
  - `extract_codeblocks` is ~10% faster for large inputs
- `Color`:
  - can no longer be instantiated with `Color["red"]`, use
    `Color.from_string("red")` instead
  - members now use PascalCase names, e.g. `Color.BLUE` is now `Color.Blue`
- `extract_codeblocks`:
  - no longer strips CR and LF characters
  - now returns a list instead of an iterator
- `Theme` keys are now PascalCase instead of snake_case

## [v0.2.3] - 2025-02-16

### Fixed
- Fixed call-highlight checks consuming tokens instead of peeking them
  (this only seemed to have affected invalid Zig code)

## [v0.2.2] - 2025-02-15

### Fixed
- Code blocks with 1-char-long bodies are now correctly detected
- Zig sources ending with an identifier token no longer crash the highlighter

## [v0.2.1] - 2025-02-11

### Changed
- Optimized reset code insertion
- The [`Theme`](https://github.com/trag1c/zig-codeblocks/blob/b6d25f780ad260be4ff90ed0657ee08d69cf2e86/README.md#theme)
  `dataclass` was turned into a `TypedDict`

### Fixed
- A leading reset code is no longer inserted
- `process_markdown(only_code=False)` works as intended now
- String identifiers are now properly highlighted when string syntax
  highlighting is disabled

## [v0.2.0] - 2025-02-09

### Added
- Theming support
- Improved reset code insertion
- Improved type highlighting
- Primitive value highlighting (i.e. `true`, `false`, `null`, `undefined`)

### Changed
- Swapped keyword and type colors in the default theme

## [v0.1.2] - 2025-02-09

### Added
- Character literal highlighting

### Changed
- Public API functions can now operate on `bytes` objects
- Improved code block extraction on Windows

### Fixed
- Multi-byte characters no longer derail the highlighter

## [v0.1.1] - 2025-02-08

### Changed
- The Markdown parsing step now relies on a lenient regex instead of a
  CommonMark parser. This makes Discord's Markdown flavor behave more accurately (and also drops a dependency).

## [v0.1.0] - 2025-02-05

Initial release 🎉

[v0.1.0]: https://github.com/trag1c/zig-codeblocks/releases/tag/v0.1.0
[v0.1.1]: https://github.com/trag1c/zig-codeblocks/compare/v0.1.0...v0.1.1
[v0.1.2]: https://github.com/trag1c/zig-codeblocks/compare/v0.1.1...v0.1.2
[v0.2.0]: https://github.com/trag1c/zig-codeblocks/compare/v0.1.2...v0.2.0
[v0.2.1]: https://github.com/trag1c/zig-codeblocks/compare/v0.2.0...v0.2.1
[v0.2.2]: https://github.com/trag1c/zig-codeblocks/compare/v0.2.1...v0.2.2
[v0.2.3]: https://github.com/trag1c/zig-codeblocks/compare/v0.2.2...v0.2.3
[v0.3.0]: https://github.com/trag1c/zig-codeblocks/compare/v0.2.3...v0.3.0
[v0.3.1]: https://github.com/trag1c/zig-codeblocks/compare/v0.3.0...v0.3.1
[v0.3.2]: https://github.com/trag1c/zig-codeblocks/compare/v0.3.1...v0.3.2
