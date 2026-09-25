from datetime import date

import pytest

from app.services.cfo_action_command_parser import (
    CFOActionCommandParser,
)


# ==================================================
# ASSIGN / UNASSIGN
# ==================================================


def test_parse_assign_command() -> None:
    result = CFOActionCommandParser.parse(
        "Assign the funding gap action to Elie."
    )

    assert result == {
        "command": "assign",
        "action_reference": "funding gap",
        "owner": "Elie",
    }


def test_parse_unassign_command() -> None:
    result = CFOActionCommandParser.parse(
        "Unassign the funding gap action."
    )

    assert result == {
        "command": "unassign",
        "action_reference": "funding gap",
    }


def test_parse_remove_owner_command() -> None:
    result = CFOActionCommandParser.parse(
        "Remove owner from the funding gap action."
    )

    assert result == {
        "command": "unassign",
        "action_reference": "funding gap",
    }


# ==================================================
# DUE DATE
# ==================================================


def test_parse_due_date_iso() -> None:
    result = CFOActionCommandParser.parse(
        "Set the funding gap action due date to 2026-09-30."
    )

    assert result == {
        "command": "set_due_date",
        "action_reference": "funding gap",
        "due_date": "2026-09-30",
    }


def test_parse_due_date_month_name_with_year() -> None:
    result = CFOActionCommandParser.parse(
        "Set the funding gap action deadline to September 30, 2026."
    )

    assert result == {
        "command": "set_due_date",
        "action_reference": "funding gap",
        "due_date": "2026-09-30",
    }


def test_parse_due_date_without_year_uses_current_year_when_future() -> None:
    result = CFOActionCommandParser.parse(
        "Set the funding gap action deadline to September 30.",
        reference_date=date(
            2026,
            9,
            12,
        ),
    )

    assert result["due_date"] == "2026-09-30"


def test_parse_due_date_without_year_uses_next_year_when_date_passed() -> None:
    result = CFOActionCommandParser.parse(
        "Set the funding gap action deadline to September 30.",
        reference_date=date(
            2026,
            10,
            5,
        ),
    )

    assert result["due_date"] == "2027-09-30"


def test_parse_deadline_for_action_form() -> None:
    result = CFOActionCommandParser.parse(
        "Set the deadline for the funding gap action to September 30, 2026."
    )

    assert result == {
        "command": "set_due_date",
        "action_reference": "funding gap",
        "due_date": "2026-09-30",
    }


def test_parse_clear_due_date() -> None:
    result = CFOActionCommandParser.parse(
        "Clear the due date for the funding gap action."
    )

    assert result == {
        "command": "clear_due_date",
        "action_reference": "funding gap",
    }


def test_invalid_due_date_fails() -> None:
    with pytest.raises(
        ValueError,
        match="Could not understand the due date",
    ):
        CFOActionCommandParser.parse(
            "Set the funding gap action deadline to sometime next week."
        )


# ==================================================
# PROGRESS / START
# ==================================================


def test_parse_progress_command() -> None:
    result = CFOActionCommandParser.parse(
        "Update the budget review action to 60% complete."
    )

    assert result == {
        "command": "update_progress",
        "action_reference": "budget review",
        "progress_percentage": 60.0,
    }


def test_parse_progress_without_complete_word() -> None:
    result = CFOActionCommandParser.parse(
        "Set the budget review action at 45%."
    )

    assert result == {
        "command": "update_progress",
        "action_reference": "budget review",
        "progress_percentage": 45.0,
    }


def test_progress_above_100_fails() -> None:
    with pytest.raises(
        ValueError,
        match="Progress percentage must be between 0 and 100",
    ):
        CFOActionCommandParser.parse(
            "Update the budget review action to 150% complete."
        )


def test_parse_start_command() -> None:
    result = CFOActionCommandParser.parse(
        "Start the funding gap action."
    )

    assert result == {
        "command": "start",
        "action_reference": "funding gap",
    }


# ==================================================
# BLOCK / UNBLOCK
# ==================================================


def test_parse_block_command() -> None:
    result = CFOActionCommandParser.parse(
        "Block the funding gap action."
    )

    assert result == {
        "command": "block",
        "action_reference": "funding gap",
        "management_notes": None,
    }


def test_parse_block_with_notes() -> None:
    result = CFOActionCommandParser.parse(
        "Block the funding gap action - waiting for donor response."
    )

    assert result == {
        "command": "block",
        "action_reference": "funding gap",
        "management_notes": "waiting for donor response",
    }


def test_parse_unblock_command() -> None:
    result = CFOActionCommandParser.parse(
        "Unblock the funding gap action."
    )

    assert result == {
        "command": "unblock",
        "action_reference": "funding gap",
    }


# ==================================================
# COMPLETE / REOPEN / CANCEL
# ==================================================


def test_parse_mark_completed_command() -> None:
    result = CFOActionCommandParser.parse(
        "Mark the donor proposal action as completed."
    )

    assert result == {
        "command": "complete",
        "action_reference": "donor proposal",
    }


def test_parse_complete_command() -> None:
    result = CFOActionCommandParser.parse(
        "Complete the funding gap action."
    )

    assert result == {
        "command": "complete",
        "action_reference": "funding gap",
    }


def test_parse_reopen_command() -> None:
    result = CFOActionCommandParser.parse(
        "Reopen the funding gap action."
    )

    assert result == {
        "command": "reopen",
        "action_reference": "funding gap",
    }


def test_parse_cancel_command() -> None:
    result = CFOActionCommandParser.parse(
        "Cancel the funding gap action."
    )

    assert result == {
        "command": "cancel",
        "action_reference": "funding gap",
        "management_notes": None,
    }


def test_parse_cancel_with_notes() -> None:
    result = CFOActionCommandParser.parse(
        "Cancel the funding gap action: no longer required."
    )

    assert result == {
        "command": "cancel",
        "action_reference": "funding gap",
        "management_notes": "no longer required",
    }


# ==================================================
# MANAGEMENT NOTES
# ==================================================


def test_parse_management_note() -> None:
    result = CFOActionCommandParser.parse(
        (
            "Add management note for the funding gap action: "
            "Discuss with management."
        )
    )

    assert result == {
        "command": "update_notes",
        "action_reference": "funding gap",
        "management_notes": "Discuss with management",
    }


# ==================================================
# REFERENCE CLEANING
# ==================================================


def test_parser_removes_the_and_action_from_reference() -> None:
    result = CFOActionCommandParser.parse(
        "Start the projected funding gap action."
    )

    assert result["action_reference"] == (
        "projected funding gap"
    )


def test_parser_preserves_meaningful_reference_words() -> None:
    result = CFOActionCommandParser.parse(
        "Start donor financial reporting review."
    )

    assert result["action_reference"] == (
        "donor financial reporting review"
    )


# ==================================================
# PRONOUN SAFETY
# ==================================================


def test_assign_it_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Explicit action reference is required",
    ):
        CFOActionCommandParser.parse(
            "Assign it to Elie."
        )


def test_mark_it_completed_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Explicit action reference is required",
    ):
        CFOActionCommandParser.parse(
            "Mark it completed."
        )


def test_set_its_deadline_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Explicit action reference is required",
    ):
        CFOActionCommandParser.parse(
            "Set its deadline to September 30."
        )


# ==================================================
# UNSUPPORTED / UNSAFE LANGUAGE
# ==================================================


def test_empty_command_fails() -> None:
    with pytest.raises(
        ValueError,
        match="CFO action command is required",
    ):
        CFOActionCommandParser.parse(
            ""
        )


def test_unknown_command_fails_safely() -> None:
    with pytest.raises(
        ValueError,
        match="Could not safely understand the CFO action command",
    ):
        CFOActionCommandParser.parse(
            "Do something about the funding gap."
        )


def test_question_is_not_misread_as_mutation_command() -> None:
    with pytest.raises(
        ValueError,
        match="Could not safely understand the CFO action command",
    ):
        CFOActionCommandParser.parse(
            "What is the status of the funding gap action?"
        )