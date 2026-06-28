import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as go
from datetime import date, datetime
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
# DUMMY DATA GENERATOR (RETAINS ORIGINAL DATA & STRUCTURE, EXPANDS TO 247 ROWS)
# ──────────────────────────────────────────────────────────────────────────────
def _get_contract_data() -> pd.DataFrame:
    # Important specific records required by the new design
    data = [
        # Critical (Status = Expiring Soon / Critical, Sisa <= 30)
        {"No": 1, "Name/Tenant": "7-Eleven", "Sub": "Critical - Expires Soon", "Valid Period": "01 Jan 2023 - 31 Jan 2025", "Unit Name/Loc": "T1 - Area A", "Status": "Anomaly", "Conflict Info": True, "Kode": "FB-01-01", "Skema": "Revenue Sharing", "Sisa": 16, "Terminal": "T1"},
        {"No": 2, "Name/Tenant": "Sari Roti", "Sub": "Critical - Expires Soon", "Valid Period": "15 Feb 2023 - 14 Feb 2025", "Unit Name/Loc": "T2 - Area B", "Status": "Anomaly", "Conflict Info": True, "Kode": "RT-02-07", "Skema": "Revenue Sharing", "Sisa": 30, "Terminal": "T2"},
        
        # Expiring Soon (Status = Anomaly, 31 <= Sisa <= 90)
        {"No": 3, "Name/Tenant": "KFC", "Sub": "Expiring Soon", "Valid Period": "01 Mar 2023 - 01 Mar 2025", "Unit Name/Loc": "T3 - Area A", "Status": "Anomaly", "Conflict Info": False, "Kode": "FB-01-03", "Skema": "Revenue Sharing", "Sisa": 44, "Terminal": "T3"},
        {"No": 4, "Name/Tenant": "Timezone", "Sub": "Expiring Soon", "Valid Period": "02 Apr 2023 - 02 Apr 2025", "Unit Name/Loc": "T1 - Area C", "Status": "Anomaly", "Conflict Info": True, "Kode": "RT-01-02", "Skema": "RS+MO", "Sisa": 75, "Terminal": "T1"},
        {"No": 5, "Name/Tenant": "Lion Lounge", "Sub": "Expiring Soon", "Valid Period": "16 Apr 2023 - 16 Apr 2025", "Unit Name/Loc": "T1 - Area VIP", "Status": "Anomaly", "Conflict Info": True, "Kode": "LG-01-12", "Skema": "MGRS", "Sisa": 89, "Terminal": "T1"},
        
        # Approaching Renewal (Status = Valid, Sisa > 90)
        {"No": 6, "Name/Tenant": "Burger King", "Sub": "Approaching Renewal", "Valid Period": "02 May 2023 - 02 May 2025", "Unit Name/Loc": "T2 - Area D", "Status": "Valid", "Conflict Info": False, "Kode": "FB-02-05", "Skema": "RS+MO", "Sisa": 105, "Terminal": "T2"},
        {"No": 7, "Name/Tenant": "Mie Ayam 99", "Sub": "Approaching Renewal", "Valid Period": "02 Jun 2023 - 02 Jun 2025", "Unit Name/Loc": "T3 - Area B", "Status": "Valid", "Conflict Info": False, "Kode": "RT-03-02", "Skema": "Revenue Sharing", "Sisa": 136, "Terminal": "T3"},
        {"No": 8, "Name/Tenant": "Gramedia", "Sub": "Approaching Renewal", "Valid Period": "02 Jul 2023 - 02 Jul 2025", "Unit Name/Loc": "T1 - Area E", "Status": "Valid", "Conflict Info": False, "Kode": "SV-01-09", "Skema": "MGRS", "Sisa": 166, "Terminal": "T1"},
        
        # Expired (Status = Expired)
        {"No": 9, "Name/Tenant": "Dunkin", "Sub": "Contract Expired", "Valid Period": "01 Jan 2022 - 31 Dec 2024", "Unit Name/Loc": "T1 - Area F", "Status": "Expired", "Conflict Info": True, "Kode": "FB-01-09", "Skema": "Revenue Sharing", "Sisa": -15, "Terminal": "T1"},
        {"No": 10, "Name/Tenant": "HokBen", "Sub": "Contract Expired", "Valid Period": "01 Jan 2022 - 31 Dec 2024", "Unit Name/Loc": "T2 - Area A", "Status": "Expired", "Conflict Info": True, "Kode": "RT-02-11", "Skema": "Revenue Sharing", "Sisa": -20, "Terminal": "T2"},
        {"No": 11, "Name/Tenant": "Optik Seis", "Sub": "Contract Expired", "Valid Period": "01 Jan 2022 - 31 Dec 2024", "Unit Name/Loc": "T3 - Area C", "Status": "Expired", "Conflict Info": True, "Kode": "SV-03-01", "Skema": "RS+MO", "Sisa": -30, "Terminal": "T3"},
    ]
    
    # We will generate the rest of the 247 rows programmatically to match the exact counts:
    # Terminals: T1 (48), T2 (112), T3 (61), T3U (26)
    # Skema: Revenue Sharing (128), RS+MO (81), MGRS (38)
    # Status: Valid (218), Anomaly (18), Expired (11)
    
    current_t1 = 5 # 7-Eleven, Timezone, Lion Lounge, Gramedia, Dunkin
    current_t2 = 3 # Sari Roti, Burger King, HokBen
    current_t3 = 3 # KFC, Mie Ayam 99, Optik Seis
    current_t3u = 0
    
    current_rs = 6 # 7-Eleven, Sari Roti, KFC, Mie Ayam 99, Dunkin, HokBen
    current_rs_mo = 3 # Timezone, Burger King, Optik Seis
    current_mgrs = 2 # Lion Lounge, Gramedia
    
    current_valid = 3 # Burger King, Mie Ayam 99, Gramedia
    current_anomaly = 5 # 7-Eleven, Sari Roti, KFC, Timezone, Lion Lounge
    current_expired = 3 # Dunkin, HokBen, Optik Seis
    
    for i in range(12, 248):
        # Assign status
        if current_valid < 218:
            status = "Valid"
            sisa = 100 + (i % 500)
            current_valid += 1
        elif current_anomaly < 18:
            status = "Anomaly"
            sisa = 10 + (i % 80)
            current_anomaly += 1
        else:
            status = "Expired"
            sisa = -1 * (10 + (i % 300))
            current_expired += 1
            
        # Assign terminal
        if current_t1 < 48:
            terminal = "T1"
            current_t1 += 1
        elif current_t2 < 112:
            terminal = "T2"
            current_t2 += 1
        elif current_t3 < 61:
            terminal = "T3"
            current_t3 += 1
        else:
            terminal = "T3U"
            current_t3u += 1
            
        # Assign skema
        if current_rs < 128:
            skema = "Revenue Sharing"
            current_rs += 1
        elif current_rs_mo < 81:
            skema = "RS+MO"
            current_rs_mo += 1
        else:
            skema = "MGRS"
            current_mgrs += 1
            
        tenant_name = f"Tenant {i}"
        unit_name = f"{terminal} - Loc {i}"
        valid_period = f"01 Jan 2024 - 31 Dec 2025"
        
        data.append({
            "No": i,
            "Name/Tenant": tenant_name,
            "Sub": "General Contract",
            "Valid Period": valid_period,
            "Unit Name/Loc": unit_name,
            "Status": status,
            "Conflict Info": (i % 11 == 0),
            "Kode": f"KD-{i:03d}",
            "Skema": skema,
            "Sisa": sisa,
            "Terminal": terminal
        })
        
    return pd.DataFrame(data)


# Expiry Timeline Data (Next 12 Months: Jan - Dec)
EXPIRY_TIMELINE_DATA = pd.DataFrame({
    "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "Expiring": [5, 8, 4, 3, 6, 7, 2, 5, 8, 4, 4, 11],
    "Renewed": [3, 5, 3, 2, 4, 4, 1, 3, 5, 3, 2, 4]
})

# Contract Type Distribution Data
CONTRACT_TYPES = {
    "RS": 128,
    "RS+MO": 81,
    "MGRS": 38
}

# Critical Contracts (Expires within 30 days)
CRITICAL_CONTRACTS = [
    {"tenant": "7-Eleven", "terminal": "T1", "type": "Revenue Sharing", "end_date": "31 Jan 2025", "remaining": "16d", "value": "Rp 2.8M", "status": "Critical"},
    {"tenant": "Sari Roti", "terminal": "T2", "type": "Revenue Sharing", "end_date": "14 Feb 2025", "remaining": "30d", "value": "Rp 3.7M", "status": "Critical"}
]

# Expiring Soon (31 - 90 days)
EXPIRING_SOON_CONTRACTS = [
    {"tenant": "KFC", "terminal": "T3", "type": "Revenue Sharing", "end_date": "01 Mar 2025", "remaining": "44d", "value": "Rp 4.2M", "status": "Expiring Soon"},
    {"tenant": "Timezone", "terminal": "T1", "type": "Rental", "end_date": "02 Apr 2025", "remaining": "75d", "value": "Rp 7.3M", "status": "Expiring Soon"},
    {"tenant": "Lion Lounge", "terminal": "T1", "type": "MGRS", "end_date": "16 Apr 2025", "remaining": "89d", "value": "Rp 10.2M", "status": "Expiring Soon"}
]

# Approaching Renewal (91+ days)
APPROACHING_RENEWAL_CONTRACTS = [
    {"tenant": "Burger King", "terminal": "T2", "type": "Rental", "end_date": "02 May 2025", "remaining": "105d", "value": "Rp 5.5M", "status": "Approaching"},
    {"tenant": "Mie Ayam 99", "terminal": "T3", "type": "Revenue Sharing", "end_date": "02 Jun 2025", "remaining": "136d", "value": "Rp 2.2M", "status": "Approaching"},
    {"tenant": "Gramedia", "terminal": "T1", "type": "MGRS", "end_date": "02 Jul 2025", "remaining": "166d", "value": "Rp 6.8M", "status": "Approaching"}
]

# Sidebar Pipeline Data
RENEWAL_PIPELINE = [
    {"tenant": "DFS Indonesia", "value": "Rp 42.7M", "status": "Low"},
    {"tenant": "Garuda Exec", "value": "Rp 14.8M", "status": "Low"},
    {"tenant": "Gramedia", "value": "Rp 6.8M", "status": "Medium"}
]


# ──────────────────────────────────────────────────────────────────────────────
# CSS STYLE DEFINITIONS
# ──────────────────────────────────────────────────────────────────────────────
_PAGE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800&display=swap');

.stApp, .stApp * {
    font-family: 'Inter', sans-serif !important;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp [class*="-title"], .stApp [class*="-header"], .stApp [class*="title-"] {
    font-family: 'Montserrat', sans-serif !important;
}

body:has(.lc-page-marker) .stApp {
    background: #F8FAFC !important;
}

/* Jarak vertikal Filter Bar dan Header */
body:has(.lc-page-marker) div[data-testid="stHorizontalBlock"]:has(.lc-filter-v2-label) {
    margin-top: -15px !important;
}
body:has(.lc-page-marker) div[data-testid="stLayoutWrapper"]:has(.lc-filter-v2-label) {
    margin-top: -15px !important;
}

body:has(.lc-page-marker) div[data-testid="stHorizontalBlock"]:has(.kpi-card-new) {
    margin-top: -4px !important;
}

/* The premium-card columns are each wrapped in their own st.container(),
   which (unlike the plain st.markdown() cards in the KPI row above) ends
   up with a narrower effective gap between columns — force it back to
   the same 16px used between other major sections/cards. */
/* Use CSS Grid (not flex) for this row — grid items stretch to fill the
   row's height by default, which is far more reliable than chasing
   Streamlit's own nested flex wrappers level by level. */
div[data-testid="stHorizontalBlock"]:has(.premium-card-marker) {
    display: grid !important;
    grid-template-columns: 1.7fr 1fr 1fr !important;
    gap: 16px !important;
    align-items: stretch !important;
}
div[data-testid="stHorizontalBlock"]:has(.premium-card-marker) > div[data-testid="column"],
div[data-testid="stHorizontalBlock"]:has(.premium-card-marker) > div[data-testid="stColumn"] {
    width: 100% !important;
    min-width: 0 !important;
    height: 100% !important;
    display: block !important;
}
div[data-testid="stHorizontalBlock"]:has(.premium-card-marker) > div[data-testid="column"] > div,
div[data-testid="stHorizontalBlock"]:has(.premium-card-marker) > div[data-testid="stColumn"] > div {
    height: 100% !important;
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
    /* No margin-bottom here — inter-section spacing is handled solely by
       the explicit 16px spacer divs between rows, so it stays consistent
       with sections that use other card classes (e.g. .kpi-card-new),
       which don't have a baked-in margin of their own. */
    box-sizing: border-box;
    height: 100%;
    min-height: 560px;
    display: flex;
    flex-direction: column;
}
/* Contract Type Distribution is the 2nd card in this row — give its
   donut + category row room to breathe vertically so the card fills
   its now-equal height with genuinely larger content instead of gaps. */
div[data-testid="stHorizontalBlock"]:has(.premium-card-marker) > div:nth-child(2) [data-testid="stHorizontalBlock"]:has(.dist-stack) {
    flex: 1 1 auto;
    align-items: center;
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

.timeline-kpi-top {
    display: flex;
    align-items: center;
    gap: 8px;
}
.timeline-kpi-icon {
    width: 26px;
    height: 26px;
    border-radius: 999px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    background: rgba(255,255,255,0.7);
}
.timeline-kpi-icon svg { width: 14px; height: 14px; }
.timeline-kpi-card.expiring .timeline-kpi-icon { color: #4F46E5; }
.timeline-kpi-card.renewed .timeline-kpi-icon { color: #10B981; }
.timeline-kpi-card.rate .timeline-kpi-icon { color: #0EA5E9; }
.timeline-kpi-card.risk .timeline-kpi-icon { color: #EF4444; }

.timeline-kpi-val {
    font-size: 19px;
    font-weight: 800;
    line-height: 1;
}
.timeline-kpi-card.expiring .timeline-kpi-val { color: #4F46E5; }
.timeline-kpi-card.renewed .timeline-kpi-val { color: #10B981; }
.timeline-kpi-card.rate .timeline-kpi-val { color: #0EA5E9; }
.timeline-kpi-card.risk .timeline-kpi-val { color: #EF4444; }

.timeline-kpi-lbl {
    font-size: 11px;
    font-weight: 700;
    color: #0F172A;
    margin-top: 8px;
    display: flex;
    flex-direction: column;
}
.timeline-kpi-lbl span {
    font-size: 9.5px;
    font-weight: 500;
    color: #64748B;
    margin-top: 1px;
    text-transform: none;
    letter-spacing: 0;
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
div[data-testid="stHorizontalBlock"]:has(.premium-card-marker) > div:nth-child(2) [data-testid="stPlotlyChart"] {
    margin: 2px 0 10px;
    overflow: visible !important;
}
div[data-testid="stHorizontalBlock"]:has(.premium-card-marker) > div:nth-child(2) [data-testid="stPlotlyChart"] > div {
    margin: 0 auto !important;
    overflow: visible !important;
}
.dist-stack {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.dist-card {
    border-radius: 12px;
    padding: 10px 14px;
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

.dist-total-footer {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid #F1F5F9;
}
.dist-total-icon {
    width: 16px;
    height: 16px;
    color: #94A3B8;
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
}
.dist-total-icon svg {
    width: 14px;
    height: 14px;
    display: block;
}
.dist-total-label {
    font-size: 10.5px;
    font-weight: 600;
    color: #64748B;
    flex: 1;
    line-height: 16px;
}
.dist-total-val {
    font-size: 12px;
    font-weight: 800;
    color: #0F172A;
    line-height: 16px;
}

.status-card {
    border-radius: 12px;
    padding: 10px 14px;
    box-sizing: border-box;
    border: 1px solid transparent;
}
.status-card.active { background-color: #ECFDF5; border-color: #D1FAE5; }
.status-card.expiring { background-color: #FFFBEB; border-color: #FEF3C7; }
.status-card.expired { background-color: #FEF2F2; border-color: #FEE2E2; }

.status-card.active .dist-card-title-row { color: #059669; }
.status-card.expiring .dist-card-title-row { color: #D97706; }
.status-card.expired .dist-card-title-row { color: #DC2626; }

.status-card-dot {
    width: 8px;
    height: 8px;
    border-radius: 2px;
    display: inline-block;
    margin-right: 6px;
}
.status-card-dot.active { background-color: #10B981; }
.status-card-dot.expiring { background-color: #F59E0B; }
.status-card-dot.expired { background-color: #EF4444; }

.dist-card-pct.active { color: #10B981; }
.dist-card-pct.expiring { color: #F59E0B; }
.dist-card-pct.expired { color: #EF4444; }

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

.status-health-badge {
    display: inline-block;
    margin-top: 8px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 10px;
    font-weight: 700;
}
.status-health-badge.good { background-color: #ECFDF5; color: #059669; }
.status-health-badge.fair { background-color: #FFFBEB; color: #D97706; }
.status-health-badge.risk { background-color: #FEF2F2; color: #DC2626; }

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
.custom-table thead tr {
    background: rgba(99, 102, 241, 0.05);
}
.custom-table th {
    text-align: left;
    font-size: 11px;
    font-weight: 700;
    color: #4F46E5;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 11px 14px;
    border-bottom: none;
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

/* ── Contracts Expiring Soon — outer card wraps the title + all 3 pills ── */
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .lc-exp-outer-marker) {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 16px 18px;
    margin-top: -16px !important;
    margin-bottom: 0px !important;
    box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -1px rgba(0,0,0,0.015);
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] [class^="lc-exp-section-marker-"]) {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    margin-top: -6px !important;
    margin-bottom: 0px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    padding: 0px !important;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] [class^="lc-exp-section-marker-"]) > div[data-testid="stElementContainer"]:has([class^="lc-exp-section-marker-"]) {
    display: none;
}
div[data-testid="stElementContainer"]:has(.lc-exp-show-more-marker) + div[data-testid="stHorizontalBlock"] {
    margin-bottom: 16px !important;
}
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .lc-exp-outer-marker) > div[data-testid="stElementContainer"]:has(.lc-exp-outer-marker) {
    display: none;
}
.lc-exp-header-card {
    background: transparent;
    border: none;
    padding: 14px 18px;
    box-sizing: border-box;
}
.lc-exp-header-title { font-size: 16px; font-weight: 800; color: #0F172A; }
.lc-exp-header-sub { font-size: 12px; color: #64748B; margin-top: 2px; }
.lc-exp-stat {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 18px; border-radius: 14px; min-width: 0;
    height: 100%; box-sizing: border-box;
}
.lc-exp-stat.danger { background: #FEF2F2; border: 1px solid #FCA5A5; }
.lc-exp-stat.warning { background: #FFFBEB; border: 1px solid #FCD34D; }
.lc-exp-stat.success { background: #F0FDF4; border: 1px solid #86EFAC; }
.lc-exp-stat-icon {
    width: 32px; height: 32px; border-radius: 50%; background: #FFFFFF;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.lc-exp-stat-text { flex: 1; min-width: 0; display: flex; flex-direction: column; }
.lc-exp-stat-label {
    display: block; font-size: 12.5px; font-weight: 800; line-height: 1.3;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.lc-exp-stat-label.danger { color: #B91C1C; }
.lc-exp-stat-label.warning { color: #B45309; }
.lc-exp-stat-label.success { color: #15803D; }
.lc-exp-stat-caption {
    display: block; font-size: 10.5px; color: #64748B; margin-top: 1px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.lc-exp-stat-value { font-size: 22px; font-weight: 800; color: #0F172A; margin-left: auto; padding-left: 8px; }

/* ── Contracts Expiring Soon — per-severity section cards ── */
.lc-exp-section-card {
    background: transparent;
    border: none;
    margin-bottom: 0px !important;
    overflow: hidden;
}
.lc-exp-section-head {
    display: flex; align-items: center; gap: 10px;
    padding: 14px 18px;
}
.lc-exp-section-head.danger { background: #FEF2F2; }
.lc-exp-section-head.warning { background: #FFFBEB; }
.lc-exp-section-head.success { background: #F0FDF4; }
.lc-exp-section-icon {
    width: 26px; height: 26px; border-radius: 50%; background: #FFFFFF;
    display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.lc-exp-section-title { font-size: 13.5px; font-weight: 800; }
.lc-exp-section-title.danger { color: #B91C1C; }
.lc-exp-section-title.warning { color: #B45309; }
.lc-exp-section-title.success { color: #15803D; }
.lc-exp-table-wrap { padding: 4px 18px 16px; }
.lc-tenant-cell { display: flex; align-items: center; gap: 10px; }
.lc-tenant-avatar {
    width: 26px; height: 26px; border-radius: 8px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 800; color: #FFFFFF;
}

/* "Show more / Show less" toggle — real st.button widget, ghost-styled */
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .lc-exp-show-more-marker) div[data-testid="stButton"] > button {
    background: transparent !important;
    color: #64748B !important;
    border: none !important;
    font-size: 11.5px !important;
    font-weight: 700 !important;
    box-shadow: none !important;
}

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
body:has(.lc-page-marker) div[data-testid="stSelectbox"] [data-testid="stMarkdownContainer"] {
    display: none !important;
}
body:has(.lc-page-marker) div[data-testid="stSelectbox"] > div,
body:has(.lc-page-marker) div[data-testid="stSelectbox"] > div > div {
    border: none !important;
    background-color: transparent !important;
    padding: 0 !important;
    box-shadow: none !important;
}
body:has(.lc-page-marker) div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    border: 1px solid #E2E8F0 !important;
    border-radius: 999px !important;
    background-color: #FFFFFF !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02) !important;
    transition: all 0.2s ease !important;
}
body:has(.lc-page-marker) div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover {
    border-color: #CBD5E1 !important;
}
body:has(.lc-page-marker) div[data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {
    border-color: #6366F1 !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1) !important;
}

/* Minimize control container size */
body:has(.lc-page-marker) div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    min-height: 28px !important;
    height: 28px !important;
    padding: 0 4px 0 10px !important;
    display: flex !important;
    align-items: center !important;
}

/* Override selection text styling inside selectbox */
body:has(.lc-page-marker) div[data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"] {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #1E293B !important;
    line-height: 28px !important;
}

/* Pseudo-elements for prefixes */
body:has(.lc-page-marker) div[data-testid="column"]:nth-of-type(2) div[data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"]::before {
    content: "Terminal ";
    font-weight: 400 !important;
    color: #94A3B8 !important;
}
body:has(.lc-page-marker) div[data-testid="column"]:nth-of-type(3) div[data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"]::before {
    content: "Contract Type ";
    font-weight: 400 !important;
    color: #94A3B8 !important;
}
body:has(.lc-page-marker) div[data-testid="column"]:nth-of-type(4) div[data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"]::before {
    content: "Business Category ";
    font-weight: 400 !important;
    color: #94A3B8 !important;
}
body:has(.lc-page-marker) div[data-testid="column"]:nth-of-type(5) div[data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"]::before {
    content: "Contract Status ";
    font-weight: 400 !important;
    color: #94A3B8 !important;
}

/* Reduce size of Chevron Arrow */
body:has(.lc-page-marker) div[data-testid="stSelectbox"] svg {
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
def _init_state():
    if "lc_df"          not in st.session_state: st.session_state.lc_df          = _get_contract_data()
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
    terminal_options = ["All Terminal", "Terminal 1", "Terminal 2"]
    tahun_options = ["All Year", 2030, 2029, 2028, 2027, 2026, 2025, 2024, 2023]
    bulan_options = ["All Month", "January", "February", "March", "April", "May", "June",
                      "July", "August", "September", "October", "November", "December"]

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
    return dedent("""
    <style>
    /* Tighter gap between header and the Filter Data card than the
       shared 93px spacer used on other pages. */
    body:has(.lc-page-marker) .ov-fixed-header-spacer,
    body:has(.lc-page-marker) div[data-testid="stElementContainer"]:has(.ov-fixed-header-spacer) {
        height: 56px !important;
        min-height: 56px !important;
        max-height: 56px !important;
    }
    /* ── Filter Data card ──────────────────────────────────────────── */
    body:has(.lc-page-marker) div[data-testid="stHorizontalBlock"]:has(.lc-filtercard-marker),
    body:has(.lc-page-marker) div[data-testid="stLayoutWrapper"]:has(.lc-filtercard-marker) {
        margin-top: -16px !important;
    }
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"] {
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -1px rgba(0,0,0,0.015) !important;
        padding: 18px 20px 14px !important;
    }
    body:has(.lc-page-marker) div[data-testid="stHorizontalBlock"]:has(.kpi-card-new) {
        margin-top: -14px !important;
    }
    body:has(.lc-page-marker) div[data-testid="stLayoutWrapper"]:has(.kpi-card-new) {
        margin-top: -14px !important;
    }
    body:has(.lc-page-marker) div[data-testid="stElementContainer"]:has(.lc-vertical-spacer) {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        height: 0px !important;
    }
    body:has(.lc-page-marker) div[data-testid="stElementContainer"]:has(.lc-row1-row2-gap) {
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        height: 10px !important;
    }
    .lc-filtercard-head {
        display: flex; align-items: center; gap: 12px;
    }
    .lc-filtercard-icon {
        width: 34px; height: 34px; border-radius: 10px; flex: 0 0 34px;
        background: #EEF2FF; color: #4338CA;
        display: flex; align-items: center; justify-content: center;
    }
    .lc-filtercard-title {
        margin: 0 !important; color: #0F172A; font-size: 18px !important; font-weight: 700 !important;
        font-family: 'Montserrat', sans-serif !important; line-height: 1 !important;
    }
    .lc-filtercard-badge {
        display: inline-flex; align-items: center; margin-left: 8px;
        padding: 2px 8px; border-radius: 999px; vertical-align: middle;
        background: #F0FDF4; border: 1px solid #BBF7D0;
        font-size: 10.5px !important; font-weight: 700 !important; color: #16A34A;
        white-space: nowrap;
    }
    .lc-filtercard-sub {
        margin: 5px 0 0 !important; color: #64748B; font-size: 11px !important; font-weight: 400 !important;
        line-height: 1 !important;
        font-family: 'Inter', sans-serif !important;
    }
    .lc-filter-label {
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
    .lc-filter-label svg {
        display: block !important;
        flex-shrink: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }
    .lc-filter-label span {
        line-height: 1 !important;
        display: inline-block !important;
    }
    body:has(.lc-page-marker) div[data-testid="stElementContainer"]:has(.lc-filter-label) {
        margin-bottom: -4px !important;
    }
    body:has(.lc-page-marker) div[data-testid="stElementContainer"]:has(.lc-filterrow-marker) {
        margin: 0 !important; padding: 0 !important; height: 0 !important;
    }
    body:has(.lc-page-marker) div[data-testid="stElementContainer"]:has(.lc-filterrow-marker) + div[data-testid="stHorizontalBlock"],
    body:has(.lc-page-marker) div[data-testid="stElementContainer"]:has(.lc-filterrow-marker) + div[data-testid="stLayoutWrapper"] {
        margin-top: -4px !important;
    }
    body:has(.lc-page-marker) div[data-testid="stElementContainer"]:has(.lc-filtercard-footer-marker) {
        margin: 6px 0 -10px !important;
        height: 1px !important;
        border-top: 1px solid #F1F5F9 !important;
    }
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="baseButton-secondary"] {
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
    body:has(.lc-page-marker) div[data-testid="stElementContainer"]:has(.lc-reset-top-marker) + div[data-testid="stElementContainer"] [data-testid="baseButton-secondary"],
    body:has(.lc-page-marker) div[data-testid="stElementContainer"]:has(.lc-reset-top-marker) + div[data-testid="stElementContainer"] [data-testid="stBaseButton-secondary"] {
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
    body:has(.lc-page-marker) div[data-testid="stElementContainer"]:has(.lc-reset-top-marker) + div[data-testid="stElementContainer"] [data-testid="stIconMaterial"] {
        font-family: 'Material Symbols Rounded' !important;
        font-size: 15px !important;
    }
    body:has(.lc-page-marker) [data-testid="baseButton-primary"],
    body:has(.lc-page-marker) [data-testid="stBaseButton-primary"] {
        border-radius: 999px !important;
        font-size: 12.5px !important; font-weight: 700 !important;
        font-family: Inter, sans-serif !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    }
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="baseButton-primary"],
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="stBaseButton-primary"] {
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
    body:has(.lc-page-marker) [data-testid="baseButton-primary"]:hover,
    body:has(.lc-page-marker) [data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.45) !important;
    }
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="baseButton-primary"]:hover,
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="stBaseButton-primary"]:hover {
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    }
    body:has(.lc-page-marker) [data-testid="baseButton-primary"] svg,
    body:has(.lc-page-marker) [data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"] {
        color: #ffffff !important;
        fill: #ffffff !important;
        font-family: 'Material Symbols Rounded' !important;
    }
    body:has(.lc-page-marker) [data-testid="baseButton-primary"] p,
    body:has(.lc-page-marker) [data-testid="stBaseButton-primary"] p {
        color: #ffffff !important;
    }
    /* ── Selectbox Dropdowns in Filter Card ────────────────────────── */
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="stSelectbox"] {
        margin-bottom: 0 !important;
    }
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="stSelectbox"] > div {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="stSelectbox"] > div > div {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        backdrop-filter: none !important;
    }
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] {
        border: 1px solid #E2E8F0 !important;
        border-radius: 999px !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(99, 102, 241, 0.04) !important;
        transition: all 0.2s ease !important;
    }
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"]:hover {
        border-color: #CBD5E1 !important;
    }
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1) !important;
    }
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        min-height: 32px !important;
        height: 32px !important;
        max-height: 32px !important;
        padding: 0 4px 0 12px !important;
        display: flex !important;
        align-items: center !important;
    }
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"] {
        font-size: 11.5px !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }
    body:has(.lc-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.lc-filtercard-marker) [data-testid="stSelectbox"] svg {
        color: #64748B !important;
    }
    </style>
    """)


def render_lease_contract():
    _init_state()
    
    # Apply global filters dynamically on every rerun (auto-apply)
    df_filt = st.session_state.lc_df.copy()
    
    sel_term = st.session_state.get("f_terminal", "All Terminal")
    if sel_term != "All Terminal" and not df_filt.empty:
        term_map = {
            "Terminal 1": "T1",
            "Terminal 2": "T2",
        }
        sel_term_code = term_map.get(sel_term, sel_term)
        df_filt = df_filt[df_filt["Terminal"] == sel_term_code]
        
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

    st.markdown('<div class="lc-row1-row2-gap"></div>', unsafe_allow_html=True)

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
                    <div class="timeline-kpi-top">
                        <div class="timeline-kpi-icon">{_lc_timeline_icon_svg("file-text")}</div>
                        <div class="timeline-kpi-val">{tot_exp_val}</div>
                    </div>
                    <div class="timeline-kpi-lbl">Contracts<span>Expiring</span></div>
                </div>
                <div class="timeline-kpi-card renewed">
                    <div class="timeline-kpi-top">
                        <div class="timeline-kpi-icon">{_lc_timeline_icon_svg("check-circle")}</div>
                        <div class="timeline-kpi-val">{tot_ren_val}</div>
                    </div>
                    <div class="timeline-kpi-lbl">Contracts<span>Renewed</span></div>
                </div>
                <div class="timeline-kpi-card rate">
                    <div class="timeline-kpi-top">
                        <div class="timeline-kpi-icon">{_lc_timeline_icon_svg("clock")}</div>
                        <div class="timeline-kpi-val">{tot_ren_rate}%</div>
                    </div>
                    <div class="timeline-kpi-lbl">Renewal Rate<span>of expiring</span></div>
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
            
            # Calculate dynamic percentages
            d_rs = len(df_all[df_all["Skema"] == "Revenue Sharing"])
            d_rs_mo = len(df_all[df_all["Skema"] == "RS+MO"])
            d_mgrs = len(df_all[df_all["Skema"] == "MGRS"])
            t_dist = d_rs + d_rs_mo + d_mgrs
            
            d_rs_pct = (d_rs / t_dist) * 100 if t_dist > 0 else 0
            d_rs_mo_pct = (d_rs_mo / t_dist) * 100 if t_dist > 0 else 0
            d_mgrs_pct = (d_mgrs / t_dist) * 100 if t_dist > 0 else 0
            
            st.plotly_chart(_build_donut_chart({"RS": d_rs, "RS+MO": d_rs_mo, "MGRS": d_mgrs}, ["#6366F1", "#0EA5E9", "#F59E0B"], size=140), use_container_width=True, config=dict(displayModeBar=False))

            html_dist_stack = f"""
            <div class="dist-stack">
                <div class="dist-card rs">
                    <div class="dist-card-header">
                        <span class="dist-card-title-row"><span class="dist-card-dot"></span>RS</span>
                        <span class="dist-card-pct">{f"{d_rs_pct:.1f}%".replace(".", ",")}</span>
                    </div>
                    <div class="dist-card-body">
                        <span class="dist-card-count">{d_rs}</span>
                        <span class="dist-card-val">Rp {f"{d_rs*0.74:.1f}".replace(".", ",")} M</span>
                    </div>
                </div>
                <div class="dist-card rs_mo">
                    <div class="dist-card-header">
                        <span class="dist-card-title-row"><span class="dist-card-dot"></span>RS+MO</span>
                        <span class="dist-card-pct">{f"{d_rs_mo_pct:.1f}%".replace(".", ",")}</span>
                    </div>
                    <div class="dist-card-body">
                        <span class="dist-card-count">{d_rs_mo}</span>
                        <span class="dist-card-val">Rp {f"{d_rs_mo*0.74:.1f}".replace(".", ",")} M</span>
                    </div>
                </div>
                <div class="dist-card mgrs">
                    <div class="dist-card-header">
                        <span class="dist-card-title-row"><span class="dist-card-dot"></span>MGRS</span>
                        <span class="dist-card-pct">{f"{d_mgrs_pct:.1f}%".replace(".", ",")}</span>
                    </div>
                    <div class="dist-card-body">
                        <span class="dist-card-count">{d_mgrs}</span>
                        <span class="dist-card-val">Rp {f"{d_mgrs*0.72:.1f}".replace(".", ",")} M</span>
                    </div>
                </div>
            </div>
            """
            st.markdown(html_dist_stack, unsafe_allow_html=True)

            total_est_revenue = d_rs * 0.74 + d_rs_mo * 0.74 + d_mgrs * 0.72
            html_dist_footer = f"""
            <div class="dist-total-footer">
                <span class="dist-total-icon">{_lc_timeline_icon_svg("file-text")}</span>
                <span class="dist-total-label">Total Estimated Revenue</span>
                <span class="dist-total-val">Rp {f"{total_est_revenue:.2f}".replace(".", ",")} M</span>
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
                health_cls, health_label, health_color = "good", "Good", "#10B981"
            elif p_active >= 60:
                health_cls, health_label, health_color = "fair", "Fair", "#F59E0B"
            else:
                health_cls, health_label, health_color = "risk", "At Risk", "#EF4444"

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
                f'<th>End Date</th><th>Remaining</th><th>Value</th><th>Status</th></tr></thead>'
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
        val_m = f"Rp {2.0 + (r['No'] % 10) * 0.9:.1f}M".replace(".", ",")
        dynamic_critical.append({
            "tenant": r["Name/Tenant"], "terminal": r["Terminal"], "type": r["Skema"],
            "end_date": end_date, "remaining": f"{r['Sisa']}d", "value": val_m, "status": "Critical"
        })

    # Build dynamic list of expiring soon contracts
    dynamic_expiring = []
    exp_df = df_all[(df_all["Status"] == "Anomaly") & (df_all["Sisa"] > 30) & (df_all["Sisa"] <= 90)]
    for _, r in exp_df.iterrows():
        end_date = r["Valid Period"].split(" - ")[1] if " - " in r["Valid Period"] else "01 Mar 2025"
        val_m = f"Rp {4.0 + (r['No'] % 10) * 1.2:.1f}M".replace(".", ",")
        dynamic_expiring.append({
            "tenant": r["Name/Tenant"], "terminal": r["Terminal"], "type": r["Skema"],
            "end_date": end_date, "remaining": f"{r['Sisa']}d", "value": val_m, "status": "Expiring Soon"
        })

    # Build dynamic list of approaching renewal contracts (no cap here —
    # the "Show more" toggle controls how many rows are visible)
    dynamic_approaching = []
    app_df = df_all[(df_all["Status"] == "Valid") & (df_all["Sisa"] > 90)].sort_values(by="Sisa")
    for _, r in app_df.iterrows():
        end_date = r["Valid Period"].split(" - ")[1] if " - " in r["Valid Period"] else "02 May 2025"
        val_m = f"Rp {2.0 + (r['No'] % 5) * 1.5:.1f}M".replace(".", ",")
        dynamic_approaching.append({
            "tenant": r["Name/Tenant"], "terminal": r["Terminal"], "type": r["Skema"],
            "end_date": end_date, "remaining": f"{r['Sisa']}d", "value": val_m, "status": "Approaching"
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
