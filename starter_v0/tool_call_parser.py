from __future__ import annotations

import json
from typing import Any

from providers.base import ToolCall


MARKER = "TOOL_CALLS_JSON:"


def _json_after_marker(text: str) -> Any | None:
    marker_index = text.find(MARKER)
    if marker_index < 0:
        return None

    payload = text[marker_index + len(MARKER):].strip()
    if payload.startswith("```"):
        lines = payload.splitlines()
        payload = "\n".join(lines[1:])
        fence_index = payload.find("```")
        if fence_index >= 0:
            payload = payload[:fence_index]
        payload = payload.strip()

    try:
        value, _ = json.JSONDecoder().raw_decode(payload)
    except json.JSONDecodeError:
        return None
    return value


def parse_tool_calls_from_text(text: str | None) -> list[ToolCall]:
    if not text:
        return []

    value = _json_after_marker(text)
    if value is None:
        return []

    raw_calls = value.get("tool_calls") if isinstance(value, dict) else value
    if not isinstance(raw_calls, list):
        return []

    calls: list[ToolCall] = []
    for item in raw_calls:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        args = item.get("args", {})
        if isinstance(name, str) and isinstance(args, dict):
            calls.append(ToolCall(name=name, args=args))
    return calls
