"""CSS constants for the Lease Contract page, relocated out of
lease_contract.py to keep that file focused on logic. Content is unchanged
from before — this is a pure code-organization split, not a styling change."""

from textwrap import dedent

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
    min-width: 64px;
    white-space: nowrap;
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


_LC_EXTRA_CSS = dedent("""
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
