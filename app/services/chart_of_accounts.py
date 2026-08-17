from pathlib import Path
from typing import Any

import pandas as pd

from app.services.chart_normalizer import ChartNormalizer


class ChartOfAccounts:
    """
    Handles importing and managing the Chart of Accounts.
    """

    def __init__(self):
        self.raw_data = None
        self.accounts = []
        self.columns = {}
        self.normalizer = ChartNormalizer()

    def load_chart(self, file_path: str) -> pd.DataFrame:
        """
        Load the Chart of Accounts Excel file.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        self.raw_data = pd.read_excel(
            path,
            dtype=str,
            keep_default_na=False,
        )

        return self.raw_data

    def detect_columns(
        self,
    ) -> dict[str, str | None]:
        """
        Detect common Chart of Accounts columns
        from different ERP exports.
        """

        if self.raw_data is None:
            raise ValueError(
                "Load the Chart of Accounts "
                "before detecting columns."
            )

        normalized_columns = {
            str(column)
            .strip()
            .lower()
            .replace("_", " "): str(column)
            for column in self.raw_data.columns
        }

        aliases = {
            "account_number": [
                "no.",
                "no",
                "account number",
                "account no",
                "account code",
                "gl code",
                "gl account",
                "code",
            ],
            "account_name": [
                "name",
                "account name",
                "account description",
                "description",
                "gl description",
            ],
            "parent_account": [
                "parent account",
                "parent code",
                "parent account number",
            ],
            "level": [
                "level",
                "account level",
                "hierarchy level",
            ],
            "active": [
                "active",
                "is active",
                "status",
            ],
            "income_balance": [
                "income/balance",
                "income balance",
            ],
            "financial_category": [
                "account category",
                "financial category",
                "category",
            ],
            "financial_subcategory": [
                "account subcategory",
                "financial subcategory",
                "subcategory",
            ],
            "account_type": [
                "account type",
                "type",
            ],
            "totaling": [
                "totaling",
                "total formula",
            ],
        }

        detected_columns: dict[
            str,
            str | None,
        ] = {}

        for (
            field_name,
            possible_names,
        ) in aliases.items():
            detected_columns[field_name] = None

            for possible_name in possible_names:
                if possible_name in normalized_columns:
                    detected_columns[field_name] = (
                        normalized_columns[
                            possible_name
                        ]
                    )
                    break

        self.columns = detected_columns

        return self.columns

    def validate_chart(
        self,
    ) -> dict[str, list[str]]:
        """
        Validate the imported Chart of Accounts.
        """

        if self.raw_data is None:
            raise ValueError(
                "Load the Chart of Accounts "
                "before validation."
            )

        if not self.columns:
            raise ValueError(
                "Detect the columns before validation."
            )

        errors: list[str] = []
        warnings: list[str] = []

        account_number_column = self.columns.get(
            "account_number"
        )

        account_name_column = self.columns.get(
            "account_name"
        )

        if account_number_column is None:
            errors.append(
                "Account number column was not detected."
            )

        if account_name_column is None:
            errors.append(
                "Account name column was not detected."
            )

        if errors:
            return {
                "errors": errors,
                "warnings": warnings,
            }

        account_numbers = (
            self.raw_data[account_number_column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        account_names = (
            self.raw_data[account_name_column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        missing_account_numbers = (
            account_numbers.eq("").sum()
        )

        if missing_account_numbers:
            errors.append(
                f"{missing_account_numbers} "
                "row(s) have a missing account number."
            )

        missing_account_names = (
            account_names.eq("").sum()
        )

        if missing_account_names:
            warnings.append(
                f"{missing_account_names} "
                "row(s) have a missing account name."
            )

        non_blank_account_numbers = (
            account_numbers[
                account_numbers.ne("")
            ]
        )

        duplicate_count = (
            non_blank_account_numbers
            .duplicated()
            .sum()
        )

        if duplicate_count:
            errors.append(
                f"{duplicate_count} duplicate "
                "account number row(s) were found."
            )

        blank_row_count = (
            self.raw_data
            .isna()
            .all(axis=1)
            .sum()
        )

        if blank_row_count:
            warnings.append(
                f"{blank_row_count} completely "
                "blank row(s) were found."
            )

        return {
            "errors": errors,
            "warnings": warnings,
        }

    def build_hierarchy(
        self,
    ) -> list[dict[str, Any]]:
        """
        Convert the imported Chart of Accounts into
        AI-FOS account records.

        Preserve ERP hierarchy where available.
        Otherwise infer hierarchy from ordered
        Begin-Total and End-Total structures.
        """

        if self.raw_data is None:
            raise ValueError(
                "Load the Chart of Accounts before "
                "building the hierarchy."
            )

        if not self.columns:
            raise ValueError(
                "Detect the columns before "
                "building the hierarchy."
            )

        account_number_column = self.columns.get(
            "account_number"
        )

        account_name_column = self.columns.get(
            "account_name"
        )

        parent_account_column = self.columns.get(
            "parent_account"
        )

        level_column = self.columns.get(
            "level"
        )

        active_column = self.columns.get(
            "active"
        )

        financial_category_column = self.columns.get(
            "financial_category"
        )

        financial_subcategory_column = (
            self.columns.get(
                "financial_subcategory"
            )
        )

        income_balance_column = self.columns.get(
            "income_balance"
        )

        account_type_column = self.columns.get(
            "account_type"
        )

        totaling_column = self.columns.get(
            "totaling"
        )

        if (
            account_number_column is None
            or account_name_column is None
        ):
            raise ValueError(
                "Account number and account name "
                "columns are required."
            )

        accounts: list[
            dict[str, Any]
        ] = []

        #
        # STEP 1
        # Normalize all imported accounts.
        #

        for _, row in self.raw_data.iterrows():
            account_number = str(
                row.get(
                    account_number_column,
                    "",
                )
            ).strip()

            account_name = str(
                row.get(
                    account_name_column,
                    "",
                )
            ).strip()

            if not account_number:
                continue

            parent_account = None

            if parent_account_column:
                parent_value = str(
                    row.get(
                        parent_account_column,
                        "",
                    )
                ).strip()

                parent_account = (
                    parent_value or None
                )

            level = None

            if level_column:
                level_value = str(
                    row.get(
                        level_column,
                        "",
                    )
                ).strip()

                if level_value:
                    try:
                        level = int(
                            float(level_value)
                        )
                    except ValueError:
                        level = None

            active = True

            if active_column:
                active_value = str(
                    row.get(
                        active_column,
                        "",
                    )
                ).strip().lower()

                if active_value in {
                    "false",
                    "no",
                    "n",
                    "0",
                    "inactive",
                }:
                    active = False

            financial_category = None

            if financial_category_column:
                value = str(
                    row.get(
                        financial_category_column,
                        "",
                    )
                ).strip()

                financial_category = (
                    value or None
                )

            financial_subcategory = None

            if financial_subcategory_column:
                value = str(
                    row.get(
                        financial_subcategory_column,
                        "",
                    )
                ).strip()

                financial_subcategory = (
                    value or None
                )

            income_balance = None

            if income_balance_column:
                value = str(
                    row.get(
                        income_balance_column,
                        "",
                    )
                ).strip()

                income_balance = (
                    value or None
                )

            account_type = None

            if account_type_column:
                value = str(
                    row.get(
                        account_type_column,
                        "",
                    )
                ).strip()

                account_type = (
                    value or None
                )

            totaling = None

            if totaling_column:
                value = str(
                    row.get(
                        totaling_column,
                        "",
                    )
                ).strip()

                totaling = (
                    value or None
                )

            normalized_account = (
                self.normalizer.normalize_account(
                    account_number=account_number,
                    account_name=account_name,
                    parent_account=parent_account,
                    level=level,
                    active=active,
                    financial_category=(
                        financial_category
                    ),
                    financial_subcategory=(
                        financial_subcategory
                    ),
                    income_balance=income_balance,
                    account_type=account_type,
                    totaling=totaling,
                )
            )

            accounts.append(
                normalized_account
            )

        #
        # STEP 2
        # Infer hierarchy where ERP hierarchy
        # was not supplied.
        #

        hierarchy_stack: list[
            dict[str, Any]
        ] = []

        for account in accounts:
            account_type = str(
                account.get(
                    "account_type"
                )
                or ""
            ).strip().lower()

            totaling = str(
                account.get(
                    "totaling"
                )
                or ""
            ).strip()

            #
            # BEGIN-TOTAL
            #

            if account_type == "begin-total":
                if (
                    account.get(
                        "parent_account"
                    )
                    is None
                    and hierarchy_stack
                ):
                    account[
                        "parent_account"
                    ] = hierarchy_stack[-1][
                        "account_number"
                    ]

                if account.get("level") is None:
                    account["level"] = len(
                        hierarchy_stack
                    )

                hierarchy_stack.append(
                    account
                )

                continue

            #
            # END-TOTAL
            #

            if account_type == "end-total":
                matching_index = None

                if ".." in totaling:
                    range_start = (
                        totaling
                        .split(
                            "..",
                            1,
                        )[0]
                        .strip()
                    )

                    for index in range(
                        len(
                            hierarchy_stack
                        ) - 1,
                        -1,
                        -1,
                    ):
                        open_number = str(
                            hierarchy_stack[
                                index
                            ].get(
                                "account_number"
                            )
                            or ""
                        ).strip()

                        if (
                            open_number
                            == range_start
                        ):
                            matching_index = (
                                index
                            )
                            break

                if (
                    matching_index is None
                    and hierarchy_stack
                ):
                    matching_index = (
                        len(
                            hierarchy_stack
                        )
                        - 1
                    )

                if matching_index is not None:
                    matching_group = (
                        hierarchy_stack[
                            matching_index
                        ]
                    )

                    if (
                        account.get(
                            "parent_account"
                        )
                        is None
                    ):
                        account[
                            "parent_account"
                        ] = matching_group[
                            "account_number"
                        ]

                    if (
                        account.get(
                            "level"
                        )
                        is None
                    ):
                        group_level = (
                            matching_group.get(
                                "level"
                            )
                        )

                        if group_level is None:
                            group_level = (
                                matching_index
                            )

                        account["level"] = (
                            int(
                                group_level
                            )
                            + 1
                        )

                    hierarchy_stack = (
                        hierarchy_stack[
                            :matching_index
                        ]
                    )

                else:
                    if (
                        account.get(
                            "level"
                        )
                        is None
                    ):
                        account["level"] = 0

                continue

            #
            # POSTING / OTHER ACCOUNT TYPES
            #

            if (
                account.get(
                    "parent_account"
                )
                is None
                and hierarchy_stack
            ):
                account[
                    "parent_account"
                ] = hierarchy_stack[-1][
                    "account_number"
                ]

            if account.get("level") is None:
                account["level"] = len(
                    hierarchy_stack
                )

        self.accounts = accounts

        self.normalizer.register_accounts(
            self.accounts
        )

        return self.accounts

    def validate_hierarchy(
        self,
    ) -> dict[str, Any]:
        """
        Validate the hierarchy generated for the
        Chart of Accounts.

        This validation is separate from source-file
        validation. It checks the structural integrity
        of the AI-FOS account hierarchy after the
        hierarchy has been built.
        """

        if not self.accounts:
            raise ValueError(
                "Build the Chart of Accounts "
                "hierarchy before validating it."
            )

        errors: list[str] = []
        warnings: list[str] = []

        account_by_number = {
            str(
                account.get(
                    "account_number"
                )
                or ""
            ).strip(): account
            for account in self.accounts
            if str(
                account.get(
                    "account_number"
                )
                or ""
            ).strip()
        }

        orphan_parent_count = 0
        self_parent_count = 0
        invalid_level_count = 0
        negative_level_count = 0
        parent_level_mismatch_count = 0
        root_level_mismatch_count = 0
        unmatched_end_total_count = 0
        invalid_totaling_range_count = 0

        #
        # ACCOUNT-BY-ACCOUNT STRUCTURAL CHECKS
        #

        for account in self.accounts:
            account_number = str(
                account.get(
                    "account_number"
                )
                or ""
            ).strip()

            parent_account = account.get(
                "parent_account"
            )

            if parent_account is not None:
                parent_account = str(
                    parent_account
                ).strip()

            level = account.get("level")

            account_type = str(
                account.get(
                    "account_type"
                )
                or ""
            ).strip().lower()

            totaling = str(
                account.get(
                    "totaling"
                )
                or ""
            ).strip()

            #
            # Validate level.
            #

            if level is None:
                invalid_level_count += 1

            else:
                try:
                    level = int(level)

                    if level < 0:
                        negative_level_count += 1

                except (
                    TypeError,
                    ValueError,
                ):
                    invalid_level_count += 1
                    level = None

            #
            # Root accounts should normally
            # be level 0.
            #

            if (
                parent_account is None
                and level is not None
                and level != 0
            ):
                root_level_mismatch_count += 1

            #
            # Parent relationship checks.
            #

            if parent_account:
                if parent_account == account_number:
                    self_parent_count += 1

                elif (
                    parent_account
                    not in account_by_number
                ):
                    orphan_parent_count += 1

                else:
                    parent = account_by_number[
                        parent_account
                    ]

                    parent_level = parent.get(
                        "level"
                    )

                    try:
                        parent_level = int(
                            parent_level
                        )
                    except (
                        TypeError,
                        ValueError,
                    ):
                        parent_level = None

                    if (
                        level is not None
                        and parent_level is not None
                        and level
                        != parent_level + 1
                    ):
                        parent_level_mismatch_count += 1

            #
            # End-Total checks.
            #

            if account_type == "end-total":
                if ".." not in totaling:
                    unmatched_end_total_count += 1

                else:
                    (
                        range_start,
                        range_end,
                    ) = totaling.split(
                        "..",
                        1,
                    )

                    range_start = (
                        range_start.strip()
                    )

                    range_end = (
                        range_end.strip()
                    )

                    if (
                        not range_start
                        or not range_end
                    ):
                        invalid_totaling_range_count += 1

                    elif (
                        range_start
                        not in account_by_number
                    ):
                        unmatched_end_total_count += 1

                    elif (
                        parent_account
                        != range_start
                    ):
                        unmatched_end_total_count += 1

        #
        # REPORT RESULTS
        #

        if orphan_parent_count:
            errors.append(
                f"{orphan_parent_count} account(s) "
                "reference a parent account that "
                "does not exist."
            )

        if self_parent_count:
            errors.append(
                f"{self_parent_count} account(s) "
                "reference themselves as parent."
            )

        if invalid_level_count:
            errors.append(
                f"{invalid_level_count} account(s) "
                "have a missing or invalid "
                "hierarchy level."
            )

        if negative_level_count:
            errors.append(
                f"{negative_level_count} account(s) "
                "have a negative hierarchy level."
            )

        if parent_level_mismatch_count:
            errors.append(
                f"{parent_level_mismatch_count} "
                "account(s) do not sit exactly one "
                "level below their parent."
            )

        if root_level_mismatch_count:
            warnings.append(
                f"{root_level_mismatch_count} "
                "root account(s) are not at "
                "hierarchy level 0."
            )

        if unmatched_end_total_count:
            warnings.append(
                f"{unmatched_end_total_count} "
                "End-Total account(s) could not be "
                "cleanly matched to their "
                "Begin-Total account."
            )

        if invalid_totaling_range_count:
            warnings.append(
                f"{invalid_totaling_range_count} "
                "End-Total account(s) have an "
                "invalid totaling range."
            )

        root_accounts = sum(
            1
            for account in self.accounts
            if not account.get(
                "parent_account"
            )
        )

        posting_accounts = sum(
            1
            for account in self.accounts
            if str(
                account.get(
                    "account_type"
                )
                or ""
            ).strip().lower()
            == "posting"
        )

        structural_accounts = (
            len(self.accounts)
            - posting_accounts
        )

        max_level = max(
            (
                int(account.get("level"))
                for account in self.accounts
                if account.get("level")
                is not None
                and str(
                    account.get("level")
                ).lstrip("-")
                .isdigit()
            ),
            default=0,
        )

        return {
            "errors": errors,
            "warnings": warnings,
            "summary": {
                "account_count": len(
                    self.accounts
                ),
                "root_account_count": (
                    root_accounts
                ),
                "posting_account_count": (
                    posting_accounts
                ),
                "structural_account_count": (
                    structural_accounts
                ),
                "maximum_hierarchy_level": (
                    max_level
                ),
                "orphan_parent_count": (
                    orphan_parent_count
                ),
                "self_parent_count": (
                    self_parent_count
                ),
                "invalid_level_count": (
                    invalid_level_count
                ),
                "negative_level_count": (
                    negative_level_count
                ),
                "parent_level_mismatch_count": (
                    parent_level_mismatch_count
                ),
                "root_level_mismatch_count": (
                    root_level_mismatch_count
                ),
                "unmatched_end_total_count": (
                    unmatched_end_total_count
                ),
                "invalid_totaling_range_count": (
                    invalid_totaling_range_count
                ),
            },
        }

    def enrich_accounts(
        self,
    ) -> list[dict[str, Any]]:
        """
        Preserve imported ERP classifications and
        use the fallback classifier only when
        financial metadata is missing.
        """

        from app.services.account_classifier import (
            classify_account,
        )

        if not self.accounts:
            raise ValueError(
                "Build the Chart of Accounts "
                "hierarchy before enrichment."
            )

        for account in self.accounts:
            classification = classify_account(
                account_number=(
                    account[
                        "account_number"
                    ]
                ),
                account_name=(
                    account[
                        "account_name"
                    ]
                ),
            )

            if not account.get(
                "financial_category"
            ):
                account[
                    "financial_category"
                ] = classification[
                    "financial_category"
                ]

            if not account.get(
                "financial_subcategory"
            ):
                account[
                    "financial_subcategory"
                ] = classification[
                    "financial_subcategory"
                ]

            if not account.get(
                "normal_balance"
            ):
                account[
                    "normal_balance"
                ] = classification[
                    "normal_balance"
                ]

            if (
                account.get(
                    "classification_confidence"
                )
                is None
            ):
                account[
                    "classification_confidence"
                ] = classification[
                    "classification_confidence"
                ]

            account["requires_review"] = (
                not account.get(
                    "financial_category"
                )
                or account[
                    "financial_category"
                ]
                == "Unknown"
            )

            is_cash_account = (
                account.get("financial_category") == "Asset"
                and account.get("financial_subcategory")
                in {"Cash", "Cash and Bank"}
                and account.get("is_posting_account") is True
            )

            if is_cash_account:
                account["liquidity_status"] = "Available"
            else:
                account["liquidity_status"] = "Not Applicable"            

        self.normalizer.register_accounts(
            self.accounts
        )

        return self.accounts

    def get_accounts(self):
        return self.accounts