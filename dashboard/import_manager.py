import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, datetime, timedelta
from textwrap import dedent
import time

from .shared_import import (
    KETENTUAN_RULES,
    get_shared_import_meta,
    store_shared_import,
    validate_import_upload,
    SHARED_DATA_KEY,
    SHARED_META_KEY,
    MAX_IMPORT_FILE_BYTES,
)
from .navigation import topnav_actions_html

IM_PAGE_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'width="18" height="18" fill="none" stroke="currentColor" '
    'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true">'
    '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
    '<polyline points="17 8 12 3 7 8"/>'
    '<line x1="12" y1="3" x2="12" y2="15"/>'
    '</svg>'
)


def _im_page_header_html():
    return dedent(f"""
    <div class="ov-page-header">
        <div class="ov-page-header-left">
            <div class="ov-page-icon" aria-hidden="true">{IM_PAGE_ICON_SVG}</div>
            <div class="ov-page-header-copy">
                <div class="ov-page-title-row">
                    <h2 class="ov-page-title">Import Manager</h2>
                </div>
                <p class="ov-page-sub">Unggah file performa komersial Anda untuk memperbarui analytics engine.</p>
            </div>
        </div>
        {topnav_actions_html()}
    </div>
    """).strip()


def _mount_im_fixed_header():
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
# DUMMY DATA
# ─────────────────────────────────────────────
PERIOD_ACTIVE = "April 2026"
DEADLINE      = date(2026, 4, 30)

SBU_LIST = ["Cikarang", "Bali", "Ginung", "Lombok", "Manado", "Kupang", "Jayapura", "Sorong"]

def _get_pic_history() -> pd.DataFrame:
    return pd.DataFrame([
        {"Periode": "Apr 2026", "Tanggal Upload": "26 Apr 2026 - 14:22", "Nama File": "tenant_registry_2026.xlsx", "Rows": 1734, "Status": "Approve"},
        {"Periode": "Mar 2026", "Tanggal Upload": "25 Mar 2026 - 09:10", "Nama File": "tenant_registry_mar.xlsx",  "Rows": 1698, "Status": "Approve"},
        {"Periode": "Feb 2026", "Tanggal Upload": "24 Feb 2026 - 11:45", "Nama File": "tenant_data_feb.csv",       "Rows": 1710, "Status": "Rejected"},
        {"Periode": "Jan 2026", "Tanggal Upload": "22 Jan 2026 - 08:30", "Nama File": "tenant_jan_2026.xlsx",      "Rows": 1650, "Status": "Approve"},
        {"Periode": "Des 2025", "Tanggal Upload": "20 Des 2025 - 16:00", "Nama File": "tenant_des_2025.xlsx",      "Rows": 1589, "Status": "Approve"},
    ])

def _get_admin_history() -> pd.DataFrame:
    return pd.DataFrame([
        {"PIC": "Cikarang",  "Periode": "Apr 2026", "File": "tenant_registry_2023.xlsx", "Rows": 1734, "Status": "Success",  "Anomali": 0},
        {"PIC": "Bali",      "Periode": "Apr 2026", "File": "sap_attributes_file.csv",   "Rows": 420,  "Status": "Failed",   "Anomali": 12},
        {"PIC": "Ginung",    "Periode": "Apr 2026", "File": "ginung_apr_2026.xlsx",       "Rows": 980,  "Status": "Pending",  "Anomali": 3},
        {"PIC": "Lombok",    "Periode": "Apr 2026", "File": "lombok_data.xlsx",           "Rows": 670,  "Status": "Approve",  "Anomali": 0},
        {"PIC": "Manado",    "Periode": "Mar 2026", "File": "manado_mar_2026.csv",        "Rows": 510,  "Status": "Approve",  "Anomali": 0},
        {"PIC": "Kupang",    "Periode": "Mar 2026", "File": "kupang_mar.xlsx",            "Rows": 340,  "Status": "Rejected", "Anomali": 8},
        {"PIC": "Jayapura",  "Periode": "Apr 2026", "File": "jayapura_apr.xlsx",          "Rows": 290,  "Status": "Pending",  "Anomali": 5},
        {"PIC": "Sorong",    "Periode": "Apr 2026", "File": "—",                          "Rows": 0,    "Status": "Pending",  "Anomali": 0},
    ])

UPLOAD_HISTORY_DATA = [
    {"period": "Dec 2024", "upload_date": "03 Jan 2025", "upload_time": "09:14 WIB", "uploader": "Rudi Darmawan",  "role": "Super Admin", "initials": "RD", "color": "#6366f1", "total_records": 1842, "tenants": 247, "file_size": "2.4 MB", "rs_total": "Rp 24.2B", "status": "Success"},
    {"period": "Nov 2024", "upload_date": "04 Dec 2024", "upload_time": "06:52 WIB", "uploader": "Sari Wulandari", "role": "Admin",       "initials": "SW", "color": "#f59e0b", "total_records": 1836, "tenants": 244, "file_size": "2.3 MB", "rs_total": "Rp 18.9B", "status": "Success"},
    {"period": "Oct 2024", "upload_date": "05 Nov 2024", "upload_time": "10:03 WIB", "uploader": "Rudi Darmawan",  "role": "Super Admin", "initials": "RD", "color": "#6366f1", "total_records": 1858, "tenants": 246, "file_size": "2.4 MB", "rs_total": "Rp 20.7B", "status": "Warning"},
    {"period": "Sep 2024", "upload_date": "03 Oct 2024", "upload_time": "09:44 WIB", "uploader": "Budi Santoso",   "role": "Admin",       "initials": "BS", "color": "#10b981", "total_records": 1792, "tenants": 243, "file_size": "2.2 MB", "rs_total": "Rp 19.2B", "status": "Success"},
    {"period": "Aug 2024", "upload_date": "04 Sep 2024", "upload_time": "11:21 WIB", "uploader": "Sari Wulandari", "role": "Admin",       "initials": "SW", "color": "#f59e0b", "total_records": 1801, "tenants": 245, "file_size": "2.3 MB", "rs_total": "Rp 18.4B", "status": "Success"},
    {"period": "Jul 2024", "upload_date": "05 Aug 2024", "upload_time": "08:33 WIB", "uploader": "Rudi Darmawan",  "role": "Super Admin", "initials": "RD", "color": "#6366f1", "total_records": 1776, "tenants": 241, "file_size": "2.2 MB", "rs_total": None,        "status": "Failed"},
    {"period": "Jun 2024", "upload_date": "03 Jul 2024", "upload_time": "09:58 WIB", "uploader": "Budi Santoso",   "role": "Admin",       "initials": "BS", "color": "#10b981", "total_records": 1748, "tenants": 239, "file_size": "2.1 MB", "rs_total": "Rp 17.1B", "status": "Success"},
    {"period": "May 2024", "upload_date": "04 Jun 2024", "upload_time": "14:05 WIB", "uploader": "Sari Wulandari", "role": "Admin",       "initials": "SW", "color": "#f59e0b", "total_records": 1715, "tenants": 237, "file_size": "2.1 MB", "rs_total": "Rp 16.8B", "status": "Success"},
    {"period": "Apr 2024", "upload_date": "03 May 2024", "upload_time": "10:30 WIB", "uploader": "Rudi Darmawan",  "role": "Super Admin", "initials": "RD", "color": "#6366f1", "total_records": 1690, "tenants": 235, "file_size": "2.0 MB", "rs_total": "Rp 16.2B", "status": "Success"},
    {"period": "Mar 2024", "upload_date": "02 Apr 2024", "upload_time": "08:15 WIB", "uploader": "Budi Santoso",   "role": "Admin",       "initials": "BS", "color": "#10b981", "total_records": 1665, "tenants": 233, "file_size": "2.0 MB", "rs_total": "Rp 15.9B", "status": "Warning"},
    {"period": "Feb 2024", "upload_date": "04 Mar 2024", "upload_time": "11:42 WIB", "uploader": "Sari Wulandari", "role": "Admin",       "initials": "SW", "color": "#f59e0b", "total_records": 1638, "tenants": 231, "file_size": "1.9 MB", "rs_total": "Rp 15.3B", "status": "Success"},
    {"period": "Jan 2024", "upload_date": "02 Feb 2024", "upload_time": "09:22 WIB", "uploader": "Rudi Darmawan",  "role": "Super Admin", "initials": "RD", "color": "#6366f1", "total_records": 1610, "tenants": 229, "file_size": "1.9 MB", "rs_total": "Rp 14.8B", "status": "Success"},
]

def _get_belum_submit():
    return ["Manado", "Kupang", "Sorong"]


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
_PAGE_CSS = """
<style>
/* Pull the workspace surface up to close the default Streamlit gap left
   after the fixed header's spacer (mirrors the same fix used elsewhere)
   — keeps it compact/close to the header. */
body:has(.im-page-marker) div[data-testid="stElementContainer"]:has(.im-manager-surface) {
    margin-top: -85px !important;
}

/* ── STEPPER ── */
.stepper-wrap {
    display: flex; align-items: center; gap: 0;
    margin-bottom: 24px; position: relative;
}
.step-item {
    display: flex; flex-direction: column; align-items: center; flex: 1;
    position: relative; z-index: 1;
}
.step-circle {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 800;
    transition: all 0.3s;
}
.step-circle.done   { background: linear-gradient(135deg,#059669,#10b981); color:#fff; box-shadow:0 4px 12px rgba(16,185,129,0.35); }
.step-circle.active { background: linear-gradient(135deg,#6366f1,#06b6d4); color:#fff; box-shadow:0 4px 12px rgba(99,102,241,0.40); }
.step-circle.idle   { background: rgba(148,163,184,0.18); color:#94a3b8; border:2px solid rgba(148,163,184,0.30); }
.step-label { font-size:10.5px; font-weight:700; margin-top:6px; text-align:center; line-height:1.3; }
.step-label.done   { color:#059669; }
.step-label.active { color:#4f46e5; }
.step-label.idle   { color:#94a3b8; }
.step-line {
    flex: 1; height: 2px; margin-top:-18px; position: relative; z-index: 0;
    border-radius: 999px;
}
.step-line.done { background: linear-gradient(90deg,#059669,#10b981); }
.step-line.idle { background: rgba(148,163,184,0.22); }

/* ── UPLOAD DROP ── */
.lc-dropzone {
    border: 2px dashed rgba(99,102,241,0.30);
    border-radius: 18px;
    background: rgba(255,255,255,0.62);
    backdrop-filter: blur(12px);
    padding: 40px 24px;
    text-align: center;
    transition: all 0.2s;
}
.lc-dropzone:hover { border-color: rgba(99,102,241,0.55); background: rgba(99,102,241,0.03); }
.lc-drop-icon { font-size: 40px; margin-bottom: 10px; }
.lc-drop-title { font-size: 15px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
.lc-drop-sub   { font-size: 11.5px; color: #94a3b8; margin-bottom: 16px; line-height: 1.6; }

/* ── FILE ITEM ── */
.lc-file-item {
    display: flex; align-items: center; gap: 14px;
    background: rgba(255,255,255,0.68);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.92);
    border-radius: 14px;
    padding: 14px 16px;
    margin-top: 10px;
    box-shadow: 0 3px 12px rgba(99,102,241,0.06);
}
.lc-file-icon {
    width: 40px; height: 40px; border-radius: 10px;
    background: rgba(16,185,129,0.12);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
}
.lc-file-name { font-size: 13px; font-weight: 700; color: #1e293b; }
.lc-file-sub  { font-size: 11px; color: #94a3b8; margin-top: 2px; }

/* ── PREVIEW CARD ── */
.preview-kpi-row { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.preview-kpi {
    flex: 1; min-width: 120px;
    background: rgba(255,255,255,0.68);
    border: 1px solid rgba(255,255,255,0.92);
    border-radius: 14px; padding: 14px 16px;
    box-shadow: 0 3px 12px rgba(99,102,241,0.05);
    text-align: center;
}
.preview-kpi-label { font-size:10px; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:5px; }
.preview-kpi-val   { font-size:20px; font-weight:800; color:#1e293b; }
.preview-kpi-val.err { color:#dc2626; }

/* ── PERIOD BANNER ── */
.period-banner {
    background: linear-gradient(135deg, rgba(99,102,241,0.09), rgba(6,182,212,0.07));
    border: 1px solid rgba(99,102,241,0.18);
    border-radius: 14px; padding: 14px 18px;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 18px; flex-wrap: wrap; gap: 8px;
}
.period-title { font-size:13px; font-weight:800; color:#4f46e5; }
.period-sub   { font-size:11.5px; color:#64748b; margin-top:2px; }
.period-badge {
    background: rgba(245,158,11,0.12); color:#d97706;
    border:1px solid rgba(245,158,11,0.26);
    padding:5px 14px; border-radius:999px;
    font-size:11.5px; font-weight:700;
}

/* ── KPI CARDS (Admin) ── */
.adm-kpi {
    background: rgba(255,255,255,0.62); backdrop-filter: blur(22px);
    border: 1px solid rgba(255,255,255,0.94); border-radius: 18px;
    padding: 18px 16px; position:relative; overflow:hidden;
    box-shadow: 0 6px 24px rgba(99,102,241,0.07), inset 0 1px 0 rgba(255,255,255,1);
    transition: transform .2s;
}
.adm-kpi:hover { transform: translateY(-2px); }
.adm-kpi::before {
    content:""; position:absolute; left:16px; right:16px; top:0; height:3px;
    border-radius:0 0 999px 999px;
    background: var(--accent, linear-gradient(135deg,#6366f1,#06b6d4)); opacity:.9;
}
.adm-kpi-label { font-size:9.5px; font-weight:800; color:#94a3b8; text-transform:uppercase; letter-spacing:.6px; margin-bottom:6px; }
.adm-kpi-val   { font-size:26px; font-weight:800; background:var(--accent,linear-gradient(135deg,#4f46e5,#0891b2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:4px; }
.adm-kpi-sub   { font-size:10.5px; color:#64748b; font-weight:600; }

/* ── REMINDER BANNER ── */
.reminder-banner {
    background: linear-gradient(135deg,rgba(245,158,11,0.09),rgba(251,146,60,0.07));
    border:1px solid rgba(245,158,11,0.26); border-radius:14px;
    padding:14px 18px; margin-bottom:14px;
    display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;
}
.reminder-txt { font-size:12.5px; color:#92400e; font-weight:500; line-height:1.5; }
.reminder-txt strong { color:#b45309; font-weight:800; }

/* ── TABLE ── */
.im-table { width:100%; border-collapse:collapse; }
.im-table thead tr { background:rgba(99,102,241,0.04); border-bottom:1px solid rgba(99,102,241,0.10); }
.im-table th { padding:11px 13px; text-align:left; font-size:10px; font-weight:800; color:#94a3b8; text-transform:uppercase; letter-spacing:.6px; white-space:nowrap; }
.im-table td { padding:12px 13px; font-size:12.5px; color:#334155; border-bottom:1px solid rgba(99,102,241,0.05); vertical-align:middle; }
.im-table tbody tr:hover { background:rgba(99,102,241,0.025); }
.im-table tbody tr:last-child td { border-bottom:none; }

/* ── STATUS BADGES ── */
.b-approve  { background:rgba(16,185,129,0.12); color:#059669; border:1px solid rgba(16,185,129,0.25); padding:3px 11px; border-radius:999px; font-size:11px; font-weight:700; }
.b-rejected { background:rgba(239,68,68,0.10);  color:#dc2626; border:1px solid rgba(239,68,68,0.22); padding:3px 11px; border-radius:999px; font-size:11px; font-weight:700; }
.b-pending  { background:rgba(245,158,11,0.12); color:#d97706; border:1px solid rgba(245,158,11,0.25); padding:3px 11px; border-radius:999px; font-size:11px; font-weight:700; }
.b-success  { background:rgba(16,185,129,0.12); color:#059669; border:1px solid rgba(16,185,129,0.25); padding:3px 11px; border-radius:999px; font-size:11px; font-weight:700; }
.b-failed   { background:rgba(239,68,68,0.10);  color:#dc2626; border:1px solid rgba(239,68,68,0.22); padding:3px 11px; border-radius:999px; font-size:11px; font-weight:700; }

/* ── ADMIN CONTROL CARDS ── */
.admin-ctrl {
    background:rgba(255,255,255,0.56); backdrop-filter:blur(20px);
    border:1px solid rgba(255,255,255,0.90); border-radius:16px;
    padding:16px 18px; margin-bottom:10px;
    box-shadow:0 4px 16px rgba(99,102,241,0.06);
}
.admin-ctrl-title { font-size:12.5px; font-weight:800; color:#1e293b; margin-bottom:3px; }
.admin-ctrl-sub   { font-size:11px; color:#94a3b8; margin-bottom:10px; }

/* ── SCHEME MAPPING ── */
.scheme-row {
    display:flex; align-items:center; gap:10px;
    background:rgba(255,255,255,0.56); border:1px solid rgba(255,255,255,0.88);
    border-radius:12px; padding:10px 14px; margin-bottom:8px;
    box-shadow:0 2px 8px rgba(99,102,241,0.04);
}
.scheme-col { flex:1; font-size:11.5px; font-weight:600; color:#475569; }
.scheme-arrow { color:#94a3b8; font-size:14px; flex-shrink:0; }
.scheme-master { flex:1; font-size:11.5px; color:#94a3b8; font-weight:500; }

.im-footer { display:flex; align-items:center; justify-content:space-between; padding:12px 16px; border-top:1px solid rgba(99,102,241,0.07); }
.im-footer-info { font-size:11.5px; color:#94a3b8; font-weight:500; }
</style>
"""

_REFINED_IMPORT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800;900&display=swap');

.stApp, .stApp * {
    font-family: 'Poppins', sans-serif !important;
}
.im-manager-surface {
    margin-top: -8px !important;
}
.im-page-head {
    display: grid;
    grid-template-columns: minmax(220px, 1.25fr) minmax(260px, 0.95fr) minmax(210px, 0.7fr);
    gap: 18px;
    align-items: center;
    margin-bottom: 10px;
}
.im-page-title {
    font-size: 19px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
}
.im-page-subtitle {
    margin-top: 2px;
    font-size: 11px;
    color: #64748b;
    font-weight: 500;
}
.im-userbar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
}
.im-bell {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: rgba(255,255,255,0.62);
    border: 1px solid rgba(255,255,255,0.94);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #4f46e5;
    font-size: 15px;
    font-weight: 900;
    box-shadow: 0 4px 18px rgba(99,102,241,0.08);
}
.im-user {
    display: flex;
    align-items: center;
    gap: 9px;
    min-width: 0;
}
.im-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 13px;
    font-weight: 800;
    background: linear-gradient(135deg,#6366f1,#06b6d4);
    box-shadow: 0 5px 16px rgba(99,102,241,0.28);
}
.im-user-name {
    font-size: 12.5px;
    font-weight: 800;
    color: #1e293b;
    line-height: 1.2;
}
.im-user-mail {
    font-size: 10.5px;
    color: #94a3b8;
    max-width: 170px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.im-workspace {
    display: grid;
    grid-template-columns: minmax(0, 1.72fr) minmax(300px, 0.78fr);
    gap: 22px;
    align-items: start;
}
.im-panel {
    background: rgba(255,255,255,0.56);
    backdrop-filter: blur(26px);
    -webkit-backdrop-filter: blur(26px);
    border: 1px solid rgba(255,255,255,0.90);
    border-radius: 18px;
    box-shadow:
        0 8px 32px rgba(99,102,241,0.07),
        0 2px 8px rgba(0,0,0,0.025),
        inset 0 1px 0 rgba(255,255,255,1);
}
.im-upload-shell {
    padding: 18px 18px 16px;
}
.im-upload-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 12px;
}
.im-section-title {
    font-size: 13px;
    font-weight: 800;
    color: #1e293b;
}
.im-section-sub {
    margin-top: 3px;
    font-size: 11px;
    color: #94a3b8;
}
.im-period-chip {
    flex-shrink: 0;
    padding: 6px 12px;
    border-radius: 999px;
    background: linear-gradient(135deg,rgba(99,102,241,0.13),rgba(6,182,212,0.10));
    border: 1px solid rgba(99,102,241,0.20);
    color: #4f46e5;
    font-size: 11px;
    font-weight: 800;
}

/* Custom Drag & Drop visual styles */
.im-dropzone-wrapper {
    position: relative;
    width: 100%;
    margin-bottom: 14px;
}
.im-dropzone-visual {
    border: 2px dashed rgba(99, 102, 241, 0.25);
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.72), rgba(245, 243, 255, 0.45));
    padding: 40px 24px;
    text-align: center;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.04);
    height: 254px !important;
    box-sizing: border-box !important;
}
.im-dropzone-wrapper:hover .im-dropzone-visual {
    border-color: rgba(99, 102, 241, 0.6);
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.8), rgba(245, 243, 255, 0.6));
    box-shadow: 0 12px 40px rgba(99, 102, 241, 0.08);
}
.im-dropzone-icon-box {
    width: 64px;
    height: 64px;
    border-radius: 18px;
    background: #f3f0ff;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.08);
}
.im-dropzone-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #a78bfa;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(167, 139, 250, 0.35);
    font-size: 18px;
    font-weight: 700;
}
.im-dropzone-title {
    font-size: 16.5px;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 4px;
}
.im-dropzone-subtitle {
    font-size: 12.5px;
    color: #64748b;
    margin-bottom: 22px;
}
.im-dropzone-browse {
    color: #6366f1;
    font-weight: 800;
    text-decoration: none;
    cursor: pointer;
}
.im-dropzone-browse:hover {
    text-decoration: underline;
}
.im-dropzone-badges {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}
.im-dropzone-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    background: #f5f3ff;
    border: 1px solid rgba(99, 102, 241, 0.18);
    border-radius: 999px;
    color: #6366f1;
    font-size: 10.5px;
    font-weight: 700;
}
.badge-icon {
    stroke: #6366f1;
    stroke-width: 2.2;
}

/* Transparent Sibling and Class Overlay Uploader */
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) {
    position: relative !important;
    margin-top: -268px !important;
    height: 254px !important;
    z-index: 1000 !important;
    cursor: pointer !important;
}
.im-refined-uploader {
    opacity: 0 !important;
    cursor: pointer !important;
    width: 100% !important;
    height: 100% !important;
}
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) *,
.im-refined-uploader * {
    cursor: pointer !important;
    width: 100% !important;
    height: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
}
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploadDropzone"],
.im-refined-uploader [data-testid="stFileUploadDropzone"],
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzone"],
.im-refined-uploader [data-testid="stFileUploaderDropzone"] {
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    background: transparent !important;
}


/* Success State styling */
.im-success-visual {
    border: 2px solid rgba(16, 185, 129, 0.2);
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.72), rgba(240, 253, 244, 0.45));
    padding: 40px 24px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(16, 185, 129, 0.04);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 14px;
    animation: cardPopIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}
.im-success-icon-box {
    width: 64px;
    height: 64px;
    border-radius: 18px;
    background: #e6fcf5;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(16, 185, 129, 0.08);
}
.im-success-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #10b981;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.35);
    font-size: 20px;
    font-weight: bold;
}
.im-success-title {
    font-size: 19px;
    font-weight: 850;
    color: #059669;
    margin-bottom: 4px;
}
.im-success-subtitle {
    font-size: 12.5px;
    color: #64748b;
    margin-bottom: 24px;
}

/* Progress bar container and animations */
.im-progress-bar-container {
    width: 100%;
    max-width: 460px;
    height: 10px;
    background: #f1f5f9;
    border-radius: 999px;
    overflow: hidden;
    margin-bottom: 24px;
}
@keyframes progressBarWidth {
    0% { width: 0%; }
    100% { width: 100%; }
}
@keyframes progressBarColor {
    0% { background-color: #8b5cf6; } /* purple */
    45% { background-color: #8b5cf6; }
    75% { background-color: #eab308; } /* yellow */
    100% { background-color: #10b981; } /* green */
}
.im-progress-bar-fill {
    height: 100%;
    border-radius: 999px;
    width: 0%;
    animation: progressBarWidth 2.5s cubic-bezier(0.4, 0, 0.2, 1) forwards,
               progressBarColor 2.5s cubic-bezier(0.4, 0, 0.2, 1) forwards;
}

/* Success details and buttons slide up/fade in */
@keyframes successDetailsFadeIn {
    0% {
        opacity: 0;
        transform: translateY(16px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}
@keyframes cardPopIn {
    0% {
        opacity: 0;
        transform: scale(0.96) translateY(12px);
    }
    100% {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}
@keyframes failureDetailsSlideUp {
    0% {
        opacity: 0;
        transform: translateY(12px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}
.im-success-details {
    width: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    animation: successDetailsFadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 2.5s both;
}

/* Stats Cards container and cards */
.im-stats-row {
    display: flex;
    justify-content: center;
    gap: 12px;
    width: 100%;
    margin-bottom: 24px;
    flex-wrap: wrap;
}
.im-stat-card {
    flex: 1;
    min-width: 100px;
    border-radius: 16px;
    padding: 14px 10px;
    text-align: center;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.03);
    transition: transform 0.2s;
}
.im-stat-card:hover {
    transform: translateY(-2px);
}
/* Purple Stat Card: Records */
.stat-records {
    background: #f5f3ff;
    border: 1px solid #ddd6fe;
}
.stat-records .stat-value {
    color: #6366f1;
}
/* Green Stat Card: Valid */
.stat-valid {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
}
.stat-valid .stat-value {
    color: #10b981;
}
/* Yellow Stat Card: Warnings */
.stat-warnings {
    background: #fefbeb;
    border: 1px solid #fef08a;
}
.stat-warnings .stat-value {
    color: #d97706;
}
/* Green Teal Stat Card: Score */
.stat-score {
    background: #f0fdfa;
    border: 1px solid #ccfbf1;
}
.stat-score .stat-value {
    color: #14b8a6;
}

.stat-value {
    font-size: 19px;
    font-weight: 800;
    margin-bottom: 4px;
    line-height: 1.2;
}
.stat-label {
    font-size: 11px;
    color: #64748b;
    font-weight: 600;
}

/* Custom Streamlit Buttons override inside success buttons container */
.im-success-buttons-container {
    width: 100%;
    max-width: 380px;
    margin: 0 auto;
    animation: successDetailsFadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 2.5s both;
}
.im-success-buttons-container [data-testid="stButton"] button {
    width: 100% !important;
    height: 42px !important;
    border-radius: 12px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
}
/* Style for Col 1 button (Upload Another) */
.im-success-buttons-container [data-testid="column"]:first-child button {
    background: #ffffff !important;
    color: #4f46e5 !important;
    border: 1px solid rgba(99, 102, 241, 0.25) !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.05) !important;
}
.im-success-buttons-container [data-testid="column"]:first-child button:hover {
    background: #f5f3ff !important;
    border-color: rgba(99, 102, 241, 0.4) !important;
    transform: translateY(-1px) !important;
}
/* Style for Col 2 button (View Data) */
.im-success-buttons-container [data-testid="column"]:last-child button {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 16px rgba(99, 102, 241, 0.3) !important;
}
.im-success-buttons-container [data-testid="column"]:last-child button:hover {
    background: linear-gradient(135deg, #4f46e5, #4338ca) !important;
    box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45) !important;
    transform: translateY(-1px) !important;
}

/* Failure State styling */
.im-failure-visual {
    border: 2px solid rgba(239, 68, 68, 0.2);
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.72), rgba(254, 242, 242, 0.45));
    padding: 40px 24px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(239, 68, 68, 0.04);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 14px;
    animation: cardPopIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}
.im-failure-icon-box {
    width: 64px;
    height: 64px;
    border-radius: 18px;
    background: #fef2f2;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(239, 68, 68, 0.08);
}
.im-failure-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #ef4444;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.35);
    font-size: 20px;
    font-weight: bold;
}
.im-failure-title {
    font-size: 19px;
    font-weight: 850;
    color: #dc2626;
    margin-bottom: 4px;
}
.im-failure-subtitle {
    font-size: 12.5px;
    color: #64748b;
    margin-bottom: 24px;
}
.im-failure-details {
    width: 100%;
    max-width: 460px;
    background: rgba(255, 255, 255, 0.68);
    border: 1px solid rgba(239, 68, 68, 0.15);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 24px;
    text-align: left;
    animation: failureDetailsSlideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.15s both;
}
.im-failure-detail-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-size: 12.5px;
    color: #475569;
}
.im-failure-detail-item:last-child {
    margin-bottom: 0;
}

.im-side-stack {
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.im-side-control {
    padding: 14px 14px 13px;
}
.im-side-control-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(130px, 1fr);
    gap: 10px;
    align-items: end;
}
.im-control-title {
    font-size: 12px;
    color: #64748b;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.im-map-card {
    padding: 0;
    overflow: hidden;
}
.im-card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 15px 16px 11px;
    border-bottom: 1px solid rgba(99,102,241,0.08);
}
.im-auto-badge {
    padding: 5px 10px;
    border-radius: 999px;
    color: #047857;
    background: rgba(16,185,129,0.13);
    border: 1px solid rgba(16,185,129,0.20);
    font-size: 10px;
    font-weight: 850;
    letter-spacing: 0.4px;
    white-space: nowrap;
    box-shadow: none;
}
.im-map-body {
    padding: 12px 16px 15px;
    max-height: 238px;
    overflow-y: auto;
}
.im-map-row {
    display: block;
    margin-bottom: 9px;
}
.im-map-box {
    min-height: 66px;
    border-radius: 12px;
    background: rgba(255,255,255,0.68);
    border: 1px solid rgba(255,255,255,0.92);
    box-shadow: 0 2px 10px rgba(99,102,241,0.05);
    padding: 10px 12px;
    border-left: 5px solid rgba(99,102,241,0.62);
}
.im-map-label {
    font-size: 10px;
    font-weight: 800;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: 4px;
}
.im-map-value {
    font-size: 12px;
    font-weight: 800;
    color: #1e293b;
    line-height: 1.35;
}
.im-map-arrow {
    color: #64748b;
    font-size: 15px;
    font-weight: 900;
    line-height: 1;
    margin: 2px 0;
}
.im-execute-wrap {
    padding: 0 16px 15px;
}
.im-ketentuan-card {
    padding: 0;
    overflow: hidden;
}
.im-ketentuan-head {
    padding: 15px 16px 11px;
    border-bottom: 1px solid rgba(99,102,241,0.08);
}
.im-ketentuan-body {
    padding: 14px 16px 18px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.im-ketentuan-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    font-size: 12px;
    font-weight: 600;
    color: #334155;
    line-height: 1.45;
}
.im-ketentuan-check {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #059669;
    font-size: 11px;
    font-weight: 900;
    background: rgba(16,185,129,0.13);
    border: 1px solid rgba(16,185,129,0.22);
    margin-top: 1px;
}
.im-ketentuan-fail {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #dc2626;
    font-size: 11px;
    font-weight: 900;
    background: rgba(239,68,68,0.10);
    border: 1px solid rgba(239,68,68,0.22);
    margin-top: 1px;
}
.im-ketentuan-item.is-fail span:last-child {
    color: #64748b;
}
.im-ketentuan-item.is-pass span:last-child {
    color: #334155;
}
.im-info-banner {
    margin-top: 14px;
    padding: 12px 14px;
    border-radius: 12px;
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.18);
    color: #4338ca;
    font-size: 11.5px;
    font-weight: 650;
    line-height: 1.5;
}
.im-history {
    margin-top: 18px;
    padding: 0;
    overflow: hidden;
}
.im-history-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 20px 24px 16px;
    border-bottom: 1px solid rgba(99,102,241,0.08);
}
.im-history-head-left .im-section-title {
    font-size: 15px;
    font-weight: 850;
}
.im-history-head-left .im-section-sub {
    margin-top: 2px;
    font-size: 11.5px;
}
.im-history-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}
.im-btn-refresh, .im-btn-export {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
}
.im-btn-refresh, .im-btn-export {
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(99,102,241,0.15);
    color: #4f46e5;
}
.im-btn-refresh:hover, .im-btn-export:hover {
    background: #f5f3ff;
    border-color: rgba(99,102,241,0.3);
    transform: none;
    box-shadow: none;
}
/* History Table Row Design */
.im-hist-table {
    width: 100%;
    border-collapse: collapse;
}
.im-hist-table thead tr {
    background: rgba(248,250,252,0.8);
    border-bottom: 1px solid #f1f5f9;
}
.im-hist-table th {
    padding: 12px 16px;
    text-align: left;
    font-size: 10px;
    font-weight: 800;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    white-space: nowrap;
}
.im-hist-table td {
    padding: 16px 16px;
    font-size: 12.5px;
    color: #334155;
    border-bottom: 1px solid #f8fafc;
    vertical-align: middle;
}
.im-hist-table tbody tr {
    transition: background 0.15s;
}
.im-hist-table tbody tr:hover {
    background: rgba(99,102,241,0.02);
}
.im-hist-table tbody tr:last-child td {
    border-bottom: none;
}
/* Period cell with colored dot */
.im-period-cell {
    display: flex;
    align-items: center;
    gap: 10px;
}
.im-period-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.im-period-dot.dot-success { background: #10b981; }
.im-period-dot.dot-warning { background: #f59e0b; }
.im-period-dot.dot-failed  { background: #ef4444; }
.im-period-name {
    font-size: 13px;
    font-weight: 800;
    color: #1e293b;
}
/* Upload date with sub-time */
.im-date-cell {
    line-height: 1.3;
}
.im-date-main {
    font-size: 13px;
    font-weight: 700;
    color: #1e293b;
}
.im-date-time {
    font-size: 10.5px;
    color: #94a3b8;
    font-weight: 500;
}
/* Uploader cell with avatar */
.im-uploader-cell {
    display: flex;
    align-items: center;
    gap: 10px;
}
.im-uploader-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 11px;
    font-weight: 800;
    flex-shrink: 0;
    box-shadow: 0 3px 8px rgba(0,0,0,0.12);
}
.im-uploader-name {
    font-size: 12.5px;
    font-weight: 700;
    color: #1e293b;
    line-height: 1.2;
}
.im-uploader-role {
    font-size: 10.5px;
    color: #94a3b8;
    font-weight: 500;
}
/* Records cell */
.im-records-val {
    font-size: 16px;
    font-weight: 850;
    color: #1e293b;
    line-height: 1.2;
}
.im-records-sub {
    font-size: 10px;
    color: #94a3b8;
    font-weight: 600;
    text-transform: lowercase;
}
/* Tenants link */
.im-tenants-link {
    font-size: 13px;
    font-weight: 700;
    color: #6366f1;
    cursor: pointer;
}
.im-tenants-link:hover {
    text-decoration: underline;
}
/* File size */
.im-filesize {
    font-size: 12.5px;
    color: #64748b;
    font-weight: 600;
}
/* RS Total */
.im-rs-total {
    font-size: 12.5px;
    font-weight: 700;
    color: #1e293b;
}
.im-rs-empty {
    font-size: 12.5px;
    color: #cbd5e1;
    font-weight: 500;
}
/* Status badges with dot */
.im-status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 11.5px;
    font-weight: 700;
    white-space: nowrap;
}
.im-status-badge .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
}
.im-status-success {
    background: rgba(16,185,129,0.10);
    color: #059669;
    border: 1px solid rgba(16,185,129,0.20);
}
.im-status-success .status-dot { background: #10b981; }
.im-status-warning {
    background: rgba(245,158,11,0.10);
    color: #d97706;
    border: 1px solid rgba(245,158,11,0.20);
}
.im-status-warning .status-dot { background: #f59e0b; }
.im-status-failed {
    background: rgba(239,68,68,0.08);
    color: #dc2626;
    border: 1px solid rgba(239,68,68,0.18);
}
.im-status-failed .status-dot { background: #ef4444; }
/* Action buttons */
.im-action-btns {
    display: flex;
    align-items: center;
    gap: 6px;
}
.im-action-btn {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #f1f5f9;
    background: #fff;
    color: #94a3b8;
    cursor: pointer;
    transition: all 0.15s;
    font-size: 13px;
}
.im-action-btn:hover {
    background: #f5f3ff;
    color: #6366f1;
    border-color: rgba(99,102,241,0.2);
}
.im-action-btn.btn-delete:hover {
    background: #fef2f2;
    color: #ef4444;
    border-color: rgba(239,68,68,0.2);
}
/* Pagination */
.im-pagination-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 24px;
    border-top: 1px solid #f1f5f9;
}
.im-pagination-info {
    font-size: 12px;
    color: #94a3b8;
    font-weight: 500;
}
.im-pagination-btns {
    display: flex;
    align-items: center;
    gap: 4px;
}
.im-pg-btn {
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid #e2e8f0;
    background: #fff;
    color: #64748b;
    cursor: pointer;
    transition: all 0.15s;
}
.im-pg-btn:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
}
.im-pg-btn.active {
    background: #fff;
    color: #1e293b;
    border-color: #6366f1;
    box-shadow: 0 0 10px rgba(99,102,241,0.28);
}
.im-pg-btn.active:hover {
    background: #fff;
    color: #1e293b;
    border-color: #6366f1;
}
.im-pg-btn.disabled {
    opacity: 0.4;
    cursor: not-allowed;
}
.im-refresh {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: rgba(255,255,255,0.62);
    border: 1px solid rgba(255,255,255,0.92);
    color: #4f46e5;
    font-size: 13px;
    font-weight: 900;
}
.im-table thead tr {
    background: linear-gradient(135deg,rgba(99,102,241,0.08),rgba(6,182,212,0.05));
}
.im-table th {
    color: #64748b;
    font-size: 10.5px;
}
.im-table td {
    padding: 12px 20px;
    font-size: 12px;
}
[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.68) !important;
    color: #4f46e5 !important;
    border: 1px solid rgba(99,102,241,0.20) !important;
    border-radius: 12px !important;
    font-size: 12.5px !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.08) !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: rgba(99,102,241,0.36) !important;
    box-shadow: 0 7px 22px rgba(99,102,241,0.13) !important;
}
@media (max-width: 1050px) {
    .im-page-head {
        grid-template-columns: 1fr;
    }
    .im-userbar {
        justify-content: flex-start;
    }
    .im-workspace {
        grid-template-columns: 1fr;
    }
}
@media (max-width: 640px) {
    .im-page-title {
        font-size: 19px;
    }
    .im-upload-heading,
    .im-card-head,
    .im-history-head {
        align-items: flex-start;
        flex-direction: column;
    }
    .im-map-row {
        grid-template-columns: 1fr;
    }
    .im-map-arrow {
        transform: rotate(90deg);
    }
}
</style>
"""

_NEW_DESIGN_CSS = """
<style>
/* ── Page title ── */
.im-page-title-v2 {
    font-size: 20px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.2;
}
.im-page-sub-v2 {
    margin-top: 4px;
    font-size: 12px;
    color: #64748B;
    font-weight: 400;
}
.im-page-sub-v2 a, .im-page-sub-v2 span {
    color: #4F46E5;
    font-weight: 600;
    text-decoration: none;
}

/* ── Upload card: three-section visual card ──
   Heading (HTML card-top) + drop zone (stFileUploadDropzone) + hint row
   all appear as one card via matching borders and zero-margin CSS. */
.im-upload-card-v2 {
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-bottom: none;
    border-radius: 14px 14px 0 0;
    padding: 18px 20px 14px;
}
.im-upload-title-v2 {
    font-size: 15px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.2;
}
.im-upload-sub-v2 {
    font-size: 12px;
    color: #94A3B8;
    margin-top: 3px;
}
/* ── File uploader: MINIMAL overrides only — do not touch layout props ──
   Only section cleanup; card appearance is handled by HTML im-upload-card-v2.
   The drop zone (stFileUploadDropzone) IS the visual dashed inner box. */
[data-testid="stFileUploader"] > section {
    gap: 0 !important;
    padding: 0 !important;
}
[data-testid="stFileUploader"] > section > small { display: none !important; }

/* ── Drop zone: lavender dashed box, flex column, cloud icon via ::before ── */
[data-testid="stFileUploadDropzone"] {
    border: 1.5px dashed #C4C9F4 !important;
    border-radius: 0 0 12px 12px !important;
    background: #F5F3FF !important;
    padding: 36px 20px 24px !important;
    min-height: 200px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0 !important;
    cursor: pointer !important;
    transition: border-color 0.18s, background 0.18s !important;
    box-shadow: none !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #818CF8 !important;
    background: #EEF2FF !important;
}
/* Cloud upload icon as first flex item */
[data-testid="stFileUploadDropzone"]::before {
    content: '' !important;
    display: block !important;
    width: 52px !important;
    height: 52px !important;
    border-radius: 13px !important;
    background-color: #EEF2FF !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%234F46E5' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='16 16 12 12 8 16'%3E%3C/polyline%3E%3Cline x1='12' y1='12' x2='12' y2='21'%3E%3C/line%3E%3Cpath d='M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3'%3E%3C/path%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-size: 22px 22px !important;
    flex-shrink: 0 !important;
    margin-bottom: 14px !important;
}
/* Instruction text container */
[data-testid="stFileUploadDropzoneInstructions"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    text-align: center !important;
    margin-bottom: 18px !important;
}
[data-testid="stFileUploadDropzoneInstructions"] > div {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 5px !important;
}
[data-testid="stFileUploadDropzoneInstructions"] svg { display: none !important; }
[data-testid="stFileUploadDropzoneInstructions"] > div > span {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #1E293B !important;
    font-family: 'Poppins', sans-serif !important;
}
[data-testid="stFileUploadDropzoneInstructions"] small,
[data-testid="stFileUploadDropzoneInstructions"] > div > small {
    font-size: 12px !important;
    color: #94A3B8 !important;
    font-weight: 400 !important;
}
/* Browse Files button inside the drop zone */
[data-testid="stFileUploadDropzone"] button {
    background: #4F46E5 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    min-height: 40px !important;
    padding: 0 32px !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 4px 14px rgba(79,70,229,0.28) !important;
    width: auto !important;
}
[data-testid="stFileUploadDropzone"] button:hover { background: #4338CA !important; }

/* Hint row below — negative margin-top closes the Streamlit ~1rem vertical gap
   so it appears flush against the drop zone bottom border. */
.im-upload-hint {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-top: 1px solid #F0EEFF;
    border-radius: 0 0 14px 14px;
    padding: 11px 18px 13px;
    margin-top: -1rem;
    position: relative;
    z-index: 2;
}
.im-upload-hint-icon {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    color: #ffffff;
    font-size: 9px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    letter-spacing: 0.3px;
}
.im-upload-hint-text {
    font-size: 12px;
    color: #64748B;
    line-height: 1.5;
}

/* ── Ketentuan Import (white card) ── */
.im-ketentuan-card {
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 22px 22px 18px;
    box-shadow: 0 1px 4px rgba(15,23,42,0.05);
}
.im-ketentuan-icon-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
}
.im-ketentuan-icon-box {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    background: #EEF2FF;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}
.im-ketentuan-title {
    font-size: 13.5px;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: 0.2px;
}
.im-ketentuan-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 12px;
}
.im-ketentuan-check {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #059669;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    color: #ffffff;
    font-size: 10px;
    font-weight: 900;
    margin-top: 1px;
}
.im-ketentuan-text {
    font-size: 12px;
    color: #64748B;
    line-height: 1.55;
    font-weight: 500;
}
.im-ketentuan-text strong { color: #1E293B; font-weight: 700; }
.im-ketentuan-footer {
    margin-top: 18px;
    padding-top: 14px;
    border-top: 1px solid #F1F5F9;
}
.im-ketentuan-footer-label {
    font-size: 9px;
    font-weight: 800;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin-bottom: 3px;
}
.im-ketentuan-footer-val {
    font-size: 11.5px;
    font-weight: 700;
    color: #475569;
}

/* ── Riwayat Import table card ── */
.im-riwayat-card {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(15,23,42,0.05);
    overflow: hidden;
    margin-top: 20px;
}
.im-riwayat-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    padding: 18px 20px 14px;
    border-bottom: 1px solid #F1F5F9;
}
.im-riwayat-title-v2 {
    font-size: 14px;
    font-weight: 800;
    color: #0F172A;
}
.im-riwayat-search-box {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 7px 12px;
    border-radius: 8px;
    border: 1px solid #E2E8F0;
    background: #F8FAFC;
    min-width: 220px;
}
.im-riwayat-search-icon { color: #94A3B8; font-size: 13px; }
.im-riwayat-btns { display: flex; gap: 7px; flex-shrink: 0; }
.im-riwayat-btn-v2 {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 7px 14px; border-radius: 8px;
    border: 1px solid #E2E8F0; background: #ffffff;
    font-size: 12px; font-weight: 600; color: #475569;
    cursor: pointer; white-space: nowrap;
}
.im-riwayat-btn-export {
    background: #4F46E5; color: #ffffff; border-color: #4F46E5;
}
/* table */
.im-table-v2 { width:100%; border-collapse:collapse; }
.im-table-v2 thead tr { background:#F8FAFC; }
.im-table-v2 th { padding:11px 16px; text-align:left; font-size:10.5px; font-weight:800; color:#64748B; text-transform:uppercase; letter-spacing:.5px; white-space:nowrap; border-bottom:1px solid #F1F5F9; }
.im-table-v2 td { padding:13px 16px; font-size:12.5px; color:#334155; border-bottom:1px solid #F8FAFC; vertical-align:middle; }
.im-table-v2 tbody tr:hover { background:#FAFBFF; }
.im-table-v2 tbody tr:last-child td { border-bottom:none; }
.im-file-ext-icon {
    display: inline-flex; align-items: center; gap: 8px;
}
.im-file-badge {
    width: 28px; height: 28px; border-radius: 6px;
    background: #DCFCE7; color: #16A34A;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 9.5px; font-weight: 800; flex-shrink: 0;
}
.im-file-badge.xls { background: #D1FAE5; color: #059669; }
.im-file-badge.csv { background: #DBEAFE; color: #2563EB; }
.im-file-badge.err { background: #FEE2E2; color: #DC2626; }
/* status badges v2 */
.bv2-sukses  { background:#DCFCE7; color:#16A34A; padding:4px 12px; border-radius:999px; font-size:11.5px; font-weight:700; display:inline-block; }
.bv2-gagal   { background:#FEE2E2; color:#DC2626; padding:4px 12px; border-radius:999px; font-size:11.5px; font-weight:700; display:inline-block; }
.bv2-pending { background:#FEF9C3; color:#92400E; padding:4px 12px; border-radius:999px; font-size:11.5px; font-weight:700; display:inline-block; }
/* eye action icon */
.im-eye-btn {
    width: 30px; height: 30px; border-radius: 8px;
    background: #F1F5F9; display: inline-flex;
    align-items: center; justify-content: center;
    color: #64748B; font-size: 14px; cursor: pointer;
}
/* pagination */
.im-pagination-row {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 13px 20px; border-top: 1px solid #F1F5F9;
    flex-wrap: wrap; gap: 8px;
}
.im-pagination-info { font-size: 12px; color: #94A3B8; font-weight: 500; }
.im-page-btns { display: flex; gap: 4px; align-items: center; }
.im-page-btn-v2 {
    min-width: 30px; height: 30px; padding: 0 6px;
    border-radius: 6px; border: 1px solid #E2E8F0;
    background: #ffffff; font-size: 12px; font-weight: 600;
    color: #64748B; display: inline-flex; align-items: center;
    justify-content: center; cursor: pointer;
}
.im-page-btn-v2.active { background: #4F46E5; color: #ffffff; border-color: #4F46E5; }
.im-page-btn-v2.dots { border: none; background: transparent; color: #94A3B8; }

/* ── Bottom info cards ── */
.im-info-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 18px;
}
.im-info-card-v2 {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(15,23,42,0.04);
    padding: 18px 20px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
}
.im-info-icon-v2 {
    width: 40px; height: 40px; border-radius: 10px;
    background: #F1F5F9; display: flex;
    align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
.im-info-title-v2 { font-size: 13px; font-weight: 800; color: #1E293B; margin-bottom: 5px; }
.im-info-text-v2 { font-size: 11.5px; color: #64748B; line-height: 1.55; font-weight: 400; }
</style>
"""


# ─────────────────────────────────────────────
# INIT STATE
# ─────────────────────────────────────────────
def _init_state():
    defaults = {
        "im_view":        "PIC",       # "PIC" | "Admin"
        "im_step":        1,           # 1-4
        "im_file":        None,
        "im_preview_ok":  False,
        "im_submitted":   False,
        "im_confirmed":   False,
        "im_sbu":         SBU_LIST[0],
        "im_deadline":    str(DEADLINE),
        "im_validation":  {key: False for key, _ in KETENTUAN_RULES},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _status_badge(s):
    s = str(s)
    cls = {"Approve":"b-approve","Rejected":"b-rejected","Pending":"b-pending",
           "Success":"b-success","Failed":"b-failed"}.get(s, "b-pending")
    return f'<span class="{cls}">{s}</span>'

def _stepper(current: int):
    steps = [
        ("1", "Template"),
        ("2", "Upload"),
        ("3", "Preview"),
        ("4", "Submit"),
    ]
    html = '<div class="stepper-wrap">'
    for i, (num, label) in enumerate(steps):
        idx = i + 1
        state = "done" if idx < current else ("active" if idx == current else "idle")
        icon  = "✓" if state == "done" else num
        html += f'<div class="step-item"><div class="step-circle {state}">{icon}</div><div class="step-label {state}">{label}</div></div>'
        if i < len(steps) - 1:
            line_state = "done" if idx < current else "idle"
            html += f'<div class="step-line {line_state}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PIC VIEW
# ─────────────────────────────────────────────
def _render_pic_view():
    # Period Banner
    sisa = (DEADLINE - date.today()).days
    st.markdown(f"""
    <div class="period-banner">
        <div>
            <div class="period-title">📅 Periode {PERIOD_ACTIVE} — Belum Ada Submission</div>
            <div class="period-sub">Deadline upload: {DEADLINE.strftime("%d %B %Y")} · Hanya 1 kali submission per periode</div>
        </div>
        <span class="period-badge">⏳ {sisa} hari lagi</span>
    </div>""", unsafe_allow_html=True)

    # Stepper
    _stepper(st.session_state.im_step)

    col_up, col_scheme = st.columns([5, 4])

    # ── LEFT: Upload Area ──
    with col_up:
        st.markdown('<div class="nad-card" style="padding:20px 22px;">', unsafe_allow_html=True)

        step = st.session_state.im_step

        # STEP 1 — Download Template
        if step == 1:
            st.markdown('<div class="nad-card-title">📥 Step 1 — Download Template</div>', unsafe_allow_html=True)
            st.markdown('<div class="nad-card-sub">Unduh template Excel standar sebagai panduan pengisian data pendapatan.</div>', unsafe_allow_html=True)
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

            template_data = "Kode Ruang,Brand,Omzet,Periode\nFB-01-01,Example Brand,10000000,April 2026\n"
            c1, c2 = st.columns(2)
            with c1:
                st.download_button("⬇️ Download Template Excel", data=template_data,
                                   file_name="template_pendapatan.csv", mime="text/csv",
                                   use_container_width=True, key="im_dl_tmpl")
            with c2:
                if st.button("Lanjut ke Upload →", use_container_width=True, key="im_step1_next"):
                    st.session_state.im_step = 2
                    st.rerun()

        # STEP 2 — Upload
        elif step == 2:
            st.markdown('<div class="nad-card-title">📤 Step 2 — Upload File</div>', unsafe_allow_html=True)
            st.markdown('<div class="nad-card-sub">Unggah file Excel yang sudah diisi. Maks. 20MB.</div>', unsafe_allow_html=True)

            st.markdown("""
            <div class="lc-dropzone">
                <div class="lc-drop-icon">☁️</div>
                <div class="lc-drop-title">Drag & Drop Excel File</div>
                <div class="lc-drop-sub">Maximum file size 20MB. Only .xlsx and .xls supported.</div>
            </div>""", unsafe_allow_html=True)

            uploaded = st.file_uploader("", type=["xlsx", "xls"],
                                        label_visibility="collapsed", key="im_uploader")

            if uploaded:
                validation = validate_import_upload(uploaded)
                st.session_state.im_validation = validation
                st.session_state.im_import_ready = all(validation.values())
                st.session_state.im_file = uploaded.name
                size_kb = round(uploaded.size / 1024)

                if not st.session_state.im_import_ready:
                    st.error("File belum memenuhi semua ketentuan import.")
                else:
                    try:
                        df_imported, missing_columns = store_shared_import(uploaded, st.session_state.im_sbu)
                        st.session_state.im_preview_rows = len(df_imported)
                        st.session_state.im_preview_total_omzet = float(df_imported["real_omzet"].sum()) if "real_omzet" in df_imported.columns else 0
                        st.session_state.im_preview_errors = len(missing_columns)
                        if missing_columns:
                            st.warning("File terbaca, tetapi ada kolom yang belum lengkap: " + ", ".join(missing_columns))
                        else:
                            st.success("File berhasil terbaca dan siap diverifikasi.")
                    except Exception as exc:
                        st.session_state.im_import_ready = False
                        st.error(f"Gagal membaca file: {exc}")

                status_label = "ready" if st.session_state.im_import_ready else "invalid"
                st.markdown(f"""
                <div class="lc-file-item">
                    <div class="lc-file-icon">📊</div>
                    <div style="flex:1;">
                        <div class="lc-file-name">{uploaded.name}</div>
                        <div class="lc-file-sub">{size_kb} KB · {status_label}</div>
                    </div>
                    <span style="font-size:18px;color:#dc2626;cursor:pointer;">🗑️</span>
                </div>""", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("← Kembali", use_container_width=True, key="im_step2_back"):
                    st.session_state.im_step = 1; st.rerun()
            with c2:
                if st.button("Preview Data →", use_container_width=True, key="im_step2_next",
                             disabled=((uploaded is None and st.session_state.im_file is None) or not st.session_state.get("im_import_ready", False))):
                    st.session_state.im_step = 3; st.rerun()

        # STEP 3 — Preview
        elif step == 3:
            st.markdown('<div class="nad-card-title">🔍 Step 3 — Preview Data</div>', unsafe_allow_html=True)
            st.markdown('<div class="nad-card-sub">Periksa ringkasan data sebelum melanjutkan ke submit.</div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="preview-kpi-row">
                <div class="preview-kpi"><div class="preview-kpi-label">Total Rows</div><div class="preview-kpi-val">1,734</div></div>
                <div class="preview-kpi"><div class="preview-kpi-label">Total Omzet</div><div class="preview-kpi-val">Rp 21.4B</div></div>
                <div class="preview-kpi"><div class="preview-kpi-label">Periode</div><div class="preview-kpi-val" style="font-size:15px;">Apr 2026</div></div>
                <div class="preview-kpi"><div class="preview-kpi-label">Errors</div><div class="preview-kpi-val err">0</div></div>
            </div>""", unsafe_allow_html=True)

            confirmed = st.checkbox("✅ Saya menyatakan bahwa data yang diunggah adalah benar dan sesuai.", key="im_confirm_check")
            st.session_state.im_preview_ok = confirmed

            c1, c2 = st.columns(2)
            with c1:
                if st.button("← Kembali", use_container_width=True, key="im_step3_back"):
                    st.session_state.im_step = 2; st.rerun()
            with c2:
                if st.button("Lanjut Submit →", use_container_width=True, key="im_step3_next",
                             disabled=not confirmed):
                    st.session_state.im_step = 4; st.rerun()

        # STEP 4 — Submit
        elif step == 4:
            st.markdown('<div class="nad-card-title">🚀 Step 4 — Submit Data</div>', unsafe_allow_html=True)
            st.markdown('<div class="nad-card-sub">Konfirmasi final. Data akan dikunci dan dikirim ke Admin untuk ditinjau.</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div style="background:rgba(99,102,241,0.06);border:1px solid rgba(99,102,241,0.18);border-radius:12px;padding:14px 16px;margin-bottom:14px;">
                <div style="font-size:12px;color:#475569;font-weight:600;">📁 File: <strong style="color:#1e293b;">{st.session_state.im_file or 'tenant_data.xlsx'}</strong></div>
                <div style="font-size:12px;color:#475569;font-weight:600;margin-top:6px;">📅 Periode: <strong style="color:#1e293b;">{PERIOD_ACTIVE}</strong></div>
                <div style="font-size:12px;color:#475569;font-weight:600;margin-top:6px;">🏢 SBU: <strong style="color:#1e293b;">{st.session_state.im_sbu}</strong></div>
            </div>""", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("← Kembali", use_container_width=True, key="im_step4_back"):
                    st.session_state.im_step = 3; st.rerun()
            with c2:
                if st.button("🚀 SUBMIT", use_container_width=True, key="im_step4_submit"):
                    with st.spinner("Mengirim data..."):
                        time.sleep(1)
                    st.session_state.im_submitted = True
                    st.success("✅ Data berhasil dikirim! Menunggu review Admin.")
                    st.balloons()

        st.markdown('</div>', unsafe_allow_html=True)

    # ── RIGHT: Ketentuan Import ──
    with col_scheme:
        _render_ketentuan_import(st.session_state.get("im_validation"))

    # ── Import History (PIC) ──
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="nad-card" style="padding:0;overflow:hidden;">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;justify-content:space-between;padding:16px 18px 10px;">'
                '<div class="nad-card-title">Import History</div>'
                '<span style="font-size:18px;color:#94a3b8;cursor:pointer;">🔄</span></div>', unsafe_allow_html=True)

    df_h = _get_pic_history()
    rows_html = ""
    for _, r in df_h.iterrows():
        rows_html += f"""<tr>
          <td>{r['Periode']}</td><td style="color:#64748b;">{r['Tanggal Upload']}</td>
          <td style="font-weight:600;">{r['Nama File']}</td>
          <td style="font-weight:700;">{r['Rows']:,}</td>
          <td>{_status_badge(r['Status'])}</td>
        </tr>"""

    st.markdown(f"""
    <div style="overflow-x:auto;">
      <table class="im-table">
        <thead><tr>
          <th>Periode</th><th>Tanggal Upload</th><th>Nama File</th><th>Rows</th><th>Status</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ADMIN VIEW
# ─────────────────────────────────────────────
def _render_admin_view():
    df_all = _get_admin_history()
    belum  = _get_belum_submit()

    # KPI
    total_pic  = len(SBU_LIST)
    sudah      = len(df_all[df_all["Status"].isin(["Success","Approve","Pending"])])
    blm        = len(belum)
    perlu_tl   = int((df_all["Anomali"] > 0).sum())

    k1, k2, k3, k4 = st.columns(4)
    kpi_cfg = [
        (k1, "linear-gradient(135deg,#4f46e5,#6366f1)", "PIC Terdaftar",         str(total_pic), "Total PIC aktif"),
        (k2, "linear-gradient(135deg,#059669,#10b981)", "Sudah Submit",           str(sudah),     "Periode ini"),
        (k3, "linear-gradient(135deg,#d97706,#f59e0b)", "Belum Submit",           str(blm),       "Perlu reminder"),
        (k4, "linear-gradient(135deg,#dc2626,#f43f5e)", "Perlu Tindak Lanjut",   str(perlu_tl),  "Anomali / konflik"),
    ]
    for col, accent, label, val, sub in kpi_cfg:
        with col:
            st.markdown(f"""
            <div class="adm-kpi" style="--accent:{accent};">
                <div class="adm-kpi-label">{label}</div>
                <div class="adm-kpi-val">{val}</div>
                <div class="adm-kpi-sub">{sub}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Reminder Banner
    if belum:
        belum_str = ", ".join(belum)
        st.markdown(f"""
        <div class="reminder-banner">
            <div class="reminder-txt">
                ⚠️ <strong>{len(belum)} PIC belum submit</strong> untuk periode {PERIOD_ACTIVE}:
                <span style="color:#92400e;font-weight:700;"> {belum_str}</span>
            </div>
        </div>""", unsafe_allow_html=True)
        if st.button("📣 Kirim Reminder ke Semua PIC Belum Submit", key="im_remind"):
            st.toast(f"Reminder dikirim ke: {belum_str}", icon="📣")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Filter Row
    fc1, fc2, fsp = st.columns([2, 2, 6])
    with fc1:
        f_pic = st.selectbox("", ["Semua PIC"] + SBU_LIST, label_visibility="collapsed", key="adm_fpic")
    with fc2:
        f_status = st.selectbox("", ["Semua Status","Success","Approve","Pending","Rejected","Failed"],
                                label_visibility="collapsed", key="adm_fstatus")
    # Apply filter
    df = df_all.copy()
    if f_pic    != "Semua PIC":    df = df[df["PIC"] == f_pic]
    if f_status != "Semua Status": df = df[df["Status"] == f_status]
    df = df.reset_index(drop=True)

    # Table
    rows_html = ""
    for _, r in df.iterrows():
        anomali_html = f'<span style="color:#dc2626;font-weight:700;">{r["Anomali"]}</span>' if r["Anomali"] > 0 else '<span style="color:#94a3b8;">0</span>'
        rows_html += f"""<tr>
          <td style="font-weight:700;color:#4f46e5;">{r['PIC']}</td>
          <td>{r['Periode']}</td>
          <td style="font-size:12px;">{r['File']}</td>
          <td style="font-weight:700;">{r['Rows']:,}</td>
          <td>{_status_badge(r['Status'])}</td>
          <td>{anomali_html}</td>
          <td>
            <span title="Review"  style="cursor:pointer;font-size:14px;margin-right:4px;">🔍</span>
            <span title="Approve" style="cursor:pointer;font-size:14px;margin-right:4px;">✅</span>
            <span title="Reject"  style="cursor:pointer;font-size:14px;margin-right:4px;">❌</span>
            <span title="Lock"    style="cursor:pointer;font-size:14px;margin-right:4px;">🔒</span>
            <span title="Unlock"  style="cursor:pointer;font-size:14px;">🔓</span>
          </td>
        </tr>"""

    st.markdown('<div class="nad-card" style="padding:0;overflow:hidden;">', unsafe_allow_html=True)
    st.markdown('<div style="display:flex;align-items:center;justify-content:space-between;padding:16px 18px 8px;">'
                '<div class="nad-card-title">Semua Import History</div>'
                '<span style="font-size:18px;color:#94a3b8;cursor:pointer;">🔄</span></div>',
                unsafe_allow_html=True)
    st.markdown(f"""
    <div style="overflow-x:auto;">
      <table class="im-table">
        <thead><tr>
          <th>PIC</th><th>Periode</th><th>File</th><th>Rows</th><th>Status</th><th>Anomali</th><th>Aksi</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    <div class="im-footer"><span class="im-footer-info">Showing {len(df)} entries</span></div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Admin Controls ──
    st.markdown('<div class="nad-card-title" style="margin-bottom:10px;">⚙️ Kontrol Admin</div>', unsafe_allow_html=True)
    ac1, ac2 = st.columns(2)

    with ac1:
        # Buka Kunci
        st.markdown('<div class="admin-ctrl">', unsafe_allow_html=True)
        st.markdown('<div class="admin-ctrl-title">🔓 Buka Kunci Upload PIC</div>', unsafe_allow_html=True)
        st.markdown('<div class="admin-ctrl-sub">Izinkan PIC upload ulang setelah periode dikunci.</div>', unsafe_allow_html=True)
        unlock_pic    = st.selectbox("PIC", SBU_LIST, key="adm_unlock_pic", label_visibility="collapsed")
        unlock_reason = st.text_input("Alasan pembukaan kunci", placeholder="Masukkan alasan...", key="adm_unlock_reason")
        if st.button("🔓 Buka Kunci", use_container_width=True, key="adm_do_unlock"):
            if unlock_reason:
                st.success(f"✅ Upload PIC {unlock_pic} berhasil dibuka.")
            else:
                st.error("Wajib mengisi alasan.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Atur Deadline
        st.markdown('<div class="admin-ctrl">', unsafe_allow_html=True)
        st.markdown('<div class="admin-ctrl-title">📅 Atur Batas Waktu Upload</div>', unsafe_allow_html=True)
        st.markdown('<div class="admin-ctrl-sub">Perpanjang atau persingkat deadline submission PIC.</div>', unsafe_allow_html=True)
        new_deadline = st.date_input("Deadline baru", value=DEADLINE, key="adm_deadline")
        if st.button("💾 Simpan Deadline", use_container_width=True, key="adm_save_deadline"):
            st.success(f"✅ Deadline diperbarui ke {new_deadline.strftime('%d %b %Y')}.")
        st.markdown('</div>', unsafe_allow_html=True)

    with ac2:
        # Hapus Import
        st.markdown('<div class="admin-ctrl">', unsafe_allow_html=True)
        st.markdown('<div class="admin-ctrl-title">🗑️ Hapus Import</div>', unsafe_allow_html=True)
        st.markdown('<div class="admin-ctrl-sub">Hapus permanen data import bermasalah dari sistem.</div>', unsafe_allow_html=True)
        del_pic    = st.selectbox("PIC", SBU_LIST, key="adm_del_pic", label_visibility="collapsed")
        del_period = st.selectbox("Periode", ["Apr 2026","Mar 2026","Feb 2026"], key="adm_del_period", label_visibility="collapsed")
        if st.button("🗑️ Hapus Data", use_container_width=True, key="adm_do_delete"):
            st.warning(f"⚠️ Data import {del_pic} periode {del_period} telah dihapus.")
        st.markdown('</div>', unsafe_allow_html=True)

        # Approve & Publish Massal
        st.markdown('<div class="admin-ctrl">', unsafe_allow_html=True)
        st.markdown('<div class="admin-ctrl-title">✅ Approve & Publish Massal</div>', unsafe_allow_html=True)
        st.markdown('<div class="admin-ctrl-sub">Publikasikan semua data valid ke dashboard produksi.</div>', unsafe_allow_html=True)
        st.markdown(f'<div style="font-size:12px;color:#64748b;margin-bottom:10px;">Periode aktif: <strong style="color:#4f46e5;">{PERIOD_ACTIVE}</strong></div>', unsafe_allow_html=True)
        if st.button("🚀 Approve & Publish Semua", use_container_width=True, key="adm_publish_all"):
            with st.spinner("Mempublikasikan..."):
                time.sleep(1)
            st.success("✅ Semua data valid berhasil dipublikasikan!")
            st.balloons()
        st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def render_import_manager():
    _init_state()
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)

    # ── Header ──
    h1, h2 = st.columns([5, 5])
    with h1:
        st.markdown("""
        <div style="padding-top:0;">
            <div style="font-size:19px;font-weight:800;color:#0f172a;line-height:1.2;">Data Import Manager</div>
            <div style="font-size:11px;color:#94a3b8;margin-top:2px;">
                Kelola unggahan data pendapatan tenant dari seluruh PIC terminal/SBU.
            </div>
        </div>""", unsafe_allow_html=True)
    with h2:
        initial = st.session_state.get("user_name","Admin")[0].upper()
        uname   = st.session_state.get("user_name","Admin")
        uemail  = st.session_state.get("user_email","angkasapura@mail.com")
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:flex-end;gap:12px;padding-top:0;">
            <div style="width:34px;height:34px;border-radius:50%;background:rgba(255,255,255,0.72);
                border:1px solid rgba(255,255,255,0.95);backdrop-filter:blur(10px);
                display:flex;align-items:center;justify-content:center;font-size:16px;">🔔</div>
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="background:linear-gradient(135deg,#6366f1,#ec4899);border-radius:50%;
                    width:34px;height:34px;display:flex;align-items:center;justify-content:center;
                    color:#fff;font-size:13px;font-weight:700;">{initial}</div>
                <div>
                    <div style="font-size:12px;font-weight:700;color:#1e293b;">{uname}</div>
                    <div style="font-size:10px;color:#94a3b8;">{uemail}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="nad-top-divider"></div>', unsafe_allow_html=True)

    # ── View Toggle ──
    role = st.session_state.get("user_role","Admin")
    t1, t2, _ = st.columns([1.2, 1.2, 7.6])
    with t1:
        if st.button("👤 Tampilan PIC", use_container_width=True, key="im_view_pic"):
            st.session_state.im_view = "PIC"; st.rerun()
    with t2:
        if st.button("🛡️ Tampilan Admin", use_container_width=True, key="im_view_admin"):
            st.session_state.im_view = "Admin"; st.rerun()

    view_indicator = "👤 **PIC View**" if st.session_state.im_view == "PIC" else "🛡️ **Admin View**"
    st.markdown(f'<div style="font-size:11px;color:#94a3b8;margin:-6px 0 14px 2px;">Mode aktif: {view_indicator}</div>',
                unsafe_allow_html=True)

    if st.session_state.im_view == "PIC":
        _render_pic_view()
    else:
        _render_admin_view()


# ── Standalone ──
def _render_import_page_header():
    initial = st.session_state.get("user_name", "Admin")[0].upper()
    uname = st.session_state.get("user_name", "Admin")
    uemail = st.session_state.get("user_email", "angkasapura@mail.com")

    h_title, h_user = st.columns([7.6, 2.4])
    with h_title:
        st.markdown("""
        <div>
            <div class="im-page-title">Data Import Manager</div>
            <div class="im-page-subtitle">Upload dan kelola file data dari tim integrasi.</div>
        </div>
        """, unsafe_allow_html=True)
    with h_user:
        st.markdown(f"""
        <div class="im-userbar">
            <div class="im-bell">!</div>
            <div class="im-user">
                <div class="im-avatar">{initial}</div>
                <div style="min-width:0;">
                    <div class="im-user-name">{uname}</div>
                    <div class="im-user-mail">{uemail}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="nad-top-divider"></div>', unsafe_allow_html=True)


def _render_selected_file(uploaded, validation: dict[str, bool] | None = None):
    validation = validation or {key: False for key, _ in KETENTUAN_RULES}
    all_valid = uploaded is not None and all(validation.values())

    if uploaded:
        size_kb = max(1, round(uploaded.size / 1024))
        st.markdown(f"""
        <div class="im-file-card">
            <div class="im-file-icon">XLS</div>
            <div style="min-width:0;">
                <div class="im-file-name">{uploaded.name}</div>
                <div class="im-file-meta">{size_kb:,} KB</div>
            </div>
            <div class="im-delete">x</div>
        </div>
        """, unsafe_allow_html=True)

        if not all_valid:
            failed = [label for key, label in KETENTUAN_RULES if not validation.get(key, False)]
            st.error(
                "File belum memenuhi ketentuan import. Perbaiki item yang ditandai ✗ di panel kanan."
                + (f" ({failed[0]})" if failed else "")
            )
            return

        current_sbu = st.session_state.get("im_sbu", SBU_LIST[0])
        try:
            df_imported, missing_columns = store_shared_import(uploaded, current_sbu)
            st.session_state.im_file = uploaded.name
            st.session_state.im_import_ready = len(missing_columns) == 0
        except Exception as exc:
            st.session_state.im_import_ready = False
            st.error(f"Gagal membaca file: {exc}")
            return

        if missing_columns:
            st.warning(
                "File sudah tersimpan sebagai sumber import, tetapi belum bisa dipakai penuh di Overview. "
                f"Kolom yang kurang: {', '.join(missing_columns)}"
            )
        else:
            st.success("File berhasil dijadikan sumber data pusat untuk semua dashboard.")
            st.dataframe(df_imported.head(10), use_container_width=True, hide_index=True)
        return

    last_file = st.session_state.get("im_file")
    if last_file:
        meta = get_shared_import_meta()
        rows = meta.get("rows", 0)
        uploaded_at = meta.get("uploaded_at", "sesi ini")
        st.markdown(f"""
        <div class="im-file-card">
            <div class="im-file-icon">XLS</div>
            <div style="min-width:0;">
                <div class="im-file-name">{last_file}</div>
                <div class="im-file-meta">{rows:,} rows - tersimpan pada {uploaded_at}</div>
            </div>
            <div class="im-delete">x</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="im-file-card is-empty">
            <div class="im-file-icon">XLS</div>
            <div style="min-width:0;">
                <div class="im-file-name">Belum ada file dipilih</div>
                <div class="im-file-meta">Gunakan tombol Browse Files untuk memilih file Excel (.xlsx / .xls).</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_ketentuan_import(validation: dict[str, bool] | None = None):
    validation = validation or {key: False for key, _ in KETENTUAN_RULES}

    items_html = ""
    for key, label in KETENTUAN_RULES:
        passed = validation.get(key, False)
        icon_class = "im-ketentuan-check" if passed else "im-ketentuan-fail"
        item_class = "is-pass" if passed else "is-fail"
        icon = "✓" if passed else "✗"
        items_html += dedent(f"""
        <div class="im-ketentuan-item {item_class}">
            <span class="{icon_class}">{icon}</span>
            <span>{label}</span>
        </div>
        """).strip()

    st.markdown(dedent(f"""
    <div class="im-panel im-ketentuan-card">
        <div class="im-ketentuan-head">
            <div class="im-section-title">Ketentuan Import</div>
        </div>
        <div class="im-ketentuan-body">{items_html}</div>
    </div>
    """).strip(), unsafe_allow_html=True)


def _render_import_history_refined():
    data = UPLOAD_HISTORY_DATA
    per_page = 7
    total = len(data)
    total_pages = max(1, (total + per_page - 1) // per_page)

    if "im_hist_page" not in st.session_state:
        st.session_state.im_hist_page = 1

    # Render a hidden input to sync page state from HTML pagination clicks
    st.markdown('<div class="im-page-trigger-container" style="display:none;">', unsafe_allow_html=True)
    page_input = st.text_input(
        "Page Sync Trigger",
        value=str(st.session_state.im_hist_page),
        key="im_page_trigger_input"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if page_input and page_input.isdigit():
        new_page = int(page_input)
        if new_page != st.session_state.im_hist_page:
            st.session_state.im_hist_page = new_page
            st.rerun()

    page = st.session_state.im_hist_page
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total)
    page_data = data[start_idx:end_idx]

    # Build status badge helper
    def _hist_status(status):
        s = status.lower()
        if s == "success":
            return '<span class="im-status-badge im-status-success"><span class="status-dot"></span>Success</span>'
        elif s == "warning":
            return '<span class="im-status-badge im-status-warning"><span class="status-dot"></span>Warning</span>'
        elif s == "failed":
            return '<span class="im-status-badge im-status-failed"><span class="status-dot"></span>Failed</span>'
        return '<span class="im-status-badge im-status-success"><span class="status-dot"></span>' + status + '</span>'

    # Build dot class
    def _dot_class(status):
        s = status.lower()
        if s == "success": return "dot-success"
        if s == "warning": return "dot-warning"
        if s == "failed": return "dot-failed"
        return "dot-success"

    # Build rows
    rows_html = ""
    for r in page_data:
        rs_html = f'<span class="im-rs-total">{r["rs_total"]}</span>' if r["rs_total"] else '<span class="im-rs-empty">—</span>'
        rows_html += (
            '<tr>'
            '<td>'
            f'<div class="im-period-cell">'
            f'<span class="im-period-dot {_dot_class(r["status"])}"></span>'
            f'<span class="im-period-name">{r["period"]}</span>'
            '</div>'
            '</td>'
            '<td>'
            f'<div class="im-date-cell">'
            f'<div class="im-date-main">{r["upload_date"]}</div>'
            f'<div class="im-date-time">{r["upload_time"]}</div>'
            '</div>'
            '</td>'
            '<td>'
            f'<div class="im-uploader-cell">'
            f'<div class="im-uploader-avatar" style="background:{r["color"]};">{r["initials"]}</div>'
            '<div>'
            f'<div class="im-uploader-name">{r["uploader"]}</div>'
            f'<div class="im-uploader-role">{r["role"]}</div>'
            '</div>'
            '</div>'
            '</td>'
            '<td>'
            f'<div class="im-records-val">{r["total_records"]:,}</div>'
            '<div class="im-records-sub">rows</div>'
            '</td>'
            f'<td><span class="im-tenants-link">{r["tenants"]}</span></td>'
            f'<td><span class="im-filesize">{r["file_size"]}</span></td>'
            f'<td>{rs_html}</td>'
            f'<td>{_hist_status(r["status"])}</td>'
            '<td>'
            '<div class="im-action-btns">'
            '<div class="im-action-btn" title="View">👁</div>'
            '<div class="im-action-btn" title="Download">⬇</div>'
            '<div class="im-action-btn" title="Reload">↻</div>'
            '<div class="im-action-btn btn-delete" title="Delete">🗑</div>'
            '</div>'
            '</td>'
            '</tr>'
        )

    if not rows_html:
        rows_html = '<tr><td colspan="9" style="text-align:center;color:#94a3b8;padding:30px;">Belum ada data import yang tersedia.</td></tr>'

    # Pagination buttons
    pg_html = ''
    pg_html += f'<span class="im-pg-btn {"disabled" if page <= 1 else ""}" data-page="{page - 1}">Previous</span>'
    for p in range(1, total_pages + 1):
        pg_html += f'<span class="im-pg-btn {"active" if p == page else ""}" data-page="{p}">{p}</span>'
    pg_html += f'<span class="im-pg-btn {"disabled" if page >= total_pages else ""}" data-page="{page + 1}">Next</span>'

    history_html = (
        '<div class="im-panel im-history">'
        '<div class="im-history-head">'
        '<div class="im-history-head-left">'
        '<div class="im-section-title">Upload History</div>'
        '<div class="im-section-sub">All import sessions — most recent first</div>'
        '</div>'
        '<div class="im-history-actions">'
        '<span class="im-btn-refresh">Refresh</span>'
        '<span class="im-btn-export">Export Log</span>'
        '</div>'
        '</div>'
        '<div style="overflow-x:auto;">'
        '<table class="im-hist-table">'
        '<thead><tr>'
        '<th>Period</th>'
        '<th>Upload Date</th>'
        '<th>Uploaded By</th>'
        '<th>Total Records</th>'
        '<th>Tenants</th>'
        '<th>File Size</th>'
        '<th>RS Total</th>'
        '<th>Status</th>'
        '<th>Actions</th>'
        '</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        '</table>'
        '</div>'
        '<div class="im-pagination-wrap">'
        f'<span class="im-pagination-info">Showing {start_idx + 1}-{end_idx} of {total} upload sessions</span>'
        f'<div class="im-pagination-btns">{pg_html}</div>'
        '</div>'
        '</div>'
    )
    st.markdown(history_html, unsafe_allow_html=True)


def _render_info_cards():
    st.markdown(dedent("""
    <div class="im-info-row">
        <div class="im-info-card-v2">
            <div class="im-info-icon-v2">🛡️</div>
            <div>
                <div class="im-info-title-v2">Enkripsi Data</div>
                <div class="im-info-text-v2">
                    Semua dokumen yang diunggah diproses dan disimpan dalam lingkungan
                    sandbox yang aman dan terenkripsi.
                </div>
            </div>
        </div>
        <div class="im-info-card-v2">
            <div class="im-info-icon-v2">✨</div>
            <div>
                <div class="im-info-title-v2">AI Auto-Cleaning</div>
                <div class="im-info-text-v2">
                    Engine kami secara otomatis memperbaiki masalah format umum dan
                    mengidentifikasi potensi outlier pada data yang diunggah.
                </div>
            </div>
        </div>
    </div>
    """).strip(), unsafe_allow_html=True)


def _render_new_workspace():
    if "uploader_version" not in st.session_state:
        st.session_state.uploader_version = 0
    uploader_key = f"im_uploader_refined_{st.session_state.uploader_version}"

    left, right = st.columns([6, 4], gap="medium")

    # ── LEFT: three-section upload card ──
    # Section 1: HTML heading card  (border-bottom: none, top-only radius)
    # Section 2: native file uploader styled as lavender dashed drop zone
    # Section 3: hint row (negative margin-top closes the Streamlit flex gap)
    with left:
        st.markdown("""
        <div class="im-panel im-upload-shell">
            <div class="im-upload-heading">
                <div>
                    <div class="im-section-title">Upload Data File</div>
                    <div class="im-section-sub">Format yang didukung: .xlsx dan .xls (Excel).</div>
                </div>
                <div class="im-period-chip">April 2026</div>
            </div>
        """, unsafe_allow_html=True)

        # Let's get the uploaded file from st.file_uploader
        # If we use a key that depends on version to reset it
        # We check if file is uploaded or not
        uploaded = st.session_state.get(uploader_key)

        if not uploaded:
            st.markdown(f"""
            <div class="im-dropzone-wrapper">
                <div class="im-dropzone-visual">
                    <div class="im-dropzone-icon-box">
                        <div class="im-dropzone-icon">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                                <line x1="12" y1="19" x2="12" y2="5"></line>
                                <polyline points="5 12 12 5 19 12"></polyline>
                            </svg>
                        </div>
                    </div>
                    <div class="im-dropzone-title">Drag & Drop Excel File</div>
                    <div class="im-dropzone-subtitle">or <span class="im-dropzone-browse">browse files</span> from your computer</div>
                    <div class="im-dropzone-badges">
                        <div class="im-dropzone-badge">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="badge-icon"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                            <span style="margin-left: 4px;">.xlsx / .xls supported</span>
                        </div>
                        <div class="im-dropzone-badge">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="badge-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                            <span style="margin-left: 4px;">Auto validation</span>
                        </div>
                        <div class="im-dropzone-badge">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="badge-icon"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"></path></svg>
                            <span style="margin-left: 4px;">Max file size 20 MB</span>
                        </div>
                    </div>
                </div>
                <div class="im-uploader-overlay">
            """, unsafe_allow_html=True)

            # Render uploader inside the overlay
            uploaded = st.file_uploader(
                "Browse Files",
                type=["xlsx", "xls"],
                label_visibility="collapsed",
                key=uploader_key,
            )

            st.markdown("""
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div class="im-info-banner">
                    Pastikan struktur file sesuai template untuk menghindari error pada proses import.
                </div>
            """, unsafe_allow_html=True)
        else:
            validation = validate_import_upload(uploaded)
            st.session_state.im_validation = validation
            all_valid = all(validation.values())
            st.session_state.im_import_ready = all_valid

            if all_valid:
                current_sbu = st.session_state.get("im_sbu", SBU_LIST[0])
                try:
                    df_imported, missing_columns = store_shared_import(uploaded, current_sbu)
                    st.session_state.im_file = uploaded.name
                    st.session_state.im_import_ready = len(missing_columns) == 0

                    total_records = len(df_imported)
                    
                    # Calculate dynamic warnings based on logic:
                    # check for 0 or negative real_omzet and empty cells
                    warnings = 0
                    if "real_omzet" in df_imported.columns:
                        warnings += int((df_imported["real_omzet"] <= 0).sum())
                    
                    null_counts = df_imported.isnull().sum().sum()
                    warnings += int(null_counts)
                    
                    # Capping warnings if they exceed record count for safety
                    warnings = min(warnings, total_records)
                    valid_records = max(0, total_records - warnings)
                    score = int((valid_records / total_records) * 100) if total_records > 0 else 100

                    success_html = (
                        '<div class="im-success-visual">'
                        '<div class="im-success-icon-box">'
                        '<div class="im-success-icon">✓</div>'
                        '</div>'
                        '<div class="im-success-title">Upload Successful!</div>'
                        f'<div class="im-success-subtitle">{uploaded.name} · {total_records:,} records processed</div>'
                        '<div class="im-progress-bar-container">'
                        '<div class="im-progress-bar-fill"></div>'
                        '</div>'
                        '<div class="im-success-details">'
                        '<div class="im-stats-row">'
                        f'<div class="im-stat-card stat-records"><div class="stat-value">{total_records:,}</div><div class="stat-label">Records</div></div>'
                        f'<div class="im-stat-card stat-valid"><div class="stat-value">{valid_records:,}</div><div class="stat-label">Valid</div></div>'
                        f'<div class="im-stat-card stat-warnings"><div class="stat-value">{warnings:,}</div><div class="stat-label">Warnings</div></div>'
                        f'<div class="im-stat-card stat-score"><div class="stat-value">{score}%</div><div class="stat-label">Score</div></div>'
                        '</div>'
                        '</div>'
                        '</div>'
                    )

                    st.markdown(success_html, unsafe_allow_html=True)

                    st.markdown("<div class='im-success-buttons-container'>", unsafe_allow_html=True)
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("Upload Another", key=f"im_upload_another_{st.session_state.uploader_version}"):
                            st.session_state.uploader_version += 1
                            if SHARED_DATA_KEY in st.session_state:
                                del st.session_state[SHARED_DATA_KEY]
                            if SHARED_META_KEY in st.session_state:
                                del st.session_state[SHARED_META_KEY]
                            st.session_state.im_file = None
                            st.session_state.im_import_ready = False
                            st.rerun()
                    with btn_col2:
                        if st.button("View Data", key=f"im_view_data_{st.session_state.uploader_version}"):
                            st.session_state.active_menu = "Data Verification"
                            st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                except Exception as exc:
                    st.error(f"Gagal memproses file: {exc}")
                    all_valid = False

            if not all_valid:
                failed_reasons = []
                for key, label in KETENTUAN_RULES:
                    if not validation.get(key, False):
                        failed_reasons.append(label)

                is_size_failed = uploaded.size > MAX_IMPORT_FILE_BYTES
                size_kb = max(1, round(uploaded.size / 1024))

                reasons_html = ""
                for reason in failed_reasons:
                    reasons_html += (
                        '<div class="im-failure-detail-item">'
                        '<span style="color: #ef4444; font-weight: bold;">•</span>'
                        f'<span>{reason}</span>'
                        '</div>'
                    )

                failure_html = (
                    '<div class="im-failure-visual">'
                    '<div class="im-failure-icon-box">'
                    '<div class="im-failure-icon">✗</div>'
                    '</div>'
                    '<div class="im-failure-title">Upload Failed</div>'
                    f'<div class="im-failure-subtitle">{uploaded.name} ({size_kb:,} KB) tidak memenuhi ketentuan import.</div>'
                    '<div class="im-failure-details">'
                    '<div style="font-weight: 700; color: #dc2626; margin-bottom: 8px;">Detail Masalah:</div>'
                    f'{reasons_html}'
                    '</div>'
                    '</div>'
                )

                st.markdown(failure_html, unsafe_allow_html=True)

                st.markdown("<div class='im-success-buttons-container' style='max-width: 240px; margin: 0 auto;'>", unsafe_allow_html=True)
                if st.button("Upload Another", key=f"im_upload_another_fail_{st.session_state.uploader_version}"):
                    st.session_state.uploader_version += 1
                    if SHARED_DATA_KEY in st.session_state:
                        del st.session_state[SHARED_DATA_KEY]
                    if SHARED_META_KEY in st.session_state:
                        del st.session_state[SHARED_META_KEY]
                    st.session_state.im_file = None
                    st.session_state.im_import_ready = False
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── RIGHT: Ketentuan Import (white card) ──
    with right:
        _render_ketentuan_import(st.session_state.get("im_validation"))

    # ── Riwayat Import table ──
    _render_import_history_refined()

    # ── Bottom info cards ──
    _render_info_cards()


def _patch_upload_limit_text():
    components.html(
        """
        <script>
        (function () {
            const doc = window.parent.document;

            function patchUploadLimit() {
                doc.querySelectorAll('[data-testid="stFileUploader"]').forEach((uploader) => {
                    uploader.classList.add('im-refined-uploader');

                    const walker = doc.createTreeWalker(uploader, NodeFilter.SHOW_TEXT);
                    let node = walker.nextNode();
                    while (node) {
                        if (/200\\s*MB/i.test(node.nodeValue || '')) {
                            node.nodeValue = (node.nodeValue || '').replace(/200\\s*MB/gi, '20MB');
                        }
                        node = walker.nextNode();
                    }
                });
            }

            function setupHistoryPagination() {
                const buttons = doc.querySelectorAll('.im-pg-btn');
                buttons.forEach(btn => {
                    if (btn.classList.contains('disabled') || btn.classList.contains('active')) return;
                    if (btn.dataset.hasListener) return;
                    btn.dataset.hasListener = "true";

                    btn.addEventListener('click', () => {
                        const targetPage = btn.getAttribute('data-page');
                        if (!targetPage) return;

                        const triggerContainer = doc.querySelector('.im-page-trigger-container');
                        if (triggerContainer) {
                            const input = triggerContainer.querySelector('input');
                            if (input) {
                                input.value = targetPage;
                                input.dispatchEvent(new Event('input', { bubbles: true }));
                                input.dispatchEvent(new Event('change', { bubbles: true }));
                            }
                        }
                    });
                });
            }

            function hidePageSyncTrigger() {
                doc.querySelectorAll('[data-testid="stTextInput"]').forEach((widget) => {
                    const label = widget.querySelector('label');
                    if (label && label.textContent.includes('Page Sync Trigger')) {
                        widget.style.display = 'none';
                    }
                });
            }

            patchUploadLimit();
            setupHistoryPagination();
            hidePageSyncTrigger();

            const observer = new MutationObserver(() => {
                patchUploadLimit();
                setupHistoryPagination();
                hidePageSyncTrigger();
            });

            observer.observe(doc.body, {
                childList: true,
                subtree: true,
                characterData: true,
            });
        })();
        </script>
        """,
        height=0,
        width=0,
    )


def render_import_manager():
    _init_state()
    st.markdown('<div class="overview-page-marker im-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)
    st.markdown(_REFINED_IMPORT_CSS, unsafe_allow_html=True)
    st.markdown(_NEW_DESIGN_CSS, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="ov-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_im_page_header_html(), unsafe_allow_html=True)
        st.markdown('<div class="ov-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="ov-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)
    _mount_im_fixed_header()

    st.markdown('<div class="im-manager-surface">', unsafe_allow_html=True)
    _render_new_workspace()
    st.markdown('</div>', unsafe_allow_html=True)
    _patch_upload_limit_text()


if __name__ == "__main__":
    st.set_page_config(page_title="Data Import Manager", layout="wide")
    render_import_manager()
