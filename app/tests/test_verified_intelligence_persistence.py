import json
from pathlib import Path

from app.services.financial_model_service import (
    FinancialModelService,
)


def _sample_verified_intelligence():
    return {
        "financial_health": {
            "score": 54,
            "rating": "Weak",
        },
        "risk_assessment": [
            {
                "severity": "High",
                "category": "Financial Health",
                "title": "Weak financial health",
                "evidence": "Financial Health Score is 54/100.",
            }
        ],
        "forward_risks": [
            {
                "severity": "Medium",
                "category": "Funding Sustainability",
                "title": "Future funding pressure",
                "evidence": "Future funding coverage may weaken.",
            }
        ],
        "financial_opportunities": [
            {
                "priority": "High",
                "category": "Funding",
                "title": "Secured funding coverage opportunity",
                "evidence": "Eligible secured funding coverage exists.",
            }
        ],
        "cfo_recommendations": [
            {
                "priority": "High",
                "category": "Financial Health",
                "title": "Address Weak financial health",
                "action": "Prepare a recovery plan.",
                "source": "risk_assessment",
            }
        ],
        "executive_decision_intelligence": {
            "status": "available",
            "executive_signal": "priority_attention",
            "highest_priority": "High",
            "priority_count": 1,
            "priorities": [
                {
                    "rank": 1,
                    "priority": "High",
                    "category": "Financial Health",
                    "title": "Weak financial health",
                    "management_action": "Prepare a recovery plan.",
                }
            ],
            "controls": {
                "deterministic": True,
                "financial_recalculation_performed": False,
                "validated_outputs_preserved": True,
                "missing_evidence_not_invented": True,
                "opportunities_do_not_cancel_risks": True,
            },
        },
    }


def test_save_verified_intelligence_outputs_creates_expected_files(
    tmp_path: Path,
):
    data = _sample_verified_intelligence()

    result = (
        FinancialModelService
        .save_verified_intelligence_outputs(
            financial_model_folder=tmp_path,
            financial_health=data["financial_health"],
            risk_assessment=data["risk_assessment"],
            forward_risks=data["forward_risks"],
            financial_opportunities=data[
                "financial_opportunities"
            ],
            cfo_recommendations=data[
                "cfo_recommendations"
            ],
            executive_decision_intelligence=data[
                "executive_decision_intelligence"
            ],
        )
    )

    expected_files = {
        "financial_health": "financial_health.json",
        "risk_assessment": "risk_assessment.json",
        "forward_risks": "forward_risks.json",
        "financial_opportunities": (
            "financial_opportunities.json"
        ),
        "cfo_recommendations": (
            "cfo_recommendations.json"
        ),
        "executive_decision_intelligence": (
            "executive_decision_intelligence.json"
        ),
    }

    assert set(result.keys()) == set(
        expected_files.keys()
    )

    for key, filename in expected_files.items():
        file_path = tmp_path / filename

        assert file_path.exists()
        assert result[key] == str(file_path)


def test_saved_verified_intelligence_matches_source_data(
    tmp_path: Path,
):
    data = _sample_verified_intelligence()

    FinancialModelService.save_verified_intelligence_outputs(
        financial_model_folder=tmp_path,
        financial_health=data["financial_health"],
        risk_assessment=data["risk_assessment"],
        forward_risks=data["forward_risks"],
        financial_opportunities=data[
            "financial_opportunities"
        ],
        cfo_recommendations=data[
            "cfo_recommendations"
        ],
        executive_decision_intelligence=data[
            "executive_decision_intelligence"
        ],
    )

    expected = {
        "financial_health.json": data[
            "financial_health"
        ],
        "risk_assessment.json": data[
            "risk_assessment"
        ],
        "forward_risks.json": data[
            "forward_risks"
        ],
        "financial_opportunities.json": data[
            "financial_opportunities"
        ],
        "cfo_recommendations.json": data[
            "cfo_recommendations"
        ],
        "executive_decision_intelligence.json": data[
            "executive_decision_intelligence"
        ],
    }

    for filename, expected_data in expected.items():
        with (
            tmp_path / filename
        ).open(
            "r",
            encoding="utf-8",
        ) as file:
            saved_data = json.load(file)

        assert saved_data == expected_data


def test_verified_intelligence_persistence_does_not_create_scenario_files(
    tmp_path: Path,
):
    data = _sample_verified_intelligence()

    FinancialModelService.save_verified_intelligence_outputs(
        financial_model_folder=tmp_path,
        financial_health=data["financial_health"],
        risk_assessment=data["risk_assessment"],
        forward_risks=data["forward_risks"],
        financial_opportunities=data[
            "financial_opportunities"
        ],
        cfo_recommendations=data[
            "cfo_recommendations"
        ],
        executive_decision_intelligence=data[
            "executive_decision_intelligence"
        ],
    )

    assert not (
        tmp_path / "financial_scenario.json"
    ).exists()

    assert not (
        tmp_path
        / "scenario_decision_intelligence.json"
    ).exists()

    assert not (
        tmp_path
        / "scenario_comparison_intelligence.json"
    ).exists()


def test_verified_intelligence_persistence_does_not_modify_core_files(
    tmp_path: Path,
):
    core_file = (
        tmp_path
        / "financial_forecast.json"
    )

    original_core_data = {
        "status": "available",
        "forecast_totals": {
            "revenue": 1000.0,
            "expenses": 700.0,
            "net_result": 300.0,
        },
    }

    FinancialModelService.save_json(
        financial_model_folder=tmp_path,
        filename="financial_forecast.json",
        data=original_core_data,
    )

    data = _sample_verified_intelligence()

    FinancialModelService.save_verified_intelligence_outputs(
        financial_model_folder=tmp_path,
        financial_health=data["financial_health"],
        risk_assessment=data["risk_assessment"],
        forward_risks=data["forward_risks"],
        financial_opportunities=data[
            "financial_opportunities"
        ],
        cfo_recommendations=data[
            "cfo_recommendations"
        ],
        executive_decision_intelligence=data[
            "executive_decision_intelligence"
        ],
    )

    with core_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        saved_core_data = json.load(file)

    assert saved_core_data == original_core_data


def test_verified_intelligence_outputs_are_independently_loadable(
    tmp_path: Path,
):
    data = _sample_verified_intelligence()

    FinancialModelService.save_verified_intelligence_outputs(
        financial_model_folder=tmp_path,
        financial_health=data["financial_health"],
        risk_assessment=data["risk_assessment"],
        forward_risks=data["forward_risks"],
        financial_opportunities=data[
            "financial_opportunities"
        ],
        cfo_recommendations=data[
            "cfo_recommendations"
        ],
        executive_decision_intelligence=data[
            "executive_decision_intelligence"
        ],
    )

    financial_health = (
        FinancialModelService.load_json(
            financial_model_folder=tmp_path,
            filename="financial_health.json",
        )
    )

    executive_decision_intelligence = (
        FinancialModelService.load_json(
            financial_model_folder=tmp_path,
            filename=(
                "executive_decision_intelligence.json"
            ),
        )
    )

    assert financial_health == data[
        "financial_health"
    ]

    assert (
        executive_decision_intelligence
        == data[
            "executive_decision_intelligence"
        ]
    )