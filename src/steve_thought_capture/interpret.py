from __future__ import annotations

from steve_thought_capture.models import IntentDecision, NormalizedTranscript


def _matches_any(text: str, phrases: list[str]) -> bool:
    return any(phrase and phrase in text for phrase in phrases)


def interpret_transcript(transcript: NormalizedTranscript, steve_context: dict) -> IntentDecision:
    text = transcript.normalized_text
    keywords = steve_context.get("routing_preferences", {}).get("keywords", {})

    if _matches_any(text, keywords.get("note_capture", [])):
        intent = "note_capture"
    elif _matches_any(text, keywords.get("task_capture", [])):
        intent = "task_capture"
    elif _matches_any(text, keywords.get("project_artifact_input", [])):
        intent = "project_artifact_input"
    elif _matches_any(text, keywords.get("knowledge_capture", [])):
        intent = "knowledge_capture"
    elif "?" in text or "？" in text:
        intent = "conversation_reply"
    else:
        intent = "conversation_reply"

    return IntentDecision(intent, [], 0.9, False, None, {})
