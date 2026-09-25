from app.services.scenario_decision_intelligence import (
    generate_scenario_decision_intelligence,
)


def _scenario(
    *,
    net_result_variance: float = -500.0,
    direction: str = "deteriorated",
    cash_variance: float | None = None,
    runway_change: float | None = None,
) -> dict:
    return {
        "status": "available",
        "scenario_name": "Test Scenario",
        "scenario_type": "what_if",
        "forecast_horizon_months": 3,
        "baseline": {
            "revenue": 3000.0,
            "expenses": 2100.0,
            "net_result": 900.0,
        },
        "scenario": {
            "revenue": 2700.0,
            "expenses": 2300.0,
            "net_result": 400.0,
        },
        "impact": {
            "revenue_variance": -300.0,
            "expense_variance": 200.0,
            "net_result_variance": net_result_variance,
            "net_result_direction": direction,
        },
        "cash": {
            "baseline_available_cash": 1200.0,
            "scenario_available_cash": (
                None
                if cash_variance is None
                else 1200.0 + cash_variance
            ),
            "available_cash_variance": cash_variance,
        },
        "runway": {
            "baseline_cash_runway_months": 6.0,
            "scenario_cash_runway_months": (
                None
                if runway_change is None
                else 6.0 + runway_change
            ),
            "cash_runway_change_months": runway_change,
            "available": runway_change is not None,
        },
        "controls": {
            "baseline_forecast_preserved": True,
        },
        "cautions": [
            "Scenario results are hypothetical.",
        ],
    }


def test_deteriorating_scenario_is_identified():
    result = generate_scenario_decision_intelligence(
        _scenario()
    )

    assert result["status"] == "available"
    assert result["overall_direction"] == "deteriorated"
    assert result["decision_signal"] == "negative"


def test_improving_scenario_is_identified():
    result = generate_scenario_decision_intelligence(
        _scenario(
            net_result_variance=500.0,
            direction="improved",
        )
    )

    assert result["overall_direction"] == "improved"
    assert result["decision_signal"] == "positive"


def test_unchanged_scenario_is_identified():
    result = generate_scenario_decision_intelligence(
        _scenario(
            net_result_variance=0.0,
            direction="unchanged",
        )
    )

    assert result["overall_direction"] == "unchanged"
    assert result["decision_signal"] == "neutral"


def test_cash_deterioration_is_exposed_when_available():
    result = generate_scenario_decision_intelligence(
        _scenario(
            cash_variance=-400.0,
        )
    )

    assert result["cash_impact"]["available"] is True
    assert result["cash_impact"]["direction"] == "deteriorated"
    assert result["cash_impact"]["variance"] == -400.0


def test_missing_cash_impact_is_not_invented():
    result = generate_scenario_decision_intelligence(
        _scenario(
            cash_variance=None,
        )
    )

    assert result["cash_impact"]["available"] is False
    assert result["cash_impact"]["direction"] is None
    assert result["cash_impact"]["variance"] is None


def test_runway_deterioration_is_exposed_when_available():
    result = generate_scenario_decision_intelligence(
        _scenario(
            runway_change=-2.0,
        )
    )

    assert result["runway_impact"]["available"] is True
    assert (
        result["runway_impact"]["direction"]
        == "deteriorated"
    )
    assert result["runway_impact"]["change_months"] == -2.0


def test_missing_runway_is_not_invented():
    result = generate_scenario_decision_intelligence(
        _scenario(
            runway_change=None,
        )
    )

    assert result["runway_impact"]["available"] is False
    assert result["runway_impact"]["direction"] is None
    assert result["runway_impact"]["change_months"] is None


def test_unavailable_scenario_remains_unavailable():
    result = generate_scenario_decision_intelligence(
        {
            "status": "not_available",
            "reason": "Baseline forecast unavailable.",
        }
    )

    assert result["status"] == "not_available"


def test_decision_intelligence_preserves_scenario_identity():
    result = generate_scenario_decision_intelligence(
        _scenario()
    )

    assert result["scenario_name"] == "Test Scenario"
    assert result["scenario_type"] == "what_if"
    assert result["forecast_horizon_months"] == 3


def test_decision_intelligence_is_traceable():
    result = generate_scenario_decision_intelligence(
        _scenario()
    )

    assert (
        result["controls"]["source_is_deterministic_scenario"]
        is True
    )

    assert (
        result["controls"]["financial_recalculation_performed"]
        is False
    )

    assert (
        result["controls"]["missing_impacts_not_invented"]
        is True
    )
def test_negative_net_result_only_requires_review():
    result = generate_scenario_decision_intelligence(
        _scenario(
            net_result_variance=-500.0,
            direction="deteriorated",
            cash_variance=None,
            runway_change=None,
        )
    )

    assert result["severity"] == "medium"
    assert result["management_attention"] == "review"


def test_multiple_deteriorating_factors_raise_severity():
    result = generate_scenario_decision_intelligence(
        _scenario(
            net_result_variance=-500.0,
            direction="deteriorated",
            cash_variance=-400.0,
            runway_change=-2.0,
        )
    )

    assert result["severity"] == "high"
    assert result["management_attention"] == "priority_review"


def test_low_resulting_runway_is_critical():
    result = generate_scenario_decision_intelligence(
        _scenario(
            net_result_variance=-500.0,
            direction="deteriorated",
            cash_variance=-400.0,
            runway_change=-4.0,
        )
    )

    assert result["severity"] == "critical"
    assert result["management_attention"] == "immediate"


def test_improving_net_result_with_cash_decline_is_not_treated_as_simple_positive():
    result = generate_scenario_decision_intelligence(
        _scenario(
            net_result_variance=500.0,
            direction="improved",
            cash_variance=-400.0,
            runway_change=None,
        )
    )

    assert result["decision_signal"] == "mixed"
    assert result["severity"] == "medium"


def test_decision_factors_expose_verified_deteriorations():
    result = generate_scenario_decision_intelligence(
        _scenario(
            net_result_variance=-500.0,
            direction="deteriorated",
            cash_variance=-400.0,
            runway_change=-2.0,
        )
    )

    assert "net_result" in result["decision_factors"]
    assert "cash" in result["decision_factors"]
    assert "runway" in result["decision_factors"]


def test_recommended_actions_are_structured_and_deterministic():
    result = generate_scenario_decision_intelligence(
        _scenario(
            net_result_variance=-500.0,
            direction="deteriorated",
            cash_variance=-400.0,
            runway_change=-2.0,
        )
    )

    assert isinstance(
        result["recommended_actions"],
        list,
    )

    assert len(
        result["recommended_actions"]
    ) > 0

    assert (
        result["controls"]["recommendations_are_rule_based"]
        is True
    )    