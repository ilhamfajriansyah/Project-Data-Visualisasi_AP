import pandas as pd
import numpy as np
import streamlit as st
from sqlalchemy import text
from .connection import get_engine

TM_YEAR_OPTIONS = ["All Year", "2030", "2029", "2028", "2027", "2026", "2025", "2024", "2023"]
TM_MONTH_OPTIONS = ["All Month", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
                    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
TM_TERMINAL_OPTIONS = ["All Terminal", "Terminal 1", "Terminal 2", "Terminal 3"]
TM_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
TM_FULL_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

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
    "oktober": "October", "okt": "October", "october": "October", "oct": "October",
    "november": "November", "nov": "November",
    "december": "December", "dec": "December", "desember": "December", "des": "December",
}

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
TM_DONUT_COLORS = DEFAULT_TERMINAL_COLORS

def _terminal_style(name, index=0):
    style = TERMINAL_STYLES.get(name, {})
    color = style.get("color", DEFAULT_TERMINAL_COLORS[index % len(DEFAULT_TERMINAL_COLORS)])
    return {
        "code": style.get("code", "".join(part[:1] for part in str(name).split()[:2]).upper() or f"T{index + 1}"),
        "color": color,
        "soft_bg": style.get("soft_bg", f"{color}12"),
    }

def _canonical_month(value):
    if pd.isna(value):
        return None
    raw = str(value).strip()
    if not raw:
        return None
    key = raw.lower()[:3] if raw.lower() not in MONTH_ALIASES else raw.lower()
    return MONTH_ALIASES.get(raw.lower(), MONTH_ALIASES.get(key, raw))

def _month_short(value):
    month = _canonical_month(value)
    if month in TM_MONTH_OPTIONS:
        return month[:3]
    return str(value)[:3] if value is not None else "-"

def _prior_month_key(month_name: str, year: int) -> tuple[str, int]:
    """Dapatkan bulan dan tahun kalender sebelumnya (menangani pergantian tahun)."""
    idx = TM_FULL_MONTHS.index(month_name)
    if idx == 0:
        return TM_FULL_MONTHS[-1], year - 1
    return TM_FULL_MONTHS[idx - 1], year

def _apply_non_period_filters(source_df, terminal_filter="All Terminal", sub_terminal_filter="All Sub Terminal",
                               bidang_usaha_filter="All Bidang Usaha", kerja_sama_filter="All Kerja Sama"):
    """Terapkan filter non-periode (terminal/bidang usaha/kerjasama) agar YoY dan MoM konsisten."""
    filtered = source_df
    if terminal_filter != "All Terminal":
        filtered = filtered[filtered["terminal"] == terminal_filter]
    if sub_terminal_filter != "All Sub Terminal":
        filtered = filtered[filtered["sub_terminal"] == sub_terminal_filter]
    if bidang_usaha_filter != "All Bidang Usaha":
        filtered = filtered[filtered["bidang_usaha"] == bidang_usaha_filter]
    if kerja_sama_filter != "All Kerja Sama":
        filtered = filtered[filtered["kerja_sama"] == kerja_sama_filter]
    return filtered

@st.cache_data(ttl=60)
def _load_traffic_database_data():
    try:
        engine = get_engine()
        with engine.connect() as conn:
            # Ambil data traffic dari DB; parsing format masa_jasa dilakukan di Python secara fleksibel.
            query = text("""
                SELECT
                    tr.tahun,
                    tr.masa_jasa,
                    tm.terminal,
                    SUM(COALESCE(tr.subtotal_trafik_dom, 0))  AS pax_domestik,
                    SUM(COALESCE(tr.subtotal_trafik_int, 0))  AS pax_internasional,
                    SUM(COALESCE(tr.total_trafik, 0))         AS total_pax,
                    SUM(COALESCE(tr.real_omzet, 0))           AS real_omzet,
                    SUM(COALESCE(tr.total_kontribusi, 0))     AS total_kontribusi,
                    SUM(COALESCE(tr.spending_per_pax, 0))     AS spending_per_pax
                FROM transaction_revenue tr
                LEFT JOIN tenant_master tm ON tr.tenant_id = tm.id
                WHERE EXISTS (
                    SELECT 1
                    FROM import_history ih
                    WHERE ih.import_id = tr.import_id
                      AND COALESCE(ih.is_active, true) = true
                )
                GROUP BY tr.tahun, tr.masa_jasa, tm.terminal
            """)
            df = pd.read_sql(query, conn)
        if df.empty:
            return pd.DataFrame()
        return _normalize_traffic_dataframe(df)
    except Exception:
        return pd.DataFrame()

def _parse_masa_jasa_str(val):
    # Parsing format masa_jasa dipusatkan di _normalize_traffic_dataframe agar semua sumber data konsisten.
    if pd.isna(val):
        return None
    s = str(val).strip()
    try:
        dt = pd.to_datetime(s, errors="raise")
        return dt.strftime("%B")
    except Exception:
        pass
    return s

@st.cache_data(ttl=300)
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

    # Kelompokkan data transaksi agar level agregasinya sama dengan data database (bulanan).
    numeric_cols = [
        "tahun", "pax_domestik", "pax_internasional", "total_pax",
        "real_omzet", "total_kontribusi", "spending_per_pax",
    ]
    for col in numeric_cols:
        mapped[col] = pd.to_numeric(mapped[col], errors="coerce")

    grouped = (
        mapped.groupby(["tahun", "masa_jasa", "terminal"], dropna=False)[numeric_cols[1:]]
        .sum(min_count=1)
        .reset_index()
    )
    return _normalize_traffic_dataframe(grouped)

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
    normalized["masa_jasa"] = normalized["masa_jasa"].map(_parse_masa_jasa_str).map(_canonical_month)
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
    # Gunakan df_raw sebagai sumber utama agar data konsisten antar halaman, gunakan query DB sebagai fallback.
    mapped = _traffic_from_dashboard_data(df_raw)
    if not mapped.empty:
        return mapped
    return _load_traffic_database_data()

def _apply_filters(df, year_filter="All Year", month_filter="All Month", terminal_filter="All Terminal",
                   sub_terminal_filter="All Sub Terminal", bidang_usaha_filter="All Bidang Usaha", kerja_sama_filter="All Kerja Sama"):
    filtered = df.copy()
    if year_filter != "All Year":
        filtered = filtered[filtered["tahun"] == int(year_filter)]
    if month_filter != "All Month":
        full_month = _canonical_month(month_filter)
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

def _pct_change(curr, prior):
    return ((curr - prior) / prior * 100) if prior else 0

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
    spp = sum(r["spp"] * r["total"] for r in rows) / total if total else 0

    prior_rows = build_rows(prior_df)
    prior_total = float(prior_df["total_pax"].sum()) if not prior_df.empty else 0
    prior_domestic = float(prior_df["pax_domestik"].sum()) if not prior_df.empty else 0
    prior_international = float(prior_df["pax_internasional"].sum()) if not prior_df.empty else 0
    prior_spp = sum(r["spp"] * r["total"] for r in prior_rows) / prior_total if prior_total else 0

    yoy = _pct_change(total, prior_total)
    domestic_yoy = _pct_change(domestic, prior_domestic)
    international_yoy = _pct_change(international, prior_international)
    spp_yoy = _pct_change(spp, prior_spp)
    shares = {r["name"]: (r["total"] / total * 100 if total else 0) for r in rows}
    for row in rows:
        prior_terminal = prior_df[prior_df["terminal"] == row["name"]]
        prior_terminal_total = float(prior_terminal["total_pax"].sum()) if not prior_terminal.empty else 0
        row["yoy"] = ((row["total"] - prior_terminal_total) / prior_terminal_total * 100) if prior_terminal_total else None

    # Gunakan YoY jika data pembanding tahun lalu ada, jika tidak, gunakan MoM sebagai fallback.
    growth_pct = yoy
    growth_label = f"YoY vs FY{current_year - 1}" if current_year is not None else "YoY"
    growth_available = bool(prior_total)

    if not growth_available:
        ref_df = current_df.dropna(subset=["tahun", "masa_jasa"]).copy()
        if not ref_df.empty:
            ref_df["_month_idx"] = ref_df["masa_jasa"].map(lambda m: TM_FULL_MONTHS.index(m) if m in TM_FULL_MONTHS else -1)
            ref_df = ref_df[ref_df["_month_idx"] >= 0]

        if ref_df.empty:
            growth_pct = 0
            growth_label = "Data pembanding belum tersedia"
        else:
            latest = ref_df.sort_values(["tahun", "_month_idx"]).iloc[-1]
            cur_month_name, cur_month_year = latest["masa_jasa"], int(latest["tahun"])
            cur_month_total = float(
                ref_df.loc[
                    (ref_df["tahun"] == cur_month_year) & (ref_df["masa_jasa"] == cur_month_name),
                    "total_pax",
                ].sum()
            )
            prior_month_name, prior_month_year = _prior_month_key(cur_month_name, cur_month_year)
            non_period_df = _apply_non_period_filters(
                df, terminal_filter, sub_terminal_filter, bidang_usaha_filter, kerja_sama_filter
            )
            prior_month_df = non_period_df[
                (non_period_df["tahun"] == prior_month_year) & (non_period_df["masa_jasa"] == prior_month_name)
            ]
            prior_month_total = float(prior_month_df["total_pax"].sum()) if not prior_month_df.empty else 0

            if prior_month_total:
                growth_pct = _pct_change(cur_month_total, prior_month_total)
                growth_label = f"MoM vs {_month_short(prior_month_name)} {prior_month_year}"
                growth_available = True
            else:
                growth_pct = 0
                growth_label = "Data pembanding belum tersedia"

    return {
        "total": total,
        "domestic": domestic,
        "international": international,
        "domestic_pct": (domestic / total * 100) if total else 0,
        "intl_pct": (international / total * 100) if total else 0,
        "spp": spp,
        "yoy": yoy,
        "domestic_yoy": domestic_yoy,
        "international_yoy": international_yoy,
        "spp_yoy": spp_yoy,
        "growth_pct": growth_pct,
        "growth_label": growth_label,
        "growth_available": growth_available,
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
    )
    values = []
    for short_month in TM_MONTH_OPTIONS[1:]:
        full_month = _canonical_month(short_month)
        if grouped.empty or full_month not in grouped.index:
            values.append(0)
            continue
        row = grouped.loc[full_month]
        spp = row["real_omzet"] / row["total_pax"] if row["total_pax"] else 0
        values.append(float(spp or 0) / 1000.0)
    return pd.DataFrame({"Month": TM_MONTHS, "SPP": values})

def _format_yoy_html(val, has_prior_data=True):
    if not has_prior_data:
        return '<span class="tm-neutral">N/A</span>'
    if val > 0.005:
        return f'<span class="tm-positive">↑ +{f"{val:.1f}".replace(".", ",")}%</span>'
    elif val < -0.005:
        return f'<span class="tm-negative">↓ {f"{val:.1f}".replace(".", ",")}%</span>'
    else:
        return f'<span class="tm-neutral">→ {f"{val:.1f}".replace(".", ",")}%</span>'

def get_terminal_table_df(metrics):
    rows = []
    has_prior = bool(metrics.get("prior_total", 0))
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
            "YoY Growth": _format_yoy_html(row["yoy"], has_prior),
            "_share": share,
            "_total": total,
        })

    total_dom = metrics["domestic"]
    total_intl = metrics["international"]
    total_all = metrics["total"]
    dom_pct_total = total_dom / total_all * 100 if total_all else 0
    intl_pct_total = total_intl / total_all * 100 if total_all else 0
    
    current_year_val = f"FY {metrics['current_year']}" if metrics.get('current_year') else "Tahun Ini"
    prior_year_val = f"FY {metrics['prior_year']}" if metrics.get('prior_year') else "Tahun Lalu"
    terminal_val = metrics.get('terminal_label', 'All Terminals')

    yoy_html = (
        f'<div class="tm-cell-stack">{_format_yoy_html(metrics["yoy"], has_prior)}<span class="tm-subcell">vs {prior_year_val}</span></div>'
        if has_prior else
        '<div class="tm-cell-stack"><span class="tm-neutral">N/A</span><span class="tm-subcell">Data pembanding N/A</span></div>'
    )

    rows.append({
        "Terminal": f'<div class="tm-cell-stack">TOTAL — {terminal_val}<span class="tm-subcell">Ringkasan {terminal_val}</span></div>',
        "Domestic Traffic": f'<div class="tm-cell-stack">{_fmt_pax_short(total_dom)}<span class="tm-subcell">{dom_pct_total:.0f}% dari total</span></div>',
        "International Traffic": f'<div class="tm-cell-stack">{_fmt_pax_short(total_intl)}<span class="tm-subcell">{intl_pct_total:.0f}% dari total</span></div>',
        "Total Traffic": f'<div class="tm-cell-stack">{_fmt_pax_short(total_all)}<span class="tm-subcell">Total {current_year_val}</span></div>',
        "Traffic Share": '<div class="tm-cell-stack">100%<span class="tm-subcell">Seluruh terminal</span></div>',
        "Spending Per Pax": f'<div class="tm-cell-stack">{_fmt_rp_k(metrics["spp"])}<span class="tm-subcell">Rata-rata tertimbang</span></div>',
        "YoY Growth": yoy_html,
        "_share": 100,
        "_total": total_all,
    })
    return pd.DataFrame(rows)
