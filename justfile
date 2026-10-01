# Vault Heist task runner. Run `just` to list every task.
# https://just.systems

# On Windows, run recipes in PowerShell 7. Elsewhere, just uses sh.
set windows-shell := ["pwsh.exe", "-NoLogo", "-NoProfile", "-Command"]

# List available tasks
default:
    @just --list

# Install backend dependencies exactly as locked in uv.lock
[working-directory: 'backend']
install:
    uv sync --locked

# Run the backend with auto-reload at http://localhost:8000
[working-directory: 'backend']
dev:
    uv run uvicorn app.main:create_app --factory --reload

# Run all tests
[working-directory: 'backend']
test:
    uv run pytest

# Check style and formatting (changes nothing)
[working-directory: 'backend']
lint:
    uv run ruff check .
    uv run ruff format --check .

# Check types with mypy
[working-directory: 'backend']
typecheck:
    uv run mypy

# Auto-format and fix what can be fixed
[working-directory: 'backend']
format:
    uv run ruff format .
    uv run ruff check --fix .

# Chat with Gus in the terminal, e.g. `just chat --model ollama_chat/granite4.2:8b`
[working-directory: 'backend']
chat *args:
    uv run python -m scripts.chat_cli {{args}}

# Bring the database up to date (creates it the first time)
[working-directory: 'backend']
migrate:
    uv run alembic upgrade head

# Generate a migration after changing app/db/models.py, e.g. `just migration "add nickname"`
[working-directory: 'backend']
migration message:
    uv run alembic revision --autogenerate -m "{{message}}"

# Everything CI checks: lint, types and tests
check: lint typecheck test
