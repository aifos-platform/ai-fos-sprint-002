from pathlib import Path

from app.services.cfo_action_history import (
    CFOActionHistoryService,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)


def test_create_action_records_history_event(
    tmp_path: Path,
) -> None:
    action = CFOActionPlanService.create_action(
        financial_model_folder=tmp_path,
        title="Review funding gap",
        description="Review projected funding gap.",
        priority="High",
        category="Funding",
        owner=None,
        due_date="2026-09-30",
    )

    events = CFOActionHistoryService.list_action_events(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert len(events) == 1

    event = events[0]

    assert (
        event["event_type"]
        == "action_created"
    )

    assert (
        event["action_id"]
        == action["action_id"]
    )

    assert (
        event["occurred_at"]
        == action["created_at"]
    )

    assert event["actor"] is None

    assert (
        event["new_value"]["title"]
        == "Review funding gap"
    )

    assert (
        event["new_value"]["priority"]
        == "High"
    )

    assert (
        event["new_value"]["due_date"]
        == "2026-09-30"
    )


def test_create_completed_action_history_matches_initial_state(
    tmp_path: Path,
) -> None:
    action = CFOActionPlanService.create_action(
        financial_model_folder=tmp_path,
        title="Close grant",
        description="Complete grant closeout.",
        status="completed",
        progress_percentage=25,
    )

    events = CFOActionHistoryService.list_action_events(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert len(events) == 1

    event = events[0]

    assert (
        event["new_value"]["status"]
        == "completed"
    )

    assert (
        event["new_value"][
            "progress_percentage"
        ]
        == 100
    )

    assert (
        action["completed_at"]
        == action["created_at"]
    )


def test_create_action_has_no_extra_history_events(
    tmp_path: Path,
) -> None:
    action = CFOActionPlanService.create_action(
        financial_model_folder=tmp_path,
        title="Budget review",
        description="Review budget position.",
    )

    events = CFOActionHistoryService.list_action_events(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert (
        [event["event_type"] for event in events]
        == ["action_created"]
    )