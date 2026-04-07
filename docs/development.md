# Development

This document contains maintainer-oriented repository documentation. Public
package-facing information should stay in `README.md` so it renders cleanly on
PyPI and GitHub.

## Repository layout

The repository follows a hexagonal architecture layout:

```text
src/llmframe/
├── domain/          # Pure business logic and invariants
├── application/     # Use cases and port interfaces
│   └── ports/
└── adapters/        # Input/output adapters at the system boundary
    ├── input/
    └── output/
tests/
├── unit/
└── integration/
```

## Local quality checks

Run the local quality gate with `uv`:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy .
uv run pytest
```

## Documentation split

- `README.md` is the public/package-facing overview.
- `docs/` is for maintainer, contributor, and internal project documentation.
