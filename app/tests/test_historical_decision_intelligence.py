from copy import deepcopy

from app.services.historical_decision_intelligence import (
    generate_historical_decision_intelligence,
)


def _base_change_analysis():
    return {
        "status": "available",
        "snapshot_a": {
            "snapshot_id": "A",
            "captured_at": (
                "2026-08-31T12:00:00"
            ),
        },
        "snapshot_b": {
            "snapshot_id": "B",
            "captured_at": (
                "2026-09-30T12:00:00"
            ),
        },
        "overall_direction": "mixed",
        "management_attention": (
            "priority_review"
        ),
        "evidence_summary": {
            "positive_evidence_count": 2,
            "negative_evidence_count": 2,
            "improved_metric_count": 1,
            "deteriorated_metric_count": 1,
            "new_risk_count": 1,
            "resolved_risk_count": 1,
            "risk_severity_increased_count": 0,
            "risk_severity_decreased_count": 0,
        },
        "metric_change": {
            "status": "available",
            "comparisons": [
                {
                    "metric_id": (
                        "financial_health_score"
                    ),
                    "label": (
                        "Financial Health Score"
                    ),
                    "section": (
                        "financial_health"
                    ),
                    "unit": "points",
                    "previous_value": 60.0,
                    "current_value": 50.0,
                    "absolute_change": -10.0,
                    "percentage_change": -16.67,
                    "signal": "deteriorated",
                },
                {
                    "metric_id": (
                        "cash_runway_months"
                    ),
                    "label": "Cash Runway",
                    "section": "liquidity",
                    "unit": "months",
                    "previous_value": 6.0,
                    "current_value": 8.0,
                    "absolute_change": 2.0,
                    "percentage_change": 33.33,
                    "signal": "improved",
                },
                {
                    "metric_id": "total_cash",
                    "label": "Total Cash",
                    "section": "liquidity",
                    "unit": "currency",
                    "previous_value": 100.0,
                    "current_value": 90.0,
                    "absolute_change": -10.0,
                    "percentage_change": -10.0,
                    "signal": "decreased",
                },
            ],
        },
        "risk_change": {
            "status": "available",
            "summary": {
                "new_count": 1,
                "resolved_count": 1,
                "persistent_count": 0,
                "severity_increased_count": 0,
                "severity_decreased_count": 0,
                "unchanged_count": 0,
            },
            "movements": [
                {
                    "risk_family": (
                        "operating_deficit"
                    ),
                    "movement": "new",
                    "previous": None,
                    "current": {
                        "severity": "High",
                        "category": (
                            "Operating Performance"
                        ),
                        "title": (
                            "Operating deficit"
                        ),
                        "evidence": (
                            "Expenses exceed revenue."
                        ),
                    },
                },
                {
                    "risk_family": (
                        "cash_runway"
                    ),
                    "movement": "resolved",
                    "previous": {
                        "severity": "High",
                        "category": "Liquidity",
                        "title": (
                            "Low cash runway"
                        ),
                        "evidence": (
                            "Runway was low."
                        ),
                    },
                    "current": None,
                },
            ],
        },
        "controls": {
            "deterministic": True,
            "read_only": True,
            "financial_recalculation_performed": (
                False
            ),
            "historical_snapshots_modified": False,
            "missing_evidence_not_invented": True,
            "hypothetical_scenarios_excluded": True,
            "positive_and_negative_evidence_kept_separate": (
                True
            ),
        },
    }


def test_returns_available_historical_decision():
    result = (
        generate_historical_decision_intelligence(
            _base_change_analysis()
        )
    )

    assert result["status"] == "available"

    assert (
        result["overall_direction"]
        == "mixed"
    )

    assert (
        result["management_attention"]
        == "priority_review"
    )


def test_new_high_risk_becomes_high_priority():
    result = (
        generate_historical_decision_intelligence(
            _base_change_analysis()
        )
    )

    priority = next(
        item
        for item in result["priorities"]
        if item["title"]
        == "Operating deficit"
    )

    assert priority["priority"] == "High"

    assert (
        priority["historical_change"]
        == "new_risk"
    )

    assert (
        priority["source_type"]
        == "new_risk"
    )


def test_deteriorated_metric_becomes_medium_priority():
    result = (
        generate_historical_decision_intelligence(
            _base_change_analysis()
        )
    )

    priority = next(
        item
        for item in result["priorities"]
        if item["title"]
        == "Financial Health Score deteriorated"
    )

    assert (
        priority["priority"]
        == "Medium"
    )

    assert (
        priority["historical_change"]
        == "metric_deteriorated"
    )


def test_direction_only_metric_does_not_become_priority():
    result = (
        generate_historical_decision_intelligence(
            _base_change_analysis()
        )
    )

    titles = {
        item["title"]
        for item in result["priorities"]
    }

    assert (
        "Total Cash deteriorated"
        not in titles
    )

    assert all(
        item["title"] != "Total Cash"
        for item in result["priorities"]
    )


def test_improved_metric_is_kept_separate():
    result = (
        generate_historical_decision_intelligence(
            _base_change_analysis()
        )
    )

    improvement = next(
        item
        for item in result["improvements"]
        if item["title"]
        == "Cash Runway improved"
    )

    assert (
        improvement["historical_change"]
        == "metric_improved"
    )

    assert (
        improvement["source_type"]
        == "improved_metric"
    )


def test_resolved_risk_is_kept_as_improvement():
    result = (
        generate_historical_decision_intelligence(
            _base_change_analysis()
        )
    )

    improvement = next(
        item
        for item in result["improvements"]
        if item["title"]
        == "Low cash runway"
    )

    assert (
        improvement["historical_change"]
        == "risk_resolved"
    )

    assert (
        improvement["source_type"]
        == "resolved_risk"
    )


def test_improvements_do_not_cancel_priorities():
    result = (
        generate_historical_decision_intelligence(
            _base_change_analysis()
        )
    )

    assert result["priority_count"] > 0
    assert result["improvement_count"] > 0

    assert (
        result["highest_priority"]
        == "High"
    )

    assert (
        result["historical_signal"]
        == "priority_attention"
    )


def test_critical_new_risk_drives_immediate_action_signal():
    data = _base_change_analysis()

    data["risk_change"]["movements"][0][
        "current"
    ]["severity"] = "Critical"

    result = (
        generate_historical_decision_intelligence(
            data
        )
    )

    assert (
        result["highest_priority"]
        == "Critical"
    )

    assert (
        result["historical_signal"]
        == "immediate_action"
    )


def test_severity_increase_uses_current_verified_severity():
    data = _base_change_analysis()

    data["risk_change"]["movements"] = [
        {
            "risk_family": "cash_runway",
            "movement": (
                "severity_increased"
            ),
            "previous": {
                "severity": "Medium",
                "category": "Liquidity",
                "title": (
                    "Cash runway requires monitoring"
                ),
                "evidence": (
                    "Runway requires monitoring."
                ),
            },
            "current": {
                "severity": "High",
                "category": "Liquidity",
                "title": "Low cash runway",
                "evidence": (
                    "Runway has deteriorated."
                ),
            },
        }
    ]

    result = (
        generate_historical_decision_intelligence(
            data
        )
    )

    assert (
        result["priorities"][0][
            "priority"
        ]
        == "High"
    )

    assert (
        result["priorities"][0][
            "previous_value"
        ]
        == "Medium"
    )

    assert (
        result["priorities"][0][
            "current_value"
        ]
        == "High"
    )


def test_severity_decrease_is_improvement_not_priority():
    data = _base_change_analysis()

    data["metric_change"][
        "comparisons"
    ] = []

    data["risk_change"]["movements"] = [
        {
            "risk_family": "cash_runway",
            "movement": (
                "severity_decreased"
            ),
            "previous": {
                "severity": "High",
                "category": "Liquidity",
                "title": "Low cash runway",
                "evidence": (
                    "Runway was low."
                ),
            },
            "current": {
                "severity": "Medium",
                "category": "Liquidity",
                "title": (
                    "Cash runway requires monitoring"
                ),
                "evidence": (
                    "Runway improved."
                ),
            },
        }
    ]

    result = (
        generate_historical_decision_intelligence(
            data
        )
    )

    assert result["priority_count"] == 0

    assert (
        result["improvement_count"]
        == 1
    )

    assert (
        result["improvements"][0][
            "historical_change"
        ]
        == "risk_severity_decreased"
    )


def test_no_available_change_analysis_is_safe():
    result = (
        generate_historical_decision_intelligence(
            {
                "status": (
                    "insufficient_history"
                )
            }
        )
    )

    assert (
        result["status"]
        == "not_available"
    )

    assert result["priority_count"] == 0

    assert (
        result["historical_signal"]
        == "monitor"
    )


def test_missing_input_is_safe():
    result = (
        generate_historical_decision_intelligence(
            None
        )
    )

    assert (
        result["status"]
        == "not_available"
    )

    assert result["priorities"] == []
    assert result["improvements"] == []


def test_input_is_not_mutated():
    data = _base_change_analysis()

    original = deepcopy(
        data
    )

    generate_historical_decision_intelligence(
        data
    )

    assert data == original


def test_controls_protect_historical_architecture():
    result = (
        generate_historical_decision_intelligence(
            _base_change_analysis()
        )
    )

    controls = result["controls"]

    assert controls["deterministic"] is True
    assert controls["read_only"] is True

    assert (
        controls[
            "financial_recalculation_performed"
        ]
        is False
    )

    assert (
        controls[
            "historical_snapshots_modified"
        ]
        is False
    )

    assert (
        controls[
            "missing_evidence_not_invented"
        ]
        is True
    )

    assert (
        controls[
            "hypothetical_scenarios_excluded"
        ]
        is True
    )

    assert (
        controls[
            "positive_and_negative_evidence_kept_separate"
        ]
        is True
    )

    assert (
        controls[
            "improvements_do_not_cancel_priorities"
        ]
        is True
    )

    assert (
        controls[
            "owners_not_invented"
        ]
        is True
    )

    assert (
        controls[
            "due_dates_not_invented"
        ]
        is True
    )

    assert (
        controls[
            "action_plan_not_modified"
        ]
        is True
    )