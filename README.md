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
from llmframe.adapters.output.llm import LlmAdapter
from llmframe.adapters.output.llm.providers.openai import OpenAIClientSettings, build_provider
from llmframe.adapters.output.llm.usage_tracker import LlmUsageTrackerConfig, OpenAILlmUsageTracker
```
