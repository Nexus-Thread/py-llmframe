# llmframe

OpenAI-first Python hexagonal application scaffold for the `llmframe` repository.

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) for environment and dependency management

## Setup

Install the project and development dependencies:

```bash
uv sync --all-extras
```

## LLM adapters

The repository includes reusable LLM output adapters under `llmframe.adapters.output.llm`.
Today this package is intentionally **OpenAI-first**: OpenAI is the only implemented provider integration, while the surrounding structure is being kept hexagonal so additional providers can be added later without leaking provider-specific concerns into the shared/application layers.

Key package areas:

- `llmframe.adapters.output.llm.llm_adapter` - provider-neutral high-level structured JSON and text generation adapter
- `llmframe.adapters.output.llm.providers.openai` - OpenAI provider adapter, client builder, transport, DTOs, and parsing helpers
- `llmframe.adapters.output.llm.usage_tracker` - aggregated token/cost tracking utilities

Example imports:

```python
from llmframe import OpenAIClientSettings, build_openai_llm_adapter
from llmframe.adapters.output.llm.usage_tracker import LlmUsageTrackerConfig, OpenAILlmUsageTracker
```

Recommended construction for third-party code:

```python
from llmframe import OpenAIClientSettings, build_openai_llm_adapter

adapter = build_openai_llm_adapter(
    settings=OpenAIClientSettings(
        base_url="https://api.openai.com/v1",
        api_key="...",
    ),
    model="gpt-4.1-mini",
    debug_json_enabled=True,
)
```

This keeps third-party callers on a stable, provider-neutral `LlmAdapter` API while hiding the internal provider assembly details.

When `debug_json_enabled=True`, the factory automatically creates a `JsonFileWriterAdapter` and writes formatted request/response snapshots to `artifacts/llm-debug`.

To override the output location:

```python
from pathlib import Path

from llmframe import OpenAIClientSettings, build_openai_llm_adapter

adapter = build_openai_llm_adapter(
    settings=OpenAIClientSettings(
        base_url="https://api.openai.com/v1",
        api_key="...",
    ),
    model="gpt-4.1-mini",
    debug_json_enabled=True,
    debug_json_output_dir=Path("custom/debug-dir"),
)
```

The shared LLM adapter depends on the application-layer `JsonArtifactWriterPort`, while the factory wires in the filesystem-backed `JsonFileWriterAdapter` by default for this convenience path.
