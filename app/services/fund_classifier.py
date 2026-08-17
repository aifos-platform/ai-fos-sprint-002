from __future__ import annotations

from typing import Any


class FundClassifier:
    """
    Classify organisation fund codes into business meanings.

    Important:
    - A Fund Code is not automatically a Grant.
    - Classification is separate from transaction accounting treatment.
    - The classifier should prefer explicit metadata when available.
    - Organisation-specific hard-coded codes should be avoided where possible.
    """

    FUND_TYPE_GRANT = "Grant"
    FUND_TYPE_ORGANISATIONAL = "Organisational"
    FUND_TYPE_UNRESTRICTED = "Unrestricted"
    FUND_TYPE_INTERNAL = "Internal"
    FUND_TYPE_OTHER = "Other"
    FUND_TYPE_UNKNOWN = "Unknown"

    NON_GRANT_NAME_PATTERNS = (
        "organisational",
        "organizational",
        "organisation",
        "organization",
        "core",
        "unrestricted",
        "general fund",
        "general operating",
        "operating fund",
        "internal",
        "administrative",
        "administration",
        "own funds",
        "own fund",
    )

    GRANT_NAME_PATTERNS = (
        "grant",
        "donor",
        "award",
        "agreement",
        "project grant",
    )

    def classify(
        self,
        fund_code: Any = None,
        fund_name: Any = None,
        donor_code: Any = None,
        donor_name: Any = None,
        explicit_fund_type: Any = None,
        explicit_is_grant: Any = None,
    ) -> dict[str, Any]:
        """
        Classify one fund.

        Explicit metadata takes priority over inferred classification.
        """

        code = self._clean(fund_code)
        name = self._clean(fund_name)
        donor = self._clean(donor_code)
        donor_display_name = self._clean(donor_name)

        explicit_type = self._clean(
            explicit_fund_type
        )

        explicit_grant_flag = self._to_bool(
            explicit_is_grant
        )

        #
        # 1. Explicit fund type
        #
        if explicit_type:
            normalized_type = self._normalize_fund_type(
                explicit_type
            )

            return self._result(
                fund_code=code,
                fund_name=name,
                fund_type=normalized_type,
                is_grant=(
                    normalized_type
                    == self.FUND_TYPE_GRANT
                ),
                donor_code=donor,
                donor_name=donor_display_name,
                confidence=1.0,
                requires_review=False,
                reason=(
                    "Fund classification supplied explicitly."
                ),
            )

        #
        # 2. Explicit grant flag
        #
        if explicit_grant_flag is not None:
            return self._result(
                fund_code=code,
                fund_name=name,
                fund_type=(
                    self.FUND_TYPE_GRANT
                    if explicit_grant_flag
                    else self.FUND_TYPE_OTHER
                ),
                is_grant=explicit_grant_flag,
                donor_code=donor,
                donor_name=donor_display_name,
                confidence=1.0,
                requires_review=False,
                reason=(
                    "Grant status supplied explicitly."
                ),
            )

        name_lower = (
            name.lower()
            if name
            else ""
        )

        #
        # 3. Strong non-grant name signals
        #
        if any(
            pattern in name_lower
            for pattern in self.NON_GRANT_NAME_PATTERNS
        ):
            fund_type = (
                self.FUND_TYPE_UNRESTRICTED
                if "unrestricted" in name_lower
                else self.FUND_TYPE_ORGANISATIONAL
            )

            return self._result(
                fund_code=code,
                fund_name=name,
                fund_type=fund_type,
                is_grant=False,
                donor_code=donor,
                donor_name=donor_display_name,
                confidence=0.9,
                requires_review=False,
                reason=(
                    "Fund name indicates organisational "
                    "or non-grant funding."
                ),
            )

        #
        # 4. Strong grant name signals
        #
        if any(
            pattern in name_lower
            for pattern in self.GRANT_NAME_PATTERNS
        ):
            return self._result(
                fund_code=code,
                fund_name=name,
                fund_type=self.FUND_TYPE_GRANT,
                is_grant=True,
                donor_code=donor,
                donor_name=donor_display_name,
                confidence=0.9,
                requires_review=False,
                reason=(
                    "Fund name indicates donor/grant funding."
                ),
            )

        #
        # 5. Donor metadata is a useful signal,
        # but not sufficient by itself.
        #
        if donor or donor_display_name:
            return self._result(
                fund_code=code,
                fund_name=name,
                fund_type=self.FUND_TYPE_UNKNOWN,
                is_grant=None,
                donor_code=donor,
                donor_name=donor_display_name,
                confidence=0.5,
                requires_review=True,
                reason=(
                    "Donor metadata exists, but Fund Code alone "
                    "does not prove that this is a real grant."
                ),
            )

        #
        # 6. Unknown
        #
        return self._result(
            fund_code=code,
            fund_name=name,
            fund_type=self.FUND_TYPE_UNKNOWN,
            is_grant=None,
            donor_code=donor,
            donor_name=donor_display_name,
            confidence=0.0,
            requires_review=True,
            reason=(
                "Insufficient information to determine "
                "whether this fund is a grant."
            ),
        )

    @classmethod
    def _normalize_fund_type(
        cls,
        value: str,
    ) -> str:

        normalized = value.strip().lower()

        mapping = {
            "grant": cls.FUND_TYPE_GRANT,
            "donor grant": cls.FUND_TYPE_GRANT,
            "organisational": cls.FUND_TYPE_ORGANISATIONAL,
            "organizational": cls.FUND_TYPE_ORGANISATIONAL,
            "core": cls.FUND_TYPE_ORGANISATIONAL,
            "unrestricted": cls.FUND_TYPE_UNRESTRICTED,
            "internal": cls.FUND_TYPE_INTERNAL,
            "other": cls.FUND_TYPE_OTHER,
            "unknown": cls.FUND_TYPE_UNKNOWN,
        }

        return mapping.get(
            normalized,
            value.strip(),
        )

    @staticmethod
    def _result(
        fund_code: str | None,
        fund_name: str | None,
        fund_type: str,
        is_grant: bool | None,
        donor_code: str | None,
        donor_name: str | None,
        confidence: float,
        requires_review: bool,
        reason: str,
    ) -> dict[str, Any]:

        return {
            "fund_code": fund_code,
            "fund_name": fund_name,
            "fund_type": fund_type,
            "is_grant": is_grant,
            "donor_code": donor_code,
            "donor_name": donor_name,
            "classification_confidence": confidence,
            "requires_review": requires_review,
            "reason": reason,
        }

    @staticmethod
    def _clean(
        value: Any,
    ) -> str | None:

        if value is None:
            return None

        cleaned = str(value).strip()

        if not cleaned:
            return None

        if cleaned.lower() in {
            "none",
            "null",
            "nan",
        }:
            return None

        return cleaned

    @staticmethod
    def _to_bool(
        value: Any,
    ) -> bool | None:

        if value is None:
            return None

        if isinstance(value, bool):
            return value

        normalized = str(value).strip().lower()

        if normalized in {
            "true",
            "yes",
            "y",
            "1",
        }:
            return True

        if normalized in {
            "false",
            "no",
            "n",
            "0",
        }:
            return False

        return None