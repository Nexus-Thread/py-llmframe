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

## OpenAI Responses Batch API

The shared `LlmAdapter` also supports OpenAI's asynchronous Batch API for the Responses endpoint. This preserves the current synchronous `generate_text()` and `extract_json()` methods while adding separate batch submission and retrieval methods for lower-cost bulk execution.

Example plain-text batch submission:

```python
from llmframe import LlmBatchTextRequest, OpenAIClientSettings, build_openai_llm_adapter

adapter = build_openai_llm_adapter(
    settings=OpenAIClientSettings(
        base_url="https://api.openai.com/v1",
        api_key="...",
    ),
    model="gpt-4.1-mini",
)

submission = adapter.submit_text_batch(
    requests=[
        LlmBatchTextRequest(
            custom_id="item-1",
            developer_prompt="You are a concise assistant.",
            user_prompt="Summarize this document.",
        )
    ]
)

status = adapter.get_batch_status(batch_id=submission.batch_id)
```

Once the batch is complete, callers can retrieve parsed plain-text or structured results with `get_text_batch_result()` or `get_structured_batch_result()`. Batch execution is asynchronous and OpenAI-specific under the hood, but remains exposed through the same shared adapter package.

Submitted batch metadata is also persisted by default to `artifacts/llm-batches`, with one JSON record per batch ID. This makes batch IDs durable across process restarts so callers can reload a previously submitted batch ID and continue polling or fetching results later.

To override the batch metadata storage location:

```python
from pathlib import Path

from llmframe import OpenAIClientSettings, build_openai_llm_adapter

adapter = build_openai_llm_adapter(
    settings=OpenAIClientSettings(
        base_url="https://api.openai.com/v1",
        api_key="...",
    ),
    model="gpt-4.1-mini",
    batch_request_output_dir=Path("custom/batch-dir"),
)
```

If you need custom persistence behavior, pass your own implementation of the application-layer `BatchRequestStorePort` to `build_openai_llm_adapter()`.

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

## On-demand live integration tests

The repository also includes opt-in live integration tests for the main OpenAI-backed flows:

- single-request text generation
- single-request structured JSON extraction
- batch submission plus status/result retrieval

These tests are intentionally excluded from normal development runs and only execute when you opt in with environment variables.

Required environment variables:

- `LLMFRAME_RUN_ON_DEMAND_INTEGRATION=1`
- `OPENAI_API_KEY` or `LLMFRAME_OPENAI_API_KEY`

Optional environment variables:

- `LLMFRAME_OPENAI_BASE_URL` (defaults to `https://api.openai.com/v1`)
- `LLMFRAME_OPENAI_MODEL` (defaults to `gpt-4.1-nano`)
- `LLMFRAME_BATCH_WAIT_TIMEOUT_SECONDS` (defaults to `120`)
- `LLMFRAME_BATCH_POLL_INTERVAL_SECONDS` (defaults to `5`)

Run only the on-demand live suite with:

```bash
uv run pytest -m "integration and on_demand" tests/integration/openai_live
```

For the live batch workflow, the submission test persists batch metadata under
`artifacts/llm-batches`. The retrieval test can then read a previously
submitted batch either from the newest persisted record or from an explicit
batch ID provided via `LLMFRAME_TEST_BATCH_ID`.

Useful live batch commands:

```bash
LLMFRAME_RUN_ON_DEMAND_INTEGRATION=1 OPENAI_API_KEY=... uv run pytest -m "integration and on_demand" tests/integration/openai_live/test_batch_submission.py
```

```bash
LLMFRAME_RUN_ON_DEMAND_INTEGRATION=1 OPENAI_API_KEY=... uv run pytest -m "integration and on_demand" tests/integration/openai_live/test_batch_result_retrieval.py
```

These tests use very short prompts and tiny expected outputs so token usage stays minimal.
