from typing import Any
from app.services.balance_sheet import generate_balance_sheet
from app.services.financial_analysis import analyze_financials
from app.services.financial_facts import generate_financial_facts
from app.services.income_statement import generate_income_statement
from app.services.standard_income_statement import (
    generate_standard_income_statement,
)
from app.services.standard_balance_sheet import (
    generate_standard_balance_sheet,
)
from app.services.trial_balance import generate_trial_balance
from app.services.cash_flow import generate_cash_flow_statement
from datetime import datetime
from app.services.period_filter import filter_transactions
from app.services.budget import Budget
from app.services.needed_budget import NeededBudget
from app.services.budget_summary import generate_budget_summary
from app.services.budget_vs_actual import generate_budget_vs_actual
from app.services.budget_mapping_intelligence import (
    generate_budget_mapping_intelligence,
)
from app.services.budget_dimension_drilldown import (
    generate_budget_dimension_drilldown,
)
from app.services.budget_actual_classifier import (
    BudgetActualClassifier,
)
from app.services.needed_budget_vs_actual import (
    generate_needed_budget_vs_actual,
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
from app.services.funding_gap import (
    generate_funding_gap,
)
from app.services.financial_trends import generate_financial_trends
from app.services.financial_forecast import generate_financial_forecast
from app.services.financial_scenarios import (
    generate_financial_scenario,
)
from app.services.funding_scenarios import (
    generate_funding_scenario,
)
from app.services.scenario_decision_intelligence import (
    generate_scenario_decision_intelligence,
)
from app.services.scenario_comparison_intelligence import (
    generate_scenario_comparison_intelligence,
)
from app.services.forward_risk import (
    generate_forward_risks,
)
from app.services.financial_opportunities import (
    generate_financial_opportunities,
)
from app.services.executive_decision_intelligence import (
    generate_executive_decision_intelligence,
)
from app.services.cfo_report_builder import (
    build_cfo_report as build_structured_cfo_report,
)
from app.services.expected_funding_intelligence import (
    generate_expected_funding_intelligence,
)
from app.services.core_cost_coverage import (
    generate_core_cost_coverage,
)
from app.services.standard_cash_flow_statement import (
    generate_standard_cash_flow_statement,
)

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
        self.standard_balance_sheet = None
        self.income_statement = None
        self.standard_income_statement = None
        self.financial_facts = None
        self.financial_analysis = None
        self.financial_trends = None
        self.financial_forecast = None
        self.financial_scenario = None
        self.scenario_decision_intelligence = None
        self.scenario_comparison_intelligence = None
        self.cash_flow = None
        self.standard_cash_flow_statement = None
        self.liquidity = None

        # Planning
        self.budget = Budget()
        self.budget_summary = None
        self.budget_vs_actual = None
        self.budget_mapping_intelligence = None
        self.budget_dashboard = None

        self.needed_budget = NeededBudget()
        self.needed_budget_summary = None
        self.needed_budget_vs_actual = None

        # Prospective Expected Funding
        self.expected_funding: list[dict[str, Any]] = []
        self.expected_funding_intelligence = None
        self.funding_gap = None

        self.core_cost_coverage_inputs: list[
            dict[str, Any]
        ] = []
        self.core_cost_coverage = None
        self.fund_knowledge: dict[str, Any] = {}
        self.grants: dict[str, Grant] = {}
        self.grant_diagnostics = None
        self.ai_cfo_report = None
        self.financial_health = None
        self.risk_assessment: list[dict[str, Any]] = []
        self.forward_risks: list[dict[str, Any]] = []
        self.financial_opportunities = []
        self.cfo_recommendations: list[dict[str, Any]] = []
        self.executive_decision_intelligence: dict[str, Any] = {}
        self.kpi_dashboard = None
        self.executive_dashboard = None

        # Existing AI-generated CFO report
        self.cfo_report = None

        # Deterministic structured CFO report
        self.structured_cfo_report: dict[str, Any] = {}

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
                enriched_line.get("donor_code") or enriched_line.get("donor") or ""
            ).strip()

            fund_code = str(
                enriched_line.get("fund_code") or enriched_line.get("fund") or ""
            ).strip()

            if not donor_code and derive_funder_from_fund_code and fund_code:
                fund_code_parts = fund_code.split(fund_code_separator)

                if 0 <= funder_code_segment < len(fund_code_parts):
                    derived_donor_code = fund_code_parts[funder_code_segment].strip()

                    if derived_donor_code:
                        enriched_line["donor_code"] = derived_donor_code

            enriched_budget_lines.append(enriched_line)

        self.budget.load_budget(enriched_budget_lines)

        self.budget_summary = generate_budget_summary(enriched_budget_lines)

    def load_needed_budget(
        self,
        needed_budget_lines: list[dict[str, Any]],
    ) -> None:
        """
        Store the organization's normalized annual
        Needed Budget and generate a summary.
        """

        self.needed_budget.load_budget(
            needed_budget_lines
        )

        fiscal_years = sorted(
            {
                line.get("fiscal_year")
                for line in self.needed_budget.lines
                if line.get("fiscal_year") is not None
            }
        )

        review_count = sum(
            bool(
                line.get("requires_review")
            )
            for line in self.needed_budget.lines
        )

        self.needed_budget_summary = {
            "line_count": len(
                self.needed_budget.lines
            ),
            "total_needed_budget": (
                self.needed_budget.total_needed_budget()
            ),
            "fiscal_years": fiscal_years,
            "review_count": review_count,
        }


    def load_expected_funding(
        self,
        expected_funding_lines: list[
            dict[str, Any]
        ],
    ) -> None:
        """
        Store normalized prospective Expected Funding.

        Expected Funding remains separate from secured
        funding and does not modify Budget, Funding Gap,
        revenue, or cash.
        """

        self.expected_funding = [
            dict(line)
            for line in (
                expected_funding_lines or []
            )
            if isinstance(
                line,
                dict,
            )
        ]

    def load_core_cost_coverage(
        self,
        core_cost_coverage_lines: list[
            dict[str, Any]
        ],
    ) -> None:
        """
        Store normalized Core Cost Coverage records.

        Loading preserves source records and does not
        infer, allocate, or recalculate financial coverage.
        """

        self.core_cost_coverage_inputs = [
            dict(line)
            for line in (
                core_cost_coverage_lines or []
            )
            if isinstance(
                line,
                dict,
            )
        ]

    def generate_core_cost_coverage_analysis(
        self,
    ) -> None:
        """
        Generate deterministic Core Cost Coverage &
        Allocation Intelligence.

        Needed core costs come from the normalized
        Needed Budget. Coverage records remain explicit
        and are applied only by their coverage type.
        """

        direct_grant_coverage = [
            line
            for line in self.core_cost_coverage_inputs
            if line.get("coverage_type")
            == "direct_grant_coverage"
        ]

        indirect_recovery_allocations = [
            line
            for line in self.core_cost_coverage_inputs
            if line.get("coverage_type")
            == "indirect_recovery_allocation"
        ]

        unrestricted_core_funding = [
            line
            for line in self.core_cost_coverage_inputs
            if line.get("coverage_type")
            == "unrestricted_core_funding"
        ]

        available_indirect_recovery = [
            line
            for line in self.core_cost_coverage_inputs
            if line.get("coverage_type")
            == "available_indirect_recovery"
        ]

        used_indirect_recovery = [
            line
            for line in self.core_cost_coverage_inputs
            if line.get("coverage_type")
            == "used_indirect_recovery"
        ]

        self.core_cost_coverage = (
            generate_core_cost_coverage(
                needed_core_costs=(
                    self.needed_budget.lines
                ),
                direct_grant_coverage=(
                    direct_grant_coverage
                ),
                indirect_recovery_allocations=(
                    indirect_recovery_allocations
                ),
                unrestricted_core_funding=(
                    unrestricted_core_funding
                ),
                available_indirect_recovery=(
                    available_indirect_recovery
                ),
                used_indirect_recovery=(
                    used_indirect_recovery
                ),
            )
        )

    def generate_expected_funding_analysis(
        self,
    ) -> None:
        """
        Generate deterministic Expected Funding Intelligence
        from prospective funding records.
        """

        self.expected_funding_intelligence = (
            generate_expected_funding_intelligence(
                self.expected_funding
            )
        )


    def generate_needed_budget_analysis(
        self,
    ) -> None:
        """
        Compare the organization's Needed Budget
        against budget-consuming General Ledger actuals.
        """

        if not self.needed_budget.lines:
            raise ValueError(
                "Load the Needed Budget before generating "
                "Needed Budget vs Actual."
            )

        if not self.general_ledger:
            raise ValueError(
                "Load the General Ledger before generating "
                "Needed Budget vs Actual."
            )

        transactions_for_analysis = getattr(
            self,
            "normalized_general_ledger",
            None,
        )

        if not transactions_for_analysis:
            transactions_for_analysis = (
                self.general_ledger
            )

        self.needed_budget_vs_actual = (
            generate_needed_budget_vs_actual(
                needed_budget_lines=(
                    self.needed_budget.lines
                ),
                available_budget_lines=(
                    self.budget.lines
                ),
                transactions=(
                    transactions_for_analysis
                ),
                accounts_by_number=(
                    self.accounts_by_number
                ),
            )
        )


    def generate_funding_gap_analysis(
        self,
    ) -> None:
        """
        Calculate the organization's current Funding Gap
        using Needed Budget, actual spending, remaining
        secured funding, and validated grant periods.
        """

        if not self.needed_budget_vs_actual:
            self.funding_gap = None
            return

        grant_periods = {
            grant_code: {
                "start_date": grant.start_date,
                "end_date": grant.end_date,
            }
            for grant_code, grant in self.grants.items()
        }

        self.funding_gap = generate_funding_gap(
            needed_budget_vs_actual=(
                self.needed_budget_vs_actual
            ),
            available_budget_lines=(
                self.budget.lines
            ),
            budget_vs_actual=(
                self.budget_vs_actual
            ),
            grant_periods=(
                grant_periods
            ),
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
            raise ValueError("Load the Budget before generating Budget vs Actual.")

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

        self.budget_mapping_intelligence = (
            generate_budget_mapping_intelligence(
                budget_lines=self.budget.lines,
                transactions=transactions_for_analysis,
                accounts_by_number=self.accounts_by_number,
            )
        )

        self.budget_dimension_drilldown = (
            generate_budget_dimension_drilldown(
                budget_lines=self.budget.lines,
                transactions=transactions_for_analysis,
                accounts_by_number=self.accounts_by_number,
            )
        )

        self.budget_dashboard = generate_budget_dashboard(
            budget_summary=self.budget_summary,
            budget_vs_actual=self.budget_vs_actual,
            budget_dimension_drilldown=(
                self.budget_dimension_drilldown
            ),
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

            grant_name = str(
                budget_line.get(
                    "fund_name"
                )
                or ""
            ).strip()

            if grant_name:
                grant.name = grant_name

            grant_start_date = str(
                budget_line.get(
                    "grant_start_date"
                )
                or ""
            ).strip()

            grant_end_date = str(
                budget_line.get(
                    "grant_end_date"
                )
                or ""
            ).strip()

            if grant_start_date:
                if (
                    grant.start_date
                    and grant.start_date
                    != grant_start_date
                ):
                    raise ValueError(
                        f"Conflicting grant start dates "
                        f"found for grant {grant_code}: "
                        f"{grant.start_date} and "
                        f"{grant_start_date}."
                    )

                grant.start_date = (
                    grant_start_date
                )

            if grant_end_date:
                if (
                    grant.end_date
                    and grant.end_date
                    != grant_end_date
                ):
                    raise ValueError(
                        f"Conflicting grant end dates "
                        f"found for grant {grant_code}: "
                        f"{grant.end_date} and "
                        f"{grant_end_date}."
                    )

                grant.end_date = (
                    grant_end_date
                )

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

            grant = self.grants.get(grant_code)

            #
            # If this fund was not present in the Budget,
            # determine whether the GL activity belongs to
            # a confirmed real grant.
            #
            if grant is None:

                donor_code = str(
                    transaction.get("donor_code") or transaction.get("donor") or ""
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
                        fund_name=transaction.get("fund_name"),
                        donor_code=transaction.get("donor_code"),
                        donor_name=transaction.get("donor_name"),
                        explicit_fund_type=transaction.get("fund_type"),
                        explicit_is_grant=transaction.get("is_grant"),
                    )

                    is_grant = fund_classification.get("is_grant") is True

                #
                # Do not convert unknown or non-grant funds
                # into Grant objects.
                #
                if not is_grant:
                    continue

                grant = Grant()
                grant.code = grant_code

                grant_name = str(transaction.get("fund_name") or "").strip()

                if grant_name:
                    grant.name = grant_name

                self.grants[grant_code] = grant

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
            funding_gap=self.funding_gap,
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

        Cash Flow:
        {self.cash_flow}

        Financial Health:
        {self.financial_health}

        Budget Dashboard:
        {self.budget_dashboard}

        Funding Gap:
        {self.funding_gap}

        Risk Assessment:
        {self.risk_assessment}

        CFO Recommendations:
        {self.cfo_recommendations}

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

        standard_income_statement_transactions = filter_transactions(
            transactions=self.normalized_general_ledger,
            start_date=start_date,
            end_date=end_date,
        )

        self.standard_income_statement = (
            generate_standard_income_statement(
                transactions=period_transactions,
                accounts_by_number=self.accounts_by_number,
                validated_income_statement=self.income_statement,
            )
        )

        self.balance_sheet = generate_balance_sheet(

            trial_balance=self.trial_balance,
            accounts_by_number=self.accounts_by_number,
            current_period_result=self.income_statement.get(
                "current_period_result",
                0,
            ),
        )

        self.standard_balance_sheet = (
            generate_standard_balance_sheet(
                trial_balance=self.trial_balance,
                accounts_by_number=self.accounts_by_number,
                validated_balance_sheet=self.balance_sheet,
            )
        )

        self.cash_flow = generate_cash_flow_statement(
            period_transactions,
            self.trial_balance,
            self.accounts_by_number,
        )

        self.standard_cash_flow_statement = (
            generate_standard_cash_flow_statement(
                cash_flow=self.cash_flow,
            )
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

        self.financial_trends = generate_financial_trends(
            transactions=period_transactions,
            accounts_by_number=self.accounts_by_number,
        )

        self.financial_forecast = generate_financial_forecast(
            financial_trends=self.financial_trends,
        )

    def run_financial_scenario(
        self,
        *,
        scenario_name: str = "Custom Scenario",
        revenue_change_percentage: float = 0.0,
        expense_change_percentage: float = 0.0,
        one_time_revenue_adjustment: float = 0.0,
        one_time_expense_adjustment: float = 0.0,
        cash_inflow_adjustment: float = 0.0,
        cash_outflow_adjustment: float = 0.0,
    ) -> dict[str, Any]:
        """
        Run an explicit financial what-if scenario.

        Scenarios are generated only when assumptions are
        supplied by the user or another AI-FOS workflow.

        The validated baseline financial forecast is never
        modified.
        """
        self.financial_scenario = generate_financial_scenario(
            financial_forecast=self.financial_forecast,
            liquidity=self.liquidity,
            scenario_name=scenario_name,
            revenue_change_percentage=(
                revenue_change_percentage
            ),
            expense_change_percentage=(
                expense_change_percentage
            ),
            one_time_revenue_adjustment=(
                one_time_revenue_adjustment
            ),
            one_time_expense_adjustment=(
                one_time_expense_adjustment
            ),
            cash_inflow_adjustment=(
                cash_inflow_adjustment
            ),
            cash_outflow_adjustment=(
                cash_outflow_adjustment
            ),
        )

        self.scenario_decision_intelligence = (
            generate_scenario_decision_intelligence(
                self.financial_scenario
            )
        )

        return self.financial_scenario

    def compare_financial_scenarios(
        self,
        scenario_a: dict[str, Any],
        scenario_b: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Compare two existing financial scenario decision
        intelligence outputs.

        This method does not rerun financial scenarios and
        does not modify either source scenario.
        """

        self.scenario_comparison_intelligence = (
            generate_scenario_comparison_intelligence(
                scenario_a,
                scenario_b,
            )
        )

        return self.scenario_comparison_intelligence

    def run_funding_scenario(
        self,
        *,
        scenario_name: str = "Funding Scenario",
        expected_funding_change_percentage: float = 0.0,
        failed_expected_funding_codes: list[str] | None = None,
        scenario_basis: str = "most_likely",
    ) -> dict[str, Any]:
        """
        Run an explicit Expected Funding what-if scenario.

        Funding scenarios consume only validated Expected
        Funding Intelligence.

        They do not modify:
        - secured funding;
        - Funding Gap;
        - revenue;
        - cash;
        - the validated Expected Funding baseline.
        """

        self.funding_scenario = generate_funding_scenario(
            expected_funding_intelligence=(
                self.expected_funding_intelligence
            ),
            scenario_name=scenario_name,
            expected_funding_change_percentage=(
                expected_funding_change_percentage
            ),
            failed_expected_funding_codes=(
                failed_expected_funding_codes
            ),
            scenario_basis=scenario_basis,
        )

        return self.funding_scenario

    def calculate_financial_health(
        self,
    ) -> None:
        """
        Calculate the organisation's Financial Health Score.

        Funding Gap intelligence is included so financial
        health reflects validated secured-funding coverage,
        not gross funding availability alone.
        """

        self.financial_health = (
            calculate_financial_health(
                income_statement=(
                    self.income_statement
                ),
                balance_sheet=(
                    self.balance_sheet
                ),
                budget_dashboard=(
                    self.budget_dashboard
                ),
                grant_diagnostics=(
                    self.grant_diagnostics
                ),
                liquidity=(
                    self.liquidity
                ),
                funding_gap=(
                    self.funding_gap
                ),

                budget_mapping_intelligence=(
                    self.budget_mapping_intelligence
                ),

            )
        )

    def build_risk_assessment(self) -> None:
        """
        Build the organisation's CFO Risk Register.
        """

        self.risk_assessment = generate_risk_assessment(
            income_statement=self.income_statement,
            balance_sheet=self.balance_sheet,
            liquidity=self.liquidity,
            financial_health=self.financial_health,
            budget_dashboard=self.budget_dashboard,
            grant_diagnostics=self.grant_diagnostics,
            funding_gap=self.funding_gap,
        )

    def build_forward_risks(self) -> None:
        """
        Build evidence-based forward-looking financial risks.

        Forward-looking risks remain separate from the current
        CFO Risk Register and consume only validated AI-FOS
        outputs.
        """

        self.forward_risks = generate_forward_risks(
            risk_assessment=self.risk_assessment,
            financial_trends=self.financial_trends,
            financial_forecast=self.financial_forecast,
            liquidity=self.liquidity,
            funding_gap=self.funding_gap,
            grant_diagnostics=self.grant_diagnostics,
        )

    def build_financial_opportunities(self) -> None:
        """
        Build evidence-based financial opportunities.

        Financial opportunities remain separate from current
        risks and forward-looking risks and consume only
        validated AI-FOS outputs.
        """

        self.financial_opportunities = (
            generate_financial_opportunities(
                financial_trends=self.financial_trends,
                financial_forecast=self.financial_forecast,
                liquidity=self.liquidity,
                funding_gap=self.funding_gap,
                budget_dashboard=self.budget_dashboard,
                grant_diagnostics=self.grant_diagnostics,
            )
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
            financial_opportunities=self.financial_opportunities,
            forward_risks=self.forward_risks,
            budget_dashboard=self.budget_dashboard,
            grant_diagnostics=self.grant_diagnostics,
            funding_gap=self.funding_gap,
        )

    def build_executive_decision_intelligence(
        self,
    ) -> None:
        """
        Build deterministic Executive Decision Intelligence.

        This layer prioritizes existing verified AI-FOS risks,
        forward-looking risks, CFO recommendations, and financial
        opportunities for executive management attention.

        It does not recalculate validated financial outputs.
        """

        self.executive_decision_intelligence = (
            generate_executive_decision_intelligence(
                risk_assessment=self.risk_assessment,
                forward_risks=self.forward_risks,
                cfo_recommendations=self.cfo_recommendations,
                financial_opportunities=self.financial_opportunities,
            )
        )

    def build_structured_cfo_report(self) -> None:
        """
        Build the deterministic structured AI-FOS CFO Report.

        This report consumes validated financial intelligence
        outputs and remains separate from the existing AI-written
        CFO report.
        """

        self.structured_cfo_report = build_structured_cfo_report(
            financial_health=self.financial_health,
            liquidity=self.liquidity,
            budget_dashboard=self.budget_dashboard,
            funding_gap=self.funding_gap,
            grant_diagnostics=self.grant_diagnostics,
            risk_assessment=self.risk_assessment,
            forward_risks=self.forward_risks,
            financial_opportunities=self.financial_opportunities,
            cfo_recommendations=self.cfo_recommendations,
            financial_trends=self.financial_trends,
            financial_forecast=self.financial_forecast,
            core_cost_coverage=self.core_cost_coverage,
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
