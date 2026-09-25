from app.services.funding_scenarios import (
    generate_funding_scenario,
)


def _expected_funding_intelligence():
    return {
        "status": "available",
        "summary": {
            "record_count": 2,
            "record_count_requiring_review": 0,
            "minimum_pipeline_value": 300000.0,
            "most_likely_pipeline_value": 500000.0,
            "maximum_pipeline_value": 700000.0,
            "probability_weighted_expected_funding": 350000.0,
            "weighted_record_count": 2,
        },
        "records": [
            {
                "expected_funding_code": "EF-001",
                "funding_name": "Ford Proposal",
                "donor_code": "FORD",
                "donor_name": "Ford Foundation",
                "stage": "Proposal Submitted",
                "probability_percentage": 50.0,
                "minimum_amount": 100000.0,
                "most_likely_amount": 200000.0,
                "maximum_amount": 300000.0,
                "probability_weighted_amount": 100000.0,
                "requires_review": False,
                "review_reasons": [],
            },
            {
                "expected_funding_code": "EF-002",
                "funding_name": "OSF Proposal",
                "donor_code": "OSF",
                "donor_name": "Open Society Foundations",
                "stage": "Advanced",
                "probability_percentage": 62.5,
                "minimum_amount": 200000.0,
                "most_likely_amount": 300000.0,
                "maximum_amount": 400000.0,
                "probability_weighted_amount": 187500.0,
                "requires_review": False,
                "review_reasons": [],
            },
        ],
        "controls": {
            "prospective_funding_only": True,
            "treated_as_secured_funding": False,
            "expected_funding_not_assumed_revenue": True,
            "expected_funding_not_assumed_cash": True,
        },
    }


def test_percentage_reduction_scenario():
    result = generate_funding_scenario(
        expected_funding_intelligence=(
            _expected_funding_intelligence()
        ),
        scenario_name="Expected Funding Down 20%",
        expected_funding_change_percentage=-20.0,
    )

    assert result["status"] == "available"

    assert (
        result["baseline"][
            "most_likely_pipeline_value"
        ]
        == 500000.0
    )

    assert (
        result["scenario"][
            "most_likely_pipeline_value"
        ]
        == 400000.0
    )

    assert (
        result["impact"][
            "most_likely_pipeline_variance"
        ]
        == -100000.0
    )


def test_expected_grant_failure_by_code():
    result = generate_funding_scenario(
        expected_funding_intelligence=(
            _expected_funding_intelligence()
        ),
        scenario_name="Ford Proposal Fails",
        failed_expected_funding_codes=[
            "EF-001",
        ],
    )

    assert result["status"] == "available"

    assert (
        result["scenario"][
            "most_likely_pipeline_value"
        ]
        == 300000.0
    )

    assert (
        result["impact"][
            "most_likely_pipeline_variance"
        ]
        == -200000.0
    )


def test_minimum_scenario_uses_minimum_pipeline():
    result = generate_funding_scenario(
        expected_funding_intelligence=(
            _expected_funding_intelligence()
        ),
        scenario_name="Minimum Funding Case",
        scenario_basis="minimum",
    )

    assert (
        result["scenario"][
            "selected_pipeline_value"
        ]
        == 300000.0
    )


def test_maximum_scenario_uses_maximum_pipeline():
    result = generate_funding_scenario(
        expected_funding_intelligence=(
            _expected_funding_intelligence()
        ),
        scenario_name="Maximum Funding Case",
        scenario_basis="maximum",
    )

    assert (
        result["scenario"][
            "selected_pipeline_value"
        ]
        == 700000.0
    )


def test_expected_funding_remains_non_secured():
    result = generate_funding_scenario(
        expected_funding_intelligence=(
            _expected_funding_intelligence()
        ),
        scenario_name="Funding Scenario",
    )

    assert (
        result["controls"][
            "prospective_funding_only"
        ]
        is True
    )

    assert (
        result["controls"][
            "treated_as_secured_funding"
        ]
        is False
    )

    assert (
        result["controls"][
            "treated_as_revenue"
        ]
        is False
    )

    assert (
        result["controls"][
            "treated_as_cash"
        ]
        is False
    )


def test_missing_expected_funding_intelligence_is_not_available():
    result = generate_funding_scenario(
        expected_funding_intelligence=None,
        scenario_name="Unavailable Funding Scenario",
    )

    assert result["status"] == "not_available"