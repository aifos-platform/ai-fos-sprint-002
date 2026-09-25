from pathlib import Path

import pytest

from app.services.cfo_action_history import (
    CFOActionHistoryService,
)
from app.services.cfo_action_lifecycle import (
    CFOActionLifecycleService,
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


def _new_events(
    tmp_path: Path,
    action_id: str,
    before_count: int,
) -> list[dict]:
    return _events(
        tmp_path,
        action_id,
    )[before_count:]


def test_assign_owner_creates_owner_history(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    before_count = len(
        _events(tmp_path, action["action_id"])
    )

    CFOActionLifecycleService.assign_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        owner="Elie",
    )

    events = _new_events(
        tmp_path,
        action["action_id"],
        before_count,
    )

    assert len(events) == 1
    assert events[0]["event_type"] == "owner_changed"
    assert events[0]["previous_value"] is None
    assert events[0]["new_value"] == "Elie"


def test_set_due_date_creates_due_date_history(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    before_count = len(
        _events(tmp_path, action["action_id"])
    )

    CFOActionLifecycleService.set_due_date(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        due_date="2026-09-30",
    )

    events = _new_events(
        tmp_path,
        action["action_id"],
        before_count,
    )

    assert len(events) == 1
    assert events[0]["event_type"] == "due_date_changed"
    assert events[0]["previous_value"] is None
    assert events[0]["new_value"] == "2026-09-30"


def test_start_action_creates_status_history(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    before_count = len(
        _events(tmp_path, action["action_id"])
    )

    CFOActionLifecycleService.start_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    events = _new_events(
        tmp_path,
        action["action_id"],
        before_count,
    )

    assert len(events) == 1
    assert events[0]["event_type"] == "status_changed"
    assert events[0]["previous_value"] == "open"
    assert events[0]["new_value"] == "in_progress"


def test_block_and_unblock_create_status_history(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionLifecycleService.start_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    before_count = len(
        _events(tmp_path, action["action_id"])
    )

    CFOActionLifecycleService.block_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    CFOActionLifecycleService.unblock_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    events = _new_events(
        tmp_path,
        action["action_id"],
        before_count,
    )

    status_events = [
        event
        for event in events
        if event["event_type"] == "status_changed"
    ]

    assert len(status_events) == 2

    assert status_events[0]["previous_value"] == "in_progress"
    assert status_events[0]["new_value"] == "blocked"

    assert status_events[1]["previous_value"] == "blocked"
    assert status_events[1]["new_value"] == "in_progress"


def test_progress_update_creates_progress_history(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    before_count = len(
        _events(tmp_path, action["action_id"])
    )

    CFOActionLifecycleService.update_progress(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        progress_percentage=60,
    )

    events = _new_events(
        tmp_path,
        action["action_id"],
        before_count,
    )

    assert len(events) == 1
    assert events[0]["event_type"] == "progress_changed"
    assert events[0]["previous_value"] == 0
    assert events[0]["new_value"] == 60


def test_complete_action_creates_status_and_progress_history(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionLifecycleService.update_progress(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        progress_percentage=50,
    )

    before_count = len(
        _events(tmp_path, action["action_id"])
    )

    CFOActionLifecycleService.complete_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    events = _new_events(
        tmp_path,
        action["action_id"],
        before_count,
    )

    assert {
        event["event_type"]
        for event in events
    } == {
        "status_changed",
        "progress_changed",
    }

    current = CFOActionPlanService.get_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert current is not None
    assert current["status"] == "completed"
    assert current["progress_percentage"] == 100


def test_reopen_action_creates_status_history(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionLifecycleService.complete_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    before_count = len(
        _events(tmp_path, action["action_id"])
    )

    CFOActionLifecycleService.reopen_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    events = _new_events(
        tmp_path,
        action["action_id"],
        before_count,
    )

    assert len(events) == 1
    assert events[0]["event_type"] == "status_changed"
    assert events[0]["previous_value"] == "completed"
    assert events[0]["new_value"] == "open"


def test_failed_lifecycle_validation_creates_no_history(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    before_action = CFOActionPlanService.get_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    before_events = _events(
        tmp_path,
        action["action_id"],
    )

    with pytest.raises(ValueError):
        CFOActionLifecycleService.set_due_date(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
            due_date="not-a-date",
        )

    after_action = CFOActionPlanService.get_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    after_events = _events(
        tmp_path,
        action["action_id"],
    )

    assert before_action == after_action
    assert before_events == after_events

def test_lifecycle_preserves_history_source(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    before_count = len(
        _events(
            tmp_path,
            action["action_id"],
        )
    )

    CFOActionLifecycleService.assign_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        owner="Wassim",
        history_source="ask_cfo",
    )

    new_events = _events(
        tmp_path,
        action["action_id"],
    )[before_count:]

    assert len(new_events) == 1
    assert new_events[0]["event_type"] == "owner_changed"
    assert new_events[0]["source"] == "ask_cfo"
    assert new_events[0]["actor"] is None


def test_lifecycle_preserves_history_actor_and_source(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    before_count = len(
        _events(
            tmp_path,
            action["action_id"],
        )
    )

    CFOActionLifecycleService.set_due_date(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        due_date="2026-09-30",
        history_actor="Elie",
        history_source="user_interface",
    )

    new_events = _events(
        tmp_path,
        action["action_id"],
    )[before_count:]

    assert len(new_events) == 1
    assert new_events[0]["event_type"] == "due_date_changed"
    assert new_events[0]["actor"] == "Elie"
    assert new_events[0]["source"] == "user_interface"


def test_failed_lifecycle_change_writes_no_provenance_event(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    before_events = _events(
        tmp_path,
        action["action_id"],
    )

    with pytest.raises(ValueError):
        CFOActionLifecycleService.set_due_date(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
            due_date="not-a-date",
            history_actor="Elie",
            history_source="ask_cfo",
        )

    after_events = _events(
        tmp_path,
        action["action_id"],
    )

    assert before_events == after_events