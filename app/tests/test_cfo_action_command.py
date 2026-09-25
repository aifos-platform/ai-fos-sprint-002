from pathlib import Path

import pytest

from app.services.cfo_action_command import (
    CFOActionCommandService,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)


# ==================================================
# HELPERS
# ==================================================


def _create_action(
    folder: Path,
    *,
    title: str,
    description: str | None = None,
) -> dict:
    return CFOActionPlanService.create_action(
        financial_model_folder=folder,
        title=title,
        description=(
            description
            or f"Management action for {title}."
        ),
        priority="High",
        category="Financial Management",
    )


def _get(
    folder: Path,
    action_id: str,
) -> dict:
    action = CFOActionPlanService.get_action(
        financial_model_folder=folder,
        action_id=action_id,
    )

    assert action is not None

    return action


# ==================================================
# RESOLUTION
# ==================================================


def test_resolve_action_by_explicit_id(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    resolved = CFOActionCommandService.resolve_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
    )

    assert resolved["action_id"] == action["action_id"]


def test_resolve_action_by_exact_title(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    resolved = CFOActionCommandService.resolve_action(
        financial_model_folder=tmp_path,
        action_reference="Review funding gap",
    )

    assert resolved["action_id"] == action["action_id"]


def test_resolve_action_is_case_and_space_insensitive(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review Funding Gap",
    )

    resolved = CFOActionCommandService.resolve_action(
        financial_model_folder=tmp_path,
        action_reference="  review   funding   gap  ",
    )

    assert resolved["action_id"] == action["action_id"]


def test_resolve_action_by_unique_partial_title(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review projected funding gap",
    )

    resolved = CFOActionCommandService.resolve_action(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
    )

    assert resolved["action_id"] == action["action_id"]


def test_no_match_fails(
    tmp_path: Path,
) -> None:
    _create_action(
        tmp_path,
        title="Review funding gap",
    )

    with pytest.raises(
        ValueError,
        match="No CFO action matches the reference",
    ):
        CFOActionCommandService.resolve_action(
            financial_model_folder=tmp_path,
            action_reference="cash runway",
        )


def test_empty_reference_fails(
    tmp_path: Path,
) -> None:
    _create_action(
        tmp_path,
        title="Review funding gap",
    )

    with pytest.raises(
        ValueError,
        match="Action reference is required",
    ):
        CFOActionCommandService.resolve_action(
            financial_model_folder=tmp_path,
            action_reference="",
        )


# ==================================================
# AMBIGUITY SAFETY
# ==================================================


def test_partial_reference_with_multiple_matches_is_ambiguous(
    tmp_path: Path,
) -> None:
    _create_action(
        tmp_path,
        title="Review current funding gap",
    )

    _create_action(
        tmp_path,
        title="Review future funding gap",
    )

    with pytest.raises(
        ValueError,
        match="Action reference is ambiguous",
    ):
        CFOActionCommandService.resolve_action(
            financial_model_folder=tmp_path,
            action_reference="funding gap",
        )


def test_ambiguous_assignment_does_not_mutate_any_action(
    tmp_path: Path,
) -> None:
    action_1 = _create_action(
        tmp_path,
        title="Review current funding gap",
    )

    action_2 = _create_action(
        tmp_path,
        title="Review future funding gap",
    )

    with pytest.raises(
        ValueError,
        match="Action reference is ambiguous",
    ):
        CFOActionCommandService.assign(
            financial_model_folder=tmp_path,
            action_reference="funding gap",
            owner="Elie",
        )

    persisted_1 = _get(
        tmp_path,
        action_1["action_id"],
    )

    persisted_2 = _get(
        tmp_path,
        action_2["action_id"],
    )

    assert persisted_1["owner"] is None
    assert persisted_2["owner"] is None


def test_ambiguous_completion_does_not_mutate_any_action(
    tmp_path: Path,
) -> None:
    action_1 = _create_action(
        tmp_path,
        title="Review current funding gap",
    )

    action_2 = _create_action(
        tmp_path,
        title="Review future funding gap",
    )

    with pytest.raises(
        ValueError,
        match="Action reference is ambiguous",
    ):
        CFOActionCommandService.complete(
            financial_model_folder=tmp_path,
            action_reference="funding gap",
        )

    persisted_1 = _get(
        tmp_path,
        action_1["action_id"],
    )

    persisted_2 = _get(
        tmp_path,
        action_2["action_id"],
    )

    assert persisted_1["status"] == "open"
    assert persisted_2["status"] == "open"


# ==================================================
# ASSIGNMENT
# ==================================================


def test_assign_by_reference(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    updated = CFOActionCommandService.assign(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
        owner="Elie",
    )

    assert updated["action_id"] == action["action_id"]
    assert updated["owner"] == "Elie"


def test_unassign_by_reference(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    CFOActionCommandService.assign(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
        owner="Elie",
    )

    updated = CFOActionCommandService.unassign(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
    )

    assert updated["action_id"] == action["action_id"]
    assert updated["owner"] is None


# ==================================================
# DUE DATE
# ==================================================


def test_set_due_date_by_reference(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    updated = CFOActionCommandService.set_due_date(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
        due_date="2026-09-30",
    )

    assert updated["action_id"] == action["action_id"]
    assert updated["due_date"] == "2026-09-30"


def test_invalid_due_date_does_not_mutate(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    with pytest.raises(
        ValueError,
        match="Due date must use YYYY-MM-DD format",
    ):
        CFOActionCommandService.set_due_date(
            financial_model_folder=tmp_path,
            action_reference="funding gap",
            due_date="September 30",
        )

    persisted = _get(
        tmp_path,
        action["action_id"],
    )

    assert persisted["due_date"] is None


# ==================================================
# STATUS / PROGRESS
# ==================================================


def test_start_by_reference(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    updated = CFOActionCommandService.start(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
    )

    assert updated["action_id"] == action["action_id"]
    assert updated["status"] == "in_progress"


def test_update_progress_by_reference(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    CFOActionCommandService.start(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
    )

    updated = CFOActionCommandService.update_progress(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
        progress_percentage=60,
    )

    assert updated["action_id"] == action["action_id"]
    assert updated["progress_percentage"] == 60.0


def test_block_and_unblock_by_reference(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    CFOActionCommandService.start(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
    )

    blocked = CFOActionCommandService.block(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
        management_notes="Waiting for donor response.",
    )

    assert blocked["status"] == "blocked"

    unblocked = CFOActionCommandService.unblock(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
    )

    assert unblocked["action_id"] == action["action_id"]
    assert unblocked["status"] == "in_progress"


# ==================================================
# COMPLETE / REOPEN / CANCEL
# ==================================================


def test_complete_by_reference(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    updated = CFOActionCommandService.complete(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
    )

    assert updated["action_id"] == action["action_id"]
    assert updated["status"] == "completed"
    assert updated["progress_percentage"] == 100


def test_reopen_by_reference(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    CFOActionCommandService.complete(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
    )

    updated = CFOActionCommandService.reopen(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
    )

    assert updated["action_id"] == action["action_id"]
    assert updated["status"] == "open"
    assert updated["completed_at"] is None


def test_cancel_by_reference(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    updated = CFOActionCommandService.cancel(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
        management_notes="No longer required.",
    )

    assert updated["action_id"] == action["action_id"]
    assert updated["status"] == "cancelled"


# ==================================================
# NOTES
# ==================================================


def test_update_notes_by_reference(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    updated = CFOActionCommandService.update_notes(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
        management_notes="Discuss with management.",
    )

    assert updated["action_id"] == action["action_id"]
    assert (
        updated["management_notes"]
        == "Discuss with management."
    )


# ==================================================
# PROVENANCE / IMMUTABILITY
# ==================================================


def test_command_layer_preserves_source_provenance(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
    )

    original_source_type = action.get("source_type")
    original_source_id = action.get("source_id")
    original_created_at = action.get("created_at")

    CFOActionCommandService.assign(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
        owner="Elie",
    )

    CFOActionCommandService.set_due_date(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
        due_date="2026-09-30",
    )

    CFOActionCommandService.start(
        financial_model_folder=tmp_path,
        action_reference="funding gap",
    )

    persisted = _get(
        tmp_path,
        action["action_id"],
    )

    assert persisted.get("source_type") == original_source_type
    assert persisted.get("source_id") == original_source_id
    assert persisted.get("created_at") == original_created_at


def test_unknown_action_reference_never_creates_or_mutates(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Review funding gap",
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

    persisted = _get(
        tmp_path,
        action["action_id"],
    )

    assert persisted["owner"] is None
    assert (
        len(
            CFOActionPlanService.list_actions(
                tmp_path
            )
        )
        == 1
    )