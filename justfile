[private]
default:
   @just --list

# Run ruff, pytest, pyright, and taplo in check mode
check:
    uv run ruff check
    uv run pytest
    uv run pyright src tests
    uv run ruff format --check --preview
    uv run taplo fmt --check pyproject.toml

# Run ruff and taplo in fix mode
fix:
    uv run ruff format --preview
    uv run ruff check --fix
    uv run taplo fmt pyproject.toml
