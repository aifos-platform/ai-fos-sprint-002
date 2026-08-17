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


class AIQuestionEngine:
    """
    Routes AI-FOS questions to organization knowledge,
    financial intelligence, cash-flow intelligence,
    financial-health intelligence, and risk intelligence.
    """

    FINANCIAL_FACT_INTENTS = {
        "revenue",
        "expenses",
        "net_profit",
        "assets",
        "liabilities",
        "equity",
    }

    CASH_FLOW_INTENTS = {
        "operating_cash_flow",
        "investing_cash_flow",
        "financing_cash_flow",
        "net_change_in_cash",
    }

    RISK_INTENTS = {
        "risk_summary",
        "high_risks",
    }

    BUDGET_INTENTS = {
        "portfolio_total_budget",
        "portfolio_budget_utilization",
        "portfolio_budget_variance",
        "unbudgeted_actual",
        "over_budget_count",
        "portfolio_budget_summary",
        "budget_performance_summary",
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

        classification = self.question_classifier.classify(
            question=question,
        )

        intent = classification["intent"]

        workspace = self.workspace_service.get_workspace_by_organisation(
            organisation_id=organisation_id
        )

        if workspace is None:
            return {
                "status": "not_available",
                "question": question,
                "organisation_id": organisation_id,
                "answer": ("I could not find a workspace " "for this organization."),
                "knowledge_used": False,
            }

        ai_knowledge_folder = Path(workspace["paths"]["ai_knowledge"])

        financial_model_folder = Path(workspace["paths"]["financial_model"])

        knowledge = self.knowledge_reader.get_summary(folder=ai_knowledge_folder)

        if knowledge.get("status") != "available":
            return {
                "status": "not_available",
                "question": question,
                "organisation_id": organisation_id,
                "answer": ("Organization knowledge is " "not available yet."),
                "knowledge_used": False,
            }

        organisation_name = knowledge.get("organisation_name") or organisation_id

        currency = knowledge.get("currency") or ""

        financial_facts = (
            self.financial_model_service.load_json(
                financial_model_folder=financial_model_folder,
                filename="financial_facts.json",
            )
            or {}
        )

        cash_flow = (
            self.financial_model_service.load_json(
                financial_model_folder=financial_model_folder,
                filename="cash_flow.json",
            )
            or {}
        )

        liquidity = (
            self.financial_model_service.load_json(
                financial_model_folder=financial_model_folder,
                filename="liquidity.json",
            )
            or {}
        )

        financial_health = (
            self.financial_model_service.load_json(
                financial_model_folder=financial_model_folder,
                filename="financial_health.json",
            )
            or {}
        )

        risk_assessment = (
            self.financial_model_service.load_json(
                financial_model_folder=financial_model_folder,
                filename="risk_assessment.json",
            )
            or []
        )

        intelligence_hub = (
            self.financial_model_service.load_json(
                financial_model_folder=financial_model_folder,
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

        if intent in self.FINANCIAL_FACT_INTENTS and not financial_facts:
            return {
                "status": "not_available",
                "question": question,
                "organisation_id": organisation_id,
                "intent": intent,
                "answer": (
                    "Financial facts are not available yet. "
                    "Process the General Ledger first."
                ),
                "knowledge_used": True,
                "financial_data_used": False,
            }

        if intent in self.CASH_FLOW_INTENTS and not cash_flow:
            return {
                "status": "not_available",
                "question": question,
                "organisation_id": organisation_id,
                "intent": intent,
                "answer": ("Cash-flow information is not " "available yet."),
                "knowledge_used": True,
                "financial_data_used": False,
            }

        if intent == "financial_health" and not financial_health:
            return {
                "status": "not_available",
                "question": question,
                "organisation_id": organisation_id,
                "intent": intent,
                "answer": ("Financial health information is " "not available yet."),
                "knowledge_used": True,
                "financial_data_used": False,
            }

        if intent in self.RISK_INTENTS and not risk_assessment:
            return {
                "status": "not_available",
                "question": question,
                "organisation_id": organisation_id,
                "intent": intent,
                "answer": ("Risk assessment is not available yet."),
                "knowledge_used": True,
                "financial_data_used": False,
            }

        if intent in self.BUDGET_INTENTS and not budget_dashboard:
            return {
                "status": "not_available",
                "question": question,
                "organisation_id": organisation_id,
                "intent": intent,
                "answer": (
                    "Budget intelligence is not available yet. "
                    "Load the Budget and process the General Ledger first."
                ),
                "knowledge_used": True,
                "financial_data_used": False,
            }

        # ---------------------------------
        # Organization Knowledge
        # ---------------------------------

        if intent == "donor_count":
            answer = (
                f"{organisation_name} currently has "
                f"{knowledge.get('donors', 0)} donors "
                f"in its AI-FOS financial model."
            )

        elif intent == "currency":
            answer = (
                f"{organisation_name}'s base currency "
                f"is {knowledge.get('currency')}."
            )

        elif intent == "transaction_count":
            answer = (
                f"AI-FOS currently contains "
                f"{knowledge.get('transactions', 0)} "
                f"transactions for "
                f"{organisation_name}."
            )

        elif intent == "account_count":
            answer = (
                f"{organisation_name} currently has "
                f"{knowledge.get('accounts', 0)} accounts "
                f"in its financial model."
            )

        elif intent == "program_count":
            answer = (
                f"{organisation_name} currently has "
                f"{knowledge.get('programs', 0)} programs "
                f"in its financial model."
            )

        elif intent == "fund_count":
            answer = (
                f"{organisation_name} currently has "
                f"{knowledge.get('funds', 0)} funds "
                f"in its financial model."
            )

        # ---------------------------------
        # Budget Intelligence
        # ---------------------------------

        elif intent in self.BUDGET_INTENTS:

            portfolio_control = (
                budget_dashboard.get(
                    "portfolio_control",
                    {},
                )
                or {}
            )

            total_budget = float(
                portfolio_control.get(
                    "total_budget",
                    0,
                )
                or 0
            )

            utilization = float(
                portfolio_control.get(
                    "utilization_percentage",
                    0,
                )
                or 0
            )

            total_variance = float(
                portfolio_control.get(
                    "total_variance",
                    0,
                )
                or 0
            )

            unbudgeted_actual = float(
                portfolio_control.get(
                    "unbudgeted_actual",
                    0,
                )
                or 0
            )

            over_budget_count = int(
                portfolio_control.get(
                    "over_budget_count",
                    0,
                )
                or 0
            )

            total_actual = float(
                portfolio_control.get(
                    "total_actual",
                    0,
                )
                or 0
            )

            if intent == "portfolio_total_budget":

                answer = (
                    f"{organisation_name}'s total approved "
                    f"portfolio budget is "
                    f"{total_budget:,.2f} {currency}."
                )

            elif intent == "portfolio_budget_utilization":

                answer = (
                    f"{organisation_name}'s portfolio budget "
                    f"utilization is {utilization:.2f}%."
                )

            elif intent == "portfolio_budget_variance":

                answer = (
                    f"{organisation_name}'s portfolio budget "
                    f"variance is {total_variance:,.2f} "
                    f"{currency}."
                )

            elif intent == "unbudgeted_actual":

                answer = (
                    f"{organisation_name} has "
                    f"{unbudgeted_actual:,.2f} {currency} "
                    f"of portfolio actual spending without "
                    f"a matching approved budget."
                )

            elif intent == "over_budget_count":

                answer = (
                    f"{organisation_name} currently has "
                    f"{over_budget_count} portfolio budget "
                    f"line(s) above their approved limits."
                )

            else:

                answer = (
                    f"{organisation_name}'s portfolio budget is "
                    f"{total_budget:,.2f} {currency}, with "
                    f"cumulative actual spending of "
                    f"{total_actual:,.2f} {currency}. "
                    f"Portfolio budget utilization is "
                    f"{utilization:.2f}%, and the portfolio "
                    f"budget variance is "
                    f"{total_variance:,.2f} {currency}. "
                    f"Unbudgeted portfolio actual spending is "
                    f"{unbudgeted_actual:,.2f} {currency}, and "
                    f"{over_budget_count} portfolio budget line(s) "
                    f"are above their approved limits."
                )

        # ---------------------------------
        # Financial Facts
        # ---------------------------------

        elif intent in self.FINANCIAL_FACT_INTENTS:

            value = self.financial_intelligence_service.get_value(
                intent=intent,
                financial_facts=financial_facts,
            )

            labels = {
                "revenue": "total revenue",
                "expenses": "total expenses",
                "net_profit": "net result",
                "assets": "total assets",
                "liabilities": "total liabilities",
                "equity": "total equity",
            }

            answer = (
                f"{organisation_name}'s "
                f"{labels[intent]} is "
                f"{float(value or 0):,.2f} "
                f"{currency}."
            )

        # ---------------------------------
        # Cash Position Intelligence
        # ---------------------------------

        elif intent == "cash_position":

            available_cash = float(
                liquidity.get(
                    "available_cash",
                    0,
                )
                or 0
            )

            total_cash = float(
                liquidity.get(
                    "total_cash",
                    0,
                )
                or 0
            )

            blocked_cash = float(
                liquidity.get(
                    "blocked_cash",
                    0,
                )
                or 0
            )

            answer = (
                f"{organisation_name}'s available cash is "
                f"{available_cash:,.2f} {currency}. "
                f"Total cash is {total_cash:,.2f} {currency}, "
                f"of which {blocked_cash:,.2f} {currency} "
                f"is blocked."
            )            

        # ---------------------------------
        # Cash Flow Intelligence
        # ---------------------------------

        elif intent in self.CASH_FLOW_INTENTS:

            value = self.financial_intelligence_service.get_cash_flow_value(
                intent=intent,
                cash_flow=cash_flow,
            )

            labels = {
                "operating_cash_flow": ("operating cash flow"),
                "investing_cash_flow": ("investing cash flow"),
                "financing_cash_flow": ("financing cash flow"),
                "net_change_in_cash": ("net change in cash"),
            }

            answer = (
                f"{organisation_name}'s "
                f"{labels[intent]} is "
                f"{float(value or 0):,.2f} "
                f"{currency}."
            )

        # ---------------------------------
        # Financial Health
        # ---------------------------------

        elif intent == "financial_health":

            health = self.financial_intelligence_service.get_health_summary(
                financial_health=financial_health
            )

            answer = (
                f"{organisation_name}'s Financial "
                f"Health Score is "
                f"{health.get('score', 0)} out of "
                f"{health.get('maximum', 100)}, "
                f"with a rating of "
                f"{health.get('rating', 'Unknown')}."
            )

        # ---------------------------------
        # Risk Intelligence
        # ---------------------------------

        elif intent == "risk_summary":

            severity_order = {
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

            top_risks = ordered_risks[:3]

            risk_text = " ".join(
                (
                    f"{index + 1}. "
                    f"{risk.get('severity', 'Unknown')} risk: "
                    f"{risk.get('title', 'Unnamed risk')}. "
                    f"Evidence: "
                    f"{risk.get('evidence', '')} "
                    f"Recommendation: "
                    f"{risk.get('recommendation', '')}"
                )
                for index, risk in enumerate(top_risks)
            )

            answer = (
                f"The most important financial risks for "
                f"{organisation_name} are: "
                f"{risk_text}"
            )

        elif intent == "high_risks":

            high_risks = [
                risk for risk in risk_assessment if risk.get("severity") == "High"
            ]

            if not high_risks:

                answer = (
                    f"AI-FOS currently detects no "
                    f"High-severity financial risks "
                    f"for {organisation_name}."
                )

            else:

                risk_text = " ".join(
                    (
                        f"{index + 1}. "
                        f"{risk.get('title', 'Unnamed risk')}. "
                        f"Evidence: "
                        f"{risk.get('evidence', '')} "
                        f"Recommendation: "
                        f"{risk.get('recommendation', '')}"
                    )
                    for index, risk in enumerate(high_risks)
                )

                answer = (
                    f"{organisation_name} currently has "
                    f"{len(high_risks)} High-severity "
                    f"financial risk(s). "
                    f"{risk_text}"
                )

        # ---------------------------------
        # Default Summary
        # ---------------------------------

        else:
            answer = (
                f"{organisation_name} uses "
                f"{knowledge.get('source_system')} "
                f"with {knowledge.get('currency')} "
                f"as its base currency. "
                f"AI-FOS currently knows about "
                f"{knowledge.get('transactions', 0)} "
                f"transactions, "
                f"{knowledge.get('accounts', 0)} accounts, "
                f"{knowledge.get('funds', 0)} funds, "
                f"{knowledge.get('donors', 0)} donors, and "
                f"{knowledge.get('programs', 0)} programs."
            )

        return {
            "status": "success",
            "question": question,
            "organisation_id": organisation_id,
            "intent": intent,
            "domain": classification["domain"],
            "answer": answer,
            "knowledge_used": True,
            "financial_data_used": (
                intent in self.FINANCIAL_FACT_INTENTS
                or intent in self.CASH_FLOW_INTENTS
                or intent == "cash_position"
                or intent == "financial_health"
                or intent in self.RISK_INTENTS
                or intent in self.BUDGET_INTENTS
            ),
        }
