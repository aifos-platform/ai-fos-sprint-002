from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


class OrganizationKnowledgeBuilder:
    """
    Builds and saves the persistent knowledge AI-FOS
    has learned about an organization.
    """

    def build(
        self,
        *,
        organisation_id: str,
        organisation_name: str,
        source_system: str,
        currency: str,
        transaction_count: int,
        dimension_summary: dict[str, Any],
        model_validation: dict[str, Any],
    ) -> dict[str, Any]:

        dimensions = dimension_summary.get(
            "dimensions",
            {}
        )

        def dimension_count(
            dimension_name: str,
        ) -> int:
            return int(
                dimensions
                .get(dimension_name, {})
                .get("total_count", 0)
                or 0
            )

        account_count = int(
            model_validation
            .get("dim_account", {})
            .get("record_count", 0)
            or 0
        )

        now = datetime.now().isoformat()

        return {
            "organisation": {
                "id": organisation_id,
                "name": organisation_name,
            },

            "source_system": source_system,
            "currency": currency,

            "financial_model": {
                "transactions": transaction_count,

                "accounts": account_count,

                "funds": dimension_count(
                    "fund"
                ),

                "donors": dimension_count(
                    "donor"
                ),

                "programs": dimension_count(
                    "program"
                ),

                "categories": dimension_count(
                    "category"
                ),

                "budget_lines": dimension_count(
                    "budget_line"
                ),

                "donor_lines": dimension_count(
                    "donor_line"
                ),

                "calendar_dates": dimension_count(
                    "calendar"
                ),
            },

            "knowledge_updated_at": now,
        }

    def save(
        self,
        *,
        profile: dict[str, Any],
        folder: Path,
    ) -> Path:

        folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        output_file = (
            folder
            / "organization_profile.json"
        )

        with output_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                profile,
                file,
                indent=4,
                ensure_ascii=False,
            )

        return output_file