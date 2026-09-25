from app.services.cfo_insights import generate_funding_gap_insights


def test_funding_gap_insights_include_exposure_explanations():
    funding_gap = {
        "summary": {
            "remaining_requirement": 1000.0,
            "applied_secured_funding": 400.0,
            "funding_gap": 600.0,
            "applied_coverage_percentage": 40.0,
            "period_ineligible_funding_exposure": 200.0,
            "period_unknown_funding_exposure": 100.0,
            "dimension_incompatible_funding_exposure": 50.0,
            "requirements_with_period_ineligible_funding": 1,
            "requirements_with_period_unknown_funding": 1,
            "requirements_with_dimension_incompatible_funding": 1,
        }
    }

    insights = generate_funding_gap_insights(funding_gap)

    combined = " ".join(insights)

    assert "$1,000.00" in combined
    assert "$400.00" in combined
    assert "$600.00" in combined
    assert "40.00%" in combined

    assert "$200.00" in combined
    assert "$100.00" in combined
    assert "$50.00" in combined

    assert "grant period" in combined.lower()
    assert "missing or incomplete" in combined.lower()
    assert "dimensions conflict" in combined.lower()

    assert "must not be added together" in combined.lower()