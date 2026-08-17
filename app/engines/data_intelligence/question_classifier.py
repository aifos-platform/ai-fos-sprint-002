from typing import Any


class QuestionClassifier:
    """
    Classifies AI-FOS user questions into
    structured intents and domains.
    """

    def classify(
        self,
        question: str,
    ) -> dict[str, Any]:

        cleaned_question = (
            question
            .strip()
            .lower()
        )

        # ---------------------------------
        # Budget Intelligence
        # ---------------------------------

        if (
            "budget variance" in cleaned_question
            or "variance against budget" in cleaned_question
            or "variance to budget" in cleaned_question
            or "how much are we over budget" in cleaned_question
            or "how much are we over our budget" in cleaned_question
            or "how much over budget are we" in cleaned_question
            or "how far over budget are we" in cleaned_question
            or "are we spending more than we budgeted" in cleaned_question
            or "are we spending more than budgeted" in cleaned_question
            or "are we spending less than we budgeted" in cleaned_question
            or "are we spending less than budgeted" in cleaned_question
            or "how much budget do we have left" in cleaned_question
            or "do we still have budget remaining" in cleaned_question
            or "is there any budget left" in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "portfolio_budget_variance",
                "target": "total_variance",
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

        if (
            "unbudgeted expenditure" in cleaned_question
            or "unbudgeted spending" in cleaned_question
            or "unbudgeted actual" in cleaned_question
            or "unbudgeted actual spending" in cleaned_question
            or "unbudgeted actuals" in cleaned_question
            or "spending without budget" in cleaned_question
            or "spending without a budget" in cleaned_question
            or "actuals without budget" in cleaned_question
            or "spending do we have without a budget" in cleaned_question
            or "actuals without a budget" in cleaned_question
            or "actual spending without budget" in cleaned_question
            or "actual spending without a budget" in cleaned_question
            or "how much have we spent without a budget" in cleaned_question
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
            or "how many budget lines" in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "over_budget_count",
                "target": "over_budget_count",
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
            or "are we over our budget" in cleaned_question
            or "are we under budget" in cleaned_question
            or "are we under our budget" in cleaned_question
        ):
            return {
                "domain": "budget",
                "intent": "budget_performance_summary",
                "target": "budget_dashboard",
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

        if (
            "budget actual" in cleaned_question
            or "budget vs actual" in cleaned_question
            or "budget versus actual" in cleaned_question
            or "budget performance" in cleaned_question
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

        # ---------------------------------
        # Organization Knowledge
        # ---------------------------------

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
            "fund" in cleaned_question
            or "grant" in cleaned_question
        ):
            return {
                "domain": "organization",
                "intent": "fund_count",
                "target": "funds",
            }

        # ---------------------------------
        # Financial Facts
        # ---------------------------------

        if "revenue" in cleaned_question:
            return {
                "domain": "financial",
                "intent": "revenue",
                "target": "revenue",
            }

        if "expense" in cleaned_question:
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

        # ---------------------------------
        # Financial Health
        # ---------------------------------

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

        # ---------------------------------
        # Cash Position
        # ---------------------------------

        if (
            "how much cash do we have" in cleaned_question
            or "what is our cash position" in cleaned_question
            or "what is our cash balance" in cleaned_question
            or "how much cash is available" in cleaned_question
            or "how much available cash do we have" in cleaned_question
            or "available cash" in cleaned_question
            or "cash position" in cleaned_question
        ):
            return {
                "domain": "cash",
                "intent": "cash_position",
                "target": "cash_position",
            }


        # ---------------------------------
        # Cash Flow
        # ---------------------------------

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

        # ---------------------------------
        # Recommendation Intelligence
        # ---------------------------------

        if (
            "what should management do" in cleaned_question
            or "what should we do" in cleaned_question
            or "what do you recommend" in cleaned_question
            or "recommendation" in cleaned_question
            or "how can we improve" in cleaned_question
            or "improve our financial position" in cleaned_question
        ):
            return {
                "domain": "recommendation",
                "intent": "recommendation_summary",
                "target": "recommendations",
            }

        if (
            "what should we prioritize" in cleaned_question
            or "what should management prioritize" in cleaned_question
            or "priority actions" in cleaned_question
            or "top actions" in cleaned_question
            or "highest priority" in cleaned_question
        ):
            return {
                "domain": "recommendation",
                "intent": "priority_actions",
                "target": "recommendations",
            }

        # ---------------------------------
        # Risk Intelligence
        # ---------------------------------

        if (
            "biggest financial risk" in cleaned_question
            or "biggest risk" in cleaned_question
            or "financial risks" in cleaned_question
            or "main risks" in cleaned_question
            or "what should management worry about" in cleaned_question
            or "what should we worry about" in cleaned_question
        ):
            return {
                "domain": "risk",
                "intent": "risk_summary",
                "target": "risks",
            }

        if (
            "high risk" in cleaned_question
            or "high-risk" in cleaned_question
            or "high severity risk" in cleaned_question
            or "high-severity risk" in cleaned_question
        ):
            return {
                "domain": "risk",
                "intent": "high_risks",
                "target": "risks",
            }

        # ---------------------------------
        # Default
        # ---------------------------------

        return {
            "domain": "organization",
            "intent": "organization_summary",
            "target": "summary",
        }