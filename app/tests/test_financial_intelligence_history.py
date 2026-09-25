from pathlib import Path

import pytest

from app.services.financial_intelligence_history import (
    FinancialIntelligenceHistoryService,
)


def test_empty_history_returns_empty_list(
    tmp_path: Path,
):
    result = (
        FinancialIntelligenceHistoryService.list_snapshots(
            tmp_path
        )
    )

    assert result == []


def test_record_snapshot_persists_verified_outputs(
    tmp_path: Path,
):
    snapshot = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health={
                "score": 72,
            },
            liquidity={
                "available_cash": 1000.0,
            },
            funding_gap={
                "funding_gap": 500.0,
            },
            risk_assessment=[
                {
                    "title": "Funding gap",
                    "severity": "High",
                }
            ],
            executive_decision_intelligence={
                "highest_priority": "High",
            },
            captured_at="2026-09-13T12:00:00+00:00",
        )
    )

    assert snapshot["snapshot_id"]
    assert (
        snapshot["captured_at"]
        == "2026-09-13T12:00:00+00:00"
    )

    intelligence = snapshot[
        "financial_intelligence"
    ]

    assert intelligence["financial_health"] == {
        "score": 72,
    }

    assert intelligence["liquidity"] == {
        "available_cash": 1000.0,
    }

    assert intelligence["funding_gap"] == {
        "funding_gap": 500.0,
    }

    assert intelligence["risk_assessment"][0][
        "title"
    ] == "Funding gap"

    saved = (
        FinancialIntelligenceHistoryService.list_snapshots(
            tmp_path
        )
    )

    assert len(saved) == 1
    assert (
        saved[0]["snapshot_id"]
        == snapshot["snapshot_id"]
    )


def test_history_is_append_only(
    tmp_path: Path,
):
    first = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health={
                "score": 50,
            },
            captured_at="2026-09-01T12:00:00+00:00",
        )
    )

    second = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health={
                "score": 60,
            },
            captured_at="2026-09-13T12:00:00+00:00",
        )
    )

    snapshots = (
        FinancialIntelligenceHistoryService.list_snapshots(
            tmp_path
        )
    )

    assert len(snapshots) == 2

    assert snapshots[0]["snapshot_id"] == first[
        "snapshot_id"
    ]

    assert snapshots[1]["snapshot_id"] == second[
        "snapshot_id"
    ]

    assert (
        snapshots[0]["financial_intelligence"][
            "financial_health"
        ]["score"]
        == 50
    )

    assert (
        snapshots[1]["financial_intelligence"][
            "financial_health"
        ]["score"]
        == 60
    )


def test_get_snapshot_returns_exact_snapshot(
    tmp_path: Path,
):
    created = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health={
                "score": 81,
            },
        )
    )

    loaded = (
        FinancialIntelligenceHistoryService.get_snapshot(
            financial_model_folder=tmp_path,
            snapshot_id=created["snapshot_id"],
        )
    )

    assert loaded is not None
    assert (
        loaded["snapshot_id"]
        == created["snapshot_id"]
    )


def test_get_unknown_snapshot_returns_none(
    tmp_path: Path,
):
    result = (
        FinancialIntelligenceHistoryService.get_snapshot(
            financial_model_folder=tmp_path,
            snapshot_id="unknown",
        )
    )

    assert result is None


def test_get_snapshot_requires_id(
    tmp_path: Path,
):
    with pytest.raises(
        ValueError,
        match="Snapshot ID is required",
    ):
        FinancialIntelligenceHistoryService.get_snapshot(
            financial_model_folder=tmp_path,
            snapshot_id="",
        )


def test_snapshot_does_not_include_scenario_state(
    tmp_path: Path,
):
    snapshot = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health={
                "score": 70,
            },
        )
    )

    intelligence = snapshot[
        "financial_intelligence"
    ]

    assert "financial_scenario" not in intelligence
    assert (
        "scenario_decision_intelligence"
        not in intelligence
    )
    assert (
        "scenario_comparison_intelligence"
        not in intelligence
    )
    assert "funding_scenario" not in intelligence


def test_snapshot_does_not_include_action_plan_state(
    tmp_path: Path,
):
    snapshot = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
        )
    )

    intelligence = snapshot[
        "financial_intelligence"
    ]

    assert "cfo_action_plan" not in intelligence
    assert "action_plan" not in intelligence


def test_snapshot_preserves_original_values(
    tmp_path: Path,
):
    financial_health = {
        "score": 55,
    }

    snapshot = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health=financial_health,
        )
    )

    financial_health["score"] = 99

    assert (
        snapshot["financial_intelligence"][
            "financial_health"
        ]["score"]
        == 55
    )


def test_controls_protect_verified_history(
    tmp_path: Path,
):
    snapshot = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
        )
    )

    controls = snapshot["controls"]

    assert controls["deterministic"] is True
    assert controls["read_only_history"] is True
    assert (
        controls["financial_recalculation_performed"]
        is False
    )
    assert (
        controls["validated_outputs_preserved"]
        is True
    )
    assert (
        controls["hypothetical_scenarios_excluded"]
        is True
    )
    assert (
        controls["action_plan_state_excluded"]
        is True
    )
    assert (
        controls["missing_evidence_not_invented"]
        is True
    )
    assert (
        controls[
            "historical_snapshot_mutation_supported"
        ]
        is False
    )

def test_snapshot_can_capture_complete_verified_intelligence_state(
    tmp_path: Path,
):
    snapshot = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health={
                "score": 54,
            },
            liquidity={
                "available_cash": 1971271.45,
            },
            financial_facts={
                "net_result": -1061081.91,
            },
            budget_dashboard={
                "status": "available",
            },
            funding_gap={
                "status": "available",
            },
            grant_diagnostics={
                "status": "available",
            },
            expected_funding_intelligence={
                "status": "available",
            },
            financial_trends={
                "status": "available",
            },
            financial_forecast={
                "status": "available",
            },
            risk_assessment=[
                {
                    "title": "Operating deficit",
                    "severity": "High",
                }
            ],
            forward_risks=[
                {
                    "title": "Runway risk",
                    "severity": "High",
                }
            ],
            financial_opportunities=[
                {
                    "title": "Funding opportunity",
                }
            ],
            cfo_recommendations=[
                {
                    "title": "Address operating deficit",
                }
            ],
            executive_decision_intelligence={
                "highest_priority": "High",
                "priority_count": 2,
            },
            source="financial_processing",
            captured_at="2026-09-13T12:00:00+00:00",
        )
    )

    intelligence = snapshot[
        "financial_intelligence"
    ]

    assert snapshot["source"] == "financial_processing"

    assert intelligence["financial_health"][
        "score"
    ] == 54

    assert intelligence["liquidity"][
        "available_cash"
    ] == 1971271.45

    assert intelligence["risk_assessment"][0][
        "title"
    ] == "Operating deficit"

    assert intelligence["forward_risks"][0][
        "title"
    ] == "Runway risk"

    assert intelligence[
        "executive_decision_intelligence"
    ]["highest_priority"] == "High"

    snapshots = (
        FinancialIntelligenceHistoryService.list_snapshots(
            tmp_path
        )
    )

    assert len(snapshots) == 1  

def test_compare_persisted_snapshots_by_id(
    tmp_path: Path,
):
    first = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health={
                "score": 50,
            },
            liquidity={
                "cash_runway_months": 5.0,
            },
            captured_at="2026-09-01T12:00:00+00:00",
        )
    )

    second = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health={
                "score": 60,
            },
            liquidity={
                "cash_runway_months": 8.0,
            },
            captured_at="2026-09-13T12:00:00+00:00",
        )
    )

    result = (
        FinancialIntelligenceHistoryService.compare_snapshots(
            financial_model_folder=tmp_path,
            snapshot_a_id=first["snapshot_id"],
            snapshot_b_id=second["snapshot_id"],
        )
    )

    assert result["status"] == "available"

    assert (
        result["overall_direction"]
        == "improved"
    )

    assert (
        result["snapshot_a"]["snapshot_id"]
        == first["snapshot_id"]
    )

    assert (
        result["snapshot_b"]["snapshot_id"]
        == second["snapshot_id"]
    )


def test_compare_latest_uses_two_latest_snapshots(
    tmp_path: Path,
):
    FinancialIntelligenceHistoryService.record_snapshot(
        financial_model_folder=tmp_path,
        financial_health={
            "score": 40,
        },
        captured_at="2026-08-01T12:00:00+00:00",
    )

    second = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health={
                "score": 50,
            },
            captured_at="2026-09-01T12:00:00+00:00",
        )
    )

    third = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health={
                "score": 60,
            },
            captured_at="2026-09-13T12:00:00+00:00",
        )
    )

    result = (
        FinancialIntelligenceHistoryService.compare_latest(
            tmp_path
        )
    )

    assert (
        result["snapshot_a"]["snapshot_id"]
        == second["snapshot_id"]
    )

    assert (
        result["snapshot_b"]["snapshot_id"]
        == third["snapshot_id"]
    )

    assert (
        result["overall_direction"]
        == "improved"
    )


def test_compare_latest_requires_two_snapshots(
    tmp_path: Path,
):
    FinancialIntelligenceHistoryService.record_snapshot(
        financial_model_folder=tmp_path,
        financial_health={
            "score": 50,
        },
    )

    result = (
        FinancialIntelligenceHistoryService.compare_latest(
            tmp_path
        )
    )

    assert (
        result["status"]
        == "insufficient_history"
    )

    assert result["snapshot_count"] == 1

    assert (
        result["controls"][
            "missing_history_not_invented"
        ]
        is True
    )


def test_compare_snapshots_rejects_same_snapshot(
    tmp_path: Path,
):
    snapshot = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health={
                "score": 50,
            },
        )
    )

    with pytest.raises(
        ValueError,
        match="Two different snapshot IDs are required",
    ):
        FinancialIntelligenceHistoryService.compare_snapshots(
            financial_model_folder=tmp_path,
            snapshot_a_id=snapshot["snapshot_id"],
            snapshot_b_id=snapshot["snapshot_id"],
        )


def test_compare_snapshots_rejects_unknown_snapshot(
    tmp_path: Path,
):
    snapshot = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=tmp_path,
            financial_health={
                "score": 50,
            },
        )
    )

    with pytest.raises(
        ValueError,
        match="Snapshot B was not found",
    ):
        FinancialIntelligenceHistoryService.compare_snapshots(
            financial_model_folder=tmp_path,
            snapshot_a_id=snapshot["snapshot_id"],
            snapshot_b_id="unknown",
        )

def test_build_latest_historical_decision_uses_latest_two_snapshots(
    tmp_path: Path,
):
    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    first = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=(
                financial_model_folder
            ),
            financial_health={
                "score": 70.0,
            },
            liquidity={
                "cash_runway_months": 10.0,
            },
            financial_facts={},
            budget_dashboard={},
            funding_gap={},
            grant_diagnostics={},
            expected_funding_intelligence={},
            financial_trends={},
            financial_forecast={},
            risk_assessment=[],
            forward_risks=[],
            financial_opportunities=[],
            cfo_recommendations=[],
            executive_decision_intelligence={},
            analysis_start_date=None,
            analysis_end_date=None,
            source="test",
        )
    )

    second = (
        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=(
                financial_model_folder
            ),
            financial_health={
                "score": 50.0,
            },
            liquidity={
                "cash_runway_months": 6.0,
            },
            financial_facts={},
            budget_dashboard={},
            funding_gap={},
            grant_diagnostics={},
            expected_funding_intelligence={},
            financial_trends={},
            financial_forecast={},
            risk_assessment=[
                {
                    "title": "Low cash runway",
                    "severity": "High",
                    "category": "Liquidity",
                    "evidence": (
                        "Cash runway deteriorated."
                    ),
                }
            ],
            forward_risks=[],
            financial_opportunities=[],
            cfo_recommendations=[],
            executive_decision_intelligence={},
            analysis_start_date=None,
            analysis_end_date=None,
            source="test",
        )
    )

    result = (
        FinancialIntelligenceHistoryService
        .build_latest_historical_decision(
            financial_model_folder
        )
    )

    assert result["status"] == "available"

    assert (
        result["snapshot_a"]["snapshot_id"]
        == first["snapshot_id"]
    )

    assert (
        result["snapshot_b"]["snapshot_id"]
        == second["snapshot_id"]
    )

    assert (
        result["priority_count"]
        > 0
    )


def test_build_latest_historical_decision_with_one_snapshot_is_safe(
    tmp_path: Path,
):
    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    FinancialIntelligenceHistoryService.record_snapshot(
        financial_model_folder=(
            financial_model_folder
        ),
        financial_health={
            "score": 60.0,
        },
        liquidity={},
        financial_facts={},
        budget_dashboard={},
        funding_gap={},
        grant_diagnostics={},
        expected_funding_intelligence={},
        financial_trends={},
        financial_forecast={},
        risk_assessment=[],
        forward_risks=[],
        financial_opportunities=[],
        cfo_recommendations=[],
        executive_decision_intelligence={},
        analysis_start_date=None,
        analysis_end_date=None,
        source="test",
    )

    result = (
        FinancialIntelligenceHistoryService
        .build_latest_historical_decision(
            financial_model_folder
        )
    )

    assert (
        result["status"]
        == "not_available"
    )

    assert (
        result["priority_count"]
        == 0
    )

    assert (
        result["historical_signal"]
        == "monitor"
    )


def test_build_latest_historical_decision_does_not_mutate_history(
    tmp_path: Path,
):
    financial_model_folder = (
        tmp_path
        / "financial_model"
    )

    FinancialIntelligenceHistoryService.record_snapshot(
        financial_model_folder=(
            financial_model_folder
        ),
        financial_health={
            "score": 60.0,
        },
        liquidity={},
        financial_facts={},
        budget_dashboard={},
        funding_gap={},
        grant_diagnostics={},
        expected_funding_intelligence={},
        financial_trends={},
        financial_forecast={},
        risk_assessment=[],
        forward_risks=[],
        financial_opportunities=[],
        cfo_recommendations=[],
        executive_decision_intelligence={},
        analysis_start_date=None,
        analysis_end_date=None,
        source="test",
    )

    FinancialIntelligenceHistoryService.record_snapshot(
        financial_model_folder=(
            financial_model_folder
        ),
        financial_health={
            "score": 55.0,
        },
        liquidity={},
        financial_facts={},
        budget_dashboard={},
        funding_gap={},
        grant_diagnostics={},
        expected_funding_intelligence={},
        financial_trends={},
        financial_forecast={},
        risk_assessment=[],
        forward_risks=[],
        financial_opportunities=[],
        cfo_recommendations=[],
        executive_decision_intelligence={},
        analysis_start_date=None,
        analysis_end_date=None,
        source="test",
    )

    before = (
        FinancialIntelligenceHistoryService.list_snapshots(
            financial_model_folder
        )
    )

    FinancialIntelligenceHistoryService.build_latest_historical_decision(
        financial_model_folder
    )

    after = (
        FinancialIntelligenceHistoryService.list_snapshots(
            financial_model_folder
        )
    )

    assert before == after        
      