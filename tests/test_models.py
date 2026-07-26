import os
os.environ["DATABASE_URL"] = "sqlite:///./test_ai_fos_sprint_002.db"

from sqlalchemy import inspect
from fastapi.testclient import TestClient

from app.database import engine
from app.main import app


client = TestClient(app)


def test_expected_tables_exist():
    tables = set(inspect(engine).get_table_names())
    expected = {
        "org_organisation",
        "org_legal_entity",
        "org_department",
        "org_cost_centre",
        "ops_programme",
        "ops_project",
        "grt_donor",
        "grt_grant",
        "fin_account",
        "fin_journal",
        "fin_transaction",
        "fin_budget",
        "fin_budget_line",
        "ing_import_job",
        "ing_column_mapping",
        "ai_insight",
        "ai_risk",
        "ai_recommendation",
    }
    assert expected.issubset(tables)


def test_create_organisation():
    response = client.post(
        "/organisations",
        json={
            "name": "Global Relief Foundation",
            "base_currency": "GBP",
            "fiscal_year_start_month": 4,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Global Relief Foundation"
    assert body["fiscal_year_start_month"] == 4
