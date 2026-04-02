# llmframe

Python hexagonal application scaffold for the `llmframe` repository.

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) for environment and dependency management

## Setup

Install the project and development dependencies:

```bash
uv sync --all-extras
```

## Project layout

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

## LLM adapters

The repository now includes reusable LLM output adapters under `llmframe.adapters.output.llm`.

Key package areas:

- `llmframe.adapters.output.llm.llm_adapter` - provider-neutral high-level structured JSON and text generation adapter
- `llmframe.adapters.output.llm.providers.openai` - OpenAI provider client builder, transport, DTOs, and parsing helpers
- `llmframe.adapters.output.llm.usage_tracker` - aggregated token/cost tracking utilities

Example imports:

```python
from llmframe.adapters.output.llm import LlmAdapter, OpenAIClientSettings, build_client
from llmframe.adapters.output.llm.providers import openai
from llmframe.adapters.output.llm.usage_tracker import LlmUsageTrackerConfig, OpenAILlmUsageTracker
```

## Quality checks

Run the local quality gate with `uv`:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy .
uv run pytest
```

## Release publishing

GitHub Actions publishes this package to PyPI using the workflow at
`.github/workflows/ci_cd.yaml`.

- Publishing is triggered by pushes to the `master` branch or manual workflow dispatch.
- The workflow uses Python Semantic Release to determine the next version from conventional commits, create the release commit and tag, and generate changelog updates.
- Package artifacts are built in CI and published to PyPI only.
- If no releasable commits are detected, the publish job is skipped.
- Publishing targets the `llmframe` project on `pypi.org`.

Before the workflow can publish successfully, configure a trusted publisher in
the PyPI project settings for this GitHub repository and workflow file.

Also ensure the workflow has permission to use the repository `GITHUB_TOKEN` for
creating release commits and tags.

Example release flow:

```bash
git commit -m "feat: add new llm transport option"
git push origin master
```

## Notes

- The import package name is `llmframe`.
- Keep business logic inside `domain/` and `application/`.
- Keep framework, transport, persistence, and integration concerns in `adapters/`.
