from app.services.expected_funding_mapper import (
    map_expected_funding_columns,
)


def test_maps_standard_expected_funding_headers():
    headers = [
        "Expected Funding Code",
        "Funding Name",
        "Donor Code",
        "Donor Name",
        "Stage",
        "Probability %",
        "Minimum Amount",
        "Most Likely Amount",
        "Maximum Amount",
        "Expected Decision Date",
        "Expected First Payment Date",
        "Original Currency",
        "Reporting Currency",
        "Program Code",
        "Project Code",
        "Budget Line Code",
        "Notes",
    ]

    mapping = map_expected_funding_columns(
        headers
    )

    assert mapping[
        "expected_funding_code"
    ] == "Expected Funding Code"

    assert mapping[
        "funding_name"
    ] == "Funding Name"

    assert mapping[
        "donor_code"
    ] == "Donor Code"

    assert mapping[
        "donor_name"
    ] == "Donor Name"

    assert mapping[
        "stage"
    ] == "Stage"

    assert mapping[
        "probability_percentage"
    ] == "Probability %"

    assert mapping[
        "minimum_amount"
    ] == "Minimum Amount"

    assert mapping[
        "most_likely_amount"
    ] == "Most Likely Amount"

    assert mapping[
        "maximum_amount"
    ] == "Maximum Amount"

    assert mapping[
        "expected_decision_date"
    ] == "Expected Decision Date"

    assert mapping[
        "expected_first_payment_date"
    ] == "Expected First Payment Date"


def test_maps_common_probability_aliases():
    headers = [
        "Probability Percentage",
    ]

    mapping = map_expected_funding_columns(
        headers
    )

    assert mapping[
        "probability_percentage"
    ] == "Probability Percentage"


def test_maps_expected_grant_code_alias():
    headers = [
        "Expected Grant Code",
    ]

    mapping = map_expected_funding_columns(
        headers
    )

    assert mapping[
        "expected_funding_code"
    ] == "Expected Grant Code"


def test_maps_grant_name_alias():
    headers = [
        "Grant Name",
    ]

    mapping = map_expected_funding_columns(
        headers
    )

    assert mapping[
        "funding_name"
    ] == "Grant Name"


def test_maps_amount_scenario_aliases():
    headers = [
        "Minimum",
        "Most Likely",
        "Maximum",
    ]

    mapping = map_expected_funding_columns(
        headers
    )

    assert mapping[
        "minimum_amount"
    ] == "Minimum"

    assert mapping[
        "most_likely_amount"
    ] == "Most Likely"

    assert mapping[
        "maximum_amount"
    ] == "Maximum"


def test_maps_expected_payment_date_alias():
    headers = [
        "Expected Payment Date",
    ]

    mapping = map_expected_funding_columns(
        headers
    )

    assert mapping[
        "expected_first_payment_date"
    ] == "Expected Payment Date"


def test_unknown_headers_are_not_mapped():
    headers = [
        "Random Column",
        "Another Unknown Field",
    ]

    mapping = map_expected_funding_columns(
        headers
    )

    assert mapping == {}


def test_mapping_is_case_insensitive():
    headers = [
        "EXPECTED FUNDING CODE",
        "probability %",
        "MOST LIKELY AMOUNT",
    ]

    mapping = map_expected_funding_columns(
        headers
    )

    assert mapping[
        "expected_funding_code"
    ] == "EXPECTED FUNDING CODE"

    assert mapping[
        "probability_percentage"
    ] == "probability %"

    assert mapping[
        "most_likely_amount"
    ] == "MOST LIKELY AMOUNT"