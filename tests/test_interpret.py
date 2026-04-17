from steve_thought_capture.interpret import interpret_transcript
from steve_thought_capture.models import NormalizedTranscript


class DummyContext(dict):
    pass


def test_interpret_conversation_reply_for_question():
    transcript = NormalizedTranscript("raw", "這是什麼意思?", [], [])
    decision = interpret_transcript(transcript, DummyContext(routing_preferences={"keywords": {"note_capture": [], "task_capture": [], "knowledge_capture": [], "project_artifact_input": []}}))
    assert decision.primary_intent == "conversation_reply"


def test_interpret_note_capture_for_store_phrase():
    transcript = NormalizedTranscript("raw", "這個想法存一下", [], [])
    decision = interpret_transcript(transcript, DummyContext(routing_preferences={"keywords": {"note_capture": ["存一下"], "task_capture": [], "knowledge_capture": [], "project_artifact_input": []}}))
    assert decision.primary_intent == "note_capture"


def test_interpret_task_capture_for_imperative():
    transcript = NormalizedTranscript("raw", "提醒我明天打給 Rose", [], [])
    decision = interpret_transcript(transcript, DummyContext(routing_preferences={"keywords": {"note_capture": [], "task_capture": ["提醒我"], "knowledge_capture": [], "project_artifact_input": []}}))
    assert decision.primary_intent == "task_capture"


def test_interpret_project_artifact_for_explicit_project_update():
    transcript = NormalizedTranscript("raw", "把這段加到 steve thought capture spec", [], [])
    decision = interpret_transcript(transcript, DummyContext(routing_preferences={"keywords": {"note_capture": [], "task_capture": [], "knowledge_capture": [], "project_artifact_input": ["spec"]}}))
    assert decision.primary_intent == "project_artifact_input"


def test_interpret_knowledge_capture_for_insight_statement():
    transcript = NormalizedTranscript("raw", "我覺得這件事真正的差異在於 routing 不在 ASR", [], [])
    decision = interpret_transcript(transcript, DummyContext(routing_preferences={"keywords": {"note_capture": [], "task_capture": [], "knowledge_capture": ["真正的差異"], "project_artifact_input": []}}))
    assert decision.primary_intent == "knowledge_capture"
