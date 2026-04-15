# llmframe

OpenAI-first Python scaffold for building LLM integrations with a hexagonal architecture.

## Requirements

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/) for environment and dependency management

## Setup

Install the project and development dependencies:

```bash
uv sync --frozen --all-groups
```

## Local quality gate

Run the full local quality gate through `uv` before handoff or release work:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy .
uv run pytest
```

## LLM adapters

The repository includes reusable LLM output adapters under `llmframe.adapters.output.llm`.

The package is intentionally **OpenAI-first**: OpenAI is the only implemented provider today, while the surrounding structure stays hexagonal so additional providers can be added later without leaking provider-specific concerns into the shared or application layers.

Key package areas:

- `llmframe.adapters.output.llm.llm_adapter` - provider-neutral high-level adapter for structured JSON extraction and text generation
- `llmframe.adapters.output.llm.providers.openai` - OpenAI provider adapter, client builder, transport, DTOs, and parsing helpers
- `llmframe.adapters.output.llm.usage_tracker` - aggregated token and cost tracking utilities

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

This keeps third-party callers on a stable, provider-neutral `LlmAdapter` API while hiding provider assembly details.

### Multimodal image input

The shared adapter now supports image URLs and local image file paths as part of a Responses API input through `generate_text_from_input(...)`.

```python
from llmframe import (
    LlmImageFileInputPart,
    LlmImageUrlInputPart,
    LlmTextInputPart,
    OpenAIClientSettings,
    build_openai_llm_adapter,
)

adapter = build_openai_llm_adapter(
    settings=OpenAIClientSettings(
        base_url="https://api.openai.com/v1",
        api_key="...",
    ),
    model="gpt-4.1-mini",
)

result = adapter.generate_text_from_input(
    developer_prompt="You are a concise vision assistant.",
    user_input_parts=[
        LlmTextInputPart(text="Describe the image in one sentence."),
        LlmImageUrlInputPart(url="https://example.com/image.png"),
    ],
)

local_result = adapter.generate_text_from_input(
    developer_prompt="You are a concise vision assistant.",
    user_input_parts=[
        LlmTextInputPart(text="Describe the image in one sentence."),
        LlmImageFileInputPart(path="examples/cat.png"),
    ],
)
```

The local-file variant reads the image at the adapter boundary, infers an image MIME type from the filename, and sends it to the provider as an inline data URL. The existing `generate_text(...)` method remains the simplest text-only convenience API.

## OpenAI Responses Batch API

The shared `LlmAdapter` also supports OpenAI's asynchronous Batch API for the Responses endpoint. This preserves the synchronous `generate_text()` and `extract_json()` methods while adding separate batch submission and retrieval methods for lower-cost bulk execution.

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

Once the batch completes, callers can retrieve parsed plain-text or structured results with `get_text_batch_result()` or `get_structured_batch_result()`. Execution is asynchronous and OpenAI-specific under the hood, but it remains exposed through the same shared adapter package.

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

## Debug JSON artifacts

When `debug_json_enabled=True`, the factory automatically creates a `JsonFileWriterAdapter` and writes formatted request and response snapshots to `artifacts/llm-debug`.

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

## Compliance notes

This repository follows the active `.clinerules` profile for Python hexagonal projects.

One intentional exception currently remains: `src/llmframe/adapters/output/llm/providers/openai/transport/adapter.py` is larger than the preferred module-size guidance. It is retained as a single module for now to preserve a cohesive OpenAI transport implementation while the public transport surface and test coverage stabilize. Future refactoring may split retry, debug, and batch helpers into narrower transport submodules without changing public imports.

## On-demand live integration tests

The repository also includes opt-in live integration tests for the main OpenAI-backed flows:

- single-request text generation
- single-request image-input text generation
- single-request structured JSON extraction
- batch submission plus status/result retrieval

These tests are intentionally excluded from normal development runs and run only when you opt in with environment variables.

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

Run only the image-input live test with:

```bash
LLMFRAME_RUN_ON_DEMAND_INTEGRATION=1 OPENAI_API_KEY=... uv run pytest -m "integration and on_demand" tests/integration/openai_live/test_image_input.py
```

Those tests use tiny hosted, inline, and local image inputs to keep requests cheap while exercising the supported image-input paths.

For the live batch workflow, the submission test persists batch metadata under `artifacts/llm-batches`. The retrieval test can then read a previously submitted batch either from the newest persisted record or from an explicit batch ID provided via `LLMFRAME_TEST_BATCH_ID`.

Useful live batch commands:

```bash
LLMFRAME_RUN_ON_DEMAND_INTEGRATION=1 OPENAI_API_KEY=... uv run pytest -m "integration and on_demand" tests/integration/openai_live/test_batch_submission.py
```

```bash
LLMFRAME_RUN_ON_DEMAND_INTEGRATION=1 OPENAI_API_KEY=... uv run pytest -m "integration and on_demand" tests/integration/openai_live/test_batch_result_retrieval.py
```

These tests use short prompts and tiny expected outputs to keep token usage minimal.

## Manual GitHub Actions live integration workflow

Maintainers can also run the on-demand OpenAI live suite from GitHub Actions with the manual workflow at `.github/workflows/integration_openai_live.yaml`.

Before using it, configure the repository secret:

- `OPENAI_API_KEY`

The workflow exposes `workflow_dispatch` inputs for:

- `target` - choose `all`, `text_generation`, `structured_extraction`, `batch_submission`, or `batch_result_retrieval`
- `python_version` - choose the Python runtime for the run
- `model` and `base_url` - optional OpenAI configuration overrides
- `batch_id` - optional explicit batch ID for retrieval runs
- `batch_wait_timeout_seconds` and `batch_poll_interval_seconds` - optional batch polling controls

For retrieval-only runs, provide `batch_id` unless the job environment already has access to previously persisted batch metadata. In GitHub Actions, an explicit batch ID is the reliable option because workflow runs do not share local artifacts by default.
