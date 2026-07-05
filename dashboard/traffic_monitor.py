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
from .export_utils import EXCEL_MIME, dataframe_to_excel_bytes
from .enterprise_ui import (
    ED_FONT,
    donut_legend_html,
    inject_enterprise_page_css,
    progress_bar_html,
    section_title_html,
    table_inner_html,
)
from .navigation import topnav_actions_html
TM_FONT = ED_FONT
TM_YEAR_OPTIONS = ["All Year", "2030", "2029", "2028", "2027", "2026", "2025", "2024", "2023"]
TM_MONTH_OPTIONS = ["All Month", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
TM_TERMINAL_OPTIONS = ["All Terminal", "Terminal 1", "Terminal 2", "Terminal 3"]
TM_DONUT_COLORS = ["#7C3AED", "#06B6D4", "#2563EB"]
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
    "Terminal 3": {
        "code": "T3",
        "color": "#2563EB",
        "soft_bg": "#EFF6FF",
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
            # Baca data traffic dari transaction_revenue
            # masa_jasa bisa berupa: 'Jun', 'June', 'June 2026', '2026-06-01', '2026-06-01 00:00:00'
            # Parsing dilakukan di Python agar lebih fleksibel
            query = text("""
                SELECT
                    tahun,
                    masa_jasa,
                    terminal,
                    SUM(COALESCE(subtotal_trafik_dom, 0))  AS pax_domestik,
                    SUM(COALESCE(subtotal_trafik_int, 0))  AS pax_internasional,
                    SUM(COALESCE(total_trafik, 0))         AS total_pax,
                    SUM(COALESCE(real_omzet, 0))           AS real_omzet,
                    SUM(COALESCE(total_kontribusi, 0))     AS total_kontribusi,
                    SUM(COALESCE(spending_per_pax, 0))     AS spending_per_pax
                FROM transaction_revenue tr
                WHERE EXISTS (
                    SELECT 1
                    FROM import_history ih
                    WHERE ih.import_id = tr.import_id
                      AND COALESCE(ih.is_active, true) = true
                )
                GROUP BY tahun, masa_jasa, terminal
            """)
            df = pd.read_sql(query, conn)
        if df.empty:
            return pd.DataFrame()
        # Normalise masa_jasa: convert datetime strings to month name
        def _parse_masa_jasa_str(val):
            if pd.isna(val):
                return None
            s = str(val).strip()
            try:
                dt = pd.to_datetime(s, errors="raise")
                return dt.strftime("%B")   # → 'June', 'May', etc.
            except Exception:
                pass
            return s  # leave as-is; _canonical_month will handle
        df["masa_jasa"] = df["masa_jasa"].apply(_parse_masa_jasa_str)
        return _normalize_traffic_dataframe(df)
    except Exception:
        return pd.DataFrame()


def _traffic_from_dashboard_data(df):
    if df is None or df.empty:
        return _normalize_traffic_dataframe(pd.DataFrame())

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
    mapped["total_kontribusi"] = df["total_kontribusi"] if "total_kontribusi" in df.columns else 0
    mapped["spending_per_pax"] = df["spending_per_pax"] if "spending_per_pax" in df.columns else pd.NA
    return _normalize_traffic_dataframe(mapped)


def _normalize_traffic_dataframe(df):
    if df is None or df.empty:
        return pd.DataFrame(columns=[
            "tahun", "masa_jasa", "terminal", "pax_domestik",
            "pax_internasional", "total_pax", "real_omzet", "total_kontribusi", "spending_per_pax",
        ])

    normalized = df.copy()
    for col in ["tahun", "pax_domestik", "pax_internasional", "total_pax", "real_omzet", "total_kontribusi", "spending_per_pax"]:
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
    normalized[["pax_domestik", "pax_internasional", "total_pax", "real_omzet", "total_kontribusi"]] = (
        normalized[["pax_domestik", "pax_internasional", "total_pax", "real_omzet", "total_kontribusi"]].fillna(0)
    )
    return normalized.dropna(subset=["tahun", "masa_jasa"])


def get_traffic_monitor_data(df_raw=None):
    db_df = _load_traffic_database_data()
    if not db_df.empty:
        return db_df
    return _traffic_from_dashboard_data(df_raw)


def _apply_filters(df, year_filter="All Year", month_filter="All Month", terminal_filter="All Terminal",
                   sub_terminal_filter="All Sub Terminal", bidang_usaha_filter="All Bidang Usaha", kerja_sama_filter="All Kerja Sama"):
    filtered = df.copy()
    if year_filter != "All Year":
        filtered = filtered[filtered["tahun"] == int(year_filter)]
    if month_filter != "All Month":
        full_month = _canonical_month(month_filter)  # 'Jun' → 'June'
        filtered = filtered[filtered["masa_jasa"] == full_month]
    if terminal_filter != "All Terminal":
        filtered = filtered[filtered["terminal"] == terminal_filter]
    if sub_terminal_filter != "All Sub Terminal":
        filtered = filtered[filtered["sub_terminal"] == sub_terminal_filter]
    if bidang_usaha_filter != "All Bidang Usaha":
        filtered = filtered[filtered["bidang_usaha"] == bidang_usaha_filter]
    if kerja_sama_filter != "All Kerja Sama":
        filtered = filtered[filtered["kerja_sama"] == kerja_sama_filter]
    return filtered


def _aggregate_metrics(df, year_filter="All Year", month_filter="All Month", terminal_filter="All Terminal",
                       sub_terminal_filter="All Sub Terminal", bidang_usaha_filter="All Bidang Usaha", kerja_sama_filter="All Kerja Sama"):
    current_df = _apply_filters(df, year_filter, month_filter, terminal_filter, sub_terminal_filter, bidang_usaha_filter, kerja_sama_filter)
    current_year = int(year_filter) if year_filter != "All Year" else (int(df["tahun"].max()) if not df.empty else None)
    prior_df = df[df["tahun"] == current_year - 1] if current_year is not None else df.iloc[0:0]
    if month_filter != "All Month":
        full_month = _canonical_month(month_filter)
        prior_df = prior_df[prior_df["masa_jasa"] == full_month]
    if terminal_filter != "All Terminal":
        prior_df = prior_df[prior_df["terminal"] == terminal_filter]
    if sub_terminal_filter != "All Sub Terminal":
        prior_df = prior_df[prior_df["sub_terminal"] == sub_terminal_filter]
    if bidang_usaha_filter != "All Bidang Usaha":
        prior_df = prior_df[prior_df["bidang_usaha"] == bidang_usaha_filter]
    if kerja_sama_filter != "All Kerja Sama":
        prior_df = prior_df[prior_df["kerja_sama"] == kerja_sama_filter]

    def build_rows(source):
        rows = []
        if source.empty:
            return rows
        grouped = source.groupby("terminal", dropna=False).agg(
            domestic=("pax_domestik", "sum"),
            international=("pax_internasional", "sum"),
            total=("total_pax", "sum"),
            kontribusi=("total_kontribusi", "sum"),
            revenue=("real_omzet", "sum"),
            spp_avg=("spending_per_pax", "mean"),
        ).reset_index()
        for idx, record in grouped.iterrows():
            total = float(record["total"] or 0)
            spp = float(record["spp_avg"] or 0)
            rows.append({
                **_terminal_style(record["terminal"], idx),
                "name": record["terminal"],
                "domestic": float(record["domestic"] or 0),
                "international": float(record["international"] or 0),
                "total": total,
                "spp": spp,
            })
        return rows

    rows = build_rows(current_df)
    total = sum(r["total"] for r in rows)
    domestic = sum(r["domestic"] for r in rows)
    international = sum(r["international"] for r in rows)
    spp = sum(r["spp"] for r in rows)

    prior_total = float(prior_df["total_pax"].sum()) if not prior_df.empty else 0
    yoy = ((total - prior_total) / prior_total * 100) if prior_total else 0
    shares = {r["name"]: (r["total"] / total * 100 if total else 0) for r in rows}

    for row in rows:
        prior_terminal = prior_df[prior_df["terminal"] == row["name"]]
        prior_terminal_total = float(prior_terminal["total_pax"].sum()) if not prior_terminal.empty else 0
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
        "terminal_label": terminal_filter if terminal_filter != "All Terminal" else "All Terminals",
    }

def _fmt_pax_short(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}".replace(".", ",") + " Jt"
    else:
        return f"{int(value):,}".replace(",", ".")

def _fmt_millions(value):
    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}".replace(".", ",") + " Jt pax"
    else:
        return f"{int(value):,}".replace(",", ".") + " pax"

def _fmt_rp_k(value):
    return f"Rp {value / 1_000:.1f}".replace(".", ",") + " K"

def get_monthly_traffic_trend(df, year_filter="All Year", terminal_filter="All Terminal",
                              sub_terminal_filter="All Sub Terminal", bidang_usaha_filter="All Bidang Usaha", kerja_sama_filter="All Kerja Sama"):
    current_year = int(year_filter) if year_filter != "All Year" else (int(df["tahun"].max()) if not df.empty else None)
    prior_year = current_year - 1 if current_year is not None else None

    def series_for(year):
        if year is None:
            return [0] * 12
        source = df[df["tahun"] == year]
        if terminal_filter != "All Terminal":
            source = source[source["terminal"] == terminal_filter]
        if sub_terminal_filter != "All Sub Terminal":
            source = source[source["sub_terminal"] == sub_terminal_filter]
        if bidang_usaha_filter != "All Bidang Usaha":
            source = source[source["bidang_usaha"] == bidang_usaha_filter]
        if kerja_sama_filter != "All Kerja Sama":
            source = source[source["kerja_sama"] == kerja_sama_filter]
        monthly = source.groupby("masa_jasa")["total_pax"].sum()
        # masa_jasa stored as full names ('January'); TM_MONTH_OPTIONS has short ('Jan')
        return [float(monthly.get(_canonical_month(m), 0)) / 1_000_000 for m in TM_MONTH_OPTIONS[1:]]

    return pd.DataFrame({
        "Month": TM_MONTHS,
        "Current": series_for(current_year),
        "Prior": series_for(prior_year),
    })

def get_domestic_intl_monthly(df, year_filter="All Year", terminal_filter="All Terminal",
                              sub_terminal_filter="All Sub Terminal", bidang_usaha_filter="All Bidang Usaha", kerja_sama_filter="All Kerja Sama"):
    current_year = int(year_filter) if year_filter != "All Year" else (int(df["tahun"].max()) if not df.empty else None)
    source = df[df["tahun"] == current_year] if current_year is not None else df.iloc[0:0]
    if terminal_filter != "All Terminal":
        source = source[source["terminal"] == terminal_filter]
    if sub_terminal_filter != "All Sub Terminal":
        source = source[source["sub_terminal"] == sub_terminal_filter]
    if bidang_usaha_filter != "All Bidang Usaha":
        source = source[source["bidang_usaha"] == bidang_usaha_filter]
    if kerja_sama_filter != "All Kerja Sama":
        source = source[source["kerja_sama"] == kerja_sama_filter]
    grouped = source.groupby("masa_jasa").agg(
        Domestic=("pax_domestik", "sum"),
        International=("pax_internasional", "sum"),
    )
    return pd.DataFrame({
        "Month": TM_MONTHS,
        "Domestic": [float(grouped["Domestic"].get(_canonical_month(m), 0)) / 1_000_000 if not grouped.empty else 0 for m in TM_MONTH_OPTIONS[1:]],
        "International": [float(grouped["International"].get(_canonical_month(m), 0)) / 1_000_000 if not grouped.empty else 0 for m in TM_MONTH_OPTIONS[1:]],
    })

def get_spp_monthly(df, year_filter="All Year", terminal_filter="All Terminal",
                    sub_terminal_filter="All Sub Terminal", bidang_usaha_filter="All Bidang Usaha", kerja_sama_filter="All Kerja Sama"):
    current_year = int(year_filter) if year_filter != "All Year" else (int(df["tahun"].max()) if not df.empty else None)
    source = df[df["tahun"] == current_year] if current_year is not None else df.iloc[0:0]
    if terminal_filter != "All Terminal":
        source = source[source["terminal"] == terminal_filter]
    if sub_terminal_filter != "All Sub Terminal":
        source = source[source["sub_terminal"] == sub_terminal_filter]
    if bidang_usaha_filter != "All Bidang Usaha":
        source = source[source["bidang_usaha"] == bidang_usaha_filter]
    if kerja_sama_filter != "All Kerja Sama":
        source = source[source["kerja_sama"] == kerja_sama_filter]
    grouped = source.groupby("masa_jasa").agg(
        total_pax=("total_pax", "sum"),
        real_omzet=("real_omzet", "sum"),
        spp=("spending_per_pax", "sum"),
    )
    values = []
    for short_month in TM_MONTH_OPTIONS[1:]:
        full_month = _canonical_month(short_month)  # 'Jun' -> 'June'
        if grouped.empty or full_month not in grouped.index:
            values.append(0)
            continue
        row = grouped.loc[full_month]
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
        rows.append({
            "Terminal": f'{row["code"]} {row["name"]}',
            "Domestic Traffic": f'<div class="tm-cell-stack">{_fmt_pax_short(row["domestic"])}<span class="tm-subcell">{dom_pct:.0f}% dari terminal</span></div>',
            "International Traffic": f'<div class="tm-cell-stack">{_fmt_pax_short(row["international"])}<span class="tm-subcell">{intl_pct:.0f}% dari terminal</span></div>',
            "Total Traffic": f'{_fmt_pax_short(total)}',
            "Traffic Share": f"{f"{share:.1f}".replace(".", ",")}%",
            "Spending Per Pax": _fmt_rp_k(row["spp"]),
            "YoY Growth": f'<span class="tm-positive">↑ +{f"{row["yoy"]:.1f}".replace(".", ",")}%</span>',
            "_share": share,
            "_total": total,
        })

    total_dom = metrics["domestic"]
    total_intl = metrics["international"]
    total_all = metrics["total"]
    dom_pct_total = total_dom / total_all * 100 if total_all else 0
    intl_pct_total = total_intl / total_all * 100 if total_all else 0
    rows.append({
        "Terminal": '<div class="tm-cell-stack">TOTAL — Terminal 1 & 2<span class="tm-subcell">Ringkasan Terminal 1 &amp; 2</span></div>',
        "Domestic Traffic": f'<div class="tm-cell-stack">{_fmt_pax_short(total_dom)}<span class="tm-subcell">{dom_pct_total:.0f}% dari total</span></div>',
        "International Traffic": f'<div class="tm-cell-stack">{_fmt_pax_short(total_intl)}<span class="tm-subcell">{intl_pct_total:.0f}% dari total</span></div>',
        "Total Traffic": f'<div class="tm-cell-stack">{_fmt_pax_short(total_all)}<span class="tm-subcell">Total FY2024</span></div>',
        "Traffic Share": '<div class="tm-cell-stack">100%<span class="tm-subcell">Seluruh terminal</span></div>',
        "Spending Per Pax": f'<div class="tm-cell-stack">{_fmt_rp_k(metrics["spp"])}<span class="tm-subcell">Rata-rata tertimbang</span></div>',
        "YoY Growth": f'<div class="tm-cell-stack"><span class="tm-positive">↑ +{f"{metrics["yoy"]:.1f}".replace(".", ",")}%</span><span class="tm-subcell">vs FY2023</span></div>',
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


TM_KPI_ICON_PATHS = {
    "users":         '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path>',
    "map-pin":       '<path d="M20 10c0 4.993-5.539 10.193-7.399 11.799a1 1 0 0 1-1.202 0C9.539 20.193 4 14.993 4 10a8 8 0 0 1 16 0"></path><circle cx="12" cy="10" r="3"></circle>',
    "globe":         '<circle cx="12" cy="12" r="10"></circle><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"></path><path d="M2 12h20"></path>',
    "credit-card":   '<rect width="20" height="14" x="2" y="5" rx="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line>',
    "trending-up":   '<polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline><polyline points="16 7 22 7 22 13"></polyline>',
    "shopping-bag":  '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"></path><path d="M3 6h18"></path><path d="M16 10a4 4 0 0 1-8 0"></path>',
}


def _tm_kpi_icon_svg(icon_key: str) -> str:
    paths = TM_KPI_ICON_PATHS.get(icon_key, "")
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
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
        # Check if value ends with "Jt pax", "Jt", or "%" (longest match first)
        for sfx in ["Jt pax", "Jt", "K", "%"]:
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
        f'<div class="tm-kpi-icon" style="background:{accent}14;color:{accent};">{_tm_kpi_icon_svg(icon)}</div>'
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
        {topnav_actions_html()}
    </div>
    """).strip()


_TM_FILTER_DEFAULTS = {
    "tm_terminal": "All Terminal",
    "tm_year": "All Year",
    "tm_month": "All Month",
}


def clear_tm_filters():
    """Reset both the applied filters and the pending (draft) widget values."""
    for applied_key, default in _TM_FILTER_DEFAULTS.items():
        st.session_state[applied_key] = default
        st.session_state[f"tm_pend_{applied_key[3:]}"] = default


def _apply_tm_filters():
    """Copy the pending (draft) widget values into the applied filter keys."""
    for applied_key in _TM_FILTER_DEFAULTS:
        st.session_state[applied_key] = st.session_state[f"tm_pend_{applied_key[3:]}"]


_TM_FILTER_ICONS = {
    "monitor":  '<rect width="20" height="14" x="2" y="3" rx="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line>',
    "calendar": '<path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path>',
    "filter":   '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>',
}


def _tm_filter_icon_svg(icon_key: str, size: int = 14) -> str:
    paths = _TM_FILTER_ICONS.get(icon_key, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
    )


def _render_tm_filter_card(active_count: int = 0,
                           terminal_opts=None,
                           year_opts=None,
                           month_opts=None) -> None:
    """"Filter Data" card matching the Lease Contract page — filters are
    staged in tm_pend_* widget keys and only take effect once the user
    clicks "Terapkan Filter" / "Bersihkan Semua" / the header "Reset Filter"."""
    st.markdown('<div class="tm-filtercard-marker"></div>', unsafe_allow_html=True)

    badge = (
        f'<span class="tm-filtercard-badge">{active_count} aktif</span>'
        if active_count > 0 else ""
    )
    head_l, head_r = st.columns([4, 1.2], vertical_alignment="center")
    with head_l:
        st.markdown(
            '<div class="tm-filtercard-head">'
            f'<span class="tm-filtercard-icon">{_tm_filter_icon_svg("filter", 18)}</span>'
            '<div>'
            f'<p class="tm-filtercard-title">Filter Data{badge}</p>'
            '<p class="tm-filtercard-sub">Pilih kriteria untuk memfilter data yang ditampilkan</p>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with head_r:
        st.markdown('<div class="tm-reset-top-marker"></div>', unsafe_allow_html=True)
        st.button(
            "Reset Filter", key="tm_btn_reset_top", use_container_width=True,
            icon=":material/sync:", on_click=clear_tm_filters,
        )

    st.markdown('<div class="tm-filterrow-marker"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="small")
    field_defs = [
        (c1, "monitor", "Terminal", terminal_opts or TM_TERMINAL_OPTIONS, "tm_pend_terminal"),
        (c2, "calendar", "Tahun", year_opts or TM_YEAR_OPTIONS, "tm_pend_year"),
        (c3, "calendar", "Bulan", month_opts or TM_MONTH_OPTIONS, "tm_pend_month"),
    ]
    for col, icon_key, label, options, widget_key in field_defs:
        with col:
            st.markdown(
                f'<div class="tm-filter-label">{_tm_filter_icon_svg(icon_key, 12)}<span>{label}</span></div>',
                unsafe_allow_html=True,
            )
            st.selectbox(label, options, key=widget_key, label_visibility="collapsed")

    st.markdown('<div class="tm-filtercard-footer-marker"></div>', unsafe_allow_html=True)
    _foot_spacer, foot_r1, foot_r2 = st.columns([3.2, 1.3, 1.3], vertical_alignment="center")
    with foot_r1:
        st.button("✕  Bersihkan Semua", key="tm_btn_reset_bottom", use_container_width=True, on_click=clear_tm_filters)
    with foot_r2:
        st.button(
            "Terapkan Filter", key="tm_btn_apply", use_container_width=True,
            type="primary", icon=":material/filter_alt:", on_click=_apply_tm_filters,
        )


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
                <p class="tm-terminal-meta">Dom {_fmt_pax_short(row['domestic'])} · Intl {_fmt_pax_short(row['international'])}</p>
            </div>
            <div class="tm-terminal-stats">
                <p class="tm-terminal-total">{_fmt_pax_short(row['total'])}</p>
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

    /* Container untuk Traffic Insights di Traffic Monitor Page */
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tm-insights-card):not(
        :has(div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] .tm-insights-card)
    ) {{
        padding-bottom: 35px !important;
    }}

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
        overflow: visible !important;
    }}

    body:has(.tm-page-marker) .tm-fixed-header-spacer,
    body:has(.tm-page-marker) div[data-testid="stElementContainer"]:has(.tm-fixed-header-spacer) {{
        height: 56px !important;
        min-height: 56px !important;
        max-height: 56px !important;
        margin: 0 !important;
        padding: 0 !important;
        display: block;
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
        display: flex; align-items: center; justify-content: space-between; gap: 16px;
        width: 100%;
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
    /* ── Filter Data card (same design as Lease Contract) ──────────── */
    body:has(.tm-page-marker) div[data-testid="stHorizontalBlock"]:has(.tm-filtercard-marker),
    body:has(.tm-page-marker) div[data-testid="stLayoutWrapper"]:has(.tm-filtercard-marker) {{
        margin-top: -16px !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -1px rgba(0,0,0,0.015) !important;
        padding: 18px 20px 14px !important;
    }}
    .tm-filtercard-head {{
        display: flex; align-items: center; gap: 12px;
    }}
    .tm-filtercard-icon {{
        width: 34px; height: 34px; border-radius: 10px; flex: 0 0 34px;
        background: #EEF2FF; color: #4338CA;
        display: flex; align-items: center; justify-content: center;
    }}
    .tm-filtercard-title {{
        margin: 0 !important; color: #0F172A; font-size: 18px !important; font-weight: 700 !important;
        font-family: 'Montserrat', sans-serif !important; line-height: 1 !important;
    }}
    .tm-filtercard-badge {{
        display: inline-flex; align-items: center; margin-left: 8px;
        padding: 2px 8px; border-radius: 999px; vertical-align: middle;
        background: #F0FDF4; border: 1px solid #BBF7D0;
        font-size: 10.5px !important; font-weight: 700 !important; color: #16A34A;
        white-space: nowrap;
    }}
    .tm-filtercard-sub {{
        margin: 5px 0 0 !important; color: #64748B; font-size: 11px !important; font-weight: 400 !important;
        line-height: 1 !important;
        font-family: {TM_FONT} !important;
    }}
    .tm-filter-label {{
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 6px !important;
        color: #475569 !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
        font-family: {TM_FONT} !important;
        margin: 0 0 6px 4px !important;
        height: 16px !important;
        line-height: 16px !important;
    }}
    .tm-filter-label svg {{
        display: block !important;
        flex-shrink: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    .tm-filter-label span {{
        line-height: 1 !important;
        display: inline-block !important;
    }}
    body:has(.tm-page-marker) div[data-testid="stElementContainer"]:has(.tm-filter-label) {{
        margin-bottom: -4px !important;
    }}
    body:has(.tm-page-marker) div[data-testid="stElementContainer"]:has(.tm-filterrow-marker) {{
        margin: 0 !important; padding: 0 !important; height: 0 !important;
    }}
    body:has(.tm-page-marker) div[data-testid="stElementContainer"]:has(.tm-filterrow-marker) + div[data-testid="stHorizontalBlock"],
    body:has(.tm-page-marker) div[data-testid="stElementContainer"]:has(.tm-filterrow-marker) + div[data-testid="stLayoutWrapper"] {{
        margin-top: -4px !important;
    }}
    body:has(.tm-page-marker) div[data-testid="stElementContainer"]:has(.tm-filtercard-footer-marker) {{
        margin: 6px 0 -10px !important;
        height: 1px !important;
        border-top: 1px solid #F1F5F9 !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="baseButton-secondary"] {{
        border: 1px solid #E2E8F0 !important; border-radius: 8px !important;
        background: #ffffff !important; color: #475569 !important;
        font-size: 11.5px !important; font-weight: 700 !important;
        font-family: {TM_FONT} !important;
        height: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        width: 145px !important;
        min-width: 145px !important;
        max-width: 145px !important;
        padding: 0 !important;
        margin-left: auto !important; margin-right: 0 !important;
    }}
    body:has(.tm-page-marker) div[data-testid="stElementContainer"]:has(.tm-reset-top-marker) + div[data-testid="stElementContainer"] [data-testid="baseButton-secondary"],
    body:has(.tm-page-marker) div[data-testid="stElementContainer"]:has(.tm-reset-top-marker) + div[data-testid="stElementContainer"] [data-testid="stBaseButton-secondary"] {{
        border-radius: 999px !important;
        width: auto !important;
        min-width: 0 !important;
        max-width: none !important;
        height: 36px !important;
        min-height: 36px !important;
        max-height: 36px !important;
        padding: 0 18px !important;
        font-size: 13px !important;
    }}
    body:has(.tm-page-marker) div[data-testid="stElementContainer"]:has(.tm-reset-top-marker) + div[data-testid="stElementContainer"] [data-testid="stIconMaterial"] {{
        font-family: 'Material Symbols Rounded' !important;
        font-size: 15px !important;
    }}
    body:has(.tm-page-marker) [data-testid="baseButton-primary"],
    body:has(.tm-page-marker) [data-testid="stBaseButton-primary"] {{
        border-radius: 999px !important;
        font-size: 12.5px !important; font-weight: 700 !important;
        font-family: {TM_FONT} !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="baseButton-primary"],
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="stBaseButton-primary"] {{
        border-radius: 8px !important;
        font-size: 11.5px !important; font-weight: 700 !important;
        font-family: {TM_FONT} !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        border: none !important;
        box-shadow: 0 3px 10px rgba(99, 102, 241, 0.2) !important;
        height: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        width: 145px !important;
        min-width: 145px !important;
        max-width: 145px !important;
        padding: 0 !important;
        margin-left: auto !important; margin-right: 0 !important;
    }}
    body:has(.tm-page-marker) [data-testid="baseButton-primary"]:hover,
    body:has(.tm-page-marker) [data-testid="stBaseButton-primary"]:hover {{
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.45) !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="baseButton-primary"]:hover,
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="stBaseButton-primary"]:hover {{
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    }}
    body:has(.tm-page-marker) [data-testid="baseButton-primary"] svg,
    body:has(.tm-page-marker) [data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"] {{
        color: #ffffff !important;
        fill: #ffffff !important;
        font-family: 'Material Symbols Rounded' !important;
    }}
    body:has(.tm-page-marker) [data-testid="baseButton-primary"] p,
    body:has(.tm-page-marker) [data-testid="stBaseButton-primary"] p {{
        color: #ffffff !important;
    }}
    /* ── Selectbox Dropdowns in Filter Card ────────────────────────── */
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="stSelectbox"] {{
        margin-bottom: 0 !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="stSelectbox"] > div {{
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="stSelectbox"] > div > div {{
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        backdrop-filter: none !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] {{
        border: 1px solid #E2E8F0 !important;
        border-radius: 999px !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(99, 102, 241, 0.04) !important;
        transition: all 0.2s ease !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"]:hover {{
        border-color: #CBD5E1 !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {{
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1) !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        min-height: 32px !important;
        height: 32px !important;
        max-height: 32px !important;
        padding: 0 4px 0 12px !important;
        display: flex !important;
        align-items: center !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"] {{
        font-size: 11.5px !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }}
    body:has(.tm-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-filtercard-marker) [data-testid="stSelectbox"] svg {{
        color: #64748B !important;
    }}
    body:has(.tm-page-marker) .tm-kpi-grid {{
        display: grid; grid-template-columns: repeat(6, minmax(0, 1fr)); gap: 12px; width: 100%;
        margin-top: -12px !important;
    }}
    body:has(.tm-page-marker) div[data-testid="stElementContainer"]:has(.tm-kpi-grid),
    body:has(.tm-page-marker) div[data-testid="stLayoutWrapper"]:has(.tm-kpi-grid) {{
        margin-top: -12px !important;
    }}
    body:has(.tm-page-marker) .tm-kpi-card {{
        display: flex; flex-direction: column; gap: 6px; min-height: 132px; padding: 14px 16px;
        border-radius: 12px; border: 1px solid #E2E8F0; background: #ffffff;
        box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04); box-sizing: border-box;
        transition: all 0.3s ease;
    }}
    body:has(.tm-page-marker) .tm-kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05), 0 4px 6px -2px rgba(0,0,0,0.025);
    }}
    body:has(.tm-page-marker) .tm-kpi-top {{
        display: flex; align-items: center; justify-content: space-between;
    }}
    body:has(.tm-page-marker) .tm-kpi-icon {{
        width: 34px; height: 34px; border-radius: 9px; display: flex; align-items: center;
        justify-content: center; font-size: 15px; font-weight: 700;
    }}
    body:has(.tm-page-marker) .tm-kpi-icon svg {{
        width: 18px; height: 18px;
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
    body:has(.tm-page-marker) .tm-table-wrap .ed-table-scroll {{
        border: none;
        border-radius: 10px;
        overflow: hidden;
    }}
    body:has(.tm-page-marker) .tm-table-wrap {{
        margin-top: 3px;
    }}
    body:has(.tm-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tm-export-btn) {{
        display: flex !important;
        justify-content: flex-end !important;
        width: 100% !important;
    }}
    body:has(.tm-page-marker) div[data-testid="stElementContainer"]:has(.tm-export-btn) {{
        width: 100% !important;
        display: flex !important;
        justify-content: flex-end !important;
    }}
    body:has(.tm-page-marker) .tm-export-btn {{
        display: inline-flex !important;
        align-items: center;
        justify-content: center;
        gap: 6px;
        margin-left: auto;
        padding: 8px 16px;
        border-radius: 10px;
        border: 1px solid #C7D2FE;
        background: #EEF2FF;
        color: #4F46E5;
        font-size: 13px;
        font-weight: 700;
        font-family: {TM_FONT} !important;
        cursor: pointer;
        transition: background 0.15s ease, border-color 0.15s ease;
    }}
    body:has(.tm-page-marker) .tm-export-btn svg {{
        width: 14px; height: 14px; flex-shrink: 0;
    }}
    body:has(.tm-page-marker) .tm-export-btn:hover {{
        background: #E0E7FF;
        border-color: #A5B4FC;
    }}
    body:has(.tm-page-marker) .tm-table-wrap .ed-table tbody tr:last-child {{
        background: #F1F5F9;
    }}
    body:has(.tm-page-marker) .tm-table-wrap .ed-table tbody tr:last-child td {{
        border-top: 2px solid #94A3B8 !important;
        color: #0F172A;
        font-weight: 800;
    }}
    body:has(.tm-page-marker) .tm-table-wrap .ed-table tbody tr:last-child .tm-subcell {{
        font-weight: 500;
        color: #64748B;
    }}
    /* Beda ukuran judul/sub-judul tiap card di halaman ini, mengikuti
       kontras yang dipakai pada header halaman (h2.tm-page-title vs
       p.tm-page-sub). */
    body:has(.tm-page-marker) .ed-section-title {{
        font-size: 16px !important;
        font-weight: 800 !important;
    }}
    body:has(.tm-page-marker) .ed-section-sub {{
        font-size: 11px !important;
        font-weight: 500 !important;
    }}
    body:has(.tm-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tm-insights-card),
    body:has(.tm-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tm-performance-card),
    body:has(.tm-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tm-trend-card),
    body:has(.tm-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .tm-split-card) {{
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


def page_traffic_monitor(df_raw=None):
    data_df = get_traffic_monitor_data(df_raw)

    for key, default in [
        ("tm_year", "All Year"),
        ("tm_month", "All Month"),
        ("tm_terminal", "All Terminal"),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    for pend_key, applied_key in (
        ("tm_pend_terminal", "tm_terminal"), ("tm_pend_year", "tm_year"), ("tm_pend_month", "tm_month"),
    ):
        if pend_key not in st.session_state:
            st.session_state[pend_key] = st.session_state[applied_key]

    if st.session_state.tm_year not in TM_YEAR_OPTIONS:
        st.session_state.tm_year = "All Year"
    if st.session_state.tm_month not in TM_MONTH_OPTIONS:
        st.session_state.tm_month = "All Month"
    if st.session_state.tm_terminal not in TM_TERMINAL_OPTIONS:
        st.session_state.tm_terminal = "All Terminal"

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

    with st.container(border=True):
        _render_tm_filter_card(
            active_count,
            TM_TERMINAL_OPTIONS,
            TM_YEAR_OPTIONS,
            TM_MONTH_OPTIONS,
        )

    _mount_tm_fixed_header()

    yoy_val_str = f"{metrics['yoy']:.1f}".replace(".", ",")
    domestic_pct_str = f"{metrics['domestic_pct']:.1f}".replace(".", ",")
    intl_pct_str = f"{metrics['intl_pct']:.1f}".replace(".", ",")

    spark_total = trend_df["Current"].tolist()
    spark_dom = dom_intl_df["Domestic"].tolist()
    spark_intl = dom_intl_df["International"].tolist()
    spark_spp = spp_df["SPP"].tolist()

    kpi_html = "".join([
        _tm_kpi_card("Total Traffic", _fmt_millions(metrics["total"]),
                     f"{current_year_label} · {scope_label}", metrics["yoy"], "#7C3AED", "users", spark_total),
        _tm_kpi_card("Domestic Traffic", _fmt_millions(metrics["domestic"]),
                     f"{domestic_pct_str}% of total traffic", metrics["yoy"] * 0.9,
                     "#2563EB", "map-pin", spark_dom),
        _tm_kpi_card("International Traffic", _fmt_millions(metrics["international"]),
                     f"{intl_pct_str}% of total traffic", metrics["yoy"] * 1.05,
                     "#06B6D4", "globe", spark_intl),
        _tm_kpi_card("Spending Per Pax", _fmt_rp_k(metrics["spp"]),
                     "Average across selected terminals", 6.6, "#D97706", "credit-card", spark_spp),
        _tm_kpi_card("Traffic Growth", f"+{yoy_val_str}%",
                     f"YoY vs {prior_year_label}", metrics["yoy"], "#059669", "trending-up", spark_total),
        _tm_kpi_card("Avg Spending Per Pax", _fmt_rp_k(metrics["spp"]),
                     "Weighted terminal average", 6.6, "#EA580C", "shopping-bag", spark_spp),
    ])
    st.markdown(f'<div class="tm-kpi-grid">{kpi_html}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

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
        st.markdown(f'<span class="tm-yoy-pill">YoY +{yoy_val_str} %</span>', unsafe_allow_html=True)
        st.markdown(
            '<div class="tm-mini-metrics">'
            + _mini_metric_box(current_year_label, _fmt_millions(metrics["total"]), accent="#7C3AED")
            + _mini_metric_box(prior_year_label, _fmt_millions(metrics["prior_total"]), accent="#94A3B8")
            + _mini_metric_box("Peak Month", f"{peak_month} · {_fmt_pax_short(peak_value * 1_000_000)}", accent="#2563EB")
            + _mini_metric_box("Growth", f"+{yoy_val_str}%", accent="#059669")
            + "</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(_traffic_trend_figure(trend_df, current_year_label, prior_year_label), use_container_width=True,
                        config={"displayModeBar": False})

    with row1_right:
        st.markdown('<div class="ed-card-marker tm-split-card"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Domestic vs International",
            f"Monthly split — {current_year_label} (Juta) · {scope_label}",
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

    st.markdown("<div style='height:11px'></div>", unsafe_allow_html=True)

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
            f"Annual passengers (Juta) — {current_year_label}",
        ), unsafe_allow_html=True)
        cards = []
        all_metrics = _aggregate_metrics(data_df, st.session_state.tm_year, st.session_state.tm_month, "All Terminal")
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

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

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

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

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
            st.download_button(
                "Export",
                data=dataframe_to_excel_bytes(display_df, "Traffic Performance"),
                file_name="traffic_performance_by_terminal.xlsx",
                mime=EXCEL_MIME,
                key="tm_performance_export",
                use_container_width=True,
            )
        st.markdown(
            f'<div class="tm-table-wrap">{table_inner_html(display_df, col_align=col_align)}</div>',
            unsafe_allow_html=True,
        )
