from app.engines.data_intelligence.question_classifier import QuestionClassifier


def run_tests() -> None:
    classifier = QuestionClassifier()

    test_cases = [
        # ---------------------------------
        # Budget Dimension Drill-Down
        # ---------------------------------
        (
            "Why is SIDA 4 over budget?",
            "budget",
            "budget_dimension_drilldown",
        ),
        (
            "What is causing Fund F1 to be over budget?",
            "budget",
            "budget_dimension_drilldown",
        ),
        (
            "What is driving the variance in SIDA 4?",
            "budget",
            "budget_dimension_drilldown",
        ),
        (
            "Show me the budget breakdown for Fund F1",
            "budget",
            "budget_dimension_drilldown",
        ),
        (
            "Which programs are driving Fund F1's budget variance?",
            "budget",
            "budget_dimension_drilldown",
        ),
        (
            "Show me the budget lines behind Program P1",
            "budget",
            "budget_dimension_drilldown",
        ),

        # ------------------------------
        # Financial Scenario Intelligence
        # ------------------------------
        (
            "What if revenue falls by 10%?",
            "financial_scenario",
            "revenue_scenario",
        ),
        (
            "What if expenses increase by 15%?",
            "financial_scenario",
            "expense_scenario",
        ),
        (
            "What happens if we spend an additional $500,000?",
            "financial_scenario",
            "financial_scenario_summary",
        ),
        (
            "Simulate a $250,000 cash inflow.",
            "financial_scenario",
            "financial_scenario_summary",
        ),
        (
            (
                "What if revenue drops by 10% and "
                "expenses rise by 5%?"
            ),
            "financial_scenario",
            "combined_scenario",
        ),

        # ------------------------------
        # Funding Scenario Intelligence
        # ------------------------------
        (
            "What if expected funding decreases by 20%?",
            "funding_scenario",
            "expected_funding_change_scenario",
        ),
        (
            "What happens if expected grant EF-001 does not materialize?",
            "funding_scenario",
            "expected_funding_failure_scenario",
        ),
        (
            "Show me the maximum expected funding scenario.",
            "funding_scenario",
            "expected_funding_basis_scenario",
        ),        

        # ---------------------------------
        # Financial Opportunity Intelligence
        # ---------------------------------
        (
            "What financial opportunities do we have?",
            "financial_opportunity",
            "financial_opportunity_summary",
        ),
        (
            "What are our highest financial opportunities?",
            "financial_opportunity",
            "high_financial_opportunities",
        ),
        (
            "What funding opportunities do we have?",
            "financial_opportunity",
            "funding_opportunities",
        ),
        (
            "What liquidity opportunities do we have?",
            "financial_opportunity",
            "liquidity_opportunities",
        ),
        (
            "Why is AUC over budget?",
            "budget",
            "budget_dimension_drilldown",
        ),
        (
            "Why is our portfolio over budget?",
            "budget",
            "portfolio_budget_position",
        ),
        # ---------------------------------
        # Forward-Looking Risk Intelligence
        # ---------------------------------
        (
            "What risks are emerging?",
            "risk",
            "forward_risk_summary",
        ),
        (
            "What future risks should I worry about?",
            "risk",
            "forward_high_risks",
        ),
        (
            "What forward funding risks do we have?",
            "risk",
            "forward_funding_risks",
        ),
        (
            "What future operating risks are emerging?",
            "risk",
            "forward_operating_risks",
        ),
        # ---------------------------------
        # Financial Forecast Intelligence
        # ---------------------------------
        (
            "What is our revenue forecast?",
            "financial_forecast",
            "revenue_forecast",
        ),
        (
            "What are our projected expenses?",
            "financial_forecast",
            "expense_forecast",
        ),
        (
            "What is our projected net result?",
            "financial_forecast",
            "net_result_forecast",
        ),
        (
            "What does our financial forecast look like?",
            "financial_forecast",
            "financial_forecast_summary",
        ),
        # ---------------------------------
        # Financial Scenario Intelligence
        # ---------------------------------
        (
            "What happens if revenue drops 10%?",
            "financial_scenario",
            "revenue_scenario",
        ),
        (
            "What if expenses increase 15%?",
            "financial_scenario",
            "expense_scenario",
        ),
        (
            "Show me a scenario where revenue increases 20%.",
            "financial_scenario",
            "revenue_scenario",
        ),
        (
            "What happens if expenses decrease 5%?",
            "financial_scenario",
            "expense_scenario",
        ),
        # ---------------------------------
        # Financial Trend Intelligence
        # ---------------------------------
        (
            "Is our revenue increasing?",
            "financial_trends",
            "revenue_trend",
        ),
        (
            "Are our expenses decreasing?",
            "financial_trends",
            "expense_trend",
        ),
        (
            "How has our net result changed?",
            "financial_trends",
            "net_result_trend",
        ),
        (
            "How are our finances trending?",
            "financial_trends",
            "financial_trend_summary",
        ),
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
        # ---------------------------------
        # Overall Budget Position
        # ---------------------------------
        (
            "How much are we over budget?",
            "budget",
            "portfolio_budget_position",
        ),
        (
            "How much over budget are we?",
            "budget",
            "portfolio_budget_position",
        ),
        (
            "How far over budget are we?",
            "budget",
            "portfolio_budget_position",
        ),
        (
            "Are we spending more than we budgeted?",
            "budget",
            "portfolio_budget_position",
        ),
        (
            "Are we spending less than we budgeted?",
            "budget",
            "portfolio_budget_position",
        ),
        # ---------------------------------
        # Budget Remaining
        # ---------------------------------
        (
            "How much budget do we have left?",
            "budget",
            "portfolio_budget_remaining",
        ),
        (
            "Do we still have budget remaining?",
            "budget",
            "portfolio_budget_remaining",
        ),
        (
            "Is there any budget left?",
            "budget",
            "portfolio_budget_remaining",
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
        # ---------------------------------
        # Period / Data Quality
        # ---------------------------------
        (
            "What period does our financial data cover?",
            "data_quality",
            "data_period",
        ),
        (
            "What is our latest transaction date?",
            "data_quality",
            "latest_transaction_date",
        ),
        (
            "What is our earliest transaction date?",
            "data_quality",
            "earliest_transaction_date",
        ),
        (
            "What is our reporting date?",
            "data_quality",
            "reporting_date",
        ),
        (
            "What is our date quality?",
            "data_quality",
            "date_quality",
        ),
        (
            "Do we have any future-dated transactions?",
            "data_quality",
            "future_transactions",
        ),
        # ---------------------------------
        # Organization Summary
        # ---------------------------------
        (
            "Tell me about our organization.",
            "organization",
            "organization_summary",
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

        success = actual_domain == expected_domain and actual_intent == expected_intent

        if success:
            passed += 1
            status = "PASS"
        else:
            failed += 1
            status = "FAIL"

        print()
        print(f"{index:02d}. [{status}] {question}")
        print(f"    Expected: " f"{expected_domain} / {expected_intent}")
        print(f"    Actual:   " f"{actual_domain} / {actual_intent}")

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

def test_scenario_comparison_question():
    result = QuestionClassifier().classify(
        "Compare these two financial scenarios"
    )

    assert result == {
        "domain": "financial_scenario",
        "intent": "scenario_comparison",
        "target": "scenario_comparison",
    }


def test_which_scenario_is_better_question():
    result = QuestionClassifier().classify(
        "Which scenario is better?"
    )

    assert result == {
        "domain": "financial_scenario",
        "intent": "scenario_comparison",
        "target": "scenario_comparison",
    }


def test_which_scenario_is_safer_question():
    result = QuestionClassifier().classify(
        "Which scenario is safer?"
    )

    assert result == {
        "domain": "financial_scenario",
        "intent": "scenario_comparison",
        "target": "scenario_comparison",
    }


def test_compare_scenario_a_and_scenario_b_question():
    result = QuestionClassifier().classify(
        "Compare Scenario A with Scenario B"
    )

    assert result == {
        "domain": "financial_scenario",
        "intent": "scenario_comparison",
        "target": "scenario_comparison",
    }


def test_preferred_scenario_question():
    result = QuestionClassifier().classify(
        "Which of these scenarios should management prefer?"
    )

    assert result == {
        "domain": "financial_scenario",
        "intent": "scenario_comparison",
        "target": "scenario_comparison",
    }

def test_saved_scenario_list_question():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Show me my saved scenarios"
    )

    assert result["domain"] == "financial_scenario"
    assert result["intent"] == "saved_scenario_list"
    assert result["target"] == "scenario_history"


def test_saved_scenario_list_natural_language():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What scenarios have I saved?"
    )

    assert result["domain"] == "financial_scenario"
    assert result["intent"] == "saved_scenario_list"
    assert result["target"] == "scenario_history"


def test_saved_scenario_comparison_question():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Compare my saved Scenario A with Scenario B"
    )

    assert result["domain"] == "financial_scenario"
    assert result["intent"] == "saved_scenario_comparison"
    assert result["target"] == "scenario_history"


def test_saved_scenario_safer_question():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Which of my saved scenarios is safer?"
    )

    assert result["domain"] == "financial_scenario"
    assert result["intent"] == "saved_scenario_comparison"
    assert result["target"] == "scenario_history"  

def test_action_escalation_summary_intent() -> None:
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Which actions need management intervention?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "action_escalation_summary",
        "target": "cfo_action_escalation",
    }


def test_action_escalation_summary_from_escalation_wording() -> None:
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What needs escalation right now?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "action_escalation_summary",
        "target": "cfo_action_escalation",
    }


def test_critical_action_followups_intent() -> None:
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What are my critical follow-ups?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "critical_action_followups",
        "target": "cfo_action_escalation",
    }


def test_critical_action_followups_from_immediate_attention_wording() -> None:
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Which actions require immediate attention?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "critical_action_followups",
        "target": "cfo_action_escalation",
    }


def test_existing_overdue_action_intent_still_works() -> None:
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What actions are overdue?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "overdue_actions",
        "target": "cfo_action_monitoring",
    }


def test_existing_due_soon_action_intent_still_works() -> None:
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What needs follow-up this week?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "due_soon_actions",
        "target": "cfo_action_monitoring",
    }
def test_action_performance_summary_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "How is our action plan performing?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "action_performance_summary",
        "target": "cfo_action_performance",
    }


def test_reopened_action_patterns_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Which actions keep reopening?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "reopened_action_patterns",
        "target": "cfo_action_performance",
    }


def test_repeated_blocking_patterns_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Which actions keep getting blocked?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "repeated_blocking_patterns",
        "target": "cfo_action_performance",
    }


def test_ownership_change_patterns_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Which actions keep changing owners?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "ownership_change_patterns",
        "target": "cfo_action_performance",
    }


def test_due_date_change_patterns_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Which actions keep changing due dates?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "due_date_change_patterns",
        "target": "cfo_action_performance",
    }


def test_existing_overdue_action_intent_is_not_stolen_by_performance():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What actions are overdue?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "overdue_actions",
        "target": "cfo_action_monitoring",
    }


def test_existing_escalation_intent_is_not_stolen_by_performance():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Which actions need management intervention?"
    )

    assert result == {
        "domain": "cfo_action_plan",
        "intent": "action_escalation_summary",
        "target": "cfo_action_escalation",
    }

def test_historical_change_summary_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What changed since our last financial update?"
    )

    assert result == {
        "domain": "historical_change",
        "intent": "historical_change_summary",
        "target": "financial_intelligence_history",
    }


def test_financial_position_change_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Is our financial position improving or deteriorating?"
    )

    assert result == {
        "domain": "historical_change",
        "intent": "financial_position_change",
        "target": "financial_intelligence_history",
    }


def test_risk_change_summary_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "How have our financial risks changed?"
    )

    assert result == {
        "domain": "historical_change",
        "intent": "risk_change_summary",
        "target": "financial_intelligence_history",
    }


def test_new_risks_since_previous_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What new risks appeared since the previous update?"
    )

    assert result == {
        "domain": "historical_change",
        "intent": "new_risks_since_previous",
        "target": "financial_intelligence_history",
    }


def test_resolved_risks_since_previous_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Which risks were resolved since the last update?"
    )

    assert result == {
        "domain": "historical_change",
        "intent": "resolved_risks_since_previous",
        "target": "financial_intelligence_history",
    }


def test_historical_risk_question_does_not_fall_into_generic_risk_summary():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What changed in our financial risks?"
    )

    assert result["domain"] == "historical_change"
    assert result["intent"] == "risk_change_summary"


def test_historical_position_question_does_not_fall_into_financial_trends():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "How has our financial position changed?"
    )

    assert result["domain"] == "historical_change"
    assert result["intent"] == "financial_position_change"                  

def test_historical_management_priority_summary_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What historical changes require management attention?"
    )

    assert result == {
        "domain": "historical_decision",
        "intent": (
            "historical_management_priority_summary"
        ),
        "target": (
            "historical_decision_intelligence"
        ),
    }


def test_historical_deterioration_priority_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What deteriorations should management prioritize?"
    )

    assert result["domain"] == "historical_decision"

    assert (
        result["intent"]
        == "historical_management_priority_summary"
    )


def test_latest_financial_changes_management_focus_intent():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "Based on our latest financial changes, "
        "what should management focus on?"
    )

    assert result["domain"] == "historical_decision"

    assert (
        result["intent"]
        == "historical_management_priority_summary"
    )


def test_historical_management_question_does_not_fall_into_generic_history():
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What historical financial changes "
        "need management attention?"
    )

    assert result["domain"] == "historical_decision"

    assert (
        result["intent"]
        == "historical_management_priority_summary"
    )
def test_core_cost_coverage_summary_intent() -> None:
    classifier = QuestionClassifier()

    result = classifier.classify(
        "How much of our core costs are covered?"
    )

    assert result == {
        "domain": "core_cost_coverage",
        "intent": "core_cost_coverage_summary",
        "target": "core_cost_coverage",
    }


def test_indirect_recovery_status_intent() -> None:
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What is the status of our indirect recovery?"
    )

    assert result == {
        "domain": "core_cost_coverage",
        "intent": "indirect_recovery_status",
        "target": "core_cost_coverage",
    }


def test_core_cost_gap_intent() -> None:
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What is our remaining core cost gap?"
    )

    assert result == {
        "domain": "core_cost_coverage",
        "intent": "core_cost_gap",
        "target": "core_cost_coverage",
    }


def test_core_cost_coverage_sources_intent() -> None:
    classifier = QuestionClassifier()

    result = classifier.classify(
        "What are the sources covering our core costs?"
    )

    assert result == {
        "domain": "core_cost_coverage",
        "intent": "core_cost_coverage_sources",
        "target": "core_cost_coverage",
    }
