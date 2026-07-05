import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from .export_utils import EXCEL_MIME, dataframe_to_excel_bytes
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
    normalize_imported_data,
    read_import_file,
    get_missing_dashboard_columns,
    get_column_mapping,
    REQUIRED_DASHBOARD_COLUMNS,
)
from .navigation import topnav_actions_html
from .pagination import render_pagination

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

def _load_import_history() -> pd.DataFrame:
    try:
        from .connection import get_engine
        from sqlalchemy import text

        engine = get_engine()
        try:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE import_history ADD COLUMN IF NOT EXISTS deleted_by VARCHAR(255)"))
        except Exception:
            pass

        with engine.connect() as conn:
            return pd.read_sql(
                text("""
                    SELECT import_id, periode, filename, uploaded_by, uploaded_at,
                           total_records, valid_records, rs_total, file_size, status,
                           deleted_by
                    FROM import_history ih
                    ORDER BY uploaded_at DESC NULLS LAST, import_id DESC
                """),
                conn,
            )
    except Exception:
        return pd.DataFrame()


def _get_refined_history_data() -> list[dict]:
    history = _load_import_history()
    if history.empty:
        return []

    items = []
    for _, row in history.iterrows():
        uploaded_at = pd.to_datetime(row.get("uploaded_at"), errors="coerce")
        uploader = str(row.get("uploaded_by") or "User")
        initials = "".join(part[:1] for part in uploader.split()[:2]).upper() or "U"
        rs_total = float(row.get("rs_total") or 0)
        items.append({
            "import_id": row.get("import_id"),
            "period": row.get("periode") or "-",
            "upload_date": uploaded_at.strftime("%d %b %Y") if pd.notna(uploaded_at) else "-",
            "upload_time": uploaded_at.strftime("%H:%M WIB") if pd.notna(uploaded_at) else "-",
            "uploader": uploader,
            "role": "User",
            "initials": initials,
            "color": "#6366f1",
            "total_records": int(row.get("total_records") or 0),
            "tenants": int(row.get("valid_records") or 0),
            "file_size": row.get("file_size") or "-",
            "rs_total": f"Rp {rs_total:,.0f}".replace(",", "."),
            "status": row.get("status") or "Success",
            "deleted_by": row.get("deleted_by"),
        })
    return items

def _get_belum_submit():
    return []


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

/* Nudge the pagination row down 10px on this page only. */
body:has(.im-page-marker) div[data-testid="stElementContainer"]:has(.overview-detail-pagination-footer-marker) ~ div[data-testid="stLayoutWrapper"] {
    margin-top: 10px !important;
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
.im-table thead tr { background: rgba(99, 102, 241, 0.05); border-bottom: none; }
.im-table th { padding: 11px 13px; text-align: left; font-size: 11px; font-weight: 700; color: #4F46E5; text-transform: uppercase; letter-spacing: .5px; white-space: nowrap; }
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
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800;900&display=swap');

.stApp, .stApp * {
    font-family: 'Inter', sans-serif !important;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp [class*="-title"], .stApp [class*="-header"], .stApp [class*="title-"] {
    font-family: 'Montserrat', sans-serif !important;
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
.im-top-refresh-btn {
    background: #eff6ff !important;
    border: 1px solid rgba(37, 99, 235, 0.18) !important;
    border-radius: 50% !important;
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    min-height: 32px !important;
    max-width: 32px !important;
    max-height: 32px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.05) !important;
    margin: 0 !important;
    color: #2563eb !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    cursor: pointer !important;
    line-height: 1 !important;
    outline: none !important;
}
.im-top-refresh-btn:hover {
    background: #dbeafe !important;
    border-color: rgba(37, 99, 235, 0.4) !important;
    transform: rotate(30deg) !important;
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

/* The decorative "Browse files" button/icon/instructions get blown up to
   100% x 100% by the rule above, which makes them sit on top of (and
   intercept all pointer/drag events meant for) the real, invisible
   <input type="file">. That's why clicking worked (the button's own
   click handler opens the file dialog) but dragging a file onto the
   zone did not (the drop landed on the button, not the input). Make
   the decorative layer click/drop-through so the input underneath is
   what actually receives both clicks and native drag-and-drop. */
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzone"] > span,
.im-refined-uploader [data-testid="stFileUploaderDropzone"] > span,
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzone"] > span *,
.im-refined-uploader [data-testid="stFileUploaderDropzone"] > span *,
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzoneInstructions"],
.im-refined-uploader [data-testid="stFileUploaderDropzoneInstructions"],
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzoneInstructions"] *,
.im-refined-uploader [data-testid="stFileUploaderDropzoneInstructions"] * {
    pointer-events: none !important;
}
/* The dropzone <section> lays out its <input> and the decorative <span>
   as side-by-side flex children (each ~50% width), not stacked/overlapping.
   Forcing width:100% above doesn't escape that — the input still only
   covers the LEFT half. Anywhere on the right half, pointer/drag events
   fall through the (pointer-events:none) span straight past the real
   uploader to our decorative background card behind it, which has no
   upload handlers at all. Taking the input out of flow with absolute
   positioning makes it cover the *entire* dropzone regardless of the
   sibling's flex sizing. */
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzone"],
.im-refined-uploader [data-testid="stFileUploaderDropzone"] {
    position: relative !important;
}
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzoneInput"],
.im-refined-uploader [data-testid="stFileUploaderDropzoneInput"] {
    pointer-events: auto !important;
    position: absolute !important;
    inset: 0 !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    z-index: 1 !important;
}

/* Pure-CSS equivalent of ".im-refined-uploader" above. That class is added
   by JS (a MutationObserver in a components.html iframe) which needs a
   moment to load/run — navigate here quickly and the raw Streamlit uploader
   (visible "Drag and drop"/"Browse files") flashes on top of the decorative
   dropzone before the JS hides it. Streamlit auto-applies "st-key-<key>" as
   a class on the widget's own container, so this targets the exact same
   widget with no JS dependency and no flash. */
[class*="st-key-im_uploader_refined_"] {
    opacity: 0 !important;
    position: relative !important;
    margin-top: -268px !important;
    height: 254px !important;
    z-index: 1000 !important;
    cursor: pointer !important;
}
[class*="st-key-im_uploader_refined_"] * {
    cursor: pointer !important;
    width: 100% !important;
    height: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
}
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploadDropzone"],
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploaderDropzone"] {
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    background: transparent !important;
    position: relative !important;
}
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploaderDropzone"] > span,
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploaderDropzone"] > span *,
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploaderDropzoneInstructions"],
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploaderDropzoneInstructions"] * {
    pointer-events: none !important;
}
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploaderDropzoneInput"] {
    pointer-events: auto !important;
    position: absolute !important;
    inset: 0 !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    z-index: 1 !important;
}


/* Success State styling */
.im-success-visual {
    border: 1.5px solid rgba(99, 102, 241, 0.20) !important;
    border-radius: 24px !important;
    background: rgba(255, 255, 255, 0.45) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    padding: 30px 24px 24px !important;
    text-align: center !important;
    box-shadow: 0 8px 32px 0 rgba(99, 102, 241, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    margin-bottom: 14px !important;
    animation: cardPopIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
.im-success-icon-box {
    width: 68px !important;
    height: 68px !important;
    border-radius: 50% !important;
    background: rgba(99, 102, 241, 0.08) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin-bottom: 14px !important;
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.12) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    backdrop-filter: blur(4px) !important;
}
.im-success-icon {
    width: 44px !important;
    height: 44px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    color: #ffffff !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35) !important;
    font-size: 20px !important;
    font-weight: bold !important;
}
.im-success-title {
    font-size: 22px !important;
    font-weight: 850 !important;
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin-bottom: 4px !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    letter-spacing: -0.5px !important;
}
.im-success-subtitle {
    font-size: 12px !important;
    color: #64748b !important;
    margin-bottom: 20px !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* Progress bar container and animations */
.im-progress-bar-container {
    width: 100% !important;
    max-width: 440px !important;
    height: 6px !important;
    background: rgba(226, 232, 240, 0.5) !important;
    border-radius: 999px !important;
    overflow: hidden !important;
    margin-bottom: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important;
}
@keyframes progressBarWidth {
    0% { width: 0%; }
    100% { width: 100%; }
}
@keyframes progressBarColor {
    0% { background-color: #2563eb; } /* Blue */
    45% { background-color: #2563eb; }
    75% { background-color: #f97316; } /* Orange */
    100% { background-color: #10b981; } /* Green */
}
.im-progress-bar-fill {
    height: 100% !important;
    border-radius: 999px !important;
    width: 0%;
    background-color: #2563eb;
    animation-name: progressBarWidth, progressBarColor !important;
    animation-duration: 2.5s, 2.5s !important;
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1), cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation-fill-mode: forwards, forwards !important;
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
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    animation: successDetailsFadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 2s both !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* Stats Cards container and cards */
.im-stats-row {
    display: flex !important;
    justify-content: center !important;
    gap: 12px !important;
    width: 100% !important;
    margin-bottom: 20px !important;
    flex-wrap: wrap !important;
}
.im-stat-card {
    flex: 1 !important;
    min-width: 90px !important;
    border-radius: 14px !important;
    padding: 12px 8px !important;
    text-align: center !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.02), inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
    transition: transform 0.2s, box-shadow 0.2s, background 0.2s !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
.im-stat-card:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.06) !important;
}
/* Purple Stat Card: Records */
.stat-records {
    background: rgba(99, 102, 241, 0.08) !important;
    border: 1.5px solid rgba(99, 102, 241, 0.30) !important;
}
.stat-records .stat-value {
    color: #6366f1 !important;
    background: linear-gradient(135deg, #6366F1, #4F46E5) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}
/* Green Stat Card: Valid */
.stat-valid {
    background: rgba(16, 185, 129, 0.08) !important;
    border: 1.5px solid rgba(16, 185, 129, 0.30) !important;
}
.stat-valid .stat-value {
    color: #10b981 !important;
    background: linear-gradient(135deg, #10B981, #059669) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}
/* Yellow Stat Card: Warnings */
.stat-warnings {
    background: rgba(245, 158, 11, 0.08) !important;
    border: 1.5px solid rgba(245, 158, 11, 0.30) !important;
}
.stat-warnings .stat-value {
    color: #d97706 !important;
    background: linear-gradient(135deg, #F59E0B, #D97706) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}
/* Teal Stat Card: Score */
.stat-score {
    background: rgba(20, 184, 166, 0.08) !important;
    border: 1.5px solid rgba(20, 184, 166, 0.30) !important;
}
.stat-score .stat-value {
    color: #14b8a6 !important;
    background: linear-gradient(135deg, #14B8A6, #0D9488) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

.stat-value {
    font-size: 22px !important;
    font-weight: 850 !important;
    margin-bottom: 2px !important;
    line-height: 1.2 !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
.stat-label {
    font-size: 11px !important;
    color: #64748b !important;
    font-weight: 600 !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] {
    max-width: 380px !important;
    margin: 16px 0 0 0 !important;
    width: 100% !important;
}
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stButton"] button {
    width: 100% !important;
    height: 42px !important;
    border-radius: 24px !important; /* Pill style matching mockup */
    font-size: 13.5px !important;
    font-weight: 700 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
/* Style for Col 1 button (Upload Another) */
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button,
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:first-child button {
    background: #ffffff !important;
    color: #1e293b !important;
    border: 1.5px solid #cbd5e1 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
}
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button::before,
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:first-child button::before {
    content: "";
    display: inline-block;
    width: 14px;
    height: 14px;
    margin-right: 8px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/%3E%3Cpolyline points='17 8 12 3 7 8'/%3E%3Cline x1='12' y1='3' x2='12' y2='15'/%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    flex-shrink: 0;
}
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button:hover,
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:first-child button:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
    transform: translateY(-1px) !important;
}
/* Style for Col 2 button (View Data) */
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button,
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child button {
    background: #2563eb !important; /* Solid blue background */
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
}
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button::before,
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child button::before {
    content: "";
    display: inline-block;
    width: 14px;
    height: 14px;
    margin-right: 8px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='18' height='18' rx='2'/%3E%3Cline x1='3' y1='9' x2='21' y2='9'/%3E%3Cline x1='9' y1='21' x2='9' y2='9'/%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    flex-shrink: 0;
}
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button:hover,
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child button:hover {
    background: #1d4ed8 !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35) !important;
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
    flex-direction: column;
    gap: 0;
    font-size: 12px;
    font-weight: 600;
    color: #334155;
    line-height: 1.45;
    width: 100%;
    transition: all 0.2s ease;
}
.im-ketentuan-row {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
}
.im-ketentuan-text {
    font-weight: 600;
}
.im-ketentuan-neutral {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: 2px solid #cbd5e1;
    margin-top: 1px;
    box-sizing: border-box;
}
.im-ketentuan-check {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #ffffff !important;
    font-size: 11px;
    font-weight: 900;
    background: #10b981 !important; /* Solid emerald green */
    border: 1px solid #10b981 !important;
    margin-top: 1px;
}
.im-ketentuan-fail {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #ffffff !important;
    font-size: 10px;
    font-weight: 900;
    background: #ef4444 !important; /* Solid red */
    border: 1px solid #ef4444 !important;
    margin-top: 1px;
}
.im-ketentuan-item.is-neutral .im-ketentuan-text {
    color: #64748b;
    font-weight: 500;
}
.im-ketentuan-item.is-pass .im-ketentuan-text {
    color: #1e293b;
    font-weight: 600;
}
.im-ketentuan-item.is-fail .im-ketentuan-text {
    color: #991b1b;
    font-weight: 600;
}
.im-ketentuan-item.is-fail {
    background: rgba(239, 68, 68, 0.05) !important;
    border: 1px solid rgba(239, 68, 68, 0.12) !important;
    border-radius: 12px;
    padding: 10px 12px !important;
    margin-bottom: 2px;
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.04);
}
.im-ketentuan-warning-box {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 8px;
    padding: 8px 12px;
    margin-top: 8px;
    margin-left: 30px; /* Aligns under text, offset by icon width (20px) + gap (10px) */
    font-size: 11px;
    color: #991b1b;
    font-weight: 500;
    line-height: 1.45;
}
.im-ketentuan-warning-list {
    margin: 0;
    padding-left: 16px;
    list-style: disc;
}
.im-ketentuan-warning-list li {
    margin: 2px 0;
}
.im-ketentuan-warning-list li::marker {
    color: #dc2626;
}
.im-info-banner {
    margin-top: -25px;
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
    margin-top: 1px;
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
.im-btn-refresh:hover {
    background: #f5f3ff;
    border-color: rgba(99,102,241,0.3);
    transform: none;
    box-shadow: none;
}
.im-btn-export.btn-clear-trash {
    color: #ef4444 !important;
    border-color: rgba(239, 68, 68, 0.20) !important;
}
.im-btn-export.btn-clear-trash:hover {
    background: #fef2f2 !important;
    border-color: rgba(239, 68, 68, 0.40) !important;
}
/* History Table Row Design */
.im-hist-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
}
.im-hist-table thead tr {
    background: rgba(99, 102, 241, 0.05);
    border-radius: 10px;
    overflow: hidden;
}
.im-hist-table th {
    padding: 11px 14px;
    background: transparent;
    border: none;
    color: #4F46E5;
    font-size: 11px;
    font-weight: 700;
    text-align: left;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
}
.im-hist-table th:first-child {
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
}
.im-hist-table th:last-child {
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
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
.im-period-dot.dot-deleted { background: #64748b; }
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
.im-status-deleted {
    background: rgba(100, 116, 139, 0.10);
    color: #475569;
    border: 1px solid rgba(100, 116, 139, 0.20);
}
.im-status-deleted .status-dot { background: #64748b; }
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
    border: 1px solid rgba(99,102,241,0.15);
    background: #fff;
    color: #6366F1;
    cursor: pointer;
    transition: all 0.15s;
    font-size: 13px;
}
.im-action-btn svg {
    width: 16px;
    height: 16px;
    stroke: currentColor;
}
.im-action-btn:hover {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    color: #fff;
    border-color: transparent;
}
.im-action-btn.btn-delete:hover {
    background: #fef2f2;
    color: #ef4444;
    border-color: rgba(239,68,68,0.2);
}
/* Reset native <button> appearance for action + header buttons */
button.im-action-btn {
    appearance: none;
    -webkit-appearance: none;
    padding: 0;
    outline: none;
    box-sizing: border-box;
    line-height: 1;
}
button.im-btn-refresh,
button.im-btn-export {
    appearance: none;
    -webkit-appearance: none;
    outline: none;
    font-family: inherit;
}
/* JS-action bridge input — offscreen (not display:none) so React events fire normally */
[data-testid="stElementContainer"]:has(input[placeholder="__im_action_trigger__"]) {
    position: fixed !important;
    top: -9999px !important;
    left: -9999px !important;
    width: 1px !important;
    height: 1px !important;
    overflow: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    z-index: -1 !important;
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
    background: rgba(99, 102, 241, 0.05);
}
.im-table th {
    color: #4F46E5;
    font-size: 11px;
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
    font-family: 'Inter', sans-serif !important;
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
    background: #ffffff !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    padding: 0 !important;
    box-shadow: 0 1px 4px rgba(15,23,42,0.05) !important;
    overflow: hidden !important;
}
.im-ketentuan-head {
    padding: 20px 22px 14px !important;
    border-bottom: 1px solid #F1F5F9 !important;
}
.im-ketentuan-head .im-section-title {
    font-size: 14px !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    letter-spacing: 0.1px !important;
    margin: 0 !important;
}
.im-ketentuan-body {
    padding: 20px 22px 22px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 12px !important;
}
.im-ketentuan-item {
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    width: 100% !important;
    margin-bottom: 4px !important;
    gap: 0 !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}
.im-ketentuan-item.is-neutral {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}
.im-ketentuan-item.is-pass {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}
.im-ketentuan-item.is-fail {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}
.im-ketentuan-row {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 10px !important;
    width: 100% !important;
}
.im-ketentuan-neutral,
.im-ketentuan-check,
.im-ketentuan-fail {
    width: 20px !important;
    height: 20px !important;
    min-width: 20px !important;
    min-height: 20px !important;
    max-width: 20px !important;
    max-height: 20px !important;
    border-radius: 50% !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-shrink: 0 !important;
    box-sizing: border-box !important;
    line-height: 1 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    text-align: center !important;
}
.im-ketentuan-neutral {
    background: transparent !important;
    border: 2px solid #cbd5e1 !important;
}
.im-ketentuan-check {
    background: #10b981 !important;
    border: 1px solid #10b981 !important;
    color: #ffffff !important;
    font-size: 11px !important;
    font-weight: 900 !important;
}
.im-ketentuan-fail {
    background: #ef4444 !important;
    border: 1px solid #ef4444 !important;
    color: #ffffff !important;
    font-size: 11px !important;
    font-weight: 900 !important;
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.5) !important;
}
.im-ketentuan-text {
    font-size: 12.5px !important;
    color: #1e293b !important;
    font-weight: 600 !important;
    line-height: 1.45 !important;
}
.im-ketentuan-item.is-neutral .im-ketentuan-text {
    color: #64748b !important;
    font-weight: 500 !important;
}
.im-ketentuan-item.is-pass .im-ketentuan-text {
    color: #1e293b !important;
    font-weight: 600 !important;
}
.im-ketentuan-item.is-fail .im-ketentuan-text {
    color: #1e293b !important;
    font-weight: 600 !important;
}
.im-ketentuan-warning-box {
    background: #fef2f2 !important;
    border: 1px solid #fca5a5 !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    margin-top: 8px !important;
    margin-left: 30px !important;
    font-size: 11px !important;
    color: #991b1b !important;
    font-weight: 500 !important;
    line-height: 1.45 !important;
    width: calc(100% - 30px) !important;
    box-sizing: border-box !important;
}
.im-validation-error-card {
    background: #fef2f2 !important;
    border: 1px solid #fca5a5 !important;
    border-radius: 12px !important;
    padding: 12px 20px !important;
    margin-top: 5px !important;
    width: 85% !important;
    max-width: 420px !important;
    box-sizing: border-box !important;
    text-align: center !important;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.05) !important;
}
.im-validation-error-title {
    font-size: 13px !important;
    font-weight: 750 !important;
    color: #b91c1c !important;
    margin-bottom: 3px !important;
}
.im-validation-error-desc {
    font-size: 11.5px !important;
    font-weight: 450 !important;
    color: #991b1b !important;
    line-height: 1.4 !important;
}
/* Kartu notifikasi hasil simpan (lihat _render_save_result_notice) — ikon +
   judul singkat + penjelasan bahasa awam, dengan detail teknis (mis. kode
   ruang yang bentrok) dipisah di bawah, bukan digabung jadi satu paragraf. */
.im-notice {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    border-radius: 12px;
    border: 1px solid;
    border-left-width: 4px;
    padding: 14px 16px;
    margin-top: 8px;
}
.im-notice-icon {
    flex: 0 0 auto;
    width: 32px;
    height: 32px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.im-notice-icon svg { width: 17px; height: 17px; }
.im-notice-body { flex: 1; min-width: 0; }
.im-notice-title {
    font-size: 13.5px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 3px;
}
.im-notice-desc {
    font-size: 12.5px;
    font-weight: 450;
    color: #475569;
    line-height: 1.5;
}
.im-notice-detail {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(15, 23, 42, 0.06);
}
.im-notice-detail-label {
    display: block;
    font-size: 9.5px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 6px;
}
.im-notice-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.im-notice-tag {
    font-size: 11.5px;
    font-weight: 600;
    font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    padding: 3px 9px;
    border-radius: 6px;
    background: rgba(15, 23, 42, 0.045);
    color: #334155;
    border: 1px solid rgba(15, 23, 42, 0.07);
}
.im-notice-error {
    background: #fef2f2;
    border-color: #fecaca;
}
.im-notice-error .im-notice-icon {
    background: rgba(220, 38, 38, 0.12);
    color: #dc2626;
}
.im-notice-warning {
    background: #fffbeb;
    border-color: #fde68a;
}
.im-notice-warning .im-notice-icon {
    background: rgba(217, 119, 6, 0.14);
    color: #d97706;
}
.im-notice-success {
    background: #f0fdf4;
    border-color: #bbf7d0;
}
.im-notice-success .im-notice-icon {
    background: rgba(22, 163, 74, 0.14);
    color: #16a34a;
}
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
.im-table-v2 thead tr { background: rgba(99, 102, 241, 0.05); }
.im-table-v2 th { padding:11px 16px; text-align:left; font-size:11px; font-weight:700; color:#4F46E5; text-transform:uppercase; letter-spacing:.5px; white-space:nowrap; border-bottom:none; }
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


_IM_NOTICE_ICONS = {
    "error": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    "warning": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    "success": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
}


def _render_save_result_notice(result: dict) -> None:
    """Kartu notifikasi terstruktur untuk hasil `_save_to_database()`: ikon +
    judul singkat berbahasa awam + penjelasan, dengan detail teknis (mis.
    kode ruang yang bentrok) dipisah di baris sendiri — bukan satu paragraf
    teks polos ala st.error/st.warning bawaan."""
    from html import escape

    severity = result.get("severity", "error")
    icon = _IM_NOTICE_ICONS.get(severity, _IM_NOTICE_ICONS["error"])

    detail_html = ""
    detail_items = result.get("detail_items")
    if detail_items:
        tags = "".join(f'<span class="im-notice-tag">{escape(str(v))}</span>' for v in detail_items)
        detail_html = (
            '<div class="im-notice-detail">'
            f'<span class="im-notice-detail-label">{escape(result.get("detail_label", "Detail"))}</span>'
            f'<div class="im-notice-tags">{tags}</div>'
            '</div>'
        )

    st.markdown(
        f'<div class="im-notice im-notice-{severity}">'
        f'<div class="im-notice-icon">{icon}</div>'
        '<div class="im-notice-body">'
        f'<div class="im-notice-title">{escape(result.get("title", ""))}</div>'
        f'<div class="im-notice-desc">{escape(result.get("message", ""))}</div>'
        f'{detail_html}'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _save_to_database():
    """Simpan data ke transaction_revenue. Selalu mengembalikan
    (success, result) dengan `result` sebagai dict {severity, title,
    message, detail_label, detail_items} — bukan string polos — supaya
    UI bisa menampilkan kartu notifikasi terstruktur (lihat
    _render_save_result_notice) alih-alih satu paragraf teks teknis."""
    from .shared_import import SHARED_DATA_KEY
    df = st.session_state.get(SHARED_DATA_KEY)
    if df is None or df.empty:
        return False, {
            "severity": "error",
            "title": "Tidak Ada Data untuk Disimpan",
            "message": "File yang diunggah tidak berisi data yang bisa diproses.",
        }
    
    mapping = st.session_state.get("shared_import_mapping", {})
    df_to_save = df.rename(columns={v: k for k, v in mapping.items()})

    # Nama kolom standar Import Manager berbeda dari nama kolom asli di tabel
    # transaction_revenue (lihat alias "produksi_m2 AS luas_sqm" di
    # load_dashboard_data), jadi disamakan dulu supaya tidak ikut dibuang
    # saat filter save_cols di bawah.
    DB_COLUMN_OVERRIDES = {"luas_sqm": "produksi_m2"}
    df_to_save = df_to_save.rename(columns={
        k: v for k, v in DB_COLUMN_OVERRIDES.items() if k in df_to_save.columns
    })

    from .connection import get_engine
    from sqlalchemy import inspect, text
    from sqlalchemy.exc import IntegrityError
    import time

    NATURAL_KEY = ["kode_ruang", "masa_jasa", "tahun"]

    try:
        engine = get_engine()
        import_id = int(time.time())
        inspector = inspect(engine)
        db_columns = [col['name'] for col in inspector.get_columns('transaction_revenue')]

        if 'import_id' in db_columns:
            df_to_save['import_id'] = import_id

        save_cols = [c for c in df_to_save.columns if c in db_columns]
        df_final = df_to_save[save_cols].copy()
        df_final = df_final.loc[:, ~df_final.columns.duplicated()]

        if 'id' in df_final.columns:
            df_final = df_final.drop(columns=['id'])

        skipped_count = 0
        skipped_items = []
        if all(c in df_final.columns for c in NATURAL_KEY):
            # Safety net di level database: kombinasi kode_ruang + masa_jasa +
            # tahun harus unik, supaya baris yang sama tidak pernah bisa dobel
            # tersimpan walau ada bug di pengecekan aplikasi di bawah.
            try:
                with engine.begin() as ddl_conn:
                    ddl_conn.execute(text(
                        "ALTER TABLE transaction_revenue ADD CONSTRAINT "
                        "uq_transaction_revenue_natural_key UNIQUE (kode_ruang, masa_jasa, tahun)"
                    ))
            except Exception:
                pass

            dup_mask = df_final.duplicated(subset=NATURAL_KEY, keep=False)
            if dup_mask.any():
                dup_items = []
                for kode, group in df_final.loc[dup_mask].groupby("kode_ruang", dropna=False):
                    rows = _format_row_list([int(i) + 2 for i in group.index], limit=8)
                    dup_items.append(f"{kode} — baris {rows}")
                return False, {
                    "severity": "error",
                    "title": "Data Duplikat Ditemukan",
                    "message": (
                        f"File ini punya {int(dup_mask.sum())} baris dengan kode ruang dan periode "
                        "yang sama persis. Hapus atau perbaiki salah satu baris yang bentrok, "
                        "lalu unggah ulang."
                    ),
                    "detail_label": "Kode Ruang yang Bentrok",
                    "detail_items": dup_items[:15],
                }

            tahun_values = [
                int(t) for t in pd.to_numeric(df_final["tahun"], errors="coerce").dropna().unique()
            ]
            existing = pd.DataFrame(columns=["kode_ruang", "masa_jasa", "tahun"])
            if tahun_values:
                with engine.connect() as conn:
                    existing = pd.read_sql(
                        text(
                            "SELECT kode_ruang, masa_jasa, tahun FROM transaction_revenue "
                            "WHERE kode_ruang = ANY(:kode_ruang) AND tahun = ANY(:tahun)"
                        ),
                        conn,
                        params={
                            "kode_ruang": df_final["kode_ruang"].astype(str).tolist(),
                            "tahun": tahun_values,
                        },
                    )

            if not existing.empty:
                existing_keys = set(
                    zip(
                        existing["kode_ruang"].astype(str),
                        pd.to_datetime(existing["masa_jasa"], errors="coerce"),
                        existing["tahun"],
                    )
                )
                is_dup = df_final.apply(
                    lambda r: (
                        str(r["kode_ruang"]),
                        pd.to_datetime(r["masa_jasa"], errors="coerce"),
                        r["tahun"],
                    ) in existing_keys,
                    axis=1,
                )
                skipped_count = int(is_dup.sum())
                skipped_items = [
                    f"{row['kode_ruang']} — baris {int(idx) + 2}"
                    for idx, row in df_final.loc[is_dup].iterrows()
                ][:15]
                df_final = df_final.loc[~is_dup].copy()

            if df_final.empty:
                return False, {
                    "severity": "error",
                    "title": "Semua Data Sudah Pernah Diimpor",
                    "message": (
                        f"Seluruh {skipped_count} baris pada file ini sudah ada di database "
                        "(kode ruang dan periode yang sama). Tidak ada data baru yang ditambahkan."
                    ),
                    "detail_label": "Baris yang Sudah Pernah Diimpor",
                    "detail_items": skipped_items,
                }

        # Normalisasi tenant: tenant_master adalah satu-satunya sumber
        # kebenaran untuk identitas tenant (dedup berdasarkan perusahaan +
        # brand + terminal). transaction_revenue tetap menyimpan kolom
        # tenant apa adanya (kompatibel dengan halaman lain), tapi sekarang
        # juga terhubung lewat tenant_id yang benar-benar merujuk ke sana.
        if (
            'tenant_id' in db_columns
            and all(c in df_final.columns for c in ["perusahaan", "brand", "terminal"])
        ):
            try:
                with engine.begin() as ddl_conn:
                    ddl_conn.execute(text(
                        "ALTER TABLE tenant_master ADD CONSTRAINT "
                        "uq_tenant_master_key UNIQUE (perusahaan, brand, terminal)"
                    ))
            except Exception:
                pass

            tenant_cols = [c for c in ["perusahaan", "brand", "terminal", "bidang_usaha", "lokasi"] if c in df_final.columns]
            tenant_rows = (
                df_final[tenant_cols]
                .dropna(subset=["perusahaan", "brand", "terminal"])
                .drop_duplicates(subset=["perusahaan", "brand", "terminal"])
            )
            if not tenant_rows.empty:
                with engine.begin() as tconn:
                    for _, row in tenant_rows.iterrows():
                        tconn.execute(
                            text("""
                                INSERT INTO tenant_master (perusahaan, brand, terminal, bidang_usaha, lokasi)
                                VALUES (:perusahaan, :brand, :terminal, :bidang_usaha, :lokasi)
                                ON CONFLICT (perusahaan, brand, terminal) DO NOTHING
                            """),
                            {
                                "perusahaan": row["perusahaan"],
                                "brand": row["brand"],
                                "terminal": row["terminal"],
                                "bidang_usaha": row.get("bidang_usaha"),
                                "lokasi": row.get("lokasi"),
                            },
                        )
                    tenant_lookup = pd.read_sql(
                        text("SELECT id, perusahaan, brand, terminal FROM tenant_master WHERE perusahaan = ANY(:names)"),
                        tconn,
                        params={"names": tenant_rows["perusahaan"].astype(str).unique().tolist()},
                    )
                key_to_id = {
                    (str(r.perusahaan), str(r.brand), str(r.terminal)): r.id
                    for r in tenant_lookup.itertuples()
                }
                df_final["tenant_id"] = df_final.apply(
                    lambda r: key_to_id.get((str(r.get("perusahaan")), str(r.get("brand")), str(r.get("terminal")))),
                    axis=1,
                )

        # Normalisasi kontrak: satu baris kontrak per nomor_kontrak_sistem
        # (nomor SAP), disimpan terpisah dari transaction_revenue dan
        # terhubung ke tenant_master. Hanya baris yang benar-benar punya
        # nomor kontrak sistem yang diproses di sini. Baris kontrak.import_id
        # merujuk ke import_history, jadi penyiapan datanya di sini, tapi
        # eksekusi INSERT-nya harus menunggu sampai import_history baris ini
        # sudah benar-benar ada (lihat di bawah) — kalau tidak, FK gagal
        # persis seperti bug transaction_revenue vs import_history sebelumnya.
        kontrak_rows = pd.DataFrame()
        kontrak_available = {}
        if "nomor_kontrak_sistem" in df_final.columns:
            try:
                with engine.begin() as ddl_conn:
                    ddl_conn.execute(text(
                        "ALTER TABLE kontrak ADD CONSTRAINT "
                        "uq_kontrak_nomor_sistem UNIQUE (nomor_kontrak_sistem)"
                    ))
            except Exception:
                pass

            kontrak_col_map = {
                "nomor_kontrak_sistem": "nomor_kontrak_sistem",
                "nomor_kontrak_legal": "nomor_kontrak_legal",
                "kerja_sama": "jenis_kontrak",
                "rs_percent": "sharing_percent",
                "min_omzet": "minimal_omzet",
                "mgrs_per_pax": "mgrs_per_pax",
                "start_kontrak": "start_kontrak",
                "end_kontrak": "end_kontrak",
            }
            kontrak_available = {src: dst for src, dst in kontrak_col_map.items() if src in df_final.columns}
            kontrak_rows = (
                df_final[list(kontrak_available.keys()) + (["tenant_id"] if "tenant_id" in df_final.columns else [])]
                .dropna(subset=["nomor_kontrak_sistem"])
                .drop_duplicates(subset=["nomor_kontrak_sistem"])
            )

        with engine.begin() as conn:
            if 'import_history' in inspector.get_table_names():
                meta = get_shared_import_meta()
                rs_total = 0.0
                if 'pendapatan_rs' in df_final.columns:
                    rs_total = float(pd.to_numeric(df_final['pendapatan_rs'], errors='coerce').fillna(0).sum())
                conn.execute(
                    text("""
                        INSERT INTO import_history
                            (import_id, periode, filename, uploaded_by, uploaded_at, is_active,
                             total_records, valid_records, rs_total, file_size, status)
                        VALUES
                            (:import_id, :periode, :filename, :uploaded_by, CURRENT_TIMESTAMP, true,
                             :total_records, :valid_records, :rs_total, :file_size, 'Success')
                    """),
                    {
                        'import_id': import_id,
                        'periode': meta.get('period') or meta.get('periode') or PERIOD_ACTIVE,
                        'filename': meta.get('file_name') or st.session_state.get('im_file') or '-',
                        'uploaded_by': st.session_state.get('user_name', 'Operational User'),
                        'total_records': int(len(df_final)) + skipped_count,
                        'valid_records': int(len(df_final)),
                        'rs_total': rs_total,
                        'file_size': meta.get('file_size') or '-',
                    },
                )

            if not kontrak_rows.empty:
                for _, row in kontrak_rows.iterrows():
                    params = {dst: row.get(src) for src, dst in kontrak_available.items()}
                    params["tenant_id"] = row.get("tenant_id")
                    params["import_id"] = import_id
                    cols = list(params.keys())
                    conn.execute(
                        text(
                            f"INSERT INTO kontrak ({', '.join(cols)}) "
                            f"VALUES ({', '.join(':' + c for c in cols)}) "
                            "ON CONFLICT (nomor_kontrak_sistem) DO NOTHING"
                        ),
                        params,
                    )

            df_final.to_sql("transaction_revenue", con=conn, if_exists="append", index=False)

            # Normalisasi trafik: berbeda dari tenant_master/kontrak (yang
            # berbasis identitas), traffic adalah AGREGAT per
            # tahun+bulan+terminal yang dijumlahkan dari banyak baris tenant
            # sekaligus. Jadi bukan sekadar insert baris baru — tiap kali ada
            # baris baru masuk ke transaction_revenue untuk suatu
            # tahun+bulan+terminal, agregatnya dihitung ULANG dari seluruh
            # transaction_revenue (bukan cuma batch ini), supaya tetap akurat
            # walau datanya datang dari beberapa kali import terpisah.
            if all(c in df_final.columns for c in ["tahun", "masa_jasa", "terminal"]):
                try:
                    with engine.begin() as ddl_conn:
                        ddl_conn.execute(text(
                            "ALTER TABLE traffic ADD CONSTRAINT "
                            "uq_traffic_key UNIQUE (tahun, bulan, terminal)"
                        ))
                except Exception:
                    pass

                periods = (
                    df_final[["tahun", "masa_jasa", "terminal"]]
                    .dropna()
                    .drop_duplicates()
                )
                for _, p in periods.iterrows():
                    conn.execute(
                        text("""
                            INSERT INTO traffic (tahun, bulan, terminal, pax_domestik, pax_internasional, total_pax, import_id)
                            SELECT
                                tahun,
                                TO_CHAR(MAX(masa_jasa::date), 'FMMonth'),
                                terminal,
                                SUM(COALESCE(subtotal_trafik_dom, 0)),
                                SUM(COALESCE(subtotal_trafik_int, 0)),
                                SUM(COALESCE(total_trafik, 0)),
                                :import_id
                            FROM transaction_revenue
                            WHERE tahun = :tahun AND masa_jasa::date = CAST(:masa_jasa AS date) AND terminal = :terminal
                            GROUP BY tahun, terminal
                            ON CONFLICT (tahun, bulan, terminal) DO UPDATE SET
                                pax_domestik = EXCLUDED.pax_domestik,
                                pax_internasional = EXCLUDED.pax_internasional,
                                total_pax = EXCLUDED.total_pax,
                                import_id = EXCLUDED.import_id
                        """),
                        {
                            "tahun": p["tahun"],
                            "masa_jasa": p["masa_jasa"],
                            "terminal": p["terminal"],
                            "import_id": import_id,
                        },
                    )

        st.cache_data.clear()

        if skipped_count:
            return True, {
                "severity": "warning",
                "title": "Sebagian Data Berhasil Disimpan",
                "message": (
                    f"{len(df_final)} baris baru berhasil disimpan. {skipped_count} baris "
                    "dilewati karena sudah pernah diimpor sebelumnya."
                ),
                "detail_label": "Baris yang Dilewati",
                "detail_items": skipped_items,
            }
        return True, {"severity": "success", "title": "Data Berhasil Disimpan", "message": "Seluruh baris pada file ini berhasil disimpan ke database."}
    except IntegrityError:
        return False, {
            "severity": "error",
            "title": "Data Sudah Ada di Database",
            "message": "Sebagian atau seluruh data pada file ini sudah ada di database. Tidak ada data baru yang disimpan.",
        }
    except Exception as e:
        return False, {
            "severity": "error",
            "title": "Gagal Menyimpan ke Database",
            "message": f"Terjadi kesalahan teknis saat menyimpan data: {str(e)}",
        }


_REQUIRED_COLUMN_LABELS = {
    "perusahaan": "Perusahaan",
    "brand": "Brand",
    "terminal": "Terminal",
    "kode_ruang": "Kode Ruang",
    "bidang_usaha": "Bidang Usaha",
    "masa_jasa": "Masa Jasa",
    "tahun": "Tahun",
    "min_omzet": "Min Omzet",
    "real_omzet": "Real Omzet",
    "pendapatan_sewa": "Pendapatan Sewa",
    "pendapatan_rs": "Pendapatan RS",
    "total_kontribusi": "Total Kontribusi",
    "luas_sqm": "Luas (m2)",
}


def _format_row_list(rows, limit=6) -> str:
    """Format daftar nomor baris Excel jadi teks ringkas, mis. '5, 8, 12, ...'."""
    rows = sorted(int(r) for r in rows)
    shown = ", ".join(str(r) for r in rows[:limit])
    return shown + (f", +{len(rows) - limit} lainnya" if len(rows) > limit else "")


def _get_merge_cell_detail(uploaded) -> str:
    try:
        uploaded.seek(0)
        filename = uploaded.name.lower()
        if filename.endswith(".xlsx"):
            from openpyxl import load_workbook
            workbook = load_workbook(uploaded, read_only=True)
            try:
                for ws in workbook.worksheets:
                    if ws.merged_cells.ranges:
                        ranges = [str(r) for r in list(ws.merged_cells.ranges)[:2]]
                        return f"Merge cells ditemukan pada sheet '{ws.title}', cell {', '.join(ranges)}. Silakan pisahkan."
            finally:
                workbook.close()
        elif filename.endswith(".xls"):
            import xlrd
            uploaded.seek(0)
            workbook = xlrd.open_workbook(file_contents=uploaded.read())
            for sheet in workbook.sheets():
                if sheet.merged_cells:
                    ranges = [f"{xlrd.formula.cellname(r[0], r[2])}:{xlrd.formula.cellname(r[1]-1, r[3]-1)}" for r in sheet.merged_cells[:2]]
                    return f"Merge cells ditemukan pada sheet '{sheet.name}', cell {', '.join(ranges)}. Silakan pisahkan."
    except Exception as exc:
        return f"Gagal membaca file: {exc}"
    return "Merge cells ditemukan pada file Excel Anda. Silakan pisahkan."


def _get_structure_detail(uploaded) -> list[str]:
    try:
        uploaded.seek(0)
        df = read_import_file(uploaded)
        df_norm = normalize_imported_data(df)
        missing = get_missing_dashboard_columns(df_norm)
        if missing:
            labels = [_REQUIRED_COLUMN_LABELS.get(col, col.upper()) for col in sorted(missing)]
            return [f"Header kolom berikut tidak ditemukan: {', '.join(labels)}."]
    except Exception as exc:
        return [f"Gagal membaca file: {exc}"]
    return ["Struktur kolom tidak sesuai template. Hindari perubahan struktur kolom."]


def _get_required_filled_detail(uploaded) -> list[str]:
    """Untuk tiap kolom wajib yang punya data kosong: sebutkan nama kolomnya
    dan nomor baris Excel-nya, sekaligus bedakan baris yang memang kosong di
    file asli dari baris yang datanya ada tapi tidak terbaca oleh proses
    pembersihan data (mis. teks di kolom angka, format tanggal yang tidak
    dikenali) — supaya user tahu harus mengisi atau memperbaiki format."""
    try:
        uploaded.seek(0)
        raw_df = read_import_file(uploaded)
        df_norm = normalize_imported_data(raw_df)
        mapping = get_column_mapping(df_norm)

        lines = []
        for col in sorted(REQUIRED_DASHBOARD_COLUMNS):
            orig_col = mapping.get(col)
            if not orig_col or orig_col not in df_norm.columns:
                continue

            series = df_norm[orig_col]
            empty_mask = series.isna()
            if series.dtype == object:
                cleaned = series.astype(str).str.strip()
                empty_mask = empty_mask | cleaned.eq("") | cleaned.str.lower().isin({"nan", "none", "nat"})
            if not empty_mask.any():
                continue

            raw_series = raw_df[orig_col] if orig_col in raw_df.columns else None
            blank_rows, invalid_rows = [], []
            for idx in df_norm.index[empty_mask]:
                excel_row = int(idx) + 2  # +1 untuk header, +1 karena index mulai dari 0
                raw_val = raw_series.loc[idx] if raw_series is not None else None
                raw_is_blank = pd.isna(raw_val) or str(raw_val).strip() == ""
                (blank_rows if raw_is_blank else invalid_rows).append(excel_row)

            label = _REQUIRED_COLUMN_LABELS.get(col, col.upper())
            parts = []
            if blank_rows:
                parts.append(f"kosong (baris {_format_row_list(blank_rows)})")
            if invalid_rows:
                parts.append(f"format tidak terbaca (baris {_format_row_list(invalid_rows)})")
            lines.append(f"{label}: {'; '.join(parts)}")

        if lines:
            return lines
    except Exception as exc:
        return [f"Gagal membaca file: {exc}"]
    return ["Kolom wajib harus terisi penuh. Pastikan tidak ada data kosong."]


def _render_ketentuan_import(validation: dict[str, bool] | None = None, is_uploaded: bool = False):
    validation = validation or {key: False for key, _ in KETENTUAN_RULES}
    uploaded = None
    if is_uploaded:
        uploader_key = f"im_uploader_refined_{st.session_state.uploader_version}"
        uploaded = st.session_state.get(uploader_key)

    items_html = ""
    from html import escape
    for key, label in KETENTUAN_RULES:
        if not is_uploaded:
            icon_class = "im-ketentuan-neutral"
            item_class = "is-neutral"
            icon = ""
            warning_html = ""
        else:
            passed = validation.get(key, False)
            if passed:
                icon_class = "im-ketentuan-check"
                item_class = "is-pass"
                icon = "✓"
                warning_html = ""
            else:
                icon_class = "im-ketentuan-fail"
                item_class = "is-fail"
                icon = "✗"
                detail_lines = []
                if uploaded:
                    if key == "format":
                        detail_lines = ["Format file tidak didukung. Gunakan .xlsx atau .xls."]
                    elif key == "size":
                        detail_lines = ["Ukuran file melebihi batas maksimal 20 MB."]
                    elif key == "merge_cell":
                        detail_lines = [_get_merge_cell_detail(uploaded)]
                    elif key == "structure":
                        detail_lines = _get_structure_detail(uploaded)
                    elif key == "required_filled":
                        detail_lines = _get_required_filled_detail(uploaded)
                if not detail_lines:
                    fallback_msgs = {
                        "format": "Format file tidak didukung. Gunakan .xlsx atau .xls.",
                        "size": "Ukuran file melebihi batas maksimal 20 MB.",
                        "merge_cell": "Merge cells ditemukan pada file Excel Anda.",
                        "structure": "Struktur kolom tidak sesuai template.",
                        "required_filled": "Kolom wajib harus terisi penuh."
                    }
                    detail_lines = [fallback_msgs.get(key, "Validasi gagal.")]

                if len(detail_lines) > 1:
                    items = "".join(f"<li>{escape(line)}</li>" for line in detail_lines)
                    warning_html = f'<div class="im-ketentuan-warning-box"><ul class="im-ketentuan-warning-list">{items}</ul></div>'
                else:
                    warning_html = f'<div class="im-ketentuan-warning-box">{escape(detail_lines[0])}</div>'

        items_html += dedent(f"""
        <div class="im-ketentuan-item {item_class}">
            <div class="im-ketentuan-row">
                <span class="{icon_class}">{icon}</span>
                <span class="im-ketentuan-text">{label}</span>
            </div>
            {warning_html}
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
    data = _get_refined_history_data()

    per_page = 7
    total = len(data)
    total_pages = max(1, (total + per_page - 1) // per_page)

    if "im_hist_page" not in st.session_state:
        st.session_state.im_hist_page = 1

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
        elif s == "deleted":
            return '<span class="im-status-badge im-status-deleted"><span class="status-dot"></span>Deleted</span>'
        return '<span class="im-status-badge im-status-success"><span class="status-dot"></span>' + status + '</span>'

    # Build dot class
    def _dot_class(status):
        s = status.lower()
        if s == "success": return "dot-success"
        if s == "warning": return "dot-warning"
        if s == "failed": return "dot-failed"
        if s == "deleted": return "dot-deleted"
        return "dot-success"

    # Build rows
    rows_html = ""
    for r in page_data:
        rs_html = f'<span class="im-rs-total">{r["rs_total"]}</span>' if r["rs_total"] else '<span class="im-rs-empty">—</span>'
        if r["status"].lower() == "deleted":
            action_content = '<span style="color:#94a3b8;font-size:11.5px;font-weight:500;padding-left:8px;">—</span>'
        else:
            icon_view = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>'
            icon_reload = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>'
            icon_download = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>'
            icon_delete = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>'
            action_content = (
                f'<button data-im-action="view_import" data-im-id="{r["import_id"]}" class="im-action-btn" title="View">{icon_view}</button>'
                f'<button data-im-action="download_import" data-im-id="{r["import_id"]}" class="im-action-btn" title="Download">{icon_download}</button>'
                f'<button data-im-action="reload_import" data-im-id="{r["import_id"]}" class="im-action-btn" title="Reload">{icon_reload}</button>'
                f'<button data-im-action="delete_import" data-im-id="{r["import_id"]}" class="im-action-btn btn-delete" title="Delete">{icon_delete}</button>'
            )

        uploader_role_html = f'<div class="im-uploader-role">{r["role"]}</div>'
        if r["status"].lower() == "deleted" and r.get("deleted_by"):
            uploader_role_html += f'<div style="font-size:10px;color:#ef4444;font-weight:600;margin-top:1px;">Dihapus oleh: {r["deleted_by"]}</div>'

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
            f'{uploader_role_html}'
            '</div>'
            '</div>'
            '</td>'
            '<td>'
            f'<div class="im-records-val">{f"{r["total_records"]:,}".replace(",", ".")}</div>'
            '<div class="im-records-sub">rows</div>'
            '</td>'
            f'<td><span class="im-tenants-link">{f"{r["tenants"]:,}".replace(",", ".")}</span></td>'
            f'<td><span class="im-filesize">{r["file_size"]}</span></td>'
            f'<td>{rs_html}</td>'
            f'<td>{_hist_status(r["status"])}</td>'
            '<td>'
            f'<div class="im-action-btns">{action_content}</div>'
            '</td>'
            '</tr>'
        )

    if not rows_html:
        rows_html = '<tr><td colspan="9" style="text-align:center;color:#94a3b8;padding:30px;">Belum ada data import yang tersedia.</td></tr>'

    history_html = (
        '<div class="im-panel im-history">'
        '<div class="im-history-head">'
        '<div class="im-history-head-left">'
        '<div class="im-section-title">Upload History</div>'
        '<div class="im-section-sub">All import sessions — most recent first</div>'
        '</div>'
        '<div class="im-history-actions">'
        '<button data-im-action="refresh" class="im-btn-refresh">Refresh</button>'
        '<button data-im-action="clear_trash" class="im-btn-export btn-clear-trash">Clear Trash</button>'
        '</div>'
        '</div>'
        '<div style="overflow-x:auto; margin-bottom: 0px !important;">'
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
        '</div>'
    )
    st.markdown(history_html, unsafe_allow_html=True)

    # Render standardized pagination below the table card
    st.markdown('<div class="overview-detail-pagination-footer-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    im_page_input = render_pagination(
        current_page=st.session_state.im_hist_page,
        total_pages=total_pages,
        first_item=start_idx + 1,
        last_item=end_idx,
        total_rows=total,
        sync_key="im_hist_page_sync",
    )

    if im_page_input and im_page_input.isdigit():
        new_page = int(im_page_input)
        if new_page != st.session_state.im_hist_page:
            st.session_state.im_hist_page = new_page
            st.rerun()


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
                <button data-im-action="top_refresh" class="im-top-refresh-btn" title="Reset/Upload Another">↻</button>
            </div>
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

            # Render uploader inside the overlay.
            # No `type=` restriction here on purpose: Streamlit silently
            # rejects mismatched files at the picker/drop level when `type`
            # is set, leaving `uploaded` as None with no visible feedback
            # (its own rejection message renders behind our invisible
            # overlay). Accepting anything and validating it ourselves below
            # lets the existing "Format file tidak didukung" error actually
            # surface to the user.
            uploaded = st.file_uploader(
                "Browse Files",
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

                    # Setiap file yang benar-benar baru dipilih di browser (bahkan
                    # kalau nama & isinya identik dengan upload sebelumnya) dapat
                    # `file_id` baru dari Streamlit — beda dengan rerun biasa saat
                    # file yang sama masih "duduk" di uploader, yang mengembalikan
                    # objek UploadedFile yang sama persis. Memakai file_id (bukan
                    # nama file) supaya re-upload file yang identik tetap memicu
                    # pengecekan duplikat ke database, bukan diam-diam dilewati.
                    current_file_id = getattr(uploaded, "file_id", uploaded.name)
                    if st.session_state.im_import_ready and st.session_state.get("im_file_attempt_id") != current_file_id:
                        success, result = _save_to_database()
                        st.session_state.im_file_attempt_id = current_file_id
                        st.session_state.im_last_save_ok = success
                        st.session_state.im_last_save_result = result
                        if result.get("severity") != "success":
                            _render_save_result_notice(result)
                    elif st.session_state.get("im_last_save_ok") is False:
                        # File yang sama masih terpilih dan percobaan simpan
                        # sebelumnya gagal (duplikat) — tampilkan lagi errornya
                        # secara konsisten, bukannya diam saja seolah berhasil.
                        last_result = st.session_state.get("im_last_save_result")
                        if last_result:
                            _render_save_result_notice(last_result)

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

                    # Jangan tampilkan kartu "Upload Successful" kalau file ini
                    # justru gagal/tidak tersimpan ke database (mis. duplikat) —
                    # kartu hijau ini dulu selalu muncul terlepas dari hasil
                    # simpan yang sebenarnya, jadi tampak seolah upload berhasil
                    # padahal datanya tidak masuk.
                    if st.session_state.get("im_last_save_ok") is not False:
                        st.markdown(success_html, unsafe_allow_html=True)

                except Exception as exc:
                    st.error(f"Gagal memproses file: {exc}")
                    all_valid = False

            if not all_valid:
                # Render the drag & drop zone in failed visual state, keeping it interactive
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
                        <div class="im-dropzone-subtitle" style="margin-bottom: 12px;">File Terunggah: <strong>{uploaded.name}</strong></div>
                        <div class="im-validation-error-card">
                            <div class="im-validation-error-title">Kesalahan Validasi File</div>
                            <div class="im-validation-error-desc">Silakan perbaiki kesalahan di bawah ini sebelum mengunggah kembali.</div>
                        </div>
                    </div>
                    <div class="im-uploader-overlay">
                """, unsafe_allow_html=True)

                # Render the overlay file uploader so they can drop a new file.
                # No `type=` restriction — see comment on the other
                # file_uploader call above for why.
                st.file_uploader(
                    "Browse Files",
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

        st.markdown("</div>", unsafe_allow_html=True)

    # ── RIGHT: Ketentuan Import (white card) ──
    with right:
        is_uploaded = st.session_state.get(uploader_key) is not None
        _render_ketentuan_import(st.session_state.get("im_validation"), is_uploaded=is_uploaded)

    # ── Riwayat Import table ──
    _render_import_history_refined()


def _patch_upload_limit_text():
    components.html(
        """
        <script>
        (function () {
            try {
                const doc = window.parent.document;
                const win = window.parent;

                // Suppress browser default navigation on real OS file drag-and-drop
                if (!win.__imDragGuardInstalled) {
                    win.__imDragGuardInstalled = true;
                    ["dragover", "drop"].forEach((evtName) => {
                        win.addEventListener(evtName, (e) => {
                            if (!e.target.closest('[data-testid="stFileUploaderDropzone"]')) {
                                e.preventDefault();
                            }
                        }, false);
                    });
                }

                function patchUploadLimit() {
                    try {
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
                    } catch (err) {
                        console.error("[ImportManager] Error in patchUploadLimit:", err);
                    }
                }



                function triggerAction(actionName) {
                    try {
                        const input = doc.querySelector('input[placeholder="__im_action_trigger__"]');
                        if (!input) return;

                        input.focus();

                        let prototype = Object.getPrototypeOf(input);
                        let nativeSetter = null;
                        while (prototype) {
                            const desc = Object.getOwnPropertyDescriptor(prototype, 'value');
                            if (desc && desc.set) {
                                nativeSetter = desc.set;
                                break;
                            }
                            prototype = Object.getPrototypeOf(prototype);
                        }

                        if (nativeSetter) {
                            nativeSetter.call(input, actionName);
                        } else {
                            input.value = actionName;
                        }

                        const tracker = input._valueTracker;
                        if (tracker) {
                            tracker.setValue('');
                        }

                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));

                        input.dispatchEvent(new KeyboardEvent('keydown', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true
                        }));

                        input.blur();
                    } catch (err) {
                        console.error("[ImportManager] Error sending action to Python:", err);
                    }
                }

                function handleActionClick(e) {
                    try {
                        const btn = e.target.closest('[data-im-action]');
                        if (!btn) return;

                        e.preventDefault();
                        e.stopPropagation();

                        const action = btn.getAttribute('data-im-action');
                        const id = btn.getAttribute('data-im-id') || '';
                        const triggerValue = id ? (action + ':' + id) : action;

                        console.log("[ImportManager] Action intercepted:", triggerValue);
                        triggerAction(triggerValue);
                    } catch (err) {
                        console.error("[ImportManager] Error during action click interception:", err);
                    }
                }

                // Safely install/re-install the click listener to prevent duplicate / stale handlers
                if (win.__imActionHandler) {
                    doc.removeEventListener('click', win.__imActionHandler, true);
                }
                win.__imActionHandler = handleActionClick;
                doc.addEventListener('click', win.__imActionHandler, true);

                function hideActionTriggerInput() {
                    try {
                        const input = doc.querySelector('input[placeholder="__im_action_trigger__"]');
                        if (input) {
                            const container = input.closest('[data-testid="stElementContainer"]');
                            if (container) {
                                container.style.position = 'fixed';
                                container.style.top = '-9999px';
                                container.style.left = '-9999px';
                                container.style.width = '1px';
                                container.style.height = '1px';
                                container.style.overflow = 'hidden';
                                container.style.opacity = '0';
                                container.style.pointerEvents = 'none';
                            }
                        }
                    } catch (err) {
                        console.error("[ImportManager] Error in hideActionTriggerInput:", err);
                    }
                }

                function checkModalClosure() {
                    try {
                        const modal = doc.querySelector('[data-testid="stModal"]');
                        if (modal) {
                            win.__imModalWasOpen = true;
                        } else if (win.__imModalWasOpen) {
                            win.__imModalWasOpen = false;
                            console.log("[ImportManager] Modal closure detected.");
                            triggerAction("close_dialog");
                        }
                    } catch (err) {
                        console.error("[ImportManager] Error checking modal closure:", err);
                    }
                }

                patchUploadLimit();
                hideActionTriggerInput();

                const observer = new MutationObserver(() => {
                    patchUploadLimit();
                    hideActionTriggerInput();
                    checkModalClosure();
                });

                observer.observe(doc.body, {
                    childList: true,
                    subtree: true,
                    characterData: true,
                });
            } catch (globalErr) {
                console.error("[ImportManager] Global initialization error:", globalErr);
            }
        })();
        </script>
        """,
        height=0,
        width=0,
    )


_DIALOG_ACTIONS = {"view_import", "download_import", "delete_import", "clear_trash"}


def render_import_manager():
    _init_state()

    # ── Route actions ──────────────────────────────────────────────────────────
    # Prefer JS-triggered pending action (no page reload); fall back to query params
    # (kept for backward compatibility with direct URL navigation).
    _pending = st.session_state.get("_im_action_pending", "")
    if _pending:
        del st.session_state["_im_action_pending"]
        action, _, import_id = _pending.partition(":")
    else:
        action = st.query_params.get("action", "")
        import_id = st.query_params.get("import_id", "")

    if action == "refresh":
        if "action" in st.query_params:
            del st.query_params["action"]
        st.rerun()
    elif action == "top_refresh":
        st.session_state.uploader_version = st.session_state.get("uploader_version", 0) + 1
        if SHARED_DATA_KEY in st.session_state:
            del st.session_state[SHARED_DATA_KEY]
        if SHARED_META_KEY in st.session_state:
            del st.session_state[SHARED_META_KEY]
        st.session_state.im_file = None
        st.session_state.im_import_ready = False
        st.session_state.im_validation = {key: False for key, _ in KETENTUAN_RULES}
        st.session_state.pop("im_file_attempt_id", None)
        st.session_state.pop("im_last_save_ok", None)
        st.session_state.pop("im_last_save_result", None)
        st.rerun()
    elif action == "close_dialog":
        st.session_state["_im_open_dialog"] = None
        st.rerun()
    elif action == "reload_import" and import_id:
        try:
            execute_reload_import(int(import_id))
        except Exception:
            pass
        if "action" in st.query_params:
            del st.query_params["action"]
        if "import_id" in st.query_params:
            del st.query_params["import_id"]
    elif action in _DIALOG_ACTIONS:
        # Dialogs must be re-invoked on every rerun to stay open (Streamlit
        # closes a dialog the moment its opening call is skipped on a rerun,
        # which is exactly what happened when this was a one-shot trigger:
        # the very next rerun — e.g. clicking a button inside the dialog —
        # didn't call the dialog function again, so it vanished instantly).
        st.session_state["_im_open_dialog"] = (action, import_id)
        if "action" in st.query_params:
            del st.query_params["action"]
        if "import_id" in st.query_params:
            del st.query_params["import_id"]

    # Re-open whichever dialog is currently active on every rerun, until a
    # dialog handler explicitly clears "_im_open_dialog".
    _open = st.session_state.get("_im_open_dialog")
    if _open:
        d_action, d_id = _open
        try:
            if d_action == "view_import":
                show_import_details_dialog(int(d_id))
            elif d_action == "download_import":
                show_download_dialog(int(d_id))
            elif d_action == "delete_import":
                show_delete_confirm_dialog(int(d_id))
            elif d_action == "clear_trash":
                show_clear_trash_dialog()
        except Exception:
            st.session_state["_im_open_dialog"] = None

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

    # ── JS-action bridge ──────────────────────────────────────────────────────
    # Hidden text input placed LAST so it renders after all CSS (no flash).
    # The CSS rule in _REFINED_IMPORT_CSS and the JS in _patch_upload_limit_text
    # both hide it. The callback is called inline when st.text_input runs and
    # the widget value changed; it then calls st.rerun() so the NEXT run routes
    # the action (via _im_action_pending) without any extra elements at the top
    # of the page that would disturb the layout.
    def _on_action_trigger_change():
        val = st.session_state.get("im_js_action_trigger", "")
        if val:
            st.session_state["_im_action_pending"] = val
            st.session_state["im_js_action_trigger"] = ""
            st.rerun()

    st.text_input(
        "im_action",
        key="im_js_action_trigger",
        label_visibility="collapsed",
        placeholder="__im_action_trigger__",
        on_change=_on_action_trigger_change,
    )


@st.dialog("Detail Data Import", width="large")
def show_import_details_dialog(import_id):
    from .connection import get_engine
    from sqlalchemy import text
    import pandas as pd
    
    st.write(f"Menampilkan data transaksi untuk **Import ID: {import_id}**")
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            meta = pd.read_sql(
                text("SELECT filename, periode, uploaded_by, uploaded_at FROM import_history WHERE import_id = :import_id"),
                conn,
                params={"import_id": import_id}
            )
            df = pd.read_sql(
                text("""
                    SELECT document_date, masa_jasa, tahun, perusahaan, brand, perimeter_spending_pax,
                           kode_ruang, pic, ro_number, terminal, sub_terminal, area, lokasi, lantai, gate,
                           smoking_status, sub_bidang_usaha, bidang_usaha, coa, nomor_kontrak_sistem,
                           nomor_kontrak_legal, start_kontrak, end_kontrak, csp_non_csp, kerja_sama,
                           pemilihan_mitra_usaha, produksi_m2, tarif_sewa_ruang_m2, rs_percent, min_omzet,
                           real_omzet, mgrs_per_pax, real_pax, pendapatan_rs, pendapatan_sewa, total_kontribusi,
                           acv, rev_per_sqm, spending_per_pax, doc_number_rs, doc_number_sewa, variant_no,
                           catatan, trafik_int_arr, trafik_int_dep, subtotal_trafik_int, trafik_dom_arr,
                           trafik_dom_dep, subtotal_trafik_dom, total_trafik
                    FROM transaction_revenue
                    WHERE import_id = :import_id
                """),
                conn,
                params={"import_id": import_id}
            )
            
        if meta.empty:
            st.error("Data riwayat import tidak ditemukan.")
            return
            
        row = meta.iloc[0]
        st.markdown(f"""
        **File:** `{row.get('filename')}` | **Uploader:** `{row.get('uploaded_by')}` | **Tanggal:** `{row.get('uploaded_at')}`
        """)
        
        if df.empty:
            st.warning("Tidak ada transaksi untuk import ini.")
        else:
            for col in ["document_date", "start_kontrak", "end_kontrak"]:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: pd.to_datetime(x).strftime("%Y-%m-%d") if pd.notna(x) else "-")
            if "masa_jasa" in df.columns:
                df["masa_jasa"] = df["masa_jasa"].apply(lambda x: pd.to_datetime(x).strftime("%b-%y") if pd.notna(x) else "-")
            df = df.fillna("-").replace({None: "-", "None": "-", "nan": "-", "NaN": "-"})
            
            rename_map = {
                "document_date": "DOCUMENT DATE",
                "masa_jasa": "MASA",
                "tahun": "TAHUN",
                "perusahaan": "PERUSAHAAN",
                "brand": "BRAND",
                "perimeter_spending_pax": "PERIMETER / SPENDING / PAX",
                "kode_ruang": "KODE RUANG",
                "pic": "PIC",
                "ro_number": "RO NUMBER",
                "terminal": "TERMINAL",
                "sub_terminal": "SUB TERMINAL",
                "area": "AREA",
                "lokasi": "LOKASI",
                "lantai": "LANTAI",
                "gate": "GATE",
                "smoking_status": "SMOKING STATUS",
                "sub_bidang_usaha": "SUB BIDANG USAHA",
                "bidang_usaha": "BIDANG USAHA",
                "coa": "COA",
                "nomor_kontrak_sistem": "NOMOR KONTRAK SISTEM (SAP)",
                "nomor_kontrak_legal": "NOMOR KONTRAK LEGAL",
                "start_kontrak": "START KONTRAK",
                "end_kontrak": "END KONTRAK",
                "csp_non_csp": "CSP / NON-CSP",
                "kerja_sama": "KERJA SAMA",
                "pemilihan_mitra_usaha": "PEMILIHAN MITRA USAHA",
                "produksi_m2": "PRODUKSI (M2)",
                "tarif_sewa_ruang_m2": "TARIF SEWA RUANG / M2",
                "rs_percent": "% RS",
                "min_omzet": "MIN OMZET",
                "real_omzet": "REAL OMZET",
                "mgrs_per_pax": "MGRS / PAX",
                "real_pax": "REAL PAX",
                "pendapatan_rs": "PENDAPATAN RS",
                "pendapatan_sewa": "PENDAPATAN SEWA",
                "total_kontribusi": "TOTAL KONTRIBUSI",
                "acv": "ACV",
                "rev_per_sqm": "REV / SQM",
                "spending_per_pax": "SPENDING / PAX",
                "doc_number_rs": "DOC. NUMBER RS",
                "doc_number_sewa": "DOC. NUMBER SEWA",
                "variant_no": "VARIANT NO",
                "catatan": "CATATAN",
                "trafik_int_arr": "TRAFIK INT ARR",
                "trafik_int_dep": "TRAFIK INT DEP",
                "subtotal_trafik_int": "SUBTOTAL TRAFIK INT",
                "trafik_dom_arr": "TRAFIK DOM ARR",
                "trafik_dom_dep": "TRAFIK DOM DEP",
                "subtotal_trafik_dom": "SUBTOTAL TRAFIK DOM",
                "total_trafik": "TOTAL TRAFIK",
            }
            df = df.rename(columns=rename_map)
            
            template_order = [
                "DOCUMENT DATE", "MASA", "TAHUN", "PERUSAHAAN", "BRAND", "PERIMETER / SPENDING / PAX",
                "KODE RUANG", "PIC", "RO NUMBER", "TERMINAL", "SUB TERMINAL", "AREA", "LOKASI", "LANTAI",
                "GATE", "SMOKING STATUS", "SUB BIDANG USAHA", "BIDANG USAHA", "COA",
                "NOMOR KONTRAK SISTEM (SAP)", "NOMOR KONTRAK LEGAL", "START KONTRAK", "END KONTRAK",
                "CSP / NON-CSP", "KERJA SAMA", "PEMILIHAN MITRA USAHA", "PRODUKSI (M2)", "TARIF SEWA RUANG / M2",
                "% RS", "MIN OMZET", "REAL OMZET", "MGRS / PAX", "REAL PAX", "PENDAPATAN RS", "PENDAPATAN SEWA",
                "TOTAL KONTRIBUSI", "ACV", "REV / SQM", "SPENDING / PAX", "DOC. NUMBER RS", "DOC. NUMBER SEWA",
                "VARIANT NO", "CATATAN", "TRAFIK INT ARR", "TRAFIK INT DEP", "SUBTOTAL TRAFIK INT",
                "TRAFIK DOM ARR", "TRAFIK DOM DEP", "SUBTOTAL TRAFIK DOM", "TOTAL TRAFIK"
            ]
            df = df[[col for col in template_order if col in df.columns]]
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Gagal mengambil detail data: {e}")


@st.dialog("Unduh Data Import")
def show_download_dialog(import_id):
    from .connection import get_engine
    from sqlalchemy import text
    import pandas as pd
    import io
    
    st.write(f"Mempersiapkan unduhan untuk **Import ID: {import_id}**...")
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            meta = pd.read_sql(
                text("SELECT filename FROM import_history WHERE import_id = :import_id"),
                conn,
                params={"import_id": import_id}
            )
            df = pd.read_sql(
                text("""
                    SELECT document_date, masa_jasa, tahun, perusahaan, brand, perimeter_spending_pax,
                           kode_ruang, pic, ro_number, terminal, sub_terminal, area, lokasi, lantai, gate,
                           smoking_status, sub_bidang_usaha, bidang_usaha, coa, nomor_kontrak_sistem,
                           nomor_kontrak_legal, start_kontrak, end_kontrak, csp_non_csp, kerja_sama,
                           pemilihan_mitra_usaha, produksi_m2, tarif_sewa_ruang_m2, rs_percent, min_omzet,
                           real_omzet, mgrs_per_pax, real_pax, pendapatan_rs, pendapatan_sewa, total_kontribusi,
                           acv, rev_per_sqm, spending_per_pax, doc_number_rs, doc_number_sewa, variant_no,
                           catatan, trafik_int_arr, trafik_int_dep, subtotal_trafik_int, trafik_dom_arr,
                           trafik_dom_dep, subtotal_trafik_dom, total_trafik
                    FROM transaction_revenue
                    WHERE import_id = :import_id
                """),
                conn,
                params={"import_id": import_id}
            )
            
        if df.empty:
            st.error("Data tidak ditemukan atau kosong.")
            return
            
        filename = meta.iloc[0]["filename"] if not meta.empty else f"import_{import_id}.xlsx"
        if not filename.endswith((".xlsx", ".xls")):
            filename = f"{filename}.xlsx"
            
        for col in ["document_date", "start_kontrak", "end_kontrak"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: pd.to_datetime(x).strftime("%Y-%m-%d") if pd.notna(x) else "-")
        if "masa_jasa" in df.columns:
            df["masa_jasa"] = df["masa_jasa"].apply(lambda x: pd.to_datetime(x).strftime("%b-%y") if pd.notna(x) else "-")
        df = df.fillna("-").replace({None: "-", "None": "-", "nan": "-", "NaN": "-"})
        
        rename_map = {
            "document_date": "DOCUMENT DATE",
            "masa_jasa": "MASA",
            "tahun": "TAHUN",
            "perusahaan": "PERUSAHAAN",
            "brand": "BRAND",
            "perimeter_spending_pax": "PERIMETER / SPENDING / PAX",
            "kode_ruang": "KODE RUANG",
            "pic": "PIC",
            "ro_number": "RO NUMBER",
            "terminal": "TERMINAL",
            "sub_terminal": "SUB TERMINAL",
            "area": "AREA",
            "lokasi": "LOKASI",
            "lantai": "LANTAI",
            "gate": "GATE",
            "smoking_status": "SMOKING STATUS",
            "sub_bidang_usaha": "SUB BIDANG USAHA",
            "bidang_usaha": "BIDANG USAHA",
            "coa": "COA",
            "nomor_kontrak_sistem": "NOMOR KONTRAK SISTEM (SAP)",
            "nomor_kontrak_legal": "NOMOR KONTRAK LEGAL",
            "start_kontrak": "START KONTRAK",
            "end_kontrak": "END KONTRAK",
            "csp_non_csp": "CSP / NON-CSP",
            "kerja_sama": "KERJA SAMA",
            "pemilihan_mitra_usaha": "PEMILIHAN MITRA USAHA",
            "produksi_m2": "PRODUKSI (M2)",
            "tarif_sewa_ruang_m2": "TARIF SEWA RUANG / M2",
            "rs_percent": "% RS",
            "min_omzet": "MIN OMZET",
            "real_omzet": "REAL OMZET",
            "mgrs_per_pax": "MGRS / PAX",
            "real_pax": "REAL PAX",
            "pendapatan_rs": "PENDAPATAN RS",
            "pendapatan_sewa": "PENDAPATAN SEWA",
            "total_kontribusi": "TOTAL KONTRIBUSI",
            "acv": "ACV",
            "rev_per_sqm": "REV / SQM",
            "spending_per_pax": "SPENDING / PAX",
            "doc_number_rs": "DOC. NUMBER RS",
            "doc_number_sewa": "DOC. NUMBER SEWA",
            "variant_no": "VARIANT NO",
            "catatan": "CATATAN",
            "trafik_int_arr": "TRAFIK INT ARR",
            "trafik_int_dep": "TRAFIK INT DEP",
            "subtotal_trafik_int": "SUBTOTAL TRAFIK INT",
            "trafik_dom_arr": "TRAFIK DOM ARR",
            "trafik_dom_dep": "TRAFIK DOM DEP",
            "subtotal_trafik_dom": "SUBTOTAL TRAFIK DOM",
            "total_trafik": "TOTAL TRAFIK",
        }
        df = df.rename(columns=rename_map)
        
        template_order = [
            "DOCUMENT DATE", "MASA", "TAHUN", "PERUSAHAAN", "BRAND", "PERIMETER / SPENDING / PAX",
            "KODE RUANG", "PIC", "RO NUMBER", "TERMINAL", "SUB TERMINAL", "AREA", "LOKASI", "LANTAI",
            "GATE", "SMOKING STATUS", "SUB BIDANG USAHA", "BIDANG USAHA", "COA",
            "NOMOR KONTRAK SISTEM (SAP)", "NOMOR KONTRAK LEGAL", "START KONTRAK", "END KONTRAK",
            "CSP / NON-CSP", "KERJA SAMA", "PEMILIHAN MITRA USAHA", "PRODUKSI (M2)", "TARIF SEWA RUANG / M2",
            "% RS", "MIN OMZET", "REAL OMZET", "MGRS / PAX", "REAL PAX", "PENDAPATAN RS", "PENDAPATAN SEWA",
            "TOTAL KONTRIBUSI", "ACV", "REV / SQM", "SPENDING / PAX", "DOC. NUMBER RS", "DOC. NUMBER SEWA",
            "VARIANT NO", "CATATAN", "TRAFIK INT ARR", "TRAFIK INT DEP", "SUBTOTAL TRAFIK INT",
            "TRAFIK DOM ARR", "TRAFIK DOM DEP", "SUBTOTAL TRAFIK DOM", "TOTAL TRAFIK"
        ]
        df = df[[col for col in template_order if col in df.columns]]
        
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data Revenue")
        towrite.seek(0)
        
        st.markdown(f"""
        <div class="im-dl-success">
            <div class="im-dl-success-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </div>
            <div class="im-dl-success-text">
                <div class="im-dl-success-title">File Excel berhasil dibuat!</div>
                <div class="im-dl-success-sub">{filename} &middot; {len(df)} baris data</div>
            </div>
        </div>
        <style>
        .im-dl-success {{
            display: flex;
            align-items: center;
            gap: 12px;
            background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.08) 100%);
            border: 1px solid rgba(99,102,241,0.18);
            border-radius: 12px;
            padding: 14px 16px;
            margin: 4px 0 18px 0;
        }}
        .im-dl-success-icon {{
            flex: 0 0 auto;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            box-shadow: 0 3px 10px rgba(99,102,241,0.35);
        }}
        .im-dl-success-icon svg {{ width: 18px; height: 18px; }}
        .im-dl-success-title {{
            font-size: 13.5px;
            font-weight: 700;
            color: #1e1b4b;
        }}
        .im-dl-success-sub {{
            font-size: 12px;
            color: #64748b;
            margin-top: 2px;
        }}
        div[data-testid="stDialog"] div[data-testid="stDownloadButton"] > button {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 8px !important;
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 10px !important;
            height: 42px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 14px rgba(99,102,241,0.30) !important;
            transition: all 0.15s ease-in-out !important;
        }}
        div[data-testid="stDialog"] div[data-testid="stDownloadButton"] > button:hover {{
            box-shadow: 0 6px 18px rgba(99,102,241,0.42) !important;
            transform: translateY(-1px) !important;
        }}
        div[data-testid="stDialog"] div[data-testid="stDownloadButton"] > button::before {{
            content: "" !important;
            display: inline-block !important;
            width: 16px !important;
            height: 16px !important;
            background-color: #ffffff !important;
            -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 384 512'%3E%3Cpath d='M0 64C0 28.7 28.7 0 64 0H224V128c0 17.7 14.3 32 32 32H384V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zM384 128H256V0L384 128zM216 232c0-13.3-10.7-24-24-24s-24 10.7-24 24v99.9l-31-31c-9.4-9.4-24.6-9.4-33.9 0s-9.4 24.6 0 33.9l72 72c9.4 9.4 24.6 9.4 33.9 0l72-72c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-31 31V232z'/%3E%3C/svg%3E") no-repeat center / contain !important;
            mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 384 512'%3E%3Cpath d='M0 64C0 28.7 28.7 0 64 0H224V128c0 17.7 14.3 32 32 32H384V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zM384 128H256V0L384 128zM216 232c0-13.3-10.7-24-24-24s-24 10.7-24 24v99.9l-31-31c-9.4-9.4-24.6-9.4-33.9 0s-9.4 24.6 0 33.9l72 72c9.4 9.4 24.6 9.4 33.9 0l72-72c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-31 31V232z'/%3E%3C/svg%3E") no-repeat center / contain !important;
        }}
        </style>
        """, unsafe_allow_html=True)

        st.download_button(
            label="Download File Excel",
            data=towrite,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Gagal memproses unduhan: {e}")


@st.dialog("Hapus Data Import")
def show_delete_confirm_dialog(import_id):
    from .connection import get_engine
    from sqlalchemy import text
    import pandas as pd
    import time
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            meta = pd.read_sql(
                text("SELECT filename FROM import_history WHERE import_id = :import_id"),
                conn,
                params={"import_id": import_id}
            )
        filename = meta.iloc[0]["filename"] if not meta.empty else f"ID {import_id}"
        
        st.warning(f"Apakah Anda yakin ingin menghapus data import dari file **{filename}**?")
        st.write("Tindakan ini akan menghapus semua data transaksi yang terkait dan tidak dapat dibatalkan.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ya, Hapus Data", use_container_width=True, type="primary"):
                with engine.begin() as trans_conn:
                    try:
                        trans_conn.execute(text("ALTER TABLE import_history ADD COLUMN IF NOT EXISTS deleted_by VARCHAR(255)"))
                    except Exception:
                        pass
                    trans_conn.execute(
                        text("DELETE FROM transaction_revenue WHERE import_id = :import_id"),
                        {"import_id": import_id}
                    )
                    trans_conn.execute(
                        text("UPDATE import_history SET is_active = false, status = 'Deleted', deleted_by = :deleted_by WHERE import_id = :import_id"),
                        {
                            "import_id": import_id,
                            "deleted_by": st.session_state.get("user_name", "Operational User")
                        }
                    )
                st.cache_data.clear()
                st.session_state.pop("shared_import_df", None)
                st.session_state.pop("shared_import_meta", None)
                st.session_state.pop("shared_import_mapping", None)
                st.session_state["_im_open_dialog"] = None
                st.success("Data berhasil dihapus!")
                time.sleep(1)
                st.rerun()
        with col2:
            if st.button("Batal", use_container_width=True):
                st.session_state["_im_open_dialog"] = None
                st.rerun()
    except Exception as e:
        st.error(f"Gagal menghapus data: {e}")


def execute_reload_import(import_id):
    from .connection import get_engine
    from sqlalchemy import text
    import time
    
    st.toast(f"Memulai memuat ulang data untuk Import ID: {import_id}...", icon="🔄")
    try:
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE import_history SET status = 'Success' WHERE import_id = :import_id"),
                {"import_id": import_id}
            )
        st.cache_data.clear()
        st.success("Data berhasil dimuat ulang!")
        time.sleep(0.5)
        st.rerun()
    except Exception as e:
        st.error(f"Gagal memuat ulang data: {e}")


@st.dialog("Hapus Semua Riwayat Deleted")
def show_clear_trash_dialog():
    from .connection import get_engine
    from sqlalchemy import text
    import time
    
    st.warning("Apakah Anda yakin ingin menghapus permanen semua riwayat file yang sudah di-delete?")
    st.write("Tindakan ini akan membersihkan log riwayat 'Deleted' dari database secara permanen.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ya, Bersihkan", use_container_width=True, type="primary"):
            try:
                engine = get_engine()
                with engine.begin() as conn:
                    conn.execute(
                        text("DELETE FROM import_history WHERE status = 'Deleted' OR COALESCE(is_active, true) = false")
                    )
                st.cache_data.clear()
                st.session_state["_im_open_dialog"] = None
                st.success("Riwayat berhasil dibersihkan!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Gagal membersihkan: {e}")
    with col2:
        if st.button("Batal", use_container_width=True):
            st.session_state["_im_open_dialog"] = None
            st.rerun()


if __name__ == "__main__":
    st.set_page_config(page_title="Data Import Manager", layout="wide")
    render_import_manager()
