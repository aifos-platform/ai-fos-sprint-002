from pathlib import Path

import pytest

from app.services.cfo_action_lifecycle import (
    CFOActionLifecycleService,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)


# ==================================================
# HELPERS
# ==================================================


def _create_action(
    folder: Path,
) -> dict:
    return CFOActionPlanService.create_action(
        financial_model_folder=folder,
        title="Review funding gap",
        description="Review the projected funding gap.",
        priority="High",
        category="Funding",
    )


# ==================================================
# OWNER
# ==================================================


def test_assign_action_sets_explicit_owner(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    updated = CFOActionLifecycleService.assign_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        owner="Elie",
    )

    assert updated["owner"] == "Elie"

    persisted = CFOActionPlanService.get_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert persisted is not None
    assert persisted["owner"] == "Elie"


def test_assign_action_rejects_empty_owner(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    with pytest.raises(
        ValueError,
        match="Action owner is required",
    ):
        CFOActionLifecycleService.assign_action(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
            owner="",
        )

    persisted = CFOActionPlanService.get_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert persisted is not None
    assert persisted["owner"] is None


def test_unassign_action_clears_owner(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionLifecycleService.assign_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        owner="Elie",
    )

    updated = CFOActionLifecycleService.unassign_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert updated["owner"] is None


# ==================================================
# DUE DATE
# ==================================================


def test_set_due_date(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    updated = CFOActionLifecycleService.set_due_date(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        due_date="2026-09-30",
    )

    assert updated["due_date"] == "2026-09-30"


def test_invalid_due_date_does_not_mutate_action(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    with pytest.raises(
        ValueError,
        match="Due date must use YYYY-MM-DD format",
    ):
        CFOActionLifecycleService.set_due_date(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
            due_date="September 30",
        )

    persisted = CFOActionPlanService.get_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert persisted is not None
    assert persisted["due_date"] is None


def test_clear_due_date(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionLifecycleService.set_due_date(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        due_date="2026-09-30",
    )

    updated = CFOActionLifecycleService.clear_due_date(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert updated["due_date"] is None


# ==================================================
# START / PROGRESS
# ==================================================


def test_start_action_moves_open_to_in_progress(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    updated = CFOActionLifecycleService.start_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert updated["status"] == "in_progress"


def test_update_progress_persists_percentage(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionLifecycleService.start_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    updated = CFOActionLifecycleService.update_progress(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        progress_percentage=60,
    )

    assert updated["progress_percentage"] == 60.0


def test_progress_100_does_not_auto_complete(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionLifecycleService.start_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    updated = CFOActionLifecycleService.update_progress(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        progress_percentage=100,
    )

    assert updated["progress_percentage"] == 100.0
    assert updated["status"] == "in_progress"
    assert updated.get("completed_at") is None


def test_invalid_progress_does_not_mutate_action(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    with pytest.raises(
        ValueError,
        match="Progress percentage must be between 0 and 100",
    ):
        CFOActionLifecycleService.update_progress(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
            progress_percentage=150,
        )

    persisted = CFOActionPlanService.get_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert persisted is not None
    assert persisted["progress_percentage"] == 0.0


# ==================================================
# BLOCK / UNBLOCK
# ==================================================


def test_block_action(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionLifecycleService.start_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    updated = CFOActionLifecycleService.block_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        management_notes="Waiting for donor response.",
    )

    assert updated["status"] == "blocked"
    assert (
        updated["management_notes"]
        == "Waiting for donor response."
    )


def test_unblock_action_returns_to_in_progress(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionLifecycleService.start_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    CFOActionLifecycleService.block_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    updated = CFOActionLifecycleService.unblock_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert updated["status"] == "in_progress"


def test_unblock_non_blocked_action_fails_without_mutation(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    with pytest.raises(
        ValueError,
        match="Only a blocked action can be unblocked",
    ):
        CFOActionLifecycleService.unblock_action(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
        )

    persisted = CFOActionPlanService.get_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert persisted is not None
    assert persisted["status"] == "open"


# ==================================================
# COMPLETE / REOPEN / CANCEL
# ==================================================


def test_complete_action_sets_completed_and_100_percent(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    updated = CFOActionLifecycleService.complete_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert updated["status"] == "completed"
    assert updated["progress_percentage"] == 100
    assert updated["completed_at"] is not None


def test_reopen_completed_action(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionLifecycleService.complete_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    updated = CFOActionLifecycleService.reopen_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert updated["status"] == "open"
    assert updated["completed_at"] is None


def test_completed_action_cannot_start_without_reopen(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionLifecycleService.complete_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    with pytest.raises(
        ValueError,
        match="Completed action must be reopened",
    ):
        CFOActionLifecycleService.start_action(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
        )

    persisted = CFOActionPlanService.get_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert persisted is not None
    assert persisted["status"] == "completed"


def test_cancel_action(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    updated = CFOActionLifecycleService.cancel_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        management_notes="No longer required.",
    )

    assert updated["status"] == "cancelled"
    assert updated["management_notes"] == "No longer required."


def test_reopen_cancelled_action(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    CFOActionLifecycleService.cancel_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    updated = CFOActionLifecycleService.reopen_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert updated["status"] == "open"


# ==================================================
# MANAGEMENT NOTES
# ==================================================


def test_update_management_notes(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    updated = (
        CFOActionLifecycleService.update_management_notes(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
            management_notes="Discuss at next management meeting.",
        )
    )

    assert (
        updated["management_notes"]
        == "Discuss at next management meeting."
    )


# ==================================================
# PROVENANCE / SAFETY
# ==================================================


def test_lifecycle_preserves_source_provenance(
    tmp_path: Path,
) -> None:
    action = _create_action(tmp_path)

    original_source_type = action.get("source_type")
    original_source_id = action.get("source_id")
    original_created_at = action.get("created_at")

    CFOActionLifecycleService.assign_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        owner="Elie",
    )

    CFOActionLifecycleService.set_due_date(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        due_date="2026-09-30",
    )

    CFOActionLifecycleService.start_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    persisted = CFOActionPlanService.get_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert persisted is not None
    assert persisted.get("source_type") == original_source_type
    assert persisted.get("source_id") == original_source_id
    assert persisted.get("created_at") == original_created_at


def test_unknown_action_fails_without_creating_record(
    tmp_path: Path,
) -> None:
    with pytest.raises(
        ValueError,
        match="CFO action not found",
    ):
        CFOActionLifecycleService.assign_action(
            financial_model_folder=tmp_path,
            action_id="does-not-exist",
            owner="Elie",
        )

    assert (
        CFOActionPlanService.list_actions(
            tmp_path
        )
        == []
    )