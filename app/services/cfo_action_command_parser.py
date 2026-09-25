import re
from datetime import date, datetime
from typing import Any


class CFOActionCommandParser:
    """
    Deterministic natural-language parser for CFO management
    action commands.

    This parser performs interpretation only.

    It never:
    - resolves persisted CFO actions,
    - mutates organizational state,
    - invents owners,
    - invents due dates,
    - invents progress,
    - invents management notes.

    Parsed commands must still pass through
    CFOActionCommandService before any mutation can occur.
    """

    MONTHS = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }

    # ==================================================
    # NORMALIZATION
    # ==================================================

    @staticmethod
    def _clean_text(
        value: Any,
    ) -> str:
        return " ".join(
            str(value or "")
            .strip()
            .split()
        )

    @staticmethod
    def _clean_reference(
        value: Any,
    ) -> str:
        text = CFOActionCommandParser._clean_text(
            value
        )

        text = re.sub(
            r"\b(?:the|this)\b",
            " ",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\baction\b",
            " ",
            text,
            flags=re.IGNORECASE,
        )

        text = " ".join(
            text.split()
        )

        return text.strip(
            " .,:;-"
        )

    @staticmethod
    def _result(
        command: str,
        *,
        action_reference: str,
        **values: Any,
    ) -> dict[str, Any]:
        reference = (
            CFOActionCommandParser._clean_reference(
                action_reference
            )
        )

        if not reference:
            raise ValueError(
                "Action reference is required."
            )

        result: dict[str, Any] = {
            "command": command,
            "action_reference": reference,
        }

        result.update(values)

        return result

    # ==================================================
    # DATE PARSING
    # ==================================================

    @staticmethod
    def _parse_date(
        value: Any,
        *,
        reference_date: date | None = None,
    ) -> str:
        text = (
            CFOActionCommandParser._clean_text(
                value
            )
            .strip(" .")
        )

        if not text:
            raise ValueError(
                "Due date is required."
            )

        # ISO YYYY-MM-DD
        try:
            return date.fromisoformat(
                text
            ).isoformat()

        except ValueError:
            pass

        # Month DD YYYY
        match = re.fullmatch(
            (
                r"(?P<month>[A-Za-z]+)"
                r"\s+"
                r"(?P<day>\d{1,2})"
                r"(?:,)?"
                r"(?:\s+(?P<year>\d{4}))?"
            ),
            text,
        )

        if match is None:
            raise ValueError(
                "Could not understand the due date."
            )

        month_name = (
            match.group("month")
            .lower()
        )

        month = (
            CFOActionCommandParser.MONTHS.get(
                month_name
            )
        )

        if month is None:
            raise ValueError(
                "Could not understand the due date."
            )

        day = int(
            match.group("day")
        )

        explicit_year = (
            match.group("year")
        )

        if explicit_year is not None:
            year = int(
                explicit_year
            )

        else:
            today = (
                reference_date
                or date.today()
            )

            year = today.year

            candidate = date(
                year,
                month,
                day,
            )

            if candidate < today:
                year += 1

        try:
            parsed = date(
                year,
                month,
                day,
            )

        except ValueError as exc:
            raise ValueError(
                "Could not understand the due date."
            ) from exc

        return parsed.isoformat()

    # ==================================================
    # MAIN PARSER
    # ==================================================

    @staticmethod
    def parse(
        text: Any,
        *,
        reference_date: date | None = None,
    ) -> dict[str, Any]:
        """
        Parse one explicit CFO action command.

        Pronoun-only references such as:
            "assign it to Elie"
            "mark it completed"

        are intentionally rejected in v1 because safe conversation
        context resolution is handled separately.
        """

        original = (
            CFOActionCommandParser._clean_text(
                text
            )
        )

        if not original:
            raise ValueError(
                "CFO action command is required."
            )

        # ----------------------------------------------
        # Reject unsupported pronoun-only targeting
        # ----------------------------------------------

        if re.search(
            r"\b(?:it|its|that|this)\b",
            original,
            flags=re.IGNORECASE,
        ):
            pronoun_patterns = [
                r"^\s*assign\s+(?:it|that|this)\b",
                r"^\s*unassign\s+(?:it|that|this)\b",
                r"^\s*(?:start|begin)\s+(?:it|that|this)\b",
                r"^\s*(?:block|unblock)\s+(?:it|that|this)\b",
                r"^\s*(?:complete|cancel|reopen)\s+(?:it|that|this)\b",
                r"^\s*mark\s+(?:it|that|this)\b",
                r"^\s*(?:set|change|update)\s+(?:its|that|this)\b",
            ]

            if any(
                re.search(
                    pattern,
                    original,
                    flags=re.IGNORECASE,
                )
                for pattern in pronoun_patterns
            ):
                raise ValueError(
                    "Explicit action reference is required."
                )

        # ----------------------------------------------
        # ASSIGN
        # ----------------------------------------------

        match = re.fullmatch(
            (
                r"assign\s+"
                r"(?P<reference>.+?)"
                r"\s+to\s+"
                r"(?P<owner>.+?)"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            owner = (
                CFOActionCommandParser._clean_text(
                    match.group("owner")
                )
                .strip(" .")
            )

            if not owner:
                raise ValueError(
                    "Action owner is required."
                )

            return CFOActionCommandParser._result(
                "assign",
                action_reference=match.group(
                    "reference"
                ),
                owner=owner,
            )

        # ----------------------------------------------
        # UNASSIGN
        # ----------------------------------------------

        match = re.fullmatch(
            (
                r"(?:unassign|remove\s+owner\s+from)\s+"
                r"(?P<reference>.+?)"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            return CFOActionCommandParser._result(
                "unassign",
                action_reference=match.group(
                    "reference"
                ),
            )

        # ----------------------------------------------
        # SET DUE DATE
        # ----------------------------------------------

        # Form:
        # "Set the deadline for funding gap action to ..."
        match = re.fullmatch(
            (
                r"(?:set|change|update)\s+"
                r"(?:the\s+)?"
                r"(?:deadline|due\s+date)\s+"
                r"(?:for|of)\s+"
                r"(?P<reference>.+?)"
                r"\s+to\s+"
                r"(?P<due_date>.+?)"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            due_date = (
                CFOActionCommandParser._parse_date(
                    match.group("due_date"),
                    reference_date=reference_date,
                )
            )

            return CFOActionCommandParser._result(
                "set_due_date",
                action_reference=match.group(
                    "reference"
                ),
                due_date=due_date,
            )

        # Form:
        # "Set the funding gap action deadline to ..."
        match = re.fullmatch(
            (
                r"(?:set|change|update)\s+"
                r"(?P<reference>.+?)"
                r"(?:'s)?\s+"
                r"(?:deadline|due\s+date)\s+"
                r"(?:to\s+)?"
                r"(?P<due_date>.+?)"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            due_date = (
                CFOActionCommandParser._parse_date(
                    match.group("due_date"),
                    reference_date=reference_date,
                )
            )

            return CFOActionCommandParser._result(
                "set_due_date",
                action_reference=match.group(
                    "reference"
                ),
                due_date=due_date,
            )

        # ----------------------------------------------
        # CLEAR DUE DATE
        # ----------------------------------------------

        match = re.fullmatch(
            (
                r"(?:clear|remove)\s+"
                r"(?:the\s+)?"
                r"(?:deadline|due\s+date)\s+"
                r"(?:for|from)\s+"
                r"(?P<reference>.+?)"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            return CFOActionCommandParser._result(
                "clear_due_date",
                action_reference=match.group(
                    "reference"
                ),
            )

        # ----------------------------------------------
        # PROGRESS
        # ----------------------------------------------

        match = re.fullmatch(
            (
                r"(?:update|set|mark)\s+"
                r"(?P<reference>.+?)"
                r"\s+(?:to|at)\s+"
                r"(?P<progress>\d+(?:\.\d+)?)"
                r"\s*%"
                r"(?:\s+complete)?"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            progress = float(
                match.group("progress")
            )

            if (
                progress < 0
                or progress > 100
            ):
                raise ValueError(
                    "Progress percentage must be between 0 and 100."
                )

            return CFOActionCommandParser._result(
                "update_progress",
                action_reference=match.group(
                    "reference"
                ),
                progress_percentage=progress,
            )

        # ----------------------------------------------
        # START
        # ----------------------------------------------

        match = re.fullmatch(
            (
                r"(?:start|begin)\s+"
                r"(?P<reference>.+?)"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            return CFOActionCommandParser._result(
                "start",
                action_reference=match.group(
                    "reference"
                ),
            )

        # ----------------------------------------------
        # BLOCK
        # ----------------------------------------------

        match = re.fullmatch(
            (
                r"block\s+"
                r"(?P<reference>.+?)"
                r"(?:\s*[-:]\s*"
                r"(?P<notes>.+?))?"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            notes = (
                CFOActionCommandParser._clean_text(
                    match.group("notes")
                )
                .strip(" .")
                if match.group("notes")
                else None
            )

            return CFOActionCommandParser._result(
                "block",
                action_reference=match.group(
                    "reference"
                ),
                management_notes=notes,
            )

        # ----------------------------------------------
        # UNBLOCK
        # ----------------------------------------------

        match = re.fullmatch(
            (
                r"unblock\s+"
                r"(?P<reference>.+?)"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            return CFOActionCommandParser._result(
                "unblock",
                action_reference=match.group(
                    "reference"
                ),
            )

        # ----------------------------------------------
        # COMPLETE
        # ----------------------------------------------

        match = re.fullmatch(
            (
                r"(?:complete|mark)\s+"
                r"(?P<reference>.+?)"
                r"(?:\s+as)?\s+"
                r"(?:completed|complete)"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            return CFOActionCommandParser._result(
                "complete",
                action_reference=match.group(
                    "reference"
                ),
            )

        # Alternative:
        # "Complete the funding gap action"
        match = re.fullmatch(
            (
                r"complete\s+"
                r"(?P<reference>.+?)"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            return CFOActionCommandParser._result(
                "complete",
                action_reference=match.group(
                    "reference"
                ),
            )

        # ----------------------------------------------
        # REOPEN
        # ----------------------------------------------

        match = re.fullmatch(
            (
                r"reopen\s+"
                r"(?P<reference>.+?)"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            return CFOActionCommandParser._result(
                "reopen",
                action_reference=match.group(
                    "reference"
                ),
            )

        # ----------------------------------------------
        # CANCEL
        # ----------------------------------------------

        match = re.fullmatch(
            (
                r"cancel\s+"
                r"(?P<reference>.+?)"
                r"(?:\s*[-:]\s*"
                r"(?P<notes>.+?))?"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            notes = (
                CFOActionCommandParser._clean_text(
                    match.group("notes")
                )
                .strip(" .")
                if match.group("notes")
                else None
            )

            return CFOActionCommandParser._result(
                "cancel",
                action_reference=match.group(
                    "reference"
                ),
                management_notes=notes,
            )

        # ----------------------------------------------
        # MANAGEMENT NOTES
        # ----------------------------------------------

        match = re.fullmatch(
            (
                r"(?:add|update|set)\s+"
                r"(?:a\s+)?"
                r"(?:management\s+)?note\s+"
                r"(?:for|on)\s+"
                r"(?P<reference>.+?)"
                r"\s*[-:]\s*"
                r"(?P<notes>.+?)"
                r"[.]?"
            ),
            original,
            flags=re.IGNORECASE,
        )

        if match is not None:
            notes = (
                CFOActionCommandParser._clean_text(
                    match.group("notes")
                )
                .strip(" .")
            )

            if not notes:
                raise ValueError(
                    "Management note is required."
                )

            return CFOActionCommandParser._result(
                "update_notes",
                action_reference=match.group(
                    "reference"
                ),
                management_notes=notes,
            )

        # ----------------------------------------------
        # UNKNOWN / UNSAFE
        # ----------------------------------------------

        raise ValueError(
            "Could not safely understand the CFO action command."
        )