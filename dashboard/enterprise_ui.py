"""Reusable enterprise dashboard UI components (HTML/CSS helpers)."""

from html import escape
from textwrap import dedent

import numpy as np
import pandas as pd

ED_FONT = "Poppins, sans-serif"


def fmt_rp_compact(value):
    if pd.isna(value):
        value = 0
    if value >= 1_000_000_000_000:
        return f"Rp {value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"Rp {value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"Rp {value / 1_000_000:.2f}M"
    return f"Rp {value:,.0f}"


def fmt_rp_full(value):
    if pd.isna(value):
        value = 0
    return f"Rp {value:,.0f}"


def fmt_status_badge(status, extra_colors=None):
    colors = {
        "SUCCESS": ("rgba(16,185,129,0.12)", "#059669", "rgba(16,185,129,0.24)"),
        "FAILED": ("rgba(244,63,94,0.11)", "#e11d48", "rgba(244,63,94,0.22)"),
        "RESERVED": ("rgba(99,102,241,0.12)", "#4f46e5", "rgba(99,102,241,0.24)"),
        "PAID": ("rgba(16,185,129,0.12)", "#059669", "rgba(16,185,129,0.24)"),
        "SENT": ("rgba(37,99,235,0.12)", "#2563EB", "rgba(37,99,235,0.24)"),
        "PENDING": ("rgba(245,158,11,0.13)", "#d97706", "rgba(245,158,11,0.24)"),
        "OVERDUE": ("rgba(244,63,94,0.11)", "#e11d48", "rgba(244,63,94,0.22)"),
        "WARNING": ("rgba(245,158,11,0.13)", "#d97706", "rgba(245,158,11,0.24)"),
    }
    if extra_colors:
        colors.update(extra_colors)
    bg, fg, border = colors.get(status, ("rgba(148,163,184,0.12)", "#64748b", "rgba(148,163,184,0.22)"))
    return (
        f'<span style="background:{bg};color:{fg};padding:3px 10px;'
        f'border:1px solid {border};border-radius:999px;font-size:11px;'
        f'font-weight:700;letter-spacing:0.2px;white-space:nowrap;">{status}</span>'
    )


def format_mom(value):
    cls = "ed-positive" if value >= 0 else "ed-negative"
    arrow = "↑" if value >= 0 else "↓"
    return f'<span class="{cls}">{arrow} {abs(value):.1f}%</span>'


def filter_label(label):
    return f'<p class="overview-filter-label">{escape(label)}</p>'


def section_title_html(title, subtitle=None):
    sub = f'<p class="ed-section-sub">{escape(subtitle)}</p>' if subtitle else ""
    return f'<p class="ed-section-title">{escape(title)}</p>{sub}'


def kpi_card_html(label, value, delta, delta_up, accent, icon):
    delta_bg = "#DCFCE7" if delta_up else "#FEE2E2"
    delta_fg = "#059669" if delta_up else "#DC2626"
    arrow = "↑" if delta_up else "↓"
    return dedent(f"""
    <div class="overview-kpi-card ed-kpi-card">
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


def kpi_grid_html(*cards):
    return f'<div class="ed-kpi-grid">{"".join(cards)}</div>'


def alert_card_html(severity, icon, title, subtitle):
    styles = {
        "critical": ("#FEE2E2", "#DC2626", "#FECACA"),
        "warning": ("#FFEDD5", "#EA580C", "#FED7AA"),
        "positive": ("#DCFCE7", "#059669", "#BBF7D0"),
        "info": ("#DBEAFE", "#2563EB", "#BFDBFE"),
    }
    bg, accent, border = styles.get(severity, styles["warning"])
    return (
        f'<div class="ed-alert-card" style="background:{bg};border-color:{border};">'
        f'<div class="ed-alert-card-icon" style="background:#ffffff;color:{accent};border:1px solid {border};">{escape(icon)}</div>'
        f'<div class="ed-alert-card-copy">'
        f'<p class="ed-alert-card-title">{escape(title)}</p>'
        f'<p class="ed-alert-card-sub">{escape(subtitle)}</p>'
        f"</div>"
        f'<div class="ed-alert-card-chevron">&rsaquo;</div>'
        f"</div>"
    )


def alert_grid_html(*alerts):
    return f'<div class="ed-alert-grid">{"".join(alerts)}</div>'


def progress_bar_html(pct, color="#059669"):
    pct = max(0, min(float(pct), 100))
    return (
        f'<div class="ed-progress-track"><div class="ed-progress-bar" '
        f'style="width:{pct:.0f}%;background:{color};"></div></div>'
    )


def _table_col_class(col_name, col_align, prefix="ed-th"):
    align = (col_align or {}).get(str(col_name), "left")
    return f"{prefix}-{align}"


def table_inner_html(df, col_align=None):
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
            if text.startswith("<span ") or text.startswith("<div ") or text.startswith("<a "):
                cells.append(f'<td class="{td_class}">{text}</td>')
            else:
                cells.append(f'<td class="{td_class}">{escape(text)}</td>')
        rows_html += f"<tr>{''.join(cells)}</tr>"
    return dedent(f"""
    <div class="ed-table-scroll ed-table-scroll-sticky">
        <table class="ed-table">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """).strip()


def table_card_html(df, title=None, subtitle=None, col_align=None, link_label=None):
    col_align = col_align or {}
    head_html = ""
    if title:
        link_html = f'<span class="ed-table-link">{escape(link_label)}</span>' if link_label else ""
        if subtitle:
            head_html = dedent(f"""
            <div class="ed-table-head-stack">
                <div class="ed-table-head-copy">
                    <p class="ed-table-title">{escape(title)}</p>
                    <p class="ed-table-subtitle">{escape(subtitle)}</p>
                </div>
                {link_html}
            </div>
            """).strip()
        else:
            head_html = dedent(f"""
            <div class="ed-table-head">
                <p class="ed-table-title">{escape(title)}</p>
                {link_html}
            </div>
            """).strip()
    return dedent(f"""
    <div class="ed-table-card">
        {head_html}
        {table_inner_html(df, col_align=col_align)}
    </div>
    """).strip()


def donut_legend_html(labels, values, colors, total_value, fmt_value=fmt_rp_compact):
    rows = []
    total = sum(values) or 1
    for idx, (label, val) in enumerate(zip(labels, values)):
        pct = val / total * 100
        color = colors[idx % len(colors)]
        rows.append(
            f'<div class="ed-legend-row">'
            f'<div class="ed-legend-left">'
            f'<span class="ed-legend-dot" style="background:{color};"></span>'
            f"<span>{escape(label)}</span>"
            f"</div>"
            f'<span class="ed-legend-value">{pct:.0f}% · {escape(fmt_value(val))}</span>'
            f"</div>"
        )
    return f'<div class="ed-donut-legend">{"".join(rows)}</div>'


def inject_enterprise_page_css(page_marker_class, extra_css=""):
    st_css = dedent(f"""
    <style>
    .{page_marker_class} {{ display: none; }}

    body:has(.{page_marker_class}) .ed-kpi-grid {{
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 12px;
        width: 100%;
    }}
    body:has(.{page_marker_class}) .ed-kpi-grid .ed-kpi-card {{
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
    }}
    body:has(.{page_marker_class}) .ed-alert-grid {{
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
        margin-top: 12px;
    }}
    body:has(.{page_marker_class}) .ed-alert-card {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 14px 16px;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
    }}
    body:has(.{page_marker_class}) .ed-alert-card-icon {{
        width: 36px;
        height: 36px;
        flex: 0 0 36px;
        border-radius: 999px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
        font-weight: 900;
    }}
    body:has(.{page_marker_class}) .ed-alert-card-title {{
        margin: 0;
        color: #0F172A;
        font-size: 12.5px;
        font-weight: 700;
        line-height: 1.35;
        font-family: {ED_FONT} !important;
    }}
    body:has(.{page_marker_class}) .ed-alert-card-sub {{
        margin: 3px 0 0;
        color: #64748B;
        font-size: 11px;
        font-weight: 500;
        font-family: {ED_FONT} !important;
    }}
    body:has(.{page_marker_class}) .ed-alert-card-chevron {{
        margin-left: auto;
        color: #94A3B8;
        font-size: 18px;
        font-weight: 700;
    }}
    body:has(.{page_marker_class}) .ed-donut-legend {{
        display: flex;
        flex-direction: column;
        gap: 8px;
        padding-top: 8px;
    }}
    body:has(.{page_marker_class}) .ed-legend-row {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        font-size: 11.5px;
        color: #475569;
        font-family: {ED_FONT} !important;
    }}
    body:has(.{page_marker_class}) .ed-legend-left {{
        display: flex;
        align-items: center;
        gap: 8px;
        min-width: 0;
    }}
    body:has(.{page_marker_class}) .ed-legend-dot {{
        width: 8px;
        height: 8px;
        border-radius: 999px;
        flex: 0 0 8px;
    }}
    body:has(.{page_marker_class}) .ed-legend-value {{
        color: #0F172A;
        font-weight: 700;
        white-space: nowrap;
    }}
    body:has(.{page_marker_class}) .ed-progress-track {{
        background: #E2E8F0;
        border-radius: 999px;
        height: 6px;
        overflow: hidden;
        margin-top: 8px;
    }}
    body:has(.{page_marker_class}) .ed-progress-bar {{
        height: 6px;
        border-radius: inherit;
    }}
    body:has(.{page_marker_class}) .ed-outstanding-row {{
        padding: 12px 0;
        border-bottom: 1px solid #F1F5F9;
    }}
    body:has(.{page_marker_class}) .ed-outstanding-row:last-child {{
        border-bottom: none;
    }}
    body:has(.{page_marker_class}) .ed-outstanding-head {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 10px;
    }}
    body:has(.{page_marker_class}) .ed-outstanding-name {{
        margin: 0;
        color: #0F172A;
        font-size: 12px;
        font-weight: 700;
        font-family: {ED_FONT} !important;
    }}
    body:has(.{page_marker_class}) .ed-outstanding-amt {{
        color: #DC2626;
        font-size: 12px;
        font-weight: 800;
        white-space: nowrap;
        font-family: {ED_FONT} !important;
    }}
    body:has(.{page_marker_class}) .ed-outstanding-meta {{
        display: flex;
        justify-content: space-between;
        margin-top: 4px;
        color: #64748B;
        font-size: 11px;
        font-family: {ED_FONT} !important;
    }}
    body:has(.{page_marker_class}) .ed-table-scroll-sticky thead th {{
        position: sticky;
        top: 0;
        z-index: 2;
    }}
    @media (max-width: 1100px) {{
        body:has(.{page_marker_class}) .ed-kpi-grid {{
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }}
        body:has(.{page_marker_class}) .ed-alert-grid {{
            grid-template-columns: 1fr;
        }}
    }}
    {extra_css}
    </style>
    """)
    import streamlit as st

    st.markdown(st_css, unsafe_allow_html=True)


def paginate_dataframe(df, page, rows_per_page):
    total_rows = len(df)
    total_pages = max(1, int(np.ceil(total_rows / rows_per_page)))
    page = max(1, min(page, total_pages))
    start = (page - 1) * rows_per_page
    end = start + rows_per_page
    return df.iloc[start:end], total_rows, total_pages, start + 1, min(end, total_rows)
