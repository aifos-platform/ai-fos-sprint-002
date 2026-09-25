from app.services.executive_decision_intelligence import (
    generate_executive_decision_intelligence,
)


def test_critical_risk_drives_immediate_action_signal():
    result = generate_executive_decision_intelligence(
        risk_assessment=[
            {
                "severity": "Critical",
                "category": "Liquidity",
                "title": "Critical cash runway",
                "evidence": (
                    "Available cash provides only "
                    "2.50 months of operating coverage."
                ),
                "recommendation": (
                    "Preserve cash immediately."
                ),
            }
        ],
        forward_risks=[],
        cfo_recommendations=[],
        financial_opportunities=[],
    )

    assert result["status"] == "available"
    assert result["executive_signal"] == "immediate_action"
    assert result["highest_priority"] == "Critical"
    assert result["priority_count"] == 1

    priority = result["priorities"][0]

    assert priority["rank"] == 1
    assert priority["priority"] == "Critical"
    assert priority["category"] == "Liquidity"
    assert priority["title"] == "Critical cash runway"
    assert (
        priority["management_action"]
        == "Preserve cash immediately."
    )


def test_high_risk_drives_priority_attention_signal():
    result = generate_executive_decision_intelligence(
        risk_assessment=[
            {
                "severity": "High",
                "category": "Financial Health",
                "title": "Weak financial health",
                "evidence": (
                    "Financial Health Score is 54/100."
                ),
                "recommendation": (
                    "Address the weakest financial-health areas."
                ),
            }
        ],
        forward_risks=[],
        cfo_recommendations=[],
        financial_opportunities=[],
    )

    assert (
        result["executive_signal"]
        == "priority_attention"
    )
    assert result["highest_priority"] == "High"


def test_medium_risk_drives_management_review_signal():
    result = generate_executive_decision_intelligence(
        risk_assessment=[
            {
                "severity": "Medium",
                "category": "Liquidity",
                "title": "Cash runway requires monitoring",
                "evidence": (
                    "Available cash provides 7 months of coverage."
                ),
                "recommendation": (
                    "Maintain an updated rolling cash forecast."
                ),
            }
        ],
        forward_risks=[],
        cfo_recommendations=[],
        financial_opportunities=[],
    )

    assert (
        result["executive_signal"]
        == "management_review"
    )
    assert result["highest_priority"] == "Medium"


def test_no_material_priorities_returns_monitor_signal():
    result = generate_executive_decision_intelligence(
        risk_assessment=[],
        forward_risks=[],
        cfo_recommendations=[],
        financial_opportunities=[],
    )

    assert result["executive_signal"] == "monitor"
    assert result["highest_priority"] == "Low"
    assert result["priority_count"] == 0
    assert result["priorities"] == []
    assert result["management_focus"] == []


def test_risk_uses_matching_cfo_recommendation_action():
    result = generate_executive_decision_intelligence(
        risk_assessment=[
            {
                "severity": "High",
                "category": "Funding Sustainability",
                "title": "Unfunded financial requirements",
                "evidence": (
                    "Funding Gap remains material."
                ),
                "recommendation": (
                    "Generic risk action."
                ),
            }
        ],
        forward_risks=[],
        cfo_recommendations=[
            {
                "priority": "High",
                "category": "Funding Sustainability",
                "title": (
                    "Address Unfunded financial requirements"
                ),
                "evidence": (
                    "Funding Gap remains material."
                ),
                "action": (
                    "Prioritize uncovered requirements "
                    "and donor engagement."
                ),
                "expected_impact": (
                    "Improve funding sustainability."
                ),
                "linked_risk": (
                    "Unfunded financial requirements"
                ),
                "source": "risk_assessment",
            }
        ],
        financial_opportunities=[],
    )

    assert result["priority_count"] == 1

    priority = result["priorities"][0]

    assert (
        priority["management_action"]
        == (
            "Prioritize uncovered requirements "
            "and donor engagement."
        )
    )

    assert (
        priority["expected_impact"]
        == "Improve funding sustainability."
    )


def test_duplicate_risk_and_recommendation_are_not_repeated():
    result = generate_executive_decision_intelligence(
        risk_assessment=[
            {
                "severity": "High",
                "category": "Financial Health",
                "title": "Weak financial health",
                "evidence": (
                    "Financial Health Score is 54/100."
                ),
                "recommendation": (
                    "Prioritize weak categories."
                ),
            }
        ],
        forward_risks=[],
        cfo_recommendations=[
            {
                "priority": "High",
                "category": "Financial Health",
                "title": (
                    "Address Weak financial health"
                ),
                "evidence": (
                    "Financial Health Score is 54/100."
                ),
                "action": (
                    "Prepare a financial recovery plan."
                ),
                "expected_impact": (
                    "Improve financial resilience."
                ),
                "linked_risk": (
                    "Weak financial health"
                ),
                "source": "risk_assessment",
            }
        ],
        financial_opportunities=[],
    )

    assert result["priority_count"] == 1

    priority = result["priorities"][0]

    assert (
        priority["title"]
        == "Weak financial health"
    )

    assert (
        priority["management_action"]
        == "Prepare a financial recovery plan."
    )


def test_highest_severity_duplicate_is_preserved():
    result = generate_executive_decision_intelligence(
        risk_assessment=[
            {
                "severity": "High",
                "category": "Liquidity",
                "title": "Liquidity pressure",
                "evidence": "Current liquidity pressure exists.",
                "recommendation": "Review liquidity.",
            }
        ],
        forward_risks=[
            {
                "severity": "Critical",
                "category": "Liquidity",
                "title": "Liquidity pressure",
                "evidence": (
                    "Future liquidity pressure becomes critical."
                ),
                "recommendation": (
                    "Take immediate liquidity action."
                ),
            }
        ],
        cfo_recommendations=[],
        financial_opportunities=[],
    )

    assert result["priority_count"] == 1
    assert (
        result["priorities"][0]["priority"]
        == "Critical"
    )
    assert (
        result["executive_signal"]
        == "immediate_action"
    )


def test_recommendation_without_risk_can_become_priority():
    result = generate_executive_decision_intelligence(
        risk_assessment=[],
        forward_risks=[],
        cfo_recommendations=[
            {
                "priority": "High",
                "category": "Grant Management",
                "title": (
                    "Resolve out-of-period secured funding"
                ),
                "evidence": (
                    "Secured funding exists outside "
                    "the applicable grant period."
                ),
                "action": (
                    "Review replacement funding and "
                    "possible donor-approved extensions."
                ),
                "expected_impact": (
                    "Prevent reliance on ineligible funding."
                ),
                "linked_risk": (
                    "Grant period eligibility"
                ),
                "source": "funding_gap",
            }
        ],
        financial_opportunities=[],
    )

    assert result["priority_count"] == 1

    priority = result["priorities"][0]

    assert priority["priority"] == "High"
    assert (
        priority["title"]
        == "Grant period eligibility"
    )
    assert (
        priority["source"]
        == "funding_gap"
    )


def test_opportunities_remain_separate_from_management_priorities():
    result = generate_executive_decision_intelligence(
        risk_assessment=[
            {
                "severity": "Critical",
                "category": "Liquidity",
                "title": "Critical cash runway",
                "evidence": (
                    "Cash runway is critically low."
                ),
                "recommendation": (
                    "Preserve cash immediately."
                ),
            }
        ],
        forward_risks=[],
        cfo_recommendations=[],
        financial_opportunities=[
            {
                "priority": "High",
                "category": "Funding",
                "title": (
                    "High secured-funding coverage"
                ),
                "evidence": (
                    "90% of remaining requirements are covered."
                ),
                "recommended_action": (
                    "Protect secured funding coverage."
                ),
            }
        ],
    )

    assert result["priority_count"] == 1
    assert result["opportunity_count"] == 1

    assert (
        result["priorities"][0]["title"]
        == "Critical cash runway"
    )

    assert (
        result["opportunities"][0]["title"]
        == "High secured-funding coverage"
    )

    assert (
        result["executive_signal"]
        == "immediate_action"
    )


def test_opportunity_does_not_reduce_risk_severity():
    result = generate_executive_decision_intelligence(
        risk_assessment=[
            {
                "severity": "High",
                "category": "Funding Sustainability",
                "title": (
                    "Unfunded financial requirements"
                ),
                "evidence": (
                    "A validated Funding Gap remains."
                ),
                "recommendation": (
                    "Prioritize uncovered requirements."
                ),
            }
        ],
        forward_risks=[],
        cfo_recommendations=[],
        financial_opportunities=[
            {
                "priority": "High",
                "category": "Funding",
                "title": (
                    "Secured funding coverage opportunity"
                ),
                "evidence": (
                    "Eligible secured funding covers "
                    "part of the requirement."
                ),
                "recommended_action": (
                    "Protect validated funding coverage."
                ),
            }
        ],
    )

    assert result["highest_priority"] == "High"
    assert (
        result["executive_signal"]
        == "priority_attention"
    )
    assert result["priority_count"] == 1
    assert result["opportunity_count"] == 1


def test_priorities_are_sorted_by_severity():
    result = generate_executive_decision_intelligence(
        risk_assessment=[
            {
                "severity": "Medium",
                "category": "Liquidity",
                "title": "Liquidity monitoring",
                "evidence": "Liquidity requires monitoring.",
                "recommendation": "Monitor liquidity.",
            },
            {
                "severity": "Critical",
                "category": "Financial Health",
                "title": "Critical financial health",
                "evidence": "Health is critical.",
                "recommendation": "Take immediate action.",
            },
            {
                "severity": "High",
                "category": "Budget Control",
                "title": "Material budget control issues",
                "evidence": "Budget control issues exist.",
                "recommendation": "Review budget control.",
            },
        ],
        forward_risks=[],
        cfo_recommendations=[],
        financial_opportunities=[],
    )

    priorities = result["priorities"]

    assert priorities[0]["priority"] == "Critical"
    assert priorities[1]["priority"] == "High"
    assert priorities[2]["priority"] == "Medium"

    assert priorities[0]["rank"] == 1
    assert priorities[1]["rank"] == 2
    assert priorities[2]["rank"] == 3


def test_management_focus_contains_top_five_only():
    risks = []

    for index in range(7):
        risks.append(
            {
                "severity": "High",
                "category": f"Category {index}",
                "title": f"Risk {index}",
                "evidence": f"Evidence {index}",
                "recommendation": f"Action {index}",
            }
        )

    result = generate_executive_decision_intelligence(
        risk_assessment=risks,
        forward_risks=[],
        cfo_recommendations=[],
        financial_opportunities=[],
    )

    assert result["priority_count"] == 7
    assert len(result["management_focus"]) == 5

    assert (
        result["management_focus"][0]["rank"]
        == 1
    )

    assert (
        result["management_focus"][4]["rank"]
        == 5
    )


def test_fallback_risk_is_not_treated_as_material_priority():
    result = generate_executive_decision_intelligence(
        risk_assessment=[
            {
                "severity": "Low",
                "category": "General",
                "title": (
                    "No major financial risks detected"
                ),
                "evidence": (
                    "No major deterministic risks found."
                ),
                "recommendation": (
                    "Continue monitoring."
                ),
            }
        ],
        forward_risks=[],
        cfo_recommendations=[],
        financial_opportunities=[],
    )

    assert result["priority_count"] == 0
    assert result["highest_priority"] == "Low"
    assert result["executive_signal"] == "monitor"


def test_general_monitoring_recommendation_is_not_material_priority():
    result = generate_executive_decision_intelligence(
        risk_assessment=[],
        forward_risks=[],
        cfo_recommendations=[
            {
                "priority": "Low",
                "category": "Monitoring",
                "title": "Maintain financial monitoring",
                "evidence": (
                    "No material corrective action identified."
                ),
                "action": (
                    "Continue monitoring."
                ),
                "source": "general_monitoring",
            }
        ],
        financial_opportunities=[],
    )

    assert result["priority_count"] == 0
    assert result["executive_signal"] == "monitor"


def test_controls_protect_validated_financial_outputs():
    result = generate_executive_decision_intelligence(
        risk_assessment=[],
        forward_risks=[],
        cfo_recommendations=[],
        financial_opportunities=[],
    )

    controls = result["controls"]

    assert controls["deterministic"] is True

    assert (
        controls["financial_recalculation_performed"]
        is False
    )

    assert (
        controls["validated_outputs_preserved"]
        is True
    )

    assert (
        controls["missing_evidence_not_invented"]
        is True
    )

    assert (
        controls["opportunities_do_not_cancel_risks"]
        is True
    )

def test_organization_initializes_executive_decision_intelligence():
    from app.organization import Organization

    organization = Organization()

    assert (
        organization.executive_decision_intelligence
        == {}
    )


def test_organization_builds_executive_decision_intelligence():
    from app.organization import Organization

    organization = Organization()

    organization.risk_assessment = [
        {
            "severity": "High",
            "category": "Liquidity",
            "title": "Low cash runway",
            "evidence": (
                "Available cash provides 4 months "
                "of operating coverage."
            ),
            "recommendation": (
                "Review the rolling cash forecast."
            ),
        }
    ]

    organization.forward_risks = []

    organization.financial_opportunities = [
        {
            "priority": "Medium",
            "category": "Funding",
            "title": "Funding opportunity",
            "evidence": "Validated funding opportunity exists.",
            "recommended_action": (
                "Protect the funding opportunity."
            ),
        }
    ]

    organization.cfo_recommendations = []

    organization.build_executive_decision_intelligence()

    result = (
        organization.executive_decision_intelligence
    )

    assert result["status"] == "available"
    assert result["highest_priority"] == "High"
    assert (
        result["executive_signal"]
        == "priority_attention"
    )
    assert result["priority_count"] == 1
    assert result["opportunity_count"] == 1


def test_organization_executive_decision_intelligence_preserves_sources():
    from app.organization import Organization

    organization = Organization()

    risk_assessment = [
        {
            "severity": "Critical",
            "category": "Liquidity",
            "title": "Critical cash runway",
            "evidence": "Cash runway is critical.",
            "recommendation": "Preserve cash.",
        }
    ]

    opportunities = [
        {
            "priority": "High",
            "category": "Funding",
            "title": "Secured funding coverage",
            "evidence": "Funding coverage is strong.",
            "recommended_action": "Protect coverage.",
        }
    ]

    organization.risk_assessment = risk_assessment
    organization.forward_risks = []
    organization.cfo_recommendations = []
    organization.financial_opportunities = opportunities

    organization.build_executive_decision_intelligence()

    assert organization.risk_assessment == risk_assessment

    assert (
        organization.financial_opportunities
        == opportunities
    )

    controls = (
        organization
        .executive_decision_intelligence[
            "controls"
        ]
    )

    assert (
        controls["financial_recalculation_performed"]
        is False
    )

    assert (
        controls["validated_outputs_preserved"]
        is True
    )   