# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
[v0.1.1]: https://github.com/trag1c/ixia/compare/v0.1.0...v0.1.1
[v0.1.2]: https://github.com/trag1c/ixia/compare/v0.1.1...v0.1.2
