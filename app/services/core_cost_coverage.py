from typing import Any


def generate_core_cost_coverage(
    needed_core_costs: list[dict[str, Any]] | None,
    direct_grant_coverage: list[dict[str, Any]] | None,
    indirect_recovery_allocations: list[dict[str, Any]] | None,
    unrestricted_core_funding: list[dict[str, Any]] | None,
    available_indirect_recovery: list[dict[str, Any]] | None = None,
    used_indirect_recovery: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """
    Generate Core Cost Coverage & Allocation Intelligence.

    This engine is separate from the general Funding Gap engine.

    Indirect recovery is counted as coverage only when management
    has explicitly allocated it. The engine does not automatically
    allocate available indirect recovery.
    """

    needed_core_costs = needed_core_costs or []
    direct_grant_coverage = direct_grant_coverage or []
    indirect_recovery_allocations = (
        indirect_recovery_allocations or []
    )
    unrestricted_core_funding = unrestricted_core_funding or []

    available_indirect_recovery = (
        available_indirect_recovery or []
    )

    used_indirect_recovery = used_indirect_recovery or []

    lines = []

    for needed_line in needed_core_costs:
        budget_line_code = needed_line.get(
            "budget_line_code"
        )

        needed_amount = _to_float(
            needed_line.get("needed_budget")
        )

        direct_coverage = _sum_matching_coverage(
            direct_grant_coverage,
            budget_line_code,
        )

        direct_coverage_sources = [
            {
                **coverage_line,
                "amount": _to_float(
                    coverage_line.get("amount")
                ),
            }
            for coverage_line in direct_grant_coverage
            if coverage_line.get("budget_line_code")
            == budget_line_code
        ]        

        allocated_indirect_recovery = (
            _sum_matching_coverage(
                indirect_recovery_allocations,
                budget_line_code,
            )
        )

        indirect_recovery_allocation_sources = [
            {
                **allocation_line,
                "amount": _to_float(
                    allocation_line.get("amount")
                ),
            }
            for allocation_line in indirect_recovery_allocations
            if allocation_line.get("budget_line_code")
            == budget_line_code
        ]        

        unrestricted_funding = _sum_matching_coverage(
            unrestricted_core_funding,
            budget_line_code,
        )

        unrestricted_core_funding_sources = [
            {
                **funding_line,
                "amount": _to_float(
                    funding_line.get("amount")
                ),
            }
            for funding_line in unrestricted_core_funding
            if funding_line.get("budget_line_code")
            == budget_line_code
        ]        

        remaining_gap = max(
            needed_amount
            - direct_coverage
            - allocated_indirect_recovery
            - unrestricted_funding,
            0.0,
        )

        lines.append(
            {
                "program_code": needed_line.get(
                    "program_code"
                ),
                "category_code": needed_line.get(
                    "category_code"
                ),
                "budget_line_code": budget_line_code,
                "budget_line_name": needed_line.get(
                    "budget_line_name"
                ),
                "employee_responsible": needed_line.get(
                    "employee_responsible"
                ),
                "fiscal_year": needed_line.get(
                    "fiscal_year"
                ),
                "needed_core_cost": needed_amount,
                "direct_grant_coverage": direct_coverage,
                "direct_grant_coverage_sources": (
                    direct_coverage_sources
                ),                
                "allocated_indirect_recovery": (
                    allocated_indirect_recovery
                ),
                "indirect_recovery_allocation_sources": (
                    indirect_recovery_allocation_sources
                ),                
                "unrestricted_core_funding": (
                    unrestricted_funding
                ),
                "unrestricted_core_funding_sources": (
                    unrestricted_core_funding_sources
                ),                

                "remaining_core_cost_gap": remaining_gap,
            }
        )

    total_core_cost_coverage_over_need_amount = sum(
        max(
            _to_float(line.get("direct_grant_coverage"))
            + _to_float(
                line.get("allocated_indirect_recovery")
            )
            + _to_float(
                line.get("unrestricted_core_funding")
            )
            - _to_float(line.get("needed_core_cost")),
            0.0,
        )
        for line in lines
    )        

    needed_core_cost = sum(
        line["needed_core_cost"]
        for line in lines
    )

    direct_coverage = sum(
        line["direct_grant_coverage"]
        for line in lines
    )

    allocated_indirect_recovery = sum(
        line["allocated_indirect_recovery"]
        for line in lines
    )

    unrestricted_funding = sum(
        line["unrestricted_core_funding"]
        for line in lines
    )
    total_core_cost_coverage = (
        direct_coverage
        + allocated_indirect_recovery
        + unrestricted_funding
    )

    if needed_core_cost > 0.0:
        core_cost_coverage_percentage = min(
            total_core_cost_coverage
            / needed_core_cost
            * 100.0,
            100.0,
        )
    else:
        core_cost_coverage_percentage = 0.0

    remaining_gap = sum(
        line["remaining_core_cost_gap"]
        for line in lines
    )

    available_indirect_recovery_total = sum(
        _to_float(line.get("amount"))
        for line in available_indirect_recovery
    ) 

    used_indirect_recovery_total = sum(
        _to_float(line.get("amount"))
        for line in used_indirect_recovery
    )

    used_over_allocation_amount = max(
        used_indirect_recovery_total
        - allocated_indirect_recovery,
        0.0,
    )

    allocation_over_available_amount = max(
        allocated_indirect_recovery
        - available_indirect_recovery_total,
        0.0,
    )               

    return {
        "status": "available",
        "summary": {
            "needed_core_cost": needed_core_cost,
            "direct_grant_coverage": direct_coverage,

            "available_indirect_recovery": (
                available_indirect_recovery_total
            ),

            "allocated_indirect_recovery": (
                allocated_indirect_recovery
            ),
            "used_indirect_recovery": (
                used_indirect_recovery_total
            ),                       
            "unrestricted_core_funding": (
                unrestricted_funding
            ),
            "remaining_core_cost_gap": remaining_gap,

            "core_cost_coverage_percentage": (
                core_cost_coverage_percentage
            ),

        },
        "lines": lines,
        "controls": {
            "used_indirect_recovery_exceeds_allocation": (
                used_over_allocation_amount > 0.0
            ),
            "used_indirect_recovery_over_allocation_amount": (
                used_over_allocation_amount
            ),

            "allocated_indirect_recovery_exceeds_available": (
                allocation_over_available_amount > 0.0
            ),
            "allocated_indirect_recovery_over_available_amount": (
                allocation_over_available_amount
            ),
            "total_core_cost_coverage_exceeds_need": (
                total_core_cost_coverage_over_need_amount
                > 0.0
            ),
            "total_core_cost_coverage_over_need_amount": (
                total_core_cost_coverage_over_need_amount
            ),            

        },
    }


def _sum_matching_coverage(
    coverage_lines: list[dict[str, Any]],
    budget_line_code: Any,
) -> float:
    return sum(
        _to_float(line.get("amount"))
        for line in coverage_lines
        if line.get("budget_line_code") == budget_line_code
    )


def _to_float(value: Any) -> float:
    if value is None:
        return 0.0

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0