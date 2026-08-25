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

    RECOMMENDATION_INTENTS = {
        "recommendation_summary",
        "priority_actions",
        "funding_gap_actions",
        "finance_meeting_agenda",
    }

    FUNDING_INTENTS = {
        "funding_gap",
        "funding_coverage",
        "unfunded_requirements",
        "secured_funding_total",
        "eligible_secured_funding",
        "funding_evidence",
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
        # Verified financial-model artifacts
        # --------------------------------------------------

        financial_facts = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="financial_facts.json",
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

        cfo_recommendations = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="cfo_recommendations.json",
            )
            or []
        )

        funding_gap = (
            self.financial_model_service.load_json(
                financial_model_folder=(financial_model_folder),
                filename="funding_gap.json",
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
        # ORGANIZATION KNOWLEDGE
        # ==================================================

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

            if intent == "funding_gap":

                answer = (
                    f"{organisation_name}'s current Funding Gap "
                    f"is {funding_gap_amount:,.2f} {currency}. "
                    f"Remaining identified requirements are "
                    f"{remaining_requirement:,.2f} {currency}, "
                    f"of which validated secured funding currently "
                    f"covers {coverage_percentage:.2f}%."
                )

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
                    f"{funding_gap_amount:,.2f} {currency}."
                )

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
                    f"requirements."
                )

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
                    f"available when its eligibility or allocation "
                    f"cannot be validated."
                )

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
                    f"This funding should not be treated as "
                    f"automatically available until sufficient "
                    f"eligibility and allocation evidence exists."
                )

            else:

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
                        f"{unfunded_requirement_count} requirement(s) "
                        f"classified as unfunded and "
                        f"{unmatched_requirement_count} requirement(s) "
                        f"without validated matched secured funding. "
                        f"The total Funding Gap is "
                        f"{funding_gap_amount:,.2f} {currency}. "
                        f"The largest uncovered requirements "
                        f"currently visible are: "
                        f"{detail_text}"
                    )

                else:

                    answer = (
                        f"AI-FOS identifies a total Funding Gap of "
                        f"{funding_gap_amount:,.2f} {currency}, "
                        f"but no detailed uncovered requirement "
                        f"records are currently available."
                    )

        # ==================================================
        # GRANT INTELLIGENCE
        # ==================================================

        elif intent in self.GRANT_INTENTS:

            grants = (
                self.financial_model_service.load_json(
                    financial_model_folder=(
                        financial_model_folder
                    ),
                    filename="grants.json",
                )
                or {}
            )

            grant_diagnostics = (
                self.financial_model_service.load_json(
                    financial_model_folder=(
                        financial_model_folder
                    ),
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

                grant_record = dict(
                    grant_data
                )

                grant_record["code"] = (
                    grant_record.get("code")
                    or grant_code
                )

                grant_record[
                    "is_actual_only"
                ] = (
                    grant_record["code"]
                    in actual_only_codes
                )

                grant_records.append(
                    grant_record
                )

            if intent == "grant_attention":

                attention_grants = [
                    grant
                    for grant in grant_records
                    if (
                        self._to_float(
                            grant.get(
                                "utilization"
                            )
                        )
                        >= 90
                        or self._to_float(
                            grant.get(
                                "remaining_budget"
                            )
                        )
                        < 0
                        or grant.get(
                            "is_actual_only"
                        )
                        is True
                    )
                ]

                attention_grants.sort(
                    key=lambda grant: (
                        grant.get("is_actual_only") is False,
                        self._to_float(
                            grant.get(
                                "utilization"
                            )
                        ),
                        -self._to_float(
                            grant.get(
                                "remaining_budget"
                            )
                        ),
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
                        for index, grant
                        in enumerate(
                            attention_grants[:10]
                        )
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
                        self._to_float(
                            grant.get(
                                "revised_budget"
                            )
                        )
                        > 0
                        and self._to_float(
                            grant.get(
                                "remaining_budget"
                            )
                        )
                        > 0
                    )
                ]

                grants_with_remaining_budget.sort(
                    key=lambda grant: self._to_float(
                        grant.get(
                            "remaining_budget"
                        )
                    ),
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
                        for index, grant
                        in enumerate(
                            grants_with_remaining_budget[
                                :10
                            ]
                        )
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
                        self._to_float(
                            grant.get(
                                "revised_budget"
                            )
                        )
                        > 0
                        and self._to_float(
                            grant.get(
                                "utilization"
                            )
                        )
                        >= 90
                    )
                ]

                high_utilization_grants.sort(
                    key=lambda grant: self._to_float(
                        grant.get(
                            "utilization"
                        )
                    ),
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
                        for index, grant
                        in enumerate(
                            high_utilization_grants[
                                :10
                            ]
                        )
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
                        self._to_float(
                            grant.get(
                                "actual"
                            )
                        )
                        > 0
                        and self._to_float(
                            grant.get(
                                "revised_budget"
                            )
                        )
                        <= 0
                    )
                ]

                spending_without_budget.sort(
                    key=lambda grant: self._to_float(
                        grant.get(
                            "actual"
                        )
                    ),
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
                        for index, grant
                        in enumerate(
                            spending_without_budget[
                                :10
                            ]
                        )
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
                        self._to_float(
                            grant.get(
                                "revised_budget"
                            )
                        )
                        > 0
                        and abs(
                            self._to_float(
                                grant.get(
                                    "actual"
                                )
                            )
                        )
                        < 0.01
                    )
                ]

                budget_without_spending.sort(
                    key=lambda grant: self._to_float(
                        grant.get(
                            "revised_budget"
                        )
                    ),
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
                        for index, grant
                        in enumerate(
                            budget_without_spending[
                                :10
                            ]
                        )
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

                    revised_budget = self._to_float(
                        grant.get(
                            "revised_budget"
                        )
                    )

                    actual = self._to_float(
                        grant.get(
                            "actual"
                        )
                    )

                    remaining_budget = self._to_float(
                        grant.get(
                            "remaining_budget"
                        )
                    )

                    utilization = self._to_float(
                        grant.get(
                            "utilization"
                        )
                    )

                    issues = []

                    if (
                        actual > 0
                        and revised_budget <= 0
                    ):
                        issues.append(
                            "spending without an identified budget"
                        )

                    if (
                        revised_budget > 0
                        and remaining_budget < 0
                    ):
                        issues.append(
                            "spending exceeds the identified budget"
                        )

                    elif (
                        revised_budget > 0
                        and utilization >= 90
                    ):
                        issues.append(
                            "high budget utilization"
                        )

                    if not issues:
                        continue

                    issue_grant = dict(
                        grant
                    )

                    issue_grant["issues"] = (
                        issues
                    )

                    issue_grants.append(
                        issue_grant
                    )

                issue_grants.sort(
                    key=lambda grant: (
                        self._to_float(
                            grant.get(
                                "remaining_budget"
                            )
                        )
                        < 0,
                        self._to_float(
                            grant.get(
                                "utilization"
                            )
                        ),
                        self._to_float(
                            grant.get(
                                "actual"
                            )
                        ),
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
                        for index, grant
                        in enumerate(
                            issue_grants[:10]
                        )
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
                    if self._to_float(
                        grant.get(
                            "revised_budget"
                        )
                    )
                    > 0
                ]

                total_budget = sum(
                    self._to_float(
                        grant.get(
                            "revised_budget"
                        )
                    )
                    for grant in budgeted_grants
                )

                total_actual = sum(
                    self._to_float(
                        grant.get(
                            "actual"
                        )
                    )
                    for grant in budgeted_grants
                )

                total_remaining = sum(
                    self._to_float(
                        grant.get(
                            "remaining_budget"
                        )
                    )
                    for grant in budgeted_grants
                )

                portfolio_utilization = (
                    (
                        total_actual
                        / total_budget
                    )
                    * 100
                    if total_budget > 0
                    else 0.0
                )

                over_budget_grants = [
                    grant
                    for grant in budgeted_grants
                    if self._to_float(
                        grant.get(
                            "remaining_budget"
                        )
                    )
                    < 0
                ]

                high_utilization_grants = [
                    grant
                    for grant in budgeted_grants
                    if self._to_float(
                        grant.get(
                            "utilization"
                        )
                    )
                    >= 90
                ]

                actual_only_grants = [
                    grant
                    for grant in grant_records
                    if (
                        self._to_float(
                            grant.get(
                                "actual"
                            )
                        )
                        > 0
                        and self._to_float(
                            grant.get(
                                "revised_budget"
                            )
                        )
                        <= 0
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

                    coverage_percentage = self._to_float(
                        funding_summary.get("applied_coverage_percentage")
                    )

                    answer = (
                        f"{organisation_name} currently has a "
                        f"Funding Gap of "
                        f"{funding_gap_amount:,.2f} {currency} "
                        f"against remaining requirements of "
                        f"{remaining_requirement:,.2f} {currency}. "
                        f"Validated secured funding currently "
                        f"covers {coverage_percentage:.2f}% of "
                        f"remaining requirements. "
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

        elif intent == "risk_summary":

            severity_order = {
                "Critical": 4,
                "High": 3,
                "Medium": 2,
                "Low": 1,
            }

            ordered_risks = sorted(
                risk_assessment,
                key=lambda item: (
                    severity_order.get(
                        item.get("severity"),
                        0,
                    )
                ),
                reverse=True,
            )

            top_risks = ordered_risks[:5]

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
                risk
                for risk in risk_assessment
                if risk.get("severity")
                in {
                    "Critical",
                    "High",
                }
            ]

            if not high_risks:

                answer = (
                    f"AI-FOS currently detects no "
                    f"Critical or High-severity financial "
                    f"risks for {organisation_name}."
                )

            else:

                risk_text = " ".join(
                    (
                        f"{index + 1}. "
                        f"{risk.get('severity', 'Unknown')} — "
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
                    f"{len(high_risks)} Critical or "
                    f"High-severity financial risk(s). "
                    f"{risk_text}"
                )

        elif intent == "immediate_risk":

            severity_order = {
                "Critical": 4,
                "High": 3,
                "Medium": 2,
                "Low": 1,
            }

            ordered_risks = sorted(
                risk_assessment,
                key=lambda item: (
                    severity_order.get(
                        item.get("severity"),
                        0,
                    )
                ),
                reverse=True,
            )

            if not ordered_risks:

                answer = (
                    f"AI-FOS currently detects no financial "
                    f"risks requiring immediate attention for "
                    f"{organisation_name}."
                )

            else:

                risk = ordered_risks[0]

                answer = (
                    f"The financial risk requiring the most "
                    f"immediate attention for "
                    f"{organisation_name} is the "
                    f"{risk.get('severity', 'Unknown')}-severity "
                    f"risk: "
                    f"{risk.get('title', 'Unnamed risk')}. "
                    f"Evidence: "
                    f"{risk.get('evidence', '')} "
                    f"Recommendation: "
                    f"{risk.get('recommendation', '')}"
                )

        elif intent in {
            "liquidity_risks",
            "budget_risks",
            "funding_risks",
        }:

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

            keywords = category_keywords[intent]

            filtered_risks = [
                risk
                for risk in risk_assessment
                if any(
                    keyword
                    in (
                        " ".join(
                            [
                                str(risk.get("title", "")),
                                str(risk.get("category", "")),
                                str(risk.get("evidence", "")),
                                str(risk.get("recommendation", "")),
                            ]
                        ).lower()
                    )
                    for keyword in keywords
                )
            ]

            severity_order = {
                "Critical": 4,
                "High": 3,
                "Medium": 2,
                "Low": 1,
            }

            filtered_risks = sorted(
                filtered_risks,
                key=lambda item: (
                    severity_order.get(
                        item.get("severity"),
                        0,
                    )
                ),
                reverse=True,
            )

            labels = {
                "liquidity_risks": "liquidity",
                "budget_risks": "budget",
                "funding_risks": "funding",
            }

            risk_label = labels[intent]

            if not filtered_risks:

                answer = (
                    f"AI-FOS currently detects no specific "
                    f"{risk_label} risks for "
                    f"{organisation_name} in the verified "
                    f"risk assessment."
                )

            else:

                risk_text = " ".join(
                    (
                        f"{index + 1}. "
                        f"{risk.get('severity', 'Unknown')} — "
                        f"{risk.get('title', 'Unnamed risk')}. "
                        f"Evidence: "
                        f"{risk.get('evidence', '')} "
                        f"Recommendation: "
                        f"{risk.get('recommendation', '')}"
                    )
                    for index, risk in enumerate(filtered_risks[:5])
                )

                answer = (
                    f"The main {risk_label} risks for "
                    f"{organisation_name} are: "
                    f"{risk_text}"
                )

        # ==================================================
        # FINANCIAL HEALTH
        # ==================================================

        elif intent == "financial_health":

            health = self.financial_intelligence_service.get_health_summary(
                financial_health=(financial_health)
            )

            answer = (
                f"{organisation_name}'s Financial "
                f"Health Score is "
                f"{health.get('score', 0)} out of "
                f"{health.get('maximum', 100)}, "
                f"with a rating of "
                f"{health.get('rating', 'Unknown')}."
            )

        elif intent == "financial_health_explanation":

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

            rating = financial_health.get(
                "rating",
                "Unknown",
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

                category_rows.append(
                    (
                        category_name,
                        category_score,
                        category_maximum,
                        percentage,
                        str(
                            category.get(
                                "reason",
                                "",
                            )
                            or ""
                        ),
                    )
                )

            category_rows.sort(key=lambda row: row[3])

            weakest_categories = category_rows[:3]

            if weakest_categories:

                explanation = " ".join(
                    (
                        f"{index + 1}. "
                        f"{self._format_name(row[0])}: "
                        f"{row[1]:,.0f}/{row[2]:,.0f}. "
                        f"{row[4]}"
                    )
                    for index, row in enumerate(weakest_categories)
                )

                answer = (
                    f"{organisation_name}'s Financial "
                    f"Health Score is {score}/{maximum}, "
                    f"rated {rating}. "
                    f"The main factors reducing the score "
                    f"are: {explanation}"
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

            total_budget = self._to_float(
                portfolio_control.get(
                    "total_budget"
                )
            )

            utilization = self._to_float(
                portfolio_control.get(
                    "utilization_percentage"
                )
            )

            total_variance = self._to_float(
                portfolio_control.get(
                    "total_variance"
                )
            )

            overall_variance = self._to_float(
                portfolio_control.get(
                    "overall_variance_including_unbudgeted"
                )
            )

            unbudgeted_actual = self._to_float(
                portfolio_control.get(
                    "unbudgeted_actual"
                )
            )

            over_budget_count = int(
                portfolio_control.get(
                    "over_budget_count",
                    0,
                )
                or 0
            )

            total_actual = self._to_float(
                portfolio_control.get(
                    "total_actual"
                )
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
                    f"variance against approved budget lines is "
                    f"{total_variance:,.2f} {currency}."
                )

            elif intent == "portfolio_budget_remaining":

                if overall_variance > 0:

                    answer = (
                        f"{organisation_name} has "
                        f"{overall_variance:,.2f} {currency} "
                        f"of portfolio budget remaining after "
                        f"accounting for all recorded spending, "
                        f"including unbudgeted actual spending."
                    )

                elif overall_variance < 0:

                    answer = (
                        f"{organisation_name} has no portfolio "
                        f"budget remaining. Total recorded spending "
                        f"exceeds the portfolio budget by "
                        f"{abs(overall_variance):,.2f} {currency}, "
                        f"including unbudgeted actual spending."
                    )

                else:

                    answer = (
                        f"{organisation_name}'s total recorded "
                        f"spending exactly equals the portfolio "
                        f"budget, so no budget remains."
                    )

            elif intent == "portfolio_budget_position":

                if overall_variance > 0:

                    answer = (
                        f"{organisation_name} is currently under "
                        f"its total portfolio budget by "
                        f"{overall_variance:,.2f} {currency}. "
                        f"Total recorded spending is "
                        f"{total_actual:,.2f} {currency} against "
                        f"a total budget of "
                        f"{total_budget:,.2f} {currency}."
                    )

                elif overall_variance < 0:

                    answer = (
                        f"{organisation_name} is currently over "
                        f"its total portfolio budget by "
                        f"{abs(overall_variance):,.2f} {currency}. "
                        f"Total recorded spending is "
                        f"{total_actual:,.2f} {currency} against "
                        f"a total budget of "
                        f"{total_budget:,.2f} {currency}."
                    )

                else:

                    answer = (
                        f"{organisation_name}'s total recorded "
                        f"spending exactly equals its total "
                        f"portfolio budget of "
                        f"{total_budget:,.2f} {currency}."
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
                    f"{over_budget_count} portfolio budget "
                    f"line(s) are above their approved limits."
                )

        # ==================================================
        # FINANCIAL FACTS
        # ==================================================

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
                f"{self._to_float(value):,.2f} "
                f"{currency}."
            )

        # ==================================================
        # CASH POSITION
        # ==================================================

        elif intent == "cash_position":

            available_cash = self._to_float(liquidity.get("available_cash"))

            total_cash = self._to_float(liquidity.get("total_cash"))

            blocked_cash = self._to_float(liquidity.get("blocked_cash"))

            answer = (
                f"{organisation_name}'s available cash is "
                f"{available_cash:,.2f} {currency}. "
                f"Total cash is "
                f"{total_cash:,.2f} {currency}, "
                f"of which "
                f"{blocked_cash:,.2f} {currency} "
                f"is blocked."
            )

        elif intent == "blocked_cash":

            blocked_cash = self._to_float(liquidity.get("blocked_cash"))

            total_cash = self._to_float(liquidity.get("total_cash"))

            answer = (
                f"{organisation_name} currently has "
                f"{blocked_cash:,.2f} {currency} "
                f"of blocked or restricted cash. "
                f"Total cash is "
                f"{total_cash:,.2f} {currency}."
            )

        # ==================================================
        # LIQUIDITY
        # ==================================================

        elif intent in self.LIQUIDITY_INTENTS:

            cash_runway_months = liquidity.get("cash_runway_months")

            runway_basis = liquidity.get(
                "runway_basis",
                ("Available cash divided by " "average monthly operating expenses."),
            )

            if cash_runway_months is None:

                answer = (
                    f"{organisation_name}'s cash runway "
                    f"is not available because there is "
                    f"not enough financial data to "
                    f"calculate it reliably."
                )

            else:

                answer = (
                    f"{organisation_name}'s cash runway is "
                    f"{self._to_float(cash_runway_months):,.2f} "
                    f"months. Basis: {runway_basis}"
                )

        # ==================================================
        # CASH FLOW
        # ==================================================

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
                f"{self._to_float(value):,.2f} "
                f"{currency}."
            )

        # ==================================================
        # LEGACY ORGANIZATION SUMMARY
        # ==================================================

        elif intent == "organization_summary":

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
                or intent in self.GRANT_INTENTS
                or intent in self.BUDGET_INTENTS
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
