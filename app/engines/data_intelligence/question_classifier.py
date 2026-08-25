from typing import Any


class QuestionClassifier:
    """
    Classify AI-FOS user questions into structured
    financial domains and intents.

    The classifier translates natural-language wording
    into stable AI-FOS intents. Financial calculations
    are performed by verified AI-FOS engines rather than
    inferred from the user's wording.
    """

    def classify(
        self,
        question: str,
    ) -> dict[str, Any]:

        cleaned_question = (
            str(question or "")
            .strip()
            .lower()
        )

        # ---------------------------------
        # Empty question
        # ---------------------------------

        if not cleaned_question:
            return {
                "domain": "unknown",
                "intent": "unknown",
                "target": None,
            }

        # =================================
        # CONTEXT-SPECIFIC ACTION INTENTS
        # =================================
        #
        # Action/advice intent must be checked before
        # subject-only rules such as "funding gap".
        #

        action_language = (
            "what should management do" in cleaned_question
            or "what should we do" in cleaned_question
            or "what actions should management take"
            in cleaned_question
            or "what actions should we take"
            in cleaned_question
            or "how should management respond"
            in cleaned_question
            or "how should we respond"
            in cleaned_question
            or "what do you recommend we do"
            in cleaned_question
        )

        if (
            action_language
            and (
                "funding gap" in cleaned_question
                or "funding shortage" in cleaned_question
                or "funding shortfall" in cleaned_question
            )
        ):
            return {
                "domain": "recommendation",
                "intent": "funding_gap_actions",
                "target": "funding_gap",
            }

        # =================================
        # FUNDING INTELLIGENCE
        # =================================
        #
        # Funding must be checked before the generic
        # "fund" / "grant" organization-knowledge rules.
        #

        funding_gap_phrases = (
            "funding gap",
            "funding shortage",
            "funding shortfall",
            "how much additional funding do we need",
            "how much more funding do we need",
            "how much funding do we need",
            "how much funding still needs to be secured",
            "how much funding needs to be secured",
            "how much funding remains to be secured",
            "how much funding is still needed",
            "how much funding remains needed",
            "how much money are we missing",
            "how much money do we still need",
            "how much money do we need",
        )

        if any(
            phrase in cleaned_question
            for phrase in funding_gap_phrases
        ):
            return {
                "domain": "funding",
                "intent": "funding_gap",
                "target": "funding_gap",
            }

        if (
            "funding coverage" in cleaned_question
            or "how much of our remaining requirements are funded"
            in cleaned_question
            or "how much of our requirements are funded"
            in cleaned_question
            or "what percentage of our requirements are funded"
            in cleaned_question
            or "what percentage is funded"
            in cleaned_question
            or "are our remaining requirements funded"
            in cleaned_question
            or "do we have enough funding"
            in cleaned_question
            or "do we have enough secured funding"
            in cleaned_question
            or "do we have enough money for our plans"
            in cleaned_question
            or "can our secured funding cover our plans"
            in cleaned_question
            or (
                "remaining requirements" in cleaned_question
                and "funded" in cleaned_question
            )
        ):
            return {
                "domain": "funding",
                "intent": "funding_coverage",
                "target": "applied_coverage_percentage",
            }

        if (
            "unfunded requirement" in cleaned_question
            or "unfunded requirements" in cleaned_question
            or "which requirements are not funded"
            in cleaned_question
            or "which requirements are unfunded"
            in cleaned_question
            or "what is not funded" in cleaned_question
            or "what remains unfunded" in cleaned_question
            or "what requirements still need funding"
            in cleaned_question
            or "which requirements still need funding"
            in cleaned_question
        ):
            return {
                "domain": "funding",
                "intent": "unfunded_requirements",
                "target": "unfunded_requirements",
            }

        if (
            "how much secured funding do we have"
            in cleaned_question
            or "how much secured funding have we secured"
            in cleaned_question
            or "what is our secured funding"
            in cleaned_question
            or "what is our total secured funding"
            in cleaned_question
            or "total secured funding"
            in cleaned_question
        ):
            return {
                "domain": "funding",
                "intent": "secured_funding_total",
                "target": "gross_remaining_secured_funding",
            }        

        if (
            "secured funding" in cleaned_question
            and (
                "available" in cleaned_question
                or "eligible" in cleaned_question
                or "can be used" in cleaned_question
                or "can we use" in cleaned_question
                or "usable" in cleaned_question
            )
        ):
            return {
                "domain": "funding",
                "intent": "eligible_secured_funding",
                "target": "applied_secured_funding",
            }

        funding_evidence_phrases = (
            "budget line allocation",
            "budget-line allocation",
            "funding evidence",
            "unallocated secured funding",
            "unmapped secured funding",
            "funding lacks allocation",
            "funding without allocation",
            "funding not allocated",
            "funding is excluded",
            "funding excluded",
            "why is some funding excluded",
            "why can't all our secured funding",
            "why cant all our secured funding",
            "why can't we use all our secured funding",
            "why cant we use all our secured funding",
            "why can we not use all our secured funding",
            "why can't we use all our funding",
            "why cant we use all our funding",
            "why can we not use all our funding",
            "why isn't all secured funding available",
            "why isnt all secured funding available",
            "why is not all secured funding available",
            "why isn't secured funding covering the gap",
            "why isnt secured funding covering the gap",
            "what funding cannot be used",
            "what funding can't be used",
            "what funding cant be used",
            "secured funding not eligible",
            "secured funding is not eligible",
            "how much secured funding is unallocated",
            "what funding lacks budget line allocation",
        )

        if any(
            phrase in cleaned_question
            for phrase in funding_evidence_phrases
        ):
            return {
                "domain": "funding",
                "intent": "funding_evidence",
                "target": (
                    "secured_funding_without_"
                    "budget_line_allocation"
                ),
            }


        # =================================
        # GRANT INTELLIGENCE
        # =================================

        grant_attention_phrases = (
            "which grants require financial attention",
            "which grants need financial attention",
            "which grants require attention",
            "which grants need attention",
        )

        if any(
            phrase in cleaned_question
            for phrase in grant_attention_phrases
        ):
            return {
                "domain": "grant",
                "intent": "grant_attention",
                "target": "grants",
            }

        grant_remaining_budget_phrases = (
            "which grants have remaining budget",
            "which grants still have budget",
            "which grants have budget remaining",
        )

        if any(
            phrase in cleaned_question
            for phrase in grant_remaining_budget_phrases
        ):
            return {
                "domain": "grant",
                "intent": "grant_remaining_budget",
                "target": "grants",
            }

        grant_high_utilization_phrases = (
            "which grants have high utilization",
            "which grants have high utilisation",
            "which grants are highly utilized",
            "which grants are highly utilised",
        )

        if any(
            phrase in cleaned_question
            for phrase in grant_high_utilization_phrases
        ):
            return {
                "domain": "grant",
                "intent": "grant_high_utilization",
                "target": "grants",
            }

        grant_spending_without_budget_phrases = (
            "are there grants with spending but no identified budget",
            "which grants have spending but no identified budget",
            "which grants have spending but no budget",
            "which grants have actual spending but no budget",
            "which grants have actuals but no budget",
            "grants with spending but no budget",
            "grants with actuals but no budget",
        )

        if any(
            phrase in cleaned_question
            for phrase in grant_spending_without_budget_phrases
        ):
            return {
                "domain": "grant",
                "intent": "grant_spending_without_budget",
                "target": "grants",
            }

        grant_budget_without_spending_phrases = (
            "are there grants with budget but no spending",
            "which grants have budget but no spending",
            "which grants have budget but no actual spending",
            "which grants have budget but no actuals",
            "grants with budget but no spending",
            "grants with budget but no actuals",
        )

        if any(
            phrase in cleaned_question
            for phrase in grant_budget_without_spending_phrases
        ):
            return {
                "domain": "grant",
                "intent": "grant_budget_without_spending",
                "target": "grants",
            }

        grant_funding_budget_issues_phrases = (
            "which grants may have funding or budget issues",
            "which grants have funding or budget issues",
            "which grants have budget or funding issues",
            "which grants have financial issues",
            "which grants have budget issues",
            "which grants have funding issues",
            "grants with funding or budget issues",
        )

        if any(
            phrase in cleaned_question
            for phrase in grant_funding_budget_issues_phrases
        ):
            return {
                "domain": "grant",
                "intent": "grant_funding_budget_issues",
                "target": "grants",
            }

        grant_portfolio_summary_phrases = (
            "what should management know about our grant portfolio",
            "what should management know about the grant portfolio",
            "summarize our grant portfolio",
            "summarise our grant portfolio",
            "grant portfolio summary",
            "how is our grant portfolio performing",
            "what is happening across our grant portfolio",
            "what should we know about our grants",
        )

        if any(
            phrase in cleaned_question
            for phrase in grant_portfolio_summary_phrases
        ):
            return {
                "domain": "grant",
                "intent": "grant_portfolio_summary",
                "target": "grants",
            }

        # =================================
        # RECOMMENDATION INTELLIGENCE
        # =================================


        priority_action_phrases = (
            "what should we prioritize",
            "what should management prioritize",
            "what should management prioritise",
            "what should we prioritise",
            "priority actions",
            "top actions",
            "highest priority",
            "highest-priority actions",
            "top priorities",
            "management priorities",
            "most important actions",
            "most urgent actions",
            "what actions require immediate management attention",            
            "what should we focus on first",
            "what should management focus on first",
            "what are the highest priority actions",
            "what are the highest-priority actions",
        )

        if any(
            phrase in cleaned_question
            for phrase in priority_action_phrases
        ):
            return {
                "domain": "recommendation",
                "intent": "priority_actions",
                "target": "recommendations",
            }

        funding_gap_action_phrases = (
            "what should management do about the funding gap",
            "what should we do about the funding gap",
            "what actions should we take on the funding gap",
            "how should we address the funding gap",
            "how can we reduce the funding gap",
            "how can we close the funding gap",
            "what should management do about unfunded requirements",
            "what should we do about unfunded requirements",
        )

        if any(
            phrase in cleaned_question
            for phrase in funding_gap_action_phrases
        ):
            return {
                "domain": "recommendation",
                "intent": "funding_gap_actions",
                "target": "recommendations",
            }

        finance_meeting_agenda_phrases = (
            "what should management discuss at the next finance meeting",
            "what should we discuss at the next finance meeting",
            "what should be discussed at the next finance meeting",
            "what should management discuss in the next finance meeting",
            "what should we discuss in our next finance meeting",
            "what should be on the finance meeting agenda",
            "what should be on our finance meeting agenda",
            "finance meeting agenda",
            "next finance meeting agenda",
        )

        if any(
            phrase in cleaned_question
            for phrase in finance_meeting_agenda_phrases
        ):
            return {
                "domain": "recommendation",
                "intent": "finance_meeting_agenda",
                "target": "management_agenda",
            }

        recommendation_summary_phrases = (
            "what should management do",
            "what should management do next",
            "what should we do",
            "what should we do next",
            "what do you recommend",
            "what do you recommend we do",
            "what actions do you recommend",
            "what actions should we take",
            "what should our next steps be",
            "what are our next steps",
            "recommendation",
            "recommendations",
            "how can we improve",
            "improve our financial position",
            "how should management respond",
        )

        if any(
            phrase in cleaned_question
            for phrase in recommendation_summary_phrases
        ):
            return {
                "domain": "recommendation",
                "intent": "recommendation_summary",
                "target": "recommendations",
            }

        if (
            "action" in cleaned_question
            and (
                "priority" in cleaned_question
                or "urgent" in cleaned_question
                or "first" in cleaned_question
            )
        ):
            return {
                "domain": "recommendation",
                "intent": "priority_actions",
                "target": "recommendations",
            }

        if (
            "recommend" in cleaned_question
            or (
                "management" in cleaned_question
                and "do" in cleaned_question
            )
        ):
            return {
                "domain": "recommendation",
                "intent": "recommendation_summary",
                "target": "recommendations",
            }

        # =================================
        # RISK INTELLIGENCE
        # =================================

        high_risk_phrases = (
            "high risk",
            "high-risk",
            "high risks",
            "high-risk risks",
            "high severity risk",
            "high-severity risk",
            "high severity risks",
            "high-severity risks",
            "critical risk",
            "critical risks",
            "serious financial warning signs",
            "serious warning signs",
            "serious financial risks",
            "serious risks",
            "major financial warning signs",
            "major warning signs",
        )

        if any(
            phrase in cleaned_question
            for phrase in high_risk_phrases
        ):
            return {
                "domain": "risk",
                "intent": "high_risks",
                "target": "risks",
            }

        risk_summary_phrases = (
            "biggest financial risk",
            "biggest financial risks",
            "biggest risk",
            "biggest risks",
            "financial risks",
            "main risks",
            "top risks",
            "main financial risks",
            "top financial risks",
            "what should management worry about",
            "what should we worry about",
            "what are our main financial risks",
            "what are the biggest threats to our financial position",
            "what financial risks should management focus on",
            "summarize our financial risks",
            "what could negatively affect our financial position",
            "what could negatively affect the financial position",
            "what could hurt our financial position",
            "what could weaken our financial position",
            "which risks should management monitor closely",
            "what risks should management monitor closely",
            "which financial risks should management monitor closely",
            "risks management should monitor",            
            "risk summary",
        )

        if any(
            phrase in cleaned_question
            for phrase in risk_summary_phrases
        ):
            return {
                "domain": "risk",
                "intent": "risk_summary",
                "target": "risks",
            }

        if (
            "which financial risk needs immediate attention"
            in cleaned_question
            or "which risk needs immediate attention"
            in cleaned_question
            or "what financial risk needs immediate attention"
            in cleaned_question
            or "what risk needs immediate attention"
            in cleaned_question
            or "most urgent financial risk"
            in cleaned_question
            or "most urgent risk"
            in cleaned_question
        ):
            return {
                "domain": "risk",
                "intent": "immediate_risk",
                "target": "risks",
            }

        if (
            "liquidity risks" in cleaned_question
            or "liquidity risk" in cleaned_question
            or "cash risks" in cleaned_question
            or "cash risk" in cleaned_question
        ):
            return {
                "domain": "risk",
                "intent": "liquidity_risks",
                "target": "risks",
            }

        if (
            "budget risks" in cleaned_question
            or "budget risk" in cleaned_question
            or "overspending risks" in cleaned_question
            or "overspending risk" in cleaned_question
        ):
            return {
                "domain": "risk",
                "intent": "budget_risks",
                "target": "risks",
            }

        if (
            "funding risks" in cleaned_question
            or "funding risk" in cleaned_question
            or "grant risks" in cleaned_question
            or "grant risk" in cleaned_question
        ):
            return {
                "domain": "risk",
                "intent": "funding_risks",
                "target": "risks",
            }

        if (
            "risk" in cleaned_question
            and (
                "warning" in cleaned_question
                or "serious" in cleaned_question
                or "critical" in cleaned_question
                or "high" in cleaned_question
            )
        ):
            return {
                "domain": "risk",
                "intent": "high_risks",
                "target": "risks",
            }

        if (
            "risk" in cleaned_question
            and (
                "main" in cleaned_question
                or "biggest" in cleaned_question
                or "top" in cleaned_question
                or "summary" in cleaned_question
                or "worry" in cleaned_question
            )
        ):
            return {
                "domain": "risk",
                "intent": "risk_summary",
                "target": "risks",
            }
        # =================================
        # FINANCIAL HEALTH
        # =================================

        financial_health_explanation_phrases = (
            "why is our financial health",
            "why is the financial health",
            "what is affecting our financial health",
            "what affects our financial health",
            "what is hurting our financial health",
            "what is hurting our financial health the most",
            "what is affecting our financial health the most",
            "financial health breakdown",
            "health score breakdown",
            "why is our health score",
            "what is affecting our health score",
            "what is driving our health score down",
            "what is driving our financial health",
            "what are the main weaknesses in our financial position",
            "what are our financial weaknesses",
            "what are the weaknesses in our financial position",
            "why is our financial position weak",
            "where are we financially weak",
            "what are our strongest financial areas",
            "what are the strongest areas of our financial health",
            "where are we financially strong",
            "financial strengths",
            "strongest areas",
            "strong areas",
            "what is strongest in our financial health",
            "summarize our financial health for management",
            "how would you summarize our financial health for management",
            "what should management focus on to improve financial health",
            "what should management do to improve our financial health",
        )

        if any(
            phrase in cleaned_question
            for phrase in financial_health_explanation_phrases
        ):
            return {
                "domain": "financial_health",
                "intent": "financial_health_explanation",
                "target": "financial_health",
            }

        if (
            "weakness" in cleaned_question
            or "weaknesses" in cleaned_question
            or "weakest" in cleaned_question
            or (
                "financial position" in cleaned_question
                and "weak" in cleaned_question
            )
            or (
                "financial health" in cleaned_question
                and "hurting" in cleaned_question
            )
            or (
                "financial health" in cleaned_question
                and "affecting" in cleaned_question
            )
            or (
                "health score" in cleaned_question
                and "driving" in cleaned_question
            )
            or (
                "financial health" in cleaned_question
                and "strongest" in cleaned_question
            )
            or (
                "financial health" in cleaned_question
                and "strength" in cleaned_question
            )
            or (
                "financial health" in cleaned_question
                and "summarize" in cleaned_question
            )
            or (
                "financial health" in cleaned_question
                and "management" in cleaned_question
                and (
                    "improve" in cleaned_question
                    or "focus" in cleaned_question
                )
            )
        ):
            return {
                "domain": "financial_health",
                "intent": "financial_health_explanation",
                "target": "financial_health",
            }

        if (
            "financial health" in cleaned_question
            or "health score" in cleaned_question
            or "financially healthy" in cleaned_question
            or "are we financially healthy" in cleaned_question
            or "how healthy are our finances" in cleaned_question
            or "how healthy is our financial position" in cleaned_question
        ):
            return {
                "domain": "financial_health",
                "intent": "financial_health",
                "target": "financial_health",
            }

        # =================================
        # CASH AND LIQUIDITY
        # =================================

        if (
            "cash runway" in cleaned_question
            or "runway" in cleaned_question
            or "months of cash" in cleaned_question
            or "how long can we operate" in cleaned_question
            or "how many months can we operate"
            in cleaned_question
        ):
            return {
                "domain": "liquidity",
                "intent": "cash_runway",
                "target": "cash_runway_months",
            }

        if (
            "blocked cash" in cleaned_question
            or "restricted cash" in cleaned_question
            or "how much cash is blocked"
            in cleaned_question
            or "how much cash is restricted"
            in cleaned_question
            or "how much of our cash is blocked"
            in cleaned_question
            or "how much of our cash is restricted"
            in cleaned_question
            or (
                "cash" in cleaned_question
                and (
                    "blocked" in cleaned_question
                    or "restricted" in cleaned_question
                )
            )
        ):
            return {
                "domain": "cash",
                "intent": "blocked_cash",
                "target": "blocked_cash",
            }

        if (
            "how much cash do we have" in cleaned_question
            or "how much cash do we currently have"
            in cleaned_question
            or "what is our cash position" in cleaned_question
            or "what is our cash balance" in cleaned_question
            or "how much cash is available" in cleaned_question
            or "how much available cash do we have"
            in cleaned_question
            or "available cash" in cleaned_question
            or "cash position" in cleaned_question
            or (
                "cash" in cleaned_question
                and "available" in cleaned_question
            )
        ):
            return {
                "domain": "cash",
                "intent": "cash_position",
                "target": "cash_position",
            }

        if (
            "liquidity position" in cleaned_question
            or "liquidity health" in cleaned_question
            or "liquidity healthy" in cleaned_question
            or "healthy liquidity" in cleaned_question
            or "is our liquidity healthy"
            in cleaned_question
            or "how healthy is our liquidity"
            in cleaned_question
        ):
            return {
                "domain": "liquidity",
                "intent": "liquidity_health",
                "target": "liquidity",
            }

        # =================================
        # CASH FLOW
        # =================================

        if (
            "operating cash flow" in cleaned_question
            or "cash from operations" in cleaned_question
            or "cash comes from operations"
            in cleaned_question
        ):
            return {
                "domain": "cash_flow",
                "intent": "operating_cash_flow",
                "target": "operating_activities",
            }

        if (
            "investing cash flow" in cleaned_question
            or "cash from investing" in cleaned_question
        ):
            return {
                "domain": "cash_flow",
                "intent": "investing_cash_flow",
                "target": "investing_activities",
            }

        if (
            "financing cash flow" in cleaned_question
            or "cash from financing" in cleaned_question
        ):
            return {
                "domain": "cash_flow",
                "intent": "financing_cash_flow",
                "target": "financing_activities",
            }

        if (
            "net change in cash" in cleaned_question
            or "change in cash" in cleaned_question
        ):
            return {
                "domain": "cash_flow",
                "intent": "net_change_in_cash",
                "target": "net_change_in_cash",
            }

        # =================================
        # BUDGET INTELLIGENCE
        # =================================

        if (
            "unbudgeted expenditure" in cleaned_question
            or "unbudgeted spending" in cleaned_question
            or "unbudgeted actual" in cleaned_question
            or "unbudgeted actual spending"
            in cleaned_question
            or "unbudgeted actuals" in cleaned_question
            or "spending without budget" in cleaned_question
            or "spending without a budget"
            in cleaned_question
            or "actuals without budget" in cleaned_question
            or "actuals without a budget"
            in cleaned_question
            or "actual spending without budget"
            in cleaned_question
            or "actual spending without a budget"
            in cleaned_question
            or "how much have we spent without a budget"
            in cleaned_question
            or "how much spending do we have without a budget"
            in cleaned_question            
        ):
            return {
                "domain": "budget",
                "intent": "unbudgeted_actual",
                "target": "unbudgeted_actual",
            }

        if (
            "over budget lines" in cleaned_question
            or "over-budget lines" in cleaned_question
            or "budget lines are over" in cleaned_question
            or "budget lines exceeded" in cleaned_question
            or "how many budget lines are over"
            in cleaned_question
            or "how many budget lines have exceeded their budgets"
            in cleaned_question            
        ):
            return {
                "domain": "budget",
                "intent": "over_budget_count",
                "target": "over_budget_count",
            }

        if (
            "which areas are over budget"
            in cleaned_question
            or "which areas are currently over budget"
            in cleaned_question
            or "where are we over budget"
            in cleaned_question
            or "where are we currently over budget"
            in cleaned_question
            or "which budget areas are over budget"
            in cleaned_question
            or "where do we still have available budget"
            in cleaned_question
            or "where do we have available budget"
            in cleaned_question
            or "where is budget still available"
            in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "portfolio_budget_summary",
                "target": "portfolio_control",
            }

        if (
            "which budget lines need management attention"
            in cleaned_question
            or "which budget lines need attention"
            in cleaned_question
            or "budget lines needing management attention"
            in cleaned_question
            or "budget lines requiring management attention"
            in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "budget_performance_summary",
                "target": "budget_dashboard",
            }

        if (
            "budget utilization" in cleaned_question
            or "budget utilisation" in cleaned_question
            or "how much of the budget" in cleaned_question
            or "how much of our budget" in cleaned_question
            or "how much budget have we used"
            in cleaned_question
            or "how much budget has been used"
            in cleaned_question
            or "what percentage of our budget have we spent"
            in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "portfolio_budget_utilization",
                "target": "utilization_percentage",
            }

        # ---------------------------------
        # Budget variance
        #
        # Variance against identified
        # approved budget lines only.
        # ---------------------------------

        if (
            "budget variance" in cleaned_question
            or "variance against budget" in cleaned_question
            or "variance to budget" in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "portfolio_budget_variance",
                "target": "total_variance",
            }

        # ---------------------------------
        # Budget remaining
        #
        # What is actually left after all
        # portfolio spending, including
        # unbudgeted actual spending.
        # ---------------------------------

        if (
            "how much budget do we have left"
            in cleaned_question
            or "how much budget is left"
            in cleaned_question
            or "how much budget remains"
            in cleaned_question
            or "how much budget is remaining"
            in cleaned_question
            or "do we still have budget remaining"
            in cleaned_question
            or "is there any budget left"
            in cleaned_question
            or "do we have any budget left"
            in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "portfolio_budget_remaining",
                "target": (
                    "overall_variance_including_unbudgeted"
                ),
            }

        # ---------------------------------
        # Overall budget position
        #
        # Whether total portfolio spending
        # is above or below total budget.
        # ---------------------------------

        if (
            "how much are we over budget"
            in cleaned_question
            or "how much are we over our budget"
            in cleaned_question
            or "how much over budget are we"
            in cleaned_question
            or "how far over budget are we"
            in cleaned_question
            or "are we spending more than we budgeted"
            in cleaned_question
            or "are we spending more than budgeted"
            in cleaned_question
            or "are we spending less than we budgeted"
            in cleaned_question
            or "are we spending less than budgeted"
            in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "portfolio_budget_position",
                "target": (
                    "overall_variance_including_unbudgeted"
                ),
            }

        if (
            "how is our budget performing"
            in cleaned_question
            or "how is the budget performing"
            in cleaned_question
            or "budget performance overall"
            in cleaned_question
            or "overall budget performance"
            in cleaned_question
            or "overall budget position"
            in cleaned_question
            or "how are we doing against budget"
            in cleaned_question
            or "are we overspending against our budget"
            in cleaned_question
            or "are we overspending against budget"
            in cleaned_question
            or "are we over budget" in cleaned_question
            or "are we currently over budget"
            in cleaned_question
            or "are we over our budget" in cleaned_question
            or "are we currently over our budget"
            in cleaned_question
            or "are we under budget" in cleaned_question
            or "are we under our budget" in cleaned_question
            or "main budget control issues"
            in cleaned_question
            or "what are the main budget control issues"
            in cleaned_question
            or "budget control issues"
            in cleaned_question
            or "budget control problems"
            in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "budget_performance_summary",
                "target": "budget_dashboard",
            }

        if (
            "budget actual" in cleaned_question
            or "budget vs actual" in cleaned_question
            or "budget versus actual" in cleaned_question
            or "compare our budget to actual spending"
            in cleaned_question
            or "compare budget to actual spending"
            in cleaned_question
            or "compare our budget to actual"
            in cleaned_question
            or "compare budget to actual"
            in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "portfolio_budget_summary",
                "target": "portfolio_control",
            }

        if (
            "total budget" in cleaned_question
            or "portfolio budget" in cleaned_question
            or "approved budget" in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "portfolio_total_budget",
                "target": "total_budget",
            }

        # =================================
        # FINANCIAL PERFORMANCE
        # =================================

        if (
            "how much have we spent" in cleaned_question
            or "how much did we spend" in cleaned_question
            or "how much are we spending" in cleaned_question
            or "total spending" in cleaned_question
            or "total expenditure" in cleaned_question
        ):
            return {
                "domain": "financial",
                "intent": "expenses",
                "target": "expenses",
            }

        if (
            "main drivers of our financial performance"
            in cleaned_question
            or "main drivers of financial performance"
            in cleaned_question
            or "drivers of our financial performance"
            in cleaned_question
            or "drivers of financial performance"
            in cleaned_question
            or "what is driving our financial performance"
            in cleaned_question
            or "what is driving financial performance"
            in cleaned_question
        ):
            return {
                "domain": "financial_health",
                "intent": "financial_health_explanation",
                "target": "financial_health",
            }

        if (
            "is our current operating performance sustainable"
            in cleaned_question
            or "is our operating performance sustainable"
            in cleaned_question
            or "is our financial performance sustainable"
            in cleaned_question
            or "is this financial performance sustainable"
            in cleaned_question
            or "operating performance sustainable"
            in cleaned_question
        ):
            return {
                "domain": "financial_health",
                "intent": "financial_health_explanation",
                "target": "financial_health",
            }

        if (
            "what should management focus on to improve financial performance"
            in cleaned_question
            or "what should management focus on to improve our financial performance"
            in cleaned_question
            or "how should management improve financial performance"
            in cleaned_question
            or "how can management improve financial performance"
            in cleaned_question
            or "what actions should management take to improve financial performance"
            in cleaned_question
        ):
            return {
                "domain": "recommendation",
                "intent": "recommendation_summary",
                "target": "recommendations",
            }

        # =================================
        # FINANCIAL FACTS
        # =================================

        if "revenue" in cleaned_question:
            return {
                "domain": "financial",
                "intent": "revenue",
                "target": "revenue",
            }

        if (
            "expense" in cleaned_question
            or "expenses" in cleaned_question
        ):
            return {
                "domain": "financial",
                "intent": "expenses",
                "target": "expenses",
            }

        if (
            "net profit" in cleaned_question
            or "net result" in cleaned_question
            or "profit" in cleaned_question
            or "surplus" in cleaned_question
            or "deficit" in cleaned_question
        ):
            return {
                "domain": "financial",
                "intent": "net_profit",
                "target": "net_profit",
            }

        if "asset" in cleaned_question:
            return {
                "domain": "financial",
                "intent": "assets",
                "target": "assets",
            }

        if "liabilit" in cleaned_question:
            return {
                "domain": "financial",
                "intent": "liabilities",
                "target": "liabilities",
            }

        if "equity" in cleaned_question:
            return {
                "domain": "financial",
                "intent": "equity",
                "target": "equity",
            }

        # =================================
        # ORGANIZATION KNOWLEDGE
        # =================================

        if "donor" in cleaned_question:
            return {
                "domain": "organization",
                "intent": "donor_count",
                "target": "donors",
            }

        if "currency" in cleaned_question:
            return {
                "domain": "organization",
                "intent": "currency",
                "target": "currency",
            }

        if "transaction" in cleaned_question:
            return {
                "domain": "financial_model",
                "intent": "transaction_count",
                "target": "transactions",
            }

        if "account" in cleaned_question:
            return {
                "domain": "financial_model",
                "intent": "account_count",
                "target": "accounts",
            }

        if "program" in cleaned_question:
            return {
                "domain": "organization",
                "intent": "program_count",
                "target": "programs",
            }

        if (
            "how many funds" in cleaned_question
            or "how many grants" in cleaned_question
            or "number of funds" in cleaned_question
            or "number of grants" in cleaned_question
        ):
            return {
                "domain": "organization",
                "intent": "fund_count",
                "target": "funds",
            }

        # =================================
        # SAFE DEFAULT
        # =================================

        return {
            "domain": "unknown",
            "intent": "unknown",
            "target": None,
        }