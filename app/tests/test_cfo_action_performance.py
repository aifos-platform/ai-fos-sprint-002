from copy import deepcopy

from app.services.cfo_action_performance import (
    generate_cfo_action_performance,
)


def _event(
    *,
    event_id: str,
    action_id: str,
    event_type: str,
    previous_value=None,
    new_value=None,
    actor=None,
    source=None,
    occurred_at: str = "2026-09-01T10:00:00+00:00",
):
    return {
        "event_id": event_id,
        "action_id": action_id,
        "event_type": event_type,
        "field": None,
        "previous_value": previous_value,
        "new_value": new_value,
        "actor": actor,
        "source": source,
        "metadata": {},
        "occurred_at": occurred_at,
    }


def test_empty_history_is_available():
    result = (
        generate_cfo_action_performance(
            []
        )
    )

    assert result["status"] == "available"

    assert (
        result["summary"]["total_events"]
        == 0
    )

    assert (
        result["summary"]["action_count"]
        == 0
    )

    assert (
        result["management_patterns"]
        == []
    )


def test_history_input_is_not_modified():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="action_created",
        )
    ]

    before = deepcopy(
        events
    )

    generate_cfo_action_performance(
        events
    )

    assert events == before


def test_counts_distinct_actions():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="action_created",
        ),
        _event(
            event_id="2",
            action_id="A1",
            event_type="owner_changed",
        ),
        _event(
            event_id="3",
            action_id="A2",
            event_type="action_created",
        ),
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    assert (
        result["summary"]["total_events"]
        == 3
    )

    assert (
        result["summary"]["action_count"]
        == 2
    )


def test_completion_is_detected():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="status_changed",
            previous_value="in_progress",
            new_value="completed",
        )
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    assert (
        result["summary"][
            "completed_action_count"
        ]
        == 1
    )


def test_reopen_is_detected_only_after_completion():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="status_changed",
            previous_value="in_progress",
            new_value="completed",
        ),
        _event(
            event_id="2",
            action_id="A1",
            event_type="status_changed",
            previous_value="completed",
            new_value="open",
        ),
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    assert (
        result["summary"][
            "reopened_action_count"
        ]
        == 1
    )

    assert (
        result["summary"][
            "completion_reopen_rate_percentage"
        ]
        == 100.0
    )


def test_open_status_without_completed_previous_is_not_reopen():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="status_changed",
            previous_value="blocked",
            new_value="open",
        )
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    assert (
        result["summary"][
            "reopened_action_count"
        ]
        == 0
    )


def test_blocked_action_is_detected():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="status_changed",
            previous_value="in_progress",
            new_value="blocked",
        )
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    assert (
        result["summary"][
            "blocked_action_count"
        ]
        == 1
    )


def test_repeated_blocking_creates_high_pattern():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="status_changed",
            previous_value="in_progress",
            new_value="blocked",
        ),
        _event(
            event_id="2",
            action_id="A1",
            event_type="status_changed",
            previous_value="in_progress",
            new_value="blocked",
        ),
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    assert (
        result["summary"][
            "actions_with_repeated_blocks"
        ]
        == 1
    )

    patterns = result[
        "management_patterns"
    ]

    assert any(
        pattern["pattern"]
        == "repeated_blocking"
        and pattern["severity"]
        == "High"
        for pattern in patterns
    )


def test_multiple_owner_changes_are_detected():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="owner_changed",
            previous_value=None,
            new_value="Elie",
        ),
        _event(
            event_id="2",
            action_id="A1",
            event_type="owner_changed",
            previous_value="Elie",
            new_value="Wassim",
        ),
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    assert (
        result["summary"][
            "actions_with_multiple_owner_changes"
        ]
        == 1
    )


def test_multiple_due_date_changes_are_detected():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="due_date_changed",
            previous_value=None,
            new_value="2026-09-15",
        ),
        _event(
            event_id="2",
            action_id="A1",
            event_type="due_date_changed",
            previous_value="2026-09-15",
            new_value="2026-09-30",
        ),
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    assert (
        result["summary"][
            "actions_with_multiple_due_date_changes"
        ]
        == 1
    )


def test_progress_updates_are_counted():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="progress_changed",
            previous_value=0,
            new_value=25,
        ),
        _event(
            event_id="2",
            action_id="A1",
            event_type="progress_changed",
            previous_value=25,
            new_value=60,
        ),
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    record = (
        result[
            "action_performance"
        ][0]
    )

    assert (
        record[
            "progress_update_count"
        ]
        == 2
    )


def test_known_source_is_preserved():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="owner_changed",
            source="ask_cfo",
        )
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    assert (
        result[
            "source_activity"
        ][
            "known_sources"
        ][
            "ask_cfo"
        ]
        == 1
    )

    assert (
        result[
            "source_activity"
        ][
            "unknown_source_events"
        ]
        == 0
    )


def test_missing_source_is_not_invented():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="owner_changed",
            source=None,
        )
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    assert (
        result[
            "source_activity"
        ][
            "known_sources"
        ]
        == {}
    )

    assert (
        result[
            "source_activity"
        ][
            "unknown_source_events"
        ]
        == 1
    )


def test_known_actor_is_preserved():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="owner_changed",
            actor="Elie",
        )
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    assert (
        result[
            "actor_activity"
        ][
            "known_actors"
        ][
            "Elie"
        ]
        == 1
    )


def test_missing_actor_is_not_invented():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="owner_changed",
            actor=None,
        )
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    assert (
        result[
            "actor_activity"
        ][
            "known_actors"
        ]
        == {}
    )

    assert (
        result[
            "actor_activity"
        ][
            "unknown_actor_events"
        ]
        == 1
    )


def test_action_performance_tracks_last_event_time():
    events = [
        _event(
            event_id="1",
            action_id="A1",
            event_type="action_created",
            occurred_at=(
                "2026-09-01T10:00:00+00:00"
            ),
        ),
        _event(
            event_id="2",
            action_id="A1",
            event_type="owner_changed",
            occurred_at=(
                "2026-09-03T10:00:00+00:00"
            ),
        ),
    ]

    result = (
        generate_cfo_action_performance(
            events
        )
    )

    record = (
        result[
            "action_performance"
        ][0]
    )

    assert (
        record["last_event_at"]
        == "2026-09-03T10:00:00+00:00"
    )


def test_controls_protect_read_only_architecture():
    result = (
        generate_cfo_action_performance(
            []
        )
    )

    controls = result[
        "controls"
    ]

    assert controls["deterministic"] is True
    assert controls["read_only"] is True

    assert (
        controls[
            "action_records_modified"
        ]
        is False
    )

    assert (
        controls[
            "history_records_modified"
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
            "current_action_state_not_inferred"
        ]
        is True
    )

    assert (
        controls[
            "missing_actor_not_invented"
        ]
        is True
    )

    assert (
        controls[
            "missing_source_not_invented"
        ]
        is True
    )