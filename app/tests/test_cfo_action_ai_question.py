from datetime import date, timedelta
from pathlib import Path

from app.engines.data_intelligence.question_classifier import (
    QuestionClassifier,
)
from app.services.ai_question_engine import (
    AIQuestionEngine,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)
from app.services.financial_model_service import (
    FinancialModelService,
)


class FakeWorkspaceService:
    def __init__(
        self,
        root: Path,
    ) -> None:
        self.root = root

    def get_workspace_by_organisation(
        self,
        organisation_id: str,
    ):
        financial_model = (
            self.root
            / "financial_model"
        )

        ai_knowledge = (
            self.root
            / "ai_knowledge"
        )

        financial_model.mkdir(
            parents=True,
            exist_ok=True,
        )

        ai_knowledge.mkdir(
            parents=True,
            exist_ok=True,
        )

        return {
            "organisation_id": organisation_id,
            "paths": {
                "financial_model": str(
                    financial_model
                ),
                "ai_knowledge": str(
                    ai_knowledge
                ),
            },
        }


class FakeKnowledgeReader:
    def get_summary(
        self,
        folder: Path,
    ):
        return {
            "status": "available",
            "organisation_name": (
                "Test Organization"
            ),
            "currency": "USD",
        }


class FakeFinancialIntelligenceService:
    pass


def _build_engine(
    tmp_path: Path,
) -> AIQuestionEngine:

    return AIQuestionEngine(
        workspace_service=(
            FakeWorkspaceService(
                tmp_path
            )
        ),
        knowledge_reader=(
            FakeKnowledgeReader()
        ),
        financial_intelligence_service=(
            FakeFinancialIntelligenceService()
        ),
        financial_model_service=(
            FinancialModelService()
        ),
    )


def _folder(
    tmp_path: Path,
) -> Path:

    folder = (
        tmp_path
        / "financial_model"
    )

    folder.mkdir(
        parents=True,
        exist_ok=True,
    )

    return folder


def test_classifier_routes_action_plan_summary():
    result = QuestionClassifier().classify(
        question=(
            "Give me the CFO action plan status."
        )
    )

    assert (
        result["intent"]
        == "action_plan_summary"
    )

    assert (
        result["domain"]
        == "cfo_action_plan"
    )


def test_classifier_routes_overdue_actions():
    result = QuestionClassifier().classify(
        question=(
            "What actions are overdue?"
        )
    )

    assert (
        result["intent"]
        == "overdue_actions"
    )


def test_classifier_routes_follow_up_this_week():
    result = QuestionClassifier().classify(
        question=(
            "What needs follow-up this week?"
        )
    )

    assert (
        result["intent"]
        == "due_soon_actions"
    )


def test_classifier_routes_blocked_actions():
    result = QuestionClassifier().classify(
        question=(
            "Which actions are blocked?"
        )
    )

    assert (
        result["intent"]
        == "blocked_actions"
    )


def test_classifier_routes_unassigned_high_priority():
    result = QuestionClassifier().classify(
        question=(
            "Which high-priority actions "
            "still have no owner?"
        )
    )

    assert (
        result["intent"]
        == "unassigned_high_priority_actions"
    )


def test_action_plan_summary_answer(
    tmp_path: Path,
):
    folder = _folder(
        tmp_path
    )

    CFOActionPlanService.create_action(
        financial_model_folder=folder,
        title="Close funding gap",
        description="Accelerate fundraising.",
        priority="High",
        owner="Executive Director",
        status="in_progress",
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "Give me the CFO action plan status."
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "action_plan_summary"
    )

    assert (
        "1 action(s)"
        in result["answer"]
    )

    assert (
        "1 in progress"
        in result["answer"]
    )


def test_overdue_action_answer(
    tmp_path: Path,
):
    folder = _folder(
        tmp_path
    )

    CFOActionPlanService.create_action(
        financial_model_folder=folder,
        title="Submit donor proposal",
        description="Submit donor proposal.",
        priority="High",
        owner="Executive Director",
        due_date="2000-01-01",
        status="in_progress",
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question="What actions are overdue?",
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "overdue_actions"
    )

    assert (
        "Submit donor proposal"
        in result["answer"]
    )

    assert (
        "Executive Director"
        in result["answer"]
    )


def test_due_soon_action_answer(
    tmp_path: Path,
):
    folder = _folder(
        tmp_path
    )

    due_date = (
        date.today()
        + timedelta(days=3)
    ).isoformat()

    CFOActionPlanService.create_action(
        financial_model_folder=folder,
        title="Prepare finance update",
        description="Prepare finance update.",
        priority="Medium",
        owner="Finance Manager",
        due_date=due_date,
        status="open",
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "What needs follow-up this week?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "due_soon_actions"
    )

    assert (
        "Prepare finance update"
        in result["answer"]
    )


def test_blocked_action_answer(
    tmp_path: Path,
):
    folder = _folder(
        tmp_path
    )

    CFOActionPlanService.create_action(
        financial_model_folder=folder,
        title="Finalize budget",
        description="Finalize budget.",
        priority="High",
        owner="Finance Manager",
        status="blocked",
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "Which actions are blocked?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "blocked_actions"
    )

    assert (
        "Finalize budget"
        in result["answer"]
    )


def test_unassigned_high_priority_answer(
    tmp_path: Path,
):
    folder = _folder(
        tmp_path
    )

    CFOActionPlanService.create_action(
        financial_model_folder=folder,
        title="Protect liquidity",
        description="Protect available liquidity.",
        priority="Critical",
        owner=None,
        status="open",
    )

    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "Which high-priority actions "
            "still have no owner?"
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        result["intent"]
        == "unassigned_high_priority_actions"
    )

    assert (
        "Protect liquidity"
        in result["answer"]
    )

    assert (
        "Owner: not assigned."
        in result["answer"]
    )


def test_empty_action_plan_answers_safely(
    tmp_path: Path,
):
    engine = _build_engine(
        tmp_path
    )

    result = engine.answer(
        question=(
            "Give me the CFO action plan status."
        ),
        organisation_id="ORG-001",
    )

    assert result["status"] == "success"

    assert (
        "no CFO management actions"
        in result["answer"]
    )