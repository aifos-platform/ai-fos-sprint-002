from app.services.gl_account_builder import GLAccountBuilder


def test_builds_unique_posting_accounts_from_general_ledger():
    builder = GLAccountBuilder()

    transactions = [
        {
            "account_number": "610001",
            "account_name": "Salaries",
        },
        {
            "account_number": "610001",
            "account_name": "Salaries",
        },
        {
            "account_number": "250001",
            "account_name": "Computer Equipment",
        },
    ]

    result = builder.build(transactions)

    assert len(result["accounts"]) == 2
    assert set(result["accounts_by_number"]) == {
        "610001",
        "250001",
    }

    for account in result["accounts"]:
        assert account["account_type"] == "Posting"
        assert account["is_posting_account"] is True


def test_skips_transactions_without_account_number():
    builder = GLAccountBuilder()

    transactions = [
        {
            "account_number": None,
            "account_name": "Missing Account",
        },
        {
            "account_number": "",
            "account_name": "Blank Account",
        },
        {
            "account_number": "610001",
            "account_name": "Salaries",
        },
    ]

    result = builder.build(transactions)

    assert len(result["accounts"]) == 1
    assert "610001" in result["accounts_by_number"]


def test_uses_existing_account_classifier():
    builder = GLAccountBuilder()

    transactions = [
        {
            "account_number": "250001",
            "account_name": "Computer Equipment",
        }
    ]

    result = builder.build(transactions)

    account = result["accounts_by_number"]["250001"]

    assert account["financial_category"] is not None
    assert "classification_confidence" in account
    assert "requires_review" in account
