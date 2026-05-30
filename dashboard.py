from accrual_billing import page_accrual_billing
from revenue_sharing import page_revenue_sharing
from room_database import render_room_database
from lease_contract import render_lease_contract
from import_manager import render_import_manager
from shared_import import get_shared_import_data, has_dashboard_ready_import, import_status_html
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
# LOAD CSS
# ─────────────────────────────────────────────
def load_css(filepath: str):
    with open(filepath, "r", encoding="utf-8") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css("style.css")


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
if "started" not in st.query_params:
    st.session_state["active_menu"] = "Overview"
    st.session_state["user_name"]   = "Administrator"
    st.session_state["user_role"]   = "Admin"
    st.session_state["user_email"]  = "admin@injourneyairports.com"
    st.query_params["started"] = "1"

defaults = {
    "user_name":   "Administrator",
    "user_role":   "Admin",
    "user_email":  "admin@injourneyairports.com",
    "active_menu": "Overview",
    "sidebar_minimized": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

st.markdown(
    f'<div class="ap-sidebar-state {"is-mini" if st.session_state.sidebar_minimized else "is-expanded"}"></div>',
    unsafe_allow_html=True
)


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
    except Exception:
        return generate_dummy_data()

def get_active_dashboard_data():
    imported_df = get_shared_import_data()
    if imported_df is not None and has_dashboard_ready_import():
        return imported_df
    return load_data()

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

KPI_GRADIENTS = [
    ("linear-gradient(135deg,#4f46e5,#6366f1)", "rgba(99,102,241,0.12)"),
    ("linear-gradient(135deg,#0891b2,#06b6d4)", "rgba(6,182,212,0.12)"),
    ("linear-gradient(135deg,#059669,#10b981)", "rgba(16,185,129,0.12)"),
    ("linear-gradient(135deg,#e11d48,#f43f5e)", "rgba(244,63,94,0.10)"),
    ("linear-gradient(135deg,#7c3aed,#8b5cf6)", "rgba(139,92,246,0.12)"),
    ("linear-gradient(135deg,#d97706,#f59e0b)", "rgba(245,158,11,0.12)"),
    ("linear-gradient(135deg,#db2777,#ec4899)", "rgba(236,72,153,0.10)"),
]


# ══════════════════════════════════════════════
# HELPER: Render satu KPI card (HTML)
# ══════════════════════════════════════════════
def _kpi_html(label, value, delta, delta_up, idx):
    grad, orb = KPI_GRADIENTS[idx % len(KPI_GRADIENTS)]
    delta_col = "#059669" if delta_up else "#e11d48"
    arrow     = "↑" if delta_up else "↓"
    return f"""
    <div style="
        background:rgba(255,255,255,0.62);
        backdrop-filter:blur(22px);
        -webkit-backdrop-filter:blur(22px);
        border:1px solid rgba(255,255,255,0.94);
        border-radius:18px;
        padding:16px 15px 14px;
        position:relative;overflow:hidden;
        box-shadow:0 6px 24px rgba(99,102,241,0.08),inset 0 1px 0 rgba(255,255,255,1);
        transition:transform .2s,box-shadow .2s;
    ">
        <div style="position:absolute;top:-20px;right:-20px;width:64px;height:64px;
                    border-radius:50%;
                    background:radial-gradient(circle,{orb},transparent 70%);"></div>
        <div style="font-size:9.5px;font-weight:700;color:#94a3b8;
                    text-transform:uppercase;letter-spacing:0.6px;margin-bottom:7px;">
            {label}</div>
        <div style="font-size:17px;font-weight:800;
                    background:{grad};
                    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                    background-clip:text;line-height:1.2;margin-bottom:6px;">
            {value}</div>
        <div style="font-size:10px;font-weight:600;color:{delta_col};">
            {arrow} {delta}</div>
    </div>"""


# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
NAV_ICONS = {
    "Overview": "📊",
    "Revenue Sharing": "💰",
    "Accrual & Billing": "🧾",
    "Room Database": "🏢",
    "Lease Contract": "📄",
    "Import Manager": "📤",
    "Data Verification": "✓",
    "Traffic Monitor": "📈",
}


def _toggle_sidebar():
    st.session_state.sidebar_minimized = not st.session_state.sidebar_minimized


def _go_to_menu(menu_name):
    st.session_state.active_menu = menu_name


_SIDEBAR_MENU_BUTTONS = {
    "tb_sidebar_home_mini": "Overview",
    "tb_sidebar_import_mini": "Import Manager",
    "tb_sidebar_home": "Overview",
    "tb_sidebar_import": "Import Manager",
}
_SIDEBAR_TOGGLE_BUTTONS = {"tb_sidebar_expand", "tb_sidebar_collapse"}

if not hasattr(st, "_ap_original_button"):
    st._ap_original_button = st.button


def _ap_button(*args, **kwargs):
    key = kwargs.get("key")

    if key in _SIDEBAR_TOGGLE_BUTTONS:
        kwargs.setdefault("on_click", _toggle_sidebar)
        st._ap_original_button(*args, **kwargs)
        return False

    if key in _SIDEBAR_MENU_BUTTONS:
        kwargs.setdefault("on_click", _go_to_menu)
        kwargs.setdefault("args", (_SIDEBAR_MENU_BUTTONS[key],))
        st._ap_original_button(*args, **kwargs)
        return False

    if isinstance(key, str) and key.startswith("nav_"):
        kwargs.setdefault("on_click", _go_to_menu)
        kwargs.setdefault("args", (key.removeprefix("nav_"),))
        st._ap_original_button(*args, **kwargs)
        return False

    return st._ap_original_button(*args, **kwargs)


st.button = _ap_button


def _sidebar_brand():
    if st.session_state.sidebar_minimized:
        st.markdown("""
        <div class="ap-brand ap-brand-mini">
            <div class="ap-logo">IA</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown("""
    <div class="ap-brand">
        <div style="display:flex;align-items:center;gap:10px;">
            <div class="ap-logo">IA</div>
            <div class="ap-brand-copy">
                <div class="ap-brand-name">INJOURNEY AIRPORTS</div>
                <div class="ap-brand-sub">NON AERO SYSTEM</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


def _sidebar_toolbar():
    mini = st.session_state.sidebar_minimized
    if mini:
        if st.button("›", key="tb_sidebar_expand", help="Perbesar sidebar", use_container_width=True):
            _toggle_sidebar()
        if st.button("⌂", key="tb_sidebar_home_mini", help="Overview", use_container_width=True):
            _go_to_menu("Overview")
        if st.button("⇧", key="tb_sidebar_import_mini", help="Import Manager", use_container_width=True):
            _go_to_menu("Import Manager")
        return

    st.markdown('<div class="ap-toolbar-title">TOOLBAR</div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("‹", key="tb_sidebar_collapse", help="Minimize sidebar", use_container_width=True):
            _toggle_sidebar()
    with c2:
        if st.button("⌂", key="tb_sidebar_home", help="Overview", use_container_width=True):
            _go_to_menu("Overview")
    with c3:
        if st.button("⇧", key="tb_sidebar_import", help="Import Manager", use_container_width=True):
            _go_to_menu("Import Manager")


def _nav_group(label):
    if st.session_state.sidebar_minimized:
        st.markdown('<div class="nav-group-mini"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="nav-group">{label}</div>', unsafe_allow_html=True)


def _sidebar_user():
    initial = st.session_state.user_name[0].upper() if st.session_state.user_name else "U"
    if st.session_state.sidebar_minimized:
        st.markdown(f"""
        <div class="ap-user ap-user-mini" title="{st.session_state.user_name}">
            <div class="ap-avatar">{initial}</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="ap-user">
        <div class="ap-avatar">{initial}</div>
        <div style="flex:1;min-width:0;">
            <div style="font-size:12px;font-weight:700;color:#1e293b;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
                {st.session_state.user_name}</div>
            <div style="font-size:10px;color:#94a3b8;">{st.session_state.user_role}</div>
        </div>
    </div>""", unsafe_allow_html=True)


def show_sidebar():
    with st.sidebar:

        _sidebar_brand()
        _sidebar_toolbar()

        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        _nav_item(NAV_ICONS["Overview"], "Overview")

        _nav_group("FINANCIAL")
        _nav_sub(NAV_ICONS["Revenue Sharing"], "Revenue Sharing")
        _nav_sub(NAV_ICONS["Accrual & Billing"], "Accrual & Billing")

        _nav_group("SPACE MGMT")
        _nav_sub(NAV_ICONS["Room Database"], "Room Database")
        _nav_sub(NAV_ICONS["Lease Contract"], "Lease Contract")

        _nav_group("DATA CENTER")
        _nav_sub(NAV_ICONS["Import Manager"], "Import Manager")
        _nav_sub(NAV_ICONS["Data Verification"], "Data Verification")

        _nav_group("MONITOR")
        _nav_item(NAV_ICONS["Traffic Monitor"], "Traffic Monitor")

        st.markdown("<br>" * 4, unsafe_allow_html=True)
        st.markdown("<hr>", unsafe_allow_html=True)

        _sidebar_user()


def _nav_item(icon, label):
    mini = st.session_state.sidebar_minimized
    is_active = st.session_state.active_menu == label
    if is_active:
        st.markdown(f"""
        <div class="nav-active" title="{label}">
            <span class="nav-icon">{icon}</span>
            <span class="nav-label">{'' if mini else label}</span>
        </div>""", unsafe_allow_html=True)
    else:
        button_label = icon if mini else f"{icon}  {label}"
        if st.button(button_label, key=f"nav_{label}", help=label if mini else None, use_container_width=True):
            _go_to_menu(label)


def _nav_sub(icon, label):
    mini = st.session_state.sidebar_minimized
    is_active = st.session_state.active_menu == label
    if is_active:
        st.markdown(f"""
        <div class="nav-active" title="{label}">
            <span class="nav-icon">{icon}</span>
            <span class="nav-label">{'' if mini else label}</span>
        </div>""", unsafe_allow_html=True)
    else:
        button_label = icon if mini else f"{icon}  {label}"
        if st.button(button_label, key=f"nav_{label}", help=label if mini else None, use_container_width=True):
            _go_to_menu(label)


# ══════════════════════════════════════════════
# TOP NAVBAR
# ══════════════════════════════════════════════
def show_topnav(title="Non Aeronautical Dashboard", show_search=True):
    if show_search:
        n1, n2, n3 = st.columns([3, 4, 3])
    else:
        n1, n3 = st.columns([4, 6])
        n2 = None
    with n1:
        st.markdown(
            f'<h2 style="margin:0;font-size:19px;font-weight:800;color:#0f172a;'
            f'padding-top:6px;">{title}</h2>',
            unsafe_allow_html=True
        )
    if show_search:
        with n2:
            st.text_input("search", placeholder="🔍  Searching anything...",
                          label_visibility="collapsed", key="search_bar")
    with n3:
        initial = st.session_state.user_name[0].upper() if st.session_state.user_name else "U"
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:flex-end;
                    gap:12px;padding-top:4px;">
            <div style="width:34px;height:34px;border-radius:50%;
                        background:rgba(255,255,255,0.72);
                        border:1px solid rgba(255,255,255,0.95);
                        backdrop-filter:blur(10px);
                        display:flex;align-items:center;justify-content:center;
                        font-size:16px;box-shadow:0 2px 8px rgba(99,102,241,0.08);">🔔</div>
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="background:linear-gradient(135deg,#6366f1,#ec4899);
                            border-radius:50%;width:34px;height:34px;
                            display:flex;align-items:center;justify-content:center;
                            color:#fff;font-size:13px;font-weight:700;
                            box-shadow:0 3px 12px rgba(99,102,241,0.35);">{initial}</div>
                <div>
                    <div style="font-size:12px;font-weight:700;color:#1e293b;">
                        {st.session_state.user_name}</div>
                    <div style="font-size:10px;color:#94a3b8;">
                        {st.session_state.user_email}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
    st.markdown('<div class="nad-top-divider"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════
def page_overview(df_raw):
    show_topnav("Overview", show_search=False)

    fb1, fb2, fb3, _, fe1, fe2 = st.columns([2, 2, 2, 2, 1, 1])
    with fb1:
        sel_terminal = st.selectbox(
            "", ["All Terminal"] + sorted(df_raw["terminal"].unique().tolist()),
            key="f_terminal")
    with fb2:
        sel_tahun = st.selectbox(
            "", ["Semua Tahun"] + sorted(df_raw["tahun"].unique().tolist(), reverse=True),
            key="f_tahun")
    with fb3:
        sel_masa = st.selectbox("", ["Semua Bulan"] + BULAN, key="f_masa")
    with fe1:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.button("⇅ Share", key="btn_share", use_container_width=True)
    with fe2:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.button("↑ Export", key="btn_export", use_container_width=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    df = df_raw.copy()
    if sel_terminal != "All Terminal": df = df[df["terminal"]  == sel_terminal]
    if sel_tahun    != "Semua Tahun":  df = df[df["tahun"]     == int(sel_tahun)]
    if sel_masa     != "Semua Bulan":  df = df[df["masa_jasa"] == sel_masa]

    kpi_data = [
        ("Real Omzet",       fmt_rp(df["real_omzet"].sum()),      "5.2% vs last month",  True),
        ("Min Omzet",        fmt_rp(df["min_omzet"].sum()),       "3.1% growth",          True),
        ("Pendapatan Sewa",  fmt_rp(df["pendapatan_sewa"].sum()), "4.2% this month",      True),
        ("Pendapatan RS",    fmt_rp(df["pendapatan_rs"].sum()),   "1.2% decline",         False),
        ("Total Kontribusi", fmt_rp(df["kontribusi"].sum()),      "4.2% this month",      True),
        ("Revenue / Sqm",    fmt_rp(df["rev_sqm"].mean()),        "2.8% increase",        True),
        ("ACV",              f"{df['acv'].mean():.2f}%",          "8.4% improvement",     True),
    ]
    cols_kpi = st.columns(7)
    for i, (label, val, delta, up) in enumerate(kpi_data):
        with cols_kpi[i]:
            st.markdown(_kpi_html(label, val, delta, up, i), unsafe_allow_html=True)

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    col_line, col_donut, col_insight = st.columns([4, 3, 3])

    with col_line:
        st.markdown('<div class="nad-card">', unsafe_allow_html=True)
        rc1, rc2 = st.columns([3, 1])
        with rc1:
            st.markdown('<p class="nad-card-title">Pendapatan 2026</p>', unsafe_allow_html=True)
        with rc2:
            st.selectbox("", ["This Year", "This Month", "This Week"],
                         key="sel_line", label_visibility="collapsed")

        st.markdown("""
        <div style="display:flex;gap:18px;margin-bottom:8px;">
            <span style="display:flex;align-items:center;gap:5px;font-size:10.5px;color:#64748b;font-weight:500;">
                <span style="width:22px;height:3px;background:#6366f1;display:inline-block;border-radius:2px;"></span>Pendapatan Sewa
            </span>
            <span style="display:flex;align-items:center;gap:5px;font-size:10.5px;color:#64748b;font-weight:500;">
                <span style="width:22px;height:3px;background:#06b6d4;display:inline-block;border-radius:2px;"></span>Pendapatan RS
            </span>
            <span style="display:flex;align-items:center;gap:5px;font-size:10.5px;color:#64748b;font-weight:500;">
                <span style="width:22px;height:3px;background:#f59e0b;display:inline-block;border-radius:2px;"></span>Others
            </span>
        </div>""", unsafe_allow_html=True)

        df_line = df.groupby("masa_jasa").agg(
            pend_sewa=("pendapatan_sewa", "sum"),
            pend_rs=("pendapatan_rs", "sum"),
            others=("kontribusi", "sum")
        ).reset_index()
        df_line["masa_jasa"] = pd.Categorical(df_line["masa_jasa"], categories=BULAN, ordered=True)
        df_line = df_line.sort_values("masa_jasa")
        df_line["short"] = df_line["masa_jasa"].astype(str).str[:3]

        chart_data = [
            ("pend_sewa", "#6366f1", "rgba(99,102,241,0.09)"),
            ("pend_rs",   "#06b6d4", "rgba(6,182,212,0.08)"),
            ("others",    "#f59e0b", "rgba(245,158,11,0.07)"),
        ]
        fig = go.Figure()
        for col_key, color, fill in chart_data:
            fig.add_trace(go.Scatter(
                x=df_line["short"], y=df_line[col_key],
                mode="lines+markers",
                line=dict(color=color, width=2.5),
                marker=dict(size=5, color="#fff", line=dict(color=color, width=2)),
                fill="tozeroy", fillcolor=fill, showlegend=False,
            ))
        fig.update_layout(
            height=225, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=4, b=0, l=0, r=0),
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#94a3b8"), showline=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(99,102,241,0.07)",
                       tickfont=dict(size=10, color="#94a3b8"), showline=False),
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_donut:
        st.markdown('<div class="nad-card">', unsafe_allow_html=True)
        dc1, dc2 = st.columns([3, 1])
        with dc1:
            st.markdown('<p class="nad-card-title">Terminal Contribution</p>', unsafe_allow_html=True)
        with dc2:
            st.selectbox("", ["This Month", "This Week"], key="sel_donut", label_visibility="collapsed")

        df_donut = df.groupby("terminal")["kontribusi"].sum().reset_index()
        colors_donut = ["#06b6d4", "#f97316", "#6366f1", "#10b981", "#f59e0b"]

        fig_d = go.Figure(go.Pie(
            labels=df_donut["terminal"], values=df_donut["kontribusi"],
            hole=0.65,
            marker=dict(colors=colors_donut[:len(df_donut)],
                        line=dict(color="rgba(255,255,255,0.95)", width=5)),
            textinfo="percent", textfont=dict(size=11, color="#fff"),
        ))
        fig_d.update_layout(
            height=210, margin=dict(t=0, b=0, l=0, r=80),
            paper_bgcolor="rgba(0,0,0,0)", showlegend=True,
            legend=dict(orientation="v", x=0.80, y=0.5,
                        font=dict(size=11, color="#64748b"), bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_d, use_container_width=True, config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    with col_insight:
        df_t    = df.groupby("terminal")["kontribusi"].sum()
        top_t   = df_t.idxmax() if len(df_t) > 0 else "Terminal 2"
        top_pct = int(df_t.max() / df_t.sum() * 100) if df_t.sum() > 0 else 50
        df_p    = df.groupby("perusahaan")["kontribusi"].sum().nlargest(3)
        t3_pct  = int(df_p.sum() / df["kontribusi"].sum() * 100) if df["kontribusi"].sum() > 0 else 40
        top_sec = df.groupby("bidang_usaha")["acv"].mean().idxmax() if len(df) > 0 else "Food & Beverage"

        st.markdown(f"""
        <div class="nad-card" style="min-height:295px;">
            <p class="nad-card-title">💡 Insight</p>
            <div class="insight-box">
                <strong style="color:#4f46e5;">{top_t}</strong> menghasilkan
                <strong style="color:#4f46e5;">{top_pct}%</strong>
                total kontribusi pendapatan periode ini.
            </div>
            <div class="insight-box">
                3 tenant teratas menyumbang
                <strong style="color:#0891b2;">{t3_pct}%</strong>
                dari seluruh pendapatan bulan ini.
            </div>
            <div class="insight-box">
                <strong style="color:#059669;">{top_sec}</strong>
                memimpin kategori dengan rata‑rata ACV tertinggi.
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    col_rev, col_best = st.columns([1, 1])

    with col_rev:
        st.markdown('<div class="nad-card">', unsafe_allow_html=True)
        rh1, rh2 = st.columns([3, 1])
        with rh1:
            st.markdown('<p class="nad-card-title">Revenue Per Sqm</p>', unsafe_allow_html=True)
        with rh2:
            st.markdown("<p style='font-size:11px;color:#6366f1;text-align:right;margin:2px 0;font-weight:600;cursor:pointer;'>View All ▾</p>", unsafe_allow_html=True)

        df_rev = (
            df.groupby(["perusahaan", "brand", "kode_ruang"])
              .agg(rev=("rev_sqm", "mean")).reset_index().head(5)
        )
        df_rev["rev"] = df_rev["rev"].apply(lambda x: f"Rp {x:,.0f}")
        df_rev.columns = ["Tenant", "Brand", "Kode Ruang", "Rev/Sqm"]
        st.dataframe(df_rev, use_container_width=True, hide_index=True, height=175)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_best:
        st.markdown('<div class="nad-card">', unsafe_allow_html=True)
        bh1, bh2 = st.columns([3, 1])
        with bh1:
            st.markdown('<p class="nad-card-title">Best 3 Achievement</p>', unsafe_allow_html=True)
        with bh2:
            st.markdown("<p style='font-size:11px;color:#6366f1;text-align:right;margin:2px 0;font-weight:600;cursor:pointer;'>View All ▾</p>", unsafe_allow_html=True)

        df_best = (
            df.groupby(["perusahaan", "brand"])
              .agg(r=("real_omzet", "sum"), m=("min_omzet", "sum")).reset_index()
        )
        df_best["ACV %"] = (df_best["r"] / df_best["m"] * 100).round(1).astype(str) + "%"
        df_best = df_best.nlargest(3, "r")[["perusahaan", "brand", "ACV %"]]
        df_best.columns = ["Tenant", "Brand", "ACV %"]
        st.dataframe(df_best, use_container_width=True, hide_index=True, height=175)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="nad-card">', unsafe_allow_html=True)
    th1, th2 = st.columns([3, 1])
    with th1:
        st.markdown('<p class="nad-card-title">Detail Revenue Tenant</p>', unsafe_allow_html=True)
        st.markdown('<p class="nad-card-sub">Data lengkap seluruh tenant aktif</p>', unsafe_allow_html=True)
    with th2:
        st.markdown("<p style='font-size:11px;color:#6366f1;text-align:right;margin:4px 0;font-weight:600;cursor:pointer;'>View All ▾</p>", unsafe_allow_html=True)

    df_det = df[["perusahaan", "brand", "kode_ruang", "min_omzet", "real_omzet", "kontribusi"]].copy()
    df_det["min_omzet"]  = df_det["min_omzet"].apply(lambda x: f"Rp {x:,.0f}")
    df_det["real_omzet"] = df_det["real_omzet"].apply(lambda x: f"Rp {x:,.0f}")
    df_det["kontribusi"] = df_det["kontribusi"].apply(lambda x: f"Rp {x:,.0f}")
    df_det.columns = ["Tenant", "Brand", "Kode Ruang", "Min Omzet", "Target Omzet", "Real Omzet"]
    st.dataframe(df_det, use_container_width=True, hide_index=True, height=270)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE: IMPORT MANAGER
# ══════════════════════════════════════════════
def page_import():
    show_topnav("Import Manager")
    st.markdown('<div class="nad-card">', unsafe_allow_html=True)
    st.markdown('<p class="nad-card-title">Central Import Source</p>', unsafe_allow_html=True)
    st.markdown('<p class="nad-card-sub">Upload data dipusatkan di halaman Import Manager.</p>', unsafe_allow_html=True)
    uploaded = None
    st.markdown(
        import_status_html("nad-card", "nad-card-title", "nad-card-sub"),
        unsafe_allow_html=True,
    )
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
        <div style="font-size:18px;font-weight:700;color:#1e293b;margin-bottom:8px;">
            Coming Soon</div>
        <div style="font-size:13px;color:#94a3b8;">
            Halaman <b>{name}</b> sedang dalam pengembangan</div>
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# MAIN — ROUTING
# ══════════════════════════════════════════════
df_raw = get_active_dashboard_data()
show_sidebar()

menu = st.session_state.active_menu

if   menu == "Overview":          page_overview(df_raw)
elif menu == "Revenue Sharing":   page_revenue_sharing()
elif menu == "Accrual & Billing": page_accrual_billing()
elif menu == "Import Manager":    render_import_manager()
elif menu == "Room Database":     render_room_database()          # ← AKTIF
elif menu == "Lease Contract":    render_lease_contract()
elif menu in ["Data Verification", "Traffic Monitor"]:
    page_coming_soon(menu)
else:
    page_overview(df_raw)
