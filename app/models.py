import enum
import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class ImportStatus(str, enum.Enum):
    REGISTERED = "registered"
    PROFILING = "profiling"
    MAPPING_REQUIRED = "mapping_required"
    DISCOVERING = "discovering"
    COMPLETED = "completed"
    FAILED = "failed"


class InsightSeverity(str, enum.Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationStatus(str, enum.Enum):
    OPEN = "open"
    ACCEPTED = "accepted"
    DISMISSED = "dismissed"
    COMPLETED = "completed"


class Organisation(Base):
    __tablename__ = "org_organisation"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False, default="GBP")
    fiscal_year_start_month: Mapped[int] = mapped_column(default=1)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    entities: Mapped[list["LegalEntity"]] = relationship(back_populates="organisation")
    imports: Mapped[list["ImportJob"]] = relationship(back_populates="organisation")

    __table_args__ = (
        CheckConstraint("fiscal_year_start_month BETWEEN 1 AND 12"),
    )


class LegalEntity(Base):
    __tablename__ = "org_legal_entity"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    country_code: Mapped[str | None] = mapped_column(String(2))
    functional_currency: Mapped[str] = mapped_column(String(3), default="GBP")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    organisation: Mapped["Organisation"] = relationship(back_populates="entities")

    __table_args__ = (
        UniqueConstraint("organisation_id", "code", name="uq_entity_code"),
    )


class Department(Base):
    __tablename__ = "org_department"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("organisation_id", "code", name="uq_department_code"),
    )


class CostCentre(Base):
    __tablename__ = "org_cost_centre"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    department_id: Mapped[str | None] = mapped_column(ForeignKey("org_department.id"))
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint("organisation_id", "code", name="uq_cost_centre_code"),
    )


class Programme(Base):
    __tablename__ = "ops_programme"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("organisation_id", "code", name="uq_programme_code"),
    )


class Project(Base):
    __tablename__ = "ops_project"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    programme_id: Mapped[str | None] = mapped_column(ForeignKey("ops_programme.id"))
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("organisation_id", "code", name="uq_project_code"),
    )


class Donor(Base):
    __tablename__ = "grt_donor"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    donor_type: Mapped[str | None] = mapped_column(String(100))
    country_code: Mapped[str | None] = mapped_column(String(2))

    __table_args__ = (
        UniqueConstraint("organisation_id", "code", name="uq_donor_code"),
    )


class Grant(Base):
    __tablename__ = "grt_grant"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    donor_id: Mapped[str | None] = mapped_column(ForeignKey("grt_donor.id"))
    project_id: Mapped[str | None] = mapped_column(ForeignKey("ops_project.id"))
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    agreement_reference: Mapped[str | None] = mapped_column(String(100))
    start_date: Mapped[date | None] = mapped_column(Date)
    end_date: Mapped[date | None] = mapped_column(Date)
    award_currency: Mapped[str] = mapped_column(String(3), default="GBP")
    award_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    restricted: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("organisation_id", "code", name="uq_grant_code"),
    )


class Account(Base):
    __tablename__ = "fin_account"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    account_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reporting_category: Mapped[str | None] = mapped_column(String(100))
    parent_account_id: Mapped[str | None] = mapped_column(ForeignKey("fin_account.id"))
    active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("organisation_id", "code", name="uq_account_code"),
    )


class Journal(Base):
    __tablename__ = "fin_journal"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    legal_entity_id: Mapped[str | None] = mapped_column(ForeignKey("org_legal_entity.id"))
    import_job_id: Mapped[str | None] = mapped_column(ForeignKey("ing_import_job.id"))
    journal_number: Mapped[str] = mapped_column(String(100), nullable=False)
    posting_date: Mapped[date] = mapped_column(Date, nullable=False)
    source_system: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint("organisation_id", "journal_number", name="uq_journal_number"),
        Index("ix_journal_posting_date", "posting_date"),
    )


class FinanceTransaction(Base):
    __tablename__ = "fin_transaction"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    journal_id: Mapped[str] = mapped_column(ForeignKey("fin_journal.id"), nullable=False)
    account_id: Mapped[str] = mapped_column(ForeignKey("fin_account.id"), nullable=False)
    department_id: Mapped[str | None] = mapped_column(ForeignKey("org_department.id"))
    cost_centre_id: Mapped[str | None] = mapped_column(ForeignKey("org_cost_centre.id"))
    programme_id: Mapped[str | None] = mapped_column(ForeignKey("ops_programme.id"))
    project_id: Mapped[str | None] = mapped_column(ForeignKey("ops_project.id"))
    grant_id: Mapped[str | None] = mapped_column(ForeignKey("grt_grant.id"))
    donor_id: Mapped[str | None] = mapped_column(ForeignKey("grt_donor.id"))
    transaction_date: Mapped[date] = mapped_column(Date, nullable=False)
    document_number: Mapped[str | None] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(Text)
    debit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    credit: Mapped[Decimal] = mapped_column(Numeric(18, 2), default=0)
    transaction_currency: Mapped[str] = mapped_column(String(3), default="GBP")
    functional_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    source_row_number: Mapped[int | None]
    source_hash: Mapped[str | None] = mapped_column(String(64))

    __table_args__ = (
        CheckConstraint("debit >= 0", name="ck_debit_non_negative"),
        CheckConstraint("credit >= 0", name="ck_credit_non_negative"),
        CheckConstraint("NOT (debit > 0 AND credit > 0)", name="ck_not_both_debit_credit"),
        Index("ix_transaction_org_date", "organisation_id", "transaction_date"),
        Index("ix_transaction_grant", "grant_id"),
        Index("ix_transaction_account", "account_id"),
    )


class Budget(Base):
    __tablename__ = "fin_budget"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    fiscal_year: Mapped[int] = mapped_column(nullable=False)
    version: Mapped[str] = mapped_column(String(50), default="approved")
    currency: Mapped[str] = mapped_column(String(3), default="GBP")
    approved: Mapped[bool] = mapped_column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("organisation_id", "name", "fiscal_year", "version", name="uq_budget_version"),
    )


class BudgetLine(Base):
    __tablename__ = "fin_budget_line"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    budget_id: Mapped[str] = mapped_column(ForeignKey("fin_budget.id"), nullable=False)
    account_id: Mapped[str] = mapped_column(ForeignKey("fin_account.id"), nullable=False)
    department_id: Mapped[str | None] = mapped_column(ForeignKey("org_department.id"))
    cost_centre_id: Mapped[str | None] = mapped_column(ForeignKey("org_cost_centre.id"))
    programme_id: Mapped[str | None] = mapped_column(ForeignKey("ops_programme.id"))
    project_id: Mapped[str | None] = mapped_column(ForeignKey("ops_project.id"))
    grant_id: Mapped[str | None] = mapped_column(ForeignKey("grt_grant.id"))
    period_start: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(18, 2), nullable=False)


class ImportJob(Base):
    __tablename__ = "ing_import_job"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    source_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    source_system: Mapped[str | None] = mapped_column(String(100))
    file_hash: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[ImportStatus] = mapped_column(Enum(ImportStatus), default=ImportStatus.REGISTERED)
    row_count: Mapped[int | None]
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)

    organisation: Mapped["Organisation"] = relationship(back_populates="imports")
    mappings: Mapped[list["ColumnMapping"]] = relationship(back_populates="import_job")

    __table_args__ = (
        Index("ix_import_org_created", "organisation_id", "created_at"),
    )


class ColumnMapping(Base):
    __tablename__ = "ing_column_mapping"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    import_job_id: Mapped[str] = mapped_column(ForeignKey("ing_import_job.id"), nullable=False)
    source_column: Mapped[str] = mapped_column(String(255), nullable=False)
    canonical_field: Mapped[str] = mapped_column(String(255), nullable=False)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    confirmed_by_user: Mapped[bool] = mapped_column(Boolean, default=False)

    import_job: Mapped["ImportJob"] = relationship(back_populates="mappings")

    __table_args__ = (
        UniqueConstraint("import_job_id", "source_column", name="uq_import_source_column"),
        CheckConstraint("confidence IS NULL OR (confidence >= 0 AND confidence <= 1)", name="ck_mapping_confidence"),
    )


class AIInsight(Base):
    __tablename__ = "ai_insight"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    insight_type: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    narrative: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[InsightSeverity] = mapped_column(Enum(InsightSeverity), default=InsightSeverity.INFO)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    evidence_json: Mapped[str | None] = mapped_column(Text)
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AIRisk(Base):
    __tablename__ = "ai_risk"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[InsightSeverity] = mapped_column(Enum(InsightSeverity), nullable=False)
    likelihood: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    financial_impact: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AIRecommendation(Base):
    __tablename__ = "ai_recommendation"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    organisation_id: Mapped[str] = mapped_column(ForeignKey("org_organisation.id"), nullable=False)
    risk_id: Mapped[str | None] = mapped_column(ForeignKey("ai_risk.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    recommendation: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    expected_impact: Mapped[str | None] = mapped_column(Text)
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))
    status: Mapped[RecommendationStatus] = mapped_column(
        Enum(RecommendationStatus), default=RecommendationStatus.OPEN
    )
    generated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
