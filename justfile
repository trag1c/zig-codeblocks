[private]
default:
    @just --list

# Run ruff, pyright, pytest, cargo test, clippy, and taplo in check mode
check:
    uv run ruff check
    uv run pyright src tests
    uv run pytest
    cargo test
    cargo clippy
    uv run ruff format --diff
    uv run taplo fmt --check --diff pyproject.toml Cargo.toml rustfmt.toml

# Run ruff, taplo, and clippy in fix mode
fix:
    uv run ruff format
    uv run ruff check --fix
    uv run taplo fmt pyproject.toml Cargo.toml rustfmt.toml
    cargo clippy --fix
