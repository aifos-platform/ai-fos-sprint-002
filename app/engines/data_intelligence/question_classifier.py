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

        cleaned_question = str(question or "").strip().lower()

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
            or "what actions should management take" in cleaned_question
            or "what actions should we take" in cleaned_question
            or "how should management respond" in cleaned_question
            or "how should we respond" in cleaned_question
            or "what do you recommend we do" in cleaned_question
        )

        if action_language and (
            "funding gap" in cleaned_question
            or "funding shortage" in cleaned_question
            or "funding shortfall" in cleaned_question
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

        if any(phrase in cleaned_question for phrase in funding_gap_phrases):
            return {
                "domain": "funding",
                "intent": "funding_gap",
                "target": "funding_gap",
            }

        if (
            "funding coverage" in cleaned_question
            or "how much of our remaining requirements are funded" in cleaned_question
            or "how much of our requirements are funded" in cleaned_question
            or "what percentage of our requirements are funded" in cleaned_question
            or "what percentage is funded" in cleaned_question
            or "are our remaining requirements funded" in cleaned_question
            or "do we have enough funding" in cleaned_question
            or "do we have enough secured funding" in cleaned_question
            or "do we have enough money for our plans" in cleaned_question
            or "can our secured funding cover our plans" in cleaned_question
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
            or "which requirements are not funded" in cleaned_question
            or "which requirements are unfunded" in cleaned_question
            or "what is not funded" in cleaned_question
            or "what remains unfunded" in cleaned_question
            or "what requirements still need funding" in cleaned_question
            or "which requirements still need funding" in cleaned_question
        ):
            return {
                "domain": "funding",
                "intent": "unfunded_requirements",
                "target": "unfunded_requirements",
            }

        if (
            "how much secured funding do we have" in cleaned_question
            or "how much secured funding have we secured" in cleaned_question
            or "what is our secured funding" in cleaned_question
            or "what is our total secured funding" in cleaned_question
            or "total secured funding" in cleaned_question
        ):
            return {
                "domain": "funding",
                "intent": "secured_funding_total",
                "target": "gross_remaining_secured_funding",
            }

        if "secured funding" in cleaned_question and (
            "available" in cleaned_question
            or "eligible" in cleaned_question
            or "can be used" in cleaned_question
            or "can we use" in cleaned_question
            or "usable" in cleaned_question
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

        if any(phrase in cleaned_question for phrase in funding_evidence_phrases):
            return {
                "domain": "funding",
                "intent": "funding_evidence",
                "target": ("secured_funding_without_" "budget_line_allocation"),
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

        if any(phrase in cleaned_question for phrase in grant_attention_phrases):
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

        if any(phrase in cleaned_question for phrase in grant_remaining_budget_phrases):
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

        if any(phrase in cleaned_question for phrase in grant_high_utilization_phrases):
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
            phrase in cleaned_question for phrase in grant_funding_budget_issues_phrases
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
            phrase in cleaned_question for phrase in grant_portfolio_summary_phrases
        ):
            return {
                "domain": "grant",
                "intent": "grant_portfolio_summary",
                "target": "grants",
            }

        # =========================================
        # CFO ACTION PLAN / ACTION MONITORING
        # =========================================

        action_plan_summary_phrases = (
            "cfo action plan status",
            "action plan status",
            "status of our action plan",
            "status of the action plan",
            "summarize our action plan",
            "summarise our action plan",
            "show our action plan",
            "how many actions are open",
            "how many actions are still open",
        )

        overdue_action_phrases = (
            "what actions are overdue",
            "which actions are overdue",
            "show overdue actions",
            "overdue management actions",
            "overdue financial actions",
        )

        due_soon_action_phrases = (
            "what needs follow-up this week",
            "what needs follow up this week",
            "which actions are due soon",
            "what actions are due soon",
            "show actions due soon",
            "what is due this week",
            "what actions are due this week",
        )

        blocked_action_phrases = (
            "which actions are blocked",
            "what actions are blocked",
            "show blocked actions",
            "blocked management actions",
        )

        unassigned_action_phrases = (
            "which high-priority actions have no owner",
            "which high priority actions have no owner",
            "which high-priority actions still have no owner",
            "which high priority actions still have no owner",
            "unassigned high-priority actions",
            "unassigned high priority actions",
            "critical actions without owners",
            "high priority actions without owners",
        )

        action_performance_summary_phrases = (
            "how is our action plan performing",
            "how is the action plan performing",
            "how are our management actions performing",
            "how are our cfo actions performing",
            "summarize action performance",
            "summarise action performance",
            "action performance summary",
            "cfo action performance",
            "management action performance",
            "what does our action history show",
            "summarize our action history",
            "summarise our action history",
        )

        reopened_action_pattern_phrases = (
            "which actions keep reopening",
            "which actions are repeatedly reopened",
            "which actions have been reopened",
            "show reopened action patterns",
            "show reopening patterns",
            "reopened action patterns",
            "reopening patterns",
            "are actions being reopened",
        )

        repeated_blocking_pattern_phrases = (
            "which actions keep getting blocked",
            "which actions are repeatedly blocked",
            "which actions have been blocked repeatedly",
            "show repeated blocking patterns",
            "show blocking patterns",
            "repeated blocking patterns",
            "blocking patterns",
            "are actions repeatedly getting blocked",
        )

        ownership_change_pattern_phrases = (
            "which actions keep changing owners",
            "which actions have changed owners",
            "which actions have ownership changes",
            "show ownership change patterns",
            "show owner change patterns",
            "ownership change patterns",
            "owner change patterns",
            "how often are action owners changing",
        )

        due_date_change_pattern_phrases = (
            "which actions keep changing due dates",
            "which actions have changed due dates",
            "which actions have deadline changes",
            "show due date change patterns",
            "show deadline change patterns",
            "due date change patterns",
            "deadline change patterns",
            "how often are action deadlines changing",
        )        

        action_escalation_phrases = (
            "which actions need management intervention",
            "what actions need management intervention",
            "which actions require management intervention",
            "what actions require management intervention",
            "what needs escalation right now",
            "which actions need escalation",
            "what actions need escalation",
            "show management escalations",
            "show action escalations",
            "management action escalation",
            "management action escalations",
            "what needs management attention right now",
            "which management actions need attention",
        )

        critical_followup_phrases = (
            "what are my critical follow-ups",
            "what are my critical follow ups",
            "show critical follow-ups",
            "show critical follow ups",
            "which actions require immediate attention",
            "what requires immediate management attention",
            "which actions need immediate intervention",
            "what needs immediate intervention",
            "show critical management actions",
            "critical management follow-ups",
            "critical management follow ups",
        )

        if any(
            phrase in cleaned_question
            for phrase in reopened_action_pattern_phrases
        ):
            return {
                "domain": "cfo_action_plan",
                "intent": "reopened_action_patterns",
                "target": "cfo_action_performance",
            }

        if any(
            phrase in cleaned_question
            for phrase in repeated_blocking_pattern_phrases
        ):
            return {
                "domain": "cfo_action_plan",
                "intent": "repeated_blocking_patterns",
                "target": "cfo_action_performance",
            }

        if any(
            phrase in cleaned_question
            for phrase in ownership_change_pattern_phrases
        ):
            return {
                "domain": "cfo_action_plan",
                "intent": "ownership_change_patterns",
                "target": "cfo_action_performance",
            }

        if any(
            phrase in cleaned_question
            for phrase in due_date_change_pattern_phrases
        ):
            return {
                "domain": "cfo_action_plan",
                "intent": "due_date_change_patterns",
                "target": "cfo_action_performance",
            }

        if any(
            phrase in cleaned_question
            for phrase in action_performance_summary_phrases
        ):
            return {
                "domain": "cfo_action_plan",
                "intent": "action_performance_summary",
                "target": "cfo_action_performance",
            }                

        if any(
            phrase in cleaned_question
            for phrase in critical_followup_phrases
        ):
            return {
                "domain": "cfo_action_plan",
                "intent": "critical_action_followups",
                "target": "cfo_action_escalation",
            }

        if any(
            phrase in cleaned_question
            for phrase in action_escalation_phrases
        ):
            return {
                "domain": "cfo_action_plan",
                "intent": "action_escalation_summary",
                "target": "cfo_action_escalation",
            }

        if any(
            phrase in cleaned_question
            for phrase in overdue_action_phrases
        ):
            
            return {
                "domain": "cfo_action_plan",
                "intent": "overdue_actions",
                "target": "cfo_action_monitoring",
            }

        if any(
            phrase in cleaned_question
            for phrase in due_soon_action_phrases
        ):
            return {
                "domain": "cfo_action_plan",
                "intent": "due_soon_actions",
                "target": "cfo_action_monitoring",
            }

        if any(
            phrase in cleaned_question
            for phrase in blocked_action_phrases
        ):
            return {
                "domain": "cfo_action_plan",
                "intent": "blocked_actions",
                "target": "cfo_action_monitoring",
            }

        if any(
            phrase in cleaned_question
            for phrase in unassigned_action_phrases
        ):
            return {
                "domain": "cfo_action_plan",
                "intent": (
                    "unassigned_high_priority_actions"
                ),
                "target": "cfo_action_monitoring",
            }

        if any(
            phrase in cleaned_question
            for phrase in action_plan_summary_phrases
        ):
            return {
                "domain": "cfo_action_plan",
                "intent": "action_plan_summary",
                "target": "cfo_action_monitoring",
            }

        # =========================================
        # EXECUTIVE DECISION INTELLIGENCE
        # =========================================
        #
        # Broad executive-prioritization questions
        # are intentionally separate from the older
        # CFO Recommendation priority_actions intent.
        #

        executive_priority_phrases = (
            "what should management focus on right now",
            "what should we focus on right now",
            "what should management focus on now",
            "what should we focus on now",
            "what should management focus on overall",
            "what should we focus on overall",
            "what are our top management priorities",
            "what are the top management priorities",
            "what needs management attention right now",
            "what requires management attention right now",
            "what should management prioritize overall",
            "what should management prioritise overall",
        )

        if any(
            phrase in cleaned_question
            for phrase in executive_priority_phrases
        ):
            return {
                "domain": "executive_decision",
                "intent": "executive_priority_summary",
                "target": "executive_decision_intelligence",
            }

        # =========================================
        # HISTORICAL FINANCIAL INTELLIGENCE
        # =========================================
        #
        # Historical comparison must be checked
        # before generic Risk, Financial Health,
        # Financial Trend, and Financial Fact rules.
        #

        new_risk_history_phrases = (
            "what new risks appeared since the previous update",
            "what new risks appeared since our previous update",
            "what new risks appeared since the last update",
            "what new risks appeared since our last update",
            "what new risks have appeared",
            "what new financial risks have appeared",
            "which new risks appeared",
            "which new financial risks appeared",
            "what risks are new since the previous snapshot",
            "what risks are new since the last snapshot",
            "what new risks do we have since the previous period",
            "what new risks do we have since the last period",
        )

        if any(
            phrase in cleaned_question
            for phrase in new_risk_history_phrases
        ):
            return {
                "domain": "historical_change",
                "intent": "new_risks_since_previous",
                "target": "financial_intelligence_history",
            }

        resolved_risk_history_phrases = (
            "which risks were resolved",
            "what risks were resolved",
            "which financial risks were resolved",
            "what financial risks were resolved",
            "which risks have been resolved",
            "what risks have been resolved",
            "which risks disappeared",
            "what risks disappeared",
            "which risks are no longer present",
            "what risks are no longer present",
            "which risks were resolved since the previous update",
            "which risks were resolved since the last update",
            "what risks were resolved since the previous period",
            "what risks were resolved since the last period",
        )

        if any(
            phrase in cleaned_question
            for phrase in resolved_risk_history_phrases
        ):
            return {
                "domain": "historical_change",
                "intent": "resolved_risks_since_previous",
                "target": "financial_intelligence_history",
            }

        risk_change_history_phrases = (
            "how have our risks changed",
            "how have our financial risks changed",
            "what changed in our risks",
            "what changed in our financial risks",
            "how did our risks change",
            "how did our financial risks change",
            "compare our risks with the previous update",
            "compare our risks to the previous update",
            "compare our risks with the last update",
            "compare our risks to the last update",
            "risk changes since the previous update",
            "risk changes since the last update",
            "risk movement",
            "risk movement summary",
        )

        if any(
            phrase in cleaned_question
            for phrase in risk_change_history_phrases
        ):
            return {
                "domain": "historical_change",
                "intent": "risk_change_summary",
                "target": "financial_intelligence_history",
            }

        financial_position_change_phrases = (
            "is our financial position improving or deteriorating",
            "is our financial position improving",
            "is our financial position deteriorating",
            "has our financial position improved",
            "has our financial position deteriorated",
            "how has our financial position changed",
            "how did our financial position change",
            "how have our finances changed",
            "how did our finances change",
            "compare our financial position with the previous update",
            "compare our financial position to the previous update",
            "compare our financial position with the last update",
            "compare our financial position to the last update",
            "financial position change since the previous update",
            "financial position change since the last update",
        )

        if any(
            phrase in cleaned_question
            for phrase in financial_position_change_phrases
        ):
            return {
                "domain": "historical_change",
                "intent": "financial_position_change",
                "target": "financial_intelligence_history",
            }

        historical_management_priority_phrases = (
            "what historical changes require management attention",
            "what changes require management attention",
            "what deteriorations should management prioritize",
            "what financial deteriorations should management prioritize",
            "based on our latest financial changes, what should management focus on",
            "based on our latest financial changes, what should management prioritize",
            "what should management focus on based on recent financial changes",
            "what should management prioritize based on recent financial changes",
            "what historical financial changes need management attention",
            "what historical financial changes need management action",
            "what change driven priorities do we have",
            "what are our change driven priorities",
            "historical management priorities",
            "historical decision priorities",
        )

        if any(
            phrase in cleaned_question
            for phrase in historical_management_priority_phrases
        ):
            return {
                "domain": "historical_decision",
                "intent": (
                    "historical_management_priority_summary"
                ),
                "target": (
                    "historical_decision_intelligence"
                ),
            }        

        historical_change_summary_phrases = (
            "what changed since our last financial update",
            "what changed since the last financial update",
            "what changed since our previous financial update",
            "what changed since the previous financial update",
            "what has changed since our last financial update",
            "what has changed since the last financial update",
            "what changed since our last reporting cycle",
            "what changed since the last reporting cycle",
            "what changed since the previous reporting cycle",
            "what changed since our previous reporting cycle",
            "compare the latest two financial snapshots",
            "compare our latest two financial snapshots",
            "compare the last two financial snapshots",
            "compare our last two financial snapshots",
            "historical financial change",
            "historical financial changes",
            "historical change summary",
            "financial change summary",
        )

        if any(
            phrase in cleaned_question
            for phrase in historical_change_summary_phrases
        ):
            return {
                "domain": "historical_change",
                "intent": "historical_change_summary",
                "target": "financial_intelligence_history",
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

        if any(phrase in cleaned_question for phrase in priority_action_phrases):
            return {
                "domain": "recommendation",
                "intent": "priority_actions",
                "target": "recommendations",
            }

        core_cost_coverage_summary_phrases = (
            "how much of our core costs are covered",
        )

        if any(
            phrase in cleaned_question
            for phrase in core_cost_coverage_summary_phrases
        ):
            return {
                "domain": "core_cost_coverage",
                "intent": "core_cost_coverage_summary",
                "target": "core_cost_coverage",
            }

        core_cost_gap_phrases = (
            "what is our remaining core cost gap",
        )

        if any(
            phrase in cleaned_question
            for phrase in core_cost_gap_phrases
        ):
            return {
                "domain": "core_cost_coverage",
                "intent": "core_cost_gap",
                "target": "core_cost_coverage",
            }

        indirect_recovery_status_phrases = (
            "what is the status of our indirect recovery",
        )

        if any(
            phrase in cleaned_question
            for phrase in indirect_recovery_status_phrases
        ):
            return {
                "domain": "core_cost_coverage",
                "intent": "indirect_recovery_status",
                "target": "core_cost_coverage",
            }

        core_cost_coverage_sources_phrases = (
            "what are the sources covering our core costs",
        )

        if any(
            phrase in cleaned_question
            for phrase in core_cost_coverage_sources_phrases
        ):
            return {
                "domain": "core_cost_coverage",
                "intent": "core_cost_coverage_sources",
                "target": "core_cost_coverage",
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

        if any(phrase in cleaned_question for phrase in funding_gap_action_phrases):
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

        if any(phrase in cleaned_question for phrase in finance_meeting_agenda_phrases):
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

        if any(phrase in cleaned_question for phrase in recommendation_summary_phrases):
            return {
                "domain": "recommendation",
                "intent": "recommendation_summary",
                "target": "recommendations",
            }

        if "action" in cleaned_question and (
            "priority" in cleaned_question
            or "urgent" in cleaned_question
            or "first" in cleaned_question
        ):
            return {
                "domain": "recommendation",
                "intent": "priority_actions",
                "target": "recommendations",
            }

        if "recommend" in cleaned_question or (
            "management" in cleaned_question and "do" in cleaned_question
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

        if any(phrase in cleaned_question for phrase in high_risk_phrases):
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

        # ==================================================
        # FINANCIAL OPPORTUNITY INTELLIGENCE
        # ==================================================

        # ------------------------------------------
        # Funding opportunities
        # ------------------------------------------

        if "opportunit" in cleaned_question and (
            "funding" in cleaned_question
            or "fund" in cleaned_question
            or "grant" in cleaned_question
        ):
            return {
                "domain": "financial_opportunity",
                "intent": "funding_opportunities",
                "target": "financial_opportunities",
            }

        # ------------------------------------------
        # Liquidity opportunities
        # ------------------------------------------

        if "opportunit" in cleaned_question and (
            "liquidity" in cleaned_question
            or "cash runway" in cleaned_question
            or "cash position" in cleaned_question
        ):
            return {
                "domain": "financial_opportunity",
                "intent": "liquidity_opportunities",
                "target": "financial_opportunities",
            }

        # ------------------------------------------
        # Highest-priority financial opportunities
        # ------------------------------------------

        if (
            "financial opportunity" in cleaned_question
            or "financial opportunities" in cleaned_question
            or "opportunity" in cleaned_question
            or "opportunities" in cleaned_question
        ) and (
            "highest" in cleaned_question
            or "high priority" in cleaned_question
            or "high-priority" in cleaned_question
            or "most important" in cleaned_question
            or "best" in cleaned_question
            or "priority" in cleaned_question
        ):
            return {
                "domain": "financial_opportunity",
                "intent": "high_financial_opportunities",
                "target": "financial_opportunities",
            }

        # ------------------------------------------
        # Overall financial opportunity summary
        # ------------------------------------------

        if (
            "financial opportunity" in cleaned_question
            or "financial opportunities" in cleaned_question
            or "what opportunities do we have" in cleaned_question
            or "what opportunities are available" in cleaned_question
        ):
            return {
                "domain": "financial_opportunity",
                "intent": "financial_opportunity_summary",
                "target": "financial_opportunities",
            }

        # ==================================================
        # FORWARD-LOOKING RISK INTELLIGENCE
        # ==================================================

        # ------------------------------------------
        # Forward funding risks
        # ------------------------------------------

        if (
            "future" in cleaned_question
            or "forward" in cleaned_question
            or "emerging" in cleaned_question
        ) and (
            "funding risk" in cleaned_question
            or "funding risks" in cleaned_question
            or "fund risk" in cleaned_question
            or "fund risks" in cleaned_question
            or "grant risk" in cleaned_question
            or "grant risks" in cleaned_question
        ):
            return {
                "domain": "risk",
                "intent": "forward_funding_risks",
                "target": "forward_risks",
            }

        # ------------------------------------------
        # Forward operating risks
        # ------------------------------------------

        if (
            "future" in cleaned_question
            or "forward" in cleaned_question
            or "emerging" in cleaned_question
        ) and (
            "operating risk" in cleaned_question
            or "operating risks" in cleaned_question
            or "operational risk" in cleaned_question
            or "operational risks" in cleaned_question
            or "performance risk" in cleaned_question
            or "performance risks" in cleaned_question
        ):
            return {
                "domain": "risk",
                "intent": "forward_operating_risks",
                "target": "forward_risks",
            }

        # ------------------------------------------
        # High / significant forward risks
        # ------------------------------------------

        if (
            "future risk" in cleaned_question
            or "future risks" in cleaned_question
            or "forward risk" in cleaned_question
            or "forward risks" in cleaned_question
            or "emerging risk" in cleaned_question
            or "emerging risks" in cleaned_question
        ) and (
            "worry" in cleaned_question
            or "most important" in cleaned_question
            or "most significant" in cleaned_question
            or "highest" in cleaned_question
            or "high risk" in cleaned_question
            or "high risks" in cleaned_question
        ):
            return {
                "domain": "risk",
                "intent": "forward_high_risks",
                "target": "forward_risks",
            }

        # ------------------------------------------
        # Overall forward-risk summary
        # ------------------------------------------

        if (
            "what risks are emerging" in cleaned_question
            or "what risk is emerging" in cleaned_question
            or "future risks" in cleaned_question
            or "future risk" in cleaned_question
            or "forward risks" in cleaned_question
            or "forward risk" in cleaned_question
            or "emerging risks" in cleaned_question
            or "emerging risk" in cleaned_question
        ):
            return {
                "domain": "risk",
                "intent": "forward_risk_summary",
                "target": "forward_risks",
            }

        if any(phrase in cleaned_question for phrase in risk_summary_phrases):
            return {
                "domain": "risk",
                "intent": "risk_summary",
                "target": "risks",
            }

        if (
            "which financial risk needs immediate attention" in cleaned_question
            or "which risk needs immediate attention" in cleaned_question
            or "what financial risk needs immediate attention" in cleaned_question
            or "what risk needs immediate attention" in cleaned_question
            or "most urgent financial risk" in cleaned_question
            or "most urgent risk" in cleaned_question
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

        if "risk" in cleaned_question and (
            "warning" in cleaned_question
            or "serious" in cleaned_question
            or "critical" in cleaned_question
            or "high" in cleaned_question
        ):
            return {
                "domain": "risk",
                "intent": "high_risks",
                "target": "risks",
            }

        if "risk" in cleaned_question and (
            "main" in cleaned_question
            or "biggest" in cleaned_question
            or "top" in cleaned_question
            or "summary" in cleaned_question
            or "worry" in cleaned_question
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
            or ("financial position" in cleaned_question and "weak" in cleaned_question)
            or (
                "financial health" in cleaned_question and "hurting" in cleaned_question
            )
            or (
                "financial health" in cleaned_question
                and "affecting" in cleaned_question
            )
            or ("health score" in cleaned_question and "driving" in cleaned_question)
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
                and ("improve" in cleaned_question or "focus" in cleaned_question)
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
            or "how many months can we operate" in cleaned_question
        ):
            return {
                "domain": "liquidity",
                "intent": "cash_runway",
                "target": "cash_runway_months",
            }

        if (
            "blocked cash" in cleaned_question
            or "restricted cash" in cleaned_question
            or "how much cash is blocked" in cleaned_question
            or "how much cash is restricted" in cleaned_question
            or "how much of our cash is blocked" in cleaned_question
            or "how much of our cash is restricted" in cleaned_question
            or (
                "cash" in cleaned_question
                and ("blocked" in cleaned_question or "restricted" in cleaned_question)
            )
        ):
            return {
                "domain": "cash",
                "intent": "blocked_cash",
                "target": "blocked_cash",
            }

        if (
            "how much cash do we have" in cleaned_question
            or "how much cash do we currently have" in cleaned_question
            or "what is our cash position" in cleaned_question
            or "what is our cash balance" in cleaned_question
            or "how much cash is available" in cleaned_question
            or "how much available cash do we have" in cleaned_question
            or "available cash" in cleaned_question
            or "cash position" in cleaned_question
            or ("cash" in cleaned_question and "available" in cleaned_question)
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
            or "is our liquidity healthy" in cleaned_question
            or "how healthy is our liquidity" in cleaned_question
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
            or "cash comes from operations" in cleaned_question
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

        budget_dimension_drilldown_phrases = (
            "why is",
            "what is causing",
            "what is driving",
            "show me the budget breakdown",
            "which programs are driving",
            "show me the budget lines behind",
        )

        generic_named_budget_subject = (
            (
                cleaned_question.startswith("why is ")
                and " over budget" in cleaned_question
            )
            or cleaned_question.startswith("what is driving the variance in ")
        ) and ("portfolio" not in cleaned_question)

        budget_dimension_context = (
            "fund" in cleaned_question
            or "program" in cleaned_question
            or "donor" in cleaned_question
            or "category" in cleaned_question
            or "budget line" in cleaned_question
            or generic_named_budget_subject
        )

        if (
            budget_dimension_context
            and any(
                phrase in cleaned_question
                for phrase in budget_dimension_drilldown_phrases
            )
            and (
                "budget" in cleaned_question
                or "variance" in cleaned_question
                or "over budget" in cleaned_question
            )
        ):
            return {
                "domain": "budget",
                "intent": "budget_dimension_drilldown",
                "target": "dimension_drilldown",
            }

        if (
            "unbudgeted expenditure" in cleaned_question
            or "unbudgeted spending" in cleaned_question
            or "unbudgeted actual" in cleaned_question
            or "unbudgeted actual spending" in cleaned_question
            or "unbudgeted actuals" in cleaned_question
            or "spending without budget" in cleaned_question
            or "spending without a budget" in cleaned_question
            or "actuals without budget" in cleaned_question
            or "actuals without a budget" in cleaned_question
            or "actual spending without budget" in cleaned_question
            or "actual spending without a budget" in cleaned_question
            or "how much have we spent without a budget" in cleaned_question
            or "how much spending do we have without a budget" in cleaned_question
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
            or "how many budget lines are over" in cleaned_question
            or "how many budget lines have exceeded their budgets" in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "over_budget_count",
                "target": "over_budget_count",
            }

        if (
            "which areas are over budget" in cleaned_question
            or "which areas are currently over budget" in cleaned_question
            or "where are we over budget" in cleaned_question
            or "where are we currently over budget" in cleaned_question
            or "which budget areas are over budget" in cleaned_question
            or "where do we still have available budget" in cleaned_question
            or "where do we have available budget" in cleaned_question
            or "where is budget still available" in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "portfolio_budget_summary",
                "target": "portfolio_control",
            }

        if (
            "which budget lines need management attention" in cleaned_question
            or "which budget lines need attention" in cleaned_question
            or "budget lines needing management attention" in cleaned_question
            or "budget lines requiring management attention" in cleaned_question
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
            or "how much budget have we used" in cleaned_question
            or "how much budget has been used" in cleaned_question
            or "what percentage of our budget have we spent" in cleaned_question
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
            "how much budget do we have left" in cleaned_question
            or "how much budget is left" in cleaned_question
            or "how much budget remains" in cleaned_question
            or "how much budget is remaining" in cleaned_question
            or "do we still have budget remaining" in cleaned_question
            or "is there any budget left" in cleaned_question
            or "do we have any budget left" in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "portfolio_budget_remaining",
                "target": ("overall_variance_including_unbudgeted"),
            }

        # ---------------------------------
        # Overall budget position
        #
        # Whether total portfolio spending
        # is above or below total budget.
        # ---------------------------------
        if (
            "why is our portfolio over budget" in cleaned_question
            or "why is the portfolio over budget" in cleaned_question
            or "why are we over budget overall" in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "portfolio_budget_position",
                "target": ("overall_variance_including_unbudgeted"),
            }

        if (
            "how much are we over budget" in cleaned_question
            or "how much are we over our budget" in cleaned_question
            or "how much over budget are we" in cleaned_question
            or "how far over budget are we" in cleaned_question
            or "are we spending more than we budgeted" in cleaned_question
            or "are we spending more than budgeted" in cleaned_question
            or "are we spending less than we budgeted" in cleaned_question
            or "are we spending less than budgeted" in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "portfolio_budget_position",
                "target": ("overall_variance_including_unbudgeted"),
            }

        if (
            "how is our budget performing" in cleaned_question
            or "how is the budget performing" in cleaned_question
            or "budget performance overall" in cleaned_question
            or "overall budget performance" in cleaned_question
            or "overall budget position" in cleaned_question
            or "how are we doing against budget" in cleaned_question
            or "are we overspending against our budget" in cleaned_question
            or "are we overspending against budget" in cleaned_question
            or "are we over budget" in cleaned_question
            or "are we currently over budget" in cleaned_question
            or "are we over our budget" in cleaned_question
            or "are we currently over our budget" in cleaned_question
            or "are we under budget" in cleaned_question
            or "are we under our budget" in cleaned_question
            or "main budget control issues" in cleaned_question
            or "what are the main budget control issues" in cleaned_question
            or "budget control issues" in cleaned_question
            or "budget control problems" in cleaned_question
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
            or "compare our budget to actual spending" in cleaned_question
            or "compare budget to actual spending" in cleaned_question
            or "compare our budget to actual" in cleaned_question
            or "compare budget to actual" in cleaned_question
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
            "main drivers of our financial performance" in cleaned_question
            or "main drivers of financial performance" in cleaned_question
            or "drivers of our financial performance" in cleaned_question
            or "drivers of financial performance" in cleaned_question
            or "what is driving our financial performance" in cleaned_question
            or "what is driving financial performance" in cleaned_question
        ):
            return {
                "domain": "financial_health",
                "intent": "financial_health_explanation",
                "target": "financial_health",
            }

        if (
            "is our current operating performance sustainable" in cleaned_question
            or "is our operating performance sustainable" in cleaned_question
            or "is our financial performance sustainable" in cleaned_question
            or "is this financial performance sustainable" in cleaned_question
            or "operating performance sustainable" in cleaned_question
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
            or "how should management improve financial performance" in cleaned_question
            or "how can management improve financial performance" in cleaned_question
            or "what actions should management take to improve financial performance"
            in cleaned_question
        ):
            return {
                "domain": "recommendation",
                "intent": "recommendation_summary",
                "target": "recommendations",
            }

        # ================================
        # FINANCIAL SCENARIO INTELLIGENCE
        # ================================

        scenario_language = (
            "what happens if" in cleaned_question
            or "what if" in cleaned_question
            or "scenario" in cleaned_question
            or "simulate" in cleaned_question
            or "simulation" in cleaned_question
        )

        saved_scenario_language = (
            "saved scenario" in cleaned_question
            or "saved scenarios" in cleaned_question
            or "scenarios have i saved" in cleaned_question
        )

        saved_scenario_comparison_language = (
            saved_scenario_language
            and (
                "compare" in cleaned_question
                or "which" in cleaned_question
                and (
                    "safer" in cleaned_question
                    or "better" in cleaned_question
                    or "prefer" in cleaned_question
                )
            )
        )

        if saved_scenario_comparison_language:
            return {
                "domain": "financial_scenario",
                "intent": "saved_scenario_comparison",
                "target": "scenario_history",
            }

        if saved_scenario_language:
            return {
                "domain": "financial_scenario",
                "intent": "saved_scenario_list",
                "target": "scenario_history",
            }        

        scenario_comparison_language = (
            "compare scenario" in cleaned_question
            or "compare scenarios" in cleaned_question
            or "compare these two financial scenarios" in cleaned_question
            or "which scenario is better" in cleaned_question
            or "which scenario is safer" in cleaned_question
            or "which scenario should" in cleaned_question
            or (
                "which of these scenarios" in cleaned_question
                and "prefer" in cleaned_question
            )
        )

        if scenario_comparison_language:
            return {
                "domain": "financial_scenario",
                "intent": "scenario_comparison",
                "target": "scenario_comparison",
            }        

        expected_funding_language = (
            "expected funding" in cleaned_question
            or "expected grant" in cleaned_question
            or "expected grants" in cleaned_question
            or "prospective funding" in cleaned_question
        )

        if (
            scenario_language
            and expected_funding_language
            and (
                "does not materialize" in cleaned_question
                or "doesn't materialize" in cleaned_question
                or "fails" in cleaned_question
                or "fail" in cleaned_question
                or "lost" in cleaned_question
                or "not materialize" in cleaned_question
            )
        ):
            return {
                "domain": "funding_scenario",
                "intent": "expected_funding_failure_scenario",
                "target": "expected_funding",
            }

        if (
            scenario_language
            and expected_funding_language
            and (
                "minimum" in cleaned_question
                or "most likely" in cleaned_question
                or "maximum" in cleaned_question
                or "probability weighted" in cleaned_question
                or "probability-weighted" in cleaned_question
            )
        ):
            return {
                "domain": "funding_scenario",
                "intent": "expected_funding_basis_scenario",
                "target": "expected_funding",
            }

        if (
            scenario_language
            and expected_funding_language
        ):
            return {
                "domain": "funding_scenario",
                "intent": "expected_funding_change_scenario",
                "target": "expected_funding",
            }        

        if (
            scenario_language
            and (
                "revenue" in cleaned_question
                or "income" in cleaned_question
            )
            and (
                "expense" in cleaned_question
                or "expenses" in cleaned_question
                or "cost" in cleaned_question
                or "costs" in cleaned_question
            )
        ):
            return {
                "domain": "financial_scenario",
                "intent": "combined_scenario",
                "target": "financial_performance",
            }

        if scenario_language and (
            "revenue" in cleaned_question or "income" in cleaned_question
        ):
            return {
                "domain": "financial_scenario",
                "intent": "revenue_scenario",
                "target": "revenue",
            }        

        if scenario_language and (
            "expense" in cleaned_question
            or "expenses" in cleaned_question
            or "cost" in cleaned_question
            or "costs" in cleaned_question
        ):
            return {
                "domain": "financial_scenario",
                "intent": "expense_scenario",
                "target": "expenses",
            }

        if scenario_language:
            return {
                "domain": "financial_scenario",
                "intent": "financial_scenario_summary",
                "target": "financial_performance",
            }


        # ================================
        # FINANCIAL FORECAST INTELLIGENCE
        # ================================

        if ("revenue" in cleaned_question or "income" in cleaned_question) and (
            "forecast" in cleaned_question
            or "projected" in cleaned_question
            or "projection" in cleaned_question
            or "expected" in cleaned_question
            or "next month" in cleaned_question
            or "next 3 months" in cleaned_question
            or "next three months" in cleaned_question
            or "will our revenue" in cleaned_question
        ):
            return {
                "domain": "financial_forecast",
                "intent": "revenue_forecast",
                "target": "revenue",
            }

        if (
            "expense" in cleaned_question
            or "expenses" in cleaned_question
            or "cost" in cleaned_question
            or "costs" in cleaned_question
        ) and (
            "forecast" in cleaned_question
            or "projected" in cleaned_question
            or "projection" in cleaned_question
            or "expected" in cleaned_question
            or "next month" in cleaned_question
            or "next 3 months" in cleaned_question
            or "next three months" in cleaned_question
            or "will our expenses" in cleaned_question
        ):
            return {
                "domain": "financial_forecast",
                "intent": "expense_forecast",
                "target": "expenses",
            }

        if (
            "net result" in cleaned_question
            or "net profit" in cleaned_question
            or "surplus" in cleaned_question
            or "deficit" in cleaned_question
        ) and (
            "forecast" in cleaned_question
            or "projected" in cleaned_question
            or "projection" in cleaned_question
            or "expected" in cleaned_question
            or "next month" in cleaned_question
            or "next 3 months" in cleaned_question
            or "next three months" in cleaned_question
            or "will our net result" in cleaned_question
        ):
            return {
                "domain": "financial_forecast",
                "intent": "net_result_forecast",
                "target": "net_result",
            }

        if (
            "financial forecast" in cleaned_question
            or "financial projection" in cleaned_question
            or "finances forecast" in cleaned_question
            or "finances projected" in cleaned_question
            or "financial outlook" in cleaned_question
            or "future financial position" in cleaned_question
            or "what do our finances look like next" in cleaned_question
        ):
            return {
                "domain": "financial_forecast",
                "intent": "financial_forecast_summary",
                "target": "financial_performance",
            }

        # =================================
        # FINANCIAL TREND INTELLIGENCE
        # =================================

        if ("revenue" in cleaned_question or "income" in cleaned_question) and (
            "trend" in cleaned_question
            or "trending" in cleaned_question
            or "increasing" in cleaned_question
            or "decreasing" in cleaned_question
            or "increased" in cleaned_question
            or "decreased" in cleaned_question
            or "changed" in cleaned_question
            or "change over time" in cleaned_question
        ):
            return {
                "domain": "financial_trends",
                "intent": "revenue_trend",
                "target": "revenue",
            }

        if (
            "expense" in cleaned_question
            or "expenses" in cleaned_question
            or "operating cost" in cleaned_question
            or "operating costs" in cleaned_question
        ) and (
            "trend" in cleaned_question
            or "trending" in cleaned_question
            or "increasing" in cleaned_question
            or "decreasing" in cleaned_question
            or "increased" in cleaned_question
            or "decreased" in cleaned_question
            or "rising" in cleaned_question
            or "falling" in cleaned_question
            or "changed" in cleaned_question
        ):
            return {
                "domain": "financial_trends",
                "intent": "expense_trend",
                "target": "expenses",
            }

        if (
            "net result" in cleaned_question
            or "net profit" in cleaned_question
            or "surplus" in cleaned_question
            or "deficit" in cleaned_question
        ) and (
            "trend" in cleaned_question
            or "trending" in cleaned_question
            or "increasing" in cleaned_question
            or "decreasing" in cleaned_question
            or "improving" in cleaned_question
            or "worsening" in cleaned_question
            or "changed" in cleaned_question
            or "change" in cleaned_question
        ):
            return {
                "domain": "financial_trends",
                "intent": "net_result_trend",
                "target": "net_result",
            }

        if (
            "financial trend" in cleaned_question
            or "financial trends" in cleaned_question
            or "finances trending" in cleaned_question
            or "financial performance changed over time" in cleaned_question
        ):
            return {
                "domain": "financial_trends",
                "intent": "financial_trend_summary",
                "target": "financial_performance",
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

        if "expense" in cleaned_question or "expenses" in cleaned_question:
            return {
                "domain": "financial",
                "intent": "expenses",
                "target": "expenses",
            }

        if (
            "net profit" in cleaned_question
            or "net result" in cleaned_question
            or (
                "profit" in cleaned_question
                and "nonprofit" not in cleaned_question
                and "non-profit" not in cleaned_question
            )
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
        # PERIOD / DATA QUALITY
        # =================================

        if (
            "what period" in cleaned_question
            or "data period" in cleaned_question
            or "period does" in cleaned_question
            or "date range" in cleaned_question
            or "data range" in cleaned_question
        ):
            return {
                "domain": "data_quality",
                "intent": "data_period",
                "target": "posting_dates",
            }

        if (
            "latest transaction date" in cleaned_question
            or "latest posting date" in cleaned_question
            or "most recent transaction date" in cleaned_question
            or "most recent posting date" in cleaned_question
        ):
            return {
                "domain": "data_quality",
                "intent": "latest_transaction_date",
                "target": "latest_posting_date",
            }

        if (
            "earliest transaction date" in cleaned_question
            or "earliest posting date" in cleaned_question
            or "oldest transaction date" in cleaned_question
            or "oldest posting date" in cleaned_question
        ):
            return {
                "domain": "data_quality",
                "intent": "earliest_transaction_date",
                "target": "earliest_posting_date",
            }

        if (
            "reporting date" in cleaned_question
            or "current reporting date" in cleaned_question
        ):
            return {
                "domain": "data_quality",
                "intent": "reporting_date",
                "target": "reporting_date",
            }

        if (
            "date quality" in cleaned_question
            or "date issues" in cleaned_question
            or "posting date issues" in cleaned_question
            or "invalid dates" in cleaned_question
            or "missing dates" in cleaned_question
        ):
            return {
                "domain": "data_quality",
                "intent": "date_quality",
                "target": "date_quality",
            }

        if (
            "future transaction" in cleaned_question
            or "future dated transaction" in cleaned_question
            or "future-dated transaction" in cleaned_question
        ):
            return {
                "domain": "data_quality",
                "intent": "future_transactions",
                "target": "future_transactions",
            }

        # =================================
        # ORGANIZATION KNOWLEDGE
        # =================================

        if (
            "organization summary" in cleaned_question
            or "organisation summary" in cleaned_question
            or "tell me about our organization" in cleaned_question
            or "tell me about our organisation" in cleaned_question
        ):
            return {
                "domain": "organization",
                "intent": "organization_summary",
                "target": "organization",
            }

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




