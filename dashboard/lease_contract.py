import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
from textwrap import dedent
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
from textwrap import dedent

# ──────────────────────────────────────────────────────────────────────────────
# DATA FROM EXCEL
# ──────────────────────────────────────────────────────────────────────────────
from .shared_import import get_mapped_column

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


def _get_contract_data(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return pd.DataFrame(columns=LC_CONTRACT_COLUMNS)

    col_perusahaan = get_mapped_column("perusahaan") or "perusahaan"
    col_terminal = get_mapped_column("terminal") or "terminal"
    col_kode = get_mapped_column("kode_ruang") or "kode_ruang"
    col_bidang = get_mapped_column("bidang_usaha") or "bidang_usaha"

    data = []
    for i, row in df.iterrows():
        data.append({
            "No": i + 1,
            "Name/Tenant": row.get(col_perusahaan, "-"),
            "Sub": "General Contract",
            "Valid Period": "N/A",
            "Unit Name/Loc": row.get(col_kode, "-"),
            "Status": "Valid",
            "Conflict Info": False,
            "Kode": row.get(col_kode, "-"),
            "Skema": row.get(col_bidang, "-"),
            "Sisa": 365,
            "Terminal": row.get(col_terminal, "-")
        })
        
    return pd.DataFrame(data, columns=LC_CONTRACT_COLUMNS)
    return pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "Expiring": [0]*12,
        "Renewed": [0]*12
    })

def _get_contract_types(df):
    if df is None or df.empty:
        return {"Revenue Sharing": 0, "Rental": 0, "MGRS": 0}
        
    col_bidang = get_mapped_column("bidang_usaha") or "bidang_usaha"
    if col_bidang in df.columns:
        return df[col_bidang].value_counts().to_dict()
    return {}


# ──────────────────────────────────────────────────────────────────────────────
# CSS STYLE DEFINITIONS
# ──────────────────────────────────────────────────────────────────────────────
_PAGE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700;800&display=swap');

.stApp, .stApp * {
    font-family: 'Poppins', sans-serif !important;
}

body:has(.lc-page-marker) .stApp {
    background: #F8FAFC !important;
}

/* Premium Card Design */
.premium-card,
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .premium-card-marker) {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -1px rgba(0,0,0,0.015);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    margin-bottom: 20px;
    box-sizing: border-box;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .premium-card-marker) > div[data-testid="stElementContainer"]:has(.premium-card-marker) {
    display: none;
}
.premium-card:hover,
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .premium-card-marker):hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05), 0 4px 6px -2px rgba(0,0,0,0.025);
}

/* Header UI Elements */
.header-wrapper {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 16px;
}
.header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.header-icon-box {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    background: linear-gradient(135deg, #3B82F6, #1D4ED8);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}
.header-title-box {
    display: flex;
    flex-direction: column;
}
.header-title-row {
    display: flex;
    align-items: center;
    gap: 10px;
}
.header-main-title {
    font-size: 17px !important;
    font-weight: 800 !important;
    color: #0F172A !important;
    margin: 0 !important;
    line-height: 1.2 !important;
}
.header-badge {
    background: rgba(245, 158, 11, 0.1) !important;
    color: #F59E0B !important;
    border: 1px solid rgba(245, 158, 11, 0.2) !important;
    font-size: 9.5px !important;
    font-weight: 700 !important;
    padding: 2.5px 8px !important;
    border-radius: 999px !important;
    letter-spacing: 0.5px !important;
}
.header-subtitle {
    font-size: 11.5px !important;
    color: #64748B !important;
    margin-top: 4px !important;
}

/* Header Mini KPI widget */
.header-kpi-widget {
    display: flex;
    align-items: center;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 0 14px;
    height: 38px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    box-sizing: border-box;
}
.header-kpi-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 0 10px;
    min-width: 50px;
}
.header-kpi-val {
    font-size: 14.5px;
    font-weight: 800;
    line-height: 1.1;
}
.header-kpi-val.total { color: #6366F1; }
.header-kpi-val.active { color: #10B981; }
.header-kpi-val.expiring { color: #F59E0B; }
.header-kpi-val.expired { color: #EF4444; }
.header-kpi-lbl {
    font-size: 9px;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-top: 2px;
}
.header-kpi-divider {
    width: 1px;
    height: 24px;
    background-color: #E2E8F0;
}

/* Header Buttons markers and styling */
div[data-testid="stElementContainer"]:has(.header-btn-add-marker) + div[data-testid="stElementContainer"] button {
    background-color: #FFFFFF !important;
    color: #4F46E5 !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    height: 38px !important;
    min-height: 38px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stElementContainer"]:has(.header-btn-add-marker) + div[data-testid="stElementContainer"] button:hover {
    background-color: #F8FAFC !important;
    border-color: #CBD5E1 !important;
}

div[data-testid="stElementContainer"]:has(.header-btn-alerts-marker) + div[data-testid="stElementContainer"] button {
    background-color: #FFFBEB !important;
    color: #D97706 !important;
    border: 1px solid rgba(245, 158, 11, 0.2) !important;
    border-radius: 999px !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    height: 38px !important;
    min-height: 38px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stElementContainer"]:has(.header-btn-alerts-marker) + div[data-testid="stElementContainer"] button:hover {
    background-color: #FEF3C7 !important;
    border-color: rgba(245, 158, 11, 0.4) !important;
}

div[data-testid="stElementContainer"]:has(.header-btn-export-marker) + div[data-testid="stElementContainer"] button {
    background: linear-gradient(135deg, #6366F1, #4F46E5) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 999px !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    height: 38px !important;
    min-height: 38px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stElementContainer"]:has(.header-btn-export-marker) + div[data-testid="stElementContainer"] button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.3) !important;
    color: #FFFFFF !important;
}


/* Custom buttons */
body:has(.lc-page-marker) [data-testid="stMain"] div[data-testid="stButton"] > button,
body:has(.lc-page-marker) [data-testid="stMain"] div[data-testid="stDownloadButton"] > button {
    border-radius: 12px !important;
    padding: 8px 16px !important;
    min-height: 38px !important;
    font-size: 12.5px !important;
    font-weight: 700 !important;
    transition: all 0.2s ease !important;
}
body:has(.lc-page-marker) [data-testid="stMain"] .btn-primary button {
    background: linear-gradient(135deg, #6366F1, #4F46E5) !important;
    color: #FFFFFF !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
}
body:has(.lc-page-marker) [data-testid="stMain"] .btn-primary button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.4) !important;
}
body:has(.lc-page-marker) [data-testid="stMain"] .btn-secondary button {
    background: #FFFFFF !important;
    color: #4F46E5 !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
}
body:has(.lc-page-marker) [data-testid="stMain"] .btn-secondary button:hover {
    background: #F8FAFC !important;
    border-color: #CBD5E1 !important;
}

/* KPI Card contents */
.kpi-card-new {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 20px;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -1px rgba(0,0,0,0.015);
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 335px; /* fixed height for alignment */
    box-sizing: border-box;
    transition: all 0.3s ease;
}
.kpi-card-new:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05), 0 4px 6px -2px rgba(0,0,0,0.025);
}
.kpi-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.kpi-icon-box {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.kpi-icon-box.total { background-color: #EEF2FF; }
.kpi-icon-box.active { background-color: #ECFDF5; }
.kpi-icon-box.expiring { background-color: #FFFBEB; }
.kpi-icon-box.expired { background-color: #FEF2F2; }

.kpi-badge {
    padding: 3px 8px;
    border-radius: 999px;
    font-size: 10.5px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 3px;
}
.kpi-badge.positive { background-color: #E6F4EA; color: #137333; }
.kpi-badge.negative { background-color: #FCE8E6; color: #C5221F; }

.kpi-card-body {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
}
.kpi-card-title {
    font-size: 10.5px;
    font-weight: 700;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 4px;
}
.kpi-card-value-row {
    display: flex;
    align-items: baseline;
    gap: 4px;
    margin-bottom: 2px;
}
.kpi-card-value {
    font-size: 30px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.1;
}
.kpi-card-unit {
    font-size: 12.5px;
    font-weight: 600;
    color: #64748B;
}
.kpi-card-subtitle {
    font-size: 11px;
    color: #64748B;
    margin-bottom: 14px;
}
.kpi-progress-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 12px;
}
.kpi-progress-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
}
.kpi-progress-label {
    font-size: 11px;
    font-weight: 600;
    color: #64748B;
    width: 36px;
    flex-shrink: 0;
}
.kpi-progress-track {
    flex-grow: 1;
    height: 4px;
    background-color: #F1F5F9;
    border-radius: 999px;
    overflow: hidden;
}
.kpi-progress-fill {
    height: 100%;
    border-radius: 999px;
}
.kpi-progress-val {
    font-size: 11px;
    font-weight: 700;
    color: #334155;
    width: 24px;
    text-align: right;
    flex-shrink: 0;
}
.kpi-card-footer {
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    margin-top: auto;
    border-top: 1px solid #F1F5F9;
    padding-top: 10px;
}
.kpi-comparison-text {
    font-size: 10.5px;
    font-weight: 600;
    color: #94A3B8;
    margin-bottom: 2px;
}
.kpi-sparkline-wrap {
    height: 35px;
    display: flex;
    align-items: flex-end;
}

/* Expiry timelines and donut details */
.card-title {
    font-size: 15px;
    font-weight: 800;
    color: #0F172A;
}
.card-subtitle {
    font-size: 11px;
    color: #64748B;
    margin-top: 2px;
    margin-bottom: 16px;
}
.timeline-kpi-row {
    display: flex;
    gap: 8px;
    margin-bottom: 14px;
    flex-wrap: nowrap;
}
.timeline-kpi-card {
    flex: 1;
    border-radius: 10px;
    padding: 10px 8px;
    text-align: left;
    box-sizing: border-box;
    border: 1px solid transparent;
}
.timeline-kpi-card.expiring { background-color: #EEF2FF; border-color: #E0E7FF; }
.timeline-kpi-card.renewed { background-color: #ECFDF5; border-color: #D1FAE5; }
.timeline-kpi-card.rate { background-color: #F0F9FF; border-color: #E0F2FE; }
.timeline-kpi-card.risk { background-color: #FEF2F2; border-color: #FEE2E2; }

.timeline-kpi-val {
    font-size: 18px;
    font-weight: 800;
    line-height: 1;
}
.timeline-kpi-card.expiring .timeline-kpi-val { color: #4F46E5; }
.timeline-kpi-card.renewed .timeline-kpi-val { color: #10B981; }
.timeline-kpi-card.rate .timeline-kpi-val { color: #0EA5E9; }
.timeline-kpi-card.risk .timeline-kpi-val { color: #EF4444; }

.timeline-kpi-lbl {
    font-size: 9px;
    font-weight: 700;
    color: #64748B;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}

.risk-strip-container {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 14px;
    border-top: 1px solid #F1F5F9;
    padding-top: 14px;
}
.risk-strip-label {
    font-size: 10.5px;
    font-weight: 700;
    color: #64748B;
    white-space: nowrap;
}
.risk-strip-blocks {
    display: flex;
    gap: 4px;
    flex-grow: 1;
}
.risk-strip-block {
    height: 8px;
    flex: 1;
    border-radius: 999px;
}
.risk-strip-block.low { background-color: #10B981; }
.risk-strip-block.medium { background-color: #F59E0B; }
.risk-strip-block.high { background-color: #EF4444; }

.risk-legend-row {
    display: flex;
    gap: 12px;
    margin-top: 8px;
    font-size: 10px;
    font-weight: 600;
    color: #64748B;
}
.risk-legend-item {
    display: flex;
    align-items: center;
    gap: 4px;
}
.risk-legend-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}
.risk-legend-dot.low { background-color: #10B981; }
.risk-legend-dot.medium { background-color: #F59E0B; }
.risk-legend-dot.high { background-color: #EF4444; }

/* Distribution layout & detail cards */
.dist-layout {
    display: flex;
    align-items: center;
    gap: 14px;
}
.dist-chart-wrap {
    flex: 1.1;
    display: flex;
    justify-content: center;
}
.dist-stack {
    flex: 1.1;
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.dist-card {
    border-radius: 10px;
    padding: 8px 10px;
    box-sizing: border-box;
    border: 1px solid transparent;
}
.dist-card.rs { background-color: #EEF2FF; border-color: #E0E7FF; }
.dist-card.rs_mo { background-color: #ECFEFF; border-color: #CFFAFE; }
.dist-card.mgrs { background-color: #FFFBEB; border-color: #FEF3C7; }

.dist-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}
.dist-card-title-row {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 10.5px;
    font-weight: 700;
}
.dist-card.rs .dist-card-title-row { color: #4F46E5; }
.dist-card.rs_mo .dist-card-title-row { color: #0EA5E9; }
.dist-card.mgrs .dist-card-title-row { color: #D97706; }

.dist-card-dot {
    width: 8px;
    height: 8px;
    border-radius: 2px;
}
.dist-card.rs .dist-card-dot { background-color: #6366F1; }
.dist-card.rs_mo .dist-card-dot { background-color: #0EA5E9; }
.dist-card.mgrs .dist-card-dot { background-color: #F59E0B; }

.dist-card-pct {
    font-size: 10.5px;
    font-weight: 700;
}
.dist-card.rs .dist-card-pct { color: #6366F1; }
.dist-card.rs_mo .dist-card-pct { color: #0EA5E9; }
.dist-card.mgrs .dist-card-pct { color: #F59E0B; }

.dist-card-body {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
}
.dist-card-count {
    font-size: 16px;
    font-weight: 800;
    color: #0F172A;
}
.dist-card-val {
    font-size: 9.5px;
    font-weight: 600;
    color: #94A3B8;
}

/* Status progress bars & Health section */
.status-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    margin-bottom: 12px;
}
.status-row {
    background: #F8FAFC;
    border: 1px solid #F1F5F9;
    border-radius: 10px;
    padding: 8px 10px;
    box-sizing: border-box;
}
.status-row-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
}
.status-row-label-row {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 10.5px;
    font-weight: 700;
    color: #0F172A;
}
.status-row-icon {
    width: 14px;
    height: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 9px;
    font-weight: 800;
    border-radius: 50%;
}
.status-row-icon.active { background-color: #ECFDF5; color: #10B981; border: 1px solid #A7F3D0; }
.status-row-icon.expiring { background-color: #FFFBEB; color: #F59E0B; border: 1px solid #FDE68A; }
.status-row-icon.expired { background-color: #FEF2F2; color: #EF4444; border: 1px solid #FCA5A5; }

.status-row-val {
    font-size: 10.5px;
    font-weight: 700;
    color: #0F172A;
}
.status-row-val span {
    font-weight: 600;
    color: #94A3B8;
    margin-left: 2px;
}

.status-row-progress-bg {
    width: 100%;
    height: 4px;
    background-color: #E2E8F0;
    border-radius: 999px;
    overflow: hidden;
}
.status-row-progress-fill {
    height: 100%;
    border-radius: 999px;
}

.status-score-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    margin-top: 12px;
    border-top: 1px solid #F1F5F9;
    padding-top: 12px;
}
.status-score-chart-wrap {
    display: flex;
    justify-content: center;
    margin-bottom: 6px;
}
.status-score-title {
    font-size: 9.5px;
    font-weight: 700;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
}
.status-score-val {
    font-size: 20px;
    font-weight: 800;
    color: #10B981;
    line-height: 1;
    margin-bottom: 2px;
}
.status-score-desc {
    font-size: 9.5px;
    font-weight: 600;
    color: #94A3B8;
}

/* Alert banners */
.alert-banner {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 14px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 14px;
}
.alert-danger {
    background: #FEF2F2;
    border: 1px solid #FCA5A5;
    color: #B91C1C;
}
.alert-warning {
    background: #FFFBEB;
    border: 1px solid #FCD34D;
    color: #B45309;
}
.alert-success {
    background: #F0FDF4;
    border: 1px solid #86EFAC;
    color: #15803D;
}

/* Custom Table style */
.custom-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 8px;
}
.custom-table th {
    text-align: left;
    font-size: 10.5px;
    font-weight: 800;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    padding: 10px 12px;
    border-bottom: 1px solid #E2E8F0;
}
.custom-table td {
    padding: 12px 12px;
    font-size: 12.5px;
    color: #334155;
    border-bottom: 1px solid #F1F5F9;
    vertical-align: middle;
}
.custom-table tbody tr:hover {
    background-color: #F8FAFC;
}
.status-badge {
    padding: 3px 8px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
}
.badge-danger { background: #FEF2F2; color: #EF4444; border: 1px solid rgba(239, 68, 68, 0.2); }
.badge-warning { background: #FFFBEB; color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.2); }
.badge-success { background: #F0FDF4; color: #10B981; border: 1px solid rgba(16, 185, 129, 0.2); }

/* Left Sidebar Action Required & Renewal Pipeline cards */
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .action-required-marker) {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 20px !important;
    padding: 20px !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -1px rgba(0,0,0,0.015) !important;
    margin-bottom: 20px !important;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .action-required-marker) > div[data-testid="stElementContainer"]:has(.action-required-marker) {
    display: none !important;
}

div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .renewal-pipeline-marker) {
    background: #F4FBF7 !important;
    border: 1px solid #A7F3D0 !important;
    border-radius: 20px !important;
    padding: 20px !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02) !important;
    margin-bottom: 20px !important;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .renewal-pipeline-marker) > div[data-testid="stElementContainer"]:has(.renewal-pipeline-marker) {
    display: none !important;
}

/* Action Required Card Header */
.sidebar-header-box {
    display: flex;
    align-items: center;
    gap: 12px;
}
.sidebar-header-icon {
    width: 36px;
    height: 36px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.sidebar-header-icon.danger {
    background-color: #FEF2F2;
    border: 1px solid rgba(239, 68, 68, 0.15);
}
.sidebar-header-text {
    display: flex;
    flex-direction: column;
}
.sidebar-header-text .sidebar-title {
    font-size: 14.5px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.2;
}
.sidebar-header-text .sidebar-subtitle {
    font-size: 11px;
    color: #64748B;
    margin-top: 2px;
}

/* Grid Badges inside Card */
.sidebar-badges-grid {
    display: flex;
    gap: 8px;
    margin-top: 16px;
    margin-bottom: 16px;
}
.sidebar-badge-box {
    flex: 1;
    border-radius: 10px;
    padding: 10px 8px;
    text-align: center;
    border: 1px solid transparent;
}
.sidebar-badge-box.danger {
    background-color: #FEF2F2;
    border-color: rgba(239, 68, 68, 0.1);
}
.sidebar-badge-box.warning {
    background-color: #FFFBEB;
    border-color: rgba(245, 158, 11, 0.1);
}
.sidebar-badge-number {
    font-size: 18px;
    font-weight: 800;
    line-height: 1.1;
    margin-bottom: 2px;
}
.sidebar-badge-box.danger .sidebar-badge-number { color: #EF4444; }
.sidebar-badge-box.warning .sidebar-badge-number { color: #F59E0B; }
.sidebar-badge-label {
    font-size: 9.5px;
    font-weight: 700;
    color: #64748B;
}

/* Sections inside Card */
.sidebar-section-container {
    margin-top: 16px;
    border-top: 1px solid #F1F5F9;
    padding-top: 14px;
}
.sidebar-section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.sidebar-section-title-left {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 12.5px;
    font-weight: 800;
    color: #0F172A;
}
.section-icon-wrap {
    width: 20px;
    height: 20px;
    border-radius: 6px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.section-icon-wrap.danger { background-color: #FEF2F2; }
.section-icon-wrap.warning { background-color: #FFFBEB; }
.sidebar-section-badge {
    font-size: 10px;
    font-weight: 800;
    padding: 2px 6px;
    border-radius: 999px;
}
.sidebar-section-badge.danger { background-color: #FEF2F2; color: #EF4444; }
.sidebar-section-badge.warning { background-color: #FFFBEB; color: #F59E0B; }

/* Section Lists */
ul.sidebar-list {
    list-style: none !important;
    padding-left: 0 !important;
    margin-top: 8px !important;
    margin-bottom: 12px !important;
}
ul.sidebar-list li {
    position: relative !important;
    padding-left: 14px !important;
    font-size: 11.5px !important;
    color: #334155 !important;
    line-height: 1.6 !important;
    margin-bottom: 4px !important;
    font-weight: 500 !important;
}
ul.sidebar-list li::before {
    content: "•" !important;
    position: absolute !important;
    left: 0 !important;
    font-size: 14px !important;
    line-height: 1 !important;
    top: 0px !important;
}
ul.sidebar-list.danger li::before { color: #EF4444 !important; }
ul.sidebar-list.warning li::before { color: #F59E0B !important; }

/* Action Buttons inside Card */
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .action-required-marker) div[data-testid="stElementContainer"]:has(.sb-btn-danger-marker) + div[data-testid="stElementContainer"] button {
    background-color: #FEF2F2 !important;
    color: #EF4444 !important;
    border: 1px solid rgba(239, 68, 68, 0.2) !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    width: 100% !important;
    height: 36px !important;
    min-height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .action-required-marker) div[data-testid="stElementContainer"]:has(.sb-btn-danger-marker) + div[data-testid="stElementContainer"] button:hover {
    background-color: #FEE2E2 !important;
    border-color: rgba(239, 68, 68, 0.4) !important;
}

div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .action-required-marker) div[data-testid="stElementContainer"]:has(.sb-btn-warning-marker) + div[data-testid="stElementContainer"] button {
    background-color: #FFFBEB !important;
    color: #D97706 !important;
    border: 1px solid rgba(245, 158, 11, 0.2) !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    font-size: 12px !important;
    width: 100% !important;
    height: 36px !important;
    min-height: 36px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .action-required-marker) div[data-testid="stElementContainer"]:has(.sb-btn-warning-marker) + div[data-testid="stElementContainer"] button:hover {
    background-color: #FEF3C7 !important;
    border-color: rgba(245, 158, 11, 0.4) !important;
}

/* Renewal Pipeline Component Styles */
.pipeline-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13.5px;
    font-weight: 800;
    color: #064E3B;
    margin-bottom: 14px;
}
.pipeline-icon-wrap {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background-color: #D1FAE5;
    border: 1.5px solid #6EE7B7;
    display: flex;
    align-items: center;
    justify-content: center;
}
.pipeline-list {
    display: flex;
    flex-direction: column;
}
.pipeline-item {
    display: flex;
    flex-direction: column;
    gap: 3px;
}
.pipeline-row-top {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.pipeline-tenant {
    font-size: 12.5px;
    font-weight: 800;
    color: #0F172A;
}
.pipeline-value {
    font-size: 12.5px;
    font-weight: 800;
    color: #0F172A;
}
.pipeline-row-bottom {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.pipeline-due {
    font-size: 11px;
    color: #64748B;
}
.pipeline-badge {
    font-size: 9px;
    font-weight: 800;
    padding: 2.5px 6.5px;
    border-radius: 4px;
    letter-spacing: 0.3px;
}
.pipeline-badge.low {
    background-color: #D1FAE5;
    color: #065F46;
}
.pipeline-badge.medium {
    background-color: #FEF3C7;
    color: #92400E;
}
.pipeline-divider {
    height: 1px;
    background-color: rgba(6, 78, 59, 0.08);
    margin: 10px 0;
}

/* Executive Insights Refactored Header */
.insights-header-box {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 20px;
}
.insights-header-icon {
    width: 42px;
    height: 42px;
    border-radius: 12px;
    background: linear-gradient(135deg, #3B82F6, #1D4ED8);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #FFFFFF;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
}
.insights-header-text {
    display: flex;
    flex-direction: column;
}
.insights-title {
    font-size: 16.5px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.2;
}
.insights-subtitle {
    font-size: 12px;
    color: #64748B;
    margin-top: 2px;
}

/* Executive Insights Grid Cards */
.insight-grid-card {
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 16px;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 8px;
    border: 1px solid transparent;
}
.insight-grid-card.danger {
    background-color: #FEF2F2;
    border-color: rgba(239, 68, 68, 0.12);
}
.insight-grid-card.warning {
    background-color: #FFFBEB;
    border-color: rgba(245, 158, 11, 0.12);
}
.insight-grid-card.success {
    background-color: #F0FDF4;
    border-color: rgba(16, 185, 129, 0.12);
}
.insight-grid-card.info {
    background-color: #EEF2FF;
    border-color: rgba(99, 102, 241, 0.12);
}
.insight-grid-card.cyan-card {
    background-color: #ECFEFF;
    border-color: rgba(6, 182, 212, 0.12);
}
.insight-grid-card.purple-card {
    background-color: #FDF4FF;
    border-color: rgba(217, 70, 239, 0.12);
}

.insight-lbl-row {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 9.5px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.insight-grid-card.danger .insight-lbl-row { color: #EF4444; }
.insight-grid-card.warning .insight-lbl-row { color: #D97706; }
.insight-grid-card.success .insight-lbl-row { color: #16A34A; }
.insight-grid-card.info .insight-lbl-row { color: #4F46E5; }
.insight-grid-card.cyan-card .insight-lbl-row { color: #0891B2; }
.insight-grid-card.purple-card .insight-lbl-row { color: #C026D3; }

.insight-grid-title {
    font-size: 13.5px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.35;
}
.insight-grid-desc {
    font-size: 11px;
    color: #475569;
    line-height: 1.55;
    font-weight: 400;
}
.insight-grid-pill {
    align-self: flex-start;
    padding: 3px 9px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
    margin-top: 4px;
}
.insight-grid-card.danger .insight-grid-pill { background-color: #FEE2E2; color: #EF4444; }
.insight-grid-card.warning .insight-grid-pill { background-color: #FEF3C7; color: #D97706; }
.insight-grid-card.success .insight-grid-pill { background-color: #DCFCE7; color: #16A34A; }
.insight-grid-card.info .insight-grid-pill { background-color: #E0E7FF; color: #4F46E5; }
.insight-grid-card.cyan-card .insight-grid-pill { background-color: #CFFAFE; color: #0891B2; }
.insight-grid-card.purple-card .insight-grid-pill { background-color: #F5D0FE; color: #C026D3; }

/* Executive Insights Premium Card container */
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .executive-insights-marker) {
    background: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 20px !important;
    padding: 20px !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -1px rgba(0,0,0,0.015) !important;
    margin-bottom: 20px !important;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .executive-insights-marker) > div[data-testid="stElementContainer"]:has(.executive-insights-marker) {
    display: none !important;
}

/* Executive Insights Bottom CTA report button */
div[data-testid="stElementContainer"]:has(.insights-cta-marker) {
    margin-bottom: -10px !important;
}
div[data-testid="stElementContainer"]:has(.insights-cta-marker) + div[data-testid="stElementContainer"] button {
    width: 100% !important;
    background: linear-gradient(135deg, #6366F1, #4F46E5) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 20px !important;
    font-size: 13.5px !important;
    font-weight: 700 !important;
    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    transition: all 0.2s ease !important;
    height: 42px !important;
    min-height: 42px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
}
div[data-testid="stElementContainer"]:has(.insights-cta-marker) + div[data-testid="stElementContainer"] button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(99, 102, 241, 0.4) !important;
    background: linear-gradient(135deg, #4F46E5, #4338CA) !important;
    color: #FFFFFF !important;
}


/* Conflict and normal link badges for registry table */
.conflict-link {
    color: #EF4444;
    font-weight: 700;
    font-size: 11px;
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.18);
    padding: 3px 8px;
    border-radius: 6px;
}
.no-conflict {
    color: #64748B;
    font-size: 11px;
    background: #F8FAFC;
    padding: 3px 8px;
    border-radius: 6px;
}

/* Pagination container styling */
.lc-tbl-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #E2E8F0;
    font-size: 12.5px;
    color: #64748B;
}
/* Centering Plotly Charts */
div[data-testid="stPlotlyChart"] {
    display: flex;
    justify-content: center;
    align-items: center;
}

/* ──────────────────────────────────────────────────────────────
   NEW DESIGN REFINEMENTS: HEADER REALIGNMENT & HORIZONTAL FILTERS
   ────────────────────────────────────────────────────────────── */

/* Move app content to the very top and remove standard Streamlit header space */
header,
[data-testid="stHeader"],
[data-testid="stDecoration"] {
    display: none !important;
    height: 0 !important;
}

.block-container,
[data-testid="stAppViewBlockContainer"] {
    padding-top: 1.5rem !important;
    padding-bottom: 2rem !important;
}

/* Pull the header row horizontal block to the absolute top of the page */
div[data-testid="stHorizontalBlock"]:first-of-type {
    margin-top: -15px !important;
    align-items: center !important;
}

/* Hide empty container elements created by marker markdowns to avoid layout gaps */
div[data-testid="stElementContainer"]:has(.lc-page-marker),
div[data-testid="stElementContainer"]:has(.header-btn-alerts-marker),
div[data-testid="stElementContainer"]:has(.header-btn-export-marker),
div[data-testid="stElementContainer"]:has(.btn-reset-marker),
div[data-testid="stElementContainer"]:has(.btn-apply-marker),
div[data-testid="stElementContainer"]:has(.filters-marker) {
    position: absolute !important;
    width: 0 !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
    overflow: hidden !important;
}

/* Horizontal Filters label and separator block */
.filters-label-box {
    display: flex;
    align-items: center;
    gap: 8px;
    height: 38px;
}
.filters-lbl-text {
    font-size: 13px;
    font-weight: 700;
    color: #6366F1;
}
.filters-lbl-divider {
    width: 1px;
    height: 18px;
    background-color: #CBD5E1;
    margin-left: 6px;
}

/* Style selectbox dropdown inputs inside filters row as capsules */
div[data-testid="stSelectbox"] [data-testid="stMarkdownContainer"] {
    display: none !important;
}
div[data-testid="stSelectbox"] > div {
    border: none !important;
    background-color: transparent !important;
    padding: 0 !important;
    box-shadow: none !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 999px !important;
    background-color: #FFFFFF !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover {
    border-color: #CBD5E1 !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1) !important;
}

/* Minimize control container size */
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    min-height: 28px !important;
    height: 28px !important;
    padding: 0 4px 0 10px !important;
    display: flex !important;
    align-items: center !important;
}

/* Override selection text styling inside selectbox */
div[data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #1E293B !important;
    line-height: 28px !important;
}

/* Pseudo-elements for prefixes */
div[data-testid="column"]:nth-of-type(2) div[data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"]::before {
    content: "Terminal ";
    font-weight: 400 !important;
    color: #94A3B8 !important;
}
div[data-testid="column"]:nth-of-type(3) div[data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"]::before {
    content: "Contract Type ";
    font-weight: 400 !important;
    color: #94A3B8 !important;
}
div[data-testid="column"]:nth-of-type(4) div[data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"]::before {
    content: "Business Category ";
    font-weight: 400 !important;
    color: #94A3B8 !important;
}
div[data-testid="column"]:nth-of-type(5) div[data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"]::before {
    content: "Contract Status ";
    font-weight: 400 !important;
    color: #94A3B8 !important;
}

/* Reduce size of Chevron Arrow */
div[data-testid="stSelectbox"] svg {
    width: 14px !important;
    height: 14px !important;
}

/* Reset Button */
div[data-testid="stElementContainer"]:has(.btn-reset-marker) + div[data-testid="stElementContainer"] button {
    background-color: #FFFFFF !important;
    color: #475569 !important;
    border: 1px solid #CBD5E1 !important;
    border-radius: 999px !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    height: 28px !important;
    min-height: 28px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
div[data-testid="stElementContainer"]:has(.btn-reset-marker) + div[data-testid="stElementContainer"] button:hover {
    background-color: #F8FAFC !important;
    border-color: #94A3B8 !important;
    color: #1E293B !important;
}

/* Apply Button */
div[data-testid="stElementContainer"]:has(.btn-apply-marker) + div[data-testid="stElementContainer"] button {
    background: linear-gradient(135deg, #6366F1, #4F46E5) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 999px !important;
    font-weight: 700 !important;
    font-size: 11px !important;
    height: 28px !important;
    min-height: 28px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.2) !important;
    transition: all 0.2s ease !important;
    width: 100% !important;
}
div[data-testid="stElementContainer"]:has(.btn-apply-marker) + div[data-testid="stElementContainer"] button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.3) !important;
    color: #FFFFFF !important;
}
</style>

"""

# ──────────────────────────────────────────────────────────────────────────────
# INIT STATE
# ──────────────────────────────────────────────────────────────────────────────
def _init_state(df_raw=None):
    if "lc_df"          not in st.session_state: st.session_state.lc_df          = _get_contract_data(df_raw)
    if "lc_page"        not in st.session_state: st.session_state.lc_page        = 0
    if "lc_show_form"   not in st.session_state: st.session_state.lc_show_form   = False
    if "lc_selected"    not in st.session_state: st.session_state.lc_selected    = set()
    if "lc_alert_toast" not in st.session_state: st.session_state.lc_alert_toast = False

    # Filter states initialization
    if "f_terminal"     not in st.session_state: st.session_state.f_terminal     = "All Terminals"
    if "f_type"         not in st.session_state: st.session_state.f_type         = "All Types"
    if "f_category"     not in st.session_state: st.session_state.f_category     = "All Categories"
    if "f_status"       not in st.session_state: st.session_state.f_status       = "All Status"
    if "lc_filtered_df" not in st.session_state: st.session_state.lc_filtered_df = st.session_state.lc_df

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
    progress_rows = ""
    if progress_items:
        max_val = max([item[1] for item in progress_items]) if progress_items else 1
        for lbl, val in progress_items:
            pct = int((val / max_val) * 85) if max_val > 0 else 0
            if val > 0 and pct < 5:
                pct = 5
            progress_rows += f"""
            <div class="kpi-progress-row">
                <span class="kpi-progress-label">{lbl}</span>
                <div class="kpi-progress-track">
                    <div class="kpi-progress-fill" style="width: {pct}%; background-color: {progress_color};"></div>
                </div>
                <span class="kpi-progress-val">{val}</span>
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

def _build_timeline_chart(df):
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    months_labels = [f"{m} 25" for m in months]
    
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
            
    # Renewed counts are derived from expiring (e.g. ~60% rate as mock renewal success)
    renewed_counts = {m: int(expiring_counts[m] * 0.6) for m in months}
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=months_labels,
        y=[expiring_counts[m] for m in months],
        name="Expiring",
        marker_color="#6366F1",
        width=0.25
    ))
    fig.add_trace(go.Bar(
        x=months_labels,
        y=[renewed_counts[m] for m in months],
        name="Renewed",
        marker_color="#10B981",
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
            tickfont=dict(family="Poppins", size=9, color="#94A3B8"),
            linecolor="#E2E8F0"
        ),
        yaxis=dict(
            gridcolor="#F1F5F9",
            tickfont=dict(family="Poppins", size=9, color="#94A3B8"),
            zeroline=False
        )
    )
    return fig

def _build_donut_chart(data_dict, colors):
    labels = list(data_dict.keys())
    values = list(data_dict.values())
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.62,
        marker=dict(colors=colors),
        textinfo="percent",
        textfont_size=10,
        textfont_color="#FFFFFF",
        textposition="inside",
        showlegend=False,
        hoverinfo="label+value+percent"
    )])
    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=145,
        width=145,
        annotations=[dict(text=f"{sum(values)}<br><span style='font-size:9px;color:#94A3B8;font-weight:bold;'>TOTAL</span>", x=0.5, y=0.5, font_size=14, font_weight="bold", font_family="Poppins", showarrow=False)]
    )
    return fig

def _build_mini_donut(active, expiring, expired):
    vals = [active, expiring, expired]
    if sum(vals) == 0:
        vals = [1, 0, 0] # fallback
    fig = go.Figure(data=[go.Pie(
        labels=["Active", "Expiring", "Expired"],
        values=vals,
        hole=0.65,
        marker=dict(colors=["#10B981", "#F59E0B", "#EF4444"]),
        showlegend=False,
        hoverinfo="none",
        textinfo="none"
    )])
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=110,
        width=110
    )
    return fig

# Sparkline dummy datasets
SPARK_TOTAL = [10, 15, 12, 18, 14, 22, 20, 25, 24, 28, 26, 30]
SPARK_ACTIVE = [8, 12, 10, 15, 12, 18, 16, 21, 20, 24, 22, 25]
SPARK_EXPIRING = [30, 28, 25, 24, 22, 20, 18, 16, 17, 18, 19, 18]
SPARK_EXPIRED = [15, 14, 13, 14, 12, 11, 10, 9, 8, 10, 11, 11]

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



def _render_action_required():
    with st.container():
        st.markdown('<div class="action-required-marker"></div>', unsafe_allow_html=True)
        
        # Header Box
        st.markdown("""
        <div class="sidebar-header-box">
            <div class="sidebar-header-icon danger">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                    <line x1="12" y1="9" x2="12" y2="13"></line>
                    <line x1="12" y1="17" x2="12.01" y2="17"></line>
                </svg>
            </div>
            <div class="sidebar-header-text">
                <div class="sidebar-title">Action Required</div>
                <div class="sidebar-subtitle">8 contracts need attention</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Badges Grid
        st.markdown("""
        <div class="sidebar-badges-grid">
            <div class="sidebar-badge-box danger">
                <div class="sidebar-badge-number">2</div>
                <div class="sidebar-badge-label">This Month</div>
            </div>
            <div class="sidebar-badge-box warning">
                <div class="sidebar-badge-number">3</div>
                <div class="sidebar-badge-label">Renewal</div>
            </div>
            <div class="sidebar-badge-box danger">
                <div class="sidebar-badge-number">3</div>
                <div class="sidebar-badge-label">Expired</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Section 1: Expiring This Month
        st.markdown("""
        <div class="sidebar-section-container" style="border-top: none; padding-top: 0; margin-top: 0;">
            <div class="sidebar-section-header">
                <span class="sidebar-section-title-left">
                    <span class="section-icon-wrap danger">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="10"></circle>
                            <line x1="15" y1="9" x2="9" y2="15"></line>
                            <line x1="9" y1="9" x2="15" y2="15"></line>
                        </svg>
                    </span>
                    Expiring This Month
                </span>
                <span class="sidebar-section-badge danger">2</span>
            </div>
            <ul class="sidebar-list danger">
                <li>7-Eleven (T1) — 16 days</li>
                <li>Sari Roti (T2) — 30 days</li>
            </ul>
        </div>
        <div class="sb-btn-danger-marker"></div>
        """, unsafe_allow_html=True)
        if st.button("Renew Immediately >", key="sb_renew_imm_new", use_container_width=True):
            st.toast("⚡ Initiating immediate renewals...")
            
        # Section 2: Requiring Renewal
        st.markdown("""
        <div class="sidebar-section-container">
            <div class="sidebar-section-header">
                <span class="sidebar-section-title-left">
                    <span class="section-icon-wrap warning">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"></path>
                        </svg>
                    </span>
                    Requiring Renewal
                </span>
                <span class="sidebar-section-badge warning">3</span>
            </div>
            <ul class="sidebar-list warning">
                <li>KFC (T3) — 44 days</li>
                <li>Timezone (T1) — 75 days</li>
                <li>Lion Lounge (T1) — 89 days</li>
            </ul>
        </div>
        <div class="sb-btn-warning-marker"></div>
        """, unsafe_allow_html=True)
        if st.button("Initiate Renewal >", key="sb_init_renew_new", use_container_width=True):
            st.toast("🔄 Launching renewal pipeline processes...")
            
        # Section 3: Expired Contracts
        st.markdown("""
        <div class="sidebar-section-container">
            <div class="sidebar-section-header">
                <span class="sidebar-section-title-left">
                    <span class="section-icon-wrap danger">
                        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                            <line x1="12" y1="9" x2="12" y2="13"></line>
                            <line x1="12" y1="17" x2="12.01" y2="17"></line>
                        </svg>
                    </span>
                    Expired Contracts
                </span>
                <span class="sidebar-section-badge danger">3</span>
            </div>
            <ul class="sidebar-list danger">
                <li>Dunkin' (T1) — 15 days overdue</li>
                <li>HokBen (T2) — 1 day overdue</li>
                <li>Optik Seis (T3) — 14 days overdue</li>
            </ul>
        </div>
        <div class="sb-btn-danger-marker"></div>
        """, unsafe_allow_html=True)
        if st.button("Resolve Urgently >", key="sb_resolve_urg_new", use_container_width=True):
            st.toast("🚨 Notifying legal and commercial teams...")

def _render_renewal_pipeline():
    with st.container():
        st.markdown('<div class="renewal-pipeline-marker"></div>', unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div class="pipeline-header">
            <span class="pipeline-icon-wrap">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="20 6 9 17 4 12"></polyline>
                </svg>
            </span>
            Renewal Pipeline
        </div>
        
        <div class="pipeline-list">
            <div class="pipeline-item">
                <div class="pipeline-row-top">
                    <span class="pipeline-tenant">DFS Indonesia</span>
                    <span class="pipeline-value">Rp 42.7B</span>
                </div>
                <div class="pipeline-row-bottom">
                    <span class="pipeline-due">Due: Mar 2025</span>
                    <span class="pipeline-badge low">LOW</span>
                </div>
            </div>
            <div class="pipeline-divider"></div>
            <div class="pipeline-item">
                <div class="pipeline-row-top">
                    <span class="pipeline-tenant">Garuda Exec</span>
                    <span class="pipeline-value">Rp 14.8B</span>
                </div>
                <div class="pipeline-row-bottom">
                    <span class="pipeline-due">Due: Jun 2025</span>
                    <span class="pipeline-badge low">LOW</span>
                </div>
            </div>
            <div class="pipeline-divider"></div>
            <div class="pipeline-item">
                <div class="pipeline-row-top">
                    <span class="pipeline-tenant">Gramedia</span>
                    <span class="pipeline-value">Rp 6.8B</span>
                </div>
                <div class="pipeline-row-bottom">
                    <span class="pipeline-due">Due: Jun 2025</span>
                    <span class="pipeline-badge medium">MEDIUM</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_executive_insights():
    with st.container():
        st.markdown('<div class="executive-insights-marker"></div>', unsafe_allow_html=True)
        
        # Header
        st.markdown("""
        <div class="insights-header-box">
            <div class="insights-header-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L14.8 9.2L22 12L14.8 14.8L12 22L9.2 14.8L2 12L9.2 9.2L12 2Z" />
                </svg>
            </div>
            <div class="insights-header-text">
                <div class="insights-title">Executive Insights</div>
                <div class="insights-subtitle">Contract risk & opportunity analysis</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            # Card 1: UPCOMING RISKS
            st.markdown("""
            <div class="insight-grid-card danger">
                <div class="insight-lbl-row">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    Upcoming Risks
                </div>
                <div class="insight-grid-title">5 high-value contracts expiring Q1 2025</div>
                <div class="insight-grid-desc">
                    Contracts worth Rp 28.2B expire within 90 days. DFS (Rp 42.7B) and Garuda (Rp 14.8B) renewals due by Q2 2025 — initiate negotiations now.
                </div>
                <span class="insight-grid-pill">Rp 28.2B at risk</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Card 2: RENEWAL RECOMMENDATIONS
            st.markdown("""
            <div class="insight-grid-card warning">
                <div class="insight-lbl-row">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
                        <polyline points="17 6 23 6 23 12"></polyline>
                    </svg>
                    Renewal Recommendations
                </div>
                <div class="insight-grid-title">Prioritize 3 expired contracts this week</div>
                <div class="insight-grid-desc">
                    Dunkin', HokBen, and Optik Seis contracts are already expired. Each day without resolution risks revenue leakage and operational disruption at T1, T2, and T3.
                </div>
                <span class="insight-grid-pill">3 immediate actions</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Card 3: STRATEGIC INSIGHT
            st.markdown("""
            <div class="insight-grid-card info">
                <div class="insight-lbl-row">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M18 10a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"></path>
                        <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                    </svg>
                    Strategic Insight
                </div>
                <div class="insight-grid-title">T2 renewal risk is highest value</div>
                <div class="insight-grid-desc">
                    Terminal 2 hosts 112 of 247 contracts (45.3%). 4 T2 contracts expire in 2025 totaling Rp 68.4B — a structured renewal calendar is recommended.
                </div>
                <span class="insight-grid-pill">Rp 68.4B renewal</span>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            # Card 4: CONTRACT DISTRIBUTION
            st.markdown("""
            <div class="insight-grid-card info">
                <div class="insight-lbl-row">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <line x1="18" y1="20" x2="18" y2="10"></line>
                        <line x1="12" y1="20" x2="12" y2="4"></line>
                        <line x1="6" y1="20" x2="6" y2="14"></line>
                    </svg>
                    Contract Distribution
                </div>
                <div class="insight-grid-title">RS dominates at 51.8% of portfolio</div>
                <div class="insight-grid-desc">
                    128 Revenue Sharing contracts hold 51.8% share. RS + Min Omzet contracts (81) provide Rp 60.4B — consider converting 8 volatile RS tenants for revenue stability.
                </div>
                <span class="insight-grid-pill">247 total contracts</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Card 5: PORTFOLIO HEALTH
            st.markdown("""
            <div class="insight-grid-card success">
                <div class="insight-lbl-row">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
                    </svg>
                    Portfolio Health
                </div>
                <div class="insight-grid-title">88.3% active rate — target 90%</div>
                <div class="insight-grid-desc">
                    Active contract rate of 88.3% is 1.7% below the 90% KPI target. Closing the 11 expired and 2 critical contracts would bring the rate to 96.4%.
                </div>
                <span class="insight-grid-pill">Target: 90%</span>
            </div>
            """, unsafe_allow_html=True)
            
            # Card 6: TIMING
            st.markdown("""
            <div class="insight-grid-card purple-card">
                <div class="insight-lbl-row">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                        <circle cx="12" cy="12" r="10"></circle>
                        <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    Timing
                </div>
                <div class="insight-grid-title">December 2025 is the peak expiry month</div>
                <div class="insight-grid-desc">
                    11 contracts expire in December 2025 — the highest risk month. Begin advance preparation in Q3 2025 to avoid year-end operational disruptions.
                </div>
                <span class="insight-grid-pill">11 contracts · Dec 25</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown('<div class="insights-cta-marker"></div>', unsafe_allow_html=True)
        if st.button("✨ Generate Contract Risk Report >", key="bottom_cta_gen_report_inside", use_container_width=True):
            st.toast("✨ Generating comprehensive contract risk audit report...")

# ──────────────────────────────────────────────────────────────────────────────
# MAIN RENDER FUNCTION
# ──────────────────────────────────────────────────────────────────────────────
def render_lease_contract(df_raw=None):
    from .navigation import show_topnav

    _init_state(df_raw)
    st.markdown(_PAGE_CSS + '<div class="lc-page-marker"></div>', unsafe_allow_html=True)

    df_all = st.session_state.lc_filtered_df

    # ─────────────────────────────────────────────
    # HEADER SECTION (SINGLE ROW REDESIGN - NO ADD CONTRACT)
    # ─────────────────────────────────────────────
    total_val = len(df_all)
    active_val = len(df_all[df_all["Status"] == "Valid"])
    expiring_val = len(df_all[df_all["Status"] == "Anomaly"])
    expired_val = len(df_all[df_all["Status"] == "Expired"])

    h_col1, h_col2, h_col3, h_col4 = st.columns([4.2, 2.5, 1.2, 1.1])
    
    with h_col1:
        st.markdown("""
        <div class="header-left">
            <div class="header-icon-box">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                    <line x1="16" y1="13" x2="8" y2="13"></line>
                    <line x1="16" y1="17" x2="8" y2="17"></line>
                    <polyline points="10 9 9 9 8 9"></polyline>
                </svg>
            </div>
            <div class="header-title-box">
                <div class="header-title-row">
                    <div class="header-main-title">Lease Contract</div>
                    <span class="header-badge">18 EXPIRING SOON</span>
                </div>
                <div class="header-subtitle">Monitor tenant contract status and contract lifecycle.</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with h_col2:
        st.markdown(f"""
        <div class="header-kpi-widget">
            <div class="header-kpi-col">
                <span class="header-kpi-val total">{total_val}</span>
                <span class="header-kpi-lbl">Total</span>
            </div>
            <div class="header-kpi-divider"></div>
            <div class="header-kpi-col">
                <span class="header-kpi-val active">{active_val}</span>
                <span class="header-kpi-lbl">Active</span>
            </div>
            <div class="header-kpi-divider"></div>
            <div class="header-kpi-col">
                <span class="header-kpi-val expiring">{expiring_val}</span>
                <span class="header-kpi-lbl">Expiring</span>
            </div>
            <div class="header-kpi-divider"></div>
            <div class="header-kpi-col">
                <span class="header-kpi-val expired">{expired_val}</span>
                <span class="header-kpi-lbl">Expired</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with h_col3:
        st.markdown('<div class="header-btn-alerts-marker"></div>', unsafe_allow_html=True)
        if st.button("🔔 Set Alerts", key="hc_set_alerts", use_container_width=True):
            st.toast("🔔 Alert triggers configured successfully!")
            
    with h_col4:
        st.markdown('<div class="header-btn-export-marker"></div>', unsafe_allow_html=True)
        csv = df_all[["No", "Name/Tenant", "Sub", "Valid Period", "Unit Name/Loc", "Status", "Skema"]].to_csv(index=False).encode("utf-8")
        st.download_button("⬇ Export", data=csv, file_name="lease_contracts.csv", mime="text/csv", use_container_width=True, key="hc_export")

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # ── Render Add Contract Form ──
    if st.session_state.lc_show_form:
        _render_add_form()

    # ─────────────────────────────────────────────
    # FILTERS ROW
    # ─────────────────────────────────────────────
    st.markdown('<div class="filters-marker"></div>', unsafe_allow_html=True)
    f_lbl_col, f_t_col, f_type_col, f_cat_col, f_stat_col, f_spacer_col, f_reset_col, f_apply_col = st.columns([0.7, 1.5, 1.5, 1.5, 1.5, 3.0, 1.1, 1.2], gap="small")

    with f_lbl_col:
        st.markdown("""
        <div class="filters-label-box">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="4" y1="21" x2="4" y2="14"></line>
                <line x1="4" y1="10" x2="4" y2="3"></line>
                <line x1="12" y1="21" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12" y2="3"></line>
                <line x1="20" y1="21" x2="20" y2="16"></line>
                <line x1="20" y1="12" x2="20" y2="3"></line>
                <line x1="1" y1="14" x2="7" y2="14"></line>
                <line x1="9" y1="8" x2="15" y2="8"></line>
                <line x1="17" y1="16" x2="23" y2="16"></line>
            </svg>
            <span class="filters-lbl-text">Filters</span>
            <div class="filters-lbl-divider"></div>
        </div>
        """, unsafe_allow_html=True)

    with f_t_col:
        st.selectbox(
            "Terminal",
            options=["All Terminals", "T1", "T2", "T3", "T3U"],
            key="f_terminal",
            label_visibility="collapsed"
        )

    with f_type_col:
        st.selectbox(
            "Contract Type",
            options=["All Types", "Revenue Sharing", "RS+MO", "MGRS"],
            key="f_type",
            label_visibility="collapsed"
        )

    with f_cat_col:
        st.selectbox(
            "Business Category",
            options=["All Categories"],
            key="f_category",
            label_visibility="collapsed"
        )

    with f_stat_col:
        st.selectbox(
            "Contract Status",
            options=["All Status", "Valid", "Anomaly", "Expired"],
            key="f_status",
            label_visibility="collapsed"
        )

    with f_spacer_col:
        st.write("")

    with f_reset_col:
        st.markdown('<div class="btn-reset-marker"></div>', unsafe_allow_html=True)
        if st.button("⟳ Reset", key="lc_btn_reset", use_container_width=True):
            st.session_state.f_terminal = "All Terminals"
            st.session_state.f_type = "All Types"
            st.session_state.f_category = "All Categories"
            st.session_state.f_status = "All Status"
            st.session_state.lc_filtered_df = st.session_state.lc_df
            st.rerun()

    with f_apply_col:
        st.markdown('<div class="btn-apply-marker"></div>', unsafe_allow_html=True)
        if st.button("Apply", key="lc_btn_apply", use_container_width=True):
            df_filt = st.session_state.lc_df.copy()
            
            # 1. Terminal Filter
            sel_term = st.session_state.f_terminal.replace("Terminal ", "")
            if sel_term != "All Terminals":
                df_filt = df_filt[df_filt["Terminal"] == sel_term]
                
            # 2. Contract Type Filter
            sel_type = st.session_state.f_type.replace("Contract Type ", "")
            if sel_type != "All Types":
                df_filt = df_filt[df_filt["Skema"] == sel_type]
                
            # 3. Contract Status Filter
            sel_status = st.session_state.f_status.replace("Contract Status ", "")
            if sel_status != "All Status":
                df_filt = df_filt[df_filt["Status"] == sel_status]
                
            st.session_state.lc_filtered_df = df_filt
            st.rerun()

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # TOP KPI CARDS
    # ─────────────────────────────────────────────
    total_val = len(df_all)
    t1_val = len(df_all[df_all["Terminal"] == "T1"])
    t2_val = len(df_all[df_all["Terminal"] == "T2"])
    t3_val = len(df_all[df_all["Terminal"] == "T3"])
    t3u_val = len(df_all[df_all["Terminal"] == "T3U"])
    
    active_df = df_all[df_all["Status"] == "Valid"]
    active_val = len(active_df)
    rs_val = len(active_df[active_df["Skema"] == "Revenue Sharing"])
    rs_mo_val = len(active_df[active_df["Skema"] == "RS+MO"])
    mgrs_val = len(active_df[active_df["Skema"] == "MGRS"])
    
    anomaly_df = df_all[df_all["Status"] == "Anomaly"]
    expiring_val = len(anomaly_df)
    d30_val = len(anomaly_df[anomaly_df["Sisa"] <= 30])
    d60_val = len(anomaly_df[(anomaly_df["Sisa"] > 30) & (anomaly_df["Sisa"] <= 60)])
    d90_val = len(anomaly_df[(anomaly_df["Sisa"] > 60) & (anomaly_df["Sisa"] <= 90)])
    
    expired_df = df_all[df_all["Status"] == "Expired"]
    expired_val = len(expired_df)
    exp_t1 = len(expired_df[expired_df["Terminal"] == "T1"])
    exp_t2 = len(expired_df[expired_df["Terminal"] == "T2"])
    exp_t3 = len(expired_df[expired_df["Terminal"] == "T3"])
    exp_t3u = len(expired_df[expired_df["Terminal"] == "T3U"])

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        svg_spark_total = _generate_svg_sparkline(SPARK_TOTAL, "#6366F1", "#6366F1", "#6366F1")
        icon_total = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>'
        html_total = _render_kpi_card_html(
            icon_svg=icon_total,
            icon_class="total",
            badge_text="↗ +3.8%",
            badge_class="positive",
            title="Total Contract",
            value=f"{total_val}",
            unit="contracts",
            subtitle="All terminals · FY 2024",
            progress_items=[("T1", t1_val), ("T2", t2_val), ("T3", t3_val), ("T3U", t3u_val)],
            progress_color="#6366F1",
            comparison="vs 238 prior yr",
            sparkline_svg=svg_spark_total
        )
        st.markdown(html_total, unsafe_allow_html=True)
        
    with col2:
        svg_spark_active = _generate_svg_sparkline(SPARK_ACTIVE, "#10B981", "#10B981", "#10B981")
        icon_active = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>'
        html_active = _render_kpi_card_html(
            icon_svg=icon_active,
            icon_class="active",
            badge_text="↗ +2.8%",
            badge_class="positive",
            title="Active Contract",
            value=f"{active_val}",
            unit="active",
            subtitle=f"{active_val/total_val*100:.1f}% of total portfolio" if total_val > 0 else "88.3% of total portfolio",
            progress_items=[("RS", rs_val), ("RS+MO", rs_mo_val), ("MGRS", mgrs_val)],
            progress_color="#10B981",
            comparison="vs 212 prior yr",
            sparkline_svg=svg_spark_active
        )
        st.markdown(html_active, unsafe_allow_html=True)
        
    with col3:
        svg_spark_expiring = _generate_svg_sparkline(SPARK_EXPIRING, "#F59E0B", "#F59E0B", "#F59E0B")
        icon_expiring = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>'
        html_expiring = _render_kpi_card_html(
            icon_svg=icon_expiring,
            icon_class="expiring",
            badge_text="↘ 22.2%",
            badge_class="negative",
            title="Expiring Soon",
            value=f"{expiring_val}",
            unit="contracts",
            subtitle="Within next 90 days",
            progress_items=[("30d", d30_val), ("60d", d60_val), ("90d", d90_val)],
            progress_color="#F59E0B",
            comparison="vs 23 prior period",
            sparkline_svg=svg_spark_expiring
        )
        st.markdown(html_expiring, unsafe_allow_html=True)
        
    with col4:
        svg_spark_expired = _generate_svg_sparkline(SPARK_EXPIRED, "#EF4444", "#EF4444", "#EF4444")
        icon_expired = '<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#EF4444" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>'
        html_expired = _render_kpi_card_html(
            icon_svg=icon_expired,
            icon_class="expired",
            badge_text="↘ 15.4%",
            badge_class="negative",
            title="Expired Contract",
            value=f"{expired_val}",
            unit="contracts",
            subtitle="Requires immediate action",
            progress_items=[("T1", exp_t1), ("T2", exp_t2), ("T3", exp_t3), ("T3U", exp_t3u)],
            progress_color="#EF4444",
            comparison="vs 13 prior yr",
            sparkline_svg=svg_spark_expired
        )
        st.markdown(html_expired, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # CONTRACT EXPIRY TIMELINE & DONUT CHARTS (3-COLUMN REDESIGN)
    # ─────────────────────────────────────────────
    col_left, col_mid, col_right = st.columns([1.7, 1.0, 1.0])
    
    # ── Column 1: Contract Expiry Timeline ──
    with col_left:
        with st.container():
            st.markdown('<div class="premium-card-marker"></div>', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Contract Expiry Timeline</div><div class="card-subtitle">Monthly contract expirations — Next 12 months (Jan-Dec 2025)</div>', unsafe_allow_html=True)
            
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
            
            ren_month_counts = {m: int(exp_month_counts[m] * 0.6) for m in months_list}
            
            tot_exp_val = sum(exp_month_counts.values())
            tot_ren_val = sum(ren_month_counts.values())
            tot_ren_rate = int(tot_ren_val / tot_exp_val * 100) if tot_exp_val > 0 else 0
            risk_months_count = sum(1 for v in exp_month_counts.values() if v >= 8)

            html_timeline_kpis = f"""
            <div class="timeline-kpi-row">
                <div class="timeline-kpi-card expiring">
                    <div class="timeline-kpi-val">{tot_exp_val}</div>
                    <div class="timeline-kpi-lbl">contracts</div>
                </div>
                <div class="timeline-kpi-card renewed">
                    <div class="timeline-kpi-val">{tot_ren_val}</div>
                    <div class="timeline-kpi-lbl">contracts</div>
                </div>
                <div class="timeline-kpi-card rate">
                    <div class="timeline-kpi-val">{tot_ren_rate}%</div>
                    <div class="timeline-kpi-lbl">of expiring</div>
                </div>
                <div class="timeline-kpi-card risk">
                    <div class="timeline-kpi-val">{risk_months_count}</div>
                    <div class="timeline-kpi-lbl">months &ge; 8</div>
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
                <div class="risk-legend-item"><span class="risk-legend-dot" style="background-color: #10B981;"></span><span>Renewed</span></div>
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
            
            c_types = _get_contract_types(df_raw)
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
            
            sub_left, sub_right = st.columns([1, 1])
            with sub_left:
                st.plotly_chart(_build_donut_chart({"RS": d_rs, "RS+MO": d_rs_mo, "MGRS": d_mgrs}, ["#6366F1", "#0EA5E9", "#F59E0B"]), use_container_width=True, config=dict(displayModeBar=False))
            with sub_right:
                html_dist_stack = f"""
                <div class="dist-stack">
                    <div class="dist-card rs">
                        <div class="dist-card-header">
                            <span class="dist-card-title-row"><span class="dist-card-dot"></span>{label_rs}</span>
                            <span class="dist-card-pct">{d_rs_pct:.1f}%</span>
                        </div>
                        <div class="dist-card-body">
                            <span class="dist-card-count">{d_rs}</span>
                            <span class="dist-card-val">Rp {d_rs*0.74:.1f}B</span>
                        </div>
                    </div>
                    <div class="dist-card rs_mo">
                        <div class="dist-card-header">
                            <span class="dist-card-title-row"><span class="dist-card-dot"></span>{label_rs_mo}</span>
                            <span class="dist-card-pct">{d_rs_mo_pct:.1f}%</span>
                        </div>
                        <div class="dist-card-body">
                            <span class="dist-card-count">{d_rs_mo}</span>
                            <span class="dist-card-val">Rp {d_rs_mo*0.74:.1f}B</span>
                        </div>
                    </div>
                    <div class="dist-card mgrs">
                        <div class="dist-card-header">
                            <span class="dist-card-title-row"><span class="dist-card-dot"></span>{label_mgrs}</span>
                            <span class="dist-card-pct">{d_mgrs_pct:.1f}%</span>
                        </div>
                        <div class="dist-card-body">
                            <span class="dist-card-count">{d_mgrs}</span>
                            <span class="dist-card-val">Rp {d_mgrs*0.72:.1f}B</span>
                        </div>
                    </div>
                </div>
                """
                st.markdown(html_dist_stack, unsafe_allow_html=True)

    # ── Column 3: Contract Status ──
    with col_right:
        with st.container():
            st.markdown('<div class="premium-card-marker"></div>', unsafe_allow_html=True)
            st.markdown('<div class="card-title">Contract Status</div><div class="card-subtitle">Portfolio health overview</div>', unsafe_allow_html=True)
            
            p_active = (active_val / total_val * 100) if total_val > 0 else 0
            p_expiring = (expiring_val / total_val * 100) if total_val > 0 else 0
            p_expired = (expired_val / total_val * 100) if total_val > 0 else 0

            html_status_list = f"""
            <div class="status-list">
                <div class="status-row">
                    <div class="status-row-header">
                        <div class="status-row-label-row"><span class="status-row-icon active">&#10003;</span>Active</div>
                        <div class="status-row-val">{active_val} <span>({p_active:.1f}%)</span></div>
                    </div>
                    <div class="status-row-progress-bg">
                        <div class="status-row-progress-fill" style="width: {p_active}%; background-color: #10B981;"></div>
                    </div>
                </div>
                <div class="status-row">
                    <div class="status-row-header">
                        <div class="status-row-label-row"><span class="status-row-icon expiring">&#9888;</span>Expiring Soon</div>
                        <div class="status-row-val">{expiring_val} <span>({p_expiring:.1f}%)</span></div>
                    </div>
                    <div class="status-row-progress-bg">
                        <div class="status-row-progress-fill" style="width: {p_expiring}%; background-color: #F59E0B;"></div>
                    </div>
                </div>
                <div class="status-row">
                    <div class="status-row-header">
                        <div class="status-row-label-row"><span class="status-row-icon expired">&#10007;</span>Expired</div>
                        <div class="status-row-val">{expired_val} <span>({p_expired:.1f}%)</span></div>
                    </div>
                    <div class="status-row-progress-bg">
                        <div class="status-row-progress-fill" style="width: {p_expired}%; background-color: #EF4444;"></div>
                    </div>
                </div>
            </div>
            """
            st.markdown(html_status_list, unsafe_allow_html=True)
            st.plotly_chart(_build_mini_donut(active_val, expiring_val, expired_val), use_container_width=True, config=dict(displayModeBar=False))
            
            html_status_score = f"""
            <div class="status-score-section">
                <span class="status-score-title">Portfolio Health Score</span>
                <span class="status-score-val">{p_active:.1f}%</span>
                <span class="status-score-desc">Active rate &middot; Target: 90%</span>
            </div>
            """
            st.markdown(html_status_score, unsafe_allow_html=True)

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # CRITICAL / EXPIRING TABLES (SECTION 1-3 DYNAMIC GENERATION)
    # ─────────────────────────────────────────────
    st.markdown(
        f'<div class="premium-card">'
        f'<div class="card-title">Contracts Expiring Soon</div>'
        f'<div class="card-subtitle">Sorted by remaining days</div>',
        unsafe_allow_html=True
    )

    # Build dynamic list of critical contracts
    dynamic_critical = []
    crit_df = df_all[(df_all["Status"] == "Anomaly") & (df_all["Sisa"] <= 30)]
    for _, r in crit_df.iterrows():
        end_date = r["Valid Period"].split(" - ")[1] if " - " in r["Valid Period"] else "31 Jan 2025"
        val_m = f"Rp {2.0 + (r['No'] % 10) * 0.9:.1f}B"
        dynamic_critical.append({
            "tenant": r["Name/Tenant"], "terminal": r["Terminal"], "type": r["Skema"],
            "end_date": end_date, "remaining": f"{r['Sisa']}d", "value": val_m, "status": "Critical"
        })

    # Build dynamic list of expiring soon contracts
    dynamic_expiring = []
    exp_df = df_all[(df_all["Status"] == "Anomaly") & (df_all["Sisa"] > 30) & (df_all["Sisa"] <= 90)]
    for _, r in exp_df.iterrows():
        end_date = r["Valid Period"].split(" - ")[1] if " - " in r["Valid Period"] else "01 Mar 2025"
        val_m = f"Rp {4.0 + (r['No'] % 10) * 1.2:.1f}B"
        dynamic_expiring.append({
            "tenant": r["Name/Tenant"], "terminal": r["Terminal"], "type": r["Skema"],
            "end_date": end_date, "remaining": f"{r['Sisa']}d", "value": val_m, "status": "Expiring Soon"
        })

    # Build dynamic list of approaching renewal contracts
    dynamic_approaching = []
    app_df = df_all[(df_all["Status"] == "Valid") & (df_all["Sisa"] > 90)].sort_values(by="Sisa")
    for _, r in app_df.head(5).iterrows():
        end_date = r["Valid Period"].split(" - ")[1] if " - " in r["Valid Period"] else "02 May 2025"
        val_m = f"Rp {2.0 + (r['No'] % 5) * 1.5:.1f}B"
        dynamic_approaching.append({
            "tenant": r["Name/Tenant"], "terminal": r["Terminal"], "type": r["Skema"],
            "end_date": end_date, "remaining": f"{r['Sisa']}d", "value": val_m, "status": "Approaching"
        })

    # Critical Contracts Banner & Table
    st.markdown('<div class="alert-banner alert-danger"><span style="font-size: 15px;">⚠️</span> Critical — Expires within 30 days</div>', unsafe_allow_html=True)
    crit_rows = ""
    for item in dynamic_critical:
        crit_rows += (
            f"<tr>"
            f"<td style='font-weight: 700; color: #0F172A;'>{item['tenant']}</td>"
            f"<td>{item['terminal']}</td>"
            f"<td style='color: #64748B;'>{item['type']}</td>"
            f"<td style='font-weight: 600;'>{item['end_date']}</td>"
            f"<td style='font-weight: 800; color: #EF4444;'>{item['remaining']}</td>"
            f"<td style='font-weight: 700; color: #0F172A;'>{item['value']}</td>"
            f"<td><span class='status-badge badge-danger'>{item['status']}</span></td>"
            f"</tr>"
        )
    st.markdown(
        f'<table class="custom-table" style="margin-bottom: 24px;">'
        f'<thead><tr><th>Tenant</th><th>Terminal</th><th>Contract Type</th><th>End Date</th><th>Remaining</th><th>Value</th><th>Status</th></tr></thead>'
        f'<tbody>{crit_rows if crit_rows else "<tr><td colspan=7 style=\'text-align:center;color:#64748B;\'>No critical contracts found for current filters</td></tr>"}</tbody>'
        f'</table>',
        unsafe_allow_html=True
    )

    # Expiring Soon Banner & Table
    st.markdown('<div class="alert-banner alert-warning"><span style="font-size: 15px;">⏳</span> Expiring Soon — Expires within 31 to 90 days</div>', unsafe_allow_html=True)
    exp_rows = ""
    for item in dynamic_expiring:
        exp_rows += (
            f"<tr>"
            f"<td style='font-weight: 700; color: #0F172A;'>{item['tenant']}</td>"
            f"<td>{item['terminal']}</td>"
            f"<td style='color: #64748B;'>{item['type']}</td>"
            f"<td style='font-weight: 600;'>{item['end_date']}</td>"
            f"<td style='font-weight: 800; color: #F59E0B;'>{item['remaining']}</td>"
            f"<td style='font-weight: 700; color: #0F172A;'>{item['value']}</td>"
            f"<td><span class='status-badge badge-warning'>{item['status']}</span></td>"
            f"</tr>"
        )
    st.markdown(
        f'<table class="custom-table" style="margin-bottom: 24px;">'
        f'<thead><tr><th>Tenant</th><th>Terminal</th><th>Contract Type</th><th>End Date</th><th>Remaining</th><th>Value</th><th>Status</th></tr></thead>'
        f'<tbody>{exp_rows if exp_rows else "<tr><td colspan=7 style=\'text-align:center;color:#64748B;\'>No expiring soon contracts found for current filters</td></tr>"}</tbody>'
        f'</table>',
        unsafe_allow_html=True
    )

    # Approaching Renewal Banner & Table
    st.markdown('<div class="alert-banner alert-success"><span style="font-size: 15px;">🛡️</span> Approaching Renewal — Expires in 90+ days</div>', unsafe_allow_html=True)
    app_rows = ""
    for item in dynamic_approaching:
        app_rows += (
            f"<tr>"
            f"<td style='font-weight: 700; color: #0F172A;'>{item['tenant']}</td>"
            f"<td>{item['terminal']}</td>"
            f"<td style='color: #64748B;'>{item['type']}</td>"
            f"<td style='font-weight: 600;'>{item['end_date']}</td>"
            f"<td style='font-weight: 800; color: #10B981;'>{item['remaining']}</td>"
            f"<td style='font-weight: 700; color: #0F172A;'>{item['value']}</td>"
            f"<td><span class='status-badge badge-success'>{item['status']}</span></td>"
            f"</tr>"
        )
    st.markdown(
        f'<table class="custom-table">'
        f'<thead><tr><th>Tenant</th><th>Terminal</th><th>Contract Type</th><th>End Date</th><th>Remaining</th><th>Value</th><th>Status</th></tr></thead>'
        f'<tbody>{app_rows if app_rows else "<tr><td colspan=7 style=\'text-align:center;color:#64748B;\'>No approaching renewal contracts found for current filters</td></tr>"}</tbody>'
        f'</table>'
        f'</div>',
        unsafe_allow_html=True
    )

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────
    # BOTTOM SECTION: SIDE-BY-SIDE PANELS
    # ─────────────────────────────────────────────
    col_left, col_right = st.columns([1.1, 2.5])
    
    with col_left:
        _render_action_required()
        _render_renewal_pipeline()
        
    with col_right:
        render_executive_insights()

# ── Standalone Running compatibility ─────────
if __name__ == "__main__":
    st.set_page_config(page_title="Lease Contract Dashboard", layout="wide")
    render_lease_contract()
