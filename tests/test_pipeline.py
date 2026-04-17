import json

from steve_thought_capture.models import IntentDecision, NormalizedTranscript, PreparedAudio, TranscriptResult, VoiceEvent
from steve_thought_capture.pipeline import process_voice_event


class DummyContext(dict):
    pass


def test_process_voice_event_happy_path(monkeypatch):
    event = VoiceEvent("telegram", "1", None, "2", "3", "/tmp/a.ogg", "audio/ogg", 4.2, "now")
    context = DummyContext()

    monkeypatch.setattr("steve_thought_capture.pipeline.prepare_audio", lambda path: PreparedAudio(path, path, "ogg", "ogg", False))
    monkeypatch.setattr("steve_thought_capture.pipeline.transcribe_audio", lambda prepared, ctx: TranscriptResult(True, "hello", "whisper_cpp", "large-v3-turbo", "auto", 12, None))
    monkeypatch.setattr("steve_thought_capture.pipeline.normalize_transcript", lambda text, ctx: NormalizedTranscript(text, text, [], []))
    monkeypatch.setattr("steve_thought_capture.pipeline.interpret_transcript", lambda nt, ctx: IntentDecision("conversation_reply", [], 0.9, False, None, {}))
    monkeypatch.setattr("steve_thought_capture.pipeline.plan_actions", lambda decision, ctx: [{"action": "reply"}])

    result = process_voice_event(event, context)

    assert result["status"] == "ok"
    assert result["actions"] == [{"action": "reply"}]


def test_process_voice_event_returns_recoverable_asr_failure(monkeypatch):
    event = VoiceEvent("telegram", "1", None, "2", "3", "/tmp/a.ogg", "audio/ogg", 4.2, "now")
    context = DummyContext()

    monkeypatch.setattr("steve_thought_capture.pipeline.prepare_audio", lambda path: PreparedAudio(path, path, "ogg", "ogg", False))
    monkeypatch.setattr("steve_thought_capture.pipeline.transcribe_audio", lambda prepared, ctx: TranscriptResult(False, "", "whisper_cpp", "large-v3-turbo", "auto", 12, "boom"))

    result = process_voice_event(event, context)

    assert result["status"] == "asr_failed"
    assert result["error"] == "boom"


def test_process_voice_event_returns_clarification_when_needed(monkeypatch):
    event = VoiceEvent("telegram", "1", None, "2", "3", "/tmp/a.ogg", "audio/ogg", 4.2, "now")
    context = DummyContext()

    monkeypatch.setattr("steve_thought_capture.pipeline.prepare_audio", lambda path: PreparedAudio(path, path, "ogg", "ogg", False))
    monkeypatch.setattr("steve_thought_capture.pipeline.transcribe_audio", lambda prepared, ctx: TranscriptResult(True, "hello", "whisper_cpp", "large-v3-turbo", "auto", 12, None))
    monkeypatch.setattr("steve_thought_capture.pipeline.normalize_transcript", lambda text, ctx: NormalizedTranscript(text, text, [], []))
    monkeypatch.setattr("steve_thought_capture.pipeline.interpret_transcript", lambda nt, ctx: IntentDecision("conversation_reply", [], 0.4, True, "Which project?", {}))

    result = process_voice_event(event, context)

    assert result["status"] == "needs_clarification"
    assert result["clarification_question"] == "Which project?"


def test_process_voice_event_writes_learning_log(monkeypatch, tmp_path):
    event = VoiceEvent("telegram", "1", None, "2", "3", "/tmp/a.ogg", "audio/ogg", 4.2, "now")
    context = DummyContext({"learning": {"log_path": str(tmp_path / "learning.jsonl")}})

    monkeypatch.setattr("steve_thought_capture.pipeline.prepare_audio", lambda path: PreparedAudio(path, path, "ogg", "ogg", False))
    monkeypatch.setattr("steve_thought_capture.pipeline.transcribe_audio", lambda prepared, ctx: TranscriptResult(True, "hello", "whisper_cpp", "large-v3-turbo", "auto", 12, None))
    monkeypatch.setattr("steve_thought_capture.pipeline.normalize_transcript", lambda text, ctx: NormalizedTranscript(text, "HELLO", ["rule"], []))
    monkeypatch.setattr("steve_thought_capture.pipeline.interpret_transcript", lambda nt, ctx: IntentDecision("conversation_reply", [], 0.9, False, None, {"topic": "mic"}))
    monkeypatch.setattr("steve_thought_capture.pipeline.plan_actions", lambda decision, ctx: [{"action": "reply"}])

    result = process_voice_event(event, context)

    assert result["status"] == "ok"
    records = (tmp_path / "learning.jsonl").read_text().strip().splitlines()
    assert len(records) == 1
    payload = json.loads(records[0])
    assert payload["raw_transcript"] == "hello"
    assert payload["normalized_transcript"] == "HELLO"
    assert payload["intent_decision"]["primary_intent"] == "conversation_reply"
    assert payload["action_plan"] == [{"action": "reply"}]
