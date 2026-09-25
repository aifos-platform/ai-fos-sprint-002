from typing import Any


def generate_cfo_insights(
    budget_dashboard: dict[str, Any],
) -> list[str]:
    """
    Generate executive narrative insights
    from the Budget Dashboard.
    """

    insights: list[str] = []

    portfolio_control = budget_dashboard.get(
        "portfolio_control",
        {},
    )

    utilization = portfolio_control.get(
        "utilization_percentage",
        0,
    )

    over_budget = portfolio_control.get(
        "over_budget_count",
        0,
    )

    no_budget = portfolio_control.get(
        "no_budget_count",
        0,
    )

    unbudgeted_actual = portfolio_control.get(
        "unbudgeted_actual",
        0,
    )

    if utilization < 30:
        insights.append(
            (
                f"Portfolio budget utilization is only "
                f"{utilization:.2f}%, indicating that "
                "most planned activities have not yet "
                "been executed."
            )
        )

    elif utilization > 100:
        insights.append(
            (
                f"Portfolio budget utilization has reached "
                f"{utilization:.2f}%, meaning cumulative actual "
                "spending against approved portfolio budget lines "
                "has exceeded the approved portfolio budget."
            )
        )

    elif utilization > 90:
        insights.append(
            (
                f"Portfolio budget utilization has reached "
                f"{utilization:.2f}%, leaving limited "
                "portfolio budget available."
            )
        )

    if over_budget > 0:
        insights.append(
            (
                f"{over_budget} portfolio budget lines are "
                "already above their approved limits."
            )
        )

    if unbudgeted_actual > 0:
        insights.append(
            (
                f"${unbudgeted_actual:,.2f} of portfolio actual "
                "spending has no matching approved "
                "budget and requires management review."
            )
        )

    elif no_budget > 0:
        insights.append(
            (
                f"{no_budget} portfolio budget line(s) have actual "
                "activity without an approved budget."
            )
        )

    if not insights:
        insights.append(
            "No significant financial concerns were detected."
        )

    return insights


def generate_funding_gap_insights(
    funding_gap: dict[str, Any] | None,
) -> list[str]:
    """
    Generate executive narrative insights from the
    validated Funding Gap analysis.

    This function does not recalculate Funding Gap.
    It only explains facts produced by the Funding
    Gap engine.
    """

    if not funding_gap:
        return []

    summary = funding_gap.get(
        "summary",
        {},
    )

    if not summary:
        return []

    insights: list[str] = []

    remaining_requirement = float(
        summary.get(
            "remaining_requirement",
            0,
        )
        or 0
    )

    applied_secured_funding = float(
        summary.get(
            "applied_secured_funding",
            0,
        )
        or 0
    )

    funding_gap_amount = float(
        summary.get(
            "funding_gap",
            0,
        )
        or 0
    )

    coverage_percentage = summary.get(
        "applied_coverage_percentage"
    )

    period_ineligible_exposure = float(
        summary.get(
            "period_ineligible_funding_exposure",
            0,
        )
        or 0
    )

    period_unknown_exposure = float(
        summary.get(
            "period_unknown_funding_exposure",
            0,
        )
        or 0
    )

    dimension_incompatible_exposure = float(
        summary.get(
            "dimension_incompatible_funding_exposure",
            0,
        )
        or 0
    )

    requirements_with_period_ineligible = int(
        summary.get(
            "requirements_with_period_ineligible_funding",
            0,
        )
        or 0
    )

    requirements_with_period_unknown = int(
        summary.get(
            "requirements_with_period_unknown_funding",
            0,
        )
        or 0
    )

    requirements_with_dimension_incompatible = int(
        summary.get(
            "requirements_with_dimension_incompatible_funding",
            0,
        )
        or 0
    )

    if remaining_requirement > 0:
        if funding_gap_amount > 0:
            message = (
                f"The organization has a remaining funding "
                f"requirement of ${remaining_requirement:,.2f}. "
                f"${applied_secured_funding:,.2f} of eligible "
                f"secured funding has been applied, leaving a "
                f"Funding Gap of ${funding_gap_amount:,.2f}."
            )

            if coverage_percentage is not None:
                message += (
                    f" Eligible secured funding currently covers "
                    f"{float(coverage_percentage):.2f}% of the "
                    f"remaining requirement."
                )

            insights.append(message)

        else:
            insights.append(
                (
                    f"The remaining funding requirement of "
                    f"${remaining_requirement:,.2f} is fully "
                    "covered by eligible secured funding under "
                    "the current Funding Gap rules."
                )
            )

    if period_ineligible_exposure > 0:
        insights.append(
            (
                f"${period_ineligible_exposure:,.2f} of "
                "requirement-level secured funding exposure "
                "could not be applied because the related grant "
                "period does not overlap the applicable fiscal "
                f"year. This affects "
                f"{requirements_with_period_ineligible} "
                "requirement(s)."
            )
        )

    if period_unknown_exposure > 0:
        insights.append(
            (
                f"${period_unknown_exposure:,.2f} of "
                "requirement-level secured funding exposure "
                "could not be confirmed as eligible because "
                "valid grant-period evidence is missing or "
                f"incomplete. This affects "
                f"{requirements_with_period_unknown} "
                "requirement(s) and requires data review."
            )
        )

    if dimension_incompatible_exposure > 0:
        insights.append(
            (
                f"${dimension_incompatible_exposure:,.2f} of "
                "requirement-level secured funding exposure "
                "could not be applied because known funding and "
                "requirement dimensions conflict. This affects "
                f"{requirements_with_dimension_incompatible} "
                "requirement(s)."
            )
        )

    if (
        period_ineligible_exposure > 0
        or period_unknown_exposure > 0
        or dimension_incompatible_exposure > 0
    ):
        insights.append(
            (
                "Funding exposure diagnostics are evaluated at "
                "requirement level and must not be added together "
                "or interpreted as unique organization-wide "
                "secured funding, because the same funding source "
                "may be assessed against more than one requirement."
            )
        )

    return insights