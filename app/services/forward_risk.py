from typing import Any


def generate_forward_risks(
    risk_assessment: list[dict[str, Any]] | None,
    financial_trends: dict[str, Any] | None,
    financial_forecast: dict[str, Any] | None,
    liquidity: dict[str, Any] | None,
    funding_gap: dict[str, Any] | None,
    grant_diagnostics: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """
    Generate evidence-based forward-looking financial risks.

    Forward-looking risks are separate from the current
    AI-FOS Risk Register.

    This engine does not recalculate financial statements,
    forecasts, liquidity, or Funding Gap values. It consumes
    validated AI-FOS outputs and identifies emerging risks
    supported by those outputs.
    """

    risk_assessment = risk_assessment or []
    financial_trends = financial_trends or {}
    financial_forecast = financial_forecast or {}
    liquidity = liquidity or {}
    funding_gap = funding_gap or {}
    grant_diagnostics = grant_diagnostics or {}

    forward_risks: list[dict[str, Any]] = []

    # --------------------------------------------------
    # Validated forward-looking evidence
    # --------------------------------------------------

    forecast_status = financial_forecast.get("status")

    forecast_totals = (
        financial_forecast.get(
            "forecast_totals",
            {},
        )
        or {}
    )

    forecast_revenue = _optional_float(
        forecast_totals.get("revenue")
    )

    forecast_expenses = _optional_float(
        forecast_totals.get("expenses")
    )

    forecast_net_result = _optional_float(
        forecast_totals.get("net_result")
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

    latest_month_comparison = (
        financial_trends.get(
            "latest_month_comparison",
            {},
        )
        or {}
    )

    revenue_change_percentage = _extract_change_percentage(
        latest_month_comparison,
        "revenue",
    )

    expense_change_percentage = _extract_change_percentage(
        latest_month_comparison,
        "expenses",
    )

    cash_runway_months = _optional_float(
        liquidity.get(
            "cash_runway_months"
        )
    )

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

    applied_coverage_percentage = _optional_float(
        funding_gap_summary.get(
            "applied_coverage_percentage"
        )
    )

    period_unknown_exposure = _optional_float(
        funding_gap_summary.get(
            "period_unknown_funding_exposure"
        )
    )

    # --------------------------------------------------
    # 1. Forecast operating deficit
    # --------------------------------------------------

    if (
        forecast_status == "available"
        and forecast_net_result is not None
        and forecast_net_result < 0
    ):
        forward_risks.append(
            {
                "severity": "High",
                "category": "Operating Performance",
                "title": "Forecast operating deficit",
                "evidence": (
                    f"The validated baseline forecast projects "
                    f"a net result of "
                    f"{forecast_net_result:,.2f} USD "
                    f"over the next "
                    f"{forecast_horizon_months} month(s). "
                    f"Forecast confidence is "
                    f"{forecast_confidence}."
                ),
                "recommendation": (
                    "Review the forecast deficit drivers, "
                    "identify controllable expenditure, assess "
                    "realistic revenue actions, and prepare a "
                    "management response before the projected "
                    "deficit materializes."
                ),
            }
        )

    # --------------------------------------------------
    # 2. Revenue deterioration combined with forecast risk
    # --------------------------------------------------

    if (
        revenue_change_percentage is not None
        and revenue_change_percentage < 0
        and forecast_status == "available"
        and forecast_net_result is not None
        and forecast_net_result < 0
    ):
        forward_risks.append(
            {
                "severity": "High",
                "category": "Revenue Sustainability",
                "title": (
                    "Revenue decline reinforcing forecast deficit"
                ),
                "evidence": (
                    f"Validated monthly trend analysis shows "
                    f"revenue changed by "
                    f"{revenue_change_percentage:,.2f}% "
                    f"from the previous observed month, while "
                    f"the baseline forecast projects a net "
                    f"result of {forecast_net_result:,.2f} USD."
                ),
                "recommendation": (
                    "Assess whether the revenue decline is "
                    "temporary or structural, review the "
                    "revenue pipeline and donor funding outlook, "
                    "and prepare corrective actions if the "
                    "decline continues."
                ),
            }
        )

    # --------------------------------------------------
    # 3. Expense growth pressure
    # --------------------------------------------------

    if (
        expense_change_percentage is not None
        and expense_change_percentage > 0
        and forecast_status == "available"
        and forecast_expenses is not None
    ):
        forward_risks.append(
            {
                "severity": "Medium",
                "category": "Cost Management",
                "title": "Rising expense pressure",
                "evidence": (
                    f"Validated monthly trend analysis shows "
                    f"expenses increased by "
                    f"{expense_change_percentage:,.2f}% "
                    f"from the previous observed month. "
                    f"The baseline forecast projects "
                    f"{forecast_expenses:,.2f} USD of expenses "
                    f"over the next "
                    f"{forecast_horizon_months} month(s)."
                ),
                "recommendation": (
                    "Review the main drivers of recent expense "
                    "growth and determine whether the increase "
                    "is planned, temporary, or likely to continue."
                ),
            }
        )

    # --------------------------------------------------
    # 4. Forward liquidity pressure
    # --------------------------------------------------

    if (
        cash_runway_months is not None
        and cash_runway_months < 6
    ):
        severity = (
            "High"
            if cash_runway_months < 3
            else "Medium"
        )

        forward_risks.append(
            {
                "severity": severity,
                "category": "Liquidity",
                "title": "Limited forward cash runway",
                "evidence": (
                    f"Validated liquidity analysis shows "
                    f"{cash_runway_months:,.2f} months of "
                    f"cash runway based on available cash and "
                    f"the authoritative operating-expense basis."
                ),
                "recommendation": (
                    "Prepare a rolling liquidity response plan, "
                    "review expected receipts and committed "
                    "payments, and identify actions required "
                    "before available cash reaches a critical "
                    "level."
                ),
            }
        )

    # --------------------------------------------------
    # 5. Material future Funding Gap
    # --------------------------------------------------

    if (
        funding_gap_amount is not None
        and funding_gap_amount > 0
    ):
        coverage_text = ""

        if applied_coverage_percentage is not None:
            coverage_text = (
                f" Applied secured-funding coverage is "
                f"{applied_coverage_percentage:,.2f}%."
            )

        requirement_text = ""

        if remaining_requirement is not None:
            requirement_text = (
                f" Remaining validated requirement is "
                f"{remaining_requirement:,.2f} USD."
            )

        forward_risks.append(
            {
                "severity": "High",
                "category": "Funding",
                "title": "Forward Funding Gap exposure",
                "evidence": (
                    f"Validated Funding Gap analysis identifies "
                    f"a remaining Funding Gap of "
                    f"{funding_gap_amount:,.2f} USD."
                    f"{requirement_text}"
                    f"{coverage_text}"
                ),
                "recommendation": (
                    "Prioritize funding actions against the "
                    "remaining requirement, distinguish secured "
                    "funding from expected funding, and maintain "
                    "management visibility over uncovered future "
                    "needs."
                ),
            }
        )

    # --------------------------------------------------
    # 6. Funding-period evidence uncertainty
    # --------------------------------------------------

    if (
        period_unknown_exposure is not None
        and period_unknown_exposure > 0
    ):
        forward_risks.append(
            {
                "severity": "Medium",
                "category": "Funding",
                "title": "Future funding eligibility uncertainty",
                "evidence": (
                    f"Funding Gap diagnostics identify "
                    f"{period_unknown_exposure:,.2f} USD of "
                    f"requirement-level funding exposure where "
                    f"grant-period evidence is missing or "
                    f"incomplete."
                ),
                "recommendation": (
                    "Complete missing grant start and end dates "
                    "and validate period eligibility before "
                    "management relies on this funding for "
                    "future requirements."
                ),
            }
        )

    # --------------------------------------------------
    # 7. Forecast revenue below forecast expenses
    # --------------------------------------------------

    if (
        forecast_status == "available"
        and forecast_revenue is not None
        and forecast_expenses is not None
        and forecast_revenue < forecast_expenses
        and not _has_title(
            forward_risks,
            "Forecast operating deficit",
        )
    ):
        forward_risks.append(
            {
                "severity": "High",
                "category": "Operating Performance",
                "title": "Forecast revenue below expenses",
                "evidence": (
                    f"The validated baseline forecast projects "
                    f"revenue of {forecast_revenue:,.2f} USD "
                    f"against expenses of "
                    f"{forecast_expenses:,.2f} USD over the "
                    f"forecast horizon."
                ),
                "recommendation": (
                    "Review the projected operating imbalance "
                    "and identify revenue, funding, or cost "
                    "actions required to improve sustainability."
                ),
            }
        )

    # --------------------------------------------------
    # Sort by severity
    # --------------------------------------------------

    severity_order = {
        "Critical": 4,
        "High": 3,
        "Medium": 2,
        "Low": 1,
    }

    forward_risks.sort(
        key=lambda risk: severity_order.get(
            str(risk.get("severity")),
            0,
        ),
        reverse=True,
    )

    return forward_risks


def _extract_change_percentage(
    comparison: dict[str, Any],
    metric: str,
) -> float | None:
    """
    Read an already-calculated percentage change from the
    validated trend artifact.

    Multiple field shapes are accepted because the trend
    artifact may expose metrics either as nested dictionaries
    or flattened comparison fields.

    No percentage is calculated here.
    """

    metric_data = comparison.get(metric)

    if isinstance(metric_data, dict):
        for field in (
            "change_percentage",
            "percentage_change",
            "change_percent",
        ):
            value = _optional_float(
                metric_data.get(field)
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
            comparison.get(field)
        )

        if value is not None:
            return value

    return None


def _has_title(
    risks: list[dict[str, Any]],
    title: str,
) -> bool:
    return any(
        str(risk.get("title")) == title
        for risk in risks
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
        return float(value)

    except (
        TypeError,
        ValueError,
    ):
        return None


def _to_int(
    value: Any,
) -> int:
    try:
        return int(value)

    except (
        TypeError,
        ValueError,
    ):
        return 0