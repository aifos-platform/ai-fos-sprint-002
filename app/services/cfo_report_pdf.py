from io import BytesIO
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ============================================================
# DESIGN CONSTANTS
# ============================================================

NAVY = colors.HexColor("#183153")
DARK_TEXT = colors.HexColor("#1F2937")
MUTED_TEXT = colors.HexColor("#667085")
LIGHT_BG = colors.HexColor("#F5F7FA")
LIGHT_BLUE = colors.HexColor("#EAF2F8")
BORDER = colors.HexColor("#D9E0E8")
WHITE = colors.white

PAGE_WIDTH = A4[0]
PAGE_HEIGHT = A4[1]


# ============================================================
# PUBLIC PDF GENERATOR
# ============================================================


def generate_cfo_report_pdf(
    report: dict[str, Any] | None,
) -> bytes:
    """
    Generate the professional AI-FOS CFO Financial Intelligence Report.

    The renderer is presentation-only.

    It consumes the validated structured CFO report and does not
    recalculate financial results.
    """

    report = report or {}

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=16 * mm,
        leftMargin=16 * mm,
        topMargin=18 * mm,
        bottomMargin=17 * mm,
        title="AI-FOS CFO Financial Intelligence Report",
        author="AI-FOS",
    )

    styles = _build_styles()

    story: list[Any] = []

    # --------------------------------------------------------
    # Source sections
    # --------------------------------------------------------

    executive_summary = _mapping(
        report.get("executive_summary")
    )

    financial_health = _mapping(
        report.get("financial_health")
    )

    liquidity = _mapping(
        report.get("liquidity")
    )

    budget = _mapping(
        report.get("budget")
    )

    funding = _mapping(
        report.get("funding")
    )

    core_cost_coverage = _mapping(
        report.get("core_cost_coverage")
    )

    risks = _mapping(
        report.get("risks")
    )

    opportunities = _mapping(
        report.get("opportunities")
    )

    recommendations = _mapping(
        report.get("recommendations")
    )

    trends = _mapping(
        report.get("trends")
    )

    forecast = _mapping(
        report.get("forecast")
    )

    methodology = _mapping(
        report.get("methodology")
    )

    # ========================================================
    # 1. COVER
    # ========================================================

    _append_cover(
        story=story,
        report=report,
        styles=styles,
    )

    story.append(PageBreak())

    # ========================================================
    # 2. EXECUTIVE SUMMARY
    # ========================================================

    _append_executive_summary(
        story=story,
        executive_summary=executive_summary,
        financial_health=financial_health,
        liquidity=liquidity,
        funding=funding,
        styles=styles,
    )

    story.append(PageBreak())

    # ========================================================
    # 3. FINANCIAL HEALTH
    # ========================================================

    _append_financial_health(
        story=story,
        financial_health=financial_health,
        styles=styles,
    )

    story.append(PageBreak())

    # ========================================================
    # 4. LIQUIDITY
    # ========================================================

    _append_liquidity(
        story=story,
        liquidity=liquidity,
        styles=styles,
    )

    story.append(PageBreak())

    # ========================================================
    # 5. BUDGET
    # ========================================================

    _append_budget(
        story=story,
        budget=budget,
        styles=styles,
    )

    story.append(PageBreak())

    # ========================================================
    # 6. FUNDING & GRANTS
    # ========================================================

    _append_funding(
        story=story,
        funding=funding,
        styles=styles,
    )

    story.append(PageBreak())

    # ========================================================
    # 7. CORE COST COVERAGE
    # ========================================================

    _append_core_cost_coverage(
        story=story,
        core_cost_coverage=core_cost_coverage,
        styles=styles,
    )

    story.append(PageBreak())

    # ========================================================
    # 8. CURRENT & FORWARD RISKS
    # ========================================================

    _append_risks(
        story=story,
        risks=risks,
        styles=styles,
    )

    story.append(PageBreak())

    # ========================================================
    # 9. OPPORTUNITIES
    # ========================================================

    _append_opportunities(
        story=story,
        opportunities=opportunities,
        styles=styles,
    )

    story.append(PageBreak())

    # ========================================================
    # 10. CFO RECOMMENDATIONS
    # ========================================================

    _append_recommendations(
        story=story,
        recommendations=recommendations,
        styles=styles,
    )

    story.append(PageBreak())

    # ========================================================
    # 11. TRENDS
    # ========================================================

    _append_trends(
        story=story,
        trends=trends,
        styles=styles,
    )

    story.append(PageBreak())

    # ========================================================
    # 12. FORECAST
    # ========================================================

    _append_forecast(
        story=story,
        forecast=forecast,
        styles=styles,
    )

    story.append(PageBreak())

    # ========================================================
    # 12. METHODOLOGY
    # ========================================================

    _append_methodology(
        story=story,
        methodology=methodology,
        funding=funding,
        styles=styles,
    )

    document.build(
        story,
        onFirstPage=_add_cover_footer,
        onLaterPages=_add_standard_header_footer,
    )

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes


# ============================================================
# STYLES
# ============================================================


def _build_styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()

    return {
        "title": ParagraphStyle(
            "AI_FOS_Title",
            parent=base["Title"],
            alignment=TA_CENTER,
            fontSize=25,
            leading=30,
            textColor=NAVY,
            spaceAfter=10,
        ),
        "cover_label": ParagraphStyle(
            "AI_FOS_Cover_Label",
            parent=base["Normal"],
            alignment=TA_CENTER,
            fontSize=11,
            leading=14,
            textColor=MUTED_TEXT,
        ),
        "cover_subtitle": ParagraphStyle(
            "AI_FOS_Cover_Subtitle",
            parent=base["Normal"],
            alignment=TA_CENTER,
            fontSize=14,
            leading=19,
            textColor=DARK_TEXT,
        ),
        "section": ParagraphStyle(
            "AI_FOS_Section",
            parent=base["Heading1"],
            fontSize=17,
            leading=21,
            textColor=NAVY,
            spaceBefore=2,
            spaceAfter=10,
        ),
        "subsection": ParagraphStyle(
            "AI_FOS_Subsection",
            parent=base["Heading2"],
            fontSize=12,
            leading=15,
            textColor=NAVY,
            spaceBefore=5,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "AI_FOS_Body",
            parent=base["BodyText"],
            fontSize=9.3,
            leading=13,
            textColor=DARK_TEXT,
            spaceAfter=5,
        ),
        "small": ParagraphStyle(
            "AI_FOS_Small",
            parent=base["BodyText"],
            fontSize=8.2,
            leading=11,
            textColor=MUTED_TEXT,
            spaceAfter=3,
        ),
        "card_label": ParagraphStyle(
            "AI_FOS_Card_Label",
            parent=base["Normal"],
            alignment=TA_CENTER,
            fontSize=8.2,
            leading=10,
            textColor=MUTED_TEXT,
        ),
        "card_value": ParagraphStyle(
            "AI_FOS_Card_Value",
            parent=base["Normal"],
            alignment=TA_CENTER,
            fontSize=15,
            leading=18,
            textColor=NAVY,
        ),
        "callout": ParagraphStyle(
            "AI_FOS_Callout",
            parent=base["BodyText"],
            fontSize=9.2,
            leading=13,
            textColor=DARK_TEXT,
            leftIndent=4,
            rightIndent=4,
            spaceAfter=3,
        ),
        "item_title": ParagraphStyle(
            "AI_FOS_Item_Title",
            parent=base["Heading3"],
            fontSize=10.5,
            leading=13,
            textColor=NAVY,
            spaceAfter=3,
        ),
        "item_text": ParagraphStyle(
            "AI_FOS_Item_Text",
            parent=base["BodyText"],
            fontSize=8.8,
            leading=12,
            textColor=DARK_TEXT,
            spaceAfter=3,
        ),
        "center_small": ParagraphStyle(
            "AI_FOS_Center_Small",
            parent=base["Normal"],
            alignment=TA_CENTER,
            fontSize=8.3,
            leading=11,
            textColor=MUTED_TEXT,
        ),
        "left": ParagraphStyle(
            "AI_FOS_Left",
            parent=base["Normal"],
            alignment=TA_LEFT,
            fontSize=9,
            leading=12,
            textColor=DARK_TEXT,
        ),
    }


# ============================================================
# COVER
# ============================================================


def _append_cover(
    *,
    story: list[Any],
    report: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    story.append(Spacer(1, 28 * mm))

    story.append(
        Paragraph(
            "AI-FOS",
            styles["cover_label"],
        )
    )

    story.append(Spacer(1, 3 * mm))

    story.append(
        Paragraph(
            "CFO Financial Intelligence Report",
            styles["title"],
        )
    )

    story.append(
        Paragraph(
            "Management & Board Financial Overview",
            styles["cover_subtitle"],
        )
    )

    story.append(Spacer(1, 11 * mm))

    line = Table(
        [[""]],
        colWidths=[160 * mm],
        rowHeights=[1.2 * mm],
        hAlign="CENTER",
    )

    line.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    NAVY,
                )
            ]
        )
    )

    story.append(line)
    story.append(Spacer(1, 15 * mm))

    version = str(
        report.get("version") or "1.0"
    )

    information = [
        [
            Paragraph(
                "Report Type",
                styles["card_label"],
            ),
            Paragraph(
                "Version",
                styles["card_label"],
            ),
        ],
        [
            Paragraph(
                "CFO Financial Intelligence Report",
                styles["card_value"],
            ),
            Paragraph(
                version,
                styles["card_value"],
            ),
        ],
    ]

    table = Table(
        information,
        colWidths=[
            110 * mm,
            50 * mm,
        ],
        rowHeights=[
            9 * mm,
            15 * mm,
        ],
        hAlign="CENTER",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_BG,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    BORDER,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
            ]
        )
    )

    story.append(table)
    story.append(Spacer(1, 18 * mm))

    story.append(
        Paragraph(
            (
                "Decision-ready financial intelligence covering "
                "financial health, liquidity, budget performance, "
                "funding, grants, risks, opportunities, forecasts, "
                "and management priorities."
            ),
            ParagraphStyle(
                "AI_FOS_Cover_Description",
                parent=styles["body"],
                alignment=TA_CENTER,
                fontSize=10,
                leading=15,
                textColor=MUTED_TEXT,
            ),
        )
    )

    story.append(Spacer(1, 20 * mm))

    story.append(
        Paragraph(
            "CONFIDENTIAL — MANAGEMENT & BOARD USE",
            styles["center_small"],
        )
    )


# ============================================================
# EXECUTIVE SUMMARY
# ============================================================


def _append_executive_summary(
    *,
    story: list[Any],
    executive_summary: dict[str, Any],
    financial_health: dict[str, Any],
    liquidity: dict[str, Any],
    funding: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    _section_title(
        story,
        "Executive Summary",
        styles,
    )

    story.append(
        Paragraph(
            (
                "AI-FOS consolidates the most decision-relevant "
                "financial indicators into one management-level view. "
                "The figures below are drawn from the validated "
                "financial model and supporting intelligence engines."
            ),
            styles["body"],
        )
    )

    story.append(Spacer(1, 4 * mm))

    health = _mapping(
        executive_summary.get(
            "financial_health"
        )
    )

    score = (
        health.get("score")
        if health
        else financial_health.get("score")
    )

    rating = (
        health.get("rating")
        or health.get("status")
        or financial_health.get("rating")
        or financial_health.get("status")
        or "-"
    )

    summary_liquidity = _mapping(
        executive_summary.get(
            "liquidity"
        )
    )

    runway = (
        summary_liquidity.get(
            "cash_runway_months"
        )
        or liquidity.get(
            "cash_runway_months"
        )
    )

    funding_gap_summary = _funding_gap_summary(
        funding
    )

    funding_gap = funding_gap_summary.get(
        "funding_gap"
    )

    coverage = funding_gap_summary.get(
        "applied_coverage_percentage"
    )

    cards = [
        (
            "Financial Health",
            (
                f"{_value(score)} / 100"
                if score is not None
                else "-"
            ),
            str(rating),
        ),
        (
            "Cash Runway",
            (
                f"{_value(runway)} months"
                if runway is not None
                else "-"
            ),
            "Available liquidity horizon",
        ),
        (
            "Funding Gap",
            _currency(funding_gap),
            (
                f"{_value(coverage)}% coverage"
                if coverage is not None
                else "Remaining requirement"
            ),
        ),
    ]

    story.append(
        _metric_cards(
            cards=cards,
            styles=styles,
        )
    )

    story.append(Spacer(1, 7 * mm))

    rows = [
        [
            "Decision Indicator",
            "Count",
        ],
        [
            "High Current Risks",
            _value(
                executive_summary.get(
                    "high_current_risk_count"
                )
            ),
        ],
        [
            "High Forward-Looking Risks",
            _value(
                executive_summary.get(
                    "high_forward_risk_count"
                )
            ),
        ],
        [
            "High-Priority Opportunities",
            _value(
                executive_summary.get(
                    "high_opportunity_count"
                )
            ),
        ],
        [
            "Priority CFO Actions",
            _value(
                executive_summary.get(
                    "priority_action_count"
                )
            ),
        ],
    ]

    story.append(
        _standard_table(
            rows,
            widths=[
                125 * mm,
                35 * mm,
            ],
        )
    )

    story.append(Spacer(1, 7 * mm))

    management_focus = (
        "Management should use this report to prioritize the "
        "highest-risk financial issues, protect validated funding "
        "coverage, maintain liquidity resilience, and address "
        "forward-looking operating and funding pressures."
    )

    _callout(
        story=story,
        title="Management Focus",
        text=management_focus,
        styles=styles,
    )


# ============================================================
# FINANCIAL HEALTH
# ============================================================


def _append_financial_health(
    *,
    story: list[Any],
    financial_health: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    _section_title(
        story,
        "Financial Health",
        styles,
    )

    score = financial_health.get("score")
    maximum = financial_health.get("maximum")
    rating = (
        financial_health.get("rating")
        or financial_health.get("status")
    )

    cards = [
        (
            "Overall Score",
            (
                f"{_value(score)} / {_value(maximum or 100)}"
                if score is not None
                else "-"
            ),
            str(rating or "-"),
        )
    ]

    story.append(
        _metric_cards(
            cards=cards,
            styles=styles,
        )
    )

    story.append(Spacer(1, 7 * mm))

    categories = _mapping(
        financial_health.get("categories")
    )

    if not categories:
        _no_data(
            story,
            styles,
        )
        return

    rows = [
        [
            "Financial Health Area",
            "Score",
            "Maximum",
            "Assessment",
        ]
    ]

    for key, item in categories.items():
        item_data = _mapping(item)

        rows.append(
            [
                _label(key),
                _value(
                    item_data.get("score")
                ),
                _value(
                    item_data.get("maximum")
                ),
                _paragraph_text(
                    item_data.get("reason"),
                    styles["small"],
                ),
            ]
        )

    story.append(
        _standard_table(
            rows,
            widths=[
                38 * mm,
                18 * mm,
                18 * mm,
                86 * mm,
            ],
            small=True,
        )
    )

    metrics = _mapping(
        financial_health.get("metrics")
    )

    if metrics:
        story.append(Spacer(1, 7 * mm))

        story.append(
            Paragraph(
                "Key Financial Health Metrics",
                styles["subsection"],
            )
        )

        selected = _select_mapping(
            metrics,
            [
                "remaining_requirement",
                "applied_secured_funding",
                "funding_gap",
                "applied_coverage_percentage",
                "matched_requirement_count",
                "unmatched_requirement_count",
                "actual_only_grant_count",
                "budget_only_grant_count",
            ],
        )

        if selected:
            story.append(
                _key_value_table(
                    selected
                )
            )


# ============================================================
# LIQUIDITY
# ============================================================


def _append_liquidity(
    *,
    story: list[Any],
    liquidity: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    _section_title(
        story,
        "Liquidity & Cash Runway",
        styles,
    )

    if not liquidity:
        _no_data(
            story,
            styles,
        )
        return

    cards = [
        (
            "Available Cash",
            _currency(
                liquidity.get(
                    "available_cash"
                )
            ),
            "Validated available liquidity",
        ),
        (
            "Blocked Cash",
            _currency(
                liquidity.get(
                    "blocked_cash"
                )
            ),
            "Restricted / blocked liquidity",
        ),
        (
            "Cash Runway",
            (
                f"{_value(liquidity.get('cash_runway_months'))} months"
                if liquidity.get(
                    "cash_runway_months"
                ) is not None
                else "-"
            ),
            "Operating-expense coverage",
        ),
    ]

    story.append(
        _metric_cards(
            cards=cards,
            styles=styles,
        )
    )

    story.append(Spacer(1, 7 * mm))

    selected = _select_mapping(
        liquidity,
        [
            "total_cash",
            "available_cash",
            "blocked_cash",
            "available_account_count",
            "blocked_account_count",
            "unclassified_cash_account_count",
            "total_expenses",
            "average_monthly_expenses",
            "cash_runway_months",
            "reporting_period_start",
            "reporting_period_end",
            "reporting_month_count",
            "runway_basis",
        ],
    )

    story.append(
        _key_value_table(
            selected
        )
    )

    runway_basis = liquidity.get(
        "runway_basis"
    )

    if runway_basis:
        story.append(Spacer(1, 6 * mm))

        _callout(
            story=story,
            title="Runway Basis",
            text=str(runway_basis),
            styles=styles,
        )


# ============================================================
# BUDGET
# ============================================================


def _append_budget(
    *,
    story: list[Any],
    budget: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    _section_title(
        story,
        "Budget Performance",
        styles,
    )

    if not budget:
        _no_data(
            story,
            styles,
        )
        return

    executive = _mapping(
        budget.get(
            "executive_summary"
        )
    )

    portfolio = _mapping(
        budget.get(
            "portfolio_control"
        )
    )

    source = executive or portfolio or budget

    cards = [
        (
            "Total Budget",
            _currency(
                source.get(
                    "total_budget"
                )
            ),
            "Current validated portfolio",
        ),
        (
            "Total Actual",
            _currency(
                source.get(
                    "total_actual"
                )
            ),
            "Recorded expenditure",
        ),
        (
            "Utilization",
            (
                f"{_value(source.get('utilization_percentage'))}%"
                if source.get(
                    "utilization_percentage"
                ) is not None
                else "-"
            ),
            "Budgeted actual / budget",
        ),
    ]

    story.append(
        _metric_cards(
            cards=cards,
            styles=styles,
        )
    )

    story.append(Spacer(1, 7 * mm))

    selected = _select_mapping(
        source,
        [
            "total_budget",
            "total_actual",
            "budgeted_actual",
            "unbudgeted_actual",
            "budget_variance",
            "total_variance",
            "overall_variance_including_unbudgeted",
            "utilization_percentage",
            "budget_line_count",
            "line_count",
            "over_budget_count",
            "within_budget_count",
            "no_budget_count",
        ],
    )

    if selected:
        story.append(
            _key_value_table(
                selected
            )
        )

    organization = _mapping(
        budget.get("organization")
    )

    if organization:
        story.append(Spacer(1, 7 * mm))

        story.append(
            Paragraph(
                "Portfolio Scope",
                styles["subsection"],
            )
        )

        scope = _select_mapping(
            organization,
            [
                "fund_count",
                "donor_count",
                "program_count",
                "project_count",
            ],
        )

        if scope:
            story.append(
                _key_value_table(
                    scope
                )
            )

    alerts = budget.get("alerts")

    if isinstance(alerts, list) and alerts:
        story.append(Spacer(1, 7 * mm))

        story.append(
            Paragraph(
                "Budget Alerts",
                styles["subsection"],
            )
        )

        _append_compact_items(
            story=story,
            items=alerts[:8],
            styles=styles,
        )


# ============================================================
# FUNDING
# ============================================================


def _append_funding(
    *,
    story: list[Any],
    funding: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    _section_title(
        story,
        "Funding & Grant Position",
        styles,
    )

    if not funding:
        _no_data(
            story,
            styles,
        )
        return

    summary = _funding_gap_summary(
        funding
    )

    cards = [
        (
            "Remaining Requirement",
            _currency(
                summary.get(
                    "remaining_requirement"
                )
            ),
            "Validated uncovered requirement basis",
        ),
        (
            "Applied Secured Funding",
            _currency(
                summary.get(
                    "applied_secured_funding"
                )
            ),
            "Eligible secured funding applied",
        ),
        (
            "Funding Gap",
            _currency(
                summary.get(
                    "funding_gap"
                )
            ),
            (
                f"{_value(summary.get('applied_coverage_percentage'))}% coverage"
                if summary.get(
                    "applied_coverage_percentage"
                ) is not None
                else "Remaining uncovered need"
            ),
        ),
    ]

    story.append(
        _metric_cards(
            cards=cards,
            styles=styles,
        )
    )

    story.append(Spacer(1, 7 * mm))

    selected = _select_mapping(
        summary,
        [
            "total_needed_budget",
            "actual_spending_against_need",
            "remaining_requirement",
            "gross_remaining_secured_funding",
            "explicitly_mapped_secured_funding",
            "applied_secured_funding",
            "excess_eligible_funding",
            "secured_funding_without_budget_line_allocation",
            "funding_gap",
            "applied_coverage_percentage",
            "matched_requirement_count",
            "unmatched_requirement_count",
            "fully_funded_requirement_count",
            "partially_funded_requirement_count",
            "unfunded_requirement_count",
            "no_remaining_requirement_count",
            "requirements_with_dimension_incompatible_funding",
            "requirements_with_period_ineligible_funding",
            "requirements_with_period_unknown_funding",
        ],
    )

    if selected:
        story.append(
            _key_value_table(
                selected
            )
        )

    diagnostic_note = summary.get(
        "diagnostic_exposure_note"
    )

    if diagnostic_note:
        story.append(Spacer(1, 7 * mm))

        _callout(
            story=story,
            title="Funding Diagnostic Note",
            text=str(diagnostic_note),
            styles=styles,
        )

    diagnostics = _mapping(
        funding.get(
            "grant_diagnostics"
        )
    )

    if diagnostics:
        story.append(Spacer(1, 7 * mm))

        story.append(
            Paragraph(
                "Grant Diagnostics",
                styles["subsection"],
            )
        )

        rows = [
            [
                "Diagnostic",
                "Count",
            ]
        ]

        for key in (
            "matched_grants",
            "budget_only_grants",
            "actual_only_grants",
        ):
            value = diagnostics.get(key)

            if isinstance(value, list):
                count = len(value)
            elif isinstance(value, int):
                count = value
            else:
                continue

            rows.append(
                [
                    _label(key),
                    str(count),
                ]
            )

        if len(rows) > 1:
            story.append(
                _standard_table(
                    rows,
                    widths=[
                        125 * mm,
                        35 * mm,
                    ],
                )
            )

# ============================================================
# CORE COST COVERAGE
# ============================================================


def _append_core_cost_coverage(
    *,
    story: list[Any],
    core_cost_coverage: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    _section_title(
        story,
        "Core Cost Coverage",
        styles,
    )

    if not core_cost_coverage:
        _no_data(
            story,
            styles,
        )
        return

    summary = _mapping(
        core_cost_coverage.get("summary")
    )

    coverage_cards = [
        (
            "Needed Core Cost",
            _currency(
                summary.get("needed_core_cost")
            ),
            "Validated core cost requirement",
        ),
        (
            "Direct Grant Coverage",
            _currency(
                summary.get("direct_grant_coverage")
            ),
            "Core costs covered directly by grants",
        ),
        (
            "Allocated Indirect Recovery",
            _currency(
                summary.get(
                    "allocated_indirect_recovery"
                )
            ),
            "Indirect recovery allocated by management",
        ),
        (
            "Unrestricted / Core Funding",
            _currency(
                summary.get(
                    "unrestricted_core_funding"
                )
            ),
            "Other unrestricted or core funding",
        ),
    ]

    story.append(
        _metric_cards(
            cards=coverage_cards,
            styles=styles,
        )
    )

    story.append(Spacer(1, 7 * mm))

    status_cards = [
        (
            "Remaining Core Cost Gap",
            _currency(
                summary.get(
                    "remaining_core_cost_gap"
                )
            ),
            "Remaining uncovered core cost requirement",
        ),
        (
            "Core Cost Coverage",
            (
                f"{_value(summary.get('core_cost_coverage_percentage'))}%"
            ),
            "Verified percentage of core costs covered",
        ),
        (
            "Available Indirect Recovery",
            _currency(
                summary.get(
                    "available_indirect_recovery"
                )
            ),
            "Recovered indirect funding available",
        ),
        (
            "Used / Charged Indirect",
            _currency(
                summary.get(
                    "used_indirect_recovery"
                )
            ),
            "Indirect recovery actually used or charged",
        ),
    ]

    story.append(
        _metric_cards(
            cards=status_cards,
            styles=styles,
        )
    )

    story.append(Spacer(1, 7 * mm)) 

           

# ============================================================
# RISKS
# ============================================================


def _append_risks(
    *,
    story: list[Any],
    risks: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    _section_title(
        story,
        "Risk Intelligence",
        styles,
    )

    current = _list_of_dicts(
        risks.get("current")
    )

    forward = _list_of_dicts(
        risks.get("forward")
    )

    story.append(
        Paragraph(
            "Current Financial Risks",
            styles["subsection"],
        )
    )

    _append_risk_cards(
        story=story,
        risks=current,
        styles=styles,
    )

    story.append(Spacer(1, 7 * mm))

    story.append(
        Paragraph(
            "Forward-Looking Risks",
            styles["subsection"],
        )
    )

    _append_risk_cards(
        story=story,
        risks=forward,
        styles=styles,
    )


def _append_risk_cards(
    *,
    story: list[Any],
    risks: list[dict[str, Any]],
    styles: dict[str, ParagraphStyle],
) -> None:
    if not risks:
        _no_data(
            story,
            styles,
        )
        return

    for risk in risks:
        title = (
            risk.get("title")
            or "Financial Risk"
        )

        severity = risk.get(
            "severity"
        )

        category = risk.get(
            "category"
        )

        evidence = risk.get(
            "evidence"
        )

        recommendation = (
            risk.get(
                "recommendation"
            )
            or risk.get(
                "action"
            )
        )

        content: list[Any] = [
            Paragraph(
                _escape(title),
                styles["item_title"],
            )
        ]

        meta = []

        if severity:
            meta.append(
                f"<b>Severity:</b> {_escape(severity)}"
            )

        if category:
            meta.append(
                f"<b>Category:</b> {_escape(category)}"
            )

        if meta:
            content.append(
                Paragraph(
                    " &nbsp;&nbsp; ".join(meta),
                    styles["small"],
                )
            )

        if evidence:
            content.append(
                Paragraph(
                    (
                        "<b>Evidence:</b> "
                        f"{_escape(evidence)}"
                    ),
                    styles["item_text"],
                )
            )

        if recommendation:
            content.append(
                Paragraph(
                    (
                        "<b>Management response:</b> "
                        f"{_escape(recommendation)}"
                    ),
                    styles["item_text"],
                )
            )

        content.append(
            Spacer(
                1,
                3 * mm,
            )
        )

        story.append(
            KeepTogether(
                content
            )
        )


# ============================================================
# OPPORTUNITIES
# ============================================================


def _append_opportunities(
    *,
    story: list[Any],
    opportunities: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    _section_title(
        story,
        "Financial Opportunities",
        styles,
    )

    items = _list_of_dicts(
        opportunities.get("all")
    )

    if not items:
        _no_data(
            story,
            styles,
        )
        return

    for opportunity in items:
        title = (
            opportunity.get("title")
            or "Financial Opportunity"
        )

        priority = opportunity.get(
            "priority"
        )

        category = opportunity.get(
            "category"
        )

        evidence = opportunity.get(
            "evidence"
        )

        action = (
            opportunity.get(
                "recommended_action"
            )
            or opportunity.get(
                "action"
            )
        )

        content = [
            Paragraph(
                _escape(title),
                styles["item_title"],
            )
        ]

        meta = []

        if priority:
            meta.append(
                f"<b>Priority:</b> {_escape(priority)}"
            )

        if category:
            meta.append(
                f"<b>Category:</b> {_escape(category)}"
            )

        if meta:
            content.append(
                Paragraph(
                    " &nbsp;&nbsp; ".join(meta),
                    styles["small"],
                )
            )

        if evidence:
            content.append(
                Paragraph(
                    (
                        "<b>Evidence:</b> "
                        f"{_escape(evidence)}"
                    ),
                    styles["item_text"],
                )
            )

        if action:
            content.append(
                Paragraph(
                    (
                        "<b>Recommended action:</b> "
                        f"{_escape(action)}"
                    ),
                    styles["item_text"],
                )
            )

        content.append(
            Spacer(
                1,
                4 * mm,
            )
        )

        story.append(
            KeepTogether(
                content
            )
        )


# ============================================================
# RECOMMENDATIONS
# ============================================================


def _append_recommendations(
    *,
    story: list[Any],
    recommendations: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    _section_title(
        story,
        "CFO Recommendations & Priority Actions",
        styles,
    )

    items = _list_of_dicts(
        recommendations.get("all")
    )

    if not items:
        _no_data(
            story,
            styles,
        )
        return

    ordered = sorted(
        items,
        key=lambda item: _priority_rank(
            item.get("priority")
        ),
    )

    for number, recommendation in enumerate(
        ordered,
        start=1,
    ):
        title = (
            recommendation.get("title")
            or recommendation.get("action")
            or f"Management Action {number}"
        )

        priority = recommendation.get(
            "priority"
        )

        category = recommendation.get(
            "category"
        )

        evidence = (
            recommendation.get(
                "evidence"
            )
            or recommendation.get(
                "reason"
            )
        )

        action = recommendation.get(
            "action"
        )

        expected_impact = recommendation.get(
            "expected_impact"
        )

        content = [
            Paragraph(
                f"{number}. {_escape(title)}",
                styles["item_title"],
            )
        ]

        meta = []

        if priority:
            meta.append(
                f"<b>Priority:</b> {_escape(priority)}"
            )

        if category:
            meta.append(
                f"<b>Category:</b> {_escape(category)}"
            )

        if meta:
            content.append(
                Paragraph(
                    " &nbsp;&nbsp; ".join(meta),
                    styles["small"],
                )
            )

        if evidence:
            content.append(
                Paragraph(
                    (
                        "<b>Evidence:</b> "
                        f"{_escape(evidence)}"
                    ),
                    styles["item_text"],
                )
            )

        if action:
            content.append(
                Paragraph(
                    (
                        "<b>Action:</b> "
                        f"{_escape(action)}"
                    ),
                    styles["item_text"],
                )
            )

        if expected_impact:
            content.append(
                Paragraph(
                    (
                        "<b>Expected impact:</b> "
                        f"{_escape(expected_impact)}"
                    ),
                    styles["item_text"],
                )
            )

        content.append(
            Spacer(
                1,
                4 * mm,
            )
        )

        story.append(
            KeepTogether(
                content
            )
        )


# ============================================================
# TRENDS
# ============================================================


def _append_trends(
    *,
    story: list[Any],
    trends: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    _section_title(
        story,
        "Financial Trends",
        styles,
    )

    if not trends:
        _no_data(
            story,
            styles,
        )
        return

    overview = _select_mapping(
        trends,
        [
            "status",
            "basis",
        ],
    )

    coverage = _mapping(
        trends.get("coverage")
    )

    quality = _mapping(
        trends.get("quality")
    )

    if overview:
        story.append(
            _key_value_table(
                overview
            )
        )

    if coverage:
        story.append(Spacer(1, 6 * mm))

        story.append(
            Paragraph(
                "Trend Coverage",
                styles["subsection"],
            )
        )

        story.append(
            _key_value_table(
                coverage
            )
        )

    if quality:
        story.append(Spacer(1, 6 * mm))

        story.append(
            Paragraph(
                "Data Quality",
                styles["subsection"],
            )
        )

        story.append(
            _key_value_table(
                quality
            )
        )

    latest_month = _mapping(
        trends.get(
            "latest_month_comparison"
        )
    )

    if latest_month:
        story.append(Spacer(1, 7 * mm))

        story.append(
            Paragraph(
                "Latest Month Comparison",
                styles["subsection"],
            )
        )

        _append_period_comparison(
            story=story,
            comparison=latest_month,
            styles=styles,
        )

    latest_year = _mapping(
        trends.get(
            "latest_year_comparison"
        )
    )

    if latest_year:
        story.append(Spacer(1, 7 * mm))

        story.append(
            Paragraph(
                "Latest Year Comparison",
                styles["subsection"],
            )
        )

        _append_period_comparison(
            story=story,
            comparison=latest_year,
            styles=styles,
        )


def _append_period_comparison(
    *,
    story: list[Any],
    comparison: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    current_period = comparison.get(
        "current_period"
    )

    previous_period = comparison.get(
        "previous_period"
    )

    if current_period or previous_period:
        story.append(
            Paragraph(
                (
                    f"<b>Current:</b> {_escape(current_period or '-')} "
                    f"&nbsp;&nbsp;&nbsp; "
                    f"<b>Previous:</b> {_escape(previous_period or '-')}"
                ),
                styles["body"],
            )
        )

    rows = [
        [
            "Measure",
            "Current",
            "Previous",
            "Change",
            "Direction",
        ]
    ]

    for key in (
        "revenue",
        "expenses",
        "net_result",
    ):
        item = _mapping(
            comparison.get(key)
        )

        if not item:
            continue

        rows.append(
            [
                _label(key),
                _currency(
                    item.get(
                        "current_value"
                    )
                ),
                _currency(
                    item.get(
                        "previous_value"
                    )
                ),
                (
                    f"{_value(item.get('change_percentage'))}%"
                    if item.get(
                        "change_percentage"
                    ) is not None
                    else "-"
                ),
                _label(
                    item.get(
                        "direction"
                    )
                    or "-"
                ),
            ]
        )

    if len(rows) > 1:
        story.append(
            _standard_table(
                rows,
                widths=[
                    35 * mm,
                    38 * mm,
                    38 * mm,
                    25 * mm,
                    24 * mm,
                ],
                small=True,
            )
        )

    caution = comparison.get(
        "caution"
    )

    if caution:
        story.append(Spacer(1, 5 * mm))

        _callout(
            story=story,
            title="Interpretation Caution",
            text=str(caution),
            styles=styles,
        )


# ============================================================
# FORECAST
# ============================================================


def _append_forecast(
    *,
    story: list[Any],
    forecast: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    _section_title(
        story,
        "Financial Forecast",
        styles,
    )

    if not forecast:
        _no_data(
            story,
            styles,
        )
        return

    selected = _select_mapping(
        forecast,
        [
            "status",
            "forecast_type",
            "methodology",
            "methodology_description",
            "forecast_horizon_months",
        ],
    )

    if selected:
        story.append(
            _key_value_table(
                selected
            )
        )

    baseline = _mapping(
        forecast.get(
            "baseline"
        )
    )

    totals = _mapping(
        forecast.get(
            "forecast_totals"
        )
    )

    confidence = _mapping(
        forecast.get(
            "confidence"
        )
    )

    if baseline:
        story.append(Spacer(1, 7 * mm))

        story.append(
            Paragraph(
                "Baseline",
                styles["subsection"],
            )
        )

        story.append(
            _key_value_table(
                baseline
            )
        )

    if totals:
        story.append(Spacer(1, 7 * mm))

        cards = [
            (
                "Forecast Revenue",
                _currency(
                    totals.get("revenue")
                ),
                "Forecast horizon total",
            ),
            (
                "Forecast Expenses",
                _currency(
                    totals.get("expenses")
                ),
                "Forecast horizon total",
            ),
            (
                "Forecast Net Result",
                _currency(
                    totals.get(
                        "net_result"
                    )
                ),
                "Forecast horizon result",
            ),
        ]

        story.append(
            _metric_cards(
                cards=cards,
                styles=styles,
            )
        )

    if confidence:
        story.append(Spacer(1, 7 * mm))

        story.append(
            Paragraph(
                "Forecast Confidence",
                styles["subsection"],
            )
        )

        story.append(
            _key_value_table(
                confidence
            )
        )


# ============================================================
# METHODOLOGY
# ============================================================


def _append_methodology(
    *,
    story: list[Any],
    methodology: dict[str, Any],
    funding: dict[str, Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    _section_title(
        story,
        "Methodology & Evidence",
        styles,
    )

    story.append(
        Paragraph(
            (
                "This section describes the evidence and calculation "
                "governance applied to the report. It is included for "
                "management transparency and traceability."
            ),
            styles["body"],
        )
    )

    if methodology:
        story.append(Spacer(1, 5 * mm))

        story.append(
            _key_value_table(
                methodology
            )
        )

    funding_gap = _mapping(
        funding.get(
            "funding_gap"
        )
    )

    for possible_key in (
        "methodology",
        "metadata",
    ):
        funding_methodology = _mapping(
            funding_gap.get(
                possible_key
            )
        )

        if funding_methodology:
            story.append(Spacer(1, 7 * mm))

            story.append(
                Paragraph(
                    "Funding Gap Methodology",
                    styles["subsection"],
                )
            )

            story.append(
                _key_value_table(
                    funding_methodology
                )
            )

            break

    story.append(Spacer(1, 8 * mm))

    _callout(
        story=story,
        title="Evidence Principle",
        text=(
            "AI-FOS report presentation consumes validated financial "
            "model outputs. The PDF renderer does not independently "
            "recalculate financial results."
        ),
        styles=styles,
    )


# ============================================================
# SHARED PRESENTATION HELPERS
# ============================================================


def _section_title(
    story: list[Any],
    title: str,
    styles: dict[str, ParagraphStyle],
) -> None:
    story.append(
        Paragraph(
            title,
            styles["section"],
        )
    )

    line = Table(
        [[""]],
        colWidths=[160 * mm],
        rowHeights=[0.7 * mm],
        hAlign="LEFT",
    )

    line.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    NAVY,
                )
            ]
        )
    )

    story.append(line)
    story.append(Spacer(1, 5 * mm))


def _metric_cards(
    *,
    cards: list[tuple[str, str, str]],
    styles: dict[str, ParagraphStyle],
) -> Table:
    count = max(
        len(cards),
        1,
    )

    width = 160 * mm / count

    labels = []
    values = []
    notes = []

    for label, value, note in cards:
        labels.append(
            Paragraph(
                _escape(label),
                styles["card_label"],
            )
        )

        values.append(
            Paragraph(
                _escape(value),
                styles["card_value"],
            )
        )

        notes.append(
            Paragraph(
                _escape(note),
                styles["card_label"],
            )
        )

    table = Table(
        [
            labels,
            values,
            notes,
        ],
        colWidths=[
            width
            for _ in cards
        ],
        rowHeights=[
            9 * mm,
            14 * mm,
            11 * mm,
        ],
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_BG,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.6,
                    BORDER,
                ),
                (
                    "INNERGRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    4,
                ),
            ]
        )
    )

    return table


def _standard_table(
    rows: list[list[Any]],
    widths: list[Any] | None = None,
    small: bool = False,
) -> Table:
    prepared_rows: list[list[Any]] = []

    for row_index, row in enumerate(rows):
        prepared_row: list[Any] = []

        for cell in row:
            if isinstance(
                cell,
                Paragraph,
            ):
                prepared_row.append(cell)
            else:
                prepared_row.append(
                    Paragraph(
                        _escape(cell),
                        ParagraphStyle(
                            f"AI_FOS_Table_{row_index}_{len(prepared_row)}",
                            fontName=(
                                "Helvetica-Bold"
                                if row_index == 0
                                else "Helvetica"
                            ),
                            fontSize=(
                                7.7
                                if small
                                else 8.4
                            ),
                            leading=(
                                9.5
                                if small
                                else 10.5
                            ),
                            textColor=(
                                WHITE
                                if row_index == 0
                                else DARK_TEXT
                            ),
                        ),
                    )
                )

        prepared_rows.append(
            prepared_row
        )

    table = Table(
        prepared_rows,
        colWidths=widths,
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    NAVY,
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    WHITE,
                ),
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    WHITE,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.35,
                    BORDER,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    return table


def _key_value_table(
    mapping: dict[str, Any],
) -> Table:
    rows: list[list[Any]] = [
        [
            "Metric",
            "Value",
        ]
    ]

    for key, value in mapping.items():
        if isinstance(
            value,
            (dict, list),
        ):
            continue

        rows.append(
            [
                _label(key),
                _format_metric_value(
                    key,
                    value,
                ),
            ]
        )

    return _standard_table(
        rows,
        widths=[
            62 * mm,
            98 * mm,
        ],
    )


def _callout(
    *,
    story: list[Any],
    title: str,
    text: str,
    styles: dict[str, ParagraphStyle],
) -> None:
    table = Table(
        [
            [
                Paragraph(
                    f"<b>{_escape(title)}</b><br/>{_escape(text)}",
                    styles["callout"],
                )
            ]
        ],
        colWidths=[
            160 * mm,
        ],
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, -1),
                    LIGHT_BLUE,
                ),
                (
                    "BOX",
                    (0, 0),
                    (-1, -1),
                    0.7,
                    BORDER,
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    7,
                ),
            ]
        )
    )

    story.append(table)


def _append_compact_items(
    *,
    story: list[Any],
    items: list[Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    valid = [
        item
        for item in items
        if isinstance(
            item,
            dict,
        )
    ]

    if not valid:
        _no_data(
            story,
            styles,
        )
        return

    for item in valid:
        title = (
            item.get("title")
            or item.get("message")
            or item.get("category")
            or "Alert"
        )

        details = []

        for field in (
            "severity",
            "priority",
            "category",
            "reason",
            "evidence",
        ):
            value = item.get(field)

            if value not in (
                None,
                "",
            ):
                details.append(
                    f"<b>{_label(field)}:</b> {_escape(value)}"
                )

        story.append(
            Paragraph(
                f"<b>{_escape(title)}</b>",
                styles["item_title"],
            )
        )

        if details:
            story.append(
                Paragraph(
                    "<br/>".join(details),
                    styles["item_text"],
                )
            )

        story.append(
            Spacer(
                1,
                2 * mm,
            )
        )


def _no_data(
    story: list[Any],
    styles: dict[str, ParagraphStyle],
) -> None:
    story.append(
        Paragraph(
            "No validated data is available for this section.",
            styles["small"],
        )
    )


# ============================================================
# DATA HELPERS
# ============================================================


def _mapping(
    value: Any,
) -> dict[str, Any]:
    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


def _list_of_dicts(
    value: Any,
) -> list[dict[str, Any]]:
    if not isinstance(
        value,
        list,
    ):
        return []

    return [
        item
        for item in value
        if isinstance(
            item,
            dict,
        )
    ]


def _select_mapping(
    source: dict[str, Any],
    fields: list[str],
) -> dict[str, Any]:
    result: dict[str, Any] = {}

    for field in fields:
        if field not in source:
            continue

        value = source.get(field)

        if isinstance(
            value,
            (dict, list),
        ):
            continue

        result[field] = value

    return result


def _funding_gap_summary(
    funding: dict[str, Any],
) -> dict[str, Any]:
    funding_gap = _mapping(
        funding.get(
            "funding_gap"
        )
    )

    return _mapping(
        funding_gap.get(
            "summary"
        )
    )


def _priority_rank(
    priority: Any,
) -> int:
    mapping = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    return mapping.get(
        str(
            priority or ""
        ).lower(),
        4,
    )


# ============================================================
# VALUE FORMATTERS
# ============================================================


def _label(
    value: Any,
) -> str:
    if value is None:
        return "-"

    return (
        str(value)
        .replace(
            "_",
            " ",
        )
        .strip()
        .title()
    )


def _value(
    value: Any,
) -> str:
    if value is None:
        return "-"

    if isinstance(
        value,
        bool,
    ):
        return (
            "Yes"
            if value
            else "No"
        )

    if isinstance(
        value,
        float,
    ):
        return f"{value:,.2f}"

    if isinstance(
        value,
        int,
    ):
        return f"{value:,}"

    return str(value)


def _currency(
    value: Any,
) -> str:
    if value is None:
        return "-"

    if isinstance(
        value,
        (int, float),
    ):
        return f"{value:,.2f}"

    return str(value)


def _format_metric_value(
    key: str,
    value: Any,
) -> str:
    key_lower = key.lower()

    if value is None:
        return "-"

    if isinstance(
        value,
        bool,
    ):
        return (
            "Yes"
            if value
            else "No"
        )

    if isinstance(
        value,
        (int, float),
    ):
        if "percentage" in key_lower:
            return f"{value:,.2f}%"

        if (
            "count" in key_lower
            or "month_count" in key_lower
            or "year_count" in key_lower
        ):
            return f"{int(value):,}"

        if (
            "cash" in key_lower
            or "budget" in key_lower
            or "funding" in key_lower
            or "requirement" in key_lower
            or "actual" in key_lower
            or "variance" in key_lower
            or "expenses" in key_lower
            or "revenue" in key_lower
            or "result" in key_lower
        ):
            return f"{value:,.2f}"

        if isinstance(
            value,
            float,
        ):
            return f"{value:,.2f}"

        return f"{value:,}"

    return str(value)


def _escape(
    value: Any,
) -> str:
    if value is None:
        return "-"

    text = str(value)

    return (
        text.replace(
            "&",
            "&amp;",
        )
        .replace(
            "<",
            "&lt;",
        )
        .replace(
            ">",
            "&gt;",
        )
    )


def _paragraph_text(
    value: Any,
    style: ParagraphStyle,
) -> Paragraph:
    return Paragraph(
        _escape(
            value
            if value is not None
            else "-"
        ),
        style,
    )


# ============================================================
# PAGE HEADER / FOOTER
# ============================================================


def _add_cover_footer(
    canvas,
    document,
) -> None:
    canvas.saveState()

    canvas.setFont(
        "Helvetica",
        7.5,
    )

    canvas.setFillColor(
        MUTED_TEXT
    )

    canvas.drawCentredString(
        PAGE_WIDTH / 2,
        9 * mm,
        "AI-FOS | CFO Financial Intelligence",
    )

    canvas.restoreState()


def _add_standard_header_footer(
    canvas,
    document,
) -> None:
    canvas.saveState()

    page_number = canvas.getPageNumber()

    canvas.setStrokeColor(
        BORDER
    )

    canvas.setLineWidth(
        0.4
    )

    canvas.line(
        16 * mm,
        PAGE_HEIGHT - 11 * mm,
        PAGE_WIDTH - 16 * mm,
        PAGE_HEIGHT - 11 * mm,
    )

    canvas.setFont(
        "Helvetica-Bold",
        7.5,
    )

    canvas.setFillColor(
        NAVY
    )

    canvas.drawString(
        16 * mm,
        PAGE_HEIGHT - 8.5 * mm,
        "AI-FOS CFO Financial Intelligence Report",
    )

    canvas.setFont(
        "Helvetica",
        7.5,
    )

    canvas.setFillColor(
        MUTED_TEXT
    )

    canvas.drawString(
        16 * mm,
        9 * mm,
        "CONFIDENTIAL — MANAGEMENT & BOARD USE",
    )

    canvas.drawRightString(
        PAGE_WIDTH - 16 * mm,
        9 * mm,
        f"Page {page_number}",
    )

    canvas.restoreState()