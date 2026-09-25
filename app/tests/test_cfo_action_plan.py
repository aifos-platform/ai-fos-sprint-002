from pathlib import Path

import pytest

from app.services.cfo_action_plan import (
    CFOActionPlanService,
)


def _create_sample_action(
    tmp_path: Path,
):
    return CFOActionPlanService.create_action(
        financial_model_folder=tmp_path,
        title="Close funding gap",
        description=(
            "Accelerate eligible fundraising "
            "and protect unrestricted cash."
        ),
        priority="High",
        category="Funding",
        source_type=(
            "executive_decision_intelligence"
        ),
        source_title="Funding gap",
        source_priority="High",
    )


def test_missing_action_plan_returns_empty_list(
    tmp_path: Path,
):
    actions = CFOActionPlanService.list_actions(
        tmp_path
    )

    assert actions == []


def test_create_action_persists_record(
    tmp_path: Path,
):
    action = _create_sample_action(
        tmp_path
    )

    saved_actions = (
        CFOActionPlanService.list_actions(
            tmp_path
        )
    )

    assert len(saved_actions) == 1

    assert (
        saved_actions[0]["action_id"]
        == action["action_id"]
    )

    assert (
        saved_actions[0]["title"]
        == "Close funding gap"
    )

    assert (
        saved_actions[0]["status"]
        == "open"
    )


def test_create_action_does_not_invent_owner_or_due_date(
    tmp_path: Path,
):
    action = _create_sample_action(
        tmp_path
    )

    assert action["owner"] is None
    assert action["due_date"] is None

    assert (
        action["progress_percentage"]
        == 0
    )

    assert (
        action["management_notes"]
        is None
    )


def test_multiple_actions_preserve_existing_records(
    tmp_path: Path,
):
    first = _create_sample_action(
        tmp_path
    )

    second = (
        CFOActionPlanService.create_action(
            financial_model_folder=tmp_path,
            title="Protect liquidity",
            description=(
                "Monitor available cash "
                "and upcoming obligations."
            ),
            priority="Critical",
            category="Liquidity",
        )
    )

    actions = CFOActionPlanService.list_actions(
        tmp_path
    )

    assert len(actions) == 2

    assert (
        actions[0]["action_id"]
        == first["action_id"]
    )

    assert (
        actions[1]["action_id"]
        == second["action_id"]
    )

    assert (
        first["action_id"]
        != second["action_id"]
    )


def test_get_action_by_id(
    tmp_path: Path,
):
    created = _create_sample_action(
        tmp_path
    )

    loaded = CFOActionPlanService.get_action(
        financial_model_folder=tmp_path,
        action_id=created["action_id"],
    )

    assert loaded == created


def test_update_management_fields(
    tmp_path: Path,
):
    created = _create_sample_action(
        tmp_path
    )

    updated = CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=created["action_id"],
        owner="Executive Director",
        due_date="2026-09-30",
        status="in_progress",
        progress_percentage=40,
        management_notes=(
            "Proposal preparation started."
        ),
    )

    assert updated is not None

    assert (
        updated["owner"]
        == "Executive Director"
    )

    assert (
        updated["due_date"]
        == "2026-09-30"
    )

    assert (
        updated["status"]
        == "in_progress"
    )

    assert (
        updated["progress_percentage"]
        == 40
    )

    assert (
        updated["management_notes"]
        == "Proposal preparation started."
    )


def test_update_preserves_source_provenance(
    tmp_path: Path,
):
    created = _create_sample_action(
        tmp_path
    )

    original_source_type = (
        created["source_type"]
    )

    original_source_title = (
        created["source_title"]
    )

    original_source_priority = (
        created["source_priority"]
    )

    updated = CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=created["action_id"],
        owner="Finance Manager",
    )

    assert updated is not None

    assert (
        updated["source_type"]
        == original_source_type
    )

    assert (
        updated["source_title"]
        == original_source_title
    )

    assert (
        updated["source_priority"]
        == original_source_priority
    )


def test_completed_action_sets_progress_and_completion_time(
    tmp_path: Path,
):
    created = _create_sample_action(
        tmp_path
    )

    updated = CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=created["action_id"],
        status="completed",
    )

    assert updated is not None

    assert (
        updated["status"]
        == "completed"
    )

    assert (
        updated["progress_percentage"]
        == 100
    )

    assert (
        updated["completed_at"]
        is not None
    )


def test_reopening_completed_action_clears_completion_time(
    tmp_path: Path,
):
    created = _create_sample_action(
        tmp_path
    )

    completed = (
        CFOActionPlanService.update_action(
            financial_model_folder=tmp_path,
            action_id=created["action_id"],
            status="completed",
        )
    )

    assert completed is not None
    assert (
        completed["completed_at"]
        is not None
    )

    reopened = CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=created["action_id"],
        status="in_progress",
        progress_percentage=80,
    )

    assert reopened is not None

    assert (
        reopened["status"]
        == "in_progress"
    )

    assert (
        reopened["completed_at"]
        is None
    )

    assert (
        reopened["progress_percentage"]
        == 80
    )


def test_invalid_status_is_rejected(
    tmp_path: Path,
):
    with pytest.raises(
        ValueError,
        match="Invalid CFO action status",
    ):
        CFOActionPlanService.create_action(
            financial_model_folder=tmp_path,
            title="Test action",
            description="Test description",
            status="waiting_for_magic",
        )


def test_invalid_progress_is_rejected(
    tmp_path: Path,
):
    with pytest.raises(
        ValueError,
        match="between 0 and 100",
    ):
        CFOActionPlanService.create_action(
            financial_model_folder=tmp_path,
            title="Test action",
            description="Test description",
            progress_percentage=150,
        )


def test_invalid_due_date_is_rejected(
    tmp_path: Path,
):
    with pytest.raises(
        ValueError,
        match="YYYY-MM-DD",
    ):
        CFOActionPlanService.create_action(
            financial_model_folder=tmp_path,
            title="Test action",
            description="Test description",
            due_date="30 September 2026",
        )


def test_create_from_executive_priority_preserves_verified_action(
    tmp_path: Path,
):
    executive_priority = {
        "rank": 1,
        "priority": "High",
        "category": "Funding",
        "title": "Material funding gap",
        "evidence": (
            "A validated funding gap exists."
        ),
        "management_action": (
            "Accelerate the funding pipeline."
        ),
        "expected_impact": (
            "Improve funding coverage."
        ),
        "source": "risk_assessment",
        "source_type": "current_risk",
    }

    action = (
        CFOActionPlanService
        .create_from_executive_priority(
            financial_model_folder=tmp_path,
            executive_priority=(
                executive_priority
            ),
        )
    )

    assert (
        action["title"]
        == "Material funding gap"
    )

    assert (
        action["description"]
        == "Accelerate the funding pipeline."
    )

    assert (
        action["priority"]
        == "High"
    )

    assert (
        action["category"]
        == "Funding"
    )

    assert (
        action["source_type"]
        == "executive_decision_intelligence"
    )

    assert (
        action["source_title"]
        == "Material funding gap"
    )

    assert (
        action["source_priority"]
        == "High"
    )

    assert action["owner"] is None
    assert action["due_date"] is None

    assert (
        action["status"]
        == "open"
    )

    assert (
        action["progress_percentage"]
        == 0
    )

def test_build_monitoring_reads_persisted_actions(
    tmp_path: Path,
):
    created = CFOActionPlanService.create_action(
        financial_model_folder=tmp_path,
        title="Submit funding proposal",
        description="Submit the funding proposal.",
        priority="High",
        owner="Executive Director",
        due_date="2026-09-10",
        status="in_progress",
    )

    from datetime import date

    monitoring = (
        CFOActionPlanService.build_monitoring(
            financial_model_folder=tmp_path,
            reference_date=date(
                2026,
                9,
                12,
            ),
        )
    )

    assert (
        monitoring["summary"]["total_actions"]
        == 1
    )

    assert (
        monitoring["summary"]["overdue"]
        == 1
    )

    assert (
        monitoring["overdue_actions"][0][
            "action_id"
        ]
        == created["action_id"]
    )


def test_build_monitoring_does_not_modify_persisted_actions(
    tmp_path: Path,
):
    created = _create_sample_action(
        tmp_path
    )

    from datetime import date

    CFOActionPlanService.build_monitoring(
        financial_model_folder=tmp_path,
        reference_date=date(
            2026,
            9,
            12,
        ),
    )

    loaded = CFOActionPlanService.get_action(
        financial_model_folder=tmp_path,
        action_id=created["action_id"],
    )

    assert loaded == created


def test_build_monitoring_handles_empty_action_plan(
    tmp_path: Path,
):
    from datetime import date

    monitoring = (
        CFOActionPlanService.build_monitoring(
            financial_model_folder=tmp_path,
            reference_date=date(
                2026,
                9,
                12,
            ),
        )
    )

    assert (
        monitoring["status"]
        == "available"
    )

    assert (
        monitoring["summary"]["total_actions"]
        == 0
    )

    assert (
        monitoring["management_attention"]
        == []
    )
