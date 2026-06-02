from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)


def json_pretty(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, default=str)


def init_state() -> None:
    st.session_state.setdefault("history", [])
    st.session_state.setdefault("turns", [])
    st.session_state.setdefault("transcript_path", None)
    st.session_state.setdefault("transcript", None)


def new_transcript(version: str, provider_name: str, model: str | None, system_prompt_path: Path, tools_path: Path) -> None:
    artifact_version = build_artifact_version(version, system_prompt_path, tools_path)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join([safe_slug(version), safe_slug(provider_name), "streamlit", timestamp])
    transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    st.session_state.transcript_path = transcript_path
    st.session_state.transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact_version),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(system_prompt_path),
        "tools": str(tools_path),
        "history_window": st.session_state.history_window,
        "max_tool_rounds": st.session_state.max_tool_rounds,
        "ui": "streamlit",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    write_transcript(transcript_path, st.session_state.transcript)


def save_turn(turn_record: dict[str, Any]) -> None:
    if st.session_state.transcript is None or st.session_state.transcript_path is None:
        return
    st.session_state.transcript["turns"].append(turn_record)
    write_transcript(Path(st.session_state.transcript_path), st.session_state.transcript)


def render_trace(turn: dict[str, Any]) -> None:
    rounds = turn.get("rounds", [])
    events = turn.get("tool_events", [])
    if not rounds and not events:
        return
    with st.expander("Tool trace", expanded=False):
        st.code(json_pretty({"rounds": rounds, "tool_events": events}), language="json")


def main() -> None:
    st.set_page_config(page_title="Lab 4 Research Agent", layout="wide")
    init_state()

    st.title("Lab 4 Research Agent")

    with st.sidebar:
        provider_name = st.selectbox("Provider", ["openai", "openrouter", "anthropic", "gemini"], index=0)
        st.session_state.history_window = st.number_input("History window", min_value=0, max_value=20, value=5)
        st.session_state.max_tool_rounds = st.number_input("Max tool rounds", min_value=1, max_value=8, value=4)
        reset = st.button("New transcript")

    version = "v3"
    system_prompt_file = ARTIFACTS_DIR / "system_prompt.md"
    tools_file = ARTIFACTS_DIR / "tools.yaml"
    model_arg = None

    if reset or st.session_state.transcript is None:
        provider_for_model = make_provider(provider_name)
        selected_model = model_arg or getattr(provider_for_model, "default_model", None)
        st.session_state.history = []
        st.session_state.turns = []
        new_transcript(version, provider_name, selected_model, system_prompt_file, tools_file)

    for turn in st.session_state.turns:
        with st.chat_message("user"):
            st.markdown(turn["user"])
        with st.chat_message("assistant"):
            st.markdown(turn.get("assistant_text") or "")
            render_trace(turn)

    user_text = st.chat_input("Ask a research question...")
    if not user_text:
        return

    with st.chat_message("user"):
        st.markdown(user_text)

    turn_index = len(st.session_state.turns) + 1
    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    try:
        provider = make_provider(provider_name)
        system_prompt = system_prompt_file.read_text(encoding="utf-8")
        openai_tools = to_openai_tools(load_tool_declarations(tools_file))
        messages = [
            {"role": "system", "content": system_prompt},
            *trim_history(st.session_state.history, int(st.session_state.history_window)),
            {"role": "user", "content": user_text},
        ]
        result = run_model_tool_loop(
            provider=provider,
            messages=messages,
            tools=openai_tools,
            model=model_arg,
            max_tool_rounds=int(st.session_state.max_tool_rounds),
        )
        turn_record.update(result)
        assistant_text = result["assistant_text"]
        st.session_state.history.append({"role": "user", "content": user_text})
        st.session_state.history.append({"role": "assistant", "content": assistant_text})
    except Exception as exc:
        turn_record.update({
            "status": "provider_error",
            "error": f"{type(exc).__name__}: {str(exc)}",
            "assistant_text": f"ERROR: {type(exc).__name__}: {str(exc)}",
        })

    turn_record["ended_at"] = now_iso()
    st.session_state.turns.append(turn_record)
    save_turn(turn_record)

    with st.chat_message("assistant"):
        st.markdown(turn_record.get("assistant_text") or "")
        render_trace(turn_record)


if __name__ == "__main__":
    main()
