from __future__ import annotations

import re
from typing import Any


FIELD_PATTERNS = {
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
    "budget_line_code": (
        r"^budget\s*line\s*code$|"
        r"^budget\s*line\s*(no|number)\.?$"
    ),
    "budget_line_name": (
        r"^budget\s*line\s*name$|"
        r"^budget\s*line\s*description$|"
        r"^budget\s*line\s*code\s*name$"
    ),
    "budget_notes": (
        r"^budget\s*notes$|"
        r"^notes$|"
        r"^remarks$"
    ),
    "employee_responsible": (
        r"^employee\s*responsible$|"
        r"^responsible\s*employee$"
    ),
}


def map_needed_budget_columns(
    headers: list[str],
) -> dict[str, str]:
    """
    Map descriptive columns from the organisation's
    Needed Budget sheet into canonical AI-FOS fields.

    Needed Budget intentionally does not require:
    - Fund Code
    - Donor Code
    - Donor Line Code

    because it represents organisational budget need,
    not secured grant funding.
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


def detect_needed_budget_columns(
    headers: list[str],
) -> list[dict[str, Any]]:
    """
    Detect annual Needed Budget amount columns.

    Examples:
    - Needed Budget 2026
    - Needed Budget 2027
    - Required Budget 2028

    Each detected column is associated with its
    fiscal year.
    """

    detected: list[dict[str, Any]] = []

    pattern = (
        r"\b(?:needed|required)\s*budget\b"
    )

    for header in headers:

        text = str(
            header
        ).strip()

        if not text:
            continue

        if not re.search(
            pattern,
            text,
            re.IGNORECASE,
        ):
            continue

        year_match = re.search(
            r"\b(20\d{2})\b",
            text,
        )

        if not year_match:
            continue

        detected.append(
            {
                "header": header,
                "type": "needed_budget",
                "fiscal_year": int(
                    year_match.group(1)
                ),
            }
        )

    return detected