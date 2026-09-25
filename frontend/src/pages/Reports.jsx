import { useState } from "react";
import { useNavigate } from "react-router-dom";

import api from "../api";

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

const reportSections = [
  "Executive Summary",
  "Financial Health",
  "Liquidity",
  "Budget Performance",
  "Funding Gap",
  "Current Risks",
  "Forward Risks",
  "Financial Opportunities",
  "CFO Recommendations",
  "Financial Trends",
  "Financial Forecast",
];

function Reports({
  readiness,
  organizationList,
  currentOrganization,
  setCurrentOrganization,
}) {
  const navigate = useNavigate();

  const [downloadStatus, setDownloadStatus] =
    useState("");

  const [isDownloading, setIsDownloading] =
    useState(false);

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

  async function handleDownloadCfoReport(
    format = "pdf"
  ) {
    if (!currentOrganization?.id) {
      setDownloadStatus(
        "Please select an organization first."
      );
      return;
    }

      const normalizedFormat =
        format === "excel"
          ? "excel"
          : format === "word"
            ? "word"
            : "pdf";

      const isExcel =
        normalizedFormat === "excel";

      const isWord =
        normalizedFormat === "word";

      const formatLabel =
        isExcel
          ? "Excel"
          : isWord
            ? "Word"
            : "PDF";

      const endpoint =
        `/reports/${currentOrganization.id}/cfo/${normalizedFormat}`;

      const mimeType =
        isExcel
          ? "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          : isWord
            ? "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            : "application/pdf";

      const filename =
        isExcel
          ? "AI-FOS_CFO_Financial_Intelligence_Report.xlsx"
          : isWord
            ? "AI-FOS_CFO_Financial_Intelligence_Report.docx"
            : "AI-FOS_CFO_Financial_Intelligence_Report.pdf";

    setIsDownloading(true);

    setDownloadStatus(
      `Preparing CFO ${formatLabel} report download...`
    );

    try {
      const response = await api.get(
        endpoint,
        {
          responseType: "blob",
        }
      );

      const reportBlob = new Blob(
        [response.data],
        {
          type: mimeType,
        }
      );

      const downloadUrl =
        window.URL.createObjectURL(
          reportBlob
        );

      const link =
        document.createElement("a");

      link.href = downloadUrl;
      link.download = filename;

      document.body.appendChild(link);

      link.click();

      document.body.removeChild(link);

      window.URL.revokeObjectURL(
        downloadUrl
      );

      setDownloadStatus(
        `CFO Financial Intelligence ${formatLabel} report downloaded successfully.`
      );
    } catch (error) {
      console.error(
        `CFO ${formatLabel} report download error:`,
        error
      );

      if (error.response?.status === 404) {
        setDownloadStatus(
          `The CFO ${formatLabel} report is not available yet. Upload and process financial data first.`
        );
      } else {
        setDownloadStatus(
          `Could not download the CFO ${formatLabel} report. Please try again.`
        );
      }
    } finally {
      setIsDownloading(false);
    }
  }

  return (
    <div className="reports-center-page">
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
                item === "Reports"
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

      <main className="reports-center-main">
        <header className="reports-center-header">
          <div>
            <p className="page-eyebrow">
              Financial reporting
            </p>

            <h1>Report Center</h1>

            <p className="page-subtitle">
              Organization:{" "}
              {currentOrganization?.name ??
                "Organization"}
            </p>
          </div>

          <div className="reports-center-actions">
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
            <section className="reports-featured-card">
              <p className="section-eyebrow">
                Organization readiness
              </p>

              <h2>
                Financial Reports not available yet
              </h2>

              <p>
                {currentOrganization?.name ??
                  "This organization"}{" "}
                does not yet have validated
                financial intelligence available
                for reporting in AI-FOS.
              </p>

              <p>
                Upload and process the
                organization's financial data to
                activate CFO-quality financial
                reporting.
              </p>
            </section>
          )}

        {readiness?.has_executive_dashboard && (
          <>
            <section className="reports-center-intro">
              <p className="section-eyebrow">
                AI-FOS reporting center
              </p>

              <h2>
                CFO-quality financial reporting
              </h2>

              <p>
                Convert validated AI-FOS financial
                intelligence into professional,
                decision-ready reports for
                management, finance teams and
                Boards.
              </p>
            </section>

            <section className="reports-center-overview">
              <article className="reports-overview-card">
                <span>
                  Available Reports
                </span>

                <strong>1</strong>

                <small>
                  Production-ready report
                </small>
              </article>

              <article className="reports-overview-card">
                <span>
                  Current Format
                </span>

                <strong>PDF</strong>

                <small>
                  Professional downloadable
                  document
                </small>
              </article>

              <article className="reports-overview-card">
                <span>
                  Intelligence Sections
                </span>

                <strong>
                  {reportSections.length}
                </strong>

                <small>
                  CFO intelligence areas
                </small>
              </article>

              <article className="reports-overview-card">
                <span>
                  Report Type
                </span>

                <strong>CFO</strong>

                <small>
                  Management & Board ready
                </small>
              </article>
            </section>

            <section className="reports-featured-card">
              <div className="reports-featured-top">
                <div className="reports-file-icon">
                  PDF
                </div>

                <div className="reports-available-badge">
                  Available
                </div>
              </div>

              <div className="reports-featured-body">
                <p className="section-eyebrow">
                  Management & Board
                </p>

                <h2>
                  CFO Financial Intelligence
                  Report
                </h2>

                <p>
                  A professional CFO report
                  generated from validated AI-FOS
                  intelligence, bringing together
                  financial health, performance,
                  funding, risks, opportunities
                  and forward-looking analysis.
                </p>

                <div className="reports-section-grid">
                  {reportSections.map(
                    (section) => (
                      <div
                        key={section}
                        className="reports-section-item"
                      >
                        <span className="reports-section-check">
                          ✓
                        </span>

                        <span>
                          {section}
                        </span>
                      </div>
                    )
                  )}
                </div>
              </div>

              <div className="reports-featured-footer">
                <div>
                  <strong>
                    CFO Financial Intelligence
                    Report
                  </strong>

                  <p>
                    PDF · Professional financial
                    report
                  </p>
                </div>

                <button
                  type="button"
                  className="primary-button reports-download-button"
                  disabled={isDownloading}
                onClick={() =>
                  handleDownloadCfoReport("pdf")
                }
                >
                  {isDownloading
                    ? "Downloading..."
                    : "Download PDF Report"}
                </button>
              </div>
            </section>

            {downloadStatus && (
              <div
                className={`reports-download-status ${downloadStatus.includes(
                  "successfully"
                )
                    ? "success"
                    : downloadStatus.includes(
                      "Preparing"
                    )
                      ? "working"
                      : "error"
                  }`}
              >
                {downloadStatus}
              </div>
            )}

            <section className="reports-formats-section">
              <div className="reports-section-heading">
                <div>
                  <p className="section-eyebrow">
                    Report formats
                  </p>

                  <h2>
                    AI-FOS Reporting Library
                  </h2>
                </div>
              </div>

              <div className="reports-format-grid">
                <article className="reports-format-card reports-format-active">
                  <div className="reports-format-icon">
                    PDF
                  </div>

                  <div>
                    <h3>
                      CFO PDF Report
                    </h3>

                    <p>
                      Professional management
                      and Board-ready financial
                      intelligence report.
                    </p>
                  </div>

                  <span className="reports-format-status active">
                    Available
                  </span>
                </article>

                <article className="reports-format-card">
                  <div className="reports-format-icon active">
                    XLS
                  </div>

                  <div>
                    <h3>
                      Excel Financial Report
                    </h3>

                    <p>
                      Structured financial
                      schedules, supporting
                      analysis and management
                      detail.
                    </p>
                  </div>

                  <span className="reports-format-status active">
                    Available
                  </span>

                  <button
                    type="button"
                    className="reports-download-button"
                    onClick={() =>
                      handleDownloadCfoReport(
                        "excel"
                      )
                    }
                    disabled={isDownloading}
                  >
                    {isDownloading
                      ? "Preparing..."
                      : "Download Excel"}
                  </button>
                </article>

                <article className="reports-format-card">
                  <div className="reports-format-icon active">
                    DOC
                  </div>

                  <div>
                    <h3>
                      Word CFO Report
                    </h3>

                    <p>
                      Editable CFO-quality
                      narrative and financial
                      reporting document.
                    </p>
                  </div>

                  <span className="reports-format-status active">
                    Available
                  </span>

                  <button
                    type="button"
                    className="reports-download-button"
                    onClick={() =>
                      handleDownloadCfoReport(
                        "word"
                      )
                    }
                    disabled={isDownloading}
                  >
                    {isDownloading
                      ? "Preparing..."
                      : "Download Word"}
                  </button>
                </article>

                <article className="reports-format-card">
                  <div className="reports-format-icon muted">
                    PPT
                  </div>

                  <div>
                    <h3>
                      Board Presentation
                    </h3>

                    <p>
                      Board-ready presentation
                      generated from validated
                      financial intelligence.
                    </p>
                  </div>

                  <span className="reports-format-status">
                    Planned
                  </span>
                </article>
              </div>
            </section>

            <section className="reports-evidence-note">
              <strong>
                Evidence-based Reporting
              </strong>

              <p>
                AI-FOS reports consume validated
                financial intelligence produced by
                the financial engines. The report
                layer presents and explains those
                results rather than recalculating
                them.
              </p>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default Reports;