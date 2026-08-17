from typing import Any
from app.services.balance_sheet import generate_balance_sheet
from app.services.financial_analysis import analyze_financials
from app.services.financial_facts import generate_financial_facts
from app.services.income_statement import generate_income_statement
from app.services.trial_balance import generate_trial_balance
from app.services.cash_flow import generate_cash_flow_statement
from datetime import datetime
from app.services.period_filter import filter_transactions
from app.services.budget import Budget
from app.services.budget_summary import generate_budget_summary
from app.services.budget_vs_actual import generate_budget_vs_actual
from app.services.budget_actual_classifier import (
    BudgetActualClassifier,
)
from app.services.fund_classifier import FundClassifier
from app.services.budget_dashboard import generate_budget_dashboard
from app.services.grant import Grant
from app.services.grant_diagnostics import generate_grant_diagnostics
from app.services.ai_cfo import generate_ai_cfo_report
from app.services.cfo_report import generate_cfo_report
from app.services.ai_chat import ask_ai
from app.services.financial_health import calculate_financial_health
from app.services.kpi_dashboard import build_kpi_dashboard
from app.services.executive_dashboard import build_executive_dashboard
from app.services.risk_engine import generate_risk_assessment
from app.services.cfo_recommendations import (
    generate_cfo_recommendations,
)
from app.services.liquidity import calculate_liquidity


class Organization:
    """
    Represents one organization's financial data inside AI-FOS.
    """

    def __init__(self):
        self.name: str | None = None

        # Chart of Accounts
        self.chart_of_accounts = None
        self.accounts_by_number: dict[str, dict[str, Any]] = {}

        # Financial data
        self.general_ledger = None
        self.trial_balance = None

        # Reports
        self.balance_sheet = None
        self.income_statement = None
        self.financial_facts = None
        self.financial_analysis = None
        self.cash_flow = None
        self.liquidity = None

        # Planning
        self.budget = Budget()
        self.budget_summary = None
        self.budget_vs_actual = None
        self.budget_dashboard = None
        self.fund_knowledge: dict[str, Any] = {}
        self.grants: dict[str, Grant] = {}
        self.grant_diagnostics = None
        self.ai_cfo_report = None
        self.financial_health = None
        self.risk_assessment: list[dict[str, Any]] = []
        self.cfo_recommendations: list[dict[str, Any]] = []
        self.kpi_dashboard = None
        self.executive_dashboard = None
        self.cfo_report = None

        # Settings
        self.base_currency = None
        self.fiscal_year = None

    def load_chart_of_accounts(
        self,
        accounts: list[dict[str, Any]],
        accounts_by_number: dict[str, dict[str, Any]],
    ) -> None:
        """
        Store the organization's normalized Chart of Accounts.
        """

        self.chart_of_accounts = accounts
        self.accounts_by_number = accounts_by_number


    def load_budget(
        self,
        budget_lines: list[dict[str, Any]],
    ) -> None:
        """
        Store the organization's normalized budget,
        enrich it using organization-specific fund
        knowledge, and generate an executive summary.
        """

        classification_rules = self.fund_knowledge.get(
            "classification_rules",
            {},
        )

        derive_funder_from_fund_code = bool(
            classification_rules.get(
                "derive_funder_from_fund_code",
                False,
            )
        )

        fund_code_separator = str(
            classification_rules.get(
                "fund_code_separator",
                "-",
            )
        )

        funder_code_segment = int(
            classification_rules.get(
                "funder_code_segment",
                0,
            )
        )

        enriched_budget_lines: list[dict[str, Any]] = []

        for budget_line in budget_lines:
            enriched_line = dict(budget_line)

            donor_code = str(
                enriched_line.get("donor_code")
                or enriched_line.get("donor")
                or ""
            ).strip()

            fund_code = str(
                enriched_line.get("fund_code")
                or enriched_line.get("fund")
                or ""
            ).strip()

            if (
                not donor_code
                and derive_funder_from_fund_code
                and fund_code
            ):
                fund_code_parts = fund_code.split(
                    fund_code_separator
                )

                if (
                    0 <= funder_code_segment
                    < len(fund_code_parts)
                ):
                    derived_donor_code = (
                        fund_code_parts[
                            funder_code_segment
                        ].strip()
                    )

                    if derived_donor_code:
                        enriched_line[
                            "donor_code"
                        ] = derived_donor_code

            enriched_budget_lines.append(
                enriched_line
            )

        self.budget.load_budget(
            enriched_budget_lines
        )

        self.budget_summary = generate_budget_summary(
            enriched_budget_lines
        )

    def load_fund_knowledge(
        self,
        fund_knowledge: dict[str, Any],
    ) -> None:
        """
        Store persistent organization-specific fund knowledge.
        """

        self.fund_knowledge = fund_knowledge or {}

    def generate_budget_analysis(self) -> None:
        """
        Compare the loaded budget against General Ledger
        actuals using the canonical AI-FOS transaction model.
        """

        if not self.budget.lines:
            raise ValueError(
                "Load the Budget before generating Budget vs Actual."
            )

        if not self.general_ledger:
            raise ValueError(
                "Load the General Ledger before generating Budget vs Actual."
            )

        transactions_for_analysis = getattr(
            self,
            "normalized_general_ledger",
            None,
        )

        if not transactions_for_analysis:
            transactions_for_analysis = self.general_ledger

        self.budget_vs_actual = generate_budget_vs_actual(
            budget_lines=self.budget.lines,
            transactions=transactions_for_analysis,
            accounts_by_number=self.accounts_by_number,
        )

        self.budget_dashboard = generate_budget_dashboard(
            budget_summary=self.budget_summary,
            budget_vs_actual=self.budget_vs_actual,
        )    

        self.build_grants()

    def build_grants(self) -> None:
        """
        Build grant objects from the loaded Budget and
        canonical AI-FOS General Ledger.
        """

        self.grants = {}

        #
        # 1. Build grants from Budget
        #
        fund_classifier = FundClassifier()

        classification_rules = self.fund_knowledge.get(
            "classification_rules",
            {},
        )

        internal_funder_codes = {
            str(code).strip()
            for code in classification_rules.get(
                "internal_funder_codes",
                [],
            )
            if str(code).strip()
        }

        default_external_funder_is_grant = bool(
            classification_rules.get(
                "default_external_funder_is_grant",
                False,
            )
        )

        derive_funder_from_fund_code = bool(
            classification_rules.get(
                "derive_funder_from_fund_code",
                False,
            )
        )

        fund_code_separator = str(
            classification_rules.get(
                "fund_code_separator",
                "-",
            )
        )

        funder_code_segment = int(
            classification_rules.get(
                "funder_code_segment",
                0,
            )
        )

        for budget_line in self.budget.lines:
            grant_code = str(
                budget_line.get("fund_code") or budget_line.get("fund") or ""
            ).strip()

            if not grant_code:
                continue

            donor_code = str(
                budget_line.get("donor_code") or budget_line.get("donor") or ""
            ).strip()

            if not donor_code and derive_funder_from_fund_code and grant_code:
                fund_code_parts = grant_code.split(fund_code_separator)

                if 0 <= funder_code_segment < len(fund_code_parts):
                    donor_code = fund_code_parts[funder_code_segment].strip()

            if donor_code in internal_funder_codes:
                is_grant = False

            elif donor_code and default_external_funder_is_grant:
                is_grant = True

            else:
                fund_classification = fund_classifier.classify(
                    fund_code=grant_code,
                    fund_name=budget_line.get("fund_name"),
                    donor_code=budget_line.get("donor_code"),
                    donor_name=budget_line.get("donor_name"),
                    explicit_fund_type=budget_line.get("fund_type"),
                    explicit_is_grant=budget_line.get("is_grant"),
                )

                is_grant = fund_classification.get("is_grant") is True

            if not is_grant:
                continue

            grant = self.grants.setdefault(
                grant_code,
                Grant(),
            )

            grant.code = grant_code

            grant_name = str(budget_line.get("fund_name") or "").strip()

            if grant_name:
                grant.name = grant_name

            grant.original_budget += float(budget_line.get("original_budget") or 0)

            grant.revised_budget += float(budget_line.get("revised_budget") or 0)

            project = str(
                budget_line.get("project_code") or budget_line.get("project") or ""
            ).strip()

            if project:
                grant.projects.add(project)

        #
        # 2. Use canonical normalized GL when available
        #
        transactions_for_grants = getattr(
            self,
            "normalized_general_ledger",
            None,
        )

        if not transactions_for_grants:
            transactions_for_grants = self.general_ledger or []

        classifier = BudgetActualClassifier()

        #
        # 3. Add actual financial activity to grants
        #
        for transaction in transactions_for_grants:
            grant_code = str(
                transaction.get("fund_code") or transaction.get("fund") or ""
            ).strip()

            if not grant_code:
                continue

            #
            # Only attach GL activity to funds that
            # were already confirmed as real grants
            # from the Budget classification step.
            #
            grant = self.grants.get(grant_code)

            if grant is None:
                continue

            grant.transactions.append(transaction)

            classification = classifier.classify(
                transaction=transaction,
                accounts_by_number=self.accounts_by_number,
            )

            if not classification["is_budget_consuming"]:
                continue

            grant.actual += float(classification["budget_actual_amount"] or 0)

            project = str(
                transaction.get("project_code") or transaction.get("project") or ""
            ).strip()

            if project:
                grant.projects.add(project)

        #
        # 4. Finalize grant calculations
        #
        for grant in self.grants.values():
            grant.original_budget = round(
                grant.original_budget,
                2,
            )

            grant.revised_budget = round(
                grant.revised_budget,
                2,
            )

            grant.actual = round(
                grant.actual,
                2,
            )

            grant.calculate_financials()

        #
        # 5. Generate grant coverage diagnostics
        #
        self.grant_diagnostics = generate_grant_diagnostics(self.grants)

    def generate_ai_cfo_report(self) -> None:
        """
        Generate the AI-written CFO report using
        verified AI-FOS financial intelligence.
        """

        self.ai_cfo_report = generate_ai_cfo_report(
            income_statement=self.income_statement,
            balance_sheet=self.balance_sheet,
            financial_facts=self.financial_facts,
            cash_flow=self.cash_flow,
            financial_health=self.financial_health,
            risk_assessment=self.risk_assessment,
            cfo_recommendations=self.cfo_recommendations,
            budget_dashboard=self.budget_dashboard,
            grant_count=len(self.grants),
        )

    def generate_cfo_report(self) -> None:
        """
        Generate an executive AI CFO report.
        """

        if not self.financial_analysis:
            raise ValueError(
                "Process the financial data before generating the CFO report."
            )

        financial_summary = f"""
    Financial Analysis:
    {self.financial_analysis}

    Financial Facts:
    {self.financial_facts}

    Income Statement:
    {self.income_statement}

    Balance Sheet:
    {self.balance_sheet}

    Budget Dashboard:
    {self.budget_dashboard}

    Grant Diagnostics:
    {self.grant_diagnostics}
    """

        self.cfo_report = generate_cfo_report(
            financial_summary=financial_summary,
        )

    def ask_financial_question(
        self,
        question: str,
    ) -> str:
        """
        Ask the AI CFO a question about the loaded financial data.
        """

        if not question.strip():
            raise ValueError("A financial question is required.")

        if not self.financial_analysis:
            raise ValueError("Process the financial data before asking the AI CFO.")

        context = f"""
    Financial Analysis:
    {self.financial_analysis}

    Financial Facts:
    {self.financial_facts}

    Income Statement:
    {self.income_statement}

    Balance Sheet:
    {self.balance_sheet}

    Cash Flow:
    {self.cash_flow}

    Budget Dashboard:
    {self.budget_dashboard}

    Grant Diagnostics:
    {self.grant_diagnostics}
    """

        return ask_ai(
            context=context,
            question=question.strip(),
        )

    def load_general_ledger(
        self,
        transactions: list[dict[str, Any]],
        normalized_transactions: list[dict[str, Any]] | None = None,
    ) -> None:
        """
        Store both the source General Ledger and the
        canonical AI-FOS normalized General Ledger.

        The source ledger remains available for existing
        accounting calculations, while the normalized
        ledger is used by the canonical financial model,
        Budget vs Actual, Grant Intelligence, and future
        AI-FOS analytics.
        """

        self.general_ledger = transactions

        self.normalized_general_ledger = (
            normalized_transactions if normalized_transactions is not None else []
        )

    def process_financials(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> None:
        """
        Build the financial reports for the requested period.

        If no dates are supplied, all General Ledger transactions are used.
        """

        if not self.accounts_by_number:
            raise ValueError("Load the Chart of Accounts before processing financials.")

        if not self.general_ledger:
            raise ValueError("Load the General Ledger before processing financials.")

        period_transactions = filter_transactions(
            transactions=self.general_ledger,
            start_date=start_date,
            end_date=end_date,
        )

        if not period_transactions:
            raise ValueError(
                "No General Ledger transactions were found for the selected period."
            )

        self.trial_balance = generate_trial_balance(period_transactions)

        self.income_statement = generate_income_statement(
            transactions=period_transactions,
            accounts_by_number=self.accounts_by_number,
        )

        self.balance_sheet = generate_balance_sheet(
            trial_balance=self.trial_balance,
            accounts_by_number=self.accounts_by_number,
            current_period_result=self.income_statement.get(
                "current_period_result",
                0,
            ),
        )

        self.cash_flow = generate_cash_flow_statement(
            period_transactions,
            self.trial_balance,
            self.accounts_by_number,
        )

        self.liquidity = calculate_liquidity(
            transactions=period_transactions,
            trial_balance=self.trial_balance,
            accounts_by_number=self.accounts_by_number,
        )

        self.financial_facts = generate_financial_facts(
            self.income_statement,
            self.balance_sheet,
        )

        self.financial_analysis = analyze_financials(
            self.income_statement,
            self.balance_sheet,
        )

    def calculate_financial_health(self) -> None:
        """
        Calculate the organisation's Financial Health Score.
        """

        self.financial_health = calculate_financial_health(
            income_statement=self.income_statement,
            balance_sheet=self.balance_sheet,
            budget_dashboard=self.budget_dashboard,
            grant_diagnostics=self.grant_diagnostics,
            liquidity=self.liquidity,
        )

    def build_risk_assessment(self) -> None:
        """
        Build the organisation's CFO Risk Register.
        """

        self.risk_assessment = generate_risk_assessment(
            income_statement=self.income_statement,
            balance_sheet=self.balance_sheet,
            financial_health=self.financial_health,
            budget_dashboard=self.budget_dashboard,
            grant_diagnostics=self.grant_diagnostics,
        )

    def build_cfo_recommendations(self) -> None:
        """
        Build prioritized evidence-based CFO recommendations.
        """

        self.cfo_recommendations = generate_cfo_recommendations(
            income_statement=self.income_statement,
            balance_sheet=self.balance_sheet,
            cash_flow=self.cash_flow,
            financial_health=self.financial_health,
            risk_assessment=self.risk_assessment,
            budget_dashboard=self.budget_dashboard,
            grant_diagnostics=self.grant_diagnostics,
        )

    def build_kpi_dashboard(self) -> None:
        """
        Build the executive KPI dashboard.
        """

        self.kpi_dashboard = build_kpi_dashboard(self)

    def build_executive_dashboard(self) -> None:
        """
        Build the Executive Dashboard.
        """

        self.executive_dashboard = build_executive_dashboard(self)
