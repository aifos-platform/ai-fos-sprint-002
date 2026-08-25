import json
from typing import Any

from app.services.ai_prompt import build_cfo_prompt
from app.ai.providers.openai_provider import OpenAIProvider


def generate_ai_cfo_report(
    income_statement: dict[str, Any] | None,
    balance_sheet: dict[str, Any] | None,
    financial_facts: dict[str, Any] | None,
    cash_flow: dict[str, Any] | None,
    financial_health: dict[str, Any] | None,
    risk_assessment: list[dict[str, Any]] | None,
    cfo_recommendations: list[dict[str, Any]] | None,
    budget_dashboard: dict[str, Any] | None,
    funding_gap: dict[str, Any] | None,
    grant_count: int,
) -> dict[str, Any]:
    """
    Generate an AI-written CFO report from verified
    AI-FOS financial intelligence.
    """

    income_statement = income_statement or {}
    balance_sheet = balance_sheet or {}
    financial_facts = financial_facts or {}
    cash_flow = cash_flow or {}
    financial_health = financial_health or {}
    risk_assessment = risk_assessment or []
    cfo_recommendations = cfo_recommendations or []
    budget_dashboard = budget_dashboard or {}
    funding_gap = funding_gap or {}

    base_prompt = build_cfo_prompt(
        income_statement=income_statement,
        balance_sheet=balance_sheet,
        financial_facts=financial_facts,
        budget_dashboard=budget_dashboard,
        grant_count=grant_count,
    )

    verified_intelligence = {
        "cash_flow": cash_flow,
        "financial_health": financial_health,
        "risk_assessment": risk_assessment,
        "cfo_recommendations": cfo_recommendations,
        "funding_gap": funding_gap,
    }

    prompt = (
        f"{base_prompt}\n\n"
        "Additional verified AI-FOS intelligence:\n"
        f"{json.dumps(verified_intelligence, indent=2, default=str)}"
    )

    provider = OpenAIProvider()

    report = provider.generate_text(
        instructions=(
            "You are the AI-FOS Digital CFO. "
            "Use only the supplied verified financial data, "
            "risk assessment, recommendations, and funding gap analysis. "
            "Do not invent figures, causes, risks, or explanations. "
            "Clearly distinguish facts from management advice. "
            "Treat secured funding without Budget-Line allocation as "
            "restricted or unverified for automatic funding-gap coverage "
            "unless the supplied data explicitly establishes eligibility. "
            "Prioritize material issues and explain recommendations "
            "in professional CFO language."
        ),
        user_input=prompt,
    )

    return {
        "status": "completed",
        "report": report,
        "input_summary": {
            "income_statement_available": bool(income_statement),
            "balance_sheet_available": bool(balance_sheet),
            "financial_facts_available": bool(financial_facts),
            "cash_flow_available": bool(cash_flow),
            "financial_health_available": bool(financial_health),
            "risk_count": len(risk_assessment),
            "recommendation_count": len(cfo_recommendations),
            "budget_dashboard_available": bool(budget_dashboard),
            "funding_gap_available": bool(funding_gap),
            "grant_count": grant_count,
        },
    }