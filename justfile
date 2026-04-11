[private]
default:
    @just --list

# Run ruff, pyright, pytest, cargo test, clippy, and taplo in check mode
check:
    uv sync --extra cli
    uv run ruff check
    uv run pyright src tests
    uv run pytest
    cargo test
    cargo clippy
    uv run ruff format --diff
    uv run taplo fmt --check --diff pyproject.toml Cargo.toml rustfmt.toml

# Run ruff's formatter, ruff's isort rules, and taplo in fix mode
format:
    uv run ruff format
    uv run ruff check --select I,RUF022,RUF023 --fix
    uv run taplo fmt pyproject.toml Cargo.toml rustfmt.toml

# Run ruff, taplo, and clippy in fix mode
fix: format
    uv run ruff check --fix
    cargo clippy --fix
