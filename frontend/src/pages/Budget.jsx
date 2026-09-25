import {
    useEffect,
    useRef,
    useState,
} from "react";
import { useNavigate } from "react-router-dom";

const navItems = [
  "Dashboard",
  "Financial Health",
  "Financial History",
  "AI CFO",
  "Action Center",
  "Budget",
  "Grants",
  "Projects",
  "Reports",
  "Settings",
];

const budgetDimensions = [
    {
        key: "fund",
        label: "Fund",
        viewKey: "by_fund",
        codeKey: "fund_code",
        nameKey: "fund_name",
    },
    {
        key: "donor",
        label: "Donor",
        viewKey: "by_donor",
        codeKey: "donor_code",
        nameKey: "donor_name",
    },
    {
        key: "program",
        label: "Program",
        viewKey: "by_program",
        codeKey: "program_code",
        nameKey: "program_name",
    },
    {
        key: "project",
        label: "Project",
        viewKey: "by_project",
        codeKey: "project_code",
        nameKey: "project_name",
    },
    {
        key: "category",
        label: "Category",
        viewKey: "by_category",
        codeKey: "category_code",
        nameKey: "category_name",
    },
    {
        key: "budget_line",
        label: "Budget Line",
        viewKey: "by_budget_line",
        codeKey: "budget_line_code",
        nameKey: "budget_line_name",
    },
    {
        key: "donor_line",
        label: "Donor Line",
        viewKey: "by_donor_line",
        codeKey: "donor_line_code",
        nameKey: "donor_line_name",
    },
];

function formatCurrency(value) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "--";
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "--";
    }

    return new Intl.NumberFormat("en-US", {
        style: "currency",
        currency: "USD",
        maximumFractionDigits: 0,
    }).format(number);
}

function formatPercent(value) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "--";
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "--";
    }

    return `${number.toFixed(2)}%`;
}

function formatCount(value) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "--";
    }

    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "--";
    }

    return number.toLocaleString("en-US");
}

function Budget({
    budget,
    coreCostCoverage,
    readiness,
    organizationList,
    currentOrganization,
    setCurrentOrganization,
}) {
    const navigate = useNavigate();

    const [selectedDimension, setSelectedDimension] =
        useState("fund");

    const [
        selectedDrilldownRecord,
        setSelectedDrilldownRecord,
    ] = useState(null);

    const [
        selectedDrilldownDimension,
        setSelectedDrilldownDimension,
    ] = useState(null);

    const drilldownSectionRef =
        useRef(null);

    const summary =
        budget?.executive_summary ?? {};

    const health =
        budget?.budget_health ?? {};

    const organization =
        budget?.organization ?? {};

    const portfolio =
        budget?.portfolio_control ?? {};

    const coreCostSummary =
        coreCostCoverage?.summary ?? {};

    const coreCostLines =
        coreCostCoverage?.lines ?? [];

    const coreCostControls =
        coreCostCoverage?.controls ?? {};  
        
    const hasCoreCostCoverage =
        coreCostCoverage?.status === "available";        

    const totalBudget =
        portfolio.total_budget ??
        summary.total_budget;

    const totalActual =
        portfolio.total_actual ??
        summary.total_actual;

    const budgetedActual =
        portfolio.budgeted_actual ??
        summary.budgeted_actual;

    const unbudgetedActual =
        portfolio.unbudgeted_actual ??
        summary.unbudgeted_actual;

    const utilization =
        portfolio.utilization_percentage ??
        summary.utilization_percentage ??
        budget?.utilization_percentage;

    const overallVariance =
        portfolio.overall_variance_including_unbudgeted ??
        summary.overall_variance_including_unbudgeted;

    const overBudgetCount =
        portfolio.over_budget_count ??
        health.over_budget_count;

    const withinBudgetCount =
        portfolio.within_budget_count ??
        health.within_budget_count;

    const noBudgetCount =
        portfolio.no_budget_count ??
        health.no_budget_count;

    const budgetLineCount =
        portfolio.budget_line_count ??
        health.budget_line_count;

    const fiscalYears =
        budget?.by_fiscal_year?.lines ?? [];

    const availableDimensions =
        budgetDimensions.filter(
            (dimension) => {
                const lines =
                    budget?.[
                        dimension.viewKey
                    ]?.lines ?? [];

                return lines.length > 0;
            }
        );

    const activeDimension =
        availableDimensions.find(
            (dimension) =>
                dimension.key ===
                selectedDimension
        ) ??
        availableDimensions[0] ??
        null;

    const dimensionLines =
        activeDimension
            ? budget?.[
                activeDimension.viewKey
            ]?.lines ?? []
            : [];

    const dimensionIntelligence =
        activeDimension
            ? budget?.dimension_intelligence?.[
            activeDimension.key
            ] ?? null
            : null;

    const priorityItems =
        dimensionIntelligence?.priority_items ??
        [];

    const dimensionDrilldown =
        activeDimension
            ? budget?.dimension_drilldown?.[
            activeDimension.key
            ] ?? null
            : null;

    const drilldownRecords =
        dimensionDrilldown?.records ?? [];

    const activeDrilldownRecord =
        selectedDrilldownRecord
            ? drilldownRecords.find(
                (record) =>
                    record.code ===
                    selectedDrilldownRecord
            ) ?? null
            : null;

    const drilldownViews =
        activeDrilldownRecord?.drilldown ?? {};

    const availableDrilldownDimensions =
        Object.keys(drilldownViews);

    const activeDrilldownDimension =
        selectedDrilldownDimension &&
            drilldownViews[
            selectedDrilldownDimension
            ]
            ? selectedDrilldownDimension
            : availableDrilldownDimensions[0] ??
            null;

    const activeDrilldownView =
        activeDrilldownDimension
            ? drilldownViews[
            activeDrilldownDimension
            ]
            : null;

    const activeDrilldownLines =
        activeDrilldownView?.lines ?? [];

    useEffect(() => {
        if (
            !activeDrilldownRecord ||
            !drilldownSectionRef.current
        ) {
            return;
        }

        drilldownSectionRef.current.scrollIntoView({
            behavior: "smooth",
            block: "start",
        });
    }, [activeDrilldownRecord]);

    function handleNavigation(item) {
        if (item === "Dashboard") {
            navigate("/dashboard");
            return;
        }

        if (item === "Financial Health") {
            navigate("/financial-health");
            return;
        }

        if (item === "AI CFO") {
            navigate("/ai-cfo");
            return;
        }

        if (item === "Action Center") {
        navigate("/action-center");
        return;
        }        

        if (item === "Budget") {
            navigate("/budget");
            return;
        }

        if (item === "Grants") {
            navigate("/grants");
            return;
        }

        if (item === "Projects") {
            navigate("/projects");
            return;
        }

        if (item === "Reports") {
            navigate("/reports");
            return;
        }

        if (item === "Settings") {
            navigate("/settings");
        }
    }

    function handleOrganizationChange(
        event
    ) {
        const selected =
            organizationList.find(
                (organizationItem) =>
                    organizationItem.id ===
                    event.target.value
            );

        if (selected) {
            setCurrentOrganization(selected);
        }
    }

    return (
        <div className="budget-page">
            <aside className="sidebar">
                <div className="brand">
                    <div className="brand-mark">
                        AF
                    </div>

                    <div>
                        <h1>AI-FOS</h1>

                        <p>
                            Financial Intelligence
                        </p>
                    </div>
                </div>

                <nav className="sidebar-nav">
                    {navItems.map(
                        (item) => (
                            <button
                                key={item}
                                type="button"
                                className={
                                    item ===
                                        "Budget"
                                        ? "nav-item active"
                                        : "nav-item"
                                }
                                onClick={() =>
                                    handleNavigation(
                                        item
                                    )
                                }
                            >
                                {item}
                            </button>
                        )
                    )}
                </nav>
            </aside>

            <main className="budget-main">
                <header className="budget-header">
                    <div>
                        <p className="page-eyebrow">
                            Financial intelligence
                        </p>

                        <h1>Budget</h1>

                        <p className="page-subtitle">
                            Organization:{" "}
                            {currentOrganization?.name ??
                                "Organization"}
                        </p>
                    </div>

                    <div className="budget-header-actions">
                        <select
                            value={
                                currentOrganization?.id ??
                                "acss"
                            }
                            onChange={
                                handleOrganizationChange
                            }
                            className="organization-select"
                        >
                            {organizationList.map(
                                (
                                    organizationItem
                                ) => (
                                    <option
                                        key={
                                            organizationItem.id
                                        }
                                        value={
                                            organizationItem.id
                                        }
                                    >
                                        {
                                            organizationItem.name
                                        }
                                    </option>
                                )
                            )}
                        </select>

                        <div className="user-avatar">
                            ER
                        </div>
                    </div>
                </header>



                {readiness &&
                    !readiness.has_budget && (
                        <section className="budget-section-card">
                            <div className="budget-section-heading">
                                <div>
                                    <p className="section-eyebrow">
                                        Organization
                                        readiness
                                    </p>

                                    <h2>
                                        Budget
                                        Intelligence
                                        not available
                                        yet
                                    </h2>
                                </div>
                            </div>

                            <p>
                                {currentOrganization?.name ??
                                    "This organization"}{" "}
                                does not yet have
                                validated budget data
                                available in AI-FOS.
                            </p>

                            <p>
                                Upload and process
                                the organization&apos;s
                                budget and financial
                                data to activate
                                Budget Intelligence.
                            </p>
                        </section>
                    )}

                {readiness?.has_budget && (
                    <>
                        <section className="budget-intro">
                            <p className="section-eyebrow">
                                Budget intelligence
                            </p>

                            <h2>
                                Budget Control
                                Overview
                            </h2>

                            <p>
                                Monitor budget
                                utilization, spending
                                control and unbudgeted
                                financial activity
                                from the validated
                                AI-FOS Budget vs
                                Actual engine.
                            </p>
                        </section>

                        <section className="budget-kpi-grid">
                            <article className="budget-kpi-card">
                                <span>
                                    Total Budget
                                </span>

                                <strong>
                                    {formatCurrency(
                                        totalBudget
                                    )}
                                </strong>

                                <small>
                                    Validated portfolio
                                    budget
                                </small>
                            </article>

                            <article className="budget-kpi-card">
                                <span>
                                    Total Actual
                                </span>

                                <strong>
                                    {formatCurrency(
                                        totalActual
                                    )}
                                </strong>

                                <small>
                                    Total recorded
                                    spending
                                </small>
                            </article>

                            <article className="budget-kpi-card">
                                <span>
                                    Budget Utilization
                                </span>

                                <strong>
                                    {formatPercent(
                                        utilization
                                    )}
                                </strong>

                                <div className="budget-progress">
                                    <div
                                        className="budget-progress-fill"
                                        style={{
                                            width: `${Math.min(
                                                Math.max(
                                                    Number(
                                                        utilization
                                                    ) ||
                                                    0,
                                                    0
                                                ),
                                                100
                                            )}%`,
                                        }}
                                    />
                                </div>
                            </article>

                            <article className="budget-kpi-card budget-kpi-alert">
                                <span>
                                    Unbudgeted Actual
                                </span>

                                <strong>
                                    {formatCurrency(
                                        unbudgetedActual
                                    )}
                                </strong>

                                <small>
                                    Actual activity
                                    without identified
                                    budget
                                </small>
                            </article>
                        </section>

                        <section className="budget-section-card">
                            <div className="budget-section-heading">
                                <div>
                                    <p className="section-eyebrow">
                                        Control status
                                    </p>

                                    <h2>
                                        Budget Status
                                    </h2>
                                </div>

                                <span className="budget-line-total">
                                    {formatCount(
                                        budgetLineCount
                                    )}{" "}
                                    budget lines
                                </span>
                            </div>

                            <div className="budget-status-grid">
                                <article className="budget-status-card status-over">
                                    <strong>
                                        {formatCount(
                                            overBudgetCount
                                        )}
                                    </strong>

                                    <span>
                                        Over Budget
                                    </span>

                                    <p>
                                        Budget lines
                                        requiring
                                        management
                                        attention.
                                    </p>
                                </article>

                                <article className="budget-status-card status-within">
                                    <strong>
                                        {formatCount(
                                            withinBudgetCount
                                        )}
                                    </strong>

                                    <span>
                                        Within Budget
                                    </span>

                                    <p>
                                        Budget lines
                                        currently within
                                        approved limits.
                                    </p>
                                </article>

                                <article className="budget-status-card status-none">
                                    <strong>
                                        {formatCount(
                                            noBudgetCount
                                        )}
                                    </strong>

                                    <span>
                                        No Budget
                                    </span>

                                    <p>
                                        Actual activity
                                        with no
                                        identified
                                        budget.
                                    </p>
                                </article>
                            </div>
                        </section>

                        <section className="budget-two-column">
                            <article className="budget-section-card">
                                <div className="budget-section-heading">
                                    <div>
                                        <p className="section-eyebrow">
                                            Spending
                                            control
                                        </p>

                                        <h2>
                                            Portfolio
                                            Control
                                        </h2>
                                    </div>
                                </div>

                                <div className="budget-detail-list">
                                    <div>
                                        <span>
                                            Budgeted
                                            Actual
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                budgetedActual
                                            )}
                                        </strong>
                                    </div>

                                    <div>
                                        <span>
                                            Unbudgeted
                                            Actual
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                unbudgetedActual
                                            )}
                                        </strong>
                                    </div>

                                    <div>
                                        <span>
                                            Overall
                                            Variance
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                overallVariance
                                            )}
                                        </strong>
                                    </div>

                                    <div>
                                        <span>
                                            Utilization
                                        </span>

                                        <strong>
                                            {formatPercent(
                                                utilization
                                            )}
                                        </strong>
                                    </div>
                                </div>
                            </article>

                            <article className="budget-section-card">
                                <div className="budget-section-heading">
                                    <div>
                                        <p className="section-eyebrow">
                                            Portfolio
                                            dimensions
                                        </p>

                                        <h2>
                                            Budget
                                            Coverage
                                        </h2>
                                    </div>
                                </div>

                                <div className="budget-coverage-grid">
                                    <div>
                                        <strong>
                                            {formatCount(
                                                organization.fund_count
                                            )}
                                        </strong>

                                        <span>
                                            Funds
                                        </span>
                                    </div>

                                    <div>
                                        <strong>
                                            {formatCount(
                                                organization.donor_count
                                            )}
                                        </strong>

                                        <span>
                                            Donors
                                        </span>
                                    </div>

                                    <div>
                                        <strong>
                                            {formatCount(
                                                organization.program_count
                                            )}
                                        </strong>

                                        <span>
                                            Programs
                                        </span>
                                    </div>

                                    <div>
                                        <strong>
                                            {formatCount(
                                                organization.project_count
                                            )}
                                        </strong>

                                        <span>
                                            Projects
                                        </span>
                                    </div>
                                </div>
                            </article>
                        </section>

                        <section className="budget-section-card">
                            <div className="budget-section-heading">
                                <div>
                                    <p className="section-eyebrow">
                                        Core funding intelligence
                                    </p>

                                    <h2>
                                        Core Cost Coverage
                                    </h2>
                                </div>
                            </div>

                            {!hasCoreCostCoverage ? (
                                <p className="budget-empty-state">
                                    Core Cost Coverage intelligence is not available yet.
                                </p>
                            ) : (
                                <>
                                    <div className="budget-kpi-grid">
                                    <article className="budget-kpi-card">
                                        <span>
                                            Needed Core Cost
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                coreCostSummary.needed_core_cost
                                            )}
                                        </strong>

                                        <small>
                                            Total identified core cost requirement
                                        </small>
                                    </article>  
                                    <article className="budget-kpi-card">
                                        <span>
                                            Direct Grant Coverage
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                coreCostSummary.direct_grant_coverage
                                            )}
                                        </strong>

                                        <small>
                                            Core costs covered directly by grants
                                        </small>
                                    </article>  
                                    <article className="budget-kpi-card">
                                        <span>
                                            Available Indirect Recovery
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                coreCostSummary.available_indirect_recovery
                                            )}
                                        </strong>

                                        <small>
                                            Recovered and available for management allocation
                                        </small>
                                    </article>  
                                    <article className="budget-kpi-card">
                                        <span>
                                            Allocated Indirect Recovery
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                coreCostSummary.allocated_indirect_recovery
                                            )}
                                        </strong>

                                        <small>
                                            Indirect recovery allocated by management
                                        </small>
                                    </article> 
                                    <article className="budget-kpi-card">
                                        <span>
                                            Used Indirect Recovery
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                coreCostSummary.used_indirect_recovery
                                            )}
                                        </strong>

                                        <small>
                                            Indirect recovery actually used or charged
                                        </small>
                                    </article> 
                                    <article className="budget-kpi-card">
                                        <span>
                                            Other Core Funding
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                coreCostSummary.unrestricted_core_funding
                                            )}
                                        </strong>

                                        <small>
                                            Unrestricted or other core funding coverage
                                        </small>
                                    </article>
                                    <article className="budget-kpi-card budget-kpi-alert">
                                        <span>
                                            Remaining Core Cost Gap
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                coreCostSummary.remaining_core_cost_gap
                                            )}
                                        </strong>

                                        <small>
                                            Core cost requirement still uncovered
                                        </small>
                                    </article>   
                                    <article className="budget-kpi-card">
                                        <span>
                                            Core Cost Coverage
                                        </span>

                                        <strong>
                                            {formatPercent(
                                                coreCostSummary.core_cost_coverage_percentage
                                            )}
                                        </strong>

                                        <small>
                                            Share of identified core costs currently covered
                                        </small>
                                    </article>                                                                                                                                                                                                                                                                                     
                                </div>
                                            {coreCostLines.length > 0 && (
                                        <div className="budget-table-wrap">
                                            <table className="budget-table">
                                                <thead>
                                                    <tr>
                                                        <th>Budget Line</th>
                                                        <th>Employee / Responsible</th>
                                                        <th>Fiscal Year</th>
                                                        <th>Needed Core Cost</th>
                                                        <th>Direct Grant Coverage</th>
                                                        <th>Allocated Indirect Recovery</th>
                                                        <th>Other Core Funding</th>
                                                        <th>Remaining Gap</th>
                                                    </tr>
                                                </thead>
                                                <tbody>
                                                    {coreCostLines.map(
                                                        (line, index) => (
                                                            <tr
                                                                key={
                                                                    line.budget_line_code ??
                                                                    index
                                                                }
                                                            >
                                                                <td>
                                                                    {line.budget_line_name ??
                                                                        line.budget_line_code ??
                                                                        "—"}
                                                                </td>

                                                                <td>
                                                                    {line.employee_responsible ??
                                                                        "—"}
                                                                </td>

                                                                <td>
                                                                    {line.fiscal_year ??
                                                                        "—"}
                                                                </td>

                                                                <td>
                                                                    {formatCurrency(
                                                                        line.needed_core_cost
                                                                    )}
                                                                </td>

                                                                <td>
                                                                    {formatCurrency(
                                                                        line.direct_grant_coverage
                                                                    )}
                                                                </td>

                                                                <td>
                                                                    {formatCurrency(
                                                                        line.allocated_indirect_recovery
                                                                    )}
                                                                </td>

                                                                <td>
                                                                    {formatCurrency(
                                                                        line.unrestricted_core_funding
                                                                    )}
                                                                </td>

                                                                <td>
                                                                    {formatCurrency(
                                                                        line.remaining_core_cost_gap
                                                                    )}
                                                                </td>
                                                            </tr>
                                                        )
                                                    )}
                                                </tbody>                                                
                                            </table>
                                        </div>
                                    )}                        
                                    {(coreCostControls.used_indirect_recovery_exceeds_allocation ||
                                        coreCostControls.allocated_indirect_recovery_exceeds_available ||
                                        coreCostControls.total_core_cost_coverage_exceeds_need) && (
                                        <div className="budget-status-grid">
                                            {coreCostControls.used_indirect_recovery_exceeds_allocation && (
                                                <article className="budget-status-card status-over">
                                                    <strong>
                                                        {formatCurrency(
                                                            coreCostControls.used_indirect_recovery_over_allocation_amount
                                                        )}
                                                    </strong>

                                                    <span>
                                                        Used Indirect Recovery Exceeds Allocation
                                                    </span>

                                                    <p>
                                                        Actual indirect recovery used or charged exceeds the amount allocated by management.
                                                    </p>
                                                </article>
                                            )} 
                                    {coreCostControls.allocated_indirect_recovery_exceeds_available && (
                                        <article className="budget-status-card status-over">
                                            <strong>
                                                {formatCurrency(
                                                    coreCostControls.allocated_indirect_recovery_over_available_amount
                                                )}
                                            </strong>

                                            <span>
                                                Allocated Indirect Recovery Exceeds Available
                                            </span>

                                            <p>
                                                Management-allocated indirect recovery exceeds the amount currently available.
                                            </p>
                                        </article>
                                    )}
                                    {coreCostControls.total_core_cost_coverage_exceeds_need && (
                                        <article className="budget-status-card status-over">
                                            <strong>
                                                {formatCurrency(
                                                    coreCostControls.total_core_cost_coverage_over_need_amount
                                                )}
                                            </strong>

                                            <span>
                                                Total Core Cost Coverage Exceeds Need
                                            </span>

                                            <p>
                                                Recorded core cost coverage exceeds the identified core cost requirement.
                                            </p>
                                        </article>
                                    )}                                                                                                                       
                                        </div>
                                    )}                                
                                </>    
                            )}
                        </section> 
 
                        <section className="budget-section-card">
                            <div className="budget-section-heading">
                                <div>
                                    <p className="section-eyebrow">
                                        Period analysis
                                    </p>

                                    <h2>
                                        Fiscal Year View
                                    </h2>
                                </div>
                            </div>

                            {fiscalYears.length >
                                0 ? (
                                <div className="budget-table-wrap">
                                    <table className="budget-table">
                                        <thead>
                                            <tr>
                                                <th>
                                                    Fiscal
                                                    Year
                                                </th>

                                                <th>
                                                    Budget
                                                </th>

                                                <th>
                                                    Spending
                                                    Plan
                                                </th>

                                                <th>
                                                    Actual
                                                </th>

                                                <th>
                                                    Variance
                                                </th>

                                                <th>
                                                    Utilization
                                                </th>

                                                <th>
                                                    Status
                                                </th>
                                            </tr>
                                        </thead>

                                        <tbody>
                                            {fiscalYears.map(
                                                (
                                                    year,
                                                    index
                                                ) => (
                                                    <tr
                                                        key={
                                                            year.fiscal_year ??
                                                            index
                                                        }
                                                    >
                                                        <td>
                                                            <strong>
                                                                {year.fiscal_year ??
                                                                    "--"}
                                                            </strong>
                                                        </td>

                                                        <td>
                                                            {formatCurrency(
                                                                year.budget
                                                            )}
                                                        </td>

                                                        <td>
                                                            {formatCurrency(
                                                                year.spending_plan
                                                            )}
                                                        </td>

                                                        <td>
                                                            {formatCurrency(
                                                                year.actual
                                                            )}
                                                        </td>

                                                        <td>
                                                            {formatCurrency(
                                                                year.variance
                                                            )}
                                                        </td>

                                                        <td>
                                                            {formatPercent(
                                                                year.utilization_percentage
                                                            )}
                                                        </td>

                                                        <td>
                                                            <span className="budget-table-status">
                                                                {year.status ??
                                                                    "--"}
                                                            </span>
                                                        </td>
                                                    </tr>
                                                )
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <p className="budget-empty">
                                    No fiscal-year
                                    budget analysis is
                                    currently available.
                                </p>
                            )}
                        </section>

                        <section className="budget-section-card">
                            <div className="budget-section-heading">
                                <div>
                                    <p className="section-eyebrow">
                                        Dimension
                                        analysis
                                    </p>

                                    <h2>
                                        {activeDimension
                                            ? `${activeDimension.label} Analysis`
                                            : "Budget Analysis"}
                                    </h2>
                                </div>

                                <span className="budget-line-total">
                                    {formatCount(
                                        dimensionLines.length
                                    )}{" "}
                                    {activeDimension
                                        ? activeDimension.label.toLowerCase()
                                        : "dimension"}{" "}
                                    {dimensionLines.length ===
                                        1
                                        ? "record"
                                        : "records"}
                                </span>
                            </div>

                            {availableDimensions.length >
                                0 && (
                                    <div className="budget-dimension-selector">
                                        {availableDimensions.map(
                                            (
                                                dimension
                                            ) => (
                                                <button
                                                    key={
                                                        dimension.key
                                                    }
                                                    type="button"
                                                    className={
                                                        activeDimension?.key ===
                                                            dimension.key
                                                            ? "budget-dimension-button active"
                                                            : "budget-dimension-button"
                                                    }
                                                    onClick={() => {
                                                        setSelectedDimension(
                                                            dimension.key
                                                        );

                                                        setSelectedDrilldownRecord(
                                                            null
                                                        );

                                                        setSelectedDrilldownDimension(
                                                            null
                                                        );
                                                    }}
                                                >
                                                    {
                                                        dimension.label
                                                    }
                                                </button>
                                            )
                                        )}
                                    </div>
                                )}

                            {dimensionIntelligence && (
                                <div className="budget-dimension-intelligence">
                                    <article className="budget-intelligence-card">
                                        <span>
                                            Over Budget
                                        </span>

                                        <strong>
                                            {formatCount(
                                                dimensionIntelligence.over_budget_count
                                            )}
                                        </strong>

                                        <small>
                                            {activeDimension?.label ??
                                                "Dimension"}{" "}
                                            records above
                                            budget
                                        </small>
                                    </article>

                                    <article className="budget-intelligence-card">
                                        <span>
                                            No Budget
                                            Exposure
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                dimensionIntelligence.no_budget_actual
                                            )}
                                        </strong>

                                        <small>
                                            {formatCount(
                                                dimensionIntelligence.no_budget_count
                                            )}{" "}
                                            record(s) with
                                            actual spending
                                        </small>
                                    </article>

                                    <article className="budget-intelligence-card">
                                        <span>
                                            Largest
                                            Unfavorable
                                            Variance
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                dimensionIntelligence
                                                    .largest_unfavorable_variance
                                                    ?.variance
                                            )}
                                        </strong>

                                        <small>
                                            {dimensionIntelligence
                                                .largest_unfavorable_variance
                                                ?.name ??
                                                dimensionIntelligence
                                                    .largest_unfavorable_variance
                                                    ?.code ??
                                                "--"}
                                        </small>
                                    </article>

                                    <article className="budget-intelligence-card">
                                        <span>
                                            Highest
                                            Utilization
                                        </span>

                                        <strong>
                                            {formatPercent(
                                                dimensionIntelligence
                                                    .highest_utilization
                                                    ?.utilization_percentage
                                            )}
                                        </strong>

                                        <small>
                                            {dimensionIntelligence
                                                .highest_utilization
                                                ?.name ??
                                                dimensionIntelligence
                                                    .highest_utilization
                                                    ?.code ??
                                                "--"}
                                        </small>
                                    </article>
                                </div>
                            )}

                            {priorityItems.length >
                                0 && (
                                    <div className="budget-priority-section">
                                        <div className="budget-priority-heading">
                                            <div>
                                                <p className="section-eyebrow">
                                                    Management
                                                    attention
                                                </p>

                                                <h3>
                                                    Priority
                                                    Items
                                                </h3>
                                            </div>

                                            <span className="budget-line-total">
                                                {formatCount(
                                                    priorityItems.length
                                                )}{" "}
                                                priority
                                                {priorityItems.length ===
                                                    1
                                                    ? " item"
                                                    : " items"}
                                            </span>
                                        </div>

                                        <div className="budget-priority-grid">
                                            {priorityItems.map(
                                                (
                                                    item,
                                                    index
                                                ) => (
                                                    <article
                                                        className="budget-priority-card"
                                                        key={`${activeDimension?.key ?? "dimension"}-${item.code ?? index}-${index}`}
                                                    >
                                                        <div className="budget-priority-card-header">
                                                            <div>
                                                                <strong>
                                                                    {item.name ??
                                                                        item.code ??
                                                                        "--"}
                                                                </strong>

                                                                {item.name &&
                                                                    item.code && (
                                                                        <small>
                                                                            {
                                                                                item.code
                                                                            }
                                                                        </small>
                                                                    )}
                                                            </div>

                                                            <span className="budget-table-status">
                                                                {item.status ??
                                                                    "--"}
                                                            </span>
                                                        </div>

                                                        <div className="budget-priority-metrics">
                                                            <div>
                                                                <span>
                                                                    Budget
                                                                </span>

                                                                <strong>
                                                                    {formatCurrency(
                                                                        item.budget
                                                                    )}
                                                                </strong>
                                                            </div>

                                                            <div>
                                                                <span>
                                                                    Actual
                                                                </span>

                                                                <strong>
                                                                    {formatCurrency(
                                                                        item.actual
                                                                    )}
                                                                </strong>
                                                            </div>

                                                            <div>
                                                                <span>
                                                                    Variance
                                                                </span>

                                                                <strong>
                                                                    {formatCurrency(
                                                                        item.variance
                                                                    )}
                                                                </strong>
                                                            </div>

                                                            <div>
                                                                <span>
                                                                    Utilization
                                                                </span>

                                                                <strong>
                                                                    {formatPercent(
                                                                        item.utilization_percentage
                                                                    )}
                                                                </strong>
                                                            </div>
                                                        </div>
                                                    </article>
                                                )
                                            )}
                                        </div>
                                    </div>
                                )}

                            {activeDimension &&
                                dimensionLines.length >
                                0 ? (
                                <div className="budget-table-wrap">
                                    <table className="budget-table">
                                        <thead>
                                            <tr>
                                                <th>
                                                    {
                                                        activeDimension.label
                                                    }{" "}
                                                    Code
                                                </th>

                                                <th>
                                                    {
                                                        activeDimension.label
                                                    }{" "}
                                                    Name
                                                </th>

                                                <th>
                                                    Budget
                                                </th>

                                                <th>
                                                    Actual
                                                </th>

                                                <th>
                                                    Variance
                                                </th>

                                                <th>
                                                    Utilization
                                                </th>

                                                <th>
                                                    Status
                                                </th>

                                                <th>
                                                    Action
                                                </th>

                                            </tr>
                                        </thead>

                                        <tbody>
                                            {dimensionLines.map(
                                                (
                                                    line,
                                                    index
                                                ) => {
                                                    const code =
                                                        line[
                                                        activeDimension
                                                            .codeKey
                                                        ] ??
                                                        line.code ??
                                                        "--";

                                                    const name =
                                                        line[
                                                        activeDimension
                                                            .nameKey
                                                        ] ??
                                                        "--";

                                                    return (
                                                        <tr
                                                            key={`${activeDimension.key}-${code}-${index}`}
                                                            className={
                                                                activeDrilldownRecord?.code ===
                                                                    code
                                                                    ? "budget-dimension-row selected"
                                                                    : "budget-dimension-row"
                                                            }
                                                            onClick={() => {
                                                                if (
                                                                    activeDrilldownRecord?.code ===
                                                                    code
                                                                ) {
                                                                    setSelectedDrilldownRecord(
                                                                        null
                                                                    );

                                                                    setSelectedDrilldownDimension(
                                                                        null
                                                                    );

                                                                    return;
                                                                }

                                                                setSelectedDrilldownRecord(
                                                                    code
                                                                );

                                                                setSelectedDrilldownDimension(
                                                                    null
                                                                );
                                                            }}
                                                        >
                                                            <td>
                                                                <strong>
                                                                    {
                                                                        code
                                                                    }
                                                                </strong>
                                                            </td>

                                                            <td>
                                                                {
                                                                    name
                                                                }
                                                            </td>

                                                            <td>
                                                                {formatCurrency(
                                                                    line.budget
                                                                )}
                                                            </td>

                                                            <td>
                                                                {formatCurrency(
                                                                    line.actual
                                                                )}
                                                            </td>

                                                            <td>
                                                                {formatCurrency(
                                                                    line.variance
                                                                )}
                                                            </td>

                                                            <td>
                                                                {formatPercent(
                                                                    line.utilization_percentage
                                                                )}
                                                            </td>

                                                            <td>
                                                                <span className="budget-table-status">
                                                                    {line.status ??
                                                                        "--"}
                                                                </span>
                                                            </td>

                                                            <td>
                                                                <button
                                                                    type="button"
                                                                    className="budget-drilldown-button"

                                                                    onClick={(event) => {
                                                                        event.stopPropagation();

                                                                        setSelectedDrilldownRecord(
                                                                            code
                                                                        );

                                                                        setSelectedDrilldownDimension(
                                                                            null
                                                                        );
                                                                    }}
                                                                >
                                                                    View Drill-Down
                                                                </button>
                                                            </td>

                                                        </tr>
                                                    );
                                                }
                                            )}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <p className="budget-empty">
                                    No dimension-level
                                    budget analysis is
                                    currently available.
                                </p>
                            )}

                            {activeDrilldownRecord && (
                                <div
                                    ref={drilldownSectionRef}
                                    className="budget-drilldown-section"
                                >
                                    <div className="budget-drilldown-heading">
                                        <div>
                                            <p className="section-eyebrow">
                                                Drill-down analysis
                                            </p>

                                            <h3>
                                                {activeDrilldownRecord.name ??
                                                    activeDrilldownRecord.code ??
                                                    "--"}
                                            </h3>

                                            {activeDrilldownRecord.name &&
                                                activeDrilldownRecord.code && (
                                                    <small>
                                                        {
                                                            activeDrilldownRecord.code
                                                        }
                                                    </small>
                                                )}
                                        </div>

                                        <span className="budget-line-total">
                                            {formatCount(
                                                activeDrilldownLines.length
                                            )}{" "}
                                            records
                                        </span>
                                    </div>

                                    {availableDrilldownDimensions.length >
                                        0 && (
                                            <div className="budget-dimension-selector">
                                                {availableDrilldownDimensions.map(
                                                    (dimensionKey) => {
                                                        const dimension =
                                                            budgetDimensions.find(
                                                                (item) =>
                                                                    item.key ===
                                                                    dimensionKey
                                                            );

                                                        return (
                                                            <button
                                                                key={
                                                                    dimensionKey
                                                                }
                                                                type="button"
                                                                className={
                                                                    activeDrilldownDimension ===
                                                                        dimensionKey
                                                                        ? "budget-dimension-button active"
                                                                        : "budget-dimension-button"
                                                                }
                                                                onClick={() =>
                                                                    setSelectedDrilldownDimension(
                                                                        dimensionKey
                                                                    )
                                                                }
                                                            >
                                                                {dimension?.label ??
                                                                    dimensionKey}
                                                            </button>
                                                        );
                                                    }
                                                )}
                                            </div>
                                        )}

                                    {activeDrilldownLines.length >
                                        0 ? (
                                        <div className="budget-table-wrap">
                                            <table className="budget-table">
                                                <thead>
                                                    <tr>
                                                        <th>
                                                            {
                                                                budgetDimensions.find(
                                                                    (item) =>
                                                                        item.key ===
                                                                        activeDrilldownDimension
                                                                )?.label ??
                                                                "Dimension"
                                                            }{" "}
                                                            Code
                                                        </th>

                                                        <th>Name</th>

                                                        <th>
                                                            Budget
                                                        </th>

                                                        <th>
                                                            Actual
                                                        </th>

                                                        <th>
                                                            Variance
                                                        </th>

                                                        <th>
                                                            Utilization
                                                        </th>

                                                        <th>
                                                            Status
                                                        </th>
                                                    </tr>
                                                </thead>

                                                <tbody>
                                                    {activeDrilldownLines.map(
                                                        (
                                                            line,
                                                            index
                                                        ) => (
                                                            <tr
                                                                key={`${activeDrilldownDimension}-${line.code ?? index}-${index}`}
                                                            >
                                                                <td>
                                                                    <strong>
                                                                        {line.code ??
                                                                            "--"}
                                                                    </strong>
                                                                </td>

                                                                <td>
                                                                    {line.name ??
                                                                        "--"}
                                                                </td>

                                                                <td>
                                                                    {formatCurrency(
                                                                        line.budget
                                                                    )}
                                                                </td>

                                                                <td>
                                                                    {formatCurrency(
                                                                        line.actual
                                                                    )}
                                                                </td>

                                                                <td>
                                                                    {formatCurrency(
                                                                        line.variance
                                                                    )}
                                                                </td>

                                                                <td>
                                                                    {formatPercent(
                                                                        line.utilization_percentage
                                                                    )}
                                                                </td>

                                                                <td>
                                                                    <span className="budget-table-status">
                                                                        {line.status ??
                                                                            "--"}
                                                                    </span>
                                                                </td>
                                                            </tr>
                                                        )
                                                    )}
                                                </tbody>
                                            </table>
                                        </div>
                                    ) : (
                                        <p className="budget-empty">
                                            No drill-down records are
                                            available for this
                                            selection.
                                        </p>
                                    )}
                                </div>
                            )}

                        </section>

                        <section className="budget-evidence-note">
                            <strong>
                                Evidence-based Budget
                                Intelligence
                            </strong>

                            <p>
                                Budget values are
                                displayed from the
                                validated AI-FOS
                                Budget vs Actual
                                engine. The frontend
                                does not recalculate
                                financial results.
                            </p>
                        </section>
                    </>
                )}
            </main>
        </div>
    );
}

export default Budget;