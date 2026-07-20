# Contributing to Social Engine

## Development Setup

We provide a setup script to get you started quickly:
```bash
./scripts/setup_dev.sh
```

This will:
- Start PostgreSQL and Redis via Docker
- Install backend dependencies
- Run database migrations

## Running Tests
Backend tests use pytest:
```bash
cd backend
pytest tests/
```

## Adding a New LLM Provider
1. Add the provider package to `backend/requirements.txt`
2. Create a new file in `backend/llm/providers/` implementing the `LLMProvider` interface
3. Register the provider in `backend/llm/factory.py`
4. Add relevant environment variables to `.env.example`

## Adding a New Social Provider
1. Create a new file in `backend/social/providers/` implementing the `SocialProvider` interface
2. Update the `Platform` enum in `backend/domain/models.py`
3. Add the provider to the frontend platform selectors

## Adding a New Research Plugin
1. Create a new plugin class in `backend/agents/tools/research/`
2. Implement the `search` and `summarize` methods
3. Register it in the `ResearchAgent` initialization

## Code Style
- Backend: Python 3.13 with full type hints, `ruff` for linting, `mypy` for type checking
- Frontend: TypeScript, Prettier, ESLint, Tailwind conventions

## Pull Request Process
1. Fork the repo and create your branch from `main`
2. Run tests and linters
3. Ensure CI passes
4. Request review from maintainers
