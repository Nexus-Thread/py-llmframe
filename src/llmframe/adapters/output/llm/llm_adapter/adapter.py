"""Public façade for shared LLM adapter operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from llmframe.application.llm import LlmService

if TYPE_CHECKING:
    from llmframe.application.ports import BatchRequestStorePort, JsonArtifactWriterPort, LlmProviderPort


class LlmAdapter(LlmService):
    """Backward-compatible façade for the application ``LlmService``."""

    def __init__(
        self,
        *,
        client: LlmProviderPort,
        model: str,
        debug_json_writer: JsonArtifactWriterPort | None = None,
        batch_request_store: BatchRequestStorePort | None = None,
        debug_json_enabled: bool = False,
    ) -> None:
        super().__init__(
            provider=client,
            model=model,
            debug_json_writer=debug_json_writer,
            batch_request_store=batch_request_store,
            debug_json_enabled=debug_json_enabled,
        )
