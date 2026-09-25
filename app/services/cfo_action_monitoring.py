from datetime import date, timedelta
from typing import Any


def generate_cfo_action_monitoring(
    actions: list[dict[str, Any]] | None,
    *,
    reference_date: date | None = None,
    due_soon_days: int = 7,
) -> dict[str, Any]:
    """
    Build deterministic CFO Action Monitoring Intelligence.

    This service interprets persisted CFO Action Plan records.
    It does not modify action records, financial outputs,
    Executive Decision Intelligence, or source provenance.

    Overdue and due-soon classifications are calculated
    dynamically relative to the supplied reference date.
    """

    if reference_date is None:
        reference_date = date.today()

    if due_soon_days < 0:
        raise ValueError(
            "due_soon_days must be zero or greater."
        )

    valid_actions = [
        action
        for action in (actions or [])
        if isinstance(action, dict)
    ]

    overdue_actions: list[dict[str, Any]] = []
    due_soon_actions: list[dict[str, Any]] = []
    blocked_actions: list[dict[str, Any]] = []
    unassigned_high_priority_actions: list[
        dict[str, Any]
    ] = []

    status_counts = {
        "open": 0,
        "in_progress": 0,
        "blocked": 0,
        "completed": 0,
        "cancelled": 0,
    }

    active_statuses = {
        "open",
        "in_progress",
        "blocked",
    }

    high_priorities = {
        "Critical",
        "High",
    }

    due_soon_end = (
        reference_date
        + timedelta(days=due_soon_days)
    )

    for action in valid_actions:
        status = str(
            action.get("status", "open")
            or "open"
        ).strip().lower()

        priority = str(
            action.get("priority", "Medium")
            or "Medium"
        ).strip().title()

        owner = str(
            action.get("owner", "")
            or ""
        ).strip()

        if status in status_counts:
            status_counts[status] += 1

        if status == "blocked":
            blocked_actions.append(
                action
            )

        if (
            status in active_statuses
            and priority in high_priorities
            and not owner
        ):
            unassigned_high_priority_actions.append(
                action
            )

        if status not in active_statuses:
            continue

        due_date = _parse_due_date(
            action.get("due_date")
        )

        if due_date is None:
            continue

        if due_date < reference_date:
            overdue_actions.append(
                action
            )

        elif (
            reference_date
            <= due_date
            <= due_soon_end
        ):
            due_soon_actions.append(
                action
            )

    overdue_actions = _sort_actions(
        overdue_actions
    )

    due_soon_actions = _sort_actions(
        due_soon_actions
    )

    blocked_actions = _sort_actions(
        blocked_actions
    )

    unassigned_high_priority_actions = (
        _sort_actions(
            unassigned_high_priority_actions
        )
    )

    management_attention = (
        _build_management_attention(
            overdue_actions=overdue_actions,
            blocked_actions=blocked_actions,
            unassigned_high_priority_actions=(
                unassigned_high_priority_actions
            ),
            due_soon_actions=due_soon_actions,
        )
    )

    summary = {
        "total_actions": len(valid_actions),
        **status_counts,
        "active_actions": sum(
            status_counts[status]
            for status in active_statuses
        ),
        "overdue": len(
            overdue_actions
        ),
        "due_soon": len(
            due_soon_actions
        ),
        "unassigned_high_priority": len(
            unassigned_high_priority_actions
        ),
    }

    return {
        "status": "available",
        "reference_date": (
            reference_date.isoformat()
        ),
        "due_soon_days": due_soon_days,
        "summary": summary,
        "overdue_actions": overdue_actions,
        "due_soon_actions": due_soon_actions,
        "blocked_actions": blocked_actions,
        "unassigned_high_priority_actions": (
            unassigned_high_priority_actions
        ),
        "management_attention": (
            management_attention
        ),
        "controls": {
            "deterministic": True,
            "action_records_modified": False,
            "financial_recalculation_performed": False,
            "due_status_calculated_dynamically": True,
            "completed_actions_excluded_from_due_monitoring": (
                True
            ),
            "cancelled_actions_excluded_from_due_monitoring": (
                True
            ),
            "owner_not_invented": True,
            "due_date_not_invented": True,
        },
    }


def _parse_due_date(
    value: Any,
) -> date | None:
    """
    Parse an ISO action due date safely.

    Invalid or missing dates are ignored rather than invented.
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


def _sort_actions(
    actions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Sort management actions deterministically.

    Priority is considered first, followed by due date,
    title, and action ID.
    """

    priority_rank = {
        "Critical": 0,
        "High": 1,
        "Medium": 2,
        "Low": 3,
    }

    def sort_key(
        action: dict[str, Any],
    ) -> tuple[Any, ...]:

        priority = str(
            action.get(
                "priority",
                "Medium",
            )
            or "Medium"
        ).strip().title()

        due_date = _parse_due_date(
            action.get(
                "due_date"
            )
        )

        due_date_key = (
            due_date.isoformat()
            if due_date is not None
            else "9999-12-31"
        )

        title = str(
            action.get(
                "title",
                "",
            )
            or ""
        ).strip().lower()

        action_id = str(
            action.get(
                "action_id",
                "",
            )
            or ""
        )

        return (
            priority_rank.get(
                priority,
                99,
            ),
            due_date_key,
            title,
            action_id,
        )

    return sorted(
        actions,
        key=sort_key,
    )


def _build_management_attention(
    *,
    overdue_actions: list[dict[str, Any]],
    blocked_actions: list[dict[str, Any]],
    unassigned_high_priority_actions: list[
        dict[str, Any]
    ],
    due_soon_actions: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Build deterministic management-attention signals.

    Positive or lower-severity items never cancel more urgent
    execution issues.
    """

    attention: list[dict[str, Any]] = []

    if overdue_actions:
        attention.append(
            {
                "priority": "Critical",
                "type": "overdue_actions",
                "title": (
                    "Overdue management actions"
                ),
                "count": len(
                    overdue_actions
                ),
                "management_action": (
                    "Review overdue actions immediately, "
                    "confirm ownership, and reset execution "
                    "dates where necessary."
                ),
            }
        )

    if blocked_actions:
        attention.append(
            {
                "priority": "High",
                "type": "blocked_actions",
                "title": (
                    "Blocked management actions"
                ),
                "count": len(
                    blocked_actions
                ),
                "management_action": (
                    "Identify and resolve the blockers "
                    "preventing these actions from progressing."
                ),
            }
        )

    if unassigned_high_priority_actions:
        attention.append(
            {
                "priority": "High",
                "type": (
                    "unassigned_high_priority_actions"
                ),
                "title": (
                    "High-priority actions without owners"
                ),
                "count": len(
                    unassigned_high_priority_actions
                ),
                "management_action": (
                    "Assign accountable owners to all "
                    "unassigned Critical and High actions."
                ),
            }
        )

    if due_soon_actions:
        attention.append(
            {
                "priority": "Medium",
                "type": "due_soon_actions",
                "title": (
                    "Actions due soon"
                ),
                "count": len(
                    due_soon_actions
                ),
                "management_action": (
                    "Confirm that actions due soon remain "
                    "on track for completion."
                ),
            }
        )

    return attention