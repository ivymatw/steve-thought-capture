from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def _to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return {key: _to_jsonable(val) for key, val in asdict(value).items()}
    if isinstance(value, dict):
        return {key: _to_jsonable(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


def append_learning_event(
    voice_event,
    prepared_audio,
    transcript_result,
    normalized_transcript,
    intent_decision,
    action_plan,
    context: dict,
) -> Path:
    learning_cfg = context.get("learning", {})
    log_path = Path(learning_cfg.get("log_path", "logs/learning.jsonl")).expanduser()
    log_path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "voice_event": _to_jsonable(voice_event),
        "prepared_audio": _to_jsonable(prepared_audio),
        "transcript_result": _to_jsonable(transcript_result),
        "raw_transcript": transcript_result.raw_text,
        "normalized_transcript": normalized_transcript.normalized_text,
        "intent_decision": _to_jsonable(intent_decision),
        "action_plan": _to_jsonable(action_plan),
    }
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return log_path
