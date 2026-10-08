# Vault Heist task runner. Run `just` to list every task.
# https://just.systems
#
# The everyday tasks (install, dev, test, lint, typecheck, format, check) cover both halves
# of the project. Each has a backend-only and a frontend-only version, e.g. `just test-frontend`.

# On Windows, run recipes in PowerShell 7. Elsewhere, just uses sh.
set windows-shell := ["pwsh.exe", "-NoLogo", "-NoProfile", "-Command"]

# List available tasks
default:
    @just --list

# ---- Everyday tasks (backend and frontend) ----

# Install all dependencies exactly as locked
install: install-backend install-frontend

# Run the backend (http://localhost:8000) and the game (http://localhost:5173) together
[parallel]
dev: dev-backend dev-frontend

# Run all tests
test: test-backend test-frontend

# Check style and formatting (changes nothing)
lint: lint-backend lint-frontend

# Check types
typecheck: typecheck-backend typecheck-frontend

# Auto-format and fix what can be fixed
format: format-backend format-frontend

# Everything CI checks
check: check-backend check-frontend

# ---- Backend ----

# Install backend dependencies exactly as locked in uv.lock
[group('backend')]
[working-directory: 'backend']
install-backend:
    uv sync --locked

# Run the backend with auto-reload at http://localhost:8000
[group('backend')]
[working-directory: 'backend']
dev-backend:
    uv run uvicorn app.main:create_app --factory --reload

# Run the backend tests
[group('backend')]
[working-directory: 'backend']
test-backend:
    uv run pytest

# Check backend style and formatting with ruff
[group('backend')]
[working-directory: 'backend']
lint-backend:
    uv run ruff check .
    uv run ruff format --check .

# Check backend types with mypy
[group('backend')]
[working-directory: 'backend']
typecheck-backend:
    uv run mypy

# Format and auto-fix the backend
[group('backend')]
[working-directory: 'backend']
format-backend:
    uv run ruff format .
    uv run ruff check --fix .

# Backend lint, types and tests
[group('backend')]
check-backend: lint-backend typecheck-backend test-backend

# Chat with Gus in the terminal, e.g. `just chat --model ollama_chat/granite4.2:8b`
[group('backend')]
[working-directory: 'backend']
chat *args:
    uv run python -m scripts.chat_cli {{args}}

# Bring the database up to date (creates it the first time)
[group('backend')]
[working-directory: 'backend']
migrate:
    uv run alembic upgrade head

# Generate a migration after changing app/db/models.py, e.g. `just migration "add nickname"`
[group('backend')]
[working-directory: 'backend']
migration message:
    uv run alembic revision --autogenerate -m "{{message}}"

# ---- Frontend ----

# Install frontend dependencies exactly as locked in package-lock.json
[group('frontend')]
[working-directory: 'frontend']
install-frontend:
    npm ci

# Run the game with hot reload at http://localhost:5173
[group('frontend')]
[working-directory: 'frontend']
dev-frontend:
    npm run dev

# Run the frontend component tests
[group('frontend')]
[working-directory: 'frontend']
test-frontend:
    npm test

# Check frontend code with oxlint and formatting with Prettier
[group('frontend')]
[working-directory: 'frontend']
lint-frontend:
    npm run lint

# Check frontend types with TypeScript
[group('frontend')]
[working-directory: 'frontend']
typecheck-frontend:
    npm run typecheck

# Format the frontend with Prettier
[group('frontend')]
[working-directory: 'frontend']
format-frontend:
    npm run format

# Build the game for production into frontend/dist
[group('frontend')]
[working-directory: 'frontend']
build-frontend:
    npm run build

# Frontend lint, types, tests and a production build
[group('frontend')]
check-frontend: lint-frontend typecheck-frontend test-frontend build-frontend
