# Development

This document contains maintainer-oriented repository documentation. Keep public, package-facing information in `README.md` so it renders cleanly on PyPI and GitHub.

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

Sync dependencies and development tools with `uv`:

```bash
uv sync --frozen --all-groups
```

Run the local quality gate with `uv`:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy .
uv run pytest
```

The default pytest configuration reports missing coverage, writes `coverage.xml`,
and enforces a conservative minimum total coverage threshold. CI runs the same
non-mutating quality checks and uploads pytest HTML and coverage XML artifacts
for diagnostics.

Local pytest HTML reports are generated under `test_results/` when enabled by
the configured test workflow. The directory is ignored by git and contains only
developer-local diagnostics, so it can be removed at any time after reviewing or
sharing the relevant report. CI retains uploaded test artifacts according to the
workflow and platform retention settings rather than the local `test_results/`
directory.

## Compliance notes

- Development-only tools are managed through `[dependency-groups].dev` in `pyproject.toml`.
- The OpenAI transport adapter currently remains in a single oversized module as an intentional exception to the preferred module-splitting guidance. Keep follow-up refactors narrowly focused on transport-internal responsibilities so public imports remain stable.

## Manual live integration workflow

The repository includes a dedicated manual GitHub Actions workflow for the opt-in OpenAI live integration suite:

- `.github/workflows/integration_openai_live.yaml`

Use the Actions UI to trigger it with `workflow_dispatch` inputs for the target test scope, Python version, optional model or base URL overrides, and optional batch timing settings.

Required repository secret:

- `OPENAI_API_KEY`

Notes:

- The workflow sets `LLMFRAME_RUN_ON_DEMAND_INTEGRATION=1` automatically.
- It maps `secrets.OPENAI_API_KEY` to `LLMFRAME_OPENAI_API_KEY` for the tests.
- Batch retrieval runs should usually be started with an explicit `batch_id` because persisted metadata from a previous local or CI run is not automatically available in a fresh GitHub Actions runner.

## Documentation split

- `README.md` is the public, package-facing overview.
- `docs/` is for maintainer, contributor, and internal project documentation.
