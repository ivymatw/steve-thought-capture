from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class VoiceEvent:
    platform: str
    chat_id: str
    thread_id: str | None
    user_id: str
    message_id: str
    audio_path: str
    mime_type: str
    duration_seconds: float | None
    received_at: Any


@dataclass(frozen=True)
class PreparedAudio:
    original_audio_path: str
    prepared_audio_path: str
    original_format: str
    prepared_format: str
    conversion_performed: bool


@dataclass(frozen=True)
class TranscriptResult:
    success: bool
    raw_text: str
    backend: str
    model: str
    language_mode: str
    latency_ms: int
    error: str | None


@dataclass(frozen=True)
class NormalizedTranscript:
    raw_text: str
    normalized_text: str
    applied_rules: list[str]
    uncertainty_flags: list[str]


@dataclass(frozen=True)
class IntentDecision:
    primary_intent: str
    secondary_intents: list[str]
    confidence: float
    needs_clarification: bool
    clarification_question: str | None
    extracted_entities: dict[str, Any]


@dataclass(frozen=True)
class PlannedAction:
    action_type: str
    target: str
    payload: dict[str, Any]
    blocking: bool
