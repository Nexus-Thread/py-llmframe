"""Input builders for the shared LLM adapter."""

from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import TYPE_CHECKING

from .dto import LlmFileInputPart, LlmImageFileInputPart, LlmImageUrlInputPart, LlmTextInputPart
from .exceptions import StructuredLlmError

if TYPE_CHECKING:
    from collections.abc import Sequence

    from llmframe.application.ports import LlmContentPart, LlmInputItem

SUPPORTED_LOCAL_FILE_MIME_TYPES = {
    ".pdf": "application/pdf",
    ".txt": "text/plain",
    ".md": "text/markdown",
    ".json": "application/json",
    ".html": "text/html",
    ".xml": "application/xml",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".rtf": "application/rtf",
    ".odt": "application/vnd.oasis.opendocument.text",
    ".ppt": "application/vnd.ms-powerpoint",
    ".pptx": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
    ".csv": "text/csv",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}
SUPPORTED_LOCAL_FILE_EXTENSIONS = frozenset(SUPPORTED_LOCAL_FILE_MIME_TYPES.keys())
SUPPORTED_LOCAL_FILE_EXTENSIONS_MESSAGE = ", ".join(sorted(SUPPORTED_LOCAL_FILE_EXTENSIONS))


def build_inputs(*, developer_prompt: str, user_prompt: str) -> list[LlmInputItem]:
    """Build the standard developer/user prompt input sequence."""
    return [
        {"role": "developer", "content": developer_prompt},
        {"role": "user", "content": user_prompt},
    ]


def build_multimodal_inputs(
    *,
    developer_prompt: str,
    user_input_parts: Sequence[LlmTextInputPart | LlmImageUrlInputPart | LlmImageFileInputPart | LlmFileInputPart],
) -> list[LlmInputItem]:
    """Build inputs for mixed text, image, and local-file user content."""
    return [
        {"role": "developer", "content": developer_prompt},
        {"role": "user", "content": build_user_content_parts(user_input_parts=user_input_parts)},
    ]


def build_user_content_parts(
    *,
    user_input_parts: Sequence[LlmTextInputPart | LlmImageUrlInputPart | LlmImageFileInputPart | LlmFileInputPart],
) -> list[LlmContentPart]:
    """Normalize high-level multimodal input parts into provider-neutral content parts."""
    content_parts: list[LlmContentPart] = []
    for input_part in user_input_parts:
        if isinstance(input_part, LlmTextInputPart):
            content_parts.append({"type": "input_text", "text": input_part.text})
            continue
        if isinstance(input_part, LlmImageUrlInputPart):
            content_parts.append({"type": "input_image", "image_url": input_part.url})
            continue
        if isinstance(input_part, LlmImageFileInputPart):
            content_parts.append({"type": "input_image", "image_url": build_image_data_url(input_part.path)})
            continue
        if isinstance(input_part, LlmFileInputPart):
            content_parts.append(build_file_content_part(input_part.path))
            continue

        msg = f"Unsupported multimodal input part: {type(input_part).__name__}"
        raise StructuredLlmError(
            msg,
            suggestion="Pass only text, image URL, local image file, or supported local file input parts",
        )
    return content_parts


def require_existing_file(file_path: str | Path, *, kind_label: str) -> Path:
    """Return an existing regular file path or raise a shared adapter error."""
    path = Path(file_path)
    if not path.exists():
        msg = f"{kind_label} does not exist: {path}"
        raise StructuredLlmError(msg, suggestion=f"Pass a valid local {kind_label.lower()} path")
    if not path.is_file():
        msg = f"{kind_label} is not a file: {path}"
        raise StructuredLlmError(msg, suggestion=f"Pass a path to a regular {kind_label.lower()}")
    return path


def build_image_data_url(image_path: str | Path) -> str:
    """Encode a local image file as a data URL content value."""
    file_path = require_existing_file(image_path, kind_label="Image file")

    mime_type, _ = mimetypes.guess_type(file_path.name)
    if mime_type is None or not mime_type.startswith("image/"):
        msg = f"Unsupported image file type: {file_path}"
        raise StructuredLlmError(msg, suggestion="Use a local image file with a recognized image extension")

    try:
        image_bytes = file_path.read_bytes()
    except OSError as err:
        msg = f"Failed to read image file: {file_path}"
        raise StructuredLlmError(msg, suggestion="Ensure the image file is readable") from err

    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def build_file_content_part(file_path: str | Path) -> LlmContentPart:
    """Encode a supported local file as an LLM file content part."""
    path = require_existing_file(file_path, kind_label="File")
    suffix = path.suffix.lower()
    if suffix not in SUPPORTED_LOCAL_FILE_EXTENSIONS:
        msg = f"Unsupported file type: {path}"
        raise StructuredLlmError(
            msg,
            suggestion=f"Use one of the supported file extensions: {SUPPORTED_LOCAL_FILE_EXTENSIONS_MESSAGE}",
        )

    try:
        file_bytes = path.read_bytes()
    except OSError as err:
        msg = f"Failed to read file: {path}"
        raise StructuredLlmError(msg, suggestion="Ensure the file is readable") from err

    mime_type = SUPPORTED_LOCAL_FILE_MIME_TYPES[suffix]
    encoded = base64.b64encode(file_bytes).decode("ascii")

    return {
        "type": "input_file",
        "file_data": f"data:{mime_type};base64,{encoded}",
        "filename": path.name,
    }
