import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime
from html import escape
from textwrap import dedent

from .navigation import topnav_actions_html
from .pagination import render_pagination, patch_pagination
from .export_utils import EXCEL_MIME, dataframe_to_excel_bytes

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

RS_FONT = "Inter, sans-serif"
RS_MONTH_ORDER = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
RS_DONUT_COLORS = ["#6366F1", "#06B6D4", "#8B5CF6", "#F59E0B", "#10B981", "#EC4899", "#64748B"]

# Fixed icon + color per service, so the donut slice, table row icon, and
# contribution pill always match regardless of row/sort order.
RS_SERVICE_ICON_PATHS = {
    "package": '<path d="m7.5 4.27 9 5.15"></path><path d="M21 8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16Z"></path><path d="m3.3 7 8.7 5 8.7-5"></path><path d="M12 22V12"></path>',
    "shopping-bag": '<path d="M6 2 3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4Z"></path><path d="M3 6h18"></path><path d="M16 10a4 4 0 0 1-8 0"></path>',
    "briefcase": '<path d="M16 20V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path><rect width="20" height="14" x="2" y="6" rx="2"></rect>',
    "user": '<circle cx="12" cy="8" r="5"></circle><path d="M20 21a8 8 0 0 0-16 0"></path>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path>',
    "car": '<path d="M19 17h2c.6 0 1-.4 1-1v-3c0-.9-.7-1.7-1.5-1.9C18.7 10.6 16 10 16 10s-1.3-1.4-2.2-2.3c-.5-.4-1.1-.7-1.8-.7H5c-.6 0-1.1.4-1.4.9l-1.4 2.9A3.7 3.7 0 0 0 2 12v4c0 .6.4 1 1 1h2"></path><circle cx="7" cy="17" r="2"></circle><path d="M9 17h6"></path><circle cx="17" cy="17" r="2"></circle>',
    "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>',
    "calendar": '<path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path>',
    "pie-chart": '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path>',
    "bar-chart": '<line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>',
}

RS_SERVICE_VISUAL = {
    "Cargo Area":                ("package", "#8B5CF6"),
    "Commercial Area":           ("shopping-bag", "#06B6D4"),
    "Ground Handling":           ("briefcase", "#6366F1"),
    "Ground Handling Services":  ("user", "#F59E0B"),
    "PSC":                       ("shield", "#10B981"),
    "Parking Area":              ("car", "#EC4899"),
    "VIP Services":              ("star", "#64748B"),
}


def _rs_service_icon_svg(icon_key: str) -> str:
    paths = RS_SERVICE_ICON_PATHS.get(icon_key, "")
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
    )


_RS_FILTER_DEFAULTS = {
    "rs_terminal": "All Terminal", "rs_year": "All Year", "rs_month": "All Month",
}


def clear_rs_filters():
    """Reset both the applied filters and the pending (draft) widget values."""
    for applied_key, default in _RS_FILTER_DEFAULTS.items():
        st.session_state[applied_key] = default
        st.session_state[f"rs_pend_{applied_key[3:]}"] = default
    if "rs_detail_search" in st.session_state:
        st.session_state.rs_detail_search = ""


def _apply_rs_filters():
    """Copy the pending (draft) widget values into the applied filter keys."""
    for applied_key in _RS_FILTER_DEFAULTS:
        st.session_state[applied_key] = st.session_state[f"rs_pend_{applied_key[3:]}"]


_RS_FILTER_ICONS = {
    "monitor":  '<rect width="20" height="14" x="2" y="3" rx="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line>',
    "calendar": '<path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path>',
    "filter":   '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>',
}


def _rs_filter_icon_svg(icon_key: str, size: int = 14) -> str:
    paths = _RS_FILTER_ICONS.get(icon_key, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
    )


def _render_rs_filter_card(active_count, terminal_options, year_options, month_options) -> None:
    """"Filter Data" card matching the Lease Contract page — filters are
    staged in rs_pend_* widget keys and only take effect once the user
    clicks "Terapkan Filter" / "Bersihkan Semua" / the header "Reset Filter"."""
    st.markdown('<div class="rs-filtercard-marker"></div>', unsafe_allow_html=True)

    badge = (
        f'<span class="rs-filtercard-badge">{active_count} aktif</span>'
        if active_count > 0 else ""
    )
    head_l, head_r = st.columns([4, 1.2], vertical_alignment="center")
    with head_l:
        st.markdown(
            '<div class="rs-filtercard-head">'
            f'<span class="rs-filtercard-icon">{_rs_filter_icon_svg("filter", 18)}</span>'
            '<div>'
            f'<p class="rs-filtercard-title">Filter Data{badge}</p>'
            '<p class="rs-filtercard-sub">Pilih kriteria untuk memfilter data yang ditampilkan</p>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with head_r:
        st.markdown('<div class="rs-reset-top-marker"></div>', unsafe_allow_html=True)
        st.button(
            "Reset Filter", key="rs_btn_reset_top", use_container_width=True,
            icon=":material/sync:", on_click=clear_rs_filters,
        )

    st.markdown('<div class="rs-filterrow-marker"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3, gap="small")
    field_defs = [
        (c1, "monitor", "Terminal", terminal_options, "rs_pend_terminal"),
        (c2, "calendar", "Tahun", year_options, "rs_pend_year"),
        (c3, "calendar", "Bulan", month_options, "rs_pend_month"),
    ]
    for col, icon_key, label, options, widget_key in field_defs:
        with col:
            st.markdown(
                f'<div class="rs-filter-label">{_rs_filter_icon_svg(icon_key, 12)}<span>{label}</span></div>',
                unsafe_allow_html=True,
            )
            st.selectbox(label, options, key=widget_key, label_visibility="collapsed")

    st.markdown('<div class="rs-filtercard-footer-marker"></div>', unsafe_allow_html=True)
    _foot_spacer, foot_r1, foot_r2 = st.columns([3.2, 1.3, 1.3], vertical_alignment="center")
    with foot_r1:
        st.button("✕  Bersihkan Semua", key="rs_btn_reset_bottom", use_container_width=True, on_click=clear_rs_filters)
    with foot_r2:
        st.button(
            "Terapkan Filter", key="rs_btn_apply", use_container_width=True,
            type="primary", icon=":material/filter_alt:", on_click=_apply_rs_filters,
        )


def _compute_filtered_kpis(filtered_detail):
    if filtered_detail.empty:
        return 0, 0
    total_rev = filtered_detail["_total_kontribusi"].sum()
    rev_share = filtered_detail["_pendapatan_rs"].sum()
    return total_rev, rev_share


def _pct_change(current, base):
    if not base:
        return None
    return (current - base) / base * 100


from .shared_import import get_mapped_column


def _resolve_col(df: pd.DataFrame, canonical: str) -> str:
    """get_mapped_column() reflects the *last* file the user previewed in
    Import Manager, which lingers in session_state independently of
    whichever dataframe (e.g. the DB-sourced df_raw) is being rendered now.
    If that stale mapping doesn't actually exist on this dataframe, fall
    back to the canonical DB column name instead of letting it silently
    zero out the column."""
    mapped = get_mapped_column(canonical)
    if mapped and mapped in df.columns:
        return mapped
    return canonical


# ─────────────────────────────────────────────
# DATA TRANSFORMATION FROM REAL EXCEL
# ─────────────────────────────────────────────
def get_services_data(df: pd.DataFrame):
    if df is None or df.empty:
        return pd.DataFrame()
        
    col_bidang = _resolve_col(df, "bidang_usaha")
    col_rs = _resolve_col(df, "pendapatan_rs")
    col_kontribusi = _resolve_col(df, "total_kontribusi")

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

def get_trend_data_from_df(df: pd.DataFrame):
    """Pivot pendapatan_rs by month x bidang_usaha for the Revenue Trend chart.
    Returns (pivot_df, unit_label) — unit_label tells the caller which scale
    (Rp Ribu/Juta/Miliar/Triliun) the values were divided by, chosen
    dynamically so small data doesn't collapse to near-zero."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["Bulan"]), "Rp"

    col_masa = _resolve_col(df, "masa_jasa")
    col_bidang = _resolve_col(df, "bidang_usaha")
    col_rs = _resolve_col(df, "pendapatan_rs")

    for col in [col_masa, col_bidang, col_rs]:
        if col not in df.columns:
            df[col] = 0 if col == col_rs else "Unknown"

    # Samakan masa_jasa jadi nama bulan penuh ("June") apa pun bentuk
    # aslinya (tanggal utuh, "Jun-2025", dll), supaya bisa diurutkan
    # kronologis lewat RS_MONTH_ORDER.
    parsed_masa = pd.to_datetime(df[col_masa], errors="coerce")
    bulan = parsed_masa.dt.strftime("%B").where(parsed_masa.notna(), df[col_masa].astype(str))

    pivot = (
        df.assign(_bulan=bulan)
        .pivot_table(index="_bulan", columns=col_bidang, values=col_rs, aggfunc="sum", fill_value=0)
        .reindex(RS_MONTH_ORDER, fill_value=0)
        .reset_index()
        .rename(columns={"_bulan": "Bulan"})
    )

    # Map 'Others' if too many columns
    if len(pivot.columns) > 4:
        top_cols = pivot.drop("Bulan", axis=1).sum().nlargest(2).index
        others = pivot.drop(["Bulan"] + list(top_cols), axis=1).sum(axis=1)
        pivot = pivot[["Bulan"] + list(top_cols)].copy()
        pivot["Others"] = others

    value_cols = [c for c in pivot.columns if c != "Bulan"]
    max_val = float(pivot[value_cols].to_numpy().max()) if value_cols and not pivot.empty else 0.0
    if max_val >= 1_000_000_000_000:
        divisor, unit_label = 1_000_000_000_000, "Rp Triliun"
    elif max_val >= 1_000_000_000:
        divisor, unit_label = 1_000_000_000, "Rp Miliar"
    elif max_val >= 1_000_000:
        divisor, unit_label = 1_000_000, "Rp Juta"
    elif max_val >= 1_000:
        divisor, unit_label = 1_000, "Rp Ribu"
    else:
        divisor, unit_label = 1, "Rp"
    for col in value_cols:
        pivot[col] = pivot[col] / divisor

    return pivot, unit_label

def get_detail_revenue_sharing_data(df: pd.DataFrame):
    if df is None or df.empty:
        return pd.DataFrame(columns=[
            "Date", "Tenant", "Brand", "Kode Ruang", "Service/SBU", "Terminal", "Omzet",
            "Revenue", "Share %", "Management Share", "_total_kontribusi",
            "_pendapatan_rs", "_tahun", "_bulan",
        ])

    col_masa = _resolve_col(df, "masa_jasa")
    col_tahun = _resolve_col(df, "tahun")
    col_perusahaan = _resolve_col(df, "perusahaan")
    col_brand = _resolve_col(df, "brand")
    col_kode_ruang = _resolve_col(df, "kode_ruang")
    col_bidang = _resolve_col(df, "bidang_usaha")
    col_terminal = _resolve_col(df, "terminal")
    col_rs = _resolve_col(df, "pendapatan_rs")
    col_rs_pct = _resolve_col(df, "rs_percent")
    col_kontribusi = _resolve_col(df, "kontribusi")

    for col in [col_masa, col_tahun, col_perusahaan, col_brand, col_kode_ruang, col_bidang, col_terminal, col_rs, col_kontribusi]:
        if col not in df.columns:
            df[col] = 0 if col in [col_rs, col_kontribusi, col_tahun] else "Unknown"

    # masa_jasa kadang berisi tanggal utuh, teks "Jun-2025", atau sudah nama
    # bulan — samakan jadi nama bulan penuh ("June") supaya filter Bulan
    # cocok dengan apa pun bentuk aslinya, bukan string-matching yang rapuh.
    parsed_masa = pd.to_datetime(df[col_masa], errors="coerce")
    bulan_norm = parsed_masa.dt.strftime("%B").where(parsed_masa.notna(), df[col_masa].astype(str))

    # Omzet basis "menang" -> Share % -> Revenue Sharing, konsisten secara
    # alur dengan rumus MAX(%RS*MIN OMZET, %RS*REAL OMZET, MGRS*REAL PAX).
    pendapatan_rs, omzet_basis = _compute_pendapatan_rs_and_omzet(df, col_rs)

    result = pd.DataFrame({
        "Date": df[col_masa],
        "Tenant": df[col_perusahaan],
        "Brand": df[col_brand],
        "Kode Ruang": df[col_kode_ruang],
        "Service/SBU": df[col_bidang],
        "Terminal": df[col_terminal],
        "Omzet": omzet_basis.apply(lambda x: f"Rp {x:,.0f}"),
        "Revenue": pendapatan_rs.apply(lambda x: f"Rp {x:,.0f}"),
        "Share %": (
            pd.to_numeric(df[col_rs_pct], errors="coerce")
            .apply(lambda x: f"{x*100:.1f}%".replace(".", ",") if pd.notna(x) and x != 0 else "N/A")
            if col_rs_pct in df.columns else "N/A"
        ),
        "Management Share": df[col_kontribusi].apply(lambda x: f"Rp {x:,.0f}"),
        # Kolom numerik/teks tersembunyi untuk filter & KPI cards (tidak ditampilkan di tabel):
        "_tahun": pd.to_numeric(df[col_tahun], errors="coerce"),
        "_bulan": bulan_norm,
        # Total Revenue = sum(total_kontribusi)
        "_total_kontribusi": pd.to_numeric(df[col_kontribusi], errors="coerce").fillna(0),
        # Revenue Share = sum(MAX(%RS*MIN OMZET, %RS*REAL OMZET, MGRS*REAL PAX))
        "_pendapatan_rs": pendapatan_rs,
    })

    return result


def _compute_pendapatan_rs_and_omzet(df: pd.DataFrame, col_rs: str) -> tuple[pd.Series, pd.Series]:
    """Rumus Pendapatan RS: =MAX(%RS*MIN OMZET; %RS*REAL OMZET; MGRS*REAL PAX).

    Kolom pendapatan_rs yang sudah tersimpan (hasil rumus ini dari Excel
    sebelum diimpor) dipakai dulu kalau ada — itu sumber paling bisa
    dipercaya. Rumus di sini hanya dipakai sebagai fallback kalau
    pendapatan_rs kosong, KARENA kalau hanya sebagian input mentahnya
    (rs_percent/mgrs_per_pax/real_pax) yang berhasil ter-import, rumus bisa
    menghasilkan angka kecil yang salah — bukan 0 — sehingga tanpa urutan
    prioritas ini nilai pendapatan_rs yang benar malah keabaikan.

    Juga mengembalikan basis Omzet yang "menang" di rumus MAX — supaya
    kolom Omzet di tabel Detail Revenue Sharing konsisten secara logika
    dengan kolom Revenue Sharing-nya (Omzet basis -> Share % -> Revenue Sharing).

    - Kalau term %RS*MIN OMZET yang menang -> Omzet = MIN OMZET.
    - Kalau term %RS*REAL OMZET yang menang -> Omzet = REAL OMZET.
    - Kalau term MGRS*REAL PAX yang menang (bukan basis omzet sama sekali,
      melainkan per-pax) -> Omzet tetap pakai REAL OMZET sebagai referensi
      omzet aktual tenant tersebut.
    - Kalau pendapatan_rs yang sudah tersimpan dipakai (rumus tidak
      dieksekusi karena datanya sudah ada), tidak ada "term pemenang" untuk
      diacu -> Omzet juga pakai REAL OMZET sebagai referensi.
    """
    col_rs_percent = _resolve_col(df, "rs_percent")
    col_min_omzet = _resolve_col(df, "min_omzet")
    col_real_omzet = _resolve_col(df, "real_omzet")
    col_mgrs = _resolve_col(df, "mgrs_per_pax")
    col_real_pax = _resolve_col(df, "real_pax")

    def _num(col):
        if col not in df.columns:
            return pd.Series(0, index=df.index)
        return pd.to_numeric(df[col], errors="coerce").fillna(0)

    rs_percent = _num(col_rs_percent)
    min_omzet = _num(col_min_omzet)
    real_omzet = _num(col_real_omzet)
    mgrs_per_pax = _num(col_mgrs)
    real_pax = _num(col_real_pax)
    existing_rs = _num(col_rs)

    term_min = rs_percent * min_omzet
    term_real = rs_percent * real_omzet
    term_mgrs = mgrs_per_pax * real_pax
    terms = pd.concat([term_min, term_real, term_mgrs], axis=1)
    terms.columns = ["min", "real", "mgrs"]

    formula_value = terms.max(axis=1)
    final_rs = existing_rs.where(existing_rs > 0, formula_value)

    using_formula = existing_rs <= 0
    winner = terms.idxmax(axis=1)
    omzet_basis = real_omzet.copy()
    omzet_basis = omzet_basis.where(~(using_formula & (winner == "min")), min_omzet)

    return final_rs, omzet_basis



# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _parse_rp(text):
    raw = str(text).replace("Rp", "").strip()
    raw = raw.replace(" ", "")
    mult = 1.0
    if raw.endswith("M") or raw.endswith("B"):
        mult = 1_000_000_000
        raw = raw[:-1]
    elif raw.endswith("Jt"):
        mult = 1_000_000
        raw = raw[:-2]
    elif raw.endswith("T"):
        mult = 1_000_000_000_000
        raw = raw[:-1]
    
    if "," in raw:
        comma_parts = raw.split(",")
        if len(comma_parts) > 1 and len(comma_parts[-1]) == 3:
            # e.g. "5,000,000" — commas are thousands separators, not a decimal point.
            raw = raw.replace(",", "")
        else:
            # e.g. "5.000,50" — Indonesian-style decimal comma.
            raw = raw.replace(".", "").replace(",", ".")
    else:
        if raw.count(".") == 1:
            parts = raw.split(".")
            if len(parts[1]) == 3:
                raw = raw.replace(".", "")
        else:
            raw = raw.replace(".", "")
            
    return float(raw) * mult


def _fmt_rp_compact(value):
    if pd.isna(value):
        value = 0
    if value >= 1_000_000_000_000:
        val_str = f"{value / 1_000_000_000_000:.2f}"
        return f"Rp {val_str.replace('.', ',')} T"
    if value >= 1_000_000_000:
        val_str = f"{value / 1_000_000_000:.2f}"
        return f"Rp {val_str.replace('.', ',')} M"
    if value >= 1_000_000:
        val_str = f"{value / 1_000_000:.2f}"
        return f"Rp {val_str.replace('.', ',')} Jt"
    val_str = f"{value:,.0f}"
    return f"Rp {val_str.replace(',', '.')}"


def _fmt_rp_full(value):
    if pd.isna(value):
        value = 0
    val_str = f"{value:,.0f}"
    return f"Rp {val_str.replace(',', '.')}"


def _format_mom(value):
    cls = "ed-positive" if value >= 0 else "ed-negative"
    arrow = "↑" if value >= 0 else "↓"
    val_str = f"{abs(value):.1f}%"
    return f'<span class="{cls}">{arrow} {val_str.replace(".", ",")}</span>'


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


def _kpi_card(label, value, delta_pct, accent, icon, tooltip_val=None):
    has_delta = delta_pct is not None
    delta_up = has_delta and delta_pct >= 0
    delta_bg = "#DCFCE7" if delta_up else "#FEE2E2"
    delta_fg = "#059669" if delta_up else "#DC2626"
    arrow = "↑" if delta_up else "↓"

    # Process unit to extract prefix (like "Rp") and suffix (like "M", "Jt", or empty)
    prefix = ""
    val_part = value
    suffix = ""

    if value.startswith("Rp"):
        prefix = "Rp "
        rest = value[2:].strip()
        # Find if rest ends with a unit suffix (like "M", "Jt", "T")
        # Let's extract the unit suffix if present
        for sfx in ["Jt", "M", "T"]:
            if rest.endswith(sfx):
                suffix = sfx
                val_part = rest[:-len(sfx)].strip()
                break
        else:
            val_part = rest

    # Swap dots and commas for values and deltas
    if not value.startswith("Rp"):
        val_part = val_part.translate(str.maketrans({',': '.', '.': ','}))

    unit_span = f'<span class="kpi-pro-unit" style="font-size:14px;color:#64748b;margin-left:4px;font-weight:600;">{escape(suffix)}</span>' if suffix else ""

    # Tanpa data periode sebelumnya, tidak ada apa pun yang bisa dibandingkan —
    # sembunyikan baris delta sepenuhnya daripada menampilkan angka palsu.
    if has_delta:
        delta_formatted = f"{abs(delta_pct):.1f}%".replace(".", ",")
        delta_html = (
            f'<div class="overview-kpi-delta">'
            f'<strong style="background:{delta_bg};color:{delta_fg};">{arrow} {escape(delta_formatted)}</strong> '
            f'vs periode sebelumnya'
            f'</div>'
        )
    else:
        delta_html = ""

    tooltip_attr = f' title="{escape(tooltip_val)}"' if tooltip_val else ""

    html = (
        f'<div class="overview-kpi-card rs-kpi-card"{tooltip_attr}>'
        f'<div class="overview-kpi-icon" style="background:{accent}14;color:{accent};">{escape(icon)}</div>'
        f'<div class="overview-kpi-copy">'
        f'<div class="overview-kpi-label">{escape(label)}</div>'
        f'<div class="overview-kpi-value">'
        f'<span class="kpi-val-num">{escape(prefix)}{escape(val_part)}</span>'
        f'{unit_span}'
        f'</div>'
        f'{delta_html}'
        f'</div>'
        f'</div>'
    )
    return html


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

    /* Same header-to-filter gap as the Lease Contract page. */
    body:has(.rs-page-marker) .ov-fixed-header-spacer,
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.ov-fixed-header-spacer) {
        height: 56px !important;
        min-height: 56px !important;
        max-height: 56px !important;
    }
    /* ── Filter Data card (same design as Lease Contract) ──────────── */
    body:has(.rs-page-marker) div[data-testid="stHorizontalBlock"]:has(.rs-filtercard-marker),
    body:has(.rs-page-marker) div[data-testid="stLayoutWrapper"]:has(.rs-filtercard-marker) {
        margin-top: -16px !important;
    }
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -1px rgba(0,0,0,0.015) !important;
        padding: 18px 20px 14px !important;
    }
    /* Jarak antara Filter dan KPI Grid di Revenue Sharing Page */
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.rs-kpi-grid),
    body:has(.rs-page-marker) div[data-testid="stLayoutWrapper"]:has(.rs-kpi-grid) {
        margin-top: -14px !important;
    }
    /* Jarak Vertikal antara KPI Grid dan Donut Card di Revenue Sharing Page */
    body:has(.rs-page-marker) [data-testid="stHorizontalBlock"]:has(.rs-donut-card),
    body:has(.rs-page-marker) [data-testid="stLayoutWrapper"]:has(.rs-donut-card) {
        margin-top: 10px !important;
    }
    /* Container untuk Revenue Alerts di Revenue Sharing Page */
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .rs-alerts-card):not(
        :has(div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] .rs-alerts-card)
    ) {
        padding-bottom: 35px !important;
    }
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.ov-vertical-spacer),
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-vertical-spacer) {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        height: 10px !important;
    }
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.ov-vertical-spacer) + div[data-testid="stElementContainer"],
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-vertical-spacer) + div[data-testid="stElementContainer"] {
        margin-top: -24px !important;
    }
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.ov-vertical-spacer) + div:has(.ed-card-marker),
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-vertical-spacer) + div:has(.ed-card-marker) {
        margin-top: -24px !important;
    }
    .rs-filtercard-head {
        display: flex; align-items: center; gap: 12px;
    }
    .rs-filtercard-icon {
        width: 34px; height: 34px; border-radius: 10px; flex: 0 0 34px;
        background: #EEF2FF; color: #4338CA;
        display: flex; align-items: center; justify-content: center;
    }
    .rs-filtercard-title {
        margin: 0 !important; color: #0F172A; font-size: 18px !important; font-weight: 700 !important;
        font-family: 'Montserrat', sans-serif !important; line-height: 1 !important;
    }
    .rs-filtercard-badge {
        display: inline-flex; align-items: center; margin-left: 8px;
        padding: 2px 8px; border-radius: 999px; vertical-align: middle;
        background: #F0FDF4; border: 1px solid #BBF7D0;
        font-size: 10.5px !important; font-weight: 700 !important; color: #16A34A;
        white-space: nowrap;
    }
    .rs-filtercard-sub {
        margin: 5px 0 0 !important; color: #64748B; font-size: 11px !important; font-weight: 400 !important;
        line-height: 1 !important;
        font-family: 'Inter', sans-serif !important;
    }
    .rs-filter-label {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 6px !important;
        color: #475569 !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
        font-family: Inter, sans-serif !important;
        margin: 0 0 6px 4px !important;
        height: 16px !important;
        line-height: 16px !important;
    }
    .rs-filter-label svg {
        display: block !important;
        flex-shrink: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .rs-filter-label span {
        line-height: 1 !important;
        display: inline-block !important;
    }
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.rs-filter-label) {
        margin-bottom: -4px !important;
    }
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.rs-filterrow-marker) {
        margin: 0 !important; padding: 0 !important; height: 0 !important;
    }
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.rs-filterrow-marker) + div[data-testid="stHorizontalBlock"],
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.rs-filterrow-marker) + div[data-testid="stLayoutWrapper"] {
        margin-top: -4px !important;
    }
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.rs-filtercard-footer-marker) {
        margin: 6px 0 -10px !important;
        height: 1px !important;
        border-top: 1px solid #F1F5F9 !important;
    }
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="baseButton-secondary"] {
        border: 1px solid #E2E8F0 !important; border-radius: 8px !important;
        background: #ffffff !important; color: #475569 !important;
        font-size: 11.5px !important; font-weight: 700 !important;
        font-family: Inter, sans-serif !important;
        height: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        width: 145px !important;
        min-width: 145px !important;
        max-width: 145px !important;
        padding: 0 !important;
        margin-left: auto !important; margin-right: 0 !important;
    }
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.rs-reset-top-marker) + div[data-testid="stElementContainer"] [data-testid="baseButton-secondary"],
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.rs-reset-top-marker) + div[data-testid="stElementContainer"] [data-testid="stBaseButton-secondary"] {
        border-radius: 999px !important;
        width: auto !important;
        min-width: 0 !important;
        max-width: none !important;
        height: 36px !important;
        min-height: 36px !important;
        max-height: 36px !important;
        padding: 0 18px !important;
        font-size: 13px !important;
    }
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.rs-reset-top-marker) + div[data-testid="stElementContainer"] [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded' !important;
        font-size: 15px !important;
    }
    body:has(.rs-page-marker) [data-testid="baseButton-primary"],
    body:has(.rs-page-marker) [data-testid="stBaseButton-primary"] {
        border-radius: 999px !important;
        font-size: 12.5px !important; font-weight: 700 !important;
        font-family: Inter, sans-serif !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    }
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="baseButton-primary"],
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="stBaseButton-primary"] {
        border-radius: 8px !important;
        font-size: 11.5px !important; font-weight: 700 !important;
        font-family: Inter, sans-serif !important;
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
    }
    body:has(.rs-page-marker) [data-testid="baseButton-primary"]:hover,
    body:has(.rs-page-marker) [data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.45) !important;
    }
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="baseButton-primary"]:hover,
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    }
    body:has(.rs-page-marker) [data-testid="baseButton-primary"] svg,
    body:has(.rs-page-marker) [data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"] {
        color: #ffffff !important;
        fill: #ffffff !important;
        font-family: 'Material Symbols Rounded' !important;
    }
    body:has(.rs-page-marker) [data-testid="baseButton-primary"] p,
    body:has(.rs-page-marker) [data-testid="stBaseButton-primary"] p {
        color: #ffffff !important;
    }
    /* ── Selectbox Dropdowns in Filter Card ────────────────────────── */
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="stSelectbox"] {
        margin-bottom: 0 !important;
    }
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="stSelectbox"] > div {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="stSelectbox"] > div > div {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        backdrop-filter: none !important;
    }
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 999px !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(99, 102, 241, 0.04) !important;
        transition: all 0.2s ease !important;
    }
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"]:hover {
        border-color: #CBD5E1 !important;
    }
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1) !important;
    }
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        min-height: 32px !important;
        height: 32px !important;
        max-height: 32px !important;
        padding: 0 4px 0 12px !important;
        display: flex !important;
        align-items: center !important;
    }
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"] {
        font-size: 11.5px !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }
    body:has(.rs-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.rs-filtercard-marker) [data-testid="stSelectbox"] svg {
        color: #64748B !important;
    }

    body:has(.rs-page-marker) .rs-kpi-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
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
        transition: all 0.3s ease !important;
    }
    body:has(.rs-page-marker) .rs-kpi-grid .rs-kpi-card:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05), 0 4px 6px -2px rgba(0,0,0,0.025) !important;
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
        font-family: Inter, sans-serif !important;
    }
    .rs-kpi-ring-card .overview-kpi-copy {
        position: relative !important;
    }

    .rs-alert-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
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
        font-family: Montserrat, sans-serif !important;
    }
    .rs-alert-sub {
        margin: 3px 0 0;
        color: #64748B;
        font-size: 11px;
        font-weight: 500;
        font-family: Inter, sans-serif !important;
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
        gap: 8px;
        font-size: 11.5px;
        color: #475569;
        font-family: Inter, sans-serif !important;
        padding: 5px 0;
        border-bottom: 1px solid #F1F5F9;
    }
    .rs-legend-row:last-child {
        border-bottom: none;
    }
    .rs-legend-left {
        display: flex;
        align-items: center;
        gap: 8px;
        min-width: 0;
        flex: 1 1 auto;
    }
    .rs-legend-icon {
        width: 22px;
        height: 22px;
        border-radius: 999px;
        flex: 0 0 22px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .rs-legend-icon svg {
        width: 12px;
        height: 12px;
    }
    .rs-legend-name {
        color: #1E293B;
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .rs-legend-revenue {
        color: #0F172A;
        font-weight: 700;
        white-space: nowrap;
        flex: 0 0 auto;
        text-align: right;
    }
    .rs-legend-pct {
        font-weight: 700;
        white-space: nowrap;
        flex: 0 0 auto;
        padding: 2px 8px;
        border-radius: 999px;
        font-size: 10.5px;
        min-width: 42px;
        text-align: center;
    }
    .rs-fy-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 6px;
        padding: 6px 12px;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
        background: #ffffff;
        color: #475569;
        font-size: 11.5px;
        font-weight: 600;
        font-family: Inter, sans-serif !important;
        float: right;
    }
    .rs-fy-pill svg {
        width: 13px;
        height: 13px;
    }
    .rs-donut-footnote {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-top: 12px;
        padding: 10px 14px;
        border-radius: 12px;
        background: #F8FAFC;
        border: 1px solid #F1F5F9;
    }
    .rs-donut-footnote-icon {
        width: 28px;
        height: 28px;
        border-radius: 8px;
        background: #EEF2FF;
        color: #6366F1;
        flex: 0 0 28px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .rs-donut-footnote-icon svg {
        width: 14px;
        height: 14px;
    }
    .rs-donut-footnote-copy p {
        margin: 0;
        font-size: 11.5px;
        color: #1E293B;
        font-weight: 600;
        font-family: Inter, sans-serif !important;
    }
    .rs-donut-footnote-sub {
        margin-top: 2px !important;
        color: #94A3B8 !important;
        font-weight: 500 !important;
        font-size: 10.5px !important;
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

    body:has(.rs-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .rs-detail-filter-marker):not(
        :has(div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] .rs-detail-filter-marker)
    ) {
        padding-top: 8px !important;
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
    body:has(.rs-page-marker) div[data-testid="stElementContainer"]:has(.rs-last-update) {
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    /* Export button on revenue sharing detail table */
    div[data-testid="stElementContainer"]:has(.rs-btn-export-marker) {
        position: absolute !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }
    div[data-testid="stElementContainer"]:has(.rs-btn-export-marker) + div[data-testid="stElementContainer"] button {
        background: rgba(255, 255, 255, 0.72) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        color: #4F46E5 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        padding: 0 16px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        min-height: 38px !important;
        height: 38px !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }
    div[data-testid="stElementContainer"]:has(.rs-btn-export-marker) + div[data-testid="stElementContainer"] button:hover {
        background: #f5f3ff !important;
        border-color: rgba(99, 102, 241, 0.45) !important;
    }
    div[data-testid="stElementContainer"]:has(.rs-btn-export-marker) + div[data-testid="stElementContainer"] button p {
        color: #4F46E5 !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stElementContainer"]:has(.rs-btn-export-marker) + div[data-testid="stElementContainer"] button::before {
        content: "" !important;
        display: inline-block !important;
        width: 14px !important;
        height: 14px !important;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%234F46E5" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>') !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        flex-shrink: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def _build_revenue_alerts(services_df):
    alerts = []
    if services_df.empty:
        return alerts

    top_svc = services_df.loc[services_df["_pendapatan_rs"].idxmax()]
    alerts.append(_alert_card_html(
        "positive", "✓",
        f"{top_svc['Service/SBU']} memberikan Revenue Sharing terbesar",
        f"Total Revenue Sharing {_fmt_rp_compact(top_svc['_pendapatan_rs'])}",
    ))
    return alerts


def _donut_figure(services_df, total_revenue):
    labels = services_df["Service/SBU"].tolist()
    values = services_df["Gross Revenue"].map(_parse_rp).tolist()
    colors = [RS_SERVICE_VISUAL.get(lbl, (None, "#94A3B8"))[1] for lbl in labels]
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        sort=False,
        direction="clockwise",
        marker=dict(colors=colors, line=dict(color="#ffffff", width=2)),
        textinfo="percent",
        textfont=dict(size=11, color="#ffffff", family=RS_FONT),
        hovertemplate="%{label}<br>%{value:,.0f}<extra></extra>",
    )])
    fig.update_layout(
        height=300,
        margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        showlegend=False,
        annotations=[dict(
            text=f"<b style='font-size:20px;'>{_fmt_rp_compact(total_revenue)}</b><br><span style='font-size:11px;color:#64748B'>Total Gross Revenue</span>",
            x=0.5, y=0.5, font=dict(size=14, color="#0F172A", family=RS_FONT), showarrow=False,
        )],
    )
    return fig


def _trend_figure(df_trend, unit_label="Rp"):
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
    y_max = 1.0
    if trend_columns:
        max_value = df_trend[trend_columns].max(numeric_only=True).max()
        if pd.notna(max_value) and max_value > 0:
            y_max = float(max_value) * 1.2
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
            title=dict(text=unit_label, font=dict(family=RS_FONT, size=11, color="#64748B")),
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
    values = services_df["Gross Revenue"].map(_parse_rp)
    display_df = services_df.assign(_val=values).sort_values("Service/SBU").reset_index(drop=True)

    rows = []
    for _, row in display_df.iterrows():
        name = row["Service/SBU"]
        pct = (row["_val"] / total_revenue * 100) if total_revenue else 0
        icon_key, color = RS_SERVICE_VISUAL.get(name, ("package", "#94A3B8"))
        rows.append(
            f'<div class="rs-legend-row">'
            f'<div class="rs-legend-left">'
            f'<span class="rs-legend-icon" style="background:{color}1A;color:{color};">{_rs_service_icon_svg(icon_key)}</span>'
            f"<span class=\"rs-legend-name\">{escape(name)}</span>"
            f"</div>"
            f'<span class="rs-legend-revenue">{escape(row["Gross Revenue"])}</span>'
            f'<span class="rs-legend-pct" style="background:{color}1A;color:{color};">{pct:.1f}%</span>'
            f"</div>"
        )
    return f'<div class="rs-donut-legend">{"".join(rows)}</div>'


# ══════════════════════════════════════════════
# PAGE: REVENUE SHARING
# ══════════════════════════════════════════════
def page_revenue_sharing(df_raw=None):
    for key, default in [
        ("rs_year", "All Year"),
        ("rs_month", "All Month"),
        ("rs_terminal", "All Terminal"),
        ("rs_detail_page", 1),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    for pend_key, applied_key in (
        ("rs_pend_terminal", "rs_terminal"), ("rs_pend_year", "rs_year"), ("rs_pend_month", "rs_month"),
    ):
        if pend_key not in st.session_state:
            st.session_state[pend_key] = st.session_state[applied_key]

    active_count = sum([
        st.session_state.get("rs_year", "All Year") != "All Year",
        st.session_state.get("rs_month", "All Month") != "All Month",
        st.session_state.get("rs_terminal", "All Terminal") != "All Terminal",
    ])

    # Load granular detail dataframe — opsi filter & filtering itu sendiri
    # sama-sama bersumber dari sini, supaya dropdown selalu cocok dengan apa
    # yang sebenarnya ada di data (bukan daftar tahun/bulan/terminal statis).
    detail_df_raw = get_detail_revenue_sharing_data(df_raw)

    terminal_options = ["All Terminal"] + sorted(
        v for v in detail_df_raw["Terminal"].dropna().unique().tolist() if v != "Unknown"
    )
    year_options = ["All Year"] + [
        str(y) for y in sorted(detail_df_raw["_tahun"].dropna().unique().tolist(), reverse=True)
    ]
    bulan_values = set(detail_df_raw["_bulan"].dropna().unique().tolist())
    month_options = ["All Month"] + [m for m in RS_MONTH_ORDER if m in bulan_values]

    if st.session_state.get("rs_terminal") not in terminal_options:
        st.session_state.rs_terminal = terminal_options[0]
    if st.session_state.get("rs_year") not in year_options:
        st.session_state.rs_year = year_options[0]
    if st.session_state.get("rs_month") not in month_options:
        st.session_state.rs_month = month_options[0]
    for pend_key, applied_key, options in (
        ("rs_pend_terminal", "rs_terminal", terminal_options),
        ("rs_pend_year", "rs_year", year_options),
        ("rs_pend_month", "rs_month", month_options),
    ):
        if st.session_state.get(pend_key) not in options:
            st.session_state[pend_key] = st.session_state[applied_key]

    st.markdown('<div class="overview-page-marker rs-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    _inject_rs_page_css()

    with st.container():
        st.markdown('<div class="ov-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_rs_page_header_html(), unsafe_allow_html=True)
        st.markdown('<div class="ov-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="ov-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        _render_rs_filter_card(active_count, terminal_options, year_options, month_options)

    _mount_rs_fixed_header()

    # Apply global filters (Year, Month, Terminal)
    filtered_detail = detail_df_raw.copy()
    if st.session_state.rs_year != "All Year":
        filtered_detail = filtered_detail[filtered_detail["_tahun"] == int(st.session_state.rs_year)]
    if st.session_state.rs_month != "All Month":
        filtered_detail = filtered_detail[filtered_detail["_bulan"] == st.session_state.rs_month]
    if st.session_state.rs_terminal != "All Terminal":
        filtered_detail = filtered_detail[filtered_detail["Terminal"] == st.session_state.rs_terminal]

    # Dynamically build SBU services summary from filtered details
    if not filtered_detail.empty:
        grouped_svc = filtered_detail.groupby("Service/SBU").agg(
            # Donut "Revenue Contribution by Service" pakai Total Kontribusi,
            # supaya konsisten dengan total di tengah donut (juga dari kontribusi).
            Gross_Revenue_Val=("Management Share", lambda x: x.map(_parse_rp).sum()),
            Mgmt_Share_Val=("Management Share", lambda x: x.map(_parse_rp).sum()),
            # Revenue Sharing asli (pendapatan_rs) per kategori — dipakai khusus
            # untuk "Revenue Alerts", terpisah dari Total Kontribusi di donut.
            RS_Val=("_pendapatan_rs", "sum"),
            Share_Rule=("Share %", "first"),
        ).reset_index()

        services_df = pd.DataFrame({
            "Service/SBU": grouped_svc["Service/SBU"],
            "Gross Revenue": grouped_svc["Gross_Revenue_Val"].map(_fmt_rp_compact),
            "SBU Share Rule %": grouped_svc["Share_Rule"],
            "Management Share": grouped_svc["Mgmt_Share_Val"].map(_fmt_rp_compact),
            "_pendapatan_rs": grouped_svc["RS_Val"],
        })
    else:
        services_df = pd.DataFrame(columns=["Service/SBU", "Gross Revenue", "SBU Share Rule %", "Management Share", "_pendapatan_rs"])

    # Compute KPIs
    total_revenue, revenue_share = _compute_filtered_kpis(filtered_detail)

    # Periode pembanding: tahun yang sama dikurangi 1, dengan filter bulan &
    # terminal yang sama. Tanpa tahun spesifik dipilih ("All Year"), tidak ada
    # satu "tahun sebelumnya" yang jelas, jadi delta-nya N/A.
    if st.session_state.rs_year != "All Year":
        prior_year = int(st.session_state.rs_year) - 1
        prior_detail = detail_df_raw.copy()
        prior_detail = prior_detail[prior_detail["_tahun"] == prior_year]
        if st.session_state.rs_month != "All Month":
            prior_detail = prior_detail[prior_detail["_bulan"] == st.session_state.rs_month]
        if st.session_state.rs_terminal != "All Terminal":
            prior_detail = prior_detail[prior_detail["Terminal"] == st.session_state.rs_terminal]
        prior_revenue, prior_share = _compute_filtered_kpis(prior_detail)
        revenue_delta = _pct_change(total_revenue, prior_revenue)
        share_delta = _pct_change(revenue_share, prior_share)
    else:
        revenue_delta = None
        share_delta = None

    st.markdown(
        _kpi_grid_html(
            _kpi_card("Total Revenue", _fmt_rp_compact(total_revenue), revenue_delta, "#2563EB", "Rp", tooltip_val=_fmt_rp_full(total_revenue)),
            _kpi_card("Revenue Share", _fmt_rp_compact(revenue_share), share_delta, "#7C3AED", "%", tooltip_val=_fmt_rp_full(revenue_share)),
        ),
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ov-vertical-spacer"></div>', unsafe_allow_html=True)

    # Sumber trend chart: df_raw mentah (bukan detail_df_raw yang sudah
    # diformat jadi teks "Rp ..."), difilter Tahun & Terminal yang sama
    # dengan filter aktif di halaman ini.
    trend_source = df_raw.copy() if df_raw is not None else pd.DataFrame()
    if not trend_source.empty:
        if st.session_state.rs_year != "All Year":
            col_tahun_raw = _resolve_col(trend_source, "tahun")
            if col_tahun_raw in trend_source.columns:
                trend_source = trend_source[
                    pd.to_numeric(trend_source[col_tahun_raw], errors="coerce") == int(st.session_state.rs_year)
                ]
        if st.session_state.rs_terminal != "All Terminal":
            col_terminal_raw = _resolve_col(trend_source, "terminal")
            if col_terminal_raw in trend_source.columns:
                trend_source = trend_source[trend_source[col_terminal_raw] == st.session_state.rs_terminal]
    trend_df, trend_unit_label = get_trend_data_from_df(trend_source)

    chart_left, chart_right = st.columns([46, 54], gap="small")
    with chart_left:
        st.markdown('<div class="ed-card-marker rs-donut-card"></div>', unsafe_allow_html=True)
        ch1, ch2 = st.columns([3.2, 1])
        with ch1:
            st.markdown(
                '<p class="ed-section-title">Revenue Contribution by Service</p>'
                '<p class="ed-section-sub">Distribusi gross revenue per layanan / SBU</p>',
                unsafe_allow_html=True,
            )
        with ch2:
            if st.session_state.rs_year != "All Year":
                fy_label = f"FY {st.session_state.rs_year}"
            else:
                years = sorted(filtered_detail["_tahun"].dropna().unique().tolist())
                if len(years) == 1:
                    fy_label = f"FY {int(years[0])}"
                elif len(years) > 1:
                    fy_label = f"FY {int(years[0])}–{int(years[-1])}"
                else:
                    fy_label = "All Year"
            st.markdown(
                f'<div class="rs-fy-pill">{_rs_service_icon_svg("calendar")}<span>{fy_label}</span></div>',
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
        st.markdown(
            '<div class="rs-donut-footnote">'
            f'<span class="rs-donut-footnote-icon">{_rs_service_icon_svg("bar-chart")}</span>'
            '<div class="rs-donut-footnote-copy">'
            f'<p>{len(services_df)} layanan berkontribusi terhadap total gross revenue</p>'
            f'<p class="rs-donut-footnote-sub">Sumber: Data Finance {fy_label}</p>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    with chart_right:
        st.markdown('<div class="ed-card-marker rs-trend-card"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<p class="ed-section-title">Revenue Trend</p>'
            f'<p class="ed-section-sub">Monthly revenue trend by service category ({trend_unit_label})</p>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            _trend_figure(trend_df, trend_unit_label),
            use_container_width=True,
            config={"displayModeBar": False},
        )

    st.markdown('<div class="ov-vertical-spacer"></div>', unsafe_allow_html=True)

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

    st.markdown('<div class="ov-vertical-spacer"></div>', unsafe_allow_html=True)

    # Moved from Overview: Revenue Per Sqm + Best 3 Achievement (tenant-level
    # data). Uses the same df_raw already passed into this page rather than
    # re-querying the backend, computing the acv/rev_sqm metrics locally
    # since this df_raw hasn't been through Overview's normalize step.
    tenant_df = df_raw.copy() if df_raw is not None else pd.DataFrame()
    for col in ["perusahaan", "brand", "kode_ruang", "real_omzet", "min_omzet", "luas_sqm", "kontribusi"]:
        if col not in tenant_df.columns:
            tenant_df[col] = 0 if col in ("real_omzet", "min_omzet", "luas_sqm", "kontribusi") else "Tidak diketahui"
    if not tenant_df.empty:
        # Pakai kolom acv asli dari data kalau terisi; rumus real_omzet/min_omzet
        # cuma fallback kalau memang kosong di sumbernya (sama seperti Overview).
        # Sel ACV di Excel berformat persen, nilai mentahnya pecahan (1 = 100%),
        # jadi dikali 100 dulu supaya skalanya sama dengan rumus fallback.
        acv_raw = pd.to_numeric(tenant_df["acv"], errors="coerce") if "acv" in tenant_df.columns else pd.Series(pd.NA, index=tenant_df.index)
        acv_raw = acv_raw * 100
        acv_fallback = (tenant_df["real_omzet"] / tenant_df["min_omzet"].replace(0, pd.NA) * 100).fillna(0)
        tenant_df["acv"] = acv_raw.where(acv_raw.notna() & (acv_raw != 0), acv_fallback)
        # Rev/Sqm = Total Kontribusi / Produksi M2 (luas_sqm), bukan Real Omzet / luas_sqm.
        tenant_df["rev_sqm"] = (tenant_df["kontribusi"] / tenant_df["luas_sqm"].replace(0, pd.NA)).fillna(0)

    if tenant_df.empty:
        tenant_summary = pd.DataFrame(columns=["perusahaan", "brand", "real_revenue", "acv", "contribution"])
        rev_sqm_source = pd.DataFrame(columns=["perusahaan", "brand", "kode_ruang", "rev_sqm"])
    else:
        tenant_summary = (
            tenant_df.groupby(["perusahaan", "brand"])
            .agg(real_revenue=("real_omzet", "sum"), acv=("acv", "mean"), contribution=("kontribusi", "sum"))
            .reset_index()
        )
        rev_sqm_source = (
            tenant_df.groupby(["perusahaan", "brand", "kode_ruang"], as_index=False)
            .agg(rev_sqm=("rev_sqm", "mean"))
            .sort_values("rev_sqm", ascending=False)
            .head(5)
        )
    df_best3 = tenant_summary.sort_values("acv", ascending=False).head(3).copy()

    rev_rows = ""
    for _, row in rev_sqm_source.iterrows():
        rev_val = f'<span class="ed-value-blue">{escape(_fmt_rp_compact(row["rev_sqm"]))}</span>'
        rev_rows += f"""<tr>
            <td>{escape(str(row["perusahaan"]))}</td>
            <td>{escape(str(row["brand"]))}</td>
            <td>{escape(str(row["kode_ruang"]))}</td>
            <td class="ed-td-right">{rev_val}</td>
        </tr>"""

    best_rows = ""
    for i, (_, row) in enumerate(df_best3.iterrows()):
        badge = f'<span class="ed-rank-badge rank-{i+1}">{i+1}</span>'
        acv_val = f'<span class="ed-positive">{row["acv"]:.1f}%</span>'.replace(".", ",")
        best_rows += f"""<tr>
            <td><span class="ed-tenant-with-rank">{badge}{escape(str(row["perusahaan"]))}</span></td>
            <td class="ed-td-center">{escape(str(row["brand"]))}</td>
            <td class="ed-td-right">{acv_val}</td>
        </tr>"""

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:12px;">
        <div class="ed-table-card" style="display:flex;flex-direction:column;">
            <div class="ed-table-head">
                <p class="ed-table-title">Revenue Per Sqm</p>
            </div>
            <div class="ed-table-scroll" style="flex:1;">
                <table class="ed-table">
                    <thead><tr>
                        <th>Tenant</th>
                        <th>Brand</th>
                        <th>Kode Ruang</th>
                        <th class="ed-th-right">Rev/Sqm</th>
                    </tr></thead>
                    <tbody>{rev_rows}</tbody>
                </table>
            </div>
        </div>
        <div class="ed-table-card ed-table-best3" style="display:flex;flex-direction:column;">
            <div class="ed-table-head">
                <p class="ed-table-title">Best 3 Achievement</p>
            </div>
            <div class="ed-table-scroll" style="flex:1;">
                <table class="ed-table">
                    <thead><tr>
                        <th>Tenant</th>
                        <th class="ed-th-center">Brand</th>
                        <th class="ed-th-right">ACT%</th>
                    </tr></thead>
                    <tbody>{best_rows}</tbody>
                </table>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="ov-vertical-spacer"></div>', unsafe_allow_html=True)

    detail_card = st.container()
    with detail_card:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        st.markdown('<div class="rs-detail-filter-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        dh1, ds, dex, dpp = st.columns([3.45, 2.40, 0.78, 0.72], vertical_alignment="center")
        with dh1:
            st.markdown(
                '<p class="ed-section-title">Detail Revenue Sharing</p>'
                '<p class="ed-section-sub">Granular revenue sharing records by service and terminal</p>',
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

        detail_df = filtered_detail.copy()
        if search_query:
            q = search_query.lower().strip()
            detail_df = detail_df[
                detail_df["Tenant"].astype(str).str.lower().str.contains(q, na=False)
                | detail_df["Brand"].astype(str).str.lower().str.contains(q, na=False)
                | detail_df["Kode Ruang"].astype(str).str.lower().str.contains(q, na=False)
                | detail_df["Service/SBU"].astype(str).str.lower().str.contains(q, na=False)
                | detail_df["Terminal"].astype(str).str.lower().str.contains(q, na=False)
            ]

        export_df = detail_df[["Tenant", "Brand", "Kode Ruang", "Terminal", "Service/SBU", "Omzet", "Share %", "Revenue"]].copy()
        export_df.columns = ["Tenant", "Brand", "Kode Ruang", "Terminal", "Service", "Omzet", "Share %", "Revenue Sharing"]
        for col in ["Omzet", "Share %", "Revenue Sharing"]:
            export_df[col] = export_df[col].apply(lambda x: str(x).translate(str.maketrans({",": ".", ".": ","})))

        with dex:
            st.markdown('<div class="rs-btn-export-marker"></div>', unsafe_allow_html=True)
            st.download_button(
                "Export",
                data=dataframe_to_excel_bytes(export_df, "Detail Revenue Sharing"),
                file_name="detail_revenue_sharing.xlsx",
                mime=EXCEL_MIME,
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
        # Translate static numeric strings (e.g. "Rp 12.1M" -> "Rp 12,1M") to Indonesian format
        detail_view["Omzet"] = detail_view["Omzet"].apply(lambda x: str(x).translate(str.maketrans({',': '.', '.': ','})))
        detail_view["Revenue"] = detail_view["Revenue"].apply(lambda x: str(x).translate(str.maketrans({',': '.', '.': ','})))
        detail_view["Share %"] = detail_view["Share %"].apply(lambda x: str(x).translate(str.maketrans({',': '.', '.': ','})))
        detail_view = detail_view[[
            "Tenant", "Brand", "Kode Ruang", "Terminal", "Service/SBU", "Omzet", "Share %", "Revenue",
        ]]
        detail_view.columns = ["Tenant", "Brand", "Kode Ruang", "Terminal", "Service", "Omzet", "Share %", "Revenue Sharing"]
        detail_align = {
            "Omzet": "right",
            "Share %": "right",
            "Revenue Sharing": "right",
        }
        st.markdown(_enterprise_table_inner_html(detail_view, col_align=detail_align), unsafe_allow_html=True)

        first_item = 0 if total_rows == 0 else start_idx + 1
        last_item = min(end_idx, total_rows)

        st.markdown('<div class="overview-detail-pagination-footer-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        rs_page_input = render_pagination(
            current_page=st.session_state.rs_detail_page,
            total_pages=total_pages,
            first_item=first_item,
            last_item=last_item,
            total_rows=total_rows,
            sync_key="rs_detail_page_sync"
        )
        if rs_page_input and rs_page_input.isdigit():
            new_page = int(rs_page_input)
            if new_page != st.session_state.rs_detail_page:
                st.session_state.rs_detail_page = new_page
                st.rerun()

        # Mount Javascript listener
        patch_pagination()


if __name__ == "__main__":
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Admin"
    if "user_email" not in st.session_state:
        st.session_state.user_email = "injourneyairports@mail.com"
    if "user_role" not in st.session_state:
        st.session_state.user_role = "Admin"
    page_revenue_sharing()
