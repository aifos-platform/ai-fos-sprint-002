from typing import Any


def generate_risk_assessment(
    income_statement: dict[str, Any] | None,
    balance_sheet: dict[str, Any] | None,
    liquidity: dict[str, Any] | None,
    financial_health: dict[str, Any] | None,
    budget_dashboard: dict[str, Any] | None,
    grant_diagnostics: dict[str, Any] | None,
    funding_gap: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """
    Build the AI-FOS CFO Risk Register.

    Risks are represented as structured objects so they
    can be reused by dashboards, reports, recommendations,
    and the AI CFO.

    Risk conclusions are based on validated financial
    evidence rather than gross balances alone.
    """

    income_statement = (
        income_statement or {}
    )

    balance_sheet = (
        balance_sheet or {}
    )

    liquidity = (
        liquidity or {}
    )

    financial_health = (
        financial_health or {}
    )

    budget_dashboard = (
        budget_dashboard or {}
    )

    grant_diagnostics = (
        grant_diagnostics or {}
    )

    funding_gap = (
        funding_gap or {}
    )

    risks: list[
        dict[str, Any]
    ] = []

    # --------------------------------------------------
    # Core financial facts
    # --------------------------------------------------

    revenue = _to_float(
        income_statement.get(
            "revenue"
        )
    )

    net_result = _to_float(
        income_statement.get(
            "net_profit",
            income_statement.get(
                "net_surplus_deficit",
                0,
            ),
        )
    )

    assets = _to_float(
        balance_sheet.get(
            "assets"
        )
    )

    liabilities = _to_float(
        balance_sheet.get(
            "liabilities"
        )
    )

    health_score = int(
        financial_health.get(
            "score",
            0,
        )
        or 0
    )

    health_rating = str(
        financial_health.get(
            "rating",
            ""
        )
        or ""
    ).strip()

    cash_runway_months = _to_float(
        liquidity.get(
            "cash_runway_months"
        )
    )

    # --------------------------------------------------
    # Budget facts
    # --------------------------------------------------

    budget_executive_summary = (
        budget_dashboard.get(
            "executive_summary",
            {},
        )
        or {}
    )

    budget_health = (
        budget_dashboard.get(
            "budget_health",
            {},
        )
        or {}
    )

    total_budget = _to_float(
        budget_executive_summary.get(
            "total_budget"
        )
    )

    budgeted_actual = _to_float(
        budget_executive_summary.get(
            "budgeted_actual"
        )
    )

    unbudgeted_actual = _to_float(
        budget_executive_summary.get(
            "unbudgeted_actual"
        )
    )

    over_budget_count = int(
        budget_health.get(
            "over_budget_count",
            0,
        )
        or 0
    )

    no_budget_count = int(
        budget_health.get(
            "no_budget_count",
            0,
        )
        or 0
    )

    budget_utilization = (
        budgeted_actual
        / total_budget
        * 100
        if total_budget > 0
        else 0.0
    )

    unbudgeted_percentage = (
        abs(
            unbudgeted_actual
        )
        / total_budget
        * 100
        if total_budget > 0
        else 0.0
    )

    # --------------------------------------------------
    # Funding Gap facts
    # --------------------------------------------------

    funding_gap_summary = (
        funding_gap.get(
            "summary",
            {},
        )
        or {}
    )

    funding_gap_amount = _to_float(
        funding_gap_summary.get(
            "funding_gap"
        )
    )

    remaining_requirement = _to_float(
        funding_gap_summary.get(
            "remaining_requirement"
        )
    )

    applied_secured_funding = _to_float(
        funding_gap_summary.get(
            "applied_secured_funding"
        )
    )

    gross_remaining_secured_funding = _to_float(
        funding_gap_summary.get(
            "gross_remaining_secured_funding"
        )
    )

    applied_coverage_percentage = _to_float(
        funding_gap_summary.get(
            "applied_coverage_percentage"
        )
    )

    matched_requirement_count = int(
        funding_gap_summary.get(
            "matched_requirement_count",
            0,
        )
        or 0
    )

    unmatched_requirement_count = int(
        funding_gap_summary.get(
            "unmatched_requirement_count",
            0,
        )
        or 0
    )

    secured_without_budget_line = _to_float(
        funding_gap_summary.get(
            "secured_funding_without_budget_line_allocation"
        )
    )

    # --------------------------------------------------
    # 1. Operating performance risk
    # --------------------------------------------------

    if (
        revenue > 0
        and net_result < 0
    ):

        deficit_ratio = (
            abs(
                net_result
            )
            / revenue
            * 100
        )

        risks.append(
            {
                "severity": "High",
                "category": "Operating Performance",
                "title": "Operating deficit",
                "evidence": (
                    f"Net result is {net_result:,.2f} USD, "
                    f"representing a deficit of "
                    f"{deficit_ratio:.2f}% of revenue."
                ),
                "recommendation": (
                    "Identify the main drivers of the deficit, "
                    "review controllable expenditure, and assess "
                    "whether additional recurring revenue or "
                    "funding is required to restore operating "
                    "sustainability."
                ),
            }
        )

    # --------------------------------------------------
    # 2. Financial position risk
    # --------------------------------------------------

    if liabilities > assets:

        risks.append(
            {
                "severity": "High",
                "category": "Financial Position",
                "title": "Liabilities exceed assets",
                "evidence": (
                    f"Liabilities are {liabilities:,.2f} USD "
                    f"while assets are {assets:,.2f} USD."
                ),
                "recommendation": (
                    "Review the composition and timing of "
                    "liabilities, assess recoverable assets and "
                    "funding commitments, and prepare a plan to "
                    "restore positive net assets."
                ),
            }
        )

    # --------------------------------------------------
    # 3. Overall Financial Health risk
    # --------------------------------------------------

    if health_score < 40:

        risks.append(
            {
                "severity": "Critical",
                "category": "Financial Health",
                "title": "Critical financial health",
                "evidence": (
                    f"Financial Health Score is "
                    f"{health_score}/100"
                    + (
                        f" with a {health_rating} rating."
                        if health_rating
                        else "."
                    )
                ),
                "recommendation": (
                    "Review the lowest-scoring Financial Health "
                    "categories immediately and prepare a "
                    "management action plan with clear owners "
                    "and deadlines."
                ),
            }
        )

    elif health_score < 55:

        risks.append(
            {
                "severity": "High",
                "category": "Financial Health",
                "title": "Weak financial health",
                "evidence": (
                    f"Financial Health Score is "
                    f"{health_score}/100"
                    + (
                        f" with a {health_rating} rating."
                        if health_rating
                        else "."
                    )
                ),
                "recommendation": (
                    "Prioritize the lowest-scoring Financial "
                    "Health categories and address the underlying "
                    "operating, funding, liquidity, and budget "
                    "control weaknesses."
                ),
            }
        )

    # --------------------------------------------------
    # 4. Liquidity risk
    # --------------------------------------------------

    if (
        0
        < cash_runway_months
        < 3
    ):

        risks.append(
            {
                "severity": "Critical",
                "category": "Liquidity",
                "title": "Critical cash runway",
                "evidence": (
                    f"Available cash provides only "
                    f"{cash_runway_months:.2f} months of "
                    f"operating expense coverage."
                ),
                "recommendation": (
                    "Take immediate action to preserve cash, "
                    "accelerate confirmed funding receipts, "
                    "secure additional eligible funding, or "
                    "reduce near-term expenditure."
                ),
            }
        )

    elif (
        3
        <= cash_runway_months
        < 6
    ):

        risks.append(
            {
                "severity": "High",
                "category": "Liquidity",
                "title": "Low cash runway",
                "evidence": (
                    f"Available cash provides "
                    f"{cash_runway_months:.2f} months of "
                    f"operating expense coverage."
                ),
                "recommendation": (
                    "Review the rolling cash forecast, expected "
                    "funding receipts, and near-term expenditure "
                    "commitments."
                ),
            }
        )

    elif (
        6
        <= cash_runway_months
        < 9
    ):

        risks.append(
            {
                "severity": "Medium",
                "category": "Liquidity",
                "title": "Cash runway requires monitoring",
                "evidence": (
                    f"Available cash provides "
                    f"{cash_runway_months:.2f} months of "
                    f"operating expense coverage."
                ),
                "recommendation": (
                    "Monitor liquidity closely and maintain an "
                    "updated forecast of funding receipts and "
                    "future operating requirements."
                ),
            }
        )

    # --------------------------------------------------
    # 5. Funding sustainability risk
    # --------------------------------------------------

    if (
        funding_gap_amount > 0
        and remaining_requirement > 0
    ):

        funding_gap_percentage = (
            funding_gap_amount
            / remaining_requirement
            * 100
        )

        if funding_gap_percentage >= 50:

            funding_gap_severity = (
                "High"
            )

        elif funding_gap_percentage >= 25:

            funding_gap_severity = (
                "High"
            )

        elif funding_gap_percentage >= 10:

            funding_gap_severity = (
                "Medium"
            )

        else:

            funding_gap_severity = (
                "Low"
            )

        risks.append(
            {
                "severity": (
                    funding_gap_severity
                ),
                "category": (
                    "Funding Sustainability"
                ),
                "title": (
                    "Unfunded financial requirements"
                ),
                "evidence": (
                    f"AI-FOS identifies a Funding Gap of "
                    f"{funding_gap_amount:,.2f} USD against "
                    f"remaining requirements of "
                    f"{remaining_requirement:,.2f} USD. "
                    f"Validated eligible secured funding of "
                    f"{applied_secured_funding:,.2f} USD covers "
                    f"{applied_coverage_percentage:.2f}% of "
                    f"remaining requirements. "
                    f"{matched_requirement_count} requirement(s) "
                    f"have validated eligible secured funding "
                    f"and {unmatched_requirement_count} "
                    f"requirement(s) currently do not."
                ),
                "recommendation": (
                    "Prioritize uncovered requirements, "
                    "identify additional eligible funding, "
                    "review whether currently unallocated or "
                    "restricted secured funding can be supported "
                    "by sufficient eligibility evidence, and "
                    "avoid committing expenditure against "
                    "funding that has not been validated."
                ),
            }
        )

    # --------------------------------------------------
    # 6. Secured funding evidence risk
    # --------------------------------------------------

    if secured_without_budget_line > 0:

        risks.append(
            {
                "severity": "Medium",
                "category": "Funding Evidence",
                "title": (
                    "Secured funding lacks explicit "
                    "Budget Line allocation"
                ),
                "evidence": (
                    f"{secured_without_budget_line:,.2f} USD of "
                    f"remaining secured funding does not have an "
                    f"explicit internal Budget Line allocation "
                    f"available for automatic Funding Gap "
                    f"coverage. Gross remaining secured funding "
                    f"is {gross_remaining_secured_funding:,.2f} USD."
                ),
                "recommendation": (
                    "Review the underlying donor budgets and "
                    "internal mappings. Where supported by donor "
                    "terms, document and map the funding to the "
                    "appropriate internal Budget Lines before "
                    "treating it as available for requirement "
                    "coverage."
                ),
            }
        )

    # --------------------------------------------------
    # 7. Budget control risk
    # --------------------------------------------------

    if (
        budget_utilization > 100
        or unbudgeted_actual > 0
        or over_budget_count > 0
        or no_budget_count > 0
    ):

        risks.append(
            {
                "severity": "High",
                "category": "Budget Control",
                "title": "Material budget control issues",
                "evidence": (
                    f"Budget utilization is "
                    f"{budget_utilization:.2f}%. "
                    f"Unbudgeted actual spending is "
                    f"{unbudgeted_actual:,.2f} USD "
                    f"({unbudgeted_percentage:.2f}% of total "
                    f"budget). {over_budget_count} aggregated "
                    f"budget line code(s) are above budget and "
                    f"{no_budget_count} aggregated budget line "
                    f"code(s) have actual activity without an "
                    f"identified budget amount."
                ),
                "recommendation": (
                    "Review overspent and unbudgeted activity, "
                    "confirm whether reallocations or formal "
                    "budget revisions are required, and "
                    "strengthen periodic budget monitoring."
                ),
            }
        )

    # --------------------------------------------------
    # Fallback
    # --------------------------------------------------

    if not risks:

        risks.append(
            {
                "severity": "Low",
                "category": "General",
                "title": "No major financial risks detected",
                "evidence": (
                    "The current deterministic financial risk "
                    "rules found no major financial issues."
                ),
                "recommendation": (
                    "Continue monitoring financial performance, "
                    "liquidity, budget execution, and funding "
                    "coverage."
                ),
            }
        )

    return risks

def _to_float(
    value: Any,
) -> float:
    """
    Safely convert a financial value to float.
    """

    if value is None:
        return 0.0

    if isinstance(
        value,
        (int, float),
    ):
        return float(value)

    text = (
        str(value)
        .replace(",", "")
        .replace("$", "")
        .strip()
    )

    if not text:
        return 0.0

    if (
        text.startswith("(")
        and text.endswith(")")
    ):
        text = "-" + text[1:-1]

    try:
        return float(text)

    except (
        TypeError,
        ValueError,
    ):
        return 0.0
