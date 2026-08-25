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
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app.models import ImportJob, Organisation
from app.organization import Organization
from app.schemas import (
    FinancialQuestion,
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
from app.services.dimension_builder import DimensionBuilder
from app.services.gl_normalizer import GLNormalizer
from app.services.model_validator import ModelValidator
from app.services.ai_question_engine import AIQuestionEngine
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

Base.metadata.create_all(bind=engine)


UPLOAD_FOLDER = Path("uploads")
UPLOAD_FOLDER.mkdir(exist_ok=True)


app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Digital CFO platform canonical data foundation",
)


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
financial_model_service = FinancialModelService()
fact_gl_service = FactGLService()
dimension_builder = DimensionBuilder()
gl_normalizer = GLNormalizer()
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
suggested_question_service = SuggestedQuestionService()


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "service": settings.app_name,
        "version": "0.2.0",
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


@app.get("/ask/{organisation_id}")
def ask_ai(
    organisation_id: str,
    question: str,
) -> dict[str, Any]:

    return ai_question_engine.answer(
        question=question,
        organisation_id=organisation_id,
    )

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

    workspace = (
        workspace_service
        .get_workspace_by_organisation(
            organisation_id=organisation_id
        )
    )

@app.get("/ai-cfo/question-catalog/validate")
def validate_ai_cfo_question_catalog() -> dict[str, Any]:
    """
    Validate all predefined AI CFO catalogue questions
    against the current QuestionClassifier.
    """

    validator = QuestionCatalogValidator()

    return validator.validate()    

    if workspace is None:

        return {
            "status": "not_available",
            "organisation_id": organisation_id,
            "suggested_questions": [],
            "message": (
                "No workspace was found for this "
                "organization."
            ),
        }

    financial_model_folder = Path(
        workspace[
            "paths"
        ][
            "financial_model"
        ]
    )

    intelligence_hub_data = (
        financial_model_service.load_json(
            financial_model_folder=(
                financial_model_folder
            ),
            filename="intelligence_hub.json",
        )
    )

    if not isinstance(
        intelligence_hub_data,
        dict,
    ):

        return {
            "status": "not_available",
            "organisation_id": organisation_id,
            "suggested_questions": [],
            "message": (
                "Verified financial intelligence is "
                "not available yet."
            ),
        }

    suggested_questions = (
        suggested_question_service
        .get_suggested_questions(
            intelligence_hub=(
                intelligence_hub_data
            ),
            limit=8,
        )
    )

    return {
        "status": "success",
        "organisation_id": organisation_id,
        "suggested_questions": (
            suggested_questions
        ),
    }

@app.get("/dashboard")
def get_dashboard():
    return organization.executive_dashboard


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

            else:
                raise HTTPException(
                    status_code=400,
                    detail={
                        "message": (
                            "Upload the "
                            "organization's "
                            "Chart of Accounts "
                            "before uploading "
                            "the General Ledger."
                        )
                    },
                )

        gl_mapping = workbook_info["gl_mapping"]

        transactions = workbook_info["transactions"]

        print("GL STEP A - normalize start")

        normalized_transactions = gl_normalizer.normalize_transactions(
            transactions=transactions,
            company_code=organisation_id.upper(),
            source_system="business_central",
        )

        print("GL STEP B - normalize done")

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
                saved_needed_budget_file = (
                    financial_model_folder
                    / "needed_budget.json"
                )

                if saved_needed_budget_file.exists():

                    with saved_needed_budget_file.open(
                        "r",
                        encoding="utf-8",
                    ) as needed_budget_json_file:
                        saved_needed_budget_lines = (
                            json.load(
                                needed_budget_json_file
                            )
                        )

                    if saved_needed_budget_lines:
                        organization.load_needed_budget(
                            saved_needed_budget_lines
                        )

                        print(
                            "NEEDED BUDGET restored "
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
            balance_sheet=organization.balance_sheet,
            cash_flow=organization.cash_flow,
            liquidity=organization.liquidity,
            financial_facts=organization.financial_facts,
            financial_analysis=organization.financial_analysis,
        )

        financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="budget_vs_actual.json",
            data=organization.budget_vs_actual,
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

        organization.build_cfo_recommendations()

        financial_model_service.save_json(
            financial_model_folder=financial_model_folder,
            filename="cfo_recommendations.json",
            data=organization.cfo_recommendations,
        )

        organization.build_kpi_dashboard()

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
