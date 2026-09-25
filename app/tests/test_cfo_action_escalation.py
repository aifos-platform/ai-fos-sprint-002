from copy import deepcopy

from app.services.cfo_action_escalation import (
    generate_cfo_action_escalation,
)


def _action(
    *,
    action_id: str,
    title: str,
    priority: str = "High",
    status: str = "open",
    owner: str | None = "Elie",
    due_date: str | None = None,
) -> dict:
    return {
        "action_id": action_id,
        "title": title,
        "priority": priority,
        "status": status,
        "owner": owner,
        "due_date": due_date,
    }


def _monitoring(
    *,
    overdue=None,
    due_soon=None,
    blocked=None,
    unassigned=None,
) -> dict:
    return {
        "status": "available",
        "reference_date": "2026-09-12",
        "due_soon_days": 7,
        "overdue_actions": (
            overdue
            or []
        ),
        "due_soon_actions": (
            due_soon
            or []
        ),
        "blocked_actions": (
            blocked
            or []
        ),
        "unassigned_high_priority_actions": (
            unassigned
            or []
        ),
    }


def test_empty_monitoring_returns_no_escalations():
    result = generate_cfo_action_escalation(
        _monitoring()
    )

    assert (
        result["status"]
        == "available"
    )

    assert (
        result["summary"][
            "total_escalations"
        ]
        == 0
    )

    assert (
        result["highest_escalation"]
        is None
    )

    assert (
        result["escalations"]
        == []
    )


def test_not_available_monitoring_is_safe():
    result = generate_cfo_action_escalation(
        {
            "status": "not_available",
        }
    )

    assert (
        result["status"]
        == "not_available"
    )

    assert (
        result["escalations"]
        == []
    )


def test_critical_priority_overdue_is_critical():
    action = _action(
        action_id="a1",
        title="Resolve liquidity issue",
        priority="Critical",
        due_date="2026-09-01",
    )

    result = generate_cfo_action_escalation(
        _monitoring(
            overdue=[
                action
            ],
        )
    )

    escalation = (
        result["escalations"][0]
    )

    assert (
        escalation["severity"]
        == "Critical"
    )

    assert (
        escalation[
            "management_attention"
        ]
        == "immediate_intervention"
    )

    assert (
        escalation["days_overdue"]
        == 11
    )


def test_overdue_and_blocked_is_critical():
    action = _action(
        action_id="a1",
        title="Submit donor report",
        priority="High",
        status="blocked",
        due_date="2026-09-05",
    )

    result = generate_cfo_action_escalation(
        _monitoring(
            overdue=[
                action
            ],
            blocked=[
                action
            ],
        )
    )

    escalation = (
        result["escalations"][0]
    )

    assert (
        escalation["severity"]
        == "Critical"
    )

    assert (
        "overdue"
        in escalation["signals"]
    )

    assert (
        "blocked"
        in escalation["signals"]
    )


def test_overdue_unassigned_high_is_critical():
    action = _action(
        action_id="a1",
        title="Funding gap mitigation",
        priority="High",
        owner=None,
        due_date="2026-09-01",
    )

    result = generate_cfo_action_escalation(
        _monitoring(
            overdue=[
                action
            ],
            unassigned=[
                action
            ],
        )
    )

    escalation = (
        result["escalations"][0]
    )

    assert (
        escalation["severity"]
        == "Critical"
    )

    assert (
        "unassigned_high_priority"
        in escalation["signals"]
    )


def test_normal_overdue_action_is_high():
    action = _action(
        action_id="a1",
        title="Budget review",
        priority="Medium",
        owner="Elie",
        due_date="2026-09-10",
    )

    result = generate_cfo_action_escalation(
        _monitoring(
            overdue=[
                action
            ],
        )
    )

    assert (
        result["escalations"][0][
            "severity"
        ]
        == "High"
    )


def test_high_priority_blocked_is_high():
    action = _action(
        action_id="a1",
        title="Grant closeout",
        priority="High",
        status="blocked",
        due_date="2026-10-01",
    )

    result = generate_cfo_action_escalation(
        _monitoring(
            blocked=[
                action
            ],
        )
    )

    assert (
        result["escalations"][0][
            "severity"
        ]
        == "High"
    )


def test_unassigned_high_priority_is_high():
    action = _action(
        action_id="a1",
        title="Funding pipeline review",
        priority="High",
        owner=None,
    )

    result = generate_cfo_action_escalation(
        _monitoring(
            unassigned=[
                action
            ],
        )
    )

    assert (
        result["escalations"][0][
            "severity"
        ]
        == "High"
    )


def test_due_soon_is_medium():
    action = _action(
        action_id="a1",
        title="Prepare management report",
        priority="Medium",
        due_date="2026-09-15",
    )

    result = generate_cfo_action_escalation(
        _monitoring(
            due_soon=[
                action
            ],
        )
    )

    assert (
        result["escalations"][0][
            "severity"
        ]
        == "Medium"
    )

    assert (
        result["escalations"][0][
            "management_attention"
        ]
        == "near_term_follow_up"
    )


def test_same_action_is_not_duplicated():
    action = _action(
        action_id="a1",
        title="Funding gap mitigation",
        priority="High",
        status="blocked",
        owner=None,
        due_date="2026-09-01",
    )

    result = generate_cfo_action_escalation(
        _monitoring(
            overdue=[
                action
            ],
            blocked=[
                action
            ],
            unassigned=[
                action
            ],
        )
    )

    assert (
        len(
            result["escalations"]
        )
        == 1
    )

    assert set(
        result["escalations"][0][
            "signals"
        ]
    ) == {
        "overdue",
        "blocked",
        "unassigned_high_priority",
    }


def test_critical_escalation_sorts_first():
    medium = _action(
        action_id="m1",
        title="Monthly report",
        priority="Medium",
        due_date="2026-09-15",
    )

    critical = _action(
        action_id="c1",
        title="Liquidity action",
        priority="Critical",
        due_date="2026-09-01",
    )

    result = generate_cfo_action_escalation(
        _monitoring(
            overdue=[
                critical
            ],
            due_soon=[
                medium
            ],
        )
    )

    assert (
        result["escalations"][0][
            "action_id"
        ]
        == "c1"
    )

    assert (
        result[
            "highest_escalation"
        ]
        == "Critical"
    )


def test_management_focus_is_limited_to_five():
    actions = [
        _action(
            action_id=f"a{i}",
            title=f"Action {i}",
            priority="High",
            due_date="2026-09-01",
        )
        for i in range(10)
    ]

    result = generate_cfo_action_escalation(
        _monitoring(
            overdue=actions
        )
    )

    assert (
        len(
            result[
                "management_focus"
            ]
        )
        == 5
    )


def test_summary_counts_severity_levels():
    critical = _action(
        action_id="c1",
        title="Critical action",
        priority="Critical",
        due_date="2026-09-01",
    )

    high = _action(
        action_id="h1",
        title="High action",
        priority="Medium",
        due_date="2026-09-01",
    )

    medium = _action(
        action_id="m1",
        title="Medium action",
        priority="Medium",
        due_date="2026-09-15",
    )

    result = generate_cfo_action_escalation(
        _monitoring(
            overdue=[
                critical,
                high,
            ],
            due_soon=[
                medium
            ],
        )
    )

    assert result["summary"] == {
        "total_escalations": 3,
        "critical": 1,
        "high": 1,
        "medium": 1,
    }


def test_source_action_is_not_modified():
    action = _action(
        action_id="a1",
        title="Funding gap review",
        priority="High",
        owner=None,
        due_date="2026-09-01",
    )

    original = deepcopy(
        action
    )

    generate_cfo_action_escalation(
        _monitoring(
            overdue=[
                action
            ],
            unassigned=[
                action
            ],
        )
    )

    assert action == original


def test_controls_protect_architecture():
    result = generate_cfo_action_escalation(
        _monitoring()
    )

    controls = result[
        "controls"
    ]

    assert (
        controls["deterministic"]
        is True
    )

    assert (
        controls[
            "source_is_action_monitoring"
        ]
        is True
    )

    assert (
        controls[
            "action_records_modified"
        ]
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
            "monitoring_recalculation_performed"
        ]
        is False
    )

    assert (
        controls[
            "owner_not_invented"
        ]
        is True
    )

    assert (
        controls[
            "due_date_not_invented"
        ]
        is True
    )

    assert (
        controls[
            "blocker_not_invented"
        ]
        is True
    )