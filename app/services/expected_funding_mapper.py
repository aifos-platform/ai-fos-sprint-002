from __future__ import annotations

import re


FIELD_PATTERNS = {
    "expected_funding_code": (
        r"^expected\s*funding\s*code$|"
        r"^expected\s*grant\s*code$|"
        r"^funding\s*code$|"
        r"^grant\s*code$"
    ),

    "funding_name": (
        r"^funding\s*name$|"
        r"^expected\s*funding\s*name$|"
        r"^grant\s*name$|"
        r"^expected\s*grant\s*name$"
    ),

    "donor_code": (
        r"^donor\s*code$|"
        r"^funder\s*code$"
    ),

    "donor_name": (
        r"^donor\s*name$|"
        r"^funder\s*name$"
    ),

    "stage": (
        r"^stage$|"
        r"^funding\s*stage$|"
        r"^grant\s*stage$|"
        r"^proposal\s*stage$"
    ),

    "probability_percentage": (
        r"^probability\s*%$|"
        r"^probability\s*percentage$|"
        r"^probability$|"
        r"^likelihood\s*%$|"
        r"^likelihood\s*percentage$"
    ),

    "minimum_amount": (
        r"^minimum\s*amount$|"
        r"^minimum$|"
        r"^min\s*amount$|"
        r"^min$"
    ),

    "most_likely_amount": (
        r"^most\s*likely\s*amount$|"
        r"^most\s*likely$|"
        r"^likely\s*amount$"
    ),

    "maximum_amount": (
        r"^maximum\s*amount$|"
        r"^maximum$|"
        r"^max\s*amount$|"
        r"^max$"
    ),

    "expected_decision_date": (
        r"^expected\s*decision\s*date$|"
        r"^decision\s*date$|"
        r"^expected\s*approval\s*date$"
    ),

    "expected_first_payment_date": (
        r"^expected\s*first\s*payment\s*date$|"
        r"^expected\s*payment\s*date$|"
        r"^first\s*payment\s*date$"
    ),

    "original_currency": (
        r"^original\s*currency$|"
        r"^funding\s*currency$|"
        r"^grant\s*currency$|"
        r"^currency$"
    ),

    "reporting_currency": (
        r"^reporting\s*currency$|"
        r"^base\s*currency$"
    ),

    "program_code": (
        r"^programs?\s*code$|"
        r"^programme\s*code$"
    ),

    "project_code": (
        r"^project\s*code$"
    ),

    "budget_line_code": (
        r"^budget\s*line\s*code$|"
        r"^budget\s*line\s*(no|number)\.?$"
    ),

    "notes": (
        r"^notes$|"
        r"^remarks$|"
        r"^comments$"
    ),
}


def map_expected_funding_columns(
    headers: list[str],
) -> dict[str, str]:
    """
    Map Expected Funding worksheet columns into
    canonical AI-FOS Expected Funding fields.

    Expected Funding is intentionally separate from
    secured / available funding.

    Mapping therefore identifies prospective funding
    attributes only and does not classify any record as
    secured funding.
    """

    mapping: dict[str, str] = {}

    for field_name, pattern in FIELD_PATTERNS.items():

        for header in headers:

            normalized_header = str(
                header
            ).strip()

            if re.search(
                pattern,
                normalized_header,
                re.IGNORECASE,
            ):

                mapping[field_name] = header

                break

    return mapping