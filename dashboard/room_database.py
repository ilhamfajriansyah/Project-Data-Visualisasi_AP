import streamlit as st
import pandas as pd
import io

# ── Sample Data ────────────────────────────────────────────────────────────────
def _get_room_data() -> pd.DataFrame:
    data = [
        {"Room ID": "T1-L2-01", "Terminal": "Terminal 1", "Location": "Terminal 1, Level 2",        "Gate Point": "Gate 3",  "Area (m²)": 120, "Facilities": "❄️ 🍽️",     "Classifications": "Food & Beverage", "Status": "Occupied"},
        {"Room ID": "T2-A-07",  "Terminal": "Terminal 2", "Location": "Terminal 2, Arrival Hall",   "Gate Point": "Gate 12", "Area (m²)": 45,  "Facilities": "📶",          "Classifications": "Retail",          "Status": "Available"},
        {"Room ID": "T2-D-42",  "Terminal": "Terminal 2", "Location": "Terminal 2, Duty Free Area", "Gate Point": "Gate 5",  "Area (m²)": 18,  "Facilities": "📶 📡",       "Classifications": "Services",        "Status": "Available"},
        {"Room ID": "T1-C-12",  "Terminal": "Terminal 1", "Location": "Terminal 1, Concourse B",    "Gate Point": "Gate 2",  "Area (m²)": 450, "Facilities": "🍸 🚿 ♿",    "Classifications": "Lounge",          "Status": "Occupied"},
        {"Room ID": "T3-N-01",  "Terminal": "Terminal 3", "Location": "Terminal 3, North Wing",     "Gate Point": "Gate 10", "Area (m²)": 75,  "Facilities": "🔒",          "Classifications": "Retail",          "Status": "Available"},
        {"Room ID": "T1-D-03",  "Terminal": "Terminal 1", "Location": "Terminal 1, Departure Hall", "Gate Point": "Gate 7",  "Area (m²)": 200, "Facilities": "❄️ 📶",       "Classifications": "Food & Beverage", "Status": "Available"},
        {"Room ID": "T2-L1-05", "Terminal": "Terminal 2", "Location": "Terminal 2, Level 1",        "Gate Point": "Gate 4",  "Area (m²)": 80,  "Facilities": "📶 ♿",        "Classifications": "Services",        "Status": "Occupied"},
        {"Room ID": "T3-S-08",  "Terminal": "Terminal 3", "Location": "Terminal 3, South Wing",     "Gate Point": "Gate 15", "Area (m²)": 60,  "Facilities": "🔒 ❄️",       "Classifications": "Retail",          "Status": "Available"},
        {"Room ID": "T1-B-11",  "Terminal": "Terminal 1", "Location": "Terminal 1, Gate B Area",    "Gate Point": "Gate 11", "Area (m²)": 300, "Facilities": "🍸 ❄️",       "Classifications": "Lounge",          "Status": "Occupied"},
        {"Room ID": "T2-G-22",  "Terminal": "Terminal 2", "Location": "Terminal 2, Gate G Area",    "Gate Point": "Gate 22", "Area (m²)": 55,  "Facilities": "📶",          "Classifications": "Food & Beverage", "Status": "Available"},
        {"Room ID": "T3-E-09",  "Terminal": "Terminal 3", "Location": "Terminal 3, East Wing",      "Gate Point": "Gate 9",  "Area (m²)": 90,  "Facilities": "❄️ 🚿",       "Classifications": "Services",        "Status": "Occupied"},
        {"Room ID": "T1-M-14",  "Terminal": "Terminal 1", "Location": "Terminal 1, Mezzanine",      "Gate Point": "Gate 14", "Area (m²)": 140, "Facilities": "📶 ♿",        "Classifications": "Retail",          "Status": "Available"},
        {"Room ID": "T2-VIP-1", "Terminal": "Terminal 2", "Location": "Terminal 2, VIP Zone",       "Gate Point": "Gate 1",  "Area (m²)": 500, "Facilities": "🍸 ❄️ ♿",    "Classifications": "Lounge",          "Status": "Occupied"},
        {"Room ID": "T3-W-17",  "Terminal": "Terminal 3", "Location": "Terminal 3, West Wing",      "Gate Point": "Gate 17", "Area (m²)": 35,  "Facilities": "📶",          "Classifications": "Retail",          "Status": "Available"},
        {"Room ID": "T1-F-06",  "Terminal": "Terminal 1", "Location": "Terminal 1, Food Court",     "Gate Point": "Gate 6",  "Area (m²)": 250, "Facilities": "❄️ 🍽️ 📶",   "Classifications": "Food & Beverage", "Status": "Occupied"},
        {"Room ID": "T2-C-33",  "Terminal": "Terminal 2", "Location": "Terminal 2, Central Hub",    "Gate Point": "Gate 33", "Area (m²)": 110, "Facilities": "♿ 🔒",        "Classifications": "Services",        "Status": "Available"},
        {"Room ID": "T3-P-04",  "Terminal": "Terminal 3", "Location": "Terminal 3, Premium Area",   "Gate Point": "Gate 4",  "Area (m²)": 180, "Facilities": "🍸 ❄️ 📶",   "Classifications": "Lounge",          "Status": "Occupied"},
        {"Room ID": "T1-A-19",  "Terminal": "Terminal 1", "Location": "Terminal 1, Arrival Zone",   "Gate Point": "Gate 19", "Area (m²)": 65,  "Facilities": "📶",          "Classifications": "Retail",          "Status": "Available"},
        {"Room ID": "T2-D-27",  "Terminal": "Terminal 2", "Location": "Terminal 2, Duty Zone B",    "Gate Point": "Gate 27", "Area (m²)": 42,  "Facilities": "🔒 ❄️",       "Classifications": "Services",        "Status": "Available"},
        {"Room ID": "T3-L2-02", "Terminal": "Terminal 3", "Location": "Terminal 3, Level 2",        "Gate Point": "Gate 8",  "Area (m²)": 320, "Facilities": "🍸 ♿ 📶",    "Classifications": "Lounge",          "Status": "Occupied"},
    ]
    return pd.DataFrame(data)


def _room_data_from_dashboard(df_raw: pd.DataFrame | None) -> pd.DataFrame:
    if df_raw is None or df_raw.empty:
        return _get_room_data()

    df = df_raw.copy()

    def col(name, default=""):
        if name in df.columns:
            return df[name]
        return pd.Series([default] * len(df), index=df.index)

    area = df["luas_sqm"] if "luas_sqm" in df.columns else col("produksi_m2", 0)
    room_df = pd.DataFrame({
        "Room ID": col("kode_ruang", "Unknown").fillna("Unknown").astype(str),
        "Terminal": col("terminal", "Unknown").fillna("Unknown").astype(str),
        "Location": col("lokasi", "").fillna("").astype(str),
        "Gate Point": col("gate", "").fillna("").astype(str),
        "Area (mÂ²)": pd.to_numeric(area, errors="coerce").fillna(0),
        "Facilities": "-",
        "Classifications": col("bidang_usaha", "Unclassified").fillna("Unclassified").astype(str),
        "Status": "Occupied",
    })

    missing_location = room_df["Location"].str.strip().eq("")
    room_df.loc[missing_location, "Location"] = room_df.loc[missing_location, "Terminal"]
    missing_gate = room_df["Gate Point"].str.strip().eq("")
    room_df.loc[missing_gate, "Gate Point"] = col("lantai", "-").fillna("-").astype(str)

    room_df = room_df.drop_duplicates(subset=["Room ID", "Terminal", "Location"]).reset_index(drop=True)
    return room_df if not room_df.empty else _get_room_data()


# ── Session State Init ─────────────────────────────────────────────────────────
def _init_state(df_raw: pd.DataFrame | None = None):
    if "room_df" not in st.session_state:
        st.session_state.room_df = _room_data_from_dashboard(df_raw)
        st.session_state.room_source_import_id = (
            int(pd.to_numeric(df_raw["import_id"], errors="coerce").max())
            if df_raw is not None and "import_id" in df_raw.columns and not df_raw.empty
            else None
        )
    elif df_raw is not None and "import_id" in df_raw.columns and not df_raw.empty:
        import_id = int(pd.to_numeric(df_raw["import_id"], errors="coerce").max())
        if st.session_state.get("room_source_import_id") != import_id:
            st.session_state.room_df = _room_data_from_dashboard(df_raw)
            st.session_state.room_source_import_id = import_id
            st.session_state.room_page = 0
    if "room_page" not in st.session_state:
        st.session_state.room_page = 0
    if "show_add_form" not in st.session_state:
        st.session_state.show_add_form = False


# ── Badge HTML helpers ─────────────────────────────────────────────────────────
_BADGE_CLASS = {
    "Food & Beverage": "badge-fb",
    "Retail":          "badge-retail",
    "Services":        "badge-services",
    "Lounge":          "badge-lounge",
}

def _badge(text: str) -> str:
    cls = _BADGE_CLASS.get(text, "badge-warning")
    return f'<span class="badge {cls}">{text}</span>'

def _status_html(status: str) -> str:
    if status == "Occupied":
        return '<span class="status-dot"><span class="dot dot-occupied"></span><span class="status-occupied">Occupied</span></span>'
    return '<span class="status-dot"><span class="dot dot-available"></span><span class="status-available">Available</span></span>'


# ── Table renderer ─────────────────────────────────────────────────────────────
def _render_table(df: pd.DataFrame, page: int, page_size: int = 5):
    total   = len(df)
    n_pages = max(1, -(-total // page_size))           # ceiling div
    page    = max(0, min(page, n_pages - 1))
    start   = page * page_size
    end     = min(start + page_size, total)
    slice_  = df.iloc[start:end]

    rows_html = ""
    for _, r in slice_.iterrows():
        area_val = r['Area (m²)']
        if isinstance(area_val, (int, float)):
            if int(area_val) == area_val:
                area_str = f"{int(area_val):,}".replace(",", ".")
            else:
                area_str = f"{area_val:,.2f}".replace(".", "X").replace(",", ".").replace("X", ",")
        else:
            area_str = str(area_val)

        rows_html += f"""
        <tr>
          <td><span class="room-id">{r['Room ID']}</span></td>
          <td><span class="location-text">{r['Location']}</span></td>
          <td><span class="gate-text">{r['Gate Point']}</span></td>
          <td><span class="area-text">{area_str} m²</span></td>
          <td><div class="facilities">{_fac_icons(str(r['Facilities']))}</div></td>
          <td>{_badge(r['Classifications'])}</td>
          <td>{_status_html(r['Status'])}</td>
        </tr>"""

    table_html = f"""
    <div class="nad-card" style="padding:0;overflow:hidden;">
      <div style="overflow-x:auto;">
        <table class="room-table">
          <thead>
            <tr>
              <th>Room ID</th>
              <th>Location</th>
              <th>Gate Point</th>
              <th>Area (m²)</th>
              <th>Facilities</th>
              <th>Classifications</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>{rows_html}</tbody>
        </table>
      </div>
      <div class="table-footer">
        <span class="table-info">Showing {start+1} to {end} of {total} entries</span>
      </div>
    </div>
    """
    st.markdown(table_html, unsafe_allow_html=True)
    return page, n_pages


def _fac_icons(fac_str: str) -> str:
    icons = fac_str.strip().split()
    return "".join(f'<div class="fac-icon">{ic}</div>' for ic in icons)


# ── Add Room Form ──────────────────────────────────────────────────────────────
def _render_add_form():
    st.markdown('<div class="nad-card">', unsafe_allow_html=True)
    st.markdown('<div class="nad-card-title">➕ Add New Room</div>', unsafe_allow_html=True)
    st.markdown('<div class="nad-card-sub">Tambahkan ruangan baru ke dalam database katalog aset.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        room_id  = st.text_input("Room ID",    placeholder="e.g. FB-01-01",  key="add_room_id")
        terminal = st.selectbox("Terminal",    ["Terminal 1", "Terminal 2", "Terminal 3"], key="add_terminal")
        gate     = st.text_input("Gate Point", placeholder="e.g. Gate 3",    key="add_gate")
    with c2:
        location = st.text_input("Location Detail", placeholder="e.g. Level 2, Departure Hall", key="add_location")
        area     = st.number_input("Area (m²)", min_value=1, value=50,        key="add_area")
        classif  = st.selectbox("Classification", ["Food & Beverage", "Retail", "Services", "Lounge"], key="add_class")

    status = st.selectbox("Status", ["Available", "Occupied"], key="add_status")
    fac_options = {"❄️ AC": "❄️", "📶 WiFi": "📶", "🍸 Bar": "🍸", "🚿 Water": "🚿", "♿ Accessible": "♿", "🔒 Secured": "🔒"}
    chosen_facs = st.multiselect("Facilities", list(fac_options.keys()), key="add_facs")

    b1, b2 = st.columns([1, 1])
    with b1:
        if st.button("✅  Save Room", key="btn_save_room", use_container_width=True):
            if not room_id or not location or not gate:
                st.error("Mohon lengkapi Room ID, Location Detail, dan Gate Point.")
            else:
                fac_str = " ".join(fac_options[f] for f in chosen_facs) or "—"
                new_row = {
                    "Room ID":        room_id,
                    "Terminal":       terminal,
                    "Location":       f"{terminal}, {location}",
                    "Gate Point":     gate,
                    "Area (m²)":      area,
                    "Facilities":     fac_str,
                    "Classifications": classif,
                    "Status":         status,
                }
                st.session_state.room_df = pd.concat(
                    [pd.DataFrame([new_row]), st.session_state.room_df],
                    ignore_index=True
                )
                st.session_state.show_add_form = False
                st.session_state.room_page = 0
                st.rerun()
    with b2:
        if st.button("✖  Cancel", key="btn_cancel_room", use_container_width=True):
            st.session_state.show_add_form = False
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


# ── Extra CSS injected on this page ───────────────────────────────────────────
_PAGE_CSS = """
<style>
/* ── TABLE ── */
.room-table {
    width: 100%;
    border-collapse: collapse;
}
.room-table thead tr {
    background: rgba(99,102,241,0.05);
    border-bottom: none;
}
.room-table th {
    padding: 11px 16px;
    text-align: left;
    font-size: 11px;
    font-weight: 700;
    color: #4F46E5;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
}
.room-table td {
    padding: 14px 16px;
    font-size: 13px;
    color: #334155;
    border-bottom: 1px solid rgba(99,102,241,0.05);
}
.room-table tbody tr { transition: background 0.15s; }
.room-table tbody tr:hover { background: rgba(99,102,241,0.025); }
.room-table tbody tr:last-child td { border-bottom: none; }

.room-id {
    font-weight: 700;
    color: #4f46e5;
    font-size: 12.5px;
    font-family: 'Inter', monospace;
}
.location-text { font-weight: 500; }
.gate-text { color: #64748b; font-size: 12px; }
.area-text { font-weight: 600; color: #374151; }

/* ── FACILITY ICONS ── */
.facilities { display: flex; gap: 5px; align-items: center; }
.fac-icon {
    width: 26px; height: 26px; border-radius: 8px;
    background: rgba(99,102,241,0.07);
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; color: #4f46e5;
}

/* ── BADGES ── */
.badge {
    padding: 4px 12px; border-radius: 20px;
    font-size: 11px; font-weight: 700;
    display: inline-block; white-space: nowrap;
}
.badge-fb       { background: rgba(6,182,212,0.12);  color: #0891b2; border: 1px solid rgba(6,182,212,0.22); }
.badge-retail   { background: rgba(251,146,60,0.12); color: #d97706; border: 1px solid rgba(251,146,60,0.22); }
.badge-services { background: rgba(99,102,241,0.12); color: #4f46e5; border: 1px solid rgba(99,102,241,0.22); }
.badge-lounge   { background: rgba(16,185,129,0.12); color: #059669; border: 1px solid rgba(16,185,129,0.22); }

/* ── STATUS ── */
.status-dot { display: flex; align-items: center; gap: 6px; font-size: 12.5px; font-weight: 600; }
.dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.dot-occupied { background: #ef4444; box-shadow: 0 0 0 3px rgba(239,68,68,0.15); }
.dot-available{ background: #10b981; box-shadow: 0 0 0 3px rgba(16,185,129,0.15); }
.status-occupied { color: #dc2626; }
.status-available{ color: #059669; }

/* ── TABLE FOOTER ── */
.table-footer {
    display: flex; align-items: center; justify-content: flex-start;
    padding: 12px 18px;
    border-top: 1px solid rgba(99,102,241,0.07);
}
.table-info { font-size: 11.5px; color: #94a3b8; font-weight: 500; }

/* ── PAGE HEADER ── */
.page-header {
    display: flex; align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 4px;
}
.page-title-text {
    font-size: 19px; font-weight: 800; color: #0f172a; line-height: 1.2;
}
.page-subtitle {
    font-size: 11px; color: #94a3b8; margin-top: 2px;
}
</style>
"""


# ── Main entrypoint ────────────────────────────────────────────────────────────
def render_room_database(df_raw: pd.DataFrame | None = None):
    """Call this function from your dashboard.py page router."""

    _init_state(df_raw)
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)

    # ── Page Header ──
    st.markdown("""
    <div class="page-header">
      <div>
        <div class="page-title-text">Room Database</div>
        <div class="page-subtitle">
          Katalog digital seluruh ruangan / space komersial di seluruh terminal bandara.
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="nad-top-divider"></div>', unsafe_allow_html=True)

    # ── Filters ──
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown('<div class="nad-card" style="padding:14px 18px;">'
                    '<div class="nad-card-sub" style="margin-bottom:4px;">Filter by Terminal</div>', unsafe_allow_html=True)
        terminal_filter = st.selectbox("terminal_label", ["All Terminals", "Terminal 1", "Terminal 2", "Terminal 3"],
                                       label_visibility="collapsed", key="rd_filter_terminal")
        st.markdown('</div>', unsafe_allow_html=True)

    with f2:
        st.markdown('<div class="nad-card" style="padding:14px 18px;">'
                    '<div class="nad-card-sub" style="margin-bottom:4px;">Business Category</div>', unsafe_allow_html=True)
        cat_filter = st.selectbox("cat_label", ["All Classifications", "Food & Beverage", "Retail", "Services", "Lounge"],
                                  label_visibility="collapsed", key="rd_filter_cat")
        st.markdown('</div>', unsafe_allow_html=True)

    with f3:
        st.markdown('<div class="nad-card" style="padding:14px 18px;">'
                    '<div class="nad-card-sub" style="margin-bottom:4px;">Status</div>', unsafe_allow_html=True)
        status_filter = st.selectbox("status_label", ["All Statuses", "Occupied", "Available"],
                                     label_visibility="collapsed", key="rd_filter_status")
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Action buttons ──
    col_spacer, col_export, col_add = st.columns([6, 1.2, 1.2])
    with col_export:
        df_all = st.session_state.room_df.drop(columns=["Terminal"])
        csv_bytes = df_all.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="⬇️  Export",
            data=csv_bytes,
            file_name="room_database.csv",
            mime="text/csv",
            use_container_width=True,
            key="btn_export"
        )
    with col_add:
        if st.button("＋  Add Room", use_container_width=True, key="btn_add_room"):
            st.session_state.show_add_form = not st.session_state.show_add_form
            st.rerun()

    # ── Add Room Form ──
    if st.session_state.show_add_form:
        _render_add_form()

    st.markdown('<div class="nad-top-divider"></div>', unsafe_allow_html=True)

    # ── Apply Filters ──
    df = st.session_state.room_df.copy()
    if terminal_filter != "All Terminals":
        df = df[df["Terminal"] == terminal_filter]
    if cat_filter != "All Classifications":
        df = df[df["Classifications"] == cat_filter]
    if status_filter != "All Statuses":
        df = df[df["Status"] == status_filter]
    df = df.reset_index(drop=True)

    # Reset page when filters change
    filter_key = f"{terminal_filter}|{cat_filter}|{status_filter}"
    if st.session_state.get("_rd_last_filter") != filter_key:
        st.session_state.room_page = 0
        st.session_state["_rd_last_filter"] = filter_key

    # ── Render Table ──
    page, n_pages = _render_table(df, st.session_state.room_page)

    # ── Pagination ──
    if n_pages > 1:
        pagination_button_count = n_pages + 2
        pg_cols = st.columns([1, *([0.12] * pagination_button_count), 1], gap="small")
        with pg_cols[1]:
            if st.button("‹", key="pg_prev", disabled=(page == 0)):
                st.session_state.room_page = page - 1
                st.rerun()
        for i in range(n_pages):
            with pg_cols[i + 2]:
                label = f"**{i+1}**" if i == page else str(i + 1)
                if st.button(label, key=f"pg_{i}"):
                    st.session_state.room_page = i
                    st.rerun()
        with pg_cols[n_pages + 2]:
            if st.button("›", key="pg_next", disabled=(page >= n_pages - 1)):
                st.session_state.room_page = page + 1
                st.rerun()


# ── Standalone run (for testing) ───────────────────────────────────────────────
if __name__ == "__main__":
    st.set_page_config(page_title="Room Database", layout="wide")
    render_room_database()
