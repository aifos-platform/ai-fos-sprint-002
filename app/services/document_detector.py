def detect_document_type(headers):
    normalised_headers = [str(header).strip().lower() for header in headers]

    print(normalised_headers)

    chart_keywords = {
        "no.",
        "name",
        "income/balance",
        "account category",
        "account subcategory",
    }

    if chart_keywords.issubset(normalised_headers):
        return "chart_of_accounts"

    gl_keywords = {
        "posting date",
        "g/l account no.",
        "debit amount (lcy)",
        "credit amount (lcy)",
    }

    if gl_keywords.issubset(normalised_headers):
        return "general_ledger"

    budget_signals = {
        "budget line code",
        "budget line code name",
        "budget notes",
        "total original budget (usd)",
    }

    matched_budget_signals = sum(
        signal in normalised_headers for signal in budget_signals
    )

    if matched_budget_signals >= 3:
        return "budget"

    return "unknown"
