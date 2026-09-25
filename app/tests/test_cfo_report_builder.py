from app.services.cfo_report_builder import build_cfo_report


def test_cfo_report_builds_structured_report():
    report = build_cfo_report(
        financial_health={
            "score": 72,
            "status": "Moderate",
        },
        liquidity={
            "cash_runway_months": 8.5,
        },
        budget_dashboard={
            "status": "available",
        },
        funding_gap={
            "summary": {
                "funding_gap": 500000.0,
            }
        },
        grant_diagnostics={
            "matched_grants": 4,
        },
        risk_assessment=[
            {
                "severity": "High",
                "category": "Budget",
                "title": "Budget pressure",
            },
            {
                "severity": "Medium",
                "category": "Liquidity",
                "title": "Liquidity watch",
            },
        ],
        forward_risks=[
            {
                "severity": "High",
                "category": "Funding",
                "title": "Forward Funding Gap exposure",
            }
        ],
        financial_opportunities=[
            {
                "priority": "High",
                "category": "Funding",
                "title": "Funding opportunity",
            },
            {
                "priority": "Medium",
                "category": "Liquidity",
                "title": "Liquidity opportunity",
            },
        ],
        cfo_recommendations=[
            {
                "priority": "High",
                "category": "Funding",
                "title": "Close funding gap",
            },
            {
                "priority": "Medium",
                "category": "Budget",
                "title": "Monitor budget",
            },
        ],
        financial_trends={
            "status": "available",
        },
        financial_forecast={
            "status": "available",
        },
        core_cost_coverage={
            "status": "available",
            "summary": {
                "needed_core_cost": 100000.0,
                "remaining_core_cost_gap": 25000.0,
                "core_cost_coverage_percentage": 75.0,
            },
        },
    )

    assert report["report_type"] == "cfo_report"
    assert report["version"] == "1.0"
    assert report["core_cost_coverage"] == {
        "status": "available",
        "summary": {
            "needed_core_cost": 100000.0,
            "remaining_core_cost_gap": 25000.0,
            "core_cost_coverage_percentage": 75.0,
        },
    }

    assert report["financial_health"]["score"] == 72
    assert report["liquidity"]["cash_runway_months"] == 8.5

    assert (
        report["funding"]["funding_gap"]["summary"]["funding_gap"]
        == 500000.0
    )

    assert len(report["risks"]["current"]) == 2
    assert len(report["risks"]["high_current"]) == 1

    assert len(report["risks"]["forward"]) == 1
    assert len(report["risks"]["high_forward"]) == 1

    assert len(report["opportunities"]["all"]) == 2
    assert len(report["opportunities"]["high_priority"]) == 1

    assert len(report["recommendations"]["all"]) == 2
    assert len(report["recommendations"]["priority_actions"]) == 1

    assert report["executive_summary"]["high_current_risk_count"] == 1
    assert report["executive_summary"]["high_forward_risk_count"] == 1
    assert report["executive_summary"]["high_opportunity_count"] == 1
    assert report["executive_summary"]["priority_action_count"] == 1


def test_cfo_report_handles_missing_artifacts():
    report = build_cfo_report()

    assert report["report_type"] == "cfo_report"

    assert report["financial_health"] == {}
    assert report["liquidity"] == {}
    assert report["budget"] == {}

    assert report["funding"]["funding_gap"] == {}
    assert report["funding"]["grant_diagnostics"] == {}

    assert report["risks"]["current"] == []
    assert report["risks"]["forward"] == []

    assert report["opportunities"]["all"] == []
    assert report["recommendations"]["all"] == []

    assert report["trends"] == {}
    assert report["forecast"] == {}

    assert report["executive_summary"]["high_current_risk_count"] == 0
    assert report["executive_summary"]["high_forward_risk_count"] == 0
    assert report["executive_summary"]["high_opportunity_count"] == 0
    assert report["executive_summary"]["priority_action_count"] == 0

    assert report["core_cost_coverage"] == {}    