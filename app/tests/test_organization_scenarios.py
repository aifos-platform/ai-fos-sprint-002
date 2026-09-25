from app.organization import Organization


def test_organization_initializes_scenario_outputs_as_none():
    organization = Organization()
    organization.name = "Test Organization"

    assert organization.financial_scenario is None

    assert (
        organization.scenario_decision_intelligence
        is None
    )


def test_run_financial_scenario_stores_result(monkeypatch):
    organization = Organization()
    organization.name = "Test Organization"

    organization.financial_forecast = {
        "forecast_type": "baseline",
    }

    organization.liquidity = {
        "available_cash": 1000.0,
    }

    expected_result = {
        "scenario_name": "Revenue Down 10%",
        "scenario_type": "what_if",
    }

    def fake_generate_financial_scenario(**kwargs):
        assert kwargs["financial_forecast"] == (
            organization.financial_forecast
        )
        assert kwargs["liquidity"] == organization.liquidity
        assert kwargs["scenario_name"] == "Revenue Down 10%"
        assert kwargs["revenue_change_percentage"] == -10.0

        return expected_result

    monkeypatch.setattr(
        "app.organization.generate_financial_scenario",
        fake_generate_financial_scenario,
    )

    result = organization.run_financial_scenario(
        scenario_name="Revenue Down 10%",
        revenue_change_percentage=-10.0,
    )

    assert result == expected_result
    assert organization.financial_scenario == expected_result


def test_running_scenario_does_not_modify_baseline_forecast(
    monkeypatch,
):
    organization = Organization()
    organization.name = "Test Organization"

    baseline_forecast = {
        "forecast_type": "baseline",
        "projected_revenue": 5000.0,
        "projected_expenses": 4000.0,
    }

    organization.financial_forecast = baseline_forecast.copy()

    monkeypatch.setattr(
        "app.organization.generate_financial_scenario",
        lambda **kwargs: {
            "scenario_name": "Expense Increase",
            "scenario_type": "what_if",
            "projected_expenses": 4400.0,
        },
    )

    organization.run_financial_scenario(
        scenario_name="Expense Increase",
        expense_change_percentage=10.0,
    )

    assert organization.financial_forecast == baseline_forecast
    assert organization.financial_scenario is not None

def test_run_financial_scenario_builds_decision_intelligence(
    monkeypatch,
):
    organization = Organization()
    organization.name = "Test Organization"

    organization.financial_forecast = {
        "forecast_type": "baseline",
    }

    scenario_result = {
        "status": "available",
        "scenario_name": "Revenue Down 10%",
        "scenario_type": "what_if",
    }

    decision_result = {
        "status": "available",
        "scenario_name": "Revenue Down 10%",
        "overall_direction": "deteriorated",
        "decision_signal": "negative",
    }

    monkeypatch.setattr(
        "app.organization.generate_financial_scenario",
        lambda **kwargs: scenario_result,
    )

    def fake_generate_decision_intelligence(
        scenario,
    ):
        assert scenario is scenario_result
        return decision_result

    monkeypatch.setattr(
        (
            "app.organization."
            "generate_scenario_decision_intelligence"
        ),
        fake_generate_decision_intelligence,
    )

    result = organization.run_financial_scenario(
        scenario_name="Revenue Down 10%",
        revenue_change_percentage=-10.0,
    )

    assert result is scenario_result

    assert (
        organization.financial_scenario
        is scenario_result
    )

    assert (
        organization.scenario_decision_intelligence
        is decision_result
    )


def test_decision_intelligence_does_not_replace_scenario_result(
    monkeypatch,
):
    organization = Organization()

    scenario_result = {
        "status": "available",
        "scenario_name": "Cash Outflow",
        "scenario_type": "what_if",
    }

    monkeypatch.setattr(
        "app.organization.generate_financial_scenario",
        lambda **kwargs: scenario_result,
    )

    monkeypatch.setattr(
        (
            "app.organization."
            "generate_scenario_decision_intelligence"
        ),
        lambda scenario: {
            "status": "available",
            "decision_signal": "negative",
        },
    )

    returned_result = (
        organization.run_financial_scenario(
            scenario_name="Cash Outflow",
            cash_outflow_adjustment=500.0,
        )
    )

    assert returned_result is scenario_result

    assert (
        organization.financial_scenario
        is scenario_result
    )

    assert (
        organization.scenario_decision_intelligence[
            "decision_signal"
        ]
        == "negative"
    )    
def test_organization_initializes_scenario_comparison_as_none():
    organization = Organization()

    assert (
        organization.scenario_comparison_intelligence
        is None
    )


def test_compare_financial_scenarios_stores_comparison(
    monkeypatch,
):
    organization = Organization()
    organization.name = "Test Organization"

    scenario_a = {
        "status": "available",
        "scenario_name": "Scenario A",
        "decision_signal": "negative",
        "severity": "high",
    }

    scenario_b = {
        "status": "available",
        "scenario_name": "Scenario B",
        "decision_signal": "positive",
        "severity": "low",
    }

    expected_comparison = {
        "status": "available",
        "preferred_scenario": "Scenario B",
        "comparison_signal": "clear_preference",
    }

    def fake_generate_scenario_comparison(
        first_scenario,
        second_scenario,
    ):
        assert first_scenario is scenario_a
        assert second_scenario is scenario_b

        return expected_comparison

    monkeypatch.setattr(
        (
            "app.organization."
            "generate_scenario_comparison_intelligence"
        ),
        fake_generate_scenario_comparison,
    )

    result = organization.compare_financial_scenarios(
        scenario_a,
        scenario_b,
    )

    assert result is expected_comparison

    assert (
        organization.scenario_comparison_intelligence
        is expected_comparison
    )    