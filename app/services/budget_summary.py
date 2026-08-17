from typing import Any
from collections import defaultdict


def generate_budget_summary(
    budget_lines: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Generate executive-level budget statistics.

    Optional dimensions are summarized only when
    actual values exist in the imported Budget.
    """

    total_original_budget = 0.0
    total_revised_budget = 0.0

    funds = defaultdict(float)
    donors = defaultdict(float)
    programs = defaultdict(float)
    projects = defaultdict(float)

    for line in budget_lines:
        original = float(
            line.get("original_budget") or 0
        )

        revised = float(
            line.get("revised_budget") or 0
        )

        fund = _get_dimension_value(
            line,
            "fund_code",
            "fund",
        )

        donor = _get_dimension_value(
            line,
            "donor_code",
            "donor",
        )

        program = _get_dimension_value(
            line,
            "program_code",
            "program",
        )

        project = _get_dimension_value(
            line,
            "project_code",
            "project",
        )

        total_original_budget += original
        total_revised_budget += revised

        if fund:
            funds[fund] += revised

        if donor:
            donors[donor] += revised

        if program:
            programs[program] += revised

        if project:
            projects[project] += revised

    return {
        "total_original_budget": round(
            total_original_budget,
            2,
        ),
        "total_revised_budget": round(
            total_revised_budget,
            2,
        ),
        "budget_line_count": len(
            budget_lines
        ),
        "fund_count": len(
            funds
        ),
        "donor_count": len(
            donors
        ),
        "program_count": len(
            programs
        ),
        "project_count": len(
            projects
        ),
        "largest_funds": _get_largest(
            funds
        ),
        "largest_donors": _get_largest(
            donors
        ),
        "largest_programs": _get_largest(
            programs
        ),
        "largest_projects": _get_largest(
            projects
        ),
    }


def _get_dimension_value(
    line: dict[str, Any],
    *field_names: str,
) -> str | None:
    """
    Return the first populated canonical or
    backward-compatible dimension value.
    """

    for field_name in field_names:

        value = line.get(
            field_name
        )

        if value is None:
            continue

        cleaned = str(
            value
        ).strip()

        if not cleaned:
            continue

        if cleaned.lower() in {
            "none",
            "null",
            "nan",
            "unknown",
        }:
            continue

        return cleaned

    return None


def _get_largest(
    values: dict[str, float],
) -> list[tuple[str, float]]:
    """
    Return the ten largest dimension values.
    """

    return sorted(
        values.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:10]