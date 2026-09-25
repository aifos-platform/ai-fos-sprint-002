from pathlib import Path
from typing import Any

from app.engines.organization_knowledge.organization_knowledge_reader import (
    OrganizationKnowledgeReader,
)
from app.engines.data_intelligence.question_classifier import (
    QuestionClassifier,
)
from app.services.workspace_service import WorkspaceService
from app.services.financial_model_service import (
    FinancialModelService,
)
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService,
)
import re

from app.services.financial_scenarios import (
    generate_financial_scenario,
)

from app.services.scenario_decision_intelligence import (
    generate_scenario_decision_intelligence,
)

from app.services.funding_scenarios import (
    generate_funding_scenario,
)
from app.services.scenario_comparison_intelligence import (
    generate_scenario_comparison_intelligence,
)
from app.services.scenario_history import (
    ScenarioHistoryService,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)
from app.services.cfo_action_command import (
    CFOActionCommandService,
)
from app.services.cfo_action_command_parser import (
    CFOActionCommandParser,
)
from app.services.financial_intelligence_history import (
    FinancialIntelligenceHistoryService,
)

class AIQuestionEngine:
    """
    Route AI-FOS questions to verified financial
    intelligence.

    The QuestionClassifier translates natural-language
    wording into stable AI-FOS intents.

    This engine then retrieves the relevant deterministic
    AI-FOS output and constructs an evidence-based answer.

    The engine must not manufacture financial calculations
    that do not already exist in verified AI-FOS outputs.
    """

    FINANCIAL_FACT_INTENTS = {
        "revenue",
        "expenses",
        "net_profit",
        "assets",
        "liabilities",
        "equity",
    }

    FINANCIAL_TREND_INTENTS = {
        "revenue_trend",
        "expense_trend",
        "net_result_trend",
        "financial_trend_summary",
    }

    FINANCIAL_FORECAST_INTENTS = {
        "revenue_forecast",
        "expense_forecast",
        "net_result_forecast",
        "financial_forecast_summary",
    }

    FINANCIAL_SCENARIO_INTENTS = {
        "revenue_scenario",
        "expense_scenario",
        "combined_scenario",
        "financial_scenario_summary",
    }

    SAVED_SCENARIO_INTENTS = {
        "saved_scenario_list",
        "saved_scenario_comparison",
    }    

    FUNDING_SCENARIO_INTENTS = {
        "expected_funding_change_scenario",
        "expected_funding_failure_scenario",
        "expected_funding_basis_scenario",
    }

    CASH_FLOW_INTENTS = {
        "operating_cash_flow",
        "investing_cash_flow",
        "financing_cash_flow",
        "net_change_in_cash",
    }

    CASH_INTENTS = {
        "cash_position",
        "blocked_cash",
    }

    LIQUIDITY_INTENTS = {
        "cash_runway",
    }

    PERIOD_INTENTS = {
        "data_period",
        "latest_transaction_date",
        "earliest_transaction_date",
        "reporting_date",
        "date_quality",
        "future_transactions",
    }

    FINANCIAL_HEALTH_INTENTS = {
        "financial_health",
        "financial_health_explanation",
    }

    RISK_INTENTS = {
        "risk_summary",
        "high_risks",
        "immediate_risk",
        "liquidity_risks",
        "budget_risks",
        "funding_risks",
    }

    FORWARD_RISK_INTENTS = {
        "forward_risk_summary",
        "forward_high_risks",
        "forward_funding_risks",
        "forward_operating_risks",
    }

    FINANCIAL_OPPORTUNITY_INTENTS = {
        "financial_opportunity_summary",
        "high_financial_opportunities",
        "funding_opportunities",
        "liquidity_opportunities",
    }

    RECOMMENDATION_INTENTS = {
        "recommendation_summary",
        "priority_actions",
        "funding_gap_actions",
        "finance_meeting_agenda",
    }

    EXECUTIVE_DECISION_INTENTS = {
        "executive_priority_summary",
    }

    HISTORICAL_CHANGE_INTENTS = {
        "historical_change_summary",
        "financial_position_change",
        "risk_change_summary",
        "new_risks_since_previous",
        "resolved_risks_since_previous",
    }

    HISTORICAL_DECISION_INTENTS = {
        "historical_management_priority_summary",
    }        

    CFO_ACTION_PLAN_INTENTS = {
        "action_plan_summary",
        "overdue_actions",
        "due_soon_actions",
        "blocked_actions",
        "unassigned_high_priority_actions",
    }

    CFO_ACTION_ESCALATION_INTENTS = {
        "action_escalation_summary",
        "critical_action_followups",
    }

    CFO_ACTION_PERFORMANCE_INTENTS = {
        "action_performance_summary",
        "reopened_action_patterns",
        "repeated_blocking_patterns",
        "ownership_change_patterns",
        "due_date_change_patterns",
    }                

    FUNDING_INTENTS = {
        "funding_gap",
        "funding_coverage",
        "unfunded_requirements",
        "secured_funding_total",
        "eligible_secured_funding",
        "funding_evidence",
    }

    CORE_COST_COVERAGE_INTENTS = {
        "core_cost_coverage_summary",
        "indirect_recovery_status",
        "core_cost_gap",
        "core_cost_coverage_sources",
    }

    GRANT_INTENTS = {
        "grant_attention",
        "grant_remaining_budget",
        "grant_high_utilization",
        "grant_spending_without_budget",
        "grant_budget_without_spending",
        "grant_funding_budget_issues",
        "grant_portfolio_summary",
    }

    BUDGET_INTENTS = {
        "portfolio_total_budget",
        "portfolio_budget_utilization",
        "portfolio_budget_variance",
        "portfolio_budget_remaining",
        "portfolio_budget_position",
        "unbudgeted_actual",
        "over_budget_count",
        "portfolio_budget_summary",
        "budget_performance_summary",
        "budget_dimension_drilldown",
    }

    ORGANIZATION_INTENTS = {
        "donor_count",
        "currency",
        "transaction_count",
        "account_count",
        "program_count",
        "fund_count",
        "organization_summary",
    }

    def __init__(
        self,
        workspace_service: WorkspaceService,
        knowledge_reader: OrganizationKnowledgeReader,
        financial_intelligence_service: FinancialIntelligenceService,
        financial_model_service: FinancialModelService,
    ) -> None:

        self.workspace_service = workspace_service
        self.knowledge_reader = knowledge_reader
        self.financial_intelligence_service = financial_intelligence_service
        self.financial_model_service = financial_model_service
        self.question_classifier = QuestionClassifier()

    def answer(
        self,
        question: str,
        organisation_id: str,
    ) -> dict[str, Any]:
        """
        Answer an AI-FOS financial question using
        verified organization and financial-model data.
        """
        # --------------------------------------------------
        # Deterministic CFO action command parsing
        # --------------------------------------------------

        cfo_action_command: dict[str, Any] | None = None

        try:
            cfo_action_command = (
                CFOActionCommandParser.parse(
                    question
                )
            )

        except ValueError:
            cfo_action_command = None

        classification = self.question_classifier.classify(
            question=question,
        )

        intent = classification.get(
            "intent",
            "unknown",
        )

        domain = classification.get(
            "domain",
            "unknown",
        )

        if cfo_action_command is not None:
            intent = "cfo_action_command"
            domain = "management"        

        # --------------------------------------------------
        # Safe unknown-question handling
        # --------------------------------------------------

        if intent == "unknown":

            return {
                "status": "unsupported",
                "question": question,
                "organisation_id": organisation_id,
                "intent": intent,
                "domain": domain,
                "answer": (
                    "AI-FOS cannot currently answer this "
                    "question from the available verified "
                    "financial intelligence. Try asking about "
                    "financial health, cash, liquidity, budget, "
                    "funding, risks, recommendations, revenue, "
                    "expenses, assets, liabilities, or other "
                    "supported financial information."
                ),
                "knowledge_used": False,
                "financial_data_used": False,
            }

        # --------------------------------------------------
        # Workspace
        # --------------------------------------------------

        workspace = self.workspace_service.get_workspace_by_organisation(
            organisation_id=organisation_id
        )

        if workspace is None:

            return {
                "status": "not_available",
                "question": question,
                "organisation_id": organisation_id,
                "intent": intent,
                "domain": domain,
                "answer": ("I could not find a workspace " "for this organization."),
                "knowledge_used": False,
                "financial_data_used": False,
            }

        ai_knowledge_folder = Path(workspace["paths"]["ai_knowledge"])

        financial_model_folder = Path(workspace["paths"]["financial_model"])

        # --------------------------------------------------
        # Organization knowledge
        # --------------------------------------------------

        knowledge = self.knowledge_reader.get_summary(folder=ai_knowledge_folder)

        if knowledge.get("status") != "available":

            return {
                "status": "not_available",
                "question": question,
                "organisation_id": organisation_id,
                "intent": intent,
                "domain": domain,
                "answer": ("Organization knowledge is " "not available yet."),
                "knowledge_used": False,
                "financial_data_used": False,
            }

        organisation_name = knowledge.get("organisation_name") or organisation_id

        currency = knowledge.get("currency") or ""

        # --------------------------------------------------
        # CFO ACTION MANAGEMENT COMMAND
        # --------------------------------------------------

        if cfo_action_command is not None:

            command = str(
                cfo_action_command.get(
                    "command",
                    "",
                )
                or ""
            ).strip()

            action_reference = str(
                cfo_action_command.get(
                    "action_reference",
                    "",
                )
                or ""
            ).strip()

            try:

                if command == "assign":

                    updated_action = (
                        CFOActionCommandService.assign(
                            financial_model_folder=(
                                financial_model_folder
                            ),
                            action_reference=action_reference,
                            owner=cfo_action_command.get(
                                "owner"
                            ),
                            history_actor=None,
                            history_source="ask_cfo",
                        )
                    )

                elif command == "unassign":

                    updated_action = (
                        CFOActionCommandService.unassign(
                            financial_model_folder=(
                                financial_model_folder
                            ),
                            action_reference=action_reference,
                            history_actor=None,
                            history_source="ask_cfo",
                        )
                    )

                elif command == "set_due_date":

                    updated_action = (
                        CFOActionCommandService.set_due_date(
                            financial_model_folder=(
                                financial_model_folder
                            ),
                            action_reference=action_reference,
                            due_date=cfo_action_command.get(
                                "due_date"
                            ),
                            history_actor=None,
                            history_source="ask_cfo",
                        )
                    )

                elif command == "clear_due_date":

                    updated_action = (
                        CFOActionCommandService.clear_due_date(
                            financial_model_folder=(
                                financial_model_folder
                            ),
                            action_reference=action_reference,
                            history_actor=None,
                            history_source="ask_cfo",
                        )
                    )

                elif command == "start":

                    updated_action = (
                        CFOActionCommandService.start(
                            financial_model_folder=(
                                financial_model_folder
                            ),
                            action_reference=action_reference,
                            history_actor=None,
                            history_source="ask_cfo",
                        )
                    )

                elif command == "update_progress":

                    updated_action = (
                        CFOActionCommandService.update_progress(
                            financial_model_folder=(
                                financial_model_folder
                            ),
                            action_reference=action_reference,
                            progress_percentage=(
                                cfo_action_command.get(
                                    "progress_percentage"
                                )
                            ),
                            history_actor=None,
                            history_source="ask_cfo",
                        )
                    )

                elif command == "block":

                    updated_action = (
                        CFOActionCommandService.block(
                            financial_model_folder=(
                                financial_model_folder
                            ),
                            action_reference=action_reference,
                            management_notes=(
                                cfo_action_command.get(
                                    "management_notes"
                                )
                            ),
                            history_actor=None,
                            history_source="ask_cfo",
                        )
                    )

                elif command == "unblock":

                    updated_action = (
                        CFOActionCommandService.unblock(
                            financial_model_folder=(
                                financial_model_folder
                            ),
                            action_reference=action_reference,
                            history_actor=None,
                            history_source="ask_cfo",
                        )
                    )

                elif command == "complete":

                    updated_action = (
                        CFOActionCommandService.complete(
                            financial_model_folder=(
                                financial_model_folder
                            ),
                            action_reference=action_reference,
                            management_notes=(
                                cfo_action_command.get(
                                    "management_notes"
                                )
                            ),
                            history_actor=None,
                            history_source="ask_cfo",
                        )
                    )

                elif command == "reopen":

                    updated_action = (
                        CFOActionCommandService.reopen(
                            financial_model_folder=(
                                financial_model_folder
                            ),
                            action_reference=action_reference,
                            history_actor=None,
                            history_source="ask_cfo",
                        )
                    )

                elif command == "cancel":

                    updated_action = (
                        CFOActionCommandService.cancel(
                            financial_model_folder=(
                                financial_model_folder
                            ),
                            action_reference=action_reference,
                            management_notes=(
                                cfo_action_command.get(
                                    "management_notes"
                                )
                            ),
                            history_actor=None,
                            history_source="ask_cfo",
                        )
                    )

                elif command == "update_notes":

                    updated_action = (
                        CFOActionCommandService.update_notes(
                            financial_model_folder=(
                                financial_model_folder
                            ),
                            action_reference=action_reference,
                            management_notes=(
                                cfo_action_command.get(
                                    "management_notes"
                                )
                            ),
                            history_actor=None,
                            history_source="ask_cfo",
                        )
                    )

                else:
                    raise ValueError(
                        "Unsupported CFO action command."
                    )

            except ValueError as exc:

                return {
                    "status": "not_executed",
                    "question": question,
                    "organisation_id": organisation_id,
                    "intent": "cfo_action_command",
                    "domain": "management",
                    "answer": str(exc),
                    "knowledge_used": True,
                    "financial_data_used": False,
                    "management_state_changed": False,
                }

            action_title = str(
                updated_action.get(
                    "title",
                    "Management action",
                )
                or "Management action"
            )

            status = str(
                updated_action.get(
                    "status",
                    "open",
                )
                or "open"
            ).replace(
                "_",
                " ",
            )

            owner = str(
                updated_action.get(
                    "owner",
                    "",
                )
                or ""
            ).strip()

            due_date = str(
                updated_action.get(
                    "due_date",
                    "",
                )
                or ""
            ).strip()

            progress = float(
                updated_action.get(
                    "progress_percentage",
                    0,
                )
                or 0
            )

            confirmation = (
                f"CFO management action updated: "
                f"{action_title}. "
                f"Status: {status}. "
                f"Progress: {progress:g}%."
            )

            if owner:
                confirmation += (
                    f" Owner: {owner}."
                )

            if due_date:
                confirmation += (
                    f" Due: {due_date}."
                )

            return {
                "status": "success",
                "question": question,
                "organisation_id": organisation_id,
                "intent": "cfo_action_command",
                "domain": "management",
                "answer": confirmation,
                "knowledge_used": True,
                "financial_data_used": False,
                "management_state_changed": True,
                "action": updated_action,
            }

        # --------------------------------------------------
        # Verified financial-model artifacts
        # --------------------------------------------------

        financial_facts = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="financial_facts.json",
            )
            or {}
        )

        financial_trends = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="financial_trends.json",
            )
            or {}
        )

        financial_forecast = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="financial_forecast.json",
            )
            or {}
        )

        expected_funding_intelligence = (
            self.financial_model_service.load_json(
                financial_model_folder=financial_model_folder,
                filename="expected_funding_intelligence.json",
            )
            or {}
        )

        cash_flow = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="cash_flow.json",
            )
            or {}
        )

        liquidity = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="liquidity.json",
            )
            or {}
        )

        gl_date_quality = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="gl_date_quality.json",
            )
            or {}
        )

        financial_health = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="financial_health.json",
            )
            or {}
        )

        risk_assessment = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="risk_assessment.json",
            )
            or []
        )

        forward_risks = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="forward_risks.json",
            )
            or []
        )

        financial_opportunities = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="financial_opportunities.json",
            )
            or []
        )

        cfo_recommendations = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="cfo_recommendations.json",
            )
            or []
        )

        executive_decision_intelligence = (
            self.financial_model_service.load_json(
                financial_model_folder=financial_model_folder,
                filename=(
                    "executive_decision_intelligence.json"
                ),
            )
            or {}
        )

        historical_change_analysis = (
            FinancialIntelligenceHistoryService.compare_latest(
                financial_model_folder
            )
        )

        historical_decision_intelligence = (
            FinancialIntelligenceHistoryService
            .build_latest_historical_decision(
                financial_model_folder
            )
        )                 

        cfo_action_monitoring = (
            CFOActionPlanService.build_monitoring(
                financial_model_folder=(
                    financial_model_folder
                ),
            )
        )

        cfo_action_escalation = (
            CFOActionPlanService.build_escalation(
                financial_model_folder=(
                    financial_model_folder
                ),
            )
        )

        cfo_action_performance = (
            CFOActionPlanService.build_performance(
                financial_model_folder=(
                    financial_model_folder
                ),
            )
        )                               

        funding_gap = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="funding_gap.json",
            )
            or {}
        )

        core_cost_coverage = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="core_cost_coverage_intelligence.json",
            )
            or {}
        )

        intelligence_hub = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="intelligence_hub.json",
            )
            or {}
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
        # Availability controls
        # --------------------------------------------------

        if intent in self.FINANCIAL_FACT_INTENTS and not financial_facts:

            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=(
                    "Financial facts are not available yet. "
                    "Process the General Ledger first."
                ),
            )

        if intent in self.FINANCIAL_TREND_INTENTS and not financial_trends:

            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=(
                    "Financial trend intelligence is not "
                    "available yet. Process the General Ledger "
                    "first."
                ),
            )

        if intent in self.FINANCIAL_FORECAST_INTENTS and not financial_forecast:

            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=(
                    "Financial Forecast Intelligence is not "
                    "available yet. Process sufficient General "
                    "Ledger history first."
                ),
            )

        if intent in self.CASH_FLOW_INTENTS and not cash_flow:

            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=("Cash-flow information is not " "available yet."),
            )

        if intent in self.CASH_INTENTS and not liquidity:

            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=("Cash-position information is " "not available yet."),
            )

        if intent in self.LIQUIDITY_INTENTS and not liquidity:

            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=("Liquidity information is " "not available yet."),
            )

        if intent in self.FINANCIAL_HEALTH_INTENTS and not financial_health:

            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=("Financial Health information is " "not available yet."),
            )

        if intent in self.RISK_INTENTS and not risk_assessment:

            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=("Risk assessment is not available yet."),
            )

        if (
            intent in self.EXECUTIVE_DECISION_INTENTS
            and (
                not executive_decision_intelligence
                or executive_decision_intelligence.get(
                    "status"
                )
                != "available"
            )
        ):
            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=(
                    "Executive Decision Intelligence is not "
                    "available yet. Process the organization's "
                    "verified financial intelligence first."
                ),
            )

        if (
            intent in self.HISTORICAL_CHANGE_INTENTS
            and (
                not historical_change_analysis
                or historical_change_analysis.get(
                    "status"
                )
                != "available"
            )
        ):
            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=(
                    "Historical Financial Intelligence is not "
                    "available yet. AI-FOS needs at least two "
                    "completed financial processing snapshots "
                    "before it can compare financial movement."
                ),
            )

        if (
            intent in self.HISTORICAL_DECISION_INTENTS
            and (
                not historical_decision_intelligence
                or historical_decision_intelligence.get(
                    "status"
                )
                != "available"
            )
        ):
            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=(
                    "Historical Decision Intelligence is not "
                    "available yet. AI-FOS needs at least two "
                    "completed verified financial processing "
                    "snapshots before it can identify management "
                    "priorities from financial changes."
                ),
            )                

        if intent in self.RECOMMENDATION_INTENTS and not cfo_recommendations:

            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=("CFO recommendations are not " "available yet."),
            )

        if intent in self.FUNDING_INTENTS and not funding_gap:

            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=(
                    "Funding Gap intelligence is not "
                    "available yet. Load the required "
                    "budget information and process the "
                    "General Ledger first."
                ),
            )

        if (
            intent in self.CORE_COST_COVERAGE_INTENTS
            and not core_cost_coverage
        ):
            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=(
                    "Core Cost Coverage intelligence is not "
                    "available yet. Load the required core cost "
                    "coverage information first."
                ),
            )

        if (
            intent in self.CORE_COST_COVERAGE_INTENTS
            and not core_cost_coverage
        ):
            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=(
                    "Core Cost Coverage intelligence is not "
                    "available yet. Load the required core cost "
                    "coverage information first."
                ),
            )

        if intent in self.BUDGET_INTENTS and not budget_dashboard:

            return self._not_available(
                question=question,
                organisation_id=organisation_id,
                intent=intent,
                domain=domain,
                answer=(
                    "Budget intelligence is not available yet. "
                    "Load the Budget and process the "
                    "General Ledger first."
                ),
            )

        # ==================================================
        # FUNDING INTELLIGENCE
        # ==================================================

        elif intent in self.FUNDING_INTENTS:

            funding_summary = (
                funding_gap.get(
                    "summary",
                    {},
                )
                or {}
            )

            remaining_requirement = self._to_float(
                funding_summary.get("remaining_requirement")
            )

            funding_gap_amount = self._to_float(funding_summary.get("funding_gap"))

            applied_secured_funding = self._to_float(
                funding_summary.get("applied_secured_funding")
            )

            eligible_secured_funding = self._to_float(
                funding_summary.get(
                    "eligible_secured_funding",
                    applied_secured_funding,
                )
            )

            gross_remaining_secured_funding = self._to_float(
                funding_summary.get("gross_remaining_secured_funding")
            )

            coverage_percentage = self._to_float(
                funding_summary.get("applied_coverage_percentage")
            )

            matched_requirement_count = int(
                funding_summary.get(
                    "matched_requirement_count",
                    0,
                )
                or 0
            )

            unmatched_requirement_count = int(
                funding_summary.get(
                    "unmatched_requirement_count",
                    0,
                )
                or 0
            )

            unfunded_requirement_count = int(
                funding_summary.get(
                    "unfunded_requirement_count",
                    0,
                )
                or 0
            )

            secured_without_budget_line = self._to_float(
                funding_summary.get(
                    ("secured_funding_without_" "budget_line_allocation")
                )
            )

            # --------------------------------------------------
            # Funding Gap diagnostics
            # --------------------------------------------------

            period_ineligible_exposure = self._to_float(
                funding_summary.get("period_ineligible_funding_exposure")
            )

            period_unknown_exposure = self._to_float(
                funding_summary.get("period_unknown_funding_exposure")
            )

            dimension_incompatible_exposure = self._to_float(
                funding_summary.get("dimension_incompatible_funding_exposure")
            )

            period_ineligible_count = int(
                self._to_float(
                    funding_summary.get("requirements_with_period_ineligible_funding")
                )
            )

            period_unknown_count = int(
                self._to_float(
                    funding_summary.get("requirements_with_period_unknown_funding")
                )
            )

            dimension_incompatible_count = int(
                self._to_float(
                    funding_summary.get(
                        "requirements_with_dimension_incompatible_funding"
                    )
                )
            )

            diagnostic_parts: list[str] = []

            if period_ineligible_exposure > 0:
                diagnostic_parts.append(
                    (
                        f"{period_ineligible_exposure:,.2f} "
                        f"{currency} of requirement-level secured "
                        f"funding exposure is outside the applicable "
                        f"grant period, affecting "
                        f"{period_ineligible_count} requirement(s)."
                    )
                )

            if period_unknown_exposure > 0:
                diagnostic_parts.append(
                    (
                        f"{period_unknown_exposure:,.2f} "
                        f"{currency} of requirement-level secured "
                        f"funding exposure has missing or incomplete "
                        f"grant-period evidence, affecting "
                        f"{period_unknown_count} requirement(s)."
                    )
                )

            if dimension_incompatible_exposure > 0:
                diagnostic_parts.append(
                    (
                        f"{dimension_incompatible_exposure:,.2f} "
                        f"{currency} of requirement-level secured "
                        f"funding exposure has dimensions that "
                        f"conflict with the related requirements, "
                        f"affecting "
                        f"{dimension_incompatible_count} "
                        f"requirement(s)."
                    )
                )

            if diagnostic_parts:
                funding_diagnostic_text = " ".join(diagnostic_parts) + (
                    " These exposure amounts are "
                    "requirement-level diagnostics and must not "
                    "be added together or interpreted as unique "
                    "organization-wide secured funding."
                )
            else:
                funding_diagnostic_text = (
                    "AI-FOS currently identifies no grant-period "
                    "or dimensional eligibility conflicts affecting "
                    "secured funding."
                )

            # --------------------------------------------------
            # Funding Gap
            # --------------------------------------------------

            if intent == "funding_gap":

                answer = (
                    f"{organisation_name}'s current Funding Gap "
                    f"is {funding_gap_amount:,.2f} {currency}. "
                    f"Remaining identified requirements are "
                    f"{remaining_requirement:,.2f} {currency}, "
                    f"of which "
                    f"{applied_secured_funding:,.2f} {currency} "
                    f"of validated secured funding has been applied, "
                    f"covering {coverage_percentage:.2f}%. "
                    f"{funding_diagnostic_text}"
                )

            # --------------------------------------------------
            # Funding coverage
            # --------------------------------------------------

            elif intent == "funding_coverage":

                answer = (
                    f"Validated secured funding currently covers "
                    f"{coverage_percentage:.2f}% of "
                    f"{organisation_name}'s remaining identified "
                    f"requirements. "
                    f"{applied_secured_funding:,.2f} {currency} "
                    f"has been applied against "
                    f"{remaining_requirement:,.2f} {currency} "
                    f"of remaining requirements, leaving a "
                    f"Funding Gap of "
                    f"{funding_gap_amount:,.2f} {currency}. "
                    f"{funding_diagnostic_text}"
                )

            # --------------------------------------------------
            # Gross secured funding
            # --------------------------------------------------

            elif intent == "secured_funding_total":

                answer = (
                    f"{organisation_name} currently has "
                    f"{gross_remaining_secured_funding:,.2f} "
                    f"{currency} of gross remaining secured funding. "
                    f"Of this amount, "
                    f"{eligible_secured_funding:,.2f} {currency} "
                    f"is currently recognized as eligible under "
                    f"AI-FOS's validated funding rules, and "
                    f"{applied_secured_funding:,.2f} {currency} "
                    f"has been applied against remaining "
                    f"requirements. "
                    f"Gross secured funding should therefore not "
                    f"be interpreted as automatically available "
                    f"Funding Gap coverage. "
                    f"{funding_diagnostic_text}"
                )

            # --------------------------------------------------
            # Eligible secured funding
            # --------------------------------------------------

            elif intent == "eligible_secured_funding":

                answer = (
                    f"AI-FOS identifies "
                    f"{eligible_secured_funding:,.2f} {currency} "
                    f"of secured funding as eligible under the "
                    f"currently validated matching and eligibility "
                    f"rules. "
                    f"{applied_secured_funding:,.2f} {currency} "
                    f"has actually been applied to remaining "
                    f"requirements. "
                    f"Funding is not treated as automatically "
                    f"available when its grant-period eligibility "
                    f"or dimensional allocation cannot be validated. "
                    f"{funding_diagnostic_text}"
                )

            # --------------------------------------------------
            # Funding evidence
            # --------------------------------------------------

            elif intent == "funding_evidence":

                answer = (
                    f"{organisation_name} has "
                    f"{secured_without_budget_line:,.2f} "
                    f"{currency} of remaining secured funding "
                    f"without explicit internal Budget Line "
                    f"allocation available for automatic "
                    f"Funding Gap coverage. "
                    f"Gross remaining secured funding is "
                    f"{gross_remaining_secured_funding:,.2f} "
                    f"{currency}. "
                    f"AI-FOS only applies secured funding when "
                    f"the required eligibility and allocation "
                    f"evidence can be validated. "
                    f"{funding_diagnostic_text}"
                )

            # --------------------------------------------------
            # Unfunded requirements
            # --------------------------------------------------

            elif intent == "unfunded_requirements":

                funding_lines = (
                    funding_gap.get(
                        "lines",
                        [],
                    )
                    or []
                )

                uncovered_lines = [
                    line
                    for line in funding_lines
                    if self._to_float(line.get("funding_gap")) > 0
                ]

                uncovered_lines.sort(
                    key=lambda line: self._to_float(line.get("funding_gap")),
                    reverse=True,
                )

                top_uncovered = uncovered_lines[:5]

                if top_uncovered:

                    detail_text = " ".join(
                        (
                            f"{index + 1}. "
                            f"{line.get('budget_line_name') or line.get('code') or 'Unnamed requirement'}: "
                            f"{self._to_float(line.get('funding_gap')):,.2f} "
                            f"{currency} gap."
                        )
                        for index, line in enumerate(top_uncovered)
                    )

                    answer = (
                        f"{organisation_name} has "
                        f"{unfunded_requirement_count} "
                        f"requirement(s) classified as unfunded and "
                        f"{unmatched_requirement_count} "
                        f"requirement(s) without validated matched "
                        f"secured funding. "
                        f"The total Funding Gap is "
                        f"{funding_gap_amount:,.2f} {currency}. "
                        f"The largest uncovered requirements "
                        f"currently visible are: "
                        f"{detail_text} "
                        f"{funding_diagnostic_text}"
                    )

                else:

                    answer = (
                        f"AI-FOS identifies a total Funding Gap of "
                        f"{funding_gap_amount:,.2f} {currency}, "
                        f"but no detailed uncovered requirement "
                        f"records are currently available. "
                        f"{funding_diagnostic_text}"
                    )

        # ==================================================
        # GRANT INTELLIGENCE
        # ==================================================

        elif intent in self.CORE_COST_COVERAGE_INTENTS:

            core_cost_summary = (
                core_cost_coverage.get(
                    "summary",
                    {},
                )
                or {}
            )
            core_cost_lines = (
                core_cost_coverage.get(
                    "lines",
                    [],
                )
                or []
            )

            needed_core_cost = self._to_float(
                core_cost_summary.get("needed_core_cost")
            )
            direct_grant_coverage = self._to_float(
                core_cost_summary.get("direct_grant_coverage")
            )
            available_indirect_recovery = self._to_float(
                core_cost_summary.get("available_indirect_recovery")
            )
            allocated_indirect_recovery = self._to_float(
                core_cost_summary.get("allocated_indirect_recovery")
            )
            used_indirect_recovery = self._to_float(
                core_cost_summary.get("used_indirect_recovery")
            )
            unrestricted_core_funding = self._to_float(
                core_cost_summary.get("unrestricted_core_funding")
            )
            remaining_core_cost_gap = self._to_float(
                core_cost_summary.get("remaining_core_cost_gap")
            )
            core_cost_coverage_percentage = self._to_float(
                core_cost_summary.get("core_cost_coverage_percentage")
            )

            if intent == "core_cost_coverage_summary":
                answer = (
                    f"Core costs currently total "
                    f"{needed_core_cost:,.2f} {currency}. "
                    f"Direct grant coverage provides "
                    f"{direct_grant_coverage:,.2f} {currency}, "
                    f"management-allocated indirect recovery provides "
                    f"{allocated_indirect_recovery:,.2f} {currency}, "
                    f"and unrestricted/core funding provides "
                    f"{unrestricted_core_funding:,.2f} {currency}. "
                    f"The remaining Core Cost Gap is "
                    f"{remaining_core_cost_gap:,.2f} {currency}, "
                    f"with {core_cost_coverage_percentage:.2f}% "
                    f"of identified core costs covered."
                )

            elif intent == "indirect_recovery_status":
                answer = (
                    f"Indirect recovery currently has "
                    f"{available_indirect_recovery:,.2f} {currency} "
                    f"recovered/available, "
                    f"{allocated_indirect_recovery:,.2f} {currency} "
                    f"internally allocated by management, and "
                    f"{used_indirect_recovery:,.2f} {currency} "
                    f"actually used/charged."
                )

            elif intent == "core_cost_gap":

                answer = (
                    f"{organisation_name}'s remaining Core Cost Gap is "
                    f"{remaining_core_cost_gap:,.2f} {currency}. "
                    f"Current verified coverage is "
                    f"{core_cost_coverage_percentage:.2f}% of identified "
                    f"core costs."
                )

            elif intent == "core_cost_coverage_sources":

                source_parts = []

                source_groups = (
                    (
                        "Direct grant coverage",
                        "direct_grant_coverage_sources",
                    ),
                    (
                        "Management-allocated indirect recovery",
                        "indirect_recovery_allocation_sources",
                    ),
                    (
                        "Unrestricted/core funding",
                        "unrestricted_core_funding_sources",
                    ),
                )

                for line in core_cost_lines:
                    for source_label, source_key in source_groups:
                        for source in line.get(source_key, []) or []:
                            fund_code = source.get("fund_code") or "Unknown fund"
                            amount = self._to_float(source.get("amount"))
                            source_parts.append(
                                f"{source_label}: {fund_code} "
                                f"({amount:,.2f} {currency})"
                            )

                if source_parts:
                    answer = (
                        "Verified Core Cost Coverage sources are: "
                        + "; ".join(source_parts)
                        + "."
                    )
                else:
                    answer = (
                        "No detailed Core Cost Coverage source records "
                        "are currently available."
                    )

        # ==================================================
        # GRANT INTELLIGENCE
        # ==================================================

        elif intent in self.GRANT_INTENTS:

            grants = (
                self.financial_model_service.load_json(
                    financial_model_folder=(financial_model_folder),
                    filename="grants.json",
                )
                or {}
            )

            grant_diagnostics = (
                self.financial_model_service.load_json(
                    financial_model_folder=(financial_model_folder),
                    filename="grant_diagnostics.json",
                )
                or {}
            )

            actual_only_codes = set(
                grant_diagnostics.get(
                    "actual_only_grants",
                    [],
                )
                or []
            )

            grant_records = []

            for grant_code, grant_data in grants.items():

                if not isinstance(
                    grant_data,
                    dict,
                ):
                    continue

                grant_record = dict(grant_data)

                grant_record["code"] = grant_record.get("code") or grant_code

                grant_record["is_actual_only"] = (
                    grant_record["code"] in actual_only_codes
                )

                grant_records.append(grant_record)

            if intent == "grant_attention":

                attention_grants = [
                    grant
                    for grant in grant_records
                    if (
                        self._to_float(grant.get("utilization")) >= 90
                        or self._to_float(grant.get("remaining_budget")) < 0
                        or grant.get("is_actual_only") is True
                    )
                ]

                attention_grants.sort(
                    key=lambda grant: (
                        grant.get("is_actual_only") is False,
                        self._to_float(grant.get("utilization")),
                        -self._to_float(grant.get("remaining_budget")),
                    ),
                    reverse=True,
                )

                if attention_grants:

                    grant_text = " ".join(
                        (
                            f"{index + 1}. "
                            f"{grant.get('name') or grant.get('code') or 'Unknown grant'} "
                            f"({grant.get('code') or 'Unknown code'}): "
                            f"utilization "
                            f"{self._to_float(grant.get('utilization')):.2f}%, "
                            f"remaining budget "
                            f"{self._to_float(grant.get('remaining_budget')):,.2f} "
                            f"{currency}"
                            f"{' [actual activity without matched budget]' if grant.get('is_actual_only') else ''}."
                        )
                        for index, grant in enumerate(attention_grants[:10])
                    )

                    answer = (
                        f"The grants requiring financial attention "
                        f"for {organisation_name} are: "
                        f"{grant_text}"
                    )

                else:

                    answer = (
                        f"AI-FOS currently identifies no grants "
                        f"requiring immediate financial attention "
                        f"for {organisation_name}."
                    )

            elif intent == "grant_remaining_budget":

                grants_with_remaining_budget = [
                    grant
                    for grant in grant_records
                    if (
                        self._to_float(grant.get("revised_budget")) > 0
                        and self._to_float(grant.get("remaining_budget")) > 0
                    )
                ]

                grants_with_remaining_budget.sort(
                    key=lambda grant: self._to_float(grant.get("remaining_budget")),
                    reverse=True,
                )

                if grants_with_remaining_budget:

                    grant_text = " ".join(
                        (
                            f"{index + 1}. "
                            f"{grant.get('name') or grant.get('code')}: "
                            f"{self._to_float(grant.get('remaining_budget')):,.2f} "
                            f"{currency} remaining "
                            f"({self._to_float(grant.get('utilization')):.2f}% utilized)."
                        )
                        for index, grant in enumerate(grants_with_remaining_budget[:10])
                    )

                    answer = (
                        f"The grants with remaining budget "
                        f"for {organisation_name} are: "
                        f"{grant_text}"
                    )

                else:

                    answer = (
                        f"AI-FOS currently identifies no grants "
                        f"with positive remaining budget "
                        f"for {organisation_name}."
                    )

            elif intent == "grant_high_utilization":

                high_utilization_grants = [
                    grant
                    for grant in grant_records
                    if (
                        self._to_float(grant.get("revised_budget")) > 0
                        and self._to_float(grant.get("utilization")) >= 90
                    )
                ]

                high_utilization_grants.sort(
                    key=lambda grant: self._to_float(grant.get("utilization")),
                    reverse=True,
                )

                if high_utilization_grants:

                    grant_text = " ".join(
                        (
                            f"{index + 1}. "
                            f"{grant.get('name') or grant.get('code')}: "
                            f"{self._to_float(grant.get('utilization')):.2f}% utilized, "
                            f"{self._to_float(grant.get('remaining_budget')):,.2f} "
                            f"{currency} remaining."
                        )
                        for index, grant in enumerate(high_utilization_grants[:10])
                    )

                    answer = (
                        f"The grants with high utilization "
                        f"for {organisation_name} are: "
                        f"{grant_text}"
                    )

                else:

                    answer = (
                        f"AI-FOS currently identifies no grants "
                        f"with utilization of 90% or higher "
                        f"for {organisation_name}."
                    )

            elif intent == "grant_spending_without_budget":

                spending_without_budget = [
                    grant
                    for grant in grant_records
                    if (
                        self._to_float(grant.get("actual")) > 0
                        and self._to_float(grant.get("revised_budget")) <= 0
                    )
                ]

                spending_without_budget.sort(
                    key=lambda grant: self._to_float(grant.get("actual")),
                    reverse=True,
                )

                if spending_without_budget:

                    grant_text = " ".join(
                        (
                            f"{index + 1}. "
                            f"{grant.get('name') or grant.get('code')}: "
                            f"{self._to_float(grant.get('actual')):,.2f} "
                            f"{currency} of recorded spending "
                            f"with no identified revised budget."
                        )
                        for index, grant in enumerate(spending_without_budget[:10])
                    )

                    answer = (
                        f"{organisation_name} has "
                        f"{len(spending_without_budget)} grant(s) "
                        f"with recorded spending but no identified "
                        f"budget. "
                        f"{grant_text}"
                    )

                else:

                    answer = (
                        f"AI-FOS currently identifies no grants "
                        f"with recorded spending but no identified "
                        f"budget for {organisation_name}."
                    )

            elif intent == "grant_budget_without_spending":

                budget_without_spending = [
                    grant
                    for grant in grant_records
                    if (
                        self._to_float(grant.get("revised_budget")) > 0
                        and abs(self._to_float(grant.get("actual"))) < 0.01
                    )
                ]

                budget_without_spending.sort(
                    key=lambda grant: self._to_float(grant.get("revised_budget")),
                    reverse=True,
                )

                if budget_without_spending:

                    grant_text = " ".join(
                        (
                            f"{index + 1}. "
                            f"{grant.get('name') or grant.get('code')}: "
                            f"{self._to_float(grant.get('revised_budget')):,.2f} "
                            f"{currency} budget with no recorded "
                            f"spending."
                        )
                        for index, grant in enumerate(budget_without_spending[:10])
                    )

                    answer = (
                        f"{organisation_name} has "
                        f"{len(budget_without_spending)} grant(s) "
                        f"with an identified budget but no recorded "
                        f"spending. "
                        f"{grant_text}"
                    )

                else:

                    answer = (
                        f"AI-FOS currently identifies no grants "
                        f"with an identified budget but no recorded "
                        f"spending for {organisation_name}."
                    )

            elif intent == "grant_funding_budget_issues":

                issue_grants = []

                for grant in grant_records:

                    revised_budget = self._to_float(grant.get("revised_budget"))

                    actual = self._to_float(grant.get("actual"))

                    remaining_budget = self._to_float(grant.get("remaining_budget"))

                    utilization = self._to_float(grant.get("utilization"))

                    issues = []

                    if actual > 0 and revised_budget <= 0:
                        issues.append("spending without an identified budget")

                    if revised_budget > 0 and remaining_budget < 0:
                        issues.append("spending exceeds the identified budget")

                    elif revised_budget > 0 and utilization >= 90:
                        issues.append("high budget utilization")

                    if not issues:
                        continue

                    issue_grant = dict(grant)

                    issue_grant["issues"] = issues

                    issue_grants.append(issue_grant)

                issue_grants.sort(
                    key=lambda grant: (
                        self._to_float(grant.get("remaining_budget")) < 0,
                        self._to_float(grant.get("utilization")),
                        self._to_float(grant.get("actual")),
                    ),
                    reverse=True,
                )

                if issue_grants:

                    grant_text = " ".join(
                        (
                            f"{index + 1}. "
                            f"{grant.get('name') or grant.get('code')}: "
                            f"{'; '.join(grant.get('issues', []))}. "
                            f"Budget "
                            f"{self._to_float(grant.get('revised_budget')):,.2f} "
                            f"{currency}, actual "
                            f"{self._to_float(grant.get('actual')):,.2f} "
                            f"{currency}, remaining "
                            f"{self._to_float(grant.get('remaining_budget')):,.2f} "
                            f"{currency}."
                        )
                        for index, grant in enumerate(issue_grants[:10])
                    )

                    answer = (
                        f"AI-FOS identifies "
                        f"{len(issue_grants)} grant(s) with "
                        f"potential funding or budget issues for "
                        f"{organisation_name}. "
                        f"{grant_text}"
                    )

                else:

                    answer = (
                        f"AI-FOS currently identifies no material "
                        f"grant funding or budget issues for "
                        f"{organisation_name} under the current "
                        f"validated rules."
                    )

            elif intent == "grant_portfolio_summary":

                budgeted_grants = [
                    grant
                    for grant in grant_records
                    if self._to_float(grant.get("revised_budget")) > 0
                ]

                total_budget = sum(
                    self._to_float(grant.get("revised_budget"))
                    for grant in budgeted_grants
                )

                total_actual = sum(
                    self._to_float(grant.get("actual")) for grant in budgeted_grants
                )

                total_remaining = sum(
                    self._to_float(grant.get("remaining_budget"))
                    for grant in budgeted_grants
                )

                portfolio_utilization = (
                    (total_actual / total_budget) * 100 if total_budget > 0 else 0.0
                )

                over_budget_grants = [
                    grant
                    for grant in budgeted_grants
                    if self._to_float(grant.get("remaining_budget")) < 0
                ]

                high_utilization_grants = [
                    grant
                    for grant in budgeted_grants
                    if self._to_float(grant.get("utilization")) >= 90
                ]

                actual_only_grants = [
                    grant
                    for grant in grant_records
                    if (
                        self._to_float(grant.get("actual")) > 0
                        and self._to_float(grant.get("revised_budget")) <= 0
                    )
                ]

                answer = (
                    f"{organisation_name}'s grant portfolio "
                    f"currently contains "
                    f"{len(budgeted_grants)} grant(s) with "
                    f"identified budgets totaling "
                    f"{total_budget:,.2f} {currency}. "
                    f"Recorded spending against those grants is "
                    f"{total_actual:,.2f} {currency}, representing "
                    f"{portfolio_utilization:.2f}% portfolio "
                    f"utilization, with "
                    f"{total_remaining:,.2f} {currency} remaining. "
                    f"{len(over_budget_grants)} budgeted grant(s) "
                    f"are currently over budget and "
                    f"{len(high_utilization_grants)} are at or above "
                    f"90% utilization. "
                    f"AI-FOS also identifies "
                    f"{len(actual_only_grants)} grant(s) with "
                    f"recorded spending but no identified budget."
                )

        # ==================================================
        # CFO ACTION PLAN / ACTION MONITORING
        # ==================================================

        elif intent in self.CFO_ACTION_PLAN_INTENTS:

            summary = (
                cfo_action_monitoring.get(
                    "summary",
                    {},
                )
                or {}
            )

            total_actions = int(
                summary.get(
                    "total_actions",
                    0,
                )
                or 0
            )

            open_count = int(
                summary.get(
                    "open",
                    0,
                )
                or 0
            )

            in_progress_count = int(
                summary.get(
                    "in_progress",
                    0,
                )
                or 0
            )

            blocked_count = int(
                summary.get(
                    "blocked",
                    0,
                )
                or 0
            )

            completed_count = int(
                summary.get(
                    "completed",
                    0,
                )
                or 0
            )

            overdue_count = int(
                summary.get(
                    "overdue",
                    0,
                )
                or 0
            )

            due_soon_count = int(
                summary.get(
                    "due_soon",
                    0,
                )
                or 0
            )

            unassigned_count = int(
                summary.get(
                    "unassigned_high_priority",
                    0,
                )
                or 0
            )

            def format_actions(
                actions: list[dict[str, Any]],
            ) -> str:

                parts: list[str] = []

                for index, action in enumerate(
                    actions[:5],
                    start=1,
                ):

                    title = str(
                        action.get(
                            "title",
                            "Management action",
                        )
                        or "Management action"
                    )

                    priority = str(
                        action.get(
                            "priority",
                            "Medium",
                        )
                        or "Medium"
                    )

                    owner = str(
                        action.get(
                            "owner",
                            "",
                        )
                        or ""
                    ).strip()

                    due_date = str(
                        action.get(
                            "due_date",
                            "",
                        )
                        or ""
                    ).strip()

                    status = str(
                        action.get(
                            "status",
                            "open",
                        )
                        or "open"
                    ).replace(
                        "_",
                        " ",
                    )

                    text = (
                        f"{index}. "
                        f"{priority} — "
                        f"{title}. "
                        f"Status: {status}."
                    )

                    if owner:
                        text += (
                            f" Owner: {owner}."
                        )

                    else:
                        text += (
                            " Owner: not assigned."
                        )

                    if due_date:
                        text += (
                            f" Due: {due_date}."
                        )

                    parts.append(
                        text
                    )

                return " ".join(
                    parts
                )

            # ------------------------------------------
            # ACTION PLAN SUMMARY
            # ------------------------------------------

            if intent == "action_plan_summary":

                if total_actions == 0:

                    answer = (
                        f"{organisation_name} currently has "
                        f"no CFO management actions recorded "
                        f"in the Action Plan."
                    )

                else:

                    answer = (
                        f"{organisation_name}'s CFO Action Plan "
                        f"contains {total_actions} action(s): "
                        f"{open_count} open, "
                        f"{in_progress_count} in progress, "
                        f"{blocked_count} blocked, and "
                        f"{completed_count} completed. "
                        f"{overdue_count} action(s) are overdue, "
                        f"{due_soon_count} are due soon, and "
                        f"{unassigned_count} Critical or High "
                        f"action(s) currently have no owner."
                    )

            # ------------------------------------------
            # OVERDUE ACTIONS
            # ------------------------------------------

            elif intent == "overdue_actions":

                overdue_actions = (
                    cfo_action_monitoring.get(
                        "overdue_actions",
                        [],
                    )
                    or []
                )

                if not overdue_actions:

                    answer = (
                        f"{organisation_name} currently has "
                        f"no overdue CFO management actions."
                    )

                else:

                    answer = (
                        f"{organisation_name} currently has "
                        f"{len(overdue_actions)} overdue "
                        f"CFO management action(s): "
                        f"{format_actions(overdue_actions)}"
                    )

            # ------------------------------------------
            # ACTIONS DUE SOON
            # ------------------------------------------

            elif intent == "due_soon_actions":

                due_soon_actions = (
                    cfo_action_monitoring.get(
                        "due_soon_actions",
                        [],
                    )
                    or []
                )

                if not due_soon_actions:

                    answer = (
                        f"{organisation_name} currently has "
                        f"no CFO management actions due within "
                        f"the monitoring window."
                    )

                else:

                    answer = (
                        f"{len(due_soon_actions)} CFO management "
                        f"action(s) require near-term follow-up "
                        f"for {organisation_name}: "
                        f"{format_actions(due_soon_actions)}"
                    )

            # ------------------------------------------
            # BLOCKED ACTIONS
            # ------------------------------------------

            elif intent == "blocked_actions":

                blocked_actions = (
                    cfo_action_monitoring.get(
                        "blocked_actions",
                        [],
                    )
                    or []
                )

                if not blocked_actions:

                    answer = (
                        f"{organisation_name} currently has "
                        f"no blocked CFO management actions."
                    )

                else:

                    answer = (
                        f"{organisation_name} currently has "
                        f"{len(blocked_actions)} blocked "
                        f"CFO management action(s): "
                        f"{format_actions(blocked_actions)}"
                    )

            # ------------------------------------------
            # HIGH-PRIORITY ACTIONS WITHOUT OWNERS
            # ------------------------------------------

            else:

                unassigned_actions = (
                    cfo_action_monitoring.get(
                        "unassigned_high_priority_actions",
                        [],
                    )
                    or []
                )

                if not unassigned_actions:

                    answer = (
                        f"{organisation_name} currently has "
                        f"no unassigned Critical or High "
                        f"CFO management actions."
                    )

                else:

                    answer = (
                        f"{organisation_name} currently has "
                        f"{len(unassigned_actions)} Critical or "
                        f"High CFO management action(s) without "
                        f"an assigned owner: "
                        f"{format_actions(unassigned_actions)}"
                    )

        # ==================================================
        # CFO ACTION ESCALATION INTELLIGENCE
        # ==================================================

        elif intent in self.CFO_ACTION_ESCALATION_INTENTS:

            summary = (
                cfo_action_escalation.get(
                    "summary",
                    {},
                )
                or {}
            )

            escalations = (
                cfo_action_escalation.get(
                    "escalations",
                    [],
                )
                or []
            )

            critical_count = int(
                summary.get(
                    "critical",
                    0,
                )
                or 0
            )

            high_count = int(
                summary.get(
                    "high",
                    0,
                )
                or 0
            )

            medium_count = int(
                summary.get(
                    "medium",
                    0,
                )
                or 0
            )

            total_escalations = int(
                summary.get(
                    "total_escalations",
                    0,
                )
                or 0
            )

            def format_escalations(
                items: list[dict[str, Any]],
            ) -> str:

                parts: list[str] = []

                for index, item in enumerate(
                    items[:5],
                    start=1,
                ):

                    title = str(
                        item.get(
                            "title",
                            "Management action",
                        )
                        or "Management action"
                    )

                    severity = str(
                        item.get(
                            "severity",
                            "Medium",
                        )
                        or "Medium"
                    )

                    priority = str(
                        item.get(
                            "priority",
                            "Medium",
                        )
                        or "Medium"
                    )

                    reasons = (
                        item.get(
                            "reasons",
                            [],
                        )
                        or []
                    )

                    follow_up = str(
                        item.get(
                            "recommended_follow_up",
                            "",
                        )
                        or ""
                    ).strip()

                    reason_text = " ".join(
                        str(reason)
                        for reason in reasons
                        if str(reason).strip()
                    )

                    text = (
                        f"{index}. "
                        f"{severity} escalation — "
                        f"{title}. "
                        f"Action priority: {priority}."
                    )

                    if reason_text:
                        text += (
                            f" {reason_text}"
                        )

                    if follow_up:
                        text += (
                            f" Recommended follow-up: "
                            f"{follow_up}"
                        )

                    parts.append(
                        text
                    )

                return " ".join(
                    parts
                )

            # ------------------------------------------
            # ESCALATION SUMMARY
            # ------------------------------------------

            if intent == "action_escalation_summary":

                if total_escalations == 0:

                    answer = (
                        f"{organisation_name} currently has "
                        f"no CFO management actions requiring "
                        f"escalation or additional management "
                        f"intervention."
                    )

                else:

                    answer = (
                        f"{organisation_name} currently has "
                        f"{total_escalations} CFO management "
                        f"action(s) requiring follow-up or "
                        f"escalation: "
                        f"{critical_count} Critical, "
                        f"{high_count} High, and "
                        f"{medium_count} Medium. "
                        f"{format_escalations(escalations)}"
                    )

            # ------------------------------------------
            # CRITICAL FOLLOW-UPS
            # ------------------------------------------

            else:

                critical_escalations = [
                    item
                    for item in escalations
                    if str(
                        item.get(
                            "severity",
                            "",
                        )
                        or ""
                    ).strip()
                    == "Critical"
                ]

                if not critical_escalations:

                    answer = (
                        f"{organisation_name} currently has "
                        f"no Critical CFO management "
                        f"follow-ups requiring immediate "
                        f"intervention."
                    )

                else:

                    answer = (
                        f"{organisation_name} currently has "
                        f"{len(critical_escalations)} Critical "
                        f"CFO management follow-up(s) requiring "
                        f"immediate intervention: "
                        f"{format_escalations(critical_escalations)}"
                    )

        # ==================================================
        # CFO ACTION PERFORMANCE INTELLIGENCE
        # ==================================================

        elif intent in self.CFO_ACTION_PERFORMANCE_INTENTS:

            summary = (
                cfo_action_performance.get(
                    "summary",
                    {},
                )
                or {}
            )

            management_patterns = [
                item
                for item in (
                    cfo_action_performance.get(
                        "management_patterns",
                        [],
                    )
                    or []
                )
                if isinstance(
                    item,
                    dict,
                )
            ]

            total_events = int(
                summary.get(
                    "total_events",
                    0,
                )
                or 0
            )

            action_count = int(
                summary.get(
                    "action_count",
                    0,
                )
                or 0
            )

            completed_count = int(
                summary.get(
                    "completed_action_count",
                    0,
                )
                or 0
            )

            reopened_count = int(
                summary.get(
                    "reopened_action_count",
                    0,
                )
                or 0
            )

            blocked_count = int(
                summary.get(
                    "blocked_action_count",
                    0,
                )
                or 0
            )

            repeated_blocks = int(
                summary.get(
                    "actions_with_repeated_blocks",
                    0,
                )
                or 0
            )

            repeated_owner_changes = int(
                summary.get(
                    "actions_with_multiple_owner_changes",
                    0,
                )
                or 0
            )

            repeated_due_date_changes = int(
                summary.get(
                    "actions_with_multiple_due_date_changes",
                    0,
                )
                or 0
            )

            reopen_rate = float(
                summary.get(
                    "completion_reopen_rate_percentage",
                    0.0,
                )
                or 0.0
            )

            def format_performance_patterns(
                items: list[dict[str, Any]],
            ) -> str:

                parts: list[str] = []

                for index, item in enumerate(
                    items[:5],
                    start=1,
                ):

                    action_id = str(
                        item.get(
                            "action_id",
                            "",
                        )
                        or ""
                    ).strip()

                    pattern = str(
                        item.get(
                            "pattern",
                            "",
                        )
                        or ""
                    ).replace(
                        "_",
                        " ",
                    ).strip()

                    severity = str(
                        item.get(
                            "severity",
                            "Medium",
                        )
                        or "Medium"
                    )

                    count = int(
                        item.get(
                            "count",
                            0,
                        )
                        or 0
                    )

                    interpretation = str(
                        item.get(
                            "interpretation",
                            "",
                        )
                        or ""
                    ).strip()

                    text = (
                        f"{index}. "
                        f"Action {action_id}: "
                        f"{pattern}. "
                        f"Severity: {severity}. "
                        f"Recorded occurrences: {count}."
                    )

                    if interpretation:
                        text += (
                            f" {interpretation}"
                        )

                    parts.append(
                        text
                    )

                return " ".join(
                    parts
                )

            # ------------------------------------------
            # PERFORMANCE SUMMARY
            # ------------------------------------------

            if intent == "action_performance_summary":

                if total_events == 0:

                    answer = (
                        f"{organisation_name} does not yet have "
                        f"recorded CFO Action History available "
                        f"for performance analysis."
                    )

                else:

                    answer = (
                        f"CFO Action Performance for "
                        f"{organisation_name} is based on "
                        f"{total_events} recorded history event(s) "
                        f"across {action_count} action(s). "
                        f"{completed_count} action(s) have a "
                        f"recorded completion, "
                        f"{reopened_count} have been reopened, and "
                        f"{blocked_count} have entered blocked status. "
                        f"{repeated_blocks} action(s) show repeated "
                        f"blocking, {repeated_owner_changes} show "
                        f"multiple ownership changes, and "
                        f"{repeated_due_date_changes} show multiple "
                        f"due-date changes. "
                        f"The completion-to-reopen rate is "
                        f"{reopen_rate:.2f}%."
                    )

            # ------------------------------------------
            # REOPENING PATTERNS
            # ------------------------------------------

            elif intent == "reopened_action_patterns":

                patterns = [
                    item
                    for item in management_patterns
                    if (
                        item.get(
                            "pattern"
                        )
                        == "action_reopened"
                    )
                ]

                if not patterns:

                    answer = (
                        f"{organisation_name} has no recorded "
                        f"CFO action reopening patterns."
                    )

                else:

                    answer = (
                        f"{len(patterns)} CFO action(s) for "
                        f"{organisation_name} show recorded "
                        f"reopening after completion: "
                        f"{format_performance_patterns(patterns)}"
                    )

            # ------------------------------------------
            # REPEATED BLOCKING
            # ------------------------------------------

            elif intent == "repeated_blocking_patterns":

                patterns = [
                    item
                    for item in management_patterns
                    if (
                        item.get(
                            "pattern"
                        )
                        == "repeated_blocking"
                    )
                ]

                if not patterns:

                    answer = (
                        f"{organisation_name} has no recorded "
                        f"repeated-blocking patterns."
                    )

                else:

                    answer = (
                        f"{len(patterns)} CFO action(s) for "
                        f"{organisation_name} show repeated "
                        f"blocking: "
                        f"{format_performance_patterns(patterns)}"
                    )

            # ------------------------------------------
            # OWNERSHIP CHANGES
            # ------------------------------------------

            elif intent == "ownership_change_patterns":

                patterns = [
                    item
                    for item in management_patterns
                    if (
                        item.get(
                            "pattern"
                        )
                        == "repeated_owner_changes"
                    )
                ]

                if not patterns:

                    answer = (
                        f"{organisation_name} has no recorded "
                        f"repeated ownership-change patterns."
                    )

                else:

                    answer = (
                        f"{len(patterns)} CFO action(s) for "
                        f"{organisation_name} show multiple "
                        f"ownership changes: "
                        f"{format_performance_patterns(patterns)}"
                    )

            # ------------------------------------------
            # DUE-DATE CHANGES
            # ------------------------------------------

            else:

                patterns = [
                    item
                    for item in management_patterns
                    if (
                        item.get(
                            "pattern"
                        )
                        == "repeated_due_date_changes"
                    )
                ]

                if not patterns:

                    answer = (
                        f"{organisation_name} has no recorded "
                        f"repeated due-date-change patterns."
                    )

                else:

                    answer = (
                        f"{len(patterns)} CFO action(s) for "
                        f"{organisation_name} show multiple "
                        f"due-date changes: "
                        f"{format_performance_patterns(patterns)}"
                    )                    

        # ==================================================
        # EXECUTIVE DECISION INTELLIGENCE
        # ==================================================

        elif intent in self.EXECUTIVE_DECISION_INTENTS:

            executive_signal = str(
                executive_decision_intelligence.get(
                    "executive_signal",
                    "monitor",
                )
                or "monitor"
            )

            highest_priority = str(
                executive_decision_intelligence.get(
                    "highest_priority",
                    "Low",
                )
                or "Low"
            )

            priorities = [
                priority
                for priority in (
                    executive_decision_intelligence.get(
                        "priorities",
                        [],
                    )
                    or []
                )
                if isinstance(
                    priority,
                    dict,
                )
            ]

            opportunities = [
                opportunity
                for opportunity in (
                    executive_decision_intelligence.get(
                        "opportunities",
                        [],
                    )
                    or []
                )
                if isinstance(
                    opportunity,
                    dict,
                )
            ]

            signal_label = (
                executive_signal
                .replace(
                    "_",
                    " ",
                )
                .strip()
            )

            if priorities:

                priority_parts: list[str] = []

                for index, priority in enumerate(
                    priorities[:5],
                    start=1,
                ):

                    priority_level = str(
                        priority.get(
                            "priority",
                            "Unknown",
                        )
                        or "Unknown"
                    )

                    category = str(
                        priority.get(
                            "category",
                            "Financial Management",
                        )
                        or "Financial Management"
                    )

                    title = str(
                        priority.get(
                            "title",
                            "Management priority",
                        )
                        or "Management priority"
                    )

                    evidence = str(
                        priority.get(
                            "evidence",
                            "",
                        )
                        or ""
                    ).strip()

                    management_action = str(
                        priority.get(
                            "management_action",
                            "",
                        )
                        or ""
                    ).strip()

                    expected_impact = str(
                        priority.get(
                            "expected_impact",
                            "",
                        )
                        or ""
                    ).strip()

                    part = (
                        f"{index}. "
                        f"{priority_level} — "
                        f"{category}: {title}."
                    )

                    if evidence:
                        part += (
                            f" Why it matters: "
                            f"{evidence}"
                        )

                    if management_action:
                        part += (
                            f" Management action: "
                            f"{management_action}"
                        )

                    if expected_impact:
                        part += (
                            f" Expected impact: "
                            f"{expected_impact}"
                        )

                    priority_parts.append(
                        part
                    )

                priority_text = " ".join(
                    priority_parts
                )

                answer = (
                    f"AI-FOS Executive Decision Intelligence "
                    f"identifies {highest_priority} as the "
                    f"highest current management priority for "
                    f"{organisation_name}. "
                    f"The executive signal is "
                    f"{signal_label}. "
                    f"Management should focus on: "
                    f"{priority_text}"
                )

            else:

                answer = (
                    f"AI-FOS currently identifies no material "
                    f"financial management priorities requiring "
                    f"escalation for {organisation_name}. "
                    f"The executive signal is "
                    f"{signal_label}. "
                    f"Management should continue monitoring the "
                    f"validated financial position."
                )

            if opportunities:

                opportunity_parts: list[str] = []

                for opportunity in opportunities[:3]:

                    title = str(
                        opportunity.get(
                            "title",
                            "Financial opportunity",
                        )
                        or "Financial opportunity"
                    )

                    recommended_action = str(
                        opportunity.get(
                            "recommended_action",
                            "",
                        )
                        or ""
                    ).strip()

                    opportunity_text = title

                    if recommended_action:
                        opportunity_text += (
                            f" — "
                            f"{recommended_action}"
                        )

                    opportunity_parts.append(
                        opportunity_text
                    )

                if opportunity_parts:

                    answer += (
                        " Verified opportunities remain "
                        "separate from the management risks "
                        "and should not be used to cancel them: "
                        + "; ".join(
                            opportunity_parts
                        )
                        + "."
                    )

        # ==================================================
        # HISTORICAL FINANCIAL INTELLIGENCE
        # ==================================================

        elif intent in self.HISTORICAL_CHANGE_INTENTS:

            overall_direction = str(
                historical_change_analysis.get(
                    "overall_direction",
                    "stable_or_insufficient_evidence",
                )
                or "stable_or_insufficient_evidence"
            )

            management_attention = str(
                historical_change_analysis.get(
                    "management_attention",
                    "monitor",
                )
                or "monitor"
            )

            evidence_summary = (
                historical_change_analysis.get(
                    "evidence_summary",
                    {},
                )
                or {}
            )

            metric_change = (
                historical_change_analysis.get(
                    "metric_change",
                    {},
                )
                or {}
            )

            risk_change = (
                historical_change_analysis.get(
                    "risk_change",
                    {},
                )
                or {}
            )

            comparisons = [
                item
                for item in (
                    metric_change.get(
                        "comparisons",
                        [],
                    )
                    or []
                )
                if isinstance(
                    item,
                    dict,
                )
            ]

            risk_movements = [
                item
                for item in (
                    risk_change.get(
                        "movements",
                        [],
                    )
                    or []
                )
                if isinstance(
                    item,
                    dict,
                )
            ]

            direction_label = (
                overall_direction
                .replace(
                    "_",
                    " ",
                )
                .strip()
            )

            attention_label = (
                management_attention
                .replace(
                    "_",
                    " ",
                )
                .strip()
            )

            # ----------------------------------------------
            # Overall historical change
            # ----------------------------------------------

            if intent == "historical_change_summary":

                improved_count = int(
                    evidence_summary.get(
                        "improved_metric_count",
                        0,
                    )
                    or 0
                )

                deteriorated_count = int(
                    evidence_summary.get(
                        "deteriorated_metric_count",
                        0,
                    )
                    or 0
                )

                new_risk_count = int(
                    evidence_summary.get(
                        "new_risk_count",
                        0,
                    )
                    or 0
                )

                resolved_risk_count = int(
                    evidence_summary.get(
                        "resolved_risk_count",
                        0,
                    )
                    or 0
                )

                answer = (
                    f"AI-FOS Historical Financial Intelligence "
                    f"indicates that the financial position of "
                    f"{organisation_name} is {direction_label} "
                    f"compared with the previous verified "
                    f"financial processing snapshot. "
                    f"{improved_count} comparable financial "
                    f"metric(s) improved and "
                    f"{deteriorated_count} deteriorated. "
                    f"{new_risk_count} new financial risk(s) "
                    f"appeared and {resolved_risk_count} "
                    f"previous risk(s) were resolved. "
                    f"Management attention is classified as "
                    f"{attention_label}."
                )

            # ----------------------------------------------
            # Financial metric movement
            # ----------------------------------------------

            elif intent == "financial_position_change":

                material_comparisons = [
                    item
                    for item in comparisons
                    if item.get(
                        "signal"
                    )
                    in {
                        "improved",
                        "deteriorated",
                        "increased",
                        "decreased",
                    }
                ]

                if material_comparisons:

                    parts: list[str] = []

                    for item in material_comparisons[:8]:

                        label = str(
                            item.get(
                                "label",
                                "Financial metric",
                            )
                            or "Financial metric"
                        )

                        previous_value = item.get(
                            "previous_value"
                        )

                        current_value = item.get(
                            "current_value"
                        )

                        absolute_change = item.get(
                            "absolute_change"
                        )

                        unit = str(
                            item.get(
                                "unit",
                                "",
                            )
                            or ""
                        )

                        signal = str(
                            item.get(
                                "signal",
                                "",
                            )
                            or ""
                        ).replace(
                            "_",
                            " ",
                        )

                        part = (
                            f"{label}: "
                            f"{previous_value} to "
                            f"{current_value}"
                        )

                        if absolute_change is not None:

                            part += (
                                f" (change "
                                f"{absolute_change}"
                            )

                            if unit:
                                part += f" {unit}"

                            part += ")"

                        if signal:
                            part += f", {signal}"

                        parts.append(
                            part
                        )

                    answer = (
                        f"Compared with the previous verified "
                        f"snapshot, AI-FOS classifies the overall "
                        f"financial direction for "
                        f"{organisation_name} as "
                        f"{direction_label}. "
                        + "; ".join(
                            parts
                        )
                        + "."
                    )

                else:

                    answer = (
                        f"AI-FOS found no comparable material "
                        f"financial metric movement between the "
                        f"latest two verified snapshots for "
                        f"{organisation_name}."
                    )

            # ----------------------------------------------
            # Risk movement summary
            # ----------------------------------------------

            elif intent == "risk_change_summary":

                risk_summary = (
                    risk_change.get(
                        "summary",
                        {},
                    )
                    or {}
                )

                answer = (
                    f"Between the latest two verified financial "
                    f"snapshots for {organisation_name}, "
                    f"AI-FOS identified "
                    f"{int(risk_summary.get('new_count', 0) or 0)} "
                    f"new risk(s), "
                    f"{int(risk_summary.get('resolved_count', 0) or 0)} "
                    f"resolved risk(s), "
                    f"{int(risk_summary.get('persistent_count', 0) or 0)} "
                    f"persistent risk(s), "
                    f"{int(risk_summary.get('severity_increased_count', 0) or 0)} "
                    f"risk(s) with increased severity, and "
                    f"{int(risk_summary.get('severity_decreased_count', 0) or 0)} "
                    f"risk(s) with decreased severity."
                )

            # ----------------------------------------------
            # New risks
            # ----------------------------------------------

            elif intent == "new_risks_since_previous":

                new_risks = [
                    movement
                    for movement in risk_movements
                    if movement.get(
                        "movement"
                    )
                    == "new"
                ]

                if new_risks:

                    parts: list[str] = []

                    for movement in new_risks:

                        current = movement.get(
                            "current",
                            {},
                        )

                        if not isinstance(
                            current,
                            dict,
                        ):
                            continue

                        severity = str(
                            current.get(
                                "severity",
                                "Unknown",
                            )
                            or "Unknown"
                        )

                        title = str(
                            current.get(
                                "title",
                                "Financial risk",
                            )
                            or "Financial risk"
                        )

                        parts.append(
                            f"{severity} — {title}"
                        )

                    answer = (
                        f"AI-FOS identified the following new "
                        f"financial risk(s) since the previous "
                        f"verified snapshot for "
                        f"{organisation_name}: "
                        + "; ".join(
                            parts
                        )
                        + "."
                    )

                else:

                    answer = (
                        f"AI-FOS identified no new financial "
                        f"risks since the previous verified "
                        f"snapshot for {organisation_name}."
                    )

            # ----------------------------------------------
            # Resolved risks
            # ----------------------------------------------

            else:

                resolved_risks = [
                    movement
                    for movement in risk_movements
                    if movement.get(
                        "movement"
                    )
                    == "resolved"
                ]

                if resolved_risks:

                    parts: list[str] = []

                    for movement in resolved_risks:

                        previous = movement.get(
                            "previous",
                            {},
                        )

                        if not isinstance(
                            previous,
                            dict,
                        ):
                            continue

                        title = str(
                            previous.get(
                                "title",
                                "Financial risk",
                            )
                            or "Financial risk"
                        )

                        parts.append(
                            title
                        )

                    answer = (
                        f"AI-FOS identified the following "
                        f"previous financial risk(s) as no longer "
                        f"present in the latest verified snapshot "
                        f"for {organisation_name}: "
                        + "; ".join(
                            parts
                        )
                        + "."
                    )

                else:

                    answer = (
                        f"AI-FOS identified no previously recorded "
                        f"financial risks as resolved between the "
                        f"latest two verified snapshots for "
                        f"{organisation_name}."
                    )

        # ==================================================
        # HISTORICAL DECISION INTELLIGENCE
        # ==================================================

        elif intent in self.HISTORICAL_DECISION_INTENTS:

            historical_signal = str(
                historical_decision_intelligence.get(
                    "historical_signal",
                    "monitor",
                )
                or "monitor"
            )

            overall_direction = str(
                historical_decision_intelligence.get(
                    "overall_direction",
                    "stable_or_insufficient_evidence",
                )
                or "stable_or_insufficient_evidence"
            )

            highest_priority = str(
                historical_decision_intelligence.get(
                    "highest_priority",
                    "Low",
                )
                or "Low"
            )

            management_attention = str(
                historical_decision_intelligence.get(
                    "management_attention",
                    "monitor",
                )
                or "monitor"
            )

            priorities = [
                priority
                for priority in (
                    historical_decision_intelligence.get(
                        "priorities",
                        [],
                    )
                    or []
                )
                if isinstance(
                    priority,
                    dict,
                )
            ]

            improvements = [
                improvement
                for improvement in (
                    historical_decision_intelligence.get(
                        "improvements",
                        [],
                    )
                    or []
                )
                if isinstance(
                    improvement,
                    dict,
                )
            ]

            direction_label = (
                overall_direction
                .replace(
                    "_",
                    " ",
                )
                .strip()
            )

            signal_label = (
                historical_signal
                .replace(
                    "_",
                    " ",
                )
                .strip()
            )

            attention_label = (
                management_attention
                .replace(
                    "_",
                    " ",
                )
                .strip()
            )

            if priorities:

                priority_parts: list[str] = []

                for index, priority in enumerate(
                    priorities[:5],
                    start=1,
                ):

                    priority_level = str(
                        priority.get(
                            "priority",
                            "Medium",
                        )
                        or "Medium"
                    )

                    category = str(
                        priority.get(
                            "category",
                            "Financial Management",
                        )
                        or "Financial Management"
                    )

                    title = str(
                        priority.get(
                            "title",
                            "Historical financial deterioration",
                        )
                        or "Historical financial deterioration"
                    )

                    evidence = str(
                        priority.get(
                            "evidence",
                            "",
                        )
                        or ""
                    ).strip()

                    historical_change = str(
                        priority.get(
                            "historical_change",
                            "",
                        )
                        or ""
                    ).replace(
                        "_",
                        " ",
                    ).strip()

                    part = (
                        f"{index}. "
                        f"{priority_level} — "
                        f"{category}: {title}."
                    )

                    if historical_change:

                        part += (
                            f" Historical change: "
                            f"{historical_change}."
                        )

                    if evidence:

                        part += (
                            f" Evidence: "
                            f"{evidence}"
                        )

                    priority_parts.append(
                        part
                    )

                answer = (
                    f"AI-FOS Historical Decision Intelligence "
                    f"classifies the latest financial movement "
                    f"for {organisation_name} as "
                    f"{direction_label}. "
                    f"The highest change-driven management "
                    f"priority is {highest_priority}, with a "
                    f"historical signal of {signal_label}. "
                    f"Management attention is "
                    f"{attention_label}. "
                    f"The main change-driven priorities are: "
                    + " ".join(
                        priority_parts
                    )
                )

            else:

                answer = (
                    f"AI-FOS Historical Decision Intelligence "
                    f"identifies no deterioration from the latest "
                    f"verified financial changes that currently "
                    f"requires a management priority for "
                    f"{organisation_name}. "
                    f"The overall historical direction is "
                    f"{direction_label}, and the historical "
                    f"signal is {signal_label}."
                )

            if improvements:

                improvement_parts: list[str] = []

                for improvement in improvements[:5]:

                    title = str(
                        improvement.get(
                            "title",
                            "Financial improvement",
                        )
                        or "Financial improvement"
                    )

                    historical_change = str(
                        improvement.get(
                            "historical_change",
                            "",
                        )
                        or ""
                    ).replace(
                        "_",
                        " ",
                    ).strip()

                    improvement_text = title

                    if historical_change:

                        improvement_text += (
                            f" ({historical_change})"
                        )

                    improvement_parts.append(
                        improvement_text
                    )

                if improvement_parts:

                    answer += (
                        " Positive historical developments remain "
                        "separate and do not cancel the identified "
                        "management priorities: "
                        + "; ".join(
                            improvement_parts
                        )
                        + "."
                    )

        # ==================================================
        # RECOMMENDATION INTELLIGENCE
        # ==================================================

        elif intent in self.RECOMMENDATION_INTENTS:

            priority_order = {
                "Critical": 4,
                "High": 3,
                "Medium": 2,
                "Low": 1,
            }

            ordered_recommendations = sorted(
                cfo_recommendations,
                key=lambda item: (
                    priority_order.get(
                        item.get("priority"),
                        0,
                    )
                ),
                reverse=True,
            )

            # ------------------------------------------
            # Funding Gap actions
            # ------------------------------------------

            if intent == "funding_gap_actions":

                funding_gap_actions = [
                    recommendation
                    for recommendation in ordered_recommendations
                    if (
                        "funding"
                        in str(
                            recommendation.get(
                                "category",
                                "",
                            )
                        ).lower()
                        or "funding gap"
                        in str(
                            recommendation.get(
                                "title",
                                "",
                            )
                        ).lower()
                        or "funding gap"
                        in str(
                            recommendation.get(
                                "linked_risk",
                                "",
                            )
                        ).lower()
                        or "unfunded financial requirements"
                        in str(
                            recommendation.get(
                                "linked_risk",
                                "",
                            )
                        ).lower()
                    )
                ]

                selected_actions = (
                    funding_gap_actions[:5]
                    if funding_gap_actions
                    else ordered_recommendations[:5]
                )

            # ------------------------------------------
            # Finance meeting agenda
            # ------------------------------------------

            elif intent == "finance_meeting_agenda":

                high_priority_actions = [
                    recommendation
                    for recommendation in ordered_recommendations
                    if recommendation.get("priority")
                    in {
                        "Critical",
                        "High",
                    }
                ]

                selected_actions = (
                    high_priority_actions[:5]
                    if high_priority_actions
                    else ordered_recommendations[:5]
                )

            # ------------------------------------------
            # Overall priority actions
            # ------------------------------------------

            elif intent == "priority_actions":

                high_priority_actions = [
                    recommendation
                    for recommendation in ordered_recommendations
                    if recommendation.get("priority")
                    in {
                        "Critical",
                        "High",
                    }
                ]

                selected_actions = (
                    high_priority_actions[:5]
                    if high_priority_actions
                    else ordered_recommendations[:5]
                )

            # ------------------------------------------
            # General recommendation summary
            # ------------------------------------------

            else:

                selected_actions = ordered_recommendations[:5]

            # ------------------------------------------
            # Build answer
            # ------------------------------------------

            if not selected_actions:

                answer = (
                    f"AI-FOS currently has no CFO "
                    f"recommendations available for "
                    f"{organisation_name}."
                )

            else:

                recommendation_text = " ".join(
                    (
                        f"{index + 1}. "
                        f"{recommendation.get('priority', 'Unknown')} "
                        f"priority — "
                        f"{recommendation.get('title', 'Unnamed recommendation')}. "
                        f"Action: "
                        f"{recommendation.get('action', '')} "
                        f"Expected impact: "
                        f"{recommendation.get('expected_impact', '')}"
                    )
                    for index, recommendation in enumerate(selected_actions)
                )

                # --------------------------------------
                # Funding Gap recommendation response
                # --------------------------------------

                if intent == "funding_gap_actions":

                    funding_summary = (
                        funding_gap.get(
                            "summary",
                            {},
                        )
                        or {}
                    )

                    funding_gap_amount = self._to_float(
                        funding_summary.get("funding_gap")
                    )

                    remaining_requirement = self._to_float(
                        funding_summary.get("remaining_requirement")
                    )

                    applied_secured_funding = self._to_float(
                        funding_summary.get("applied_secured_funding")
                    )

                    coverage_percentage = self._to_float(
                        funding_summary.get("applied_coverage_percentage")
                    )

                    period_ineligible_exposure = self._to_float(
                        funding_summary.get("period_ineligible_funding_exposure")
                    )

                    period_unknown_exposure = self._to_float(
                        funding_summary.get("period_unknown_funding_exposure")
                    )

                    dimension_incompatible_exposure = self._to_float(
                        funding_summary.get("dimension_incompatible_funding_exposure")
                    )

                    period_ineligible_count = int(
                        self._to_float(
                            funding_summary.get(
                                "requirements_with_period_ineligible_funding"
                            )
                        )
                    )

                    period_unknown_count = int(
                        self._to_float(
                            funding_summary.get(
                                "requirements_with_period_unknown_funding"
                            )
                        )
                    )

                    dimension_incompatible_count = int(
                        self._to_float(
                            funding_summary.get(
                                "requirements_with_dimension_incompatible_funding"
                            )
                        )
                    )

                    diagnostic_parts: list[str] = []

                    if period_ineligible_exposure > 0:
                        diagnostic_parts.append(
                            (
                                f"{period_ineligible_exposure:,.2f} "
                                f"{currency} of requirement-level "
                                f"secured funding exposure could not "
                                f"be applied because the related grant "
                                f"period does not overlap the applicable "
                                f"fiscal year. This affects "
                                f"{period_ineligible_count} requirement(s)."
                            )
                        )

                    if period_unknown_exposure > 0:
                        diagnostic_parts.append(
                            (
                                f"{period_unknown_exposure:,.2f} "
                                f"{currency} of requirement-level "
                                f"secured funding exposure could not "
                                f"be confirmed as eligible because "
                                f"grant-period evidence is missing or "
                                f"incomplete. This affects "
                                f"{period_unknown_count} requirement(s)."
                            )
                        )

                    if dimension_incompatible_exposure > 0:
                        diagnostic_parts.append(
                            (
                                f"{dimension_incompatible_exposure:,.2f} "
                                f"{currency} of requirement-level "
                                f"secured funding exposure could not "
                                f"be applied because known funding and "
                                f"requirement dimensions conflict. "
                                f"This affects "
                                f"{dimension_incompatible_count} "
                                f"requirement(s)."
                            )
                        )

                    if diagnostic_parts:
                        diagnostic_text = (
                            " The Funding Gap is also affected by "
                            + " ".join(diagnostic_parts)
                            + (
                                " These exposure values are "
                                "requirement-level diagnostics and "
                                "must not be added together or "
                                "interpreted as unique organization-wide "
                                "secured funding."
                            )
                        )
                    else:
                        diagnostic_text = (
                            " No secured-funding eligibility or "
                            "dimension conflicts are currently "
                            "identified in the Funding Gap diagnostics."
                        )

                    answer = (
                        f"{organisation_name} currently has a "
                        f"Funding Gap of "
                        f"{funding_gap_amount:,.2f} {currency} "
                        f"against remaining requirements of "
                        f"{remaining_requirement:,.2f} {currency}. "
                        f"AI-FOS has applied "
                        f"{applied_secured_funding:,.2f} {currency} "
                        f"of validated secured funding, covering "
                        f"{coverage_percentage:.2f}% of remaining "
                        f"requirements."
                        f"{diagnostic_text} "
                        f"Management should focus on the "
                        f"following actions: "
                        f"{recommendation_text}"
                    )

                # --------------------------------------
                # Overall priority response
                # --------------------------------------

                elif intent == "priority_actions":

                    answer = (
                        f"The highest-priority financial actions "
                        f"for {organisation_name} are: "
                        f"{recommendation_text}"
                    )

                # --------------------------------------
                # Finance meeting agenda response
                # --------------------------------------

                elif intent == "finance_meeting_agenda":

                    answer = (
                        f"For the next finance meeting, "
                        f"management should discuss the following "
                        f"priority financial matters for "
                        f"{organisation_name}: "
                        f"{recommendation_text}"
                    )

                # --------------------------------------
                # General recommendation response
                # --------------------------------------

                else:

                    answer = (
                        f"AI-FOS currently recommends the "
                        f"following management actions for "
                        f"{organisation_name}: "
                        f"{recommendation_text}"
                    )

        # ==================================================
        # RISK INTELLIGENCE
        # ==================================================

        elif intent in self.RISK_INTENTS:

            severity_order = {
                "Critical": 4,
                "High": 3,
                "Medium": 2,
                "Low": 1,
            }

            ordered_risks = sorted(
                risk_assessment,
                key=lambda item: severity_order.get(
                    item.get("severity"),
                    0,
                ),
                reverse=True,
            )

            critical_risks = [
                risk for risk in ordered_risks if risk.get("severity") == "Critical"
            ]

            high_risks = [
                risk for risk in ordered_risks if risk.get("severity") == "High"
            ]

            critical_or_high_risks = [
                risk
                for risk in ordered_risks
                if risk.get("severity")
                in {
                    "Critical",
                    "High",
                }
            ]

            def build_risk_text(
                risks: list[dict[str, Any]],
                limit: int = 5,
            ) -> str:

                return " ".join(
                    (
                        f"{index + 1}. "
                        f"{risk.get('severity', 'Unknown')} — "
                        f"{risk.get('title', 'Unnamed risk')}. "
                        f"Evidence: "
                        f"{risk.get('evidence', '')} "
                        f"Recommendation: "
                        f"{risk.get('recommendation', '')}"
                    )
                    for index, risk in enumerate(risks[:limit])
                )

            # ------------------------------------------
            # Overall risk summary
            # ------------------------------------------

            if intent == "risk_summary":

                top_risks = ordered_risks[:5]

                if not top_risks:

                    answer = (
                        f"AI-FOS currently detects no "
                        f"financial risks for "
                        f"{organisation_name} in the "
                        f"verified risk assessment."
                    )

                else:

                    risk_text = build_risk_text(top_risks)

                    answer = (
                        f"AI-FOS currently identifies "
                        f"{len(risk_assessment)} financial "
                        f"risk(s) for {organisation_name}, "
                        f"including "
                        f"{len(critical_risks)} Critical and "
                        f"{len(high_risks)} High-severity "
                        f"risk(s). "
                        f"The most important risks are: "
                        f"{risk_text}"
                    )

            # ------------------------------------------
            # Critical and High risks
            # ------------------------------------------

            elif intent == "high_risks":

                if not critical_or_high_risks:

                    answer = (
                        f"AI-FOS currently detects no "
                        f"Critical or High-severity financial "
                        f"risks for {organisation_name}."
                    )

                else:

                    risk_text = build_risk_text(critical_or_high_risks)

                    answer = (
                        f"{organisation_name} currently has "
                        f"{len(critical_or_high_risks)} "
                        f"Critical or High-severity financial "
                        f"risk(s): "
                        f"{risk_text}"
                    )

            # ------------------------------------------
            # Most immediate risk
            # ------------------------------------------

            elif intent == "immediate_risk":

                if not ordered_risks:

                    answer = (
                        f"AI-FOS currently detects no "
                        f"financial risks requiring immediate "
                        f"attention for {organisation_name}."
                    )

                else:

                    risk = ordered_risks[0]

                    answer = (
                        f"The financial risk requiring the "
                        f"most immediate attention for "
                        f"{organisation_name} is the "
                        f"{risk.get('severity', 'Unknown')}-"
                        f"severity risk: "
                        f"{risk.get('title', 'Unnamed risk')}. "
                        f"Evidence: "
                        f"{risk.get('evidence', '')} "
                        f"Recommended management response: "
                        f"{risk.get('recommendation', '')}"
                    )

            # ------------------------------------------
            # Category-specific risks
            # ------------------------------------------

            else:

                category_keywords = {
                    "liquidity_risks": (
                        "liquidity",
                        "cash",
                        "runway",
                    ),
                    "budget_risks": (
                        "budget",
                        "overspend",
                        "over budget",
                        "unbudgeted",
                    ),
                    "funding_risks": (
                        "funding",
                        "fund",
                        "grant",
                        "unfunded",
                        "secured funding",
                    ),
                }

                labels = {
                    "liquidity_risks": "liquidity",
                    "budget_risks": "budget",
                    "funding_risks": "funding",
                }

                keywords = category_keywords.get(
                    intent,
                    (),
                )

                risk_label = labels.get(
                    intent,
                    "financial",
                )

                filtered_risks = []

                for risk in ordered_risks:

                    searchable_text = " ".join(
                        [
                            str(
                                risk.get(
                                    "title",
                                    "",
                                )
                            ),
                            str(
                                risk.get(
                                    "category",
                                    "",
                                )
                            ),
                            str(
                                risk.get(
                                    "evidence",
                                    "",
                                )
                            ),
                            str(
                                risk.get(
                                    "recommendation",
                                    "",
                                )
                            ),
                        ]
                    ).lower()

                    if any(keyword in searchable_text for keyword in keywords):
                        filtered_risks.append(risk)

                if not filtered_risks:

                    answer = (
                        f"AI-FOS currently detects no "
                        f"specific {risk_label} risks for "
                        f"{organisation_name} in the verified "
                        f"risk assessment."
                    )

                else:

                    risk_text = build_risk_text(filtered_risks)

                    highest_severity = filtered_risks[0].get(
                        "severity",
                        "Unknown",
                    )

                    answer = (
                        f"AI-FOS identifies "
                        f"{len(filtered_risks)} "
                        f"{risk_label} risk(s) for "
                        f"{organisation_name}. "
                        f"The highest severity in this area "
                        f"is {highest_severity}. "
                        f"The main {risk_label} risks are: "
                        f"{risk_text}"
                    )

        # ==================================================
        # FORWARD-LOOKING RISK INTELLIGENCE
        # ==================================================

        elif intent in self.FORWARD_RISK_INTENTS:

            severity_order = {
                "Critical": 4,
                "High": 3,
                "Medium": 2,
                "Low": 1,
            }

            ordered_forward_risks = sorted(
                [risk for risk in forward_risks if isinstance(risk, dict)],
                key=lambda risk: severity_order.get(
                    str(risk.get("severity")),
                    0,
                ),
                reverse=True,
            )

            high_forward_risks = [
                risk
                for risk in ordered_forward_risks
                if str(risk.get("severity"))
                in {
                    "Critical",
                    "High",
                }
            ]

            def build_forward_risk_text(
                risks: list[dict[str, Any]],
            ) -> str:

                return "; ".join(
                    (
                        f"{risk.get('title', 'Emerging risk')} "
                        f"({risk.get('severity', 'Unknown')}): "
                        f"{risk.get('evidence', '')}"
                    )
                    for risk in risks
                )

            # ------------------------------------------
            # Overall forward-risk summary
            # ------------------------------------------

            if intent == "forward_risk_summary":

                top_risks = ordered_forward_risks[:5]

                if not top_risks:

                    answer = (
                        f"AI-FOS currently identifies no "
                        f"validated forward-looking financial "
                        f"risks for {organisation_name}."
                    )

                else:

                    risk_text = build_forward_risk_text(top_risks)

                    answer = (
                        f"AI-FOS currently identifies "
                        f"{len(ordered_forward_risks)} "
                        f"forward-looking financial risk(s) "
                        f"for {organisation_name}, including "
                        f"{len(high_forward_risks)} Critical "
                        f"or High-severity emerging risk(s). "
                        f"The most important forward risks are: "
                        f"{risk_text}"
                    )

            # ------------------------------------------
            # High forward risks
            # ------------------------------------------

            elif intent == "forward_high_risks":

                if not high_forward_risks:

                    answer = (
                        f"AI-FOS currently identifies no "
                        f"Critical or High-severity "
                        f"forward-looking risks for "
                        f"{organisation_name}."
                    )

                else:

                    risk_text = build_forward_risk_text(high_forward_risks[:5])

                    answer = (
                        f"The most significant emerging "
                        f"financial risks for "
                        f"{organisation_name} are: "
                        f"{risk_text}"
                    )

            # ------------------------------------------
            # Forward funding risks
            # ------------------------------------------

            elif intent == "forward_funding_risks":

                funding_risks = [
                    risk
                    for risk in ordered_forward_risks
                    if "fund"
                    in (
                        f"{risk.get('category', '')} "
                        f"{risk.get('title', '')} "
                        f"{risk.get('evidence', '')} "
                        f"{risk.get('recommendation', '')}"
                    ).lower()
                ]

                if not funding_risks:

                    answer = (
                        f"AI-FOS currently identifies no "
                        f"validated forward-looking funding "
                        f"risks for {organisation_name}."
                    )

                else:

                    risk_text = build_forward_risk_text(funding_risks[:5])

                    answer = (
                        f"AI-FOS identifies the following "
                        f"forward-looking funding risks for "
                        f"{organisation_name}: "
                        f"{risk_text}"
                    )

            # ------------------------------------------
            # Forward operating risks
            # ------------------------------------------

            elif intent == "forward_operating_risks":

                operating_terms = (
                    "operating",
                    "operational",
                    "performance",
                    "deficit",
                    "revenue",
                    "expense",
                )

                operating_risks = [
                    risk
                    for risk in ordered_forward_risks
                    if any(
                        term
                        in (
                            f"{risk.get('category', '')} "
                            f"{risk.get('title', '')} "
                            f"{risk.get('evidence', '')} "
                            f"{risk.get('recommendation', '')}"
                        ).lower()
                        for term in operating_terms
                    )
                ]

                if not operating_risks:

                    answer = (
                        f"AI-FOS currently identifies no "
                        f"validated forward-looking operating "
                        f"risks for {organisation_name}."
                    )

                else:

                    risk_text = build_forward_risk_text(operating_risks[:5])

                    answer = (
                        f"AI-FOS identifies the following "
                        f"forward-looking operating risks for "
                        f"{organisation_name}: "
                        f"{risk_text}"
                    )

        # ==================================================
        # FINANCIAL OPPORTUNITY INTELLIGENCE
        # ==================================================

        elif intent in self.FINANCIAL_OPPORTUNITY_INTENTS:

            organization_name = organisation_name

            valid_opportunities = [
                opportunity
                for opportunity in financial_opportunities
                if isinstance(opportunity, dict)
            ]

            priority_order = {
                "Critical": 4,
                "High": 3,
                "Medium": 2,
                "Low": 1,
            }

            valid_opportunities.sort(
                key=lambda opportunity: priority_order.get(
                    str(opportunity.get("priority")),
                    0,
                ),
                reverse=True,
            )

            def build_opportunity_text(
                opportunities: list[dict[str, Any]],
            ) -> str:
                lines: list[str] = []

                for opportunity in opportunities:
                    priority = str(
                        opportunity.get(
                            "priority",
                            "Medium",
                        )
                    )

                    category = str(
                        opportunity.get(
                            "category",
                            "Financial Opportunity",
                        )
                    )

                    title = str(
                        opportunity.get(
                            "title",
                            "Financial opportunity",
                        )
                    )

                    evidence = str(
                        opportunity.get(
                            "evidence",
                            "",
                        )
                    )

                    recommended_action = str(
                        opportunity.get(
                            "recommended_action",
                            "",
                        )
                    )

                    line = f"- [{priority}] " f"{category}: {title}"

                    if evidence:
                        line += f" — Evidence: {evidence}"

                    if recommended_action:
                        line += f" — Recommended action: " f"{recommended_action}"

                    lines.append(line)

                return "\n".join(lines)

            if intent == "financial_opportunity_summary":

                if not valid_opportunities:
                    answer = (
                        f"AI-FOS has not identified any "
                        f"validated financial opportunities "
                        f"for {organization_name}."
                    )

                else:
                    high_count = sum(
                        1
                        for opportunity in valid_opportunities
                        if str(opportunity.get("priority"))
                        in {
                            "Critical",
                            "High",
                        }
                    )

                    opportunity_text = build_opportunity_text(valid_opportunities[:5])

                    answer = (
                        f"AI-FOS identifies "
                        f"{len(valid_opportunities)} validated "
                        f"financial opportunit"
                        f"{'y' if len(valid_opportunities) == 1 else 'ies'} "
                        f"for {organization_name}. "
                        f"{high_count} are High or Critical "
                        f"priority.\n\n"
                        f"{opportunity_text}"
                    )

            elif intent == "high_financial_opportunities":

                high_opportunities = [
                    opportunity
                    for opportunity in valid_opportunities
                    if str(opportunity.get("priority"))
                    in {
                        "Critical",
                        "High",
                    }
                ]

                if not high_opportunities:
                    answer = (
                        f"AI-FOS has not identified any "
                        f"High or Critical validated financial "
                        f"opportunities for "
                        f"{organization_name}."
                    )

                else:
                    opportunity_text = build_opportunity_text(high_opportunities[:5])

                    answer = (
                        f"The highest-priority validated "
                        f"financial opportunities for "
                        f"{organization_name} are:\n\n"
                        f"{opportunity_text}"
                    )

            elif intent == "funding_opportunities":

                funding_opportunities = [
                    opportunity
                    for opportunity in valid_opportunities
                    if "fund"
                    in (
                        " ".join(
                            [
                                str(
                                    opportunity.get(
                                        "category",
                                        "",
                                    )
                                ),
                                str(
                                    opportunity.get(
                                        "title",
                                        "",
                                    )
                                ),
                                str(
                                    opportunity.get(
                                        "evidence",
                                        "",
                                    )
                                ),
                                str(
                                    opportunity.get(
                                        "recommended_action",
                                        "",
                                    )
                                ),
                            ]
                        ).lower()
                    )
                ]

                if not funding_opportunities:
                    answer = (
                        f"AI-FOS has not identified any "
                        f"validated funding opportunities for "
                        f"{organization_name}."
                    )

                else:
                    opportunity_text = build_opportunity_text(funding_opportunities[:5])

                    answer = (
                        f"AI-FOS identifies the following "
                        f"validated funding opportunities for "
                        f"{organization_name}:\n\n"
                        f"{opportunity_text}"
                    )

            elif intent == "liquidity_opportunities":

                liquidity_opportunities = [
                    opportunity
                    for opportunity in valid_opportunities
                    if "liquid"
                    in (
                        " ".join(
                            [
                                str(
                                    opportunity.get(
                                        "category",
                                        "",
                                    )
                                ),
                                str(
                                    opportunity.get(
                                        "title",
                                        "",
                                    )
                                ),
                                str(
                                    opportunity.get(
                                        "evidence",
                                        "",
                                    )
                                ),
                                str(
                                    opportunity.get(
                                        "recommended_action",
                                        "",
                                    )
                                ),
                            ]
                        ).lower()
                    )
                ]

                if not liquidity_opportunities:
                    answer = (
                        f"AI-FOS has not identified any "
                        f"validated liquidity opportunities for "
                        f"{organization_name}."
                    )

                else:
                    opportunity_text = build_opportunity_text(
                        liquidity_opportunities[:5]
                    )

                    answer = (
                        f"AI-FOS identifies the following "
                        f"validated liquidity opportunities for "
                        f"{organization_name}:\n\n"
                        f"{opportunity_text}"
                    )

        # ==================================================
        # FINANCIAL HEALTH
        # ==================================================

        elif intent in self.FINANCIAL_HEALTH_INTENTS:

            score = int(
                financial_health.get(
                    "score",
                    0,
                )
                or 0
            )

            maximum = int(
                financial_health.get(
                    "maximum",
                    100,
                )
                or 100
            )

            rating = str(
                financial_health.get(
                    "rating",
                    "Unknown",
                )
                or "Unknown"
            )

            categories = (
                financial_health.get(
                    "categories",
                    {},
                )
                or {}
            )

            category_rows: list[
                tuple[
                    str,
                    float,
                    float,
                    float,
                    str,
                ]
            ] = []

            for (
                category_name,
                category,
            ) in categories.items():

                category_score = self._to_float(category.get("score"))

                category_maximum = self._to_float(category.get("maximum"))

                percentage = (
                    category_score / category_maximum * 100
                    if category_maximum > 0
                    else 0.0
                )

                reason = str(
                    category.get(
                        "reason",
                        "",
                    )
                    or ""
                )

                category_rows.append(
                    (
                        category_name,
                        category_score,
                        category_maximum,
                        percentage,
                        reason,
                    )
                )

            category_rows.sort(key=lambda row: row[3])

            # ------------------------------------------
            # Financial Health summary
            # ------------------------------------------

            if intent == "financial_health":

                if category_rows:

                    weakest_category = category_rows[0]

                    weakest_name = self._format_name(weakest_category[0])

                    weakest_score = weakest_category[1]

                    weakest_maximum = weakest_category[2]

                    answer = (
                        f"{organisation_name}'s Financial "
                        f"Health Score is "
                        f"{score}/{maximum}, rated {rating}. "
                        f"The weakest assessed area is "
                        f"{weakest_name}, scoring "
                        f"{weakest_score:,.0f}/"
                        f"{weakest_maximum:,.0f}. "
                        f"This score is based on AI-FOS's "
                        f"validated Financial Health assessment."
                    )

                else:

                    answer = (
                        f"{organisation_name}'s Financial "
                        f"Health Score is "
                        f"{score}/{maximum}, rated {rating}. "
                        f"A detailed category breakdown is "
                        f"not currently available."
                    )

            # ------------------------------------------
            # Financial Health explanation
            # ------------------------------------------

            else:

                weakest_categories = category_rows[:3]

                if weakest_categories:

                    explanation_parts: list[str] = []

                    for (
                        index,
                        row,
                    ) in enumerate(
                        weakest_categories,
                        start=1,
                    ):

                        category_name = self._format_name(row[0])

                        category_score = row[1]

                        category_maximum = row[2]

                        reason = row[4]

                        if reason:

                            explanation_parts.append(
                                (
                                    f"{index}. "
                                    f"{category_name}: "
                                    f"{category_score:,.0f}/"
                                    f"{category_maximum:,.0f}. "
                                    f"{reason}"
                                )
                            )

                        else:

                            explanation_parts.append(
                                (
                                    f"{index}. "
                                    f"{category_name}: "
                                    f"{category_score:,.0f}/"
                                    f"{category_maximum:,.0f}."
                                )
                            )

                    explanation = " ".join(explanation_parts)

                    strongest_category = max(
                        category_rows,
                        key=lambda row: row[3],
                    )

                    strongest_name = self._format_name(strongest_category[0])

                    strongest_score = strongest_category[1]

                    strongest_maximum = strongest_category[2]

                    answer = (
                        f"{organisation_name}'s Financial "
                        f"Health Score is {score}/{maximum}, "
                        f"rated {rating}. "
                        f"The main factors reducing the score "
                        f"are: {explanation} "
                        f"The strongest assessed area is "
                        f"{strongest_name}, scoring "
                        f"{strongest_score:,.0f}/"
                        f"{strongest_maximum:,.0f}. "
                        f"AI-FOS is explaining the validated "
                        f"Financial Health assessment and is "
                        f"not recalculating the underlying "
                        f"financial results."
                    )

                else:

                    answer = (
                        f"{organisation_name}'s Financial "
                        f"Health Score is {score}/{maximum}, "
                        f"rated {rating}. "
                        f"A detailed category breakdown is "
                        f"not currently available."
                    )

        # ==================================================
        # BUDGET INTELLIGENCE
        # ==================================================

        elif intent in self.BUDGET_INTENTS:

            portfolio_control = (
                budget_dashboard.get(
                    "portfolio_control",
                    {},
                )
                or {}
            )

            total_budget = self._to_float(portfolio_control.get("total_budget"))

            total_actual = self._to_float(portfolio_control.get("total_actual"))

            utilization = self._to_float(
                portfolio_control.get("utilization_percentage")
            )

            total_variance = self._to_float(portfolio_control.get("total_variance"))

            overall_variance = self._to_float(
                portfolio_control.get("overall_variance_including_unbudgeted")
            )

            unbudgeted_actual = self._to_float(
                portfolio_control.get("unbudgeted_actual")
            )

            over_budget_count = int(
                portfolio_control.get(
                    "over_budget_count",
                    0,
                )
                or 0
            )

            # ------------------------------------------
            # Budget dimension drill-down
            # ------------------------------------------

            if intent == "budget_dimension_drilldown":

                dimension_drilldown = (
                    budget_dashboard.get(
                        "dimension_drilldown",
                        {},
                    )
                    or {}
                )

                cleaned_question = str(question or "").strip().lower()

                matched_record = None
                matched_dimension = None

                for (
                    dimension_name,
                    dimension_data,
                ) in dimension_drilldown.items():

                    records = (
                        dimension_data.get(
                            "records",
                            [],
                        )
                        or []
                    )

                    for record in records:

                        record_code = str(
                            record.get(
                                "code",
                                "",
                            )
                            or ""
                        ).strip()

                        record_name = str(
                            record.get(
                                "name",
                                "",
                            )
                            or ""
                        ).strip()

                        if record_name and record_name.lower() in cleaned_question:
                            matched_record = record
                            matched_dimension = dimension_name
                            break

                        if record_code and record_code.lower() in cleaned_question:
                            matched_record = record
                            matched_dimension = dimension_name
                            break

                    if matched_record:
                        break

                if not matched_record:

                    answer = (
                        "Budget drill-down intelligence is "
                        "available, but I could not identify "
                        "which specific Fund, Donor, Program, "
                        "Category, Budget Line, Donor Line, "
                        "or Project you want to investigate. "
                        "Please include its name or code."
                    )

                else:

                    drilldown_views = (
                        matched_record.get(
                            "drilldown",
                            {},
                        )
                        or {}
                    )

                    preferred_dimension = None

                    for candidate in [
                        "program",
                        "budget_line",
                        "category",
                        "fund",
                        "donor_line",
                        "project",
                    ]:
                        if candidate in drilldown_views:
                            preferred_dimension = candidate
                            break

                    if not preferred_dimension:

                        answer = (
                            f"Drill-down intelligence exists for "
                            f"{matched_record.get('name') or matched_record.get('code')}, "
                            f"but no underlying dimension detail "
                            f"is currently available."
                        )

                    else:

                        selected_view = (
                            drilldown_views.get(
                                preferred_dimension,
                                {},
                            )
                            or {}
                        )

                        summary = (
                            selected_view.get(
                                "summary",
                                {},
                            )
                            or {}
                        )

                        lines = (
                            selected_view.get(
                                "lines",
                                [],
                            )
                            or []
                        )

                        selected_lines = sorted(
                            lines,
                            key=lambda item: (self._to_float(item.get("variance"))),
                        )[:5]

                        record_name = (
                            matched_record.get("name")
                            or matched_record.get("code")
                            or "--"
                        )

                        record_code = matched_record.get("code") or "--"

                        total_variance = self._to_float(summary.get("total_variance"))

                        if total_variance < 0:
                            variance_text = (
                                f"an unfavorable budget variance "
                                f"of {abs(total_variance):,.2f} "
                                f"{currency}"
                            )

                        elif total_variance > 0:
                            variance_text = (
                                f"a favorable budget variance "
                                f"of {total_variance:,.2f} "
                                f"{currency}"
                            )

                        else:
                            variance_text = "no net budget variance"

                        driver_parts = []

                        for line in selected_lines:

                            line_name = line.get("name") or line.get("code") or "--"

                            line_variance = self._to_float(line.get("variance"))

                            if line_variance < 0:
                                driver_parts.append(
                                    f"{line_name}: "
                                    f"{abs(line_variance):,.2f} "
                                    f"{currency} unfavorable"
                                )

                            elif line_variance > 0:
                                driver_parts.append(
                                    f"{line_name}: "
                                    f"{line_variance:,.2f} "
                                    f"{currency} favorable"
                                )

                            else:
                                driver_parts.append(f"{line_name}: no variance")

                        drivers_text = (
                            "; ".join(driver_parts)
                            if driver_parts
                            else (
                                "No underlying variance drivers "
                                "are currently available."
                            )
                        )

                        answer = (
                            f"{record_name} ({record_code}) has "
                            f"{variance_text}. "
                            f"The available "
                            f"{preferred_dimension.replace('_', ' ')} "
                            f"drill-down shows: "
                            f"{drivers_text}. "
                            f"This explanation uses validated "
                            f"AI-FOS drill-down outputs and does "
                            f"not recalculate financial results."
                        )

            # ------------------------------------------
            # Total portfolio budget
            # ------------------------------------------

            # ------------------------------------------
            # Total portfolio budget
            # ------------------------------------------

            elif intent == "portfolio_total_budget":

                answer = (
                    f"{organisation_name}'s total approved "
                    f"portfolio budget is "
                    f"{total_budget:,.2f} {currency}. "
                    f"Recorded portfolio spending is currently "
                    f"{total_actual:,.2f} {currency}."
                )

            # ------------------------------------------
            # Portfolio utilization
            # ------------------------------------------

            elif intent == "portfolio_budget_utilization":

                answer = (
                    f"{organisation_name}'s portfolio budget "
                    f"utilization is {utilization:.2f}%. "
                    f"Recorded spending is "
                    f"{total_actual:,.2f} {currency} against "
                    f"an approved portfolio budget of "
                    f"{total_budget:,.2f} {currency}."
                )

            # ------------------------------------------
            # Portfolio variance
            # ------------------------------------------

            elif intent == "portfolio_budget_variance":

                answer = (
                    f"{organisation_name}'s portfolio budget "
                    f"variance against approved budget lines is "
                    f"{total_variance:,.2f} {currency}. "
                    f"After including unbudgeted actual spending, "
                    f"the overall portfolio variance is "
                    f"{overall_variance:,.2f} {currency}."
                )

            # ------------------------------------------
            # Remaining portfolio budget
            # ------------------------------------------

            elif intent == "portfolio_budget_remaining":

                if overall_variance > 0:

                    answer = (
                        f"{organisation_name} has "
                        f"{overall_variance:,.2f} {currency} "
                        f"of portfolio budget remaining after "
                        f"accounting for recorded spending, "
                        f"including unbudgeted actual spending. "
                        f"Current portfolio utilization is "
                        f"{utilization:.2f}%."
                    )

                elif overall_variance < 0:

                    answer = (
                        f"{organisation_name} has no portfolio "
                        f"budget remaining. Recorded spending "
                        f"exceeds the portfolio budget by "
                        f"{abs(overall_variance):,.2f} {currency} "
                        f"after including unbudgeted actual "
                        f"spending. Current portfolio utilization "
                        f"is {utilization:.2f}%."
                    )

                else:

                    answer = (
                        f"{organisation_name}'s recorded spending "
                        f"exactly equals the available portfolio "
                        f"budget after including unbudgeted actual "
                        f"spending. No portfolio budget remains."
                    )

            # ------------------------------------------
            # Overall portfolio budget position
            # ------------------------------------------

            elif intent == "portfolio_budget_position":

                if overall_variance > 0:

                    position_text = (
                        f"under its total portfolio budget by "
                        f"{overall_variance:,.2f} {currency}"
                    )

                elif overall_variance < 0:

                    position_text = (
                        f"over its total portfolio budget by "
                        f"{abs(overall_variance):,.2f} {currency}"
                    )

                else:

                    position_text = "exactly at its total portfolio budget"

                answer = (
                    f"{organisation_name} is currently "
                    f"{position_text}. "
                    f"Recorded spending is "
                    f"{total_actual:,.2f} {currency} against "
                    f"a total approved budget of "
                    f"{total_budget:,.2f} {currency}. "
                    f"Portfolio utilization is "
                    f"{utilization:.2f}%. "
                    f"Unbudgeted actual spending is "
                    f"{unbudgeted_actual:,.2f} {currency}, "
                    f"and {over_budget_count} budget line(s) "
                    f"are above their approved limits."
                )

            # ------------------------------------------
            # Unbudgeted actual spending
            # ------------------------------------------

            elif intent == "unbudgeted_actual":

                if unbudgeted_actual > 0:

                    answer = (
                        f"{organisation_name} has "
                        f"{unbudgeted_actual:,.2f} {currency} "
                        f"of actual portfolio spending without "
                        f"a matching approved budget. "
                        f"This amount is included when AI-FOS "
                        f"assesses the overall portfolio budget "
                        f"position."
                    )

                else:

                    answer = (
                        f"AI-FOS currently identifies no "
                        f"portfolio actual spending without a "
                        f"matching approved budget for "
                        f"{organisation_name}."
                    )

            # ------------------------------------------
            # Over-budget lines
            # ------------------------------------------

            elif intent == "over_budget_count":

                if over_budget_count > 0:

                    answer = (
                        f"{organisation_name} currently has "
                        f"{over_budget_count} portfolio budget "
                        f"line(s) above their approved limits. "
                        f"These lines require management review "
                        f"within the validated Budget vs Actual "
                        f"analysis."
                    )

                else:

                    answer = (
                        f"AI-FOS currently identifies no "
                        f"portfolio budget lines above their "
                        f"approved limits for "
                        f"{organisation_name}."
                    )

            # ------------------------------------------
            # Portfolio budget summary
            # ------------------------------------------

            elif intent == "portfolio_budget_summary":

                answer = (
                    f"{organisation_name}'s approved portfolio "
                    f"budget is {total_budget:,.2f} {currency}, "
                    f"with recorded spending of "
                    f"{total_actual:,.2f} {currency}. "
                    f"Portfolio utilization is "
                    f"{utilization:.2f}%. "
                    f"The variance against approved budget "
                    f"lines is {total_variance:,.2f} {currency}, "
                    f"while the overall variance after including "
                    f"unbudgeted actual spending is "
                    f"{overall_variance:,.2f} {currency}. "
                    f"Unbudgeted actual spending totals "
                    f"{unbudgeted_actual:,.2f} {currency}, "
                    f"and {over_budget_count} budget line(s) "
                    f"are above their approved limits."
                )

            # ------------------------------------------
            # Budget performance summary
            # ------------------------------------------

            else:

                if overall_variance > 0:

                    performance_position = (
                        f"the portfolio remains under budget by "
                        f"{overall_variance:,.2f} {currency}"
                    )

                elif overall_variance < 0:

                    performance_position = (
                        f"recorded spending exceeds the portfolio "
                        f"budget by "
                        f"{abs(overall_variance):,.2f} {currency}"
                    )

                else:

                    performance_position = (
                        "recorded spending currently equals the "
                        "total portfolio budget"
                    )

                control_issues: list[str] = []

                if unbudgeted_actual > 0:
                    control_issues.append(
                        (
                            f"{unbudgeted_actual:,.2f} {currency} "
                            f"of unbudgeted actual spending"
                        )
                    )

                if over_budget_count > 0:
                    control_issues.append(
                        (
                            f"{over_budget_count} budget line(s) "
                            f"above approved limits"
                        )
                    )

                if control_issues:

                    control_text = (
                        " Budget-control issues requiring "
                        "management attention include "
                        + " and ".join(control_issues)
                        + "."
                    )

                else:

                    control_text = (
                        " AI-FOS currently identifies no "
                        "unbudgeted actual spending or "
                        "over-budget portfolio lines."
                    )

                answer = (
                    f"{organisation_name}'s portfolio budget "
                    f"utilization is {utilization:.2f}%, and "
                    f"{performance_position}. "
                    f"Recorded spending is "
                    f"{total_actual:,.2f} {currency} against "
                    f"{total_budget:,.2f} {currency} of approved "
                    f"budget."
                    f"{control_text} "
                    f"This explanation uses the validated "
                    f"Budget vs Actual dashboard and does not "
                    f"recalculate the underlying financial data."
                )

        # ==================================================
        # FINANCIAL FACTS
        # ==================================================

        elif intent in self.FINANCIAL_FACT_INTENTS:

            value = self.financial_intelligence_service.get_value(
                intent=intent,
                financial_facts=financial_facts,
            )

            amount = self._to_float(value)

            labels = {
                "revenue": "total revenue",
                "expenses": "total expenses",
                "net_profit": "net result",
                "assets": "total assets",
                "liabilities": "total liabilities",
                "equity": "total equity",
            }

            statement_labels = {
                "revenue": "Income Statement",
                "expenses": "Income Statement",
                "net_profit": "Income Statement",
                "assets": "Balance Sheet",
                "liabilities": "Balance Sheet",
                "equity": "Balance Sheet",
            }

            label = labels[intent]

            statement_label = statement_labels[intent]

            # ------------------------------------------
            # Revenue
            # ------------------------------------------

            if intent == "revenue":

                answer = (
                    f"{organisation_name}'s total revenue is "
                    f"{amount:,.2f} {currency}. "
                    f"This amount comes from the validated "
                    f"{statement_label} financial facts."
                )

            # ------------------------------------------
            # Expenses
            # ------------------------------------------

            elif intent == "expenses":

                answer = (
                    f"{organisation_name}'s total expenses are "
                    f"{amount:,.2f} {currency}. "
                    f"This amount comes from the validated "
                    f"{statement_label} financial facts."
                )

            # ------------------------------------------
            # Net result
            # ------------------------------------------

            elif intent == "net_profit":

                if amount > 0:

                    result_position = f"a surplus of " f"{amount:,.2f} {currency}"

                elif amount < 0:

                    result_position = f"a deficit of " f"{abs(amount):,.2f} {currency}"

                else:

                    result_position = "a break-even net result of " f"0.00 {currency}"

                answer = (
                    f"{organisation_name} currently reports "
                    f"{result_position}. "
                    f"The validated net result is "
                    f"{amount:,.2f} {currency} in the "
                    f"{statement_label} financial facts."
                )

            # ------------------------------------------
            # Assets
            # ------------------------------------------

            elif intent == "assets":

                answer = (
                    f"{organisation_name}'s total assets are "
                    f"{amount:,.2f} {currency}. "
                    f"This amount comes from the validated "
                    f"{statement_label} financial facts."
                )

            # ------------------------------------------
            # Liabilities
            # ------------------------------------------

            elif intent == "liabilities":

                answer = (
                    f"{organisation_name}'s total liabilities "
                    f"are {amount:,.2f} {currency}. "
                    f"This amount comes from the validated "
                    f"{statement_label} financial facts."
                )

            # ------------------------------------------
            # Equity / net assets
            # ------------------------------------------

            else:

                answer = (
                    f"{organisation_name}'s total equity is "
                    f"{amount:,.2f} {currency}. "
                    f"This amount comes from the validated "
                    f"{statement_label} financial facts."
                )

        # ==================================================
        # FINANCIAL TREND INTELLIGENCE
        # ==================================================

        elif intent in self.FINANCIAL_TREND_INTENTS:

            monthly_comparison = financial_trends.get("latest_month_comparison") or {}

            annual_comparison = financial_trends.get("latest_year_comparison") or {}

            comparison = monthly_comparison or annual_comparison

            if not comparison:

                answer = (
                    f"AI-FOS does not yet have enough observed "
                    f"financial periods to determine a reliable "
                    f"trend for {organisation_name}."
                )

            else:

                current_period = comparison.get("current_period")

                previous_period = comparison.get("previous_period")

                caution = comparison.get(
                    "caution",
                    "",
                )

                if intent == "revenue_trend":

                    revenue_trend = comparison.get("revenue") or {}

                    direction = revenue_trend.get(
                        "direction",
                        "unchanged",
                    )

                    current_value = self._to_float(revenue_trend.get("current_value"))

                    previous_value = self._to_float(revenue_trend.get("previous_value"))

                    change_amount = self._to_float(revenue_trend.get("change_amount"))

                    change_percentage = revenue_trend.get("change_percentage")

                    answer = (
                        f"{organisation_name}'s revenue "
                        f"{direction} from "
                        f"{previous_period} to "
                        f"{current_period}. "
                        f"Revenue moved from "
                        f"{previous_value:,.2f} {currency} "
                        f"to {current_value:,.2f} {currency}, "
                        f"a change of "
                        f"{change_amount:,.2f} {currency}."
                    )

                    if change_percentage is not None:
                        answer += (
                            f" This represents a "
                            f"{self._to_float(change_percentage):,.2f}% "
                            f"change."
                        )

                    if caution:
                        answer += f" {caution}"

                elif intent == "expense_trend":

                    expense_trend = comparison.get("expenses") or {}

                    direction = expense_trend.get(
                        "direction",
                        "unchanged",
                    )

                    current_value = self._to_float(expense_trend.get("current_value"))

                    previous_value = self._to_float(expense_trend.get("previous_value"))

                    change_amount = self._to_float(expense_trend.get("change_amount"))

                    change_percentage = expense_trend.get("change_percentage")

                    answer = (
                        f"{organisation_name}'s expenses "
                        f"{direction} from "
                        f"{previous_period} to "
                        f"{current_period}. "
                        f"Expenses moved from "
                        f"{previous_value:,.2f} {currency} "
                        f"to {current_value:,.2f} {currency}, "
                        f"a change of "
                        f"{change_amount:,.2f} {currency}."
                    )

                    if change_percentage is not None:
                        answer += (
                            f" This represents a "
                            f"{self._to_float(change_percentage):,.2f}% "
                            f"change."
                        )

                    if caution:
                        answer += f" {caution}"

                elif intent == "net_result_trend":

                    net_result_trend = comparison.get("net_result") or {}

                    direction = net_result_trend.get(
                        "direction",
                        "unchanged",
                    )

                    current_value = self._to_float(
                        net_result_trend.get("current_value")
                    )

                    previous_value = self._to_float(
                        net_result_trend.get("previous_value")
                    )

                    change_amount = self._to_float(
                        net_result_trend.get("change_amount")
                    )

                    change_percentage = net_result_trend.get("change_percentage")

                    answer = (
                        f"{organisation_name}'s net result "
                        f"{direction} from "
                        f"{previous_period} to "
                        f"{current_period}. "
                        f"The net result moved from "
                        f"{previous_value:,.2f} {currency} "
                        f"to {current_value:,.2f} {currency}, "
                        f"a change of "
                        f"{change_amount:,.2f} {currency}."
                    )

                    if change_percentage is not None:
                        answer += (
                            f" This represents a "
                            f"{self._to_float(change_percentage):,.2f}% "
                            f"change."
                        )

                    if caution:
                        answer += f" {caution}"

                else:

                    revenue_trend = comparison.get("revenue") or {}

                    expense_trend = comparison.get("expenses") or {}

                    net_result_trend = comparison.get("net_result") or {}

                    answer = (
                        f"From {previous_period} to "
                        f"{current_period}, "
                        f"{organisation_name}'s revenue "
                        f"{revenue_trend.get('direction', 'unchanged')}, "
                        f"expenses "
                        f"{expense_trend.get('direction', 'unchanged')}, "
                        f"and net result "
                        f"{net_result_trend.get('direction', 'unchanged')}. "
                        f"AI-FOS is reporting the direction of "
                        f"change from validated observed financial "
                        f"periods without interpreting those changes "
                        f"as automatically good or bad."
                    )

                    if caution:
                        answer += f" {caution}"

        # ==================================================
        # FINANCIAL FORECAST INTELLIGENCE
        # ==================================================

        elif intent in self.FINANCIAL_FORECAST_INTENTS:

            forecast_status = financial_forecast.get("status")

            if forecast_status != "available":

                reason = financial_forecast.get(
                    "reason",
                    (
                        "AI-FOS does not yet have enough "
                        "validated historical data to build "
                        "a reliable baseline financial forecast."
                    ),
                )

                answer = (
                    f"Financial Forecast Intelligence is not "
                    f"currently available for "
                    f"{organisation_name}. "
                    f"{reason}"
                )

            else:

                forecast_horizon_months = int(
                    self._to_float(financial_forecast.get("forecast_horizon_months"))
                )

                forecast_totals = (
                    financial_forecast.get(
                        "forecast_totals",
                        {},
                    )
                    or {}
                )

                baseline = (
                    financial_forecast.get(
                        "baseline",
                        {},
                    )
                    or {}
                )

                confidence = (
                    financial_forecast.get(
                        "confidence",
                        {},
                    )
                    or {}
                )

                forecast_series = (
                    financial_forecast.get(
                        "forecast_series",
                        [],
                    )
                    or []
                )

                methodology_description = financial_forecast.get(
                    "methodology_description",
                    "",
                )

                confidence_level = confidence.get(
                    "level",
                    "Unknown",
                )

                confidence_reason = confidence.get(
                    "reason",
                    "",
                )

                forecast_periods = [
                    str(row.get("period"))
                    for row in forecast_series
                    if isinstance(row, dict) and row.get("period")
                ]

                period_text = ""

                if forecast_periods:

                    period_text = (
                        f" The forecast covers "
                        f"{forecast_periods[0]} through "
                        f"{forecast_periods[-1]}."
                    )

                # ------------------------------------------
                # Revenue forecast
                # ------------------------------------------

                if intent == "revenue_forecast":

                    monthly_revenue = self._to_float(
                        baseline.get("average_monthly_revenue")
                    )

                    total_revenue = self._to_float(forecast_totals.get("revenue"))

                    answer = (
                        f"{organisation_name}'s baseline revenue "
                        f"forecast for the next "
                        f"{forecast_horizon_months} month(s) is "
                        f"{total_revenue:,.2f} {currency}. "
                        f"The baseline assumes average monthly "
                        f"revenue of "
                        f"{monthly_revenue:,.2f} {currency}."
                        f"{period_text} "
                        f"Forecast confidence is "
                        f"{confidence_level}."
                    )

                    if confidence_reason:
                        answer += f" {confidence_reason}"

                    if methodology_description:
                        answer += f" Methodology: " f"{methodology_description}"

                # ------------------------------------------
                # Expense forecast
                # ------------------------------------------

                elif intent == "expense_forecast":

                    monthly_expenses = self._to_float(
                        baseline.get("average_monthly_expenses")
                    )

                    total_expenses = self._to_float(forecast_totals.get("expenses"))

                    answer = (
                        f"{organisation_name}'s baseline expense "
                        f"forecast for the next "
                        f"{forecast_horizon_months} month(s) is "
                        f"{total_expenses:,.2f} {currency}. "
                        f"The baseline assumes average monthly "
                        f"expenses of "
                        f"{monthly_expenses:,.2f} {currency}."
                        f"{period_text} "
                        f"Forecast confidence is "
                        f"{confidence_level}."
                    )

                    if confidence_reason:
                        answer += f" {confidence_reason}"

                    if methodology_description:
                        answer += f" Methodology: " f"{methodology_description}"

                # ------------------------------------------
                # Net result forecast
                # ------------------------------------------

                elif intent == "net_result_forecast":

                    monthly_net_result = self._to_float(
                        baseline.get("average_monthly_net_result")
                    )

                    total_net_result = self._to_float(forecast_totals.get("net_result"))

                    if total_net_result > 0:

                        forecast_position = (
                            f"a projected surplus of "
                            f"{total_net_result:,.2f} {currency}"
                        )

                    elif total_net_result < 0:

                        forecast_position = (
                            f"a projected deficit of "
                            f"{abs(total_net_result):,.2f} "
                            f"{currency}"
                        )

                    else:

                        forecast_position = (
                            f"a projected break-even result " f"of 0.00 {currency}"
                        )

                    answer = (
                        f"For the next "
                        f"{forecast_horizon_months} month(s), "
                        f"{organisation_name}'s baseline forecast "
                        f"indicates {forecast_position}. "
                        f"The baseline average monthly net result "
                        f"is "
                        f"{monthly_net_result:,.2f} {currency}."
                        f"{period_text} "
                        f"Forecast confidence is "
                        f"{confidence_level}."
                    )

                    if confidence_reason:
                        answer += f" {confidence_reason}"

                    if methodology_description:
                        answer += f" Methodology: " f"{methodology_description}"

                # ------------------------------------------
                # Financial forecast summary
                # ------------------------------------------

                else:

                    total_revenue = self._to_float(forecast_totals.get("revenue"))

                    total_expenses = self._to_float(forecast_totals.get("expenses"))

                    total_net_result = self._to_float(forecast_totals.get("net_result"))

                    answer = (
                        f"{organisation_name}'s baseline financial "
                        f"forecast covers the next "
                        f"{forecast_horizon_months} month(s). "
                        f"Projected revenue is "
                        f"{total_revenue:,.2f} {currency}, "
                        f"projected expenses are "
                        f"{total_expenses:,.2f} {currency}, "
                        f"and the projected net result is "
                        f"{total_net_result:,.2f} {currency}."
                        f"{period_text} "
                        f"Forecast confidence is "
                        f"{confidence_level}. "
                        f"These figures represent a baseline "
                        f"planning forecast rather than a "
                        f"guaranteed future outcome."
                    )

                    if confidence_reason:
                        answer += f" {confidence_reason}"

                    if methodology_description:
                        answer += f" Methodology: " f"{methodology_description}"

        # ==================================================
        # SAVED SCENARIO INTELLIGENCE
        # ==================================================

        elif intent in self.SAVED_SCENARIO_INTENTS:

            saved_scenarios = ScenarioHistoryService.list_scenarios(
                financial_model_folder
            )

            if intent == "saved_scenario_list":

                if not saved_scenarios:

                    answer = (
                        "AI-FOS does not currently have any saved "
                        "financial scenarios for this organization."
                    )

                else:

                    scenario_names = []

                    for record in saved_scenarios:

                        scenario_name = str(
                            record.get(
                                "scenario_name",
                                "Unnamed Scenario",
                            )
                            or "Unnamed Scenario"
                        )

                        scenario_names.append(
                            scenario_name
                        )

                    answer = (
                        f"AI-FOS currently has "
                        f"{len(scenario_names)} saved financial "
                        f"scenario(s): "
                        + "; ".join(scenario_names)
                        + "."
                    )

            else:

                cleaned_question = question.lower().strip()

                matching_records = []

                for record in saved_scenarios:

                    scenario_name = str(
                        record.get(
                            "scenario_name",
                            "",
                        )
                        or ""
                    ).strip()

                    if (
                        scenario_name
                        and scenario_name.lower()
                        in cleaned_question
                    ):
                        matching_records.append(
                            record
                        )

                if len(matching_records) != 2:

                    answer = (
                        "AI-FOS can compare saved financial "
                        "scenarios, but exactly two saved scenario "
                        "names must be identified in the question."
                    )

                else:

                    scenario_a_record = matching_records[0]
                    scenario_b_record = matching_records[1]

                    scenario_a_decision = (
                        scenario_a_record.get(
                            "scenario_decision_intelligence",
                            {},
                        )
                        or {}
                    )

                    scenario_b_decision = (
                        scenario_b_record.get(
                            "scenario_decision_intelligence",
                            {},
                        )
                        or {}
                    )

                    if (
                        scenario_a_decision.get("status")
                        != "available"
                        or scenario_b_decision.get("status")
                        != "available"
                    ):

                        answer = (
                            "AI-FOS cannot compare these saved "
                            "scenarios because verified Scenario "
                            "Decision Intelligence is unavailable "
                            "for one or both scenarios."
                        )

                    else:

                        comparison_result = (
                            generate_scenario_comparison_intelligence(
                                scenario_a_decision,
                                scenario_b_decision,
                            )
                        )

                        scenario_a_name = str(
                            scenario_a_record.get(
                                "scenario_name",
                                "Scenario A",
                            )
                            or "Scenario A"
                        )

                        scenario_b_name = str(
                            scenario_b_record.get(
                                "scenario_name",
                                "Scenario B",
                            )
                            or "Scenario B"
                        )

                        comparison_signal = (
                            comparison_result.get(
                                "comparison_signal",
                                "not_comparable",
                            )
                        )

                        preferred_scenario = (
                            comparison_result.get(
                                "preferred_scenario"
                            )
                        )

                        answer = (
                            f"Saved Scenario A: "
                            f"{scenario_a_name}. "
                            f"Saved Scenario B: "
                            f"{scenario_b_name}. "
                        )

                        if (
                            comparison_signal
                            == "clear_preference"
                            and preferred_scenario
                        ):

                            answer += (
                                f"AI-FOS identifies "
                                f"{preferred_scenario} "
                                f"as the preferred scenario "
                                f"based on the existing verified "
                                f"Scenario Decision Intelligence."
                            )

                        elif comparison_signal == "mixed":

                            answer += (
                                "The saved-scenario comparison is "
                                "mixed. AI-FOS does not identify a "
                                "single preferred scenario because "
                                "the verified signals conflict."
                            )

                        else:

                            answer += (
                                "AI-FOS cannot identify a preferred "
                                "scenario from the currently saved "
                                "verified comparison evidence."
                            )

        # ==================================================
        # FINANCIAL SCENARIO INTELLIGENCE
        # ==================================================

        elif intent == "scenario_comparison":

            cleaned_comparison_question = (
                question.lower().strip()
            )

            comparison_parts = re.split(
                r"\s+(?:versus|vs\.?)\s+",
                cleaned_comparison_question,
                maxsplit=1,
            )

            if len(comparison_parts) != 2:

                answer = (
                    "AI-FOS can compare financial scenarios, "
                    "but two explicit scenarios are required. "
                    "Please provide or specify both Scenario A "
                    "and Scenario B, including the financial "
                    "assumption and percentage for each."
                )

            else:

                decrease_words = (
                    "decrease",
                    "decreases",
                    "decreased",
                    "decreasing",
                    "drop",
                    "drops",
                    "dropped",
                    "dropping",
                    "fall",
                    "falls",
                    "fell",
                    "falling",
                    "decline",
                    "declines",
                    "declined",
                    "declining",
                    "reduce",
                    "reduces",
                    "reduced",
                    "reducing",
                    "reduction",
                    "cut",
                    "cuts",
                )

                increase_words = (
                    "increase",
                    "increases",
                    "increased",
                    "increasing",
                    "rise",
                    "rises",
                    "rose",
                    "rising",
                    "grow",
                    "grows",
                    "grew",
                    "growing",
                    "growth",
                    "higher",
                )

                parsed_scenarios = []

                for index, scenario_text in enumerate(
                    comparison_parts,
                    start=1,
                ):

                    percentage_match = re.search(
                        r"(-?\d+(?:\.\d+)?)\s*%",
                        scenario_text,
                    )

                    revenue_subject = (
                        "revenue" in scenario_text
                        or "income" in scenario_text
                    )

                    expense_subject = (
                        "expense" in scenario_text
                        or "expenses" in scenario_text
                        or "cost" in scenario_text
                        or "costs" in scenario_text
                    )

                    has_decrease = any(
                        word in scenario_text
                        for word in decrease_words
                    )

                    has_increase = any(
                        word in scenario_text
                        for word in increase_words
                    )

                    scenario_ready = True

                    if percentage_match is None:
                        scenario_ready = False

                    if (
                        revenue_subject
                        == expense_subject
                    ):
                        scenario_ready = False

                    if (
                        has_decrease
                        == has_increase
                    ):
                        scenario_ready = False

                    if not scenario_ready:
                        parsed_scenarios = []
                        break

                    explicit_percentage = self._to_float(
                        percentage_match.group(1)
                    )

                    if has_decrease:
                        scenario_percentage = -abs(
                            explicit_percentage
                        )

                    else:
                        scenario_percentage = abs(
                            explicit_percentage
                        )

                    revenue_change_percentage = 0.0
                    expense_change_percentage = 0.0

                    if revenue_subject:
                        revenue_change_percentage = (
                            scenario_percentage
                        )
                        subject_name = "Revenue"

                    else:
                        expense_change_percentage = (
                            scenario_percentage
                        )
                        subject_name = "Expense"

                    direction_name = (
                        "Increase"
                        if scenario_percentage > 0
                        else "Decrease"
                    )

                    scenario_name = (
                        f"Scenario "
                        f"{'A' if index == 1 else 'B'}: "
                        f"{subject_name} "
                        f"{direction_name} "
                        f"{abs(scenario_percentage):,.2f}%"
                    )

                    parsed_scenarios.append(
                        {
                            "scenario_name": scenario_name,
                            "revenue_change_percentage": (
                                revenue_change_percentage
                            ),
                            "expense_change_percentage": (
                                expense_change_percentage
                            ),
                            "percentage": abs(
                                scenario_percentage
                            ),
                        }
                    )

                if len(parsed_scenarios) != 2:

                    answer = (
                        "AI-FOS can compare financial scenarios, "
                        "but both scenarios must be explicit. "
                        "For each scenario, specify revenue or "
                        "expenses, an increase or decrease, and "
                        "a percentage."
                    )

                else:

                    scenario_results = []

                    for parsed in parsed_scenarios:

                        scenario_result = (
                            generate_financial_scenario(
                                financial_forecast=(
                                    financial_forecast
                                ),
                                liquidity=liquidity,
                                scenario_name=(
                                    parsed[
                                        "scenario_name"
                                    ]
                                ),
                                revenue_change_percentage=(
                                    parsed[
                                        "revenue_change_percentage"
                                    ]
                                ),
                                expense_change_percentage=(
                                    parsed[
                                        "expense_change_percentage"
                                    ]
                                ),
                            )
                        )

                        if (
                            scenario_result.get("status")
                            != "available"
                        ):
                            scenario_results = []
                            break

                        decision_result = (
                            generate_scenario_decision_intelligence(
                                scenario_result
                            )
                        )

                        if (
                            decision_result.get("status")
                            != "available"
                        ):
                            scenario_results = []
                            break

                        scenario_results.append(
                            decision_result
                        )

                    if len(scenario_results) != 2:

                        answer = (
                            "AI-FOS cannot compare these "
                            "scenarios yet because one or both "
                            "scenario results are unavailable."
                        )

                    else:

                        comparison_result = (
                            generate_scenario_comparison_intelligence(
                                scenario_results[0],
                                scenario_results[1],
                            )
                        )

                        preferred_scenario = (
                            comparison_result.get(
                                "preferred_scenario"
                            )
                        )

                        comparison_signal = (
                            comparison_result.get(
                                "comparison_signal",
                                "not_comparable",
                            )
                        )

                        scenario_a_name = (
                            parsed_scenarios[0][
                                "scenario_name"
                            ]
                        )

                        scenario_b_name = (
                            parsed_scenarios[1][
                                "scenario_name"
                            ]
                        )

                        answer = (
                            f"{scenario_a_name}. "
                            f"{scenario_b_name}. "
                        )

                        if (
                            comparison_signal
                            == "clear_preference"
                            and preferred_scenario
                        ):
                            answer += (
                                f"AI-FOS identifies "
                                f"{preferred_scenario} "
                                f"as the preferred scenario "
                                f"based on the verified "
                                f"comparison evidence."
                            )

                        elif comparison_signal == "mixed":
                            answer += (
                                "The comparison is mixed. "
                                "AI-FOS does not identify a "
                                "single preferred scenario "
                                "because the verified signals "
                                "conflict."
                            )

                        else:
                            answer += (
                                "AI-FOS cannot identify a "
                                "preferred scenario from the "
                                "currently available verified "
                                "comparison evidence."
                            )     
        
        elif intent in self.FINANCIAL_SCENARIO_INTENTS:

            cleaned_scenario_question = question.lower().strip()

            answer = ""

            revenue_percentage_match = re.search(
                (r"(?:revenue|income).*?" r"(-?\d+(?:\.\d+)?)\s*%"),
                cleaned_scenario_question,
            )

            expense_percentage_match = re.search(
                (r"(?:expense|expenses|cost|costs).*?" r"(-?\d+(?:\.\d+)?)\s*%"),
                cleaned_scenario_question,
            )

            combined_scenario = (
                revenue_percentage_match is not None
                and expense_percentage_match is not None
            )

            percentage_match = re.search(
                r"(-?\d+(?:\.\d+)?)\s*%",
                cleaned_scenario_question,
            )

            if percentage_match is None:

                answer = (
                    f"AI-FOS can run this what-if scenario, "
                    f"but the scenario assumption must be "
                    f"explicit. Please include a percentage, "
                    f"for example: 'What happens if revenue "
                    f"drops 10%?' or 'What if expenses "
                    f"increase 15%?'"
                )

            else:

                explicit_percentage = self._to_float(percentage_match.group(1))

                decrease_words = (
                    "decrease",
                    "decreases",
                    "decreased",
                    "drop",
                    "drops",
                    "dropped",
                    "fall",
                    "falls",
                    "fell",
                    "decline",
                    "declines",
                    "declined",
                    "reduce",
                    "reduces",
                    "reduced",
                    "reduction",
                    "cut",
                    "cuts",
                )

                increase_words = (
                    "increase",
                    "increases",
                    "increased",
                    "rise",
                    "rises",
                    "rose",
                    "grow",
                    "grows",
                    "grew",
                    "growth",
                    "higher",
                )

                has_decrease_direction = any(
                    word in cleaned_scenario_question for word in decrease_words
                )

                has_increase_direction = any(
                    word in cleaned_scenario_question for word in increase_words
                )

                revenue_change_percentage = 0.0
                expense_change_percentage = 0.0
                scenario_name = "Unspecified Scenario"
                scenario_ready = True

                if combined_scenario:

                    revenue_explicit_percentage = self._to_float(
                        revenue_percentage_match.group(1)
                    )

                    expense_explicit_percentage = self._to_float(
                        expense_percentage_match.group(1)
                    )

                    revenue_text = cleaned_scenario_question[
                        revenue_percentage_match.start() : revenue_percentage_match.end()
                    ]

                    expense_text = cleaned_scenario_question[
                        expense_percentage_match.start() : expense_percentage_match.end()
                    ]

                    revenue_has_decrease = any(
                        word in revenue_text for word in decrease_words
                    )

                    revenue_has_increase = any(
                        word in revenue_text for word in increase_words
                    )

                    expense_has_decrease = any(
                        word in expense_text for word in decrease_words
                    )

                    expense_has_increase = any(
                        word in expense_text for word in increase_words
                    )

                    if revenue_has_decrease and not revenue_has_increase:
                        revenue_change_percentage = -abs(revenue_explicit_percentage)

                    elif revenue_has_increase and not revenue_has_decrease:
                        revenue_change_percentage = abs(revenue_explicit_percentage)

                    elif revenue_explicit_percentage < 0:
                        revenue_change_percentage = revenue_explicit_percentage

                    else:
                        scenario_ready = False

                    if expense_has_decrease and not expense_has_increase:
                        expense_change_percentage = -abs(expense_explicit_percentage)

                    elif expense_has_increase and not expense_has_decrease:
                        expense_change_percentage = abs(expense_explicit_percentage)

                    elif expense_explicit_percentage < 0:
                        expense_change_percentage = expense_explicit_percentage

                    else:
                        scenario_ready = False

                    if scenario_ready:
                        scenario_name = "Combined Revenue and Expense Scenario"

                    else:
                        answer = (
                            "AI-FOS found both revenue and "
                            "expense percentage assumptions, "
                            "but the direction of one or both "
                            "assumptions is unclear. Please "
                            "specify whether each value "
                            "increases or decreases."
                        )

                else:

                    if has_decrease_direction and not has_increase_direction:
                        scenario_percentage = -abs(explicit_percentage)

                    elif has_increase_direction and not has_decrease_direction:
                        scenario_percentage = abs(explicit_percentage)

                    elif explicit_percentage < 0:
                        scenario_percentage = explicit_percentage

                    else:
                        scenario_percentage = None

                    if scenario_percentage is None:

                        scenario_ready = False

                        answer = (
                            f"AI-FOS found the explicit "
                            f"{explicit_percentage:,.2f}% "
                            f"assumption, but the direction is "
                            f"unclear. Please specify whether "
                            f"the value increases or decreases."
                        )

                    elif intent == "revenue_scenario":

                        revenue_change_percentage = scenario_percentage

                        scenario_name = (
                            f"Revenue "
                            f"{'Increase' if scenario_percentage > 0 else 'Decrease'} "
                            f"{abs(scenario_percentage):,.2f}%"
                        )

                    elif intent == "expense_scenario":

                        expense_change_percentage = scenario_percentage

                        scenario_name = (
                            f"Expense "
                            f"{'Increase' if scenario_percentage > 0 else 'Decrease'} "
                            f"{abs(scenario_percentage):,.2f}%"
                        )

                    else:

                        if (
                            "revenue" in cleaned_scenario_question
                            or "income" in cleaned_scenario_question
                        ):
                            revenue_change_percentage = scenario_percentage

                        elif (
                            "expense" in cleaned_scenario_question
                            or "expenses" in cleaned_scenario_question
                            or "cost" in cleaned_scenario_question
                            or "costs" in cleaned_scenario_question
                        ):
                            expense_change_percentage = scenario_percentage

                        else:

                            scenario_ready = False

                            answer = (
                                f"AI-FOS found the explicit "
                                f"{scenario_percentage:,.2f}% "
                                f"scenario assumption, but it "
                                f"is not clear whether it "
                                f"applies to revenue or "
                                f"expenses."
                            )

                if scenario_ready and (
                    intent != "financial_scenario_summary"
                    or revenue_change_percentage != 0.0
                    or expense_change_percentage != 0.0
                ):

                    scenario_result = generate_financial_scenario(
                        financial_forecast=(financial_forecast),
                        liquidity=liquidity,
                        scenario_name=scenario_name,
                        revenue_change_percentage=(revenue_change_percentage),
                        expense_change_percentage=(expense_change_percentage),
                    )

                    if scenario_result.get("status") != "available":

                        answer = (
                            f"AI-FOS cannot run this "
                            f"scenario yet. "
                            f"{scenario_result.get('reason', '')}"
                        )

                    else:

                        baseline_result = (
                            scenario_result.get(
                                "baseline",
                                {},
                            )
                            or {}
                        )

                        scenario_values = (
                            scenario_result.get(
                                "scenario",
                                {},
                            )
                            or {}
                        )

                        impact = (
                            scenario_result.get(
                                "impact",
                                {},
                            )
                            or {}
                        )

                        baseline_revenue = self._to_float(
                            baseline_result.get("revenue")
                        )

                        baseline_expenses = self._to_float(
                            baseline_result.get("expenses")
                        )

                        baseline_net_result = self._to_float(
                            baseline_result.get("net_result")
                        )

                        scenario_revenue = self._to_float(
                            scenario_values.get("revenue")
                        )

                        scenario_expenses = self._to_float(
                            scenario_values.get("expenses")
                        )

                        scenario_net_result = self._to_float(
                            scenario_values.get("net_result")
                        )

                        net_result_variance = self._to_float(
                            impact.get("net_result_variance")
                        )

                        direction = impact.get(
                            "net_result_direction",
                            "unchanged",
                        )

                        answer = (
                            f"{scenario_name}: "
                            f"the validated baseline forecast "
                            f"has revenue of "
                            f"{baseline_revenue:,.2f} "
                            f"{currency}, expenses of "
                            f"{baseline_expenses:,.2f} "
                            f"{currency}, and a net result "
                            f"of {baseline_net_result:,.2f} "
                            f"{currency}. "
                            f"Under the explicit scenario, "
                            f"revenue becomes "
                            f"{scenario_revenue:,.2f} "
                            f"{currency}, expenses become "
                            f"{scenario_expenses:,.2f} "
                            f"{currency}, and the net result "
                            f"becomes "
                            f"{scenario_net_result:,.2f} "
                            f"{currency}. "
                            f"The net-result impact is "
                            f"{net_result_variance:,.2f} "
                            f"{currency}, so the projected "
                            f"net result has {direction}. "
                            f"This is a hypothetical what-if "
                            f"scenario, not a prediction, and "
                            f"the validated baseline forecast "
                            f"remains unchanged."
                        )

                        decision_intelligence = generate_scenario_decision_intelligence(
                            scenario_result
                        )

                        if decision_intelligence.get("status") == "available":
                            severity = (
                                str(
                                    decision_intelligence.get(
                                        "severity",
                                        "",
                                    )
                                    or ""
                                )
                                .replace("_", " ")
                                .strip()
                            )

                            decision_signal = (
                                str(
                                    decision_intelligence.get(
                                        "decision_signal",
                                        "",
                                    )
                                    or ""
                                )
                                .replace("_", " ")
                                .strip()
                            )

                            management_attention = (
                                str(
                                    decision_intelligence.get(
                                        "management_attention",
                                        "",
                                    )
                                    or ""
                                )
                                .replace("_", " ")
                                .strip()
                            )

                            if severity:
                                severity = severity.capitalize()

                            if decision_signal:
                                decision_signal = decision_signal.capitalize()

                            if management_attention:
                                management_attention = management_attention.capitalize()

                            decision_factors = (
                                decision_intelligence.get(
                                    "decision_factors",
                                    [],
                                )
                                or []
                            )

                            factor_texts = [
                                str(factor).replace(
                                    "_",
                                    " ",
                                )
                                for factor in decision_factors
                                if factor
                            ]

                            recommended_actions = (
                                decision_intelligence.get(
                                    "recommended_actions",
                                    [],
                                )
                                or []
                            )

                            action_texts = []

                            for action in recommended_actions:

                                if isinstance(
                                    action,
                                    dict,
                                ):
                                    action_text = str(
                                        action.get(
                                            "action",
                                            "",
                                        )
                                        or ""
                                    ).strip()

                                else:
                                    action_text = str(action).strip()

                                if action_text:
                                    action_texts.append(action_text)

                            decision_parts = []

                            if severity:
                                decision_parts.append(f"Scenario severity: {severity}.")

                            if decision_signal:
                                decision_parts.append(
                                    f"Decision signal: " f"{decision_signal}."
                                )

                            if management_attention:
                                decision_parts.append(
                                    f"Management attention: " f"{management_attention}."
                                )

                            if factor_texts:
                                decision_parts.append(
                                    "Decision factors: " + " ".join(factor_texts)
                                )

                            if action_texts:
                                decision_parts.append(
                                    "Recommended actions: " + " ".join(action_texts)
                                )

                            if decision_parts:
                                answer += " " + " ".join(decision_parts)

        # ==================================================
        # FUNDING SCENARIO INTELLIGENCE
        # ==================================================

        elif intent in self.FUNDING_SCENARIO_INTENTS:

            cleaned_funding_scenario_question = question.lower().strip()

            scenario_name = "Expected Funding Scenario"
            expected_funding_change_percentage = 0.0
            failed_expected_funding_codes: list[str] = []
            scenario_basis = "most_likely"
            scenario_ready = True

            answer = ""

            if intent == "expected_funding_change_scenario":

                percentage_match = re.search(
                    r"(-?\d+(?:\.\d+)?)\s*%",
                    cleaned_funding_scenario_question,
                )

                if percentage_match is None:

                    scenario_ready = False

                    answer = (
                        "AI-FOS can run this Expected Funding "
                        "scenario, but the assumption must be "
                        "explicit. Please include a percentage, "
                        "for example: 'What if expected funding "
                        "decreases by 20%?'"
                    )

                else:

                    explicit_percentage = self._to_float(percentage_match.group(1))

                    decrease_words = (
                        "decrease",
                        "decreases",
                        "decreased",
                        "drop",
                        "drops",
                        "dropped",
                        "fall",
                        "falls",
                        "decline",
                        "declines",
                        "reduce",
                        "reduces",
                        "reduced",
                        "reduction",
                        "lower",
                        "lowered",
                    )

                    increase_words = (
                        "increase",
                        "increases",
                        "increased",
                        "rise",
                        "rises",
                        "grow",
                        "grows",
                        "growth",
                        "higher",
                    )

                    has_decrease_direction = any(
                        word in cleaned_funding_scenario_question
                        for word in decrease_words
                    )

                    has_increase_direction = any(
                        word in cleaned_funding_scenario_question
                        for word in increase_words
                    )

                    if has_decrease_direction and not has_increase_direction:
                        expected_funding_change_percentage = -abs(explicit_percentage)

                    elif has_increase_direction and not has_decrease_direction:
                        expected_funding_change_percentage = abs(explicit_percentage)

                    elif explicit_percentage < 0:
                        expected_funding_change_percentage = explicit_percentage

                    else:

                        scenario_ready = False

                        answer = (
                            "AI-FOS found the Expected Funding "
                            "percentage assumption, but the "
                            "direction is unclear. Please specify "
                            "whether expected funding increases "
                            "or decreases."
                        )

                    if scenario_ready:

                        scenario_name = (
                            f"Expected Funding "
                            f"{'Increase' if expected_funding_change_percentage > 0 else 'Decrease'} "
                            f"{abs(expected_funding_change_percentage):,.2f}%"
                        )

            elif intent == "expected_funding_failure_scenario":

                funding_code_match = re.search(
                    r"\b[A-Za-z]+-\d+\b",
                    question,
                )

                if funding_code_match is None:

                    scenario_ready = False

                    answer = (
                        "AI-FOS can run an Expected Funding "
                        "failure scenario, but the Expected "
                        "Funding code must be explicit, for "
                        "example EF-001."
                    )

                else:

                    funding_code = funding_code_match.group(0).upper()

                    failed_expected_funding_codes = [funding_code]

                    scenario_name = (
                        f"Expected Funding {funding_code} " f"Does Not Materialize"
                    )

            elif intent == "expected_funding_basis_scenario":

                if "maximum" in cleaned_funding_scenario_question:
                    scenario_basis = "maximum"

                elif "minimum" in cleaned_funding_scenario_question:
                    scenario_basis = "minimum"

                elif (
                    "probability weighted" in cleaned_funding_scenario_question
                    or "probability-weighted" in cleaned_funding_scenario_question
                ):
                    scenario_basis = "probability_weighted"

                elif "most likely" in cleaned_funding_scenario_question:
                    scenario_basis = "most_likely"

                else:

                    scenario_ready = False

                    answer = (
                        "Please specify the Expected Funding "
                        "scenario basis: minimum, most likely, "
                        "maximum, or probability weighted."
                    )

                if scenario_ready:
                    scenario_name = (
                        f"{scenario_basis.replace('_', ' ').title()} "
                        f"Expected Funding Scenario"
                    )

            if scenario_ready:

                funding_scenario_result = generate_funding_scenario(
                    expected_funding_intelligence=(expected_funding_intelligence),
                    scenario_name=scenario_name,
                    expected_funding_change_percentage=(
                        expected_funding_change_percentage
                    ),
                    failed_expected_funding_codes=(failed_expected_funding_codes),
                    scenario_basis=scenario_basis,
                )

                if funding_scenario_result.get("status") != "available":

                    answer = (
                        "AI-FOS cannot run this Expected "
                        "Funding scenario because validated "
                        "Expected Funding Intelligence is not "
                        "available."
                    )

                else:

                    baseline = (
                        funding_scenario_result.get(
                            "baseline",
                            {},
                        )
                        or {}
                    )

                    scenario_values = (
                        funding_scenario_result.get(
                            "scenario",
                            {},
                        )
                        or {}
                    )

                    impact = (
                        funding_scenario_result.get(
                            "impact",
                            {},
                        )
                        or {}
                    )

                    baseline_most_likely = self._to_float(
                        baseline.get("most_likely_pipeline_value")
                    )

                    scenario_most_likely = self._to_float(
                        scenario_values.get("most_likely_pipeline_value")
                    )

                    most_likely_variance = self._to_float(
                        impact.get("most_likely_pipeline_variance")
                    )

                    selected_pipeline_value = self._to_float(
                        scenario_values.get("selected_pipeline_value")
                    )

                    if intent == "expected_funding_basis_scenario":

                        answer = (
                            f"{scenario_name}: the "
                            f"{scenario_basis.replace('_', ' ')} "
                            f"Expected Funding pipeline value is "
                            f"{selected_pipeline_value:,.2f} "
                            f"{currency}. "
                            f"This amount remains prospective "
                            f"Expected Funding only. It is not "
                            f"treated as secured funding, "
                            f"revenue, available budget, or cash."
                        )

                    else:

                        failed_code_text = ""

                        if failed_expected_funding_codes:
                            failed_code_text = (
                                f" The scenario assumes "
                                f"{', '.join(failed_expected_funding_codes)} "
                                f"does not materialize."
                            )

                        answer = (
                            f"{scenario_name}: the validated "
                            f"baseline most-likely Expected "
                            f"Funding pipeline is "
                            f"{baseline_most_likely:,.2f} "
                            f"{currency}. Under this scenario, "
                            f"the most-likely pipeline becomes "
                            f"{scenario_most_likely:,.2f} "
                            f"{currency}, a variance of "
                            f"{most_likely_variance:,.2f} "
                            f"{currency}."
                            f"{failed_code_text} "
                            f"This is a hypothetical prospective "
                            f"funding scenario. Expected Funding "
                            f"is not treated as secured funding, "
                            f"revenue, available budget, or cash, "
                            f"and the validated baseline remains "
                            f"unchanged."
                        )

        # ==================================================
        # CASH POSITION
        # ==================================================

        elif intent in self.CASH_INTENTS:

            available_cash = self._to_float(liquidity.get("available_cash"))

            total_cash = self._to_float(liquidity.get("total_cash"))

            blocked_cash = self._to_float(liquidity.get("blocked_cash"))

            # ------------------------------------------
            # Available cash position
            # ------------------------------------------

            if intent == "cash_position":

                answer = (
                    f"{organisation_name} currently has "
                    f"{available_cash:,.2f} {currency} of "
                    f"available cash. "
                    f"Total cash is "
                    f"{total_cash:,.2f} {currency}, of which "
                    f"{blocked_cash:,.2f} {currency} is blocked "
                    f"or restricted. "
                    f"AI-FOS therefore distinguishes available "
                    f"liquidity from total recorded cash rather "
                    f"than treating all cash as immediately usable."
                )

            # ------------------------------------------
            # Blocked cash
            # ------------------------------------------

            else:

                answer = (
                    f"{organisation_name} currently has "
                    f"{blocked_cash:,.2f} {currency} of blocked "
                    f"or restricted cash. "
                    f"Total recorded cash is "
                    f"{total_cash:,.2f} {currency}, while "
                    f"{available_cash:,.2f} {currency} is "
                    f"currently classified as available cash. "
                    f"Blocked cash is not treated as immediately "
                    f"available liquidity by AI-FOS."
                )

        # ==================================================
        # LIQUIDITY
        # ==================================================

        elif intent in self.LIQUIDITY_INTENTS:

            cash_runway_months = liquidity.get("cash_runway_months")

            runway_basis = liquidity.get(
                "runway_basis",
                ("Available cash divided by average " "monthly operating expenses."),
            )

            available_cash = self._to_float(liquidity.get("available_cash"))

            if cash_runway_months is None:

                answer = (
                    f"{organisation_name}'s cash runway is "
                    f"not currently available because AI-FOS "
                    f"does not have sufficient validated "
                    f"financial data to calculate it reliably."
                )

            else:

                runway_months = self._to_float(cash_runway_months)

                answer = (
                    f"{organisation_name}'s validated cash runway "
                    f"is {runway_months:,.2f} months. "
                    f"Available cash used in the liquidity "
                    f"assessment is "
                    f"{available_cash:,.2f} {currency}. "
                    f"Runway basis: {runway_basis} "
                    f"AI-FOS reports the validated liquidity "
                    f"result and does not treat blocked or "
                    f"restricted cash as automatically available "
                    f"for operating runway."
                )

        # ==================================================
        # CASH FLOW
        # ==================================================

        elif intent in self.CASH_FLOW_INTENTS:

            value = self.financial_intelligence_service.get_cash_flow_value(
                intent=intent,
                cash_flow=cash_flow,
            )

            amount = self._to_float(value)

            # ------------------------------------------
            # Operating cash flow
            # ------------------------------------------

            if intent == "operating_cash_flow":

                if amount > 0:
                    movement_text = (
                        f"positive operating cash flow of " f"{amount:,.2f} {currency}"
                    )

                elif amount < 0:
                    movement_text = (
                        f"negative operating cash flow of "
                        f"{abs(amount):,.2f} {currency}"
                    )

                else:
                    movement_text = f"operating cash flow of " f"0.00 {currency}"

                answer = (
                    f"{organisation_name} currently reports "
                    f"{movement_text}. "
                    f"The validated operating cash-flow value is "
                    f"{amount:,.2f} {currency}."
                )

            # ------------------------------------------
            # Investing cash flow
            # ------------------------------------------

            elif intent == "investing_cash_flow":

                answer = (
                    f"{organisation_name}'s investing cash flow is "
                    f"{amount:,.2f} {currency}. "
                    f"This amount comes from the validated "
                    f"Cash Flow analysis."
                )

            # ------------------------------------------
            # Financing cash flow
            # ------------------------------------------

            elif intent == "financing_cash_flow":

                answer = (
                    f"{organisation_name}'s financing cash flow is "
                    f"{amount:,.2f} {currency}. "
                    f"This amount comes from the validated "
                    f"Cash Flow analysis."
                )

            # ------------------------------------------
            # Net change in cash
            # ------------------------------------------

            else:

                if amount > 0:
                    movement_text = (
                        f"an increase in cash of " f"{amount:,.2f} {currency}"
                    )

                elif amount < 0:
                    movement_text = (
                        f"a decrease in cash of " f"{abs(amount):,.2f} {currency}"
                    )

                else:
                    movement_text = f"no net change in cash"

                answer = (
                    f"{organisation_name} currently reports "
                    f"{movement_text}. "
                    f"The validated net change in cash is "
                    f"{amount:,.2f} {currency}."
                )

        # ==================================================
        # PERIOD / DATA QUALITY INTELLIGENCE
        # ==================================================

        elif intent in self.PERIOD_INTENTS:

            date_summary = (
                gl_date_quality.get(
                    "summary",
                    {},
                )
                or {}
            )

            date_status = gl_date_quality.get("status") or "unknown"

            reporting_date = gl_date_quality.get("reporting_date")

            transaction_count = int(
                date_summary.get(
                    "transaction_count",
                    0,
                )
                or 0
            )

            valid_date_count = int(
                date_summary.get(
                    "valid_date_count",
                    0,
                )
                or 0
            )

            missing_date_count = int(
                date_summary.get(
                    "missing_date_count",
                    0,
                )
                or 0
            )

            invalid_date_count = int(
                date_summary.get(
                    "invalid_date_count",
                    0,
                )
                or 0
            )

            current_or_historical_count = int(
                date_summary.get(
                    "current_or_historical_count",
                    0,
                )
                or 0
            )

            future_transaction_count = int(
                date_summary.get(
                    "future_transaction_count",
                    0,
                )
                or 0
            )

            earliest_posting_date = date_summary.get("earliest_posting_date")

            latest_posting_date = date_summary.get("latest_posting_date")

            if intent == "data_period":

                if earliest_posting_date and latest_posting_date:
                    answer = (
                        f"{organisation_name}'s validated "
                        f"General Ledger data covers posting dates "
                        f"from {earliest_posting_date} through "
                        f"{latest_posting_date}. "
                        f"The date-quality assessment is based on "
                        f"{transaction_count:,} transaction(s)."
                    )
                else:
                    answer = (
                        f"AI-FOS cannot currently determine a "
                        f"reliable General Ledger data period for "
                        f"{organisation_name} because validated "
                        f"posting-date coverage is not available."
                    )

            elif intent == "latest_transaction_date":

                if latest_posting_date:
                    answer = (
                        f"The latest validated posting date in "
                        f"{organisation_name}'s General Ledger is "
                        f"{latest_posting_date}. "
                        f"This is the latest date present in the "
                        f"source data and does not by itself mean "
                        f"the transaction belongs to the current "
                        f"reporting period."
                    )
                else:
                    answer = (
                        f"AI-FOS does not currently have a "
                        f"validated latest posting date for "
                        f"{organisation_name}."
                    )

            elif intent == "earliest_transaction_date":

                if earliest_posting_date:
                    answer = (
                        f"The earliest validated posting date in "
                        f"{organisation_name}'s General Ledger is "
                        f"{earliest_posting_date}."
                    )
                else:
                    answer = (
                        f"AI-FOS does not currently have a "
                        f"validated earliest posting date for "
                        f"{organisation_name}."
                    )

            elif intent == "reporting_date":

                if reporting_date:
                    answer = (
                        f"The reporting date used by AI-FOS for "
                        f"the current General Ledger date-quality "
                        f"assessment is {reporting_date}. "
                        f"Transactions after this date are "
                        f"identified as future-dated source "
                        f"transactions."
                    )
                else:
                    answer = (
                        f"The reporting date for the current "
                        f"General Ledger date-quality assessment "
                        f"is not available."
                    )

            elif intent == "date_quality":

                answer = (
                    f"{organisation_name}'s General Ledger "
                    f"date-quality status is {date_status}. "
                    f"Of {transaction_count:,} transaction(s), "
                    f"{valid_date_count:,} have valid posting "
                    f"dates, {missing_date_count:,} have missing "
                    f"posting dates, and {invalid_date_count:,} "
                    f"have invalid posting dates. "
                    f"{current_or_historical_count:,} valid "
                    f"transaction(s) are dated on or before the "
                    f"reporting date, while "
                    f"{future_transaction_count:,} are "
                    f"future-dated."
                )

            else:

                if future_transaction_count > 0:
                    answer = (
                        f"AI-FOS identified "
                        f"{future_transaction_count:,} "
                        f"future-dated transaction(s) in "
                        f"{organisation_name}'s General Ledger "
                        f"relative to the reporting date "
                        f"{reporting_date or 'not available'}. "
                        f"These transactions remain preserved in "
                        f"the source financial model but are "
                        f"identified separately for current-period "
                        f"financial analysis."
                    )
                else:
                    answer = (
                        f"AI-FOS identified no future-dated "
                        f"General Ledger transactions for "
                        f"{organisation_name} relative to the "
                        f"current reporting date."
                    )

        # ==================================================
        # ORGANIZATION KNOWLEDGE
        # ==================================================

        elif intent in self.ORGANIZATION_INTENTS:

            donor_count = int(knowledge.get("donors", 0) or 0)

            organization_transaction_count = int(knowledge.get("transactions", 0) or 0)

            account_count = int(knowledge.get("accounts", 0) or 0)

            program_count = int(knowledge.get("programs", 0) or 0)

            fund_count = int(knowledge.get("funds", 0) or 0)

            source_system = knowledge.get("source_system") or "Unknown source system"

            base_currency = knowledge.get("currency") or currency or "Unknown"

            if intent == "donor_count":

                answer = (
                    f"{organisation_name} currently has "
                    f"{donor_count:,} donor(s) represented in "
                    f"its AI-FOS financial model."
                )

            elif intent == "currency":

                answer = (
                    f"{organisation_name}'s base currency is "
                    f"{base_currency}. "
                    f"This value comes from the validated "
                    f"organization knowledge profile."
                )

            elif intent == "transaction_count":

                answer = (
                    f"AI-FOS currently contains "
                    f"{organization_transaction_count:,} "
                    f"transaction(s) for {organisation_name}. "
                    f"This count comes from the validated "
                    f"organization knowledge profile."
                )

            elif intent == "account_count":

                answer = (
                    f"{organisation_name} currently has "
                    f"{account_count:,} account(s) represented "
                    f"in its AI-FOS financial model."
                )

            elif intent == "program_count":

                answer = (
                    f"{organisation_name} currently has "
                    f"{program_count:,} program(s) represented "
                    f"in its AI-FOS financial model."
                )

            elif intent == "fund_count":

                answer = (
                    f"{organisation_name} currently has "
                    f"{fund_count:,} fund(s) represented "
                    f"in its AI-FOS financial model."
                )

            else:

                answer = (
                    f"{organisation_name} uses "
                    f"{source_system} as its source financial "
                    f"system, with {base_currency} as its base "
                    f"currency. "
                    f"AI-FOS currently knows about "
                    f"{organization_transaction_count:,} "
                    f"transaction(s), "
                    f"{account_count:,} account(s), "
                    f"{fund_count:,} fund(s), "
                    f"{donor_count:,} donor(s), and "
                    f"{program_count:,} program(s). "
                    f"This summary is based on the validated "
                    f"organization knowledge profile."
                )

        # ==================================================
        # FAIL-SAFE
        # ==================================================

        else:

            return {
                "status": "unsupported",
                "question": question,
                "organisation_id": organisation_id,
                "intent": intent,
                "domain": domain,
                "answer": (
                    "AI-FOS recognized the question category, "
                    "but a verified answer handler is not yet "
                    "available for this analysis."
                ),
                "knowledge_used": True,
                "financial_data_used": False,
            }

        # --------------------------------------------------
        # Successful response
        # --------------------------------------------------

        return {
            "status": "success",
            "question": question,
            "organisation_id": organisation_id,
            "intent": intent,
            "domain": domain,
            "answer": answer,
            "knowledge_used": True,
            "financial_data_used": (
                intent in self.FINANCIAL_FACT_INTENTS
                or intent in self.CASH_FLOW_INTENTS
                or intent in self.CASH_INTENTS
                or intent in self.LIQUIDITY_INTENTS
                or intent in self.FINANCIAL_HEALTH_INTENTS
                or intent in self.RISK_INTENTS
                or intent in self.RECOMMENDATION_INTENTS
                or intent in self.FUNDING_INTENTS
                or intent in self.CORE_COST_COVERAGE_INTENTS
                or intent in self.GRANT_INTENTS
                or intent in self.BUDGET_INTENTS
                or intent in self.EXECUTIVE_DECISION_INTENTS
                or intent in self.HISTORICAL_CHANGE_INTENTS
                or intent in self.HISTORICAL_DECISION_INTENTS
            ),
        }

    @staticmethod
    def _not_available(
        question: str,
        organisation_id: str,
        intent: str,
        domain: str,
        answer: str,
    ) -> dict[str, Any]:
        """
        Build a consistent response when a verified
        intelligence source is unavailable.
        """

        return {
            "status": "not_available",
            "question": question,
            "organisation_id": organisation_id,
            "intent": intent,
            "domain": domain,
            "answer": answer,
            "knowledge_used": True,
            "financial_data_used": False,
        }

    @staticmethod
    def _to_float(
        value: Any,
    ) -> float:
        """
        Safely convert a financial value to float.
        """

        if value is None:
            return 0.0

        if isinstance(
            value,
            (int, float),
        ):
            return float(value)

        text = (
            str(value)
            .replace(
                ",",
                "",
            )
            .replace(
                "$",
                "",
            )
            .strip()
        )

        if not text:
            return 0.0

        if text.startswith("(") and text.endswith(")"):
            text = "-" + text[1:-1]

        try:

            return float(text)

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

    @staticmethod
    def _format_name(
        value: str,
    ) -> str:
        """
        Convert an internal snake_case key into a
        management-readable label.
        """

        return (
            str(value)
            .replace(
                "_",
                " ",
            )
            .strip()
            .title()
        )














