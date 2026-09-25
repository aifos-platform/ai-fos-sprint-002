from typing import Any


METRIC_REGISTRY = [
    {
        "metric_id": "financial_health_score",
        "label": "Financial Health Score",
        "section": "financial_health",
        "path": (
            "financial_health",
            "score",
        ),
        "direction": "higher_is_better",
        "unit": "points",
    },
    {
        "metric_id": "operating_performance_score",
        "label": "Operating Performance Score",
        "section": "financial_health",
        "path": (
            "financial_health",
            "categories",
            "operating_performance",
            "score",
        ),
        "direction": "higher_is_better",
        "unit": "points",
    },
    {
        "metric_id": "financial_position_score",
        "label": "Financial Position Score",
        "section": "financial_health",
        "path": (
            "financial_health",
            "categories",
            "financial_position",
            "score",
        ),
        "direction": "higher_is_better",
        "unit": "points",
    },
    {
        "metric_id": "liquidity_score",
        "label": "Liquidity Score",
        "section": "financial_health",
        "path": (
            "financial_health",
            "categories",
            "liquidity",
            "score",
        ),
        "direction": "higher_is_better",
        "unit": "points",
    },
    {
        "metric_id": "budget_control_score",
        "label": "Budget Control Score",
        "section": "financial_health",
        "path": (
            "financial_health",
            "categories",
            "budget_control",
            "score",
        ),
        "direction": "higher_is_better",
        "unit": "points",
    },
    {
        "metric_id": "funding_and_grant_health_score",
        "label": "Funding and Grant Health Score",
        "section": "financial_health",
        "path": (
            "financial_health",
            "categories",
            "funding_and_grant_health",
            "score",
        ),
        "direction": "higher_is_better",
        "unit": "points",
    },
    {
        "metric_id": "total_cash",
        "label": "Total Cash",
        "section": "liquidity",
        "path": (
            "liquidity",
            "total_cash",
        ),
        "direction": "direction_only",
        "unit": "currency",
    },
    {
        "metric_id": "available_cash",
        "label": "Available Cash",
        "section": "liquidity",
        "path": (
            "liquidity",
            "available_cash",
        ),
        "direction": "direction_only",
        "unit": "currency",
    },
    {
        "metric_id": "blocked_cash",
        "label": "Blocked Cash",
        "section": "liquidity",
        "path": (
            "liquidity",
            "blocked_cash",
        ),
        "direction": "direction_only",
        "unit": "currency",
    },
    {
        "metric_id": "unclassified_cash_account_count",
        "label": "Unclassified Cash Account Count",
        "section": "liquidity",
        "path": (
            "liquidity",
            "unclassified_cash_account_count",
        ),
        "direction": "lower_is_better",
        "unit": "count",
    },
    {
        "metric_id": "average_monthly_expenses",
        "label": "Average Monthly Expenses",
        "section": "liquidity",
        "path": (
            "liquidity",
            "average_monthly_expenses",
        ),
        "direction": "direction_only",
        "unit": "currency",
    },
    {
        "metric_id": "cash_runway_months",
        "label": "Cash Runway",
        "section": "liquidity",
        "path": (
            "liquidity",
            "cash_runway_months",
        ),
        "direction": "higher_is_better",
        "unit": "months",
    },
    {
        "metric_id": "remaining_requirement",
        "label": "Remaining Funding Requirement",
        "section": "funding",
        "path": (
            "funding_gap",
            "summary",
            "remaining_requirement",
        ),
        "direction": "direction_only",
        "unit": "currency",
    },
    {
        "metric_id": "applied_secured_funding",
        "label": "Applied Secured Funding",
        "section": "funding",
        "path": (
            "funding_gap",
            "summary",
            "applied_secured_funding",
        ),
        "direction": "direction_only",
        "unit": "currency",
    },
    {
        "metric_id": "funding_gap",
        "label": "Funding Gap",
        "section": "funding",
        "path": (
            "funding_gap",
            "summary",
            "funding_gap",
        ),
        "direction": "lower_is_better",
        "unit": "currency",
    },
    {
        "metric_id": "applied_coverage_percentage",
        "label": "Applied Funding Coverage",
        "section": "funding",
        "path": (
            "funding_gap",
            "summary",
            "applied_coverage_percentage",
        ),
        "direction": "higher_is_better",
        "unit": "percentage",
    },
    {
        "metric_id": "matched_requirement_count",
        "label": "Matched Requirement Count",
        "section": "funding",
        "path": (
            "funding_gap",
            "summary",
            "matched_requirement_count",
        ),
        "direction": "higher_is_better",
        "unit": "count",
    },
    {
        "metric_id": "unmatched_requirement_count",
        "label": "Unmatched Requirement Count",
        "section": "funding",
        "path": (
            "funding_gap",
            "summary",
            "unmatched_requirement_count",
        ),
        "direction": "lower_is_better",
        "unit": "count",
    },
]


def generate_financial_intelligence_change(
    snapshot_a: dict[str, Any] | None,
    snapshot_b: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Compare two immutable verified Financial Intelligence
    History snapshots.

    snapshot_a is the earlier/base state.
    snapshot_b is the later/comparison state.

    This service:
    - reads already-persisted verified outputs,
    - performs deterministic comparisons only,
    - does not recalculate financial intelligence,
    - does not modify historical snapshots,
    - does not infer missing values,
    - does not compare hypothetical scenarios.
    """

    snapshot_a = (
        snapshot_a
        if isinstance(snapshot_a, dict)
        else {}
    )

    snapshot_b = (
        snapshot_b
        if isinstance(snapshot_b, dict)
        else {}
    )

    intelligence_a = snapshot_a.get(
        "financial_intelligence",
        {},
    )

    intelligence_b = snapshot_b.get(
        "financial_intelligence",
        {},
    )

    if not isinstance(
        intelligence_a,
        dict,
    ):
        intelligence_a = {}

    if not isinstance(
        intelligence_b,
        dict,
    ):
        intelligence_b = {}

    comparisons: list[dict[str, Any]] = []

    improved_count = 0
    deteriorated_count = 0
    unchanged_count = 0
    direction_only_count = 0
    unavailable_count = 0

    for metric in METRIC_REGISTRY:

        previous_value = _get_path(
            intelligence_a,
            metric["path"],
        )

        current_value = _get_path(
            intelligence_b,
            metric["path"],
        )

        comparison = _compare_metric(
            metric=metric,
            previous_value=previous_value,
            current_value=current_value,
        )

        comparisons.append(
            comparison
        )

        signal = comparison["signal"]

        if signal == "improved":
            improved_count += 1

        elif signal == "deteriorated":
            deteriorated_count += 1

        elif signal == "unchanged":
            unchanged_count += 1

        elif signal in {
            "increased",
            "decreased",
        }:
            direction_only_count += 1

        elif signal == "unavailable":
            unavailable_count += 1

    if (
        deteriorated_count > 0
        and improved_count == 0
    ):
        overall_signal = "deteriorated"

    elif (
        improved_count > 0
        and deteriorated_count == 0
    ):
        overall_signal = "improved"

    elif (
        improved_count > 0
        and deteriorated_count > 0
    ):
        overall_signal = "mixed"

    else:
        overall_signal = "stable_or_insufficient_evidence"

    return {
        "status": "available",
        "snapshot_a": {
            "snapshot_id": snapshot_a.get(
                "snapshot_id"
            ),
            "captured_at": snapshot_a.get(
                "captured_at"
            ),
        },
        "snapshot_b": {
            "snapshot_id": snapshot_b.get(
                "snapshot_id"
            ),
            "captured_at": snapshot_b.get(
                "captured_at"
            ),
        },
        "overall_signal": overall_signal,
        "summary": {
            "metric_count": len(
                METRIC_REGISTRY
            ),
            "improved_count": improved_count,
            "deteriorated_count": (
                deteriorated_count
            ),
            "unchanged_count": unchanged_count,
            "direction_only_count": (
                direction_only_count
            ),
            "unavailable_count": unavailable_count,
        },
        "comparisons": comparisons,
        "controls": {
            "deterministic": True,
            "read_only": True,
            "financial_recalculation_performed": False,
            "historical_snapshots_modified": False,
            "missing_values_not_invented": True,
            "hypothetical_scenarios_excluded": True,
            "neutral_metrics_not_interpreted_as_health": True,
        },
    }


def _compare_metric(
    *,
    metric: dict[str, Any],
    previous_value: Any,
    current_value: Any,
) -> dict[str, Any]:

    previous_number = _optional_number(
        previous_value
    )

    current_number = _optional_number(
        current_value
    )

    if (
        previous_number is None
        or current_number is None
    ):
        return {
            "metric_id": metric["metric_id"],
            "label": metric["label"],
            "section": metric["section"],
            "unit": metric["unit"],
            "direction_rule": metric["direction"],
            "previous_value": previous_number,
            "current_value": current_number,
            "absolute_change": None,
            "percentage_change": None,
            "signal": "unavailable",
        }

    absolute_change = round(
        current_number - previous_number,
        2,
    )

    if previous_number != 0:
        percentage_change = round(
            (
                absolute_change
                / abs(previous_number)
            )
            * 100.0,
            2,
        )
    else:
        percentage_change = None

    if absolute_change == 0:
        signal = "unchanged"

    elif metric["direction"] == "higher_is_better":

        signal = (
            "improved"
            if absolute_change > 0
            else "deteriorated"
        )

    elif metric["direction"] == "lower_is_better":

        signal = (
            "improved"
            if absolute_change < 0
            else "deteriorated"
        )

    else:

        signal = (
            "increased"
            if absolute_change > 0
            else "decreased"
        )

    return {
        "metric_id": metric["metric_id"],
        "label": metric["label"],
        "section": metric["section"],
        "unit": metric["unit"],
        "direction_rule": metric["direction"],
        "previous_value": previous_number,
        "current_value": current_number,
        "absolute_change": absolute_change,
        "percentage_change": percentage_change,
        "signal": signal,
    }


def _get_path(
    data: dict[str, Any],
    path: tuple[str, ...],
) -> Any:

    current: Any = data

    for key in path:

        if not isinstance(
            current,
            dict,
        ):
            return None

        if key not in current:
            return None

        current = current[key]

    return current


def _optional_number(
    value: Any,
) -> float | None:

    if value is None:
        return None

    if isinstance(
        value,
        bool,
    ):
        return None

    if isinstance(
        value,
        (int, float),
    ):
        return float(
            value
        )

    text = (
        str(
            value
        )
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
        return None

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
        return None

RISK_SEVERITY_RANK = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


RISK_FAMILY_BY_TITLE = {
    "operating deficit": "operating_deficit",
    "liabilities exceed assets": "negative_net_assets",
    "critical financial health": "financial_health",
    "weak financial health": "financial_health",
    "critical cash runway": "cash_runway",
    "low cash runway": "cash_runway",
    "cash runway requires monitoring": "cash_runway",
    "unfunded financial requirements": "funding_gap",
    (
        "secured funding lacks explicit "
        "budget line allocation"
    ): "funding_evidence",
    "material budget control issues": "budget_control",
}


def compare_risk_movement(
    snapshot_a: dict[str, Any] | None,
    snapshot_b: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Compare deterministic Risk Register movement between
    two verified Financial Intelligence History snapshots.

    Risks are matched using canonical AI-FOS risk families
    rather than evidence text or severity-dependent titles.
    """

    risks_a = _snapshot_risks(
        snapshot_a
    )

    risks_b = _snapshot_risks(
        snapshot_b
    )

    indexed_a = _index_risks(
        risks_a
    )

    indexed_b = _index_risks(
        risks_b
    )

    all_families = sorted(
        set(indexed_a)
        | set(indexed_b)
    )

    movements: list[dict[str, Any]] = []

    new_count = 0
    resolved_count = 0
    persistent_count = 0
    severity_increased_count = 0
    severity_decreased_count = 0
    unchanged_count = 0

    for family in all_families:

        previous_risk = indexed_a.get(
            family
        )

        current_risk = indexed_b.get(
            family
        )

        if (
            previous_risk is None
            and current_risk is not None
        ):
            movement = "new"
            new_count += 1

        elif (
            previous_risk is not None
            and current_risk is None
        ):
            movement = "resolved"
            resolved_count += 1

        else:
            previous_severity = (
                _risk_severity_rank(
                    previous_risk
                )
            )

            current_severity = (
                _risk_severity_rank(
                    current_risk
                )
            )

            persistent_count += 1

            if (
                current_severity
                > previous_severity
            ):
                movement = "severity_increased"
                severity_increased_count += 1

            elif (
                current_severity
                < previous_severity
            ):
                movement = "severity_decreased"
                severity_decreased_count += 1

            else:
                movement = "unchanged"
                unchanged_count += 1

        movements.append(
            {
                "risk_family": family,
                "movement": movement,
                "previous": (
                    _risk_summary(
                        previous_risk
                    )
                    if previous_risk
                    else None
                ),
                "current": (
                    _risk_summary(
                        current_risk
                    )
                    if current_risk
                    else None
                ),
            }
        )

    return {
        "status": "available",
        "summary": {
            "new_count": new_count,
            "resolved_count": resolved_count,
            "persistent_count": persistent_count,
            "severity_increased_count": (
                severity_increased_count
            ),
            "severity_decreased_count": (
                severity_decreased_count
            ),
            "unchanged_count": unchanged_count,
        },
        "movements": movements,
        "controls": {
            "deterministic": True,
            "read_only": True,
            "risk_family_matching": True,
            "evidence_text_used_for_matching": False,
            "financial_recalculation_performed": False,
            "missing_risks_not_invented": True,
            "fallback_no_risk_state_excluded": True,
        },
    }


def _snapshot_risks(
    snapshot: dict[str, Any] | None,
) -> list[dict[str, Any]]:

    if not isinstance(
        snapshot,
        dict,
    ):
        return []

    intelligence = snapshot.get(
        "financial_intelligence",
        {},
    )

    if not isinstance(
        intelligence,
        dict,
    ):
        return []

    risks = intelligence.get(
        "risk_assessment",
        [],
    )

    if not isinstance(
        risks,
        list,
    ):
        return []

    return [
        risk
        for risk in risks
        if isinstance(
            risk,
            dict,
        )
        and _normalize_risk_title(
            risk.get(
                "title"
            )
        )
        != "no major financial risks detected"
    ]

def generate_unified_financial_intelligence_change(
    snapshot_a: dict[str, Any] | None,
    snapshot_b: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Generate one deterministic management-level historical
    Change Analysis from two immutable verified Financial
    Intelligence History snapshots.

    Combines:
    - financial metric movement,
    - Risk Register movement,
    - overall historical direction,
    - deterministic management attention.

    This service does not recalculate finance, mutate history,
    interpret neutral directional metrics as financial health,
    or invent missing evidence.
    """

    metric_change = generate_financial_intelligence_change(
        snapshot_a,
        snapshot_b,
    )

    risk_change = compare_risk_movement(
        snapshot_a,
        snapshot_b,
    )

    metric_summary = metric_change.get(
        "summary",
        {},
    )

    risk_summary = risk_change.get(
        "summary",
        {},
    )

    improved_metrics = int(
        metric_summary.get(
            "improved_count",
            0,
        )
        or 0
    )

    deteriorated_metrics = int(
        metric_summary.get(
            "deteriorated_count",
            0,
        )
        or 0
    )

    new_risks = int(
        risk_summary.get(
            "new_count",
            0,
        )
        or 0
    )

    resolved_risks = int(
        risk_summary.get(
            "resolved_count",
            0,
        )
        or 0
    )

    severity_increased = int(
        risk_summary.get(
            "severity_increased_count",
            0,
        )
        or 0
    )

    severity_decreased = int(
        risk_summary.get(
            "severity_decreased_count",
            0,
        )
        or 0
    )

    negative_evidence_count = (
        deteriorated_metrics
        + new_risks
        + severity_increased
    )

    positive_evidence_count = (
        improved_metrics
        + resolved_risks
        + severity_decreased
    )

    if (
        negative_evidence_count > 0
        and positive_evidence_count == 0
    ):
        overall_direction = "deteriorated"

    elif (
        positive_evidence_count > 0
        and negative_evidence_count == 0
    ):
        overall_direction = "improved"

    elif (
        positive_evidence_count > 0
        and negative_evidence_count > 0
    ):
        overall_direction = "mixed"

    else:
        overall_direction = (
            "stable_or_insufficient_evidence"
        )

    critical_or_high_negative_risk = any(
        (
            movement.get("movement")
            in {
                "new",
                "severity_increased",
            }
            and _movement_current_severity(
                movement
            )
            in {
                "critical",
                "high",
            }
        )
        for movement in risk_change.get(
            "movements",
            [],
        )
        if isinstance(
            movement,
            dict,
        )
    )

    if critical_or_high_negative_risk:
        management_attention = "priority_review"

    elif (
        negative_evidence_count >= 2
    ):
        management_attention = "priority_review"

    elif (
        negative_evidence_count == 1
    ):
        management_attention = "review"

    else:
        management_attention = "monitor"

    return {
        "status": "available",
        "snapshot_a": metric_change.get(
            "snapshot_a",
            {},
        ),
        "snapshot_b": metric_change.get(
            "snapshot_b",
            {},
        ),
        "overall_direction": overall_direction,
        "management_attention": (
            management_attention
        ),
        "evidence_summary": {
            "positive_evidence_count": (
                positive_evidence_count
            ),
            "negative_evidence_count": (
                negative_evidence_count
            ),
            "improved_metric_count": (
                improved_metrics
            ),
            "deteriorated_metric_count": (
                deteriorated_metrics
            ),
            "new_risk_count": new_risks,
            "resolved_risk_count": (
                resolved_risks
            ),
            "risk_severity_increased_count": (
                severity_increased
            ),
            "risk_severity_decreased_count": (
                severity_decreased
            ),
        },
        "metric_change": metric_change,
        "risk_change": risk_change,
        "controls": {
            "deterministic": True,
            "read_only": True,
            "financial_recalculation_performed": False,
            "historical_snapshots_modified": False,
            "missing_evidence_not_invented": True,
            "hypothetical_scenarios_excluded": True,
            "neutral_metric_movements_excluded_from_health_direction": True,
            "positive_and_negative_evidence_kept_separate": True,
            "risk_and_metric_outputs_preserved": True,
        },
    }


def _movement_current_severity(
    movement: dict[str, Any],
) -> str | None:

    current = movement.get(
        "current"
    )

    if not isinstance(
        current,
        dict,
    ):
        return None

    severity = str(
        current.get(
            "severity",
            "",
        )
        or ""
    ).strip().lower()

    return (
        severity
        if severity
        else None
    )

def _index_risks(
    risks: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:

    indexed: dict[
        str,
        dict[str, Any],
    ] = {}

    for risk in risks:

        family = _risk_family(
            risk
        )

        existing = indexed.get(
            family
        )

        if existing is None:
            indexed[family] = risk
            continue

        if (
            _risk_severity_rank(
                risk
            )
            > _risk_severity_rank(
                existing
            )
        ):
            indexed[family] = risk

    return indexed


def _risk_family(
    risk: dict[str, Any],
) -> str:

    title = _normalize_risk_title(
        risk.get(
            "title"
        )
    )

    known_family = (
        RISK_FAMILY_BY_TITLE.get(
            title
        )
    )

    if known_family:
        return known_family

    category = (
        str(
            risk.get(
                "category",
                "",
            )
            or ""
        )
        .strip()
        .lower()
    )

    if category and title:
        return (
            f"{category}::{title}"
        )

    if title:
        return title

    return "unknown_risk"


def _risk_severity_rank(
    risk: dict[str, Any] | None,
) -> int:

    if not isinstance(
        risk,
        dict,
    ):
        return 0

    severity = (
        str(
            risk.get(
                "severity",
                "",
            )
            or ""
        )
        .strip()
        .lower()
    )

    return RISK_SEVERITY_RANK.get(
        severity,
        0,
    )


def _risk_summary(
    risk: dict[str, Any],
) -> dict[str, Any]:

    return {
        "severity": risk.get(
            "severity"
        ),
        "category": risk.get(
            "category"
        ),
        "title": risk.get(
            "title"
        ),
        "evidence": risk.get(
            "evidence"
        ),
    }


def _normalize_risk_title(
    value: Any,
) -> str:

    return (
        " ".join(
            str(
                value
                or ""
            )
            .strip()
            .lower()
            .split()
        )
    )    