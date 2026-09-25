from pathlib import Path

from app.services.ai_question_engine import AIQuestionEngine


class FakeWorkspaceService:
    def get_workspace_by_organisation(
        self,
        organisation_id: str,
    ) -> dict:
        return {
            "paths": {
                "ai_knowledge": "fake/ai_knowledge",
                "financial_model": "fake/financial_model",
            }
        }


class FakeKnowledgeReader:
    def get_summary(
        self,
        folder: Path,
    ) -> dict:
        return {
            "status": "available",
            "organisation_name": "Test NGO",
            "currency": "USD",
        }


class FakeFinancialIntelligenceService:
    pass


class FakeFinancialModelService:
    def load_json(
        self,
        financial_model_folder: Path,
        filename: str,
    ):
        data = {
            "financial_facts.json": {},
            "cash_flow.json": {},
            "liquidity.json": {},
            "financial_health.json": {},
            "risk_assessment.json": [],
            "financial_opportunities.json": [
                {
                    "priority": "High",
                    "category": "Funding",
                    "title": "Secured funding coverage opportunity",
                    "evidence": (
                        "Validated Funding Gap analysis shows "
                        "57.56% secured-funding coverage."
                    ),
                    "recommended_action": (
                        "Focus fundraising attention on the "
                        "remaining uncovered requirements."
                    ),
                },
                {
                    "priority": "Medium",
                    "category": "Liquidity",
                    "title": "Strong liquidity capacity",
                    "evidence": (
                        "Validated liquidity analysis shows " "12.59 months of runway."
                    ),
                    "recommended_action": ("Use liquidity capacity strategically."),
                },
            ],
            "intelligence_hub.json": {},
            "funding_gap.json": {
                "summary": {
                    "remaining_requirement": 1000.0,
                    "applied_secured_funding": 400.0,
                    "funding_gap": 600.0,
                    "applied_coverage_percentage": 40.0,
                    "period_ineligible_funding_exposure": 200.0,
                    "period_unknown_funding_exposure": 100.0,
                    "dimension_incompatible_funding_exposure": 50.0,
                    "requirements_with_period_ineligible_funding": 2,
                    "requirements_with_period_unknown_funding": 1,
                    "requirements_with_dimension_incompatible_funding": 1,
                    "gross_remaining_secured_funding": 700.0,
                    "eligible_secured_funding": 400.0,
                    "secured_without_budget_line": 100.0,
                    "unfunded_requirement_count": 3,
                    "unmatched_requirement_count": 2,
                }
            },
            "core_cost_coverage_intelligence.json": {
                "status": "available",
                "summary": {
                    "needed_core_cost": 1000.0,
                    "direct_grant_coverage": 300.0,
                    "available_indirect_recovery": 250.0,
                    "allocated_indirect_recovery": 200.0,
                    "used_indirect_recovery": 150.0,
                    "unrestricted_core_funding": 100.0,
                    "remaining_core_cost_gap": 400.0,
                    "core_cost_coverage_percentage": 60.0,
                },
                "lines": [
                    {
                        "budget_line_code": "SAL-001",
                        "budget_line_name": "Core Salaries",
                        "direct_grant_coverage_sources": [
                            {
                                "fund_code": "GRANT-001",
                                "budget_line_code": "SAL-001",
                                "amount": 300.0,
                            },
                        ],
                        "indirect_recovery_allocation_sources": [
                            {
                                "fund_code": "INDIRECT-001",
                                "budget_line_code": "SAL-001",
                                "amount": 200.0,
                            },
                        ],
                        "unrestricted_core_funding_sources": [
                            {
                                "fund_code": "CORE-001",
                                "budget_line_code": "SAL-001",
                                "amount": 100.0,
                            },
                        ],
                    },
                ],
                "controls": {
                    "used_indirect_recovery_exceeds_allocation": False,
                    "allocated_indirect_recovery_exceeds_available": False,
                    "total_core_cost_coverage_exceeds_need": False,
                },
            },
            "cfo_recommendations.json": [
                {
                    "priority": "High",
                    "category": "Funding",
                    "title": "Close the remaining Funding Gap",
                    "action": "Secure additional unrestricted or compatible funding.",
                    "expected_impact": "Reduce the remaining unfunded requirement.",
                    "linked_risk": "Unfunded financial requirements",
                },
                {
                    "priority": "High",
                    "category": "Funding",
                    "title": "Resolve out-of-period secured funding",
                    "action": "Review grants outside the applicable fiscal period.",
                    "expected_impact": "Improve funding-period alignment.",
                    "linked_risk": "Funding Gap",
                },
                {
                    "priority": "High",
                    "category": "Funding",
                    "title": "Complete missing grant-period evidence",
                    "action": "Complete missing grant start and end dates.",
                    "expected_impact": "Allow AI-FOS to validate grant-period eligibility.",
                    "linked_risk": "Funding Gap",
                },
                {
                    "priority": "High",
                    "category": "Funding",
                    "title": "Review incompatible funding allocations",
                    "action": "Review conflicting funding dimensions.",
                    "expected_impact": "Improve alignment between funding and requirements.",
                    "linked_risk": "Funding Gap",
                },
            ],
        }

        return data.get(filename)


def test_funding_gap_actions_include_diagnostics_and_actions(
    monkeypatch,
):
    engine = AIQuestionEngine(
        workspace_service=FakeWorkspaceService(),
        knowledge_reader=FakeKnowledgeReader(),
        financial_intelligence_service=FakeFinancialIntelligenceService(),
        financial_model_service=FakeFinancialModelService(),
    )

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": "funding_gap_actions",
            "domain": "funding",
        },
    )

    result = engine.answer(
        question="What should management do about our funding gap?",
        organisation_id="test-org",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "600.00 USD" in answer
    assert "1,000.00 USD" in answer
    assert "400.00 USD" in answer
    assert "40.00%" in answer

    assert "200.00 USD" in answer
    assert "100.00 USD" in answer
    assert "50.00 USD" in answer

    assert "grant period" in answer.lower()
    assert "missing or incomplete" in answer.lower()
    assert "dimensions conflict" in answer.lower()

    assert "must not be added together" in answer.lower()

    assert "Close the remaining Funding Gap" in answer
    assert "Resolve out-of-period secured funding" in answer
    assert "Complete missing grant-period evidence" in answer
    assert "Review incompatible funding allocations" in answer


def _build_funding_engine():
    engine = AIQuestionEngine(
        workspace_service=FakeWorkspaceService(),
        knowledge_reader=FakeKnowledgeReader(),
        financial_intelligence_service=FakeFinancialIntelligenceService(),
        financial_model_service=FakeFinancialModelService(),
    )

    return engine


def _run_funding_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "funding",
        },
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_funding_gap_answer_includes_diagnostics(
    monkeypatch,
):
    result = _run_funding_intent(
        monkeypatch=monkeypatch,
        intent="funding_gap",
        question="What is our funding gap?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "600.00 USD" in answer
    assert "1,000.00 USD" in answer
    assert "400.00 USD" in answer
    assert "40.00%" in answer

    assert "200.00 USD" in answer
    assert "100.00 USD" in answer
    assert "50.00 USD" in answer

    assert "grant period" in answer.lower()
    assert "missing or incomplete" in answer.lower()
    assert "dimensions" in answer.lower()


def test_funding_coverage_answer(
    monkeypatch,
):
    result = _run_funding_intent(
        monkeypatch=monkeypatch,
        intent="funding_coverage",
        question="How much of our funding requirement is covered?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "40.00%" in answer
    assert "400.00 USD" in answer
    assert "1,000.00 USD" in answer
    assert "600.00 USD" in answer


def test_secured_funding_total_distinguishes_gross_and_eligible(
    monkeypatch,
):
    result = _run_funding_intent(
        monkeypatch=monkeypatch,
        intent="secured_funding_total",
        question="How much secured funding do we have?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "gross remaining secured funding" in answer.lower()
    assert "eligible" in answer.lower()
    assert "applied" in answer.lower()
    assert "not be interpreted as automatically available" in answer.lower()


def test_eligible_secured_funding_explains_validation_rules(
    monkeypatch,
):
    result = _run_funding_intent(
        monkeypatch=monkeypatch,
        intent="eligible_secured_funding",
        question="How much secured funding is actually eligible?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "eligible" in answer.lower()
    assert "grant-period eligibility" in answer.lower()
    assert "dimensional allocation" in answer.lower()


def test_funding_evidence_explains_why_funding_is_not_automatic(
    monkeypatch,
):
    result = _run_funding_intent(
        monkeypatch=monkeypatch,
        intent="funding_evidence",
        question="Why can't all available grants cover the funding gap?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "budget line" in answer.lower()
    assert "eligibility" in answer.lower()
    assert "allocation evidence" in answer.lower()

    assert "200.00 USD" in answer
    assert "100.00 USD" in answer
    assert "50.00 USD" in answer

    assert "must not be added together" in answer.lower()


def _run_core_cost_coverage_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "core_cost_coverage",
        },
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_unfunded_requirements_answer(
    monkeypatch,
):
    result = _run_funding_intent(
        monkeypatch=monkeypatch,
        intent="unfunded_requirements",
        question="Which requirements are still unfunded?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "funding gap" in answer.lower()
    assert "600.00 USD" in answer


def test_financial_health_summary_identifies_weakest_area(
    monkeypatch,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": "financial_health",
            "domain": "financial_health",
        },
    )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_health(
        financial_model_folder,
        filename,
    ):
        if filename == "financial_health.json":
            return {
                "score": 54,
                "maximum": 100,
                "rating": "Weak",
                "categories": {
                    "operating_performance": {
                        "score": 15,
                        "maximum": 25,
                        "reason": ("The organization is operating " "at a deficit."),
                    },
                    "financial_position": {
                        "score": 8,
                        "maximum": 20,
                        "reason": ("Adjusted equity or net assets " "are negative."),
                    },
                    "liquidity": {
                        "score": 17,
                        "maximum": 20,
                        "reason": (
                            "Available cash provides strong "
                            "operating expense coverage."
                        ),
                    },
                    "budget_control": {
                        "score": 0,
                        "maximum": 20,
                        "reason": (
                            "Budget utilization is high and "
                            "unbudgeted actual spending exists."
                        ),
                    },
                },
            }

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_health,
    )

    result = engine.answer(
        question="How healthy are we financially?",
        organisation_id="test-org",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "54/100" in answer
    assert "weak" in answer.lower()
    assert "budget control" in answer.lower()
    assert "0/20" in answer


def test_financial_health_explanation_identifies_weakest_and_strongest_areas(
    monkeypatch,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": "financial_health_explanation",
            "domain": "financial_health",
        },
    )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_health(
        financial_model_folder,
        filename,
    ):
        if filename == "financial_health.json":
            return {
                "score": 54,
                "maximum": 100,
                "rating": "Weak",
                "categories": {
                    "operating_performance": {
                        "score": 15,
                        "maximum": 25,
                        "reason": ("The organization is operating " "at a deficit."),
                    },
                    "financial_position": {
                        "score": 8,
                        "maximum": 20,
                        "reason": ("Adjusted equity or net assets " "are negative."),
                    },
                    "liquidity": {
                        "score": 17,
                        "maximum": 20,
                        "reason": (
                            "Available cash provides strong "
                            "operating expense coverage."
                        ),
                    },
                    "budget_control": {
                        "score": 0,
                        "maximum": 20,
                        "reason": (
                            "Budget utilization is high and "
                            "unbudgeted actual spending exists."
                        ),
                    },
                },
            }

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_health,
    )

    result = engine.answer(
        question="Why is our Financial Health score weak?",
        organisation_id="test-org",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "54/100" in answer
    assert "weak" in answer.lower()

    assert "budget control" in answer.lower()
    assert "financial position" in answer.lower()
    assert "operating performance" in answer.lower()

    assert "liquidity" in answer.lower()
    assert "17/20" in answer

    assert "not recalculating" in answer.lower()


def _run_risk_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "risk",
        },
    )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_risks(
        financial_model_folder,
        filename,
    ):
        if filename == "risk_assessment.json":
            return [
                {
                    "severity": "Critical",
                    "title": "Liquidity pressure",
                    "category": "Liquidity",
                    "evidence": (
                        "Available cash runway is below "
                        "the preferred management threshold."
                    ),
                    "recommendation": (
                        "Strengthen short-term cash planning "
                        "and protect unrestricted liquidity."
                    ),
                },
                {
                    "severity": "High",
                    "title": "Budget overspend",
                    "category": "Budget",
                    "evidence": (
                        "Actual spending exceeds budget " "on material budget lines."
                    ),
                    "recommendation": (
                        "Review over-budget lines and " "approve corrective actions."
                    ),
                },
                {
                    "severity": "High",
                    "title": "Funding Gap",
                    "category": "Funding",
                    "evidence": (
                        "Remaining requirements exceed "
                        "validated applicable secured funding."
                    ),
                    "recommendation": ("Secure additional compatible funding."),
                },
                {
                    "severity": "Medium",
                    "title": "Unbudgeted spending",
                    "category": "Budget",
                    "evidence": (
                        "Some actual expenditure has no "
                        "corresponding approved budget."
                    ),
                    "recommendation": (
                        "Review and regularize unbudgeted " "expenditure."
                    ),
                },
            ]

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_risks,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_risk_summary_reports_counts_and_top_risks(
    monkeypatch,
):
    result = _run_risk_intent(
        monkeypatch=monkeypatch,
        intent="risk_summary",
        question="What are our main financial risks?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "4 financial risk" in answer.lower()
    assert "1 critical" in answer.lower()
    assert "2 high" in answer.lower()

    assert "liquidity pressure" in answer.lower()
    assert "budget overspend" in answer.lower()
    assert "funding gap" in answer.lower()


def test_high_risks_returns_only_critical_and_high(
    monkeypatch,
):
    result = _run_risk_intent(
        monkeypatch=monkeypatch,
        intent="high_risks",
        question="What are our high risks?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "3 critical or high-severity" in answer.lower()

    assert "liquidity pressure" in answer.lower()
    assert "budget overspend" in answer.lower()
    assert "funding gap" in answer.lower()

    assert "unbudgeted spending" not in answer.lower()


def test_immediate_risk_returns_highest_severity(
    monkeypatch,
):
    result = _run_risk_intent(
        monkeypatch=monkeypatch,
        intent="immediate_risk",
        question="What risk needs immediate attention?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "critical-severity" in answer.lower()
    assert "liquidity pressure" in answer.lower()
    assert "recommended management response" in answer.lower()


def test_liquidity_risks_filters_verified_risks(
    monkeypatch,
):
    result = _run_risk_intent(
        monkeypatch=monkeypatch,
        intent="liquidity_risks",
        question="What are our liquidity risks?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "1 liquidity risk" in answer.lower()
    assert "critical" in answer.lower()
    assert "liquidity pressure" in answer.lower()

    assert "budget overspend" not in answer.lower()


def test_budget_risks_filters_verified_risks(
    monkeypatch,
):
    result = _run_risk_intent(
        monkeypatch=monkeypatch,
        intent="budget_risks",
        question="What are our budget risks?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "2 budget risk" in answer.lower()
    assert "high" in answer.lower()

    assert "budget overspend" in answer.lower()
    assert "unbudgeted spending" in answer.lower()

    assert "liquidity pressure" not in answer.lower()


def test_funding_risks_filters_verified_risks(
    monkeypatch,
):
    result = _run_risk_intent(
        monkeypatch=monkeypatch,
        intent="funding_risks",
        question="What are our funding risks?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "1 funding risk" in answer.lower()
    assert "high" in answer.lower()
    assert "funding gap" in answer.lower()

    assert "budget overspend" not in answer.lower()


def _run_budget_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "budget",
        },
    )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_budget(
        financial_model_folder,
        filename,
    ):
        if filename == "intelligence_hub.json":
            return {
                "facts": {
                    "budget_dashboard": {
                        "portfolio_control": {
                            "total_budget": 1000.0,
                            "total_actual": 850.0,
                            "utilization_percentage": 85.0,
                            "total_variance": 200.0,
                            "overall_variance_including_unbudgeted": 150.0,
                            "unbudgeted_actual": 50.0,
                            "over_budget_count": 2,
                        },
                        "dimension_drilldown": {
                            "fund": {
                                "dimension": "fund",
                                "record_count": 1,
                                "records": [
                                    {
                                        "code": "FR0001-0001",
                                        "name": "SIDA 4",
                                        "drilldown": {
                                            "program": {
                                                "dimension": "program",
                                                "summary": {
                                                    "total_budget": 2209346.0,
                                                    "total_actual": 2646675.0,
                                                    "total_variance": -437329.0,
                                                    "line_count": 2,
                                                    "over_budget_count": 1,
                                                    "within_budget_count": 1,
                                                    "no_budget_count": 0,
                                                },
                                                "lines": [
                                                    {
                                                        "code": "P1",
                                                        "name": "Program One",
                                                        "budget": 1000000.0,
                                                        "actual": 1300000.0,
                                                        "variance": -300000.0,
                                                        "utilization_percentage": 130.0,
                                                        "status": "Over Budget",
                                                    },
                                                    {
                                                        "code": "P2",
                                                        "name": "Program Two",
                                                        "budget": 1209346.0,
                                                        "actual": 1346675.0,
                                                        "variance": -137329.0,
                                                        "utilization_percentage": 111.35,
                                                        "status": "Over Budget",
                                                    },
                                                ],
                                            }
                                        },
                                    }
                                ],
                            }
                        },
                    }
                }
            }

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_budget,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_portfolio_total_budget_answer(
    monkeypatch,
):
    result = _run_budget_intent(
        monkeypatch=monkeypatch,
        intent="portfolio_total_budget",
        question="What is our total portfolio budget?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "1,000.00 USD" in answer
    assert "850.00 USD" in answer


def test_portfolio_budget_utilization_answer(
    monkeypatch,
):
    result = _run_budget_intent(
        monkeypatch=monkeypatch,
        intent="portfolio_budget_utilization",
        question="What is our budget utilization?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "85.00%" in answer
    assert "850.00 USD" in answer
    assert "1,000.00 USD" in answer


def test_portfolio_budget_variance_distinguishes_variance_types(
    monkeypatch,
):
    result = _run_budget_intent(
        monkeypatch=monkeypatch,
        intent="portfolio_budget_variance",
        question="What is our portfolio budget variance?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "200.00 USD" in answer
    assert "150.00 USD" in answer
    assert "unbudgeted actual spending" in answer.lower()


def test_portfolio_budget_remaining_answer(
    monkeypatch,
):
    result = _run_budget_intent(
        monkeypatch=monkeypatch,
        intent="portfolio_budget_remaining",
        question="How much portfolio budget remains?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "150.00 USD" in answer
    assert "85.00%" in answer
    assert "budget remaining" in answer.lower()


def test_portfolio_budget_position_answer(
    monkeypatch,
):
    result = _run_budget_intent(
        monkeypatch=monkeypatch,
        intent="portfolio_budget_position",
        question="Are we over or under budget?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "under its total portfolio budget" in answer.lower()
    assert "150.00 USD" in answer
    assert "850.00 USD" in answer
    assert "1,000.00 USD" in answer
    assert "50.00 USD" in answer
    assert "2 budget line" in answer.lower()


def test_unbudgeted_actual_answer(
    monkeypatch,
):
    result = _run_budget_intent(
        monkeypatch=monkeypatch,
        intent="unbudgeted_actual",
        question="How much unbudgeted spending do we have?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "50.00 USD" in answer
    assert "without a matching approved budget" in answer.lower()


def test_over_budget_count_answer(
    monkeypatch,
):
    result = _run_budget_intent(
        monkeypatch=monkeypatch,
        intent="over_budget_count",
        question="How many budget lines are over budget?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "2 portfolio budget line" in answer.lower()
    assert "management review" in answer.lower()


def test_portfolio_budget_summary_answer(
    monkeypatch,
):
    result = _run_budget_intent(
        monkeypatch=monkeypatch,
        intent="portfolio_budget_summary",
        question="Give me a portfolio budget summary.",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "1,000.00 USD" in answer
    assert "850.00 USD" in answer
    assert "85.00%" in answer
    assert "200.00 USD" in answer
    assert "150.00 USD" in answer
    assert "50.00 USD" in answer
    assert "2 budget line" in answer.lower()


def test_budget_performance_summary_highlights_control_issues(
    monkeypatch,
):
    result = _run_budget_intent(
        monkeypatch=monkeypatch,
        intent="budget_performance_summary",
        question="How are we performing against budget?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "85.00%" in answer
    assert "under budget by 150.00 usd" in answer.lower()
    assert "50.00 USD" in answer
    assert "2 budget line" in answer.lower()

    assert "management attention" in answer.lower()
    assert "does not recalculate" in answer.lower()

def test_budget_dimension_drilldown_explains_selected_fund(
    monkeypatch,
):
    result = _run_budget_intent(
        monkeypatch=monkeypatch,
        intent="budget_dimension_drilldown",
        question="Why is SIDA 4 over budget?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "SIDA 4" in answer
    assert "FR0001-0001" in answer
    assert "Program One" in answer
    assert "Program Two" in answer
    assert "300,000.00 USD" in answer
    assert "137,329.00 USD" in answer
    assert "437,329.00 USD" in answer

    assert "does not recalculate" in answer.lower()

def _run_grant_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "grants",
        },
    )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_grants(
        financial_model_folder,
        filename,
    ):
        if filename == "grants.json":
            return {
                "GRANT-001": {
                    "code": "GRANT-001",
                    "name": "High Utilization Grant",
                    "revised_budget": 1000.0,
                    "actual": 950.0,
                    "remaining_budget": 50.0,
                    "utilization": 95.0,
                },
                "GRANT-002": {
                    "code": "GRANT-002",
                    "name": "Over Budget Grant",
                    "revised_budget": 500.0,
                    "actual": 600.0,
                    "remaining_budget": -100.0,
                    "utilization": 120.0,
                },
                "GRANT-003": {
                    "code": "GRANT-003",
                    "name": "Actual Only Grant",
                    "revised_budget": 0.0,
                    "actual": 200.0,
                    "remaining_budget": -200.0,
                    "utilization": 0.0,
                },
                "GRANT-004": {
                    "code": "GRANT-004",
                    "name": "Budget Without Spending Grant",
                    "revised_budget": 400.0,
                    "actual": 0.0,
                    "remaining_budget": 400.0,
                    "utilization": 0.0,
                },
                "GRANT-005": {
                    "code": "GRANT-005",
                    "name": "Healthy Grant",
                    "revised_budget": 800.0,
                    "actual": 300.0,
                    "remaining_budget": 500.0,
                    "utilization": 37.5,
                },
            }

        if filename == "grant_diagnostics.json":
            return {
                "actual_only_grants": [
                    "GRANT-003",
                ],
                "budget_only_grants": [
                    "GRANT-004",
                ],
                "matched_grants": [
                    "GRANT-001",
                    "GRANT-002",
                    "GRANT-005",
                ],
            }

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_grants,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_grant_attention_identifies_priority_grants(
    monkeypatch,
):
    result = _run_grant_intent(
        monkeypatch=monkeypatch,
        intent="grant_attention",
        question="Which grants need attention?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "high utilization grant" in answer.lower()
    assert "over budget grant" in answer.lower()
    assert "actual only grant" in answer.lower()

    assert "actual activity without matched budget" in answer.lower()

    assert "healthy grant" not in answer.lower()


def test_grant_remaining_budget_lists_available_balances(
    monkeypatch,
):
    result = _run_grant_intent(
        monkeypatch=monkeypatch,
        intent="grant_remaining_budget",
        question="Which grants still have remaining budget?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "healthy grant" in answer.lower()
    assert "500.00 USD" in answer

    assert "budget without spending grant" in answer.lower()
    assert "400.00 USD" in answer

    assert "high utilization grant" in answer.lower()
    assert "50.00 USD" in answer

    assert "over budget grant" not in answer.lower()


def test_grant_high_utilization_identifies_grants_above_threshold(
    monkeypatch,
):
    result = _run_grant_intent(
        monkeypatch=monkeypatch,
        intent="grant_high_utilization",
        question="Which grants have high utilization?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "over budget grant" in answer.lower()
    assert "120.00%" in answer

    assert "high utilization grant" in answer.lower()
    assert "95.00%" in answer

    assert "healthy grant" not in answer.lower()


def test_grant_spending_without_budget_identifies_actual_only_grants(
    monkeypatch,
):
    result = _run_grant_intent(
        monkeypatch=monkeypatch,
        intent="grant_spending_without_budget",
        question="Which grants have spending without budget?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "1 grant" in answer.lower()
    assert "actual only grant" in answer.lower()
    assert "200.00 USD" in answer
    assert "no identified budget" in answer.lower()


def test_grant_budget_without_spending_identifies_inactive_budget(
    monkeypatch,
):
    result = _run_grant_intent(
        monkeypatch=monkeypatch,
        intent="grant_budget_without_spending",
        question="Which grants have budget but no spending?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "1 grant" in answer.lower()
    assert "budget without spending grant" in answer.lower()
    assert "400.00 USD" in answer
    assert "no recorded spending" in answer.lower()


def test_grant_funding_budget_issues_identifies_control_issues(
    monkeypatch,
):
    result = _run_grant_intent(
        monkeypatch=monkeypatch,
        intent="grant_funding_budget_issues",
        question="Which grants have funding or budget issues?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "3 grant" in answer.lower()

    assert "over budget grant" in answer.lower()
    assert "spending exceeds the identified budget" in answer.lower()

    assert "high utilization grant" in answer.lower()
    assert "high budget utilization" in answer.lower()

    assert "actual only grant" in answer.lower()
    assert "spending without an identified budget" in answer.lower()

    assert "healthy grant" not in answer.lower()


def test_grant_portfolio_summary_uses_verified_grant_records(
    monkeypatch,
):
    result = _run_grant_intent(
        monkeypatch=monkeypatch,
        intent="grant_portfolio_summary",
        question="Give me a summary of our grant portfolio.",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "4 grant" in answer.lower()
    assert "2,700.00 USD" in answer
    assert "1,850.00 USD" in answer
    assert "68.52%" in answer
    assert "850.00 USD" in answer

    assert "1 budgeted grant" in answer.lower()
    assert "2 are at or above 90%" in answer.lower()
    assert "1 grant" in answer.lower()
    assert "recorded spending but no identified budget" in answer.lower()


def _run_recommendation_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "recommendations",
        },
    )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_recommendations(
        financial_model_folder,
        filename,
    ):
        if filename == "cfo_recommendations.json":
            return [
                {
                    "priority": "High",
                    "category": "Liquidity",
                    "title": "Protect short-term liquidity",
                    "action": (
                        "Review cash commitments and preserve "
                        "sufficient unrestricted cash."
                    ),
                    "expected_impact": ("Reduce short-term liquidity pressure."),
                },
                {
                    "priority": "High",
                    "category": "Funding",
                    "title": "Close the remaining Funding Gap",
                    "action": (
                        "Secure additional eligible funding for "
                        "uncovered requirements."
                    ),
                    "expected_impact": ("Reduce the remaining Funding Gap."),
                    "linked_risk": "Unfunded financial requirements",
                },
                {
                    "priority": "Medium",
                    "category": "Budget",
                    "title": "Review budget overspending",
                    "action": (
                        "Review overspent budget lines and "
                        "implement corrective controls."
                    ),
                    "expected_impact": ("Improve budget control."),
                },
                {
                    "priority": "Medium",
                    "category": "Funding",
                    "title": "Complete missing grant-period evidence",
                    "action": (
                        "Complete missing grant start and end " "date evidence."
                    ),
                    "expected_impact": (
                        "Improve secured-funding eligibility " "validation."
                    ),
                    "linked_risk": "Funding Gap",
                },
                {
                    "priority": "Low",
                    "category": "Operations",
                    "title": "Improve routine reporting",
                    "action": ("Standardize monthly management reporting."),
                    "expected_impact": ("Improve reporting consistency."),
                },
            ]

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_recommendations,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_priority_actions_prioritizes_high_priority_recommendations(
    monkeypatch,
):
    result = _run_recommendation_intent(
        monkeypatch=monkeypatch,
        intent="priority_actions",
        question="What should management do first?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "highest-priority financial actions" in answer.lower()

    assert "protect short-term liquidity" in answer.lower()
    assert "close the remaining funding gap" in answer.lower()

    assert "review budget overspending" not in answer.lower()
    assert "improve routine reporting" not in answer.lower()


def test_finance_meeting_agenda_focuses_on_high_priority_actions(
    monkeypatch,
):
    result = _run_recommendation_intent(
        monkeypatch=monkeypatch,
        intent="finance_meeting_agenda",
        question="What should we discuss at the finance meeting?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "next finance meeting" in answer.lower()

    assert "protect short-term liquidity" in answer.lower()
    assert "close the remaining funding gap" in answer.lower()

    assert "review budget overspending" not in answer.lower()
    assert "improve routine reporting" not in answer.lower()


def test_general_recommendations_are_sorted_by_priority(
    monkeypatch,
):
    result = _run_recommendation_intent(
        monkeypatch=monkeypatch,
        intent="recommendation_summary",
        question="What do you recommend?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "management actions" in answer.lower()

    assert "protect short-term liquidity" in answer.lower()
    assert "close the remaining funding gap" in answer.lower()
    assert "review budget overspending" in answer.lower()

    high_position = answer.lower().find("protect short-term liquidity")

    medium_position = answer.lower().find("review budget overspending")

    low_position = answer.lower().find("improve routine reporting")

    assert high_position != -1
    assert medium_position != -1
    assert low_position != -1

    assert high_position < medium_position < low_position


def test_funding_gap_actions_selects_funding_recommendations(
    monkeypatch,
):
    result = _run_recommendation_intent(
        monkeypatch=monkeypatch,
        intent="funding_gap_actions",
        question="What should management do about the funding gap?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "funding gap" in answer.lower()
    assert "close the remaining funding gap" in answer.lower()
    assert "complete missing grant-period evidence" in answer.lower()

    assert "protect short-term liquidity" not in answer.lower()
    assert "review budget overspending" not in answer.lower()

    assert "grant period" in answer.lower()
    assert "missing or incomplete" in answer.lower()
    assert "dimensions" in answer.lower()

    assert "must not be added together" in answer.lower()


def _run_financial_fact_intent(
    monkeypatch,
    intent: str,
    question: str,
    value: float,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "financial_facts",
        },
    )

    monkeypatch.setattr(
        engine.financial_intelligence_service,
        "get_value",
        lambda intent, financial_facts: value,
        raising=False,
    )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_financial_facts(
        financial_model_folder,
        filename,
    ):
        if filename == "financial_facts.json":
            return {
                "available": True,
            }

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_financial_facts,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_revenue_answer_uses_validated_income_statement_fact(
    monkeypatch,
):
    result = _run_financial_fact_intent(
        monkeypatch=monkeypatch,
        intent="revenue",
        question="What is our total revenue?",
        value=1250000.0,
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "1,250,000.00 USD" in answer
    assert "income statement" in answer.lower()
    assert "validated" in answer.lower()


def test_expenses_answer_uses_validated_income_statement_fact(
    monkeypatch,
):
    result = _run_financial_fact_intent(
        monkeypatch=monkeypatch,
        intent="expenses",
        question="What are our total expenses?",
        value=980000.0,
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "980,000.00 USD" in answer
    assert "income statement" in answer.lower()
    assert "validated" in answer.lower()


def test_net_profit_positive_is_explained_as_surplus(
    monkeypatch,
):
    result = _run_financial_fact_intent(
        monkeypatch=monkeypatch,
        intent="net_profit",
        question="Are we making a surplus or deficit?",
        value=125000.0,
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "surplus" in answer.lower()
    assert "125,000.00 USD" in answer
    assert "income statement" in answer.lower()


def test_net_profit_negative_is_explained_as_deficit(
    monkeypatch,
):
    result = _run_financial_fact_intent(
        monkeypatch=monkeypatch,
        intent="net_profit",
        question="What is our net result?",
        value=-75000.0,
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "deficit" in answer.lower()
    assert "75,000.00 USD" in answer
    assert "-75,000.00 USD" in answer


def test_assets_answer_uses_validated_balance_sheet_fact(
    monkeypatch,
):
    result = _run_financial_fact_intent(
        monkeypatch=monkeypatch,
        intent="assets",
        question="What are our total assets?",
        value=2500000.0,
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "2,500,000.00 USD" in answer
    assert "balance sheet" in answer.lower()
    assert "validated" in answer.lower()


def test_liabilities_and_equity_answers_use_balance_sheet_facts(
    monkeypatch,
):
    liabilities_result = _run_financial_fact_intent(
        monkeypatch=monkeypatch,
        intent="liabilities",
        question="What are our liabilities?",
        value=1400000.0,
    )

    equity_result = _run_financial_fact_intent(
        monkeypatch=monkeypatch,
        intent="equity",
        question="What is our equity?",
        value=1100000.0,
    )

    liabilities_answer = liabilities_result["answer"]
    equity_answer = equity_result["answer"]

    assert liabilities_result["status"] == "success"
    assert equity_result["status"] == "success"

    assert "1,400,000.00 USD" in liabilities_answer
    assert "balance sheet" in liabilities_answer.lower()

    assert "1,100,000.00 USD" in equity_answer
    assert "balance sheet" in equity_answer.lower()


def _run_cash_intent(
    monkeypatch,
    intent: str,
    question: str,
    cash_flow_value: float | None = None,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "cash",
        },
    )

    if cash_flow_value is not None:
        monkeypatch.setattr(
            engine.financial_intelligence_service,
            "get_cash_flow_value",
            lambda intent, cash_flow: cash_flow_value,
            raising=False,
        )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_cash(
        financial_model_folder,
        filename,
    ):
        if filename == "cash_flow.json":
            return {
                "available": True,
            }

        if filename == "liquidity.json":
            return {
                "available_cash": 700000.0,
                "total_cash": 1000000.0,
                "blocked_cash": 300000.0,
                "cash_runway_months": 7.5,
                "runway_basis": (
                    "Available cash divided by average " "monthly operating expenses."
                ),
            }

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_cash,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_operating_cash_flow_positive_answer(
    monkeypatch,
):
    result = _run_cash_intent(
        monkeypatch=monkeypatch,
        intent="operating_cash_flow",
        question="What is our operating cash flow?",
        cash_flow_value=125000.0,
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "positive operating cash flow" in answer.lower()
    assert "125,000.00 USD" in answer
    assert "validated" in answer.lower()


def test_investing_cash_flow_answer_uses_validated_analysis(
    monkeypatch,
):
    result = _run_cash_intent(
        monkeypatch=monkeypatch,
        intent="investing_cash_flow",
        question="What is our investing cash flow?",
        cash_flow_value=-50000.0,
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "-50,000.00 USD" in answer
    assert "validated cash flow analysis" in answer.lower()


def test_financing_cash_flow_answer_uses_validated_analysis(
    monkeypatch,
):
    result = _run_cash_intent(
        monkeypatch=monkeypatch,
        intent="financing_cash_flow",
        question="What is our financing cash flow?",
        cash_flow_value=75000.0,
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "75,000.00 USD" in answer
    assert "validated cash flow analysis" in answer.lower()


def test_net_change_in_cash_negative_is_explained_as_decrease(
    monkeypatch,
):
    result = _run_cash_intent(
        monkeypatch=monkeypatch,
        intent="net_change_in_cash",
        question="How did our cash change?",
        cash_flow_value=-25000.0,
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "decrease in cash" in answer.lower()
    assert "25,000.00 USD" in answer
    assert "-25,000.00 USD" in answer


def test_cash_position_distinguishes_available_total_and_blocked_cash(
    monkeypatch,
):
    result = _run_cash_intent(
        monkeypatch=monkeypatch,
        intent="cash_position",
        question="What is our cash position?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "700,000.00 USD" in answer
    assert "1,000,000.00 USD" in answer
    assert "300,000.00 USD" in answer

    assert "available cash" in answer.lower()
    assert "blocked or restricted" in answer.lower()
    assert "treating all cash as immediately usable" in answer.lower()


def test_blocked_cash_is_not_treated_as_available_liquidity(
    monkeypatch,
):
    result = _run_cash_intent(
        monkeypatch=monkeypatch,
        intent="blocked_cash",
        question="How much cash is blocked?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "300,000.00 USD" in answer
    assert "1,000,000.00 USD" in answer
    assert "700,000.00 USD" in answer

    assert "blocked or restricted cash" in answer.lower()
    assert "not treated as immediately available liquidity" in answer.lower()


def test_cash_runway_uses_validated_liquidity_result(
    monkeypatch,
):
    result = _run_cash_intent(
        monkeypatch=monkeypatch,
        intent="cash_runway",
        question="What is our cash runway?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "7.50 months" in answer
    assert "700,000.00 USD" in answer

    assert "runway basis" in answer.lower()
    assert "validated cash runway" in answer.lower()

    assert "blocked or restricted cash" in answer.lower()
    assert "not" in answer.lower()
    assert "automatically available" in answer.lower()


def _run_organization_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "organization",
        },
    )

    monkeypatch.setattr(
        engine.knowledge_reader,
        "get_summary",
        lambda folder: {
            "status": "available",
            "organisation_name": "Test Organization",
            "source_system": "Business Central",
            "currency": "USD",
            "transactions": 35078,
            "accounts": 877,
            "funds": 12,
            "donors": 8,
            "programs": 14,
        },
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_organization_donor_count(monkeypatch):
    result = _run_organization_intent(
        monkeypatch,
        intent="donor_count",
        question="How many donors do we have?",
    )

    answer = result["answer"]

    assert "Test Organization" in answer
    assert "8 donor" in answer


def test_organization_currency(monkeypatch):
    result = _run_organization_intent(
        monkeypatch,
        intent="currency",
        question="What is our base currency?",
    )

    answer = result["answer"]

    assert "Test Organization" in answer
    assert "USD" in answer
    assert "base currency" in answer.lower()


def test_organization_transaction_count(monkeypatch):
    result = _run_organization_intent(
        monkeypatch,
        intent="transaction_count",
        question="How many transactions are in AI-FOS?",
    )

    answer = result["answer"]

    assert "35,078" in answer
    assert "transaction" in answer.lower()


def test_organization_account_count(monkeypatch):
    result = _run_organization_intent(
        monkeypatch,
        intent="account_count",
        question="How many accounts do we have?",
    )

    answer = result["answer"]

    assert "877" in answer
    assert "account" in answer.lower()


def test_organization_program_count(monkeypatch):
    result = _run_organization_intent(
        monkeypatch,
        intent="program_count",
        question="How many programs do we have?",
    )

    answer = result["answer"]

    assert "14" in answer
    assert "program" in answer.lower()


def test_organization_fund_count(monkeypatch):
    result = _run_organization_intent(
        monkeypatch,
        intent="fund_count",
        question="How many funds do we have?",
    )

    answer = result["answer"]

    assert "12" in answer
    assert "fund" in answer.lower()


def test_organization_summary(monkeypatch):
    result = _run_organization_intent(
        monkeypatch,
        intent="organization_summary",
        question="Tell me about our organization.",
    )

    answer = result["answer"]

    assert "Test Organization" in answer
    assert "Business Central" in answer
    assert "USD" in answer
    assert "35,078" in answer
    assert "877" in answer
    assert "12" in answer
    assert "8" in answer
    assert "14" in answer


def _run_period_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "data_quality",
        },
    )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_date_quality(
        financial_model_folder,
        filename,
    ):
        if filename == "gl_date_quality.json":
            return {
                "status": "warning",
                "reporting_date": "2026-08-29",
                "summary": {
                    "transaction_count": 35078,
                    "valid_date_count": 35070,
                    "missing_date_count": 3,
                    "invalid_date_count": 5,
                    "current_or_historical_count": 35060,
                    "future_transaction_count": 10,
                    "earliest_posting_date": "2023-12-31",
                    "latest_posting_date": "2032-01-01",
                },
                "warnings": [
                    "3 transaction(s) have no posting date.",
                    "5 transaction(s) have an invalid posting date.",
                    (
                        "10 transaction(s) are dated after the "
                        "reporting date 2026-08-29."
                    ),
                ],
                "future_transactions": [],
            }

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_date_quality,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_data_period_uses_validated_date_quality(
    monkeypatch,
):
    result = _run_period_intent(
        monkeypatch,
        intent="data_period",
        question="What period does our financial data cover?",
    )

    answer = result["answer"]

    assert "2023-12-31" in answer
    assert "2032-01-01" in answer
    assert "35,078" in answer
    assert "validated" in answer.lower()


def test_latest_transaction_date_uses_validated_posting_date(
    monkeypatch,
):
    result = _run_period_intent(
        monkeypatch,
        intent="latest_transaction_date",
        question="What is our latest transaction date?",
    )

    answer = result["answer"]

    assert "2032-01-01" in answer
    assert "latest validated posting date" in answer.lower()
    assert "current reporting period" in answer.lower()


def test_earliest_transaction_date_uses_validated_posting_date(
    monkeypatch,
):
    result = _run_period_intent(
        monkeypatch,
        intent="earliest_transaction_date",
        question="What is our earliest transaction date?",
    )

    answer = result["answer"]

    assert "2023-12-31" in answer
    assert "earliest validated posting date" in answer.lower()


def test_reporting_date_uses_date_quality_reporting_date(
    monkeypatch,
):
    result = _run_period_intent(
        monkeypatch,
        intent="reporting_date",
        question="What reporting date is AI-FOS using?",
    )

    answer = result["answer"]

    assert "2026-08-29" in answer
    assert "reporting date" in answer.lower()
    assert "future-dated" in answer.lower()


def test_date_quality_explains_valid_missing_invalid_and_future_dates(
    monkeypatch,
):
    result = _run_period_intent(
        monkeypatch,
        intent="date_quality",
        question=("Are there any date-quality issues " "in our General Ledger?"),
    )

    answer = result["answer"]

    assert "warning" in answer.lower()
    assert "35,078" in answer
    assert "35,070" in answer
    assert "3" in answer
    assert "5" in answer
    assert "10" in answer
    assert "future-dated" in answer.lower()


def test_future_transactions_are_preserved_but_identified_separately(
    monkeypatch,
):
    result = _run_period_intent(
        monkeypatch,
        intent="future_transactions",
        question="Do we have any future-dated transactions?",
    )

    answer = result["answer"]

    assert "10" in answer
    assert "2026-08-29" in answer
    assert "preserved" in answer.lower()
    assert "current-period" in answer.lower()


def _run_financial_trend_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "financial_trends",
        },
    )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_financial_trends(
        financial_model_folder,
        filename,
    ):
        if filename == "financial_trends.json":
            return {
                "status": "available",
                "latest_month_comparison": {
                    "period_type": "month",
                    "current_period": "2026-08",
                    "previous_period": "2026-07",
                    "revenue": {
                        "current_value": 1200.0,
                        "previous_value": 1000.0,
                        "change_amount": 200.0,
                        "change_percentage": 20.0,
                        "direction": "increased",
                    },
                    "expenses": {
                        "current_value": 700.0,
                        "previous_value": 800.0,
                        "change_amount": -100.0,
                        "change_percentage": -12.5,
                        "direction": "decreased",
                    },
                    "net_result": {
                        "current_value": 500.0,
                        "previous_value": 200.0,
                        "change_amount": 300.0,
                        "change_percentage": 150.0,
                        "direction": "increased",
                    },
                    "caution": ("The latest observed period may be " "incomplete."),
                },
                "latest_year_comparison": None,
            }

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_financial_trends,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_revenue_trend_uses_validated_trend_artifact(
    monkeypatch,
):
    result = _run_financial_trend_intent(
        monkeypatch,
        intent="revenue_trend",
        question="Is our revenue increasing?",
    )

    answer = result["answer"]

    assert "revenue increased" in answer.lower()
    assert "2026-07" in answer
    assert "2026-08" in answer
    assert "1,000.00" in answer
    assert "1,200.00" in answer
    assert "200.00" in answer
    assert "20.00%" in answer


def test_expense_trend_uses_validated_trend_artifact(
    monkeypatch,
):
    result = _run_financial_trend_intent(
        monkeypatch,
        intent="expense_trend",
        question="Are our expenses increasing?",
    )

    answer = result["answer"]

    assert "expenses decreased" in answer.lower()
    assert "800.00" in answer
    assert "700.00" in answer
    assert "-100.00" in answer
    assert "-12.50%" in answer


def test_net_result_trend_uses_validated_trend_artifact(
    monkeypatch,
):
    result = _run_financial_trend_intent(
        monkeypatch,
        intent="net_result_trend",
        question="How has our net result changed?",
    )

    answer = result["answer"]

    assert "net result increased" in answer.lower()
    assert "200.00" in answer
    assert "500.00" in answer
    assert "300.00" in answer
    assert "150.00%" in answer


def test_financial_trend_summary_reports_directions_without_judgment(
    monkeypatch,
):
    result = _run_financial_trend_intent(
        monkeypatch,
        intent="financial_trend_summary",
        question="How are our finances trending?",
    )

    answer = result["answer"]

    assert "revenue increased" in answer.lower()
    assert "expenses decreased" in answer.lower()
    assert "net result increased" in answer.lower()
    assert "without interpreting" in answer.lower()
    assert "automatically good or bad" in answer.lower()


def _run_financial_forecast_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "financial_forecast",
        },
    )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_financial_forecast(
        financial_model_folder,
        filename,
    ):
        if filename == "financial_forecast.json":
            return {
                "status": "available",
                "forecast_type": "baseline",
                "forecast_horizon_months": 3,
                "methodology": ("historical_average_run_rate"),
                "methodology_description": (
                    "The forecast uses recent validated " "historical monthly averages."
                ),
                "baseline": {
                    "average_monthly_revenue": 1250.0,
                    "average_monthly_expenses": 750.0,
                    "average_monthly_net_result": 500.0,
                },
                "forecast_series": [
                    {
                        "period": "2026-08",
                        "revenue": 1250.0,
                        "expenses": 750.0,
                        "net_result": 500.0,
                    },
                    {
                        "period": "2026-09",
                        "revenue": 1250.0,
                        "expenses": 750.0,
                        "net_result": 500.0,
                    },
                    {
                        "period": "2026-10",
                        "revenue": 1250.0,
                        "expenses": 750.0,
                        "net_result": 500.0,
                    },
                ],
                "forecast_totals": {
                    "revenue": 3750.0,
                    "expenses": 2250.0,
                    "net_result": 1500.0,
                },
                "confidence": {
                    "level": "Medium",
                    "history_month_count": 6,
                    "reason": (
                        "The baseline uses six validated " "historical monthly periods."
                    ),
                },
            }

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_financial_forecast,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_revenue_forecast_uses_validated_forecast_artifact(
    monkeypatch,
):
    result = _run_financial_forecast_intent(
        monkeypatch,
        intent="revenue_forecast",
        question="What is our revenue forecast?",
    )

    answer = result["answer"]

    assert "baseline revenue forecast" in answer.lower()
    assert "3,750.00" in answer
    assert "1,250.00" in answer
    assert "2026-08" in answer
    assert "2026-10" in answer
    assert "medium" in answer.lower()


def test_expense_forecast_uses_validated_forecast_artifact(
    monkeypatch,
):
    result = _run_financial_forecast_intent(
        monkeypatch,
        intent="expense_forecast",
        question="What are our projected expenses?",
    )

    answer = result["answer"]

    assert "baseline expense forecast" in answer.lower()
    assert "2,250.00" in answer
    assert "750.00" in answer
    assert "2026-08" in answer
    assert "2026-10" in answer


def test_net_result_forecast_reports_projected_surplus(
    monkeypatch,
):
    result = _run_financial_forecast_intent(
        monkeypatch,
        intent="net_result_forecast",
        question="What is our projected net result?",
    )

    answer = result["answer"]

    assert "projected surplus" in answer.lower()
    assert "1,500.00" in answer
    assert "500.00" in answer
    assert "medium" in answer.lower()


def test_financial_forecast_summary_is_explicitly_baseline(
    monkeypatch,
):
    result = _run_financial_forecast_intent(
        monkeypatch,
        intent="financial_forecast_summary",
        question="What does our financial forecast look like?",
    )

    answer = result["answer"]

    assert "baseline financial forecast" in answer.lower()
    assert "3,750.00" in answer
    assert "2,250.00" in answer
    assert "1,500.00" in answer
    assert "guaranteed future outcome" in answer.lower()

def _run_saved_scenario_intent(
    monkeypatch,
    intent: str,
    question: str,
    saved_scenarios: list[dict],
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "financial_scenario",
        },
    )

    monkeypatch.setattr(
        "app.services.scenario_history."
        "ScenarioHistoryService.list_scenarios",
        lambda financial_model_folder: saved_scenarios,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )

def _run_financial_scenario_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "financial_scenario",
        },
    )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_scenario_inputs(
        financial_model_folder,
        filename,
    ):
        if filename == "financial_forecast.json":
            return {
                "status": "available",
                "forecast_horizon_months": 3,
                "forecast_series": [
                    {
                        "period": "2026-09",
                        "revenue": 1000.0,
                        "expenses": 700.0,
                        "net_result": 300.0,
                    },
                    {
                        "period": "2026-10",
                        "revenue": 1000.0,
                        "expenses": 700.0,
                        "net_result": 300.0,
                    },
                    {
                        "period": "2026-11",
                        "revenue": 1000.0,
                        "expenses": 700.0,
                        "net_result": 300.0,
                    },
                ],
                "forecast_totals": {
                    "revenue": 3000.0,
                    "expenses": 2100.0,
                    "net_result": 900.0,
                },
            }

        if filename == "liquidity.json":
            return {
                "available_cash": 1200.0,
                "cash_runway_months": 6.0,
                "average_monthly_operating_expenses": 200.0,
            }

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_scenario_inputs,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_revenue_drop_scenario_uses_explicit_percentage(
    monkeypatch,
):
    result = _run_financial_scenario_intent(
        monkeypatch,
        intent="revenue_scenario",
        question="What happens if revenue drops 10%?",
    )

    answer = result["answer"]

    assert "Revenue Decrease 10.00%" in answer
    assert "3,000.00" in answer
    assert "2,700.00" in answer
    assert "900.00" in answer
    assert "600.00" in answer
    assert "-300.00" in answer
    assert "hypothetical" in answer.lower()
    assert "baseline forecast remains unchanged" in answer.lower()


def test_expense_increase_scenario_uses_explicit_percentage(
    monkeypatch,
):
    result = _run_financial_scenario_intent(
        monkeypatch,
        intent="expense_scenario",
        question="What if expenses increase 10%?",
    )

    answer = result["answer"]

    assert "Expense Increase 10.00%" in answer
    assert "2,100.00" in answer
    assert "2,310.00" in answer
    assert "900.00" in answer
    assert "690.00" in answer
    assert "-210.00" in answer

def test_combined_revenue_and_expense_scenario_uses_both_percentages(
    monkeypatch,
):
    captured = {}

    def fake_generate_financial_scenario(**kwargs):
        captured.update(kwargs)

        return {
            "status": "available",
            "baseline": {
                "revenue": 3000.0,
                "expenses": 2100.0,
                "net_result": 900.0,
            },
            "scenario": {
                "revenue": 2700.0,
                "expenses": 2205.0,
                "net_result": 495.0,
            },
            "impact": {
                "net_result_variance": -405.0,
                "net_result_direction": "deteriorated",
            },
        }

    monkeypatch.setattr(
        "app.services.ai_question_engine."
        "generate_financial_scenario",
        fake_generate_financial_scenario,
    )

    result = _run_financial_scenario_intent(
        monkeypatch,
        intent="revenue_scenario",
        question=(
            "What if revenue drops by 10% "
            "and expenses rise by 5%?"
        ),
    )

    assert captured["revenue_change_percentage"] == -10.0
    assert captured["expense_change_percentage"] == 5.0

    answer = result["answer"]

    assert "2,700.00" in answer
    assert "2,205.00" in answer
    assert "495.00" in answer
    assert "-405.00" in answer    


def test_scenario_without_percentage_does_not_invent_assumption(
    monkeypatch,
):
    result = _run_financial_scenario_intent(
        monkeypatch,
        intent="revenue_scenario",
        question="What happens if revenue changes?",
    )

    answer = result["answer"].lower()

    assert "assumption must be explicit" in answer
    assert "include a percentage" in answer


def test_scenario_with_percentage_but_no_direction_asks_for_direction(
    monkeypatch,
):
    result = _run_financial_scenario_intent(
        monkeypatch,
        intent="revenue_scenario",
        question="What happens if revenue changes by 10%?",
    )

    answer = result["answer"].lower()

    assert "direction is unclear" in answer
    assert "increases or decreases" in answer

def test_funding_scenario_intents_are_supported():
    assert (
        "expected_funding_change_scenario"
        in AIQuestionEngine.FUNDING_SCENARIO_INTENTS
    )
    assert (
        "expected_funding_failure_scenario"
        in AIQuestionEngine.FUNDING_SCENARIO_INTENTS
    )
    assert (
        "expected_funding_basis_scenario"
        in AIQuestionEngine.FUNDING_SCENARIO_INTENTS
    )

def _run_funding_scenario_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "funding_scenario",
        },
    )

    original_load_json = (
        engine.financial_model_service.load_json
    )

    def load_json_with_funding_scenario_inputs(
        financial_model_folder,
        filename,
    ):
        if filename == "expected_funding_intelligence.json":
            return {
                "status": "available",
                "summary": {
                    "record_count": 2,
                    "minimum_pipeline_value": 300000.0,
                    "most_likely_pipeline_value": 500000.0,
                    "maximum_pipeline_value": 700000.0,
                    "probability_weighted_expected_funding": 350000.0,
                },
                "records": [
                    {
                        "expected_funding_code": "EF-001",
                        "funding_name": "Ford Proposal",
                        "minimum_amount": 100000.0,
                        "most_likely_amount": 200000.0,
                        "maximum_amount": 300000.0,
                        "probability_weighted_amount": 100000.0,
                    },
                    {
                        "expected_funding_code": "EF-002",
                        "funding_name": "OSF Proposal",
                        "minimum_amount": 200000.0,
                        "most_likely_amount": 300000.0,
                        "maximum_amount": 400000.0,
                        "probability_weighted_amount": 250000.0,
                    },
                ],
            }

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_funding_scenario_inputs,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_expected_funding_change_scenario_uses_explicit_percentage(
    monkeypatch,
):
    result = _run_funding_scenario_intent(
        monkeypatch,
        intent="expected_funding_change_scenario",
        question="What if expected funding decreases by 20%?",
    )

    answer = result["answer"]

    assert "500,000.00" in answer
    assert "400,000.00" in answer
    assert "-100,000.00" in answer
    assert "prospective" in answer.lower()
    assert "secured funding" in answer.lower()


def test_expected_funding_failure_scenario_uses_explicit_code(
    monkeypatch,
):
    result = _run_funding_scenario_intent(
        monkeypatch,
        intent="expected_funding_failure_scenario",
        question=(
            "What happens if expected grant EF-001 "
            "does not materialize?"
        ),
    )

    answer = result["answer"]

    assert "EF-001" in answer
    assert "500,000.00" in answer
    assert "300,000.00" in answer
    assert "-200,000.00" in answer


def test_expected_funding_basis_scenario_uses_maximum_basis(
    monkeypatch,
):
    result = _run_funding_scenario_intent(
        monkeypatch,
        intent="expected_funding_basis_scenario",
        question="Show me the maximum expected funding scenario.",
    )

    answer = result["answer"]

    assert "maximum" in answer.lower()
    assert "700,000.00" in answer

def _run_forward_risk_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = _build_funding_engine()

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "forward_risk",
        },
    )

    original_load_json = engine.financial_model_service.load_json

    def load_json_with_forward_risks(
        financial_model_folder,
        filename,
    ):
        if filename == "forward_risks.json":
            return [
                {
                    "severity": "High",
                    "category": "Operating Performance",
                    "title": "Forecast operating deficit",
                    "evidence": (
                        "The validated baseline forecast " "projects a future deficit."
                    ),
                    "recommendation": ("Review forecast deficit drivers."),
                },
                {
                    "severity": "High",
                    "category": "Funding",
                    "title": "Forward Funding Gap exposure",
                    "evidence": ("The validated Funding Gap remains " "material."),
                    "recommendation": ("Prioritize funding actions."),
                },
            ]

        return original_load_json(
            financial_model_folder=financial_model_folder,
            filename=filename,
        )

    monkeypatch.setattr(
        engine.financial_model_service,
        "load_json",
        load_json_with_forward_risks,
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_forward_risk_summary_uses_validated_forward_risks(
    monkeypatch,
):
    result = _run_forward_risk_intent(
        monkeypatch,
        intent="forward_risk_summary",
        question="What risks are emerging?",
    )

    answer = result["answer"].lower()

    assert "2 forward-looking financial risk" in answer
    assert "forecast operating deficit" in answer
    assert "forward funding gap exposure" in answer


def test_forward_high_risks_returns_high_emerging_risks(
    monkeypatch,
):
    result = _run_forward_risk_intent(
        monkeypatch,
        intent="forward_high_risks",
        question="What major future risks should we worry about?",
    )

    answer = result["answer"].lower()

    assert "most significant emerging financial risks" in answer
    assert "forecast operating deficit" in answer
    assert "forward funding gap exposure" in answer


def test_forward_funding_risks_filters_funding_risks(
    monkeypatch,
):
    result = _run_forward_risk_intent(
        monkeypatch,
        intent="forward_funding_risks",
        question="What future funding risks do we have?",
    )

    answer = result["answer"].lower()

    assert "forward-looking funding risks" in answer
    assert "forward funding gap exposure" in answer
    assert "forecast operating deficit" not in answer


def test_forward_operating_risks_filters_operating_risks(
    monkeypatch,
):
    result = _run_forward_risk_intent(
        monkeypatch,
        intent="forward_operating_risks",
        question="What operating risks are emerging?",
    )

    answer = result["answer"].lower()

    assert "forward-looking operating risks" in answer
    assert "forecast operating deficit" in answer
    assert "forward funding gap exposure" not in answer


def _run_financial_opportunity_intent(
    monkeypatch,
    intent: str,
    question: str,
):
    engine = AIQuestionEngine(
        workspace_service=FakeWorkspaceService(),
        knowledge_reader=FakeKnowledgeReader(),
        financial_intelligence_service=FakeFinancialIntelligenceService(),
        financial_model_service=FakeFinancialModelService(),
    )

    monkeypatch.setattr(
        engine.question_classifier,
        "classify",
        lambda question: {
            "intent": intent,
            "domain": "financial_opportunity",
        },
    )

    return engine.answer(
        question=question,
        organisation_id="test-org",
    )


def test_financial_opportunity_summary_uses_validated_opportunities(
    monkeypatch,
):
    result = _run_financial_opportunity_intent(
        monkeypatch=monkeypatch,
        intent="financial_opportunity_summary",
        question="What financial opportunities do we have?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "2 validated financial opportunities" in answer
    assert "Secured funding coverage opportunity" in answer
    assert "Strong liquidity capacity" in answer


def test_high_financial_opportunities_returns_high_priority_only(
    monkeypatch,
):
    result = _run_financial_opportunity_intent(
        monkeypatch=monkeypatch,
        intent="high_financial_opportunities",
        question="What are our highest financial opportunities?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "Secured funding coverage opportunity" in answer
    assert "Strong liquidity capacity" not in answer


def test_funding_opportunities_filters_funding_items(
    monkeypatch,
):
    result = _run_financial_opportunity_intent(
        monkeypatch=monkeypatch,
        intent="funding_opportunities",
        question="What funding opportunities do we have?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "Secured funding coverage opportunity" in answer
    assert "Strong liquidity capacity" not in answer


def test_liquidity_opportunities_filters_liquidity_items(
    monkeypatch,
):
    result = _run_financial_opportunity_intent(
        monkeypatch=monkeypatch,
        intent="liquidity_opportunities",
        question="What liquidity opportunities do we have?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "Strong liquidity capacity" in answer
    assert "Secured funding coverage opportunity" not in answer

def test_combined_scenario_intent_is_supported():
    assert "combined_scenario" in AIQuestionEngine.FINANCIAL_SCENARIO_INTENTS

def test_financial_scenario_includes_decision_intelligence(
    monkeypatch,
):
    captured = {}

    def fake_generate_scenario_decision_intelligence(
        scenario_result,
    ):
        captured["scenario_result"] = scenario_result

        return {
            "status": "available",
            "severity": "High",
            "decision_signal": "Negative",
            "management_attention": "Priority review",
            "decision_factors": [
                "Projected net result deteriorates materially.",
                "Projected liquidity weakens.",
            ],
            "recommended_actions": [
                "Review the revenue downside assumptions.",
                "Protect available liquidity.",
            ],
        }

    monkeypatch.setattr(
        "app.services.ai_question_engine."
        "generate_scenario_decision_intelligence",
        fake_generate_scenario_decision_intelligence,
    )

    result = _run_financial_scenario_intent(
        monkeypatch=monkeypatch,
        intent="revenue_scenario",
        question="What happens if revenue drops 10%?",
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert captured["scenario_result"]["status"] == "available"

    assert "High" in answer
    assert "Negative" in answer
    assert "Priority review" in answer

    assert "Projected net result deteriorates materially." in answer
    assert "Projected liquidity weakens." in answer

    assert "Review the revenue downside assumptions." in answer
    assert "Protect available liquidity." in answer


def test_scenario_decision_intelligence_preserves_financial_scenario_numbers(
    monkeypatch,
):
    def fake_generate_scenario_decision_intelligence(
        scenario_result,
    ):
        return {
            "status": "available",
            "severity": "High",
            "decision_signal": "Negative",
            "management_attention": "Priority review",
            "decision_factors": [
                "Projected performance deteriorates.",
            ],
            "recommended_actions": [
                "Review the scenario assumptions.",
            ],
        }

    monkeypatch.setattr(
        "app.services.ai_question_engine."
        "generate_scenario_decision_intelligence",
        fake_generate_scenario_decision_intelligence,
    )

    result = _run_financial_scenario_intent(
        monkeypatch=monkeypatch,
        intent="revenue_scenario",
        question="What happens if revenue drops 10%?",
    )

    answer = result["answer"]

    assert "3,000.00" in answer
    assert "2,700.00" in answer
    assert "900.00" in answer
    assert "600.00" in answer
    assert "-300.00" in answer

    assert "baseline forecast remains unchanged" in answer.lower()


def test_combined_scenario_includes_decision_intelligence(
    monkeypatch,
):
    def fake_generate_scenario_decision_intelligence(
        scenario_result,
    ):
        return {
            "status": "available",
            "severity": "Critical",
            "decision_signal": "Negative",
            "management_attention": "Immediate management attention",
            "decision_factors": [
                "Revenue declines while expenses increase.",
            ],
            "recommended_actions": [
                "Review both revenue and expense assumptions.",
            ],
        }

    monkeypatch.setattr(
        "app.services.ai_question_engine."
        "generate_scenario_decision_intelligence",
        fake_generate_scenario_decision_intelligence,
    )

    result = _run_financial_scenario_intent(
        monkeypatch=monkeypatch,
        intent="combined_scenario",
        question=(
            "What if revenue drops by 10% "
            "and expenses rise by 5%?"
        ),
    )

    answer = result["answer"]

    assert result["status"] == "success"

    assert "Critical" in answer
    assert "Negative" in answer
    assert "Immediate management attention" in answer

    assert "Revenue declines while expenses increase." in answer
    assert "Review both revenue and expense assumptions." in answer    

def test_scenario_comparison_requires_two_explicit_scenarios(
    monkeypatch,
):
    result = _run_financial_scenario_intent(
        monkeypatch=monkeypatch,
        intent="scenario_comparison",
        question="Which scenario is safer?",
    )

    assert result["status"] == "success"

    answer = result["answer"].lower()

    assert "two" in answer
    assert "scenario" in answer
    assert (
        "explicit" in answer
        or "provide" in answer
        or "specify" in answer
    ) 

def test_inline_scenario_comparison_prefers_less_harmful_scenario(
    monkeypatch,
):
    result = _run_financial_scenario_intent(
        monkeypatch=monkeypatch,
        intent="scenario_comparison",
        question=(
            "Compare revenue decreasing 10% "
            "versus revenue decreasing 20%."
        ),
    )

    assert result["status"] == "success"

    answer = result["answer"].lower()

    assert "scenario a" in answer
    assert "scenario b" in answer
    assert "10" in answer
    assert "20" in answer

    assert (
        "preferred" in answer
        or "safer" in answer
        or "better" in answer
    )

def test_inline_scenario_comparison_does_not_invent_missing_direction(
    monkeypatch,
):
    result = _run_financial_scenario_intent(
        monkeypatch=monkeypatch,
        intent="scenario_comparison",
        question=(
            "Compare revenue decreasing 10% "
            "versus expenses 20%."
        ),
    )

    assert result["status"] == "success"

    answer = result["answer"].lower()

    assert "both scenarios" in answer
    assert "explicit" in answer

    assert (
        "increase" in answer
        or "decrease" in answer
    )

    assert "preferred scenario" not in answer 

def test_inline_scenario_comparison_does_not_invent_missing_percentage(
    monkeypatch,
):
    result = _run_financial_scenario_intent(
        monkeypatch=monkeypatch,
        intent="scenario_comparison",
        question=(
            "Compare revenue decreasing 10% "
            "versus expenses increasing."
        ),
    )

    assert result["status"] == "success"

    answer = result["answer"].lower()

    assert "both scenarios" in answer
    assert "explicit" in answer
    assert "percentage" in answer

    assert "preferred scenario" not in answer   

def test_inline_scenario_comparison_accepts_zero_percentage(
    monkeypatch,
):
    result = _run_financial_scenario_intent(
        monkeypatch=monkeypatch,
        intent="scenario_comparison",
        question=(
            "Compare revenue decreasing 0% "
            "versus revenue decreasing 10%."
        ),
    )

    assert result["status"] == "success"

    answer = result["answer"].lower()

    assert "scenario a" in answer
    assert "scenario b" in answer
    assert "0" in answer
    assert "10" in answer

    assert (
        "preferred" in answer
        or "safer" in answer
        or "better" in answer
    )
def test_inline_scenario_comparison_does_not_double_invert_negative_percentage(
    monkeypatch,
):
    result = _run_financial_scenario_intent(
        monkeypatch=monkeypatch,
        intent="scenario_comparison",
        question=(
            "Compare revenue decreasing -10% "
            "versus revenue decreasing 20%."
        ),
    )

    assert result["status"] == "success"

    answer = result["answer"].lower()

    assert "scenario a" in answer
    assert "scenario b" in answer
    assert "10" in answer
    assert "20" in answer

    assert (
        "preferred" in answer
        or "safer" in answer
        or "better" in answer
    )        
def test_inline_scenario_comparison_supports_cross_type_scenarios(
    monkeypatch,
):
    result = _run_financial_scenario_intent(
        monkeypatch=monkeypatch,
        intent="scenario_comparison",
        question=(
            "Compare revenue decreasing 10% "
            "versus expenses increasing 20%."
        ),
    )

    assert result["status"] == "success"

    answer = result["answer"].lower()

    assert "scenario a" in answer
    assert "scenario b" in answer
    assert "10" in answer
    assert "20" in answer

    assert (
        "preferred" in answer
        or "safer" in answer
        or "better" in answer
    )

def test_saved_scenario_list_uses_scenario_history(
    monkeypatch,
):
    saved_scenarios = [
        {
            "scenario_id": "scenario-1",
            "scenario_name": "Revenue Down 10%",
            "financial_scenario": {},
            "scenario_decision_intelligence": {},
        },
        {
            "scenario_id": "scenario-2",
            "scenario_name": "Expense Up 15%",
            "financial_scenario": {},
            "scenario_decision_intelligence": {},
        },
    ]

    result = _run_saved_scenario_intent(
        monkeypatch=monkeypatch,
        intent="saved_scenario_list",
        question="Show me my saved scenarios",
        saved_scenarios=saved_scenarios,
    )

    assert result["status"] == "success"

    answer = result["answer"]

    assert "Revenue Down 10%" in answer
    assert "Expense Up 15%" in answer


def test_saved_scenario_comparison_reuses_saved_decision_intelligence(
    monkeypatch,
):
    saved_scenarios = [
        {
            "scenario_id": "scenario-1",
            "scenario_name": "Revenue Down 10%",
            "financial_scenario": {
                "scenario_name": "Revenue Down 10%",
            },
            "scenario_decision_intelligence": {
                "status": "available",
                "severity": "medium",
                "management_attention": "review",
                "decision_signal": "negative",
            },
        },
        {
            "scenario_id": "scenario-2",
            "scenario_name": "Revenue Down 20%",
            "financial_scenario": {
                "scenario_name": "Revenue Down 20%",
            },
            "scenario_decision_intelligence": {
                "status": "available",
                "severity": "high",
                "management_attention": "priority_review",
                "decision_signal": "negative",
            },
        },
    ]

    captured = {}

    def fake_generate_comparison(
        scenario_a,
        scenario_b,
    ):
        captured["scenario_a"] = scenario_a
        captured["scenario_b"] = scenario_b

        return {
            "status": "available",
            "comparison_signal": "clear_preference",
            "preferred_scenario": "Scenario A",
        }

    def fail_if_financial_scenario_is_rerun(*args, **kwargs):
        raise AssertionError(
            "Saved scenarios must not rerun "
            "generate_financial_scenario()."
        )

    monkeypatch.setattr(
        "app.services.ai_question_engine."
        "generate_scenario_comparison_intelligence",
        fake_generate_comparison,
    )

    monkeypatch.setattr(
        "app.services.ai_question_engine."
        "generate_financial_scenario",
        fail_if_financial_scenario_is_rerun,
    )

    result = _run_saved_scenario_intent(
        monkeypatch=monkeypatch,
        intent="saved_scenario_comparison",
        question=(
            "Compare my saved Revenue Down 10% "
            "versus Revenue Down 20%"
        ),
        saved_scenarios=saved_scenarios,
    )

    assert result["status"] == "success"

    assert captured["scenario_a"] == (
        saved_scenarios[0]["scenario_decision_intelligence"]
    )

    assert captured["scenario_b"] == (
        saved_scenarios[1]["scenario_decision_intelligence"]
    )

    answer = result["answer"]

    assert "Revenue Down 10%" in answer
    assert "Revenue Down 20%" in answer

    assert (
        "preferred" in answer.lower()
        or "safer" in answer.lower()
    ) 

def test_saved_scenario_list_handles_empty_history(
    monkeypatch,
):
    result = _run_saved_scenario_intent(
        monkeypatch=monkeypatch,
        intent="saved_scenario_list",
        question="Show me my saved scenarios",
        saved_scenarios=[],
    )

    assert result["status"] == "success"

    answer = result["answer"].lower()

    assert "does not currently have any saved" in answer
    assert "scenario" in answer


def test_saved_scenario_comparison_requires_two_matching_saved_scenarios(
    monkeypatch,
):
    saved_scenarios = [
        {
            "scenario_id": "scenario-1",
            "scenario_name": "Revenue Down 10%",
            "financial_scenario": {},
            "scenario_decision_intelligence": {
                "status": "available",
            },
        },
    ]

    result = _run_saved_scenario_intent(
        monkeypatch=monkeypatch,
        intent="saved_scenario_comparison",
        question=(
            "Compare my saved Revenue Down 10% "
            "versus Revenue Down 20%"
        ),
        saved_scenarios=saved_scenarios,
    )

    assert result["status"] == "success"

    answer = result["answer"].lower()

    assert "exactly two" in answer
    assert "saved scenario" in answer


def test_saved_scenario_comparison_requires_available_decision_intelligence(
    monkeypatch,
):
    saved_scenarios = [
        {
            "scenario_id": "scenario-1",
            "scenario_name": "Revenue Down 10%",
            "financial_scenario": {},
            "scenario_decision_intelligence": {
                "status": "available",
            },
        },
        {
            "scenario_id": "scenario-2",
            "scenario_name": "Revenue Down 20%",
            "financial_scenario": {},
            "scenario_decision_intelligence": {
                "status": "not_available",
            },
        },
    ]

    result = _run_saved_scenario_intent(
        monkeypatch=monkeypatch,
        intent="saved_scenario_comparison",
        question=(
            "Compare my saved Revenue Down 10% "
            "versus Revenue Down 20%"
        ),
        saved_scenarios=saved_scenarios,
    )

    assert result["status"] == "success"

    answer = result["answer"].lower()

    assert "cannot compare" in answer
    assert "decision intelligence" in answer              


def test_core_cost_coverage_summary_uses_verified_intelligence(
    monkeypatch,
):
    result = _run_core_cost_coverage_intent(
        monkeypatch=monkeypatch,
        intent="core_cost_coverage_summary",
        question="How much of our core costs are covered?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "1,000.00 USD" in answer
    assert "300.00 USD" in answer
    assert "200.00 USD" in answer
    assert "100.00 USD" in answer
    assert "400.00 USD" in answer
    assert "60.00%" in answer
    assert result["financial_data_used"] is True




def test_indirect_recovery_status_preserves_lifecycle(
    monkeypatch,
):
    result = _run_core_cost_coverage_intent(
        monkeypatch=monkeypatch,
        intent="indirect_recovery_status",
        question="What is the status of our indirect recovery?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "250.00 USD" in answer
    assert "200.00 USD" in answer
    assert "150.00 USD" in answer
    assert result["financial_data_used"] is True


def test_core_cost_gap_uses_verified_intelligence(
    monkeypatch,
):
    result = _run_core_cost_coverage_intent(
        monkeypatch=monkeypatch,
        intent="core_cost_gap",
        question="What is our remaining core cost gap?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "400.00 USD" in answer
    assert "60.00%" in answer
    assert result["financial_data_used"] is True



def test_core_cost_coverage_sources_use_verified_source_records(
    monkeypatch,
):
    result = _run_core_cost_coverage_intent(
        monkeypatch=monkeypatch,
        intent="core_cost_coverage_sources",
        question="What are the sources covering our core costs?",
    )

    answer = result["answer"]

    assert result["status"] == "success"
    assert "GRANT-001" in answer
    assert "300.00 USD" in answer
    assert "INDIRECT-001" in answer
    assert "200.00 USD" in answer
    assert "CORE-001" in answer
    assert "100.00 USD" in answer
    assert result["financial_data_used"] is True
