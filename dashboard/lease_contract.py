import streamlit as st
import pandas as pd
from datetime import date

# ─────────────────────────────────────────────
# DUMMY DATA
# ─────────────────────────────────────────────
def _get_contract_data() -> pd.DataFrame:
    data = [
        {"No": 1,  "Name/Tenant": "NAST Merch",   "Sub": "august on lesant.com",    "Valid Period": "31 Mar 2023 - 15 Sep 2023", "Unit Name/Loc": "Unit Name/Loc. 1",  "Status": "Valid",   "Conflict Info": True,  "Kode": "FB-01-01", "Skema": "Rental",          "Sisa": 120},
        {"No": 2,  "Name/Tenant": "NAST Dyonh",   "Sub": "tengat - 07-2023-2023",   "Valid Period": "06 Jan 2023 - 10 Jan 2024", "Unit Name/Loc": "Unit Name/Loc. 2",  "Status": "Anomaly", "Conflict Info": True,  "Kode": "RT-02-07", "Skema": "Revenue Sharing", "Sisa": 25},
        {"No": 3,  "Name/Tenant": "NAST 7508A",   "Sub": "tengat - 17-2023-2053",   "Valid Period": "15 Jan 2023 - 27 Dec 2023", "Unit Name/Loc": "Unit Name/Loc. 3",  "Status": "Valid",   "Conflict Info": True,  "Kode": "LG-01-12", "Skema": "MGRS",            "Sisa": 580},
        {"No": 4,  "Name/Tenant": "NAST Dyonh",   "Sub": "tengat - 17-2023-2024",   "Valid Period": "23 Sep 2023 - 25 Sep 2023", "Unit Name/Loc": "Unit Name/Loc. 4",  "Status": "Valid",   "Conflict Info": True,  "Kode": "FB-01-03", "Skema": "Rental",          "Sisa": 4},
        {"No": 5,  "Name/Tenant": "NAST Pertamina","Sub": "tengat - 05-2022-2024",   "Valid Period": "01 May 2022 - 31 Dec 2024", "Unit Name/Loc": "Unit Name/Loc. 5",  "Status": "Expired", "Conflict Info": False, "Kode": "SV-02-05", "Skema": "Revenue Sharing", "Sisa": -150},
        {"No": 6,  "Name/Tenant": "NAST Bogajaya", "Sub": "tengat - 06-2023-2026",  "Valid Period": "01 Jun 2023 - 31 May 2026", "Unit Name/Loc": "Unit Name/Loc. 6",  "Status": "Valid",   "Conflict Info": False, "Kode": "RT-03-08", "Skema": "Rental",          "Sisa": 366},
        {"No": 7,  "Name/Tenant": "GAUSD VIP",     "Sub": "tengat - 01-2024-2026",  "Valid Period": "01 Jan 2024 - 31 Dec 2026", "Unit Name/Loc": "Unit Name/Loc. 7",  "Status": "Valid",   "Conflict Info": True,  "Kode": "LG-02-01", "Skema": "MGRS",            "Sisa": 580},
        {"No": 8,  "Name/Tenant": "GMFA Services", "Sub": "tengat - 03-2024-2025",  "Valid Period": "01 Mar 2024 - 28 Aug 2025", "Unit Name/Loc": "Unit Name/Loc. 8",  "Status": "Anomaly", "Conflict Info": True,  "Kode": "SV-01-09", "Skema": "Revenue Sharing", "Sisa": 15},
        {"No": 9,  "Name/Tenant": "Aquarus Cafe",  "Sub": "tengat - 02-2024-2027",  "Valid Period": "14 Feb 2024 - 13 Feb 2027", "Unit Name/Loc": "Unit Name/Loc. 9",  "Status": "Valid",   "Conflict Info": False, "Kode": "FB-03-02", "Skema": "Rental",          "Sisa": 620},
        {"No": 10, "Name/Tenant": "Bon Bon Express","Sub": "tengat - 08-2022-2024",  "Valid Period": "01 Aug 2022 - 31 Jul 2024", "Unit Name/Loc": "Unit Name/Loc. 10", "Status": "Expired", "Conflict Info": True,  "Kode": "RT-01-11", "Skema": "Revenue Sharing", "Sisa": -300},
        {"No": 11, "Name/Tenant": "Bakso Corner",  "Sub": "tengat - 01-2025-2025",  "Valid Period": "01 Jan 2025 - 15 Jul 2025", "Unit Name/Loc": "Unit Name/Loc. 11", "Status": "Anomaly", "Conflict Info": True,  "Kode": "SV-03-04", "Skema": "Rental",          "Sisa": 45},
        {"No": 12, "Name/Tenant": "Majapahit Premium","Sub": "tengat - 03-2025-2025","Valid Period": "01 Mar 2025 - 28 Sep 2025","Unit Name/Loc": "Unit Name/Loc. 12", "Status": "Valid",   "Conflict Info": False, "Kode": "LG-03-06", "Skema": "MGRS",            "Sisa": 120},
        {"No": 13, "Name/Tenant": "Wingman Bistro", "Sub": "tengat - 04-2025-2025", "Valid Period": "01 Apr 2025 - 14 Jun 2025", "Unit Name/Loc": "Unit Name/Loc. 13", "Status": "Valid",   "Conflict Info": True,  "Kode": "FB-02-07", "Skema": "Rental",          "Sisa": 15},
        {"No": 14, "Name/Tenant": "Aquarus Shop",   "Sub": "tengat - 02-2025-2025", "Valid Period": "01 Feb 2025 - 10 Oct 2025", "Unit Name/Loc": "Unit Name/Loc. 14", "Status": "Valid",   "Conflict Info": False, "Kode": "RT-02-14", "Skema": "Revenue Sharing", "Sisa": 160},
        {"No": 15, "Name/Tenant": "Pertamina Expr.","Sub": "tengat - 07-2023-2024",  "Valid Period": "01 Jul 2023 - 30 Jun 2024", "Unit Name/Loc": "Unit Name/Loc. 15", "Status": "Expired", "Conflict Info": True,  "Kode": "SV-01-03", "Skema": "Revenue Sharing", "Sisa": -330},
    ]
    return pd.DataFrame(data)


# ─────────────────────────────────────────────
# PAGE CSS
# ─────────────────────────────────────────────
_PAGE_CSS = """
<style>
body:has(.lc-page-marker) .stApp {
    background: linear-gradient(135deg, #f7fafc 0%, #eef5f7 50%, #f8fbfa 100%) !important;
}
body:has(.lc-page-marker) .block-container {
    padding-top: 18px !important;
}
body:has(.lc-page-marker) [data-testid="stMain"] div[data-testid="stButton"] > button,
body:has(.lc-page-marker) [data-testid="stMain"] div[data-testid="stDownloadButton"] > button {
    border-radius: 14px !important;
    padding: 9px 18px !important;
    min-height: 40px !important;
    font-size: 12.5px !important;
    font-weight: 700 !important;
    box-shadow: 0 8px 18px rgba(20, 137, 130, 0.16) !important;
}
body:has(.lc-page-marker) [data-testid="stMain"] div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, #4eb7b0, #2f9f99) !important;
    color: #ffffff !important;
}
body:has(.lc-page-marker) [data-testid="stMain"] div[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.72) !important;
    color: #2f8f8a !important;
    border: 1px solid rgba(47,143,138,0.38) !important;
}
body:has(.lc-page-marker) [data-testid="stMain"] div[data-testid="stButton"] > button:hover,
body:has(.lc-page-marker) [data-testid="stMain"] div[data-testid="stDownloadButton"] > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 10px 24px rgba(20, 137, 130, 0.22) !important;
}

/* ── PAGE HEADER ── */
.lc-header-title {
    padding-top: 4px;
}
.lc-header-title h1 {
    margin: 0;
    font-size: 22px;
    line-height: 1.15;
    font-weight: 850;
    color: #111827;
}
.lc-header-title p {
    margin: 4px 0 0;
    font-size: 12px;
    color: #7f8a98;
    font-weight: 500;
}
.lc-userbar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
    padding-top: 2px;
}
.lc-bell {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(30,41,59,0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 15px;
    box-shadow: 0 5px 16px rgba(15,23,42,0.06);
}
.lc-avatar {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: linear-gradient(135deg, #e5e7eb, #cbd5e1);
    color: #111827;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 13px;
    font-weight: 800;
    box-shadow: 0 5px 16px rgba(15,23,42,0.10);
}
.lc-user-name {
    font-size: 12px;
    font-weight: 800;
    color: #1f2937;
    line-height: 1.15;
}
.lc-user-mail {
    font-size: 10px;
    color: #64748b;
    font-weight: 600;
}

/* ── KPI CARD ── */
.lc-kpi-wrap {
    background: rgba(255,255,255,0.84);
    backdrop-filter: blur(18px);
    border: 1px solid rgba(15,23,42,0.06);
    border-radius: 8px;
    padding: 18px 18px;
    min-height: 102px;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 10px 28px rgba(15,23,42,0.11);
    transition: transform .2s, box-shadow .2s;
    margin-bottom: 4px;
}
.lc-kpi-wrap:hover {
    transform: translateY(-2px);
    box-shadow: 0 14px 34px rgba(15,23,42,0.14);
}
.lc-kpi-icon-wrap {
    width: 48px; height: 48px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; flex-shrink: 0;
    color: #ffffff;
}
.lc-kpi-label {
    font-size: 13px; font-weight: 800; color: #1f2937;
    letter-spacing: 0; margin-bottom: 4px;
}
.lc-kpi-value {
    font-size: 30px; font-weight: 850; line-height: 1.08;
    color: #0f172a;
}
.lc-kpi-sub { font-size: 10.5px; color: #7f8a98; font-weight: 600; margin-top: 3px; }

/* ── WARNING BANNER ── */
.lc-warn {
    background: linear-gradient(135deg, rgba(245,158,11,0.10), rgba(251,146,60,0.07));
    border: 1px solid rgba(245,158,11,0.30);
    border-radius: 14px; padding: 13px 18px;
    display: flex; align-items: center; gap: 12px;
    margin-bottom: 14px;
}
.lc-warn-txt { font-size: 12.5px; color: #92400e; font-weight: 500; line-height: 1.5; }
.lc-warn-txt strong { color: #b45309; font-weight: 800; }

/* ── TABLE ── */
.lc-table-card {
    padding: 0 !important;
    overflow: hidden !important;
    border-radius: 8px !important;
    background: rgba(255,255,255,0.86) !important;
    border: 1px solid rgba(15,23,42,0.08) !important;
    box-shadow: 0 10px 28px rgba(15,23,42,0.10) !important;
}
.lc-table-scroll {
    overflow: auto;
    max-height: 420px;
}
.lc-table { width: 100%; border-collapse: separate; border-spacing: 0; }
.lc-table thead tr {
    background: #f0f3f5;
}
.lc-table th {
    position: sticky; top: 0; z-index: 1;
    padding: 14px 18px; text-align: left;
    font-size: 12px; font-weight: 850; color: #111827;
    letter-spacing: 0; white-space: nowrap;
    border-bottom: 1px solid rgba(15,23,42,0.10);
}
.lc-table td {
    padding: 16px 18px; font-size: 13px; color: #1f2937;
    border-bottom: 1px solid rgba(15,23,42,0.10);
    vertical-align: middle;
    background: rgba(255,255,255,0.92);
}
.lc-table tbody tr { transition: background 0.15s; }
.lc-table tbody tr:hover td { background: #f8fbfb; }
.lc-table tbody tr:last-child td { border-bottom: none; }

.lc-no { font-size: 13px; color: #111827; font-weight: 700; text-align: center; }
.lc-name { font-weight: 800; color: #111827; font-size: 13px; }
.lc-sub  { font-size: 12px; color: #111827; margin-top: 3px; font-weight: 500; }
.lc-period { font-size: 13px; color: #111827; font-weight: 600; }
.lc-unit   { font-size: 13px; color: #111827; font-weight: 600; }

/* ── STATUS BADGES ── */
.badge-valid   { background:#8bc34a; color:#12340f; border:1px solid rgba(70,125,30,0.20); padding:5px 14px; border-radius:999px; font-size:12px; font-weight:800; white-space:nowrap; }
.badge-anomaly { background:#f0a83b; color:#3d2300; border:1px solid rgba(177,101,7,0.22); padding:5px 14px; border-radius:999px; font-size:12px; font-weight:800; white-space:nowrap; }
.badge-expired { background:#e06152; color:#ffffff; border:1px solid rgba(176,45,33,0.22); padding:5px 14px; border-radius:999px; font-size:12px; font-weight:800; white-space:nowrap; }
.conflict-link { color:#9f3a36; font-weight:800; font-size:12px; text-decoration:none; cursor:pointer; }
.no-conflict   { color:#94a3b8; font-size:12px; }

/* ── FOOTER ── */
.lc-tbl-footer {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 18px; border-top: 1px solid rgba(99,102,241,0.07);
    flex-wrap: wrap; gap: 8px;
}
.lc-footer-info { font-size: 11.5px; color: #94a3b8; font-weight: 500; }

/* ── BOTTOM ACTION BAR ── */
.lc-bottom-bar {
    background: rgba(255,255,255,0.82);
    backdrop-filter: blur(16px);
    border-top: 1px solid rgba(15,23,42,0.08);
    padding: 12px 0 0;
    margin-top: 8px;
}

/* ── FILTER PILLS ── */
.lc-filter-row {
    display: flex; align-items: center; gap: 10px;
    justify-content: flex-end; margin-bottom: 14px; flex-wrap: wrap;
}
.lc-filter-pill {
    background: rgba(255,255,255,0.72); backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.92); border-radius: 22px;
    padding: 7px 16px; font-size: 12px; font-weight: 600; color: #64748b;
    cursor: pointer; display: flex; align-items: center; gap: 6px;
    box-shadow: 0 2px 8px rgba(99,102,241,0.06);
    white-space: nowrap;
}

/* ── FORM ── */
.lc-add-card { margin-bottom: 16px; }
</style>
"""


# ─────────────────────────────────────────────
# INIT STATE
# ─────────────────────────────────────────────
def _init_state():
    if "lc_df"          not in st.session_state: st.session_state.lc_df          = _get_contract_data()
    if "lc_page"        not in st.session_state: st.session_state.lc_page        = 0
    if "lc_show_form"   not in st.session_state: st.session_state.lc_show_form   = False
    if "lc_selected"    not in st.session_state: st.session_state.lc_selected    = set()


# ─────────────────────────────────────────────
# TABLE
# ─────────────────────────────────────────────
def _status_badge(s):
    if s == "Valid":   return '<span class="badge-valid">Valid</span>'
    if s == "Anomaly": return '<span class="badge-anomaly">Anomaly</span>'
    if s == "Expired": return '<span class="badge-expired">Expired</span>'
    return f'<span>{s}</span>'

def _render_table(df):
    total   = len(df)
    rows    = df

    rows_html = ""
    if total == 0:
        rows_html = """
        <tr>
          <td colspan="6" style="text-align:center;padding:28px;color:#64748b;font-weight:600;">
            Tidak ada data kontrak yang sesuai dengan filter.
          </td>
        </tr>"""
    for _, r in rows.iterrows():
        conflict = '<span class="conflict-link">Conflict Info</span>' if r["Conflict Info"] else '<span class="no-conflict">—</span>'
        rows_html += f"""
        <tr>
          <td class="lc-no">{r['No']}</td>
          <td>
            <div class="lc-name">{r['Name/Tenant']}</div>
            <div class="lc-sub">{r['Sub']}</div>
          </td>
          <td class="lc-period">{r['Valid Period']}</td>
          <td class="lc-unit">{r['Unit Name/Loc']}</td>
          <td>{_status_badge(r['Status'])}</td>
          <td>{conflict}</td>
        </tr>"""

    html = f"""
    <div class="nad-card lc-table-card">
      <div class="lc-table-scroll">
        <table class="lc-table">
          <thead>
            <tr>
              <th style="width:48px;">No.</th>
              <th>Name / Tenant</th>
              <th>Valid Period</th>
              <th>Unit Name/Loc</th>
              <th>Status</th>
              <th>Conflict Info</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# ADD FORM
# ─────────────────────────────────────────────
def _render_add_form():
    st.markdown('<div class="nad-card lc-add-card">', unsafe_allow_html=True)
    st.markdown('<div class="nad-card-title">➕ Tambah Kontrak Baru</div>', unsafe_allow_html=True)
    st.markdown('<div class="nad-card-sub">Isi detail kontrak kerjasama sewa ruangan baru.</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        name   = st.text_input("Name/Tenant",    placeholder="e.g. NAST Merch",     key="lc_f_name")
        sub    = st.text_input("Sub / Tengat ID", placeholder="e.g. august on ...",  key="lc_f_sub")
        unit   = st.text_input("Unit Name/Loc",   placeholder="e.g. Unit Name/Loc. 1", key="lc_f_unit")
    with c2:
        mulai    = st.date_input("Tanggal Mulai",    key="lc_f_mulai")
        berakhir = st.date_input("Tanggal Berakhir", key="lc_f_berakhir")
        skema    = st.selectbox("Skema", ["Rental", "Revenue Sharing", "MGRS"], key="lc_f_skema")
    with c3:
        status_opt = st.selectbox("Status", ["Valid", "Anomaly", "Expired"], key="lc_f_status")
        has_conflict = st.checkbox("Ada Conflict Info", key="lc_f_conflict")
        kode = st.text_input("Kode Ruang", placeholder="e.g. FB-01-01", key="lc_f_kode")

    b1, b2, _ = st.columns([1.2, 1, 5])
    with b1:
        if st.button("✅ Simpan", key="lc_save", use_container_width=True):
            if not name or not unit:
                st.error("Mohon isi Name/Tenant dan Unit Name/Loc.")
            else:
                period_str = f"{mulai.strftime('%d %b %Y')} - {berakhir.strftime('%d %b %Y')}"
                sisa = (berakhir - date.today()).days
                new_no = int(st.session_state.lc_df["No"].max()) + 1
                new_row = {
                    "No": new_no, "Name/Tenant": name, "Sub": sub,
                    "Valid Period": period_str, "Unit Name/Loc": unit,
                    "Status": status_opt, "Conflict Info": has_conflict,
                    "Kode": kode, "Skema": skema, "Sisa": sisa,
                }
                st.session_state.lc_df = pd.concat(
                    [pd.DataFrame([new_row]), st.session_state.lc_df], ignore_index=True)
                st.session_state.lc_show_form = False
                st.session_state.lc_page = 0
                st.rerun()
    with b2:
        if st.button("✖ Batal", key="lc_cancel", use_container_width=True):
            st.session_state.lc_show_form = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def render_lease_contract():
    _init_state()
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)
    st.markdown('<div class="lc-page-marker"></div>', unsafe_allow_html=True)

    df_all = st.session_state.lc_df

    # ── KPI values ──
    total_records = len(df_all)
    valid_records = int((df_all["Status"] == "Valid").sum())
    anomalies     = int((df_all["Status"] == "Anomaly").sum())
    conflicts     = int(df_all["Conflict Info"].sum())

    # ── Page Header ──
    h_title, h_search, h_user = st.columns([3.8, 3.4, 2.8])
    with h_title:
        st.markdown("""
        <div class="lc-header-title">
            <h1>Lease Contract</h1>
            <p>Pengelolaan kontrak sewa ruangan tenant di seluruh terminal.</p>
        </div>""", unsafe_allow_html=True)
    with h_search:
        search_f = st.text_input("search_contract", placeholder="🔍  Searching anything...",
                                 label_visibility="collapsed", key="lc_fsearch")
    with h_user:
        initial = st.session_state.get("user_name", "Admin")[0].upper()
        uname   = st.session_state.get("user_name", "Admin")
        uemail  = st.session_state.get("user_email", "angkasapura@mail.com")
        st.markdown(f"""
        <div class="lc-userbar">
            <div class="lc-bell">🔔</div>
            <div style="display:flex;align-items:center;gap:8px;">
                <div class="lc-avatar">{initial}</div>
                <div>
                    <div class="lc-user-name">{uname}</div>
                    <div class="lc-user-mail">{uemail}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="nad-top-divider"></div>', unsafe_allow_html=True)

    # ── Action Buttons (top right) ──
    _, ab1, ab2 = st.columns([6.3, 1.8, 1.9])
    with ab1:
        df_exp = df_all.copy()
        csv = df_exp[["No","Name/Tenant","Sub","Valid Period","Unit Name/Loc","Status","Skema"]].to_csv(index=False).encode("utf-8")
        st.download_button("↓  Export Logs", data=csv,
                           file_name="lease_contract.csv", mime="text/csv",
                           use_container_width=True, key="lc_export")
    with ab2:
        if st.button("↑  Approve & Publish", use_container_width=True, key="lc_approve"):
            st.toast("✅ Kontrak berhasil dipublikasikan!")

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    # ── 4 KPI Cards ──
    k1, k2, k3, k4 = st.columns(4)
    kpi_cfg = [
        (k1, "▣", "#3aa7a1", "Total Records", str(total_records), "Seluruh data kontrak"),
        (k2, "✓", "#7abf3f", "Valid Records", str(valid_records), "Kontrak aktif"),
        (k3, "△", "#e3a332", "Anomalies", str(anomalies), "Perlu pengecekan"),
        (k4, "↔", "#d65b4f", "Conflicts", str(conflicts), "Ada tumpang tindih"),
    ]
    for col, icon, icon_bg, label, value, sub in kpi_cfg:
        with col:
            st.markdown(f"""
            <div class="lc-kpi-wrap">
                <div class="lc-kpi-icon-wrap" style="background:{icon_bg};">{icon}</div>
                <div>
                    <div class="lc-kpi-label">{label}</div>
                    <div class="lc-kpi-value">{value}</div>
                    <div class="lc-kpi-sub">{sub}</div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Add Form ──
    if st.session_state.lc_show_form:
        _render_add_form()

    # ── Filter Row ──
    _, fc1, fc2 = st.columns([5.6, 2.1, 2.3])
    with fc1:
        status_f = st.selectbox("", ["STATUS: ALL STATUS", "Valid", "Anomaly", "Expired"],
                                label_visibility="collapsed", key="lc_fs")
    with fc2:
        anom_f = st.selectbox("", ["ANOMALY TYPE: ALL CATEGORIES", "Rental", "Revenue Sharing", "MGRS"],
                              label_visibility="collapsed", key="lc_fa")

    # ── Apply Filters ──
    df = df_all.copy()
    if status_f not in ["STATUS: ALL STATUS", ""]:
        df = df[df["Status"] == status_f]
    if anom_f not in ["ANOMALY TYPE: ALL CATEGORIES", ""]:
        df = df[df["Skema"] == anom_f]
    if search_f:
        mask = (df["Name/Tenant"].str.contains(search_f, case=False, na=False) |
                df["Unit Name/Loc"].str.contains(search_f, case=False, na=False) |
                df["Sub"].str.contains(search_f, case=False, na=False))
        df = df[mask]
    df = df.reset_index(drop=True)

    # ── Table ──
    _render_table(df)

    # ── Bottom Action Bar ──
    st.markdown("<div class='lc-bottom-bar'></div>", unsafe_allow_html=True)
    bb1, bb2, bb3 = st.columns([5.4, 2.2, 2.4])
    with bb2:
        if st.button("Clear Selected Information", use_container_width=True, key="lc_clear"):
            st.toast("Selected information cleared.", icon="🗑️")
    with bb3:
        if st.button("Confirm and Publish Operator", use_container_width=True, key="lc_confirm"):
            st.toast("✅ Operator berhasil dipublikasikan!", icon="✅")


# ── Standalone ─────────────────────────────
if __name__ == "__main__":
    st.set_page_config(page_title="Lease Contract", layout="wide")
    render_lease_contract()
