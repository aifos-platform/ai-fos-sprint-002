import { useNavigate } from "react-router-dom";
import AppShell from "../components/AppShell";

function formatCompactCurrency(value, currency = "USD") {
  if (value === null || value === undefined || value === "") {
    return "--";
  }

  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "--";
  }

  const normalizedCurrency =
    typeof currency === "string" &&
    /^[A-Za-z]{3}$/.test(currency)
      ? currency.toUpperCase()
      : "USD";

  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: normalizedCurrency,
    notation: "compact",
    compactDisplay: "short",
    maximumFractionDigits: 2,
  }).format(number);
}

function Dashboard({
  health,
  kpis,
  alerts,
  error,
  readiness,
  organizationList,
  currentOrganization,
  setCurrentOrganization,
  setSelectedFile,
  setUploadStatus,
  setInspectionResult,
}) {
  const navigate = useNavigate();

  const handleUploadNavigation = () => {
    setSelectedFile(null);
    setUploadStatus("");
    setInspectionResult(null);
    navigate("/upload");
  };

  const financialIntelligenceUnavailable =
    readiness &&
    !readiness.has_executive_dashboard;

  return (
    <AppShell
      organizationList={organizationList}
      currentOrganization={currentOrganization}
      setCurrentOrganization={setCurrentOrganization}
      onUploadData={handleUploadNavigation}
    >
      <div className="dashboard-heading">
        <h2>Dashboard</h2>
      </div>

      {error && (
        <section className="card">
          <p className="card-note negative">
            {error}
          </p>
        </section>
      )}

      {financialIntelligenceUnavailable ? (
        <section className="dashboard-grid">
          <article className="card wide-card">
            <div className="card-header">
              <div>
            <p className="card-label">
              Grants
            </p>

                <h3>
                  Financial data not available yet
                </h3>
              </div>
            </div>

            <p className="card-note">
              {currentOrganization?.name ??
                "This organization"}{" "}
              does not yet have a processed
              financial intelligence model in
              AI-FOS.
            </p>

            <p className="card-note">
              Upload and process the
              organization&apos;s financial data
              to activate its Dashboard,
              Financial Health, AI CFO,
              Budget Intelligence, Grants,
              Projects, and reporting features.
            </p>

            <div>
              <button
                className="secondary-button"
                type="button"
                onClick={handleUploadNavigation}
              >
                Upload data
              </button>
            </div>
          </article>
        </section>
      ) : (
        <section className="dashboard-grid">
          <article className="card hero-card">
            <div>
              <p className="card-label">
                Financial health
              </p>

              <h3>
                {health
                  ? `${health.score} / 100`
                  : "-- / 100"}
              </h3>

              <span className="status critical">
                {health?.rating ?? "Loading"}
              </span>
            </div>

            <div className="score-ring">
              <span>
                {health?.score ?? "--"}
              </span>
            </div>
          </article>

          <article className="card">
            <p className="card-label">
              Revenue
            </p>

<h3>
  {formatCompactCurrency(
    kpis?.revenue,
    currentOrganization?.baseCurrency
  )}
</h3>

            <p className="card-note">
              Current reporting period
            </p>
          </article>

          <article className="card">
            <p className="card-label">
              Expenses
            </p>

<h3>
  {formatCompactCurrency(
    kpis?.expenses,
    currentOrganization?.baseCurrency
  )}
</h3>

            <p className="card-note">
              Current reporting period
            </p>
          </article>

          <article className="card">
            <p className="card-label">
              Net result
            </p>

<h3>
  {formatCompactCurrency(
    kpis?.net_result,
    currentOrganization?.baseCurrency
  )}
</h3>

            <p className="card-note negative">
              Operating deficit
            </p>
          </article>

          <article className="card wide-card">
            <div className="card-header">
              <div>
                <p className="card-label">
                  AI CFO summary
                </p>

                <h3>
                  Key financial risks
                </h3>
              </div>

              <button
                className="text-button"
                type="button"
                onClick={() =>
                  navigate("/ai-cfo")
                }
              >
                Open AI CFO
              </button>
            </div>

            <div className="insight-list">
              {alerts.length > 0 ? (
                alerts
                  .slice(0, 3)
                  .map((alert, index) => (
                    <div
                      className="insight-item"
                      key={index}
                    >
                      <span
                        className={`risk-dot ${
                          index < 2
                            ? "high"
                            : "medium"
                        }`}
                      />

                      <p>
                        {typeof alert ===
                        "string"
                          ? alert
                          : alert
                              .recommendation ??
                            alert.message ??
                            "Financial alert"}
                      </p>
                    </div>
                  ))
              ) : (
                <p className="card-note">
                  No financial alerts available.
                </p>
              )}
            </div>
          </article>

          <div className="dashboard-support-grid">

          <article className="card dashboard-support-card">
            <p className="card-label">
              Budget utilisation
            </p>

            <h3>
              {kpis?.budget_utilization != null
                ? `${kpis
                    .budget_utilization
                    .toFixed(2)}%`
                : "--"}
            </h3>

            <div className="progress-track">
              <div
                className="progress-bar"
                style={{
                  width: `${Math.min(
                    Math.max(
                      kpis
                        ?.budget_utilization ??
                        0,
                      0
                    ),
                    100
                  )}%`,
                }}
              />
            </div>
          </article>

          <article className="card dashboard-support-card">
            <p className="card-label">
              Grants
            </p>

            <h3>
              {kpis?.grant_count ?? "--"}
            </h3>

            <p className="card-note">
              {kpis?.project_count > 0
                ? `Across ${kpis.project_count} projects`
                : kpis?.program_count > 0
                  ? `Across ${kpis.program_count} programs`
                  : "No project or program dimension available"}
            </p>
          </article>

          <article className="card dashboard-support-card">
            <p className="card-label">
              Donors
            </p>

            <h3>
              {kpis?.donor_count ?? "--"}
            </h3>

            <p className="card-note">
              Funding relationships
            </p>
          </article>
        </div>
        </section>
      )}
    </AppShell>
  );
}

export default Dashboard;