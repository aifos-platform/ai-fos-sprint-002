from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class IntelligenceHub:
    """
    Builds the consolidated AI-FOS intelligence object.

    The Hub separates:
    1. Facts
    2. Intelligence
    3. Advice

    It does not perform financial calculations itself.
    It only consolidates verified outputs produced by
    the specialized AI-FOS engines.
    """

    VERSION = "1.0"

    def build(
        self,
        *,
        organisation_id: str,
        organisation_name: str,
        currency: str,
        financial_facts: dict[str, Any] | None,
        financial_analysis: dict[str, Any] | None,
        financial_health: dict[str, Any] | None,
        trial_balance: dict[str, Any] | None,
        income_statement: dict[str, Any] | None,
        balance_sheet: dict[str, Any] | None,
        cash_flow: dict[str, Any] | None,
        budget_dashboard: dict[str, Any] | None,
        grant_diagnostics: dict[str, Any] | None,
        risk_assessment: list[dict[str, Any]] | None,
        cfo_recommendations: list[dict[str, Any]] | None,
        kpi_dashboard: dict[str, Any] | None,
        executive_dashboard: dict[str, Any] | None,
    ) -> dict[str, Any]:

        generated_at = datetime.now(
            timezone.utc
        ).isoformat()

        return {
            "hub_version": self.VERSION,

            "generated_at": generated_at,

            "organisation": {
                "id": organisation_id,
                "name": organisation_name,
                "currency": currency,
            },

            # ---------------------------------
            # Layer 1 — Verified Facts
            # ---------------------------------

            "facts": {
                "financial_facts": (
                    financial_facts or {}
                ),
                "trial_balance": (
                    trial_balance or {}
                ),
                "income_statement": (
                    income_statement or {}
                ),
                "balance_sheet": (
                    balance_sheet or {}
                ),
                "cash_flow": (
                    cash_flow or {}
                ),
                "budget_dashboard": (
                    budget_dashboard or {}
                ),
                "grant_diagnostics": (
                    grant_diagnostics or {}
                ),
            },

            # ---------------------------------
            # Layer 2 — Deterministic Intelligence
            # ---------------------------------

            "intelligence": {
                "financial_analysis": (
                    financial_analysis or {}
                ),
                "financial_health": (
                    financial_health or {}
                ),
                "risk_assessment": (
                    risk_assessment or []
                ),
                "kpi_dashboard": (
                    kpi_dashboard or {}
                ),
                "executive_dashboard": (
                    executive_dashboard or {}
                ),
            },

            # ---------------------------------
            # Layer 3 — Advice
            # ---------------------------------

            "advice": {
                "cfo_recommendations": (
                    cfo_recommendations or []
                ),
            },

            # ---------------------------------
            # Hub Summary
            # ---------------------------------

            "summary": {
                "risk_count": len(
                    risk_assessment or []
                ),
                "high_risk_count": sum(
                    1
                    for risk in (
                        risk_assessment or []
                    )
                    if risk.get("severity") == "High"
                ),
                "recommendation_count": len(
                    cfo_recommendations or []
                ),
                "financial_health_score": (
                    (financial_health or {}).get(
                        "score"
                    )
                ),
                "financial_health_rating": (
                    (financial_health or {}).get(
                        "rating"
                    )
                ),
            },
        }