# AI-FOS — Sprint 002 Canonical Data Model

Sprint 002 turns the initial backend scaffold into a proper NGO finance platform foundation.

## What is included

- Organisation structure
- Legal entities and departments
- Programmes, projects and cost centres
- Donors and grants
- Chart of accounts
- General ledger journals and transactions
- Budgets and budget lines
- Import jobs and source mappings
- AI insights, risks and recommendations
- Database constraints and indexes
- Architecture documentation
- Automated model tests

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Swagger is available at:

```text
http://localhost:8000/docs
```

## Sprint 002 outcome

AI-FOS now has a stable canonical model that can accept finance data from different ERPs without changing the Digital CFO reasoning layer.
