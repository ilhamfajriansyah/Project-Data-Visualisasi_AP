import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from html import escape
from textwrap import dedent

RS_FONT = "Poppins, sans-serif"
RS_PERIOD_OPTIONS = ["June 2026", "May 2026", "April 2026"]
RS_DONUT_COLORS = ["#6366F1", "#06B6D4", "#8B5CF6", "#F59E0B", "#10B981", "#EC4899", "#64748B"]
RS_SETTLEMENT_FILTER_OPTIONS = ["All", "Settled", "Pending", "Failed", "Conflict"]


from .shared_import import get_mapped_column


# ─────────────────────────────────────────────
# STATUS BADGE FORMATTER
# ─────────────────────────────────────────────
def fmt_status_badge(status):
    colors = {
        "SUCCESS":  ("rgba(16,185,129,0.12)", "#059669", "rgba(16,185,129,0.24)"),
        "FAILED":   ("rgba(244,63,94,0.11)",  "#e11d48", "rgba(244,63,94,0.22)"),
        "CONFLICT": ("rgba(245,158,11,0.13)", "#d97706", "rgba(245,158,11,0.24)"),
        "WARNING":  ("rgba(245,158,11,0.13)", "#d97706", "rgba(245,158,11,0.24)"),
        "Settled":  ("rgba(16,185,129,0.12)", "#059669", "rgba(16,185,129,0.24)"),
        "Pending":  ("rgba(245,158,11,0.13)", "#d97706", "rgba(245,158,11,0.24)"),
        "Failed":   ("rgba(244,63,94,0.11)",  "#e11d48", "rgba(244,63,94,0.22)"),
        "Conflict": ("rgba(250,204,21,0.16)", "#ca8a04", "rgba(250,204,21,0.28)"),
    }
    bg, fg, border = colors.get(status, ("rgba(148,163,184,0.12)", "#64748b", "rgba(148,163,184,0.22)"))
    return (
        f'<span style="background:{bg};color:{fg};padding:3px 10px;'
        f'border:1px solid {border};border-radius:999px;font-size:11px;'
        f'font-weight:700;letter-spacing:0.2px;white-space:nowrap;">{status}</span>'
    )

# ─────────────────────────────────────────────
# DATA TRANSFORMATION FROM REAL EXCEL
# ─────────────────────────────────────────────
def get_services_data(df: pd.DataFrame):
    if df is None or df.empty:
        return pd.DataFrame()
        
    col_bidang = get_mapped_column("bidang_usaha") or "bidang_usaha"
    col_rs = get_mapped_column("pendapatan_rs") or "pendapatan_rs"
    col_kontribusi = get_mapped_column("total_kontribusi") or "total_kontribusi"
    
    # Ensure columns exist
    for col in [col_bidang, col_rs, col_kontribusi]:
        if col not in df.columns:
            df[col] = 0 if col != col_bidang else "Unknown"

    grouped = df.groupby(col_bidang, as_index=False).agg({
        col_rs: "sum",
        col_kontribusi: "sum"
    })
    
    grouped["Gross Revenue"] = grouped[col_rs].apply(lambda x: f"Rp {x:,.0f}")
    grouped["Management Share"] = grouped[col_kontribusi].apply(lambda x: f"Rp {x:,.0f}")
    grouped["SBU Share Rule %"] = "N/A"
    grouped["Status"] = "SUCCESS"
    grouped.rename(columns={col_bidang: "Service/SBU"}, inplace=True)
    
    return grouped

def get_trend_data(df: pd.DataFrame):
    if df is None or df.empty:
        return pd.DataFrame(columns=["Bulan"])
        
    col_masa = get_mapped_column("masa_jasa") or "masa_jasa"
    col_bidang = get_mapped_column("bidang_usaha") or "bidang_usaha"
    col_rs = get_mapped_column("pendapatan_rs") or "pendapatan_rs"
    
    for col in [col_masa, col_bidang, col_rs]:
        if col not in df.columns:
            df[col] = 0 if col == col_rs else "Unknown"
            
    pivot = df.pivot_table(index=col_masa, columns=col_bidang, values=col_rs, aggfunc="sum", fill_value=0)
    pivot = pivot.reset_index().rename(columns={col_masa: "Bulan"})
    
    # Scale down values to billions for trend chart
    for col in pivot.columns:
        if col != "Bulan":
            pivot[col] = pivot[col] / 1_000_000_000
            
    # Map 'Others' if too many columns
    if len(pivot.columns) > 4:
        top_cols = pivot.drop("Bulan", axis=1).sum().nlargest(2).index
        others = pivot.drop(["Bulan"] + list(top_cols), axis=1).sum(axis=1)
        pivot = pivot[["Bulan"] + list(top_cols)].copy()
        pivot["Others"] = others
        
    return pivot

def get_detail_revenue_sharing_data(df: pd.DataFrame):
    if df is None or df.empty:
        return pd.DataFrame()
        
    col_masa = get_mapped_column("masa_jasa") or "masa_jasa"
    col_bidang = get_mapped_column("bidang_usaha") or "bidang_usaha"
    col_terminal = get_mapped_column("terminal") or "terminal"
    col_rs = get_mapped_column("pendapatan_rs") or "pendapatan_rs"
    col_kontribusi = get_mapped_column("kontribusi") or "kontribusi"
    
    for col in [col_masa, col_bidang, col_terminal, col_rs, col_kontribusi]:
        if col not in df.columns:
            df[col] = 0 if col in [col_rs, col_kontribusi] else "Unknown"

    result = pd.DataFrame({
        "Date": df[col_masa],
        "Service/SBU": df[col_bidang],
        "Terminal": df[col_terminal],
        "Revenue": df[col_rs].apply(lambda x: f"Rp {x:,.0f}"),
        "Share %": "N/A",
        "Management Share": df[col_kontribusi].apply(lambda x: f"Rp {x:,.0f}"),
        "Settlement Status": "Settled",
        "Variance": 0.0,
        "Remark": "Reconciled",
        "_raw_status": "SUCCESS"
    })
    
    return result



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


def _build_settlement_summary(services_df):
    growth_map = {
        "Ground Handling": 5.2,
        "PSC": 3.1,
        "VIP Services": -2.4,
        "Commercial Area": 1.8,
        "Cargo Area": -18.0,
        "Parking Area": 4.6,
        "Ground Handling Services": 2.9,
    }
    rows = []
    for _, row in services_df.iterrows():
        svc = row["Service/SBU"]
        status = "WARNING" if row["Status"] == "CONFLICT" else row["Status"]
        rows.append({
            "Service / SBU": svc,
            "Revenue": row["Gross Revenue"],
            "Share %": row["SBU Share Rule %"],
            "Management Share": row["Management Share"],
            "Growth %": _format_mom(growth_map.get(svc, 0.0)),
            "Status": fmt_status_badge(status),
        })
    return pd.DataFrame(rows)


def _build_revenue_alerts(services_df):
    alerts = []
    if services_df.empty:
        return alerts
        
    top_svc = services_df.iloc[services_df["Gross Revenue"].map(_parse_rp).argmax()]
    alerts.append(_alert_card_html(
        "positive", "✓",
        f"{top_svc['Service/SBU']} memiliki revenue tertinggi",
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
    if df_trend is None or df_trend.empty or "Bulan" not in df_trend.columns:
        trend_columns = []
    else:
        trend_columns = [col for col in df_trend.columns if col != "Bulan"]

    line_colors = {
        "Ground Handling": "#6366F1",
        "Ground Handling Services": "#6366F1",
        "PSC": "#06B6D4",
        "Others": "#F59E0B",
    }
    fallback_colors = ["#6366F1", "#06B6D4", "#8B5CF6", "#F59E0B", "#10B981", "#EC4899", "#64748B"]
    for idx, col in enumerate(trend_columns):
        color = line_colors.get(col, fallback_colors[idx % len(fallback_colors)])
        fig.add_trace(go.Scatter(
            x=df_trend["Bulan"],
            y=df_trend[col],
            mode="lines+markers",
            name=col,
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color="#ffffff", line=dict(color=color, width=2)),
        ))
    y_max = 1.6
    if trend_columns:
        max_value = df_trend[trend_columns].max(numeric_only=True).max()
        if pd.notna(max_value) and max_value > 0:
            y_max = max(1.6, float(max_value) * 1.2)
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
            range=[0, y_max],
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
def page_revenue_sharing(df_raw):
    from .navigation import show_topnav

    st.markdown('<div class="overview-page-marker rs-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    _inject_rs_page_css()
    show_topnav("Revenue Sharing", show_search=False)

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

    services_df = get_services_data(df_raw)
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
            _trend_figure(get_trend_data(df_raw)),
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

    settlement_df = _build_settlement_summary(services_df)
    settlement_align = {
        "Revenue": "right",
        "Share %": "right",
        "Management Share": "right",
        "Growth %": "right",
        "Status": "center",
    }
    st.markdown(
        _enterprise_table_html(
            settlement_df,
            title="Service Settlement Summary",
            subtitle="Primary analytical view — revenue, share rules, and settlement status by service",
            col_align=settlement_align,
        ),
        unsafe_allow_html=True,
    )

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

        detail_df = get_detail_revenue_sharing_data(df_raw)
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
