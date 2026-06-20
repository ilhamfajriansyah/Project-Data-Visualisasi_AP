"""Traffic Monitor dashboard — Terminal 1 & Terminal 2 only."""

from html import escape
from textwrap import dedent

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components
from sqlalchemy import text

from .connection import get_engine
from .enterprise_ui import (
    ED_FONT,
    donut_legend_html,
    inject_enterprise_page_css,
    progress_bar_html,
    section_title_html,
    table_inner_html,
)

TM_FONT = ED_FONT
TM_YEAR_OPTIONS = ["Year"]
TM_MONTH_OPTIONS = ["Month", "All Months", "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"]
TM_TERMINAL_OPTIONS = ["Terminal", "All Terminals"]
TM_DONUT_COLORS = ["#7C3AED", "#06B6D4"]
TM_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

TERMINAL_STYLES = {
    "Terminal 1": {
        "code": "T1",
        "color": "#7C3AED",
        "soft_bg": "#F5F3FF",
    },
    "Terminal 2": {
        "code": "T2",
        "color": "#06B6D4",
        "soft_bg": "#ECFEFF",
    },
}
DEFAULT_TERMINAL_COLORS = ["#7C3AED", "#06B6D4", "#2563EB", "#059669", "#EA580C", "#D97706"]
MONTH_ALIASES = {
    "january": "January", "jan": "January", "januari": "January",
    "february": "February", "feb": "February", "februari": "February",
    "march": "March", "mar": "March", "maret": "March",
    "april": "April", "apr": "April",
    "may": "May", "mei": "May",
    "june": "June", "jun": "June", "juni": "June",
    "july": "July", "jul": "July", "juli": "July",
    "august": "August", "aug": "August", "agustus": "August", "agu": "August",
    "september": "September", "sep": "September",
    "october": "October", "oct": "October", "oktober": "October", "okt": "October",
    "november": "November", "nov": "November",
    "december": "December", "dec": "December", "desember": "December", "des": "December",
}


def _canonical_month(value):
    if pd.isna(value):
        return None
    raw = str(value).strip()
    if not raw:
        return None
    key = raw.lower()[:3] if raw.lower() not in MONTH_ALIASES else raw.lower()
    return MONTH_ALIASES.get(raw.lower(), MONTH_ALIASES.get(key, raw))


def _month_sort_value(value):
    month = _canonical_month(value)
    try:
        return TM_MONTH_OPTIONS.index(month)
    except ValueError:
        return 99


def _month_short(value):
    month = _canonical_month(value)
    if month in TM_MONTH_OPTIONS:
        return month[:3]
    return str(value)[:3] if value is not None else "-"


def _terminal_style(name, index=0):
    style = TERMINAL_STYLES.get(name, {})
    color = style.get("color", DEFAULT_TERMINAL_COLORS[index % len(DEFAULT_TERMINAL_COLORS)])
    return {
        "code": style.get("code", "".join(part[:1] for part in str(name).split()[:2]).upper() or f"T{index + 1}"),
        "color": color,
        "soft_bg": style.get("soft_bg", f"{color}12"),
    }


@st.cache_data(ttl=60)
def _load_traffic_database_data():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            traffic_df = pd.read_sql(
                text("""
                    SELECT
                        tahun,
                        bulan AS masa_jasa,
                        terminal,
                        SUM(COALESCE(pax_domestik, 0)) AS pax_domestik,
                        SUM(COALESCE(pax_internasional, 0)) AS pax_internasional,
                        SUM(COALESCE(total_pax, 0)) AS total_pax
                    FROM traffic
                    GROUP BY tahun, bulan, terminal
                """),
                conn,
            )
            revenue_df = pd.read_sql(
                text("""
                    SELECT
                        tahun,
                        masa_jasa,
                        terminal,
                        SUM(COALESCE(real_omzet, 0)) AS real_omzet,
                        AVG(NULLIF(spending_per_pax, 0)) AS spending_per_pax
                    FROM transaction_revenue
                    GROUP BY tahun, masa_jasa, terminal
                """),
                conn,
            )
    except Exception:
        return pd.DataFrame()

    if traffic_df.empty:
        return pd.DataFrame()

    merged = traffic_df.merge(
        revenue_df,
        how="left",
        on=["tahun", "masa_jasa", "terminal"],
    )
    return _normalize_traffic_dataframe(merged)


def _traffic_from_dashboard_data(df):
    if df is None or df.empty:
        return pd.DataFrame()

    mapped = pd.DataFrame()
    mapped["tahun"] = df["tahun"] if "tahun" in df.columns else pd.NA
    mapped["masa_jasa"] = df["masa_jasa"] if "masa_jasa" in df.columns else pd.NA
    mapped["terminal"] = df["terminal"] if "terminal" in df.columns else "Unknown"
    mapped["pax_domestik"] = df["subtotal_trafik_dom"] if "subtotal_trafik_dom" in df.columns else 0
    mapped["pax_internasional"] = df["subtotal_trafik_int"] if "subtotal_trafik_int" in df.columns else 0
    if "total_trafik" in df.columns:
        mapped["total_pax"] = df["total_trafik"]
    elif "jumlah_pax" in df.columns:
        mapped["total_pax"] = df["jumlah_pax"]
    else:
        mapped["total_pax"] = mapped["pax_domestik"] + mapped["pax_internasional"]
    mapped["real_omzet"] = df["real_omzet"] if "real_omzet" in df.columns else 0
    mapped["spending_per_pax"] = df["spending_per_pax"] if "spending_per_pax" in df.columns else pd.NA
    return _normalize_traffic_dataframe(mapped)


def _normalize_traffic_dataframe(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=[
            "tahun", "masa_jasa", "terminal", "pax_domestik",
            "pax_internasional", "total_pax", "real_omzet", "spending_per_pax",
        ])

    normalized = df.copy()
    for col in ["tahun", "pax_domestik", "pax_internasional", "total_pax", "real_omzet", "spending_per_pax"]:
        if col in normalized.columns:
            normalized[col] = pd.to_numeric(normalized[col], errors="coerce")
        else:
            normalized[col] = 0

    normalized["tahun"] = normalized["tahun"].dropna().astype(int).reindex(normalized.index)
    normalized["masa_jasa"] = normalized["masa_jasa"].map(_canonical_month)
    normalized["terminal"] = normalized["terminal"].fillna("Unknown").astype(str).str.strip()
    normalized["terminal"] = normalized["terminal"].replace("", "Unknown")

    missing_total = normalized["total_pax"].isna() | normalized["total_pax"].eq(0)
    normalized.loc[missing_total, "total_pax"] = (
        normalized.loc[missing_total, "pax_domestik"].fillna(0)
        + normalized.loc[missing_total, "pax_internasional"].fillna(0)
    )
    missing_split = normalized["pax_domestik"].fillna(0).eq(0) & normalized["pax_internasional"].fillna(0).eq(0)
    normalized.loc[missing_split, "pax_domestik"] = normalized.loc[missing_split, "total_pax"].fillna(0)
    normalized[["pax_domestik", "pax_internasional", "total_pax", "real_omzet"]] = (
        normalized[["pax_domestik", "pax_internasional", "total_pax", "real_omzet"]].fillna(0)
    )
    return normalized.dropna(subset=["tahun", "masa_jasa"])


def get_traffic_monitor_data(df_raw=None):
    db_df = _load_traffic_database_data()
    if not db_df.empty:
        return db_df
    return _traffic_from_dashboard_data(df_raw)


def _apply_filters(df, year_filter="Year", month_filter="Month", terminal_filter="Terminal"):
    filtered = df.copy()
    if year_filter != "Year":
        filtered = filtered[filtered["tahun"] == int(year_filter)]
    if month_filter not in ("Month", "All Months"):
        filtered = filtered[filtered["masa_jasa"] == month_filter]
    if terminal_filter not in ("Terminal", "All Terminals"):
        filtered = filtered[filtered["terminal"] == terminal_filter]
    return filtered


def _aggregate_metrics(df, year_filter="Year", month_filter="Month", terminal_filter="Terminal"):
    current_df = _apply_filters(df, year_filter, month_filter, terminal_filter)
    current_year = int(year_filter) if year_filter != "Year" else (int(df["tahun"].max()) if not df.empty else None)
    prior_df = df[df["tahun"] == current_year - 1] if current_year is not None else df.iloc[0:0]
    if month_filter not in ("Month", "All Months"):
        prior_df = prior_df[prior_df["masa_jasa"] == month_filter]
    if terminal_filter not in ("Terminal", "All Terminals"):
        prior_df = prior_df[prior_df["terminal"] == terminal_filter]

    def build_rows(source):
        rows = []
        if source.empty:
            return rows
        grouped = source.groupby("terminal", dropna=False).agg(
            domestic=("pax_domestik", "sum"),
            international=("pax_internasional", "sum"),
            total=("total_pax", "sum"),
            revenue=("real_omzet", "sum"),
            spp_avg=("spending_per_pax", "mean"),
        ).reset_index()
        for idx, record in grouped.iterrows():
            total = float(record["total"] or 0)
            revenue = float(record["revenue"] or 0)
            spp = float(record["spp_avg"]) if pd.notna(record["spp_avg"]) else (revenue / total if total else 0)
            rows.append({
                **_terminal_style(record["terminal"], idx),
                "name": record["terminal"],
                "domestic": float(record["domestic"] or 0) / 1_000_000,
                "international": float(record["international"] or 0) / 1_000_000,
                "total": total / 1_000_000,
                "spp": spp,
            })
        return rows

    rows = build_rows(current_df)
    total = sum(r["total"] for r in rows)
    domestic = sum(r["domestic"] for r in rows)
    international = sum(r["international"] for r in rows)
    revenue = float(current_df["real_omzet"].sum()) if not current_df.empty else 0
    spp = revenue / (total * 1_000_000) if total else 0
    if not spp and rows and total:
        spp = sum(r["spp"] * r["total"] for r in rows) / total

    prior_total = float(prior_df["total_pax"].sum()) / 1_000_000 if not prior_df.empty else 0
    yoy = ((total - prior_total) / prior_total * 100) if prior_total else 0
    shares = {r["name"]: (r["total"] / total * 100 if total else 0) for r in rows}

    for row in rows:
        prior_terminal = prior_df[prior_df["terminal"] == row["name"]]
        prior_terminal_total = float(prior_terminal["total_pax"].sum()) / 1_000_000 if not prior_terminal.empty else 0
        row["yoy"] = ((row["total"] - prior_terminal_total) / prior_terminal_total * 100) if prior_terminal_total else 0

    return {
        "total": total,
        "domestic": domestic,
        "international": international,
        "domestic_pct": (domestic / total * 100) if total else 0,
        "intl_pct": (international / total * 100) if total else 0,
        "spp": spp,
        "yoy": yoy,
        "prior_total": prior_total,
        "rows": rows,
        "shares": shares,
        "current_year": current_year,
        "prior_year": current_year - 1 if current_year is not None else None,
        "terminal_label": terminal_filter if terminal_filter not in ("Terminal", "All Terminals") else "All Terminals",
    }

def _fmt_millions(value):
    return f"{value:.1f}M"

def _fmt_rp_k(value):
    return f"Rp {value / 1_000:.1f}K"

def get_monthly_traffic_trend(df, year_filter="Year", terminal_filter="Terminal"):
    current_year = int(year_filter) if year_filter != "Year" else (int(df["tahun"].max()) if not df.empty else None)
    prior_year = current_year - 1 if current_year is not None else None

    def series_for(year):
        if year is None:
            return [0] * 12
        source = df[df["tahun"] == year]
        if terminal_filter not in ("Terminal", "All Terminals"):
            source = source[source["terminal"] == terminal_filter]
        monthly = source.groupby("masa_jasa")["total_pax"].sum()
        return [float(monthly.get(month, 0)) / 1_000_000 for month in TM_MONTH_OPTIONS[2:]]

    return pd.DataFrame({
        "Month": TM_MONTHS,
        "Current": series_for(current_year),
        "Prior": series_for(prior_year),
    })

def get_domestic_intl_monthly(df, year_filter="Year", terminal_filter="Terminal"):
    current_year = int(year_filter) if year_filter != "Year" else (int(df["tahun"].max()) if not df.empty else None)
    source = df[df["tahun"] == current_year] if current_year is not None else df.iloc[0:0]
    if terminal_filter not in ("Terminal", "All Terminals"):
        source = source[source["terminal"] == terminal_filter]
    grouped = source.groupby("masa_jasa").agg(
        Domestic=("pax_domestik", "sum"),
        International=("pax_internasional", "sum"),
    )
    return pd.DataFrame({
        "Month": TM_MONTHS,
        "Domestic": [float(grouped["Domestic"].get(month, 0)) / 1_000_000 if not grouped.empty else 0 for month in TM_MONTH_OPTIONS[2:]],
        "International": [float(grouped["International"].get(month, 0)) / 1_000_000 if not grouped.empty else 0 for month in TM_MONTH_OPTIONS[2:]],
    })

def get_spp_monthly(df, year_filter="Year", terminal_filter="Terminal"):
    current_year = int(year_filter) if year_filter != "Year" else (int(df["tahun"].max()) if not df.empty else None)
    source = df[df["tahun"] == current_year] if current_year is not None else df.iloc[0:0]
    if terminal_filter not in ("Terminal", "All Terminals"):
        source = source[source["terminal"] == terminal_filter]
    grouped = source.groupby("masa_jasa").agg(
        total_pax=("total_pax", "sum"),
        real_omzet=("real_omzet", "sum"),
        spp=("spending_per_pax", "mean"),
    )
    values = []
    for month in TM_MONTH_OPTIONS[2:]:
        if grouped.empty or month not in grouped.index:
            values.append(0)
            continue
        row = grouped.loc[month]
        spp = row["spp"] if pd.notna(row["spp"]) else (row["real_omzet"] / row["total_pax"] if row["total_pax"] else 0)
        values.append(float(spp or 0) / 1_000)
    return pd.DataFrame({"Month": TM_MONTHS, "SPP": values})

def get_terminal_table_df(metrics):
    rows = []
    for row in metrics["rows"]:
        total = row["total"]
        dom_pct = row["domestic"] / total * 100 if total else 0
        intl_pct = row["international"] / total * 100 if total else 0
        share = metrics["shares"][row["name"]]
        spp_status = "Above target" if row["spp"] >= 90_000 else "Below target"
        rows.append({
            "Terminal": f'{row["code"]} {row["name"]}',
            "Domestic Traffic": f'<div class="tm-cell-stack">{row["domestic"]:.1f}M<span class="tm-subcell">{dom_pct:.0f}% of terminal</span></div>',
            "International Traffic": f'<div class="tm-cell-stack">{row["international"]:.1f}M<span class="tm-subcell">{intl_pct:.0f}% of terminal</span></div>',
            "Total Traffic": f'{total:.1f}M',
            "Traffic Share": f"{share:.1f}%",
            "Spending Per Pax": f'<div class="tm-cell-stack">{_fmt_rp_k(row["spp"])}<span class="tm-spp-tag {"is-above" if row["spp"] >= 90_000 else "is-below"}">{spp_status}</span></div>',
            "YoY Growth": f'<span class="tm-positive">↑ +{row["yoy"]:.1f}%</span>',
            "_share": share,
            "_total": total,
        })

    total_dom = metrics["domestic"]
    total_intl = metrics["international"]
    total_all = metrics["total"]
    rows.append({
        "Terminal": "TOTAL — Terminal 1 & 2",
        "Domestic Traffic": f"{total_dom:.1f}M",
        "International Traffic": f"{total_intl:.1f}M",
        "Total Traffic": f"{total_all:.1f}M",
        "Traffic Share": "100%",
        "Spending Per Pax": _fmt_rp_k(metrics["spp"]),
        "YoY Growth": f'<span class="tm-positive">↑ +{metrics["yoy"]:.1f}%</span>',
        "_share": 100,
        "_total": total_all,
    })
    return pd.DataFrame(rows)

def _sparkline_svg(values, color):
    if not values:
        return ""
    vals = np.array(values, dtype=float)
    vmin, vmax = vals.min(), vals.max()
    span = vmax - vmin or 1
    pts = []
    for i, val in enumerate(vals):
        x = 4 + (i / max(len(vals) - 1, 1)) * 92
        y = 28 - ((val - vmin) / span) * 22
        pts.append(f"{x:.1f},{y:.1f}")
    polyline = " ".join(pts)
    return (
        f'<svg class="tm-sparkline" viewBox="0 0 100 32" preserveAspectRatio="none" aria-hidden="true">'
        f'<polyline points="{polyline}" fill="none" stroke="{color}" stroke-width="2.2" '
        f'stroke-linecap="round" stroke-linejoin="round"/></svg>'
    )


def _tm_kpi_card(label, value, subtitle, delta_pct, accent, icon, spark_values):
    up = delta_pct >= 0
    badge_bg = "#DCFCE7" if up else "#FEE2E2"
    badge_fg = "#059669" if up else "#DC2626"
    arrow = "↑" if up else "↓"
    return dedent(f"""
    <div class="tm-kpi-card">
        <div class="tm-kpi-top">
            <div class="tm-kpi-icon" style="background:{accent}14;color:{accent};">{escape(icon)}</div>
            <span class="tm-kpi-badge" style="background:{badge_bg};color:{badge_fg};">{arrow} {abs(delta_pct):.1f}%</span>
        </div>
        <div class="tm-kpi-label">{escape(label)}</div>
        <div class="tm-kpi-value">{escape(value)}</div>
        <div class="tm-kpi-sub">{escape(subtitle)}</div>
        {_sparkline_svg(spark_values, accent)}
    </div>
    """).strip()


def _tm_page_header():
    return dedent(f"""
    <div class="tm-page-header">
        <div class="tm-page-header-left">
            <div class="tm-page-icon" aria-hidden="true">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"
                     stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
            </div>
            <div class="tm-page-header-copy">
                <div class="tm-page-title-row">
                    <h2 class="tm-page-title">Traffic Monitor</h2>
                </div>
                <p class="tm-page-sub">Monitor passenger traffic and spending performance.</p>
            </div>
        </div>
    </div>
    """).strip()


def _filter_bar_html():
    return dedent("""
    <div class="tm-filter-label-row">
        <span class="tm-filter-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                 stroke-linecap="round" stroke-linejoin="round">
                <path d="M3 5h18l-7 8v5l-4 2v-7L3 5z"/>
            </svg>
        </span>
        <span class="tm-filter-title">Filter Aktif</span>
    </div>
    """).strip()


def _filter_state_marker(kind, is_active):
    state = "active" if is_active else "empty"
    return f'<span class="tm-filter-marker tm-filter-kind-{kind} tm-filter-state-{state}" aria-hidden="true"></span>'


def _mount_tm_fixed_header():
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
                const marker = doc.querySelector('.tm-sticky-header-marker');
                if (!marker) return;

                const host = findHeaderHost(marker);
                if (!host) return;

                host.classList.add('tm-fixed-header-active');

                const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                const left = sidebar ? sidebar.getBoundingClientRect().width : 258;
                host.style.left = left + 'px';

                const height = host.getBoundingClientRect().height;
                doc.documentElement.style.setProperty('--tm-header-height', height + 'px');

                const spacer = doc.querySelector('.tm-fixed-header-spacer');
                if (spacer) {
                    spacer.style.height = height + 'px';
                }
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


def _mini_metric_box(label, value, sub="", accent="#7C3AED"):
    sub_html = f'<span class="tm-mini-sub">{escape(sub)}</span>' if sub else ""
    return (
        f'<div class="tm-mini-metric" style="border-color:{accent}22;background:{accent}08;">'
        f'<span class="tm-mini-label">{escape(label)}</span>'
        f'<span class="tm-mini-value" style="color:{accent};">{escape(value)}</span>{sub_html}</div>'
    )


def _terminal_card_html(row, share):
    dom_pct = row["domestic"] / row["total"] * 100 if row["total"] else 0
    intl_pct = row["international"] / row["total"] * 100 if row["total"] else 0
    return dedent(f"""
    <div class="tm-terminal-card" style="border-color:{row['color']}22;">
        <div class="tm-terminal-head">
            <div class="tm-terminal-id" style="background:{row['soft_bg']};color:{row['color']};">{row['code']}</div>
            <div class="tm-terminal-copy">
                <p class="tm-terminal-name">{escape(row['name'])}</p>
                <p class="tm-terminal-meta">Dom {row['domestic']:.1f}M · Intl {row['international']:.1f}M</p>
            </div>
            <div class="tm-terminal-stats">
                <p class="tm-terminal-total">{row['total']:.1f}M</p>
                <p class="tm-terminal-share">{share:.1f}% share</p>
            </div>
        </div>
        {progress_bar_html(share, row['color'])}
        <div class="tm-terminal-foot">
            <span>SPP: {_fmt_rp_k(row['spp'])}</span>
            <span>YoY Growth: <strong style="color:#059669;">+{row['yoy']:.1f}%</strong></span>
        </div>
    </div>
    """).strip()


def _insight_card_html(title, body, badge, accent, soft_bg):
    return dedent(f"""
    <div class="tm-insight-card" style="background:{soft_bg};border-color:{accent}22;">
        <p class="tm-insight-title">{escape(title)}</p>
        <p class="tm-insight-body">{escape(body)}</p>
        <span class="tm-insight-badge" style="background:#ffffff;color:{accent};border:1px solid {accent}33;">{escape(badge)}</span>
    </div>
    """).strip()


def _traffic_trend_figure(df, current_label="Current", prior_label="Prior"):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Month"], y=df["Current"], mode="lines+markers", name=current_label,
        line=dict(color="#7C3AED", width=2.8),
        marker=dict(size=5, color="#ffffff", line=dict(color="#7C3AED", width=2)),
    ))
    fig.add_trace(go.Scatter(
        x=df["Month"], y=df["Prior"], mode="lines+markers", name=prior_label,
        line=dict(color="#C4B5FD", width=2, dash="dash"),
        marker=dict(size=4, color="#ffffff", line=dict(color="#C4B5FD", width=1.5)),
    ))
    fig.update_layout(
        autosize=True, height=300, margin=dict(t=8, b=8, l=8, r=8),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", hovermode="x unified",
        font=dict(family=TM_FONT, size=11, color="#475569"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#64748B"), fixedrange=True),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", zeroline=False,
                   tickfont=dict(size=11, color="#64748B"), fixedrange=True),
    )
    return fig


def _dom_intl_figure(df):
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["Month"], y=df["Domestic"], name="Domestic",
        marker_color="#2563EB", marker_line_width=0,
    ))
    fig.add_trace(go.Bar(
        x=df["Month"], y=df["International"], name="International",
        marker_color="#06B6D4", marker_line_width=0,
    ))
    fig.update_layout(
        barmode="stack", autosize=True, height=300, margin=dict(t=8, b=8, l=8, r=8),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", hovermode="x unified",
        font=dict(family=TM_FONT, size=11, color="#475569"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#64748B"), fixedrange=True),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", zeroline=False,
                   tickfont=dict(size=11, color="#64748B"), fixedrange=True),
    )
    return fig


def _spp_trend_figure(df, target=90.0):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Month"], y=df["SPP"], mode="lines+markers", name="SPP",
        line=dict(color="#D97706", width=2.8),
        marker=dict(size=5, color="#ffffff", line=dict(color="#D97706", width=2)),
        fill="tozeroy", fillcolor="rgba(217,119,6,0.08)",
    ))
    fig.add_hline(y=target, line_dash="dot", line_color="#94A3B8", line_width=1.5,
                  annotation_text="Target Rp 90K", annotation_position="top right")
    fig.update_layout(
        autosize=True, height=280, margin=dict(t=8, b=8, l=8, r=8),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", hovermode="x unified",
        showlegend=False,
        font=dict(family=TM_FONT, size=11, color="#475569"),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#64748B"), fixedrange=True),
        yaxis=dict(showgrid=True, gridcolor="#E2E8F0", zeroline=False,
                   tickfont=dict(size=11, color="#64748B"), fixedrange=True),
    )
    return fig


def _donut_figure(labels, values, total_label):
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.62, sort=False,
        marker=dict(colors=TM_DONUT_COLORS[: len(labels)], line=dict(color="#ffffff", width=2)),
        textinfo="none",
        hovertemplate="%{label}<br>%{value:.1f}M<extra></extra>",
    )])
    fig.update_layout(
        height=260, margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff", showlegend=False,
        annotations=[dict(
            text=f"<b>{total_label}</b><br><span style='font-size:11px;color:#64748B'>TOTAL PAX</span>",
            x=0.5, y=0.5, font=dict(size=13, color="#0F172A", family=TM_FONT), showarrow=False,
        )],
    )
    return fig


def _yoy_bar_figure(rows):
    names = [r["code"] for r in rows]
    values = [r["yoy"] for r in rows]
    colors = [r["color"] for r in rows]
    fig = go.Figure(go.Bar(
        x=values, y=names, orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=[f"+{v:.1f}%" for v in values], textposition="outside",
        textfont=dict(size=11, color="#475569", family=TM_FONT),
    ))
    fig.update_layout(
        autosize=True, height=180, margin=dict(t=8, b=8, l=8, r=36),
        plot_bgcolor="#ffffff", paper_bgcolor="#ffffff",
        font=dict(family=TM_FONT, size=11, color="#475569"),
        xaxis=dict(showgrid=True, gridcolor="#E2E8F0", zeroline=False, ticksuffix="%",
                   tickfont=dict(size=11, color="#64748B"), fixedrange=True),
        yaxis=dict(showgrid=False, tickfont=dict(size=11, color="#64748B"), fixedrange=True),
    )
    return fig


def _inject_tm_css():
    inject_enterprise_page_css("tm-page-marker", extra_css=dedent(f"""
    body:has(.tm-page-marker) .nad-top-divider {{ display: none !important; }}

    body:has(.tm-page-marker),
    body:has(.tm-page-marker) .stApp,
    body:has(.tm-page-marker) [data-testid="stAppViewContainer"],
    body:has(.tm-page-marker) [data-testid="stMain"],
    body:has(.tm-page-marker) section.main {{
        height: 100vh !important;
        max-height: 100vh !important;
        overflow: hidden !important;
    }}

    body:has(.tm-page-marker) [data-testid="stMainBlockContainer"] {{
        height: 100vh !important;
        max-height: 100vh !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        overscroll-behavior: contain !important;
        scroll-behavior: smooth;
        padding-bottom: 28px !important;
        box-sizing: border-box !important;
    }}

    body:has(.tm-page-marker) .tm-fixed-header-active {{
        position: fixed !important;
        top: 0 !important;
        right: 0 !important;
        z-index: 200 !important;
        background: #F8FAFC !important;
        border-bottom: 1px solid #E2E8F0 !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.08) !important;
        padding: 14px 28px 12px !important;
        margin: 0 !important;
        width: auto !important;
        box-sizing: border-box !important;
    }}

    body:has(.tm-page-marker) .tm-fixed-header-spacer {{
        display: block;
        height: var(--tm-header-height, 84px);
        width: 100%;
        flex-shrink: 0;
    }}

    body:has(.tm-page-marker) .tm-sticky-header-marker,
    body:has(.tm-page-marker) .tm-sticky-header-end {{
        display: none;
    }}

    body:has(.tm-page-marker) .tm-page-header {{
        display: flex; align-items: flex-start; justify-content: flex-start; gap: 16px;
        margin: 0 0 0; padding: 0;
    }}
    body:has(.tm-page-marker) .tm-page-header-left {{
        display: flex; align-items: center; gap: 12px; min-width: 0;
    }}
    body:has(.tm-page-marker) .tm-page-icon {{
        width: 42px; height: 42px; flex: 0 0 42px; border-radius: 12px;
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
        color: #ffffff; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.18);
    }}
    body:has(.tm-page-marker) .tm-page-icon svg {{
        width: 20px; height: 20px;
    }}
    body:has(.tm-page-marker) .tm-page-header-copy {{
        display: flex; flex-direction: column; justify-content: center; gap: 1px;
        min-height: 42px; min-width: 0;
    }}
    body:has(.tm-page-marker) .tm-page-title-row {{
        display: flex; align-items: center; gap: 10px; min-height: 22px;
    }}
    body:has(.tm-page-marker) .tm-page-title {{
        margin: 0; font-size: 20px; line-height: 1.08; font-weight: 800;
        color: #0F172A; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-page-sub {{
        margin: 0; color: #64748B; font-size: 12.5px; line-height: 1.12;
        font-weight: 500; font-family: {TM_FONT} !important;
    }}
    @keyframes tmFilterBadgeIn {{
        0% {{ transform: translateY(2px) scale(0.98); opacity: 0.72; }}
        100% {{ transform: translateY(0) scale(1); opacity: 1; }}
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row):has([data-testid="stSelectbox"]) {{
        align-items: center !important;
        gap: 14px !important;
        margin: 0 0 14px !important;
        padding: 12px 18px !important;
        background: #ffffff !important;
        border: 1px solid #EEF2F7 !important;
        border-radius: 10px !important;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.06) !important;
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row):has([data-testid="stSelectbox"]) .overview-filter-label {{
        display: none !important;
    }}
    body:has(.tm-page-marker) .tm-filter-label-row {{
        display: flex; align-items: center; gap: 10px;
        height: 32px; padding-right: 18px; border-right: 1px solid #E5EAF3;
    }}
    body:has(.tm-page-marker) .tm-filter-icon {{
        display: inline-flex; width: 16px; height: 16px; color: #0F172A; flex: 0 0 16px;
    }}
    body:has(.tm-page-marker) .tm-filter-icon svg {{
        width: 16px; height: 16px;
    }}
    body:has(.tm-page-marker) .tm-filter-title {{
        font-size: 13px; font-weight: 800; color: #0F172A; white-space: nowrap;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row) [data-testid="column"] {{
        min-width: 0 !important;
        display: flex !important;
        align-items: center !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row) div[data-testid="stSelectbox"] {{
        width: 100% !important;
        max-width: 168px !important;
    }}
    body:has(.tm-page-marker) [data-testid="column"]:has(.tm-filter-kind-month) div[data-testid="stSelectbox"] {{
        max-width: 190px !important;
    }}
    body:has(.tm-page-marker) [data-testid="column"]:has(.tm-filter-kind-terminal) div[data-testid="stSelectbox"] {{
        max-width: 220px !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row) div[data-testid="stElementContainer"]:has(div[data-testid="stSelectbox"]) {{
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row) div[data-testid="stSelectbox"] label {{
        display: none !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row) div[data-baseweb="select"] > div {{
        min-height: 34px !important;
        height: 34px !important;
        border: 1px solid #E5EAF3 !important;
        border-radius: 9px !important;
        background: #ffffff !important;
        box-shadow: none !important;
        padding-left: 34px !important;
        padding-right: 30px !important;
        color: #64748B !important;
        position: relative !important;
        transition: background 180ms ease, border-color 180ms ease, box-shadow 180ms ease, color 180ms ease, transform 180ms ease !important;
    }}
    body:has(.tm-page-marker) [data-testid="column"]:has(.tm-filter-state-active) div[data-baseweb="select"] > div {{
        border-color: #DFE9FF !important;
        background: #EEF4FF !important;
        box-shadow: 0 3px 10px rgba(37, 99, 235, 0.08) !important;
        color: #2563EB !important;
        animation: tmFilterBadgeIn 180ms ease-out both;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row) div[data-baseweb="select"] > div::before {{
        content: "";
        position: absolute;
        left: 12px;
        top: 50%;
        width: 15px;
        height: 15px;
        transform: translateY(-50%);
        background: currentColor;
        color: #64748B;
        -webkit-mask: var(--tm-filter-icon, url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='18' rx='2' ry='2'/%3E%3Cline x1='16' y1='2' x2='16' y2='6'/%3E%3Cline x1='8' y1='2' x2='8' y2='6'/%3E%3Cline x1='3' y1='10' x2='21' y2='10'/%3E%3C/svg%3E")) center / contain no-repeat;
        mask: var(--tm-filter-icon, url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='4' width='18' height='18' rx='2' ry='2'/%3E%3Cline x1='16' y1='2' x2='16' y2='6'/%3E%3Cline x1='8' y1='2' x2='8' y2='6'/%3E%3Cline x1='3' y1='10' x2='21' y2='10'/%3E%3C/svg%3E")) center / contain no-repeat;
    }}
    body:has(.tm-page-marker) [data-testid="column"]:has(.tm-filter-state-active) div[data-baseweb="select"] > div::before {{
        color: #2563EB;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row) div[data-baseweb="select"] > div::after {{
        content: "+";
        position: absolute;
        right: 12px;
        top: 50%;
        transform: translateY(-50%) rotate(45deg);
        color: #94A3B8;
        font-size: 15px;
        font-weight: 500;
        line-height: 1;
        opacity: 0;
        transition: opacity 160ms ease, color 160ms ease, transform 160ms ease;
    }}
    body:has(.tm-page-marker) [data-testid="column"]:has(.tm-filter-state-active) div[data-baseweb="select"] > div::after {{
        color: #2563EB;
        opacity: 1;
    }}
    body:has(.tm-page-marker) .tm-filter-marker {{
        display: none !important;
    }}
    body:has(.tm-page-marker) div[data-testid="stElementContainer"]:has(.tm-filter-marker) {{
        display: none !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row) [data-testid="column"]:has(.tm-filter-kind-terminal) div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        --tm-filter-icon: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='4' y='2' width='16' height='20' rx='2' ry='2'/%3E%3Cpath d='M9 22v-4h6v4'/%3E%3Cpath d='M8 6h.01'/%3E%3Cpath d='M16 6h.01'/%3E%3Cpath d='M8 10h.01'/%3E%3Cpath d='M16 10h.01'/%3E%3Cpath d='M8 14h.01'/%3E%3Cpath d='M16 14h.01'/%3E%3C/svg%3E");
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row) div[data-baseweb="select"] [data-testid="stMarkdownContainer"],
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row) div[data-baseweb="select"] div {{
        color: inherit !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-label-row) div[data-baseweb="select"] svg {{
        display: none !important;
    }}
    body:has(.tm-page-marker) .tm-filter-actions {{
        display: flex; justify-content: flex-start; gap: 8px; align-items: center; height: 34px; width: 100%;
    }}
    body:has(.tm-page-marker) .tm-filter-btn {{
        display: inline-flex; align-items: center; gap: 6px;
        min-height: 34px; padding: 0 14px; border-radius: 9px; font-size: 12px; font-weight: 800;
        font-family: {TM_FONT} !important; border: 1px dashed #BBD2FF; background: #ffffff; color: #2563EB;
        white-space: nowrap;
    }}
    body:has(.tm-page-marker) .tm-kpi-grid {{
        display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 10px; width: 100%;
    }}
    body:has(.tm-page-marker) .tm-kpi-card {{
        display: flex; flex-direction: column; gap: 6px; min-height: 132px; padding: 14px 16px;
        border-radius: 12px; border: 1px solid #E2E8F0; background: #ffffff;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04); box-sizing: border-box;
    }}
    body:has(.tm-page-marker) .tm-kpi-top {{
        display: flex; align-items: center; justify-content: space-between;
    }}
    body:has(.tm-page-marker) .tm-kpi-icon {{
        width: 34px; height: 34px; border-radius: 9px; display: flex; align-items: center;
        justify-content: center; font-size: 15px; font-weight: 700;
    }}
    body:has(.tm-page-marker) .tm-kpi-badge {{
        padding: 3px 8px; border-radius: 999px; font-size: 10px; font-weight: 700; white-space: nowrap;
    }}
    body:has(.tm-page-marker) .tm-kpi-label {{
        color: #64748B; font-size: 10px; font-weight: 700; letter-spacing: 0.35px;
        text-transform: uppercase; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-kpi-value {{
        color: #0F172A; font-size: 22px; font-weight: 800; line-height: 1.1; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-kpi-sub {{
        color: #94A3B8; font-size: 10.5px; font-weight: 500; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-sparkline {{
        width: 100%; height: 28px; margin-top: auto;
    }}
    body:has(.tm-page-marker) .tm-mini-metrics {{
        display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin: 10px 0 12px;
    }}
    body:has(.tm-page-marker) .tm-mini-metric {{
        display: flex; flex-direction: column; gap: 4px; padding: 10px 12px; border-radius: 10px; border: 1px solid;
    }}
    body:has(.tm-page-marker) .tm-mini-label {{
        font-size: 10px; font-weight: 700; color: #64748B; text-transform: uppercase; letter-spacing: 0.3px;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-mini-value {{
        font-size: 16px; font-weight: 800; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-mini-sub {{
        font-size: 10px; color: #94A3B8; font-weight: 500; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-yoy-pill {{
        display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 999px;
        background: #DCFCE7; color: #059669; font-size: 11px; font-weight: 700; white-space: nowrap;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-terminal-stack {{
        display: flex; flex-direction: column; gap: 10px; margin-top: 8px;
    }}
    body:has(.tm-page-marker) .tm-terminal-card {{
        padding: 14px; border-radius: 12px; border: 1px solid; background: #ffffff;
    }}
    body:has(.tm-page-marker) .tm-terminal-head {{
        display: flex; align-items: center; gap: 10px; margin-bottom: 10px;
    }}
    body:has(.tm-page-marker) .tm-terminal-id {{
        width: 34px; height: 34px; border-radius: 999px; display: flex; align-items: center;
        justify-content: center; font-size: 11px; font-weight: 800; flex: 0 0 34px;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-terminal-copy {{ flex: 1; min-width: 0; }}
    body:has(.tm-page-marker) .tm-terminal-name {{
        margin: 0; font-size: 13px; font-weight: 700; color: #0F172A; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-terminal-meta {{
        margin: 2px 0 0; font-size: 11px; color: #64748B; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-terminal-stats {{ text-align: right; }}
    body:has(.tm-page-marker) .tm-terminal-total {{
        margin: 0; font-size: 16px; font-weight: 800; color: #0F172A; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-terminal-share {{
        margin: 2px 0 0; font-size: 10px; color: #64748B; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-terminal-foot {{
        display: flex; justify-content: space-between; margin-top: 10px; font-size: 11px;
        color: #64748B; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-split-bar {{
        display: flex; height: 8px; border-radius: 999px; overflow: hidden; margin-top: 10px;
        background: #E2E8F0;
    }}
    body:has(.tm-page-marker) .tm-split-dom {{ background: #2563EB; }}
    body:has(.tm-page-marker) .tm-split-intl {{ background: #06B6D4; }}
    body:has(.tm-page-marker) .tm-split-legend {{
        display: flex; justify-content: space-between; margin-top: 8px; font-size: 11px; color: #64748B;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-insight-grid {{
        display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 10px; margin-top: 12px;
    }}
    body:has(.tm-page-marker) .tm-insight-card {{
        padding: 16px; border-radius: 12px; border: 1px solid; min-height: 148px;
        display: flex; flex-direction: column; gap: 8px;
    }}
    body:has(.tm-page-marker) .tm-insight-title {{
        margin: 0; font-size: 13px; font-weight: 800; color: #0F172A; line-height: 1.35;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-insight-body {{
        margin: 0; font-size: 11px; color: #64748B; line-height: 1.5; flex: 1;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-insight-badge {{
        display: inline-flex; align-self: flex-start; padding: 4px 10px; border-radius: 999px;
        font-size: 10px; font-weight: 700; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-positive {{ color: #059669; font-weight: 700; }}
    body:has(.tm-page-marker) .tm-subcell {{
        display: block; font-size: 10px; color: #94A3B8; font-weight: 500; margin-top: 2px;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-spp-tag {{
        display: inline-block; margin-top: 4px; padding: 2px 8px; border-radius: 999px;
        font-size: 10px; font-weight: 700; font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) .tm-spp-tag.is-above {{
        background: #DCFCE7; color: #059669;
    }}
    body:has(.tm-page-marker) .tm-spp-tag.is-below {{
        background: #FFEDD5; color: #EA580C;
    }}
    body:has(.tm-page-marker) .tm-table-wrap .ed-table-scroll {{
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        overflow: hidden;
    }}
    body:has(.tm-page-marker) .tm-table-wrap .ed-table tbody tr:last-child {{
        background: #F8FAFC; font-weight: 700;
    }}
    body:has(.tm-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tm-insights-card),
    body:has(.tm-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tm-performance-card) {{
        padding: 18px 20px !important;
    }}
    @media (max-width: 1400px) {{
        body:has(.tm-page-marker) .tm-kpi-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
        body:has(.tm-page-marker) .tm-insight-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    """))


def page_traffic_monitor(df_raw=None):
    st.markdown('<div class="overview-page-marker tm-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    _inject_tm_css()
    data_df = get_traffic_monitor_data(df_raw)

    for key, default in [
        ("tm_year", "Year"),
        ("tm_month", "Month"),
        ("tm_terminal", "Terminal"),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    if not st.session_state.get("_tm_filter_defaults_migrated"):
        old_defaults = {
            "tm_year": "2024",
            "tm_month": "All Months",
            "tm_terminal": "All Terminals",
        }
        new_defaults = {
            "tm_year": "Year",
            "tm_month": "Month",
            "tm_terminal": "Terminal",
        }
        for key, old_default in old_defaults.items():
            if st.session_state.get(key) == old_default:
                st.session_state[key] = new_defaults[key]
        st.session_state["_tm_filter_defaults_migrated"] = True

    year_options = ["Year"] + (
        [str(int(year)) for year in sorted(data_df["tahun"].dropna().unique(), reverse=True)]
        if not data_df.empty else []
    )
    month_options = ["Month", "All Months"] + [
        month for month in TM_MONTH_OPTIONS[2:]
        if not data_df.empty and month in set(data_df["masa_jasa"].dropna())
    ]
    if len(month_options) == 2:
        month_options = TM_MONTH_OPTIONS
    terminal_options = ["Terminal", "All Terminals"] + (
        sorted(data_df["terminal"].dropna().unique().tolist()) if not data_df.empty else []
    )

    if st.session_state.tm_year not in year_options:
        st.session_state.tm_year = "Year"
    if st.session_state.tm_month not in month_options:
        st.session_state.tm_month = "Month"
    if st.session_state.tm_terminal not in terminal_options:
        st.session_state.tm_terminal = "Terminal"

    metrics = _aggregate_metrics(
        data_df,
        st.session_state.tm_year,
        st.session_state.tm_month,
        st.session_state.tm_terminal,
    )
    trend_df = get_monthly_traffic_trend(data_df, st.session_state.tm_year, st.session_state.tm_terminal)
    dom_intl_df = get_domestic_intl_monthly(data_df, st.session_state.tm_year, st.session_state.tm_terminal)
    spp_df = get_spp_monthly(data_df, st.session_state.tm_year, st.session_state.tm_terminal)
    current_year_label = f"FY {metrics['current_year']}" if metrics["current_year"] else "Current"
    prior_year_label = f"FY {metrics['prior_year']}" if metrics["prior_year"] else "Prior"
    scope_label = metrics["terminal_label"]

    with st.container():
        st.markdown('<div class="tm-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_tm_page_header(), unsafe_allow_html=True)

        st.markdown('<div class="tm-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="tm-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)
    _mount_tm_fixed_header()

    ff0, ff1, ff2, ff3, ff4 = st.columns([1.15, 1.35, 1.55, 1.75, 1.45])
    with ff0:
        st.markdown(_filter_bar_html(), unsafe_allow_html=True)
    with ff1:
        st.markdown(_filter_state_marker("year", st.session_state.tm_year != "Year"), unsafe_allow_html=True)
        st.selectbox("Year", year_options, key="tm_year", label_visibility="collapsed")
    with ff2:
        st.markdown(_filter_state_marker("month", st.session_state.tm_month != "Month"), unsafe_allow_html=True)
        st.selectbox("Month", month_options, key="tm_month", label_visibility="collapsed")
    with ff3:
        st.markdown(_filter_state_marker("terminal", st.session_state.tm_terminal != "Terminal"), unsafe_allow_html=True)
        st.selectbox("Terminal", terminal_options, key="tm_terminal", label_visibility="collapsed")
    with ff4:
        st.markdown(
            '<div class="tm-filter-actions">'
            '<span class="tm-filter-btn">+ Tambah Filter</span>'
            "</div>",
            unsafe_allow_html=True,
        )

    spark_total = trend_df["Current"].tolist()
    spark_dom = dom_intl_df["Domestic"].tolist()
    spark_intl = dom_intl_df["International"].tolist()
    spark_spp = spp_df["SPP"].tolist()

    kpi_html = "".join([
        _tm_kpi_card("Total Traffic", _fmt_millions(metrics["total"]),
                     f"{current_year_label} · {scope_label}", metrics["yoy"], "#7C3AED", "👥", spark_total),
        _tm_kpi_card("Domestic Traffic", _fmt_millions(metrics["domestic"]),
                     f"{metrics['domestic_pct']:.1f}% of total traffic", metrics["yoy"] * 0.9,
                     "#2563EB", "📍", spark_dom),
        _tm_kpi_card("International Traffic", _fmt_millions(metrics["international"]),
                     f"{metrics['intl_pct']:.1f}% of total traffic", metrics["yoy"] * 1.05,
                     "#06B6D4", "🌐", spark_intl),
        _tm_kpi_card("Spending Per Pax", _fmt_rp_k(metrics["spp"]),
                     "Average across selected terminals", 6.6, "#D97706", "💳", spark_spp),
        _tm_kpi_card("Traffic Growth", f"+{metrics['yoy']:.1f}%",
                     f"YoY vs {prior_year_label}", metrics["yoy"], "#059669", "📈", spark_total),
        _tm_kpi_card("Avg Spending Per Pax", _fmt_rp_k(metrics["spp"]),
                     "Weighted terminal average", 6.6, "#EA580C", "🛍", spark_spp),
    ])
    st.markdown(f'<div class="tm-kpi-grid">{kpi_html}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    row1_left, row1_right = st.columns([1.55, 1], gap="small")
    peak_month = trend_df.loc[trend_df["Current"].idxmax(), "Month"] if not trend_df.empty else "-"
    peak_value = trend_df["Current"].max() if not trend_df.empty else 0

    with row1_left:
        st.markdown('<div class="ed-card-marker tm-trend-card"></div>', unsafe_allow_html=True)
        h1, h2 = st.columns([3.2, 1])
        with h1:
            st.markdown(section_title_html(
                "Total Traffic Trend",
                f"Monthly passengers — {current_year_label} vs {prior_year_label} (Millions) · {scope_label}",
            ), unsafe_allow_html=True)
        with h2:
            st.markdown(f'<span class="tm-yoy-pill">YoY +{metrics["yoy"]:.1f}%</span>', unsafe_allow_html=True)
        st.markdown(
            '<div class="tm-mini-metrics">'
            + _mini_metric_box(current_year_label, _fmt_millions(metrics["total"]), accent="#7C3AED")
            + _mini_metric_box(prior_year_label, _fmt_millions(metrics["prior_total"]), accent="#94A3B8")
            + _mini_metric_box("Peak Month", f"{peak_month} · {peak_value:.1f}M", accent="#2563EB")
            + _mini_metric_box("Growth", f"+{metrics['yoy']:.1f}%", accent="#059669")
            + "</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(_traffic_trend_figure(trend_df, current_year_label, prior_year_label), use_container_width=True,
                        config={"displayModeBar": False})

    with row1_right:
        st.markdown('<div class="ed-card-marker tm-split-card"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Domestic vs International",
            f"Monthly split — {current_year_label} (Millions) · {scope_label}",
        ), unsafe_allow_html=True)
        st.markdown(
            '<div class="tm-mini-metrics" style="grid-template-columns:repeat(2,minmax(0,1fr));">'
            + _mini_metric_box("Domestic", _fmt_millions(metrics["domestic"]),
                               f"{metrics['domestic_pct']:.1f}% share", "#2563EB")
            + _mini_metric_box("International", _fmt_millions(metrics["international"]),
                               f"{metrics['intl_pct']:.1f}% share", "#06B6D4")
            + "</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(_dom_intl_figure(dom_intl_df), use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f'<div class="tm-split-bar">'
            f'<div class="tm-split-dom" style="width:{metrics["domestic_pct"]:.1f}%;"></div>'
            f'<div class="tm-split-intl" style="width:{metrics["intl_pct"]:.1f}%;"></div>'
            f"</div>"
            f'<div class="tm-split-legend">'
            f'<span>Domestic {metrics["domestic_pct"]:.1f}%</span>'
            f'<span>International {metrics["intl_pct"]:.1f}%</span>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    row2_a, row2_b, row2_c = st.columns([1.15, 1.05, 0.95], gap="small")
    spp_avg = spp_df["SPP"].mean()
    spp_peak = spp_df["SPP"].max()
    spp_peak_month = spp_df.loc[spp_df["SPP"].idxmax(), "Month"]
    achievement = (spp_avg / 90 - 1) * 100

    with row2_a:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Spending per Pax Trend",
            f"Monthly Rp '000 per passenger vs Rp 90K target · {scope_label}",
        ), unsafe_allow_html=True)
        st.markdown(
            '<div class="tm-mini-metrics" style="grid-template-columns:repeat(4,minmax(0,1fr));">'
            + _mini_metric_box(f"{current_year_label} Avg", _fmt_rp_k(metrics["spp"]), accent="#D97706")
            + _mini_metric_box("Dec Peak", _fmt_rp_k(spp_peak * 1000), spp_peak_month, "#EA580C")
            + _mini_metric_box("Target", "Rp 90.0K", accent="#64748B")
            + _mini_metric_box("Achievement", f"+{achievement:.1f}%", accent="#059669")
            + "</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(_spp_trend_figure(spp_df), use_container_width=True, config={"displayModeBar": False})

    with row2_b:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Traffic by Terminal",
            f"Annual passengers (Millions) — {current_year_label}",
        ), unsafe_allow_html=True)
        cards = []
        all_metrics = _aggregate_metrics(data_df, st.session_state.tm_year, st.session_state.tm_month, "All Terminals")
        for row in all_metrics["rows"]:
            cards.append(_terminal_card_html(row, all_metrics["shares"][row["name"]]))
        st.markdown(f'<div class="tm-terminal-stack">{"".join(cards)}</div>', unsafe_allow_html=True)

    with row2_c:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Traffic Distribution",
            f"Contribution by terminal — {current_year_label} · All Terminals",
        ), unsafe_allow_html=True)
        labels = [r["name"] for r in all_metrics["rows"]]
        values = [r["total"] for r in all_metrics["rows"]]
        chart_slot, legend_slot = st.columns([1.05, 1], gap="small")
        with chart_slot:
            st.plotly_chart(
                _donut_figure(labels, values, _fmt_millions(all_metrics["total"])),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        with legend_slot:
            st.markdown(
                donut_legend_html(labels, values, TM_DONUT_COLORS, sum(values), _fmt_millions),
                unsafe_allow_html=True,
            )
        st.markdown(section_title_html("YoY Growth by Terminal", ""), unsafe_allow_html=True)
        st.plotly_chart(_yoy_bar_figure(all_metrics["rows"]), use_container_width=True,
                        config={"displayModeBar": False})

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    top_row = max(all_metrics["rows"], key=lambda row: row["total"], default=None)
    top_name = top_row["name"] if top_row else "No terminal"
    top_total = top_row["total"] if top_row else 0
    top_share = all_metrics["shares"].get(top_name, 0) if top_row else 0
    top_spp = top_row["spp"] if top_row else 0
    intl_mix = (metrics["international"] / metrics["total"] * 100) if metrics["total"] else 0

    with st.container():
        st.markdown('<div class="ed-card-marker tm-insights-card"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Executive Insights",
            f"Traffic & spending analysis · {current_year_label} · {scope_label}",
        ), unsafe_allow_html=True)
        st.markdown(
            '<div class="tm-insight-grid">'
            + _insight_card_html(
                f"{top_name} leads at {top_total:.1f}M pax ({top_share:.1f}%)",
                "Traffic leader is calculated directly from the latest Import Manager traffic table.",
                f"{top_share:.1f}% share",
                "#0891B2", "#ECFEFF",
            )
            + _insight_card_html(
                f"Traffic growth {metrics['yoy']:+.1f}% YoY",
                f"{scope_label} traffic reached {_fmt_millions(metrics['total'])} vs {_fmt_millions(metrics['prior_total'])} in {prior_year_label}.",
                f"{metrics['yoy']:+.1f}% YoY",
                "#059669", "#F0FDF4",
            )
            + _insight_card_html(
                f"SPP at {_fmt_rp_k(metrics['spp'])}",
                "Spending per passenger is calculated from imported revenue and traffic values.",
                f"{(metrics['spp'] / 90_000 - 1) * 100:+.1f}% vs target",
                "#D97706", "#FFF7ED",
            )
            + _insight_card_html(
                f"International mix {intl_mix:.1f}%",
                f"Top terminal SPP is {_fmt_rp_k(top_spp)}, based on the current imported period.",
                f"{_fmt_rp_k(top_spp)} top SPP",
                "#7C3AED", "#F5F3FF",
            )
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    table_df = get_terminal_table_df(all_metrics)
    display_df = table_df.drop(columns=["_share", "_total"]).copy()
    col_align = {
        "Domestic Traffic": "right",
        "International Traffic": "right",
        "Total Traffic": "right",
        "Traffic Share": "right",
        "Spending Per Pax": "right",
        "YoY Growth": "right",
    }

    with st.container():
        st.markdown('<div class="ed-card-marker tm-performance-card"></div>', unsafe_allow_html=True)
        th1, th2 = st.columns([3.5, 1])
        with th1:
            st.markdown(section_title_html(
                "Traffic Performance by Terminal",
                "Annual traffic and spending summary — FY 2024 · Terminal 1 & Terminal 2",
            ), unsafe_allow_html=True)
        with th2:
            st.markdown('<div class="ed-card-action">Export</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="tm-table-wrap">{table_inner_html(display_df, col_align=col_align)}</div>',
            unsafe_allow_html=True,
        )
