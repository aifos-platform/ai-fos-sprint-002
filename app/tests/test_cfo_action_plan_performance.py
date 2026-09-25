from pathlib import Path

from app.services.cfo_action_history import (
    CFOActionHistoryService,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)


def test_build_performance_reads_persisted_history(
    tmp_path: Path,
) -> None:
    CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="A1",
        event_type="action_created",
        source="system",
    )

    CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="A1",
        event_type="owner_changed",
        previous_value=None,
        new_value="Elie",
        source="ask_cfo",
    )

    result = (
        CFOActionPlanService.build_performance(
            financial_model_folder=tmp_path
        )
    )

    assert result["status"] == "available"
    assert (
        result["summary"]["total_events"]
        == 2
    )
    assert (
        result["summary"]["action_count"]
        == 1
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


def test_build_performance_does_not_modify_history(
    tmp_path: Path,
) -> None:
    CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="A1",
        event_type="action_created",
    )

    before = (
        CFOActionHistoryService.list_events(
            tmp_path
        )
    )

    CFOActionPlanService.build_performance(
        financial_model_folder=tmp_path
    )

    after = (
        CFOActionHistoryService.list_events(
            tmp_path
        )
    )

    assert before == after


def test_build_performance_does_not_create_action_plan(
    tmp_path: Path,
) -> None:
    CFOActionHistoryService.record_event(
        financial_model_folder=tmp_path,
        action_id="A1",
        event_type="action_created",
    )

    CFOActionPlanService.build_performance(
        financial_model_folder=tmp_path
    )

    actions = (
        CFOActionPlanService.list_actions(
            tmp_path
        )
    )

    assert actions == []


def test_build_performance_handles_empty_history(
    tmp_path: Path,
) -> None:
    result = (
        CFOActionPlanService.build_performance(
            financial_model_folder=tmp_path
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