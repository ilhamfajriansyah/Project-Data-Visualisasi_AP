import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from html import escape
from textwrap import dedent

from .navigation import topnav_actions_html

RS_PAGE_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'width="18" height="18" fill="none" stroke="currentColor" '
    'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true">'
    '<circle cx="18" cy="5" r="3"/>'
    '<circle cx="6" cy="12" r="3"/>'
    '<circle cx="18" cy="19" r="3"/>'
    '<line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>'
    '<line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>'
    '</svg>'
)


def _rs_page_header_html():
    return dedent(f"""
    <div class="ov-page-header">
        <div class="ov-page-header-left">
            <div class="ov-page-icon" aria-hidden="true">{RS_PAGE_ICON_SVG}</div>
            <div class="ov-page-header-copy">
                <div class="ov-page-title-row">
                    <h2 class="ov-page-title">Revenue Sharing</h2>
                </div>
                <p class="ov-page-sub">Track revenue distribution and settlement performance.</p>
            </div>
        </div>
        {topnav_actions_html()}
    </div>
    """).strip()


def _mount_rs_fixed_header():
    components.html(
        """
        <script>
        (function () {
            const doc = window.parent.document;

            function findHeaderHost(marker) {
                return (
                    marker.closest('[data-testid="stVerticalBlockBorderWrapper"]')
                    || marker.closest('[data-testid="stVerticalBlock"]')
                );
            }

            function applyFixedHeader() {
                const marker = doc.querySelector('.ov-sticky-header-marker');
                if (!marker) return;

                const host = findHeaderHost(marker);
                if (!host) return;

                host.classList.add('ov-fixed-header-active');

                const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                const left = sidebar ? sidebar.getBoundingClientRect().width : 258;
                host.style.left = left + 'px';
            }

            applyFixedHeader();
            window.parent.addEventListener('resize', applyFixedHeader);
            setTimeout(applyFixedHeader, 120);
            setTimeout(applyFixedHeader, 450);
            setTimeout(applyFixedHeader, 900);
        })();
        </script>
        """,
        height=0,
    )

RS_FONT = "Poppins, sans-serif"
RS_PERIOD_OPTIONS = ["June 2026", "May 2026", "April 2026"]
RS_DONUT_COLORS = ["#6366F1", "#06B6D4", "#8B5CF6", "#F59E0B", "#10B981", "#EC4899", "#64748B"]
RS_SETTLEMENT_FILTER_OPTIONS = ["All", "Settled", "Pending", "Failed", "Conflict"]


# ─────────────────────────────────────────────
# DUMMY DATA (unchanged business data sources)
# ─────────────────────────────────────────────
def get_services_data():
    return pd.DataFrame({
        "Service/SBU":      ["Ground Handling", "PSC", "VIP Services", "Commercial Area", "Cargo Area", "Parking Area", "Ground Handling Services"],
        "Gross Revenue":    ["Rp 12.1B", "Rp 6.4B", "Rp 4.2B", "Rp 3.9B", "Rp 12.1B", "Rp 12.1B", "Rp 12.1B"],
        "SBU Share Rule %": ["70%", "100%", "65%", "50%", "70%", "70%", "70%"],
        "Management Share": ["Rp 8.47B", "Rp 6.4B", "Rp 2.73B", "Rp 1.95B", "Rp 8.47B", "Rp 8.47B", "Rp 8.47B"],
        "Status":           ["SUCCESS", "SUCCESS", "CONFLICT", "CONFLICT", "FAILED", "FAILED", "FAILED"],
    })


def get_transaction_data():
    return pd.DataFrame({
        "Transaction ID": ["7007001001"] * 7,
        "Revenue/SBU":    ["Ground Handling"] * 7,
        "Type":           ["Revenue"] * 7,
        "Date":           ["12 Jun 2026"] * 7,
        "Amount":         ["Rp 12.1B"] * 7,
        "Status":         ["SUCCESS"] * 7,
    })


def get_terminal_files():
    return pd.DataFrame({
        "File Name":  ["Prod_Jun_Terminal1.xlsx", "Prod_Jun_Terminal2.xlsx"],
        "Tenant/SBU": ["Terminal 1", "Terminal 2"],
        "Date":       ["12 Jun 2026", "17 Jun 2026"],
        "Status":     ["SUCCESS", "FAILED"],
    })


def get_trend_data():
    return pd.DataFrame({
        "Bulan":           ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun"],
        "Ground Handling": [0.9, 1.0, 0.95, 1.1, 1.05, 1.2],
        "PSC":             [0.7, 0.8, 0.75, 0.85, 0.9, 0.95],
        "Others":          [0.5, 0.6, 0.55, 0.65, 0.7, 0.8],
    })


def fmt_status_badge(status):
    colors = {
        "SUCCESS":  ("rgba(16,185,129,0.12)", "#059669", "rgba(16,185,129,0.24)"),
        "FAILED":   ("rgba(244,63,94,0.11)", "#e11d48", "rgba(244,63,94,0.22)"),
        "CONFLICT": ("rgba(245,158,11,0.13)", "#d97706", "rgba(245,158,11,0.24)"),
        "WARNING":  ("rgba(245,158,11,0.13)", "#d97706", "rgba(245,158,11,0.24)"),
        "Settled":  ("rgba(16,185,129,0.12)", "#059669", "rgba(16,185,129,0.24)"),
        "Pending":  ("rgba(245,158,11,0.13)", "#d97706", "rgba(245,158,11,0.24)"),
        "Failed":   ("rgba(244,63,94,0.11)", "#e11d48", "rgba(244,63,94,0.22)"),
        "Conflict": ("rgba(250,204,21,0.16)", "#ca8a04", "rgba(250,204,21,0.28)"),
    }
    bg, fg, border = colors.get(status, ("rgba(148,163,184,0.12)", "#64748b", "rgba(148,163,184,0.22)"))
    return (
        f'<span style="background:{bg};color:{fg};padding:3px 10px;'
        f'border:1px solid {border};border-radius:999px;font-size:11px;'
        f'font-weight:700;letter-spacing:0.2px;white-space:nowrap;">{status}</span>'
    )


def _map_settlement_status(raw_status, index):
    if raw_status == "SUCCESS":
        return "Pending" if index % 5 == 0 else "Settled"
    if raw_status == "CONFLICT":
        return "Conflict"
    return "Failed"


def get_detail_revenue_sharing_data():
    """Detail rows derived from service and transaction dummy sources."""
    rng = np.random.default_rng(42)
    services = get_services_data()
    trx = get_transaction_data()
    terminals = ["Terminal 1", "Terminal 2", "Terminal 3"]
    remarks = ["", "Review variance", "Pending SBU confirmation", "Awaiting finance approval", "Reconciled"]
    rows = []
    for i in range(128):
        svc = services.iloc[i % len(services)]
        trx_row = trx.iloc[i % len(trx)]
        raw_status = svc["Status"]
        settlement = _map_settlement_status(raw_status, i)
        rows.append({
            "Date": trx_row["Date"] if i % 4 else f"{1 + (i % 28)} Jun 2026",
            "Service/SBU": svc["Service/SBU"],
            "Terminal": terminals[i % len(terminals)],
            "Revenue": svc["Gross Revenue"],
            "Share %": svc["SBU Share Rule %"],
            "Management Share": svc["Management Share"],
            "Settlement Status": settlement,
            "Variance": round(rng.uniform(-14.5, 16.8), 1),
            "Remark": remarks[i % len(remarks)],
            "_raw_status": raw_status,
        })
    return pd.DataFrame(rows)


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _parse_rp(text):
    raw = str(text).replace("Rp", "").strip().replace(",", "")
    mult = 1.0
    if raw.endswith("B"):
        mult = 1_000_000_000
        raw = raw[:-1]
    elif raw.endswith("M"):
        mult = 1_000_000
        raw = raw[:-1]
    elif raw.endswith("T"):
        mult = 1_000_000_000_000
        raw = raw[:-1]
    return float(raw) * mult


def _fmt_rp_compact(value):
    if pd.isna(value):
        value = 0
    if value >= 1_000_000_000_000:
        return f"Rp {value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"Rp {value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"Rp {value / 1_000_000:.2f}M"
    return f"Rp {value:,.0f}"


def _format_mom(value):
    cls = "ed-positive" if value >= 0 else "ed-negative"
    arrow = "↑" if value >= 0 else "↓"
    return f'<span class="{cls}">{arrow} {abs(value):.1f}%</span>'


def _table_col_class(col_name, col_align, prefix="ed-th"):
    align = (col_align or {}).get(str(col_name), "left")
    return f"{prefix}-{align}"


def _enterprise_table_inner_html(df, col_align=None):
    col_align = col_align or {}
    header_html = "".join(
        f'<th class="{_table_col_class(col, col_align, "ed-th")}">{escape(str(col))}</th>'
        for col in df.columns
    )
    rows_html = ""
    for _, row in df.iterrows():
        cells = []
        for col, value in zip(df.columns, row):
            text = str(value)
            td_class = _table_col_class(col, col_align, "ed-td")
            if text.startswith("<span ") or text.startswith("<div "):
                cells.append(f'<td class="{td_class}">{text}</td>')
            else:
                cells.append(f'<td class="{td_class}">{escape(text)}</td>')
        rows_html += f"<tr>{''.join(cells)}</tr>"
    return dedent(f"""
    <div class="ed-table-scroll">
        <table class="ed-table">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """).strip()


def _enterprise_table_html(df, title=None, subtitle=None, col_align=None):
    col_align = col_align or {}
    head_html = ""
    if title:
        if subtitle:
            head_html = dedent(f"""
            <div class="ed-table-head-stack">
                <div class="ed-table-head-copy">
                    <p class="ed-table-title">{escape(title)}</p>
                    <p class="ed-table-subtitle">{escape(subtitle)}</p>
                </div>
            </div>
            """).strip()
        else:
            head_html = dedent(f"""
            <div class="ed-table-head">
                <p class="ed-table-title">{escape(title)}</p>
            </div>
            """).strip()
    return dedent(f"""
    <div class="ed-table-card">
        {head_html}
        {_enterprise_table_inner_html(df, col_align=col_align)}
    </div>
    """).strip()


def _overview_filter_label(label):
    return f'<p class="overview-filter-label">{escape(label)}</p>'


def _filter_select_label(value):
    return "Filter" if value == "All" else value


def _kpi_card(label, value, delta, delta_up, accent, icon):
    delta_bg = "#DCFCE7" if delta_up else "#FEE2E2"
    delta_fg = "#059669" if delta_up else "#DC2626"
    arrow = "↑" if delta_up else "↓"
    return dedent(f"""
    <div class="overview-kpi-card rs-kpi-card">
        <div class="overview-kpi-icon" style="background:{accent}14;color:{accent};">{escape(icon)}</div>
        <div class="overview-kpi-copy">
            <div class="overview-kpi-label">{escape(label)}</div>
            <div class="overview-kpi-value">{escape(value)}</div>
            <div class="overview-kpi-delta">
                <strong style="background:{delta_bg};color:{delta_fg};">{arrow} {escape(delta)}</strong>
                vs periode sebelumnya
            </div>
        </div>
    </div>
    """).strip()


def _kpi_ring_card(label, value, delta, accent):
    pct = int(value.replace("%", "")) if isinstance(value, str) else int(value)
    return dedent(f"""
    <div class="overview-kpi-card rs-kpi-card rs-kpi-ring-card">
        <div class="rs-progress-ring" style="background:conic-gradient({accent} 0 {pct}%, #E2E8F0 {pct}% 100%);">
            <span>{escape(value)}</span>
        </div>
        <div class="overview-kpi-copy">
            <div class="overview-kpi-label">{escape(label)}</div>
            <div class="overview-kpi-value rs-kpi-value-spacer" aria-hidden="true">00%</div>
            <div class="overview-kpi-delta">
                <strong style="background:#DCFCE7;color:#059669;">↑ {escape(delta)}</strong>
                vs periode sebelumnya
            </div>
        </div>
    </div>
    """).strip()


def _kpi_grid_html(*cards):
    return f'<div class="rs-kpi-grid">{"".join(cards)}</div>'


def _alert_card_html(severity, icon, title, subtitle):
    styles = {
        "critical": ("#FEE2E2", "#DC2626", "#FECACA"),
        "warning":  ("#FFEDD5", "#EA580C", "#FED7AA"),
        "positive": ("#DCFCE7", "#059669", "#BBF7D0"),
    }
    bg, accent, border = styles.get(severity, styles["warning"])
    return dedent(f"""
    <div class="rs-alert-card" style="background:{bg};border-color:{border};">
        <div class="rs-alert-icon" style="background:#ffffff;color:{accent};border:1px solid {border};">{escape(icon)}</div>
        <div class="rs-alert-copy">
            <p class="rs-alert-title">{escape(title)}</p>
            <p class="rs-alert-sub">{escape(subtitle)}</p>
        </div>
        <div class="rs-alert-chevron">&rsaquo;</div>
    </div>
    """).strip()


def _inject_rs_page_css():
    st.markdown("""
    <style>
    .rs-page-marker { display: none; }

    body:has(.rs-page-marker) .rs-kpi-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        width: 100%;
        margin: 0;
    }
    body:has(.rs-page-marker) .rs-kpi-grid .rs-kpi-card {
        padding: 20px 22px !important;
        min-height: 124px !important;
        height: 100% !important;
        box-sizing: border-box !important;
        margin: 0 !important;
        display: flex !important;
        align-items: center !important;
        gap: 16px !important;
        border-radius: 12px !important;
        border: 1px solid #E2E8F0 !important;
        background: #ffffff !important;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04) !important;
    }
    body:has(.rs-page-marker) .rs-kpi-grid .overview-kpi-copy {
        flex: 1 1 auto;
        min-width: 0;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    body:has(.rs-page-marker) .rs-kpi-grid .overview-kpi-icon,
    body:has(.rs-page-marker) .rs-kpi-grid .rs-progress-ring {
        flex: 0 0 52px;
        align-self: center;
    }
    body:has(.rs-page-marker) .rs-kpi-value-spacer {
        visibility: hidden;
        margin-top: 7px;
        font-size: 26px;
        font-weight: 800;
        line-height: 1.05;
        min-height: 27px;
    }
    body:has(.rs-page-marker) .ed-table-card .ed-table-head-stack,
    body:has(.rs-page-marker) .ed-table-card .ed-table-head {
        padding-left: 22px !important;
        padding-right: 22px !important;
    }
    body:has(.rs-page-marker) .ed-table-card .ed-table-scroll {
        padding-left: 22px !important;
        padding-right: 22px !important;
        padding-bottom: 22px !important;
    }

    .rs-progress-ring {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 52px;
    }
    .rs-progress-ring span {
        width: 38px;
        height: 38px;
        border-radius: 50%;
        background: #ffffff;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #0F172A;
        font-size: 13px;
        font-weight: 800;
        font-family: Poppins, sans-serif !important;
    }
    .rs-kpi-ring-card .overview-kpi-copy {
        position: relative !important;
    }

    .rs-alert-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
        margin-top: 12px;
    }
    .rs-alert-card {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 16px;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
    }
    .rs-alert-icon {
        width: 36px;
        height: 36px;
        flex: 0 0 36px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 900;
    }
    .rs-alert-title {
        margin: 0;
        color: #0F172A;
        font-size: 12.5px;
        font-weight: 700;
        line-height: 1.35;
        font-family: Poppins, sans-serif !important;
    }
    .rs-alert-sub {
        margin: 3px 0 0;
        color: #64748B;
        font-size: 11px;
        font-weight: 500;
        font-family: Poppins, sans-serif !important;
    }
    .rs-alert-chevron {
        margin-left: auto;
        color: #94A3B8;
        font-size: 18px;
        font-weight: 700;
        line-height: 1;
    }
    .rs-donut-body {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 4px;
    }
    .rs-donut-chart-slot {
        flex: 0 0 52%;
        min-width: 0;
    }
    .rs-donut-legend-slot {
        flex: 1 1 auto;
        min-width: 0;
        padding-top: 8px;
    }
    .rs-donut-legend {
        display: flex;
        flex-direction: column;
        gap: 8px;
    }
    .rs-legend-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        font-size: 11.5px;
        color: #475569;
        font-family: Poppins, sans-serif !important;
    }
    .rs-legend-left {
        display: flex;
        align-items: center;
        gap: 8px;
        min-width: 0;
    }
    .rs-legend-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        flex: 0 0 8px;
    }
    .rs-legend-value {
        color: #0F172A;
        font-weight: 700;
        white-space: nowrap;
    }

    div[data-testid="stHorizontalBlock"]:has(.rs-donut-card):has(.rs-trend-card) {
        align-items: stretch !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.rs-donut-card):has(.rs-trend-card) > div[data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
    }
    div[data-testid="stHorizontalBlock"]:has(.rs-donut-card):has(.rs-trend-card)
    > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(.rs-donut-card),
    div[data-testid="stHorizontalBlock"]:has(.rs-donut-card):has(.rs-trend-card)
    > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(.rs-trend-card) {
        flex: 1 1 auto !important;
        min-height: 100% !important;
    }

    body:has(.rs-page-marker) div[data-testid="stVerticalBlock"]:has(.rs-detail-filter-marker)
    [data-testid="stSelectbox"] > div > div {
        min-height: 40px !important;
    }
    body:has(.rs-page-marker) div[data-testid="stVerticalBlock"]:has(.rs-detail-filter-marker)
    [data-testid="stSelectbox"] div[data-baseweb="select"] {
        min-height: 38px !important;
    }

    @media (max-width: 1100px) {
        body:has(.rs-page-marker) .rs-kpi-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }
        .rs-alert-grid { grid-template-columns: 1fr; }
        .rs-donut-body { flex-direction: column; }
        .rs-donut-chart-slot { flex-basis: auto; width: 100%; }
    }
    </style>
    """, unsafe_allow_html=True)


def _compute_kpis(services_df):
    total_revenue = services_df["Gross Revenue"].map(_parse_rp).sum()
    revenue_share = services_df["Management Share"].map(_parse_rp).sum()
    success_count = (services_df["Status"] == "SUCCESS").sum()
    settlement_rate = int(round(success_count / len(services_df) * 100)) if len(services_df) else 0
    issues = int((services_df["Status"] != "SUCCESS").sum())
    return total_revenue, revenue_share, settlement_rate, issues


def _build_revenue_alerts(services_df):
    alerts = []
    cargo = services_df[services_df["Service/SBU"] == "Cargo Area"]
    if not cargo.empty:
        alerts.append(_alert_card_html(
            "critical", "↓",
            "Cargo Area revenue turun 18%",
            "Perlu investigasi penyebab penurunan kontribusi bulan ini",
        ))

    unsettled = services_df[services_df["Status"].isin(["FAILED", "CONFLICT"])]
    if len(unsettled):
        alerts.append(_alert_card_html(
            "warning", "!",
            f"{len(unsettled)} layanan belum selesai settlement",
            "Revenue sharing masih In Progress atau Unsettled",
        ))

    alerts.append(_alert_card_html(
        "warning", "A",
        "VIP Services ACV di bawah target 80%",
        "Monitor performa kontrak dan realisasi omzet",
    ))

    top_svc = services_df.iloc[services_df["Gross Revenue"].map(_parse_rp).argmax()]
    alerts.append(_alert_card_html(
        "positive", "✓",
        f"{top_svc['Service/SBU']} melampaui target revenue",
        f"Kontribusi management share {top_svc['Management Share']}",
    ))
    return alerts


def _donut_figure(services_df, total_revenue):
    labels = services_df["Service/SBU"].tolist()
    values = services_df["Gross Revenue"].map(_parse_rp).tolist()
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        sort=False,
        direction="clockwise",
        marker=dict(colors=RS_DONUT_COLORS[: len(labels)], line=dict(color="#ffffff", width=2)),
        textinfo="none",
        hovertemplate="%{label}<br>%{value:,.0f}<extra></extra>",
    )])
    fig.update_layout(
        height=300,
        margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        showlegend=False,
        annotations=[dict(
            text=f"<b>{_fmt_rp_compact(total_revenue)}</b><br><span style='font-size:11px;color:#64748B'>Total</span>",
            x=0.5, y=0.5, font=dict(size=14, color="#0F172A", family=RS_FONT), showarrow=False,
        )],
    )
    return fig


def _trend_figure(df_trend):
    fig = go.Figure()
    line_colors = {"Ground Handling": "#6366F1", "PSC": "#06B6D4", "Others": "#F59E0B"}
    for col in ["Ground Handling", "PSC", "Others"]:
        fig.add_trace(go.Scatter(
            x=df_trend["Bulan"],
            y=df_trend[col],
            mode="lines+markers",
            name=col,
            line=dict(color=line_colors[col], width=2.5),
            marker=dict(size=6, color="#ffffff", line=dict(color=line_colors[col], width=2)),
        ))
    fig.update_layout(
        autosize=True,
        height=300,
        margin=dict(t=16, b=8, l=8, r=8),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        hovermode="x unified",
        font=dict(family=RS_FONT, size=11, color="#475569"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(family=RS_FONT, size=11, color="#475569"),
        ),
        xaxis=dict(showgrid=False, tickfont=dict(family=RS_FONT, size=11, color="#64748B"), fixedrange=True),
        yaxis=dict(
            title=dict(text="Rp Miliar", font=dict(family=RS_FONT, size=11, color="#64748B")),
            showgrid=True,
            gridcolor="#E2E8F0",
            zeroline=False,
            tickfont=dict(family=RS_FONT, size=11, color="#64748B"),
            fixedrange=True,
            range=[0, 1.6],
        ),
    )
    return fig


def _donut_legend_html(services_df, total_revenue):
    rows = []
    values = services_df["Gross Revenue"].map(_parse_rp)
    for idx, (_, row) in enumerate(services_df.iterrows()):
        val = values.iloc[idx]
        pct = (val / total_revenue * 100) if total_revenue else 0
        color = RS_DONUT_COLORS[idx % len(RS_DONUT_COLORS)]
        rows.append(
            f'<div class="rs-legend-row">'
            f'<div class="rs-legend-left">'
            f'<span class="rs-legend-dot" style="background:{color};"></span>'
            f"<span>{escape(row['Service/SBU'])}</span>"
            f"</div>"
            f'<span class="rs-legend-value">{pct:.1f}% · {escape(row["Gross Revenue"])}</span>'
            f"</div>"
        )
    return f'<div class="rs-donut-legend">{"".join(rows)}</div>'


# ══════════════════════════════════════════════
# PAGE: REVENUE SHARING
# ══════════════════════════════════════════════
def page_revenue_sharing():
    st.markdown('<div class="overview-page-marker rs-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    _inject_rs_page_css()

    with st.container():
        st.markdown('<div class="ov-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_rs_page_header_html(), unsafe_allow_html=True)
        st.markdown('<div class="ov-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="ov-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)
    _mount_rs_fixed_header()

    for key in ["rs_detail_page", "rs_filter_status"]:
        if key not in st.session_state:
            st.session_state[key] = 1 if key == "rs_detail_page" else "All"
    if st.session_state.get("rs_filter_status") not in RS_SETTLEMENT_FILTER_OPTIONS:
        st.session_state.rs_filter_status = "All"

    pf1, pf2, pf3 = st.columns([1.35, 1.35, 3.3])
    with pf1:
        st.markdown(_overview_filter_label("Periode"), unsafe_allow_html=True)
        st.selectbox("Periode", RS_PERIOD_OPTIONS, key="rs_period", label_visibility="collapsed")
    with pf3:
        st.markdown(
            '<div style="height:52px;display:flex;align-items:end;justify-content:flex-end;'
            f'color:#64748B;font-size:12px;font-weight:500;font-family:{RS_FONT};">'
            "Data terakhir diperbarui: 02 Jun 2026 10:30 WIB</div>",
            unsafe_allow_html=True,
        )

    services_df = get_services_data()
    total_revenue, revenue_share, settlement_rate, issues = _compute_kpis(services_df)

    st.markdown(
        _kpi_grid_html(
            _kpi_card("Total Revenue", _fmt_rp_compact(total_revenue), "5.2%", True, "#2563EB", "Rp"),
            _kpi_card("Revenue Share", _fmt_rp_compact(revenue_share), "3.1%", True, "#7C3AED", "%"),
            _kpi_ring_card("Settlement Rate", f"{settlement_rate}%", "1.4%", "#059669"),
            _kpi_card("Issues", str(issues), "2 vs May 2026", False, "#DC2626", "!"),
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    chart_left, chart_right = st.columns([46, 54], gap="small")
    with chart_left:
        st.markdown('<div class="ed-card-marker rs-donut-card"></div>', unsafe_allow_html=True)
        ch1, _ = st.columns([3.2, 1])
        with ch1:
            st.markdown(
                '<p class="ed-section-title">Revenue Contribution by Service</p>'
                '<p class="ed-section-sub">Distribusi gross revenue per layanan / SBU</p>',
                unsafe_allow_html=True,
            )
        chart_slot, legend_slot = st.columns([1.05, 1], gap="small")
        with chart_slot:
            st.plotly_chart(
                _donut_figure(services_df, total_revenue),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        with legend_slot:
            st.markdown(
                f'<div class="rs-donut-legend-slot">{_donut_legend_html(services_df, total_revenue)}</div>',
                unsafe_allow_html=True,
            )

    with chart_right:
        st.markdown('<div class="ed-card-marker rs-trend-card"></div>', unsafe_allow_html=True)
        th1, th2 = st.columns([3.2, 1])
        with th1:
            st.markdown(
                '<p class="ed-section-title">Revenue Trend</p>'
                '<p class="ed-section-sub">Monthly revenue trend by service category (Rp billion)</p>',
                unsafe_allow_html=True,
            )
        with th2:
            st.selectbox("Trend period", ["Monthly"], key="rs_trend_period", label_visibility="collapsed")
        st.plotly_chart(
            _trend_figure(get_trend_data()),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    alert_card = st.container()
    with alert_card:
        st.markdown('<div class="ed-card-marker rs-alerts-card"></div>', unsafe_allow_html=True)
        ah1, _ = st.columns([3, 1])
        with ah1:
            st.markdown(
                '<p class="ed-section-title">Revenue Alerts</p>'
                '<p class="ed-section-sub">Actionable insights for revenue sharing exceptions</p>',
                unsafe_allow_html=True,
            )
        alerts = _build_revenue_alerts(services_df)
        st.markdown(f'<div class="rs-alert-grid">{"".join(alerts)}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    detail_card = st.container()
    with detail_card:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        st.markdown('<div class="rs-detail-filter-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        dh1, ds, df_btn, dex, dpp = st.columns([2.55, 2.25, 1.05, 0.78, 0.72], vertical_alignment="center")
        with dh1:
            st.markdown(
                '<p class="ed-section-title">Detail Revenue Sharing</p>'
                '<p class="ed-section-sub">Granular settlement records with variance monitoring</p>',
                unsafe_allow_html=True,
            )
        with ds:
            search_query = st.text_input(
                "Search",
                placeholder="Search service, tenant, or SBU...",
                key="rs_detail_search",
                label_visibility="collapsed",
                on_change=lambda: st.session_state.update({"rs_detail_page": 1}),
            )
        with df_btn:
            st.selectbox(
                "Settlement Status",
                RS_SETTLEMENT_FILTER_OPTIONS,
                key="rs_filter_status",
                label_visibility="collapsed",
                format_func=_filter_select_label,
                on_change=lambda: st.session_state.update({"rs_detail_page": 1}),
            )

        detail_df = get_detail_revenue_sharing_data()
        if search_query:
            q = search_query.lower().strip()
            detail_df = detail_df[
                detail_df["Service/SBU"].astype(str).str.lower().str.contains(q, na=False)
                | detail_df["Terminal"].astype(str).str.lower().str.contains(q, na=False)
                | detail_df["Remark"].astype(str).str.lower().str.contains(q, na=False)
            ]
        if st.session_state.rs_filter_status != "All":
            detail_df = detail_df[detail_df["Settlement Status"] == st.session_state.rs_filter_status]

        export_df = detail_df.drop(columns=["_raw_status"], errors="ignore").copy()

        with dex:
            st.download_button(
                "Export",
                data=export_df.to_csv(index=False).encode("utf-8"),
                file_name="detail_revenue_sharing.csv",
                mime="text/csv",
                key="rs_detail_export",
                width="stretch",
            )
        with dpp:
            rows_per_page = st.selectbox(
                "Rows per page",
                [10, 25, 50],
                key="rs_rows_per_page",
                label_visibility="collapsed",
            )

        total_rows = len(detail_df)
        total_pages = max(1, int(np.ceil(total_rows / rows_per_page)))
        if st.session_state.rs_detail_page > total_pages:
            st.session_state.rs_detail_page = total_pages
        if st.session_state.rs_detail_page < 1:
            st.session_state.rs_detail_page = 1

        start_idx = (st.session_state.rs_detail_page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        detail_view = detail_df.iloc[start_idx:end_idx].copy()
        detail_view["Variance"] = detail_view["Variance"].apply(_format_mom)
        detail_view["Settlement Status"] = detail_view["Settlement Status"].apply(fmt_status_badge)
        detail_view = detail_view[[
            "Date", "Service/SBU", "Terminal", "Revenue", "Share %",
            "Management Share", "Settlement Status", "Variance", "Remark",
        ]]
        detail_align = {
            "Revenue": "right",
            "Share %": "right",
            "Management Share": "right",
            "Variance": "right",
            "Settlement Status": "center",
        }
        st.markdown(_enterprise_table_inner_html(detail_view, col_align=detail_align), unsafe_allow_html=True)

        first_item = 0 if total_rows == 0 else start_idx + 1
        last_item = min(end_idx, total_rows)

        st.markdown('<div class="overview-detail-pagination-footer-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        pa, pb, pc, pd_ = st.columns([6.6, 0.28, 0.68, 0.28], gap="small")
        with pa:
            st.markdown(
                f'<div class="ed-pagination-info">{first_item}–{last_item} dari {total_rows} data</div>',
                unsafe_allow_html=True,
            )
        with pb:
            if st.button("‹", key="rs_prev_page", disabled=st.session_state.rs_detail_page <= 1):
                st.session_state.rs_detail_page -= 1
                st.rerun()
        with pc:
            st.markdown(
                f'<div class="ed-pagination-label">Page {st.session_state.rs_detail_page} / {total_pages}</div>',
                unsafe_allow_html=True,
            )
        with pd_:
            if st.button("›", key="rs_next_page", disabled=st.session_state.rs_detail_page >= total_pages):
                st.session_state.rs_detail_page += 1
                st.rerun()


if __name__ == "__main__":
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Admin"
    if "user_email" not in st.session_state:
        st.session_state.user_email = "injourneyairports@mail.com"
    if "user_role" not in st.session_state:
        st.session_state.user_role = "Admin"
    page_revenue_sharing()
