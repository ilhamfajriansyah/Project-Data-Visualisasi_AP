"""Traffic Monitor dashboard — Terminal 1 & Terminal 2 only."""

from html import escape
from textwrap import dedent

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import streamlit.components.v1 as components

from .enterprise_ui import (
    ED_FONT,
    donut_legend_html,
    inject_enterprise_page_css,
    progress_bar_html,
    section_title_html,
    table_inner_html,
)
TM_FONT = ED_FONT
TM_YEAR_OPTIONS = ["All Year", "2030", "2029", "2028", "2027", "2026", "2025", "2024", "2023"]
TM_MONTH_OPTIONS = ["All Month", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
TM_TERMINAL_OPTIONS = ["All Terminal", "Terminal 1", "Terminal 2"]
TM_DONUT_COLORS = ["#7C3AED", "#06B6D4"]
TM_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

TERMINAL_PROFILES = {
    "Terminal 1": {
        "code": "T1",
        "color": "#7C3AED",
        "soft_bg": "#F5F3FF",
        "domestic": 14.2,
        "international": 5.8,
        "spp": 88_200,
        "yoy": 8.4,
    },
    "Terminal 2": {
        "code": "T2",
        "color": "#06B6D4",
        "soft_bg": "#ECFEFF",
        "domestic": 16.8,
        "international": 11.4,
        "spp": 102_400,
        "yoy": 13.2,
    },
}


def _terminal_rows():
    rows = []
    for name, profile in TERMINAL_PROFILES.items():
        total = profile["domestic"] + profile["international"]
        rows.append({**profile, "name": name, "total": total})
    return rows


def _aggregate_metrics(terminal_filter="All Terminal"):
    term_map = {"T1": "Terminal 1", "T2": "Terminal 2"}
    normalized_filter = term_map.get(terminal_filter, terminal_filter)
    rows = _terminal_rows()
    if normalized_filter != "All Terminal":
        rows = [r for r in rows if r["name"] == normalized_filter]

    total = sum(r["total"] for r in rows)
    domestic = sum(r["domestic"] for r in rows)
    international = sum(r["international"] for r in rows)
    if total:
        spp = sum(r["spp"] * r["total"] for r in rows) / total
        yoy = sum(r["yoy"] * r["total"] for r in rows) / total
    else:
        spp = yoy = 0

    shares = {r["name"]: (r["total"] / total * 100 if total else 0) for r in rows}
    prior_total = total / (1 + yoy / 100) if yoy else total

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
    }


def _fmt_millions(value):
    return f"{value:.1f}".replace(".", ",") + " Jt"


def _fmt_rp_k(value):
    return f"Rp {value / 1_000:.1f}".replace(".", ",") + " K"


def _monthly_traffic_series(total_m, seed=7):
    rng = np.random.default_rng(seed)
    weights = rng.uniform(0.85, 1.15, 12)
    weights = weights / weights.sum()
    return (weights * total_m).tolist()


def get_monthly_traffic_trend(terminal_filter="All Terminal"):
    metrics = _aggregate_metrics(terminal_filter)
    current = _monthly_traffic_series(metrics["total"], seed=11)
    prior = _monthly_traffic_series(metrics["prior_total"], seed=23)
    return pd.DataFrame({
        "Month": TM_MONTHS,
        "FY 2024": current,
        "FY 2023": prior,
    })


def get_domestic_intl_monthly(terminal_filter="All Terminal"):
    metrics = _aggregate_metrics(terminal_filter)
    dom_series = _monthly_traffic_series(metrics["domestic"], seed=31)
    intl_series = _monthly_traffic_series(metrics["international"], seed=37)
    return pd.DataFrame({
        "Month": TM_MONTHS,
        "Domestic": dom_series,
        "International": intl_series,
    })


def get_spp_monthly(terminal_filter="All Terminal"):
    metrics = _aggregate_metrics(terminal_filter)
    base = metrics["spp"] / 1_000
    rng = np.random.default_rng(45)
    values = base + rng.uniform(-8, 14, 12)
    return pd.DataFrame({"Month": TM_MONTHS, "SPP": values})


def get_terminal_table_df():
    metrics = _aggregate_metrics("All Terminal")
    rows = []
    for row in metrics["rows"]:
        total = row["total"]
        dom_pct = row["domestic"] / total * 100 if total else 0
        intl_pct = row["international"] / total * 100 if total else 0
        share = metrics["shares"][row["name"]]
        spp_status = "Above target" if row["spp"] >= 90_000 else "Below target"
        rows.append({
            "Terminal": f'{row["code"]} {row["name"]}',
            "Domestic Traffic": f'<div class="tm-cell-stack">{f"{row["domestic"]:.1f}".replace(".", ",")} Jt<span class="tm-subcell">{dom_pct:.0f}% dari terminal</span></div>',
            "International Traffic": f'<div class="tm-cell-stack">{f"{row["international"]:.1f}".replace(".", ",")} Jt<span class="tm-subcell">{intl_pct:.0f}% dari terminal</span></div>',
            "Total Traffic": f'{f"{total:.1f}".replace(".", ",")} Jt',
            "Traffic Share": f"{f"{share:.1f}".replace(".", ",")}%",
            "Spending Per Pax": f'<div class="tm-cell-stack">{_fmt_rp_k(row["spp"])}<span class="tm-spp-tag {"is-above" if row["spp"] >= 90_000 else "is-below"}">{spp_status}</span></div>',
            "YoY Growth": f'<span class="tm-positive">↑ +{f"{row["yoy"]:.1f}".replace(".", ",")}%</span>',
            "_share": share,
            "_total": total,
        })

    total_dom = metrics["domestic"]
    total_intl = metrics["international"]
    total_all = metrics["total"]
    rows.append({
        "Terminal": "TOTAL — Terminal 1 & 2",
        "Domestic Traffic": f"{total_dom:.1f}".replace(".", ",") + " Jt",
        "International Traffic": f"{total_intl:.1f}".replace(".", ",") + " Jt",
        "Total Traffic": f"{total_all:.1f}".replace(".", ",") + " Jt",
        "Traffic Share": "100%",
        "Spending Per Pax": _fmt_rp_k(metrics["spp"]),
        "YoY Growth": f'<span class="tm-positive">↑ +{f"{metrics["yoy"]:.1f}".replace(".", ",")}%</span>',
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
    
    # Process unit to extract prefix (like "Rp") and suffix (like "Jt", "K", "%" or empty)
    prefix = ""
    val_part = str(value)
    suffix = ""
    
    # Format delta percentage
    delta_formatted = f"{abs(delta_pct):.1f}".replace(".", ",")
    
    # Format subtitle
    subtitle_formatted = str(subtitle).translate(str.maketrans({',': '.', '.': ','}))
    
    if value.startswith("Rp"):
        prefix = "Rp "
        rest = value[2:].strip()
        # Extract suffix like "K" or "Jt"
        for sfx in ["K", "Jt", "M", "T"]:
            if rest.endswith(sfx):
                suffix = sfx
                val_part = rest[:-len(sfx)].strip()
                break
        else:
            val_part = rest
    else:
        # Check if value ends with "Jt" or "%"
        for sfx in ["Jt", "K", "%"]:
            if value.endswith(sfx):
                suffix = sfx
                val_part = value[:-len(sfx)].strip()
                break
                
    # Replace dot with comma in value part (decimals)
    val_part = val_part.replace(".", ",")
    
    unit_span = f'<span class="tm-kpi-unit" style="font-size:13px;color:#64748b;margin-left:2px;font-weight:600;"> {escape(suffix)}</span>' if suffix else ""
    
    html = (
        f'<div class="tm-kpi-card">'
        f'<div class="tm-kpi-top">'
        f'<div class="tm-kpi-icon" style="background:{accent}14;color:{accent};">{escape(icon)}</div>'
        f'<span class="tm-kpi-badge" style="background:{badge_bg};color:{badge_fg};">{arrow} {delta_formatted}%</span>'
        f'</div>'
        f'<div class="tm-kpi-label">{escape(label)}</div>'
        f'<div class="tm-kpi-value">'
        f'<span class="tm-kpi-val-num">{escape(prefix)}{escape(val_part)}</span>'
        f'{unit_span}'
        f'</div>'
        f'<div class="tm-kpi-sub">{escape(subtitle_formatted)}</div>'
        f'{_sparkline_svg(spark_values, accent)}'
        f'</div>'
    )
    return html


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


def _filter_bar_v2_html(active_count: int) -> str:
    badge = (
        f'<span class="tm-filter-v2-badge">'
        f'<span class="tm-filter-v2-dot"></span>&nbsp;{active_count} active'
        f'</span>'
        if active_count > 0 else ""
    )
    return dedent(f"""
    <div class="tm-filter-v2-label">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none"
             stroke="currentColor" stroke-width="2.5"
             stroke-linecap="round" stroke-linejoin="round">
            <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>
        </svg>
        Filter Aktif
        {badge}
    </div>
    """).strip()


def _filter_chip_state_css() -> str:
    """Inject per-chip color based on whether the filter is at its default value."""
    _DEFAULTS = {"tm_terminal": "All Terminal", "tm_year": "All Year", "tm_month": "All Month"}
    # columns: label=1st-child, terminal=2nd, year=3rd, month=4th
    _NTH = {"tm_terminal": 2, "tm_year": 3, "tm_month": 4}

    rules = []
    for key, default in _DEFAULTS.items():
        nth = _NTH[key]
        is_active = st.session_state.get(key, default) != default
        if is_active:
            bg, border, color, svg = "#EEF2FF", "#C7D2FE", "#4338CA", "#818CF8"
        else:
            bg, border, color, svg = "#F8FAFC", "#E2E8F0", "#94A3B8", "#CBD5E1"
        base = (
            f"body:has(.tm-page-marker) "
            f"[data-testid='stHorizontalBlock']:has(.tm-filter-v2-label) "
            f"> div:nth-child({nth}) "
            f"[data-testid='stSelectbox'] > div[data-baseweb='select'] > div:first-child"
        )
        rules.append(f"{base} {{ background:{bg}!important; border-color:{border}!important; color:{color}!important; }}")
        rules.append(f"{base} svg {{ fill:{svg}!important; }}")

    return f"<style>{''.join(rules)}</style>"


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
                <p class="tm-terminal-meta">Dom {f"{row['domestic']:.1f}".replace(".", ",")} Jt · Intl {f"{row['international']:.1f}".replace(".", ",")} Jt</p>
            </div>
            <div class="tm-terminal-stats">
                <p class="tm-terminal-total">{f"{row['total']:.1f}".replace(".", ",")} Jt</p>
                <p class="tm-terminal-share">{f"{share:.1f}".replace(".", ",")}% share</p>
            </div>
        </div>
        {progress_bar_html(share, row['color'])}
        <div class="tm-terminal-foot">
            <span>SPP: {_fmt_rp_k(row['spp'])}</span>
            <span>YoY Growth: <strong style="color:#059669;">+{f"{row['yoy']:.1f}".replace(".", ",")}%</strong></span>
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


def _traffic_trend_figure(df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Month"], y=df["FY 2024"], mode="lines+markers", name="FY 2024",
        line=dict(color="#7C3AED", width=2.8),
        marker=dict(size=5, color="#ffffff", line=dict(color="#7C3AED", width=2)),
    ))
    fig.add_trace(go.Scatter(
        x=df["Month"], y=df["FY 2023"], mode="lines+markers", name="FY 2023",
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
                  annotation_text="Target Rp 90 K", annotation_position="top right")
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
    st.markdown("<style>@import url('https://cdn.jsdelivr.net/gh/lykmapipo/themify-icons@0.1.2/css/themify-icons.css'); @import url('https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css');</style>", unsafe_allow_html=True)
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
        padding-top: 8px !important;
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
        height: 93px !important;
        min-height: 93px !important;
        max-height: 93px !important;
        padding: 0 28px !important;
        margin: 0 !important;
        width: auto !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        overflow: hidden !important;
    }}

    body:has(.tm-page-marker) .tm-fixed-header-spacer {{
        display: block;
        height: 93px;
        width: 100%;
        flex-shrink: 0;
    }}

    body:has(.tm-page-marker) .tm-sticky-header-marker,
    body:has(.tm-page-marker) .tm-sticky-header-end {{
        display: none;
    }}

    body:has(.tm-page-marker) [data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tm-sticky-header-marker) {{
        gap: 0 !important;
        height: 100% !important;
        justify-content: center !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tm-sticky-header-marker) > div[data-testid="stElementContainer"] {{
        margin: 0 !important;
        padding: 0 !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-sticky-header-marker) {{
        height: 100% !important;
        display: flex !important;
        align-items: center !important;
    }}

    body:has(.tm-page-marker) .tm-page-header {{
        display: flex; align-items: center; justify-content: flex-start; gap: 16px;
        margin: 0; padding: 0;
        height: 100%;
    }}
    body:has(.tm-page-marker) .tm-page-header-left {{
        display: flex; align-items: center; gap: 12px; min-width: 0;
    }}
    body:has(.tm-page-marker) .tm-page-icon {{
        width: 36px; height: 36px; flex: 0 0 36px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
        color: #ffffff; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.18);
    }}
    body:has(.tm-page-marker) .tm-page-icon svg {{
        width: 18px; height: 18px;
    }}
    body:has(.tm-page-marker) .tm-page-header-copy {{
        display: flex; flex-direction: column; justify-content: center; gap: 4px !important;
        min-height: 36px; min-width: 0;
    }}
    body:has(.tm-page-marker) .tm-page-title-row {{
        display: flex; align-items: center; gap: 10px; min-height: 0 !important;
        margin: 0 !important; padding: 0 !important;
    }}
    body:has(.tm-page-marker) h2.tm-page-title {{
        margin: 0 !important; padding: 0 !important;
        font-size: 18px; line-height: 1 !important; font-weight: 800;
        color: #0F172A; font-family: 'Montserrat', sans-serif !important;
    }}
    body:has(.tm-page-marker) p.tm-page-sub {{
        margin: 0 !important; padding: 0 !important;
        color: #64748B; font-size: 12px; line-height: 1 !important;
        font-weight: 500; font-family: {TM_FONT} !important;
    }}
    /* ── Filter bar v2 ──────────────────────────────────────────── */
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) {{
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 16px !important;
        margin-top: -28px !important;
        margin-bottom: 0px !important;
        padding: 6px 16px !important;
        background: #ffffff !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        box-shadow: 0 1px 3px rgba(15,23,42,0.05) !important;
        flex-wrap: nowrap !important;
        width: fit-content !important;
    }}
    /* Center columns vertically and remove default Streamlit paddings/margins */
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) > div {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        padding: 0 !important;
        margin: 0 !important;
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: 0 !important;
    }}
    /* Keep the separator on Filter Aktif from causing alignment issues */
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) > div:first-child {{
        display: flex !important;
        align-items: center !important;
    }}
    /* Separator after "Filter Aktif" has the same height as the area filter and does not push alignment */
    body:has(.tm-page-marker) .tm-filter-v2-label {{
        display: flex; align-items: center; gap: 7px;
        padding-right: 18px; border-right: 1.5px solid #E2E8F0;
        white-space: nowrap; line-height: 1;
        font-size: 13px; font-weight: 700; color: #475569;
        font-family: {TM_FONT} !important;
        height: 38px !important;
        box-sizing: border-box !important;
    }}
    /* Spacing of 24px between the last dropdown (Month, 4th child) and Clear All (5th child) */
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) > div:nth-child(5) {{
        margin-left: 8px !important;
    }}
    /* Perfect horizontal and vertical centering for all components in the capsule */
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) [data-testid="stVerticalBlock"] {{
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
        padding: 0 !important;
        gap: 0 !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) [data-testid="stElementContainer"] {{
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) [data-testid="stSelectbox"] {{
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        width: 180px !important;
        flex-shrink: 0 !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) [data-testid="stButton"] {{
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) [data-testid="stMarkdownContainer"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    body:has(.tm-page-marker) .tm-filter-v2-badge {{
        display: inline-flex; align-items: center; gap: 4px;
        padding: 2px 8px; border-radius: 999px;
        background: #F0FDF4; border: 1px solid #BBF7D0;
        font-size: 10.5px; font-weight: 700; color: #16A34A;
        white-space: nowrap; font-family: {TM_FONT} !important;
        flex-shrink: 0;
    }}
    body:has(.tm-page-marker) .tm-filter-v2-dot {{
        width: 6px; height: 6px; border-radius: 50%;
        background: #16A34A; display: inline-block; flex-shrink: 0;
    }}
    /* Selectboxes inside filter bar → chip style with 180px width */
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) [data-testid="stSelectbox"] {{
        margin: 0 !important;
        width: 180px !important;
        flex-shrink: 0 !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) [data-testid="stSelectbox"] > div[data-baseweb="select"] {{
        width: 180px !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) [data-testid="stSelectbox"] > div[data-baseweb="select"] > div:first-child {{
        border-radius: 12px !important;
        background: #F8FAFC !important;
        border: 1px solid #E2E8F0 !important;
        min-height: 38px !important; height: 38px !important;
        width: 180px !important;
        padding: 0 12px 0 16px !important;
        display: flex !important; align-items: center !important;
        box-sizing: border-box !important;
        font-size: 13px !important; font-weight: 600 !important;
        color: #94A3B8 !important; font-family: {TM_FONT} !important;
        transition: all 0.2s ease !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) [data-testid="stSelectbox"] > div[data-baseweb="select"] > div:first-child svg {{
        fill: #CBD5E1 !important;
        flex-shrink: 0 !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) [data-testid="stSelectbox"] > div[data-baseweb="select"] > div:first-child:hover {{
        border-color: #6366F1 !important;
        background: #ffffff !important;
    }}
    /* Clear All Button */
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) [data-testid="baseButton-secondary"] {{
        border: 1px solid #E2E8F0 !important; border-radius: 12px !important;
        background: #ffffff !important; color: #475569 !important;
        font-size: 13px !important; font-weight: 700 !important;
        min-height: 38px !important; height: 38px !important;
        width: auto !important; padding: 0 16px !important;
        font-family: {TM_FONT} !important; white-space: nowrap !important;
        transition: all 0.2s ease !important;
        box-shadow: none !important;
        margin: 0 !important;
    }}
    body:has(.tm-page-marker) [data-testid="stHorizontalBlock"]:has(.tm-filter-v2-label) [data-testid="baseButton-secondary"]:hover {{
        border-color: #6366F1 !important;
        color: #6366F1 !important;
        background: #F8FAFC !important;
    }}
    body:has(.tm-page-marker) .tm-kpi-grid {{
        display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; width: 100%;
        margin-top: -4px !important;
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
    body:has(.tm-page-marker) .tm-sparkline polyline {{
        stroke-linecap: round !important;
        stroke-linejoin: round !important;
    }}
    body:has(.tm-page-marker) .tm-mini-metrics {{
        display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin: 10px 0 12px;
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
        display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 12px; margin-top: 12px;
    }}
    body:has(.tm-page-marker) .tm-insight-card {{
        padding: 16px; border-radius: 12px; border: 1px solid; min-height: 148px;
        display: flex; flex-direction: column; gap: 8px;
    }}
    body:has(.tm-page-marker) .tm-insight-title {{
        margin: 0; font-size: 13px; font-weight: 800; color: #0F172A; line-height: 1.35;
        font-family: 'Montserrat', sans-serif !important;
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

    /* ── Filter Card Container ── */
    body:has(.tm-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tm-filter-container-marker) {{
        background: #ffffff !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 16px !important;
        padding: 16px 20px !important;
        box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05) !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
        margin-bottom: 16px !important;
    }}
    body:has(.tm-page-marker) .tm-filter-container-marker {{
        display: none !important;
    }}

    /* ── Filter Chips Bar (Redesigned horizontal component) ── */
    body:has(.tm-page-marker) .active-filter-bar-wrap {{
        display: none !important; /* marker only */
    }}
    
    body:has(.tm-page-marker) div[data-testid="stHorizontalBlock"]:has(.active-filter-bar-wrap) {{
        display: flex !important;
        align-items: center !important;
        gap: 8px !important;
        padding: 8px 16px !important;
        background: #F6F8FD !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 30px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        margin-bottom: 0 !important;
        box-shadow: none !important;
    }}

    body:has(.tm-page-marker) div[data-testid="stHorizontalBlock"]:has(.active-filter-bar-wrap) [data-testid="column"],
    body:has(.tm-page-marker) div[data-testid="stHorizontalBlock"]:has(.active-filter-bar-wrap) [data-testid="stColumn"] {{
        width: auto !important;
        min-width: 0 !important;
        flex: 0 0 auto !important;
        padding: 0 !important;
    }}

    body:has(.tm-page-marker) div[data-testid="stHorizontalBlock"]:has(.active-filter-bar-wrap) [data-testid="column"]:has(.filter-spacer-marker),
    body:has(.tm-page-marker) div[data-testid="stHorizontalBlock"]:has(.active-filter-bar-wrap) [data-testid="stColumn"]:has(.filter-spacer-marker) {{
        flex: 1 1 auto !important;
    }}

    body:has(.tm-page-marker) .filter-chip-marker,
    body:has(.tm-page-marker) .add-filter-marker,
    body:has(.tm-page-marker) .filter-spacer-marker,
    body:has(.tm-page-marker) .clear-all-marker,
    body:has(.tm-page-marker) .apply-marker {{
        display: none !important;
    }}

    body:has(.tm-page-marker) .filter-aktif-label {{
        font-size: 13px !important;
        color: #64748B !important; /* secondary */
        font-weight: 500 !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        white-space: nowrap !important;
        font-family: {TM_FONT} !important;
        border: none !important;
        border-right: 1px solid #e0e0e0 !important;
        background: transparent !important;
        padding-right: 16px !important;
        margin-right: 8px !important;
        height: 24px !important;
    }}
    body:has(.tm-page-marker) .filter-aktif-label::before {{
        content: "\\e6a2" !important; /* ti-filter */
        font-family: 'themify' !important;
        font-size: 16px !important;
        color: #64748B !important;
    }}

    body:has(.tm-page-marker) [data-testid="column"]:has(.filter-chip-marker) button,
    body:has(.tm-page-marker) [data-testid="stColumn"]:has(.filter-chip-marker) button {{
        background: #E6F1FB !important;
        border: 1px solid #B5D4F4 !important;
        border-radius: 20px !important;
        padding: 5px 10px !important;
        font-size: 13px !important;
        color: #0C447C !important;
        font-weight: 400 !important;
        height: auto !important;
        min-height: 0 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        box-shadow: none !important;
        cursor: pointer !important;
        line-height: 1.2 !important;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) [data-testid="column"]:has(.filter-chip-marker) button:hover,
    body:has(.tm-page-marker) [data-testid="stColumn"]:has(.filter-chip-marker) button:hover {{
        background: #D9ECFA !important;
        border-color: #94C4F0 !important;
    }}

    body:has(.tm-page-marker) [data-testid="column"]:has(.filter-chip-marker.year-chip) button::before,
    body:has(.tm-page-marker) [data-testid="stColumn"]:has(.filter-chip-marker.year-chip) button::before,
    body:has(.tm-page-marker) [data-testid="column"]:has(.filter-chip-marker.month-chip) button::before,
    body:has(.tm-page-marker) [data-testid="stColumn"]:has(.filter-chip-marker.month-chip) button::before {{
        content: "\\e6b6" !important; /* ti-calendar */
        font-family: 'themify' !important;
        color: #185FA5 !important;
        font-size: 14px !important;
    }}

    body:has(.tm-page-marker) [data-testid="column"]:has(.filter-chip-marker.terminal-chip) button::before,
    body:has(.tm-page-marker) [data-testid="stColumn"]:has(.filter-chip-marker.terminal-chip) button::before {{
        content: "\\f1dd" !important; /* bi-building from Bootstrap Icons */
        font-family: 'bootstrap-icons' !important;
        color: #185FA5 !important;
        font-size: 14px !important;
    }}

    body:has(.tm-page-marker) [data-testid="column"]:has(.filter-chip-marker) button::after,
    body:has(.tm-page-marker) [data-testid="stColumn"]:has(.filter-chip-marker) button::after {{
        content: "×" !important;
        font-size: 13px !important;
        color: #185FA5 !important;
        font-weight: normal !important;
        cursor: pointer !important;
        margin-left: 0 !important;
    }}

    body:has(.tm-page-marker) [data-testid="column"]:has(.add-filter-marker) button,
    body:has(.tm-page-marker) [data-testid="stColumn"]:has(.add-filter-marker) button {{
        border: 1.5px dashed #B5D4F4 !important;
        border-radius: 20px !important;
        padding: 5px 14px !important;
        background: transparent !important;
        font-size: 13px !important;
        color: #378ADD !important;
        height: auto !important;
        min-height: 0 !important;
        box-shadow: none !important;
        cursor: pointer !important;
        line-height: 1.2 !important;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) [data-testid="column"]:has(.add-filter-marker) button:hover,
    body:has(.tm-page-marker) [data-testid="stColumn"]:has(.add-filter-marker) button:hover {{
        background: #F0F7FF !important;
        border-color: #378ADD !important;
    }}

    body:has(.tm-page-marker) .active-indicator-wrapper {{
        font-size: 13px !important;
        color: #475569 !important;
        display: flex !important;
        align-items: center !important;
        gap: 6px !important;
        white-space: nowrap !important;
        font-family: {TM_FONT} !important;
        background: #F1F5F9 !important;
        border-radius: 20px !important;
        padding: 4px 10px !important;
    }}
    body:has(.tm-page-marker) .dot-green {{
        color: #22C55E !important;
        background: #DCFCE7 !important;
        border-radius: 50% !important;
        width: 14px !important;
        height: 14px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        font-size: 6px !important;
        line-height: 1 !important;
    }}

    body:has(.tm-page-marker) [data-testid="column"]:has(.clear-all-marker) button,
    body:has(.tm-page-marker) [data-testid="stColumn"]:has(.clear-all-marker) button {{
        background: white !important;
        border: 0.5px solid #d0d0d0 !important;
        border-radius: 8px !important;
        padding: 6px 14px !important;
        font-size: 13px !important;
        color: #444 !important;
        height: auto !important;
        min-height: 0 !important;
        box-shadow: none !important;
        cursor: pointer !important;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) [data-testid="column"]:has(.clear-all-marker) button:hover,
    body:has(.tm-page-marker) [data-testid="stColumn"]:has(.clear-all-marker) button:hover {{
        background: #F8FAFC !important;
        border-color: #94A3B8 !important;
    }}

    body:has(.tm-page-marker) [data-testid="column"]:has(.apply-marker) button,
    body:has(.tm-page-marker) [data-testid="stColumn"]:has(.apply-marker) button {{
        background: #378ADD !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 6px 18px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        height: auto !important;
        min-height: 0 !important;
        box-shadow: none !important;
        cursor: pointer;
        font-family: {TM_FONT} !important;
    }}
    body:has(.tm-page-marker) [data-testid="column"]:has(.apply-marker) button:hover,
    body:has(.tm-page-marker) [data-testid="stColumn"]:has(.apply-marker) button:hover {{
        background: #2D78C8 !important;
    }}

    body:has(.tm-page-marker) .tm-filter-selectbox-container {{
        display: none !important;
    }}

    @media (max-width: 1400px) {{
        body:has(.tm-page-marker) .tm-kpi-grid {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
        body:has(.tm-page-marker) .tm-insight-grid {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
    }}
    """))


def clear_tm_filters():
    st.session_state.tm_year = "All Year"
    st.session_state.tm_month = "All Month"
    st.session_state.tm_terminal = "All Terminal"


def page_traffic_monitor():
    for key, default in [
        ("tm_year", "All Year"),
        ("tm_month", "All Month"),
        ("tm_terminal", "All Terminal"),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    metrics = _aggregate_metrics(st.session_state.tm_terminal)
    trend_df = get_monthly_traffic_trend(st.session_state.tm_terminal)
    dom_intl_df = get_domestic_intl_monthly(st.session_state.tm_terminal)
    spp_df = get_spp_monthly(st.session_state.tm_terminal)

    active_count = sum([
        st.session_state.get("tm_year", "All Year") != "All Year",
        st.session_state.get("tm_month", "All Month") != "All Month",
        st.session_state.get("tm_terminal", "All Terminal") != "All Terminal",
    ])

    st.markdown('<div class="overview-page-marker tm-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    _inject_tm_css()

    with st.container():
        st.markdown('<div class="tm-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_tm_page_header(), unsafe_allow_html=True)
        st.markdown('<div class="tm-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="tm-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)

    ff0, ff1, ff2, ff3, ff4 = st.columns(
        [0.85, 1.1, 1.1, 1.1, 0.85], gap="small"
    )
    with ff0:
        st.markdown(_filter_bar_v2_html(active_count), unsafe_allow_html=True)
    with ff1:
        st.selectbox("Terminal", TM_TERMINAL_OPTIONS, key="tm_terminal", label_visibility="collapsed")
    with ff2:
        st.selectbox("Tahun", TM_YEAR_OPTIONS, key="tm_year", label_visibility="collapsed")
    with ff3:
        st.selectbox("Bulan", TM_MONTH_OPTIONS, key="tm_month", label_visibility="collapsed")
    with ff4:
        st.button("Clear All", key="tm_clear_all", use_container_width=True, on_click=clear_tm_filters)

    _mount_tm_fixed_header()
    st.markdown(_filter_chip_state_css(), unsafe_allow_html=True)

    yoy_val_str = f"{metrics['yoy']:.1f}".replace(".", ",")
    domestic_pct_str = f"{metrics['domestic_pct']:.1f}".replace(".", ",")
    intl_pct_str = f"{metrics['intl_pct']:.1f}".replace(".", ",")

    spark_total = trend_df["FY 2024"].tolist()
    spark_dom = dom_intl_df["Domestic"].tolist()
    spark_intl = dom_intl_df["International"].tolist()
    spark_spp = spp_df["SPP"].tolist()

    kpi_html = "".join([
        _tm_kpi_card("Total Traffic", _fmt_millions(metrics["total"]),
                     "FY 2024 · Terminal 1 & 2", metrics["yoy"], "#7C3AED", "👥", spark_total),
        _tm_kpi_card("Domestic Traffic", _fmt_millions(metrics["domestic"]),
                     f"{domestic_pct_str}% of total traffic", metrics["yoy"] * 0.9,
                     "#2563EB", "📍", spark_dom),
        _tm_kpi_card("International Traffic", _fmt_millions(metrics["international"]),
                     f"{intl_pct_str}% of total traffic", metrics["yoy"] * 1.05,
                     "#06B6D4", "🌐", spark_intl),
        _tm_kpi_card("Spending Per Pax", _fmt_rp_k(metrics["spp"]),
                     "Average across selected terminals", 6.6, "#D97706", "💳", spark_spp),
        _tm_kpi_card("Traffic Growth", f"+{yoy_val_str}%",
                     "YoY vs FY 2023", metrics["yoy"], "#059669", "📈", spark_total),
        _tm_kpi_card("Avg Spending Per Pax", _fmt_rp_k(metrics["spp"]),
                     "Weighted terminal average", 6.6, "#EA580C", "🛍", spark_spp),
    ])
    st.markdown(f'<div class="tm-kpi-grid">{kpi_html}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    row1_left, row1_right = st.columns([1.55, 1], gap="small")
    peak_month = trend_df.loc[trend_df["FY 2024"].idxmax(), "Month"]
    peak_value = trend_df["FY 2024"].max()

    with row1_left:
        st.markdown('<div class="ed-card-marker tm-trend-card"></div>', unsafe_allow_html=True)
        h1, h2 = st.columns([3.2, 1])
        with h1:
            st.markdown(section_title_html(
                "Total Traffic Trend",
                "Monthly passengers — FY 2024 vs FY 2023 (Millions) · Terminal 1 & 2",
            ), unsafe_allow_html=True)
        st.markdown(f'<span class="tm-yoy-pill">YoY +{yoy_val_str} %</span>', unsafe_allow_html=True)
        st.markdown(
            '<div class="tm-mini-metrics">'
            + _mini_metric_box("FY 2024", _fmt_millions(metrics["total"]), accent="#7C3AED")
            + _mini_metric_box("FY 2023", _fmt_millions(metrics["prior_total"]), accent="#94A3B8")
            + _mini_metric_box("Peak Month", f"{peak_month} · {f'{peak_value:.1f}'.replace('.', ',')} Jt", accent="#2563EB")
            + _mini_metric_box("Growth", f"+{yoy_val_str}%", accent="#059669")
            + "</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(_traffic_trend_figure(trend_df), use_container_width=True,
                        config={"displayModeBar": False})

    with row1_right:
        st.markdown('<div class="ed-card-marker tm-split-card"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Domestic vs International",
            "Monthly split — FY 2024 (Juta) · Terminal 1 & 2",
        ), unsafe_allow_html=True)
        st.markdown(
            '<div class="tm-mini-metrics" style="grid-template-columns:repeat(2,minmax(0,1fr));">'
            + _mini_metric_box("Domestic", _fmt_millions(metrics["domestic"]),
                               f"{domestic_pct_str}% share", "#2563EB")
            + _mini_metric_box("International", _fmt_millions(metrics["international"]),
                               f"{intl_pct_str}% share", "#06B6D4")
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
            f'<span>Domestic {domestic_pct_str}%</span>'
            f'<span>International {intl_pct_str}%</span>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    row2_a, row2_b, row2_c = st.columns([1.15, 1.05, 0.95], gap="small")
    spp_avg = spp_df["SPP"].mean()
    spp_peak = spp_df["SPP"].max()
    spp_peak_month = spp_df.loc[spp_df["SPP"].idxmax(), "Month"]
    achievement = (spp_avg / 90 - 1) * 100

    with row2_a:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Spending per Pax Trend",
            "Monthly Rp '000 per passenger vs Rp 90K target · Terminal 1 & 2",
        ), unsafe_allow_html=True)
        st.markdown(
            '<div class="tm-mini-metrics" style="grid-template-columns:repeat(4,minmax(0,1fr));">'
            + _mini_metric_box("FY 2024 Avg", _fmt_rp_k(metrics["spp"]), accent="#D97706")
            + _mini_metric_box("Dec Peak", _fmt_rp_k(spp_peak * 1000), spp_peak_month, "#EA580C")
            + _mini_metric_box("Target", "Rp 90,0 K", accent="#64748B")
            + _mini_metric_box("Achievement", f"+{f'{achievement:.1f}'.replace('.', ',')}%", accent="#059669")
            + "</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(_spp_trend_figure(spp_df), use_container_width=True, config={"displayModeBar": False})

    with row2_b:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Traffic by Terminal",
            "Annual passengers (Juta) — FY 2024",
        ), unsafe_allow_html=True)
        cards = []
        all_metrics = _aggregate_metrics("All Terminal")
        for row in all_metrics["rows"]:
            cards.append(_terminal_card_html(row, all_metrics["shares"][row["name"]]))
        st.markdown(f'<div class="tm-terminal-stack">{"".join(cards)}</div>', unsafe_allow_html=True)

    with row2_c:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Traffic Distribution",
            "Contribution by terminal — FY 2024 · Terminal 1 & 2",
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

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    t2 = TERMINAL_PROFILES["Terminal 2"]
    t1 = TERMINAL_PROFILES["Terminal 1"]
    t2_total = t2["domestic"] + t2["international"]
    t2_share = t2_total / (t1["domestic"] + t1["international"] + t2_total) * 100
    intl_premium = t2["spp"] / t1["spp"]

    t2_total_str = f"{t2_total:.1f}".replace(".", ",")
    t2_share_str = f"{t2_share:.1f}".replace(".", ",")
    achievement_str = f"{(metrics['spp'] / 90_000 - 1) * 100:.1f}".replace(".", ",")
    intl_premium_str = f"{intl_premium:.1f}".replace(".", ",")

    with st.container():
        st.markdown('<div class="ed-card-marker tm-insights-card"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Executive Insights",
            "AI-powered traffic & spending analysis · FY 2024 · Terminal 1 & Terminal 2",
        ), unsafe_allow_html=True)
        st.markdown(
            '<div class="tm-insight-grid">'
            + _insight_card_html(
                f"Terminal 2 leads at {t2_total_str} M pax ({t2_share_str}%)",
                "Terminal 2 carries the larger international mix and higher SPP, driving overall airport commercial performance.",
                f"T2 · {t2_share_str}%",
                "#0891B2", "#ECFEFF",
            )
            + _insight_card_html(
                f"Terminals grew +{yoy_val_str}% YoY — above 8% target",
                f"Combined Terminal 1 & 2 traffic reached {_fmt_millions(metrics['total'])} vs {_fmt_millions(metrics['prior_total'])} in FY 2023.",
                f"+{yoy_val_str}% vs 8% target",
                "#059669", "#F0FDF4",
            )
            + _insight_card_html(
                f"SPP at {_fmt_rp_k(metrics['spp'])} — above Rp 90 K target",
                "Terminal 2 exceeds the spending target while Terminal 1 remains below target, creating a blended uplift across both terminals.",
                f"+{achievement_str}% above target",
                "#D97706", "#FFF7ED",
            )
            + _insight_card_html(
                "International pax spend more per passenger",
                f"Terminal 2 international mix supports higher SPP at {_fmt_rp_k(t2['spp'])} compared with Terminal 1 at {_fmt_rp_k(t1['spp'])}.",
                f"{intl_premium_str}x T2 vs T1 SPP",
                "#7C3AED", "#F5F3FF",
            )
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    table_df = get_terminal_table_df()
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
