from app.organization import Organization


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


def test_run_funding_scenario():
    organization = Organization()

    organization.expected_funding_intelligence = (
        _expected_funding_intelligence()
    )

    result = organization.run_funding_scenario(
        scenario_name="Expected Funding Down 20%",
        expected_funding_change_percentage=-20.0,
    )

    assert result["status"] == "available"

    assert (
        result["scenario"][
            "most_likely_pipeline_value"
        ]
        == 400000.0
    )

    assert (
        organization.funding_scenario
        == result
    )


def test_run_funding_scenario_preserves_funding_gap():
    organization = Organization()

    organization.expected_funding_intelligence = (
        _expected_funding_intelligence()
    )

    organization.funding_gap = {
        "status": "available",
        "total_funding_gap": 250000.0,
    }

    baseline_funding_gap = dict(
        organization.funding_gap
    )

    organization.run_funding_scenario(
        scenario_name="Ford Proposal Fails",
        failed_expected_funding_codes=[
            "EF-001",
        ],
    )

    assert (
        organization.funding_gap
        == baseline_funding_gap
    )


def test_run_funding_scenario_without_expected_funding():
    organization = Organization()

    result = organization.run_funding_scenario(
        scenario_name="Unavailable Scenario",
    )

    assert result["status"] == "not_available"