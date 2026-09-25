from app.organization import Organization


def test_build_financial_opportunities_sets_empty_list_with_no_inputs():
    organization = Organization()

    organization.financial_trends = {}
    organization.financial_forecast = {}
    organization.liquidity = {}
    organization.funding_gap = {}
    organization.budget_dashboard = {}
    organization.grant_diagnostics = {}

    organization.build_financial_opportunities()

    assert organization.financial_opportunities == []


def test_build_financial_opportunities_uses_validated_forecast():
    organization = Organization()

    organization.financial_trends = {}

    organization.financial_forecast = {
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

    organization.liquidity = {}
    organization.funding_gap = {}
    organization.budget_dashboard = {}
    organization.grant_diagnostics = {}

    organization.build_financial_opportunities()

    titles = [
        opportunity["title"]
        for opportunity in organization.financial_opportunities
    ]

    assert "Forecast operating surplus" in titles


def test_build_financial_opportunities_uses_validated_liquidity():
    organization = Organization()

    organization.financial_trends = {}
    organization.financial_forecast = {}

    organization.liquidity = {
        "cash_runway_months": 15,
    }

    organization.funding_gap = {}
    organization.budget_dashboard = {}
    organization.grant_diagnostics = {}

    organization.build_financial_opportunities()

    titles = [
        opportunity["title"]
        for opportunity in organization.financial_opportunities
    ]

    assert "Strong liquidity capacity" in titles