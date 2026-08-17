from typing import Any


class FinancialIntelligenceService:
    """
    Provides financial facts, cash-flow intelligence,
    and financial-health information to AI-FOS.
    """

    FINANCIAL_FACT_KEYS = {
        "revenue",
        "expenses",
        "net_profit",
        "assets",
        "liabilities",
        "equity",
        "difference",
    }

    CASH_FLOW_KEYS = {
        "operating_cash_flow": "operating_activities",
        "investing_cash_flow": "investing_activities",
        "financing_cash_flow": "financing_activities",
        "net_change_in_cash": "net_change_in_cash",
    }

    def get_financial_facts(
        self,
        financial_facts: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "revenue": financial_facts.get("revenue", 0),
            "expenses": financial_facts.get("expenses", 0),
            "net_profit": financial_facts.get("net_profit", 0),
            "assets": financial_facts.get("assets", 0),
            "liabilities": financial_facts.get("liabilities", 0),
            "equity": financial_facts.get("equity", 0),
            "difference": financial_facts.get("difference", 0),
        }

    def get_value(
        self,
        intent: str,
        financial_facts: dict[str, Any],
    ) -> Any:

        facts = self.get_financial_facts(
            financial_facts
        )

        return facts.get(intent)

    def get_cash_flow_value(
        self,
        intent: str,
        cash_flow: dict[str, Any],
    ) -> Any:

        source_key = self.CASH_FLOW_KEYS.get(intent)

        if source_key is None:
            return None

        return cash_flow.get(
            source_key,
            0,
        )

    def get_health_score(
        self,
        financial_health: dict[str, Any],
    ) -> Any:

        return financial_health.get(
            "score"
        )

    def get_health_rating(
        self,
        financial_health: dict[str, Any],
    ) -> str | None:

        rating = financial_health.get(
            "rating"
        )

        if rating is None:
            return None

        return str(rating)

    def get_health_summary(
        self,
        financial_health: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "score": financial_health.get("score"),
            "maximum": financial_health.get(
                "maximum",
                100,
            ),
            "rating": financial_health.get("rating"),
            "categories": financial_health.get(
                "categories",
                {},
            ),
        }