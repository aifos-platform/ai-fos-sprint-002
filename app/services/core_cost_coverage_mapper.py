import re


FIELD_PATTERNS = {
    "coverage_type": (
        r"^coverage\s*type$|"
        r"^core\s*cost\s*coverage\s*type$"
    ),

    "fund_code": (
        r"^fund\s*code$|"
        r"^grant\s*code$"
    ),

    "budget_line_code": (
        r"^budget\s*line\s*code$"
    ),

    "amount": (
        r"^amount$|"
        r"^coverage\s*amount$"
    ),
}


def map_core_cost_coverage_columns(
    headers: list[str],
) -> dict[str, str]:
    """
    Map Core Cost Coverage worksheet columns into
    canonical AI-FOS Core Cost Coverage fields.

    Mapping identifies source fields only and does not
    infer, allocate, or recalculate financial coverage.
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