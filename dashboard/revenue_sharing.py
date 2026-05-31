import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, date
from .shared_import import import_status_html

# ─────────────────────────────────────────────
# DUMMY DATA
# ─────────────────────────────────────────────
def get_services_data():
    return pd.DataFrame({
        "Service/SBU":      ["Ground Handling","PSC","VIP Services","Commercial Area","Cargo Area","Parking Area","Ground Handling Services"],
        "Gross Revenue":    ["Rp 12.1B","Rp 6.4B","Rp 4.2B","Rp 3.9B","Rp 12.1B","Rp 12.1B","Rp 12.1B"],
        "SBU Share Rule %": ["70%","100%","65%","50%","70%","70%","70%"],
        "Management Share": ["Rp 8.47B","Rp 6.4B","Rp 2.73B","Rp 1.95B","Rp 8.47B","Rp 8.47B","Rp 8.47B"],
        "Status":           ["SUCCESS","SUCCESS","CONFLICT","CONFLICT","FAILED","FAILED","FAILED"]
    })

def get_transaction_data():
    return pd.DataFrame({
        "Transaction ID": ["7007001001"]*7,
        "Revenue/SBU":    ["Ground Handling"]*7,
        "Type":           ["Revenue"]*7,
        "Date":           ["12 Jun 2026"]*7,
        "Amount":         ["Rp 12.1B"]*7,
        "Status":         ["SUCCESS"]*7
    })

def get_terminal_files():
    return pd.DataFrame({
        "File Name":  ["Prod_Jun_Terminal1.xlsx","Prod_Jun_Terminal2.xlsx"],
        "Tenant/SBU": ["Terminal 1","Terminal 2"],
        "Date":       ["12 Jun 2026","17 Jun 2026"],
        "Status":     ["SUCCESS","FAILED"]
    })

def get_trend_data():
    return pd.DataFrame({
        "Bulan":           ["Jan","Feb","Mar","Apr","Mei","Jun"],
        "Ground Handling": [0.9,1.0,0.95,1.1,1.05,1.2],
        "PSC":             [0.7,0.8,0.75,0.85,0.9,0.95],
        "Others":          [0.5,0.6,0.55,0.65,0.7,0.8],
    })

def fmt_status_badge(status):
    colors = {
        "SUCCESS":  ("rgba(16,185,129,0.12)", "#059669", "rgba(16,185,129,0.24)"),
        "FAILED":   ("rgba(244,63,94,0.11)", "#e11d48", "rgba(244,63,94,0.22)"),
        "CONFLICT": ("rgba(245,158,11,0.13)", "#d97706", "rgba(245,158,11,0.24)"),
    }
    bg, fg, border = colors.get(status, ("rgba(148,163,184,0.12)", "#64748b", "rgba(148,163,184,0.22)"))
    return (f'<span style="background:{bg};color:{fg};padding:3px 10px;'
            f'border:1px solid {border};border-radius:999px;font-size:11px;'
            f'font-weight:700;letter-spacing:0.2px;">{status}</span>')


# ══════════════════════════════════════════════
# PAGE: REVENUE SHARING
# ══════════════════════════════════════════════
def page_revenue_sharing():

    st.markdown("""
    <style>
    .rs-card {
        background: rgba(255, 255, 255, 0.56); border-radius:10px; padding:18px 20px;
        box-shadow:0 1px 3px rgba(0,0,0,0.06);
        border:1px solid #e8eaed; margin-bottom:14px;
    }
    .rs-card-title  { font-size:13px; font-weight:600; color:#5f6368; margin:0 0 6px 0; }
    .rs-card-value  { font-size:26px; font-weight:800; color:#202124; margin:0 0 4px 0; }
    .rs-card-sub    { font-size:11px; color:#9aa0a6; margin:0; }
    .rs-delta-up    { font-size:12px; color:#1e7e34; font-weight:600; }
    .rs-section-title { font-size:15px; font-weight:700; color:#202124; margin:0 0 4px 0; }
    .rs-section-sub   { font-size:11px; color:#9aa0a6; margin:0 0 14px 0; }

    /* ── FIX: teks file uploader wajib hitam ── */
    [data-testid="stFileUploader"] * {
        color: #202124 !important;
    }
    [data-testid="stFileUploader"] section {
        border: 2px dashed #9ca3af !important;
        border-radius: 10px !important;
        background: #f8f9fa !important;
        padding: 20px !important;
    }
    [data-testid="stFileUploader"] section span,
    [data-testid="stFileUploader"] section p,
    [data-testid="stFileUploader"] section small,
    [data-testid="stFileUploader"] section div {
        color: #202124 !important;
        opacity: 1 !important;
    }
    [data-testid="stFileUploader"] section svg {
        fill: #202124 !important;
        color: #202124 !important;
        opacity: 1 !important;
    }
    [data-testid="stFileUploadDropzone"] span { color: #202124 !important; opacity:1 !important; }
    [data-testid="stFileUploadDropzone"] small { color: #5f6368 !important; opacity:1 !important; }
    [data-testid="stFileUploadDropzone"] p { color: #202124 !important; opacity:1 !important; }

    .tbl-header {
        display:grid; grid-template-columns:2fr 1fr 1fr 1fr;
        font-size:12px; font-weight:600; color:#5f6368;
        padding:8px 4px; border-bottom:1px solid #e8eaed; margin-bottom:4px;
    }
    .tbl-row {
        display:grid; grid-template-columns:2fr 1fr 1fr 1fr;
        font-size:12px; color:#202124;
        padding:8px 4px; border-bottom:1px solid #f1f3f4; align-items:center;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .rs-card {
        background: rgba(255, 255, 255, 0.56) !important;
        backdrop-filter: blur(26px);
        -webkit-backdrop-filter: blur(26px);
        border-radius: 20px !important;
        padding: 20px 22px !important;
        border: 1px solid rgba(255,255,255,0.90) !important;
        box-shadow:
            0 8px 32px rgba(99,102,241,0.07),
            0 2px 8px rgba(15,23,42,0.025),
            inset 0 1px 0 rgba(255,255,255,1) !important;
        margin-bottom: 14px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .rs-card:hover {
        transform: translateY(-1px);
        box-shadow:
            0 14px 42px rgba(99,102,241,0.11),
            0 2px 8px rgba(15,23,42,0.03),
            inset 0 1px 0 rgba(255,255,255,1) !important;
    }
    .rs-kpi-card {
        min-height: 126px;
        overflow: hidden;
        position: relative;
    }
    .rs-kpi-card::before {
        content: "";
        position: absolute;
        left: 16px;
        right: 16px;
        top: 0;
        height: 3px;
        border-radius: 0 0 999px 999px;
        background: var(--accent, linear-gradient(135deg,#6366f1,#06b6d4));
        opacity: 0.9;
    }
    .rs-card-title {
        font-size: 9.5px !important;
        font-weight: 800 !important;
        color: #94a3b8 !important;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        margin: 3px 0 8px 0 !important;
    }
    .rs-card-value {
        font-size: 23px !important;
        line-height: 1.15;
        font-weight: 850 !important;
        margin: 0 0 7px 0 !important;
        background: var(--accent, linear-gradient(135deg,#4f46e5,#0891b2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .rs-card-sub {
        font-size: 10.5px !important;
        color: #64748b !important;
        font-weight: 600;
        margin: 0 !important;
    }
    .rs-delta-up {
        font-size: 10.5px !important;
        color: #059669 !important;
        font-weight: 700 !important;
    }
    .rs-section-title {
        font-size: 13px !important;
        font-weight: 800 !important;
        color: #1e293b !important;
        margin: 0 0 3px 0 !important;
    }
    .rs-section-sub {
        font-size: 11px !important;
        color: #94a3b8 !important;
        margin: 0 0 14px 0 !important;
    }
    .rs-top-divider {
        position: relative;
        height: 2px;
        margin: 18px 0 18px;
        border-radius: 999px;
        background: linear-gradient(90deg, rgba(99,102,241,0), rgba(99,102,241,0.50), rgba(6,182,212,0.58), rgba(16,185,129,0.52), rgba(16,185,129,0));
        box-shadow: 0 8px 24px rgba(6,182,212,0.14);
    }
    .rs-progress-ring {
        width: 74px;
        height: 74px;
        border-radius: 50%;
        background: conic-gradient(#6366f1 0 92%, rgba(99,102,241,0.14) 92% 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: inset 0 0 0 1px rgba(255,255,255,0.85);
        margin: 0;
        flex: 0 0 auto;
    }
    .rs-progress-ring span {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: rgba(255,255,255,0.82);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #4f46e5;
        font-size: 13px;
        font-weight: 850;
    }
    .rs-ingestion-card {
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .rs-ingestion-copy {
        min-width: 0;
    }
    .rs-ingestion-copy .rs-card-title {
        margin: 0 0 8px 0 !important;
    }
    .rs-ingestion-copy .rs-card-sub {
        line-height: 1.35;
    }
    [data-testid="stFileUploader"] * {
        color: #1e293b !important;
        opacity: 1 !important;
    }
    [data-testid="stFileUploader"] section {
        border: 2px dashed rgba(99,102,241,0.28) !important;
        border-radius: 16px !important;
        background: rgba(255,255,255,0.62) !important;
        backdrop-filter: blur(12px) !important;
        padding: 20px !important;
    }
    [data-testid="stFileUploader"] section svg,
    [data-testid="stFileUploadDropzone"] svg {
        fill: #6366f1 !important;
        color: #6366f1 !important;
        opacity: 1 !important;
    }
    [data-testid="stFileUploadDropzone"] small { color: #94a3b8 !important; opacity:1 !important; }
    .tbl-header,
    .rs-wide-header,
    .rs-trx-header {
        display: grid;
        font-size: 10.5px !important;
        font-weight: 800 !important;
        color: #64748b !important;
        letter-spacing: 0.45px;
        text-transform: uppercase;
        padding: 10px 12px !important;
        background: rgba(99,102,241,0.08) !important;
        border: 1px solid rgba(255,255,255,0.86) !important;
        border-radius: 12px;
        margin-bottom: 7px;
    }
    .tbl-row,
    .rs-wide-row,
    .rs-trx-row {
        display: grid;
        font-size: 12px !important;
        color: #334155 !important;
        padding: 10px 12px !important;
        border: 1px solid rgba(255,255,255,0.78) !important;
        border-radius: 12px;
        background: rgba(255,255,255,0.42);
        align-items: center;
        margin-bottom: 6px;
        box-shadow: 0 2px 8px rgba(99,102,241,0.04);
    }
    .tbl-header,
    .tbl-row { grid-template-columns: 2fr 1fr 1fr 1fr; }
    .rs-wide-header,
    .rs-wide-row { grid-template-columns: 2fr 1fr 1fr 1fr 1fr; }
    .rs-trx-header,
    .rs-trx-row { grid-template-columns: 1fr 1.5fr 1fr 1fr 1fr 1fr; }
    </style>
    """, unsafe_allow_html=True)

    # ── TOP NAVBAR ──
    n1, n3 = st.columns([4, 6])
    with n1:
        st.markdown('<h2 style="margin:0;font-size:19px;font-weight:800;'
                    'color:#0f172a;padding-top:6px;">Revenue Sharing</h2>',
                    unsafe_allow_html=True)
    with n3:
        initial = st.session_state.get("user_name","Admin")[0].upper()
        uname   = st.session_state.get("user_name","Admin")
        uemail  = st.session_state.get("user_email","injourneyairports@mail.com")
        st.markdown(f"""
        <div style="display:flex;align-items:center;justify-content:flex-end;
                    gap:12px;padding-top:4px;">
            <div style="width:34px;height:34px;border-radius:50%;
                        background:rgba(255,255,255,0.72);
                        border:1px solid rgba(255,255,255,0.95);
                        backdrop-filter:blur(10px);
                        display:flex;align-items:center;justify-content:center;
                        color:#6366f1;font-size:16px;font-weight:800;
                        box-shadow:0 2px 8px rgba(99,102,241,0.08);">!</div>
            <div style="display:flex;align-items:center;gap:8px;">
                <div style="background:linear-gradient(135deg,#6366f1,#ec4899);
                            border-radius:50%;width:34px;height:34px;
                            display:flex;align-items:center;justify-content:center;
                            color:#fff;font-size:13px;font-weight:700;
                            box-shadow:0 3px 12px rgba(99,102,241,0.35);">{initial}</div>
                <div>
                    <div style="font-size:12px;font-weight:700;color:#1e293b;">{uname}</div>
                    <div style="font-size:10px;color:#94a3b8;">{uemail}</div>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown('<div class="rs-top-divider"></div>', unsafe_allow_html=True)

    # ── ROW 1: 4 KPI CARDS ──
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown("""
        <div class="rs-card rs-kpi-card" style="--accent:linear-gradient(135deg,#4f46e5,#6366f1);">
            <p class="rs-card-title">Total Revenue Sub</p>
            <p class="rs-card-value">Rp 32.4B</p>
            <span class="rs-delta-up">+5.2% vs last month</span>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown("""
        <div class="rs-card rs-kpi-card" style="--accent:linear-gradient(135deg,#0891b2,#06b6d4);">
            <p class="rs-card-title">Service Revenue Share</p>
            <p class="rs-card-value">Rp 21.1B</p>
            <p class="rs-card-sub">Top service contribution</p>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown("""
        <div class="rs-card rs-kpi-card rs-ingestion-card" style="--accent:linear-gradient(135deg,#059669,#10b981);">
            <div class="rs-progress-ring"><span>92%</span></div>
            <div class="rs-ingestion-copy">
                <p class="rs-card-title">Ingestion Complete</p>
                <p class="rs-card-sub">Expected files processed</p>
            </div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown("""
        <div class="rs-card rs-kpi-card" style="--accent:linear-gradient(135deg,#e11d48,#f97316);">
            <p class="rs-card-title">Production/Revenue Alerts</p>
            <p class="rs-card-value">5 Issues</p>
            <p class="rs-card-sub">3 conflicts, 2 anomalies</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    # ── ROW 2: Terminal Contribution + Chart ──
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown('<div class="rs-card">', unsafe_allow_html=True)
        tc1, tc2 = st.columns([3, 1])
        with tc1:
            st.markdown('<p class="rs-section-title">Terminal Contribution</p>',
                        unsafe_allow_html=True)
            st.markdown('<p class="rs-section-sub">Uploaded production files by terminal</p>',
                        unsafe_allow_html=True)
        with tc2:
            st.selectbox("", ["June","May","April"], key="tc_period",
                         label_visibility="collapsed")

        st.markdown(
            import_status_html("", "rs-section-title", "rs-section-sub"),
            unsafe_allow_html=True,
        )

        # Tabel file status
        df_files = get_terminal_files()
        st.markdown("""
        <div class="tbl-header">
            <span>File Name</span><span>Tenant/SBU</span>
            <span>Date</span><span>Status</span>
        </div>""", unsafe_allow_html=True)

        for _, row in df_files.iterrows():
            badge = fmt_status_badge(row["Status"])
            st.markdown(f"""
            <div class="tbl-row">
                <span>{row['File Name']}</span>
                <span>{row['Tenant/SBU']}</span>
                <span>{row['Date']}</span>
                <span>{badge}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="rs-card">', unsafe_allow_html=True)
        cc1, cc2 = st.columns([3, 1])
        with cc1:
            st.markdown('<p class="rs-section-title">SUB PRODUCTION & REVENUE</p>',
                        unsafe_allow_html=True)
            st.markdown('<p class="rs-section-sub">Monthly Trend Analysis</p>',
                        unsafe_allow_html=True)
        with cc2:
            st.selectbox("", ["June","May","April"], key="spr_period",
                         label_visibility="collapsed")

        df_trend = get_trend_data()
        fig_trend = go.Figure()
        for col, color in {"Ground Handling":"#6366f1","PSC":"#06b6d4","Others":"#f59e0b"}.items():
            fig_trend.add_trace(go.Scatter(
                x=df_trend["Bulan"], y=df_trend[col],
                mode="lines+markers", name=col,
                line=dict(color=color, width=2.6),
                marker=dict(size=6, color="#fff", line=dict(color=color, width=2))
            ))
        fig_trend.update_layout(
            height=260, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=10,b=0,l=0,r=0),
            legend=dict(orientation="h", y=-0.2, font=dict(size=10, color="#64748b")),
            xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#94a3b8")),
            yaxis=dict(showgrid=True, gridcolor="rgba(99,102,241,0.09)",
                       tickfont=dict(size=10, color="#94a3b8"), range=[0,1.6]))
        st.plotly_chart(fig_trend, use_container_width=True,
                        config={"displayModeBar": False})
        st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 3: Services Revenue + Transaction History ──
    col_svc, col_trx = st.columns([1, 1])

    with col_svc:
        st.markdown('<div class="rs-card">', unsafe_allow_html=True)
        sc1, sc2 = st.columns([3, 1])
        with sc1:
            st.markdown('<p class="rs-section-title">Services Revenue Calculation & Settlement</p>',
                        unsafe_allow_html=True)
            st.markdown('<p class="rs-section-sub">Revenue rules and settlement status by service</p>',
                        unsafe_allow_html=True)
        with sc2:
            st.markdown("<div style='text-align:right;padding-top:4px;'>"
                        "<span style='font-size:11px;color:#4f46e5;font-weight:700;'>"
                        "View Service Rules</span></div>", unsafe_allow_html=True)

        df_svc = get_services_data()
        st.markdown("""
        <div class="rs-wide-header">
            <span>Service/SBU</span><span>Gross Revenue</span>
            <span>SBU Share %</span><span>Mgmt Share</span><span>Status</span>
        </div>""", unsafe_allow_html=True)

        for _, row in df_svc.iterrows():
            badge = fmt_status_badge(row["Status"])
            st.markdown(f"""
            <div class="rs-wide-row">
                <span>{row['Service/SBU']}</span>
                <span>{row['Gross Revenue']}</span>
                <span>{row['SBU Share Rule %']}</span>
                <span>{row['Management Share']}</span>
                <span>{badge}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_trx:
        st.markdown('<div class="rs-card">', unsafe_allow_html=True)
        tc1, tc2 = st.columns([3, 1])
        with tc1:
            st.markdown('<p class="rs-section-title">Transaction History & SBU Export</p>',
                        unsafe_allow_html=True)
            st.markdown('<p class="rs-section-sub">Cleared transaction history ready for export</p>',
                        unsafe_allow_html=True)
        with tc2:
            st.markdown("<div style='text-align:right;padding-top:4px;'>"
                        "<span style='font-size:11px;color:#4f46e5;font-weight:700;'>"
                        "View Service Rules</span></div>", unsafe_allow_html=True)

        df_trx = get_transaction_data()
        st.markdown("""
        <div class="rs-trx-header">
            <span>Transaction ID</span><span>Revenue/SBU</span>
            <span>Type</span><span>Date</span><span>Amount</span><span>Status</span>
        </div>""", unsafe_allow_html=True)

        for _, row in df_trx.iterrows():
            badge = fmt_status_badge(row["Status"])
            st.markdown(f"""
            <div class="rs-trx-row">
                <span style="color:#4f46e5;font-weight:700;">{row['Transaction ID']}</span>
                <span>{row['Revenue/SBU']}</span><span>{row['Type']}</span>
                <span>{row['Date']}</span><span>{row['Amount']}</span>
                <span>{badge}</span>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    if "user_name"  not in st.session_state: st.session_state.user_name  = "Admin"
    if "user_email" not in st.session_state: st.session_state.user_email = "injourneyairports@mail.com"
    if "user_role"  not in st.session_state: st.session_state.user_role  = "Admin"
    page_revenue_sharing()
