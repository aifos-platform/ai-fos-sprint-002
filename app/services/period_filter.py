from datetime import datetime


def filter_transactions(
    transactions,
    start_date=None,
    end_date=None,
):
    """
    Return only transactions within the requested period.
    """

    if start_date is None and end_date is None:
        end_date = datetime.now()

    filtered = []

    for transaction in transactions:
        value = transaction.get("transaction_date")

        if not value:
            continue

        transaction_date = datetime.fromisoformat(
            str(value)
        )

        if start_date and transaction_date < start_date:
            continue

        if end_date and transaction_date > end_date:
            continue

        filtered.append(transaction)

    return filtered