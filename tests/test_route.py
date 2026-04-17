from steve_thought_capture.models import IntentDecision
from steve_thought_capture.route import plan_actions


def _decision(intent):
    return IntentDecision(
        primary_intent=intent,
        secondary_intents=[],
        confidence=0.9,
        needs_clarification=False,
        clarification_question=None,
        extracted_entities={},
    )


def test_route_conversation_reply_creates_reply_action():
    actions = plan_actions(_decision("conversation_reply"), {})
    assert actions[0].action_type == "reply"


def test_route_note_capture_creates_note_action():
    actions = plan_actions(_decision("note_capture"), {})
    assert actions[0].action_type == "note_capture"


def test_route_task_capture_creates_task_action():
    actions = plan_actions(_decision("task_capture"), {})
    assert actions[0].action_type == "task_capture"


def test_route_project_artifact_input_creates_project_action():
    actions = plan_actions(_decision("project_artifact_input"), {})
    assert actions[0].action_type == "project_artifact_input"


def test_route_knowledge_capture_creates_knowledge_action():
    actions = plan_actions(_decision("knowledge_capture"), {})
    assert actions[0].action_type == "knowledge_capture"
