from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


class OrganizationRegistryService:
    """
    Persistent backend source of truth for
    AI-FOS organizations.

    Organization codes such as "acss" are stable
    application identifiers used by workspaces,
    API routes, readiness, and the frontend.

    This registry is intentionally separate from
    the legacy SQL Organisation table until the
    tenant/onboarding architecture is migrated
    deliberately.
    """

    def __init__(
        self,
        registry_file: Path | str = (
            "data/organization_registry.json"
        ),
    ) -> None:
        self.registry_file = Path(
            registry_file
        )

    def _ensure_registry(self) -> None:
        self.registry_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if self.registry_file.exists():
            return

        initial_registry = {
            "organizations": [
                {
                    "id": "acss",
                    "name": "ACSS",
                    "base_currency": "USD",
                    "active": True,
                },
                {
                    "id": "naacss",
                    "name": "NAACSS",
                    "base_currency": "USD",
                    "active": True,
                },
            ]
        }

        self._write_registry(
            initial_registry
        )

    def _read_registry(
        self,
    ) -> dict[str, Any]:
        self._ensure_registry()

        try:
            with self.registry_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)
        except (
            OSError,
            json.JSONDecodeError,
        ):
            return {
                "organizations": [],
            }

        if not isinstance(data, dict):
            return {
                "organizations": [],
            }

        organizations = data.get(
            "organizations",
            [],
        )

        if not isinstance(
            organizations,
            list,
        ):
            organizations = []

        return {
            "organizations": organizations,
        }

    def _write_registry(
        self,
        data: dict[str, Any],
    ) -> None:
        self.registry_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with self.registry_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

    @staticmethod
    def normalize_organisation_id(
        organisation_id: str,
    ) -> str:
        normalized_id = (
            str(organisation_id)
            .strip()
            .lower()
        )

        normalized_id = re.sub(
            r"[^a-z0-9_-]+",
            "-",
            normalized_id,
        )

        normalized_id = re.sub(
            r"-+",
            "-",
            normalized_id,
        )

        return normalized_id.strip(
            "-_"
        )

    def list_organizations(
        self,
        active_only: bool = True,
    ) -> list[dict[str, Any]]:
        data = self._read_registry()

        organizations = data.get(
            "organizations",
            [],
        )

        clean_organizations = []

        for organization in organizations:
            if not isinstance(
                organization,
                dict,
            ):
                continue

            organisation_id = (
                self.normalize_organisation_id(
                    organization.get(
                        "id",
                        "",
                    )
                )
            )

            name = str(
                organization.get(
                    "name",
                    "",
                )
            ).strip()

            base_currency = (
                str(
                    organization.get(
                        "base_currency",
                        "USD",
                    )
                )
                .strip()
                .upper()
            )

            active = bool(
                organization.get(
                    "active",
                    True,
                )
            )

            if (
                not organisation_id
                or not name
            ):
                continue

            if (
                active_only
                and not active
            ):
                continue

            clean_organizations.append(
                {
                    "id": organisation_id,
                    "name": name,
                    "base_currency": (
                        base_currency
                    ),
                    "active": active,
                }
            )

        clean_organizations.sort(
            key=lambda item: (
                item["name"].lower()
            )
        )

        return clean_organizations

    def get_organization(
        self,
        organisation_id: str,
    ) -> dict[str, Any] | None:
        normalized_id = (
            self.normalize_organisation_id(
                organisation_id
            )
        )

        for organization in (
            self.list_organizations(
                active_only=False,
            )
        ):
            if (
                organization["id"]
                == normalized_id
            ):
                return organization

        return None

    def create_organization(
        self,
        organisation_id: str,
        name: str,
        base_currency: str = "USD",
    ) -> dict[str, Any]:
        normalized_id = (
            self.normalize_organisation_id(
                organisation_id
            )
        )

        normalized_name = str(
            name
        ).strip()

        normalized_currency = (
            str(base_currency)
            .strip()
            .upper()
        )

        if not normalized_id:
            raise ValueError(
                "Organization ID is required."
            )

        if not normalized_name:
            raise ValueError(
                "Organization name is required."
            )

        if (
            len(normalized_currency)
            != 3
            or not normalized_currency.isalpha()
        ):
            raise ValueError(
                "Base currency must be a "
                "3-letter currency code."
            )

        if self.get_organization(
            normalized_id
        ):
            raise ValueError(
                "Organization already exists."
            )

        data = self._read_registry()

        organizations = data.get(
            "organizations",
            [],
        )

        organization = {
            "id": normalized_id,
            "name": normalized_name,
            "base_currency": (
                normalized_currency
            ),
            "active": True,
        }

        organizations.append(
            organization
        )

        data["organizations"] = (
            organizations
        )

        self._write_registry(
            data
        )

        return organization