from pathlib import Path
from typing import Any
from uuid import uuid4

from app.services.financial_model_service import (
    FinancialModelService,
)


class ScenarioHistoryService:
    """
    Persist and retrieve explicit financial scenarios.

    Scenario history remains separate from the validated
    financial baseline and from the latest-scenario artifacts.
    """

    FILENAME = "scenario_history.json"

    @staticmethod
    def list_scenarios(
        financial_model_folder: Path,
    ) -> list[dict[str, Any]]:
        """
        Return all saved scenario-history records.

        Missing or invalid history files are treated as an
        empty history.
        """

        history = FinancialModelService.load_json(
            financial_model_folder,
            ScenarioHistoryService.FILENAME,
        )

        if not isinstance(
            history,
            list,
        ):
            return []

        return [
            item
            for item in history
            if isinstance(
                item,
                dict,
            )
        ]

    @staticmethod
    def save_scenario(
        *,
        financial_model_folder: Path,
        financial_scenario: dict[str, Any],
        scenario_decision_intelligence: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Append one explicit financial scenario to history.

        Existing history records are preserved.
        """

        history = ScenarioHistoryService.list_scenarios(
            financial_model_folder
        )

        scenario_name = str(
            financial_scenario.get(
                "scenario_name",
                "Unnamed Scenario",
            )
            or "Unnamed Scenario"
        )

        record = {
            "scenario_id": str(
                uuid4()
            ),
            "scenario_name": scenario_name,
            "financial_scenario": financial_scenario,
            "scenario_decision_intelligence": (
                scenario_decision_intelligence
            ),
        }

        history.append(
            record
        )

        FinancialModelService.save_json(
            financial_model_folder,
            ScenarioHistoryService.FILENAME,
            history,
        )

        return record

    @staticmethod
    def get_scenario(
        *,
        financial_model_folder: Path,
        scenario_id: str,
    ) -> dict[str, Any] | None:
        """
        Retrieve one saved scenario-history record by ID.
        """

        history = ScenarioHistoryService.list_scenarios(
            financial_model_folder
        )

        for record in history:
            if (
                record.get(
                    "scenario_id"
                )
                == scenario_id
            ):
                return record

        return None