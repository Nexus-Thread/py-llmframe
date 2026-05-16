"""Compatibility re-exports for LLM application input builders."""

from __future__ import annotations

from llmframe.application.llm.input_builders import (
    SUPPORTED_LOCAL_FILE_EXTENSIONS,
    SUPPORTED_LOCAL_FILE_EXTENSIONS_MESSAGE,
    SUPPORTED_LOCAL_FILE_MIME_TYPES,
    build_file_content_part,
    build_image_data_url,
    build_inputs,
    build_multimodal_inputs,
    build_user_content_parts,
    require_existing_file,
)

__all__ = [
    "SUPPORTED_LOCAL_FILE_EXTENSIONS",
    "SUPPORTED_LOCAL_FILE_EXTENSIONS_MESSAGE",
    "SUPPORTED_LOCAL_FILE_MIME_TYPES",
    "build_file_content_part",
    "build_image_data_url",
    "build_inputs",
    "build_multimodal_inputs",
    "build_user_content_parts",
    "require_existing_file",
]
