import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from textwrap import dedent

from .navigation import topnav_actions_html

LC_PAGE_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'width="18" height="18" fill="none" stroke="currentColor" '
    'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true">'
    '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>'
    '<polyline points="14 2 14 8 20 8"></polyline>'
    '<line x1="16" y1="13" x2="8" y2="13"></line>'
    '<line x1="16" y1="17" x2="8" y2="17"></line>'
    '<polyline points="10 9 9 9 8 9"></polyline>'
    '</svg>'
)


def _lc_page_header_html():
    return dedent(f"""
    <div class="ov-page-header">
        <div class="ov-page-header-left">
            <div class="ov-page-icon" aria-hidden="true">{LC_PAGE_ICON_SVG}</div>
            <div class="ov-page-header-copy">
                <div class="ov-page-title-row">
                    <h2 class="ov-page-title">Lease Contract</h2>
                </div>
                <p class="ov-page-sub">Monitor tenant contract status and contract lifecycle.</p>
            </div>
        </div>
        {topnav_actions_html()}
    </div>
    """).strip()


def _mount_lc_fixed_header():
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

# ──────────────────────────────────────────────────────────────────────────────
# DATA FROM EXCEL
# ──────────────────────────────────────────────────────────────────────────────
from .connection import get_engine
from sqlalchemy import text

LC_CONTRACT_COLUMNS = [
    "No",
    "Name/Tenant",
    "Sub",
    "Valid Period",
    "Unit Name/Loc",
    "Status",
    "Conflict Info",
    "Kode",
    "Skema",
    "Sisa",
    "Terminal",
]



def _empty_contract_data() -> pd.DataFrame:
    return pd.DataFrame(columns=LC_CONTRACT_COLUMNS)


def _first_present(row: pd.Series, columns: list[str], default="-"):
    for col in columns:
        if col in row.index:
            value = row.get(col)
            if pd.notna(value) and str(value).strip() not in {"", "nan", "NaT", "None"}:
                return value
    return default


def _format_contract_date(value) -> str | None:
    if pd.isna(value) or str(value).strip() in {"", "nan", "NaT", "None"}:
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return str(value)
    return parsed.strftime("%d %b %Y")


def _contract_status(end_value) -> tuple[str, int]:
    parsed = pd.to_datetime(end_value, errors="coerce")
    if pd.isna(parsed):
        return "Valid", 365

    remaining = int((parsed.date() - date.today()).days)
    if remaining < 0:
        return "Expired", remaining
    if remaining <= 90:
        return "Anomaly", remaining
    return "Valid", remaining


def _normalize_contract_data(df: pd.DataFrame | None) -> pd.DataFrame:
    if df is None or df.empty:
        return _empty_contract_data()

    data = []
    for no, (_, row) in enumerate(df.iterrows(), start=1):
        tenant = _first_present(row, ["perusahaan", "tenant", "Name/Tenant", "brand"], "-")
        brand = _first_present(row, ["brand"], "-")
        terminal = _first_present(row, ["terminal", "Terminal"], "-")
        kode = _first_present(row, ["kode_ruang", "Kode", "unit", "Unit Name/Loc"], "-")
        lokasi = _first_present(row, ["lokasi", "area", "Unit Name/Loc"], kode)
        start_value = _first_present(row, ["start_kontrak", "start_contract", "Start"], None)
        end_value = _first_present(row, ["end_kontrak", "end_contract", "End"], None)
        start_label = _format_contract_date(start_value)
        end_label = _format_contract_date(end_value)
        valid_period = f"{start_label or 'N/A'} - {end_label or 'N/A'}"
        status, remaining = _contract_status(end_value)
        skema = _first_present(
            row,
            ["kerja_sama", "jenis_kontrak", "csp_non_csp", "bidang_usaha", "Skema"],
            "-",
        )
        contract_no = _first_present(row, ["nomor_kontrak_legal", "nomor_kontrak_sistem"], "")
        sub = str(contract_no).strip() or (str(brand).strip() if str(brand).strip() != "-" else "General Contract")

        data.append({
            "No": no,
            "Name/Tenant": tenant,
            "Sub": sub,
            "Valid Period": valid_period,
            "Unit Name/Loc": lokasi,
            "Status": status,
            "Conflict Info": status != "Valid",
            "Kode": kode,
            "Skema": skema,
            "Sisa": remaining,
            "Terminal": terminal,
        })

    return pd.DataFrame(data, columns=LC_CONTRACT_COLUMNS)


@st.cache_data(ttl=60, show_spinner=False)
def _load_contract_data_from_database() -> pd.DataFrame:
    query = text("""
        SELECT
            import_id,
            nomor_kontrak_sistem,
            nomor_kontrak_legal,
            perusahaan,
            brand,
            kode_ruang,
            terminal,
            lokasi,
            start_kontrak,
            end_kontrak,
            csp_non_csp,
            kerja_sama,
            pemilihan_mitra_usaha,
            rs_percent,
            min_omzet,
            mgrs_per_pax
        FROM vw_lease_contract
        WHERE EXISTS (
            SELECT 1
            FROM import_history ih
            WHERE ih.import_id = vw_lease_contract.import_id
              AND COALESCE(ih.is_active, true) = true
        )
        ORDER BY end_kontrak NULLS LAST, perusahaan, kode_ruang
    """)
    with get_engine().connect() as conn:
        return pd.read_sql(query, conn)


def _get_contract_data(df: pd.DataFrame | None = None) -> pd.DataFrame:
    return _normalize_contract_data(df)


def _get_contract_source_data(df_raw: pd.DataFrame | None = None) -> tuple[pd.DataFrame, str]:
    try:
        db_df = _load_contract_data_from_database()
        if db_df is not None and not db_df.empty:
            st.session_state.pop("lc_data_error", None)
            return _normalize_contract_data(db_df), "database"
    except Exception as exc:
        st.session_state["lc_data_error"] = str(exc)

    fallback_df = _get_contract_data(df_raw)
    return fallback_df, "dashboard" if not fallback_df.empty else "empty"


def _get_contract_types(df):
    if df is None or df.empty:
        return {"Revenue Sharing": 0, "Rental": 0, "MGRS": 0}

    # df di sini adalah lc_df (level kontrak: No/Name/Tenant/.../Skema/...),
    # bukan transaction_revenue mentah — jadi field skemanya ada di kolom
    # "Skema", bukan "bidang_usaha".
    if "Skema" in df.columns:
        counts = df[df["Skema"] != "-"]["Skema"].value_counts().to_dict()
        return counts if counts else {}
    return {}


# ──────────────────────────────────────────────────────────────────────────────
# CSS STYLE DEFINITIONS
# ──────────────────────────────────────────────────────────────────────────────
from .lease_contract_styles import _PAGE_CSS, _LC_EXTRA_CSS

# ──────────────────────────────────────────────────────────────────────────────
# INIT STATE
# ──────────────────────────────────────────────────────────────────────────────
def _init_state(contract_df=None, data_source="unknown"):
    if contract_df is None:
        contract_df = _empty_contract_data()
    source_key = f"{data_source}:{len(contract_df)}:{tuple(contract_df.columns)}"
    if "lc_df" not in st.session_state or st.session_state.get("lc_data_source_key") != source_key:
        st.session_state.lc_df = contract_df
        st.session_state.lc_data_source_key = source_key
    if "lc_page"        not in st.session_state: st.session_state.lc_page        = 0
    if "lc_show_form"   not in st.session_state: st.session_state.lc_show_form   = False
    if "lc_selected"    not in st.session_state: st.session_state.lc_selected    = set()
    if "lc_alert_toast" not in st.session_state: st.session_state.lc_alert_toast = False

    # Filter states initialization — "applied" values, used to actually
    # filter the data. The filter card's widgets write to separate
    # "lc_pend_*" keys and only copy into these on "Terapkan Filter".
    if "f_terminal"     not in st.session_state: st.session_state.f_terminal     = "All Terminal"
    if "f_tahun"        not in st.session_state: st.session_state.f_tahun        = "All Year"
    if "f_masa"         not in st.session_state: st.session_state.f_masa         = "All Month"
    if "f_perusahaan"   not in st.session_state: st.session_state.f_perusahaan   = "All Perusahaan"
    if "f_kode_ruang"   not in st.session_state: st.session_state.f_kode_ruang   = "All Kode Ruang"
    if "lc_filtered_df" not in st.session_state: st.session_state.lc_filtered_df = st.session_state.lc_df

    _LC_PENDING_DEFAULTS = {
        "lc_pend_terminal": "f_terminal", "lc_pend_tahun": "f_tahun", "lc_pend_masa": "f_masa",
        "lc_pend_perusahaan": "f_perusahaan", "lc_pend_kode_ruang": "f_kode_ruang",
    }
    for pend_key, applied_key in _LC_PENDING_DEFAULTS.items():
        if pend_key not in st.session_state:
            st.session_state[pend_key] = st.session_state[applied_key]

    # "Show more" toggles for the Contracts Expiring Soon cards
    for _key in ("lc_show_all_critical", "lc_show_all_expiring", "lc_show_all_approaching"):
        if _key not in st.session_state:
            st.session_state[_key] = False

# ──────────────────────────────────────────────────────────────────────────────
# SPARKLINE & CHART GENERATION
# ──────────────────────────────────────────────────────────────────────────────
def _generate_svg_sparkline(values, color, fill_color_grad_start, fill_color_grad_stop):
    if not values:
        return ""
    min_val = min(values)
    max_val = max(values)
    val_range = max_val - min_val if max_val != min_val else 1
    
    width = 100
    height = 30
    padding = 2
    
    points = []
    for i, val in enumerate(values):
        x = padding + (i / (len(values) - 1)) * (width - 2 * padding)
        y = (height - padding) - ((val - min_val) / val_range) * (height - 2 * padding)
        points.append((x, y))
    
    path_data = "M " + " L ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    fill_data = f"{path_data} L {points[-1][0]:.1f},{height} L {points[0][0]:.1f},{height} Z"
    
    import random
    grad_id = f"grad_{color.replace('#', '')}_{int(random.random()*100000)}"
    
    svg = f"""
    <svg class="sparkline-svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg" style="display: block;">
        <defs>
            <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="{fill_color_grad_start}" stop-opacity="0.3" />
                <stop offset="100%" stop-color="{fill_color_grad_stop}" stop-opacity="0.0" />
            </linearGradient>
        </defs>
        <path d="{fill_data}" fill="url(#{grad_id})" />
        <path d="{path_data}" fill="none" stroke="{color}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
    """
    return svg.replace("\n", "").replace("  ", "")

def _render_kpi_card_html(icon_svg, icon_class, badge_text, badge_class, title, value, unit, subtitle, progress_items, progress_color, comparison, sparkline_svg):
    # Swap dots and commas for Indonesian formatting
    badge_text = str(badge_text).translate(str.maketrans({',': '.', '.': ','}))
    subtitle = str(subtitle).translate(str.maketrans({',': '.', '.': ','}))
    value = str(value).translate(str.maketrans({',': '.', '.': ','}))
    comparison = str(comparison).translate(str.maketrans({',': '.', '.': ','}))

    progress_rows = ""
    if progress_items:
        max_val = max([item[1] for item in progress_items]) if progress_items else 1
        for lbl, val in progress_items:
            pct = int((val / max_val) * 85) if max_val > 0 else 0
            if val > 0 and pct < 5:
                pct = 5
            val_formatted = f"{val:,.0f}".replace(",", ".") if isinstance(val, (int, float)) else str(val)
            progress_rows += f"""
            <div class="kpi-progress-row">
                <span class="kpi-progress-label">{lbl}</span>
                <div class="kpi-progress-track">
                    <div class="kpi-progress-fill" style="width: {pct}%; background-color: {progress_color};"></div>
                </div>
                <span class="kpi-progress-val">{val_formatted}</span>
            </div>
            """
            
    html = f"""
    <div class="kpi-card-new">
        <div class="kpi-card-header">
            <div class="kpi-icon-box {icon_class}">
                {icon_svg}
            </div>
            <div class="kpi-badge {badge_class}">
                {badge_text}
            </div>
        </div>
        <div class="kpi-card-body">
            <div class="kpi-card-title">{title}</div>
            <div class="kpi-card-value-row">
                <span class="kpi-card-value">{value}</span>
                <span class="kpi-card-unit">{unit}</span>
            </div>
            <div class="kpi-card-subtitle">{subtitle}</div>
            <div class="kpi-progress-list">
                {progress_rows}
            </div>
        </div>
        <div class="kpi-card-footer">
            <span class="kpi-comparison-text">{comparison}</span>
            <div class="kpi-sparkline-wrap">
                {sparkline_svg}
            </div>
        </div>
    </div>
    """
    return html.replace("\n", "").replace("  ", "")

LC_TIMELINE_ICON_PATHS = {
    "file-text":     '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path>',
    "check-circle":  '<path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path>',
    "clock":         '<circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline>',
    "alert-circle":  '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>',
}


def _lc_timeline_icon_svg(icon_key: str) -> str:
    paths = LC_TIMELINE_ICON_PATHS.get(icon_key, "")
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
    )


def _build_timeline_chart(df):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    year_suffix = str(date.today().year)[-2:]
    months_labels = [f"{m} {year_suffix}" for m in months]

    # Calculate expiring count per month from the filtered dataframe
    expiring_counts = {m: 0 for m in months}
    for _, r in df[df["Status"] == "Anomaly"].iterrows():
        try:
            end_part = r["Valid Period"].split(" - ")[1]
            m = end_part.split(" ")[1][:3]
            if m in expiring_counts:
                expiring_counts[m] += 1
        except Exception:
            m_idx = (r["Sisa"] // 30) % 12
            expiring_counts[months[m_idx]] += 1

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months_labels,
        y=[expiring_counts[m] for m in months],
        name="Expiring",
        marker_color="#6366F1",
        width=0.25
    ))
    fig.update_layout(
        barmode="group",
        bargap=0.35,
        bargroupgap=0.08,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=210,
        xaxis=dict(
            showgrid=False,
            tickfont=dict(family="Inter", size=9, color="#94A3B8"),
            linecolor="#E2E8F0"
        ),
        yaxis=dict(
            gridcolor="#F1F5F9",
            tickfont=dict(family="Inter", size=9, color="#94A3B8"),
            zeroline=False
        )
    )
    return fig

def _build_donut_chart(data_dict, colors, size=145):
    labels = list(data_dict.keys())
    values = list(data_dict.values())
    pct_font = max(10, round(size * 0.052))
    total_font = max(14, round(size * 0.1))
    sub_font = max(9, round(size * 0.05))
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors),
        textinfo="percent",
        textfont_size=pct_font,
        textfont_color="#FFFFFF",
        textposition="inside",
        showlegend=False,
        hoverinfo="label+value+percent"
    )])
    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=size,
        annotations=[dict(text=f"{sum(values)}<br><span style='font-size:{sub_font}px;color:#94A3B8;font-weight:bold;'>TOTAL</span>", x=0.5, y=0.5, font_size=total_font, font_weight="bold", font_family="Inter", showarrow=False)]
    )
    return fig

# Sparkline dummy datasets
SPARK_TOTAL = [0] * 12
SPARK_ACTIVE = [0] * 12
SPARK_EXPIRING = [0] * 12
SPARK_EXPIRED = [0] * 12

# ──────────────────────────────────────────────────────────────────────────────
# ADD CONTRACT FORM (PRESERVES EXISTING DESIGN SYSTEM & FUNCTIONALITY)
# ──────────────────────────────────────────────────────────────────────────────
def _render_add_form():
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.markdown('<div class="card-title">➕ Tambah Kontrak Baru</div>', unsafe_allow_html=True)
    st.markdown('<div class="card-subtitle">Isi detail kontrak kerjasama sewa ruangan baru.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        name   = st.text_input("Name/Tenant",    placeholder="e.g. NAST Merch",     key="lc_f_name")
        sub    = st.text_input("Sub / Tengat ID", placeholder="e.g. august on ...",  key="lc_f_sub")
        unit   = st.text_input("Unit Name/Loc",   placeholder="e.g. T1 - Area A",    key="lc_f_unit")
    with c2:
        mulai    = st.date_input("Tanggal Mulai",    key="lc_f_mulai")
        berakhir = st.date_input("Tanggal Berakhir", key="lc_f_berakhir")
        skema    = st.selectbox("Skema", ["Revenue Sharing", "RS+MO", "MGRS"], key="lc_f_skema")
    with c3:
        status_opt = st.selectbox("Status", ["Valid", "Anomaly", "Expired"], key="lc_f_status")
        has_conflict = st.checkbox("Ada Conflict Info", key="lc_f_conflict")
        kode = st.text_input("Kode Ruang", placeholder="e.g. FB-01-01", key="lc_f_kode")

    b1, b2, _ = st.columns([1.2, 1, 5])
    with b1:
        st.markdown('<div class="btn-primary">', unsafe_allow_html=True)
        if st.button("✅ Simpan", key="lc_save", use_container_width=True):
            if not name or not unit:
                st.error("Mohon isi Name/Tenant dan Unit Name/Loc.")
            else:
                period_str = f"{mulai.strftime('%d %b %Y')} - {berakhir.strftime('%d %b %Y')}"
                sisa = (berakhir - date.today()).days
                new_no = int(st.session_state.lc_df["No"].max()) + 1
                
                # Determine terminal from unit name
                terminal = "T1"
                for t in ["T1", "T2", "T3", "T3U"]:
                    if t in unit.upper():
                        terminal = t
                        break
                        
                new_row = {
                    "No": new_no, "Name/Tenant": name, "Sub": sub,
                    "Valid Period": period_str, "Unit Name/Loc": unit,
                    "Status": status_opt, "Conflict Info": has_conflict,
                    "Kode": kode, "Skema": skema, "Sisa": sisa,
                    "Terminal": terminal
                }
                st.session_state.lc_df = pd.concat(
                    [pd.DataFrame([new_row]), st.session_state.lc_df], ignore_index=True)
                st.session_state.lc_show_form = False
                st.session_state.lc_page = 0
                st.toast("✅ Kontrak baru berhasil disimpan!")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with b2:
        st.markdown('<div class="btn-secondary">', unsafe_allow_html=True)
        if st.button("✖ Batal", key="lc_cancel", use_container_width=True):
            st.session_state.lc_show_form = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────────────────────
# MAIN RENDER FUNCTION
# ──────────────────────────────────────────────────────────────────────────────
_LC_FILTER_DEFAULTS = {
    "f_terminal": "All Terminal", "f_tahun": "All Year", "f_masa": "All Month",
    "f_perusahaan": "All Perusahaan", "f_kode_ruang": "All Kode Ruang",
}


def clear_lc_filters():
    """Reset both the applied filters and the pending (draft) widget values."""
    for applied_key, default in _LC_FILTER_DEFAULTS.items():
        st.session_state[applied_key] = default
        st.session_state[f"lc_pend_{applied_key[2:]}"] = default
    st.session_state.lc_filtered_df = st.session_state.lc_df


def _apply_lc_filters():
    """Copy the pending (draft) widget values into the applied filter keys."""
    for applied_key in _LC_FILTER_DEFAULTS:
        st.session_state[applied_key] = st.session_state[f"lc_pend_{applied_key[2:]}"]


_LC_FILTER_ICONS = {
    "building": '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"></path><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"></path><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"></path><path d="M10 6h4"></path><path d="M10 10h4"></path><path d="M10 14h4"></path><path d="M10 18h4"></path>',
    "grid":     '<rect width="7" height="7" x="3" y="3" rx="1"></rect><rect width="7" height="7" x="14" y="3" rx="1"></rect><rect width="7" height="7" x="14" y="14" rx="1"></rect><rect width="7" height="7" x="3" y="14" rx="1"></rect>',
    "monitor":  '<rect width="20" height="14" x="2" y="3" rx="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line>',
    "calendar": '<path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path>',
    "filter":   '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>',
    "refresh":  '<path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path><path d="M21 3v5h-5"></path><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path><path d="M8 16H3v5"></path>',
}


def _lc_filter_icon_svg(icon_key: str, size: int = 14) -> str:
    paths = _LC_FILTER_ICONS.get(icon_key, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
    )


def _render_lc_filter_card(df_full: pd.DataFrame, active_count: int = 0) -> None:
    """The redesigned "Filter Data" card — filters are staged in lc_pend_*
    widget keys and only take effect (filter the data) once the user
    clicks "Terapkan Filter" / "Bersihkan Semua" / the header "Reset Filter"."""
    perusahaan_options = ["All Perusahaan"] + sorted(df_full["Name/Tenant"].dropna().unique().tolist())
    kode_options = ["All Kode Ruang"] + sorted(df_full["Kode"].dropna().unique().tolist())
    terminal_options = ["All Terminal"] + sorted(
        v for v in df_full["Terminal"].dropna().unique().tolist() if v not in ("-", "Unknown", "")
    )

    # Tahun & Bulan diambil dari tanggal akhir kontrak ("Valid Period",
    # format "dd Mon yyyy" hasil _format_contract_date) yang benar-benar
    # ada di data — bukan daftar statis.
    def _end_date_parts(valid_period):
        if " - " not in str(valid_period):
            return None, None
        end_part = str(valid_period).split(" - ")[1].strip()
        parts = end_part.split(" ")
        if len(parts) == 3 and parts[2].isdigit():
            return parts[1], parts[2]  # (bulan singkat "Jun", tahun "2026")
        return None, None

    end_parts = df_full["Valid Period"].apply(_end_date_parts)
    years_present = sorted({y for _, y in end_parts if y}, reverse=True)
    tahun_options = ["All Year"] + years_present

    _MONTH_ABBR_ORDER = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                         "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    _MONTH_FULL_NAME = {
        "Jan": "January", "Feb": "February", "Mar": "March", "Apr": "April",
        "May": "May", "Jun": "June", "Jul": "July", "Aug": "August",
        "Sep": "September", "Oct": "October", "Nov": "November", "Dec": "December",
    }
    months_present = {m for m, _ in end_parts if m}
    bulan_options = ["All Month"] + [
        _MONTH_FULL_NAME[m] for m in _MONTH_ABBR_ORDER if m in months_present
    ]

    # Opsi dropdown berubah mengikuti data (bukan daftar tetap), jadi nilai
    # yang sudah dipilih sebelumnya bisa jadi tidak valid lagi setelah data
    # berubah — reset ke default supaya tidak error/nyangkut.
    for applied_key, pend_key, options in (
        ("f_terminal", "lc_pend_terminal", terminal_options),
        ("f_tahun", "lc_pend_tahun", tahun_options),
        ("f_masa", "lc_pend_masa", bulan_options),
    ):
        if st.session_state.get(applied_key) not in options:
            st.session_state[applied_key] = options[0]
        if st.session_state.get(pend_key) not in options:
            st.session_state[pend_key] = st.session_state[applied_key]

    st.markdown('<div class="lc-filtercard-marker"></div>', unsafe_allow_html=True)

    badge = (
        f'<span class="lc-filtercard-badge">{active_count} aktif</span>'
        if active_count > 0 else ""
    )
    head_l, head_r = st.columns([4, 1.2], vertical_alignment="center")
    with head_l:
        st.markdown(
            '<div class="lc-filtercard-head">'
            f'<span class="lc-filtercard-icon">{_lc_filter_icon_svg("filter", 18)}</span>'
            '<div>'
            f'<p class="lc-filtercard-title">Filter Data{badge}</p>'
            '<p class="lc-filtercard-sub">Pilih kriteria untuk memfilter data yang ditampilkan</p>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with head_r:
        st.markdown('<div class="lc-reset-top-marker"></div>', unsafe_allow_html=True)
        st.button(
            "Reset Filter", key="lc_btn_reset_top", use_container_width=True,
            icon=":material/sync:", on_click=clear_lc_filters,
        )

    st.markdown('<div class="lc-filterrow-marker"></div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5, gap="small")
    field_defs = [
        (c1, "building", "Nama Perusahaan", perusahaan_options, "lc_pend_perusahaan"),
        (c2, "grid", "Kode Ruangan", kode_options, "lc_pend_kode_ruang"),
        (c3, "monitor", "Terminal", terminal_options, "lc_pend_terminal"),
        (c4, "calendar", "Tahun", tahun_options, "lc_pend_tahun"),
        (c5, "calendar", "Bulan", bulan_options, "lc_pend_masa"),
    ]
    for col, icon_key, label, options, widget_key in field_defs:
        with col:
            st.markdown(
                f'<div class="lc-filter-label">{_lc_filter_icon_svg(icon_key, 12)}<span>{label}</span></div>',
                unsafe_allow_html=True,
            )
            st.selectbox(label, options, key=widget_key, label_visibility="collapsed")

    st.markdown('<div class="lc-filtercard-footer-marker"></div>', unsafe_allow_html=True)
    _foot_spacer, foot_r1, foot_r2 = st.columns([3.2, 1.3, 1.3], vertical_alignment="center")
    with foot_r1:
        st.button("✕  Bersihkan Semua", key="lc_btn_reset_bottom", use_container_width=True, on_click=clear_lc_filters)
    with foot_r2:
        st.button(
            "Terapkan Filter", key="lc_btn_apply", use_container_width=True,
            type="primary", icon=":material/filter_alt:", on_click=_apply_lc_filters,
        )


def _get_lc_extra_css():
    return _LC_EXTRA_CSS


def render_lease_contract(df_raw=None):
    contract_df, data_source = _get_contract_source_data(df_raw)
    _init_state(contract_df, data_source)

    # Apply global filters dynamically on every rerun (auto-apply)
    df_filt = st.session_state.lc_df.copy()
    
    sel_term = st.session_state.get("f_terminal", "All Terminal")
    if sel_term != "All Terminal" and not df_filt.empty:
        df_filt = df_filt[df_filt["Terminal"] == sel_term]
        
    sel_year = st.session_state.get("f_tahun", "All Year")
    if sel_year != "All Year" and not df_filt.empty:
        df_filt = df_filt[df_filt["Valid Period"].apply(lambda x: x.split(" - ")[1].endswith(str(sel_year)) if " - " in x else False)]
        
    sel_month = st.session_state.get("f_masa", "All Month")
    if sel_month != "All Month" and not df_filt.empty:
        month_map = {
            "January": "Jan", "February": "Feb", "March": "Mar", "April": "Apr",
            "May": "May", "June": "Jun", "July": "Jul", "August": "Aug",
            "September": "Sep", "October": "Oct", "November": "Nov", "December": "Dec"
        }
        month_abbr = month_map.get(sel_month, sel_month[:3])
        df_filt = df_filt[df_filt["Valid Period"].apply(lambda x: x.split(" - ")[1].split(" ")[1] == month_abbr if " - " in x else False)]

    sel_perusahaan = st.session_state.get("f_perusahaan", "All Perusahaan")
    if sel_perusahaan != "All Perusahaan" and not df_filt.empty:
        df_filt = df_filt[df_filt["Name/Tenant"] == sel_perusahaan]

    sel_kode = st.session_state.get("f_kode_ruang", "All Kode Ruang")
    if sel_kode != "All Kode Ruang" and not df_filt.empty:
        df_filt = df_filt[df_filt["Kode"] == sel_kode]

    df_all = df_filt
    st.session_state.lc_filtered_df = df_filt

    active_count = sum([
        st.session_state.get("f_terminal", "All Terminal") != "All Terminal",
        st.session_state.get("f_perusahaan", "All Perusahaan") != "All Perusahaan",
        st.session_state.get("f_kode_ruang", "All Kode Ruang") != "All Kode Ruang",
        st.session_state.get("f_tahun", "All Year") != "All Year",
        st.session_state.get("f_masa", "All Month") != "All Month",
    ])

    st.markdown(_PAGE_CSS + '<div class="overview-page-marker lc-page-marker"></div>', unsafe_allow_html=True)
    st.markdown(_get_lc_extra_css(), unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="ov-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_lc_page_header_html(), unsafe_allow_html=True)
        st.markdown('<div class="ov-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="ov-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        _render_lc_filter_card(st.session_state.lc_df, active_count)

    _mount_lc_fixed_header()
    st.markdown('<div class="filters-marker"></div>', unsafe_allow_html=True)

    if st.session_state.lc_show_form:
        _render_add_form()
        st.markdown('<div class="lc-vertical-spacer"></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="lc-vertical-spacer"></div>', unsafe_allow_html=True)


    # ─────────────────────────────────────────────
    # TOP KPI CARDS
    # ─────────────────────────────────────────────
    total_val = len(df_all)

    # Label Terminal & Skema ikut nilai yang benar-benar ada di data
    # (mis. "Terminal 1"/"Terminal 2"/"Terminal 3"), bukan kode tetap
    # "T1"/"T2"/"T3"/"T3U" atau "Revenue Sharing"/"RS+MO"/"MGRS" yang
    # tidak pernah cocok dengan data riil.
    terminal_labels = sorted(
        v for v in df_all["Terminal"].dropna().unique().tolist() if v not in ("-", "Unknown", "")
    )
    total_progress_items = [(t, len(df_all[df_all["Terminal"] == t])) for t in terminal_labels]

    active_df = df_all[df_all["Status"] == "Valid"]
    active_val = len(active_df)
    skema_labels = sorted(
        v for v in df_all["Skema"].dropna().unique().tolist() if v not in ("-", "Unknown", "")
    )
    active_progress_items = [(s, len(active_df[active_df["Skema"] == s])) for s in skema_labels]

    anomaly_df = df_all[df_all["Status"] == "Anomaly"]
    expiring_val = len(anomaly_df)
    d30_val = len(anomaly_df[anomaly_df["Sisa"] <= 30])
    d60_val = len(anomaly_df[(anomaly_df["Sisa"] > 30) & (anomaly_df["Sisa"] <= 60)])
    d90_val = len(anomaly_df[(anomaly_df["Sisa"] > 60) & (anomaly_df["Sisa"] <= 90)])

    expired_df = df_all[df_all["Status"] == "Expired"]
    expired_val = len(expired_df)
    expired_progress_items = [(t, len(expired_df[expired_df["Terminal"] == t])) for t in terminal_labels]

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        svg_spark_total = _generate_svg_sparkline(SPARK_TOTAL, "#6366F1", "#6366F1", "#6366F1")
        icon_total = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>'
        html_total = _render_kpi_card_html(
            icon_svg=icon_total,
            icon_class="total",
            badge_text="N/A",
            badge_class="positive",
            title="Total Contract",
            value=f"{total_val}",
            unit="contracts",
            subtitle=f"All terminals · FY {date.today().year}",
            progress_items=total_progress_items,
            progress_color="#6366F1",
            comparison="No prior data",
            sparkline_svg=svg_spark_total
        )
        st.markdown(html_total, unsafe_allow_html=True)
        
    with col2:
        svg_spark_active = _generate_svg_sparkline(SPARK_ACTIVE, "#10B981", "#10B981", "#10B981")
        icon_active = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
        html_active = _render_kpi_card_html(
            icon_svg=icon_active,
            icon_class="active",
            badge_text="N/A",
            badge_class="positive",
            title="Active Contract",
            value=f"{active_val}",
            unit="active",
            subtitle=f"{active_val/total_val*100:.1f}% of total portfolio" if total_val > 0 else "0.0% of total portfolio",
            progress_items=active_progress_items,
            progress_color="#10B981",
            comparison="No prior data",
            sparkline_svg=svg_spark_active
        )
        st.markdown(html_active, unsafe_allow_html=True)
        
    with col3:
        svg_spark_expiring = _generate_svg_sparkline(SPARK_EXPIRING, "#F59E0B", "#F59E0B", "#F59E0B")
        icon_expiring = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
        html_expiring = _render_kpi_card_html(
            icon_svg=icon_expiring,
            icon_class="expiring",
            badge_text="N/A",
            badge_class="negative",
            title="Expiring Soon",
            value=f"{expiring_val}",
            unit="contracts",
            subtitle="Within next 90 days",
            progress_items=[("30d", d30_val), ("60d", d60_val), ("90d", d90_val)],
            progress_color="#F59E0B",
            comparison="No prior data",
            sparkline_svg=svg_spark_expiring
        )
        st.markdown(html_expiring, unsafe_allow_html=True)
        
    with col4:
        svg_spark_expired = _generate_svg_sparkline(SPARK_EXPIRED, "#EF4444", "#EF4444", "#EF4444")
        icon_expired = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>'
        html_expired = _render_kpi_card_html(
            icon_svg=icon_expired,
            icon_class="expired",
            badge_text="N/A",
            badge_class="negative",
            title="Expired Contract",
            value=f"{expired_val}",
            unit="contracts",
            subtitle="Requires immediate action",
            progress_items=expired_progress_items,
            progress_color="#EF4444",
            comparison="No prior data",
            sparkline_svg=svg_spark_expired
        )
        st.markdown(html_expired, unsafe_allow_html=True)

    st.markdown('<div class="lc-row1-row2-gap"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # CONTRACT EXPIRY TIMELINE & DONUT CHARTS (3-COLUMN REDESIGN)
    # ─────────────────────────────────────────────
    col_left, col_mid, col_right = st.columns([1.7, 1.0, 1.0])
    
    # ── Column 1: Contract Expiry Timeline ──
    with col_left:
        with st.container():
            st.markdown('<div class="premium-card-marker"></div>', unsafe_allow_html=True)
            st.markdown(
                '<div class="card-title">Contract Expiry Timeline</div>'
                f'<div class="card-subtitle">Monthly contract expirations — Next 12 months (Jan-Dec {date.today().year})</div>',
                unsafe_allow_html=True,
            )
            
            # Dynamic calculations for timeline stats
            months_list = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
            exp_month_counts = {m: 0 for m in months_list}
            for _, r in df_all[df_all["Status"] == "Anomaly"].iterrows():
                try:
                    end_part = r["Valid Period"].split(" - ")[1]
                    m = end_part.split(" ")[1][:3]
                    if m in exp_month_counts:
                        exp_month_counts[m] += 1
                except Exception:
                    m_idx = (r["Sisa"] // 30) % 12
                    exp_month_counts[months_list[m_idx]] += 1
            
            tot_exp_val = sum(exp_month_counts.values())
            risk_months_count = sum(1 for v in exp_month_counts.values() if v >= 8)

            # "Renewed"/"Renewal Rate" dihapus — tidak ada data riwayat
            # perpanjangan kontrak yang bisa dilacak; sebelumnya ini cuma
            # estimasi fiktif 60% dari jumlah expiring.
            html_timeline_kpis = f"""
            <div class="timeline-kpi-row">
                <div class="timeline-kpi-card expiring">
                    <div class="timeline-kpi-top">
                        <div class="timeline-kpi-icon">{_lc_timeline_icon_svg("file-text")}</div>
                        <div class="timeline-kpi-val">{tot_exp_val}</div>
                    </div>
                    <div class="timeline-kpi-lbl">Contracts<span>Expiring</span></div>
                </div>
                <div class="timeline-kpi-card risk">
                    <div class="timeline-kpi-top">
                        <div class="timeline-kpi-icon">{_lc_timeline_icon_svg("alert-circle")}</div>
                        <div class="timeline-kpi-val">{risk_months_count}</div>
                    </div>
                    <div class="timeline-kpi-lbl">Risk Months<span>&ge; 8 contracts</span></div>
                </div>
            </div>
            """
            st.markdown(html_timeline_kpis, unsafe_allow_html=True)
            st.plotly_chart(_build_timeline_chart(df_all), use_container_width=True, config=dict(displayModeBar=False))
            
            # Dynamic HTML Legend & Risk level indicator strip
            risk_blocks = ""
            for val in [exp_month_counts[m] for m in months_list]:
                cls = "low" if val < 5 else ("medium" if val <= 7 else "high")
                risk_blocks += f'<div class="risk-strip-block {cls}" title="Expiring: {val}"></div>'
                
            html_risk_strip = f"""
            <div class="risk-legend-row" style="justify-content: center; margin-top: 4px; margin-bottom: 8px;">
                <div class="risk-legend-item"><span class="risk-legend-dot" style="background-color: #6366F1;"></span><span>Expiring</span></div>
            </div>
            <div class="risk-strip-container">
                <span class="risk-strip-label">Risk Level &rarr;</span>
                <div class="risk-strip-blocks">{risk_blocks}</div>
            </div>
            <div class="risk-legend-row">
                <div class="risk-legend-item"><span class="risk-legend-dot low"></span><span>Low (&lt; 5)</span></div>
                <div class="risk-legend-item"><span class="risk-legend-dot medium"></span><span>Medium (5-7)</span></div>
                <div class="risk-legend-item"><span class="risk-legend-dot high"></span><span>High (&ge; 8)</span></div>
            </div>
            """
            st.markdown(html_risk_strip, unsafe_allow_html=True)

    # ── Column 2: Contract Type Distribution ──
    with col_mid:
        with st.container():
            st.markdown('<div class="premium-card-marker"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="card-title">Contract Type Distribution</div><div class="card-subtitle">By revenue model · {len(df_all)} active contracts</div>', unsafe_allow_html=True)
            
            c_types = _get_contract_types(st.session_state.lc_df)
            keys = list(c_types.keys())
            d_rs = c_types.get(keys[0] if len(keys) > 0 else "N/A", 0)
            d_rs_mo = c_types.get(keys[1] if len(keys) > 1 else "N/A", 0)
            d_mgrs = c_types.get(keys[2] if len(keys) > 2 else "N/A", 0)
            
            d_total = sum(c_types.values()) if sum(c_types.values()) > 0 else 1
            d_rs_pct = (d_rs / d_total) * 100
            d_rs_mo_pct = (d_rs_mo / d_total) * 100
            d_mgrs_pct = (d_mgrs / d_total) * 100
            
            label_rs = keys[0] if len(keys) > 0 else "Type 1"
            label_rs_mo = keys[1] if len(keys) > 1 else "Type 2"
            label_mgrs = keys[2] if len(keys) > 2 else "Type 3"
            
            st.plotly_chart(_build_donut_chart({"RS": d_rs, "RS+MO": d_rs_mo, "MGRS": d_mgrs}, ["#6366F1", "#0EA5E9", "#F59E0B"], size=140), use_container_width=True, config=dict(displayModeBar=False))

            html_dist_stack = f"""
            <div class="dist-stack">
                <div class="dist-card rs">
                    <div class="dist-card-header">
                        <span class="dist-card-title-row"><span class="dist-card-dot"></span>{label_rs}</span>
                        <span class="dist-card-pct">{f"{d_rs_pct:.1f}%".replace(".", ",")}</span>
                    </div>
                    <div class="dist-card-body">
                        <span class="dist-card-count">{d_rs}</span>
                        <span class="dist-card-val">N/A</span>
                    </div>
                </div>
                <div class="dist-card rs_mo">
                    <div class="dist-card-header">
                        <span class="dist-card-title-row"><span class="dist-card-dot"></span>{label_rs_mo}</span>
                        <span class="dist-card-pct">{f"{d_rs_mo_pct:.1f}%".replace(".", ",")}</span>
                    </div>
                    <div class="dist-card-body">
                        <span class="dist-card-count">{d_rs_mo}</span>
                        <span class="dist-card-val">N/A</span>
                    </div>
                </div>
                <div class="dist-card mgrs">
                    <div class="dist-card-header">
                        <span class="dist-card-title-row"><span class="dist-card-dot"></span>{label_mgrs}</span>
                        <span class="dist-card-pct">{f"{d_mgrs_pct:.1f}%".replace(".", ",")}</span>
                    </div>
                    <div class="dist-card-body">
                        <span class="dist-card-count">{d_mgrs}</span>
                        <span class="dist-card-val">N/A</span>
                    </div>
                </div>
            </div>
            """
            st.markdown(html_dist_stack, unsafe_allow_html=True)

            # "Total Estimated Revenue" dihapus dari sini — sebelumnya dihitung
            # dari multiplier fiktif (0.74/0.72 per kontrak), bukan data riil.
            # Kartu di bawah ini hanya menunjukkan jumlah kontrak per skema.
            html_dist_footer = f"""
            <div class="dist-total-footer">
                <span class="dist-total-icon">{_lc_timeline_icon_svg("file-text")}</span>
                <span class="dist-total-label">Total Contracts</span>
                <span class="dist-total-val">{d_rs + d_rs_mo + d_mgrs}</span>
            </div>
            """
            st.markdown(html_dist_footer, unsafe_allow_html=True)

    # ── Column 3: Contract Status ──
    with col_right:
        with st.container():
            st.markdown('<div class="premium-card-marker"></div>', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Contract Status</div><div class="card-subtitle">Portfolio health overview</div>', unsafe_allow_html=True)
            
            p_active = (active_val / total_val * 100) if total_val > 0 else 0
            p_expiring = (expiring_val / total_val * 100) if total_val > 0 else 0
            p_expired = (expired_val / total_val * 100) if total_val > 0 else 0

            # Donut chart on top (just like Column 2)
            st.plotly_chart(_build_donut_chart({"Active": active_val, "Expiring Soon": expiring_val, "Expired": expired_val}, ["#10B981", "#F59E0B", "#EF4444"], size=140), use_container_width=True, config=dict(displayModeBar=False))
            
            # Status list below the donut chart, styled like Column 2
            html_status_stack = f"""
            <div class="dist-stack">
                <div class="status-card active">
                    <div class="dist-card-header">
                        <span class="dist-card-title-row"><span class="status-card-dot active"></span>Active</span>
                        <span class="dist-card-pct active">{f"{p_active:.1f}%".replace(".", ",")}</span>
                    </div>
                    <div class="dist-card-body">
                        <span class="dist-card-count">{active_val}</span>
                        <span class="dist-card-val">Valid contracts</span>
                    </div>
                </div>
                <div class="status-card expiring">
                    <div class="dist-card-header">
                        <span class="dist-card-title-row"><span class="status-card-dot expiring"></span>Expiring Soon</span>
                        <span class="dist-card-pct expiring">{f"{p_expiring:.1f}%".replace(".", ",")}</span>
                    </div>
                    <div class="dist-card-body">
                        <span class="dist-card-count">{expiring_val}</span>
                        <span class="dist-card-val">Within next 90 days</span>
                    </div>
                </div>
                <div class="status-card expired">
                    <div class="dist-card-header">
                        <span class="dist-card-title-row"><span class="status-card-dot expired"></span>Expired</span>
                        <span class="dist-card-pct expired">{f"{p_expired:.1f}%".replace(".", ",")}</span>
                    </div>
                    <div class="dist-card-body">
                        <span class="dist-card-count">{expired_val}</span>
                        <span class="dist-card-val">Requires attention</span>
                    </div>
                </div>
            </div>
            """
            st.markdown(html_status_stack, unsafe_allow_html=True)
            
            if p_active >= 80:
                health_label, health_color = "Good", "#10B981"
            elif p_active >= 60:
                health_label, health_color = "Fair", "#F59E0B"
            else:
                health_label, health_color = "At Risk", "#EF4444"

            # Single-line footer matching Column 2's footer
            html_status_footer = f"""
            <div class="dist-total-footer">
                <span class="dist-total-icon">{_lc_timeline_icon_svg("check-circle")}</span>
                <span class="dist-total-label">Portfolio Health Score</span>
                <span class="dist-total-val" style="color: {health_color};">{f"{p_active:.1f}%".replace(".", ",")} ({health_label})</span>
            </div>
            """
            st.markdown(html_status_footer, unsafe_allow_html=True)

    st.markdown('<div class="lc-vertical-spacer"></div>', unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # CONTRACTS EXPIRING SOON — header card + 3 stat pills, then one
    # bordered card per severity (icon + colored title + "View all (N)"
    # strip, table, and a "Show more" toggle past the first 5 rows).
    # ─────────────────────────────────────────────
    AVATAR_PALETTE = ["#6366F1", "#EC4899", "#10B981", "#F59E0B", "#0EA5E9", "#8B5CF6", "#EF4444", "#14B8A6"]
    VARIANT_COLOR = {"danger": "#EF4444", "warning": "#F59E0B", "success": "#10B981"}

    def _tenant_avatar_html(name: str) -> str:
        initial = (name or "?").strip()[:1].upper() or "?"
        color = AVATAR_PALETTE[abs(hash(name)) % len(AVATAR_PALETTE)]
        return f'<span class="lc-tenant-avatar" style="background:{color};">{initial}</span>'

    def _render_exp_section(key, variant, icon, title, items):
        show_all_key = f"lc_show_all_{key}"
        total = len(items)
        visible_items = items if st.session_state[show_all_key] else items[:5]

        rows_html = ""
        for item in visible_items:
            rows_html += (
                "<tr>"
                f"<td><div class='lc-tenant-cell'>{_tenant_avatar_html(item['tenant'])}"
                f"<span style='font-weight:700;color:#0F172A;'>{item['tenant']}</span></div></td>"
                f"<td>{item['terminal']}</td>"
                f"<td style='color:#64748B;'>{item['type']}</td>"
                f"<td style='font-weight:600;'>{item['end_date']}</td>"
                f"<td style='font-weight:800;color:{VARIANT_COLOR[variant]};'>{item['remaining']}</td>"
                f"<td style='font-weight:700;color:#0F172A;'>{item['value']}</td>"
                f"<td><span class='status-badge badge-{variant}'>{item['status']}</span></td>"
                "</tr>"
            )
        if not rows_html:
            rows_html = (
                "<tr><td colspan=7 style='text-align:center;color:#64748B;'>"
                "No contracts found for current filters</td></tr>"
            )

        with st.container():
            st.markdown(f'<div class="lc-exp-section-marker-{key}"></div>', unsafe_allow_html=True)
            st.markdown(
                f'<div class="lc-exp-section-card">'
                f'<div class="lc-exp-section-head {variant}">'
                f'<span class="lc-exp-section-icon">{icon}</span>'
                f'<span class="lc-exp-section-title {variant}">{title}</span>'
                f'<span style="margin-left:auto;font-size:11px;font-weight:700;color:#334155;'
                f'background:#fff;border:1px solid rgba(15,23,42,0.08);border-radius:10px;'
                f'padding:5px 12px;white-space:nowrap;">{total} Contracts</span>'
                f'</div>'
                f'<div class="lc-exp-table-wrap">'
                f'<table class="custom-table">'
                f'<thead><tr><th>Tenant</th><th>Terminal</th><th>Contract Type</th>'
                f'<th>End Date</th><th>Remaining</th><th>Contract Value</th><th>Status</th></tr></thead>'
                f'<tbody>{rows_html}</tbody>'
                f'</table>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

            if total > 5:
                st.markdown('<div class="lc-exp-show-more-marker"></div>', unsafe_allow_html=True)
                _, mid, _ = st.columns([2, 1, 2])
                with mid:
                    label = "Show less ▲" if st.session_state[show_all_key] else "Show more ▾"
                    if st.button(label, key=f"lc_toggle_{key}", use_container_width=True):
                        st.session_state[show_all_key] = not st.session_state[show_all_key]
                        st.rerun()

    # Build dynamic list of critical contracts
    dynamic_critical = []
    crit_df = df_all[(df_all["Status"] == "Anomaly") & (df_all["Sisa"] <= 30)]
    for _, r in crit_df.iterrows():
        end_date = r["Valid Period"].split(" - ")[1] if " - " in r["Valid Period"] else "31 Jan 2025"
        dynamic_critical.append({
            "tenant": r["Name/Tenant"], "terminal": r["Terminal"], "type": r["Skema"],
            "end_date": end_date, "remaining": f"{r['Sisa']}d", "value": "N/A", "status": "Critical"
        })

    # Build dynamic list of expiring soon contracts
    dynamic_expiring = []
    exp_df = df_all[(df_all["Status"] == "Anomaly") & (df_all["Sisa"] > 30) & (df_all["Sisa"] <= 90)]
    for _, r in exp_df.iterrows():
        end_date = r["Valid Period"].split(" - ")[1] if " - " in r["Valid Period"] else "01 Mar 2025"
        dynamic_expiring.append({
            "tenant": r["Name/Tenant"], "terminal": r["Terminal"], "type": r["Skema"],
            "end_date": end_date, "remaining": f"{r['Sisa']}d", "value": "N/A", "status": "Expiring Soon"
        })

    # Build dynamic list of approaching renewal contracts (no cap here —
    # the "Show more" toggle controls how many rows are visible)
    dynamic_approaching = []
    app_df = df_all[(df_all["Status"] == "Valid") & (df_all["Sisa"] > 90)].sort_values(by="Sisa")
    for _, r in app_df.iterrows():
        end_date = r["Valid Period"].split(" - ")[1] if " - " in r["Valid Period"] else "02 May 2025"
        dynamic_approaching.append({
            "tenant": r["Name/Tenant"], "terminal": r["Terminal"], "type": r["Skema"],
            "end_date": end_date, "remaining": f"{r['Sisa']}d", "value": "N/A", "status": "Approaching"
        })

    # Header card: title + 3 stat pills, all wrapped in one outer card
    with st.container():
        st.markdown('<div class="lc-exp-outer-marker"></div>', unsafe_allow_html=True)
        h_left, h_s1, h_s2, h_s3 = st.columns(4)
        with h_left:
            st.markdown(
                '<div class="lc-exp-header-card" style="height:100%;box-sizing:border-box;">'
                '<div class="lc-exp-header-title">Contracts Expiring Soon</div>'
                '<div class="lc-exp-header-sub">Sorted by remaining days</div>'
                '</div>',
                unsafe_allow_html=True,
            )
        stat_defs = [
            (h_s1, "danger", "⚠️", "Critical", "Expires within 30 days", len(dynamic_critical)),
            (h_s2, "warning", "⏳", "Expiring Soon", "Expires in 31 to 90 days", len(dynamic_expiring)),
            (h_s3, "success", "🛡️", "Approaching Renewal", "Expires in 90+ days", len(dynamic_approaching)),
        ]
        for col, variant, icon, label, caption, count in stat_defs:
            with col:
                st.markdown(
                    f'<div class="lc-exp-stat {variant}" style="height:100%;box-sizing:border-box;">'
                    f'<span class="lc-exp-stat-icon">{icon}</span>'
                    f'<span class="lc-exp-stat-text">'
                    f'<span class="lc-exp-stat-label {variant}">{label}</span>'
                    f'<span class="lc-exp-stat-caption">{caption}</span>'
                    f'</span>'
                    f'<span class="lc-exp-stat-value">{count}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

    _render_exp_section("critical", "danger", "⚠️", "Critical — Expires within 30 days", dynamic_critical)
    _render_exp_section("expiring", "warning", "⏳", "Expiring Soon — Expires within 31 to 90 days", dynamic_expiring)
    _render_exp_section("approaching", "success", "🛡️", "Approaching Renewal — Expires in 90+ days", dynamic_approaching)

# ── Standalone Running compatibility ─────────
if __name__ == "__main__":
    st.set_page_config(page_title="Lease Contract Dashboard", layout="wide")
    render_lease_contract()
