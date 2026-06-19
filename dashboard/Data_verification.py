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
    <div class="dv-page-header">
        <div class="dv-page-header-left">
            <div class="dv-page-icon" aria-hidden="true">{DV_PAGE_ICON_SVG}</div>
            <div class="dv-page-header-copy">
                <div class="dv-page-title-row">
                    <h2 class="dv-page-title">Data Verification</h2>
                </div>
                <p class="dv-page-sub">Verifikasi dan validasi data yang telah diimport dari Import Manager.</p>
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
                const marker = doc.querySelector('.dv-sticky-header-marker');
                if (!marker) return;

                const host = findHeaderHost(marker);
                if (!host) return;

                host.classList.add('dv-fixed-header-active');

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
                conflict_info = f"Rp {float(real_omzet) / 1_000_000_000:.2f}M"
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
        {"Kode Ruang": "FB-01-01", "Brand/Tenant": "Starbucks Corp",  "SAP ID": "SAP: 10233",  "Legal ID": "Legal 4C-2021-001", "Real Onset": "01 Jun 2023 – 31 Dec 2023", "End Kontrak": "31 Dec 2023", "Status": "Active",       "Skema": "Rental", "Conflict Info": "Rp 152M", "Anomali": False},
        {"Kode Ruang": "RT-02-07", "Brand/Tenant": "Burger King",     "SAP ID": "SAP: 10233",  "Legal ID": "Legal 4C-2021-003", "Real Onset": "01 Jul 2026 – 30 Dec 2024", "End Kontrak": "30 Dec 2024", "Status": "Expired Soon",  "Skema": "RS",     "Conflict Info": "Rp 95M",  "Anomali": True},
        {"Kode Ruang": "LG-01-12", "Brand/Tenant": "Local Cafe",      "SAP ID": "SAP: 10223",  "Legal ID": "Legal 4C-2021-005", "Real Onset": "01 Jun 2026 – 31 Dec 2024", "End Kontrak": "31 Dec 2024", "Status": "Expired",       "Skema": "MG45",   "Conflict Info": "Rp 80M",  "Anomali": True},
        {"Kode Ruang": "SV-01-03", "Brand/Tenant": "Rod Boy",         "SAP ID": "SAP: 10233",  "Legal ID": "Legal 4C-2021-006", "Real Onset": "01 Jun 2026 – 31 Dec 2024", "End Kontrak": "31 Dec 2024", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 75M",  "Anomali": False},
        {"Kode Ruang": "FB-03-02", "Brand/Tenant": "KFC Outlet",      "SAP ID": "SAP: 10244",  "Legal ID": "Legal 4C-2022-001", "Real Onset": "15 Mar 2023 – 14 Mar 2025", "End Kontrak": "14 Mar 2025", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 110M", "Anomali": False},
        {"Kode Ruang": "RT-03-08", "Brand/Tenant": "Majapahit Store", "SAP ID": "SAP: 10255",  "Legal ID": "Legal 4C-2022-003", "Real Onset": "01 Jun 2022 – 31 May 2025", "End Kontrak": "31 May 2025", "Status": "Expired Soon",  "Skema": "RS",     "Conflict Info": "Rp 88M",  "Anomali": True},
        {"Kode Ruang": "LG-02-01", "Brand/Tenant": "GAUSD VIP",       "SAP ID": "SAP: 10266",  "Legal ID": "Legal 4C-2023-001", "Real Onset": "01 Jan 2023 – 31 Dec 2025", "End Kontrak": "31 Dec 2025", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 200M", "Anomali": False},
        {"Kode Ruang": "SV-02-05", "Brand/Tenant": "Pertamina Outlet","SAP ID": "SAP: 10277",  "Legal ID": "Legal 4C-2023-002", "Real Onset": "01 May 2023 – 30 Apr 2025", "End Kontrak": "30 Apr 2025", "Status": "Expired",       "Skema": "MG45",   "Conflict Info": "Rp 60M",  "Anomali": True},
        {"Kode Ruang": "FB-02-07", "Brand/Tenant": "Wingman Bistro",  "SAP ID": "SAP: 10288",  "Legal ID": "Legal 4C-2023-004", "Real Onset": "01 Apr 2024 – 31 Mar 2026", "End Kontrak": "31 Mar 2026", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 92M",  "Anomali": False},
        {"Kode Ruang": "RT-01-11", "Brand/Tenant": "Aquarus Cafe",    "SAP ID": "SAP: 10299",  "Legal ID": "Legal 4C-2023-005", "Real Onset": "14 Feb 2023 – 13 Feb 2026", "End Kontrak": "13 Feb 2026", "Status": "Active",        "Skema": "RS",     "Conflict Info": "Rp 78M",  "Anomali": False},
        {"Kode Ruang": "SV-03-04", "Brand/Tenant": "Bon Bon Express", "SAP ID": "SAP: 10310",  "Legal ID": "Legal 4C-2024-001", "Real Onset": "01 Aug 2024 – 31 Jul 2026", "End Kontrak": "31 Jul 2026", "Status": "Expired Soon",  "Skema": "Rental", "Conflict Info": "Rp 45M",  "Anomali": True},
        {"Kode Ruang": "LG-03-06", "Brand/Tenant": "Bakso Corner",    "SAP ID": "SAP: 10321",  "Legal ID": "Legal 4C-2024-002", "Real Onset": "01 Jan 2024 – 31 Dec 2025", "End Kontrak": "31 Dec 2025", "Status": "Active",        "Skema": "MG45",   "Conflict Info": "Rp 55M",  "Anomali": False},
        {"Kode Ruang": "FB-01-09", "Brand/Tenant": "Pizza Hut",       "SAP ID": "SAP: 10332",  "Legal ID": "Legal 4C-2024-003", "Real Onset": "01 Mar 2024 – 28 Feb 2026", "End Kontrak": "28 Feb 2026", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 130M", "Anomali": False},
        {"Kode Ruang": "RT-02-14", "Brand/Tenant": "Indomaret",       "SAP ID": "SAP: 10343",  "Legal ID": "Legal 4C-2024-004", "Real Onset": "01 Jun 2024 – 31 May 2026", "End Kontrak": "31 May 2026", "Status": "Expired Soon",  "Skema": "RS",     "Conflict Info": "Rp 67M",  "Anomali": True},
        {"Kode Ruang": "SV-01-07", "Brand/Tenant": "Alfamart",        "SAP ID": "SAP: 10354",  "Legal ID": "Legal 4C-2024-005", "Real Onset": "15 Sep 2024 – 14 Sep 2026", "End Kontrak": "14 Sep 2026", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 48M",  "Anomali": False},
        {"Kode Ruang": "LG-01-04", "Brand/Tenant": "J.CO Donuts",     "SAP ID": "SAP: 10365",  "Legal ID": "Legal 4C-2024-006", "Real Onset": "01 Oct 2024 – 30 Sep 2026", "End Kontrak": "30 Sep 2026", "Status": "Active",        "Skema": "MG45",   "Conflict Info": "Rp 72M",  "Anomali": False},
        {"Kode Ruang": "FB-03-11", "Brand/Tenant": "Solaria",         "SAP ID": "SAP: 10376",  "Legal ID": "Legal 4C-2025-001", "Real Onset": "01 Jan 2025 – 31 Dec 2026", "End Kontrak": "31 Dec 2026", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 98M",  "Anomali": False},
        {"Kode Ruang": "RT-03-05", "Brand/Tenant": "Gramedia",        "SAP ID": "SAP: 10387",  "Legal ID": "Legal 4C-2025-002", "Real Onset": "01 Feb 2025 – 31 Jan 2027", "End Kontrak": "31 Jan 2027", "Status": "Active",        "Skema": "RS",     "Conflict Info": "Rp 85M",  "Anomali": False},
        {"Kode Ruang": "SV-02-09", "Brand/Tenant": "Timezone",        "SAP ID": "SAP: 10398",  "Legal ID": "Legal 4C-2025-003", "Real Onset": "01 Mar 2025 – 28 Feb 2027", "End Kontrak": "28 Feb 2027", "Status": "Active",        "Skema": "Rental", "Conflict Info": "Rp 115M", "Anomali": False},
        {"Kode Ruang": "LG-02-08", "Brand/Tenant": "Hypermart",       "SAP ID": "SAP: 10409",  "Legal ID": "Legal 4C-2025-004", "Real Onset": "15 Apr 2025 – 14 Apr 2027", "End Kontrak": "14 Apr 2027", "Status": "Expired",       "Skema": "MG45",   "Conflict Info": "Rp 140M", "Anomali": True},
    ]
    return pd.DataFrame(data)


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
_PAGE_CSS = """
<style>
/* ── Main Container Restrictor & Spacing (Matches Overview) ── */
body:has(.dv-page-marker) [data-testid="stMainBlockContainer"],
body:has(.dv-page-marker) [data-testid="stAppViewContainer"] .block-container,
body:has(.dv-page-marker) section.main > div,
body:has(.dv-page-marker) .main > div {
    padding-top: 0 !important;
    padding-bottom: 34px !important;
    margin-top: 0 !important;
}

body:has(.dv-page-marker) .block-container {
    max-width: 1440px !important;
    margin: 0 auto !important;
    padding: 0 32px 34px !important;
}

/* ── Collapse Spacing/Markers ── */
body:has(.dv-page-marker) div[data-testid="stElementContainer"]:has(.dv-page-marker),
body:has(.dv-page-marker) div[data-testid="stElementContainer"]:has(.dv-kpi-row-marker),
body:has(.dv-page-marker) div[data-testid="stElementContainer"]:has(.dv-sticky-header-marker),
body:has(.dv-page-marker) div[data-testid="stElementContainer"]:has(.dv-sticky-header-end) {
    display: none !important;
}

/* ── Section Card Container Style (Matches Overview) ── */
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker):not(
    :has(div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] .ed-card-marker)
) {
    position: relative !important;
    overflow: hidden !important;
    padding: 24px 32px !important;
    margin-top: 8px !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.90) !important;
    background: rgba(255, 255, 255, 0.56) !important;
    backdrop-filter: blur(26px) !important;
    -webkit-backdrop-filter: blur(26px) !important;
    box-shadow: 
        0 8px 32px rgba(99, 102, 241, 0.07) !important,
        0 2px 8px rgba(0, 0, 0, 0.025) !important,
        inset 0 1px 0 rgba(255, 255, 255, 1) !important,
        inset 0 -1px 0 rgba(99, 102, 241, 0.025) !important;
}

body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker):not(
    :has(div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] .ed-card-marker)
)
> div[data-testid="stElementContainer"]:has(.ed-card-marker) {
    display: none !important;
}

body:has(.dv-page-marker) .ed-section-title {
    margin: 0 !important;
    color: #0F172A !important;
    font-size: 15px !important;
    font-weight: 700 !important;
    font-family: 'Poppins', sans-serif !important;
}

body:has(.dv-page-marker) .ed-section-sub {
    margin: 3px 0 0 !important;
    color: #64748B !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    font-family: 'Poppins', sans-serif !important;
}

body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(.ed-card-marker),
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(.ed-card-marker) * {
    font-family: 'Poppins', sans-serif !important;
}

/* ── Fixed Header Override (Matches Overview) ── */
body:has(.dv-page-marker) .dv-fixed-header-active {
    position: fixed !important;
    top: 0 !important;
    right: 0 !important;
    z-index: 200 !important;
    background: #F8FAFC !important;
    border-bottom: 1px solid #E5E7EB !important;
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
}

body:has(.dv-page-marker) .dv-fixed-header-spacer {
    display: block !important;
    height: 93px !important;
    min-height: 93px !important;
    max-height: 93px !important;
    margin: 0 !important;
    padding: 0 !important;
    width: 100%;
    flex-shrink: 0;
}

body:has(.dv-page-marker) div[data-testid="stElementContainer"]:has(.dv-fixed-header-spacer) {
    margin: 0 !important;
    padding: 0 !important;
    height: 93px !important;
    min-height: 93px !important;
    max-height: 93px !important;
}

body:has(.dv-page-marker) div[data-testid="stElementContainer"]:has(iframe) {
    display: none !important;
}

body:has(.dv-page-marker) .dv-sticky-header-marker,
body:has(.dv-page-marker) .dv-sticky-header-end {
    display: none;
}

body:has(.dv-page-marker) [data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .dv-sticky-header-marker) {
    gap: 0 !important;
    height: 100% !important;
    justify-content: center !important;
}

body:has(.dv-page-marker) [data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .dv-sticky-header-marker) > div[data-testid="stElementContainer"] {
    margin: 0 !important;
    padding: 0 !important;
}

body:has(.dv-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.dv-sticky-header-marker) {
    height: 100% !important;
    display: flex !important;
    align-items: center !important;
}

body:has(.dv-page-marker) .dv-page-header {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    width: 100%;
    gap: 16px;
    height: 100%;
}

body:has(.dv-page-marker) .dv-page-header-left {
    display: flex; align-items: center; gap: 12px; min-width: 0;
}

body:has(.dv-page-marker) .dv-page-icon {
    width: 36px; height: 36px; flex: 0 0 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
    color: #ffffff; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.18);
}

body:has(.dv-page-marker) .dv-page-icon svg {
    width: 18px; height: 18px;
}

body:has(.dv-page-marker) .dv-page-header-copy {
    display: flex; flex-direction: column; justify-content: center; gap: 4px !important;
    min-height: 36px; min-width: 0;
}

body:has(.dv-page-marker) .dv-page-title-row {
    display: flex; align-items: center; gap: 10px; min-height: 0 !important;
    margin: 0 !important; padding: 0 !important;
}

body:has(.dv-page-marker) h2.dv-page-title {
    margin: 0 !important; padding: 0 !important;
    font-size: 18px; line-height: 1 !important; font-weight: 800;
    color: #0F172A; font-family: 'Poppins', sans-serif !important;
}

body:has(.dv-page-marker) p.dv-page-sub {
    margin: 0 !important; padding: 0 !important;
    color: #64748B; font-size: 12px; line-height: 1 !important;
    font-weight: 500; font-family: 'Poppins', sans-serif !important;
}

body:has(.dv-page-marker) .ap-top-actions {
    flex-shrink: 0;
}

/* ── KPI Row Spacing & Gap ── */
body:has(.dv-page-marker) div[data-testid="stHorizontalBlock"]:has(.dv-kpi) {
    margin-top: -28px !important;
    gap: 24px !important;
    flex-wrap: nowrap !important;
}
body:has(.dv-page-marker) div[data-testid="stHorizontalBlock"]:has(.dv-kpi) > div[data-testid="column"] {
    width: calc(25% - 18px) !important;
    min-width: calc(25% - 18px) !important;
    flex: 1 1 calc(25% - 18px) !important;
}

/* ── KPI CARDS ── */
.dv-kpi {
    background: #ffffff !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    box-shadow: 0 4px 20px rgba(15, 23, 42, 0.05) !important;
    transition: transform .2s ease, box-shadow .2s ease !important;
    position: relative !important;
    overflow: hidden !important;
    min-height: 90px !important;
    height: 100% !important;
    box-sizing: border-box !important;
}
.dv-kpi:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 25px rgba(99, 102, 241, 0.12) !important;
}
.dv-kpi-left {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    gap: 4px !important;
}
.dv-kpi-label {
    font-size: 11px !important;
    font-weight: 700 !important;
    color: #64748B !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
    margin: 0 !important;
    padding: 0 !important;
}
.dv-kpi-value {
    font-size: 26px !important;
    font-weight: 800 !important;
    color: #0F172A !important;
    line-height: 1 !important;
    margin: 0 !important;
    padding: 0 !important;
}
.dv-kpi-icon {
    width: 40px !important;
    height: 40px !important;
    border-radius: 50% !important;
    background: var(--icon-bg, rgba(99, 102, 241, 0.10)) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 18px !important;
    flex-shrink: 0 !important;
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
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 24px !important;
    border-top: 1px solid rgba(99,102,241,0.07);
    min-height: 56px !important;
    box-sizing: border-box !important;
}
.dv-footer-info {
    font-size: 12px !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    line-height: 1 !important;
}

/* ── PAGINATION OVERRIDES ── */
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) {
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"],
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] {
    position: absolute !important;
    right: 56px !important;
    bottom: 36px !important;
    z-index: 10 !important;
    display: flex !important;
    align-items: center !important;
    gap: 4px !important;
    width: auto !important;
    max-width: fit-content !important;
    margin: 0 !important;
}
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"],
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"],
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    width: auto !important;
    flex: 0 0 auto !important;
    min-width: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}
/* Previous & Next Buttons */
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child button,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child button,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child button,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child button,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child button,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child button,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child button,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child button {
    background: transparent !important;
    border: 1px solid transparent !important;
    color: #94a3b8 !important;
    font-weight: 500 !important;
    box-shadow: none !important;
    padding: 6px 12px !important;
    min-height: 32px !important;
    height: 32px !important;
    border-radius: 8px !important;
    font-size: 12px !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    font-family: 'Poppins', sans-serif !important;
}
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child button p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child button p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child button p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child button p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child button p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child button p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child button p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child button p {
    color: #94a3b8 !important;
    font-weight: 500 !important;
    margin: 0 !important;
    padding: 0 !important;
}
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child button:hover,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child button:hover,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child button:hover,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child button:hover,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child button:hover,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child button:hover,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child button:hover,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child button:hover {
    background: #f1f5f9 !important;
    color: #475569 !important;
}
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child button:hover p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child button:hover p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child button:hover p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child button:hover p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child button:hover p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child button:hover p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child button:hover p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child button:hover p {
    color: #475569 !important;
}
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child button:disabled,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child button:disabled,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:first-child button:disabled,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child button:disabled,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child button:disabled,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child button:disabled,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:last-child button:disabled,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:last-child button:disabled {
    opacity: 0.4 !important;
    cursor: not-allowed !important;
    background: transparent !important;
    border-color: transparent !important;
}
/* Inactive Page Number Buttons */
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:not(:first-child):not(:last-child) button,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:not(:first-child):not(:last-child) button,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:not(:first-child):not(:last-child) button,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:not(:first-child):not(:last-child) button {
    background: transparent !important;
    border: 1px solid #cbd5e1 !important;
    color: #475569 !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    padding: 6px 10px !important;
    min-height: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    box-shadow: none !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    transition: all 0.15s !important;
    font-family: 'Poppins', sans-serif !important;
}
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:not(:first-child):not(:last-child) button p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:not(:first-child):not(:last-child) button p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:not(:first-child):not(:last-child) button p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:not(:first-child):not(:last-child) button p {
    color: #475569 !important;
    font-weight: 600 !important;
    margin: 0 !important;
    padding: 0 !important;
}
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:not(:first-child):not(:last-child) button:hover,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:not(:first-child):not(:last-child) button:hover,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:not(:first-child):not(:last-child) button:hover,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:not(:first-child):not(:last-child) button:hover {
    background: #f8fafc !important;
    border-color: #cbd5e1 !important;
    color: #1e293b !important;
}
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:not(:first-child):not(:last-child) button:hover p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:not(:first-child):not(:last-child) button:hover p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:not(:first-child):not(:last-child) button:hover p,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:not(:first-child):not(:last-child) button:hover p {
    color: #1e293b !important;
}
/* Disable Focus Glow/Shadow Rings globally on pagination row */
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] button:focus,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] button:focus-visible,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] button:active,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] button:focus,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] button:focus-visible,
div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] button:active {
    box-shadow: none !important;
    outline: none !important;
}

/* ── ANOMALI BADGE ── */
.anomali-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #f59e0b;
    display: inline-block; margin-right: 5px;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.18);
}

/* ── Dropdown Filters Overrides ── */
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) [data-testid="stSelectbox"] {
    max-width: 280px !important;
    margin-left: auto !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) [data-testid="stSelectbox"] > div > div {
    height: 44px !important;
    min-height: 44px !important;
    border-radius: 22px !important;
    border: 1px solid #E2E8F0 !important;
    background: #ffffff !important;
    padding: 0 12px 0 16px !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04) !important;
    display: flex !important;
    align-items: center !important;
    box-sizing: border-box !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] {
    height: 44px !important;
    min-height: 44px !important;
    width: 100% !important;
    padding: 0 !important;
    margin: 0 !important;
    background: transparent !important;
    border: none !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    height: 44px !important;
    line-height: 44px !important;
    display: flex !important;
    align-items: center !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
    font-size: 13px !important;
    font-weight: 500 !important;
    color: #475569 !important;
    margin: 0 !important;
    font-family: 'Poppins', sans-serif !important;
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
    <div style="overflow-x:auto; margin-top: 16px; border: 1px solid rgba(99,102,241,0.08); border-radius: 12px; overflow: hidden;">
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
    st.markdown('<div class="dv-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)

    # ── Active Pagination Button Styling ──
    active_child = st.session_state.dv_page + 2
    st.markdown(f"""
    <style>
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child({active_child}) button,
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child({active_child}) button,
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child({active_child}) button,
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child({active_child}) button {{
        background: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #6366f1 !important;
        border-radius: 8px !important;
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.28) !important;
    }}
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child({active_child}) button p,
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child({active_child}) button p,
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child({active_child}) button p,
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child({active_child}) button p {{
        color: #1e293b !important;
        font-weight: 700 !important;
    }}
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child({active_child}) button:hover,
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child({active_child}) button:hover,
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child({active_child}) button:hover,
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child({active_child}) button:hover {{
        background: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #6366f1 !important;
        box-shadow: 0 0 10px rgba(99, 102, 241, 0.28) !important;
    }}
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child({active_child}) button:hover p,
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child({active_child}) button:hover p,
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="column"]:nth-child({active_child}) button:hover p,
    div[data-testid="stElementContainer"]:has(.dv-pagination-marker) ~ * [data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child({active_child}) button:hover p {{
        color: #1e293b !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="dv-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_dv_page_header_html(), unsafe_allow_html=True)
        st.markdown('<div class="dv-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="dv-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)

    # ── KPI Cards Row Marker ──
    st.markdown('<div class="dv-kpi-row-marker"></div>', unsafe_allow_html=True)

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

    # ── Main Content Section Header & Table Container ──
    main_section = st.container()
    with main_section:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        
        # ── Header Row ──
        dh1, df1, df2 = st.columns([5.2, 2.4, 2.4], vertical_alignment="center")
        with dh1:
            st.markdown(
                '<p class="ed-section-title">Verification Records</p>'
                '<p class="ed-section-sub">Daftar lengkap status validasi dan anomali data tenant</p>',
                unsafe_allow_html=True,
            )
        with df1:
            status_f = st.selectbox(
                "", ["Status ▾", "Active", "Expired Soon", "Expired"],
                label_visibility="collapsed", key="dv_fstatus")
        with df2:
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
            st.markdown('<div class="dv-pagination-marker"></div>', unsafe_allow_html=True)
            pg_cols = st.columns(n_pages + 2)
            with pg_cols[0]:
                if st.button("Previous", key="dv_pg_prev", disabled=(page == 0)):
                    st.session_state.dv_page = page - 1
                    st.rerun()
            for i in range(n_pages):
                with pg_cols[i + 1]:
                    lbl = str(i + 1)
                    if st.button(lbl, key=f"dv_pg_{i}"):
                        st.session_state.dv_page = i
                        st.rerun()
            with pg_cols[n_pages + 1]:
                if st.button("Next", key="dv_pg_next", disabled=(page >= n_pages - 1)):
                    st.session_state.dv_page = page + 1
                    st.rerun()

    # ── INFO BOX: Integrasi Import Manager ──
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
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

    _mount_dv_fixed_header()


# ── Standalone ──────────────────────────────
if __name__ == "__main__":
    st.set_page_config(page_title="Data Verification", layout="wide")
    try:
        with open("style.css") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass
    render_data_verification()
