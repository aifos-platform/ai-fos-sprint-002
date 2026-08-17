from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

from app.models import ImportStatus


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
