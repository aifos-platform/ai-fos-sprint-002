from app.organization import Organization


def test_build_grants_preserves_derived_donor_code_from_budget():
    organization = Organization()

    organization.fund_knowledge = {
        "classification_rules": {
            "internal_funder_codes": ["FR0012"],
            "default_external_funder_is_grant": True,
            "derive_funder_from_fund_code": True,
            "fund_code_separator": "-",
            "funder_code_segment": 0,
        }
    }

    organization.budget.lines = [
        {
            "fund_code": "FR0004-0002",
            "fund_name": "Carnegie 8",
            "revised_budget": 100000.0,
        }
    ]

    organization.build_grants()

    grant = organization.grants["FR0004-0002"]

    assert grant.code == "FR0004-0002"
    assert grant.donor_code == "FR0004"

def test_build_grants_preserves_derived_donor_code_from_gl_only_grant():
    organization = Organization()

    organization.fund_knowledge = {
        "classification_rules": {
            "internal_funder_codes": ["FR0012"],
            "default_external_funder_is_grant": True,
            "derive_funder_from_fund_code": True,
            "fund_code_separator": "-",
            "funder_code_segment": 0,
        }
    }

    organization.budget.lines = []

    organization.normalized_general_ledger = [
        {
            "fund_code": "FR0009-0001",
            "account_number": "600000",
            "amount": 1000.0,
            "debit_amount": 1000.0,
            "credit_amount": 0.0,
        }
    ]

    organization.build_grants()

    grant = organization.grants["FR0009-0001"]

    assert grant.code == "FR0009-0001"
    assert grant.donor_code == "FR0009"    