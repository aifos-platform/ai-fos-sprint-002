from datetime import date
from typing import Any


def generate_cfo_action_escalation(
    monitoring: dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Build deterministic Management Follow-Up &
    Escalation Intelligence from CFO Action Monitoring.

    This service does not:
    - recalculate financial information,
    - recalculate Action Plan monitoring classifications,
    - modify action records,
    - invent owners,
    - invent due dates,
    - invent blockers,
    - replace persisted management state.

    It interprets already-calculated monitoring signals and
    determines which actions require management intervention.
    """

    monitoring = monitoring or {}

    if (
        monitoring.get("status")
        != "available"
    ):
        return {
            "status": "not_available",
            "summary": {
                "total_escalations": 0,
                "critical": 0,
                "high": 0,
                "medium": 0,
            },
            "highest_escalation": None,
            "escalations": [],
            "management_focus": [],
            "controls": _controls(),
        }

    reference_date = _parse_date(
        monitoring.get(
            "reference_date"
        )
    )

    overdue_actions = _valid_actions(
        monitoring.get(
            "overdue_actions"
        )
    )

    due_soon_actions = _valid_actions(
        monitoring.get(
            "due_soon_actions"
        )
    )

    blocked_actions = _valid_actions(
        monitoring.get(
            "blocked_actions"
        )
    )

    unassigned_high_priority_actions = (
        _valid_actions(
            monitoring.get(
                "unassigned_high_priority_actions"
            )
        )
    )

    signals_by_action: dict[
        str,
        dict[str, Any],
    ] = {}

    def register_signal(
        action: dict[str, Any],
        signal: str,
    ) -> None:
        key = _action_key(
            action
        )

        if key not in signals_by_action:
            signals_by_action[key] = {
                "action": action,
                "signals": set(),
            }

        signals_by_action[
            key
        ]["signals"].add(
            signal
        )

    for action in overdue_actions:
        register_signal(
            action,
            "overdue",
        )

    for action in due_soon_actions:
        register_signal(
            action,
            "due_soon",
        )

    for action in blocked_actions:
        register_signal(
            action,
            "blocked",
        )

    for action in (
        unassigned_high_priority_actions
    ):
        register_signal(
            action,
            "unassigned_high_priority",
        )

    escalations: list[
        dict[str, Any]
    ] = []

    for item in (
        signals_by_action.values()
    ):
        action = item[
            "action"
        ]

        signals = set(
            item[
                "signals"
            ]
        )

        escalation = (
            _build_escalation(
                action=action,
                signals=signals,
                reference_date=(
                    reference_date
                ),
            )
        )

        if escalation is not None:
            escalations.append(
                escalation
            )

    escalations = sorted(
        escalations,
        key=_escalation_sort_key,
    )

    critical_count = sum(
        1
        for item in escalations
        if item.get(
            "severity"
        )
        == "Critical"
    )

    high_count = sum(
        1
        for item in escalations
        if item.get(
            "severity"
        )
        == "High"
    )

    medium_count = sum(
        1
        for item in escalations
        if item.get(
            "severity"
        )
        == "Medium"
    )

    highest_escalation = (
        escalations[0].get(
            "severity"
        )
        if escalations
        else None
    )

    management_focus = [
        {
            "action_id": item.get(
                "action_id"
            ),
            "title": item.get(
                "title"
            ),
            "severity": item.get(
                "severity"
            ),
            "management_attention": (
                item.get(
                    "management_attention"
                )
            ),
            "reasons": item.get(
                "reasons",
                [],
            ),
            "recommended_follow_up": (
                item.get(
                    "recommended_follow_up"
                )
            ),
        }
        for item in escalations[:5]
    ]

    return {
        "status": "available",
        "reference_date": (
            monitoring.get(
                "reference_date"
            )
        ),
        "summary": {
            "total_escalations": len(
                escalations
            ),
            "critical": (
                critical_count
            ),
            "high": high_count,
            "medium": medium_count,
        },
        "highest_escalation": (
            highest_escalation
        ),
        "escalations": escalations,
        "management_focus": (
            management_focus
        ),
        "controls": _controls(),
    }


def _build_escalation(
    *,
    action: dict[str, Any],
    signals: set[str],
    reference_date: date | None,
) -> dict[str, Any] | None:

    if not signals:
        return None

    action_id = str(
        action.get(
            "action_id",
            "",
        )
        or ""
    ).strip()

    title = str(
        action.get(
            "title",
            "Management action",
        )
        or "Management action"
    ).strip()

    priority = str(
        action.get(
            "priority",
            "Medium",
        )
        or "Medium"
    ).strip().title()

    status = str(
        action.get(
            "status",
            "open",
        )
        or "open"
    ).strip().lower()

    owner = (
        str(
            action.get(
                "owner",
                "",
            )
            or ""
        ).strip()
        or None
    )

    due_date_text = (
        str(
            action.get(
                "due_date",
                "",
            )
            or ""
        ).strip()
        or None
    )

    days_overdue: int | None = (
        None
    )

    if (
        "overdue" in signals
        and reference_date is not None
    ):
        parsed_due_date = (
            _parse_date(
                due_date_text
            )
        )

        if (
            parsed_due_date
            is not None
        ):
            days_overdue = (
                reference_date
                - parsed_due_date
            ).days

    severity = (
        _determine_severity(
            priority=priority,
            signals=signals,
        )
    )

    reasons = (
        _build_reasons(
            priority=priority,
            signals=signals,
            days_overdue=days_overdue,
        )
    )

    management_attention = (
        _management_attention(
            severity
        )
    )

    recommended_follow_up = (
        _recommended_follow_up(
            signals=signals,
        )
    )

    return {
        "action_id": action_id,
        "title": title,
        "priority": priority,
        "status": status,
        "owner": owner,
        "due_date": due_date_text,
        "days_overdue": (
            days_overdue
        ),
        "severity": severity,
        "management_attention": (
            management_attention
        ),
        "signals": sorted(
            signals
        ),
        "reasons": reasons,
        "recommended_follow_up": (
            recommended_follow_up
        ),
    }


def _determine_severity(
    *,
    priority: str,
    signals: set[str],
) -> str:
    """
    Determine execution escalation severity.

    Critical:
    - Critical-priority action is overdue.
    - Any overdue action is also blocked.
    - Any overdue Critical/High action has no owner.

    High:
    - Any other overdue action.
    - Critical/High action is blocked.
    - Critical/High action has no owner.

    Medium:
    - Due soon.
    - Lower-priority blocked action.
    """

    overdue = (
        "overdue"
        in signals
    )

    blocked = (
        "blocked"
        in signals
    )

    unassigned_high = (
        "unassigned_high_priority"
        in signals
    )

    due_soon = (
        "due_soon"
        in signals
    )

    high_priority = (
        priority
        in {
            "Critical",
            "High",
        }
    )

    if (
        overdue
        and priority == "Critical"
    ):
        return "Critical"

    if (
        overdue
        and blocked
    ):
        return "Critical"

    if (
        overdue
        and unassigned_high
    ):
        return "Critical"

    if overdue:
        return "High"

    if (
        blocked
        and high_priority
    ):
        return "High"

    if unassigned_high:
        return "High"

    if (
        due_soon
        or blocked
    ):
        return "Medium"

    return "Medium"


def _build_reasons(
    *,
    priority: str,
    signals: set[str],
    days_overdue: int | None,
) -> list[str]:

    reasons: list[str] = []

    if "overdue" in signals:
        if (
            days_overdue
            is not None
        ):
            reasons.append(
                "Action is overdue by "
                f"{days_overdue} day(s)."
            )

        else:
            reasons.append(
                "Action is overdue."
            )

    if "blocked" in signals:
        reasons.append(
            "Action is currently blocked."
        )

    if (
        "unassigned_high_priority"
        in signals
    ):
        reasons.append(
            f"{priority}-priority action "
            "has no assigned owner."
        )

    if "due_soon" in signals:
        reasons.append(
            "Action is due soon."
        )

    return reasons


def _recommended_follow_up(
    *,
    signals: set[str],
) -> str:

    overdue = (
        "overdue"
        in signals
    )

    blocked = (
        "blocked"
        in signals
    )

    unassigned = (
        "unassigned_high_priority"
        in signals
    )

    due_soon = (
        "due_soon"
        in signals
    )

    if (
        overdue
        and blocked
    ):
        return (
            "Escalate the action to management, "
            "resolve the blocker, confirm ownership, "
            "and agree an updated execution date."
        )

    if (
        overdue
        and unassigned
    ):
        return (
            "Assign an accountable owner immediately "
            "and agree a recovery date for the "
            "overdue action."
        )

    if overdue:
        return (
            "Review the overdue action with the "
            "responsible owner and agree the next "
            "execution step and revised date."
        )

    if (
        blocked
        and unassigned
    ):
        return (
            "Assign an accountable owner and resolve "
            "the blocker before execution can continue."
        )

    if blocked:
        return (
            "Identify the blocking issue and agree "
            "the management action required to "
            "resume execution."
        )

    if unassigned:
        return (
            "Assign an accountable owner before the "
            "action requires further escalation."
        )

    if due_soon:
        return (
            "Confirm that the action remains on track "
            "for completion by its due date."
        )

    return (
        "Continue monitoring the action."
    )


def _management_attention(
    severity: str,
) -> str:

    mapping = {
        "Critical": (
            "immediate_intervention"
        ),
        "High": (
            "priority_follow_up"
        ),
        "Medium": (
            "near_term_follow_up"
        ),
    }

    return mapping.get(
        severity,
        "monitor",
    )


def _valid_actions(
    value: Any,
) -> list[dict[str, Any]]:

    if not isinstance(
        value,
        list,
    ):
        return []

    return [
        action
        for action in value
        if isinstance(
            action,
            dict,
        )
    ]


def _action_key(
    action: dict[str, Any],
) -> str:

    action_id = str(
        action.get(
            "action_id",
            "",
        )
        or ""
    ).strip()

    if action_id:
        return (
            f"id:{action_id}"
        )

    title = str(
        action.get(
            "title",
            "",
        )
        or ""
    ).strip().lower()

    due_date = str(
        action.get(
            "due_date",
            "",
        )
        or ""
    ).strip()

    priority = str(
        action.get(
            "priority",
            "",
        )
        or ""
    ).strip().lower()

    return (
        f"fallback:"
        f"{title}|"
        f"{due_date}|"
        f"{priority}"
    )


def _parse_date(
    value: Any,
) -> date | None:

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


def _escalation_sort_key(
    escalation: dict[str, Any],
) -> tuple[Any, ...]:

    severity_rank = {
        "Critical": 0,
        "High": 1,
        "Medium": 2,
    }

    priority_rank = {
        "Critical": 0,
        "High": 1,
        "Medium": 2,
        "Low": 3,
    }

    severity = str(
        escalation.get(
            "severity",
            "Medium",
        )
        or "Medium"
    )

    priority = str(
        escalation.get(
            "priority",
            "Medium",
        )
        or "Medium"
    )

    due_date = str(
        escalation.get(
            "due_date",
            "",
        )
        or "9999-12-31"
    )

    title = str(
        escalation.get(
            "title",
            "",
        )
        or ""
    ).lower()

    action_id = str(
        escalation.get(
            "action_id",
            "",
        )
        or ""
    )

    return (
        severity_rank.get(
            severity,
            99,
        ),
        priority_rank.get(
            priority,
            99,
        ),
        due_date,
        title,
        action_id,
    )


def _controls() -> dict[str, bool]:

    return {
        "deterministic": True,
        "source_is_action_monitoring": True,
        "action_records_modified": False,
        "financial_recalculation_performed": False,
        "monitoring_recalculation_performed": False,
        "owner_not_invented": True,
        "due_date_not_invented": True,
        "blocker_not_invented": True,
        "positive_items_do_not_offset_escalations": True,
    }
