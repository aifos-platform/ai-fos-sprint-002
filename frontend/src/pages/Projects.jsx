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

function formatCurrency(value) {
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
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "--";
    }

    return `${number.toFixed(2)}%`;
}

function formatCount(value) {
    const number = Number(value);

    if (!Number.isFinite(number)) {
        return "--";
    }

    return number.toLocaleString("en-US");
}

function displayProgramName(line) {
    return (
        line?.program_name ||
        line?.program_code ||
        line?.code ||
        "Unidentified Program"
    );
}

function displayProgramCode(line) {
    return (
        line?.program_code ||
        line?.code ||
        "--"
    );
}

function statusClass(status) {
    const normalized =
        String(status || "")
            .toLowerCase()
            .replaceAll(" ", "-");

    if (normalized.includes("over-budget")) {
        return "project-status-over";
    }

    if (normalized.includes("within-budget")) {
        return "project-status-within";
    }

    if (
        normalized.includes("no-budget") ||
        normalized.includes(
            "budget-not-identified"
        )
    ) {
        return "project-status-none";
    }

    return "";
}

function Projects({
    projectIntelligence,
    readiness,
    organizationList,
    currentOrganization,
    setCurrentOrganization,
}) {
    const navigate = useNavigate();


    const summary =
        projectIntelligence?.summary ?? {};

    const lines =
        projectIntelligence?.lines ?? [];

    const sourceDimension =
        projectIntelligence?.dimension ??
        "program";

    const dimensionLabel =
        sourceDimension === "program"
            ? "Program"
            : "Project";

    const totalBudget =
        summary.total_budget;

    const totalActual =
        summary.total_actual;

    const variance =
        summary.total_variance ??
        summary.variance;

    const utilization =
        summary.utilization_percentage;

    const lineCount =
        summary.line_count ??
        lines.length;

    const overBudgetCount =
        summary.over_budget_count;

    const withinBudgetCount =
        summary.within_budget_count;

    const noBudgetCount =
        summary.no_budget_count;

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
            return;
        }

    }

    function handleOrganizationChange(event) {
        const selected =
            organizationList.find(
                (organization) =>
                    organization.id ===
                    event.target.value
            );

        if (selected) {
            setCurrentOrganization(selected);
        }
    }

    return (
        <div className="projects-page">
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
                    {navItems.map((item) => (
                        <button
                            key={item}
                            type="button"
                            className={
                                item === "Projects"
                                    ? "nav-item active"
                                    : "nav-item"
                            }
                            onClick={() =>
                                handleNavigation(item)
                            }
                        >
                            {item}
                        </button>
                    ))}
                </nav>
            </aside>

            <main className="projects-main">
                <header className="projects-header">
                    <div>
                        <p className="page-eyebrow">
                            Financial intelligence
                        </p>

                        <h1>Projects</h1>

                        <p className="page-subtitle">
                            Organization:{" "}
                            {currentOrganization?.name ??
                                "Organization"}
                        </p>
                    </div>

                    <div className="projects-header-actions">
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
                                (organization) => (
                                    <option
                                        key={organization.id}
                                        value={organization.id}
                                    >
                                        {organization.name}
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
                    !readiness.has_executive_dashboard && (
                        <section className="projects-section-card">
                            <div className="projects-section-heading">
                                <div>
                                    <p className="section-eyebrow">
                                        Organization readiness
                                    </p>

                                    <h2>
                                        Project Intelligence not available yet
                                    </h2>
                                </div>
                            </div>

                            <p>
                                {currentOrganization?.name ??
                                    "This organization"}{" "}
                                does not yet have validated program or
                                project intelligence available in AI-FOS.
                            </p>

                            <p>
                                Upload and process the organization's
                                budget and financial data to activate
                                Project Intelligence.
                            </p>
                        </section>
                    )}

                {readiness?.has_executive_dashboard && (
                    <>
                        <section className="projects-intro">
                            <p className="section-eyebrow">
                                Program & project intelligence
                            </p>

                            <h2>
                                Programs / Projects Overview
                            </h2>

                            <p>
                                AI-FOS is using the validated{" "}
                                <strong>{dimensionLabel}</strong>{" "}
                                dimension for this organization.
                                For ACSS, Programs represent the
                                operational Project dimension.
                            </p>
                        </section>

                        <section className="projects-kpi-grid">
                            <article className="projects-kpi-card">
                                <span>
                                    Total Program Budget
                                </span>

                                <strong>
                                    {formatCurrency(
                                        totalBudget
                                    )}
                                </strong>

                                <small>
                                    Validated budget across the
                                    program portfolio
                                </small>
                            </article>

                            <article className="projects-kpi-card">
                                <span>
                                    Total Actual
                                </span>

                                <strong>
                                    {formatCurrency(
                                        totalActual
                                    )}
                                </strong>

                                <small>
                                    Actual financial activity
                                    assigned to programs
                                </small>
                            </article>

                            <article className="projects-kpi-card">
                                <span>
                                    Portfolio Utilization
                                </span>

                                <strong>
                                    {formatPercent(
                                        utilization
                                    )}
                                </strong>

                                <div className="projects-progress">
                                    <div
                                        className="projects-progress-fill"
                                        style={{
                                            width: `${Math.min(
                                                Math.max(
                                                    Number(utilization) || 0,
                                                    0
                                                ),
                                                100
                                            )}%`,
                                        }}
                                    />
                                </div>
                            </article>

                            <article className="projects-kpi-card">
                                <span>
                                    Portfolio Variance
                                </span>

                                <strong>
                                    {formatCurrency(
                                        variance
                                    )}
                                </strong>

                                <small>
                                    Validated program-level
                                    budget variance
                                </small>
                            </article>
                        </section>

                        <section className="projects-section-card">
                            <div className="projects-section-heading">
                                <div>
                                    <p className="section-eyebrow">
                                        Portfolio control
                                    </p>

                                    <h2>
                                        Program / Project Status
                                    </h2>
                                </div>

                                <span className="projects-summary-chip">
                                    {formatCount(lineCount)}{" "}
                                    program lines
                                </span>
                            </div>

                            <div className="projects-status-grid">
                                <article className="projects-status-card project-status-over">
                                    <strong>
                                        {formatCount(
                                            overBudgetCount
                                        )}
                                    </strong>

                                    <span>
                                        Over Budget
                                    </span>

                                    <p>
                                        Programs requiring financial
                                        management attention.
                                    </p>
                                </article>

                                <article className="projects-status-card project-status-within">
                                    <strong>
                                        {formatCount(
                                            withinBudgetCount
                                        )}
                                    </strong>

                                    <span>
                                        Within Budget
                                    </span>

                                    <p>
                                        Programs operating within
                                        identified budget limits.
                                    </p>
                                </article>

                                <article className="projects-status-card project-status-none">
                                    <strong>
                                        {formatCount(
                                            noBudgetCount
                                        )}
                                    </strong>

                                    <span>
                                        No Budget
                                    </span>

                                    <p>
                                        Program activity without an
                                        identified budget amount.
                                    </p>
                                </article>
                            </div>
                        </section>

                        <section className="projects-section-card">
                            <div className="projects-section-heading">
                                <div>
                                    <p className="section-eyebrow">
                                        Detailed financial control
                                    </p>

                                    <h2>
                                        Program / Project Portfolio
                                    </h2>
                                </div>
                            </div>

                            {lines.length > 0 ? (
                                <div className="projects-table-wrap">
                                    <table className="projects-table">
                                        <thead>
                                            <tr>
                                                <th>
                                                    Program / Project
                                                </th>
                                                <th>Code</th>
                                                <th>Budget</th>
                                                <th>Actual</th>
                                                <th>Variance</th>
                                                <th>Utilization</th>
                                                <th>Status</th>
                                            </tr>
                                        </thead>

                                        <tbody>
                                            {lines.map(
                                                (line, index) => (
                                                    <tr
                                                        key={
                                                            line.program_code ||
                                                            line.code ||
                                                            index
                                                        }
                                                    >
                                                        <td>
                                                            <strong>
                                                                {displayProgramName(
                                                                    line
                                                                )}
                                                            </strong>
                                                        </td>

                                                        <td>
                                                            {displayProgramCode(
                                                                line
                                                            )}
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
                                                            <span
                                                                className={`projects-table-status ${statusClass(
                                                                    line.status
                                                                )}`}
                                                            >
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
                                <p className="projects-empty">
                                    No validated Program / Project
                                    financial analysis is currently
                                    available.
                                </p>
                            )}
                        </section>

                        <section className="projects-evidence-note">
                            <strong>
                                Evidence-based Program / Project Intelligence
                            </strong>

                            <p>
                                Values are displayed from the
                                validated AI-FOS Budget vs Actual
                                dimension analysis. The frontend
                                does not recalculate program
                                budgets, actuals, variances or
                                utilization.
                            </p>
                        </section>
                    </>
                )}
            </main>
        </div>
    );
}

export default Projects;