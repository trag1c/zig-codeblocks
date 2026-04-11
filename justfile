[private]
default:
    @just --list

# Run ruff, pyright, pytest, and taplo in check mode
check:
    uv run ruff check
    uv run pyright src tests
    uv run pytest
    uv run ruff format --diff
    uv run taplo fmt --check --diff pyproject.toml

# Run ruff and taplo in fix mode
fix:
    uv run ruff format
    uv run ruff check --fix
    uv run taplo fmt pyproject.toml
