from .navigation import show_topnav, topnav_actions_html
from .revenue_sharing import page_revenue_sharing, get_detail_revenue_sharing_data
from .room_database import render_room_database
from .lease_contract import render_lease_contract, _get_contract_source_data
from .import_manager import render_import_manager
from .Data_verification import render_data_verification
from .traffic_monitor import page_traffic_monitor
from .dashboard_style import DASHBOARD_CSS
from .app_styles import _APP_MAIN_CSS, _OVERVIEW_EXTRA_CSS
from .pagination import render_pagination, patch_pagination
from login.access_control import (
    IDLE_TIMEOUT_SECONDS,
    IDLE_WARNING_LEAD_SECONDS,
    Role,
    get_current_role,
    init_auth_state,
    is_authenticated,
    session_time_remaining,
)
from .session_watchdog import inject_session_watchdog
from .connection import get_engine
from .export_utils import EXCEL_MIME, dataframe_to_excel_bytes
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from sqlalchemy import text
from html import escape
from textwrap import dedent
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

OVERVIEW_FONT_FAMILY = "Inter, sans-serif"

# ─────────────────────────────────────────────
# MEMUAT CSS
# ─────────────────────────────────────────────
def inject_dashboard_css():
    st.markdown(f"<style>{DASHBOARD_CSS}</style>", unsafe_allow_html=True)
    st.markdown(_APP_MAIN_CSS, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
ROLE_MENUS = {
    Role.USER: [
        "Overview",
        "Revenue Sharing",
        "Lease Contract",
        "Traffic Monitor",
        "Room Database",
        "Import Manager",
        "Data Verification",
    ],
    Role.ADMIN: [
        "Overview",
        "Revenue Sharing",
        "Lease Contract",
        "Traffic Monitor",
    ],
}


def get_allowed_menus():
    return ROLE_MENUS.get(get_current_role(), ["Overview"])


def can_access_menu(menu_name):
    return menu_name in get_allowed_menus()


# ─────────────────────────────────────────────
# DATABASE & DATA
# ─────────────────────────────────────────────
@st.cache_data(ttl=300)
def load_dashboard_data():
    query = text("""
        SELECT
            tr.document_date,
            tr.masa_jasa,
            tr.tahun,
            tm.perusahaan,
            tm.brand,
            tr.kode_ruang,
            tr.pic,
            tr.ro_number,
            tm.terminal,
            tr.sub_terminal,
            tr.area,
            tm.lokasi,
            tr.lantai,
            tr.gate,
            tr.smoking_status,
            tr.sub_bidang_usaha,
            tm.bidang_usaha,
            tr.coa,
            tr.nomor_kontrak_sistem,
            k.nomor_kontrak_legal,
            k.start_kontrak,
            k.end_kontrak,
            tr.csp_non_csp,
            k.jenis_kontrak AS kerja_sama,
            tr.pemilihan_mitra_usaha,
            tr.produksi_m2,
            tr.produksi_m2 AS luas_sqm,
            tr.tarif_sewa_ruang_m2,
            k.sharing_percent AS rs_percent,
            k.minimal_omzet AS min_omzet,
            tr.real_omzet,
            k.mgrs_per_pax,
            tr.real_pax,
            tr.real_pax AS jumlah_pax,
            tr.pendapatan_rs,
            tr.pendapatan_sewa,
            tr.total_kontribusi,
            tr.total_kontribusi AS kontribusi,
            tr.acv,
            tr.rev_per_sqm,
            tr.rev_per_sqm AS rev_sqm,
            tr.spending_per_pax,
            tr.doc_number_rs,
            tr.doc_number_sewa,
            tr.variant_no,
            tr.catatan,
            tr.trafik_int_arr,
            tr.trafik_int_dep,
            tr.subtotal_trafik_int,
            tr.trafik_dom_arr,
            tr.trafik_dom_dep,
            tr.subtotal_trafik_dom,
            tr.total_trafik,
            tr.tenant_id,
            tr.import_id
        FROM transaction_revenue tr
        LEFT JOIN tenant_master tm ON tr.tenant_id = tm.id
        LEFT JOIN kontrak k ON tr.nomor_kontrak_sistem = k.nomor_kontrak_sistem
        WHERE EXISTS (
            SELECT 1
            FROM import_history ih
            WHERE ih.import_id = tr.import_id
              AND COALESCE(ih.is_active, true) = true
        )
        ORDER BY tr.import_id DESC NULLS LAST, tr.tahun DESC NULLS LAST, tr.masa_jasa
    """)

    try:
        with get_engine().connect() as conn:
            df = pd.read_sql(query, conn)
    except Exception as exc:
        st.session_state["dashboard_data_error"] = str(exc)
        return None

    st.session_state.pop("dashboard_data_error", None)
    return df

def get_active_dashboard_data():
    return load_dashboard_data()


BULAN = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]

KPI_GRADIENTS = [
    ("linear-gradient(135deg,#4f46e5,#6366f1)", "rgba(99,102,241,0.12)"),
    ("linear-gradient(135deg,#0891b2,#06b6d4)", "rgba(6,182,212,0.12)"),
    ("linear-gradient(135deg,#059669,#10b981)", "rgba(16,185,129,0.12)"),
    ("linear-gradient(135deg,#e11d48,#f43f5e)", "rgba(244,63,94,0.10)"),
    ("linear-gradient(135deg,#7c3aed,#8b5cf6)", "rgba(139,92,246,0.12)"),
    ("linear-gradient(135deg,#d97706,#f59e0b)", "rgba(245,158,11,0.12)"),
    ("linear-gradient(135deg,#db2777,#ec4899)", "rgba(236,72,153,0.10)"),
]


def _ed_card_marker(container, extra_class: str = "") -> None:
    marker_class = "ed-card-marker"
    if extra_class:
        marker_class = f"{marker_class} {extra_class}"
    container.markdown(f'<div class="{marker_class}"></div>', unsafe_allow_html=True)


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


# ══════════════════════════════════════════════
# FUNGSI BANTU: Kartu KPI "pro" (ikon + badge + progress bar)
# ══════════════════════════════════════════════
KPI_PRO_ICON_PATHS = {
    "omzet":  '<line x1="12" y1="2" x2="12" y2="22"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
    "layers": '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path>',
    "file":   '<path d="m3 9 9-7 9 7"></path><path d="M4 10v10a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1V10"></path>',
    "bars":   '<line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>',
    "users":  '<rect width="20" height="14" x="2" y="5" rx="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line>',
    "expand": '<rect width="18" height="18" x="3" y="3" rx="2"></rect>',
    "award":  '<circle cx="12" cy="8" r="6"></circle><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"></path>',
    "plane":  '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"></path>',
}


def _kpi_pro_icon_svg(icon_key: str) -> str:
    paths = KPI_PRO_ICON_PATHS[icon_key]
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
    )


def _compact_number(value, decimals=1):
    if value is None or pd.isna(value):
        value = 0
    value = float(value)
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        val_str = f"{value / 1_000_000_000_000:.{decimals}f}"
        return val_str.replace(".", ","), "T"
    if abs_value >= 1_000_000_000:
        val_str = f"{value / 1_000_000_000:.{decimals}f}"
        return val_str.replace(".", ","), "M"
    if abs_value >= 1_000_000:
        val_str = f"{value / 1_000_000:.{decimals}f}"
        return val_str.replace(".", ","), "Jt"
    if abs_value >= 1_000:
        val_str = f"{value:,.0f}"
        return val_str.replace(",", "."), ""
    val_str = f"{value:.{decimals}f}"
    return val_str.replace(".", ","), ""


def _pct_change(current, base):
    if not base:
        return None
    return (current - base) / base * 100


def _kpi_pro_card(label, value, unit, subtitle, delta_pct, accent, icon_key, bar_label, tooltip_val=None):
    has_delta = delta_pct is not None
    is_down = has_delta and delta_pct < 0
    badge_cls = "is-down" if is_down else ""
    arrow = "↘" if is_down else "↗"
    bar_width = min(100, max(6, 50 + delta_pct * 2.2)) if has_delta else 50

    # Mengurai satuan untuk memisahkan awalan (seperti "Rp") dan akhiran (seperti "M", "Jt", atau kosong)
    prefix = ""
    display_unit = unit
    if unit.startswith("Rp"):
        prefix = "Rp "
        display_unit = unit[2:].strip()

    unit_gap = "" if display_unit == "%" else " "
    unit_span = f'<span class="kpi-pro-unit">{unit_gap}{escape(display_unit)}</span>' if display_unit else ""

    # Format tampilan persentase ke format desimal Indonesia (koma)
    formatted_pct = f"{arrow} {abs(delta_pct):.1f}%".replace(".", ",") if has_delta else "N/A"

    # Sembunyikan footer pembanding jika tidak ada data untuk periode pembanding.
    foot_html = (
        f'<div class="kpi-pro-foot">'
        f'<div class="kpi-pro-bar-row">'
        f'<span>{escape(bar_label)}</span>'
        f'<span style="color:{accent};">{formatted_pct}</span>'
        f'</div>'
        f'<div class="kpi-pro-bar-track">'
        f'<div class="kpi-pro-bar-fill" style="width:{bar_width:.0f}%;background:{accent};"></div>'
        f'</div>'
        f'</div>'
    ) if has_delta else ""

    tooltip_attr = f' title="{escape(tooltip_val)}"' if tooltip_val else ""

    html = (
        f'<div class="kpi-pro-card"{tooltip_attr}>'
        f'<div class="kpi-pro-head">'
        f'<div class="kpi-pro-icon" style="background:{accent}1A;color:{accent};">{_kpi_pro_icon_svg(icon_key)}</div>'
        f'<div class="kpi-pro-badge {badge_cls}">{formatted_pct}</div>'
        f'</div>'
        f'<div class="kpi-pro-body">'
        f'<div class="kpi-pro-label">{escape(label)}</div>'
        f'<div class="kpi-pro-value-row">'
        f'<span class="kpi-pro-value">{escape(prefix)}{escape(value)}</span>'
        f'{unit_span}'
        f'</div>'
        f'<div class="kpi-pro-sub">{escape(subtitle)}</div>'
        f'</div>'
        f'{foot_html}'
        f'</div>'
    )
    return html


ALERT_ICON_PATHS = {
    "trending-down":   '<polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline>',
    "trending-up":     '<polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline>',
    "briefcase":       '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path>',
    "map-pin":         '<path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle>',
    "alert-triangle":  '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line>',
    "file-minus":      '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="9" y1="15" x2="15" y2="15"></line>',
    "clock":           '<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>',
    "pie-chart":       '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path>',
}

def _alert_icon_svg(icon_key: str) -> str:
    paths = ALERT_ICON_PATHS.get(icon_key, "")
    if not paths:
        return ""
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
    )

def _alert_item_html(icon_key_or_html, accent, title, subtitle):
    if icon_key_or_html in ALERT_ICON_PATHS:
        icon_content = _alert_icon_svg(icon_key_or_html)
    elif icon_key_or_html.startswith("<svg"):
        icon_content = icon_key_or_html
    else:
        icon_content = escape(icon_key_or_html)

    return dedent(f"""
    <div class="ed-alert-item">
        <div class="ed-alert-icon" style="background:{accent}14;color:{accent};">{icon_content}</div>
        <div style="flex:1;min-width:0;">
            <p class="ed-alert-title">{escape(title)}</p>
            <p class="ed-alert-sub">{escape(subtitle)}</p>
        </div>
    </div>
    """).strip()


def _table_col_class(col_name: str, col_align: dict | None, prefix: str = "ed-th") -> str:
    align = (col_align or {}).get(str(col_name), "left")
    return f'{prefix}-{align}'


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
            if text.startswith("<span "):
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


# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════


def _nav_icon(*paths: str) -> str:
    inner = "".join(paths)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'width="18" height="18" fill="none" stroke="currentColor" '
        'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{inner}</svg>'
    )


NAV_ICONS = {
    "Overview": _nav_icon(
        '<rect x="3" y="3" width="7" height="7" rx="1.5"/>',
        '<rect x="14" y="3" width="7" height="7" rx="1.5"/>',
        '<rect x="3" y="14" width="7" height="7" rx="1.5"/>',  
        '<rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    ),
    "Revenue Sharing": _nav_icon(
        '<circle cx="18" cy="5" r="3"/>',
        '<circle cx="6" cy="12" r="3"/>',
        '<circle cx="18" cy="19" r="3"/>',
        '<line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>',
        '<line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>',
    ),
    "Lease Contract": _nav_icon(
        '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>',
        '<polyline points="14 2 14 8 20 8"/>',
        '<path d="M10 16h4"/>',
        '<path d="m8 12.5 4-4a1.5 1.5 0 0 1 2 2l-4 4-2 0z"/>',
    ),
    "Traffic Monitor": _nav_icon(
        '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    ),
    "Import Manager": _nav_icon(
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>',
        '<polyline points="17 8 12 3 7 8"/>',
        '<line x1="12" y1="3" x2="12" y2="15"/>',
    ),
    "Data Verification": _nav_icon(
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
        '<path d="m9 12 2 2 4-4"/>',
    ),
}


def _overview_page_header_html():
    return dedent(f"""
    <div class="ov-page-header">
        <div class="ov-page-header-left">
            <div class="ov-page-icon" aria-hidden="true">{NAV_ICONS["Overview"]}</div>
            <div class="ov-page-header-copy">
                <div class="ov-page-title-row">
                    <h2 class="ov-page-title">Overview</h2>
                </div>
                <p class="ov-page-sub">Monitor commercial revenue and operational performance.</p>
            </div>
        </div>
        {topnav_actions_html()}
    </div>
    """).strip()


def _mount_overview_fixed_header():
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


def _go_to_menu(menu_name):
    if not can_access_menu(menu_name):
        st.session_state.active_menu = "Overview"
        return
    st.session_state.active_menu = menu_name


if not hasattr(st, "_ap_original_button"):
    st._ap_original_button = st.button


def _ap_button(*args, **kwargs):
    key = kwargs.get("key")

    if isinstance(key, str) and key.startswith("nav_"):
        kwargs.setdefault("on_click", _go_to_menu)
        kwargs.setdefault("args", (key.removeprefix("nav_"),))
        st._ap_original_button(*args, **kwargs)
        return False

    return st._ap_original_button(*args, **kwargs)


st.button = _ap_button


def _sidebar_brand_logo_svg():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'width="18" height="18" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="color: #ffffff;">'
        '<path d="M17.8 19.2 16 11l3.5-3.5a2.1 2.1 0 1 0-3-3L13 8 4.8 6.2c-.5-.1-1 .1-1.2.5l-.3.3c-.2.3-.2.7 0 1l6.7 4.1L6 16.2c-.3.3-.4.8-.2 1.1l.3.3c.3.2.8.1 1.1-.2l4.1-4.1 4.1 6.7c.3.2.7.2 1 0l.3-.3c.4-.2.6-.7.5-1.2z"/>'
        '</svg>'
    )


def _sidebar_brand():
    if st.session_state.get("sidebar_minimized", False):
        st.markdown(f"""
        <div class="ap-brand ap-brand-mini">
            <div class="ap-logo">{_sidebar_brand_logo_svg()}</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="ap-brand">
        <div style="display:flex;align-items:center;gap:12px;">
            <div class="ap-logo">{_sidebar_brand_logo_svg()}</div>
            <div class="ap-brand-copy">
                <div class="ap-brand-name">AirportBI</div>
                <div class="ap-brand-sub">Commercial Suite</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


def _sidebar_footer():
    if st.session_state.get("sidebar_minimized", False):
        st.markdown(
            '<div class="ap-sidebar-footer" style="font-size: 12px !important;">'
            '© 2026</div>',
            unsafe_allow_html=True,
        )
        return
    st.markdown("""
    <div class="ap-sidebar-footer">
        © 2026 INJOURNEY AIRPORTS. ALL RIGHTS RESERVED.
    </div>
    """, unsafe_allow_html=True)


def show_sidebar():
    with st.sidebar:

        _sidebar_brand()

        st.markdown('<div class="nav-category-header">NAVIGATION</div>', unsafe_allow_html=True)

        menu_items = [
            "Overview",
            "Revenue Sharing",
            "Lease Contract",
            "Traffic Monitor",
            "Import Manager",
            "Data Verification",
        ]
        for label in menu_items:
            _nav_row(NAV_ICONS[label], label)

        st.markdown('<div class="ap-sidebar-spacer"></div>', unsafe_allow_html=True)
        _sidebar_footer()


def _nav_row(icon, label):
    if not can_access_menu(label):
        return

    mini = st.session_state.get("sidebar_minimized", False)
    is_active = st.session_state.active_menu == label
    label_html = "" if mini else f'<span class="nav-label">{escape(label)}</span>'

    st.button(" ", key=f"nav_{label}", help=label if mini else None, use_container_width=True)

    if is_active:
        st.markdown(
            f"""
            <div class="nav-active nav-overlay" title="{escape(label)}">
                <span class="nav-indicator-pill"></span>
                <span class="nav-icon-box">{icon}</span>
                {label_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="nav-row nav-overlay" title="{escape(label)}">
                <span class="nav-icon-box">{icon}</span>
                {label_html}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ══════════════════════════════════════════════
# HALAMAN OVERVIEW
# ══════════════════════════════════════════════
_OV_FILTER_DEFAULTS = {
    "f_terminal": "All Terminal", "f_tahun": "All Year", "f_masa": "All Month",
    "f_perusahaan": "All Perusahaan", "f_kode_ruang": "All Kode Ruang",
}


def _overview_normalize_and_ensure_columns(df_raw):
    """Menyelaraskan nama kolom dari data sumber (query DB / upload Import Manager)
    ke nama internal dashboard menggunakan alias. Mengisi kolom wajib yang kosong
    dengan nilai default aman agar proses filter dan perhitungan KPI berikutnya tidak error."""
    df = df_raw.copy()

    # =========================================================
    # 1. NORMALISASI NAMA KOLOM
    # =========================================================
    def _normalize_colname(col):
        return (
            str(col)
            .strip()
            .lower()
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("-", "_")
            .replace("/", "_")
            .replace(" ", "_")
        )

    df.columns = [_normalize_colname(col) for col in df.columns]

    # Hindari duplicate column setelah normalisasi
    df = df.loc[:, ~df.columns.duplicated()].copy()

    # =========================================================
    # 2. HELPER UNTUK MEMASTIKAN KOLOM ADA
    # =========================================================
    def _ensure_column(target_col, aliases=None, default_value=0, numeric=False):
        target_col = _normalize_colname(target_col)
        aliases = aliases or []
        aliases = [_normalize_colname(alias) for alias in aliases]

        if target_col not in df.columns:
            found_col = None

            for alias in aliases:
                if alias in df.columns:
                    found_col = alias
                    break

            if found_col:
                df[target_col] = df[found_col]
            else:
                df[target_col] = default_value

        if numeric:
            df[target_col] = pd.to_numeric(df[target_col], errors="coerce").fillna(0)
        else:
            df[target_col] = df[target_col].fillna(default_value)

    # =========================================================
    # 3. KOLOM ANGKA WAJIB OVERVIEW
    # =========================================================
    _ensure_column(
        "real_omzet",
        aliases=[
            "real omzet",
            "omzet",
            "realisasi_omzet",
            "realisasi omzet",
            "realomzet",
        ],
        default_value=0,
        numeric=True,
    )

    _ensure_column(
        "pendapatan_rs",
        aliases=[
            "pendapatan rs",
            "revenue_sharing",
            "revenue sharing",
            "rs",
        ],
        default_value=0,
        numeric=True,
    )

    _ensure_column(
        "kontribusi",
        aliases=[
            "total_kontribusi",
            "total kontribusi",
            "nilai_kontribusi",
            "nilai kontribusi",
            "contribution",
            "pendapatan_kontribusi",
            "pendapatan kontribusi",
        ],
        default_value=0,
        numeric=True,
    )

    _ensure_column(
        "pendapatan_sewa",
        aliases=[
            "pendapatan sewa",
            "sewa",
            "revenue_sewa",
            "rental_revenue",
        ],
        default_value=0,
        numeric=True,
    )

    _ensure_column(
        "min_omzet",
        aliases=[
            "minimum_omzet",
            "minimum omzet",
            "min omzet",
        ],
        default_value=0,
        numeric=True,
    )

    _ensure_column(
        "luas_sqm",
        aliases=[
            "luas sqm",
            "sqm",
            "luas",
            "luas_m2",
            "luas m2",
        ],
        default_value=0,
        numeric=True,
    )

    _ensure_column(
        "jumlah_pax",
        aliases=[
            "jumlah pax",
            "pax",
            "traffic",
            "jumlah_traffic",
            "jumlah traffic",
        ],
        default_value=0,
        numeric=True,
    )

    _ensure_column(
        "total_trafik",
        aliases=[
            "total trafik",
            "trafik",
            "traffic",
            "total_traffic",
            "trafik_total",
            "jumlah_trafik",
            "jumlah trafik",
        ],
        default_value=0,
        numeric=True,
    )

    # =========================================================
    # 4. KOLOM KATEGORI WAJIB OVERVIEW
    # =========================================================
    _ensure_column(
        "terminal",
        aliases=["nama_terminal", "nama terminal"],
        default_value="Tidak diketahui",
        numeric=False,
    )

    _ensure_column(
        "tahun",
        aliases=["year"],
        default_value="Tidak diketahui",
        numeric=False,
    )

    _ensure_column(
        "masa_jasa",
        aliases=["masa jasa", "masa", "bulan", "month"],
        default_value="Tidak diketahui",
        numeric=False,
    )

    _ensure_column(
        "perusahaan",
        aliases=["nama_perusahaan", "nama perusahaan", "company"],
        default_value="Tidak diketahui",
        numeric=False,
    )

    _ensure_column(
        "brand",
        aliases=["nama_brand", "nama brand"],
        default_value="Tidak diketahui",
        numeric=False,
    )

    _ensure_column(
        "kode_ruang",
        aliases=["kode ruang", "room_code", "kode_lokasi"],
        default_value="Tidak diketahui",
        numeric=False,
    )

    # Samakan nama bulan menjadi format nama bulan penuh demi konsistensi.
    _parsed_masa = pd.to_datetime(df["masa_jasa"], errors="coerce")
    df["masa_jasa"] = _parsed_masa.dt.strftime("%B").where(
        _parsed_masa.notna(), df["masa_jasa"].astype(str)
    )

    # Hitung metrik per baris yang dibutuhkan oleh bagian halaman lainnya.
    df["rev_sqm"] = df["real_omzet"] / df["luas_sqm"].replace(0, pd.NA)
    df["rev_sqm"] = pd.to_numeric(df["rev_sqm"], errors="coerce").fillna(0)

    # Hitung persentase ACV dengan opsi fallback perhitungan lokal.
    acv_raw = pd.to_numeric(df["acv"], errors="coerce") if "acv" in df.columns else pd.Series(pd.NA, index=df.index)
    acv_raw = acv_raw * 100
    acv_fallback = (df["real_omzet"] / df["min_omzet"].replace(0, pd.NA) * 100).round(2)
    df["acv"] = acv_raw.where(acv_raw.notna() & (acv_raw != 0), acv_fallback)
    df["acv"] = pd.to_numeric(df["acv"], errors="coerce").fillna(0)

    return df


def clear_overview_filters():
    """Reset both the applied filters and the pending (draft) widget values."""
    for applied_key, default in _OV_FILTER_DEFAULTS.items():
        st.session_state[applied_key] = default
        st.session_state[f"f_pend_{applied_key[2:]}"] = default


def _apply_overview_filters():
    """Copy the pending (draft) widget values into the applied filter keys."""
    for applied_key in _OV_FILTER_DEFAULTS:
        st.session_state[applied_key] = st.session_state[f"f_pend_{applied_key[2:]}"]


_OV_FILTER_ICONS = {
    "building": '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"></path><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"></path><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"></path><path d="M10 6h4"></path><path d="M10 10h4"></path><path d="M10 14h4"></path><path d="M10 18h4"></path>',
    "grid":     '<rect width="7" height="7" x="3" y="3" rx="1"></rect><rect width="7" height="7" x="14" y="3" rx="1"></rect><rect width="7" height="7" x="14" y="14" rx="1"></rect><rect width="7" height="7" x="3" y="14" rx="1"></rect>',
    "monitor":  '<rect width="20" height="14" x="2" y="3" rx="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line>',
    "calendar": '<path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path>',
    "filter":   '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>',
}


def _ov_filter_icon_svg(icon_key: str, size: int = 14) -> str:
    paths = _OV_FILTER_ICONS.get(icon_key, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
    )


def _render_overview_filter_card(
    active_count, terminal_options, year_options, month_options,
    perusahaan_options, kode_ruang_options,
) -> None:
    """"Filter Data" card matching the Lease Contract page — filters are
    staged in f_pend_* widget keys and only take effect once the user
    clicks "Terapkan Filter" / "Bersihkan Semua" / the header "Reset Filter"."""
    st.markdown('<div class="ov-filtercard-marker"></div>', unsafe_allow_html=True)

    badge = (
        f'<span class="ov-filtercard-badge">{active_count} aktif</span>'
        if active_count > 0 else ""
    )
    head_l, head_r = st.columns([4, 1.2], vertical_alignment="center")
    with head_l:
        st.markdown(
            '<div class="ov-filtercard-head">'
            f'<span class="ov-filtercard-icon">{_ov_filter_icon_svg("filter", 18)}</span>'
            '<div>'
            f'<p class="ov-filtercard-title">Filter Data{badge}</p>'
            '<p class="ov-filtercard-sub">Pilih kriteria untuk memfilter data yang ditampilkan</p>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with head_r:
        st.markdown('<div class="ov-reset-top-marker"></div>', unsafe_allow_html=True)
        st.button(
            "Reset Filter", key="ov_btn_reset_top", use_container_width=True,
            icon=":material/sync:", on_click=clear_overview_filters,
        )

    st.markdown('<div class="ov-filterrow-marker"></div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5, gap="small")
    field_defs = [
        (c1, "building", "Nama Perusahaan", perusahaan_options, "f_pend_perusahaan"),
        (c2, "grid", "Kode Ruangan", kode_ruang_options, "f_pend_kode_ruang"),
        (c3, "monitor", "Terminal", terminal_options, "f_pend_terminal"),
        (c4, "calendar", "Tahun", year_options, "f_pend_tahun"),
        (c5, "calendar", "Bulan", month_options, "f_pend_masa"),
    ]
    for col, icon_key, label, options, widget_key in field_defs:
        with col:
            st.markdown(
                f'<div class="ov-filter-label">{_ov_filter_icon_svg(icon_key, 12)}<span>{label}</span></div>',
                unsafe_allow_html=True,
            )
            st.selectbox(label, options, key=widget_key, label_visibility="collapsed")

    st.markdown('<div class="ov-filtercard-footer-marker"></div>', unsafe_allow_html=True)
    _foot_spacer, foot_r1, foot_r2 = st.columns([3.2, 1.3, 1.3], vertical_alignment="center")
    with foot_r1:
        st.button("✕  Bersihkan Semua", key="ov_btn_reset_bottom", use_container_width=True, on_click=clear_overview_filters)
    with foot_r2:
        st.button(
            "Terapkan Filter", key="ov_btn_apply", use_container_width=True,
            type="primary", icon=":material/filter_alt:", on_click=_apply_overview_filters,
        )


def _get_overview_extra_css():
    return _OVERVIEW_EXTRA_CSS


def page_overview(df_raw):
    for key in ["show_all_rev", "show_all_best", "show_all_detail", "overview_detail_page"]:
        if key not in st.session_state:
            st.session_state[key] = 1 if key == "overview_detail_page" else False

    df_raw = _overview_normalize_and_ensure_columns(df_raw)

    # Gunakan tahun dan bulan yang benar-benar ada di data, bukan daftar statis.
    year_options = ["All Year"] + sorted(
        (int(y) for y in df_raw["tahun"].dropna().unique()), reverse=True
    )
    # Cocokkan bulan hasil normalisasi dengan urutan kalender BULAN.
    masa_jasa_values = set(df_raw["masa_jasa"].dropna().unique().tolist())
    month_options = ["All Month"] + [m for m in BULAN if m in masa_jasa_values]
    perusahaan_options = ["All Perusahaan"] + sorted(df_raw["perusahaan"].dropna().unique().tolist())

    # Filter opsi dropdown Terminal dan Kode Ruang secara dinamis berdasarkan Perusahaan yang dipilih.
    sel_pend_perusahaan = st.session_state.get("f_pend_perusahaan", "All Perusahaan")
    sel_pend_terminal = st.session_state.get("f_pend_terminal", "All Terminal")
    sel_pend_kode_ruang = st.session_state.get("f_pend_kode_ruang", "All Kode Ruang")

    perusahaan_scoped_df = df_raw
    if sel_pend_perusahaan not in (None, "All Perusahaan"):
        perusahaan_scoped_df = perusahaan_scoped_df[perusahaan_scoped_df["perusahaan"] == sel_pend_perusahaan]

    terminal_scope = perusahaan_scoped_df
    if sel_pend_kode_ruang not in (None, "All Kode Ruang"):
        terminal_scope = terminal_scope[terminal_scope["kode_ruang"] == sel_pend_kode_ruang]
    terminal_options = ["All Terminal"] + sorted(terminal_scope["terminal"].dropna().unique().tolist())

    kode_ruang_scope = perusahaan_scoped_df
    if sel_pend_terminal not in (None, "All Terminal"):
        kode_ruang_scope = kode_ruang_scope[kode_ruang_scope["terminal"] == sel_pend_terminal]
    kode_ruang_options = ["All Kode Ruang"] + sorted(kode_ruang_scope["kode_ruang"].dropna().unique().tolist())

    if st.session_state.get("f_terminal") not in terminal_options:
        st.session_state.f_terminal = terminal_options[0]

    if st.session_state.get("f_tahun") not in year_options:
        st.session_state.f_tahun = year_options[0]

    if st.session_state.get("f_masa") not in month_options:
        st.session_state.f_masa = month_options[0]
    if st.session_state.get("f_perusahaan") not in perusahaan_options:
        st.session_state.f_perusahaan = perusahaan_options[0]
    if st.session_state.get("f_kode_ruang") not in kode_ruang_options:
        st.session_state.f_kode_ruang = kode_ruang_options[0]

    for pend_key, applied_key, options in (
        ("f_pend_terminal", "f_terminal", terminal_options),
        ("f_pend_tahun", "f_tahun", year_options),
        ("f_pend_masa", "f_masa", month_options),
        ("f_pend_perusahaan", "f_perusahaan", perusahaan_options),
        ("f_pend_kode_ruang", "f_kode_ruang", kode_ruang_options),
    ):
        if st.session_state.get(pend_key) not in options:
            st.session_state[pend_key] = st.session_state[applied_key]

    active_count = sum([
        st.session_state.get("f_terminal", "All Terminal") != "All Terminal",
        st.session_state.get("f_tahun", "All Year") != "All Year",
        st.session_state.get("f_masa", "All Month") != "All Month",
        st.session_state.get("f_perusahaan", "All Perusahaan") != "All Perusahaan",
        st.session_state.get("f_kode_ruang", "All Kode Ruang") != "All Kode Ruang",
    ])

    st.markdown('<div class="overview-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown(_get_overview_extra_css(), unsafe_allow_html=True)
    _mount_overview_fixed_header()

    with st.container():
        st.markdown('<div class="ov-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_overview_page_header_html(), unsafe_allow_html=True)
        st.markdown('<div class="ov-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="ov-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        _render_overview_filter_card(
            active_count, terminal_options, year_options, month_options,
            perusahaan_options, kode_ruang_options,
        )

    sel_terminal = st.session_state.f_terminal
    sel_tahun = st.session_state.f_tahun
    sel_masa = st.session_state.f_masa
    sel_perusahaan = st.session_state.f_perusahaan
    sel_kode_ruang = st.session_state.f_kode_ruang

    df = df_raw.copy()
    if sel_terminal   != "All Terminal":   df = df[df["terminal"]    == sel_terminal]
    if sel_tahun      != "All Year":       df = df[df["tahun"]       == int(sel_tahun)]
    if sel_masa       != "All Month":      df = df[df["masa_jasa"]   == sel_masa]
    if sel_perusahaan != "All Perusahaan": df = df[df["perusahaan"]  == sel_perusahaan]
    if sel_kode_ruang != "All Kode Ruang": df = df[df["kode_ruang"]  == sel_kode_ruang]

    # Bandingkan dengan bulan/terminal yang sama pada tahun sebelumnya.
    current_year = int(sel_tahun) if sel_tahun != "All Year" else (int(df["tahun"].max()) if not df.empty else None)
    prior_df = df_raw.iloc[0:0]
    if current_year is not None:
        prior_df = df_raw[df_raw["tahun"] == current_year - 1]
        if sel_terminal   != "All Terminal":   prior_df = prior_df[prior_df["terminal"]   == sel_terminal]
        if sel_masa       != "All Month":      prior_df = prior_df[prior_df["masa_jasa"]  == sel_masa]
        if sel_perusahaan != "All Perusahaan": prior_df = prior_df[prior_df["perusahaan"] == sel_perusahaan]
        if sel_kode_ruang != "All Kode Ruang": prior_df = prior_df[prior_df["kode_ruang"] == sel_kode_ruang]

    # =========================================================
    # 11. SAFETY FINAL SEBELUM CHART / GROUPBY
    # =========================================================
    for col in ["real_omzet", "pendapatan_rs", "kontribusi", "pendapatan_sewa", "min_omzet", "luas_sqm", "total_trafik"]:
        if col not in df.columns:
            df[col] = 0
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    for col in ["terminal", "tahun", "masa_jasa", "perusahaan", "brand", "kode_ruang"]:
        if col not in df.columns:
            df[col] = "Tidak diketahui"
        df[col] = df[col].fillna("Tidak diketahui").astype(str)

    def _safe_sum(col):  return df[col].sum() if col in df.columns else 0
    def _safe_mean(col): return df[col].mean() if col in df.columns and not df.empty else 0

    def _rev_per_sqm_sum(frame):
        # Jumlahkan hasil pembagian Rev/Sqm per baris agar cocok dengan logika di Excel.
        if frame.empty or "kontribusi" not in frame.columns or "luas_sqm" not in frame.columns:
            return 0
        sqm = frame["luas_sqm"].replace(0, pd.NA)
        return (frame["kontribusi"] / sqm).fillna(0).sum()

    def _spending_per_pax_sum(frame):
        # Jumlahkan hasil pembagian Spending/Pax per baris agar cocok dengan logika di Excel.
        if frame.empty or "kontribusi" not in frame.columns or "total_trafik" not in frame.columns:
            return 0
        kontribusi = pd.to_numeric(frame["kontribusi"], errors="coerce").fillna(0)
        pax = pd.to_numeric(frame["total_trafik"], errors="coerce").replace(0, pd.NA)
        return (kontribusi / pax).fillna(0).sum()

    real_revenue       = _safe_sum("real_omzet")
    revenue_sharing    = _safe_sum("pendapatan_rs")
    rental_revenue     = _safe_sum("pendapatan_sewa")
    total_contribution = _safe_sum("kontribusi")
    total_pax          = _safe_sum("total_trafik")
    avg_acv            = _safe_mean("acv")
    rev_per_sqm        = _rev_per_sqm_sum(df)
    spending_per_pax   = _spending_per_pax_sum(df)

    def _psum(col):  return prior_df[col].sum()  if col in prior_df.columns else 0
    def _pmean(col): return prior_df[col].mean() if col in prior_df.columns and not prior_df.empty else 0

    prior_revenue_sharing  = _psum("pendapatan_rs")
    prior_rental_revenue   = _psum("pendapatan_sewa")
    prior_contribution     = _psum("kontribusi")
    prior_pax              = _psum("total_trafik")
    prior_avg_acv          = _pmean("acv")
    prior_rev_per_sqm      = _rev_per_sqm_sum(prior_df)
    prior_spending_per_pax = _spending_per_pax_sum(prior_df)

    omzet_val, omzet_scale = _compact_number(real_revenue)
    rs_val, rs_scale = _compact_number(revenue_sharing)
    rental_val, rental_scale = _compact_number(rental_revenue)
    contrib_val, contrib_scale = _compact_number(total_contribution)
    spend_val, spend_scale = _compact_number(spending_per_pax, decimals=0)
    revsqm_val, revsqm_scale = _compact_number(rev_per_sqm, decimals=2)
    # Tampilkan koma hanya jika nilai persentase ACV bukan angka bulat.
    acv_decimals = 0 if float(round(avg_acv, 1)).is_integer() else 1
    acv_val, acv_scale = _compact_number(avg_acv, decimals=acv_decimals)
    traffic_val, traffic_scale = _compact_number(total_pax)

    contribution_delta = _pct_change(total_contribution, prior_contribution)
    spending_delta = _pct_change(spending_per_pax, prior_spending_per_pax)
    revenue_sharing_delta = _pct_change(revenue_sharing, prior_revenue_sharing)
    traffic_subtitle = f"Tahun {current_year}" if sel_tahun != "All Year" else "Seluruh periode"

    kpi_cards = [
        _kpi_pro_card("Real Omzet", omzet_val, f"Rp {omzet_scale}".strip(),
                       "Total realisasi omzet",
                       None, "#4F46E5", "omzet", "vs target",
                       tooltip_val=_fmt_rp_full(real_revenue)),
        _kpi_pro_card("Revenue Sharing", rs_val, f"Rp {rs_scale}".strip(),
                       "Total bagi hasil pendapatan",
                       revenue_sharing_delta, "#0891B2", "layers", "YoY growth",
                       tooltip_val=_fmt_rp_full(revenue_sharing)),
        _kpi_pro_card("Rental Revenue", rental_val, f"Rp {rental_scale}".strip(),
                       "Total pendapatan sewa",
                       _pct_change(rental_revenue, prior_rental_revenue), "#2563EB", "file", "vs prior yr",
                       tooltip_val=_fmt_rp_full(rental_revenue)),
        _kpi_pro_card("Total Contribution", contrib_val, f"Rp {contrib_scale}".strip(),
                       "Total kontribusi tenant",
                       contribution_delta, "#059669", "bars", "vs prior yr",
                       tooltip_val=_fmt_rp_full(total_contribution)),
        _kpi_pro_card("Spending per Pax", spend_val, f"Rp {spend_scale}".strip(),
                       "Kontribusi per pengunjung",
                       spending_delta, "#D97706", "users", "vs prior yr",
                       tooltip_val=_fmt_rp_full(spending_per_pax)),
        _kpi_pro_card("Rev / SQM", revsqm_val, f"Rp {revsqm_scale}/m2".strip(),
                       "Revenue per square meter",
                       _pct_change(rev_per_sqm, prior_rev_per_sqm), "#E11D48", "expand", "YoY",
                       tooltip_val=f"{_fmt_rp_full(rev_per_sqm)}/m2"),
        _kpi_pro_card("ACV", acv_val, f"{acv_scale}%".strip(),
                       "Rata-rata ACV tenant",
                       _pct_change(avg_acv, prior_avg_acv), "#7C3AED", "award", "vs prior yr",
                       tooltip_val=f"{avg_acv:.2f}%".replace(".", ",")),
        _kpi_pro_card("Total Traffic", traffic_val, f"{traffic_scale} pax".strip(),
                       traffic_subtitle,
                       _pct_change(total_pax, prior_pax), "#2563EB", "plane", "YoY growth",
                       tooltip_val=f"{total_pax:,.0f}".replace(",", ".") + " pax"),
    ]

    kpi_row1 = st.columns(4)
    for col, card_html in zip(kpi_row1, kpi_cards[:4]):
        with col:
            st.markdown(card_html, unsafe_allow_html=True)

    kpi_row2 = st.columns(4)
    for col, card_html in zip(kpi_row2, kpi_cards[4:]):
        with col:
            st.markdown(card_html, unsafe_allow_html=True)

    st.markdown('<div class="ov-vertical-spacer"></div>', unsafe_allow_html=True)

    main_left, main_right = st.columns([65, 35], gap="small")
    with main_left:
        st.markdown('<div class="ed-card-marker overview-trend-card"></div>', unsafe_allow_html=True)

        trend = (
            df.groupby("masa_jasa")
            .agg(
                real_revenue=("real_omzet", "sum"),
                revenue_sharing=("pendapatan_rs", "sum"),
                contribution=("kontribusi", "sum"),
            )
            .reindex(BULAN, fill_value=0)
            .reset_index()
            .rename(columns={"index": "masa_jasa"})
        )
        trend["month"] = trend["masa_jasa"].astype(str).str[:3]

        # Tentukan skala grafik tren secara dinamis sesuai dengan volume data.
        max_val = float(trend[["real_revenue", "revenue_sharing", "contribution"]].to_numpy().max() or 0)
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

        st.markdown(
            f'<p class="ed-section-title">Revenue Trend</p>'
            f'<p class="ed-section-sub">Monthly revenue, sharing, and contribution in {unit_label}</p>',
            unsafe_allow_html=True,
        )

        line_specs = [
            ("real_revenue", "Real Revenue", "#2563EB"),
            ("revenue_sharing", "Revenue Sharing", "#7C3AED"),
            ("contribution", "Contribution", "#059669"),
        ]
        fig = go.Figure()
        for col, name, color in line_specs:
            fig.add_trace(go.Scatter(
                x=trend["month"], y=trend[col] / divisor,
                mode="lines+markers", name=name,
                line=dict(color=color, width=2.5), marker=dict(size=6),
                text=[_fmt_rp_full(v) for v in trend[col]],
                hovertemplate="%{x}<br>" + name + ": %{text}<extra></extra>",
            ))
        fig.update_layout(
            autosize=True,
            height=388,
            margin=dict(t=20, b=8, l=8, r=8),
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            hovermode="x unified",
            font=dict(family=OVERVIEW_FONT_FAMILY, size=11, color="#475569"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(family=OVERVIEW_FONT_FAMILY, size=11, color="#475569"),
            ),
            xaxis=dict(
                showgrid=False,
                tickfont=dict(family=OVERVIEW_FONT_FAMILY, size=11, color="#64748B"),
                fixedrange=True,
            ),
            yaxis=dict(
                title=dict(
                    text=unit_label,
                    font=dict(family=OVERVIEW_FONT_FAMILY, size=11, color="#64748B"),
                ),
                showgrid=True,
                gridcolor="#E2E8F0",
                zeroline=False,
                tickfont=dict(family=OVERVIEW_FONT_FAMILY, size=11, color="#64748B"),
                fixedrange=True,
            ),
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with main_right:
        st.markdown('<div class="ed-card-marker overview-alert-card"></div>', unsafe_allow_html=True)
        st.markdown('<p class="ed-section-title">Alert & Insight</p><p class="ed-section-sub">Highlights requiring analyst attention</p>', unsafe_allow_html=True)

        trend_nonzero = trend[trend["real_revenue"] > 0]
        if len(trend_nonzero) >= 2:
            current_rev = trend_nonzero.iloc[-1]["real_revenue"]
            prev_rev = trend_nonzero.iloc[-2]["real_revenue"]
            rev_change = ((current_rev - prev_rev) / prev_rev * 100) if prev_rev else 0
        else:
            rev_change = 0
        low_acv = int((df["acv"] < 80).sum()) if not df.empty else 0
        terminal_sum = df.groupby("terminal")["kontribusi"].sum()
        top_terminal = terminal_sum.idxmax() if len(terminal_sum) else "Terminal 1"
        top_terminal_share = int((terminal_sum.max() / terminal_sum.sum()) * 100) if terminal_sum.sum() else 0

        bidang_sum = df.groupby("bidang_usaha")["kontribusi"].sum()
        top_bidang = bidang_sum.idxmax() if len(bidang_sum) else "-"
        top_bidang_share = int((bidang_sum.max() / bidang_sum.sum()) * 100) if bidang_sum.sum() else 0

        # Ambil data anomali kontrak untuk peringatan lintas menu.
        try:
            contract_df, _ = _get_contract_source_data(df)
        except Exception:
            contract_df = pd.DataFrame()
        expiring_contracts = int((contract_df["Status"] == "Anomaly").sum()) if not contract_df.empty else 0
        expired_contracts = int((contract_df["Status"] == "Expired").sum()) if not contract_df.empty else 0

        # Ambil rincian revenue sharing untuk periode aktif.
        rs_detail = get_detail_revenue_sharing_data(df)
        total_rs = rs_detail["_pendapatan_rs"].sum() if not rs_detail.empty else 0
        rs_by_bidang = rs_detail.groupby("Service/SBU")["_pendapatan_rs"].sum() if not rs_detail.empty else pd.Series(dtype=float)
        top_rs_bidang = rs_by_bidang.idxmax() if len(rs_by_bidang) else "-"

        rev_icon = "trending-down" if rev_change < 0 else "trending-up"
        rev_color = "#DC2626" if rev_change < 0 else "#059669"

        alerts = [
            _alert_item_html(rev_icon, rev_color, f"Revenue {'turun' if rev_change < 0 else 'naik'} {abs(rev_change):.1f}% dibanding periode lalu".replace(".", ","), f"Realisasi periode aktif: {_fmt_rp_compact(real_revenue)}"),
            _alert_item_html("briefcase", "#7C3AED", f"{top_bidang} menyumbang {top_bidang_share}% kontribusi", "Bidang usaha dengan kontribusi terbesar"),
            _alert_item_html("map-pin", "#2563EB", f"{top_terminal} menyumbang {top_terminal_share}% kontribusi", "Monitor perubahan komposisi terminal"),
            _alert_item_html("alert-triangle", "#EA580C", f"{low_acv} tenant memiliki ACV < 80%", "Perlu perhatian untuk potensi risiko"),
        ]
        if expired_contracts > 0:
            alerts.append(_alert_item_html("file-minus", "#DC2626", f"{expired_contracts} kontrak sudah expired", "Perlu tindakan segera di menu Lease Contract"))
        alerts.append(_alert_item_html("clock", "#EA580C", f"{expiring_contracts} kontrak akan expired dalam 90 hari", "Pantau perpanjangan di menu Lease Contract"))
        alerts.append(_alert_item_html("pie-chart", "#059669", f"Total Revenue Sharing {_fmt_rp_compact(total_rs)}", f"{top_rs_bidang} penyumbang RS terbesar" if top_rs_bidang != "-" else "Belum ada data Revenue Sharing"))

        st.markdown(f'<div class="ed-alert-list">{"".join(alerts)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="ov-vertical-spacer"></div>', unsafe_allow_html=True)

    detail_card = st.container()
    with detail_card:
        _ed_card_marker(detail_card)
        dh1, ds, dex, dpp = st.columns([3.85, 2.85, 0.78, 0.72], vertical_alignment="center")
        with dh1:
            st.markdown(
                '<p class="ed-section-title">Detail Revenue Perusahaan</p>'
                '<p class="ed-section-sub">Data lengkap seluruh perusahaan aktif</p>',
                unsafe_allow_html=True,
            )
        with ds:
            search_query = st.text_input(
                "Search Perusahaan / Brand / Kode Ruang",
                placeholder="Cari perusahaan atau brand atau kode ruang...",
                key="overview_detail_search",
                label_visibility="collapsed",
                on_change=lambda: st.session_state.update({"overview_detail_page": 1}),
            )

        detail_df = df[["perusahaan", "brand", "kode_ruang", "min_omzet", "real_omzet", "kontribusi", "acv"]].copy()
        if search_query:
            q = search_query.lower().strip()
            detail_df = detail_df[
                detail_df["perusahaan"].astype(str).str.lower().str.contains(q, na=False)
                | detail_df["brand"].astype(str).str.lower().str.contains(q, na=False)
                | detail_df["kode_ruang"].astype(str).str.lower().str.contains(q, na=False)
            ]

        export_df = detail_df.copy()
        export_df["Min Omzet"] = export_df["min_omzet"].apply(_fmt_rp_full)
        export_df["Real Omzet"] = export_df["real_omzet"].apply(_fmt_rp_full)
        export_df["total_Kontribusi"] = export_df["kontribusi"].apply(_fmt_rp_full)
        export_df["ACV"] = export_df["acv"].apply(lambda x: f"{x:.1f}%".replace(".", ","))
        export_df = export_df[["perusahaan", "brand", "kode_ruang", "Min Omzet", "Real Omzet", "total_Kontribusi", "ACV"]]
        export_df.columns = ["Perusahaan", "Brand", "Kode Ruang", "Min Omzet", "Real Omzet", "total_Kontribusi", "ACV"]

        with dex:
            st.markdown('<div class="ov-btn-export-marker"></div>', unsafe_allow_html=True)
            st.download_button(
                "Export",
                data=dataframe_to_excel_bytes(export_df, "Detail Revenue Perusahaan"),
                file_name="detail_revenue_perusahaan.xlsx",
                mime=EXCEL_MIME,
                key="overview_detail_export",
                width="stretch",
            )
        with dpp:
            rows_per_page = st.selectbox("Rows per page", [10, 25, 50], key="overview_rows_per_page", label_visibility="collapsed")

        total_rows = len(detail_df)
        total_pages = max(1, int(np.ceil(total_rows / rows_per_page)))
        if st.session_state.overview_detail_page > total_pages:
            st.session_state.overview_detail_page = total_pages
        if st.session_state.overview_detail_page < 1:
            st.session_state.overview_detail_page = 1

        start_idx = (st.session_state.overview_detail_page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        detail_view = detail_df.iloc[start_idx:end_idx].copy()
        detail_view["Min Omzet"] = detail_view["min_omzet"].apply(_fmt_rp_full)
        detail_view["Real Omzet"] = detail_view["real_omzet"].apply(_fmt_rp_full)
        detail_view["total_Kontribusi"] = detail_view["kontribusi"].apply(_fmt_rp_full)
        detail_view["ACV"] = detail_view["acv"].apply(lambda x: f"{x:.1f}%".replace(".", ","))
        detail_view = detail_view[["perusahaan", "brand", "kode_ruang", "Min Omzet", "Real Omzet", "total_Kontribusi", "ACV"]]
        detail_view.columns = ["Perusahaan", "Brand", "Kode Ruang", "Min Omzet", "Real Omzet", "total_Kontribusi", "ACV"]
        detail_col_align = {
            "Min Omzet": "right",
            "Real Omzet": "right",
            "total_Kontribusi": "right",
            "ACV": "right",
        }
        st.markdown(_enterprise_table_inner_html(detail_view, col_align=detail_col_align), unsafe_allow_html=True)

        first_item = 0 if total_rows == 0 else start_idx + 1
        last_item = min(end_idx, total_rows)

        # Gunakan modul paginasi umum yang baru
        st.markdown('<div class="overview-detail-pagination-footer-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        ov_page_input = render_pagination(
            current_page=st.session_state.overview_detail_page,
            total_pages=total_pages,
            first_item=first_item,
            last_item=last_item,
            total_rows=total_rows,
            sync_key="overview_detail_page_sync"
        )
        if ov_page_input and ov_page_input.isdigit():
            new_page = int(ov_page_input)
            if new_page != st.session_state.overview_detail_page:
                st.session_state.overview_detail_page = new_page
                st.rerun()

        # Pasang event listener JavaScript
        patch_pagination()


# ══════════════════════════════════════════════
# ALUR UTAMA (ROUTING)
# ══════════════════════════════════════════════
def init_dashboard_state():
    init_auth_state()
    q_menu = st.query_params.get("menu")
    if q_menu and can_access_menu(q_menu):
        st.session_state.active_menu = q_menu
        del st.query_params["menu"]
        
    defaults = {
        "active_menu": "Overview",
        "sidebar_minimized": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    st.session_state.sidebar_minimized = False

    if not can_access_menu(st.session_state.active_menu):
        st.session_state.active_menu = "Overview"


def render_dashboard_app():
    # Fungsi logout dan keepalive ditangani di bagian awal login/app.py.
    init_dashboard_state()
    inject_dashboard_css()

    session_status = session_time_remaining(st.session_state.get("session_token"))
    if session_status:
        inject_session_watchdog(
            idle_elapsed_seconds=session_status["idle_elapsed_seconds"],
            idle_timeout_seconds=IDLE_TIMEOUT_SECONDS,
            warning_lead_seconds=IDLE_WARNING_LEAD_SECONDS,
        )

    st.markdown(
        f'<div class="ap-sidebar-state {"is-mini" if st.session_state.get("sidebar_minimized", False) else "is-expanded"}"></div>',
        unsafe_allow_html=True,
    )

    df_raw = get_active_dashboard_data()
    show_sidebar()

    menu = st.session_state.active_menu

    # Bersihkan status dialog Import Manager saat berpindah menu.
    prev_menu = st.session_state.get("_prev_active_menu")
    if menu != prev_menu:
        st.session_state["_prev_active_menu"] = menu
        if menu == "Import Manager":
            st.session_state["_im_open_dialog"] = None

    if df_raw is None and menu != "Import Manager":
        show_topnav(menu, show_search=False)
        st.markdown(f"<div style='padding:40px;text-align:center;'>", unsafe_allow_html=True)
        data_error = st.session_state.get("dashboard_data_error")
        if data_error:
            st.error(f"Gagal membaca data PostgreSQL: {data_error}")
        else:
            st.warning("Gagal membaca data dashboard. Silakan periksa koneksi PostgreSQL.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    if menu == "Overview":
        page_overview(df_raw)
    elif menu == "Revenue Sharing":
        page_revenue_sharing(df_raw)
    elif menu == "Lease Contract":
        render_lease_contract(df_raw)
    elif menu == "Traffic Monitor":
        page_traffic_monitor(df_raw)
    elif menu == "Room Database":
        render_room_database(df_raw)
    elif menu == "Import Manager":
        render_import_manager()
    elif menu == "Data Verification":
        render_data_verification(df_raw)
    else:
        page_overview(df_raw)

def main():
    st.set_page_config(
        page_title="Non Aeronautical Dashboard",
        page_icon="A",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_auth_state()

    if os.getenv("DEV_BYPASS_LOGIN", "false").lower() == "true" and not st.session_state.get("is_authenticated"):
        st.session_state.is_authenticated = True
        st.session_state.auth_user = {
            "email": "admin@airport.com",
            "name": "Developer",
            "role": "Admin"
        }
        st.session_state.user_name = "Developer"
        st.session_state.user_email = "admin@airport.com"
        st.session_state.user_role = Role.ADMIN.value
        st.session_state.login_role = Role.ADMIN.value

    if not is_authenticated():
        from login.app import render_current_page as render_login_page

        render_login_page()
        st.stop()

    render_dashboard_app()


if __name__ == "__main__":
    main()
