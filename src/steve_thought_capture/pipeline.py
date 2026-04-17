from __future__ import annotations

from steve_thought_capture.audio_prepare import prepare_audio
from steve_thought_capture.interpret import interpret_transcript
from steve_thought_capture.normalize import normalize_transcript
from steve_thought_capture.route import plan_actions
from steve_thought_capture.transcription import transcribe_audio


def process_voice_event(voice_event, steve_context: dict) -> dict:
    prepared = prepare_audio(voice_event.audio_path)
    transcript_result = transcribe_audio(prepared, steve_context)
    if not transcript_result.success:
        return {
            "status": "asr_failed",
            "error": transcript_result.error,
            "prepared_audio": prepared,
            "transcript_result": transcript_result,
        }

    normalized = normalize_transcript(transcript_result.raw_text, steve_context)
    decision = interpret_transcript(normalized, steve_context)
    if decision.needs_clarification:
        return {
            "status": "needs_clarification",
            "clarification_question": decision.clarification_question,
            "prepared_audio": prepared,
            "transcript_result": transcript_result,
            "normalized_transcript": normalized,
            "intent_decision": decision,
        }

    actions = plan_actions(decision, steve_context)
    return {
        "status": "ok",
        "prepared_audio": prepared,
        "transcript_result": transcript_result,
        "normalized_transcript": normalized,
        "intent_decision": decision,
        "actions": actions,
    }
