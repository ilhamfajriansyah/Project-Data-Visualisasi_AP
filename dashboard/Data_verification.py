import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
from datetime import date, datetime
from textwrap import dedent

from .shared_import import get_shared_import_data, get_shared_import_meta
from .navigation import topnav_actions_html
from .pagination import render_pagination, patch_pagination


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
# DATA PROCESSING
# ─────────────────────────────────────────────
def _empty_verification_data() -> pd.DataFrame:
    return pd.DataFrame(columns=[
        "Kode Ruang",
        "Brand/Tenant",
        "Perusahaan",
        "SAP ID",
        "Legal ID",
        "Real Onset",
        "End Kontrak",
        "Status",
        "Skema",
        "Conflict Info",
        "Anomali",
        "Conflict",
        "_tahun",
    ])


def _filter_active_import_rows(df: pd.DataFrame | None) -> pd.DataFrame | None:
    if df is None or df.empty or "import_id" not in df.columns:
        return df

    try:
        from .connection import get_engine
        from sqlalchemy import text

        with get_engine().connect() as conn:
            active_ids = pd.read_sql(
                text("""
                    SELECT import_id
                    FROM import_history
                    WHERE COALESCE(is_active, true) = true
                """),
                conn,
            )
    except Exception:
        return df.iloc[0:0]

    if active_ids.empty:
        return df.iloc[0:0]

    allowed = set(pd.to_numeric(active_ids["import_id"], errors="coerce").dropna().astype(int))
    row_ids = pd.to_numeric(df["import_id"], errors="coerce")
    return df[row_ids.isin(allowed)].copy()


def _get_verification_data(df_raw: pd.DataFrame | None = None) -> pd.DataFrame:
    """
    DATA SOURCE:
    Uses real dashboard data from PostgreSQL first, then an uploaded file that
    still lives in Import Manager session state. If both are empty, return an
    empty shaped dataframe so the page keeps its design with all counters at 0.
    """
    db_df = _filter_active_import_rows(df_raw)
    imported_df = db_df if (db_df is not None and not db_df.empty) else get_shared_import_data()
    if imported_df is None or imported_df.empty:
        return _empty_verification_data()

    meta = get_shared_import_meta()
    df = imported_df.copy()
    rows = []
    for _, r in df.iterrows():
        real_omzet = r.get("real_omzet", r.get("omzet", 0))
        brand = r.get("brand", r.get("perusahaan", r.get("tenant_name", "-")))
        perusahaan = r.get("perusahaan", "-")
        kode_ruang = r.get("kode_ruang", r.get("unit", "-"))
        periode = r.get("masa_jasa", r.get("periode", meta.get("period", "-")))
        tahun = r.get("tahun", "-")
        try:
            omzet_value = float(real_omzet or 0)
        except (TypeError, ValueError):
            omzet_value = 0
        status = "Active" if pd.notna(real_omzet) and omzet_value > 0 else "Pending"
        rows.append({
            "Kode Ruang": kode_ruang if pd.notna(kode_ruang) else "-",
            "Brand/Tenant": brand if pd.notna(brand) else "-",
            "Perusahaan": perusahaan if pd.notna(perusahaan) else "-",
            "SAP ID": str(r.get("sap_id", "SAP: -")),
            "Legal ID": str(r.get("legal_id", "Legal: -")),
            "Real Onset": str(periode),
            "End Kontrak": str(r.get("end_kontrak", "-")),
            "Status": status,
            "Skema": str(r.get("skema", r.get("bidang_usaha", "-"))),
            "Anomali": bool(pd.isna(real_omzet) or pd.isna(kode_ruang) or pd.isna(brand)),
            "_tahun": str(tahun) if pd.notna(tahun) else "-",
        })
    result = pd.DataFrame(rows)

    # Conflict = data bentrok/duplikat: dua baris atau lebih mengklaim Kode
    # Ruang yang sama di Tahun + Periode (masa_jasa) yang sama. Kode Ruang
    # placeholder "-" (tidak diketahui) dikecualikan supaya tidak terhitung
    # bentrok satu sama lain.
    dup_key = result[["Kode Ruang", "_tahun", "Real Onset"]]
    has_known_kode = result["Kode Ruang"] != "-"
    result["Conflict"] = has_known_kode & dup_key.duplicated(keep=False)

    def _conflict_info(row):
        if not row["Conflict"]:
            return "-"
        same_slot = result[
            (result["Kode Ruang"] == row["Kode Ruang"])
            & (result["_tahun"] == row["_tahun"])
            & (result["Real Onset"] == row["Real Onset"])
            & (result.index != row.name)
        ]
        other_tenants = sorted(set(same_slot["Brand/Tenant"].tolist()) - {row["Brand/Tenant"]})
        if other_tenants:
            return "Bentrok dengan " + ", ".join(other_tenants)
        return f"Bentrok ({len(same_slot) + 1} entri kode ruang sama)"

    result["Conflict Info"] = result.apply(_conflict_info, axis=1)

    return result

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
    margin-top: -15px !important;
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
    gap: 0px !important;
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
    font-family: 'Montserrat', sans-serif !important;
}

body:has(.dv-page-marker) .ed-section-sub {
    margin: 3px 0 0 !important;
    color: #64748B !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    font-family: 'Inter', sans-serif !important;
}

body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(.ed-card-marker),
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(.ed-card-marker) * {
    font-family: 'Inter', sans-serif !important;
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
    overflow: visible !important;
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
    color: #0F172A; font-family: 'Montserrat', sans-serif !important;
}

body:has(.dv-page-marker) p.dv-page-sub {
    margin: 0 !important; padding: 0 !important;
    color: #64748B; font-size: 12px; line-height: 1 !important;
    font-weight: 500; font-family: 'Inter', sans-serif !important;
}

body:has(.dv-page-marker) .ap-top-actions {
    flex-shrink: 0;
}

/* ── KPI Row Spacing & Gap ── */
body:has(.dv-page-marker) div[data-testid="stHorizontalBlock"]:has(.dv-kpi-card) {
    margin-top: -123px !important;
    gap: 24px !important;
    flex-wrap: nowrap !important;
}
body:has(.dv-page-marker) div[data-testid="stHorizontalBlock"]:has(.dv-kpi-card) > div[data-testid="column"] {
    width: calc(25% - 18px) !important;
    min-width: calc(25% - 18px) !important;
    flex: 1 1 calc(25% - 18px) !important;
}

/* ── KPI CARDS ── */
.dv-kpi-card {
    background: #ffffff !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    padding: 20px 24px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    box-shadow: 0 4px 16px rgba(15, 23, 42, 0.03) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
    min-height: 106px !important;
    box-sizing: border-box !important;
}
.dv-kpi-card:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 30px rgba(15, 23, 42, 0.08) !important;
}
.dv-kpi-content {
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    gap: 6px !important;
}
.dv-kpi-label {
    font-size: 11px !important;
    font-weight: 600 !important;
    color: #64748B !important;
    text-transform: uppercase !important;
    letter-spacing: 0.8px !important;
    margin: 0 !important;
    padding: 0 !important;
}
.dv-kpi-value {
    font-size: 28px !important;
    font-weight: 800 !important;
    color: #0F172A !important;
    line-height: 1.1 !important;
    margin: 0 !important;
    padding: 0 !important;
}
.dv-kpi-trend {
    font-size: 11px !important;
    font-weight: 500 !important;
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    gap: 4px !important;
}
.dv-kpi-icon-container {
    width: 48px !important;
    height: 48px !important;
    border-radius: 12px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-shrink: 0 !important;
    transition: all 0.25s ease !important;
}

/* Card-specific accents */
.kpi-total { border-left: 4px solid #2563EB !important; }
.kpi-total .dv-kpi-icon-container { background: rgba(37, 99, 235, 0.08) !important; color: #2563EB !important; }
.trend-total { color: #2563EB !important; }

.kpi-valid { border-left: 4px solid #10B981 !important; }
.kpi-valid .dv-kpi-icon-container { background: rgba(16, 185, 129, 0.08) !important; color: #10B981 !important; }
.trend-valid { color: #059669 !important; }

.kpi-anomalies { border-left: 4px solid #F59E0B !important; }
.kpi-anomalies .dv-kpi-icon-container { background: rgba(245, 158, 11, 0.08) !important; color: #F59E0B !important; }
.trend-anomalies { color: #D97706 !important; }

.kpi-conflicts { border-left: 4px solid #EF4444 !important; }
.kpi-conflicts .dv-kpi-icon-container { background: rgba(239, 68, 68, 0.08) !important; color: #EF4444 !important; }
.trend-conflicts { color: #DC2626 !important; }

/* ── TABLE ── */
.dv-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
}
.dv-table thead tr {
    background: rgba(99, 102, 241, 0.05) !important;
}
.dv-table th {
    padding: 11px 20px !important;
    text-align: left;
    font-size: 11px;
    font-weight: 700;
    color: #4F46E5 !important;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
    border-bottom: none;
}
.dv-table td {
    padding: 10px 20px !important;
    font-size: 13px;
    color: #334155;
    border-bottom: 1px solid #E2E8F0;
    vertical-align: middle;
    transition: all 0.2s;
}
.dv-table tbody tr {
    transition: background-color 0.2s ease;
}
.dv-table tbody tr:nth-child(even) {
    background-color: #FAFAFB;
}
.dv-table tbody tr:nth-child(odd) {
    background-color: #FFFFFF;
}
.dv-table tbody tr:hover {
    background-color: rgba(37, 99, 235, 0.03) !important;
}
.dv-table tbody tr.anomali-row {
    background-color: rgba(245, 158, 11, 0.02);
}
.dv-table tbody tr.anomali-row:hover {
    background-color: rgba(245, 158, 11, 0.05) !important;
}
.dv-table tbody tr.conflict-row {
    background-color: rgba(239, 68, 68, 0.03);
}
.dv-table tbody tr.conflict-row:hover {
    background-color: rgba(239, 68, 68, 0.06) !important;
}
.dv-table tbody tr:last-child td {
    border-bottom: none;
}

.dv-kode {
    font-weight: 700;
    color: #0F172A;
    font-size: 13px;
}
.dv-brand {
    font-weight: 600;
    color: #0F172A;
    font-size: 13.5px;
}
.dv-sap {
    font-size: 11px;
    color: #64748B;
    margin-top: 3px;
}
.dv-onset {
    font-size: 12.5px;
    color: #475569;
}

/* ── STATUS BADGES ── */
.b-active {
    background: #ECFDF5 !important;
    color: #047857 !important;
    border: 1px solid #A7F3D0 !important;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 11.5px;
    font-weight: 600;
    white-space: nowrap;
    display: inline-block;
}
.b-expiredsoon {
    background: #FFFBEB !important;
    color: #B45309 !important;
    border: 1px solid #FDE68A !important;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 11.5px;
    font-weight: 600;
    white-space: nowrap;
    display: inline-block;
}
.b-expired {
    background: #FEF2F2 !important;
    color: #B91C1C !important;
    border: 1px solid #FCA5A5 !important;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 11.5px;
    font-weight: 600;
    white-space: nowrap;
    display: inline-block;
}

.dv-skema {
    font-size: 12px;
    font-weight: 600;
    color: #4F46E5;
}
.dv-conflict {
    font-size: 14px;
    font-weight: 700;
    color: #0F172A;
    font-family: 'Poppins', sans-serif !important;
}

/* ── BRAND ICONS ── */
.brand-logo-wrapper {
    width: 38px;
    height: 38px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.brand-coffee {
    background: rgba(16, 185, 129, 0.08) !important;
    color: #10B981 !important;
}
.brand-food {
    background: rgba(245, 158, 11, 0.08) !important;
    color: #F59E0B !important;
}
.brand-store {
    background: rgba(37, 99, 235, 0.08) !important;
    color: #2563EB !important;
}
.brand-default {
    background: rgba(99, 102, 241, 0.08) !important;
    color: #6366F1 !important;
}

/* ── ACTION BUTTONS ── */
.dv-action-btns {
    display: flex;
    gap: 8px;
    justify-content: flex-end;
}
.dv-btn-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    border: 1px solid #E2E8F0;
    background: #FFFFFF;
    color: #64748B;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s ease;
}
.dv-btn-icon:hover {
    background: #F8FAFC;
    color: #0F172A;
    border-color: #CBD5E1;
}
.dv-btn-edit:hover {
    color: #2563EB;
    border-color: rgba(37, 99, 235, 0.2);
    background: rgba(37, 99, 235, 0.04);
}
.dv-btn-detail:hover {
    color: #10B981;
    border-color: rgba(16, 185, 129, 0.2);
    background: rgba(16, 185, 129, 0.04);
}

/* ── ANOMALI DOT ── */
.anomali-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #f59e0b;
    display: inline-block; margin-right: 6px;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.15);
}

/* ── CONFLICT DOT ── */
.conflict-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #ef4444;
    display: inline-block; margin-right: 6px;
    box-shadow: 0 0 0 3px rgba(239,68,68,0.15);
}

/* ── FOOTER & PAGINATION ── */
.dv-footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px 24px !important;
    border-top: 1px solid #E2E8F0;
    background: #FFFFFF;
}
.dv-footer-info {
    font-size: 12.5px !important;
    color: #64748B !important;
    font-weight: 500 !important;
}

/* ── FILTER BAR STYLES ── */
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) div[data-testid="stHorizontalBlock"] {
    background: transparent !important;
    margin-top: 16px !important;
    margin-bottom: 5px !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) div[data-testid="stHorizontalBlock"] div[data-testid="stTextInput"] {
    overflow: visible !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) div[data-testid="stHorizontalBlock"] div[data-testid="stTextInputRootElement"] {
    border-radius: 9999px !important;
    border: 1px solid #E2E8F0 !important;
    background: #FFFFFF !important;
    height: 42px !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03) !important;
    box-sizing: border-box !important;
    overflow: visible !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) div[data-testid="stHorizontalBlock"] div[data-testid="stTextInputRootElement"]:focus-within {
    border-color: #2563EB !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) div[data-testid="stHorizontalBlock"] div[data-testid="stTextInput"] input,
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) div[data-testid="stHorizontalBlock"] div[data-testid="stTextInput"] input:focus {
    border: none !important;
    background: transparent !important;
    padding-left: 18px !important;
    font-size: 13.5px !important;
    height: 100% !important;
    outline: none !important;
    box-shadow: none !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"] > div {
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"] > div > div {
    border-radius: 9999px !important;
    border: 1px solid #E2E8F0 !important;
    background: #FFFFFF !important;
    height: 42px !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03) !important;
}
body:has(.dv-page-marker) div[data-testid="column"]:nth-of-type(4) div[data-testid="stSelectbox"] {
    width: 90px !important;
    max-width: 90px !important;
    margin-left: auto !important;
}
body:has(.dv-page-marker) div[data-testid="column"]:nth-of-type(4) div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    padding-left: 10px !important;
    padding-right: 28px !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button {
    border-radius: 9999px !important;
    background: #FFFFFF !important;
    color: #475569 !important;
    border: 1px solid #E2E8F0 !important;
    box-shadow: 0 2px 6px rgba(15, 23, 42, 0.03) !important;
    height: 42px !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
    width: 100% !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button [data-testid="stIconMaterial"] {
    font-family: 'Material Symbols Rounded' !important;
}
body:has(.dv-page-marker) div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) div[data-testid="stHorizontalBlock"] div[data-testid="stButton"] button:hover {
    background: #F8FAFC !important;
    color: #0F172A !important;
    border-color: #CBD5E1 !important;
    transform: none !important;
}

/* ── PAGINATION STYLING ── */
.dv-pagination-btns {
    display: flex;
    align-items: center;
    gap: 8px;
}
.dv-pg-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border-radius: 8px;
    border: 1px solid #cbd5e1;
    background: #FFFFFF;
    color: #475569;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    box-sizing: border-box;
    outline: none;
    user-select: none;
    height: 36px;
    padding: 0 12px;
    min-width: 36px;
    transition:
      background-color 0.18s ease,
      color 0.18s ease,
      border-color 0.18s ease,
      transform 0.12s ease;
}
.dv-pg-btn:hover:not(.active):not(.disabled) {
    background-color: #EFF6FF !important;
    color: #2563EB !important;
    border-color: #EFF6FF !important;
}
.dv-pg-btn.active {
    background-color: #2563EB !important;
    color: #FFFFFF !important;
    border-color: #2563EB !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
}
.dv-pg-btn.disabled {
    color: #9CA3AF !important;
    border-color: #cbd5e1 !important;
    background-color: #F8FAFC !important;
    cursor: not-allowed !important;
    opacity: 0.4 !important;
}
.dv-pg-btn:active:not(.disabled) {
    transform: scale(0.94) !important;
}
</style>
"""


# ─────────────────────────────────────────────
# INIT STATE
# ─────────────────────────────────────────────
def _init_state(df_raw: pd.DataFrame | None = None):
    if "dv_page" not in st.session_state: st.session_state.dv_page = 1
    current_data = _get_verification_data(df_raw)
    current_import_id = (
        int(pd.to_numeric(df_raw["import_id"], errors="coerce").max())
        if df_raw is not None and "import_id" in df_raw.columns and not df_raw.empty
        else None
    )
    if (
        "dv_df" not in st.session_state
        or st.session_state.get("dv_source_import_id") != current_import_id
        or (current_import_id is None and current_data.empty)
    ):
        st.session_state.dv_df = current_data
        st.session_state.dv_source_import_id = current_import_id


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def _status_badge(s):
    if s == "Active":
        return '<span class="b-active">Active</span>'
    if s in ["Expired Soon", "Expiring Soon"]:
        return '<span class="b-expiredsoon">Expiring Soon</span>'
    if s == "Expired":
        return '<span class="b-expired">Expired</span>'
    return f'<span>{s}</span>'


def _get_brand_icon(brand_name: str) -> str:
    brand_lower = brand_name.lower()

    # SVG definition for coffee cup (Starbucks, Cafe)
    coffee_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M18 8h1a4 4 0 0 1 0 8h-1"></path>'
        '<path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path>'
        '<line x1="6" y1="1" x2="6" y2="4"></line>'
        '<line x1="10" y1="1" x2="10" y2="4"></line>'
        '<line x1="14" y1="1" x2="14" y2="4"></line>'
        '</svg>'
    )

    # SVG definition for food/burger (Burger King, Rod Boy, KFC, Wingman, Pizza, Bakso, Solaria)
    food_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 21a9 9 0 0 0 9-9c0-1.66-2-3-4.35-3h-9.3C5 9 3 10.34 3 12a9 9 0 0 0 9 9z"></path>'
        '<path d="M3 12h18"></path>'
        '<path d="M12 3a9 9 0 0 0-9 6h18a9 9 0 0 0-9-6z"></path>'
        '</svg>'
    )

    # SVG definition for shopping bag (Gramedia, Hypermart, Indomaret, Alfamart)
    store_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z"></path>'
        '<line x1="3" y1="6" x2="21" y2="6"></line>'
        '<path d="M16 10a4 4 0 0 1-8 0"></path>'
        '</svg>'
    )

    # SVG definition for general business/store
    default_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect>'
        '<path d="M17 21v-2a4 4 0 0 0-4-4h-2a4 4 0 0 0-4 4v2"></path>'
        '<path d="M16 3H8a2 2 0 0 0-2 2v2h12V5a2 2 0 0 0-2-2z"></path>'
        '</svg>'
    )

    if "starbucks" in brand_lower or "cafe" in brand_lower or "coffee" in brand_lower:
        return f'<div class="brand-logo-wrapper brand-coffee">{coffee_svg}</div>'
    elif any(x in brand_lower for x in ["burger", "king", "rod boy", "kfc", "bistro", "pizza", "bakso", "solaria", "wingman"]):
        return f'<div class="brand-logo-wrapper brand-food">{food_svg}</div>'
    elif any(x in brand_lower for x in ["store", "indomaret", "alfamart", "hypermart", "gramedia", "timezone", "outlet"]):
        return f'<div class="brand-logo-wrapper brand-store">{store_svg}</div>'
    else:
        return f'<div class="brand-logo-wrapper brand-default">{default_svg}</div>'


# ─────────────────────────────────────────────
# TABLE RENDERER
# ─────────────────────────────────────────────
def _render_table(df: pd.DataFrame, page: int, page_size: int = 5):
    total   = len(df)
    n_pages = max(1, -(-total // page_size))
    page    = max(1, min(page, n_pages))
    start   = (page - 1) * page_size
    end     = min(start + page_size, total)
    rows    = df.iloc[start:end]

    rows_html = ""
    for _, r in rows.iterrows():
        anomali_class = "anomali-row" if r["Anomali"] else ""
        anomali_dot   = '<span class="anomali-dot"></span>' if r["Anomali"] else ""
        conflict_class = "conflict-row" if r["Conflict"] else ""
        conflict_dot   = '<span class="conflict-dot" title="Kode Ruang bentrok/duplikat pada periode yang sama"></span>' if r["Conflict"] else ""

        # Get custom brand icon
        brand_icon_html = _get_brand_icon(r['Brand/Tenant'])

        # Action column buttons
        action_html = """
        <div class="dv-action-btns">
          <button class="dv-btn-icon dv-btn-edit" title="Edit Record">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
              <path d="M18.5 2.5a2.121 2.121 0 1 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
            </svg>
          </button>
          <button class="dv-btn-icon dv-btn-detail" title="View Details">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
              <circle cx="12" cy="12" r="3"></circle>
            </svg>
          </button>
        </div>
        """

        rows_html += f"""
        <tr class="{anomali_class} {conflict_class}">
          <td>
            <div class="dv-kode">{conflict_dot}{r['Kode Ruang']}</div>
          </td>
          <td>
            <div style="display: flex; align-items: center; gap: 12px;">
              {brand_icon_html}
              <div>
                <div class="dv-brand">{anomali_dot}{r['Brand/Tenant']}</div>
                <div class="dv-sap">{r['SAP ID']} · {r['Legal ID']}</div>
              </div>
            </div>
          </td>
          <td class="dv-onset">{r['Real Onset']}</td>
          <td>{_status_badge(r['Status'])}</td>
          <td class="dv-skema">{r['Skema']}</td>
          <td class="dv-conflict">{r['Conflict Info']}</td>
          <td>{action_html}</td>
        </tr>"""

    if not rows_html:
        rows_html = '<tr><td colspan="7" style="text-align:center;color:#94a3b8;padding:30px;">Tidak ada data yang cocok dengan filter.</td></tr>'

    html = f"""
    <div style="overflow-x:auto; margin-top: 0px !important; border: 1px solid rgba(99,102,241,0.08); border-radius: 12px; overflow: hidden;">
      <table class="dv-table">
        <thead>
          <tr>
            <th>Kode Ruang</th>
            <th>Brand / Tenant</th>
            <th>Real Onset</th>
            <th>Status</th>
            <th>Skema</th>
            <th>Conflict Info</th>
            <th style="text-align: right; padding-right: 24px;">Action</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>"""

    st.markdown(html, unsafe_allow_html=True)
    return page, n_pages


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def render_data_verification(df_raw: pd.DataFrame | None = None):
    """Call this from dashboard.py router."""
    _init_state(df_raw)
    st.markdown('<div class="dv-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="dv-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_dv_page_header_html(), unsafe_allow_html=True)
        st.markdown('<div class="dv-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="dv-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)

    # ── Action Buttons ──
    st.markdown('<div class="dv-actions-marker"></div>', unsafe_allow_html=True)
    _, ab2 = st.columns([7.6, 1.8])
    with ab2:
        if st.button("✅ Approve & Publish", use_container_width=True, key="dv_approve"):
            st.toast("✅ Data berhasil dipublikasikan!", icon="✅")

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── KPI Cards Row Marker ──
    st.markdown('<div class="dv-kpi-row-marker"></div>', unsafe_allow_html=True)

    # ── 4 KPI Cards ──
    df_all = st.session_state.dv_df
    total_records = len(df_all)
    valid_records = int((df_all["Status"] == "Active").sum())
    anomalies     = int(df_all["Anomali"].sum())
    conflicts     = int(df_all["Conflict"].sum())

    # Define clean, professional SVG icons
    total_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>'
        '<polyline points="14 2 14 8 20 8"></polyline>'
        '<line x1="16" y1="13" x2="8" y2="13"></line>'
        '<line x1="16" y1="17" x2="8" y2="17"></line>'
        '<polyline points="10 9 9 9 8 9"></polyline>'
        '</svg>'
    )

    valid_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>'
        '<polyline points="9 11 11 13 15 9"></polyline>'
        '</svg>'
    )

    anom_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>'
        '<line x1="12" y1="9" x2="12" y2="13"></line>'
        '<line x1="12" y1="17" x2="12.01" y2="17"></line>'
        '</svg>'
    )

    conflict_svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">'
        '<circle cx="12" cy="12" r="10"></circle>'
        '<line x1="12" y1="8" x2="12" y2="12"></line>'
        '<line x1="12" y1="16" x2="12.01" y2="16"></line>'
        '</svg>'
    )

    k1, k2, k3, k4 = st.columns(4)

    valid_pct = (valid_records / total_records * 100) if total_records > 0 else 0
    anom_pct = (anomalies / total_records * 100) if total_records > 0 else 0
    conflict_pct = (conflicts / total_records * 100) if total_records > 0 else 0

    kpi_cfg = [
        (k1, total_svg, "total", "Total Records", total_records, "Updated just now"),
        (k2, valid_svg, "valid", "Valid Records", valid_records, f"{valid_pct:.1f}% accuracy rate"),
        (k3, anom_svg, "anomalies", "Anomalies", anomalies, f"{anom_pct:.1f}% anomaly rate"),
        (k4, conflict_svg, "conflicts", "Conflicts", conflicts, f"{conflict_pct:.1f}% conflict rate"),
    ]
    for col, icon_svg, kpi_type, label, value, trend in kpi_cfg:
        with col:
            val_formatted = f"{value:,}".replace(",", ".")
            st.markdown(f"""
            <div class="dv-kpi-card kpi-{kpi_type}">
                <div class="dv-kpi-content">
                    <div class="dv-kpi-label">{label}</div>
                    <div class="dv-kpi-value">{val_formatted}</div>
                    <div class="dv-kpi-trend trend-{kpi_type}">{trend}</div>
                </div>
                <div class="dv-kpi-icon-container">
                    {icon_svg}
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # ── Main Content Section Header & Table Container ──
    main_section = st.container()
    with main_section:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)

        # ── Header & Filter Controls ──
        st.markdown(
            '<div style="margin-bottom: 8px;">'
            '<p class="ed-section-title">Verification Records</p>'
            '<p class="ed-section-sub">Daftar lengkap status validasi dan anomali data tenant</p>'
            '</div>',
            unsafe_allow_html=True,
        )

        f_col1, f_col2, f_col3, f_col_page, f_col4 = st.columns([3.8, 2.2, 2.2, 0.8, 1.0], vertical_alignment="bottom")
        with f_col1:
            search_q = st.text_input(
                "Search Brand / Tenant",
                placeholder="Search brand, tenant or unit code...",
                label_visibility="collapsed",
                key="dv_search"
            )
        with f_col2:
            status_f = st.selectbox(
                "Status",
                ["All Status", "Active", "Expired Soon", "Expired"],
                label_visibility="collapsed",
                key="dv_fstatus"
            )
        with f_col3:
            anom_f = st.selectbox(
                "Anomalies Type",
                ["All Anomalies", "Dengan Anomali", "Tanpa Anomali"],
                label_visibility="collapsed",
                key="dv_fanom"
            )
        with f_col_page:
            st.selectbox(
                "Rows per page",
                [10, 25, 50],
                key="dv_rows_per_page",
                label_visibility="collapsed",
            )
        # Define callback to reset filter values safely before next render run
        def handle_reset():
            st.session_state.dv_search = ""
            st.session_state.dv_fstatus = "All Status"
            st.session_state.dv_fanom = "All Anomalies"
            st.session_state.dv_page = 1

        with f_col4:
            st.button(
                "Reset", key="dv_reset_btn", use_container_width=True,
                icon=":material/sync:", on_click=handle_reset,
            )

        # ── Apply Filters ──
        df = st.session_state.dv_df.copy()

        # Search Filter
        if search_q:
            df = df[
                df["Brand/Tenant"].str.contains(search_q, case=False, na=False) |
                df["Kode Ruang"].str.contains(search_q, case=False, na=False)
            ]

        # Status Filter
        if status_f not in ["All Status", "Status ▾", ""]:
            # Handle user display "Expired Soon" mapping to data status
            df = df[df["Status"] == status_f]

        # Anomalies Filter
        if anom_f == "Dengan Anomali":
            df = df[df["Anomali"] == True]
        elif anom_f == "Tanpa Anomali":
            df = df[df["Anomali"] == False]

        df = df.reset_index(drop=True)

        # Reset page on filter change
        dv_rows = st.session_state.get("dv_rows_per_page", 10)
        fkey = f"{search_q}|{status_f}|{anom_f}|{dv_rows}"
        if st.session_state.get("_dv_last_filter") != fkey:
            st.session_state.dv_page = 1
            st.session_state["_dv_last_filter"] = fkey

        # ── Table ──
        page, n_pages = _render_table(df, st.session_state.dv_page, page_size=dv_rows)
        first_item = 0 if len(df) == 0 else ((page - 1) * dv_rows) + 1
        last_item = min(page * dv_rows, len(df))

    # ── Pagination di LUAR with main_section agar CSS DV tidak override ──
    st.markdown('<div class="overview-detail-pagination-footer-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    dv_page_input = render_pagination(
        current_page=st.session_state.dv_page,
        total_pages=n_pages,
        first_item=first_item,
        last_item=last_item,
        total_rows=len(df),
        sync_key="dv_page_sync",
    )
    if dv_page_input and dv_page_input.isdigit():
        new_page = int(dv_page_input)
        if new_page != st.session_state.dv_page:
            st.session_state.dv_page = new_page
            st.rerun()
    patch_pagination()

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
