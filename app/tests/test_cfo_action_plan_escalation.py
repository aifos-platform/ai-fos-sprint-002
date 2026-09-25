from datetime import date
from pathlib import Path

from app.services.cfo_action_plan import (
    CFOActionPlanService,
)


def _create_action(
    folder: Path,
    *,
    title: str,
    priority: str = "High",
    owner: str | None = None,
    due_date: str | None = None,
    status: str = "open",
) -> dict:
    return CFOActionPlanService.create_action(
        financial_model_folder=folder,
        title=title,
        description=f"Action for {title}.",
        priority=priority,
        category="Financial Management",
        owner=owner,
        due_date=due_date,
        status=status,
    )


def test_build_escalation_reads_persisted_actions(
    tmp_path: Path,
) -> None:
    _create_action(
        tmp_path,
        title="Funding gap mitigation",
        priority="High",
        owner=None,
        due_date="2026-09-01",
    )

    result = CFOActionPlanService.build_escalation(
        financial_model_folder=tmp_path,
        reference_date=date(
            2026,
            9,
            12,
        ),
    )

    assert result["status"] == "available"
    assert (
        result["summary"][
            "total_escalations"
        ]
        == 1
    )

    escalation = (
        result["escalations"][0]
    )

    assert (
        escalation["title"]
        == "Funding gap mitigation"
    )

    assert (
        escalation["severity"]
        == "Critical"
    )

    assert (
        "overdue"
        in escalation["signals"]
    )

    assert (
        "unassigned_high_priority"
        in escalation["signals"]
    )


def test_build_escalation_uses_monitoring_classifications(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Donor reporting follow-up",
        priority="High",
        owner="Elie",
        due_date="2026-09-30",
    )

    CFOActionPlanService.update_action(
        financial_model_folder=tmp_path,
        action_id=action["action_id"],
        status="blocked",
    )

    result = CFOActionPlanService.build_escalation(
        financial_model_folder=tmp_path,
        reference_date=date(
            2026,
            9,
            12,
        ),
    )

    escalation = (
        result["escalations"][0]
    )

    assert (
        escalation["severity"]
        == "High"
    )

    assert (
        escalation["signals"]
        == ["blocked"]
    )


def test_build_escalation_respects_due_soon_window(
    tmp_path: Path,
) -> None:
    _create_action(
        tmp_path,
        title="Monthly finance review",
        priority="Medium",
        owner="Elie",
        due_date="2026-09-15",
    )

    result = CFOActionPlanService.build_escalation(
        financial_model_folder=tmp_path,
        reference_date=date(
            2026,
            9,
            12,
        ),
        due_soon_days=7,
    )

    escalation = (
        result["escalations"][0]
    )

    assert (
        escalation["severity"]
        == "Medium"
    )

    assert (
        escalation["signals"]
        == ["due_soon"]
    )


def test_build_escalation_empty_action_plan_is_safe(
    tmp_path: Path,
) -> None:
    result = CFOActionPlanService.build_escalation(
        financial_model_folder=tmp_path,
        reference_date=date(
            2026,
            9,
            12,
        ),
    )

    assert result["status"] == "available"

    assert result["summary"] == {
        "total_escalations": 0,
        "critical": 0,
        "high": 0,
        "medium": 0,
    }

    assert (
        result["highest_escalation"]
        is None
    )

    assert (
        result["escalations"]
        == []
    )


def test_build_escalation_does_not_modify_actions(
    tmp_path: Path,
) -> None:
    action = _create_action(
        tmp_path,
        title="Funding gap review",
        priority="High",
        owner=None,
        due_date="2026-09-01",
    )

    before = (
        CFOActionPlanService.get_action(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
        )
    )

    CFOActionPlanService.build_escalation(
        financial_model_folder=tmp_path,
        reference_date=date(
            2026,
            9,
            12,
        ),
    )

    after = (
        CFOActionPlanService.get_action(
            financial_model_folder=tmp_path,
            action_id=action["action_id"],
        )
    )

    assert before == after