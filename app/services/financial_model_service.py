import json
from pathlib import Path
from typing import Any


class FinancialModelService:
    """
    Handles saving and loading the persistent
    AI-FOS financial model.
    """


    @staticmethod
    def save_json(
        financial_model_folder: Path,
        filename: str,
        data,
    ) -> Path:
        """
        Save AI-FOS financial-model data as JSON.

        Datetime and date values are converted to
        ISO-formatted strings automatically.
        """

        from datetime import date, datetime

        financial_model_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            financial_model_folder
            / filename
        )

        def json_serializer(value):
            if isinstance(
                value,
                (datetime, date),
            ):
                return value.isoformat()

            raise TypeError(
                f"Object of type "
                f"{type(value).__name__} "
                f"is not JSON serializable"
            )

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
                default=json_serializer,
            )

        return output_file

    @staticmethod
    def load_json(
        financial_model_folder: Path,
        filename: str,
    ) -> Any:

        input_file = (
            financial_model_folder
            / filename
        )

        if not input_file.exists():
            return None

        with input_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    @staticmethod
    def save_dim_account(
        financial_model_folder: Path,
        accounts: list,
    ) -> Path:

        return FinancialModelService.save_json(
            financial_model_folder=financial_model_folder,
            filename="dim_account.json",
            data=accounts,
        )

    @staticmethod
    def load_dim_account(
        financial_model_folder: Path,
    ) -> list:
        """
        Load the saved DIM_ACCOUNT from the workspace.
        """

        accounts = FinancialModelService.load_json(
            financial_model_folder=financial_model_folder,
            filename="dim_account.json",
        )

        if accounts is None:
            return []

        return accounts

    @staticmethod
    def save_financial_outputs(
        financial_model_folder: Path,
        trial_balance: Any,
        income_statement: Any,
        standard_income_statement: Any,
        balance_sheet: Any,
        standard_balance_sheet: Any,
        cash_flow: Any,
        standard_cash_flow_statement: Any,
        liquidity: Any,
        financial_facts: Any,
        financial_analysis: Any,
        financial_trends: Any,
        financial_forecast: Any,
    ) -> dict[str, str]:
        """
        Persist the calculated financial outputs so
        AI-FOS can use them after an application restart.
        """

        files = {
            "trial_balance": FinancialModelService.save_json(
                financial_model_folder,
                "trial_balance.json",
                trial_balance,
            ),
            "income_statement": FinancialModelService.save_json(
                financial_model_folder,
                "income_statement.json",
                income_statement,
            ),
            "standard_income_statement": FinancialModelService.save_json(
                financial_model_folder,
                "standard_income_statement.json",
                standard_income_statement,
            ),
            "balance_sheet": FinancialModelService.save_json(
                financial_model_folder,
                "balance_sheet.json",
                balance_sheet,
            ),            

            "standard_balance_sheet": FinancialModelService.save_json(
                financial_model_folder,
                "standard_balance_sheet.json",
                standard_balance_sheet,
            ),

            "cash_flow": FinancialModelService.save_json(
                financial_model_folder,
                "cash_flow.json",
                cash_flow,
            ),

            "standard_cash_flow_statement": FinancialModelService.save_json(
                financial_model_folder,
                "standard_cash_flow_statement.json",
                standard_cash_flow_statement,
            ),

            "liquidity": FinancialModelService.save_json(
                financial_model_folder,
                "liquidity.json",
                liquidity,
            ),
            "financial_facts": FinancialModelService.save_json(
                financial_model_folder,
                "financial_facts.json",
                financial_facts,
            ),
            "financial_analysis": FinancialModelService.save_json(
                financial_model_folder,
                "financial_analysis.json",
                financial_analysis,
            ),
            "financial_trends": FinancialModelService.save_json(
                financial_model_folder,
                "financial_trends.json",
                financial_trends,
            ),
            "financial_forecast": FinancialModelService.save_json(
                financial_model_folder,
                "financial_forecast.json",
                financial_forecast,
            ),

        }

        return {
            name: str(path)
            for name, path in files.items()
        }

    @staticmethod
    def save_verified_intelligence_outputs(
        financial_model_folder: Path,
        financial_health: Any,
        risk_assessment: Any,
        forward_risks: Any,
        financial_opportunities: Any,
        cfo_recommendations: Any,
        executive_decision_intelligence: Any,
    ) -> dict[str, str]:
        """
        Persist verified AI-FOS intelligence outputs separately
        from the core financial model and explicit scenarios.
        """

        files = {
            "financial_health": (
                FinancialModelService.save_json(
                    financial_model_folder,
                    "financial_health.json",
                    financial_health,
                )
            ),
            "risk_assessment": (
                FinancialModelService.save_json(
                    financial_model_folder,
                    "risk_assessment.json",
                    risk_assessment,
                )
            ),
            "forward_risks": (
                FinancialModelService.save_json(
                    financial_model_folder,
                    "forward_risks.json",
                    forward_risks,
                )
            ),
            "financial_opportunities": (
                FinancialModelService.save_json(
                    financial_model_folder,
                    "financial_opportunities.json",
                    financial_opportunities,
                )
            ),
            "cfo_recommendations": (
                FinancialModelService.save_json(
                    financial_model_folder,
                    "cfo_recommendations.json",
                    cfo_recommendations,
                )
            ),
            "executive_decision_intelligence": (
                FinancialModelService.save_json(
                    financial_model_folder,
                    "executive_decision_intelligence.json",
                    executive_decision_intelligence,
                )
            ),
        }

        return {
            name: str(path)
            for name, path in files.items()
        }

    @staticmethod
    def save_scenario_outputs(
        financial_model_folder: Path,
        financial_scenario: Any,
        scenario_decision_intelligence: Any,
        scenario_comparison_intelligence: Any = None,
    ) -> dict[str, str]:
        """
        Persist explicit financial scenario outputs.

        Scenario artifacts remain separate from the normal
        financial-processing outputs because scenarios are
        generated only when explicitly requested.

        The deterministic scenario, its decision intelligence,
        and optional comparison intelligence are stored as
        separate artifacts.
        """

        files = {
            "financial_scenario": (
                FinancialModelService.save_json(
                    financial_model_folder,
                    "financial_scenario.json",
                    financial_scenario,
                )
            ),
            "scenario_decision_intelligence": (
                FinancialModelService.save_json(
                    financial_model_folder,
                    "scenario_decision_intelligence.json",
                    scenario_decision_intelligence,
                )
            ),
        }

        if scenario_comparison_intelligence is not None:
            files["scenario_comparison_intelligence"] = (
                FinancialModelService.save_json(
                    financial_model_folder,
                    "scenario_comparison_intelligence.json",
                    scenario_comparison_intelligence,
                )
            )

        return {
            name: str(path)
            for name, path in files.items()
        }

    @staticmethod
    def load_financial_facts(
        financial_model_folder: Path,
    ) -> dict[str, Any]:
        """
        Load persistent financial facts for AI questions.
        """

        financial_facts = FinancialModelService.load_json(
            financial_model_folder=financial_model_folder,
            filename="financial_facts.json",
        )

        if not isinstance(
            financial_facts,
            dict,
        ):
            return {}

        return financial_facts