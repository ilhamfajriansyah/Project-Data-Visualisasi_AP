import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, datetime
from textwrap import dedent

from .shared_import import get_shared_import_data, get_shared_import_meta
from .navigation import topnav_actions_html

DV_PAGE_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'width="18" height="18" fill="none" stroke="currentColor" '
    'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true">'
    '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>'
    '<path d="m9 12 2 2 4-4"/>'
    '</svg>'
)


def _dv_page_header_html():
    return dedent(f"""
    <div class="ov-page-header">
        <div class="ov-page-header-left">
            <div class="ov-page-icon" aria-hidden="true">{DV_PAGE_ICON_SVG}</div>
            <div class="ov-page-header-copy">
                <div class="ov-page-title-row">
                    <h2 class="ov-page-title">Data Verification</h2>
                </div>
                <p class="ov-page-sub">Verifikasi dan validasi data yang telah diimport dari Import Manager.</p>
            </div>
        </div>
        {topnav_actions_html()}
    </div>
    """).strip()


def _mount_dv_fixed_header():
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

# ─────────────────────────────────────────────
# DUMMY DATA — nanti diganti dari session_state import_manager
# ─────────────────────────────────────────────
def _get_verification_data() -> pd.DataFrame:
    """
    DATA SOURCE:
    Saat ini menggunakan dummy data.
    Nanti sambungkan ke st.session_state['im_imported_data']
    yang di-set dari import_manager.py setelah Execute Import.
    
    Contoh integrasi:
        if 'im_imported_data' in st.session_state:
            return st.session_state['im_imported_data']
        return _dummy_data()
    """
    imported_df = get_shared_import_data()
    if imported_df is not None:
        meta = get_shared_import_meta()
        df = imported_df.copy()
        rows = []
        for idx, r in df.iterrows():
            real_omzet = r.get("real_omzet", r.get("omzet", 0))
            try:
                conflict_info = f"Rp {float(real_omzet) / 1_000_000_000:.2f}B"
            except (TypeError, ValueError):
                conflict_info = str(real_omzet or "-")

            brand = r.get("brand", r.get("perusahaan", r.get("tenant_name", "-")))
            kode_ruang = r.get("kode_ruang", r.get("unit", "-"))
            periode = r.get("masa_jasa", r.get("periode", meta.get("period", "April 2026")))
            rows.append({
                "Kode Ruang": kode_ruang if pd.notna(kode_ruang) else "-",
                "Brand/Tenant": brand if pd.notna(brand) else "-",
                "SAP ID": str(r.get("sap_id", "SAP: -")),
                "Legal ID": str(r.get("legal_id", "Legal: -")),
                "Real Onset": str(periode),
                "End Kontrak": str(r.get("end_kontrak", "-")),
                "Status": "Active",
                "Skema": str(r.get("skema", r.get("bidang_usaha", "-"))),
                "Conflict Info": conflict_info,
                "Anomali": bool(pd.isna(real_omzet) or pd.isna(kode_ruang) or pd.isna(brand)),
            })
        return pd.DataFrame(rows)

    data = [
        {"Kode Ruang": "FB-01-01", "Brand/Tenant": "Starbucks Corp",  "SAP ID": "SAP: 10233",  "Legal ID": "Legal 4C-2021-001", "Real Onset": "01 Jun 2023 – 31 Dec 2023", "End Kontrak": "31 Dec 2023", "Status": "Active",       "Skema": "Rental", "Conflict Info": "Rp 152B", "Anomali": False},
        {"Kode Ruang": "RT-02-07", "Brand/Tenant": "Burger King",     "SAP ID": "SAP: 10233",  "Legal ID": "Legal 4C-2021-003", "Real Onset": "01 Jul 2026 – 30 Dec 2024", "End Kontrak": "30 Dec 2024", "Status": "Expired Soon",  "Skema": "RS",     "Conflict Info": "Rp 95B",  "Anomali": True},
        {"Kode Ruang": "LG-01-12", "Brand/Tenant": "Local Cafe",      "SAP ID": "SAP: 10223",  "Legal ID": "Legal 4C-2021-005", "Real Onset": "01 Jun 2026 – 31 Dec 2024", "End Kontrak": "31 Dec 2024", "Status": "Expired",       "Skema": "MG45",   "Conflict Info": "Rp 80B",  "Anomali": True},
        {"Kode Ruang": "SV-01-03", "Brand/Tenant": "Rod Boy",         "SAP ID": "SAP: 10233",  "Legal ID": "Legal 4C-2021-006", "Real Onset": "01 Jun 2026 – 31 Dec 2024", "End Kontrak": "31 Dec 2024", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 75B",  "Anomali": False},
        {"Kode Ruang": "FB-03-02", "Brand/Tenant": "KFC Outlet",      "SAP ID": "SAP: 10244",  "Legal ID": "Legal 4C-2022-001", "Real Onset": "15 Mar 2023 – 14 Mar 2025", "End Kontrak": "14 Mar 2025", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 110B", "Anomali": False},
        {"Kode Ruang": "RT-03-08", "Brand/Tenant": "Majapahit Store", "SAP ID": "SAP: 10255",  "Legal ID": "Legal 4C-2022-003", "Real Onset": "01 Jun 2022 – 31 May 2025", "End Kontrak": "31 May 2025", "Status": "Expired Soon",  "Skema": "RS",     "Conflict Info": "Rp 88B",  "Anomali": True},
        {"Kode Ruang": "LG-02-01", "Brand/Tenant": "GAUSD VIP",       "SAP ID": "SAP: 10266",  "Legal ID": "Legal 4C-2023-001", "Real Onset": "01 Jan 2023 – 31 Dec 2025", "End Kontrak": "31 Dec 2025", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 200B", "Anomali": False},
        {"Kode Ruang": "SV-02-05", "Brand/Tenant": "Pertamina Outlet","SAP ID": "SAP: 10277",  "Legal ID": "Legal 4C-2023-002", "Real Onset": "01 May 2023 – 30 Apr 2025", "End Kontrak": "30 Apr 2025", "Status": "Expired",       "Skema": "MG45",   "Conflict Info": "Rp 60B",  "Anomali": True},
        {"Kode Ruang": "FB-02-07", "Brand/Tenant": "Wingman Bistro",  "SAP ID": "SAP: 10288",  "Legal ID": "Legal 4C-2023-004", "Real Onset": "01 Apr 2024 – 31 Mar 2026", "End Kontrak": "31 Mar 2026", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 92B",  "Anomali": False},
        {"Kode Ruang": "RT-01-11", "Brand/Tenant": "Aquarus Cafe",    "SAP ID": "SAP: 10299",  "Legal ID": "Legal 4C-2023-005", "Real Onset": "14 Feb 2023 – 13 Feb 2026", "End Kontrak": "13 Feb 2026", "Status": "Active",        "Skema": "RS",     "Conflict Info": "Rp 78B",  "Anomali": False},
        {"Kode Ruang": "SV-03-04", "Brand/Tenant": "Bon Bon Express", "SAP ID": "SAP: 10310",  "Legal ID": "Legal 4C-2024-001", "Real Onset": "01 Aug 2024 – 31 Jul 2026", "End Kontrak": "31 Jul 2026", "Status": "Expired Soon",  "Skema": "Rental", "Conflict Info": "Rp 45B",  "Anomali": True},
        {"Kode Ruang": "LG-03-06", "Brand/Tenant": "Bakso Corner",    "SAP ID": "SAP: 10321",  "Legal ID": "Legal 4C-2024-002", "Real Onset": "01 Jan 2024 – 31 Dec 2025", "End Kontrak": "31 Dec 2025", "Status": "Active",        "Skema": "MG45",   "Conflict Info": "Rp 55B",  "Anomali": False},
        {"Kode Ruang": "FB-01-09", "Brand/Tenant": "Pizza Hut",       "SAP ID": "SAP: 10332",  "Legal ID": "Legal 4C-2024-003", "Real Onset": "01 Mar 2024 – 28 Feb 2026", "End Kontrak": "28 Feb 2026", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 130B", "Anomali": False},
        {"Kode Ruang": "RT-02-14", "Brand/Tenant": "Indomaret",       "SAP ID": "SAP: 10343",  "Legal ID": "Legal 4C-2024-004", "Real Onset": "01 Jun 2024 – 31 May 2026", "End Kontrak": "31 May 2026", "Status": "Expired Soon",  "Skema": "RS",     "Conflict Info": "Rp 67B",  "Anomali": True},
        {"Kode Ruang": "SV-01-07", "Brand/Tenant": "Alfamart",        "SAP ID": "SAP: 10354",  "Legal ID": "Legal 4C-2024-005", "Real Onset": "15 Sep 2024 – 14 Sep 2026", "End Kontrak": "14 Sep 2026", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 48B",  "Anomali": False},
        {"Kode Ruang": "LG-01-04", "Brand/Tenant": "J.CO Donuts",     "SAP ID": "SAP: 10365",  "Legal ID": "Legal 4C-2024-006", "Real Onset": "01 Oct 2024 – 30 Sep 2026", "End Kontrak": "30 Sep 2026", "Status": "Active",        "Skema": "MG45",   "Conflict Info": "Rp 72B",  "Anomali": False},
        {"Kode Ruang": "FB-03-11", "Brand/Tenant": "Solaria",         "SAP ID": "SAP: 10376",  "Legal ID": "Legal 4C-2025-001", "Real Onset": "01 Jan 2025 – 31 Dec 2026", "End Kontrak": "31 Dec 2026", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 98B",  "Anomali": False},
        {"Kode Ruang": "RT-03-05", "Brand/Tenant": "Gramedia",        "SAP ID": "SAP: 10387",  "Legal ID": "Legal 4C-2025-002", "Real Onset": "01 Feb 2025 – 31 Jan 2027", "End Kontrak": "31 Jan 2027", "Status": "Active",        "Skema": "RS",     "Conflict Info": "Rp 85B",  "Anomali": False},
        {"Kode Ruang": "SV-02-09", "Brand/Tenant": "Timezone",        "SAP ID": "SAP: 10398",  "Legal ID": "Legal 4C-2025-003", "Real Onset": "01 Mar 2025 – 28 Feb 2027", "End Kontrak": "28 Feb 2027", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 115B", "Anomali": False},
        {"Kode Ruang": "LG-02-08", "Brand/Tenant": "Hypermart",       "SAP ID": "SAP: 10409",  "Legal ID": "Legal 4C-2025-004", "Real Onset": "15 Apr 2025 – 14 Apr 2027", "End Kontrak": "14 Apr 2027", "Status": "Expired",       "Skema": "MG45",   "Conflict Info": "Rp 140B", "Anomali": True},
    ]
    return pd.DataFrame(data)


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
_PAGE_CSS = """
<style>
/* Pull the action-buttons row up to close the default Streamlit gap left
   after the fixed header's spacer (mirrors the same fix used elsewhere)
   — keeps it compact/close to the header. */
body:has(.dv-page-marker) div[data-testid="stElementContainer"]:has(.dv-actions-marker) + div[data-testid="stHorizontalBlock"] {
    margin-top: -85px !important;
}

/* ── KPI CARDS ── */
.dv-kpi {
    background: rgba(255,255,255,0.68);
    backdrop-filter: blur(22px);
    border: 1px solid rgba(255,255,255,0.94);
    border-radius: 18px;
    padding: 18px 16px 16px;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 6px 24px rgba(99,102,241,0.07), inset 0 1px 0 rgba(255,255,255,1);
    transition: transform .2s, box-shadow .2s;
    position: relative; overflow: hidden;
}
.dv-kpi:hover { transform: translateY(-2px); box-shadow: 0 12px 32px rgba(99,102,241,0.12), inset 0 1px 0 rgba(255,255,255,1); }
.dv-kpi-left {}
.dv-kpi-label { font-size: 11px; font-weight: 700; color: #64748b; margin-bottom: 6px; }
.dv-kpi-value { font-size: 30px; font-weight: 800; color: #0f172a; line-height: 1.1; }
.dv-kpi-icon {
    width: 44px; height: 44px; border-radius: 50%;
    background: var(--icon-bg, rgba(99,102,241,0.10));
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
}

/* ── TABLE ── */
.dv-table { width: 100%; border-collapse: collapse; }
.dv-table thead tr {
    border-bottom: 1px solid rgba(99,102,241,0.08);
}
.dv-table th {
    padding: 12px 16px; text-align: left;
    font-size: 11px; font-weight: 700; color: #64748b;
    letter-spacing: 0.3px; white-space: nowrap;
}
.dv-table td {
    padding: 14px 16px; font-size: 12.5px; color: #334155;
    border-bottom: 1px solid rgba(99,102,241,0.04);
    vertical-align: middle;
}
.dv-table tbody tr { transition: background 0.15s; }
.dv-table tbody tr:hover { background: rgba(99,102,241,0.025); }
.dv-table tbody tr.anomali-row { background: rgba(245,158,11,0.03); }
.dv-table tbody tr:last-child td { border-bottom: none; }

.dv-kode   { font-weight: 700; color: #1e293b; font-size: 12.5px; }
.dv-brand  { font-weight: 600; color: #1e293b; font-size: 12.5px; }
.dv-sap    { font-size: 10.5px; color: #94a3b8; margin-top: 2px; }
.dv-onset  { font-size: 12px; color: #475569; }

/* ── STATUS BADGES ── */
.b-active      { background:rgba(6,182,212,0.12);  color:#0891b2; border:1px solid rgba(6,182,212,0.25); padding:4px 14px; border-radius:999px; font-size:11.5px; font-weight:700; white-space:nowrap; }
.b-expiredsoon { background:rgba(245,158,11,0.13); color:#d97706; border:1px solid rgba(245,158,11,0.28); padding:4px 14px; border-radius:999px; font-size:11.5px; font-weight:700; white-space:nowrap; }
.b-expired     { background:rgba(239,68,68,0.10);  color:#dc2626; border:1px solid rgba(239,68,68,0.22); padding:4px 14px; border-radius:999px; font-size:11.5px; font-weight:700; white-space:nowrap; }

.dv-skema      { font-size: 11.5px; font-weight: 700; color: #4f46e5; }
.dv-conflict   { font-size: 12.5px; font-weight: 700; color: #0f172a; }

/* ── FOOTER ── */
.dv-footer {
    display: flex; align-items: center; justify-content: space-between;
    padding: 13px 18px;
    border-top: 1px solid rgba(99,102,241,0.07);
    flex-wrap: wrap; gap: 8px;
}
.dv-footer-info { font-size: 11.5px; color: #94a3b8; font-weight: 500; }

/* ── PAGINATION ── */
.dv-pg-btn {
    width: 30px; height: 30px; border-radius: 8px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 12.5px; font-weight: 600; cursor: pointer;
    border: 1px solid rgba(99,102,241,0.12);
    background: rgba(255,255,255,0.6); color: #64748b;
}
.dv-pg-btn.active {
    background: linear-gradient(135deg,#6366f1,#4f46e5);
    color:#fff; border-color:transparent;
    box-shadow: 0 3px 10px rgba(99,102,241,0.30);
}

/* ── ANOMALI BADGE ── */
.anomali-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #f59e0b;
    display: inline-block; margin-right: 5px;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.18);
}
</style>
"""


# ─────────────────────────────────────────────
# INIT STATE
# ─────────────────────────────────────────────
def _init_state():
    if "dv_page"   not in st.session_state: st.session_state.dv_page   = 0
    current_data = _get_verification_data()
    if get_shared_import_data() is not None:
        st.session_state.dv_df = current_data
    elif "dv_df" not in st.session_state:
        st.session_state.dv_df = current_data


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _status_badge(s):
    if s == "Active":       return '<span class="b-active">Active</span>'
    if s == "Expired Soon": return '<span class="b-expiredsoon">Expired Soon</span>'
    if s == "Expired":      return '<span class="b-expired">Expired</span>'
    return f'<span>{s}</span>'


# ─────────────────────────────────────────────
# TABLE RENDERER
# ─────────────────────────────────────────────
def _render_table(df: pd.DataFrame, page: int, page_size: int = 5):
    total   = len(df)
    n_pages = max(1, -(-total // page_size))
    page    = max(0, min(page, n_pages - 1))
    start   = page * page_size
    end     = min(start + page_size, total)
    rows    = df.iloc[start:end]

    rows_html = ""
    for _, r in rows.iterrows():
        anomali_class = "anomali-row" if r["Anomali"] else ""
        anomali_dot   = '<span class="anomali-dot"></span>' if r["Anomali"] else ""
        rows_html += f"""
        <tr class="{anomali_class}">
          <td>
            <div class="dv-kode">{r['Kode Ruang']}</div>
          </td>
          <td>
            <div class="dv-brand">{anomali_dot}{r['Brand/Tenant']}</div>
            <div class="dv-sap">{r['SAP ID']} · {r['Legal ID']}</div>
          </td>
          <td class="dv-onset">{r['Real Onset']}</td>
          <td>{_status_badge(r['Status'])}</td>
          <td class="dv-skema">{r['Skema']}</td>
          <td class="dv-conflict">{r['Conflict Info']}</td>
        </tr>"""

    html = f"""
    <div class="nad-card" style="padding:0;overflow:hidden;">
      <div style="overflow-x:auto;">
        <table class="dv-table">
          <thead>
            <tr>
              <th>Kode Ruang</th>
              <th>Brand / Tenant</th>
              <th>Real Onset</th>
              <th>Status</th>
              <th>Skema</th>
              <th>Conflict Info</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
      <div class="dv-footer">
        <span class="dv-footer-info">Showing {start+1} to {end} of {total} entries</span>
      </div>
    </div>"""

    st.markdown(html, unsafe_allow_html=True)
    return page, n_pages


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def render_data_verification():
    """Call this from dashboard.py router."""
    _init_state()
    st.markdown('<div class="overview-page-marker dv-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="ov-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_dv_page_header_html(), unsafe_allow_html=True)
        st.markdown('<div class="ov-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="ov-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)
    _mount_dv_fixed_header()

    # ── Action Buttons ──
    st.markdown('<div class="dv-actions-marker"></div>', unsafe_allow_html=True)
    _, ab1, ab2 = st.columns([6, 1.6, 1.8])
    with ab1:
        df_exp = st.session_state.dv_df.copy()
        csv = df_exp.drop(columns=["Anomali"]).to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ + Export Logs", data=csv,
                           file_name="data_verification.csv", mime="text/csv",
                           use_container_width=True, key="dv_export")
    with ab2:
        if st.button("✅ Approve & Publish", use_container_width=True, key="dv_approve"):
            st.toast("✅ Data berhasil dipublikasikan!", icon="✅")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── 4 KPI Cards ── (mirip screenshot: Total Records, Valid, Anomalies, Conflicts)
    df_all = st.session_state.dv_df
    total_records = len(df_all)
    valid_records = int((df_all["Status"] == "Active").sum())
    anomalies     = int(df_all["Anomali"].sum())
    conflicts     = int((df_all["Status"] == "Expired").sum())

    k1, k2, k3, k4 = st.columns(4)
    kpi_cfg = [
        (k1, "📄", "rgba(99,102,241,0.10)",  "Total Records",  total_records),
        (k2, "✅", "rgba(16,185,129,0.10)",  "Valid Records",  valid_records),
        (k3, "⚠️", "rgba(245,158,11,0.10)", "Anomalies",      anomalies),
        (k4, "🔄", "rgba(239,68,68,0.10)",  "Conflicts",      conflicts),
    ]
    for col, icon, icon_bg, label, value in kpi_cfg:
        with col:
            st.markdown(f"""
            <div class="dv-kpi">
                <div class="dv-kpi-left">
                    <div class="dv-kpi-label">{label}</div>
                    <div class="dv-kpi-value">{value:,}</div>
                </div>
                <div class="dv-kpi-icon" style="--icon-bg:{icon_bg};">{icon}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Filter Row ──
    fc1, fc2, fsp = st.columns([2, 2.4, 5.6])
    with fc1:
        status_f = st.selectbox(
            "", ["Status ▾", "Active", "Expired Soon", "Expired"],
            label_visibility="collapsed", key="dv_fstatus")
    with fc2:
        anom_f = st.selectbox(
            "", ["Anomalies Type ▾", "Dengan Anomali", "Tanpa Anomali"],
            label_visibility="collapsed", key="dv_fanom")

    # ── Apply Filters ──
    df = st.session_state.dv_df.copy()
    if status_f not in ["Status ▾", ""]:
        df = df[df["Status"] == status_f]
    if anom_f == "Dengan Anomali":
        df = df[df["Anomali"] == True]
    elif anom_f == "Tanpa Anomali":
        df = df[df["Anomali"] == False]
    df = df.reset_index(drop=True)

    # Reset page on filter change
    fkey = f"{status_f}|{anom_f}"
    if st.session_state.get("_dv_last_filter") != fkey:
        st.session_state.dv_page = 0
        st.session_state["_dv_last_filter"] = fkey

    # ── Table ──
    page, n_pages = _render_table(df, st.session_state.dv_page)

    # ── Pagination ──
    if n_pages > 1:
        pg_cols = st.columns(n_pages + 2)
        with pg_cols[0]:
            if st.button("‹", key="dv_pg_prev", disabled=(page == 0)):
                st.session_state.dv_page = page - 1
                st.rerun()
        for i in range(n_pages):
            with pg_cols[i + 1]:
                lbl = f"**{i+1}**" if i == page else str(i + 1)
                if st.button(lbl, key=f"dv_pg_{i}"):
                    st.session_state.dv_page = i
                    st.rerun()
        with pg_cols[n_pages + 1]:
            if st.button("›", key="dv_pg_next", disabled=(page >= n_pages - 1)):
                st.session_state.dv_page = page + 1
                st.rerun()

    # ── INFO BOX: Integrasi Import Manager ──
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.16);
        border-radius:14px;padding:13px 18px;display:flex;align-items:flex-start;gap:10px;">
        <span style="font-size:16px;flex-shrink:0;">🔗</span>
        <div>
            <div style="font-size:12px;font-weight:700;color:#4f46e5;margin-bottom:3px;">
                Integrasi Import Manager</div>
            <div style="font-size:11.5px;color:#64748b;line-height:1.6;">
                Data pada halaman ini bersumber dari <strong>Import Manager → Execute Import</strong>.
                Setelah PIC melakukan upload dan Admin menekan <em>Execute Import</em>,
                data akan otomatis tersinkronisasi ke halaman ini melalui
                <code>st.session_state['im_imported_data']</code>.
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


# ── Standalone ──────────────────────────────
if __name__ == "__main__":
    st.set_page_config(page_title="Data Verification", layout="wide")
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    render_data_verification()
