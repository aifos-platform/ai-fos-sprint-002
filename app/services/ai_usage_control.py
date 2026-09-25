from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class AIUsageControlService:
    """
    Control and record OpenAI usage for AI-FOS organizations.

    Responsibilities:

    1. Maintain organization-level AI usage policies.
    2. Check whether a paid AI request is authorized.
    3. Record actual OpenAI token consumption.
    4. Report current usage against configured allowances.

    Deterministic AI-FOS functionality is intentionally
    outside this service and must remain available even when
    an organization's OpenAI allowance has been exhausted.
    """

    DEFAULT_MONTHLY_TOKEN_ALLOWANCE = 250_000

    DEFAULT_DAILY_TOKEN_ALLOWANCE = 50_000

    DEFAULT_MAX_OUTPUT_TOKENS_PER_REQUEST = 4_000

    def __init__(
        self,
        storage_root: Path | str = (
            "data/ai_usage"
        ),
    ) -> None:
        self.storage_root = Path(
            storage_root
        )

        self.policy_file = (
            self.storage_root
            / "policies.json"
        )

        self.ledger_file = (
            self.storage_root
            / "usage_ledger.json"
        )

    # --------------------------------------------------
    # Policy
    # --------------------------------------------------

    def get_policy(
        self,
        organisation_id: str,
    ) -> dict[str, Any]:
        """
        Return the organization's effective AI policy.

        Organizations without an explicit policy receive
        conservative default limits.
        """

        organisation_id = (
            self._normalize_organisation_id(
                organisation_id
            )
        )

        policies = self._read_policies()

        configured_policy = (
            policies.get(
                organisation_id,
                {},
            )
            or {}
        )

        return {
            "organisation_id": organisation_id,
            "enabled": bool(
                configured_policy.get(
                    "enabled",
                    True,
                )
            ),
            "plan": str(
                configured_policy.get(
                    "plan",
                    "default",
                )
                or "default"
            ),
            "monthly_token_allowance": (
                self._positive_int(
                    configured_policy.get(
                        "monthly_token_allowance"
                    ),
                    self.DEFAULT_MONTHLY_TOKEN_ALLOWANCE,
                )
            ),
            "daily_token_allowance": (
                self._positive_int(
                    configured_policy.get(
                        "daily_token_allowance"
                    ),
                    self.DEFAULT_DAILY_TOKEN_ALLOWANCE,
                )
            ),
            "max_output_tokens_per_request": (
                self._positive_int(
                    configured_policy.get(
                        "max_output_tokens_per_request"
                    ),
                    self.DEFAULT_MAX_OUTPUT_TOKENS_PER_REQUEST,
                )
            ),
            "general_cfo_enabled": bool(
                configured_policy.get(
                    "general_cfo_enabled",
                    True,
                )
            ),
            "verified_cfo_reasoning_enabled": bool(
                configured_policy.get(
                    "verified_cfo_reasoning_enabled",
                    True,
                )
            ),
        }

    def set_policy(
        self,
        organisation_id: str,
        *,
        plan: str = "default",
        enabled: bool = True,
        monthly_token_allowance: int | None = None,
        daily_token_allowance: int | None = None,
        max_output_tokens_per_request: int | None = None,
        general_cfo_enabled: bool = True,
        verified_cfo_reasoning_enabled: bool = True,
    ) -> dict[str, Any]:
        """
        Persist an explicit organization AI policy.
        """

        organisation_id = (
            self._normalize_organisation_id(
                organisation_id
            )
        )

        if not organisation_id:
            raise ValueError(
                "Organisation ID is required."
            )

        policy = {
            "enabled": bool(
                enabled
            ),
            "plan": str(
                plan or "default"
            ).strip(),
            "monthly_token_allowance": (
                self._positive_int(
                    monthly_token_allowance,
                    self.DEFAULT_MONTHLY_TOKEN_ALLOWANCE,
                )
            ),
            "daily_token_allowance": (
                self._positive_int(
                    daily_token_allowance,
                    self.DEFAULT_DAILY_TOKEN_ALLOWANCE,
                )
            ),
            "max_output_tokens_per_request": (
                self._positive_int(
                    max_output_tokens_per_request,
                    self.DEFAULT_MAX_OUTPUT_TOKENS_PER_REQUEST,
                )
            ),
            "general_cfo_enabled": bool(
                general_cfo_enabled
            ),
            "verified_cfo_reasoning_enabled": bool(
                verified_cfo_reasoning_enabled
            ),
        }

        policies = self._read_policies()

        policies[
            organisation_id
        ] = policy

        self._write_json(
            self.policy_file,
            policies,
        )

        return self.get_policy(
            organisation_id
        )

    # --------------------------------------------------
    # Authorization
    # --------------------------------------------------

    def authorize(
        self,
        organisation_id: str,
        request_type: str,
    ) -> dict[str, Any]:
        """
        Decide whether an OpenAI request may proceed.

        request_type examples:

        - general_cfo
        - verified_cfo_reasoning
        """

        policy = self.get_policy(
            organisation_id
        )

        if not policy["enabled"]:
            return self._denied(
                organisation_id=organisation_id,
                reason="ai_disabled",
                policy=policy,
            )

        request_type = (
            str(
                request_type or ""
            )
            .strip()
            .lower()
        )

        if (
            request_type == "general_cfo"
            and not policy[
                "general_cfo_enabled"
            ]
        ):
            return self._denied(
                organisation_id=organisation_id,
                reason="general_cfo_disabled",
                policy=policy,
            )

        if (
            request_type
            == "verified_cfo_reasoning"
            and not policy[
                "verified_cfo_reasoning_enabled"
            ]
        ):
            return self._denied(
                organisation_id=organisation_id,
                reason=(
                    "verified_cfo_reasoning_disabled"
                ),
                policy=policy,
            )

        usage = self.get_usage_summary(
            organisation_id
        )

        if (
            usage["month"]["total_tokens"]
            >= policy[
                "monthly_token_allowance"
            ]
        ):
            return self._denied(
                organisation_id=organisation_id,
                reason=(
                    "monthly_token_limit_reached"
                ),
                policy=policy,
                usage=usage,
            )

        if (
            usage["today"]["total_tokens"]
            >= policy[
                "daily_token_allowance"
            ]
        ):
            return self._denied(
                organisation_id=organisation_id,
                reason=(
                    "daily_token_limit_reached"
                ),
                policy=policy,
                usage=usage,
            )

        return {
            "allowed": True,
            "organisation_id": (
                self._normalize_organisation_id(
                    organisation_id
                )
            ),
            "reason": "authorized",
            "request_type": request_type,
            "policy": policy,
            "usage": usage,
            "max_output_tokens": policy[
                "max_output_tokens_per_request"
            ],
        }

    # --------------------------------------------------
    # Usage recording
    # --------------------------------------------------

    def record_usage(
        self,
        organisation_id: str,
        request_type: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        status: str = "success",
    ) -> dict[str, Any]:
        """
        Record actual token usage returned by OpenAI.

        Token values are recorded as supplied by the API.
        This service does not estimate financial cost.
        """

        organisation_id = (
            self._normalize_organisation_id(
                organisation_id
            )
        )

        entry = {
            "timestamp": (
                datetime.now(
                    timezone.utc
                ).isoformat()
            ),
            "organisation_id": (
                organisation_id
            ),
            "request_type": (
                str(
                    request_type or ""
                )
                .strip()
                .lower()
            ),
            "model": str(
                model or ""
            ).strip(),
            "input_tokens": (
                self._non_negative_int(
                    input_tokens
                )
            ),
            "output_tokens": (
                self._non_negative_int(
                    output_tokens
                )
            ),
            "total_tokens": (
                self._non_negative_int(
                    total_tokens
                )
            ),
            "status": str(
                status or "unknown"
            ).strip(),
        }

        ledger = self._read_ledger()

        ledger.append(
            entry
        )

        self._write_json(
            self.ledger_file,
            ledger,
        )

        return entry

    # --------------------------------------------------
    # Reporting
    # --------------------------------------------------

    def get_usage_summary(
        self,
        organisation_id: str,
    ) -> dict[str, Any]:
        organisation_id = (
            self._normalize_organisation_id(
                organisation_id
            )
        )

        now = datetime.now(
            timezone.utc
        )

        today_key = (
            now.date()
            .isoformat()
        )

        month_key = (
            now.strftime(
                "%Y-%m"
            )
        )

        today_totals = (
            self._empty_totals()
        )

        month_totals = (
            self._empty_totals()
        )

        for entry in self._read_ledger():
            if not isinstance(
                entry,
                dict,
            ):
                continue

            if (
                self._normalize_organisation_id(
                    entry.get(
                        "organisation_id",
                        "",
                    )
                )
                != organisation_id
            ):
                continue

            timestamp = str(
                entry.get(
                    "timestamp",
                    "",
                )
            )

            if timestamp.startswith(
                today_key
            ):
                self._add_entry(
                    today_totals,
                    entry,
                )

            if timestamp.startswith(
                month_key
            ):
                self._add_entry(
                    month_totals,
                    entry,
                )

        return {
            "organisation_id": (
                organisation_id
            ),
            "today": today_totals,
            "month": month_totals,
        }

    # --------------------------------------------------
    # Persistence
    # --------------------------------------------------

    def _read_policies(
        self,
    ) -> dict[str, Any]:
        data = self._read_json(
            self.policy_file,
            {},
        )

        if not isinstance(
            data,
            dict,
        ):
            return {}

        return data

    def _read_ledger(
        self,
    ) -> list[dict[str, Any]]:
        data = self._read_json(
            self.ledger_file,
            [],
        )

        if not isinstance(
            data,
            list,
        ):
            return []

        return data

    @staticmethod
    def _read_json(
        path: Path,
        default: Any,
    ) -> Any:
        if not path.exists():
            return default

        try:
            with path.open(
                "r",
                encoding="utf-8",
            ) as file:
                return json.load(
                    file
                )

        except (
            OSError,
            json.JSONDecodeError,
        ):
            return default

    @staticmethod
    def _write_json(
        path: Path,
        data: Any,
    ) -> None:
        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    @staticmethod
    def _empty_totals(
        ) -> dict[str, int]:
        return {
            "requests": 0,
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    def _add_entry(
        self,
        totals: dict[str, int],
        entry: dict[str, Any],
    ) -> None:
        totals["requests"] += 1

        totals[
            "input_tokens"
        ] += self._non_negative_int(
            entry.get(
                "input_tokens"
            )
        )

        totals[
            "output_tokens"
        ] += self._non_negative_int(
            entry.get(
                "output_tokens"
            )
        )

        totals[
            "total_tokens"
        ] += self._non_negative_int(
            entry.get(
                "total_tokens"
            )
        )

    @staticmethod
    def _denied(
        organisation_id: str,
        reason: str,
        policy: dict[str, Any],
        usage: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "allowed": False,
            "organisation_id": (
                str(
                    organisation_id
                )
                .strip()
                .lower()
            ),
            "reason": reason,
            "policy": policy,
            "usage": (
                usage
                or {}
            ),
        }

    @staticmethod
    def _normalize_organisation_id(
        organisation_id: Any,
    ) -> str:
        return (
            str(
                organisation_id
                or ""
            )
            .strip()
            .lower()
        )

    @staticmethod
    def _positive_int(
        value: Any,
        default: int,
    ) -> int:
        try:
            parsed = int(
                value
            )

        except (
            TypeError,
            ValueError,
        ):
            return default

        if parsed <= 0:
            return default

        return parsed

    @staticmethod
    def _non_negative_int(
        value: Any,
    ) -> int:
        try:
            parsed = int(
                value or 0
            )

        except (
            TypeError,
            ValueError,
        ):
            return 0

        return max(
            parsed,
            0,
        )