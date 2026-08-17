from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class OrganizationKnowledgeReader:
    """
    Reads the persistent organization knowledge
    stored by AI-FOS.
    """

    def load(
        self,
        folder: Path,
    ) -> dict[str, Any]:

        profile_file = folder / "organization_profile.json"

        if not profile_file.exists():
            return {}

        with profile_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)


    def load_fund_knowledge(
        self,
        folder: Path,
    ) -> dict[str, Any]:

        fund_knowledge_file = folder / "fund_knowledge.json"

        if not fund_knowledge_file.exists():
            return {}

        with fund_knowledge_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def get_summary(
        self,
        folder: Path,
    ) -> dict[str, Any]:

        profile = self.load(folder)

        if not profile:
            return {
                "status": "not_available",
                "message": (
                    "No organization knowledge " "profile has been created yet."
                ),
            }

        organisation = profile.get("organisation", {})

        financial_model = profile.get("financial_model", {})

        return {
            "status": "available",
            "organisation_id": organisation.get("id"),
            "organisation_name": organisation.get("name"),
            "source_system": profile.get("source_system"),
            "currency": profile.get("currency"),
            "transactions": financial_model.get(
                "transactions",
                0,
            ),
            "accounts": financial_model.get(
                "accounts",
                0,
            ),
            "funds": financial_model.get(
                "funds",
                0,
            ),
            "donors": financial_model.get(
                "donors",
                0,
            ),
            "programs": financial_model.get(
                "programs",
                0,
            ),
            "categories": financial_model.get(
                "categories",
                0,
            ),
            "budget_lines": financial_model.get(
                "budget_lines",
                0,
            ),
            "donor_lines": financial_model.get(
                "donor_lines",
                0,
            ),
            "calendar_dates": financial_model.get(
                "calendar_dates",
                0,
            ),
            "knowledge_updated_at": profile.get("knowledge_updated_at"),
        }
