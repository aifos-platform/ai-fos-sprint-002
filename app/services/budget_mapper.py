from __future__ import annotations

import re
from typing import Dict, List


FIELD_PATTERNS = {
    "account_number": (
        r"^(account|g/l\s*account)"
        r"\s*(no|number|code)?\.?$"
    ),

    "budget_line_code": (
        r"^budget\s*line\s*code$|"
        r"^budget\s*line\s*(no|number)\.?$"
    ),

    "budget_line_name": (
        r"^budget\s*line\s*name$|"
        r"^budget\s*line\s*description$|"
        r"^budget\s*line\s*code\s*name$"
    ),

    "original_budget": (
        r"^(total\s*)?"
        r"original\s*budget"
        r"(\s*\(usd\))?$"
    ),

    "remaining_secured_budget": (
        r"^original\s*\(\s*-\s*\)\s*actual\s*spending$|"
        r"^original\s*-\s*actual\s*spending$|"
        r"^remaining\s*secured\s*budget$|"
        r"^remaining\s*available\s*budget$"
    ),    

    "revised_budget": (
        r"^(total\s*)?"
        r"revised\s*budget"
        r"(\s*\(usd\))?$"
    ),

    "current_budget_usd": (
        r"^current\s*budget\s*usd$|"
        r"^current\s*budget\s*\(usd\)$|"
        r"^budget\s*usd$"
    ),

    "fund_code": (
        r"^fund\s*code$|"
        r"^fund\s*(no|number)\.?$|"
        r"^grant\s*code$|"
        r"^grant\s*id$"
    ),

    "fund_name": (
        r"^fund\s*name$|"
        r"^grant\s*name$"
    ),

    "donor_code": (
        r"^funder\s*code$|"
        r"^donor\s*code$|"
        r"^funder\s*(no|number)\.?$|"
        r"^donor\s*(no|number)\.?$"
    ),

    "donor_name": (
        r"^funder\s*name$|"
        r"^donor\s*name$"
    ),

    "program_code": (
        r"^programs?\s*code$|"
        r"^programme\s*code$"
    ),

    "program_name": (
        r"^programs?\s*name$|"
        r"^programme\s*name$"
    ),

    "category_code": (
        r"^category\s*code$|"
        r"^expense\s*category\s*code$"
    ),

    "category_name": (
        r"^category\s*name$|"
        r"^expense\s*category\s*name$"
    ),

    "donor_line_code": (
        r"^donor\s*line\s*code$|"
        r"^funder\s*line\s*code$"
    ),

    "project_code": (
        r"^project\s*code$|"
        r"^project\s*(no|number)\.?$"
    ),

    "project_name": (
        r"^project\s*name$"
    ),

    "original_currency": (
        r"^original\s*currency$|"
        r"^budget\s*currency$"
    ),

    "reporting_currency": (
        r"^reporting\s*currency$|"
        r"^base\s*currency$"
    ),

    "exchange_rate": (
        r"^exchange\s*rate$|"
        r"^fx\s*rate$"
    ),

    "fiscal_year": (
        r"^(fiscal\s*)?year$|"
        r"^budget\s*year$"
    ),

    "notes": (
        r"^budget\s*notes$|"
        r"^notes$|"
        r"^remarks$"
    ),

    "grant_start_date": (
        r"^grant\s*start\s*date$|"
        r"^fund\s*start\s*date$|"
        r"^start\s*date$"
    ),

    "grant_end_date": (
        r"^grant\s*end\s*date$|"
        r"^fund\s*end\s*date$|"
        r"^end\s*date$"
    ),
}


def map_budget_columns(
    headers: List[str],
) -> Dict[str, str]:
    """
    Detect Budget columns and map them into
    the AI-FOS canonical Budget model.
    """

    mapping: Dict[str, str] = {}

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

def detect_budget_period_columns(
    headers: List[str],
) -> List[Dict[str, str | int]]:
    """
    Detect dynamic budget-period columns.

    Examples:
    - Requested 2026
    - Spending Plan (2027)
    - Budget 2028
    - FY29 Budget
    - Forecast 2030

    The function extracts:
    - original header
    - semantic type
    - fiscal year

    It does not depend on any specific organisation.
    """

    detected: List[
        Dict[str, str | int]
    ] = []

    type_patterns = {
        "requested": (
            r"\brequested\b|"
            r"\brequired\b|"
            r"\brequest\b"
        ),
        "spending_plan": (
            r"\bspending\s*plan\b|"
            r"\bplanned\s*spend\b|"
            r"\bspend\s*plan\b"
        ),
        "budget": (
            r"\bbudget\b|"
            r"\ballocation\b"
        ),
        "forecast": (
            r"\bforecast\b|"
            r"\bprojection\b"
        ),
    }

    for header in headers:
        text = str(
            header
        ).strip()

        if not text:
            continue

        year_match = re.search(
            r"\b(20\d{2})\b",
            text,
            re.IGNORECASE,
        )

        if year_match:
            fiscal_year = int(
                year_match.group(1)
            )

        else:
            short_year_match = re.search(
                r"\bFY\s*['\-]?\s*(\d{2})\b",
                text,
                re.IGNORECASE,
            )

            if not short_year_match:
                continue

            fiscal_year = 2000 + int(
                short_year_match.group(1)
            )

        period_type = None

        for (
            candidate_type,
            pattern,
        ) in type_patterns.items():

            if re.search(
                pattern,
                text,
                re.IGNORECASE,
            ):
                period_type = candidate_type
                break

        if period_type is None:
            continue

        detected.append(
            {
                "header": header,
                "type": period_type,
                "fiscal_year": fiscal_year,
            }
        )

    return detected
