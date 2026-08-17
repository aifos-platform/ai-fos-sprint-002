from typing import Any


class Grant:
    """
    Represents one donor grant.
    """

    def __init__(self):
        self.code: str | None = None
        self.name: str | None = None

        self.original_budget = 0.0
        self.revised_budget = 0.0
        self.actual = 0.0

        self.remaining_budget = 0.0
        self.utilization = 0.0

        self.projects: set[str] = set()

        self.transactions: list[dict[str, Any]] = []

    def calculate_financials(self) -> None:
        """
        Calculate the grant's remaining budget and utilization.
        """

        self.remaining_budget = self.revised_budget - self.actual

        self.utilization = (
            self.actual / self.revised_budget * 100 if self.revised_budget else 0.0
        )

        self.remaining_budget = round(
            self.remaining_budget,
            2,
        )

        self.utilization = round(
            self.utilization,
            2,
        )
