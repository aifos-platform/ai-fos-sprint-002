

import AppShell from "../components/AppShell";

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

function Grants({
    fundingGap,
    fundingGapInsights,
    grantDiagnostics,
    readiness,
    organizationList,
    currentOrganization,
    setCurrentOrganization,
}) {


    const summary =
        fundingGap?.summary ?? {};

    const diagnostics =
        fundingGap?.diagnostics ?? {};

    const insights =
        fundingGapInsights ??
        fundingGap?.funding_gap_insights ??
        [];

    const remainingRequirement =
        summary.remaining_requirement;

    const appliedSecuredFunding =
        summary.applied_secured_funding;

    const fundingGapValue =
        summary.funding_gap;

    const coverage =
        summary.applied_coverage_percentage;

    const matchedRequirements =
        summary.matched_requirement_count;

    const unmatchedRequirements =
        summary.unmatched_requirement_count;

    const fullyFunded =
        summary.fully_funded_requirement_count;

    const partiallyFunded =
        summary.partially_funded_requirement_count;

    const unfunded =
        summary.unfunded_requirement_count;

    const actualOnlyGrants =
        diagnostics.actual_only_grant_count ??
        grantDiagnostics?.actual_only_grant_count;

    const budgetOnlyGrants =
        diagnostics.budget_only_grant_count ??
        grantDiagnostics?.budget_only_grant_count;

    const periodIneligible =
        diagnostics
            .requirements_with_period_ineligible_funding;

    const periodUnknown =
        diagnostics
            .requirements_with_period_unknown_funding;

    const dimensionIncompatible =
        diagnostics
            .requirements_with_dimension_incompatible_funding;

    const periodIneligibleExposure =
        diagnostics
            .period_ineligible_funding_exposure;

    const periodUnknownExposure =
        diagnostics
            .period_unknown_funding_exposure;

    const dimensionIncompatibleExposure =
        diagnostics
            .dimension_incompatible_funding_exposure;

    return (
        <AppShell
            eyebrow="Financial intelligence"
            title="Grants"
            organizationList={organizationList}
            currentOrganization={currentOrganization}
            setCurrentOrganization={setCurrentOrganization}
            mainClassName="grants-main"
        >
                {readiness &&
                    !readiness.has_executive_dashboard && (
                        <section className="grants-section-card">
                            <div className="grants-section-heading">
                                <div>
                                    <p className="section-eyebrow">
                                        Organization readiness
                                    </p>

                                    <h2>
                                        Grant Intelligence not available yet
                                    </h2>
                                </div>
                            </div>

                            <p>
                                {currentOrganization?.name ??
                                    "This organization"}{" "}
                                does not yet have validated grant and
                                funding intelligence available in AI-FOS.
                            </p>

                            <p>
                                Upload and process the organization's
                                budget and financial data to activate
                                Grant Intelligence.
                            </p>
                        </section>
                    )}
                {readiness?.has_executive_dashboard && (
                    <>

                        <section className="grants-intro">
                            <p className="section-eyebrow">
                                Grant intelligence
                            </p>

                            <h2>
                                Grant Portfolio Overview
                            </h2>

                            <p>
                                Monitor funding coverage,
                                remaining requirements,
                                validated secured funding and
                                grant portfolio risks from the
                                AI-FOS Funding Gap engine.
                            </p>
                        </section>

                        <section className="grants-kpi-grid">
                            <article className="grants-kpi-card">
                                <span>
                                    Remaining Requirement
                                </span>

                                <strong>
                                    {formatCurrency(
                                        remainingRequirement
                                    )}
                                </strong>

                                <small>
                                    Remaining validated funding
                                    requirement
                                </small>
                            </article>

                            <article className="grants-kpi-card">
                                <span>
                                    Applied Secured Funding
                                </span>

                                <strong>
                                    {formatCurrency(
                                        appliedSecuredFunding
                                    )}
                                </strong>

                                <small>
                                    Eligible secured funding
                                    applied
                                </small>
                            </article>

                            <article className="grants-kpi-card grants-gap-card">
                                <span>
                                    Funding Gap
                                </span>

                                <strong>
                                    {formatCurrency(
                                        fundingGapValue
                                    )}
                                </strong>

                                <small>
                                    Remaining uncovered need
                                </small>
                            </article>

                            <article className="grants-kpi-card">
                                <span>
                                    Funding Coverage
                                </span>

                                <strong>
                                    {formatPercent(
                                        coverage
                                    )}
                                </strong>

                                <div className="grants-progress">
                                    <div
                                        className="grants-progress-fill"
                                        style={{
                                            width: `${Math.min(
                                                Math.max(
                                                    Number(coverage) || 0,
                                                    0
                                                ),
                                                100
                                            )}%`,
                                        }}
                                    />
                                </div>
                            </article>
                        </section>

                        <section className="grants-section-card">
                            <div className="grants-section-heading">
                                <div>
                                    <p className="section-eyebrow">
                                        Funding status
                                    </p>

                                    <h2>
                                        Requirement Coverage
                                    </h2>
                                </div>

                                <span className="grants-summary-chip">
                                    {formatCount(
                                        matchedRequirements
                                    )}{" "}
                                    matched
                                </span>
                            </div>

                            <div className="grants-status-grid">
                                <article className="grants-status-card status-funded">
                                    <strong>
                                        {formatCount(
                                            fullyFunded
                                        )}
                                    </strong>

                                    <span>
                                        Fully Funded
                                    </span>

                                    <p>
                                        Requirements fully covered
                                        by validated eligible
                                        secured funding.
                                    </p>
                                </article>

                                <article className="grants-status-card status-partial">
                                    <strong>
                                        {formatCount(
                                            partiallyFunded
                                        )}
                                    </strong>

                                    <span>
                                        Partially Funded
                                    </span>

                                    <p>
                                        Requirements with partial
                                        secured-funding coverage.
                                    </p>
                                </article>

                                <article className="grants-status-card status-unfunded">
                                    <strong>
                                        {formatCount(
                                            unfunded
                                        )}
                                    </strong>

                                    <span>
                                        Unfunded
                                    </span>

                                    <p>
                                        Requirements with no
                                        validated eligible secured
                                        funding.
                                    </p>
                                </article>
                            </div>

                            <div className="grants-match-row">
                                <div>
                                    <span>
                                        Requirements with eligible
                                        secured funding
                                    </span>

                                    <strong>
                                        {formatCount(
                                            matchedRequirements
                                        )}
                                    </strong>
                                </div>

                                <div>
                                    <span>
                                        Requirements without
                                        validated eligible funding
                                    </span>

                                    <strong>
                                        {formatCount(
                                            unmatchedRequirements
                                        )}
                                    </strong>
                                </div>
                            </div>
                        </section>

                        <section className="grants-two-column">
                            <article className="grants-section-card">
                                <div className="grants-section-heading">
                                    <div>
                                        <p className="section-eyebrow">
                                            Portfolio diagnostics
                                        </p>

                                        <h2>
                                            Grant Data Quality
                                        </h2>
                                    </div>
                                </div>

                                <div className="grants-diagnostic-list">
                                    <div>
                                        <span>
                                            Actual activity with no
                                            identified grant budget
                                        </span>

                                        <strong>
                                            {formatCount(
                                                actualOnlyGrants
                                            )}
                                        </strong>
                                    </div>

                                    <div>
                                        <span>
                                            Grant budget with no
                                            actual activity
                                        </span>

                                        <strong>
                                            {formatCount(
                                                budgetOnlyGrants
                                            )}
                                        </strong>
                                    </div>
                                </div>
                            </article>

                            <article className="grants-section-card">
                                <div className="grants-section-heading">
                                    <div>
                                        <p className="section-eyebrow">
                                            Funding eligibility
                                        </p>

                                        <h2>
                                            Eligibility Diagnostics
                                        </h2>
                                    </div>
                                </div>

                                <div className="grants-diagnostic-grid">
                                    <div>
                                        <strong>
                                            {formatCount(
                                                periodIneligible
                                            )}
                                        </strong>

                                        <span>
                                            Period ineligible
                                        </span>
                                    </div>

                                    <div>
                                        <strong>
                                            {formatCount(
                                                periodUnknown
                                            )}
                                        </strong>

                                        <span>
                                            Period unknown
                                        </span>
                                    </div>

                                    <div>
                                        <strong>
                                            {formatCount(
                                                dimensionIncompatible
                                            )}
                                        </strong>

                                        <span>
                                            Dimension incompatible
                                        </span>
                                    </div>

                                    <div>
                                        <strong>
                                            {formatCurrency(
                                                dimensionIncompatibleExposure
                                            )}
                                        </strong>

                                        <span>
                                            Dimension-incompatible
                                            funding exposure
                                        </span>
                                    </div>
                                </div>

                                <div className="grants-diagnostic-list">
                                    <div>
                                        <span>
                                            Period-ineligible funding
                                            exposure
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                periodIneligibleExposure
                                            )}
                                        </strong>
                                    </div>

                                    <div>
                                        <span>
                                            Period-unknown funding
                                            exposure
                                        </span>

                                        <strong>
                                            {formatCurrency(
                                                periodUnknownExposure
                                            )}
                                        </strong>
                                    </div>
                                </div>
                            </article>
                        </section>

                        <section className="grants-section-card">
                            <div className="grants-section-heading">
                                <div>
                                    <p className="section-eyebrow">
                                        AI CFO interpretation
                                    </p>

                                    <h2>
                                        Funding Gap Intelligence
                                    </h2>
                                </div>
                            </div>

                            {insights.length > 0 ? (
                                <div className="grants-insights-list">
                                    {insights.map(
                                        (insight, index) => (
                                            <div
                                                key={index}
                                                className="grants-insight-card"
                                            >
                                                {insight}
                                            </div>
                                        )
                                    )}
                                </div>
                            ) : (
                                <p className="grants-empty">
                                    No Funding Gap insights are
                                    currently available.
                                </p>
                            )}
                        </section>

                        <section className="grants-evidence-note">
                            <strong>
                                Evidence-based Grant Intelligence
                            </strong>

                            <p>
                                Funding values and eligibility
                                diagnostics are displayed from
                                validated AI-FOS Funding Gap and
                                Grant Diagnostic outputs. The
                                frontend does not recalculate
                                grant funding eligibility or
                                Funding Gap values.
                            </p>
                        </section>
                    </>
                )}
        </AppShell>
    );
}

export default Grants;