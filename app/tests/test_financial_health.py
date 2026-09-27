from app.services.financial_health import calculate_financial_health


def _calculate_health(
    *,
    budget_mapping_intelligence=None,
):
    return calculate_financial_health(
        income_statement={},
        balance_sheet={},
        budget_dashboard={
            "budget_health": {
                "over_budget_count": 27,
                "no_budget_count": 25,
            },
            "executive_summary": {
                "total_budget": 4725605.92,
                "budgeted_actual": 4346959.89,
                "unbudgeted_actual": 359941.88,
            },
        },
        grant_diagnostics={},
        liquidity={},
        funding_gap={},
        budget_mapping_intelligence=budget_mapping_intelligence,
    )


def test_budget_control_score_remains_strict_with_mapping_intelligence():
    result = _calculate_health(
        budget_mapping_intelligence={
            "summary": {
                "exception_budget_line_count": 25,
                "broader_match_actual": 296215.66,
                "no_budget_identified_actual": 63726.22,
                "total_exception_actual": 359941.88,
            }
        }
    )

    budget_control = result["categories"]["budget_control"]

    assert budget_control["score"] == 12
    assert budget_control["maximum"] == 20


def test_budget_control_reason_explains_mapping_evidence():
    result = _calculate_health(
        budget_mapping_intelligence={
            "summary": {
                "exception_budget_line_count": 25,
                "broader_match_actual": 296215.66,
                "no_budget_identified_actual": 63726.22,
                "total_exception_actual": 359941.88,
            }
        }
    )

    reason = result["categories"]["budget_control"]["reason"]

    assert "359,941.88" in reason
    assert "296,215.66" in reason
    assert "63,726.22" in reason
    assert "broader budget" in reason.lower()
    assert "review" in reason.lower()