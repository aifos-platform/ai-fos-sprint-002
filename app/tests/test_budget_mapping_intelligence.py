from app.services.budget_mapping_intelligence import (
    generate_budget_mapping_intelligence,
)


def test_identifies_broader_budget_match_when_budget_line_differs():
    budget_lines = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNGA001",
            "budget_line_name": "General & Administrative (G&A)",
            "budget": 500000.0,
        }
    ]

    transactions = [
        {
            "fund": "FR0007-0004",
            "donor_line": "OSF807",
            "program": "RC101",
            "category": "CAT008",
            "budget_line": "UNRC011",
            "budget_actual_amount": 6000.0,
        }
    ]

    result = generate_budget_mapping_intelligence(
        budget_lines=budget_lines,
        transactions=transactions,
    )

    assert result["summary"]["broader_match_evidence_count"] == 1
    assert result["summary"]["broader_match_actual"] == 6000.0
    assert result["summary"]["no_budget_identified_evidence_count"] == 0
    assert result["summary"]["no_budget_identified_actual"] == 0.0

    item = result["items"][0]

    assert item["status"] == "Broader Budget Match - Review Required"
    assert item["actual_budget_line_code"] == "UNRC011"
    assert item["matched_budget_line_code"] == "UNGA001"
    assert item["actual"] == 6000.0

def test_identifies_no_budget_when_no_compatible_envelope_exists():
    budget_lines = [
        {
            "fund_code": "FR0001-0001",
            "donor_line_code": "SIDA401",
            "program_code": "GF101",
            "category_code": "CAT001",
            "budget_line_code": "UNGR027",
            "budget": 616385.0,
        }
    ]

    transactions = [
        {
            "fund": "FR0001-0001",
            "donor_line": "SIDA401",
            "program": "CO101",
            "category": "CAT004",
            "budget_line": "UNCS025",
            "budget_actual_amount": 9180.0,
        }
    ]

    result = generate_budget_mapping_intelligence(
        budget_lines=budget_lines,
        transactions=transactions,
    )

    assert result["summary"]["broader_match_evidence_count"] == 0
    assert result["summary"]["broader_match_actual"] == 0.0
    assert result["summary"]["no_budget_identified_evidence_count"] == 1
    assert result["summary"]["no_budget_identified_actual"] == 9180.0

    item = result["items"][0]

    assert item["status"] == "No Budget Identified - Review Required"
    assert item["actual_budget_line_code"] == "UNCS025"
    assert item["matched_budget_line_code"] is None
    assert item["actual"] == 9180.0  

def test_flags_multiple_possible_budget_lines_in_broader_envelope():
    budget_lines = [
        {
            "fund_code": "FR0001-0001",
            "donor_line_code": "SIDA401",
            "program_code": "TR104",
            "category_code": "CAT001",
            "budget_line_code": "UNGR017",
            "budget_line_name": "Travel and Accommodation",
            "budget": 1045.0,
        },
        {
            "fund_code": "FR0001-0001",
            "donor_line_code": "SIDA401",
            "program_code": "TR104",
            "category_code": "CAT001",
            "budget_line_code": "UNGR018",
            "budget_line_name": "Food & Beverage",
            "budget": 667.0,
        },
        {
            "fund_code": "FR0001-0001",
            "donor_line_code": "SIDA401",
            "program_code": "TR104",
            "category_code": "CAT001",
            "budget_line_code": "UNGR021",
            "budget_line_name": "Honoraria",
            "budget": 1500.0,
        },
    ]

    transactions = [
        {
            "fund": "FR0001-0001",
            "donor_line": "SIDA401",
            "program": "TR104",
            "category": "CAT001",
            "budget_line": "UNGR099",
            "budget_actual_amount": 750.0,
        }
    ]

    result = generate_budget_mapping_intelligence(
        budget_lines=budget_lines,
        transactions=transactions,
    )

    assert result["summary"]["broader_match_evidence_count"] == 1
    assert result["summary"]["broader_match_actual"] == 750.0

    item = result["items"][0]

    assert (
        item["status"]
        == "Broader Budget Envelope - Multiple Possible Budget Lines - Review Required"
    )
    assert item["actual_budget_line_code"] == "UNGR099"
    assert item["matched_budget_line_code"] is None
    assert item["actual"] == 750.0
    assert item["candidate_budget_line_codes"] == [
        "UNGR017",
        "UNGR018",
        "UNGR021",
    ]  

def test_classifies_raw_gl_transaction_before_mapping():
    budget_lines = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNGA001",
            "amount": 500000.00,
        }
    ]

    transactions = [
        {
            "account_number": "250001",
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNRC011",
            "amount": 2500.00,
        }
    ]

    accounts_by_number = {
        "250001": {
            "financial_category": "Asset",
            "financial_subcategory": "Computer Equipment",
        }
    }

    result = generate_budget_mapping_intelligence(
        budget_lines=budget_lines,
        transactions=transactions,
        accounts_by_number=accounts_by_number,
    )

    assert result["summary"]["broader_match_evidence_count"] == 1
    assert result["summary"]["broader_match_actual"] == 2500.00
    assert result["summary"]["no_budget_identified_evidence_count"] == 0
    assert result["summary"]["no_budget_identified_actual"] == 0.00

    assert len(result["items"]) == 1

    item = result["items"][0]

    assert item["status"] == (
        "Broader Budget Match - Review Required"
    )
    assert item["actual_budget_line_code"] == "UNRC011"
    assert item["matched_budget_line_code"] == "UNGA001"
    assert item["candidate_budget_line_codes"] == ["UNGA001"]
    assert item["actual"] == 2500.00 

def test_duplicate_budget_records_do_not_create_false_ambiguity():
    budget_lines = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNGA001",
            "amount": 300000.00,
        },
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNGA001",
            "amount": 200000.00,
        },
    ]

    transactions = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNRC011",
            "budget_actual_amount": 6000.00,
        }
    ]

    result = generate_budget_mapping_intelligence(
        budget_lines=budget_lines,
        transactions=transactions,
    )

    assert result["summary"]["broader_match_evidence_count"] == 1
    assert result["summary"]["broader_match_actual"] == 6000.00

    assert len(result["items"]) == 1

    item = result["items"][0]

    assert item["status"] == (
        "Broader Budget Match - Review Required"
    )
    assert item["matched_budget_line_code"] == "UNGA001"
    assert item["candidate_budget_line_codes"] == ["UNGA001"] 

def test_blank_budget_line_still_identifies_broader_budget_envelope():
    budget_lines = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "",
            "amount": 2000000.00,
        }
    ]

    transactions = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNRC011",
            "budget_actual_amount": 6000.00,
        }
    ]

    result = generate_budget_mapping_intelligence(
        budget_lines=budget_lines,
        transactions=transactions,
    )

    assert result["summary"]["broader_match_evidence_count"] == 1
    assert result["summary"]["broader_match_actual"] == 6000.00
    assert result["summary"]["no_budget_identified_evidence_count"] == 0
    assert result["summary"]["no_budget_identified_actual"] == 0.00

    assert len(result["items"]) == 1

    item = result["items"][0]

    assert item["status"] == (
        "Broader Budget Envelope - No Specific Budget Line - "
        "Review Required"
    )
    assert item["actual_budget_line_code"] == "UNRC011"
    assert item["matched_budget_line_code"] is None
    assert item["candidate_budget_line_codes"] == []
    assert item["actual"] == 6000.00   

def test_exact_budget_line_with_zero_budget_is_not_silently_skipped():
    budget_lines = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNRC011",
            "current_budget": 0.00,
        }
    ]

    transactions = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNRC011",
            "budget_actual_amount": 6000.00,
        }
    ]

    result = generate_budget_mapping_intelligence(
        budget_lines=budget_lines,
        transactions=transactions,
    )

    assert result["summary"]["broader_match_evidence_count"] == 0
    assert result["summary"]["broader_match_actual"] == 0.00
    assert result["summary"]["no_budget_identified_evidence_count"] == 1
    assert result["summary"]["no_budget_identified_actual"] == 6000.00

    assert len(result["items"]) == 1

    item = result["items"][0]

    assert item["status"] == (
        "No Budget Identified - Review Required"
    )
    assert item["actual_budget_line_code"] == "UNRC011"
    assert item["matched_budget_line_code"] is None
    assert item["actual"] == 6000.00

def test_repeated_transactions_for_same_budget_line_are_one_mapping_exception():
    budget_lines = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNGA001",
            "current_budget": 500000.00,
        }
    ]

    transactions = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNRC011",
            "budget_actual_amount": 2000.00,
        },
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNRC011",
            "budget_actual_amount": 4000.00,
        },
    ]

    result = generate_budget_mapping_intelligence(
        budget_lines=budget_lines,
        transactions=transactions,
    )

    assert result["summary"]["broader_match_evidence_count"] == 1
    assert result["summary"]["broader_match_actual"] == 6000.00
    assert result["summary"]["no_budget_identified_evidence_count"] == 0

    assert len(result["items"]) == 1

    item = result["items"][0]

    assert item["status"] == (
        "Broader Budget Match - Review Required"
    )
    assert item["actual_budget_line_code"] == "UNRC011"
    assert item["matched_budget_line_code"] == "UNGA001"
    assert item["actual"] == 6000.00        

def test_budget_line_budgeted_elsewhere_is_not_a_mapping_exception():
    budget_lines = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNRC011",
            "current_budget": 500000.00,
        },

        {
            "fund_code": "FR0001-0001",
            "donor_line_code": "OTHER",
            "program_code": "OTHER",
            "category_code": "OTHER",
            "budget_line_code": "OTHER001",
            "current_budget": 1000.00,
        },

    ]

    transactions = [
        {
            "fund_code": "FR0001-0001",
            "donor_line_code": "SIDA407",
            "program_code": "CO101",
            "category_code": "CAT004",
            "budget_line_code": "UNRC011",
            "budget_actual_amount": 6000.00,
        }
    ]

    result = generate_budget_mapping_intelligence(
        budget_lines=budget_lines,
        transactions=transactions,
    )

    assert result["summary"]["broader_match_evidence_count"] == 0
    assert result["summary"]["broader_match_actual"] == 0.00
    assert result["summary"]["no_budget_identified_evidence_count"] == 0
    assert result["summary"]["no_budget_identified_actual"] == 0.00
    assert result["items"] == []  

def test_blank_actual_budget_line_is_not_a_mapping_exception():
    budget_lines = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "UNGA001",
            "current_budget": 500000.00,
        }
    ]

    transactions = [
        {
            "fund_code": "FR0007-0004",
            "donor_line_code": "OSF807",
            "program_code": "RC101",
            "category_code": "CAT008",
            "budget_line_code": "",
            "budget_actual_amount": 6000.00,
        }
    ]

    result = generate_budget_mapping_intelligence(
        budget_lines=budget_lines,
        transactions=transactions,
    )

    assert result["summary"]["broader_match_evidence_count"] == 0
    assert result["summary"]["broader_match_actual"] == 0.00
    assert result["summary"]["no_budget_identified_evidence_count"] == 0
    assert result["summary"]["no_budget_identified_actual"] == 0.00
    assert result["items"] == []                 