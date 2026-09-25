from pathlib import Path
from typing import Any

from app.services.financial_model_service import (
    FinancialModelService,
)
from app.services.workspace_service import (
    WorkspaceService,
)


class VerifiedCFOContextBuilder:
    """
    Build a compact, verified organization-specific
    context for the AI-FOS Digital CFO.

    This service does not calculate financial results.

    It reads already-persisted AI-FOS intelligence and
    selects management-relevant information that may be
    supplied to the OpenAI reasoning layer.

    Raw General Ledger transactions and other large
    source datasets are intentionally excluded.
    """

    MAX_ITEMS = 5

    def __init__(
        self,
        workspace_service: WorkspaceService,
        financial_model_service: FinancialModelService,
    ) -> None:
        self.workspace_service = workspace_service
        self.financial_model_service = (
            financial_model_service
        )

    def build(
        self,
        organisation_id: str,
    ) -> dict[str, Any]:
        """
        Build compact verified CFO context for one
        organization.
        """

        workspace = (
            self.workspace_service
            .get_workspace_by_organisation(
                organisation_id=organisation_id
            )
        )

        if workspace is None:
            return {
                "status": "not_available",
                "organisation_id": organisation_id,
                "context": {},
                "available_sections": [],
                "missing_sections": [],
                "source_files": {},
            }

        financial_model_folder = Path(
            workspace["paths"][
                "financial_model"
            ]
        )

        # --------------------------------------------------
        # Load only validated persisted AI-FOS outputs
        # --------------------------------------------------

        financial_facts = self._load(
            financial_model_folder,
            "financial_facts.json",
            {},
        )

        financial_trends = self._load(
            financial_model_folder,
            "financial_trends.json",
            {},
        )

        financial_forecast = self._load(
            financial_model_folder,
            "financial_forecast.json",
            {},
        )

        cash_flow = self._load(
            financial_model_folder,
            "cash_flow.json",
            {},
        )

        liquidity = self._load(
            financial_model_folder,
            "liquidity.json",
            {},
        )

        financial_health = self._load(
            financial_model_folder,
            "financial_health.json",
            {},
        )

        risk_assessment = self._load(
            financial_model_folder,
            "risk_assessment.json",
            [],
        )

        forward_risks = self._load(
            financial_model_folder,
            "forward_risks.json",
            [],
        )

        financial_opportunities = self._load(
            financial_model_folder,
            "financial_opportunities.json",
            [],
        )

        cfo_recommendations = self._load(
            financial_model_folder,
            "cfo_recommendations.json",
            [],
        )

        executive_decision_intelligence = self._load(
            financial_model_folder,
            "executive_decision_intelligence.json",
            {},
        )        

        executive_decision_intelligence = self._load(
            financial_model_folder,
            "executive_decision_intelligence.json",
            {},
        )        

        funding_gap = self._load(
            financial_model_folder,
            "funding_gap.json",
            {},
        )

        intelligence_hub = self._load(
            financial_model_folder,
            "intelligence_hub.json",
            {},
        )

        budget_dashboard = (
            intelligence_hub.get(
                "facts",
                {},
            ).get(
                "budget_dashboard",
                {},
            )
            or {}
        )

        # --------------------------------------------------
        # Build compact management context
        # --------------------------------------------------

        context: dict[str, Any] = {}

        if financial_facts:
            context[
                "financial_facts"
            ] = self._compact_financial_facts(
                financial_facts
            )

        if liquidity:
            context[
                "liquidity"
            ] = self._compact_liquidity(
                liquidity
            )

        if cash_flow:
            context[
                "cash_flow"
            ] = self._compact_cash_flow(
                cash_flow
            )

        if financial_health:
            context[
                "financial_health"
            ] = self._compact_financial_health(
                financial_health
            )

        if budget_dashboard:
            context[
                "budget"
            ] = self._compact_budget_dashboard(
                budget_dashboard
            )

        if funding_gap:
            context[
                "funding_gap"
            ] = self._compact_funding_gap(
                funding_gap
            )

        if financial_trends:
            context[
                "financial_trends"
            ] = self._compact_financial_trends(
                financial_trends
            )

        if financial_forecast:
            context[
                "financial_forecast"
            ] = self._compact_financial_forecast(
                financial_forecast
            )

        if risk_assessment:
            context[
                "current_risks"
            ] = self._compact_list(
                risk_assessment
            )

        if forward_risks:
            context[
                "forward_risks"
            ] = self._compact_list(
                forward_risks
            )

        if financial_opportunities:
            context[
                "financial_opportunities"
            ] = self._compact_list(
                financial_opportunities
            )

        if cfo_recommendations:
            context[
                "cfo_recommendations"
            ] = self._compact_list(
                cfo_recommendations
            )

        if executive_decision_intelligence:
            context[
                "executive_decision_intelligence"
            ] = (
                executive_decision_intelligence
            )            

        if executive_decision_intelligence:
            context[
                "executive_decision_intelligence"
            ] = (
                executive_decision_intelligence
            )            

        source_files = {
            "financial_facts": (
                "financial_facts.json"
            ),
            "liquidity": "liquidity.json",
            "cash_flow": "cash_flow.json",
            "financial_health": (
                "financial_health.json"
            ),
            "budget": "intelligence_hub.json",
            "funding_gap": "funding_gap.json",
            "financial_trends": (
                "financial_trends.json"
            ),
            "financial_forecast": (
                "financial_forecast.json"
            ),
            "current_risks": (
                "risk_assessment.json"
            ),
            "forward_risks": (
                "forward_risks.json"
            ),
            "financial_opportunities": (
                "financial_opportunities.json"
            ),
            "cfo_recommendations": (
                "cfo_recommendations.json"
            ),
            "executive_decision_intelligence": (
                "executive_decision_intelligence.json"
            ),            
        }

        available_sections = list(
            context.keys()
        )

        missing_sections = [
            section
            for section in source_files
            if section not in context
        ]

        return {
            "status": (
                "available"
                if context
                else "not_available"
            ),
            "organisation_id": organisation_id,
            "context": context,
            "available_sections": (
                available_sections
            ),
            "missing_sections": (
                missing_sections
            ),
            "source_files": {
                section: filename
                for section, filename
                in source_files.items()
                if section in context
            },
            "trust": {
                "financial_source": (
                    "validated_ai_fos_outputs"
                ),
                "raw_general_ledger_included": False,
                "financial_recalculation_performed": False,
                "max_items_per_list": (
                    self.MAX_ITEMS
                ),
            },
        }

    def _load(
        self,
        financial_model_folder: Path,
        filename: str,
        default: Any,
    ) -> Any:
        value = (
            self.financial_model_service
            .load_json(
                financial_model_folder=(
                    financial_model_folder
                ),
                filename=filename,
            )
        )

        if value is None:
            return default

        return value

    @staticmethod
    def _compact_financial_facts(
        financial_facts: dict[str, Any],
    ) -> dict[str, Any]:
        keys = [
            "revenue",
            "expenses",
            "net_profit",
            "assets",
            "liabilities",
            "equity",
            "difference",
        ]

        return {
            key: financial_facts.get(key)
            for key in keys
            if key in financial_facts
        }

    @staticmethod
    def _compact_liquidity(
        liquidity: dict[str, Any],
    ) -> dict[str, Any]:
        keys = [
            "available_cash",
            "blocked_cash",
            "total_cash",
            "cash_runway_months",
            "average_monthly_operating_expenses",
            "runway_basis",
        ]

        return {
            key: liquidity.get(key)
            for key in keys
            if key in liquidity
        }

    @staticmethod
    def _compact_cash_flow(
        cash_flow: dict[str, Any],
    ) -> dict[str, Any]:
        keys = [
            "operating_activities",
            "investing_activities",
            "financing_activities",
            "net_change_in_cash",
        ]

        return {
            key: cash_flow.get(key)
            for key in keys
            if key in cash_flow
        }

    @staticmethod
    def _compact_financial_health(
        financial_health: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "score": financial_health.get(
                "score"
            ),
            "maximum": financial_health.get(
                "maximum"
            ),
            "rating": financial_health.get(
                "rating"
            ),
            "categories": financial_health.get(
                "categories",
                {},
            ),
        }

    @staticmethod
    def _compact_budget_dashboard(
        budget_dashboard: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "executive_summary": (
                budget_dashboard.get(
                    "executive_summary",
                    {},
                )
                or {}
            ),
            "budget_health": (
                budget_dashboard.get(
                    "budget_health",
                    {},
                )
                or {}
            ),
            "portfolio_control": (
                budget_dashboard.get(
                    "portfolio_control",
                    {},
                )
                or {}
            ),
            "alerts": (
                budget_dashboard.get(
                    "alerts",
                    [],
                )
                or []
            )[:5],
            "cfo_insights": (
                budget_dashboard.get(
                    "cfo_insights",
                    [],
                )
                or []
            )[:5],
        }

    @staticmethod
    def _compact_funding_gap(
        funding_gap: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "summary": (
                funding_gap.get(
                    "summary",
                    {},
                )
                or {}
            )
        }

    @staticmethod
    def _compact_financial_trends(
        financial_trends: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "latest_month_comparison": (
                financial_trends.get(
                    "latest_month_comparison",
                    {},
                )
                or {}
            ),
            "latest_year_comparison": (
                financial_trends.get(
                    "latest_year_comparison",
                    {},
                )
                or {}
            ),
        }

    @staticmethod
    def _compact_financial_forecast(
        financial_forecast: dict[str, Any],
    ) -> dict[str, Any]:
        keys = [
            "status",
            "reason",
            "forecast_horizon_months",
            "forecast_totals",
            "baseline",
            "confidence",
            "methodology_description",
        ]

        return {
            key: financial_forecast.get(key)
            for key in keys
            if key in financial_forecast
        }

    def _compact_list(
        self,
        items: Any,
    ) -> list[Any]:
        if not isinstance(
            items,
            list,
        ):
            return []

        return items[
            : self.MAX_ITEMS
        ]