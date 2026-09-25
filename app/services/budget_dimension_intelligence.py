from typing import Any


DIMENSION_CONFIG = {
    "fund": {
        "view_key": "by_fund",
        "code_key": "fund_code",
        "name_key": "fund_name",
    },
    "donor": {
        "view_key": "by_donor",
        "code_key": "donor_code",
        "name_key": "donor_name",
    },
    "program": {
        "view_key": "by_program",
        "code_key": "program_code",
        "name_key": "program_name",
    },
    "project": {
        "view_key": "by_project",
        "code_key": "project_code",
        "name_key": "project_name",
    },
    "category": {
        "view_key": "by_category",
        "code_key": "category_code",
        "name_key": "category_name",
    },
    "budget_line": {
        "view_key": "by_budget_line",
        "code_key": "budget_line_code",
        "name_key": "budget_line_name",
    },
    "donor_line": {
        "view_key": "by_donor_line",
        "code_key": "donor_line_code",
        "name_key": "donor_line_name",
    },
}


def _number(value: Any) -> float | None:
    if value is None or value == "":
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _record_identity(
    line: dict[str, Any],
    code_key: str,
    name_key: str,
) -> dict[str, Any]:
    code = (
        line.get(code_key)
        or line.get("code")
        or None
    )

    name = line.get(name_key) or None

    return {
        "code": code,
        "name": name,
    }


def _build_priority_item(
    line: dict[str, Any],
    code_key: str,
    name_key: str,
) -> dict[str, Any]:
    identity = _record_identity(
        line=line,
        code_key=code_key,
        name_key=name_key,
    )

    return {
        **identity,
        "budget": _number(line.get("budget")),
        "actual": _number(line.get("actual")),
        "variance": _number(line.get("variance")),
        "utilization_percentage": _number(
            line.get("utilization_percentage")
        ),
        "status": line.get("status"),
    }


def _largest_unfavorable_variance(
    lines: list[dict[str, Any]],
    code_key: str,
    name_key: str,
) -> dict[str, Any] | None:
    candidates = []

    for line in lines:
        variance = _number(line.get("variance"))

        if variance is None:
            continue

        if variance < 0:
            candidates.append(line)

    if not candidates:
        return None

    selected = min(
        candidates,
        key=lambda line: _number(
            line.get("variance")
        )
        or 0,
    )

    return _build_priority_item(
        selected,
        code_key,
        name_key,
    )


def _highest_utilization(
    lines: list[dict[str, Any]],
    code_key: str,
    name_key: str,
) -> dict[str, Any] | None:
    candidates = []

    for line in lines:
        budget = _number(line.get("budget"))
        utilization = _number(
            line.get("utilization_percentage")
        )

        if (
            budget is None
            or budget <= 0
            or utilization is None
        ):
            continue

        candidates.append(line)

    if not candidates:
        return None

    selected = max(
        candidates,
        key=lambda line: _number(
            line.get("utilization_percentage")
        )
        or 0,
    )

    return _build_priority_item(
        selected,
        code_key,
        name_key,
    )


def _lowest_utilization(
    lines: list[dict[str, Any]],
    code_key: str,
    name_key: str,
) -> dict[str, Any] | None:
    candidates = []

    for line in lines:
        budget = _number(line.get("budget"))
        utilization = _number(
            line.get("utilization_percentage")
        )

        if (
            budget is None
            or budget <= 0
            or utilization is None
        ):
            continue

        candidates.append(line)

    if not candidates:
        return None

    selected = min(
        candidates,
        key=lambda line: _number(
            line.get("utilization_percentage")
        )
        or 0,
    )

    return _build_priority_item(
        selected,
        code_key,
        name_key,
    )


def _build_priority_items(
    lines: list[dict[str, Any]],
    code_key: str,
    name_key: str,
    limit: int = 5,
) -> list[dict[str, Any]]:
    priority_lines = []

    for line in lines:
        status = line.get("status")
        actual = _number(line.get("actual")) or 0
        variance = _number(line.get("variance"))
        utilization = _number(
            line.get("utilization_percentage")
        )

        if status == "Over Budget":
            priority_lines.append(line)
            continue

        if status == "No Budget" and actual > 0:
            priority_lines.append(line)
            continue

        if variance is not None and variance < 0:
            priority_lines.append(line)
            continue

        if (
            utilization is not None
            and utilization > 100
        ):
            priority_lines.append(line)

    def priority_score(
        line: dict[str, Any],
    ) -> tuple[int, float, float]:
        status = line.get("status")

        severity_rank = {
            "No Budget": 3,
            "Over Budget": 2,
        }.get(status, 1)

        actual = abs(
            _number(line.get("actual")) or 0
        )

        unfavorable_variance = abs(
            min(
                _number(line.get("variance")) or 0,
                0,
            )
        )

        return (
            severity_rank,
            actual,
            unfavorable_variance,
        )

    sorted_lines = sorted(
        priority_lines,
        key=priority_score,
        reverse=True,
    )

    return [
        _build_priority_item(
            line,
            code_key,
            name_key,
        )
        for line in sorted_lines[:limit]
    ]


def _analyze_dimension(
    lines: list[dict[str, Any]],
    code_key: str,
    name_key: str,
) -> dict[str, Any]:
    over_budget_lines = [
        line
        for line in lines
        if line.get("status") == "Over Budget"
    ]

    no_budget_lines = [
        line
        for line in lines
        if (
            line.get("status") == "No Budget"
            and (
                _number(line.get("actual")) or 0
            )
            > 0
        )
    ]

    no_budget_actual = sum(
        _number(line.get("actual")) or 0
        for line in no_budget_lines
    )

    total_budget = sum(
        _number(line.get("budget")) or 0
        for line in lines
    )

    total_actual = sum(
        _number(line.get("actual")) or 0
        for line in lines
    )

    return {
        "record_count": len(lines),
        "total_budget": total_budget,
        "total_actual": total_actual,
        "over_budget_count": len(
            over_budget_lines
        ),
        "no_budget_count": len(
            no_budget_lines
        ),
        "no_budget_actual": no_budget_actual,
        "largest_unfavorable_variance": (
            _largest_unfavorable_variance(
                lines=lines,
                code_key=code_key,
                name_key=name_key,
            )
        ),
        "highest_utilization": (
            _highest_utilization(
                lines=lines,
                code_key=code_key,
                name_key=name_key,
            )
        ),
        "lowest_utilization": (
            _lowest_utilization(
                lines=lines,
                code_key=code_key,
                name_key=name_key,
            )
        ),
        "priority_items": (
            _build_priority_items(
                lines=lines,
                code_key=code_key,
                name_key=name_key,
            )
        ),
    }


def generate_budget_dimension_intelligence(
    budget_dashboard: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Generate structured management intelligence
    from validated Budget vs Actual dimension views.

    This service does not recalculate Budget vs Actual.
    It interprets already-validated dimension outputs.

    Empty organization dimensions are skipped
    automatically.
    """

    budget_dashboard = (
        budget_dashboard or {}
    )

    intelligence: dict[str, Any] = {}

    for (
        dimension,
        config,
    ) in DIMENSION_CONFIG.items():
        view = budget_dashboard.get(
            config["view_key"],
            {},
        )

        lines = view.get(
            "lines",
            [],
        )

        if not lines:
            continue

        intelligence[dimension] = (
            _analyze_dimension(
                lines=lines,
                code_key=config["code_key"],
                name_key=config["name_key"],
            )
        )

    return intelligence