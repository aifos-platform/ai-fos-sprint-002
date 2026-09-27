import json
import os
import traceback
from pathlib import Path
from typing import Any

from fastapi import (
    Depends,
    FastAPI,
    HTTPException,
    File,
    Form,
    Request,
    UploadFile,
    status,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, Response
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.models import ImportJob, Organisation
from app.organization import Organization
from app.schemas import (
    FinancialQuestion,
    FinancialScenarioRequest,
    FundingScenarioRequest,
    ScenarioComparisonRequest,
    SavedScenarioComparisonRequest,
    ImportCreate,
    ImportRead,
    OrganisationCreate,
    OrganisationRead,
)

from app.services.chart_of_accounts import ChartOfAccounts
from app.services.excel_reader import inspect_workbook
from app.services.fact_gl_service import FactGLService
from app.services.financial_model_service import FinancialModelService
from app.services.workspace_service import WorkspaceService
from app.services.organization_readiness import (
    OrganizationReadinessService,
)
from app.services.dimension_builder import DimensionBuilder
from app.services.gl_normalizer import GLNormalizer
from app.services.gl_account_builder import GLAccountBuilder
from app.services.model_validator import ModelValidator
from app.services.ai_question_engine import AIQuestionEngine
from app.services.digital_cfo_orchestrator import DigitalCFOOrchestrator
from app.services.financial_intelligence_service import (
    FinancialIntelligenceService,
)
from app.services.intelligence_hub import IntelligenceHub

from app.engines.organization_knowledge.organization_knowledge_builder import (
    OrganizationKnowledgeBuilder,
)
from app.engines.organization_knowledge.organization_knowledge_reader import (
    OrganizationKnowledgeReader,
)
from app.services.gl_date_validator import GLDateValidator
from app.services.gl_integrity_validator import GLIntegrityValidator
from app.services.budget_actual_classifier import (
    BudgetActualClassifier,
)
from app.services.question_catalog import (
    get_question_catalog,
)
from app.services.suggested_question_service import (
    SuggestedQuestionService,
)
from app.engines.data_intelligence.question_catalog_validator import (
    QuestionCatalogValidator,
)
from app.services.cfo_report_pdf import generate_cfo_report_pdf
from app.services.organization_registry_service import (
    OrganizationRegistryService,
)
from app.services.cfo_report_excel import (
    generate_cfo_report_excel,
)
from app.services.cfo_report_word import (
    generate_cfo_report_word,
)
from app.services.verified_cfo_context import (
    VerifiedCFOContextBuilder,
)
from app.services.digital_cfo_scope_guard import DigitalCFOScopeGuard
from app.services.ai_usage_control import (
    AIUsageControlService,
)
from app.services.scenario_history import (
    ScenarioHistoryService,
)
from app.services.cfo_action_plan import (
    CFOActionPlanService,
)
from app.services.cfo_action_command import (
    CFOActionCommandService,
)
from app.services.financial_intelligence_history import (
    FinancialIntelligenceHistoryService,
)
from app.services.financial_intelligence_history import (
    FinancialIntelligenceHistoryService,
)
from app.services.standard_income_statement_excel import (
    generate_standard_income_statement_excel,
)
from app.services.standard_balance_sheet_excel import (
    generate_standard_balance_sheet_excel,
)
from app.services.standard_cash_flow_statement_excel import (
    generate_standard_cash_flow_statement_excel,
)
from io import BytesIO
from fastapi.responses import StreamingResponse


Base.metadata.create_all(bind=engine)


UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Digital CFO platform canonical data foundation",
)

organization_registry_service = OrganizationRegistryService()


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def debug_exception_handler(
    request: Request,
    exc: Exception,
):
    trace = traceback.format_exc()

    print(trace)

    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "path": request.url.path,
            "traceback": trace,
        },
    )


organization = Organization()
workspace_service = WorkspaceService()
organization_readiness_service = OrganizationReadinessService()
financial_model_service = FinancialModelService()
fact_gl_service = FactGLService()
dimension_builder = DimensionBuilder()
gl_normalizer = GLNormalizer()
gl_account_builder = GLAccountBuilder()
model_validator = ModelValidator()
gl_date_validator = GLDateValidator()
gl_integrity_validator = GLIntegrityValidator()
organization_knowledge_builder = OrganizationKnowledgeBuilder()

organization_knowledge_reader = OrganizationKnowledgeReader()

financial_intelligence_service = FinancialIntelligenceService()

intelligence_hub = IntelligenceHub()
budget_actual_classifier = BudgetActualClassifier()
ai_question_engine = AIQuestionEngine(
    workspace_service=workspace_service,
    knowledge_reader=organization_knowledge_reader,
    financial_intelligence_service=financial_intelligence_service,
    financial_model_service=financial_model_service,
)

verified_cfo_context_builder = VerifiedCFOContextBuilder(
    workspace_service=workspace_service,
    financial_model_service=financial_model_service,
)

digital_cfo_scope_guard = DigitalCFOScopeGuard(
    question_classifier=ai_question_engine.question_classifier,
)

ai_usage_control = AIUsageControlService()

digital_cfo_orchestrator = DigitalCFOOrchestrator(
    ai_question_engine=ai_question_engine,
    context_builder=verified_cfo_context_builder,
    scope_guard=digital_cfo_scope_guard,
    usage_control=ai_usage_control,
)
suggested_question_service = SuggestedQuestionService()


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.2.0",
    }


@app.get("/organisations/{organisation_id}/readiness")
def get_organisation_readiness(
    organisation_id: str,
) -> dict[str, Any]:
    """
    Return persisted-data readiness for an
    organization.

    Readiness is derived from existing AI-FOS
    workspace artifacts and does not recalculate
    financial results.
    """

    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    readiness = organization_readiness_service.assess(workspace=workspace)

    return {
        "organisation_id": organisation_id,
        **readiness,
    }

@app.get(
    "/organisations/{organisation_id}/cfo-action-center"
)
def get_cfo_action_center(
    organisation_id: str,
) -> dict[str, Any]:
    """
    Return the read-only CFO Executive Action Center.

    The Action Center consolidates:
    - current CFO Action Plan state,
    - dynamic monitoring,
    - escalation intelligence,
    - immutable history-based performance intelligence.

    It does not mutate management state.
    """

    workspace = (
        workspace_service.get_workspace_by_organisation(
            organisation_id=organisation_id
        )
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Workspace not found for this organisation."
            ),
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    actions = (
        CFOActionPlanService.list_actions(
            financial_model_folder
        )
    )

    monitoring = (
        CFOActionPlanService.build_monitoring(
            financial_model_folder=(
                financial_model_folder
            )
        )
    )

    escalation = (
        CFOActionPlanService.build_escalation(
            financial_model_folder=(
                financial_model_folder
            )
        )
    )

    performance = (
        CFOActionPlanService.build_performance(
            financial_model_folder=(
                financial_model_folder
            )
        )
    )

    monitoring_summary = (
        monitoring.get(
            "summary",
            {},
        )
        or {}
    )

    escalation_summary = (
        escalation.get(
            "summary",
            {},
        )
        or {}
    )

    performance_summary = (
        performance.get(
            "summary",
            {},
        )
        or {}
    )

    summary = {
        "total_actions": int(
            monitoring_summary.get(
                "total_actions",
                0,
            )
            or 0
        ),
        "open_actions": int(
            monitoring_summary.get(
                "open",
                0,
            )
            or 0
        ),
        "in_progress_actions": int(
            monitoring_summary.get(
                "in_progress",
                0,
            )
            or 0
        ),
        "blocked_actions": int(
            monitoring_summary.get(
                "blocked",
                0,
            )
            or 0
        ),
        "completed_actions": int(
            monitoring_summary.get(
                "completed",
                0,
            )
            or 0
        ),
        "overdue_actions": len(
            monitoring.get(
                "overdue_actions",
                [],
            )
            or []
        ),
        "due_soon_actions": len(
            monitoring.get(
                "due_soon_actions",
                [],
            )
            or []
        ),
        "total_escalations": int(
            escalation_summary.get(
                "total_escalations",
                0,
            )
            or 0
        ),
        "critical_escalations": int(
            escalation_summary.get(
                "critical",
                0,
            )
            or 0
        ),
        "high_escalations": int(
            escalation_summary.get(
                "high",
                0,
            )
            or 0
        ),
        "history_events": int(
            performance_summary.get(
                "total_events",
                0,
            )
            or 0
        ),
        "reopened_actions": int(
            performance_summary.get(
                "reopened_action_count",
                0,
            )
            or 0
        ),
        "actions_with_repeated_blocks": int(
            performance_summary.get(
                "actions_with_repeated_blocks",
                0,
            )
            or 0
        ),
    }

    executive_decision_intelligence = (
        financial_model_service.load_json(
            financial_model_folder,
            "executive_decision_intelligence.json",
        )
        or {}
    )

    executive_priorities = (
        executive_decision_intelligence.get(
            "priorities",
            [],
        )
        if isinstance(
            executive_decision_intelligence,
            dict,
        )
        else []
    )

    if not isinstance(
        executive_priorities,
        list,
    ):
        executive_priorities = []

    return {
        "status": "available",
        "organisation_id": organisation_id,
        "summary": summary,
        "actions": actions,
        "monitoring": monitoring,
        "escalation": escalation,
        "performance": performance,
        "executive_priorities": executive_priorities,
        "controls": {
            "read_only": True,
            "action_records_modified": False,
            "history_records_modified": False,
            "financial_recalculation_performed": False,
        },
    }

@app.get(
    "/organisations/{organisation_id}/financial-intelligence-history"
)
def get_financial_intelligence_history(
    organisation_id: str,
) -> dict[str, Any]:
    """
    Return read-only Historical Financial Intelligence.

    The endpoint exposes:
    - available immutable snapshot count,
    - latest deterministic historical Change Analysis,
    - latest deterministic Historical Decision Intelligence.

    It does not:
    - recalculate financials,
    - modify historical snapshots,
    - include hypothetical scenarios,
    - mutate CFO Action Plan state.
    """

    workspace = (
        workspace_service.get_workspace_by_organisation(
            organisation_id=organisation_id
        )
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Workspace not found for this organisation."
            ),
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    snapshots = (
        FinancialIntelligenceHistoryService.list_snapshots(
            financial_model_folder
        )
    )

    latest_change = (
        FinancialIntelligenceHistoryService.compare_latest(
            financial_model_folder
        )
    )

    historical_decision = (
        FinancialIntelligenceHistoryService
        .build_latest_historical_decision(
            financial_model_folder
        )
    )

    snapshot_metadata: list[
        dict[str, Any]
    ] = []

    for snapshot in snapshots:

        if not isinstance(
            snapshot,
            dict,
        ):
            continue

        snapshot_metadata.append(
            {
                "snapshot_id": snapshot.get(
                    "snapshot_id"
                ),
                "captured_at": snapshot.get(
                    "captured_at"
                ),
                "analysis_start_date": snapshot.get(
                    "analysis_start_date"
                ),
                "analysis_end_date": snapshot.get(
                    "analysis_end_date"
                ),
                "source": snapshot.get(
                    "source"
                ),
            }
        )

    latest_change_available = (
        isinstance(
            latest_change,
            dict,
        )
        and latest_change.get(
            "status"
        )
        == "available"
    )

    return {
        "status": (
            "available"
            if latest_change_available
            else "insufficient_history"
        ),
        "organisation_id": organisation_id,
        "snapshot_count": len(
            snapshots
        ),
        "snapshots": snapshot_metadata,
        "latest_change": latest_change,
        "historical_decision": (
            historical_decision
        ),
        "controls": {
            "read_only": True,
            "financial_recalculation_performed": False,
            "historical_snapshots_modified": False,
            "hypothetical_scenarios_excluded": True,
            "action_plan_modified": False,
            "missing_history_not_invented": True,
        },
    }

@app.get("/organization-knowledge/{organisation_id}")
def get_organization_knowledge(
    organisation_id: str,
) -> dict[str, Any]:

    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    if workspace is None:
        return {
            "status": "not_available",
            "message": "No workspace found for this organization.",
        }

    ai_knowledge_folder = Path(workspace["paths"]["ai_knowledge"])

    return organization_knowledge_reader.get_summary(folder=ai_knowledge_folder)

@app.post(
    "/organisations/{organisation_id}/cfo-actions/"
    "from-executive-priority"
)
def create_cfo_action_from_executive_priority(
    organisation_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Create one CFO Action Plan item from persisted
    Executive Decision Intelligence.

    The frontend selects an existing verified priority by index.
    It does not supply or redefine the financial intelligence.
    """

    workspace = (
        workspace_service.get_workspace_by_organisation(
            organisation_id=organisation_id
        )
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found for this organisation.",
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    priority_index = payload.get(
        "priority_index"
    )

    if (
        isinstance(priority_index, bool)
        or not isinstance(priority_index, int)
    ):
        raise HTTPException(
            status_code=400,
            detail="priority_index must be an integer.",
        )

    executive_decision_intelligence = (
        financial_model_service.load_json(
            financial_model_folder,
            "executive_decision_intelligence.json",
        )
    )

    if not isinstance(
        executive_decision_intelligence,
        dict,
    ):
        raise HTTPException(
            status_code=404,
            detail=(
                "Executive Decision Intelligence "
                "is not available."
            ),
        )

    priorities = executive_decision_intelligence.get(
        "priorities",
        [],
    )

    if not isinstance(
        priorities,
        list,
    ):
        raise HTTPException(
            status_code=400,
            detail=(
                "Persisted Executive Decision Intelligence "
                "priorities are invalid."
            ),
        )

    if (
        priority_index < 0
        or priority_index >= len(priorities)
    ):
        raise HTTPException(
            status_code=400,
            detail="Executive priority index is out of range.",
        )

    executive_priority = priorities[
        priority_index
    ]

    if not isinstance(
        executive_priority,
        dict,
    ):
        raise HTTPException(
            status_code=400,
            detail="Selected executive priority is invalid.",
        )

    try:
        action = (
            CFOActionPlanService.create_from_executive_priority(
                financial_model_folder=(
                    financial_model_folder
                ),
                executive_priority=executive_priority,
            )
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "status": "created",
        "organisation_id": organisation_id,
        "action": action,
    }


@app.post(
    "/organisations/{organisation_id}/cfo-actions/"
    "{action_id}/command"
)
def execute_cfo_action_command(
    organisation_id: str,
    action_id: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute one deterministic CFO management-action command.

    All mutations pass through CFOActionCommandService and
    therefore through the protected lifecycle and Action Plan
    mutation boundary.

    Until authenticated user identity exists:
    - actor remains None,
    - UI provenance is recorded as user_interface.
    """

    workspace = (
        workspace_service.get_workspace_by_organisation(
            organisation_id=organisation_id
        )
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Workspace not found for this organisation.",
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    command = str(
        payload.get(
            "command",
            "",
        )
        or ""
    ).strip().lower()

    value = payload.get(
        "value"
    )

    management_notes = payload.get(
        "management_notes"
    )

    command_handlers = {
        "assign": lambda: CFOActionCommandService.assign(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            owner=value,
            history_actor=None,
            history_source="user_interface",
        ),
        "unassign": lambda: CFOActionCommandService.unassign(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=None,
            history_source="user_interface",
        ),
        "set_due_date": lambda: (
            CFOActionCommandService.set_due_date(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                due_date=value,
                history_actor=None,
                history_source="user_interface",
            )
        ),
        "clear_due_date": lambda: (
            CFOActionCommandService.clear_due_date(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                history_actor=None,
                history_source="user_interface",
            )
        ),
        "start": lambda: CFOActionCommandService.start(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=None,
            history_source="user_interface",
        ),
        "update_progress": lambda: (
            CFOActionCommandService.update_progress(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                progress_percentage=value,
                history_actor=None,
                history_source="user_interface",
            )
        ),
        "block": lambda: CFOActionCommandService.block(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            management_notes=management_notes,
            history_actor=None,
            history_source="user_interface",
        ),
        "unblock": lambda: CFOActionCommandService.unblock(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=None,
            history_source="user_interface",
        ),
        "complete": lambda: CFOActionCommandService.complete(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            management_notes=management_notes,
            history_actor=None,
            history_source="user_interface",
        ),
        "reopen": lambda: CFOActionCommandService.reopen(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            history_actor=None,
            history_source="user_interface",
        ),
        "cancel": lambda: CFOActionCommandService.cancel(
            financial_model_folder=financial_model_folder,
            action_id=action_id,
            management_notes=management_notes,
            history_actor=None,
            history_source="user_interface",
        ),
        "update_notes": lambda: (
            CFOActionCommandService.update_notes(
                financial_model_folder=financial_model_folder,
                action_id=action_id,
                management_notes=value,
                history_actor=None,
                history_source="user_interface",
            )
        ),
    }

    handler = command_handlers.get(
        command
    )

    if handler is None:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported CFO action command. "
                "Expected one of: "
                + ", ".join(
                    sorted(
                        command_handlers.keys()
                    )
                )
                + "."
            ),
        )

    try:
        action = handler()

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    return {
        "status": "success",
        "organisation_id": organisation_id,
        "action": action,
    }

@app.get("/ask/{organisation_id}")
def ask_ai(
    organisation_id: str,
    question: str,
) -> dict[str, Any]:

    return digital_cfo_orchestrator.answer(
        question=question,
        organisation_id=organisation_id,
    )

@app.post("/scenario-comparison/{organization_id}")
def compare_financial_scenarios(
    organization_id: str,
    request: ScenarioComparisonRequest,
) -> dict[str, Any]:
    """
    Compare two existing financial scenario decision
    intelligence outputs for an organization.

    The comparison does not rerun either scenario and does
    not modify the validated financial forecast.
    """

    workspace = (
        workspace_service.get_workspace_by_organisation(
            organization_id
        )
    )

    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="No workspace found for this organization.",
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    organization = Organization()
    organization.name = organization_id

    scenario_comparison_intelligence = (
        organization.compare_financial_scenarios(
            request.scenario_a,
            request.scenario_b,
        )
    )

    FinancialModelService.save_scenario_outputs(
        financial_model_folder=financial_model_folder,
        financial_scenario=None,
        scenario_decision_intelligence=None,
        scenario_comparison_intelligence=(
            scenario_comparison_intelligence
        ),
    )

    return {
        "status": scenario_comparison_intelligence.get(
            "status",
            "not_available",
        ),
        "organization_id": organization_id,
        "scenario_comparison_intelligence": (
            scenario_comparison_intelligence
        ),
    }

@app.post("/scenario-comparison/{organization_id}/saved")
def compare_saved_financial_scenarios(
    organization_id: str,
    request: SavedScenarioComparisonRequest,
) -> dict[str, Any]:
    """
    Compare two financial scenarios previously saved in
    Scenario History.

    Existing saved decision-intelligence outputs are used.
    Neither financial scenario is rerun and the validated
    baseline forecast is not modified.
    """

    workspace = (
        workspace_service.get_workspace_by_organisation(
            organization_id
        )
    )

    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="No workspace found for this organization.",
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    scenario_a = ScenarioHistoryService.get_scenario(
        financial_model_folder=financial_model_folder,
        scenario_id=request.scenario_a_id,
    )

    scenario_b = ScenarioHistoryService.get_scenario(
        financial_model_folder=financial_model_folder,
        scenario_id=request.scenario_b_id,
    )

    if scenario_a is None:
        raise HTTPException(
            status_code=404,
            detail="Scenario A not found.",
        )

    if scenario_b is None:
        raise HTTPException(
            status_code=404,
            detail="Scenario B not found.",
        )

    organization = Organization()
    organization.name = organization_id

    scenario_comparison_intelligence = (
        organization.compare_financial_scenarios(
            scenario_a[
                "scenario_decision_intelligence"
            ],
            scenario_b[
                "scenario_decision_intelligence"
            ],
        )
    )

    FinancialModelService.save_scenario_outputs(
        financial_model_folder=financial_model_folder,
        financial_scenario=None,
        scenario_decision_intelligence=None,
        scenario_comparison_intelligence=(
            scenario_comparison_intelligence
        ),
    )

    return {
        "status": scenario_comparison_intelligence.get(
            "status",
            "not_available",
        ),
        "organization_id": organization_id,
        "scenario_comparison_intelligence": (
            scenario_comparison_intelligence
        ),
    }

@app.get("/scenario-history/{organization_id}")
def list_scenario_history(
    organization_id: str,
) -> dict[str, Any]:
    """
    Return saved financial scenarios for an organization.
    """

    workspace = (
        workspace_service.get_workspace_by_organisation(
            organization_id
        )
    )

    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="No workspace found for this organization.",
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    scenarios = ScenarioHistoryService.list_scenarios(
        financial_model_folder
    )

    return {
        "status": "available",
        "organization_id": organization_id,
        "scenarios": scenarios,
    }


@app.get(
    "/scenario-history/{organization_id}/{scenario_id}"
)
def get_scenario_history_item(
    organization_id: str,
    scenario_id: str,
) -> dict[str, Any]:
    """
    Return one saved financial scenario by ID.
    """

    workspace = (
        workspace_service.get_workspace_by_organisation(
            organization_id
        )
    )

    if not workspace:
        raise HTTPException(
            status_code=404,
            detail="No workspace found for this organization.",
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    scenario = ScenarioHistoryService.get_scenario(
        financial_model_folder=financial_model_folder,
        scenario_id=scenario_id,
    )

    if scenario is None:
        raise HTTPException(
            status_code=404,
            detail="Scenario not found.",
        )

    return {
        "status": "available",
        "organization_id": organization_id,
        "scenario": scenario,
    }

@app.post("/scenario/{organisation_id}")
def run_financial_scenario(
    organisation_id: str,
    request: FinancialScenarioRequest,
) -> dict[str, Any]:
    """
    Run and persist an explicit AI-FOS financial
    what-if scenario for an organization.

    The scenario uses the organization's persisted,
    validated baseline forecast and liquidity outputs.
    It does not modify the baseline forecast.
    """

    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="No workspace found for this organization.",
        )

    financial_model_folder = Path(workspace["paths"]["financial_model"])

    financial_forecast = financial_model_service.load_json(
        financial_model_folder,
        "financial_forecast.json",
    )

    liquidity = financial_model_service.load_json(
        financial_model_folder,
        "liquidity.json",
    )

    organization = Organization()
    organization.name = organisation_id
    organization.financial_forecast = financial_forecast
    organization.liquidity = liquidity

    financial_scenario = organization.run_financial_scenario(
        scenario_name=request.scenario_name,
        revenue_change_percentage=(request.revenue_change_percentage),
        expense_change_percentage=(request.expense_change_percentage),
        one_time_revenue_adjustment=(request.one_time_revenue_adjustment),
        one_time_expense_adjustment=(request.one_time_expense_adjustment),
        cash_inflow_adjustment=(request.cash_inflow_adjustment),
        cash_outflow_adjustment=(request.cash_outflow_adjustment),
    )

    financial_model_service.save_scenario_outputs(
        financial_model_folder=financial_model_folder,
        financial_scenario=financial_scenario,
        scenario_decision_intelligence=(organization.scenario_decision_intelligence),
    )

    ScenarioHistoryService.save_scenario(
        financial_model_folder=financial_model_folder,
        financial_scenario=financial_scenario,
        scenario_decision_intelligence=(
            organization.scenario_decision_intelligence
        ),
    )

    return {
        "status": financial_scenario.get(
            "status",
            "not_available",
        ),
        "organisation_id": organisation_id,
        "financial_scenario": financial_scenario,
        "scenario_decision_intelligence": (organization.scenario_decision_intelligence),
    }

@app.post("/funding-scenario/{organisation_id}")
def run_funding_scenario(
    organisation_id: str,
    request: FundingScenarioRequest,
) -> dict[str, Any]:
    """
    Run and persist an explicit AI-FOS Expected Funding
    what-if scenario for an organization.

    The scenario uses the organization's persisted,
    validated Expected Funding Intelligence.

    It does not modify secured funding, Funding Gap,
    revenue, cash, or the validated Expected Funding
    baseline.
    """

    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="No workspace found for this organization.",
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    expected_funding_intelligence = (
        financial_model_service.load_json(
            financial_model_folder,
            "expected_funding_intelligence.json",
        )
    )

    organization = Organization()
    organization.name = organisation_id
    organization.expected_funding_intelligence = (
        expected_funding_intelligence
    )

    funding_scenario = organization.run_funding_scenario(
        scenario_name=request.scenario_name,
        expected_funding_change_percentage=(
            request.expected_funding_change_percentage
        ),
        failed_expected_funding_codes=(
            request.failed_expected_funding_codes
        ),
        scenario_basis=request.scenario_basis,
    )

    financial_model_service.save_json(
        financial_model_folder=financial_model_folder,
        filename="funding_scenario.json",
        data=funding_scenario,
    )

    return {
        "status": funding_scenario.get(
            "status",
            "not_available",
        ),
        "organisation_id": organisation_id,
        "funding_scenario": funding_scenario,
    }

@app.get("/ai-cfo/questions")
def get_ai_cfo_questions() -> dict[str, Any]:
    """
    Return the AI-FOS suggested-question catalogue.
    """

    return {
        "status": "success",
        "categories": get_question_catalog(),
    }


@app.get("/ai-cfo/suggested/{organisation_id}")
def get_ai_cfo_suggested_questions(
    organisation_id: str,
) -> dict[str, Any]:
    """
    Return organization-specific AI CFO suggested
    questions from persisted verified financial
    intelligence.
    """

    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    if workspace is None:

        return {
            "status": "not_available",
            "organisation_id": organisation_id,
            "suggested_questions": [],
            "message": ("No workspace was found for this " "organization."),
        }

    financial_model_folder = Path(workspace["paths"]["financial_model"])

    intelligence_hub_data = financial_model_service.load_json(
        financial_model_folder=(financial_model_folder),
        filename="intelligence_hub.json",
    )

    if not isinstance(
        intelligence_hub_data,
        dict,
    ):

        return {
            "status": "not_available",
            "organisation_id": organisation_id,
            "suggested_questions": [],
            "message": ("Verified financial intelligence is " "not available yet."),
        }

    suggested_questions = suggested_question_service.get_suggested_questions(
        intelligence_hub=(intelligence_hub_data),
        limit=8,
    )

    return {
        "status": "success",
        "organisation_id": organisation_id,
        "suggested_questions": (suggested_questions),
    }


@app.get("/ai-cfo/question-catalog/validate")
def validate_ai_cfo_question_catalog() -> dict[str, Any]:
    """
    Validate all predefined AI CFO catalogue questions
    against the current QuestionClassifier.
    """

    validator = QuestionCatalogValidator()

    return validator.validate()


@app.get("/reports/{organisation_id}/cfo/pdf")
def download_cfo_report_pdf(
    organisation_id: str,
):
    """
    Download the persisted AI-FOS CFO Financial
    Intelligence Report for an organization.

    The endpoint serves the PDF already generated by
    the validated financial processing pipeline.
    It does not recalculate financial results.
    """

    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail=("No workspace found for this " "organization."),
        )

    financial_model_folder = Path(workspace["paths"]["financial_model"])

    pdf_path = financial_model_folder / "cfo_report.pdf"

    if not pdf_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "CFO report PDF is not available yet. " "Process financial data first."
            ),
        )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=("AI-FOS_CFO_" "Financial_Intelligence_Report.pdf"),
    )

@app.get("/reports/{organisation_id}/cfo/excel")
def download_cfo_report_excel(
    organisation_id: str,
):
    """
    Download the persisted AI-FOS CFO Financial
    Intelligence Excel workbook for an organization.

    The endpoint serves the Excel workbook already
    generated by the validated financial processing
    pipeline. It does not recalculate financial results.
    """

    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No workspace found for this "
                "organization."
            ),
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    excel_path = (
        financial_model_folder
        / "cfo_report.xlsx"
    )

    if not excel_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "CFO report Excel workbook is not "
                "available yet. Process financial "
                "data first."
            ),
        )

    return FileResponse(
        path=excel_path,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        filename=(
            "AI-FOS_CFO_"
            "Financial_Intelligence_Report.xlsx"
        ),
    )

@app.get("/reports/{organisation_id}/cfo/word")
def download_cfo_report_word(
    organisation_id: str,
):
    """
    Download the persisted professional AI-FOS CFO Word report.
    """

    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No workspace found for this "
                "organisation."
            ),
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    word_path = (
        financial_model_folder
        / "cfo_report.docx"
    )

    if not word_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "CFO report Word document is not "
                "available yet. Process financial "
                "data first."
            ),
        )

    return FileResponse(
        path=word_path,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.wordprocessingml.document"
        ),
        filename=(
            "AI-FOS_CFO_"
            "Financial_Intelligence_Report.docx"
        ),
    )


@app.get(
    "/reports/{organisation_id}/cash-flow"
)
def get_standard_cash_flow_statement(
    organisation_id: str,
) -> dict[str, Any]:
    """
    Return the persisted AI-FOS Standard Cash Flow Statement.

    This endpoint is read-only. It serves the detailed
    reporting output generated by the validated financial
    processing pipeline and does not recalculate financial
    results.
    """

    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No workspace found for this "
                "organization."
            ),
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    cash_flow_statement = FinancialModelService.load_json(
        financial_model_folder,
        "standard_cash_flow_statement.json",
    )

    if not isinstance(cash_flow_statement, dict):
        raise HTTPException(
            status_code=404,
            detail=(
                "Standard Cash Flow Statement is not "
                "available yet. Process financial "
                "data first."
            ),
        )

    if cash_flow_statement.get("status") != "available":
        raise HTTPException(
            status_code=404,
            detail=(
                "Standard Cash Flow Statement is not "
                "available yet. Process financial "
                "data first."
            ),
        )

    return {
        "status": "available",
        "organisation_id": organisation_id,
        "report": cash_flow_statement,
        "controls": {
            "read_only": True,
            "financial_recalculation_performed": False,
            "validated_financial_output_preserved": True,
            "persisted_reporting_output_used": True,
        },
    }

@app.get(
    "/reports/{organisation_id}/income-statement"
)
def get_standard_income_statement(
    organisation_id: str,
) -> dict[str, Any]:
    """
    Return the persisted AI-FOS Standard Income Statement.

    This endpoint is read-only. It serves the detailed
    reporting output generated by the validated financial
    processing pipeline and does not recalculate financial
    results.
    """

    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No workspace found for this "
                "organization."
            ),
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    income_statement = FinancialModelService.load_json(
        financial_model_folder,
        "standard_income_statement.json",
    )

    if not isinstance(income_statement, dict):
        raise HTTPException(
            status_code=404,
            detail=(
                "Standard Income Statement is not "
                "available yet. Process financial "
                "data first."
            ),
        )

    if income_statement.get("status") != "available":
        raise HTTPException(
            status_code=404,
            detail=(
                "Standard Income Statement is not "
                "available yet. Process financial "
                "data first."
            ),
        )

    return {
        "status": "available",
        "organisation_id": organisation_id,
        "report": income_statement,
        "controls": {
            "read_only": True,
            "financial_recalculation_performed": False,
            "validated_financial_output_preserved": True,
            "persisted_reporting_output_used": True,
        },
    }

@app.get(
    "/reports/{organisation_id}/cash-flow/excel"
)
def download_standard_cash_flow_statement_excel(
    organisation_id: str,
):
    """
    Download the persisted AI-FOS Standard Cash Flow
    Statement as a professionally formatted Excel
    workbook.

    The endpoint is presentation-only.

    It reads the already persisted Standard Cash Flow
    Statement and does not recalculate financial
    results.
    """

    workspace = (
        workspace_service
        .get_workspace_by_organisation(
            organisation_id=organisation_id
        )
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No workspace found for this "
                "organization."
            ),
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    report = FinancialModelService.load_json(
        financial_model_folder,
        "standard_cash_flow_statement.json",
    )

    if not isinstance(report, dict):
        raise HTTPException(
            status_code=404,
            detail=(
                "Standard Cash Flow Statement is not "
                "available yet. Process financial "
                "data first."
            ),
        )

    organization_metadata = (
        organization_registry_service
        .get_organization(
            organisation_id
        )
    )

    if organization_metadata is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Organization metadata was not "
                "found in the organization registry."
            ),
        )

    organisation_name = str(
        organization_metadata.get(
            "name",
            "",
        )
    ).strip()

    base_currency = str(
        organization_metadata.get(
            "base_currency",
            "",
        )
    ).strip().upper()

    if not organisation_name:
        raise HTTPException(
            status_code=500,
            detail=(
                "Organization name is missing from "
                "the organization registry."
            ),
        )

    if (
        len(base_currency) != 3
        or not base_currency.isalpha()
    ):
        raise HTTPException(
            status_code=500,
            detail=(
                "Organization base currency is "
                "invalid in the organization "
                "registry."
            ),
        )

    excel_bytes = (
        generate_standard_cash_flow_statement_excel(
            report,
            organisation_name=organisation_name,
            base_currency=base_currency,
        )
    )

    safe_organisation_id = (
        organization_registry_service
        .normalize_organisation_id(
            organisation_id
        )
    )

    filename = (
        f"AI-FOS_{safe_organisation_id}_"
        "Cash_Flow_Statement.xlsx"
    )

    return StreamingResponse(
        BytesIO(excel_bytes),
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            ),
        },
    )

@app.get(
    "/reports/{organisation_id}/income-statement/excel"
)
def download_standard_income_statement_excel(
    organisation_id: str,
):
    """
    Download the persisted AI-FOS Standard Income
    Statement as a professionally formatted Excel
    workbook.

    The endpoint is presentation-only.

    It reads the already persisted Standard Income
    Statement and does not recalculate financial
    results.
    """

    workspace = (
        workspace_service
        .get_workspace_by_organisation(
            organisation_id=organisation_id
        )
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No workspace found for this "
                "organization."
            ),
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    report = FinancialModelService.load_json(
        financial_model_folder,
        "standard_income_statement.json",
    )

    if not isinstance(report, dict):
        raise HTTPException(
            status_code=404,
            detail=(
                "Standard Income Statement is not "
                "available yet. Process financial "
                "data first."
            ),
        )

    organization_metadata = (
        organization_registry_service
        .get_organization(
            organisation_id
        )
    )

    if organization_metadata is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Organization metadata was not "
                "found in the organization registry."
            ),
        )

    organisation_name = str(
        organization_metadata.get(
            "name",
            "",
        )
    ).strip()

    base_currency = str(
        organization_metadata.get(
            "base_currency",
            "",
        )
    ).strip().upper()

    if not organisation_name:
        raise HTTPException(
            status_code=500,
            detail=(
                "Organization name is missing from "
                "the organization registry."
            ),
        )

    if (
        len(base_currency) != 3
        or not base_currency.isalpha()
    ):
        raise HTTPException(
            status_code=500,
            detail=(
                "Organization base currency is "
                "invalid in the organization "
                "registry."
            ),
        )

    excel_bytes = (
        generate_standard_income_statement_excel(
            report,
            organisation_name=organisation_name,
            base_currency=base_currency,
        )
    )

    safe_organisation_id = (
        organization_registry_service
        .normalize_organisation_id(
            organisation_id
        )
    )

    filename = (
        f"AI-FOS_{safe_organisation_id}_"
        "Income_Statement.xlsx"
    )

    return Response(
        content=excel_bytes,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            ),
        },
    )

@app.get(
    "/reports/{organisation_id}/balance-sheet"
)
def get_standard_balance_sheet(
    organisation_id: str,
) -> dict[str, Any]:
    """
    Return the persisted AI-FOS Standard Balance Sheet.

    This endpoint is read-only. It serves the detailed
    reporting output generated by the validated financial
    processing pipeline and does not recalculate financial
    results.
    """

    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No workspace found for this "
                "organization."
            ),
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    balance_sheet = FinancialModelService.load_json(
        financial_model_folder,
        "standard_balance_sheet.json",
    )

    if not isinstance(balance_sheet, dict):
        raise HTTPException(
            status_code=404,
            detail=(
                "Standard Balance Sheet is not "
                "available yet. Process financial "
                "data first."
            ),
        )

    if balance_sheet.get("status") != "available":
        raise HTTPException(
            status_code=404,
            detail=(
                "Standard Balance Sheet is not "
                "available yet. Process financial "
                "data first."
            ),
        )

    return {
        "status": "available",
        "organisation_id": organisation_id,
        "report": balance_sheet,
        "controls": {
            "read_only": True,
            "financial_recalculation_performed": False,
            "validated_financial_output_preserved": True,
            "persisted_reporting_output_used": True,
        },
    }



@app.get(
    "/reports/{organisation_id}/balance-sheet/excel"
)
def download_standard_balance_sheet_excel(
    organisation_id: str,
):
    """
    Download the persisted AI-FOS Standard Balance
    Sheet as a professionally formatted Excel
    workbook.

    The endpoint is presentation-only.

    It reads the already persisted Standard Balance
    Sheet and does not recalculate financial
    results.
    """

    workspace = (
        workspace_service
        .get_workspace_by_organisation(
            organisation_id=organisation_id
        )
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "No workspace found for this "
                "organization."
            ),
        )

    financial_model_folder = Path(
        workspace["paths"]["financial_model"]
    )

    report = FinancialModelService.load_json(
        financial_model_folder,
        "standard_balance_sheet.json",
    )

    if not isinstance(report, dict):
        raise HTTPException(
            status_code=404,
            detail=(
                "Standard Balance Sheet is not "
                "available yet. Process financial "
                "data first."
            ),
        )

    organization_metadata = (
        organization_registry_service
        .get_organization(
            organisation_id
        )
    )

    if organization_metadata is None:
        raise HTTPException(
            status_code=404,
            detail=(
                "Organization metadata was not "
                "found in the organization registry."
            ),
        )

    organisation_name = str(
        organization_metadata.get(
            "name",
            "",
        )
    ).strip()

    base_currency = str(
        organization_metadata.get(
            "base_currency",
            "",
        )
    ).strip().upper()

    if not organisation_name:
        raise HTTPException(
            status_code=500,
            detail=(
                "Organization name is missing from "
                "the organization registry."
            ),
        )

    if (
        len(base_currency) != 3
        or not base_currency.isalpha()
    ):
        raise HTTPException(
            status_code=500,
            detail=(
                "Organization base currency is "
                "invalid in the organization "
                "registry."
            ),
        )

    excel_bytes = (
        generate_standard_balance_sheet_excel(
            report,
            organisation_name=organisation_name,
            base_currency=base_currency,
        )
    )

    safe_organisation_id = (
        organization_registry_service
        .normalize_organisation_id(
            organisation_id
        )
    )

    filename = (
        f"AI-FOS_{safe_organisation_id}_"
        "Balance_Sheet.xlsx"
    )

    return Response(
        content=excel_bytes,
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": (
                f'attachment; filename="{filename}"'
            ),
        },
    )

def get_standard_income_statement(
    organisation_id: str,
) -> dict[str, Any]:
    """
    Return the persisted AI-FOS Standard Income Statement.

    This endpoint is read-only. It serves the detailed
    reporting output generated by the validated financial
    processing pipeline and does not recalculate financial
    results.
    """

    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail="Organisation workspace not found.",
        )

    financial_model_folder = (
        workspace_service.get_financial_model_folder(
            workspace
        )
    )

    income_statement = FinancialModelService.load_json(
        financial_model_folder,
        "standard_income_statement.json",
    )

    if not isinstance(income_statement, dict):
        raise HTTPException(
            status_code=404,
            detail=(
                "Standard Income Statement is not available yet. "
                "Process the organisation's financial data first."
            ),
        )

    if income_statement.get("status") != "available":
        raise HTTPException(
            status_code=404,
            detail=(
                "Standard Income Statement is not available yet. "
                "Process the organisation's financial data first."
            ),
        )

    return {
        "status": "available",
        "organisation_id": organisation_id,
        "report": income_statement,
        "controls": {
            "read_only": True,
            "financial_recalculation_performed": False,
            "validated_financial_output_preserved": True,
            "persisted_reporting_output_used": True,
        },
    }

@app.get("/dashboard")
def get_dashboard(
    organisation_id: str = "acss",
):
    workspace = workspace_service.get_workspace_by_organisation(
        organisation_id=organisation_id
    )

    if workspace is None:
        raise HTTPException(
            status_code=404,
            detail=("No workspace was found for this " "organization."),
        )

    financial_model_folder = Path(workspace["paths"]["financial_model"])

    dashboard_path = financial_model_folder / "executive_dashboard.json"

    if not dashboard_path.exists():
        raise HTTPException(
            status_code=404,
            detail=(
                "Executive Dashboard is not available yet. "
                "Process financial data first."
            ),
        )

    with dashboard_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


@app.get("/organisations/registry")
def list_organisation_registry() -> dict[str, Any]:
    """
    Return the active AI-FOS organization registry.

    This is the backend source of truth for
    organization selection in the frontend.
    """
    return {"organizations": (organization_registry_service.list_organizations())}


@app.post("/organisations/onboard")
def onboard_organisation(
    payload: dict[str, Any],
) -> dict[str, Any]:
    """
    Create a new AI-FOS organization and ensure
    that it has a persistent workspace.

    This onboarding path belongs to the current
    workspace-based multi-organization architecture
    and is intentionally separate from the legacy
    SQL Organisation table.
    """

    organisation_id = str(
        payload.get(
            "id",
            "",
        )
    ).strip()

    organisation_name = str(
        payload.get(
            "name",
            "",
        )
    ).strip()

    base_currency = (
        str(
            payload.get(
                "base_currency",
                "USD",
            )
        )
        .strip()
        .upper()
    )

    normalized_id = organization_registry_service.normalize_organisation_id(
        organisation_id
    )

    if not normalized_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization ID is required.",
        )

    if not organisation_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Organization name is required.",
        )

    if len(base_currency) != 3 or not base_currency.isalpha():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=("Base currency must be a " "3-letter currency code."),
        )

    existing_organization = organization_registry_service.get_organization(
        normalized_id
    )

    if existing_organization is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("An organization with this ID " "already exists."),
        )

    existing_workspace = workspace_service.get_workspace_by_organisation(normalized_id)

    if existing_workspace is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=("A workspace already exists for " "this organization ID."),
        )

    try:
        workspace = workspace_service.ensure_organization_workspace(
            organisation_id=normalized_id,
            organisation_name=organisation_name,
            base_currency=base_currency,
        )

        organization = organization_registry_service.create_organization(
            organisation_id=normalized_id,
            name=organisation_name,
            base_currency=base_currency,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Organization onboarding failed.",
        ) from exc

    return {
        "status": "created",
        "organization": organization,
        "workspace": {
            "workspace_id": workspace.get("workspace_id"),
            "organisation_id": workspace.get("organisation_id"),
            "status": workspace.get("status"),
        },
    }


@app.post(
    "/organisations",
    response_model=OrganisationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_organisation(
    payload: OrganisationCreate,
    db: Session = Depends(get_db),
) -> Organisation:
    organisation = Organisation(
        name=payload.name.strip(),
        base_currency=payload.base_currency.upper(),
        fiscal_year_start_month=payload.fiscal_year_start_month,
    )

    db.add(organisation)
    db.commit()
    db.refresh(organisation)

    return organisation


@app.get(
    "/organisations/{organisation_id}",
    response_model=OrganisationRead,
)
def get_organisation(
    organisation_id: str,
    db: Session = Depends(get_db),
) -> Organisation:
    organisation = db.get(
        Organisation,
        organisation_id,
    )

    if organisation is None:
        raise HTTPException(
            status_code=404,
            detail="Organisation not found",
        )

    return organisation


@app.post(
    "/organisations/{organisation_id}/imports",
    response_model=ImportRead,
    status_code=status.HTTP_201_CREATED,
)
def register_import(
    organisation_id: str,
    payload: ImportCreate,
    db: Session = Depends(get_db),
) -> ImportJob:
    organisation = db.get(
        Organisation,
        organisation_id,
    )

    if organisation is None:
        raise HTTPException(
            status_code=404,
            detail="Organisation not found",
        )

    import_job = ImportJob(
        organisation_id=organisation_id,
        source_filename=payload.source_filename,
        source_system=payload.source_system,
    )

    db.add(import_job)
    db.commit()
    db.refresh(import_job)

    return import_job


@app.get(
    "/imports/{import_id}",
    response_model=ImportRead,
)
def get_import(
    import_id: str,
    db: Session = Depends(get_db),
) -> ImportJob:
    import_job = db.get(
        ImportJob,
        import_id,
    )

    if import_job is None:
        raise HTTPException(
            status_code=404,
            detail="Import job not found",
        )

    return import_job


@app.post("/ai/chat")
def ask_ai_cfo(
    payload: FinancialQuestion,
) -> dict[str, str]:
    """
    Ask the AI-FOS Digital CFO about the loaded financial data.
    """

    try:
        answer = organization.ask_financial_question(payload.question)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return {
        "question": payload.question,
        "answer": answer,
    }


@app.get("/debug-marker")
def debug_marker():
    return {
        "status": "ok",
        "message": "AI-FOS CURRENT MAIN.PY",
    }


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    organisation_id: str = Form(...),
    organisation_name: str = Form(...),
    base_currency: str = Form("USD"),
):

    print("=" * 60)
    print("UPLOAD ENDPOINT WAS CALLED")
    print("=" * 60)

    try:
        file_path = UPLOAD_FOLDER / file.filename

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        file_size = os.path.getsize(file_path)

        saved_to = str(file_path)

        workbook_info = inspect_workbook(file_path)

        sheet_count = workbook_info["sheet_count"]
        sheet_names = workbook_info["sheet_names"]
        sheet_name = workbook_info["sheet_name"]
        row_count = workbook_info["row_count"]
        column_count = workbook_info["column_count"]
        headers = workbook_info["headers"]
        document_type = workbook_info["document_type"]

        print(f"Document detected: {document_type}")

        workspace = workspace_service.create_workspace(
            organisation_id=organisation_id,
            organisation_name=organisation_name,
            base_currency=base_currency,
        )

        workspace_upload = workspace_service.save_upload(
            workspace_id=workspace["workspace_id"],
            source_file=file_path,
            document_type=document_type,
        )

        print(
            f"Workspace ready: "
            f"{workspace['workspace_id']} "
            f"for organisation "
            f"{organisation_name}"
        )

        print("STEP 1 OK")

    except Exception as exc:
        import traceback

        traceback.print_exc()

        return {
            "status": "error",
            "stage": "upload_initialization",
            "error_type": type(exc).__name__,
            "error": str(exc),
        }

    #
    # CHART OF ACCOUNTS
    #

    if document_type == "chart_of_accounts":
        chart = ChartOfAccounts()

        chart.load_chart(str(file_path))

        detected_columns = chart.detect_columns()

        validation = chart.validate_chart()

        if validation["errors"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": ("The Chart of Accounts " "failed validation."),
                    "validation": validation,
                },
            )

        chart.build_hierarchy()

        hierarchy_validation = chart.validate_hierarchy()

        if hierarchy_validation["errors"]:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": (
                        "The Chart of Accounts hierarchy " "failed validation."
                    ),
                    "hierarchy_validation": (hierarchy_validation),
                },
            )

        accounts = chart.enrich_accounts()

        financial_model_folder = Path(workspace["paths"]["financial_model"])

        dim_account_file = financial_model_service.save_dim_account(
            financial_model_folder=(financial_model_folder),
            accounts=accounts,
        )

        organization.load_chart_of_accounts(
            accounts=accounts,
            accounts_by_number=(chart.normalizer.get_all_accounts()),
        )

        return {
            "message": (
                f"{file.filename} uploaded " f"successfully as a " f"Chart of Accounts"
            ),
            "workspace_id": workspace["workspace_id"],
            "organisation_id": (organisation_id),
            "organisation_name": (organisation_name),
            "workspace_status": (workspace["status"]),
            "workspace_upload": (workspace_upload),
            "dim_account_file": str(dim_account_file),
            "document_type": (document_type),
            "size_bytes": file_size,
            "saved_to": saved_to,
            "sheet_count": sheet_count,
            "sheet_names": sheet_names,
            "sheet_name": sheet_name,
            "row_count": row_count,
            "column_count": column_count,
            "headers": headers,
            "detected_columns": (detected_columns),
            "validation": validation,
            "hierarchy_validation": hierarchy_validation,
            "account_count": len(accounts),
            "accounts": accounts[:10],
        }

    #
    # GENERAL LEDGER
    #

    if document_type == "general_ledger":

        if not organization.accounts_by_number:
            financial_model_folder = Path(workspace["paths"]["financial_model"])

            saved_accounts = financial_model_service.load_dim_account(
                financial_model_folder=(financial_model_folder)
            )

            if saved_accounts:
                accounts_by_number = {
                    str(account["account_number"]): account
                    for account in saved_accounts
                    if account.get("account_number")
                }

                organization.load_chart_of_accounts(
                    accounts=saved_accounts,
                    accounts_by_number=(accounts_by_number),
                )

                print("DIM_ACCOUNT restored " "from workspace.")


        gl_mapping = workbook_info["gl_mapping"]

        transactions = workbook_info["transactions"]

        print("GL STEP A - normalize start")

        normalized_transactions = gl_normalizer.normalize_transactions(
            transactions=transactions,
            company_code=organisation_id.upper(),
            source_system="business_central",
        )

        print("GL STEP B - normalize done")

        if not organization.accounts_by_number:
            gl_account_result = gl_account_builder.build(
                normalized_transactions
            )

            organization.load_chart_of_accounts(
                accounts=gl_account_result["accounts"],
                accounts_by_number=(
                    gl_account_result["accounts_by_number"]
                ),
            )

            if not gl_account_result["accounts_by_number"]:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        "The General Ledger does not contain "
                        "any usable account numbers."
                    ),
                )


            financial_model_service.save_dim_account(
                financial_model_folder=financial_model_folder,
                accounts=gl_account_result["accounts"],
            )

            print(
                "Minimal DIM_ACCOUNT generated "
                "from General Ledger."
            )

        print("GL STEP C - date validation start")

        date_quality = gl_date_validator.validate(
            transactions=normalized_transactions,
        )

        print("GL STEP D - date validation done")

        budget_actual_classification_summary = {
            "operating_expense": 0,
            "capital_purchase": 0,
            "closing_entry": 0,
            "depreciation": 0,
            "revenue": 0,
            "non_budget": 0,
            "budget_consuming_count": 0,
            "excluded_count": 0,
        }

        budget_actual_classification_samples = {
            "operating_expense": [],
            "capital_purchase": [],
            "closing_entry": [],
            "depreciation": [],
            "revenue": [],
            "non_budget": [],
        }

        print("GL STEP E - budget classification start")

        for transaction in normalized_transactions:
            classification = budget_actual_classifier.classify(
                transaction=transaction,
                accounts_by_number=organization.accounts_by_number,
            )

            treatment = classification.get(
                "budget_treatment",
                "non_budget",
            )

            if treatment not in budget_actual_classification_summary:
                budget_actual_classification_summary[treatment] = 0

            if treatment not in budget_actual_classification_samples:
                budget_actual_classification_samples[treatment] = []

            budget_actual_classification_summary[treatment] += 1

            if classification.get("is_budget_consuming"):
                budget_actual_classification_summary["budget_consuming_count"] += 1
            else:
                budget_actual_classification_summary["excluded_count"] += 1

            if len(budget_actual_classification_samples[treatment]) < 5:
                budget_actual_classification_samples[treatment].append(
                    {
                        "transaction_id": transaction.get("transaction_id"),
                        "posting_date": transaction.get("posting_date"),
                        "account_number": transaction.get("account_number"),
                        "account_name": transaction.get("account_name"),
                        "description": transaction.get("description"),
                        "fund_code": transaction.get("fund_code"),
                        "budget_line_code": transaction.get("budget_line_code"),
                        "amount": transaction.get("amount"),
                        "budget_actual_amount": classification.get(
                            "budget_actual_amount"
                        ),
                        "reason": classification.get("reason"),
                    }
                )

        print("GL STEP F - budget classification done")

        print("GL STEP G - GL integrity validation start")

        gl_integrity = gl_integrity_validator.validate(
            transactions=normalized_transactions,
            accounts_by_number=organization.accounts_by_number,
        )

        print("GL STEP H - GL integrity validation done")

        financial_model_folder = Path(workspace["paths"]["financial_model"])

        gl_date_quality_file = financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="gl_date_quality.json",
            data=date_quality,
        )

        gl_integrity_file = financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="gl_integrity.json",
            data=gl_integrity,
        )

        fact_gl_file = fact_gl_service.save_fact_gl(
            financial_model_folder=(financial_model_folder),
            transactions=normalized_transactions,
        )

        dimension_summary = dimension_builder.build_all_dimensions(
            financial_model_folder=(financial_model_folder),
            transactions=normalized_transactions,
        )

        model_validation = model_validator.validate_model(financial_model_folder)

        organization_profile = organization_knowledge_builder.build(
            organisation_id=organisation_id,
            organisation_name=organisation_name,
            source_system="business_central",
            currency=base_currency,
            transaction_count=len(normalized_transactions),
            dimension_summary=dimension_summary,
            model_validation=model_validation,
        )

        organization_profile_file = organization_knowledge_builder.save(
            profile=organization_profile,
            folder=Path(workspace["paths"]["ai_knowledge"]),
        )

        fund_knowledge = organization_knowledge_reader.load_fund_knowledge(
            Path(workspace["paths"]["ai_knowledge"])
        )

        organization.load_fund_knowledge(fund_knowledge)

        organization.load_general_ledger(
            transactions=transactions,
            normalized_transactions=normalized_transactions,
        )

        financial_model_folder = Path(workspace["paths"]["financial_model"])

        if not organization.budget.lines:
            saved_budget_file = financial_model_folder / "budget.json"

            if saved_budget_file.exists():

                with saved_budget_file.open(
                    "r",
                    encoding="utf-8",
                ) as budget_json_file:
                    saved_budget_lines = json.load(budget_json_file)

                if saved_budget_lines:
                    organization.load_budget(saved_budget_lines)

                    print("BUDGET restored from workspace.")

        if not organization.needed_budget.lines:
            saved_needed_budget_file = financial_model_folder / "needed_budget.json"

            if saved_needed_budget_file.exists():

                with saved_needed_budget_file.open(
                    "r",
                    encoding="utf-8",
                ) as needed_budget_json_file:
                    saved_needed_budget_lines = json.load(needed_budget_json_file)

                if saved_needed_budget_lines:
                    organization.load_needed_budget(saved_needed_budget_lines)

                    print("NEEDED BUDGET restored " "from workspace.")

        if not organization.expected_funding:
            saved_expected_funding_file = (
                financial_model_folder
                / "expected_funding.json"
            )

            if saved_expected_funding_file.exists():

                with saved_expected_funding_file.open(
                    "r",
                    encoding="utf-8",
                ) as expected_funding_json_file:
                    saved_expected_funding_lines = (
                        json.load(
                            expected_funding_json_file
                        )
                    )

                if saved_expected_funding_lines:
                    organization.load_expected_funding(
                        saved_expected_funding_lines
                    )

                    organization.generate_expected_funding_analysis()

                    print(
                        "EXPECTED FUNDING restored "
                        "from workspace."
                    )

        if not organization.core_cost_coverage_inputs:
            saved_core_cost_coverage_file = (
                financial_model_folder
                / "core_cost_coverage.json"
            )

            if saved_core_cost_coverage_file.exists():

                with saved_core_cost_coverage_file.open(
                    "r",
                    encoding="utf-8",
                ) as core_cost_coverage_json_file:
                    saved_core_cost_coverage_lines = (
                        json.load(
                            core_cost_coverage_json_file
                        )
                    )

                if saved_core_cost_coverage_lines:
                    organization.load_core_cost_coverage(
                        saved_core_cost_coverage_lines
                    )

                    organization.generate_core_cost_coverage_analysis()

                    print(
                        "CORE COST COVERAGE restored "
                        "from workspace."
                    )

        if organization.budget.lines:
            organization.generate_budget_analysis()

        if organization.needed_budget.lines:
            organization.generate_needed_budget_analysis()

        if organization.needed_budget_vs_actual:
            organization.generate_funding_gap_analysis()

        organization.process_financials()

        financial_model_files = financial_model_service.save_financial_outputs(
            financial_model_folder=financial_model_folder,
            trial_balance=organization.trial_balance,
            income_statement=organization.income_statement,
            standard_income_statement=(
                organization.standard_income_statement
            ),
            balance_sheet=organization.balance_sheet,
            standard_balance_sheet=organization.standard_balance_sheet,
            cash_flow=organization.cash_flow,
            standard_cash_flow_statement=(
                organization.standard_cash_flow_statement
            ),
            liquidity=organization.liquidity,
            financial_facts=organization.financial_facts,
            financial_analysis=organization.financial_analysis,
            financial_trends=organization.financial_trends,
            financial_forecast=organization.financial_forecast,
        )

        organization.calculate_financial_health()
        organization.build_risk_assessment()
        organization.build_forward_risks()
        organization.build_financial_opportunities()
        organization.build_cfo_recommendations()
        organization.build_executive_decision_intelligence()

        FinancialModelService.save_verified_intelligence_outputs(
            financial_model_folder=financial_model_folder,
            financial_health=organization.financial_health,
            risk_assessment=organization.risk_assessment,
            forward_risks=organization.forward_risks,
            financial_opportunities=organization.financial_opportunities,
            cfo_recommendations=organization.cfo_recommendations,
            executive_decision_intelligence=(
                organization.executive_decision_intelligence
            ),
        )

        FinancialIntelligenceHistoryService.record_snapshot(
            financial_model_folder=financial_model_folder,
            financial_health=organization.financial_health,
            liquidity=organization.liquidity,
            financial_facts=organization.financial_facts,
            budget_dashboard=organization.budget_dashboard,
            funding_gap=organization.funding_gap,
            grant_diagnostics=organization.grant_diagnostics,
            expected_funding_intelligence=(
                organization.expected_funding_intelligence
            ),
            financial_trends=organization.financial_trends,
            financial_forecast=organization.financial_forecast,
            risk_assessment=organization.risk_assessment,
            forward_risks=organization.forward_risks,
            financial_opportunities=(
                organization.financial_opportunities
            ),
            cfo_recommendations=organization.cfo_recommendations,
            executive_decision_intelligence=(
                organization.executive_decision_intelligence
            ),
            analysis_start_date=None,
            analysis_end_date=None,
            source="financial_processing",
        )

        financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="budget_vs_actual.json",
            data=organization.budget_vs_actual,
        )

        financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="budget_mapping_intelligence.json",
            data=organization.budget_mapping_intelligence,
        )

        if organization.needed_budget_vs_actual:
            financial_model_service.save_json(
                financial_model_folder=financial_model_folder,
                filename="needed_budget_vs_actual.json",
                data=organization.needed_budget_vs_actual,
            )

        if organization.funding_gap:
            financial_model_service.save_json(
                financial_model_folder=financial_model_folder,
                filename="funding_gap.json",
                data=organization.funding_gap,
            )

        if organization.expected_funding_intelligence:
            financial_model_service.save_json(
                financial_model_folder=financial_model_folder,
                filename="expected_funding_intelligence.json",
                data=organization.expected_funding_intelligence,
            )

        print("STEP 2")
        organization.calculate_financial_health()
        print("STEP 2")

        financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="financial_health.json",
            data=organization.financial_health,
        )

        grants_data = {
            grant_code: {
                "code": grant.code,
                "name": grant.name,
                "start_date": grant.start_date,
                "end_date": grant.end_date,
                "original_budget": grant.original_budget,
                "revised_budget": grant.revised_budget,
                "actual": grant.actual,
                "remaining_budget": grant.remaining_budget,
                "utilization": grant.utilization,
                "projects": sorted(grant.projects),
            }
            for grant_code, grant in organization.grants.items()
        }

        financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="grants.json",
            data=grants_data,
        )

        financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="grant_diagnostics.json",
            data=organization.grant_diagnostics,
        )
        print("STEP 4")
        organization.build_risk_assessment()
        print("STEP 5")
        financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="risk_assessment.json",
            data=organization.risk_assessment,
        )

        organization.build_forward_risks()

        financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="forward_risks.json",
            data=organization.forward_risks,
        )

        organization.build_financial_opportunities()

        financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="financial_opportunities.json",
            data=organization.financial_opportunities,
        )

        organization.build_structured_cfo_report()

        financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="cfo_report.json",
            data=organization.structured_cfo_report,
        )

        cfo_report_pdf = generate_cfo_report_pdf(
            organization.structured_cfo_report
        )

        (financial_model_folder / "cfo_report.pdf").write_bytes(
            cfo_report_pdf
        )

        cfo_report_excel = generate_cfo_report_excel(
            organization.structured_cfo_report,
            standard_income_statement=(
                organization.standard_income_statement
            ),
            standard_balance_sheet=(
                organization.standard_balance_sheet
            ),
            organisation_name=organisation_name,
            base_currency=base_currency,
        )

        (financial_model_folder / "cfo_report.xlsx").write_bytes(
            cfo_report_excel
        )

        organization.build_kpi_dashboard()

        cfo_report_word = generate_cfo_report_word(
            organization.structured_cfo_report
        )

        (financial_model_folder / "cfo_report.docx").write_bytes(
            cfo_report_word
        )

        organization.build_executive_dashboard()

        financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="executive_dashboard.json",
            data=organization.executive_dashboard,
        )

        intelligence_hub_data = intelligence_hub.build(
            organisation_id=organisation_id,
            organisation_name=organisation_name,
            currency=base_currency,
            financial_facts=organization.financial_facts,
            financial_analysis=organization.financial_analysis,
            financial_health=organization.financial_health,
            trial_balance=organization.trial_balance,
            income_statement=organization.income_statement,
            balance_sheet=organization.balance_sheet,
            cash_flow=organization.cash_flow,
            budget_dashboard=organization.budget_dashboard,
            grant_diagnostics=organization.grant_diagnostics,
            risk_assessment=organization.risk_assessment,
            cfo_recommendations=organization.cfo_recommendations,
            kpi_dashboard=organization.kpi_dashboard,
            executive_dashboard=organization.executive_dashboard,
        )

        intelligence_hub_file = financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="intelligence_hub.json",
            data=intelligence_hub_data,
        )
        print("STEP 6")

        ai_cfo_generation_status = {
            "status": "not_attempted",
            "message": None,
        }

        try:
            organization.generate_ai_cfo_report()

            ai_cfo_generation_status = {
                "status": "success",
                "message": "AI CFO report generated successfully.",
            }

        except Exception as exc:
            print("=" * 60)
            print("AI CFO REPORT GENERATION FAILED")
            print(f"{type(exc).__name__}: {exc}")
            print("=" * 60)

            organization.ai_cfo_report = {}

            ai_cfo_generation_status = {
                "status": "unavailable",
                "message": (
                    "AI CFO report could not be generated. "
                    "The financial model and deterministic analysis "
                    "were completed successfully."
                ),
                "error_type": type(exc).__name__,
            }

        print("STEP 7")

        cfo_report_generation_status = {
            "status": "not_attempted",
            "message": None,
        }

        try:
            organization.generate_cfo_report()

            cfo_report_generation_status = {
                "status": "success",
                "message": "CFO report generated successfully.",
            }

        except Exception as exc:
            print("=" * 60)
            print("CFO REPORT GENERATION FAILED")
            print(f"{type(exc).__name__}: {exc}")
            print("=" * 60)

            organization.cfo_report = {}

            cfo_report_generation_status = {
                "status": "unavailable",
                "message": (
                    "CFO report could not be generated. "
                    "The financial model and deterministic analysis "
                    "were completed successfully."
                ),
                "error_type": type(exc).__name__,
            }

        grant_portfolio = [
            {
                "code": grant.code,
                "name": grant.name,
                "start_date": grant.start_date,
                "end_date": grant.end_date,
                "original_budget": (grant.original_budget),
                "revised_budget": (grant.revised_budget),
                "actual": grant.actual,
                "remaining_budget": (grant.remaining_budget),
                "utilization": (grant.utilization),
                "project_count": len(grant.projects),
                "transaction_count": len(grant.transactions),
            }
            for grant in organization.grants.values()
        ]

        return {
            "message": (
                f"{file.filename} uploaded " f"successfully as a " f"General Ledger"
            ),
            "workspace_id": workspace["workspace_id"],
            "organisation_id": (organisation_id),
            "organisation_name": (organisation_name),
            "workspace_status": (workspace["status"]),
            "workspace_upload": (workspace_upload),
            "fact_gl_file": str(fact_gl_file),
            "document_type": (document_type),
            "dimension_summary": dimension_summary,
            "date_quality": date_quality,
            "gl_date_quality_file": str(gl_date_quality_file),
            "gl_date_quality_file": str(gl_date_quality_file),
            "gl_integrity": gl_integrity,
            "gl_integrity_file": str(gl_integrity_file),
            "budget_actual_classification_summary": (
                budget_actual_classification_summary
            ),
            "budget_actual_classification_samples": (
                budget_actual_classification_samples
            ),
            "model_validation": model_validation,
            "organization_profile": organization_profile,
            "organization_profile_file": str(organization_profile_file),
            "size_bytes": file_size,
            "saved_to": saved_to,
            "sheet_count": sheet_count,
            "sheet_names": sheet_names,
            "sheet_name": sheet_name,
            "row_count": row_count,
            "column_count": column_count,
            "headers": headers,
            "gl_mapping": gl_mapping,
            "trial_balance": (organization.trial_balance),
            "income_statement": (organization.income_statement),
            "balance_sheet": (organization.balance_sheet),
            "cash_flow": (organization.cash_flow),
            "liquidity": (organization.liquidity),
            "financial_facts": (organization.financial_facts),
            "financial_model_files": financial_model_files,
            "financial_analysis": (organization.financial_analysis),
            "financial_health": (organization.financial_health),
            "risk_assessment": organization.risk_assessment,
            "cfo_recommendations": organization.cfo_recommendations,
            "intelligence_hub": intelligence_hub_data,
            "intelligence_hub_file": str(intelligence_hub_file),
            "kpi_dashboard": (organization.kpi_dashboard),
            "executive_dashboard": (organization.executive_dashboard),
            "budget_vs_actual": (organization.budget_vs_actual),
            "budget_dashboard": (organization.budget_dashboard),
            "ai_cfo_generation_status": ai_cfo_generation_status,
            "ai_cfo_report": (organization.ai_cfo_report),
            "cfo_report_generation_status": cfo_report_generation_status,
            "cfo_report": (organization.cfo_report),
            "grant_count": len(organization.grants),
            "grant_diagnostics": (organization.grant_diagnostics),
            "grants": (grant_portfolio[:50]),
            "transactions": (transactions[:10]),
        }

    #
    # BUDGET
    #

    if document_type == "budget":
        budget_mapping = workbook_info["budget_mapping"]

        budget_lines = workbook_info["budget_lines"]

        if not budget_lines:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": ("No valid budget " "lines were found."),
                    "budget_mapping": (budget_mapping),
                },
            )

        organization.load_budget(budget_lines)

        needed_budget_lines = workbook_info.get(
            "needed_budget_lines",
            [],
        )

        if needed_budget_lines:
            organization.load_needed_budget(
                needed_budget_lines
            )

        expected_funding_lines = workbook_info.get(
            "expected_funding_lines",
            [],
        )

        if expected_funding_lines:
            organization.load_expected_funding(
                expected_funding_lines
            )

            organization.generate_expected_funding_analysis()

        core_cost_coverage_lines = workbook_info.get(
            "core_cost_coverage_lines",
            [],
        )

        if core_cost_coverage_lines:
            organization.load_core_cost_coverage(
                core_cost_coverage_lines
            )

            organization.generate_core_cost_coverage_analysis()

            organization.generate_expected_funding_analysis()

        financial_model_folder = Path(workspace["paths"]["financial_model"])

        budget_file = financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="budget.json",
            data=budget_lines,
        )

        needed_budget_lines = workbook_info.get(
            "needed_budget_lines",
            [],
        )

        needed_budget_file = None

        if needed_budget_lines:
            needed_budget_file = financial_model_service.save_json(
                financial_model_folder=financial_model_folder,
                filename="needed_budget.json",
                data=needed_budget_lines,
            )

        expected_funding_file = None

        if expected_funding_lines:
            expected_funding_file = financial_model_service.save_json(
                financial_model_folder=financial_model_folder,
                filename="expected_funding.json",
                data=expected_funding_lines,
            )

        expected_funding_intelligence_file = None

        if organization.expected_funding_intelligence:
            expected_funding_intelligence_file = (
                financial_model_service.save_json(
                    financial_model_folder=financial_model_folder,
                    filename="expected_funding_intelligence.json",
                    data=organization.expected_funding_intelligence,
                )
            )

        core_cost_coverage_file = None

        if core_cost_coverage_lines:
            core_cost_coverage_file = (
                financial_model_service.save_json(
                    financial_model_folder=financial_model_folder,
                    filename="core_cost_coverage.json",
                    data=core_cost_coverage_lines,
                )
            )

        core_cost_coverage_intelligence_file = None

        if organization.core_cost_coverage:
            core_cost_coverage_intelligence_file = (
                financial_model_service.save_json(
                    financial_model_folder=financial_model_folder,
                    filename="core_cost_coverage_intelligence.json",
                    data=organization.core_cost_coverage,
                )
            )

        return {
            "message": (f"{file.filename} uploaded " f"successfully as a Budget"),
            "workspace_id": workspace["workspace_id"],
            "organisation_id": (organisation_id),
            "organisation_name": (organisation_name),
            "workspace_status": (workspace["status"]),
            "workspace_upload": (workspace_upload),
            "document_type": (document_type),
            "size_bytes": file_size,
            "saved_to": saved_to,
            "budget_file": str(budget_file),
            "needed_budget_file": (
                str(needed_budget_file) if needed_budget_file else None
            ),

            "needed_budget_line_count": len(needed_budget_lines),
            "expected_funding_file": (
                str(expected_funding_file)
                if expected_funding_file
                else None
            ),
            "expected_funding_line_count": len(
                expected_funding_lines
            ),
            "expected_funding_intelligence_file": (
                str(expected_funding_intelligence_file)
                if expected_funding_intelligence_file
                else None
            ),
            "core_cost_coverage_file": (
                str(core_cost_coverage_file)
                if core_cost_coverage_file
                else None
            ),
            "core_cost_coverage_line_count": len(
                core_cost_coverage_lines
            ),
            "core_cost_coverage_intelligence_file": (
                str(core_cost_coverage_intelligence_file)
                if core_cost_coverage_intelligence_file
                else None
            ),
            "sheet_count": sheet_count,
            "sheet_names": sheet_names,
            "sheet_name": sheet_name,
            "row_count": row_count,
            "column_count": column_count,
            "headers": headers,
            "budget_mapping": (budget_mapping),
            "budget_line_count": len(budget_lines),
            "budget_account_count": (organization.budget.account_count()),
            "unique_budget_line_count": (organization.budget.budget_line_count()),
            "budget_summary": (organization.budget_summary),
            "budget_lines": (budget_lines[:10]),
        }

    #
    # UNKNOWN DOCUMENT
    #

    raise HTTPException(
        status_code=400,
        detail={
            "message": ("AI-FOS could not identify " "the uploaded document."),
            "document_type": (document_type),
            "headers": headers,
        },
    )




