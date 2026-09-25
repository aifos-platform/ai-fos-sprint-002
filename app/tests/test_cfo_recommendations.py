from app.services.cfo_recommendations import (
    generate_cfo_recommendations,
)


def test_funding_gap_generates_management_recommendations():
    funding_gap = {
        "summary": {
            "remaining_requirement": 1000.0,
            "applied_secured_funding": 400.0,
            "funding_gap": 600.0,
            "period_ineligible_funding_exposure": 200.0,
            "period_unknown_funding_exposure": 100.0,
            "dimension_incompatible_funding_exposure": 50.0,
            "requirements_with_period_ineligible_funding": 1,
            "requirements_with_period_unknown_funding": 1,
            "requirements_with_dimension_incompatible_funding": 1,
        }
    }

    recommendations = generate_cfo_recommendations(
        income_statement={},
        balance_sheet={},
        cash_flow={},
        financial_health={
            "score": 100,
            "rating": "Strong",
        },
        risk_assessment=[],
        forward_risks=[],
        financial_opportunities=[],
        budget_dashboard={},
        grant_diagnostics={},
        funding_gap=funding_gap,
    )

    funding_recommendations = [
        item
        for item in recommendations
        if item.get("source") == "funding_gap"
    ]

    titles = {
        item["title"]
        for item in funding_recommendations
    }

    assert len(funding_recommendations) == 4

    assert "Close the remaining Funding Gap" in titles
    assert "Resolve out-of-period secured funding" in titles
    assert "Complete missing grant-period evidence" in titles
    assert "Review incompatible funding allocations" in titles

    combined_evidence = " ".join(
        item["evidence"]
        for item in funding_recommendations
    )

    assert "$1,000.00" in combined_evidence
    assert "$600.00" in combined_evidence
    assert "$200.00" in combined_evidence
    assert "$100.00" in combined_evidence
    assert "$50.00" in combined_evidence

def test_forward_risk_creates_cfo_recommendation():
    recommendations = generate_cfo_recommendations(
        income_statement={},
        balance_sheet={},
        cash_flow={},
        financial_health={},
        risk_assessment=[],
        forward_risks=[
            {
                "severity": "High",
                "category": "Operating Performance",
                "title": "Forecast operating deficit",
                "evidence": (
                    "The validated baseline forecast projects "
                    "a future operating deficit."
                ),
                "recommendation": (
                    "Review the forecast deficit drivers and "
                    "prepare corrective action."
                ),
            }
        ],
        financial_opportunities=[],
        budget_dashboard={},
        grant_diagnostics={},
        funding_gap={},
    )

    forward_recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation.get("source") == "forward_risk"
    ]

    assert len(forward_recommendations) == 1

    recommendation = forward_recommendations[0]

    assert recommendation["priority"] == "High"
    assert recommendation["category"] == "Operating Performance"
    assert recommendation["title"] == (
        "Prepare for Forecast operating deficit"
    )
    assert recommendation["linked_risk"] == (
        "Forecast operating deficit"
    )
    assert recommendation["source"] == "forward_risk"
    assert "future operating deficit" in recommendation[
        "evidence"
    ].lower()
    assert "corrective action" in recommendation[
        "action"
    ].lower()


def test_forward_risk_does_not_replace_current_risk_recommendation():
    recommendations = generate_cfo_recommendations(
        income_statement={},
        balance_sheet={},
        cash_flow={},
        financial_health={},
        risk_assessment=[
            {
                "severity": "High",
                "category": "Operating Performance",
                "title": "Operating deficit",
                "evidence": "Current operating deficit exists.",
                "recommendation": "Address the current deficit.",
            }
        ],
        forward_risks=[
            {
                "severity": "High",
                "category": "Operating Performance",
                "title": "Forecast operating deficit",
                "evidence": "Future operating deficit is forecast.",
                "recommendation": "Prepare corrective action.",
            }
        ],
        financial_opportunities=[],
        budget_dashboard={},
        grant_diagnostics={},
        funding_gap={},
    )

    sources = [
        recommendation.get("source")
        for recommendation in recommendations
    ]

    assert "risk_assessment" in sources
    assert "forward_risk" in sources 


def test_financial_opportunity_creates_cfo_recommendation():
    recommendations = generate_cfo_recommendations(
        income_statement={},
        balance_sheet={},
        cash_flow={},
        financial_health={},
        risk_assessment=[],
        forward_risks=[],
        financial_opportunities=[
            {
                "priority": "High",
                "category": "Funding",
                "title": "Secured funding coverage opportunity",
                "evidence": (
                    "Validated Funding Gap analysis shows "
                    "57.56% secured-funding coverage."
                ),
                "recommended_action": (
                    "Focus fundraising attention on the "
                    "remaining uncovered requirements."
                ),
            }
        ],
        budget_dashboard={},
        grant_diagnostics={},
        funding_gap={},
    )

    opportunity_recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation.get("source") == "financial_opportunity"
    ]

    assert len(opportunity_recommendations) == 1

    recommendation = opportunity_recommendations[0]

    assert recommendation["priority"] == "High"
    assert recommendation["category"] == "Funding"
    assert (
        recommendation["linked_opportunity"]
        == "Secured funding coverage opportunity"
    )


def test_financial_opportunity_without_action_is_not_recommended():
    recommendations = generate_cfo_recommendations(
        income_statement={},
        balance_sheet={},
        cash_flow={},
        financial_health={},
        risk_assessment=[],
        forward_risks=[],
        financial_opportunities=[
            {
                "priority": "Medium",
                "category": "Liquidity",
                "title": "Strong liquidity capacity",
                "evidence": (
                    "Validated liquidity analysis shows "
                    "12.59 months of runway."
                ),
                "recommended_action": "",
            }
        ],
        budget_dashboard={},
        grant_diagnostics={},
        funding_gap={},
    )

    opportunity_recommendations = [
        recommendation
        for recommendation in recommendations
        if recommendation.get("source") == "financial_opportunity"
    ]

    assert opportunity_recommendations == []       