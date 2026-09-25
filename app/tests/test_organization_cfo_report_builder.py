from app.organization import Organization


def test_build_structured_cfo_report_creates_report():
    organization = Organization()

    organization.financial_health = {
        "score": 75,
        "status": "Moderate",
    }

    organization.liquidity = {
        "cash_runway_months": 10.0,
    }

    organization.budget_dashboard = {}
    organization.funding_gap = {}
    organization.grant_diagnostics = {}

    organization.risk_assessment = [
        {
            "severity": "High",
            "category": "Budget",
            "title": "Budget pressure",
        }
    ]

    organization.forward_risks = [
        {
            "severity": "High",
            "category": "Funding",
            "title": "Forward Funding Gap exposure",
        }
    ]

    organization.financial_opportunities = [
        {
            "priority": "High",
            "category": "Funding",
            "title": "Funding opportunity",
        }
    ]

    organization.cfo_recommendations = [
        {
            "priority": "High",
            "category": "Funding",
            "title": "Close funding gap",
        }
    ]

    organization.financial_trends = {}
    organization.financial_forecast = {}
    organization.core_cost_coverage = {
        "status": "available",
        "summary": {
            "needed_core_cost": 100000.0,
            "remaining_core_cost_gap": 25000.0,
            "core_cost_coverage_percentage": 75.0,
        },
    }

    organization.build_structured_cfo_report()

    report = organization.structured_cfo_report

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

    assert (
        report["executive_summary"]["high_current_risk_count"]
        == 1
    )

    assert (
        report["executive_summary"]["high_forward_risk_count"]
        == 1
    )

    assert (
        report["executive_summary"]["high_opportunity_count"]
        == 1
    )

    assert (
        report["executive_summary"]["priority_action_count"]
        == 1
    )


def test_build_structured_cfo_report_remains_separate_from_ai_cfo_report():
    organization = Organization()

    organization.cfo_report = {
        "summary": "Existing AI-written CFO report"
    }

    organization.financial_health = {}
    organization.liquidity = {}
    organization.budget_dashboard = {}
    organization.funding_gap = {}
    organization.grant_diagnostics = {}
    organization.risk_assessment = []
    organization.forward_risks = []
    organization.financial_opportunities = []
    organization.cfo_recommendations = []
    organization.financial_trends = {}
    organization.financial_forecast = {}

    organization.build_structured_cfo_report()

    assert organization.cfo_report == {
        "summary": "Existing AI-written CFO report"
    }

    assert (
        organization.structured_cfo_report["report_type"]
        == "cfo_report"
    )