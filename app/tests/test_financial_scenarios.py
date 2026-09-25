from app.services.financial_scenarios import (
    generate_financial_scenario,
)


def _forecast() -> dict:
    return {
        "status": "available",
        "forecast_horizon_months": 3,
        "forecast_series": [
            {
                "period": "2026-09",
                "revenue": 1000.0,
                "expenses": 700.0,
                "net_result": 300.0,
            },
            {
                "period": "2026-10",
                "revenue": 1000.0,
                "expenses": 700.0,
                "net_result": 300.0,
            },
            {
                "period": "2026-11",
                "revenue": 1000.0,
                "expenses": 700.0,
                "net_result": 300.0,
            },
        ],
        "forecast_totals": {
            "revenue": 3000.0,
            "expenses": 2100.0,
            "net_result": 900.0,
        },
    }


def _liquidity() -> dict:
    return {
        "available_cash": 1200.0,
        "cash_runway_months": 6.0,
        "average_monthly_operating_expenses": 200.0,
    }


def test_revenue_reduction_changes_scenario_not_baseline():
    forecast = _forecast()

    result = generate_financial_scenario(
        financial_forecast=forecast,
        revenue_change_percentage=-10.0,
    )

    assert result["status"] == "available"

    assert result["baseline"]["revenue"] == 3000.0
    assert result["scenario"]["revenue"] == 2700.0
    assert result["impact"]["revenue_variance"] == -300.0

    assert forecast["forecast_totals"]["revenue"] == 3000.0

    assert (
        result["controls"]["baseline_forecast_preserved"]
        is True
    )


def test_expense_increase_reduces_net_result():
    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        expense_change_percentage=10.0,
    )

    assert result["scenario"]["expenses"] == 2310.0
    assert result["scenario"]["net_result"] == 690.0

    assert result["impact"]["expense_variance"] == 210.0
    assert result["impact"]["net_result_variance"] == -210.0
    assert (
        result["impact"]["net_result_direction"]
        == "deteriorated"
    )


def test_combined_revenue_and_expense_scenario():
    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        revenue_change_percentage=-10.0,
        expense_change_percentage=10.0,
    )

    assert result["scenario"]["revenue"] == 2700.0
    assert result["scenario"]["expenses"] == 2310.0
    assert result["scenario"]["net_result"] == 390.0

    assert result["impact"]["net_result_variance"] == -510.0
    assert (
        result["impact"]["net_result_direction"]
        == "deteriorated"
    )


def test_one_time_adjustments_are_applied_once():
    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        one_time_revenue_adjustment=300.0,
        one_time_expense_adjustment=150.0,
    )

    assert result["scenario"]["revenue"] == 3300.0
    assert result["scenario"]["expenses"] == 2250.0
    assert result["scenario"]["net_result"] == 1050.0

    series = result["scenario_series"]

    assert series[0]["scenario_revenue"] == 1300.0
    assert series[1]["scenario_revenue"] == 1000.0
    assert series[2]["scenario_revenue"] == 1000.0

    assert series[0]["scenario_expenses"] == 850.0
    assert series[1]["scenario_expenses"] == 700.0
    assert series[2]["scenario_expenses"] == 700.0


def test_revenue_change_does_not_automatically_change_cash():
    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        liquidity=_liquidity(),
        revenue_change_percentage=-25.0,
    )

    cash = result["cash"]

    assert cash["baseline_available_cash"] == 1200.0
    assert cash["net_cash_adjustment"] == 0.0
    assert cash["scenario_available_cash"] == 1200.0

    assert (
        result["controls"]["revenue_expense_not_assumed_cash"]
        is True
    )


def test_explicit_cash_outflow_changes_available_cash():
    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        liquidity=_liquidity(),
        cash_outflow_adjustment=400.0,
    )

    cash = result["cash"]

    assert cash["baseline_available_cash"] == 1200.0
    assert cash["net_cash_adjustment"] == -400.0
    assert cash["scenario_available_cash"] == 800.0
    assert cash["available_cash_variance"] == -400.0


def test_explicit_cash_inflow_changes_available_cash():
    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        liquidity=_liquidity(),
        cash_inflow_adjustment=600.0,
    )

    cash = result["cash"]

    assert cash["scenario_available_cash"] == 1800.0
    assert cash["available_cash_variance"] == 600.0


def test_cash_runway_recalculates_only_with_authoritative_inputs():
    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        liquidity=_liquidity(),
        cash_outflow_adjustment=400.0,
    )

    runway = result["runway"]

    assert runway["available"] is True
    assert runway["baseline_cash_runway_months"] == 6.0
    assert runway["scenario_cash_runway_months"] == 4.0
    assert runway["cash_runway_change_months"] == -2.0


def test_cash_runway_is_not_invented_without_expense_basis():
    liquidity = {
        "available_cash": 1200.0,
        "cash_runway_months": 6.0,
    }

    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        liquidity=liquidity,
        cash_outflow_adjustment=400.0,
    )

    runway = result["runway"]

    assert runway["available"] is False
    assert runway["scenario_cash_runway_months"] is None
    assert runway["cash_runway_change_months"] is None


def test_scenario_requires_validated_baseline_forecast():
    result = generate_financial_scenario(
        financial_forecast={
            "status": "not_available",
        },
        revenue_change_percentage=-10.0,
    )

    assert result["status"] == "not_available"
    assert "validated baseline financial forecast" in (
        result["reason"].lower()
    )


def test_scenario_exposes_controls_and_cautions():
    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        liquidity=_liquidity(),
    )

    assert result["scenario_type"] == "what_if"

    assert (
        result["methodology"]
        == "explicit_assumption_scenario"
    )

    assert (
        result["controls"]["baseline_forecast_preserved"]
        is True
    )

    assert (
        result["controls"]["cash_requires_explicit_adjustment"]
        is True
    )

    caution_text = " ".join(
        result["cautions"]
    ).lower()

    assert "hypothetical" in caution_text
    assert "not predictions" in caution_text
    assert "cash movements" in caution_text

def test_expense_decrease_improves_net_result():
    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        expense_change_percentage=-10.0,
    )

    assert result["scenario"]["expenses"] == 1890.0
    assert result["scenario"]["net_result"] == 1110.0

    assert result["impact"]["expense_variance"] == -210.0
    assert result["impact"]["net_result_variance"] == 210.0
    assert (
        result["impact"]["net_result_direction"]
        == "improved"
    )


def test_combined_revenue_increase_and_expense_decrease():
    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        revenue_change_percentage=10.0,
        expense_change_percentage=-10.0,
    )

    assert result["scenario"]["revenue"] == 3300.0
    assert result["scenario"]["expenses"] == 1890.0
    assert result["scenario"]["net_result"] == 1410.0

    assert result["impact"]["revenue_variance"] == 300.0
    assert result["impact"]["expense_variance"] == -210.0
    assert result["impact"]["net_result_variance"] == 510.0

    assert (
        result["impact"]["net_result_direction"]
        == "improved"
    )


def test_scenario_series_reconciles_to_scenario_totals():
    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        revenue_change_percentage=-10.0,
        expense_change_percentage=10.0,
        one_time_revenue_adjustment=300.0,
        one_time_expense_adjustment=150.0,
    )

    series = result["scenario_series"]

    total_revenue = round(
        sum(
            period["scenario_revenue"]
            for period in series
        ),
        2,
    )

    total_expenses = round(
        sum(
            period["scenario_expenses"]
            for period in series
        ),
        2,
    )

    total_net_result = round(
        sum(
            period["scenario_net_result"]
            for period in series
        ),
        2,
    )

    assert total_revenue == result["scenario"]["revenue"]
    assert total_expenses == result["scenario"]["expenses"]
    assert total_net_result == result["scenario"]["net_result"]


def test_missing_liquidity_does_not_invent_cash_or_runway():
    result = generate_financial_scenario(
        financial_forecast=_forecast(),
        revenue_change_percentage=10.0,
    )

    assert result["cash"]["baseline_available_cash"] is None
    assert result["cash"]["scenario_available_cash"] is None
    assert result["cash"]["available_cash_variance"] is None

    assert result["runway"]["available"] is False
    assert result["runway"]["scenario_cash_runway_months"] is None
    assert result["runway"]["cash_runway_change_months"] is None    