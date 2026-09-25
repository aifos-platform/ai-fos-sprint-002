from copy import deepcopy
from datetime import date

import pytest

from app.services.cfo_action_monitoring import (
    generate_cfo_action_monitoring,
)


REFERENCE_DATE = date(
    2026,
    9,
    12,
)


def _action(
    *,
    action_id: str,
    title: str,
    priority: str = "Medium",
    status: str = "open",
    owner: str | None = None,
    due_date: str | None = None,
):
    return {
        "action_id": action_id,
        "title": title,
        "description": (
            f"Management action for {title}."
        ),
        "priority": priority,
        "category": "Financial Management",
        "owner": owner,
        "due_date": due_date,
        "status": status,
        "progress_percentage": 0,
    }


def test_empty_action_plan_is_available():
    result = generate_cfo_action_monitoring(
        [],
        reference_date=REFERENCE_DATE,
    )

    assert (
        result["status"]
        == "available"
    )

    assert (
        result["summary"]["total_actions"]
        == 0
    )

    assert (
        result["summary"]["active_actions"]
        == 0
    )

    assert (
        result["management_attention"]
        == []
    )


def test_status_counts_are_calculated():
    actions = [
        _action(
            action_id="1",
            title="Open",
            status="open",
        ),
        _action(
            action_id="2",
            title="In progress",
            status="in_progress",
        ),
        _action(
            action_id="3",
            title="Blocked",
            status="blocked",
        ),
        _action(
            action_id="4",
            title="Completed",
            status="completed",
        ),
        _action(
            action_id="5",
            title="Cancelled",
            status="cancelled",
        ),
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
    )

    summary = result["summary"]

    assert summary["total_actions"] == 5
    assert summary["open"] == 1
    assert summary["in_progress"] == 1
    assert summary["blocked"] == 1
    assert summary["completed"] == 1
    assert summary["cancelled"] == 1
    assert summary["active_actions"] == 3


def test_overdue_action_is_detected():
    actions = [
        _action(
            action_id="1",
            title="Submit funding proposal",
            priority="High",
            status="in_progress",
            owner="Executive Director",
            due_date="2026-09-10",
        )
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
    )

    assert (
        result["summary"]["overdue"]
        == 1
    )

    assert (
        result["overdue_actions"][0]["action_id"]
        == "1"
    )


def test_action_due_today_is_due_soon_not_overdue():
    actions = [
        _action(
            action_id="1",
            title="Review liquidity",
            due_date="2026-09-12",
        )
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
    )

    assert (
        result["summary"]["overdue"]
        == 0
    )

    assert (
        result["summary"]["due_soon"]
        == 1
    )


def test_action_due_within_seven_days_is_due_soon():
    actions = [
        _action(
            action_id="1",
            title="Prepare Board update",
            due_date="2026-09-19",
        )
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
        due_soon_days=7,
    )

    assert (
        result["summary"]["due_soon"]
        == 1
    )


def test_action_beyond_due_soon_window_is_not_due_soon():
    actions = [
        _action(
            action_id="1",
            title="Prepare annual plan",
            due_date="2026-09-20",
        )
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
        due_soon_days=7,
    )

    assert (
        result["summary"]["due_soon"]
        == 0
    )


def test_completed_action_is_not_overdue():
    actions = [
        _action(
            action_id="1",
            title="Completed action",
            status="completed",
            due_date="2026-09-01",
        )
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
    )

    assert (
        result["summary"]["overdue"]
        == 0
    )

    assert (
        result["overdue_actions"]
        == []
    )


def test_cancelled_action_is_not_overdue():
    actions = [
        _action(
            action_id="1",
            title="Cancelled action",
            status="cancelled",
            due_date="2026-09-01",
        )
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
    )

    assert (
        result["summary"]["overdue"]
        == 0
    )


def test_blocked_action_is_identified():
    actions = [
        _action(
            action_id="1",
            title="Blocked proposal",
            status="blocked",
        )
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
    )

    assert (
        len(result["blocked_actions"])
        == 1
    )

    assert (
        result["blocked_actions"][0]["action_id"]
        == "1"
    )


def test_unassigned_critical_action_is_identified():
    actions = [
        _action(
            action_id="1",
            title="Protect liquidity",
            priority="Critical",
            status="open",
            owner=None,
        )
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
    )

    assert (
        result["summary"][
            "unassigned_high_priority"
        ]
        == 1
    )

    assert (
        result[
            "unassigned_high_priority_actions"
        ][0]["action_id"]
        == "1"
    )


def test_unassigned_high_action_is_identified():
    actions = [
        _action(
            action_id="1",
            title="Close funding gap",
            priority="High",
            status="in_progress",
            owner="",
        )
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
    )

    assert (
        result["summary"][
            "unassigned_high_priority"
        ]
        == 1
    )


def test_completed_unassigned_high_action_is_not_flagged():
    actions = [
        _action(
            action_id="1",
            title="Completed funding action",
            priority="High",
            status="completed",
            owner=None,
        )
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
    )

    assert (
        result["summary"][
            "unassigned_high_priority"
        ]
        == 0
    )


def test_management_attention_prioritizes_overdue_first():
    actions = [
        _action(
            action_id="1",
            title="Overdue",
            priority="High",
            status="in_progress",
            owner="Director",
            due_date="2026-09-01",
        ),
        _action(
            action_id="2",
            title="Blocked",
            priority="Medium",
            status="blocked",
            owner="Finance",
        ),
        _action(
            action_id="3",
            title="Unassigned",
            priority="Critical",
            status="open",
            owner=None,
        ),
        _action(
            action_id="4",
            title="Due soon",
            priority="Medium",
            status="open",
            owner="Finance",
            due_date="2026-09-15",
        ),
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
    )

    types = [
        item["type"]
        for item in result[
            "management_attention"
        ]
    ]

    assert types == [
        "overdue_actions",
        "blocked_actions",
        "unassigned_high_priority_actions",
        "due_soon_actions",
    ]


def test_source_actions_are_not_modified():
    actions = [
        _action(
            action_id="1",
            title="Funding action",
            priority="High",
            due_date="2026-09-01",
        )
    ]

    original = deepcopy(
        actions
    )

    generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
    )

    assert actions == original


def test_invalid_due_date_is_not_invented_or_flagged():
    actions = [
        _action(
            action_id="1",
            title="Invalid date",
            due_date="not-a-date",
        )
    ]

    result = generate_cfo_action_monitoring(
        actions,
        reference_date=REFERENCE_DATE,
    )

    assert (
        result["summary"]["overdue"]
        == 0
    )

    assert (
        result["summary"]["due_soon"]
        == 0
    )


def test_negative_due_soon_window_is_rejected():
    with pytest.raises(
        ValueError,
        match="zero or greater",
    ):
        generate_cfo_action_monitoring(
            [],
            reference_date=REFERENCE_DATE,
            due_soon_days=-1,
        )


def test_controls_protect_architecture():
    result = generate_cfo_action_monitoring(
        [],
        reference_date=REFERENCE_DATE,
    )

    controls = result["controls"]

    assert (
        controls["deterministic"]
        is True
    )

    assert (
        controls["action_records_modified"]
        is False
    )

    assert (
        controls[
            "financial_recalculation_performed"
        ]
        is False
    )

    assert (
        controls[
            "due_status_calculated_dynamically"
        ]
        is True
    )

    assert (
        controls["owner_not_invented"]
        is True
    )

    assert (
        controls["due_date_not_invented"]
        is True
    )