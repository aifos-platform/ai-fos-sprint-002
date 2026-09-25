from pathlib import Path

import pytest

from app.services.cfo_action_history import (
    CFOActionHistoryService,
)
from app.services.financial_model_service import (
    FinancialModelService,
)


def test_empty_history_is_safe(
    tmp_path: Path,
) -> None:
    assert (
        CFOActionHistoryService.list_events(
            tmp_path
        )
        == []
    )


def test_record_action_created_event(
    tmp_path: Path,
) -> None:
    event = CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="action_created",
        new_value={
            "title": "Review funding gap",
            "priority": "High",
        },
    )

    assert event["action_id"] == "action-1"
    assert (
        event["event_type"]
        == "action_created"
    )
    assert event["event_id"]
    assert event["occurred_at"]

    persisted = (
        CFOActionHistoryService.list_events(
            tmp_path
        )
    )

    assert len(persisted) == 1
    assert (
        persisted[0]["event_id"]
        == event["event_id"]
    )


def test_record_field_change_event(
    tmp_path: Path,
) -> None:
    event = CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="owner_changed",
        field="owner",
        previous_value=None,
        new_value="Elie",
    )

    assert event["field"] == "owner"
    assert event["previous_value"] is None
    assert event["new_value"] == "Elie"


def test_multiple_events_are_appended(
    tmp_path: Path,
) -> None:
    first = CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="owner_changed",
        field="owner",
        previous_value=None,
        new_value="Elie",
        occurred_at=(
            "2026-09-13T08:00:00+00:00"
        ),
    )

    second = CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="progress_changed",
        field="progress_percentage",
        previous_value=0,
        new_value=50,
        occurred_at=(
            "2026-09-13T09:00:00+00:00"
        ),
    )

    events = (
        CFOActionHistoryService.list_events(
            tmp_path
        )
    )

    assert len(events) == 2
    assert events[0]["event_id"] == first["event_id"]
    assert events[1]["event_id"] == second["event_id"]


def test_list_action_events_filters_other_actions(
    tmp_path: Path,
) -> None:
    CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="owner_changed",
        field="owner",
        new_value="Elie",
    )

    CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-2",
        event_type="owner_changed",
        field="owner",
        new_value="Wassim",
    )

    events = (
        CFOActionHistoryService.list_action_events(
            financial_model_folder=tmp_path,
            action_id="action-1",
        )
    )

    assert len(events) == 1
    assert (
        events[0]["action_id"]
        == "action-1"
    )


def test_action_events_are_sorted_chronologically(
    tmp_path: Path,
) -> None:
    CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="progress_changed",
        field="progress_percentage",
        previous_value=50,
        new_value=75,
        occurred_at=(
            "2026-09-13T10:00:00+00:00"
        ),
    )

    CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="progress_changed",
        field="progress_percentage",
        previous_value=0,
        new_value=50,
        occurred_at=(
            "2026-09-13T09:00:00+00:00"
        ),
    )

    events = (
        CFOActionHistoryService.list_action_events(
            financial_model_folder=tmp_path,
            action_id="action-1",
        )
    )

    assert (
        events[0]["new_value"]
        == 50
    )

    assert (
        events[1]["new_value"]
        == 75
    )


def test_actor_is_optional_and_never_invented(
    tmp_path: Path,
) -> None:
    event = CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="status_changed",
        field="status",
        previous_value="open",
        new_value="in_progress",
    )

    assert event["actor"] is None


def test_explicit_actor_is_preserved(
    tmp_path: Path,
) -> None:
    event = CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="status_changed",
        field="status",
        previous_value="open",
        new_value="in_progress",
        actor="Elie",
    )

    assert event["actor"] == "Elie"


def test_metadata_is_preserved(
    tmp_path: Path,
) -> None:
    event = CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="due_date_changed",
        field="due_date",
        previous_value="2026-09-20",
        new_value="2026-09-30",
        metadata={
            "source": "ask_cfo",
        },
    )

    assert event["metadata"] == {
        "source": "ask_cfo",
    }


def test_invalid_event_type_is_rejected_without_persistence(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "Invalid CFO action history event type"
        ),
    ):
        CFOActionHistoryService.record_event(
            financial_model_folder=tmp_path,
            action_id="action-1",
            event_type="unknown_event",
        )

    assert (
        CFOActionHistoryService.list_events(
            tmp_path
        )
        == []
    )


def test_empty_action_id_is_rejected(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="Action ID is required",
    ):
        CFOActionHistoryService.record_event(
            financial_model_folder=tmp_path,
            action_id="",
            event_type="action_created",
        )


def test_invalid_timestamp_is_rejected_without_persistence(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match=(
            "History event timestamp must be ISO format"
        ),
    ):
        CFOActionHistoryService.record_event(
            financial_model_folder=tmp_path,
            action_id="action-1",
            event_type="action_created",
            occurred_at="yesterday",
        )

    assert (
        CFOActionHistoryService.list_events(
            tmp_path
        )
        == []
    )


def test_naive_timestamp_is_normalized_to_timezone_aware_iso(
    tmp_path: Path,
) -> None:
    event = CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="action_created",
        occurred_at="2026-09-13T10:30:00",
    )

    assert (
        event["occurred_at"]
        == "2026-09-13T10:30:00+00:00"
    )


def test_existing_event_is_not_changed_when_new_event_is_added(
    tmp_path: Path,
) -> None:
    first = CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="owner_changed",
        field="owner",
        previous_value=None,
        new_value="Elie",
    )

    original_first = dict(
        first
    )

    CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="progress_changed",
        field="progress_percentage",
        previous_value=0,
        new_value=25,
    )

    events = (
        CFOActionHistoryService.list_events(
            tmp_path
        )
    )

    assert events[0] == original_first


def test_history_does_not_create_action_plan_file(
    tmp_path: Path,
) -> None:
    CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="action_created",
    )

    action_plan = (
        FinancialModelService.load_json(
            tmp_path,
            "cfo_action_plan.json",
        )
    )

    assert action_plan is None

def test_source_is_optional_and_never_invented(
    tmp_path: Path,
) -> None:
    event = CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="status_changed",
        field="status",
        previous_value="open",
        new_value="in_progress",
    )

    assert event["source"] is None


def test_explicit_source_is_preserved(
    tmp_path: Path,
) -> None:
    event = CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="status_changed",
        field="status",
        previous_value="open",
        new_value="in_progress",
        source="ask_cfo",
    )

    assert event["source"] == "ask_cfo"


def test_actor_and_source_are_independent(
    tmp_path: Path,
) -> None:
    event = CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="action-1",
        event_type="owner_changed",
        field="owner",
        previous_value=None,
        new_value="Wassim",
        actor="Elie",
        source="user_interface",
    )

    assert event["actor"] == "Elie"
    assert event["source"] == "user_interface"    