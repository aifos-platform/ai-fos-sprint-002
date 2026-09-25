from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models import ImportStatus
from typing import Any


class OrganisationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    base_currency: str = Field(default="GBP", min_length=3, max_length=3)
    fiscal_year_start_month: int = Field(default=1, ge=1, le=12)


class OrganisationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    base_currency: str
    fiscal_year_start_month: int
    active: bool
    created_at: datetime


class ImportCreate(BaseModel):
    source_filename: str = Field(min_length=1, max_length=255)
    source_system: str | None = Field(default=None, max_length=100)


class ImportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    organisation_id: str
    source_filename: str
    source_system: str | None
    status: ImportStatus
    row_count: int | None
    error_message: str | None
    created_at: datetime


class FinancialQuestion(BaseModel):
    question: str = Field(
        ...,
        min_length=1,
        description="Question to ask the AI-FOS Digital CFO.",
    )

class FinancialScenarioRequest(BaseModel):
    scenario_name: str = Field(
        default="Custom Scenario",
        min_length=1,
        max_length=255,
    )

    revenue_change_percentage: float = 0.0
    expense_change_percentage: float = 0.0

    one_time_revenue_adjustment: float = 0.0
    one_time_expense_adjustment: float = 0.0

    cash_inflow_adjustment: float = 0.0
    cash_outflow_adjustment: float = 0.0


class ScenarioComparisonRequest(BaseModel):
    scenario_a: dict[str, Any]
    scenario_b: dict[str, Any]

class SavedScenarioComparisonRequest(BaseModel):
    scenario_a_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )
    scenario_b_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )    


class FundingScenarioRequest(BaseModel):
    scenario_name: str = Field(
        default="Funding Scenario",
        min_length=1,
        max_length=255,
    )

    expected_funding_change_percentage: float = 0.0

    failed_expected_funding_codes: list[str] = []

    scenario_basis: str = Field(
        default="most_likely",
        pattern=(
            "^(minimum|most_likely|maximum|"
            "probability_weighted)$"
        ),
    )      
