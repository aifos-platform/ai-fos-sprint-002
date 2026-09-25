from app.services.financial_opportunities import (
    generate_financial_opportunities,
)


def _generate(
    financial_trends=None,
    financial_forecast=None,
    liquidity=None,
    funding_gap=None,
    budget_dashboard=None,
    grant_diagnostics=None,
):
    return generate_financial_opportunities(
        financial_trends=financial_trends,
        financial_forecast=financial_forecast,
        liquidity=liquidity,
        funding_gap=funding_gap,
        budget_dashboard=budget_dashboard,
        grant_diagnostics=grant_diagnostics,
    )


def test_returns_empty_list_when_no_validated_opportunities_exist():
    result = _generate()

    assert result == []


def test_identifies_forecast_operating_surplus():
    result = _generate(
        financial_forecast={
            "status": "available",
            "forecast_horizon_months": 3,
            "forecast_totals": {
                "revenue": 360000,
                "expenses": 300000,
                "net_result": 60000,
            },
            "confidence": {
                "level": "Medium",
            },
        }
    )

    titles = [
        opportunity["title"]
        for opportunity in result
    ]

    assert "Forecast operating surplus" in titles

    surplus = next(
        opportunity
        for opportunity in result
        if opportunity["title"]
        == "Forecast operating surplus"
    )

    assert surplus["priority"] == "High"
    assert (
        surplus["category"]
        == "Operating Performance"
    )
    assert "60,000.00 USD" in surplus["evidence"]


def test_does_not_duplicate_forecast_coverage_when_surplus_exists():
    result = _generate(
        financial_forecast={
            "status": "available",
            "forecast_horizon_months": 3,
            "forecast_totals": {
                "revenue": 360000,
                "expenses": 300000,
                "net_result": 60000,
            },
            "confidence": {
                "level": "Medium",
            },
        }
    )

    titles = [
        opportunity["title"]
        for opportunity in result
    ]

    assert "Forecast operating surplus" in titles
    assert (
        "Forecast revenue coverage strength"
        not in titles
    )


def test_identifies_positive_revenue_momentum():
    result = _generate(
        financial_trends={
            "latest_month_comparison": {
                "revenue": {
                    "change_percentage": 12.5,
                }
            }
        }
    )

    opportunity = next(
        opportunity
        for opportunity in result
        if opportunity["title"]
        == "Positive revenue momentum"
    )

    assert opportunity["priority"] == "Medium"
    assert (
        opportunity["category"]
        == "Revenue Sustainability"
    )
    assert "12.50%" in opportunity["evidence"]


def test_identifies_improving_expense_trend():
    result = _generate(
        financial_trends={
            "latest_month_comparison": {
                "expenses": {
                    "change_percentage": -8.25,
                }
            }
        }
    )

    opportunity = next(
        opportunity
        for opportunity in result
        if opportunity["title"]
        == "Improving expense trend"
    )

    assert opportunity["priority"] == "Medium"
    assert opportunity["category"] == "Cost Management"
    assert "8.25%" in opportunity["evidence"]


def test_identifies_strong_liquidity_capacity():
    result = _generate(
        liquidity={
            "cash_runway_months": 14.5,
        }
    )

    opportunity = next(
        opportunity
        for opportunity in result
        if opportunity["title"]
        == "Strong liquidity capacity"
    )

    assert opportunity["priority"] == "Medium"
    assert opportunity["category"] == "Liquidity"
    assert "14.50 months" in opportunity["evidence"]


def test_identifies_secured_funding_coverage():
    result = _generate(
        funding_gap={
            "summary": {
                "remaining_requirement": 500000,
                "funding_gap": 200000,
                "applied_secured_funding": 300000,
                "applied_coverage_percentage": 60,
            }
        }
    )

    opportunity = next(
        opportunity
        for opportunity in result
        if opportunity["title"]
        == "Secured funding coverage opportunity"
    )

    assert opportunity["priority"] == "High"
    assert opportunity["category"] == "Funding"
    assert "300,000.00 USD" in opportunity["evidence"]
    assert "60.00%" in opportunity["evidence"]


def test_identifies_high_secured_funding_coverage():
    result = _generate(
        funding_gap={
            "summary": {
                "remaining_requirement": 500000,
                "funding_gap": 50000,
                "applied_secured_funding": 450000,
                "applied_coverage_percentage": 90,
            }
        }
    )

    titles = [
        opportunity["title"]
        for opportunity in result
    ]

    assert (
        "Secured funding coverage opportunity"
        in titles
    )
    assert "High secured-funding coverage" in titles


def test_high_priority_opportunities_are_sorted_first():
    result = _generate(
        financial_trends={
            "latest_month_comparison": {
                "expenses": {
                    "change_percentage": -5,
                }
            }
        },
        financial_forecast={
            "status": "available",
            "forecast_horizon_months": 3,
            "forecast_totals": {
                "revenue": 360000,
                "expenses": 300000,
                "net_result": 60000,
            },
            "confidence": {
                "level": "Medium",
            },
        },
    )

    assert len(result) >= 2

    assert result[0]["priority"] == "High"

    priorities = [
        opportunity["priority"]
        for opportunity in result
    ]

    first_medium = priorities.index("Medium")

    assert all(
        priority == "High"
        for priority in priorities[:first_medium]
    )


def test_forecast_not_available_does_not_create_forecast_opportunity():
    result = _generate(
        financial_forecast={
            "status": "not_available",
            "forecast_horizon_months": 3,
            "forecast_totals": {
                "revenue": 360000,
                "expenses": 300000,
                "net_result": 60000,
            },
        }
    )

    titles = [
        opportunity["title"]
        for opportunity in result
    ]

    assert "Forecast operating surplus" not in titles
    assert (
        "Forecast revenue coverage strength"
        not in titles
    )