from openpyxl import Workbook

from app.services.excel_reader import (
    inspect_workbook,
)


def test_budget_workbook_reads_expected_funding_sheet(
    tmp_path,
):
    file_path = (
        tmp_path
        / "budget_with_expected_funding.xlsx"
    )

    workbook = Workbook()

    #
    # First sheet must be detectable as a Budget
    # workbook by AI-FOS.
    #
    budget_sheet = workbook.active
    budget_sheet.title = "Available Budget"

    budget_sheet.append(
        [
            "Budget Line Code",
            "Budget Line Code Name",
            "Budget Notes",
            "Total Original Budget (USD)",
        ]
    )

    budget_sheet.append(
        [
            "BL-001",
            "Personnel",
            "Secured budget",
            100000,
        ]
    )

    #
    # Separate prospective funding dataset.
    #
    expected_sheet = workbook.create_sheet(
        "Expected Funding"
    )

    expected_sheet.append(
        [
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
    )

    expected_sheet.append(
        [
            "EF-001",
            "Core Support Proposal",
            "OSF",
            "Open Society Foundations",
            "Proposal Submitted",
            75,
            400000,
            500000,
            600000,
            "2026-11-15",
            "2027-01-15",
            "USD",
            "USD",
            "CORE",
            "PRJ-001",
            "BL-001",
            "Management estimate",
        ]
    )

    workbook.save(
        file_path
    )

    result = inspect_workbook(
        str(file_path)
    )

    assert result[
        "document_type"
    ] == "budget"

    assert result[
        "expected_funding_sheet_name"
    ] == "Expected Funding"

    assert len(
        result[
            "expected_funding_lines"
        ]
    ) == 1

    expected_funding = result[
        "expected_funding_lines"
    ][0]

    assert (
        expected_funding[
            "expected_funding_code"
        ]
        == "EF-001"
    )

    assert (
        expected_funding[
            "most_likely_amount"
        ]
        == 500000.0
    )

    assert (
        expected_funding[
            "probability_percentage"
        ]
        == 75.0
    )

    assert (
        expected_funding[
            "requires_review"
        ]
        is False
    )