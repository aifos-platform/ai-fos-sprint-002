def generate_financial_facts(income_statement, balance_sheet):
    return {
        "revenue": income_statement["revenue"],
        "expenses": income_statement["expenses"],
        "net_profit": income_statement["net_profit"],
        "assets": balance_sheet["assets"],
        "liabilities": balance_sheet["liabilities"],
        "equity": balance_sheet["equity"],
        "difference": balance_sheet["difference"],
    }