# AI-FOS Canonical Data Model v0.2

## Design principle

Source ERP data is translated into one canonical model before any analysis is performed.

The Digital CFO reasoning layer must never depend on source-specific column names.

## Domains

### Organisation
- `org_organisation`
- `org_legal_entity`
- `org_department`
- `org_cost_centre`

### Operations
- `ops_programme`
- `ops_project`

### Grants
- `grt_donor`
- `grt_grant`

### Finance
- `fin_account`
- `fin_journal`
- `fin_transaction`
- `fin_budget`
- `fin_budget_line`

### Ingestion
- `ing_import_job`
- `ing_column_mapping`

### Intelligence
- `ai_insight`
- `ai_risk`
- `ai_recommendation`

## Core transaction grain

One row in `fin_transaction` represents one posted ledger line.

This is the canonical financial fact table for Sprint 002.

## Important rules

- Every record belongs to one organisation.
- Source-specific values are mapped into canonical entities.
- Debit and credit cannot both be positive.
- Mapping confidence is between 0 and 1.
- Account, donor, grant, project and cost-centre codes are unique within an organisation.
- AI outputs store confidence and supporting rationale.
