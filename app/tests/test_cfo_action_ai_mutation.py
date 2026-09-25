from pathlib import Path
from typing import Any

import pytest

from app.services.ai_question_engine import (
    AIQuestionEngine,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)
from app.services.cfo_action_history import (
    CFOActionHistoryService,
)


# ==================================================
# STUBS
# ==================================================


class _QuestionClassifier:
    def classify(
        self,
        *,
        question: str,
    ) -> dict[str, str]:
        return {
            "intent": "unknown",
            "domain": "unknown",
        }


class _WorkspaceService:
    def __init__(
        self,
        *,
        financial_model_folder: Path,
        ai_knowledge_folder: Path,
    ) -> None:
        self.financial_model_folder = (
            financial_model_folder
        )
        self.ai_knowledge_folder = (
            ai_knowledge_folder
        )

    def get_workspace_by_organisation(
        self,
        *,
        organisation_id: str,
    ) -> dict[str, Any]:
        return {
            "paths": {
                "financial_model": str(
                    self.financial_model_folder
                ),
                "ai_knowledge": str(
                    self.ai_knowledge_folder
                ),
            }
        }


class _KnowledgeReader:
    def get_summary(
        self,
        *,
        folder: Path,
    ) -> dict[str, Any]:
        return {
            "status": "available",
            "organisation_name": "Test NGO",
            "currency": "USD",
        }


class _FinancialModelService:
    @staticmethod
    def load_json(
        *,
        financial_model_folder: Path,
        filename: str,
    ) -> Any:
        return None


def _build_engine(
    *,
    financial_model_folder: Path,
    ai_knowledge_folder: Path,
) -> AIQuestionEngine:
    engine = AIQuestionEngine.__new__(
        AIQuestionEngine
    )

    engine.question_classifier = (
        _QuestionClassifier()
    )

    engine.workspace_service = (
        _WorkspaceService(
            financial_model_folder=(
                financial_model_folder
            ),
            ai_knowledge_folder=(
                ai_knowledge_folder
            ),
        )
    )

    engine.knowledge_reader = (
        _KnowledgeReader()
    )

    engine.financial_model_service = (
        _FinancialModelService()
    )

    return engine


def _create_action(
    folder: Path,
    *,
    title: str,
) -> dict[str, Any]:
    return CFOActionPlanService.create_action(
        financial_model_folder=folder,
        title=title,
        description=(
            f"Management action for {title}."
        ),
        priority="High",
        category="Financial Management",
    )


def _get_action(
    folder: Path,
    action_id: str,
) -> dict[str, Any]:
    action = CFOActionPlanService.get_action(
        financial_model_folder=folder,
        action_id=action_id,
    )

    assert action is not None

    return action


# ==================================================
# ASSIGN
# ==================================================


def test_ai_question_engine_assigns_action(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "Assign the funding gap action to Elie."
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"
    assert (
        result["intent"]
        == "cfo_action_command"
    )
    assert (
        result["domain"]
        == "management"
    )
    assert (
        result["management_state_changed"]
        is True
    )
    assert (
        result["financial_data_used"]
        is False
    )

    persisted = _get_action(
        financial_model_folder,
        action["action_id"],
    )

    assert persisted["owner"] == "Elie"


# ==================================================
# DUE DATE
# ==================================================


def test_ai_question_engine_sets_due_date(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "Set the funding gap action due date "
            "to 2026-09-30."
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    persisted = _get_action(
        financial_model_folder,
        action["action_id"],
    )

    assert (
        persisted["due_date"]
        == "2026-09-30"
    )


# ==================================================
# START / PROGRESS
# ==================================================


def test_ai_question_engine_starts_action(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "Start the funding gap action."
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    persisted = _get_action(
        financial_model_folder,
        action["action_id"],
    )

    assert (
        persisted["status"]
        == "in_progress"
    )


def test_ai_question_engine_updates_progress(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    engine.answer(
        question=(
            "Start the funding gap action."
        ),
        organisation_id="org-1",
    )

    result = engine.answer(
        question=(
            "Update the funding gap action "
            "to 60% complete."
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    persisted = _get_action(
        financial_model_folder,
        action["action_id"],
    )

    assert (
        persisted["progress_percentage"]
        == 60.0
    )


# ==================================================
# BLOCK / UNBLOCK
# ==================================================


def test_ai_question_engine_blocks_action(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "Block the funding gap action - "
            "waiting for donor response."
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    persisted = _get_action(
        financial_model_folder,
        action["action_id"],
    )

    assert persisted["status"] == "blocked"
    assert (
        persisted["management_notes"]
        == "waiting for donor response"
    )


def test_ai_question_engine_unblocks_action(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    engine.answer(
        question=(
            "Block the funding gap action."
        ),
        organisation_id="org-1",
    )

    result = engine.answer(
        question=(
            "Unblock the funding gap action."
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    persisted = _get_action(
        financial_model_folder,
        action["action_id"],
    )

    assert (
        persisted["status"]
        == "in_progress"
    )


# ==================================================
# COMPLETE / REOPEN / CANCEL
# ==================================================


def test_ai_question_engine_completes_action(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "Complete the funding gap action."
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    persisted = _get_action(
        financial_model_folder,
        action["action_id"],
    )

    assert persisted["status"] == "completed"
    assert (
        persisted["progress_percentage"]
        == 100
    )
    assert persisted["completed_at"] is not None


def test_ai_question_engine_reopens_action(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    engine.answer(
        question=(
            "Complete the funding gap action."
        ),
        organisation_id="org-1",
    )

    result = engine.answer(
        question=(
            "Reopen the funding gap action."
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    persisted = _get_action(
        financial_model_folder,
        action["action_id"],
    )

    assert persisted["status"] == "open"
    assert persisted["completed_at"] is None


def test_ai_question_engine_cancels_action(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "Cancel the funding gap action: "
            "no longer required."
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    persisted = _get_action(
        financial_model_folder,
        action["action_id"],
    )

    assert persisted["status"] == "cancelled"
    assert (
        persisted["management_notes"]
        == "no longer required"
    )


# ==================================================
# SAFETY — AMBIGUITY
# ==================================================


def test_ai_question_engine_ambiguous_command_does_not_mutate(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action_1 = _create_action(
        financial_model_folder,
        title="Review current funding gap",
    )

    action_2 = _create_action(
        financial_model_folder,
        title="Review future funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "Assign the funding gap action to Elie."
        ),
        organisation_id="org-1",
    )

    assert (
        result["status"]
        == "not_executed"
    )
    assert (
        result["management_state_changed"]
        is False
    )

    persisted_1 = _get_action(
        financial_model_folder,
        action_1["action_id"],
    )

    persisted_2 = _get_action(
        financial_model_folder,
        action_2["action_id"],
    )

    assert persisted_1["owner"] is None
    assert persisted_2["owner"] is None


# ==================================================
# SAFETY — INVALID TRANSITION
# ==================================================


def test_ai_question_engine_invalid_transition_does_not_mutate(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    engine.answer(
        question=(
            "Complete the funding gap action."
        ),
        organisation_id="org-1",
    )

    result = engine.answer(
        question=(
            "Start the funding gap action."
        ),
        organisation_id="org-1",
    )

    assert (
        result["status"]
        == "not_executed"
    )
    assert (
        result["management_state_changed"]
        is False
    )

    persisted = _get_action(
        financial_model_folder,
        action["action_id"],
    )

    assert persisted["status"] == "completed"


# ==================================================
# SAFETY — NORMAL QUESTION
# ==================================================


def test_normal_question_is_not_treated_as_mutation_command(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "What is the status of the funding gap action?"
        ),
        organisation_id="org-1",
    )

    assert (
        result["intent"]
        != "cfo_action_command"
    )
    assert (
        result.get(
            "management_state_changed"
        )
        is not True
    )
# ==================================================
# HISTORY PROVENANCE — ASK CFO
# ==================================================


def test_ask_cfo_assignment_records_ask_cfo_source(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "Assign the funding gap action "
            "to Wassim."
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"
    assert (
        result["management_state_changed"]
        is True
    )

    events = (
        CFOActionHistoryService.list_action_events(
            financial_model_folder=(
                financial_model_folder
            ),
            action_id=action["action_id"],
        )
    )

    owner_events = [
        event
        for event in events
        if (
            event.get("event_type")
            == "owner_changed"
        )
    ]

    assert len(owner_events) == 1

    assert (
        owner_events[0]["new_value"]
        == "Wassim"
    )

    assert owner_events[0]["actor"] is None

    assert (
        owner_events[0]["source"]
        == "ask_cfo"
    )


def test_ask_cfo_assignee_is_not_history_actor(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "Assign the funding gap action "
            "to Elie."
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    events = (
        CFOActionHistoryService.list_action_events(
            financial_model_folder=(
                financial_model_folder
            ),
            action_id=action["action_id"],
        )
    )

    owner_events = [
        event
        for event in events
        if (
            event.get("event_type")
            == "owner_changed"
        )
    ]

    assert len(owner_events) == 1

    owner_event = owner_events[0]

    assert (
        owner_event["new_value"]
        == "Elie"
    )

    # The assignee is NOT the actor.
    # Authenticated user identity is not wired yet.
    assert owner_event["actor"] is None

    assert (
        owner_event["source"]
        == "ask_cfo"
    )


def test_rejected_ask_cfo_command_creates_no_history_event(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = _create_action(
        financial_model_folder,
        title="Review funding gap",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    before_events = (
        CFOActionHistoryService.list_action_events(
            financial_model_folder=(
                financial_model_folder
            ),
            action_id=action["action_id"],
        )
    )

    result = engine.answer(
        question="Assign it to Wassim.",
        organisation_id="org-1",
    )

    after_events = (
        CFOActionHistoryService.list_action_events(
            financial_model_folder=(
                financial_model_folder
            ),
            action_id=action["action_id"],
        )
    )

    assert (
        result.get(
            "management_state_changed"
        )
        is not True
    )

    assert before_events == after_events