from __future__ import annotations

from typing import Any

from openpyxl import load_workbook

from app.services.budget_mapper import (
    detect_budget_period_columns,
    map_budget_columns,
)
from app.services.budget_normalizer import (
    BudgetNormalizer,
)
from app.services.document_detector import (
    detect_document_type,
)
from app.services.gl_mapper import (
    map_gl_columns,
)



def inspect_workbook(
    file_path: str,
) -> dict[str, Any]:
    """
    Inspect the first worksheet and extract data
    according to the detected AI-FOS document type.
    """

    workbook = load_workbook(
        file_path,
        data_only=True,
    )

    sheet_names = workbook.sheetnames

    worksheet = workbook[
        sheet_names[0]
    ]

    headers = [
        (
            str(cell.value).strip()
            if cell.value is not None
            else ""
        )
        for cell in worksheet[1]
    ]

    document_type = (
        detect_document_type(
            headers
        )
    )

    gl_mapping: dict[
        str,
        str,
    ] = {}

    transactions: list[
        dict[str, Any]
    ] = []

    budget_mapping: dict[
        str,
        str,
    ] = {}

    budget_lines: list[
        dict[str, Any]
    ] = []

    #
    # GENERAL LEDGER
    #

    if document_type == (
        "general_ledger"
    ):

        gl_mapping = (
            map_gl_columns(
                headers
            )
        )

        transactions = (
            _extract_rows(
                worksheet=worksheet,
                headers=headers,
                mapping=gl_mapping,
            )
        )

    #
    # BUDGET
    #

    elif document_type == "budget":

        budget_mapping = (
            map_budget_columns(
                headers
            )
        )

        budget_period_columns = (
            detect_budget_period_columns(
                headers
            )
        )        

        raw_budget_rows = (
            _extract_budget_rows(
                worksheet=worksheet,
                headers=headers,
                mapping=budget_mapping,
                period_columns=budget_period_columns,
            )
        )

        normalizer = (
            BudgetNormalizer()
        )

        for row in raw_budget_rows:

            normalized_line = (
                normalizer.normalize_line(
                    account_number=(
                        row.get(
                            "account_number"
                        )
                    ),
                    budget_line_code=(
                        row.get(
                            "budget_line_code"
                        )
                    ),
                    budget_line_name=(
                        row.get(
                            "budget_line_name"
                        )
                    ),
                    original_budget=(
                        row.get(
                            "original_budget"
                        )
                    ),
                    revised_budget=(
                        row.get(
                            "revised_budget"
                        )
                    ),
                    current_budget_usd=(
                        row.get(
                            "current_budget_usd"
                        )
                    ),
                    fund_code=(
                        row.get(
                            "fund_code"
                        )
                    ),
                    fund_name=(
                        row.get(
                            "fund_name"
                        )
                    ),
                    donor_code=(
                        row.get(
                            "donor_code"
                        )
                    ),
                    donor_name=(
                        row.get(
                            "donor_name"
                        )
                    ),
                    program_code=(
                        row.get(
                            "program_code"
                        )
                    ),
                    program_name=(
                        row.get(
                            "program_name"
                        )
                    ),
                    category_code=(
                        row.get(
                            "category_code"
                        )
                    ),
                    category_name=(
                        row.get(
                            "category_name"
                        )
                    ),
                    donor_line_code=(
                        row.get(
                            "donor_line_code"
                        )
                    ),
                    project_code=(
                        row.get(
                            "project_code"
                        )
                    ),
                    project_name=(
                        row.get(
                            "project_name"
                        )
                    ),
                    original_currency=(
                        row.get(
                            "original_currency"
                        )
                    ),
                    reporting_currency=(
                        row.get(
                            "reporting_currency"
                        )
                    ),
                    exchange_rate=(
                        row.get(
                            "exchange_rate"
                        )
                    ),
                    fiscal_year=(
                        row.get(
                            "fiscal_year"
                        )
                    ),
                    period_amounts=(
                        row.get(
                            "period_amounts"
                        )
                    ),
                    notes=(
                        row.get(
                            "notes"
                        )
                    ),
                )
            )

            if _is_blank_budget_line(
                normalized_line
            ):
                continue

            budget_lines.append(
                normalized_line
            )

    return {
        "sheet_count": len(
            sheet_names
        ),
        "sheet_names": sheet_names,
        "sheet_name": (
            worksheet.title
        ),
        "row_count": (
            worksheet.max_row
        ),
        "column_count": (
            worksheet.max_column
        ),
        "headers": headers,
        "document_type": (
            document_type
        ),
        "gl_mapping": (
            gl_mapping
        ),
        "transactions": (
            transactions
        ),
        "budget_mapping": (
            budget_mapping
        ),
        "budget_lines": (
            budget_lines
        ),
    }


def _extract_rows(
    worksheet,
    headers: list[str],
    mapping: dict[str, str],
) -> list[dict[str, Any]]:
    """
    Extract worksheet rows using a detected
    AI-FOS field mapping.
    """

    extracted_rows: list[
        dict[str, Any]
    ] = []

    column_indexes = {
        field_name: headers.index(
            header_name
        )
        for (
            field_name,
            header_name,
        ) in mapping.items()
        if header_name in headers
    }

    for row in worksheet.iter_rows(
        min_row=2,
        values_only=True,
    ):

        extracted_row = {
            field_name: (
                row[column_index]
            )
            for (
                field_name,
                column_index,
            ) in column_indexes.items()
        }

        if all(
            value in {
                None,
                "",
            }
            for value
            in extracted_row.values()
        ):
            continue

        extracted_rows.append(
            extracted_row
        )

    return extracted_rows

def _extract_budget_rows(
    worksheet,
    headers: list[str],
    mapping: dict[str, str],
    period_columns: list[dict[str, str | int]],
) -> list[dict[str, Any]]:
    """
    Extract Budget rows while preserving canonical
    fields and dynamic year-specific Budget amounts.

    Dynamic period fields are preserved even when
    their cells are blank.

    This allows AI-FOS to distinguish between:

    - null: no amount was provided
    - 0: an explicit zero amount was provided
    - non-zero: an entered financial amount
    """

    extracted_rows: list[
        dict[str, Any]
    ] = []

    column_indexes = {
        field_name: headers.index(
            header_name
        )
        for (
            field_name,
            header_name,
        ) in mapping.items()
        if header_name in headers
    }

    period_column_indexes: list[
        dict[str, Any]
    ] = []

    for period_column in period_columns:

        header_name = period_column.get(
            "header"
        )

        if header_name not in headers:
            continue

        period_column_indexes.append(
            {
                "column_index": headers.index(
                    header_name
                ),
                "header": header_name,
                "type": period_column.get(
                    "type"
                ),
                "fiscal_year": period_column.get(
                    "fiscal_year"
                ),
            }
        )

    for row in worksheet.iter_rows(
        min_row=2,
        values_only=True,
    ):

        extracted_row = {
            field_name: row[
                column_index
            ]
            for (
                field_name,
                column_index,
            ) in column_indexes.items()
        }

        period_amounts: list[
            dict[str, Any]
        ] = []

        for period_column in period_column_indexes:

            value = row[
                period_column[
                    "column_index"
                ]
            ]

            if isinstance(
                value,
                str,
            ) and not value.strip():
                value = None

            period_amounts.append(
                {
                    "header": period_column[
                        "header"
                    ],
                    "type": period_column[
                        "type"
                    ],
                    "fiscal_year": period_column[
                        "fiscal_year"
                    ],
                    "amount": value,
                }
            )

        extracted_row[
            "period_amounts"
        ] = period_amounts

        canonical_values = [
            value
            for (
                key,
                value,
            ) in extracted_row.items()
            if key != "period_amounts"
        ]

        has_canonical_data = any(
            value not in {
                None,
                "",
            }
            for value in canonical_values
        )

        if (
            not has_canonical_data
            and not period_column_indexes
        ):
            continue

        extracted_rows.append(
            extracted_row
        )

    return extracted_rows

def _is_blank_budget_line(
    budget_line: dict[str, Any],
) -> bool:
    """
    Determine whether a normalized Budget row
    contains useful financial or dimensional data.
    """

    return not any(
        [
            budget_line.get(
                "account_number"
            ),
            budget_line.get(
                "budget_line_code"
            ),
            budget_line.get(
                "budget_line_name"
            ),
            budget_line.get(
                "fund_code"
            ),
            budget_line.get(
                "donor_code"
            ),
            budget_line.get(
                "program_code"
            ),
            budget_line.get(
                "category_code"
            ),
            budget_line.get(
                "donor_line_code"
            ),
            budget_line.get(
                "project_code"
            ),
            budget_line.get(
                "original_budget"
            ),
            budget_line.get(
                "revised_budget"
            ),
            budget_line.get(
                "current_budget_usd"
            ),
        ]
    )