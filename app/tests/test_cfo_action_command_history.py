from pathlib import Path

import pytest

from app.services.cfo_action_command import (
    CFOActionCommandService,
)
from app.services.cfo_action_history import (
    CFOActionHistoryService,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)


def _create_action(
    tmp_path: Path,
    *,
    title: str,
) -> dict:
    return CFOActionPlanService.create_action(
        financial_model_folder=tmp_path,
        title=title,
        description=f"Action for {title}.",
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


def test_assign_command_creates_owner_history(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Funding gap review",
    )

    before_count = len(
        _events(
            tmp_path,
            action["action_id"],
        )
    )

    CFOActionCommandService.assign(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
        owner="Elie",
    )

    new_events = _events(
        tmp_path,
        action["action_id"],
    )[before_count:]

    assert len(new_events) == 1
    assert (
        new_events[0]["event_type"]
        == "owner_changed"
    )
    assert (
        new_events[0]["previous_value"]
        is None
    )
    assert (
        new_events[0]["new_value"]
        == "Elie"
    )


def test_set_due_date_command_creates_history(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Funding gap review",
    )

    before_count = len(
        _events(
            tmp_path,
            action["action_id"],
        )
    )

    CFOActionCommandService.set_due_date(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
        due_date="2026-09-30",
    )

    new_events = _events(
        tmp_path,
        action["action_id"],
    )[before_count:]

    assert len(new_events) == 1
    assert (
        new_events[0]["event_type"]
        == "due_date_changed"
    )


def test_complete_command_creates_status_and_progress_history(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Funding gap review",
    )

    before_count = len(
        _events(
            tmp_path,
            action["action_id"],
        )
    )

    CFOActionCommandService.complete(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
    )

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


def test_ambiguous_command_creates_no_history(
    tmp_path: Path,
) -> None:
    action_1 = _create_action(
        tmp_path,
        title="Current funding gap review",
    )

    action_2 = _create_action(
        tmp_path,
        title="Future funding gap review",
    )

    before_1 = _events(
        tmp_path,
        action_1["action_id"],
    )

    before_2 = _events(
        tmp_path,
        action_2["action_id"],
    )

    with pytest.raises(
        ValueError,
        match="Multiple CFO actions match",
    ):
        CFOActionCommandService.assign(
            financial_model_folder=tmp_path,
            action_reference="funding gap",
            owner="Elie",
        )

    after_1 = _events(
        tmp_path,
        action_1["action_id"],
    )

    after_2 = _events(
        tmp_path,
        action_2["action_id"],
    )

    assert before_1 == after_1
    assert before_2 == after_2


def test_unknown_action_command_creates_no_history(
    tmp_path: Path,
) -> None:
    assert (
        CFOActionHistoryService.list_events(
            tmp_path
        )
        == []
    )

    with pytest.raises(
        ValueError,
        match="No CFO action matches the reference",
    ):
        CFOActionCommandService.assign(
            financial_model_folder=tmp_path,
            action_reference="cash runway",
            owner="Elie",
        )

    assert (
        CFOActionHistoryService.list_events(
            tmp_path
        )
        == []
    )