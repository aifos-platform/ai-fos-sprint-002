from typing import Any


def build_cfo_prompt(
    income_statement: dict[str, Any],
    balance_sheet: dict[str, Any],
    financial_facts: dict[str, Any],
    budget_dashboard: dict[str, Any],
    grant_count: int,
) -> str:
    """
    Build the prompt sent to the AI CFO.
    """

    return f"""
You are an experienced Chief Financial Officer working for an international nonprofit organisation.

Below is the organisation's verified financial information.

Income Statement:
{income_statement}

Balance Sheet:
{balance_sheet}

Financial Facts:
{financial_facts}

Budget Dashboard:
{budget_dashboard}

Number of Grants:
{grant_count}

IMPORTANT BUDGET INTERPRETATION RULES:

- For organisation-wide portfolio budget conclusions, use the
  "portfolio_control" section of the Budget Dashboard as the
  authoritative source.

- Do not substitute annual, fiscal-year, or other period-specific
  budget figures for portfolio-level figures.

- Clearly distinguish portfolio-level conclusions from
  period-specific conclusions.

- Do not recalculate financial figures when an authoritative
  calculated value is already supplied.

Please produce:

1. Executive Summary
2. Financial Performance
3. Budget Analysis
4. Liquidity & Financial Position
5. Grant Portfolio Observations
6. Key Risks
7. CFO Recommendations

Write professionally.
Do not invent numbers.
Base your analysis only on the supplied data.
If the supplied data is insufficient to support a conclusion,
state that clearly rather than making an assumption.
"""