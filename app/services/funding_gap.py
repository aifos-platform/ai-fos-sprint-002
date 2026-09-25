from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Any


MATCH_DIMENSIONS = (
    "budget_line_code",
    "program_code",
    "category_code",
    "project_code",
)

def _get_funding_period_status(
    ledger_entry: dict[str, Any],
    fiscal_year: Any,
    grant_periods: dict[
        str,
        dict[str, str | None],
    ],
) -> str:
    """
    Return the grant-period status for one funding source.

    Possible values:
    - eligible
    - ineligible
    - unknown
    """

    fund_code = _clean(
        ledger_entry.get(
            "fund_code"
        )
    )

    if not fund_code:
        return "unknown"

    grant_period = (
        grant_periods.get(
            fund_code
        )
        or {}
    )

    grant_start_date = _parse_iso_date(
        grant_period.get(
            "start_date"
        )
    )

    grant_end_date = _parse_iso_date(
        grant_period.get(
            "end_date"
        )
    )

    if (
        grant_start_date is None
        or grant_end_date is None
    ):
        return "unknown"

    try:
        year = int(
            fiscal_year
        )
    except (
        TypeError,
        ValueError,
    ):
        return "unknown"

    requirement_start = date(
        year,
        1,
        1,
    )

    requirement_end = date(
        year,
        12,
        31,
    )

    if (
        grant_start_date <= requirement_end
        and grant_end_date >= requirement_start
    ):
        return "eligible"

    return "ineligible"

def generate_funding_gap(
    needed_budget_vs_actual: dict[str, Any] | None,
    available_budget_lines: list[dict[str, Any]] | None,
    budget_vs_actual: dict[str, Any] | None = None,
    grant_periods: dict[
        str,
        dict[str, str | None],
    ] | None = None,
) -> dict[str, Any]:
    """
    Build the AI-FOS Funding Gap analysis.

    Core concepts
    -------------

    Gross Remaining Secured Funding:
        All remaining secured funding in the available
        budget dataset.

    Explicitly Mapped Secured Funding:
        Secured funding with an explicit internal
        Budget Line allocation.

    Eligible Secured Funding:
        Funding available to one requirement after
        Budget Line matching, dimensional compatibility,
        and grant-period eligibility checks.

    Applied Secured Funding:
        The portion of eligible secured funding actually
        consumed to cover identified remaining needs.

    Excess Eligible Funding:
        Explicitly mapped secured funding that remains
        unused after requirements have been processed.

    Funding Gap:
        Remaining requirement that cannot be covered
        by eligible secured funding.

    Critical accounting controls
    ----------------------------

    Each secured funding dollar can be applied only once.

    A funding balance ledger is maintained during the
    allocation process. Once part of a secured budget
    record is applied to one requirement, only the
    remaining balance is available to subsequent
    requirements.

    The overall Fund / Grant remaining balance also acts
    as a hard ceiling across all detailed allocations
    belonging to that Fund.

    Automatic funding eligibility currently requires:

    - explicit internal Budget Line allocation
    - no conflict between known Program, Category,
      Project, and Donor Line dimensions
    - grant-period eligibility for the Needed Budget
      fiscal year

    Missing dimensions do not automatically create a
    conflict.

    Spending Plan is intentionally excluded from Funding
    Gap because it represents management allocation and
    timing, not whether funding has been secured.

    Broader donor contractual restrictions, ceilings,
    cost-sharing rules, and special conditions are not
    yet applied.
    """

    needed_budget_vs_actual = (
        needed_budget_vs_actual or {}
    )

    available_budget_lines = (
        available_budget_lines or []
    )

    budget_vs_actual = (
        budget_vs_actual or {}
    )

    grant_periods = (
        grant_periods or {}
    )

    needed_lines = _get_needed_lines(
        needed_budget_vs_actual
    )

    #
    # Build the authoritative remaining secured
    # balance by Fund / Grant.
    #
    fund_balances = (
        _get_remaining_secured_funding_by_fund(
            budget_vs_actual
        )
    )

    #
    # Build the mutable funding ledger.
    #
    funding_ledger = _build_funding_ledger(
        available_budget_lines=(
            available_budget_lines
        ),
        fund_balances=(
            fund_balances
        ),
    )

    #
    # Create a simple Budget Line index.
    #
    available_by_budget_line = (
        _group_funding_ledger_by_budget_line(
            funding_ledger
        )
    )

    analysis_lines: list[
        dict[str, Any]
    ] = []

    #
    # Organization-level totals.
    #
    total_needed_budget = 0.0
    total_actual_against_need = 0.0
    total_remaining_requirement = 0.0

    total_applied_secured_funding = 0.0
    total_funding_gap = 0.0

    total_dimension_incompatible_funding_exposure = 0.0
    total_period_ineligible_funding_exposure = 0.0
    total_period_unknown_funding_exposure = 0.0

    requirements_with_dimension_incompatible_funding = 0
    requirements_with_period_ineligible_funding = 0
    requirements_with_period_unknown_funding = 0    

    matched_requirement_count = 0
    unmatched_requirement_count = 0

    fully_funded_requirement_count = 0
    partially_funded_requirement_count = 0
    unfunded_requirement_count = 0
    no_remaining_requirement_count = 0

    for needed_line in needed_lines:

        needed_budget = _to_float(
            needed_line.get(
                "needed_budget"
            )
        )

        actual = _to_float(
            needed_line.get(
                "actual"
            )
        )

        remaining_requirement = (
            _get_remaining_requirement(
                needed_line
            )
        )

        #
        # Needed Budget totals represent identified
        # organizational requirements.
        #
        if needed_budget > 0:

            total_needed_budget += (
                needed_budget
            )

            total_actual_against_need += min(
                max(
                    actual,
                    0.0,
                ),
                needed_budget,
            )

        total_remaining_requirement += (
            remaining_requirement
        )

        match_dimension = (
            _resolve_primary_match_dimension(
                needed_line
            )
        )

        match_value = (
            _get_match_value(
                needed_line=needed_line,
                match_dimension=match_dimension,
            )
        )

        #
        # Per-requirement funding pools.
        #
        candidate_ledger_entries: list[
            dict[str, Any]
        ] = []

        dimensionally_compatible_entries: list[
            dict[str, Any]
        ] = []

        dimension_incompatible_entries: list[
            dict[str, Any]
        ] = []

        matched_ledger_entries: list[
            dict[str, Any]
        ] = []

        period_ineligible_entries: list[
            dict[str, Any]
        ] = []

        period_unknown_entries: list[
            dict[str, Any]
        ] = []

        dimension_incompatible_funding = 0.0
        period_ineligible_funding = 0.0
        period_unknown_funding = 0.0

        #
        # Current safe matching rule:
        #
        # Only explicit internal Budget Line allocation
        # is sufficient evidence to begin automatic
        # funding eligibility analysis.
        #
        # We deliberately do NOT fall back to Program,
        # Category, or Project.
        #
        if (
            match_dimension
            == "budget_line_code"
            and match_value
        ):

            #
            # Stage 1:
            # Explicit Budget Line match.
            #
            candidate_ledger_entries = (
                available_by_budget_line.get(
                    match_value,
                    [],
                )
            )

            #
            # Stage 2:
            # Known dimensions must not conflict.
            #
            dimensionally_compatible_entries = [
                entry
                for entry in candidate_ledger_entries
                if _is_dimensionally_compatible(
                    ledger_entry=entry,
                    needed_line=needed_line,
                )
            ]

            dimension_incompatible_entries = [
                entry
                for entry in candidate_ledger_entries
                if entry
                not in dimensionally_compatible_entries
            ]

            dimension_incompatible_funding = sum(
                _ledger_available_balance(
                    entry
                )
                for entry
                in dimension_incompatible_entries
            )

        #
        # Stage 3:
        # Classify grant-period evidence.
        #
        # Eligible:
        #     Grant period is known and overlaps the
        #     Needed Budget fiscal year.
        #
        # Ineligible:
        #     Grant period is known but falls outside
        #     the Needed Budget fiscal year.
        #
        # Unknown:
        #     Grant-period eligibility cannot be
        #     confirmed from available data.
        #
        for entry in dimensionally_compatible_entries:

            period_status = (
                _get_funding_period_status(
                    ledger_entry=entry,
                    fiscal_year=(
                        needed_line.get(
                            "fiscal_year"
                        )
                    ),
                    grant_periods=(
                        grant_periods
                    ),
                )
            )

            if period_status == "eligible":

                matched_ledger_entries.append(
                    entry
                )

            elif period_status == "ineligible":

                period_ineligible_entries.append(
                    entry
                )

            else:

                period_unknown_entries.append(
                    entry
                )


        period_ineligible_funding = sum(
            _ledger_available_balance(
                entry
            )
            for entry in period_ineligible_entries
        )


        period_unknown_funding = sum(
            _ledger_available_balance(
                entry
            )
            for entry in period_unknown_entries
        )

        #
        # Available eligible funding immediately BEFORE
        # funding this requirement.
        #
        eligible_secured_funding = sum(
            _ledger_available_balance(
                entry
            )
            for entry in matched_ledger_entries
        )

        #
        # Apply secured funding.
        #
        # The operation reduces both:
        #
        # - detailed allocation balance
        # - shared Fund / Grant balance
        #
        allocation_result = (
            _apply_secured_funding(
                ledger_entries=(
                    matched_ledger_entries
                ),
                amount_required=(
                    remaining_requirement
                ),
            )
        )

        applied_secured_funding = (
            allocation_result[
                "applied_amount"
            ]
        )

        applied_sources = (
            allocation_result[
                "sources"
            ]
        )

        funding_gap = max(
            remaining_requirement
            - applied_secured_funding,
            0.0,
        )

        #
        # Remaining eligible funding after this
        # requirement has been financed.
        #
        remaining_eligible_after_application = sum(
            _ledger_available_balance(
                entry
            )
            for entry in matched_ledger_entries
        )

        coverage_percentage = (
            applied_secured_funding
            / remaining_requirement
            * 100
            if remaining_requirement > 0
            else None
        )

        #
        # Requirement status.
        #
        if remaining_requirement <= 0:

            funding_status = (
                "No Remaining Requirement"
            )

            no_remaining_requirement_count += 1

        elif not matched_ledger_entries:

            funding_status = (
                "No Eligible Secured Funding"
            )

            unmatched_requirement_count += 1
            unfunded_requirement_count += 1

        elif eligible_secured_funding <= 0:

            funding_status = (
                "Eligible Funding Fully Consumed"
            )

            matched_requirement_count += 1
            unfunded_requirement_count += 1

        elif funding_gap > 0:

            funding_status = (
                "Partially Funded"
            )

            matched_requirement_count += 1
            partially_funded_requirement_count += 1

        else:

            funding_status = (
                "Fully Funded"
            )

            matched_requirement_count += 1
            fully_funded_requirement_count += 1

        #
        # Aggregate totals.
        #
        if remaining_requirement > 0:

            total_applied_secured_funding += (
                applied_secured_funding
            )

            total_funding_gap += (
                funding_gap
            )

            total_dimension_incompatible_funding_exposure += (
                dimension_incompatible_funding
            )

            total_period_ineligible_funding_exposure += (
                period_ineligible_funding
            )

            total_period_unknown_funding_exposure += (
                period_unknown_funding
            )

            if dimension_incompatible_funding > 0:
                requirements_with_dimension_incompatible_funding += 1

            if period_ineligible_funding > 0:
                requirements_with_period_ineligible_funding += 1

            if period_unknown_funding > 0:
                requirements_with_period_unknown_funding += 1

        #
        # Detailed requirement result.
        #
        analysis_lines.append(
            {
                "code": (
                    needed_line.get(
                        "code"
                    )
                    or needed_line.get(
                        "budget_line_code"
                    )
                ),

                "fiscal_year": (
                    needed_line.get(
                        "fiscal_year"
                    )
                ),

                "budget_line_code": (
                    needed_line.get(
                        "budget_line_code"
                    )
                ),

                "budget_line_name": (
                    needed_line.get(
                        "budget_line_name"
                    )
                ),

                "program_code": (
                    needed_line.get(
                        "program_code"
                    )
                ),

                "program_name": (
                    needed_line.get(
                        "program_name"
                    )
                ),

                "category_code": (
                    needed_line.get(
                        "category_code"
                    )
                ),

                "category_name": (
                    needed_line.get(
                        "category_name"
                    )
                ),

                "project_code": (
                    needed_line.get(
                        "project_code"
                    )
                ),

                "project_name": (
                    needed_line.get(
                        "project_name"
                    )
                ),

                "needed_budget": round(
                    needed_budget,
                    2,
                ),

                "actual_spending": round(
                    actual,
                    2,
                ),

                "remaining_requirement": round(
                    remaining_requirement,
                    2,
                ),

                #
                # Funding available immediately before
                # allocation to this requirement.
                #
                "eligible_secured_funding": round(
                    eligible_secured_funding,
                    2,
                ),

                #
                # Funding actually consumed.
                #
                "applied_secured_funding": round(
                    applied_secured_funding,
                    2,
                ),

                #
                # Funding remaining in the eligible pool.
                #
                "remaining_eligible_funding": round(
                    remaining_eligible_after_application,
                    2,
                ),

                "funding_gap": round(
                    funding_gap,
                    2,
                ),

                "coverage_percentage": (
                    round(
                        coverage_percentage,
                        2,
                    )
                    if coverage_percentage
                    is not None
                    else None
                ),

                "status": (
                    funding_status
                ),

                "match_dimension": (
                    match_dimension
                ),

                "match_value": (
                    match_value
                ),

                #
                # Structural Budget Line candidates.
                #
                "candidate_funding_record_count": (
                    len(
                        candidate_ledger_entries
                    )
                ),

                #
                # Final eligible records after all
                # currently supported restrictions.
                #
                "matched_funding_record_count": (
                    len(
                        matched_ledger_entries
                    )
                ),

                #
                # Dimension conflict diagnostics.
                #
                "dimension_incompatible_funding_record_count": (
                    len(
                        dimension_incompatible_entries
                    )
                ),

                "dimension_incompatible_funding": round(
                    dimension_incompatible_funding,
                    2,
                ),

                "dimension_incompatible_funding_sources": [
                    {
                        "ledger_id": (
                            entry.get(
                                "ledger_id"
                            )
                        ),

                        "fund_code": (
                            entry.get(
                                "fund_code"
                            )
                        ),

                        "fund_name": (
                            (
                                entry.get(
                                    "source",
                                    {},
                                )
                                or {}
                            ).get(
                                "fund_name"
                            )
                        ),

                        "program_code": (
                            (
                                entry.get(
                                    "source",
                                    {},
                                )
                                or {}
                            ).get(
                                "program_code"
                            )
                        ),

                        "category_code": (
                            (
                                entry.get(
                                    "source",
                                    {},
                                )
                                or {}
                            ).get(
                                "category_code"
                            )
                        ),

                        "project_code": (
                            (
                                entry.get(
                                    "source",
                                    {},
                                )
                                or {}
                            ).get(
                                "project_code"
                            )
                        ),

                        "donor_line_code": (
                            (
                                entry.get(
                                    "source",
                                    {},
                                )
                                or {}
                            ).get(
                                "donor_line_code"
                            )
                        ),

                        "opening_balance": round(
                            _to_float(
                                entry.get(
                                    "opening_balance"
                                )
                            ),
                            2,
                        ),

                        "remaining_balance": round(
                            _to_float(
                                entry.get(
                                    "remaining_balance"
                                )
                            ),
                            2,
                        ),
                    }
                    for entry
                    in dimension_incompatible_entries
                ],

                #
                # Grant-period diagnostics.
                #
                "period_ineligible_funding_record_count": (
                    len(
                        period_ineligible_entries
                    )
                ),

                "period_ineligible_funding": round(
                    period_ineligible_funding,
                    2,
                ),

                "period_ineligible_funding_sources": [
                    {
                        "ledger_id": (
                            entry.get(
                                "ledger_id"
                            )
                        ),

                        "fund_code": (
                            entry.get(
                                "fund_code"
                            )
                        ),

                        "fund_name": (
                            (
                                entry.get(
                                    "source",
                                    {},
                                )
                                or {}
                            ).get(
                                "fund_name"
                            )
                        ),

                        "opening_balance": round(
                            _to_float(
                                entry.get(
                                    "opening_balance"
                                )
                            ),
                            2,
                        ),

                        "remaining_balance": round(
                            _to_float(
                                entry.get(
                                    "remaining_balance"
                                )
                            ),
                            2,
                        ),
                    }
                    for entry
                    in period_ineligible_entries
                ],

        #
        # Unknown grant-period diagnostics.
        #
        "period_unknown_funding_record_count": (
            len(
                period_unknown_entries
            )
        ),

        "period_unknown_funding": round(
            period_unknown_funding,
            2,
        ),

        "period_unknown_funding_sources": [
            {
                "ledger_id": (
                    entry.get(
                        "ledger_id"
                    )
                ),

                "fund_code": (
                    entry.get(
                        "fund_code"
                    )
                ),

                "fund_name": (
                    (
                        entry.get(
                            "source",
                            {},
                        )
                        or {}
                    ).get(
                        "fund_name"
                    )
                ),

                "opening_balance": round(
                    _to_float(
                        entry.get(
                            "opening_balance"
                        )
                    ),
                    2,
                ),

                "remaining_balance": round(
                    _to_float(
                        entry.get(
                            "remaining_balance"
                        )
                    ),
                    2,
                ),

                "reason": (
                    "Grant period could not be "
                    "validated because start date, "
                    "end date, fiscal year, or grant "
                    "identity is missing or invalid."
                ),
            }
            for entry in period_unknown_entries
        ],                

                #
                # Only funding sources actually consumed
                # for this requirement are listed here.
                #
                "funding_sources": (
                    applied_sources
                ),
            }
        )

    #
    # Gross secured funding is independent of whether
    # the funding is explicitly mapped to a requirement.
    #
    gross_remaining_secured_funding = (
        _get_gross_remaining_secured_funding(
            budget_vs_actual=budget_vs_actual,
            available_budget_lines=(
                available_budget_lines
            ),
        )
    )

    #
    # Opening secured funding carrying an explicit
    # internal Budget Line allocation.
    #
    # This represents structural mapping only.
    #
    explicitly_mapped_secured_funding = sum(
        entry[
            "opening_balance"
        ]
        for entry in funding_ledger
        if entry.get(
            "budget_line_code"
        )
    )

    #
    # Explicitly mapped funding still unused after
    # allocations.
    #
    excess_eligible_funding = sum(
        _ledger_available_balance(
            entry
        )
        for entry in funding_ledger
        if entry.get(
            "budget_line_code"
        )
    )

    #
    # Secured funding without an explicit internal
    # Budget Line allocation.
    #
    # This amount is not assumed to be unrestricted.
    #
    secured_funding_without_budget_line_allocation = sum(
        _ledger_available_balance(
            entry
        )
        for entry in funding_ledger
        if not entry.get(
            "budget_line_code"
        )
    )

    applied_coverage_percentage = (
        total_applied_secured_funding
        / total_remaining_requirement
        * 100
        if total_remaining_requirement > 0
        else None
    )

    #
    # Overall status.
    #
    if total_remaining_requirement <= 0:

        overall_status = (
            "No Remaining Requirement"
        )

    elif total_funding_gap > 0:

        overall_status = (
            "Funding Gap"
        )

    elif unmatched_requirement_count > 0:

        overall_status = (
            "Coverage Requires Review"
        )

    else:

        overall_status = (
            "Remaining Requirements Fully Funded"
        )

    return {
        "summary": {

            "total_needed_budget": round(
                total_needed_budget,
                2,
            ),

            "actual_spending_against_need": round(
                total_actual_against_need,
                2,
            ),

            "remaining_requirement": round(
                total_remaining_requirement,
                2,
            ),

            "gross_remaining_secured_funding": round(
                gross_remaining_secured_funding,
                2,
            ),

            "explicitly_mapped_secured_funding": round(
                explicitly_mapped_secured_funding,
                2,
            ),

            "applied_secured_funding": round(
                total_applied_secured_funding,
                2,
            ),

            "excess_eligible_funding": round(
                excess_eligible_funding,
                2,
            ),

            "secured_funding_without_budget_line_allocation": round(
                secured_funding_without_budget_line_allocation,
                2,
            ),

            "funding_gap": round(
                total_funding_gap,
                2,
            ),

            "dimension_incompatible_funding_exposure": round(
                total_dimension_incompatible_funding_exposure,
                2,
            ),

            "period_ineligible_funding_exposure": round(
                total_period_ineligible_funding_exposure,
                2,
            ),

            "period_unknown_funding_exposure": round(
                total_period_unknown_funding_exposure,
                2,
            ),

            "requirements_with_dimension_incompatible_funding": (
                requirements_with_dimension_incompatible_funding
            ),

            "requirements_with_period_ineligible_funding": (
                requirements_with_period_ineligible_funding
            ),

            "requirements_with_period_unknown_funding": (
                requirements_with_period_unknown_funding
            ),            

            "applied_coverage_percentage": (
                round(
                    applied_coverage_percentage,
                    2,
                )
                if applied_coverage_percentage
                is not None
                else None
            ),

            "matched_requirement_count": (
                matched_requirement_count
            ),

            "unmatched_requirement_count": (
                unmatched_requirement_count
            ),

            "fully_funded_requirement_count": (
                fully_funded_requirement_count
            ),

            "partially_funded_requirement_count": (
                partially_funded_requirement_count
            ),

            "unfunded_requirement_count": (
                unfunded_requirement_count
            ),

            "no_remaining_requirement_count": (
                no_remaining_requirement_count
            ),

            "status": (
                overall_status
            ),
        },

        "diagnostic_exposure_note": (
            "Funding exposure amounts are requirement-level "
            "diagnostics. They identify secured funding that "
            "could not support particular requirements because "
            "of dimensional conflicts, grant-period exclusion, "
            "or missing grant-period evidence. Exposure amounts "
            "must not be added together or interpreted as unique "
            "organization-wide secured funding because the same "
            "funding record may be evaluated against more than "
            "one requirement."
        ),

        "lines": (
            analysis_lines
        ),

        "scope": (
            "matched_requirement_level"
        ),

        "matching_method": (
            "explicit_budget_line_allocation"
        ),

        "dimension_compatibility_rule": (
            "known_values_must_not_conflict"
        ),

        "grant_period_rule": (
            "fiscal_year_overlap_required"
        ),

        "allocation_control": (
            "one_secured_dollar_one_use"
        ),

        "restriction_analysis": (
            "partial"
        ),

        "restriction_note": (
            "Secured funding is currently treated as "
            "eligible only when an explicit internal "
            "Budget Line allocation exists, known "
            "requirement and funding dimensions do not "
            "conflict, and the grant period is eligible "
            "for the requirement. Funding balances are "
            "reduced when applied so the same secured "
            "dollar cannot finance more than one "
            "requirement. Missing dimensions do not "
            "create an automatic conflict. Broader donor "
            "contractual, ceiling, cost-sharing, and "
            "special-condition eligibility rules are "
            "not yet applied."
        ),

        "spending_plan_treatment": (
            "excluded_from_funding_gap"
        ),
    }


def _get_needed_lines(
    needed_budget_vs_actual: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Return the most detailed reliable requirement
    records currently available.

    The detailed requirement view is preferred because
    it preserves the full dimensional identity of each
    organizational need.

    Aggregated Budget Line records remain as a fallback
    for backward compatibility.
    """

    detailed = (
        needed_budget_vs_actual.get(
            "detailed",
            {},
        )
        or {}
    )

    detailed_lines = (
        detailed.get(
            "lines",
            [],
        )
        or []
    )

    if detailed_lines:
        return detailed_lines

    by_budget_line = (
        needed_budget_vs_actual.get(
            "by_budget_line",
            {},
        )
        or {}
    )

    budget_line_lines = (
        by_budget_line.get(
            "lines",
            [],
        )
        or []
    )

    if budget_line_lines:
        return budget_line_lines

    return (
        needed_budget_vs_actual.get(
            "lines",
            [],
        )
        or []
    )


def _build_funding_ledger(
    available_budget_lines: list[
        dict[str, Any]
    ],
    fund_balances: dict[
        str,
        float,
    ] | None = None,
) -> list[dict[str, Any]]:
    """
    Build the funding balance ledger.

    The authoritative remaining secured balance is held
    at Fund / Grant level.

    Imported remaining_secured_budget values are used
    only as the allocation basis for distributing that
    authoritative Fund balance across detailed Available
    Budget records.

    Controls:

    1. Detailed allocations cannot collectively exceed
       the Fund's true remaining secured balance.

    2. Mapped and unmapped allocations share the same
       Fund ceiling.

    3. If the authoritative Fund balance exceeds the
       explicitly allocated imported balances, the
       difference remains visible as an unallocated
       Fund-level reserve.
    """

    fund_balances = (
        fund_balances or {}
    )

    imported_total_by_fund: dict[
        str,
        float,
    ] = {}

    first_source_by_fund: dict[
        str,
        dict[str, Any],
    ] = {}

    for line in available_budget_lines:

        fund_code = _clean(
            line.get(
                "fund_code"
            )
            or line.get(
                "fund"
            )
        )

        if not fund_code:
            continue

        imported_amount = (
            _remaining_secured_amount(
                line
            )
        )

        imported_total_by_fund[
            fund_code
        ] = (
            imported_total_by_fund.get(
                fund_code,
                0.0,
            )
            + imported_amount
        )

        if (
            fund_code
            not in first_source_by_fund
        ):

            first_source_by_fund[
                fund_code
            ] = line

    ledger: list[
        dict[str, Any]
    ] = []

    ledger_id = 0

    #
    # Detailed allocation records.
    #
    for line in available_budget_lines:

        fund_code = _clean(
            line.get(
                "fund_code"
            )
            or line.get(
                "fund"
            )
        )

        imported_opening_balance = (
            _remaining_secured_amount(
                line
            )
        )

        opening_balance = (
            imported_opening_balance
        )

        if (
            fund_code
            and fund_code
            in fund_balances
        ):

            authoritative_fund_balance = max(
                _to_float(
                    fund_balances.get(
                        fund_code
                    )
                ),
                0.0,
            )

            imported_fund_total = max(
                _to_float(
                    imported_total_by_fund.get(
                        fund_code
                    )
                ),
                0.0,
            )

            if imported_fund_total > 0:

                allocation_factor = min(
                    authoritative_fund_balance
                    / imported_fund_total,
                    1.0,
                )

                opening_balance = (
                    imported_opening_balance
                    * allocation_factor
                )

            else:

                opening_balance = 0.0

        ledger.append(
            {
                "ledger_id": (
                    ledger_id
                ),

                "source": (
                    line
                ),

                "fund_code": (
                    fund_code
                ),

                "budget_line_code": (
                    _clean(
                        line.get(
                            "budget_line_code"
                        )
                    )
                ),

                "opening_balance": (
                    opening_balance
                ),

                "remaining_balance": (
                    opening_balance
                ),

                "fund_balance_state": (
                    fund_balances
                ),

                "allocation_basis": (
                    "proportional_to_imported_"
                    "remaining_secured_budget"
                    if (
                        fund_code
                        and fund_code
                        in fund_balances
                    )
                    else (
                        "imported_remaining_"
                        "secured_budget"
                    )
                ),
            }
        )

        ledger_id += 1

    #
    # Preserve authoritative Fund balances not allocated
    # to detailed Budget Lines.
    #
    for (
        fund_code,
        authoritative_balance,
    ) in fund_balances.items():

        authoritative_balance = max(
            _to_float(
                authoritative_balance
            ),
            0.0,
        )

        imported_total = max(
            _to_float(
                imported_total_by_fund.get(
                    fund_code
                )
            ),
            0.0,
        )

        unallocated_reserve = max(
            authoritative_balance
            - imported_total,
            0.0,
        )

        if unallocated_reserve <= 0:
            continue

        reference_source = (
            first_source_by_fund.get(
                fund_code,
                {},
            )
            or {}
        )

        reserve_source = {
            "fund_code": (
                fund_code
            ),

            "fund_name": (
                reference_source.get(
                    "fund_name"
                )
            ),

            "donor_code": (
                reference_source.get(
                    "donor_code"
                )
            ),

            "donor_name": (
                reference_source.get(
                    "donor_name"
                )
            ),

            "donor_line_code": None,
            "budget_line_code": None,
            "program_code": None,
            "category_code": None,
            "project_code": None,

            "funding_source_type": (
                "unallocated_fund_reserve"
            ),
        }

        ledger.append(
            {
                "ledger_id": (
                    ledger_id
                ),

                "source": (
                    reserve_source
                ),

                "fund_code": (
                    fund_code
                ),

                "budget_line_code": None,

                "opening_balance": (
                    unallocated_reserve
                ),

                "remaining_balance": (
                    unallocated_reserve
                ),

                "fund_balance_state": (
                    fund_balances
                ),

                "allocation_basis": (
                    "unallocated_authoritative_"
                    "fund_balance"
                ),
            }
        )

        ledger_id += 1

    return ledger


def _parse_iso_date(
    value: Any,
) -> date | None:
    """
    Parse a canonical AI-FOS ISO date.

    Invalid or missing dates are treated as unknown
    rather than inferred.
    """

    if value is None:
        return None

    text = str(
        value
    ).strip()

    if not text:
        return None

    try:
        return date.fromisoformat(
            text
        )

    except ValueError:
        return None


period_ineligible_entries: list[
    dict[str, Any]
] = []

dimension_incompatible_funding = 0.0
period_ineligible_funding = 0.0


def _is_dimensionally_compatible(
    ledger_entry: dict[str, Any],
    needed_line: dict[str, Any],
) -> bool:
    """
    Determine whether a funding source is compatible
    with the requirement's known dimensions.

    A conflict exists only when:

    - the requirement has a value
    - the funding source has a value
    - the two values differ

    Missing dimensions therefore do not automatically
    disqualify funding.
    """

    source = (
        ledger_entry.get(
            "source"
        )
        or {}
    )

    for dimension in (
        "program_code",
        "category_code",
        "project_code",
        "donor_line_code",
    ):

        requirement_value = _clean(
            needed_line.get(
                dimension
            )
        )

        source_value = _clean(
            source.get(
                dimension
            )
        )

        if (
            requirement_value
            and source_value
            and requirement_value
            != source_value
        ):

            return False

    return True


def _group_funding_ledger_by_budget_line(
    funding_ledger: list[
        dict[str, Any]
    ],
) -> dict[
    str,
    list[dict[str, Any]],
]:
    """
    Group funding ledger entries by explicit internal
    Budget Line allocation.
    """

    grouped: dict[
        str,
        list[dict[str, Any]],
    ] = defaultdict(
        list
    )

    for entry in funding_ledger:

        budget_line_code = (
            entry.get(
                "budget_line_code"
            )
        )

        if not budget_line_code:
            continue

        grouped[
            budget_line_code
        ].append(
            entry
        )

    return dict(
        grouped
    )


def _apply_secured_funding(
    ledger_entries: list[
        dict[str, Any]
    ],
    amount_required: float,
) -> dict[str, Any]:
    """
    Apply secured funding to one requirement.

    Funding is controlled at two levels:

    1. Detailed secured allocation balance.
    2. Overall Fund / Grant remaining balance.

    Every amount applied reduces both balances.

    Therefore the same secured dollar cannot be reused,
    and all allocations belonging to one Fund cannot
    collectively exceed that Fund's authoritative
    remaining secured funding.
    """

    amount_remaining = max(
        amount_required,
        0.0,
    )

    applied_amount = 0.0

    sources: list[
        dict[str, Any]
    ] = []

    if amount_remaining <= 0:

        return {
            "applied_amount": 0.0,
            "sources": [],
        }

    for entry in ledger_entries:

        if amount_remaining <= 0:
            break

        allocation_available = (
            _ledger_available_balance(
                entry
            )
        )

        if allocation_available <= 0:
            continue

        source = (
            entry.get(
                "source",
                {},
            )
            or {}
        )

        fund_code = _clean(
            entry.get(
                "fund_code"
            )
            or source.get(
                "fund_code"
            )
            or source.get(
                "fund"
            )
        )

        fund_balance_state = (
            entry.get(
                "fund_balance_state",
                {},
            )
            or {}
        )

        #
        # Authoritative Fund-level hard ceiling.
        #
        if (
            fund_code
            and fund_code
            in fund_balance_state
        ):

            fund_available = max(
                _to_float(
                    fund_balance_state.get(
                        fund_code
                    )
                ),
                0.0,
            )

            available_balance = min(
                allocation_available,
                fund_available,
            )

        else:

            available_balance = (
                allocation_available
            )

        if available_balance <= 0:
            continue

        amount_from_source = min(
            amount_remaining,
            available_balance,
        )

        #
        # Reduce detailed allocation balance.
        #
        entry[
            "remaining_balance"
        ] = max(
            allocation_available
            - amount_from_source,
            0.0,
        )

        #
        # Reduce shared Fund balance.
        #
        if (
            fund_code
            and fund_code
            in fund_balance_state
        ):

            fund_balance_state[
                fund_code
            ] = max(
                _to_float(
                    fund_balance_state.get(
                        fund_code
                    )
                )
                - amount_from_source,
                0.0,
            )

        applied_amount += (
            amount_from_source
        )

        amount_remaining -= (
            amount_from_source
        )

        sources.append(
            {
                "ledger_id": (
                    entry.get(
                        "ledger_id"
                    )
                ),

                "fund_code": (
                    source.get(
                        "fund_code"
                    )
                ),

                "fund_name": (
                    source.get(
                        "fund_name"
                    )
                ),

                "donor_code": (
                    source.get(
                        "donor_code"
                    )
                ),

                "donor_name": (
                    source.get(
                        "donor_name"
                    )
                ),

                "donor_line_code": (
                    source.get(
                        "donor_line_code"
                    )
                ),

                "budget_line_code": (
                    source.get(
                        "budget_line_code"
                    )
                ),

                "program_code": (
                    source.get(
                        "program_code"
                    )
                ),

                "category_code": (
                    source.get(
                        "category_code"
                    )
                ),

                "project_code": (
                    source.get(
                        "project_code"
                    )
                ),

                "opening_secured_balance": round(
                    _to_float(
                        entry.get(
                            "opening_balance"
                        )
                    ),
                    2,
                ),

                "applied_to_requirement": round(
                    amount_from_source,
                    2,
                ),

                "remaining_after_application": round(
                    _to_float(
                        entry.get(
                            "remaining_balance"
                        )
                    ),
                    2,
                ),

                "fund_remaining_after_application": (
                    round(
                        _to_float(
                            fund_balance_state.get(
                                fund_code
                            )
                        ),
                        2,
                    )
                    if (
                        fund_code
                        and fund_code
                        in fund_balance_state
                    )
                    else None
                ),
            }
        )

    return {
        "applied_amount": (
            applied_amount
        ),

        "sources": (
            sources
        ),
    }


def _ledger_available_balance(
    ledger_entry: dict[str, Any],
) -> float:
    """
    Return the remaining usable balance of one ledger
    allocation.
    """

    return max(
        _to_float(
            ledger_entry.get(
                "remaining_balance"
            )
        ),
        0.0,
    )


def _resolve_primary_match_dimension(
    needed_line: dict[str, Any],
) -> str | None:
    """
    Select the strongest currently supported canonical
    matching dimension.

    Budget Line is preferred.

    Other dimensions remain visible for diagnostics and
    future organization-aware eligibility logic but are
    not used as automatic fallback matching dimensions.
    """

    budget_line_code = _clean(
        needed_line.get(
            "budget_line_code"
        )
        or needed_line.get(
            "code"
        )
    )

    if budget_line_code:

        return (
            "budget_line_code"
        )

    for dimension in MATCH_DIMENSIONS[1:]:

        value = _clean(
            needed_line.get(
                dimension
            )
        )

        if value:
            return dimension

    return None


def _get_match_value(
    needed_line: dict[str, Any],
    match_dimension: str | None,
) -> str | None:
    """
    Return the canonical value used for the selected
    matching dimension.
    """

    if not match_dimension:
        return None

    if (
        match_dimension
        == "budget_line_code"
    ):

        return _clean(
            needed_line.get(
                "budget_line_code"
            )
            or needed_line.get(
                "code"
            )
        )

    return _clean(
        needed_line.get(
            match_dimension
        )
    )


def _get_remaining_requirement(
    needed_line: dict[str, Any],
) -> float:
    """
    Return the remaining positive requirement for one
    identified need.

    Overspending on one requirement must not reduce the
    unmet requirement of another requirement.
    """

    needed_budget = _to_float(
        needed_line.get(
            "needed_budget"
        )
    )

    if needed_budget <= 0:
        return 0.0

    value = needed_line.get(
        "remaining_requirement"
    )

    if value is not None:

        return max(
            _to_float(
                value
            ),
            0.0,
        )

    actual = _to_float(
        needed_line.get(
            "actual"
        )
    )

    return max(
        needed_budget
        - actual,
        0.0,
    )


def _get_remaining_secured_funding_by_fund(
    budget_vs_actual: dict[str, Any],
) -> dict[str, float]:
    """
    Build the authoritative remaining secured funding
    balance for each Fund / Grant.

    Remaining secured funding per Fund:

        Current secured Fund budget
        - cumulative budget-consuming GL actuals
        = remaining secured funding

    This Fund-level balance acts as a hard ceiling.
    """

    by_fund = (
        budget_vs_actual.get(
            "by_fund",
            {},
        )
        or {}
    )

    fund_lines = (
        by_fund.get(
            "lines",
            [],
        )
        or []
    )

    balances: dict[
        str,
        float,
    ] = {}

    for fund_line in fund_lines:

        fund_code = _clean(
            fund_line.get(
                "fund_code"
            )
            or fund_line.get(
                "code"
            )
        )

        if not fund_code:
            continue

        budget = _to_float(
            fund_line.get(
                "budget"
            )
        )

        actual = _to_float(
            fund_line.get(
                "actual"
            )
        )

        remaining = max(
            budget
            - actual,
            0.0,
        )

        balances[
            fund_code
        ] = remaining

    return balances


def _get_gross_remaining_secured_funding(
    budget_vs_actual: dict[str, Any],
    available_budget_lines: list[
        dict[str, Any]
    ],
) -> float:
    """
    Calculate organization-level remaining secured
    funding.

    Preferred calculation:

        Secured Fund Budget
        - cumulative budget-consuming GL actuals
        = remaining secured funding

    Imported remaining secured balances are used only
    as a fallback when Fund-level Budget vs Actual data
    is unavailable.
    """

    fund_balances = (
        _get_remaining_secured_funding_by_fund(
            budget_vs_actual
        )
    )

    if fund_balances:

        return sum(
            fund_balances.values()
        )

    return sum(
        _remaining_secured_amount(
            line
        )
        for line in available_budget_lines
    )


def _remaining_secured_amount(
    funding_line: dict[str, Any],
) -> float:
    """
    Return the explicitly imported remaining secured
    budget.

    There is deliberately no fallback to Original,
    Revised, or Current Budget.
    """

    value = funding_line.get(
        "remaining_secured_budget"
    )

    if value is None:
        return 0.0

    return max(
        _to_float(
            value
        ),
        0.0,
    )


def _clean(
    value: Any,
) -> str | None:
    """
    Return a clean canonical string value.
    """

    if value is None:
        return None

    cleaned = str(
        value
    ).strip()

    if not cleaned:
        return None

    if cleaned.lower() in {
        "none",
        "null",
        "nan",
    }:

        return None

    return cleaned


def _to_float(
    value: Any,
) -> float:
    """
    Convert an imported financial value safely to float.
    """

    if value is None:
        return 0.0

    if isinstance(
        value,
        (int, float),
    ):

        return float(
            value
        )

    text = (
        str(value)
        .replace(
            ",",
            "",
        )
        .replace(
            "$",
            "",
        )
        .strip()
    )

    if not text:
        return 0.0

    if (
        text.startswith("(")
        and text.endswith(")")
    ):

        text = (
            "-"
            + text[1:-1]
        )

    try:

        return float(
            text
        )

    except (
        TypeError,
        ValueError,
    ):

        return 0.0