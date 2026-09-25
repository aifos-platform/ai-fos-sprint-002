from app.services.forward_risk import (
    generate_forward_risks,
)


def _forecast(
    *,
    revenue: float = 3000.0,
    expenses: float = 2100.0,
    net_result: float = 900.0,
) -> dict:
    return {
        "status": "available",
        "forecast_horizon_months": 3,
        "forecast_totals": {
            "revenue": revenue,
            "expenses": expenses,
            "net_result": net_result,
        },
        "confidence": {
            "level": "Medium",
        },
    }


def test_forecast_deficit_creates_high_forward_risk():
    risks = generate_forward_risks(
        risk_assessment=[],
        financial_trends={},
        financial_forecast=_forecast(
            revenue=1800.0,
            expenses=2400.0,
            net_result=-600.0,
        ),
        liquidity={},
        funding_gap={},
        grant_diagnostics={},
    )

    titles = {
        risk["title"]
        for risk in risks
    }

    assert "Forecast operating deficit" in titles

    deficit_risk = next(
        risk
        for risk in risks
        if risk["title"] == "Forecast operating deficit"
    )

    assert deficit_risk["severity"] == "High"
    assert "-600.00 USD" in deficit_risk["evidence"]
    assert "3 month(s)" in deficit_risk["evidence"]
    assert "Medium" in deficit_risk["evidence"]


def test_declining_revenue_plus_deficit_creates_combined_risk():
    trends = {
        "latest_month_comparison": {
            "revenue": {
                "change_percentage": -12.5,
            },
        },
    }

    risks = generate_forward_risks(
        risk_assessment=[],
        financial_trends=trends,
        financial_forecast=_forecast(
            revenue=1800.0,
            expenses=2400.0,
            net_result=-600.0,
        ),
        liquidity={},
        funding_gap={},
        grant_diagnostics={},
    )

    titles = {
        risk["title"]
        for risk in risks
    }

    assert (
        "Revenue decline reinforcing forecast deficit"
        in titles
    )

    risk = next(
        item
        for item in risks
        if item["title"]
        == "Revenue decline reinforcing forecast deficit"
    )

    assert "-12.50%" in risk["evidence"]
    assert "-600.00 USD" in risk["evidence"]


def test_expense_growth_creates_medium_forward_risk():
    trends = {
        "latest_month_comparison": {
            "expenses": {
                "change_percentage": 15.0,
            },
        },
    }

    risks = generate_forward_risks(
        risk_assessment=[],
        financial_trends=trends,
        financial_forecast=_forecast(),
        liquidity={},
        funding_gap={},
        grant_diagnostics={},
    )

    risk = next(
        item
        for item in risks
        if item["title"] == "Rising expense pressure"
    )

    assert risk["severity"] == "Medium"
    assert "15.00%" in risk["evidence"]
    assert "2,100.00 USD" in risk["evidence"]


def test_low_cash_runway_creates_forward_liquidity_risk():
    risks = generate_forward_risks(
        risk_assessment=[],
        financial_trends={},
        financial_forecast=_forecast(),
        liquidity={
            "cash_runway_months": 4.5,
        },
        funding_gap={},
        grant_diagnostics={},
    )

    risk = next(
        item
        for item in risks
        if item["title"] == "Limited forward cash runway"
    )

    assert risk["severity"] == "Medium"
    assert "4.50 months" in risk["evidence"]


def test_critical_cash_runway_threshold_is_high():
    risks = generate_forward_risks(
        risk_assessment=[],
        financial_trends={},
        financial_forecast=_forecast(),
        liquidity={
            "cash_runway_months": 2.5,
        },
        funding_gap={},
        grant_diagnostics={},
    )

    risk = next(
        item
        for item in risks
        if item["title"] == "Limited forward cash runway"
    )

    assert risk["severity"] == "High"
    assert "2.50 months" in risk["evidence"]


def test_positive_funding_gap_creates_high_forward_risk():
    risks = generate_forward_risks(
        risk_assessment=[],
        financial_trends={},
        financial_forecast=_forecast(),
        liquidity={},
        funding_gap={
            "summary": {
                "remaining_requirement": 1000.0,
                "funding_gap": 600.0,
                "applied_coverage_percentage": 40.0,
            },
        },
        grant_diagnostics={},
    )

    risk = next(
        item
        for item in risks
        if item["title"] == "Forward Funding Gap exposure"
    )

    assert risk["severity"] == "High"
    assert "600.00 USD" in risk["evidence"]
    assert "1,000.00 USD" in risk["evidence"]
    assert "40.00%" in risk["evidence"]


def test_unknown_grant_period_exposure_creates_medium_risk():
    risks = generate_forward_risks(
        risk_assessment=[],
        financial_trends={},
        financial_forecast=_forecast(),
        liquidity={},
        funding_gap={
            "summary": {
                "period_unknown_funding_exposure": 250.0,
            },
        },
        grant_diagnostics={},
    )

    risk = next(
        item
        for item in risks
        if item["title"]
        == "Future funding eligibility uncertainty"
    )

    assert risk["severity"] == "Medium"
    assert "250.00 USD" in risk["evidence"]


def test_no_forward_evidence_returns_empty_list():
    risks = generate_forward_risks(
        risk_assessment=[],
        financial_trends={},
        financial_forecast={
            "status": "not_available",
        },
        liquidity={},
        funding_gap={},
        grant_diagnostics={},
    )

    assert risks == []


def test_duplicate_forecast_operating_risk_is_not_created():
    risks = generate_forward_risks(
        risk_assessment=[],
        financial_trends={},
        financial_forecast=_forecast(
            revenue=1800.0,
            expenses=2400.0,
            net_result=-600.0,
        ),
        liquidity={},
        funding_gap={},
        grant_diagnostics={},
    )

    operating_titles = [
        risk["title"]
        for risk in risks
        if risk["category"] == "Operating Performance"
    ]

    assert operating_titles.count(
        "Forecast operating deficit"
    ) == 1

    assert "Forecast revenue below expenses" not in (
        operating_titles
    )


def test_forward_risks_are_sorted_by_severity():
    trends = {
        "latest_month_comparison": {
            "expenses": {
                "change_percentage": 10.0,
            },
        },
    }

    risks = generate_forward_risks(
        risk_assessment=[],
        financial_trends=trends,
        financial_forecast=_forecast(
            revenue=1800.0,
            expenses=2400.0,
            net_result=-600.0,
        ),
        liquidity={
            "cash_runway_months": 4.0,
        },
        funding_gap={},
        grant_diagnostics={},
    )

    severities = [
        risk["severity"]
        for risk in risks
    ]

    first_medium_index = severities.index("Medium")

    assert all(
        severity == "High"
        for severity in severities[:first_medium_index]
    )