from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from steve_thought_capture.models import VoiceEvent
from steve_thought_capture.pipeline import process_voice_event


_MIME_BY_SUFFIX = {
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".flac": "audio/flac",
    ".opus": "audio/opus",
}


def _infer_mime_type(audio_path: Path) -> str:
    return _MIME_BY_SUFFIX.get(audio_path.suffix.lower(), "application/octet-stream")


def build_local_voice_event(audio_path: str | Path) -> VoiceEvent:
    resolved = Path(audio_path).expanduser().resolve()
    return VoiceEvent(
        platform="local-smoke",
        chat_id="local-smoke",
        thread_id=None,
        user_id="steve",
        message_id=resolved.stem,
        audio_path=str(resolved),
        mime_type=_infer_mime_type(resolved),
        duration_seconds=None,
        received_at=datetime.now(timezone.utc).isoformat(),
    )



def run_local_voice_event(audio_path: str | Path, steve_context: dict) -> dict:
    event = build_local_voice_event(audio_path)
    return process_voice_event(event, steve_context)
