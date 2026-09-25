from typing import Any


class DigitalCFOScopeGuard:
    """
    Decide whether a user question belongs inside the
    AI-FOS Digital CFO scope.

    This guard must run before any OpenAI call so that
    unrelated requests do not consume AI usage.

    It intentionally does not perform financial analysis.
    Its only responsibility is scope control.
    """

    def __init__(
        self,
        question_classifier: Any,
    ) -> None:
        self.question_classifier = (
            question_classifier
        )

    def evaluate(
        self,
        question: str,
    ) -> dict[str, Any]:
        cleaned_question = (
            str(question or "")
            .strip()
            .lower()
        )

        # --------------------------------------------------
        # Empty request
        # --------------------------------------------------

        if not cleaned_question:
            return {
                "allowed": False,
                "scope": "out_of_scope",
                "reason": "empty_question",
                "classifier_domain": "unknown",
                "classifier_intent": "unknown",
            }

        # --------------------------------------------------
        # Explicitly out-of-scope requests
        # --------------------------------------------------

        if self._is_clearly_out_of_scope(
            cleaned_question
        ):
            return {
                "allowed": False,
                "scope": "out_of_scope",
                "reason": "non_cfo_request",
                "classifier_domain": "unknown",
                "classifier_intent": "unknown",
            }

        # --------------------------------------------------
        # Existing AI-FOS classifier
        # --------------------------------------------------

        classification = (
            self.question_classifier
            .classify(
                question=question
            )
        )

        domain = self._normalize(
            classification.get(
                "domain"
            )
        )

        intent = self._normalize(
            classification.get(
                "intent"
            )
        )

        if (
            domain != "unknown"
            and intent != "unknown"
        ):
            return {
                "allowed": True,
                "scope": "cfo",
                "reason": "ai_fos_classified",
                "classifier_domain": domain,
                "classifier_intent": intent,
            }

        # --------------------------------------------------
        # General CFO / finance knowledge
        # --------------------------------------------------

        if self._contains_cfo_language(
            cleaned_question
        ):
            return {
                "allowed": True,
                "scope": "cfo",
                "reason": "general_cfo_scope",
                "classifier_domain": domain,
                "classifier_intent": intent,
            }

        # --------------------------------------------------
        # Conservative default
        # --------------------------------------------------

        return {
            "allowed": False,
            "scope": "out_of_scope",
            "reason": "scope_not_established",
            "classifier_domain": domain,
            "classifier_intent": intent,
        }

    @staticmethod
    def _contains_cfo_language(
        question: str,
    ) -> bool:
        """
        Recognize broad professional CFO topics that may not
        yet have deterministic AI-FOS intents.
        """

        finance_terms = (
            "accounting",
            "accountant",
            "audit",
            "auditor",
            "balance sheet",
            "bank reconciliation",
            "budget",
            "budgeting",
            "cash flow",
            "cashflow",
            "cash runway",
            "cfo",
            "chief financial officer",
            "cost control",
            "donor budget",
            "donor reporting",
            "ebitda",
            "expense",
            "expenses",
            "financial",
            "finance",
            "financial health",
            "financial management",
            "financial position",
            "financial report",
            "financial reporting",
            "financial statement",
            "forecast",
            "forecasting",
            "funding",
            "fundraising",
            "grant",
            "grants",
            "income statement",
            "liability",
            "liabilities",
            "liquidity",
            "management accounts",
            "management reporting",
            "net assets",
            "nonprofit finance",
            "ngo finance",
            "operating deficit",
            "operating surplus",
            "payables",
            "profit",
            "profitability",
            "receivables",
            "restricted fund",
            "restricted funding",
            "revenue",
            "risk",
            "scenario planning",
            "surplus",
            "tax",
            "treasury",
            "variance",
            "working capital",
        )

        return any(
            term in question
            for term in finance_terms
        )

    @staticmethod
    def _is_clearly_out_of_scope(
        question: str,
    ) -> bool:
        """
        Block obvious non-CFO use cases before OpenAI.

        This list is intentionally limited to clear categories.
        The guard should not become a giant blacklist.
        """

        # --------------------------------------------------
        # Clear creative-content requests
        # --------------------------------------------------
        #
        # Detect the request pattern rather than attempting
        # to enumerate every possible type of song or poem.
        #

        creative_content_terms = (
            "song",
            "poem",
            "love letter",
        )

        creative_action_terms = (
            "write",
            "create",
            "compose",
            "make",
        )

        if (
            any(
                term in question
                for term in creative_content_terms
            )
            and any(
                term in question
                for term in creative_action_terms
            )
        ):
            return True

        # --------------------------------------------------
        # Clear non-CFO request categories
        # --------------------------------------------------

        out_of_scope_phrases = (
            "write me a song",
            "write a song",
            "write me a poem",
            "write a poem",
            "birthday poem",
            "recipe",
            "how do i cook",
            "how to cook",
            "plan my vacation",
            "plan my holiday",
            "travel itinerary",
            "hotel recommendation",
            "restaurant recommendation",
            "weather",
            "football score",
            "soccer score",
            "basketball score",
            "who won the match",
            "movie recommendation",
            "tv show recommendation",
            "write python code",
            "write javascript code",
            "write react code",
            "debug my website",
            "build my website",
            "create a logo",
            "generate an image",
            "write a love letter",
            "dating advice",
            "gaming tips",
        )

        return any(
            phrase in question
            for phrase in out_of_scope_phrases
        )

    @staticmethod
    def _normalize(
        value: Any,
    ) -> str:
        return (
            str(value or "")
            .strip()
            .lower()
        )