from typing import Dict, List

import re


FIELD_PATTERNS = {
    "entry_no": (
        r"^entry\s*(no|number)\.?$"
    ),
    "document_no": (
        r"^document\s*(no|number)\.?$"
    ),
    "document_type": (
        r"^document\s*type$"
    ),
    "external_document_no": (
        r"^external\s*document\s*"
        r"(no|number)\.?$"
    ),
    "transaction_date": (
        r"^posting\s*date$"
    ),
    "account": (
        r"^g/l\s*account\s*"
        r"(no|number|code)\.?$"
    ),
    "account_name": (
        r"^g/l\s*account\s*name$"
    ),
    "description": (
        r"^(description|details|narration)$"
    ),
    "debit": (
        r"^debit\s*amount\s*\(lcy\)$"
    ),
    "credit": (
        r"^credit\s*amount\s*\(lcy\)$"
    ),
    "amount": (
        r"^amount\s*\(lcy\)$"
    ),

    #
    # FINANCIAL DIMENSIONS
    #

    "fund": (
        r"^(fund\s*code|"
        r"fund\s*no|"
        r"grant\s*code|"
        r"grant\s*id)$"
    ),

    "donor": (
        r"^(funder\s*code|"
        r"donor\s*code|"
        r"funder|"
        r"donor|"
        r"sponsor)$"
    ),

    "program": (
        r"^(programs?\s*code|"
        r"programme\s*code|"
        r"projects?\s*code|"
        r"program|"
        r"project)$"
    ),

    "category": (
        r"^(category\s*code|"
        r"expense\s*category|"
        r"category)$"
    ),

    "donor_line": (
        r"^(donor\s*line\s*code|"
        r"funder\s*line\s*code|"
        r"donor\s*line)$"
    ),

    "budget_line": (
        r"^(budget\s*line\s*code|"
        r"budget\s*line|"
        r"budget\s*code)$"
    ),

    "department": (
        r"^department(\s*code)?$"
    ),

    "cost_center": (
        r"^cost\s*center(\s*code)?$"
    ),

    "grant": (
        r"^grant(\s*code)?$"
    ),

    "employee": (
        r"^(employee|staff)"
        r"(\s*code)?$"
    ),
}


def map_gl_columns(
    headers: List[str],
) -> Dict[str, str]:
    """
    Map source General Ledger column headers to
    AI-FOS canonical GL fields.

    Patterns are deliberately strict so related
    financial dimensions cannot overwrite each
    other.

    Example:

        Fund Code       -> fund
        Funder Code     -> donor
        Donor Line Code -> donor_line
    """

    mapping: Dict[str, str] = {}

    for field_name, pattern in (
        FIELD_PATTERNS.items()
    ):
        for header in headers:
            cleaned_header = str(
                header
            ).strip()

            if re.fullmatch(
                pattern,
                cleaned_header,
                re.IGNORECASE,
            ):
                mapping[field_name] = (
                    header
                )

                #
                # Once a field is matched,
                # stop searching. This prevents
                # later columns from overwriting
                # the correct source column.
                #
                break

    return mapping