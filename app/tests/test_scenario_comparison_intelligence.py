from copy import deepcopy

from app.services.scenario_comparison_intelligence import (
    generate_scenario_comparison_intelligence,
)


def _decision(
    *,
    scenario_name: str,
    net_result_variance: float,
    net_result_direction: str,
    severity: str,
    management_attention: str,
    cash_variance: float | None = None,
    cash_direction: str | None = None,
    runway_change: float | None = None,
    runway_direction: str | None = None,
) -> dict:
    return {
        "status": "available",
        "scenario_name": scenario_name,
        "scenario_type": "what_if",
        "forecast_horizon_months": 3,
        "overall_direction": net_result_direction,
        "decision_signal": (
            "positive"
            if net_result_direction == "improved"
            else "negative"
            if net_result_direction == "deteriorated"
            else "neutral"
        ),
        "severity": severity,
        "management_attention": management_attention,
        "decision_factors": [],
        "net_result_impact": {
            "direction": net_result_direction,
            "variance": net_result_variance,
        },
        "cash_impact": {
            "available": cash_variance is not None,
            "direction": cash_direction,
            "variance": cash_variance,
        },
        "runway_impact": {
            "available": runway_change is not None,
            "direction": runway_direction,
            "change_months": runway_change,
        },
        "recommended_actions": [],
        "controls": {
            "source_is_deterministic_scenario": True,
            "financial_recalculation_performed": False,
            "missing_impacts_not_invented": True,
            "recommendations_are_rule_based": True,
        },
    }


def test_comparison_identifies_clear_preferred_scenario():
    scenario_a = _decision(
        scenario_name="Scenario A",
        net_result_variance=-500.0,
        net_result_direction="deteriorated",
        severity="high",
        management_attention="priority_review",
    )

    scenario_b = _decision(
        scenario_name="Scenario B",
        net_result_variance=300.0,
        net_result_direction="improved",
        severity="low",
        management_attention="monitor",
    )

    result = generate_scenario_comparison_intelligence(
        scenario_a,
        scenario_b,
    )

    assert result["status"] == "available"
    assert result["preferred_scenario"] == "Scenario B"
    assert result["comparison_signal"] == "clear_preference"


def test_comparison_does_not_invent_missing_cash_evidence():
    scenario_a = _decision(
        scenario_name="Scenario A",
        net_result_variance=300.0,
        net_result_direction="improved",
        severity="low",
        management_attention="monitor",
    )

    scenario_b = _decision(
        scenario_name="Scenario B",
        net_result_variance=200.0,
        net_result_direction="improved",
        severity="low",
        management_attention="monitor",
    )

    result = generate_scenario_comparison_intelligence(
        scenario_a,
        scenario_b,
    )

    assert result["cash_comparison"]["available"] is False
    assert result["controls"]["missing_impacts_not_invented"] is True


def test_comparison_returns_mixed_when_signals_conflict():
    scenario_a = _decision(
        scenario_name="Scenario A",
        net_result_variance=500.0,
        net_result_direction="improved",
        severity="medium",
        management_attention="review",
        cash_variance=-400.0,
        cash_direction="deteriorated",
    )

    scenario_b = _decision(
        scenario_name="Scenario B",
        net_result_variance=300.0,
        net_result_direction="improved",
        severity="low",
        management_attention="monitor",
        cash_variance=100.0,
        cash_direction="improved",
    )

    result = generate_scenario_comparison_intelligence(
        scenario_a,
        scenario_b,
    )

    assert result["comparison_signal"] == "mixed"
    assert result["preferred_scenario"] is None


def test_comparison_handles_unavailable_input():
    scenario_a = {
        "status": "not_available",
        "scenario_name": "Scenario A",
    }

    scenario_b = _decision(
        scenario_name="Scenario B",
        net_result_variance=300.0,
        net_result_direction="improved",
        severity="low",
        management_attention="monitor",
    )

    result = generate_scenario_comparison_intelligence(
        scenario_a,
        scenario_b,
    )

    assert result["status"] == "not_available"
    assert result["preferred_scenario"] is None


def test_comparison_preserves_both_inputs():
    scenario_a = _decision(
        scenario_name="Scenario A",
        net_result_variance=-100.0,
        net_result_direction="deteriorated",
        severity="medium",
        management_attention="review",
    )

    scenario_b = _decision(
        scenario_name="Scenario B",
        net_result_variance=100.0,
        net_result_direction="improved",
        severity="low",
        management_attention="monitor",
    )

    original_a = deepcopy(scenario_a)
    original_b = deepcopy(scenario_b)

    generate_scenario_comparison_intelligence(
        scenario_a,
        scenario_b,
    )

    assert scenario_a == original_a
    assert scenario_b == original_b

def test_identical_scenarios_do_not_create_false_preference():
    scenario_a = _decision(
        scenario_name="Scenario A",
        net_result_variance=-100.0,
        net_result_direction="deteriorated",
        severity="medium",
        management_attention="review",
    )

    scenario_b = _decision(
        scenario_name="Scenario B",
        net_result_variance=-100.0,
        net_result_direction="deteriorated",
        severity="medium",
        management_attention="review",
    )

    result = generate_scenario_comparison_intelligence(
        scenario_a,
        scenario_b,
    )

    assert result["status"] == "available"

    assert result["comparison_signal"] != "clear_preference"

    assert result["preferred_scenario"] is None    