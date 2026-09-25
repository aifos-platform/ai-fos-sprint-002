from copy import deepcopy
from pathlib import Path
from typing import Any

from app.services.ai_question_engine import (
    AIQuestionEngine,
)
from app.services.cfo_action_history import (
    CFOActionHistoryService,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)


# ==================================================
# STUBS
# ==================================================


class _QuestionClassifier:
    def __init__(
        self,
        intent: str,
    ) -> None:
        self.intent = intent

    def classify(
        self,
        *,
        question: str,
    ) -> dict[str, str]:
        return {
            "domain": "cfo_action_plan",
            "intent": self.intent,
            "target": "cfo_action_performance",
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


# ==================================================
# HELPERS
# ==================================================


def _build_engine(
    *,
    financial_model_folder: Path,
    ai_knowledge_folder: Path,
    intent: str,
) -> AIQuestionEngine:
    engine = AIQuestionEngine.__new__(
        AIQuestionEngine
    )

    engine.question_classifier = (
        _QuestionClassifier(
            intent
        )
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


def _record(
    *,
    folder: Path,
    action_id: str,
    event_type: str,
    previous_value: Any = None,
    new_value: Any = None,
) -> None:
    CFOActionHistoryService.record_event(
        financial_model_folder=folder,
        action_id=action_id,
        event_type=event_type,
        previous_value=previous_value,
        new_value=new_value,
    )


# ==================================================
# PERFORMANCE SUMMARY
# ==================================================


def test_ai_question_engine_action_performance_summary(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    _record(
        folder=financial_model_folder,
        action_id="A1",
        event_type="action_created",
    )

    _record(
        folder=financial_model_folder,
        action_id="A1",
        event_type="status_changed",
        previous_value="in_progress",
        new_value="completed",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
        intent="action_performance_summary",
    )

    result = engine.answer(
        question=(
            "How is our action plan performing?"
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "action_performance_summary"
    )

    assert (
        result["domain"]
        == "cfo_action_plan"
    )

    assert "2 recorded history event" in (
        result["answer"]
    )

    assert "1 action(s)" in (
        result["answer"]
    )

    assert (
        result.get(
            "management_state_changed"
        )
        is not True
    )

    assert (
        result["financial_data_used"]
        is False
    )


# ==================================================
# REOPENING PATTERN
# ==================================================


def test_ai_question_engine_reopened_action_patterns(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    _record(
        folder=financial_model_folder,
        action_id="A1",
        event_type="status_changed",
        previous_value="in_progress",
        new_value="completed",
    )

    _record(
        folder=financial_model_folder,
        action_id="A1",
        event_type="status_changed",
        previous_value="completed",
        new_value="open",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
        intent="reopened_action_patterns",
    )

    result = engine.answer(
        question=(
            "Which actions keep reopening?"
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    assert (
        "reopening after completion"
        in result["answer"]
    )

    assert "Action A1" in result["answer"]

    assert (
        result.get(
            "management_state_changed"
        )
        is not True
    )


# ==================================================
# REPEATED BLOCKING
# ==================================================


def test_ai_question_engine_repeated_blocking_patterns(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    _record(
        folder=financial_model_folder,
        action_id="A1",
        event_type="status_changed",
        previous_value="in_progress",
        new_value="blocked",
    )

    _record(
        folder=financial_model_folder,
        action_id="A1",
        event_type="status_changed",
        previous_value="in_progress",
        new_value="blocked",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
        intent="repeated_blocking_patterns",
    )

    result = engine.answer(
        question=(
            "Which actions keep getting blocked?"
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    assert (
        "repeated blocking"
        in result["answer"].lower()
    )

    assert "Action A1" in result["answer"]

    assert (
        result.get(
            "management_state_changed"
        )
        is not True
    )


# ==================================================
# OWNERSHIP CHANGES
# ==================================================


def test_ai_question_engine_ownership_change_patterns(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    _record(
        folder=financial_model_folder,
        action_id="A1",
        event_type="owner_changed",
        previous_value=None,
        new_value="Elie",
    )

    _record(
        folder=financial_model_folder,
        action_id="A1",
        event_type="owner_changed",
        previous_value="Elie",
        new_value="Wassim",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
        intent="ownership_change_patterns",
    )

    result = engine.answer(
        question=(
            "Which actions keep changing owners?"
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    assert (
        "multiple ownership changes"
        in result["answer"].lower()
    )

    assert "Action A1" in result["answer"]

    assert (
        result.get(
            "management_state_changed"
        )
        is not True
    )


# ==================================================
# DUE-DATE CHANGES
# ==================================================


def test_ai_question_engine_due_date_change_patterns(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    _record(
        folder=financial_model_folder,
        action_id="A1",
        event_type="due_date_changed",
        previous_value=None,
        new_value="2026-09-15",
    )

    _record(
        folder=financial_model_folder,
        action_id="A1",
        event_type="due_date_changed",
        previous_value="2026-09-15",
        new_value="2026-09-30",
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
        intent="due_date_change_patterns",
    )

    result = engine.answer(
        question=(
            "Which actions keep changing due dates?"
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    assert (
        "multiple due-date changes"
        in result["answer"].lower()
    )

    assert "Action A1" in result["answer"]

    assert (
        result.get(
            "management_state_changed"
        )
        is not True
    )


# ==================================================
# EMPTY HISTORY
# ==================================================


def test_ai_question_engine_performance_handles_empty_history(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
        intent="action_performance_summary",
    )

    result = engine.answer(
        question=(
            "How is our action plan performing?"
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"

    assert (
        "does not yet have recorded"
        in result["answer"].lower()
    )

    assert (
        result.get(
            "management_state_changed"
        )
        is not True
    )


# ==================================================
# READ-ONLY PROTECTION
# ==================================================


def test_performance_question_does_not_modify_action_plan_or_history(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )

    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    action = CFOActionPlanService.create_action(
        financial_model_folder=(
            financial_model_folder
        ),
        title="Review funding gap",
        description=(
            "Review the current funding gap."
        ),
        priority="High",
        category="Funding",
    )

    _record(
        folder=financial_model_folder,
        action_id=action["action_id"],
        event_type="owner_changed",
        previous_value=None,
        new_value="Elie",
    )

    _record(
        folder=financial_model_folder,
        action_id=action["action_id"],
        event_type="owner_changed",
        previous_value="Elie",
        new_value="Wassim",
    )

    before_actions = deepcopy(
        CFOActionPlanService.list_actions(
            financial_model_folder
        )
    )

    before_history = deepcopy(
        CFOActionHistoryService.list_events(
            financial_model_folder
        )
    )

    engine = _build_engine(
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
        intent="ownership_change_patterns",
    )

    result = engine.answer(
        question=(
            "Which actions keep changing owners?"
        ),
        organisation_id="org-1",
    )

    after_actions = (
        CFOActionPlanService.list_actions(
            financial_model_folder
        )
    )

    after_history = (
        CFOActionHistoryService.list_events(
            financial_model_folder
        )
    )

    assert result["status"] == "success"

    assert (
        result.get(
            "management_state_changed"
        )
        is not True
    )

    assert before_actions == after_actions
    assert before_history == after_history