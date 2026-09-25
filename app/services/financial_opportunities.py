from typing import Any


def generate_financial_opportunities(
    financial_trends: dict[str, Any] | None,
    financial_forecast: dict[str, Any] | None,
    liquidity: dict[str, Any] | None,
    funding_gap: dict[str, Any] | None,
    budget_dashboard: dict[str, Any] | None,
    grant_diagnostics: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """
    Generate evidence-based financial opportunities.

    Financial opportunities are separate from current risks
    and forward-looking risks.

    This engine does not recalculate financial statements,
    forecasts, liquidity, budgets, grants, or Funding Gap
    values. It consumes validated AI-FOS outputs and identifies
    positive financial conditions that may support management
    action or improved financial outcomes.
    """

    financial_trends = financial_trends or {}
    financial_forecast = financial_forecast or {}
    liquidity = liquidity or {}
    funding_gap = funding_gap or {}
    budget_dashboard = budget_dashboard or {}
    grant_diagnostics = grant_diagnostics or {}

    opportunities: list[dict[str, Any]] = []

    # --------------------------------------------------
    # Validated forecast evidence
    # --------------------------------------------------

    forecast_status = financial_forecast.get(
        "status"
    )

    forecast_totals = (
        financial_forecast.get(
            "forecast_totals",
            {},
        )
        or {}
    )

    forecast_revenue = _optional_float(
        forecast_totals.get(
            "revenue"
        )
    )

    forecast_expenses = _optional_float(
        forecast_totals.get(
            "expenses"
        )
    )

    forecast_net_result = _optional_float(
        forecast_totals.get(
            "net_result"
        )
    )

    forecast_horizon_months = _to_int(
        financial_forecast.get(
            "forecast_horizon_months"
        )
    )

    confidence = (
        financial_forecast.get(
            "confidence",
            {},
        )
        or {}
    )

    forecast_confidence = str(
        confidence.get(
            "level",
            "Unknown",
        )
    )

    # --------------------------------------------------
    # Validated trend evidence
    # --------------------------------------------------

    latest_month_comparison = (
        financial_trends.get(
            "latest_month_comparison",
            {},
        )
        or {}
    )

    revenue_change_percentage = (
        _extract_change_percentage(
            latest_month_comparison,
            "revenue",
        )
    )

    expense_change_percentage = (
        _extract_change_percentage(
            latest_month_comparison,
            "expenses",
        )
    )

    # --------------------------------------------------
    # Validated liquidity evidence
    # --------------------------------------------------

    cash_runway_months = _optional_float(
        liquidity.get(
            "cash_runway_months"
        )
    )

    # --------------------------------------------------
    # Validated Funding Gap evidence
    # --------------------------------------------------

    funding_gap_summary = (
        funding_gap.get(
            "summary",
            {},
        )
        or {}
    )

    remaining_requirement = _optional_float(
        funding_gap_summary.get(
            "remaining_requirement"
        )
    )

    funding_gap_amount = _optional_float(
        funding_gap_summary.get(
            "funding_gap"
        )
    )

    applied_secured_funding = _optional_float(
        funding_gap_summary.get(
            "applied_secured_funding"
        )
    )

    applied_coverage_percentage = _optional_float(
        funding_gap_summary.get(
            "applied_coverage_percentage"
        )
    )

    # --------------------------------------------------
    # 1. Forecast operating surplus
    # --------------------------------------------------

    if (
        forecast_status == "available"
        and forecast_net_result is not None
        and forecast_net_result > 0
    ):
        opportunities.append(
            {
                "priority": "High",
                "category": "Operating Performance",
                "title": "Forecast operating surplus",
                "evidence": (
                    f"The validated baseline forecast projects "
                    f"a positive net result of "
                    f"{forecast_net_result:,.2f} USD over the "
                    f"next {forecast_horizon_months} month(s). "
                    f"Forecast confidence is "
                    f"{forecast_confidence}."
                ),
                "recommended_action": (
                    "Assess how the projected surplus can best "
                    "strengthen financial resilience, support "
                    "priority activities, build reserves, or "
                    "reduce future funding pressure while "
                    "respecting donor restrictions."
                ),
            }
        )

    # --------------------------------------------------
    # 2. Forecast revenue exceeds expenses
    # --------------------------------------------------

    if (
        forecast_status == "available"
        and forecast_revenue is not None
        and forecast_expenses is not None
        and forecast_revenue > forecast_expenses
        and not _has_title(
            opportunities,
            "Forecast operating surplus",
        )
    ):
        opportunities.append(
            {
                "priority": "High",
                "category": "Operating Performance",
                "title": "Forecast revenue coverage strength",
                "evidence": (
                    f"The validated baseline forecast projects "
                    f"revenue of {forecast_revenue:,.2f} USD "
                    f"against expenses of "
                    f"{forecast_expenses:,.2f} USD over the "
                    f"forecast horizon."
                ),
                "recommended_action": (
                    "Protect the projected operating margin "
                    "and assess whether available financial "
                    "capacity can support strategic priorities "
                    "or strengthen reserves."
                ),
            }
        )

    # --------------------------------------------------
    # 3. Positive revenue momentum
    # --------------------------------------------------

    if (
        revenue_change_percentage is not None
        and revenue_change_percentage > 0
    ):
        opportunities.append(
            {
                "priority": "Medium",
                "category": "Revenue Sustainability",
                "title": "Positive revenue momentum",
                "evidence": (
                    f"Validated monthly trend analysis shows "
                    f"revenue increased by "
                    f"{revenue_change_percentage:,.2f}% from "
                    f"the previous observed month."
                ),
                "recommended_action": (
                    "Identify the drivers of the revenue "
                    "improvement and assess whether they can be "
                    "sustained, expanded, or incorporated into "
                    "future financial planning."
                ),
            }
        )

    # --------------------------------------------------
    # 4. Improving expense trend
    # --------------------------------------------------

    if (
        expense_change_percentage is not None
        and expense_change_percentage < 0
    ):
        opportunities.append(
            {
                "priority": "Medium",
                "category": "Cost Management",
                "title": "Improving expense trend",
                "evidence": (
                    f"Validated monthly trend analysis shows "
                    f"expenses decreased by "
                    f"{abs(expense_change_percentage):,.2f}% "
                    f"from the previous observed month."
                ),
                "recommended_action": (
                    "Review the drivers of the lower spending "
                    "level and determine whether sustainable "
                    "efficiencies can be retained without "
                    "reducing program quality or delivery."
                ),
            }
        )

    # --------------------------------------------------
    # 5. Strong liquidity capacity
    # --------------------------------------------------

    if (
        cash_runway_months is not None
        and cash_runway_months >= 12
    ):
        opportunities.append(
            {
                "priority": "Medium",
                "category": "Liquidity",
                "title": "Strong liquidity capacity",
                "evidence": (
                    f"Validated liquidity analysis shows "
                    f"{cash_runway_months:,.2f} months of "
                    f"cash runway based on available cash and "
                    f"the authoritative operating-expense "
                    f"basis."
                ),
                "recommended_action": (
                    "Use the strong liquidity position to "
                    "improve treasury planning, protect "
                    "operating resilience, and evaluate "
                    "strategic use of unrestricted cash while "
                    "preserving appropriate liquidity buffers."
                ),
            }
        )

    # --------------------------------------------------
    # 6. Secured funding coverage
    # --------------------------------------------------

    if (
        applied_secured_funding is not None
        and applied_secured_funding > 0
        and applied_coverage_percentage is not None
        and applied_coverage_percentage > 0
    ):
        requirement_text = ""

        if remaining_requirement is not None:
            requirement_text = (
                f" against validated remaining requirements "
                f"of {remaining_requirement:,.2f} USD"
            )

        opportunities.append(
            {
                "priority": "High",
                "category": "Funding",
                "title": "Secured funding coverage opportunity",
                "evidence": (
                    f"Validated Funding Gap analysis has "
                    f"applied {applied_secured_funding:,.2f} "
                    f"USD of eligible secured funding"
                    f"{requirement_text}, representing "
                    f"{applied_coverage_percentage:,.2f}% "
                    f"coverage."
                ),
                "recommended_action": (
                    "Protect the validated secured funding "
                    "coverage, align eligible funding with "
                    "priority requirements, and focus "
                    "fundraising attention on the remaining "
                    "uncovered needs."
                ),
            }
        )

    # --------------------------------------------------
    # 7. High secured-funding coverage
    # --------------------------------------------------

    if (
        applied_coverage_percentage is not None
        and applied_coverage_percentage >= 80
        and (
            funding_gap_amount is None
            or funding_gap_amount >= 0
        )
    ):
        opportunities.append(
            {
                "priority": "High",
                "category": "Funding",
                "title": "High secured-funding coverage",
                "evidence": (
                    f"Validated Funding Gap analysis shows "
                    f"{applied_coverage_percentage:,.2f}% of "
                    f"remaining requirements are covered by "
                    f"eligible secured funding."
                ),
                "recommended_action": (
                    "Concentrate management and fundraising "
                    "effort on the remaining uncovered "
                    "requirements and preserve the eligibility "
                    "evidence supporting secured-funding "
                    "coverage."
                ),
            }
        )

    # --------------------------------------------------
    # Conservative v1 treatment of budget and grants
    # --------------------------------------------------

    # Budget Dashboard and Grant Diagnostics are accepted
    # by the engine contract so they can support future
    # opportunity rules. V1 deliberately does not infer
    # opportunities from them until their validated schemas
    # and management meaning are explicitly defined.
    _ = budget_dashboard
    _ = grant_diagnostics

    # --------------------------------------------------
    # Sort by priority
    # --------------------------------------------------

    priority_order = {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1,
    }

    opportunities.sort(
        key=lambda opportunity: priority_order.get(
            str(
                opportunity.get(
                    "priority"
                )
            ),
            0,
        ),
        reverse=True,
    )

    return opportunities


def _extract_change_percentage(
    comparison: dict[str, Any],
    metric: str,
) -> float | None:
    """
    Read an already-calculated percentage change from the
    validated trend artifact.

    No percentage is calculated here.
    """

    metric_data = comparison.get(
        metric
    )

    if isinstance(
        metric_data,
        dict,
    ):
        for field in (
            "change_percentage",
            "percentage_change",
            "change_percent",
        ):
            value = _optional_float(
                metric_data.get(
                    field
                )
            )

            if value is not None:
                return value

    candidate_fields = (
        f"{metric}_change_percentage",
        f"{metric}_percentage_change",
        f"{metric}_change_percent",
    )

    for field in candidate_fields:
        value = _optional_float(
            comparison.get(
                field
            )
        )

        if value is not None:
            return value

    return None


def _has_title(
    opportunities: list[dict[str, Any]],
    title: str,
) -> bool:
    return any(
        str(
            opportunity.get(
                "title"
            )
        )
        == title
        for opportunity in opportunities
    )


def _optional_float(
    value: Any,
) -> float | None:
    if value in {
        None,
        "",
    }:
        return None

    try:
        return float(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return None


def _to_int(
    value: Any,
) -> int:
    try:
        return int(
            value
        )

    except (
        TypeError,
        ValueError,
    ):
        return 0