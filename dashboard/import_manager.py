import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
from textwrap import dedent
import time

from .shared_import import (
    get_shared_import_meta,
    store_shared_import,
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

def _get_belum_submit():
    return ["Manado", "Kupang", "Sorong"]


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
_PAGE_CSS = """
<style>
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
.im-page-head {
    display: grid;
    grid-template-columns: minmax(220px, 1.25fr) minmax(260px, 0.95fr) minmax(210px, 0.7fr);
    gap: 18px;
    align-items: center;
    margin-bottom: 10px;
}
.im-page-title {
    font-size: 24px;
    font-weight: 850;
    color: #0f172a;
    line-height: 1.15;
}
.im-page-subtitle {
    margin-top: 4px;
    font-size: 12px;
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
    width: 38px;
    height: 38px;
    border-radius: 14px;
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
    width: 38px;
    height: 38px;
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
    grid-template-columns: minmax(0, 1.55fr) minmax(320px, 0.9fr);
    gap: 18px;
    align-items: start;
}
.im-panel {
    background: rgba(255,255,255,0.56);
    backdrop-filter: blur(26px);
    -webkit-backdrop-filter: blur(26px);
    border: 1px solid rgba(255,255,255,0.90);
    border-radius: 20px;
    box-shadow:
        0 8px 32px rgba(99,102,241,0.07),
        0 2px 8px rgba(0,0,0,0.025),
        inset 0 1px 0 rgba(255,255,255,1);
}
.im-upload-shell {
    padding: 18px;
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
.im-upload-visual {
    border: 2px dashed rgba(99,102,241,0.30);
    border-radius: 18px;
    min-height: 220px;
    padding: 34px 24px;
    text-align: center;
    background:
        linear-gradient(135deg,rgba(255,255,255,0.66),rgba(255,255,255,0.42)),
        radial-gradient(circle at 50% 0%,rgba(99,102,241,0.08),transparent 55%);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
.im-cloud {
    width: 62px;
    height: 62px;
    border-radius: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 13px;
    color: #4f46e5;
    font-size: 26px;
    font-weight: 900;
    background: rgba(255,255,255,0.74);
    border: 1px solid rgba(255,255,255,0.96);
    box-shadow: 0 8px 24px rgba(99,102,241,0.11);
}
.im-upload-title {
    font-size: 16px;
    font-weight: 850;
    color: #1e293b;
    margin-bottom: 4px;
}
.im-upload-copy {
    font-size: 11.5px;
    line-height: 1.55;
    color: #64748b;
    max-width: 420px;
}
.im-uploader-slot {
    margin-top: 12px;
}
.im-uploader-slot [data-testid="stFileUploader"] section {
    min-height: 56px !important;
    padding: 12px 16px !important;
    border-radius: 14px !important;
}
.im-file-card {
    margin-top: 16px;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 16px;
    border-radius: 16px;
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(255,255,255,0.94);
    box-shadow: 0 8px 28px rgba(99,102,241,0.09);
}
.im-file-card.is-empty {
    border-style: dashed;
    box-shadow: none;
    background: rgba(255,255,255,0.44);
}
.im-file-icon {
    width: 44px;
    height: 44px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    background: linear-gradient(135deg,#059669,#10b981);
    color: #fff;
    font-size: 14px;
    font-weight: 900;
    box-shadow: 0 6px 18px rgba(16,185,129,0.24);
}
.im-file-card.is-empty .im-file-icon {
    background: linear-gradient(135deg,#94a3b8,#64748b);
    box-shadow: none;
}
.im-file-name {
    font-size: 13.5px;
    font-weight: 800;
    color: #1e293b;
    overflow-wrap: anywhere;
}
.im-file-meta {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 2px;
}
.im-delete {
    margin-left: auto;
    width: 34px;
    height: 34px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #dc2626;
    font-size: 13px;
    font-weight: 900;
    background: rgba(239,68,68,0.10);
    border: 1px solid rgba(239,68,68,0.20);
}
.im-side-stack {
    display: flex;
    flex-direction: column;
    gap: 14px;
}
.im-side-control {
    padding: 16px 16px 14px;
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
    padding: 17px 18px 13px;
    border-bottom: 1px solid rgba(99,102,241,0.08);
}
.im-auto-badge {
    padding: 6px 12px;
    border-radius: 10px;
    color: #fff;
    background: linear-gradient(135deg,#6366f1,#06b6d4);
    font-size: 10px;
    font-weight: 850;
    letter-spacing: 0.4px;
    white-space: nowrap;
    box-shadow: 0 5px 14px rgba(6,182,212,0.18);
}
.im-map-body {
    padding: 14px 18px 17px;
    max-height: 250px;
    overflow-y: auto;
}
.im-map-row {
    display: grid;
    grid-template-columns: minmax(0, 1fr) 24px minmax(0, 1fr);
    gap: 10px;
    align-items: center;
    margin-bottom: 10px;
}
.im-map-box {
    min-height: 74px;
    border-radius: 12px;
    background: rgba(255,255,255,0.68);
    border: 1px solid rgba(255,255,255,0.92);
    box-shadow: 0 2px 10px rgba(99,102,241,0.05);
    padding: 11px 12px;
    border-left: 4px solid rgba(99,102,241,0.72);
}
.im-map-box.master {
    border-left-color: rgba(6,182,212,0.76);
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
    color: #4f46e5;
    font-size: 17px;
    font-weight: 900;
    text-align: center;
}
.im-execute-wrap {
    padding: 0 18px 18px;
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
    padding: 17px 20px 13px;
    border-bottom: 1px solid rgba(99,102,241,0.08);
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
    padding: 14px 20px;
    font-size: 12.5px;
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
        font-size: 21px;
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
            st.markdown('<div class="nad-card-sub">Unggah file Excel/CSV yang sudah diisi. Maks. 50MB.</div>', unsafe_allow_html=True)

            st.markdown("""
            <div class="lc-dropzone">
                <div class="lc-drop-icon">☁️</div>
                <div class="lc-drop-title">Drag & Drop Excel or CSV File</div>
                <div class="lc-drop-sub">Maximum file size 50MB. Only .xlsx, .xls, .csv supported.<br>*CSV File on support non</div>
            </div>""", unsafe_allow_html=True)

            uploaded = st.file_uploader("", type=["xlsx","xls","csv"],
                                        label_visibility="collapsed", key="im_uploader")

            if uploaded:
                st.session_state.im_file = uploaded.name
                size_kb = round(uploaded.size / 1024)
                st.markdown(f"""
                <div class="lc-file-item">
                    <div class="lc-file-icon">📊</div>
                    <div style="flex:1;">
                        <div class="lc-file-name">{uploaded.name}</div>
                        <div class="lc-file-sub">{size_kb} KB · ready</div>
                    </div>
                    <span style="font-size:18px;color:#dc2626;cursor:pointer;">🗑️</span>
                </div>""", unsafe_allow_html=True)

            c1, c2 = st.columns(2)
            with c1:
                if st.button("← Kembali", use_container_width=True, key="im_step2_back"):
                    st.session_state.im_step = 1; st.rerun()
            with c2:
                if st.button("Preview Data →", use_container_width=True, key="im_step2_next",
                             disabled=(uploaded is None and st.session_state.im_file is None)):
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

    # ── RIGHT: SBU + Scheme Mapping ──
    with col_scheme:
        st.markdown('<div class="nad-card">', unsafe_allow_html=True)

        # Active SBU
        st.markdown('<div class="nad-card-title" style="margin-bottom:6px;">Active SBU</div>', unsafe_allow_html=True)
        sbu_sel = st.selectbox("", SBU_LIST, index=SBU_LIST.index(st.session_state.im_sbu),
                               label_visibility="collapsed", key="im_sbu_sel")
        st.session_state.im_sbu = sbu_sel

        sc1, sc2 = st.columns(2)
        with sc1:
            tmpl_data = "Kode Ruang,Brand,Omzet,Periode\n"
            st.download_button("⬇️ Download Template", data=tmpl_data,
                               file_name="template.csv", mime="text/csv",
                               use_container_width=True, key="im_dl2")

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        # Scheme Mapping
        st.markdown("""
        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:10px;">
            <div style="font-size:12.5px;font-weight:800;color:#1e293b;">Scheme Mapping</div>
            <span style="background:linear-gradient(135deg,#06b6d4,#059669);color:#fff;
                padding:4px 12px;border-radius:999px;font-size:11px;font-weight:700;">AUTO MAPPING</span>
        </div>""", unsafe_allow_html=True)

        mapping_pairs = [
            ("Import Column\nAciourature", "Tenant Name",  "Master Data\nMaster Data"),
            ("Import Column\nMaster Name", "Tenant Name",  "Master Data\nMaster Data"),
            ("Import Column\nTenant ID",   "Kode Ruang",   "Master Data\nMaster Data"),
        ]
        for imp_col, _, master in mapping_pairs:
            st.markdown(f"""
            <div class="scheme-row">
                <div class="scheme-col">{imp_col.replace(chr(10),'<br>')}</div>
                <div class="scheme-arrow">→</div>
                <div class="scheme-master">{master.replace(chr(10),'<br>')}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
        if st.button("▶ Execute Import", use_container_width=True, key="im_execute"):
            with st.spinner("Menjalankan import..."):
                time.sleep(1)
            st.success("✅ Import berhasil dijalankan!")

        st.markdown('</div>', unsafe_allow_html=True)

    # ── Import History (PIC) ──
    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
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

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

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

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Filter Row
    fc1, fc2, fc3, fsp = st.columns([2, 2, 2, 4])
    with fc1:
        f_pic = st.selectbox("", ["Semua PIC"] + SBU_LIST, label_visibility="collapsed", key="adm_fpic")
    with fc2:
        f_status = st.selectbox("", ["Semua Status","Success","Approve","Pending","Rejected","Failed"],
                                label_visibility="collapsed", key="adm_fstatus")
    with fc3:
        f_search = st.text_input("", placeholder="🔍 Cari file...", label_visibility="collapsed", key="adm_fsearch")

    # Apply filter
    df = df_all.copy()
    if f_pic    != "Semua PIC":    df = df[df["PIC"] == f_pic]
    if f_status != "Semua Status": df = df[df["Status"] == f_status]
    if f_search: df = df[df["File"].str.contains(f_search, case=False, na=False)]
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

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

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
        <div style="padding-top:4px;">
            <div style="font-size:24px;font-weight:800;color:#1e293b;">Data Import Manager</div>
            <div style="font-size:12px;color:#94a3b8;margin-top:2px;">
                Kelola unggahan data pendapatan tenant dari seluruh PIC terminal/SBU.
            </div>
        </div>""", unsafe_allow_html=True)
    with h2:
        initial = st.session_state.get("user_name","Admin")[0].upper()
        uname   = st.session_state.get("user_name","Admin")
        uemail  = st.session_state.get("user_email","angkasapura@mail.com")
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:flex-end;gap:12px;padding-top:4px;">
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

    h_title, h_search, h_user = st.columns([4.4, 3.2, 2.4])
    with h_title:
        st.markdown("""
        <div>
            <div class="im-page-title">Data Import Manager</div>
            <div class="im-page-subtitle">Upload, mapping, dan pantau data pendapatan tenant.</div>
        </div>
        """, unsafe_allow_html=True)
    with h_search:
        st.text_input(
            "",
            placeholder="Searching anything...",
            label_visibility="collapsed",
            key="im_search_refined",
        )
    with h_user:
        st.markdown(f"""
        <div class="im-userbar">
            <div class="im-bell">i</div>
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


def _render_selected_file(uploaded):
    if uploaded:
        size_kb = max(1, round(uploaded.size / 1024))
        current_sbu = st.session_state.get("im_sbu", SBU_LIST[0])
        try:
            df_imported, missing_columns = store_shared_import(uploaded, current_sbu)
            st.session_state.im_file = uploaded.name
            st.session_state.im_import_ready = len(missing_columns) == 0
        except Exception as exc:
            st.session_state.im_import_ready = False
            st.error(f"Gagal membaca file: {exc}")
            return

        st.markdown(f"""
        <div class="im-file-card">
            <div class="im-file-icon">XLS</div>
            <div style="min-width:0;">
                <div class="im-file-name">{uploaded.name}</div>
                <div class="im-file-meta">{size_kb:,} KB - {len(df_imported):,} rows terbaca</div>
            </div>
            <div class="im-delete">x</div>
        </div>
        """, unsafe_allow_html=True)

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
            <div class="im-file-icon">CSV</div>
            <div style="min-width:0;">
                <div class="im-file-name">Belum ada file dipilih</div>
                <div class="im-file-meta">Gunakan tombol Browse File untuk memilih Excel atau CSV.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _render_scheme_mapping():
    mapping_pairs = [
        ("Aciourature", "Tenant Name"),
        ("Master Name", "Tenant Name"),
        ("Tenant ID", "Kode Ruang"),
        ("Brand Name", "Brand"),
        ("Monthly Revenue", "Real Omzet"),
    ]

    rows_html = ""
    for source, target in mapping_pairs:
        rows_html += dedent(f"""
        <div class="im-map-row">
            <div class="im-map-box">
                <div class="im-map-label">Import Column</div>
                <div class="im-map-value">{source}</div>
            </div>
            <div class="im-map-arrow">></div>
            <div class="im-map-box master">
                <div class="im-map-label">Master Data</div>
                <div class="im-map-value">{target}</div>
            </div>
        </div>
        """).strip()

    st.markdown(dedent(f"""
    <div class="im-panel im-map-card">
        <div class="im-card-head">
            <div class="im-section-title">Scheme Mapping</div>
            <div class="im-auto-badge">AUTO MAPPING</div>
        </div>
        <div class="im-map-body">{rows_html}</div>
    </div>
    """).strip(), unsafe_allow_html=True)

    st.markdown('<div class="im-execute-wrap">', unsafe_allow_html=True)
    if st.button("Execute Import", use_container_width=True, key="im_execute_refined"):
        with st.spinner("Menjalankan import..."):
            time.sleep(1)
        if st.session_state.get("im_import_ready"):
            st.success("Import berhasil dijalankan. Data sudah tersedia untuk semua dashboard.")
        else:
            st.warning("Import tersimpan, tetapi schema data belum lengkap untuk semua dashboard.")
    st.markdown('</div>', unsafe_allow_html=True)


def _render_import_history_refined():
    df_all = _get_admin_history().copy()
    uploaded_lookup = {
        "Cikarang": "26 Apr 2026 - 14:22",
        "Bali": "26 Apr 2026 - 14:22",
        "Ginung": "25 Apr 2026 - 16:05",
        "Lombok": "25 Apr 2026 - 11:40",
        "Manado": "24 Mar 2026 - 09:35",
        "Kupang": "24 Mar 2026 - 10:12",
        "Jayapura": "23 Apr 2026 - 15:19",
        "Sorong": "-",
    }

    search = st.session_state.get("im_search_refined", "").strip()
    if search:
        mask = (
            df_all["PIC"].str.contains(search, case=False, na=False)
            | df_all["File"].str.contains(search, case=False, na=False)
            | df_all["Status"].str.contains(search, case=False, na=False)
        )
        df = df_all[mask].reset_index(drop=True)
    else:
        df = df_all.reset_index(drop=True)

    rows_html = ""
    for _, r in df.iterrows():
        uploaded_at = uploaded_lookup.get(r["PIC"], "-")
        rows_html += dedent(f"""
        <tr>
            <td style="font-weight:800;color:#1e293b;">{r['PIC']}</td>
            <td style="color:#64748b;">{uploaded_at}</td>
            <td style="font-weight:650;color:#334155;">{r['File']}</td>
            <td style="font-weight:800;color:#1e293b;">{r['Rows']:,}</td>
            <td>{_status_badge(r['Status'])}</td>
        </tr>
        """).strip()

    if not rows_html:
        rows_html = dedent("""
        <tr>
            <td colspan="5" style="text-align:center;color:#94a3b8;padding:24px;">
                Tidak ada data yang cocok dengan pencarian.
            </td>
        </tr>
        """).strip()

    st.markdown(dedent(f"""
    <div class="im-panel im-history">
        <div class="im-history-head">
            <div>
                <div class="im-section-title">Import History</div>
                <div class="im-section-sub">Riwayat upload data per Office/SBU.</div>
            </div>
            <div class="im-refresh">R</div>
        </div>
        <div style="overflow-x:auto;">
            <table class="im-table">
                <thead>
                    <tr>
                        <th>Office/SBU</th>
                        <th>Uploaded Date</th>
                        <th>Filename</th>
                        <th>Rows Imported</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
        <div class="im-footer">
            <span class="im-footer-info">Showing {len(df)} entries</span>
        </div>
    </div>
    """).strip(), unsafe_allow_html=True)


def _render_import_workspace():
    left, right = st.columns([6.2, 3.8], gap="large")

    with left:
        st.markdown("""
        <div class="im-panel im-upload-shell">
            <div class="im-upload-heading">
                <div>
                    <div class="im-section-title">Upload Data File</div>
                    <div class="im-section-sub">Format yang didukung: .xlsx, .xls, dan .csv.</div>
                </div>
                <div class="im-period-chip">April 2026</div>
            </div>
            <div class="im-upload-visual">
                <div class="im-cloud">UP</div>
                <div class="im-upload-title">Drag & Drop Excel or CSV File</div>
                <div class="im-upload-copy">
                    Maksimum ukuran file 50MB. Gunakan template standar agar mapping otomatis terbaca.
                </div>
            </div>
            <div class="im-uploader-slot">
        """, unsafe_allow_html=True)
        uploaded = st.file_uploader(
            "Browse File",
            type=["xlsx", "xls", "csv"],
            label_visibility="collapsed",
            key="im_uploader_refined",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        _render_selected_file(uploaded)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="im-side-stack">', unsafe_allow_html=True)
        st.markdown('<div class="im-panel im-side-control">', unsafe_allow_html=True)
        st.markdown('<div class="im-control-title">Active SBU</div>', unsafe_allow_html=True)
        current_sbu = st.session_state.get("im_sbu", SBU_LIST[0])
        current_idx = SBU_LIST.index(current_sbu) if current_sbu in SBU_LIST else 0
        sbu_sel = st.selectbox(
            "Active SBU",
            SBU_LIST,
            index=current_idx,
            label_visibility="collapsed",
            key="im_sbu_refined",
        )
        st.session_state.im_sbu = sbu_sel
        template_data = "Kode Ruang,Brand,Omzet,Periode\nFB-01-01,Example Brand,10000000,April 2026\n"
        st.download_button(
            "Download Template",
            data=template_data,
            file_name="template_pendapatan.csv",
            mime="text/csv",
            use_container_width=True,
            key="im_template_refined",
        )
        st.markdown("</div>", unsafe_allow_html=True)
        _render_scheme_mapping()
        st.markdown("</div>", unsafe_allow_html=True)

    _render_import_history_refined()


def render_import_manager():
    _init_state()
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)
    st.markdown(_REFINED_IMPORT_CSS, unsafe_allow_html=True)
    _render_import_page_header()
    _render_import_workspace()


if __name__ == "__main__":
    st.set_page_config(page_title="Data Import Manager", layout="wide")
    render_import_manager()
