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


const categoryLabels = {
    operating_performance: "Operating Performance",
    financial_position: "Financial Position",
    liquidity: "Liquidity",
    budget_control: "Budget Control",
    funding_and_grant_health:
        "Funding & Grant Health",
};


function FinancialHealth({
    health,
    readiness,
    organizationList,
    currentOrganization,
    setCurrentOrganization,
}) {
    const navigate = useNavigate();

    const financialHealthUnavailable =
        readiness &&
        !readiness.has_financial_health;

    const handleNavigation = (item) => {
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
    };


    const categories =
        health?.categories ?? {};

    const score =
        health?.score ?? null;

    const maximum =
        health?.maximum ?? 100;

    const rating =
        health?.rating ?? "Not available";

    const scorePercentage =
        score != null && maximum
            ? Math.min(
                Math.max(
                    (score / maximum) * 100,
                    0
                ),
                100
            )
            : 0;


    const fundingMetrics =
        categories
            ?.funding_and_grant_health
            ?.metrics ?? {};


    return (
        <div className="app-shell">

            <aside className="sidebar">

                <div className="brand">

                    <div className="brand-mark">
                        AF
                    </div>

                    <div>
                        <h1>AI-FOS</h1>
                        <p>Financial Intelligence</p>
                    </div>

                </div>


                <nav className="nav-list">

                    {navItems.map((item) => (

                        <button
                            key={item}
                            type="button"
                            className={`nav-item ${item === "Financial Health"
                                ? "active"
                                : ""
                                }`}
                            onClick={() =>
                                handleNavigation(item)
                            }
                        >
                            {item}
                        </button>

                    ))}

                </nav>

            </aside>


            <main className="main-content">

                <header className="topbar">

                    <div className="dashboard-heading">

                        <p className="eyebrow">
                            Financial intelligence
                        </p>

                        <h2>
                            Financial Health
                        </h2>

                        <p className="card-note">
                            Organization:{" "}
                            {currentOrganization?.name}
                        </p>

                    </div>


                    <div className="topbar-actions">

                        <select
                            className="organization-selector"
                            value={
                                currentOrganization?.id ??
                                ""
                            }
                            onChange={(event) => {
                                const selected =
                                    organizationList.find(
                                        (organization) =>
                                            organization.id ===
                                            event.target.value
                                    );

                                if (selected) {
                                    setCurrentOrganization(
                                        selected
                                    );
                                }
                            }}
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
                    !readiness.has_financial_health && (
                        <div className="readiness-state-card">
                            <p className="card-label">
                                Organization readiness
                            </p>

                            <h2>
                                Financial Health not available yet
                            </h2>

                            <p className="card-note">
                                {currentOrganization?.name} does not yet
                                have a processed Financial Health model
                                in AI-FOS.
                            </p>

                            <p className="card-note">
                                Upload and process the organization's
                                financial data to activate Financial
                                Health analysis.
                            </p>
                        </div>
                    )}

                {readiness?.has_financial_health && (

                    <section className="financial-health-page">

                        <div className="financial-health-hero">

                            <div className="financial-health-score-card">

                                <div>

                                    <p className="card-label">
                                        Overall Financial Health
                                    </p>

                                    <div className="financial-health-score">

                                        <span className="score-number">
                                            {score ?? "--"}
                                        </span>

                                        <span className="score-maximum">
                                            / {maximum}
                                        </span>

                                    </div>

                                    <span
                                        className={`health-rating ${rating
                                            .toLowerCase()
                                            .replaceAll(" ", "-")
                                            }`}
                                    >
                                        {rating}
                                    </span>

                                </div>


                                <div
                                    className="health-score-ring"
                                    style={{
                                        background: `conic-gradient(
                    #183153 ${scorePercentage}%,
                    #e8edf3 ${scorePercentage}% 100%
                  )`,
                                    }}
                                >

                                    <div className="health-score-ring-inner">

                                        <strong>
                                            {score ?? "--"}
                                        </strong>

                                        <span>
                                            score
                                        </span>

                                    </div>

                                </div>

                            </div>


                            <div className="financial-health-summary-card">

                                <p className="card-label">
                                    CFO Interpretation
                                </p>

                                <h3>
                                    {rating === "Fair"
                                        ? "Financial position requires management attention"
                                        : `Financial health is rated ${rating}`}
                                </h3>

                                <p>
                                    AI-FOS evaluates operating
                                    performance, financial position,
                                    liquidity, budget control, and
                                    funding & grant health using
                                    validated financial intelligence.
                                </p>

                            </div>

                        </div>


                        <div className="health-category-grid">

                            {Object.entries(
                                categories
                            ).map(
                                ([key, category]) => {

                                    const categoryPercentage =
                                        category?.maximum
                                            ? (
                                                category.score /
                                                category.maximum
                                            ) * 100
                                            : 0;


                                    return (

                                        <article
                                            className="health-category-card"
                                            key={key}
                                        >

                                            <div className="health-category-header">

                                                <div>

                                                    <p className="card-label">
                                                        {
                                                            categoryLabels[
                                                            key
                                                            ] ?? key
                                                        }
                                                    </p>

                                                    <h3>
                                                        {category.score}
                                                        <span>
                                                            {" "}
                                                            / {category.maximum}
                                                        </span>
                                                    </h3>

                                                </div>


                                                <div className="health-category-percent">

                                                    {Math.round(
                                                        categoryPercentage
                                                    )}
                                                    %

                                                </div>

                                            </div>


                                            <div className="health-progress-track">

                                                <div
                                                    className="health-progress-bar"
                                                    style={{
                                                        width: `${Math.min(
                                                            Math.max(
                                                                categoryPercentage,
                                                                0
                                                            ),
                                                            100
                                                        )}%`,
                                                    }}
                                                />

                                            </div>


                                            <p className="health-category-reason">
                                                {category.reason}
                                            </p>

                                        </article>

                                    );
                                }
                            )}

                        </div>


                        <section className="health-detail-section">

                            <div className="health-section-heading">

                                <div>

                                    <p className="eyebrow">
                                        Funding health
                                    </p>

                                    <h3>
                                        Funding & Grant Indicators
                                    </h3>

                                </div>

                            </div>


                            <div className="health-metric-grid">

                                <div className="health-metric-card">

                                    <p>
                                        Remaining Requirement
                                    </p>

                                    <strong>
                                        {fundingMetrics
                                            .remaining_requirement !=
                                            null
                                            ? `$${fundingMetrics
                                                .remaining_requirement
                                                .toLocaleString(
                                                    undefined,
                                                    {
                                                        minimumFractionDigits:
                                                            2,
                                                        maximumFractionDigits:
                                                            2,
                                                    }
                                                )}`
                                            : "--"}
                                    </strong>

                                </div>


                                <div className="health-metric-card">

                                    <p>
                                        Applied Secured Funding
                                    </p>

                                    <strong>
                                        {fundingMetrics
                                            .applied_secured_funding !=
                                            null
                                            ? `$${fundingMetrics
                                                .applied_secured_funding
                                                .toLocaleString(
                                                    undefined,
                                                    {
                                                        minimumFractionDigits:
                                                            2,
                                                        maximumFractionDigits:
                                                            2,
                                                    }
                                                )}`
                                            : "--"}
                                    </strong>

                                </div>


                                <div className="health-metric-card">

                                    <p>
                                        Funding Gap
                                    </p>

                                    <strong>
                                        {fundingMetrics
                                            .funding_gap != null
                                            ? `$${fundingMetrics
                                                .funding_gap
                                                .toLocaleString(
                                                    undefined,
                                                    {
                                                        minimumFractionDigits:
                                                            2,
                                                        maximumFractionDigits:
                                                            2,
                                                    }
                                                )}`
                                            : "--"}
                                    </strong>

                                </div>


                                <div className="health-metric-card">

                                    <p>
                                        Funding Coverage
                                    </p>

                                    <strong>
                                        {fundingMetrics
                                            .applied_coverage_percentage !=
                                            null
                                            ? `${fundingMetrics
                                                .applied_coverage_percentage
                                                .toFixed(2)}%`
                                            : "--"}
                                    </strong>

                                </div>

                            </div>


                            <div className="health-evidence-grid">

                                <div className="health-evidence-card">

                                    <span>
                                        {
                                            fundingMetrics
                                                .matched_requirement_count ??
                                            "--"
                                        }
                                    </span>

                                    <p>
                                        Requirements with validated
                                        eligible secured funding
                                    </p>

                                </div>


                                <div className="health-evidence-card">

                                    <span>
                                        {
                                            fundingMetrics
                                                .unmatched_requirement_count ??
                                            "--"
                                        }
                                    </span>

                                    <p>
                                        Requirements without validated
                                        eligible secured funding
                                    </p>

                                </div>


                                <div className="health-evidence-card">

                                    <span>
                                        {
                                            fundingMetrics
                                                .actual_only_grant_count ??
                                            "--"
                                        }
                                    </span>

                                    <p>
                                        Grants with actuals but no
                                        identified budget
                                    </p>

                                </div>


                                <div className="health-evidence-card">

                                    <span>
                                        {
                                            fundingMetrics
                                                .budget_only_grant_count ??
                                            "--"
                                        }
                                    </span>

                                    <p>
                                        Grants with budget but no
                                        actual activity
                                    </p>

                                </div>

                            </div>

                        </section>


                        <div className="health-methodology-note">

                            <strong>
                                Evidence-based score
                            </strong>

                            <p>
                                Financial Health is displayed from
                                the validated AI-FOS Financial
                                Health engine. The frontend does
                                not recalculate the score or its
                                category assessments.
                            </p>

                        </div>

                    </section>
                )}
            </main>

        </div>
    );
}

export default FinancialHealth;