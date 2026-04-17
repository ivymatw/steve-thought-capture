from steve_thought_capture.models import (
    IntentDecision,
    NormalizedTranscript,
    PlannedAction,
    PreparedAudio,
    TranscriptResult,
    VoiceEvent,
)


def test_voice_event_dataclass_construction():
    event = VoiceEvent(
        platform="telegram",
        chat_id="1",
        thread_id=None,
        user_id="2",
        message_id="3",
        audio_path="/tmp/a.ogg",
        mime_type="audio/ogg",
        duration_seconds=4.2,
        received_at="2026-04-17T00:00:00",
    )
    assert event.audio_path == "/tmp/a.ogg"


def test_prepared_audio_dataclass_construction():
    audio = PreparedAudio(
        original_audio_path="/tmp/a.ogg",
        prepared_audio_path="/tmp/a.wav",
        original_format="ogg",
        prepared_format="wav",
        conversion_performed=True,
    )
    assert audio.conversion_performed is True


def test_transcript_result_dataclass_construction():
    result = TranscriptResult(
        success=True,
        raw_text="hello",
        backend="whisper_cpp",
        model="large-v3-turbo",
        language_mode="auto",
        latency_ms=123,
        error=None,
    )
    assert result.model == "large-v3-turbo"


def test_normalized_transcript_dataclass_construction():
    result = NormalizedTranscript(
        raw_text="麦克风",
        normalized_text="麥克風",
        applied_rules=["s2t"],
        uncertainty_flags=[],
    )
    assert result.normalized_text == "麥克風"


def test_intent_decision_dataclass_construction():
    decision = IntentDecision(
        primary_intent="conversation_reply",
        secondary_intents=[],
        confidence=0.9,
        needs_clarification=False,
        clarification_question=None,
        extracted_entities={},
    )
    assert decision.primary_intent == "conversation_reply"


def test_planned_action_dataclass_construction():
    action = PlannedAction(
        action_type="reply",
        target="telegram",
        payload={"text": "hi"},
        blocking=True,
    )
    assert action.payload["text"] == "hi"
