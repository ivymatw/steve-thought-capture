from __future__ import annotations

from steve_thought_capture.models import PlannedAction


ACTION_MAP = {
    "conversation_reply": "reply",
    "note_capture": "note_capture",
    "task_capture": "task_capture",
    "project_artifact_input": "project_artifact_input",
    "knowledge_capture": "knowledge_capture",
}


def plan_actions(intent_decision, context) -> list[PlannedAction]:
    action_type = ACTION_MAP[intent_decision.primary_intent]
    return [PlannedAction(action_type=action_type, target="default", payload={}, blocking=True)]
