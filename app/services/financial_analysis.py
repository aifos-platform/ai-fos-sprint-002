def analyze_financials(income_statement, balance_sheet):
    findings = []

    net_profit = income_statement["net_profit"]
    revenue = income_statement["revenue"]
    expenses = income_statement["expenses"]

    if net_profit > 0:
        findings.append(
            f"The organisation generated a net profit of {net_profit:,.2f} during the selected period."
        )
    elif net_profit < 0:
        findings.append(
            f"The organisation generated a net loss of {abs(net_profit):,.2f} during the selected period."
        )
    else:
        findings.append(
            "The organisation broke even during the selected period."
        )

    if income_statement["expenses"] > income_statement["revenue"]:
        findings.append(
            f"Expenses exceeded revenue by {expenses - revenue:,.2f}."
    )

    if balance_sheet["difference"] != 0:
        findings.append(
            "The Balance Sheet is not balanced because the current year's profit or loss has not yet been transferred to Equity."
        )

    return {
        "summary": findings[0],
        "findings": findings,
    }