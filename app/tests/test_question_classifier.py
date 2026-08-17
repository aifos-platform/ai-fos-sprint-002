from app.engines.data_intelligence.question_classifier import QuestionClassifier


def run_tests() -> None:
    classifier = QuestionClassifier()

    test_cases = [
        # ---------------------------------
        # Budget Performance Summary
        # ---------------------------------
        (
            "How is our budget performing?",
            "budget",
            "budget_performance_summary",
        ),
        (
            "How is the budget performing?",
            "budget",
            "budget_performance_summary",
        ),
        (
            "How are we doing against budget?",
            "budget",
            "budget_performance_summary",
        ),
        (
            "Are we overspending against our budget?",
            "budget",
            "budget_performance_summary",
        ),
        (
            "Are we over budget?",
            "budget",
            "budget_performance_summary",
        ),
        (
            "Are we under budget?",
            "budget",
            "budget_performance_summary",
        ),
        (
            "What is our overall budget position?",
            "budget",
            "budget_performance_summary",
        ),

        # ---------------------------------
        # Budget Variance
        # ---------------------------------
        (
            "What is our budget variance?",
            "budget",
            "portfolio_budget_variance",
        ),
        (
            "What is our variance against budget?",
            "budget",
            "portfolio_budget_variance",
        ),
        (
            "How much are we over budget?",
            "budget",
            "portfolio_budget_variance",
        ),
        (
            "How much over budget are we?",
            "budget",
            "portfolio_budget_variance",
        ),
        (
            "How far over budget are we?",
            "budget",
            "portfolio_budget_variance",
        ),
        (
            "Are we spending more than we budgeted?",
            "budget",
            "portfolio_budget_variance",
        ),
        (
            "Are we spending less than we budgeted?",
            "budget",
            "portfolio_budget_variance",
        ),
        (
            "How much budget do we have left?",
            "budget",
            "portfolio_budget_variance",
        ),
        (
            "Do we still have budget remaining?",
            "budget",
            "portfolio_budget_variance",
        ),
        (
            "Is there any budget left?",
            "budget",
            "portfolio_budget_variance",
        ),

        # ---------------------------------
        # Budget Utilization
        # ---------------------------------
        (
            "What is our budget utilization?",
            "budget",
            "portfolio_budget_utilization",
        ),
        (
            "How much of our budget have we used?",
            "budget",
            "portfolio_budget_utilization",
        ),
        (
            "How much budget have we used?",
            "budget",
            "portfolio_budget_utilization",
        ),
        (
            "What percentage of our budget have we spent?",
            "budget",
            "portfolio_budget_utilization",
        ),

        # ---------------------------------
        # Unbudgeted Actual
        # ---------------------------------
        (
            "How much unbudgeted spending do we have?",
            "budget",
            "unbudgeted_actual",
        ),
        (
            "How much spending do we have without a budget?",
            "budget",
            "unbudgeted_actual",
        ),
        (
            "How much have we spent without a budget?",
            "budget",
            "unbudgeted_actual",
        ),
        (
            "What are our unbudgeted actuals?",
            "budget",
            "unbudgeted_actual",
        ),

        # ---------------------------------
        # Over Budget Count
        # ---------------------------------
        (
            "How many budget lines are over budget?",
            "budget",
            "over_budget_count",
        ),
        (
            "How many budget lines have exceeded their budgets?",
            "budget",
            "over_budget_count",
        ),
        (
            "How many over-budget lines do we have?",
            "budget",
            "over_budget_count",
        ),

        # ---------------------------------
        # Total Budget
        # ---------------------------------
        (
            "What is our total budget?",
            "budget",
            "portfolio_total_budget",
        ),
        (
            "What is our portfolio budget?",
            "budget",
            "portfolio_total_budget",
        ),
        (
            "What is our approved budget?",
            "budget",
            "portfolio_total_budget",
        ),

        # ---------------------------------
        # Budget vs Actual
        # ---------------------------------
        (
            "What is our budget vs actual?",
            "budget",
            "portfolio_budget_summary",
        ),
        (
            "Compare our budget to actual spending.",
            "budget",
            "portfolio_budget_summary",
        ),
        (
            "Compare budget to actual.",
            "budget",
            "portfolio_budget_summary",
        ),

        # ---------------------------------
        # Cash Position
        # ---------------------------------
        (
            "How much cash do we have?",
            "cash",
            "cash_position",
        ),
        (
            "What is our cash position?",
            "cash",
            "cash_position",
        ),
        (
            "What is our cash balance?",
            "cash",
            "cash_position",
        ),
        (
            "How much cash is available?",
            "cash",
            "cash_position",
        ),
        (
            "How much available cash do we have?",
            "cash",
            "cash_position",
        ),

        # ---------------------------------
        # Cash Flow
        # ---------------------------------
        (
            "What is our operating cash flow?",
            "cash_flow",
            "operating_cash_flow",
        ),
        (
            "How much cash comes from operations?",
            "cash_flow",
            "operating_cash_flow",
        ),
        (
            "What is our investing cash flow?",
            "cash_flow",
            "investing_cash_flow",
        ),
        (
            "What is our financing cash flow?",
            "cash_flow",
            "financing_cash_flow",
        ),
        (
            "What is the net change in cash?",
            "cash_flow",
            "net_change_in_cash",
        ),

        # ---------------------------------
        # Financial Health
        # ---------------------------------
        (
            "What is our financial health?",
            "financial_health",
            "financial_health",
        ),
        (
            "Are we financially healthy?",
            "financial_health",
            "financial_health",
        ),
        (
            "How healthy are our finances?",
            "financial_health",
            "financial_health",
        ),
        (
            "How healthy is our financial position?",
            "financial_health",
            "financial_health",
        ),

        # ---------------------------------
        # Core Financial Facts
        # ---------------------------------
        (
            "What is our net surplus?",
            "financial",
            "net_profit",
        ),
        (
            "What are our total expenses?",
            "financial",
            "expenses",
        ),

    ]

    passed = 0
    failed = 0

    print()
    print("=" * 72)
    print("AI-FOS QUESTION CLASSIFIER TEST SUITE")
    print("=" * 72)

    for index, (
        question,
        expected_domain,
        expected_intent,
    ) in enumerate(test_cases, start=1):

        result = classifier.classify(question)

        actual_domain = result.get("domain")
        actual_intent = result.get("intent")

        success = (
            actual_domain == expected_domain
            and actual_intent == expected_intent
        )

        if success:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print()
        print(f"{index:02d}. [{status}] {question}")
        print(
            f"    Expected: "
            f"{expected_domain} / {expected_intent}"
        )
        print(
            f"    Actual:   "
            f"{actual_domain} / {actual_intent}"
        )

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print(f"Total tests : {len(test_cases)}")
    print(f"Passed      : {passed}")
    print(f"Failed      : {failed}")
    print("=" * 72)

    if failed > 0:
        raise SystemExit(1)


if __name__ == "__main__":
    run_tests()