from pathlib import Path

from app.services.financial_model_service import (
    FinancialModelService,
)
from app.services.verified_cfo_context import (
    VerifiedCFOContextBuilder,
)
from app.services.workspace_service import (
    WorkspaceService,
)


def _build_services(tmp_path):
    workspace_service = WorkspaceService(
        storage_root=tmp_path / "workspaces"
    )

    financial_model_service = FinancialModelService()

    builder = VerifiedCFOContextBuilder(
        workspace_service=workspace_service,
        financial_model_service=financial_model_service,
    )

    return (
        workspace_service,
        financial_model_service,
        builder,
    )


def _create_workspace(
    workspace_service,
):
    return workspace_service.create_workspace(
        organisation_id="acss",
        organisation_name="ACSS",
        base_currency="USD",
    )


def _financial_model_folder(
    workspace,
) -> Path:
    return Path(
        workspace["paths"]["financial_model"]
    )


def test_context_not_available_without_workspace(
    tmp_path,
):
    (
        _,
        _,
        builder,
    ) = _build_services(tmp_path)

    result = builder.build("missing")

    assert result["status"] == "not_available"
    assert result["organisation_id"] == "missing"
    assert result["context"] == {}
    assert result["available_sections"] == []


def test_context_uses_verified_financial_facts(
    tmp_path,
):
    (
        workspace_service,
        financial_model_service,
        builder,
    ) = _build_services(tmp_path)

    workspace = _create_workspace(
        workspace_service
    )

    financial_model_folder = (
        _financial_model_folder(
            workspace
        )
    )

    financial_model_service.save_json(
        financial_model_folder=financial_model_folder,
        filename="financial_facts.json",
        data={
            "revenue": 1000,
            "expenses": 800,
            "net_profit": 200,
            "assets": 5000,
            "liabilities": 2000,
            "equity": 3000,
            "difference": 0,
            "untrusted_extra_field": 999999,
        },
    )

    result = builder.build("acss")

    assert result["status"] == "available"

    facts = result["context"][
        "financial_facts"
    ]

    assert facts["revenue"] == 1000
    assert facts["expenses"] == 800
    assert facts["net_profit"] == 200

    assert (
        "untrusted_extra_field"
        not in facts
    )


def test_context_preserves_missing_values(
    tmp_path,
):
    (
        workspace_service,
        financial_model_service,
        builder,
    ) = _build_services(tmp_path)

    workspace = _create_workspace(
        workspace_service
    )

    financial_model_folder = (
        _financial_model_folder(
            workspace
        )
    )

    financial_model_service.save_json(
        financial_model_folder=financial_model_folder,
        filename="financial_facts.json",
        data={
            "revenue": None,
            "expenses": 800,
        },
    )

    result = builder.build("acss")

    facts = result["context"][
        "financial_facts"
    ]

    assert facts["revenue"] is None
    assert facts["expenses"] == 800

    assert "net_profit" not in facts


def test_context_does_not_include_raw_gl(
    tmp_path,
):
    (
        workspace_service,
        financial_model_service,
        builder,
    ) = _build_services(tmp_path)

    workspace = _create_workspace(
        workspace_service
    )

    financial_model_folder = (
        _financial_model_folder(
            workspace
        )
    )

    financial_model_service.save_json(
        financial_model_folder=financial_model_folder,
        filename="fact_gl.json",
        data=[
            {
                "account": "6000",
                "amount": 999999,
            }
        ],
    )

    financial_model_service.save_json(
        financial_model_folder=financial_model_folder,
        filename="financial_facts.json",
        data={
            "revenue": 1000,
        },
    )

    result = builder.build("acss")

    assert "fact_gl" not in result["context"]

    assert (
        result["trust"][
            "raw_general_ledger_included"
        ]
        is False
    )


def test_context_does_not_recalculate_financials(
    tmp_path,
):
    (
        workspace_service,
        financial_model_service,
        builder,
    ) = _build_services(tmp_path)

    workspace = _create_workspace(
        workspace_service
    )

    financial_model_folder = (
        _financial_model_folder(
            workspace
        )
    )

    financial_model_service.save_json(
        financial_model_folder=financial_model_folder,
        filename="financial_facts.json",
        data={
            "revenue": 1000,
            "expenses": 800,
            "net_profit": 123,
        },
    )

    result = builder.build("acss")

    facts = result["context"][
        "financial_facts"
    ]

    # The builder must preserve the validated
    # AI-FOS result rather than recalculating
    # 1000 - 800 itself.
    assert facts["net_profit"] == 123

    assert (
        result["trust"][
            "financial_recalculation_performed"
        ]
        is False
    )


def test_context_limits_management_lists(
    tmp_path,
):
    (
        workspace_service,
        financial_model_service,
        builder,
    ) = _build_services(tmp_path)

    workspace = _create_workspace(
        workspace_service
    )

    financial_model_folder = (
        _financial_model_folder(
            workspace
        )
    )

    risks = [
        {
            "id": index,
            "title": f"Risk {index}",
        }
        for index in range(10)
    ]

    financial_model_service.save_json(
        financial_model_folder=financial_model_folder,
        filename="risk_assessment.json",
        data=risks,
    )

    result = builder.build("acss")

    assert len(
        result["context"][
            "current_risks"
        ]
    ) == 5

    assert (
        result["trust"][
            "max_items_per_list"
        ]
        == 5
    )


def test_context_tracks_source_provenance(
    tmp_path,
):
    (
        workspace_service,
        financial_model_service,
        builder,
    ) = _build_services(tmp_path)

    workspace = _create_workspace(
        workspace_service
    )

    financial_model_folder = (
        _financial_model_folder(
            workspace
        )
    )

    financial_model_service.save_json(
        financial_model_folder=financial_model_folder,
        filename="financial_facts.json",
        data={
            "revenue": 1000,
        },
    )

    financial_model_service.save_json(
        financial_model_folder=financial_model_folder,
        filename="liquidity.json",
        data={
            "available_cash": 500,
        },
    )

    result = builder.build("acss")

    assert result["source_files"][
        "financial_facts"
    ] == "financial_facts.json"

    assert result["source_files"][
        "liquidity"
    ] == "liquidity.json"

    assert (
        result["trust"]["financial_source"]
        == "validated_ai_fos_outputs"
    )


def test_context_extracts_budget_from_intelligence_hub(
    tmp_path,
):
    (
        workspace_service,
        financial_model_service,
        builder,
    ) = _build_services(tmp_path)

    workspace = _create_workspace(
        workspace_service
    )

    financial_model_folder = (
        _financial_model_folder(
            workspace
        )
    )

    financial_model_service.save_json(
        financial_model_folder=financial_model_folder,
        filename="intelligence_hub.json",
        data={
            "facts": {
                "budget_dashboard": {
                    "portfolio_control": {
                        "total_budget": 1000,
                        "total_actual": 900,
                    },
                    "alerts": [
                        {
                            "title": "Alert 1"
                        }
                    ],
                }
            }
        },
    )

    result = builder.build("acss")

    budget = result["context"]["budget"]

    assert (
        budget["portfolio_control"][
            "total_budget"
        ]
        == 1000
    )

    assert (
        budget["portfolio_control"][
            "total_actual"
        ]
        == 900
    )


def test_context_reports_missing_sections(
    tmp_path,
):
    (
        workspace_service,
        financial_model_service,
        builder,
    ) = _build_services(tmp_path)

    workspace = _create_workspace(
        workspace_service
    )

    financial_model_folder = (
        _financial_model_folder(
            workspace
        )
    )

    financial_model_service.save_json(
        financial_model_folder=financial_model_folder,
        filename="financial_facts.json",
        data={
            "revenue": 1000,
        },
    )

    result = builder.build("acss")

    assert (
        "financial_facts"
        in result["available_sections"]
    )

    assert (
        "financial_health"
        in result["missing_sections"]
    )

    assert (
        "forward_risks"
        in result["missing_sections"]
    )


def test_empty_workspace_does_not_create_fake_context(
    tmp_path,
):
    (
        workspace_service,
        _,
        builder,
    ) = _build_services(tmp_path)

    _create_workspace(
        workspace_service
    )

    result = builder.build("acss")

    assert result["status"] == "not_available"
    assert result["context"] == {}

    assert (
        result["trust"][
            "financial_recalculation_performed"
        ]
        is False
    )