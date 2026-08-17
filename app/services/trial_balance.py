def generate_trial_balance(transactions):
    trial_balance = {}

    for transaction in transactions:
            account_number = transaction.get("account")

            if account_number not in trial_balance:
                trial_balance[account_number] = {
                    "account_name": transaction.get("account_name"),
                    "total_debit": 0,
                    "total_credit": 0,
                }
            debit = transaction.get("debit", 0)
            credit = transaction.get("credit", 0)   

            trial_balance[account_number]["total_debit"] += debit
            trial_balance[account_number]["total_credit"] += credit 


    return trial_balance