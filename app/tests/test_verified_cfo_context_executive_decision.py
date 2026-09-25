from pathlib import Path

from app.services.financial_model_service import (
    FinancialModelService,
)
from app.services.verified_cfo_context import (
    VerifiedCFOContextBuilder,
)


class FakeWorkspaceService:
    def __init__(
        self,
        financial_model_folder: Path,
    ) -> None:
        self.financial_model_folder = (
            financial_model_folder
        )

    def get_workspace_by_organisation(
        self,
        organisation_id: str,
    ):
        return {
            "organisation_id": organisation_id,
            "paths": {
                "financial_model": str(
                    self.financial_model_folder
                ),
            },
        }


def _build_context_builder(
    tmp_path: Path,
) -> VerifiedCFOContextBuilder:

    return VerifiedCFOContextBuilder(
        workspace_service=FakeWorkspaceService(
            tmp_path
        ),
        financial_model_service=(
            FinancialModelService()
        ),
    )


def _sample_executive_decision_intelligence():
    return {
        "status": "available",
        "executive_signal": "priority_attention",
        "highest_priority": "High",
        "priority_count": 1,
        "opportunity_count": 1,
        "management_focus": [
            {
                "rank": 1,
                "priority": "High",
                "category": "Financial Health",
                "title": "Weak financial health",
                "management_action": (
                    "Prepare a financial recovery plan."
                ),
            }
        ],
        "priorities": [
            {
                "rank": 1,
                "priority": "High",
                "category": "Financial Health",
                "title": "Weak financial health",
                "evidence": (
                    "Financial Health Score is 54/100."
                ),
                "management_action": (
                    "Prepare a financial recovery plan."
                ),
                "expected_impact": (
                    "Improve financial resilience."
                ),
                "source": "risk_assessment",
                "source_type": "current_risk",
            }
        ],
        "opportunities": [
            {
                "priority": "High",
                "category": "Funding",
                "title": (
                    "Secured funding coverage opportunity"
                ),
                "evidence": (
                    "Eligible secured funding coverage exists."
                ),
                "recommended_action": (
                    "Protect validated secured funding."
                ),
                "source": "financial_opportunity",
            }
        ],
        "controls": {
            "deterministic": True,
            "financial_recalculation_performed": False,
            "validated_outputs_preserved": True,
            "missing_evidence_not_invented": True,
            "opportunities_do_not_cancel_risks": True,
        },
    }


def test_verified_context_includes_executive_decision_intelligence(
    tmp_path: Path,
):
    executive_decision = (
        _sample_executive_decision_intelligence()
    )

    FinancialModelService.save_json(
        financial_model_folder=tmp_path,
        filename=(
            "executive_decision_intelligence.json"
        ),
        data=executive_decision,
    )

    builder = _build_context_builder(
        tmp_path
    )

    result = builder.build(
        organisation_id="ORG-001"
    )

    assert result["status"] == "available"

    assert (
        result["context"][
            "executive_decision_intelligence"
        ]
        == executive_decision
    )


def test_executive_decision_intelligence_is_preserved_without_recalculation(
    tmp_path: Path,
):
    executive_decision = (
        _sample_executive_decision_intelligence()
    )

    FinancialModelService.save_json(
        financial_model_folder=tmp_path,
        filename=(
            "executive_decision_intelligence.json"
        ),
        data=executive_decision,
    )

    builder = _build_context_builder(
        tmp_path
    )

    result = builder.build(
        organisation_id="ORG-001"
    )

    context_decision = (
        result["context"][
            "executive_decision_intelligence"
        ]
    )

    assert context_decision == executive_decision

    assert (
        context_decision["executive_signal"]
        == "priority_attention"
    )

    assert (
        context_decision["highest_priority"]
        == "High"
    )

    assert (
        context_decision["priorities"][0][
            "management_action"
        ]
        == "Prepare a financial recovery plan."
    )

    assert (
        context_decision["controls"][
            "financial_recalculation_performed"
        ]
        is False
    )


def test_executive_decision_intelligence_has_verified_source_provenance(
    tmp_path: Path,
):
    executive_decision = (
        _sample_executive_decision_intelligence()
    )

    FinancialModelService.save_json(
        financial_model_folder=tmp_path,
        filename=(
            "executive_decision_intelligence.json"
        ),
        data=executive_decision,
    )

    builder = _build_context_builder(
        tmp_path
    )

    result = builder.build(
        organisation_id="ORG-001"
    )

    assert (
        "executive_decision_intelligence"
        in result["available_sections"]
    )

    assert (
        result["source_files"][
            "executive_decision_intelligence"
        ]
        == "executive_decision_intelligence.json"
    )

    assert (
        result["trust"][
            "financial_source"
        ]
        == "validated_ai_fos_outputs"
    )

    assert (
        result["trust"][
            "financial_recalculation_performed"
        ]
        is False
    )

    assert (
        result["trust"][
            "raw_general_ledger_included"
        ]
        is False
    )


def test_missing_executive_decision_intelligence_is_reported_safely(
    tmp_path: Path,
):
    FinancialModelService.save_json(
        financial_model_folder=tmp_path,
        filename="financial_health.json",
        data={
            "score": 70,
            "rating": "Good",
        },
    )

    builder = _build_context_builder(
        tmp_path
    )

    result = builder.build(
        organisation_id="ORG-001"
    )

    assert result["status"] == "available"

    assert (
        "executive_decision_intelligence"
        not in result["context"]
    )

    assert (
        "executive_decision_intelligence"
        in result["missing_sections"]
    )

    assert (
        "executive_decision_intelligence"
        not in result["source_files"]
    )