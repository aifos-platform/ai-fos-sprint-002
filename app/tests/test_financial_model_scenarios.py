from pathlib import Path

from app.services.financial_model_service import (
    FinancialModelService,
)


def test_save_scenario_outputs_creates_separate_files(
    tmp_path,
):
    scenario = {
        "status": "available",
        "scenario_name": "Revenue Down 10%",
    }

    decision = {
        "status": "available",
        "decision_signal": "negative",
    }

    result = (
        FinancialModelService.save_scenario_outputs(
            financial_model_folder=Path(tmp_path),
            financial_scenario=scenario,
            scenario_decision_intelligence=decision,
        )
    )

    scenario_file = Path(
        result["financial_scenario"]
    )

    decision_file = Path(
        result[
            "scenario_decision_intelligence"
        ]
    )

    assert scenario_file.exists()
    assert decision_file.exists()

    assert (
        scenario_file.name
        == "financial_scenario.json"
    )

    assert (
        decision_file.name
        == "scenario_decision_intelligence.json"
    )


def test_saved_scenario_outputs_can_be_loaded(
    tmp_path,
):
    folder = Path(tmp_path)

    comparison = {
        "status": "available",
        "preferred_scenario": "Scenario B",
        "comparison_signal": "clear_preference",
    }    

    scenario = {
        "status": "available",
        "scenario_name": "Cash Outflow",
        "cash": {
            "scenario_available_cash": 800.0,
        },
    }

    decision = {
        "status": "available",
        "decision_signal": "negative",
    }

    FinancialModelService.save_scenario_outputs(
        financial_model_folder=folder,
        financial_scenario=scenario,
        scenario_decision_intelligence=decision,
        scenario_comparison_intelligence=comparison,
    )

    loaded_scenario = (
        FinancialModelService.load_json(
            folder,
            "financial_scenario.json",
        )
    )

    loaded_comparison = (
        FinancialModelService.load_json(
            folder,
            "scenario_comparison_intelligence.json",
        )
    )    

    loaded_decision = (
        FinancialModelService.load_json(
            folder,
            "scenario_decision_intelligence.json",
        )
    )

    assert loaded_scenario == scenario
    assert loaded_decision == decision
    assert loaded_comparison == comparison


def test_scenario_persistence_does_not_replace_baseline_forecast(
    tmp_path,
):
    folder = Path(tmp_path)

    baseline_forecast = {
        "status": "available",
        "forecast_type": "baseline",
    }

    FinancialModelService.save_json(
        folder,
        "financial_forecast.json",
        baseline_forecast,
    )

    FinancialModelService.save_scenario_outputs(
        financial_model_folder=folder,
        financial_scenario={
            "status": "available",
            "scenario_type": "what_if",
        },
        scenario_decision_intelligence={
            "status": "available",
            "decision_signal": "negative",
        },
    )

    loaded_forecast = (
        FinancialModelService.load_json(
            folder,
            "financial_forecast.json",
        )
    )

    assert loaded_forecast == baseline_forecast