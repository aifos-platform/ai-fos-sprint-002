from pathlib import Path

from app.services.scenario_history import (
    ScenarioHistoryService,
)


def _scenario(
    name: str,
) -> dict:
    return {
        "status": "available",
        "scenario_name": name,
        "scenario_type": "what_if",
    }


def _decision(
    name: str,
) -> dict:
    return {
        "status": "available",
        "scenario_name": name,
        "decision_signal": "negative",
        "severity": "medium",
    }


def test_scenario_history_starts_empty(
    tmp_path,
):
    folder = Path(tmp_path)

    result = ScenarioHistoryService.list_scenarios(
        folder
    )

    assert result == []


def test_scenario_can_be_saved_to_history(
    tmp_path,
):
    folder = Path(tmp_path)

    saved = ScenarioHistoryService.save_scenario(
        financial_model_folder=folder,
        financial_scenario=_scenario(
            "Revenue Down 10%"
        ),
        scenario_decision_intelligence=_decision(
            "Revenue Down 10%"
        ),
    )

    assert saved["scenario_id"]
    assert (
        saved["scenario_name"]
        == "Revenue Down 10%"
    )

    assert (
        saved["financial_scenario"][
            "scenario_name"
        ]
        == "Revenue Down 10%"
    )

    assert (
        saved["scenario_decision_intelligence"][
            "severity"
        ]
        == "medium"
    )


def test_multiple_scenarios_are_preserved(
    tmp_path,
):
    folder = Path(tmp_path)

    ScenarioHistoryService.save_scenario(
        financial_model_folder=folder,
        financial_scenario=_scenario(
            "Scenario A"
        ),
        scenario_decision_intelligence=_decision(
            "Scenario A"
        ),
    )

    ScenarioHistoryService.save_scenario(
        financial_model_folder=folder,
        financial_scenario=_scenario(
            "Scenario B"
        ),
        scenario_decision_intelligence=_decision(
            "Scenario B"
        ),
    )

    saved = ScenarioHistoryService.list_scenarios(
        folder
    )

    assert len(saved) == 2

    assert (
        saved[0]["scenario_name"]
        == "Scenario A"
    )

    assert (
        saved[1]["scenario_name"]
        == "Scenario B"
    )


def test_saved_scenario_can_be_retrieved_by_id(
    tmp_path,
):
    folder = Path(tmp_path)

    saved = ScenarioHistoryService.save_scenario(
        financial_model_folder=folder,
        financial_scenario=_scenario(
            "Cash Outflow"
        ),
        scenario_decision_intelligence=_decision(
            "Cash Outflow"
        ),
    )

    loaded = ScenarioHistoryService.get_scenario(
        financial_model_folder=folder,
        scenario_id=saved["scenario_id"],
    )

    assert loaded == saved


def test_unknown_scenario_id_returns_none(
    tmp_path,
):
    folder = Path(tmp_path)

    result = ScenarioHistoryService.get_scenario(
        financial_model_folder=folder,
        scenario_id="missing-scenario",
    )

    assert result is None