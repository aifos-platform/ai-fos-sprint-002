from typing import Any

PRIORITY_ORDER = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


def generate_cfo_recommendations(
    income_statement: dict[str, Any] | None,
    balance_sheet: dict[str, Any] | None,
    cash_flow: dict[str, Any] | None,
    financial_health: dict[str, Any] | None,
    risk_assessment: list[dict[str, Any]] | None,
    budget_dashboard: dict[str, Any] | None,
    grant_diagnostics: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """
    Generate structured, evidence-based CFO recommendations.

    Recommendations are derived only from verified AI-FOS
    financial outputs. They can be reused by the AI CFO,
    dashboards, reports, and the Question Engine.
    """

    income_statement = income_statement or {}
    balance_sheet = balance_sheet or {}
    cash_flow = cash_flow or {}
    financial_health = financial_health or {}
    risk_assessment = risk_assessment or []
    budget_dashboard = budget_dashboard or {}
    grant_diagnostics = grant_diagnostics or {}

    recommendations: list[dict[str, Any]] = []

    # --------------------------------------------------
    # 1. Convert detected risks into management actions
    # --------------------------------------------------

    for risk in risk_assessment:

        severity = str(risk.get("severity") or "Medium")

        category = str(risk.get("category") or "Financial Management")

        title = str(risk.get("title") or "Financial risk")

        evidence = str(risk.get("evidence") or "")

        action = str(
            risk.get("recommendation") or "Review the underlying financial issue."
        )

        recommendations.append(
            {
                "priority": severity,
                "category": category,
                "title": f"Address {title}",
                "evidence": evidence,
                "action": action,
                "expected_impact": _expected_impact(
                    category=category,
                ),
                "linked_risk": title,
                "source": "risk_assessment",
            }
        )

    # --------------------------------------------------
    # 2. Cash-flow recommendations
    # --------------------------------------------------

    operating_cash_flow = _to_float(cash_flow.get("operating_activities"))

    if operating_cash_flow < 0:

        recommendations.append(
            {
                "priority": "High",
                "category": "Cash Flow",
                "title": "Improve operating cash generation",
                "evidence": (f"Operating cash flow is " f"{operating_cash_flow:,.2f}."),
                "action": (
                    "Review the drivers of negative operating "
                    "cash flow, accelerate eligible collections, "
                    "and control discretionary cash outflows."
                ),
                "expected_impact": (
                    "Strengthen liquidity and reduce pressure " "on available cash."
                ),
                "linked_risk": None,
                "source": "cash_flow",
            }
        )

    

    # --------------------------------------------------
    # 4. Grant-data recommendations
    # --------------------------------------------------

    actual_only_grants = (
        grant_diagnostics.get(
            "actual_only_grants",
            [],
        )
        or []
    )

    budget_only_grants = (
        grant_diagnostics.get(
            "budget_only_grants",
            [],
        )
        or []
    )

    if actual_only_grants:

        recommendations.append(
            {
                "priority": "Medium",
                "category": "Grant Management",
                "title": "Resolve grants with actuals but no budget",
                "evidence": (
                    f"{len(actual_only_grants)} grant(s) "
                    f"have actual transactions without "
                    f"corresponding budget data."
                ),
                "action": (
                    "Confirm the correct grant budgets and "
                    "mapping before relying on utilization "
                    "or variance results."
                ),
                "expected_impact": (
                    "Improve grant reporting accuracy and "
                    "reduce donor-reporting risk."
                ),
                "linked_risk": None,
                "source": "grant_diagnostics",
            }
        )

    if budget_only_grants:

        recommendations.append(
            {
                "priority": "Medium",
                "category": "Grant Management",
                "title": "Review grants with budget but no actuals",
                "evidence": (
                    f"{len(budget_only_grants)} grant(s) "
                    f"have budget data but no actual activity."
                ),
                "action": (
                    "Confirm whether implementation has not "
                    "started, transactions are missing, or "
                    "grant mapping requires correction."
                ),
                "expected_impact": (
                    "Improve visibility over grant execution "
                    "and delayed implementation."
                ),
                "linked_risk": None,
                "source": "grant_diagnostics",
            }
        )

    # --------------------------------------------------
    # 5. Financial-health recommendation
    # --------------------------------------------------

    health_score = _to_float(financial_health.get("score"))

    health_rating = str(financial_health.get("rating") or "Unknown")

    if health_score < 55:

        recommendations.append(
            {
                "priority": "High",
                "category": "Financial Health",
                "title": "Implement a financial recovery plan",
                "evidence": (
                    f"Financial Health Score is "
                    f"{health_score:.0f}/100 with a "
                    f"{health_rating} rating."
                ),
                "action": (
                    "Review the lowest-scoring financial-health "
                    "categories and assign corrective actions "
                    "with accountable owners and target dates."
                ),
                "expected_impact": (
                    "Create a structured path toward improving "
                    "overall financial resilience."
                ),
                "linked_risk": "Weak financial health",
                "source": "financial_health",
            }
        )

    # --------------------------------------------------
    # 6. Fallback
    # --------------------------------------------------

    if not recommendations:

        recommendations.append(
            {
                "priority": "Low",
                "category": "Monitoring",
                "title": "Maintain financial monitoring",
                "evidence": (
                    "The current rule set did not identify "
                    "a material corrective action."
                ),
                "action": (
                    "Continue monitoring financial performance, "
                    "cash flow, budgets, grants, and emerging risks."
                ),
                "expected_impact": (
                    "Maintain early visibility over changes "
                    "in financial performance."
                ),
                "linked_risk": None,
                "source": "general_monitoring",
            }
        )

    return sorted(
        recommendations,
        key=lambda item: PRIORITY_ORDER.get(
            str(item.get("priority")),
            0,
        ),
        reverse=True,
    )


def _expected_impact(
    category: str,
) -> str:

    category_lower = category.lower()

    if "operating" in category_lower:
        return (
            "Improve operating sustainability and reduce "
            "the risk of continuing deficits."
        )

    if (
        "financial position" in category_lower
        or "solvency" in category_lower
    ):
        return (
            "Strengthen the balance sheet and improve "
            "long-term financial resilience."
        )

    if "funding sustainability" in category_lower:
        return (
            "Reduce uncovered financial requirements and "
            "improve the organization's ability to finance "
            "planned activities with validated eligible funding."
        )

    if "funding evidence" in category_lower:
        return (
            "Improve the evidence and internal allocation of "
            "secured funding so management can distinguish "
            "validated available funding from funding that "
            "cannot yet be relied upon."
        )

    if "health" in category_lower:
        return (
            "Improve the organization's overall "
            "financial-health profile."
        )

    if "liquidity" in category_lower:
        return (
            "Protect available liquidity and improve "
            "the organization's ability to meet obligations."
        )

    if "budget" in category_lower:
        return (
            "Improve budget control and management "
            "of financial resources."
        )

    if "grant" in category_lower:
        return (
            "Improve grant stewardship and donor-reporting "
            "reliability."
        )

    return (
        "Reduce financial risk and improve "
        "management decision-making."
    )

def _to_float(
    value: Any,
) -> float:

    if value in {
        None,
        "",
    }:
        return 0.0

    try:
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return 0.0
