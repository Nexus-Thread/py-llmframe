#!/usr/bin/env python3
"""Log PreToolUse tool arguments and always allow the tool call.

Tool argument logging is explicit and tool-specific. Extend the formatter
mapping as more tools need structured summaries.
"""

# ruff: noqa: T201
# ruff: noqa: BLE001

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path

LOG_FILE_NAME = "cline-file-activity.log"
ToolArgumentFormatter = Callable[[dict[str, object]], str]


def _stringify_one_line(value: object) -> str:
    try:
        text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    except TypeError:
        text = str(value)
    return " ".join(text.splitlines())


def _format_value(value: object) -> str:
    if value is None:
        return "N/A"
    return _stringify_one_line(value)


def _as_dict(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def _as_str(value: object, *, default: str) -> str:
    return value if isinstance(value, str) and value else default


def _get_parameter_summary(parameters: dict[str, object], *keys: str) -> str:
    if not keys:
        return "no arguments"
    return ", ".join(f"{key}={_format_value(parameters.get(key))}" for key in keys)


def _format_path_value(parameters: dict[str, object]) -> str:
    return _format_value(parameters.get("path") or parameters.get("absolutePath"))


def _format_key_values(parameters: dict[str, object], *keys: str) -> str:
    return _get_parameter_summary(parameters, *keys)


def _format_search_files(parameters: dict[str, object]) -> str:
    return _format_key_values(parameters, "path", "regex", "file_pattern")


def _format_access_mcp_resource(parameters: dict[str, object]) -> str:
    return _format_key_values(parameters, "server_name", "uri")


def _format_ask_followup_question(parameters: dict[str, object]) -> str:
    return _format_key_values(parameters, "question")


def _format_attempt_completion(parameters: dict[str, object]) -> str:
    return _format_key_values(parameters, "result", "command")


def _format_browser_action(parameters: dict[str, object]) -> str:
    return _format_key_values(parameters, "action", "url", "coordinate", "text")


def _format_execute_command(parameters: dict[str, object]) -> str:
    return _format_key_values(parameters, "command", "requires_approval")


def _format_apply_patch(parameters: dict[str, object]) -> str:
    patch_input = parameters.get("input")
    if patch_input is None:
        return "input=N/A"

    line_count = len(str(patch_input).splitlines())
    return f"input_lines={line_count}"


def _format_plan_mode_respond(parameters: dict[str, object]) -> str:
    return _format_key_values(parameters, "response")


def _format_generate_explanation(parameters: dict[str, object]) -> str:
    return _format_key_values(parameters, "title", "from_ref", "to_ref")


def _format_use_subagents(parameters: dict[str, object]) -> str:
    prompt_keys = sorted(key for key in parameters if key.startswith("prompt_") and parameters.get(key))
    return f"prompt_count={len(prompt_keys)}"


def _format_no_arguments(_: dict[str, object]) -> str:
    return "no arguments"


SUPPORTED_TOOL_ARGUMENT_FORMATTERS: dict[str, ToolArgumentFormatter] = {
    "read_file": _format_path_value,
    "apply_patch": _format_apply_patch,
    "search_files": _format_search_files,
    "list_files": _format_path_value,
    "list_code_definition_names": _format_path_value,
    "access_mcp_resource": _format_access_mcp_resource,
    "ask_followup_question": _format_ask_followup_question,
    "attempt_completion": _format_attempt_completion,
    "browser_action": _format_browser_action,
    "execute_command": _format_execute_command,
    "load_mcp_documentation": _format_no_arguments,
    "plan_mode_respond": _format_plan_mode_respond,
    "generate_explanation": _format_generate_explanation,
    "use_subagents": _format_use_subagents,
}


def get_tracked_tool_arguments(tool_name: str, parameters: dict[str, object]) -> str:
    """Return a structured argument summary for a supported tool."""
    formatter = SUPPORTED_TOOL_ARGUMENT_FORMATTERS.get(tool_name)
    if formatter:
        try:
            return formatter(parameters)
        except Exception as error:
            return f"format_error={_stringify_one_line(error)}, raw_parameters={_stringify_one_line(parameters)}"

    return f"unsupported tool, raw_parameters={_stringify_one_line(parameters)}"


def _get_tool_details(payload: dict[str, object]) -> tuple[str, str]:
    try:
        pre_tool_use = _as_dict(payload.get("preToolUse"))
        tool_name = _as_str(
            pre_tool_use.get("toolName") or pre_tool_use.get("tool"),
            default="unknown",
        )
        parameters = _as_dict(pre_tool_use.get("parameters"))
        tool_summary = get_tracked_tool_arguments(tool_name, parameters)
    except Exception as error:
        tool_name = "unknown"
        tool_summary = f"payload_error={_stringify_one_line(error)}, raw_payload={_stringify_one_line(payload)}"

    return tool_name, tool_summary


def _append_log_entry(workspace_root: str | Path, tool_name: str, tool_summary: str) -> None:
    log_dir = Path(workspace_root) / ".cline-logs"
    log_file = log_dir / LOG_FILE_NAME

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        with log_file.open("a", encoding="utf-8") as handle:
            handle.write(f"{datetime.now(tz=UTC).strftime('%H:%M:%S')} - {tool_name}: {tool_summary}\n")
    except OSError:
        pass


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"cancel": False}))
        return 0

    workspace_roots = payload.get("workspaceRoots") or []
    workspace_root = workspace_roots[0] if workspace_roots else None

    tool_name, tool_arguments = _get_tool_details(payload)

    if workspace_root:
        _append_log_entry(workspace_root, tool_name, tool_arguments)

    print(json.dumps({"cancel": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
