from typing import Any


PRIORITY_ORDER = {
    "Critical": 4,
    "High": 3,
    "Medium": 2,
    "Low": 1,
}


HISTORICAL_SIGNAL_BY_PRIORITY = {
    "Critical": "immediate_action",
    "High": "priority_attention",
    "Medium": "management_review",
    "Low": "monitor",
}


def generate_historical_decision_intelligence(
    historical_change_analysis: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Build deterministic Historical Decision Intelligence from
    already-generated Financial Intelligence Change Analysis.

    This service interprets verified historical movement for
    management prioritization.

    It does not:
    - recalculate financial intelligence,
    - compare raw financial statements,
    - modify historical snapshots,
    - rerun Risk Intelligence,
    - interpret hypothetical scenarios,
    - invent missing evidence,
    - invent management owners,
    - invent due dates,
    - mutate the CFO Action Plan.

    Negative and positive historical evidence remain separate.
    Improvements never cancel deteriorations.
    """

    historical_change_analysis = (
        historical_change_analysis
        if isinstance(
            historical_change_analysis,
            dict,
        )
        else {}
    )

    if (
        historical_change_analysis.get(
            "status"
        )
        != "available"
    ):
        return {
            "status": "not_available",
            "historical_signal": "monitor",
            "overall_direction": (
                "stable_or_insufficient_evidence"
            ),
            "highest_priority": "Low",
            "management_attention": "monitor",
            "priority_count": 0,
            "improvement_count": 0,
            "management_focus": [],
            "priorities": [],
            "improvements": [],
            "controls": _controls(),
        }

    overall_direction = _clean_text(
        historical_change_analysis.get(
            "overall_direction"
        )
    ) or "stable_or_insufficient_evidence"

    source_management_attention = (
        _clean_text(
            historical_change_analysis.get(
                "management_attention"
            )
        )
        or "monitor"
    )

    metric_change = (
        historical_change_analysis.get(
            "metric_change",
            {},
        )
        or {}
    )

    risk_change = (
        historical_change_analysis.get(
            "risk_change",
            {},
        )
        or {}
    )

    priorities: list[
        dict[str, Any]
    ] = []

    improvements: list[
        dict[str, Any]
    ] = []

    # ==================================================
    # 1. RISK MOVEMENT
    # ==================================================

    movements = (
        risk_change.get(
            "movements",
            [],
        )
        or []
    )

    for movement in movements:

        if not isinstance(
            movement,
            dict,
        ):
            continue

        movement_type = _clean_text(
            movement.get(
                "movement"
            )
        ).lower()

        previous = (
            movement.get(
                "previous"
            )
            if isinstance(
                movement.get(
                    "previous"
                ),
                dict,
            )
            else {}
        )

        current = (
            movement.get(
                "current"
            )
            if isinstance(
                movement.get(
                    "current"
                ),
                dict,
            )
            else {}
        )

        # ----------------------------------------------
        # New risks
        # ----------------------------------------------

        if movement_type == "new":

            priority = _normalize_priority(
                current.get(
                    "severity"
                )
            )

            title = (
                _clean_text(
                    current.get(
                        "title"
                    )
                )
                or "New financial risk"
            )

            category = (
                _clean_text(
                    current.get(
                        "category"
                    )
                )
                or "Financial Risk"
            )

            evidence = _clean_text(
                current.get(
                    "evidence"
                )
            )

            priorities.append(
                {
                    "priority": priority,
                    "category": category,
                    "title": title,
                    "evidence": evidence,
                    "historical_change": (
                        "new_risk"
                    ),
                    "previous_value": None,
                    "current_value": (
                        _clean_text(
                            current.get(
                                "severity"
                            )
                        )
                        or None
                    ),
                    "source": (
                        "financial_intelligence_change"
                    ),
                    "source_type": (
                        "new_risk"
                    ),
                }
            )

        # ----------------------------------------------
        # Risk severity increased
        # ----------------------------------------------

        elif (
            movement_type
            == "severity_increased"
        ):

            priority = _normalize_priority(
                current.get(
                    "severity"
                )
            )

            title = (
                _clean_text(
                    current.get(
                        "title"
                    )
                )
                or "Financial risk"
            )

            category = (
                _clean_text(
                    current.get(
                        "category"
                    )
                )
                or "Financial Risk"
            )

            previous_severity = (
                _clean_text(
                    previous.get(
                        "severity"
                    )
                )
                or "Unknown"
            )

            current_severity = (
                _clean_text(
                    current.get(
                        "severity"
                    )
                )
                or "Unknown"
            )

            evidence = _clean_text(
                current.get(
                    "evidence"
                )
            )

            priorities.append(
                {
                    "priority": priority,
                    "category": category,
                    "title": title,
                    "evidence": evidence,
                    "historical_change": (
                        "risk_severity_increased"
                    ),
                    "previous_value": (
                        previous_severity
                    ),
                    "current_value": (
                        current_severity
                    ),
                    "source": (
                        "financial_intelligence_change"
                    ),
                    "source_type": (
                        "severity_increased"
                    ),
                }
            )

        # ----------------------------------------------
        # Resolved risks
        # ----------------------------------------------

        elif movement_type == "resolved":

            title = (
                _clean_text(
                    previous.get(
                        "title"
                    )
                )
                or "Financial risk"
            )

            category = (
                _clean_text(
                    previous.get(
                        "category"
                    )
                )
                or "Financial Risk"
            )

            previous_severity = (
                _clean_text(
                    previous.get(
                        "severity"
                    )
                )
                or None
            )

            improvements.append(
                {
                    "category": category,
                    "title": title,
                    "evidence": _clean_text(
                        previous.get(
                            "evidence"
                        )
                    ),
                    "historical_change": (
                        "risk_resolved"
                    ),
                    "previous_value": (
                        previous_severity
                    ),
                    "current_value": None,
                    "source": (
                        "financial_intelligence_change"
                    ),
                    "source_type": (
                        "resolved_risk"
                    ),
                }
            )

        # ----------------------------------------------
        # Risk severity decreased
        # ----------------------------------------------

        elif (
            movement_type
            == "severity_decreased"
        ):

            title = (
                _clean_text(
                    current.get(
                        "title"
                    )
                )
                or _clean_text(
                    previous.get(
                        "title"
                    )
                )
                or "Financial risk"
            )

            category = (
                _clean_text(
                    current.get(
                        "category"
                    )
                )
                or _clean_text(
                    previous.get(
                        "category"
                    )
                )
                or "Financial Risk"
            )

            previous_severity = (
                _clean_text(
                    previous.get(
                        "severity"
                    )
                )
                or "Unknown"
            )

            current_severity = (
                _clean_text(
                    current.get(
                        "severity"
                    )
                )
                or "Unknown"
            )

            improvements.append(
                {
                    "category": category,
                    "title": title,
                    "evidence": _clean_text(
                        current.get(
                            "evidence"
                        )
                    ),
                    "historical_change": (
                        "risk_severity_decreased"
                    ),
                    "previous_value": (
                        previous_severity
                    ),
                    "current_value": (
                        current_severity
                    ),
                    "source": (
                        "financial_intelligence_change"
                    ),
                    "source_type": (
                        "severity_decreased"
                    ),
                }
            )

    # ==================================================
    # 2. FINANCIAL METRIC MOVEMENT
    # ==================================================

    comparisons = (
        metric_change.get(
            "comparisons",
            [],
        )
        or []
    )

    for comparison in comparisons:

        if not isinstance(
            comparison,
            dict,
        ):
            continue

        signal = _clean_text(
            comparison.get(
                "signal"
            )
        ).lower()

        label = (
            _clean_text(
                comparison.get(
                    "label"
                )
            )
            or "Financial metric"
        )

        section = (
            _clean_text(
                comparison.get(
                    "section"
                )
            )
            or "Financial Performance"
        )

        previous_value = (
            comparison.get(
                "previous_value"
            )
        )

        current_value = (
            comparison.get(
                "current_value"
            )
        )

        absolute_change = (
            comparison.get(
                "absolute_change"
            )
        )

        percentage_change = (
            comparison.get(
                "percentage_change"
            )
        )

        unit = _clean_text(
            comparison.get(
                "unit"
            )
        )

        # ----------------------------------------------
        # Deteriorating health-direction metric
        # ----------------------------------------------
        #
        # Medium is a management-priority classification
        # defined by this deterministic layer.
        #
        # We do not promote metric deterioration to High
        # or Critical without a corresponding verified
        # Risk Register severity.
        # ----------------------------------------------

        if signal == "deteriorated":

            priorities.append(
                {
                    "priority": "Medium",
                    "category": _format_name(
                        section
                    ),
                    "title": (
                        f"{label} deteriorated"
                    ),
                    "evidence": (
                        _build_metric_evidence(
                            label=label,
                            previous_value=(
                                previous_value
                            ),
                            current_value=(
                                current_value
                            ),
                            absolute_change=(
                                absolute_change
                            ),
                            percentage_change=(
                                percentage_change
                            ),
                            unit=unit,
                        )
                    ),
                    "historical_change": (
                        "metric_deteriorated"
                    ),
                    "previous_value": (
                        previous_value
                    ),
                    "current_value": (
                        current_value
                    ),
                    "source": (
                        "financial_intelligence_change"
                    ),
                    "source_type": (
                        "deteriorated_metric"
                    ),
                }
            )

        # ----------------------------------------------
        # Improving health-direction metric
        # ----------------------------------------------

        elif signal == "improved":

            improvements.append(
                {
                    "category": _format_name(
                        section
                    ),
                    "title": (
                        f"{label} improved"
                    ),
                    "evidence": (
                        _build_metric_evidence(
                            label=label,
                            previous_value=(
                                previous_value
                            ),
                            current_value=(
                                current_value
                            ),
                            absolute_change=(
                                absolute_change
                            ),
                            percentage_change=(
                                percentage_change
                            ),
                            unit=unit,
                        )
                    ),
                    "historical_change": (
                        "metric_improved"
                    ),
                    "previous_value": (
                        previous_value
                    ),
                    "current_value": (
                        current_value
                    ),
                    "source": (
                        "financial_intelligence_change"
                    ),
                    "source_type": (
                        "improved_metric"
                    ),
                }
            )

        # ----------------------------------------------
        # Direction-only metrics
        # ----------------------------------------------
        #
        # Increased / decreased direction-only metrics
        # intentionally do not become priorities or
        # improvements because Change Analysis already
        # determined that they are not evidence of health
        # improvement or deterioration.
        # ----------------------------------------------

        elif signal in {
            "increased",
            "decreased",
            "unchanged",
            "unavailable",
        }:
            continue

    # ==================================================
    # 3. DETERMINISTIC PRIORITY ORDER
    # ==================================================

    priorities.sort(
        key=lambda item: (
            PRIORITY_ORDER.get(
                str(
                    item.get(
                        "priority"
                    )
                ),
                0,
            ),
            _source_rank(
                item.get(
                    "source_type"
                )
            ),
            str(
                item.get(
                    "category"
                )
                or ""
            ).lower(),
            str(
                item.get(
                    "title"
                )
                or ""
            ).lower(),
        ),
        reverse=True,
    )

    for index, priority in enumerate(
        priorities,
        start=1,
    ):
        priority["rank"] = index

    # ==================================================
    # 4. IMPROVEMENT ORDER
    # ==================================================

    improvements.sort(
        key=lambda item: (
            _improvement_source_rank(
                item.get(
                    "source_type"
                )
            ),
            str(
                item.get(
                    "category"
                )
                or ""
            ).lower(),
            str(
                item.get(
                    "title"
                )
                or ""
            ).lower(),
        ),
        reverse=True,
    )

    # ==================================================
    # 5. HIGHEST PRIORITY / SIGNAL
    # ==================================================

    if priorities:

        highest_priority = str(
            priorities[0].get(
                "priority"
            )
            or "Low"
        )

        historical_signal = (
            HISTORICAL_SIGNAL_BY_PRIORITY.get(
                highest_priority,
                "monitor",
            )
        )

    else:

        highest_priority = "Low"
        historical_signal = "monitor"

    # ==================================================
    # 6. MANAGEMENT FOCUS
    # ==================================================

    management_focus = [
        {
            "rank": priority.get(
                "rank"
            ),
            "priority": priority.get(
                "priority"
            ),
            "category": priority.get(
                "category"
            ),
            "title": priority.get(
                "title"
            ),
            "historical_change": (
                priority.get(
                    "historical_change"
                )
            ),
        }
        for priority in priorities[:5]
    ]

    # ==================================================
    # 7. RESULT
    # ==================================================

    return {
        "status": "available",
        "historical_signal": (
            historical_signal
        ),
        "overall_direction": (
            overall_direction
        ),
        "highest_priority": (
            highest_priority
        ),
        "management_attention": (
            source_management_attention
        ),
        "priority_count": len(
            priorities
        ),
        "improvement_count": len(
            improvements
        ),
        "management_focus": (
            management_focus
        ),
        "priorities": priorities,
        "improvements": improvements,
        "evidence_summary": (
            historical_change_analysis.get(
                "evidence_summary",
                {},
            )
            or {}
        ),
        "snapshot_a": (
            historical_change_analysis.get(
                "snapshot_a",
                {},
            )
            or {}
        ),
        "snapshot_b": (
            historical_change_analysis.get(
                "snapshot_b",
                {},
            )
            or {}
        ),
        "controls": _controls(),
    }


def _controls() -> dict[str, bool]:
    return {
        "deterministic": True,
        "read_only": True,
        "source_is_historical_change_analysis": True,
        "financial_recalculation_performed": False,
        "historical_snapshots_modified": False,
        "historical_change_preserved": True,
        "missing_evidence_not_invented": True,
        "hypothetical_scenarios_excluded": True,
        "neutral_metric_movements_excluded_from_health_direction": (
            True
        ),
        "positive_and_negative_evidence_kept_separate": True,
        "improvements_do_not_cancel_priorities": True,
        "management_actions_not_invented": True,
        "owners_not_invented": True,
        "due_dates_not_invented": True,
        "action_plan_not_modified": True,
    }


def _normalize_priority(
    value: Any,
) -> str:

    text = _clean_text(
        value
    ).lower()

    mapping = {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
    }

    return mapping.get(
        text,
        "Medium",
    )


def _source_rank(
    source_type: Any,
) -> int:

    source = _clean_text(
        source_type
    ).lower()

    ranking = {
        "new_risk": 4,
        "severity_increased": 3,
        "deteriorated_metric": 2,
    }

    return ranking.get(
        source,
        0,
    )


def _improvement_source_rank(
    source_type: Any,
) -> int:

    source = _clean_text(
        source_type
    ).lower()

    ranking = {
        "resolved_risk": 3,
        "severity_decreased": 2,
        "improved_metric": 1,
    }

    return ranking.get(
        source,
        0,
    )


def _build_metric_evidence(
    *,
    label: str,
    previous_value: Any,
    current_value: Any,
    absolute_change: Any,
    percentage_change: Any,
    unit: str,
) -> str:

    evidence = (
        f"{label} changed from "
        f"{_display_value(previous_value)} "
        f"to {_display_value(current_value)}"
    )

    if unit:
        evidence += f" {unit}"

    if absolute_change is not None:

        evidence += (
            f", an absolute change of "
            f"{_display_value(absolute_change)}"
        )

        if unit:
            evidence += f" {unit}"

    if percentage_change is not None:

        evidence += (
            f" ({_display_value(percentage_change)}%)."
        )

    else:
        evidence += "."

    return evidence


def _display_value(
    value: Any,
) -> str:

    if value is None:
        return "N/A"

    if isinstance(
        value,
        float,
    ):
        return (
            f"{value:.2f}"
            .rstrip("0")
            .rstrip(".")
        )

    return str(
        value
    )


def _clean_text(
    value: Any,
) -> str:

    return str(
        value or ""
    ).strip()


def _format_name(
    value: Any,
) -> str:

    text = _clean_text(
        value
    )

    if not text:
        return "Financial Management"

    return (
        text
        .replace(
            "_",
            " ",
        )
        .strip()
        .title()
    )