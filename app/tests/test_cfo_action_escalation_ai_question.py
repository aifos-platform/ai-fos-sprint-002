from pathlib import Path
from typing import Any

from app.services.ai_question_engine import (
    AIQuestionEngine,
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
        *,
        intent: str,
    ) -> None:
        self.intent = intent

    def classify(
        self,
        *,
        question: str,
    ) -> dict[str, str]:
        return {
            "intent": self.intent,
            "domain": "cfo_action_plan",
            "target": "cfo_action_escalation",
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
    intent: str,
    financial_model_folder: Path,
    ai_knowledge_folder: Path,
) -> AIQuestionEngine:
    engine = AIQuestionEngine.__new__(
        AIQuestionEngine
    )

    engine.question_classifier = (
        _QuestionClassifier(
            intent=intent
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


def _create_action(
    folder: Path,
    *,
    title: str,
    priority: str = "High",
    owner: str | None = None,
    due_date: str | None = None,
    status: str = "open",
) -> dict[str, Any]:
    return CFOActionPlanService.create_action(
        financial_model_folder=folder,
        title=title,
        description=f"Action for {title}.",
        priority=priority,
        category="Financial Management",
        owner=owner,
        due_date=due_date,
        status=status,
    )


# ==================================================
# ESCALATION SUMMARY
# ==================================================


def test_ai_question_engine_returns_escalation_summary(
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
        title="Funding gap mitigation",
        priority="High",
        owner=None,
        due_date="2026-01-01",
    )

    engine = _build_engine(
        intent="action_escalation_summary",
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "Which actions need management intervention?"
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"
    assert (
        result["intent"]
        == "action_escalation_summary"
    )
    assert (
        "Funding gap mitigation"
        in result["answer"]
    )
    assert (
        "Critical"
        in result["answer"]
    )


# ==================================================
# CRITICAL FOLLOW-UPS
# ==================================================


def test_ai_question_engine_returns_critical_followups(
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
        title="Liquidity recovery action",
        priority="Critical",
        owner="Elie",
        due_date="2026-01-01",
    )

    engine = _build_engine(
        intent="critical_action_followups",
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "What are my critical follow-ups?"
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"
    assert (
        result["intent"]
        == "critical_action_followups"
    )
    assert (
        "Liquidity recovery action"
        in result["answer"]
    )
    assert (
        "immediate intervention"
        in result["answer"].lower()
    )


# ==================================================
# EMPTY STATE
# ==================================================


def test_ai_question_engine_handles_empty_escalation_state(
    tmp_path: Path,
) -> None:
    financial_model_folder = (
        tmp_path / "financial_model"
    )
    ai_knowledge_folder = (
        tmp_path / "ai_knowledge"
    )

    engine = _build_engine(
        intent="action_escalation_summary",
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "Which actions need management intervention?"
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"
    assert (
        "no CFO management actions requiring "
        "escalation or additional management intervention"
        in result["answer"]
    )


def test_ai_question_engine_handles_no_critical_followups(
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
        title="Monthly report",
        priority="Medium",
        owner="Elie",
        due_date="2099-12-31",
    )

    engine = _build_engine(
        intent="critical_action_followups",
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "What are my critical follow-ups?"
        ),
        organisation_id="org-1",
    )

    assert result["status"] == "success"
    assert (
        "no Critical CFO management follow-ups"
        in result["answer"]
    )


# ==================================================
# READ-ONLY / MUTATION SEPARATION
# ==================================================


def test_escalation_question_does_not_modify_action_plan(
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
        title="Funding gap mitigation",
        priority="High",
        owner=None,
        due_date="2026-01-01",
    )

    before = CFOActionPlanService.get_action(
        financial_model_folder=(
            financial_model_folder
        ),
        action_id=action["action_id"],
    )

    engine = _build_engine(
        intent="action_escalation_summary",
        financial_model_folder=(
            financial_model_folder
        ),
        ai_knowledge_folder=(
            ai_knowledge_folder
        ),
    )

    result = engine.answer(
        question=(
            "Which actions need management intervention?"
        ),
        organisation_id="org-1",
    )

    after = CFOActionPlanService.get_action(
        financial_model_folder=(
            financial_model_folder
        ),
        action_id=action["action_id"],
    )

    assert result["status"] == "success"
    assert before == after
    assert (
        result.get(
            "management_state_changed"
        )
        is not True
    )