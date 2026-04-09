import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

st.set_page_config(
    page_title="Non Aeronautical Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# LOAD CSS DARI FILE EKSTERNAL
# ─────────────────────────────────────────────
def load_css(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
load_css("style.css")


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
defaults = {
    "user_name":   "Administrator",
    "user_role":   "Admin",
    "user_email":  "admin@angkasapura.com",
    "active_menu": "Revenue Sharing",
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────
# DATABASE & DATA
# ─────────────────────────────────────────────
@st.cache_resource
def get_engine():
    url = (
        f"postgresql://{os.getenv('DB_USER','postgres')}:{os.getenv('DB_PASSWORD','postgres')}"
        f"@{os.getenv('DB_HOST','localhost')}:{os.getenv('DB_PORT','5432')}"
        f"/{os.getenv('DB_NAME','dashboard_tenant')}"
    )
    return create_engine(url)

@st.cache_data(ttl=300)
def load_data():
    try:
        return pd.read_sql("SELECT * FROM pendapatan_tenant", get_engine())
    except:
        return generate_dummy_data()

def generate_dummy_data():
    np.random.seed(42)
    perusahaan = [
        "PT BUDI PUTRA BOGAJAYA", "PT DEWATAAGUNG WIBAWA", "PT PERTAMINA PATRA NIAGA",
        "PT KIJANG WAHANA KREATIFA", "PT BOGAJAYA MEGAH ABADI", "PT AQUARUS GEMILANG",
        "PT TAURUS GEMILANG", "PT GAPURA ANGKASA", "PT GARUDA MAINTENANCE"
    ]
    brands = [
        "Bakso Pak Dj", "Bon Bon Voy", "Pertamina", "Bon Bon Voy", "Kepompong",
        "Majapahit", "Wingman", "GAUSD", "GMFA"
    ]
    bulan = [
        "January","February","March","April","May","June",
        "July","August","September","October","November","December"
    ]
    rows = []
    for _ in range(600):
        idx = np.random.randint(0, len(perusahaan))
        rows.append({
            "perusahaan":      perusahaan[idx],
            "brand":           brands[idx],
            "terminal":        np.random.choice(["Terminal 1","Terminal 2"], p=[0.5,0.5]),
            "kode_ruang":      np.random.choice(["FB-02-02","POP-22-9","FTC","POP-22-8","P1"]),
            "bidang_usaha":    np.random.choice(["Food & Beverage","Retail","Services","Banking"]),
            "masa_jasa":       np.random.choice(bulan),
            "tahun":           np.random.choice([2025, 2026]),
            "min_omzet":       np.random.randint(10_000_000, 200_000_000),
            "real_omzet":      np.random.randint(10_000_000, 300_000_000),
            "pendapatan_sewa": np.random.randint(5_000_000, 70_000_000),
            "pendapatan_rs":   np.random.randint(1_000_000, 30_000_000),
            "kontribusi":      np.random.randint(5_000_000, 80_000_000),
            "luas_sqm":        np.random.randint(10, 200),
        })
    df = pd.DataFrame(rows)
    df["rev_sqm"] = df["real_omzet"] / df["luas_sqm"]
    df["acv"]     = (df["real_omzet"] / df["min_omzet"] * 100).round(2)
    return df

def fmt_rp(v):
    if v >= 1_000_000_000_000: return f"Rp {v/1_000_000_000_000:.2f}T"
    if v >= 1_000_000_000:     return f"Rp {v/1_000_000_000:.2f}B"
    if v >= 1_000_000:         return f"Rp {v/1_000_000:.2f}M"
    return f"Rp {v:,.0f}"

BULAN = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]


# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
def show_sidebar():
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="padding:24px 20px 18px 20px;border-bottom:1px solid #e8eaed;">
            <div style="font-size:15px;font-weight:900;color:#202124;letter-spacing:3px;">LOGO</div>
        </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # Overview
        _nav_item("📊", "Overview")

        # Financial Insights
        st.markdown("""
        <div class="nav-group">
            <span style="font-size:15px;">📊</span>
            <span style="flex:1;">Financial Insights</span>
            <span style="font-size:10px;color:#9aa0a6;">▾</span>
        </div>""", unsafe_allow_html=True)
        _nav_sub("Revenue Sharing")
        _nav_sub("Accrual & Billing")

        # Space Management
        st.markdown("""
        <div class="nav-group">
            <span style="font-size:15px;">🏢</span>
            <span style="flex:1;">Space Management</span>
            <span style="font-size:10px;color:#9aa0a6;">▾</span>
        </div>""", unsafe_allow_html=True)
        _nav_sub("Room Database")
        _nav_sub("Lease Contract")

        # Data Center
        st.markdown("""
        <div class="nav-group">
            <span style="font-size:15px;">🗄️</span>
            <span style="flex:1;">Data Center</span>
            <span style="font-size:10px;color:#9aa0a6;">▾</span>
        </div>""", unsafe_allow_html=True)
        _nav_sub("Import Manager")
        _nav_sub("Data Verification")

        # Traffic Monitor
        _nav_item("📈", "Traffic Monitor")

        # User info di bawah
        st.markdown("<br>" * 5, unsafe_allow_html=True)
        st.markdown("<hr style='border-color:#e8eaed;margin:0;'>", unsafe_allow_html=True)
        initial = st.session_state.user_name[0].upper() if st.session_state.user_name else "U"
        st.markdown(f"""
        <div style="padding:14px 16px 8px 16px;display:flex;align-items:center;gap:10px;">
            <div style="background:#1a73e8;border-radius:50%;width:32px;height:32px;
                        display:flex;align-items:center;justify-content:center;
                        color:#fff;font-size:13px;font-weight:700;flex-shrink:0;">{initial}</div>
            <div style="flex:1;min-width:0;">
                <div style="font-size:12px;font-weight:600;color:#202124;
                            white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                    {st.session_state.user_name}</div>
                <div style="font-size:11px;color:#9aa0a6;">{st.session_state.user_role}</div>
            </div>
        </div>""", unsafe_allow_html=True)


def _nav_item(icon, label):
    """Menu item level 1 (tidak punya sub-menu)"""
    is_active = st.session_state.active_menu == label
    if is_active:
        st.markdown(f"""
        <div style="background:#e8f0fe;border-radius:6px;padding:8px 12px;
                    margin:2px 8px;display:flex;align-items:center;gap:8px;">
            <span style="font-size:14px;">{icon}</span>
            <span style="font-size:13px;font-weight:600;color:#1a73e8;">{label}</span>
        </div>""", unsafe_allow_html=True)
    else:
        c1, c2 = st.columns([1, 5])
        with c1:
            st.markdown(
                f"<div style='padding:7px 0 0 12px;font-size:14px;'>{icon}</div>",
                unsafe_allow_html=True
            )
        with c2:
            if st.button(label, key=f"nav_{label}", use_container_width=True):
                st.session_state.active_menu = label
                st.rerun()


def _nav_sub(label):
    """Sub-menu item (dengan indentasi)"""
    is_active = st.session_state.active_menu == label
    if is_active:
        st.markdown(f'<div class="nav-active">{label}</div>', unsafe_allow_html=True)
    else:
        if st.button(f"  {label}", key=f"nav_{label}", use_container_width=True):
            st.session_state.active_menu = label
            st.rerun()


# ══════════════════════════════════════════════
# TOP NAVBAR
# ══════════════════════════════════════════════
def show_topnav(title="Non Aeronautical Dashboard"):
    n1, n2, n3 = st.columns([3, 4, 3])
    with n1:
        st.markdown(
            f'<h2 style="margin:0;font-size:20px;font-weight:700;color:#202124;'
            f'padding-top:6px;">{title}</h2>',
            unsafe_allow_html=True
        )
    with n2:
        st.text_input(
            "search",
            placeholder="🔍  Searching anything...",
            label_visibility="collapsed",
            key="search_bar"
        )
    with n3:
        initial = st.session_state.user_name[0].upper() if st.session_state.user_name else "U"
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:flex-end;
                    gap:14px;padding-top:4px;">
            <span style="font-size:22px;">🔔</span>
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="background:#1a73e8;border-radius:50%;width:34px;height:34px;
                            display:flex;align-items:center;justify-content:center;
                            color:#fff;font-size:14px;font-weight:700;">{initial}</div>
                <div>
                    <div style="font-size:13px;font-weight:600;color:#202124;">
                        {st.session_state.user_name}</div>
                    <div style="font-size:11px;color:#9aa0a6;">
                        {st.session_state.user_email}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:#e8eaed;margin:10px 0 14px 0;'>", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE: REVENUE SHARING
# ══════════════════════════════════════════════
def page_revenue_sharing(df_raw):
    show_topnav("Non Aeronautical Dashboard")

    # Filter bar
    fb1, fb2, fb3, _, fe1, fe2 = st.columns([2, 2, 2, 2, 1, 1])
    with fb1:
        sel_terminal = st.selectbox(
            "", ["All Terminal"] + sorted(df_raw["terminal"].unique().tolist()),
            key="f_terminal"
        )
    with fb2:
        sel_tahun = st.selectbox(
            "", ["Semua Tahun"] + sorted(df_raw["tahun"].unique().tolist(), reverse=True),
            key="f_tahun"
        )
    with fb3:
        sel_masa = st.selectbox("", ["Semua Bulan"] + BULAN, key="f_masa")
    with fe1:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.button("⇅", key="btn_share", use_container_width=True)
    with fe2:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.button("↑ Export", key="btn_export", use_container_width=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # Apply filters
    df = df_raw.copy()
    if sel_terminal != "All Terminal": df = df[df["terminal"]  == sel_terminal]
    if sel_tahun    != "Semua Tahun":  df = df[df["tahun"]     == int(sel_tahun)]
    if sel_masa     != "Semua Bulan":  df = df[df["masa_jasa"] == sel_masa]

    # KPI Cards
    k1, k2, k3, k4, k5, k6, k7 = st.columns(7)
    with k1: st.metric("Real Omzet",       fmt_rp(df["real_omzet"].sum()),      "+5.2% vs last month")
    with k2: st.metric("Min Omzet",        fmt_rp(df["min_omzet"].sum()),       "↑")
    with k3: st.metric("Pendapatan Sewa",  fmt_rp(df["pendapatan_sewa"].sum()), "↑")
    with k4: st.metric("Pendapatan RS",    fmt_rp(df["pendapatan_rs"].sum()),   "↓")
    with k5: st.metric("Total Kontribusi", fmt_rp(df["kontribusi"].sum()),      "↑")
    with k6: st.metric("Revenue/Sqm",      fmt_rp(df["rev_sqm"].mean()),        "↑")
    with k7: st.metric("ACV",              f"{df['acv'].mean():.2f}%",          "↑")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    # Row 2: Line Chart + Donut + Insight
    col_line, col_donut, col_insight = st.columns([4, 3, 3])

    with col_line:
        st.markdown('<div class="nad-card">', unsafe_allow_html=True)
        rc1, rc2 = st.columns([3, 1])
        with rc1:
            st.markdown('<p class="nad-card-title">Pendapatan 2026</p>', unsafe_allow_html=True)
        with rc2:
            st.selectbox("", ["This Week","This Month","This Year"],
                         key="sel_line", label_visibility="collapsed")

        df_line = df.groupby("masa_jasa").agg(
            pend_sewa=("pendapatan_sewa", "sum"),
            pend_rs=("pendapatan_rs", "sum"),
            others=("kontribusi", "sum")
        ).reset_index()
        df_line["masa_jasa"] = pd.Categorical(df_line["masa_jasa"], categories=BULAN, ordered=True)
        df_line = df_line.sort_values("masa_jasa")
        df_line["short"] = df_line["masa_jasa"].astype(str).str[:3]

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_line["short"], y=df_line["pend_sewa"],
            mode="lines+markers", name="Pendapatan Sewa",
            line=dict(color="#1a73e8", width=2), marker=dict(size=5)
        ))
        fig.add_trace(go.Scatter(
            x=df_line["short"], y=df_line["pend_rs"],
            mode="lines+markers", name="Pendapatan RS",
            line=dict(color="#34a853", width=2), marker=dict(size=5)
        ))
        fig.add_trace(go.Scatter(
            x=df_line["short"], y=df_line["others"],
            mode="lines+markers", name="Others",
            line=dict(color="#fbbc04", width=2), marker=dict(size=5)
        ))
        fig.update_layout(
            height=230, plot_bgcolor="#fff", paper_bgcolor="#fff",
            margin=dict(t=5, b=0, l=0, r=0),
            legend=dict(orientation="h", y=-0.25, font=dict(size=10, color="#5f6368")),
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#9aa0a6")),
            yaxis=dict(showgrid=True, gridcolor="#f1f3f4", tickfont=dict(size=10, color="#9aa0a6")),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_donut:
        st.markdown('<div class="nad-card">', unsafe_allow_html=True)
        dc1, dc2 = st.columns([3, 1])
        with dc1:
            st.markdown('<p class="nad-card-title">Terminal Contribution</p>', unsafe_allow_html=True)
        with dc2:
            st.selectbox("", ["This Week","This Month"],
                         key="sel_donut", label_visibility="collapsed")

        df_donut = df.groupby("terminal")["kontribusi"].sum().reset_index()
        fig_d = px.pie(
            df_donut, names="terminal", values="kontribusi",
            hole=0.55, color_discrete_sequence=["#202124","#dadce0"]
        )
        fig_d.update_layout(
            height=230, margin=dict(t=0, b=10, l=0, r=0), showlegend=True,
            legend=dict(orientation="v", x=0.85, y=0.5, font=dict(size=11, color="#5f6368")),
            paper_bgcolor="#fff"
        )
        fig_d.update_traces(textinfo="percent", textfont_size=11, textfont_color="#fff")
        st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_insight:
        st.markdown('<div class="nad-card" style="height:285px;">', unsafe_allow_html=True)
        st.markdown('<p class="nad-card-title">💡 Insight</p>', unsafe_allow_html=True)
        df_t    = df.groupby("terminal")["kontribusi"].sum()
        top_t   = df_t.idxmax() if len(df_t) > 0 else "Terminal 2"
        top_pct = int(df_t.max() / df_t.sum() * 100) if df_t.sum() > 0 else 50
        df_p    = df.groupby("perusahaan")["kontribusi"].sum().nlargest(3)
        t3_pct  = int(df_p.sum() / df["kontribusi"].sum() * 100) if df["kontribusi"].sum() > 0 else 40
        for ins in [
            f"🔦 {top_t} menghasilkan {top_pct}% total revenue",
            f"🔦 3 Tenant menghasilkan {t3_pct}% kontribusi pendapatan",
        ]:
            st.markdown(f"""
            <div style="background:#f8f9fa;border-radius:8px;padding:12px 14px;
                        margin-bottom:10px;font-size:12px;color:#5f6368;line-height:1.6;">
                {ins}</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Row 3: Revenue/Sqm + Best 3
    col_rev, col_best = st.columns([1, 1])

    with col_rev:
        st.markdown('<div class="nad-card">', unsafe_allow_html=True)
        rh1, rh2 = st.columns([3, 1])
        with rh1:
            st.markdown('<p class="nad-card-title">Revenue Per Sqm</p>', unsafe_allow_html=True)
        with rh2:
            st.markdown(
                "<p style='font-size:12px;color:#1a73e8;text-align:right;margin:2px 0;'>View All ▾</p>",
                unsafe_allow_html=True
            )
        df_rev = df.groupby(["perusahaan","brand","kode_ruang"]).agg(
            rev=("rev_sqm","mean")).reset_index().head(5)
        df_rev["rev"] = df_rev["rev"].apply(lambda x: f"Rp{x:,.0f}")
        df_rev.columns = ["Tenant","Brand","Kode Ruang","Rev/Sqm"]
        st.dataframe(df_rev, use_container_width=True, hide_index=True, height=160)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_best:
        st.markdown('<div class="nad-card">', unsafe_allow_html=True)
        bh1, bh2 = st.columns([3, 1])
        with bh1:
            st.markdown('<p class="nad-card-title">Best 3 Achievement</p>', unsafe_allow_html=True)
        with bh2:
            st.markdown(
                "<p style='font-size:12px;color:#1a73e8;text-align:right;margin:2px 0;'>View All ▾</p>",
                unsafe_allow_html=True
            )
        df_best = df.groupby(["perusahaan","brand"]).agg(
            r=("real_omzet","sum"), m=("min_omzet","sum")).reset_index()
        df_best["Rev/Sqm"] = (df_best["r"] / df_best["m"] * 100).apply(lambda x: f"Rp{x:,.0f}")
        df_best = df_best.nlargest(3, "r")[["perusahaan","brand","Rev/Sqm"]]
        df_best.columns = ["Tenant","Brand","Rev/Sqm"]
        st.dataframe(df_best, use_container_width=True, hide_index=True, height=160)
        st.markdown('</div>', unsafe_allow_html=True)

    # Row 4: Tabel Detail Lengkap
    st.markdown('<div class="nad-card">', unsafe_allow_html=True)
    th1, th2 = st.columns([3, 1])
    with th1:
        st.markdown('<p class="nad-card-title">Revenue Per Sqm</p>', unsafe_allow_html=True)
        st.markdown('<p class="nad-card-sub">Data lengkap seluruh tenant</p>', unsafe_allow_html=True)
    with th2:
        st.markdown(
            "<p style='font-size:12px;color:#1a73e8;text-align:right;margin:4px 0;'>View All ▾</p>",
            unsafe_allow_html=True
        )
    df_det = df[["perusahaan","brand","kode_ruang","min_omzet","real_omzet","kontribusi"]].copy()
    df_det["min_omzet"]  = df_det["min_omzet"].apply(lambda x: f"Rp {x:,.0f}")
    df_det["real_omzet"] = df_det["real_omzet"].apply(lambda x: f"Rp {x:,.0f}")
    df_det["kontribusi"] = df_det["kontribusi"].apply(lambda x: f"Rp {x:,.0f}")
    df_det.columns = ["Tenant","Brand","Kode Ruang","Min Omzet","Target Omzet","Real Omzet"]
    st.dataframe(df_det, use_container_width=True, hide_index=True, height=260)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE: IMPORT MANAGER
# ══════════════════════════════════════════════
def page_import():
    show_topnav("Import Manager")
    st.markdown('<div class="nad-card">', unsafe_allow_html=True)
    st.markdown('<p class="nad-card-title">📤 Upload File Excel</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="nad-card-sub">Import data pendapatan tenant dari file .xlsx ke PostgreSQL</p>',
        unsafe_allow_html=True
    )
    uploaded = st.file_uploader("Pilih file .xlsx", type=["xlsx","xls"])
    if uploaded:
        try:
            df_up = pd.read_excel(uploaded)
            st.success(f"✅ {len(df_up)} baris berhasil dibaca")
            st.dataframe(df_up.head(10), use_container_width=True)
            if st.button("💾 Simpan ke Database", type="primary"):
                try:
                    df_up.to_sql("pendapatan_tenant", get_engine(), if_exists="append", index=False)
                    st.success("✅ Data berhasil disimpan!")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"❌ Gagal simpan: {e}")
        except Exception as e:
            st.error(f"❌ Gagal baca file: {e}")
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE: COMING SOON
# ══════════════════════════════════════════════
def page_coming_soon(name):
    show_topnav(name)
    st.markdown(f"""
    <div class="nad-card" style="text-align:center;padding:80px 40px;margin-top:20px;">
        <div style="font-size:52px;margin-bottom:16px;">🚧</div>
        <div style="font-size:18px;font-weight:700;color:#202124;margin-bottom:8px;">Coming Soon</div>
        <div style="font-size:13px;color:#9aa0a6;">
            Halaman <b>{name}</b> sedang dalam pengembangan</div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# MAIN — langsung tampilkan dashboard
# ══════════════════════════════════════════════
df_raw = load_data()
show_sidebar()

st.markdown("<div style='padding:20px 28px 40px 28px;'>", unsafe_allow_html=True)
menu = st.session_state.active_menu
if   menu == "Revenue Sharing": page_revenue_sharing(df_raw)
elif menu == "Import Manager":  page_import()
elif menu in ["Accrual & Billing","Room Database","Lease Contract",
              "Data Verification","Traffic Monitor","Overview"]:
    page_coming_soon(menu)
else:
    page_revenue_sharing(df_raw)
st.markdown("</div>", unsafe_allow_html=True)