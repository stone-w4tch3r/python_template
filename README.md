# Python Project Template

[Русский](README.ru.md) | English

A modern, opinionated Python 3.14+ template with strict type safety and enforced best practices. Built for production-ready experience from the first commit.

## What You Get

- **Strict Type Safety** — basedpyright in strict mode, no `Any` types
- **Result Pattern** — Type-safe error handling via `rusty-results` (errors as values, not exceptions)
- **Modern Tooling** — uv (package manager), ruff (linting/formatting), pytest (testing)
- **Async-First** — httpx for HTTP, asyncio patterns throughout, enforced async I/O
- **Pre-Commit Hooks** — Automatic type checking, linting, and formatting on every commit
- **VS Code Focused** — Editor config, recommended extensions, and settings included
- **AI Dev Ready** — AGENTS.md and comprehensive code style included

## Quick Start

```bash
# Clone and setup (one command)
python script/bootstrap.py

## Development

```bash
uv run poe lint_full    # Type check + lint + format (must pass before commit)
uv run poe test         # Run tests with coverage
uv run poe app          # Run the application
python -m app           # Alternative: run directly
```

## Project Structure

- `src/app/` — Your application code
- `tests/` — pytest tests (asyncio supported)
- `docs/coding_rules.md` — Comprehensive coding standards (770 lines)
- `AGENTS.md` — AI agent development guidelines

## Philosophy

This template enforces **explicit, type-safe code**:
- Expected failures → `Result[T, E]` type
- Programming errors → Exceptions only
- All I/O → Async operations
- All types → Strict mode, no `Any`

Perfect for CLIs, backends, UIs, or any Python project where correctness matters.
