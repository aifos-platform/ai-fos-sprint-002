from typing import Any


def generate_grant_diagnostics(
    grants: dict[str, Any],
) -> dict[str, list[str]]:
    """
    Analyze grant coverage between
    budget and actual activity.
    """

    matched = []
    budget_only = []
    actual_only = []

    for grant in grants.values():

        has_budget = grant.original_budget > 0
        has_actual = abs(grant.actual) > 0

        if has_budget and has_actual:
            matched.append(grant.code)

        elif has_budget:
            budget_only.append(grant.code)

        elif has_actual:
            actual_only.append(grant.code)

    return {
        "matched_grants": sorted(matched),
        "budget_only_grants": sorted(budget_only),
        "actual_only_grants": sorted(actual_only),
    }