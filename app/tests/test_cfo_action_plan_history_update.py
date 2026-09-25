from pathlib import Path

import pytest

from app.services.cfo_action_history import (
    CFOActionHistoryService,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)


def _create_action(
    tmp_path: Path,
) -> dict:
    return CFOActionPlanService.create_action(
        financial_model_folder=tmp_path,
        title="Funding gap review",
        description="Review the funding gap.",
        priority="High",
    )


def _events(
    tmp_path: Path,
    action_id: str,
) -> list[dict]:
    return CFOActionHistoryService.list_action_events(
        financial_model_folder=tmp_path,
        action_id=action_id,
    )


def test_owner_change_is_recorded(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        owner="Elie",
    )

    events = _events(
        tmp_path,
        action["action_id"],
    )

    owner_events = [
        event
        for event in events
        if event["event_type"] == "owner_changed"
    ]

    assert len(owner_events) == 1
    assert owner_events[0]["field"] == "owner"
    assert owner_events[0]["previous_value"] is None
    assert owner_events[0]["new_value"] == "Elie"


def test_due_date_change_is_recorded(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        due_date="2026-09-30",
    )

    events = _events(
        tmp_path,
        action["action_id"],
    )

    due_events = [
        event
        for event in events
        if event["event_type"] == "due_date_changed"
    ]

    assert len(due_events) == 1
    assert due_events[0]["field"] == "due_date"
    assert due_events[0]["previous_value"] is None
    assert due_events[0]["new_value"] == "2026-09-30"


def test_progress_change_is_recorded(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        progress_percentage=60,
    )

    events = _events(
        tmp_path,
        action["action_id"],
    )

    progress_events = [
        event
        for event in events
        if event["event_type"] == "progress_changed"
    ]

    assert len(progress_events) == 1
    assert progress_events[0]["previous_value"] == 0
    assert progress_events[0]["new_value"] == 60


def test_status_change_is_recorded(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        status="in_progress",
    )

    events = _events(
        tmp_path,
        action["action_id"],
    )

    status_events = [
        event
        for event in events
        if event["event_type"] == "status_changed"
    ]

    assert len(status_events) == 1
    assert status_events[0]["previous_value"] == "open"
    assert status_events[0]["new_value"] == "in_progress"


def test_completion_records_status_and_progress(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        progress_percentage=40,
    )

    before_count = len(
        _events(
            tmp_path,
            action["action_id"],
        )
    )

    updated = CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        status="completed",
    )

    assert updated is not None
    assert updated["status"] == "completed"
    assert updated["progress_percentage"] == 100
    assert updated["completed_at"] is not None

    new_events = _events(
        tmp_path,
        action["action_id"],
    )[before_count:]

    assert {
        event["event_type"]
        for event in new_events
    } == {
        "status_changed",
        "progress_changed",
    }


def test_reopening_records_status_change(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        status="completed",
    )

    before_count = len(
        _events(
            tmp_path,
            action["action_id"],
        )
    )

    updated = CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        status="in_progress",
    )

    assert updated is not None
    assert updated["status"] == "in_progress"
    assert updated["completed_at"] is None

    new_events = _events(
        tmp_path,
        action["action_id"],
    )[before_count:]

    assert len(new_events) == 1
    assert new_events[0]["event_type"] == "status_changed"
    assert new_events[0]["previous_value"] == "completed"
    assert new_events[0]["new_value"] == "in_progress"


def test_multiple_changes_create_separate_events(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    before_count = len(
        _events(
            tmp_path,
            action["action_id"],
        )
    )

    CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        owner="Elie",
        due_date="2026-09-30",
        progress_percentage=50,
    )

    new_events = _events(
        tmp_path,
        action["action_id"],
    )[before_count:]

    assert len(new_events) == 3

    assert {
        event["event_type"]
        for event in new_events
    } == {
        "owner_changed",
        "due_date_changed",
        "progress_changed",
    }


def test_no_op_update_creates_no_history_event(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        owner="Elie",
    )

    before = _events(
        tmp_path,
        action["action_id"],
    )

    CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        owner="Elie",
    )

    after = _events(
        tmp_path,
        action["action_id"],
    )

    assert before == after


def test_failed_validation_creates_no_history_event(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    before_action = (
        CFOActionPlanService.get_action(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
        )
    )

    before_events = _events(
        tmp_path,
        action["action_id"],
    )

    with pytest.raises(ValueError):
        CFOActionPlanService.update_action(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
            owner="Elie",
            due_date="not-a-date",
        )

    after_action = (
        CFOActionPlanService.get_action(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
        )
    )

    after_events = _events(
        tmp_path,
        action["action_id"],
    )

    assert before_action == after_action
    assert before_events == after_events


def test_unknown_action_creates_no_history(
    tmp_path: Path,
) -> None:
    result = CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id="does-not-exist",
        owner="Elie",
    )

    assert result is None

    assert (
        CFOActionHistoryService.list_events(
            financial_model_folder=tmp_path,
        )
        == []
    )