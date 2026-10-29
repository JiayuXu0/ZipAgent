# Repository Guidelines

## Project Structure & Module Organization
Runtime code lives under `src/zipagent/`, with core agents in `agent.py`, execution control in `runner.py`, and supporting utilities across `context.py`, `stream.py`, and tool integrations (`tool.py`, `mcp_tool.py`). Shared prompts reside in `src/zipagent/system.md`. Tests mirror this layout inside `tests/`, while quick-start examples are in `examples/` and contributor docs in `docs/`. Keep new assets alongside related modules to simplify discovery.

## Build, Test & Development Commands
- `uv sync` installs dependencies from `pyproject.toml`/`uv.lock`.
- `uv run ruff check --fix` formats and lint-fixes the codebase.
- `uv run pyright` performs strict type analysis.
- `uv run pytest` executes the test suite; add `--cov=zipagent --cov-report=term-missing` to inspect coverage.
- `uv build` (or `hatch build`) produces distributable packages when preparing releases.

## Coding Style & Naming Conventions
Adhere to PEP 8 with four-space indentation, 79-character lines, and double quotes. Favor explicit type hints and Pydantic dataclass-style models. Name files and modules in snake_case, classes in PascalCase, and user-facing tool functions with descriptive verbs (e.g., `fetch_weather_tool`). Let Ruff handle import ordering and minor formatting fixes.

## Testing Guidelines
Use `pytest` for all tests and place new cases beside the implementation under `tests/`. Name files `test_*.py`, leverage fixtures from `tests/conftest.py`, and mark async flows with `@pytest.mark.asyncio`. Maintain at least 75% coverage and ensure new failure modes receive regression tests.

## Commit & Pull Request Guidelines
Commits follow Conventional Commit prefixes (`feat:`, `fix:`, `docs:`, etc.) with concise, sentence-case summaries. Squash WIP commits before opening a PR. Each PR should describe the motivation, link related issues, and include CLI output or screenshots for notable behaviors. Flag configuration or key-management changes explicitly for reviewer verification.

## Agent-Specific Notes
Document non-obvious behaviors in module docstrings or `docs/`. When adding model backends in `model.py`, provide an example under `examples/` and record required environment variables (e.g., `OPENAI_API_KEY`) to prevent setup surprises.

## Cursor Cloud specific instructions
- The image does not include `uv`. Install it with the official installer and link `uv` and `uvx` into `/usr/local/bin`, then run `uv sync --frozen --python /usr/bin/python3.12` from the repository root. Python 3.12 is already at `/usr/bin/python3.12`.
- `python3 -m venv` fails because `ensurepip` is not installed. Create environments with `uv venv`.
- `Agent()` constructs `OpenAIModel`, which reads `API_KEY` from the environment (see `.env.example`), not `OPENAI_API_KEY`. A non-empty placeholder is enough for unit tests that only construct the client. Tests that call a live API stay skipped unless `TEST_OPENAI_API` is set. Do not commit real keys.
- On current `master`, `uv run ruff check .` and `uv run pyright` report existing fullwidth-punctuation and strict-type issues, and `uv run pytest` has existing failures in `tests/test_runner.py` and `tests/test_model_integration.py`. Those failures are in the tree; they are not missing packages.
