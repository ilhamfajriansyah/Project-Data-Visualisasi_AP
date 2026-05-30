import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np
from datetime import datetime, date, timedelta
from shared_import import get_shared_import_meta, import_status_html

# ─────────────────────────────────────────────
# DUMMY DATA
# ─────────────────────────────────────────────
def get_recent_activities():
    return pd.DataFrame({
        "File Name": [
            "Accrual_Jun_Ground.xlsx", "Accrual_Jun_VIP.xlsx",
            "Accrual_Jun_Ground.xlsx", "Accrual_Jun_Ground.xlsx",
            "Accrual_Jun_VIP.xlsx",   "Accrual_Jun_VIP.xlsx",
        ],
        "Tenant/SBU": [
            "Terminal 1","Terminal 2","Terminal 1",
            "Terminal 1","Terminal 2","Terminal 2"
        ],
        "Date": [
            "28 Jun 2026","28 Jun 2026","28 Jun 2026",
            "28 Jun 2026","28 Jun 2026","28 Jun 2026"
        ],
        "Status": [
            "SUCCESS","RESERVED","SUCCESS",
            "SUCCESS","RESERVED","RESERVED"
        ],
    })

def fmt_status_badge(status):
    colors = {
        "SUCCESS":  ("rgba(16,185,129,0.12)", "#059669", "rgba(16,185,129,0.24)"),
        "RESERVED": ("rgba(99,102,241,0.12)", "#4f46e5", "rgba(99,102,241,0.24)"),
        "FAILED":   ("rgba(244,63,94,0.11)", "#e11d48", "rgba(244,63,94,0.22)"),
        "OVERDUE":  ("rgba(244,63,94,0.11)", "#e11d48", "rgba(244,63,94,0.22)"),
        "PAID":     ("rgba(16,185,129,0.12)", "#059669", "rgba(16,185,129,0.24)"),
        "PENDING":  ("rgba(245,158,11,0.13)", "#d97706", "rgba(245,158,11,0.24)"),
    }
    bg, fg, border = colors.get(status, ("rgba(148,163,184,0.12)", "#64748b", "rgba(148,163,184,0.22)"))
    return (
        f'<span style="background:{bg};color:{fg};padding:3px 10px;'
        f'border:1px solid {border};border-radius:999px;font-size:11px;'
        f'font-weight:700;letter-spacing:0.2px;">{status}</span>'
    )


# ══════════════════════════════════════════════
# PAGE: ACCRUAL & BILLING
# ══════════════════════════════════════════════
def page_accrual_billing():

    st.markdown("""
    <style>
    .ab-card {
        background: rgba(255, 255, 255, 0.56);
        border-radius: 10px;
        padding: 18px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
        border: 1px solid #e8eaed;
        margin-bottom: 14px;
    }
    .ab-kpi-label { font-size:12px; font-weight:600; color:#5f6368; margin:0 0 8px 0; }
    .ab-kpi-value { font-size:28px; font-weight:800; color:#202124; margin:0 0 6px 0; }
    .ab-kpi-sub   { font-size:11px; color:#9aa0a6; margin:0; }
    .ab-kpi-alert { font-size:28px; font-weight:800; color:#c5221f; margin:0 0 6px 0; }
    .ab-section-title { font-size:15px; font-weight:700; color:#202124; margin:0 0 14px 0; }

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

    .ab-tbl-header {
        display: grid;
        grid-template-columns: 2.5fr 1fr 1fr 1fr 1fr;
        font-size:12px; font-weight:600; color:#5f6368;
        padding:8px 8px; background:#f8f9fa;
        border-radius:6px; margin-bottom:4px;
    }
    .ab-tbl-row {
        display: grid;
        grid-template-columns: 2.5fr 1fr 1fr 1fr 1fr;
        font-size:12px; color:#202124;
        padding:9px 8px;
        border-bottom:1px solid #f1f3f4;
        align-items:center;
    }
    .ab-invoice-row {
        display:flex; justify-content:space-between;
        align-items:center; padding:12px 0;
        border-bottom:1px solid #f1f3f4; font-size:13px;
    }
    .ab-invoice-label { color:#5f6368; font-weight:500; }
    .ab-invoice-value { color:#202124; font-weight:700; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    .ab-card {
        background: rgba(255, 255, 255, 0.56) !important;
        backdrop-filter: blur(26px);
        -webkit-backdrop-filter: blur(26px);
        border-radius: 20px !important;
        padding: 20px 22px !important;
        box-shadow:
            0 8px 32px rgba(99,102,241,0.07),
            0 2px 8px rgba(15,23,42,0.025),
            inset 0 1px 0 rgba(255,255,255,1) !important;
        border: 1px solid rgba(255,255,255,0.90) !important;
        margin-bottom: 14px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .ab-card:hover {
        transform: translateY(-1px);
        box-shadow:
            0 14px 42px rgba(99,102,241,0.11),
            0 2px 8px rgba(15,23,42,0.03),
            inset 0 1px 0 rgba(255,255,255,1) !important;
    }
    .ab-kpi-card {
        min-height: 126px;
        overflow: hidden;
        position: relative;
    }
    .ab-kpi-card::before {
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
    .ab-kpi-label {
        font-size: 9.5px !important;
        font-weight: 800 !important;
        color: #94a3b8 !important;
        letter-spacing: 0.6px;
        text-transform: uppercase;
        margin: 3px 0 8px 0 !important;
    }
    .ab-kpi-value,
    .ab-kpi-alert {
        font-size: 23px !important;
        line-height: 1.15;
        font-weight: 850 !important;
        margin: 0 0 7px 0 !important;
        background: var(--accent, linear-gradient(135deg,#4f46e5,#0891b2));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    .ab-kpi-alert {
        background: linear-gradient(135deg,#e11d48,#f97316);
        -webkit-background-clip: text;
        background-clip: text;
    }
    .ab-kpi-sub {
        font-size: 10.5px !important;
        color: #64748b !important;
        font-weight: 600;
        margin: 0 !important;
    }
    .ab-section-title {
        font-size: 13px !important;
        font-weight: 800 !important;
        color: #1e293b !important;
        margin: 0 0 3px 0 !important;
    }
    .ab-section-sub {
        font-size: 11px;
        color: #94a3b8;
        margin: 0 0 14px 0;
    }
    .ab-top-divider {
        position: relative;
        height: 2px;
        margin: 18px 0 18px;
        border-radius: 999px;
        background: linear-gradient(90deg, rgba(99,102,241,0), rgba(99,102,241,0.50), rgba(6,182,212,0.58), rgba(16,185,129,0.52), rgba(16,185,129,0));
        box-shadow: 0 8px 24px rgba(6,182,212,0.14);
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
    .ab-tbl-header,
    .ab-detail-header {
        display: grid;
        grid-template-columns: 2.5fr 1fr 1fr 1fr 1fr;
        font-size: 10.5px !important;
        font-weight: 800 !important;
        color: #64748b !important;
        letter-spacing: 0.45px;
        text-transform: uppercase;
        padding: 10px 12px !important;
        background: rgba(99,102,241,0.08) !important;
        border: 1px solid rgba(255,255,255,0.86);
        border-radius: 12px !important;
        margin-bottom: 7px;
    }
    .ab-tbl-row,
    .ab-detail-row {
        display: grid;
        grid-template-columns: 2.5fr 1fr 1fr 1fr 1fr;
        font-size: 12px !important;
        color: #334155 !important;
        padding: 10px 12px !important;
        border: 1px solid rgba(255,255,255,0.78);
        border-radius: 12px;
        background: rgba(255,255,255,0.42);
        align-items: center;
        margin-bottom: 6px;
        box-shadow: 0 2px 8px rgba(99,102,241,0.04);
    }
    .ab-detail-header,
    .ab-detail-row {
        grid-template-columns: 1.2fr 1.5fr 1fr 1fr 1fr;
    }
    .ab-invoice-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 11px 13px !important;
        border: 1px solid rgba(255,255,255,0.78) !important;
        border-radius: 12px;
        background: rgba(255,255,255,0.40);
        margin-top: 7px;
        font-size: 13px;
    }
    .ab-invoice-label { color:#64748b !important; font-weight:600 !important; }
    .ab-invoice-value { color:#1e293b !important; font-weight:800 !important; }
    .ab-alert-item {
        background: rgba(255,255,255,0.48);
        border: 1px solid rgba(255,255,255,0.82);
        border-radius: 16px;
        padding: 14px 16px;
        margin-bottom: 10px;
        box-shadow: 0 2px 10px rgba(244,63,94,0.05);
    }
    .ab-alert-total {
        background: linear-gradient(135deg, rgba(244,63,94,0.12), rgba(249,115,22,0.10));
        border: 1px solid rgba(244,63,94,0.22);
        border-radius: 14px;
        padding: 13px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .ab-progress-track {
        background: rgba(148,163,184,0.18);
        border-radius: 999px;
        height: 6px;
        overflow: hidden;
    }
    .ab-progress-bar {
        border-radius: inherit;
        height: 6px;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── TOP NAVBAR ──
    n1, n3 = st.columns([4, 6])
    with n1:
        st.markdown('<h2 style="margin:0;font-size:19px;font-weight:800;'
                    'color:#0f172a;padding-top:6px;">Accrual & Billing</h2>',
                    unsafe_allow_html=True)
    with n3:
        initial = st.session_state.get("user_name", "Admin")[0].upper()
        uname   = st.session_state.get("user_name", "Admin")
        uemail  = st.session_state.get("user_email", "injourneyairports@mail.com")
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

    st.markdown('<div class="ab-top-divider"></div>', unsafe_allow_html=True)

    # ── ROW 1: 4 KPI CARDS ──
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown("""
        <div class="ab-card ab-kpi-card" style="--accent:linear-gradient(135deg,#4f46e5,#6366f1);">
            <p class="ab-kpi-label">Total Accrued Revenue</p>
            <p class="ab-kpi-value">Rp 21.1B</p>
            <p class="ab-kpi-sub">Current month accrual base</p>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown("""
        <div class="ab-card ab-kpi-card" style="--accent:linear-gradient(135deg,#0891b2,#06b6d4);">
            <p class="ab-kpi-label">Invoice Generated</p>
            <p class="ab-kpi-value">Rp 18.5B</p>
            <p class="ab-kpi-sub">90 invoices issued</p>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown("""
        <div class="ab-card ab-kpi-card" style="--accent:linear-gradient(135deg,#059669,#10b981);">
            <p class="ab-kpi-label">Total Payments Received</p>
            <p class="ab-kpi-value">Rp 15.2B</p>
            <p class="ab-kpi-sub" style="color:#059669;">+3.2% of current month</p>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown("""
        <div class="ab-card ab-kpi-card" style="--accent:linear-gradient(135deg,#e11d48,#f97316);">
            <p class="ab-kpi-label">Overdue Receivables</p>
            <p class="ab-kpi-alert">Rp 3.3B</p>
            <p class="ab-kpi-sub">15 Alarms</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # ── ROW 2: Upload + Chart ──
    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown('<div class="ab-card">', unsafe_allow_html=True)
        st.markdown('<p class="ab-section-title">Accrual & Invoice Processing</p>',
                    unsafe_allow_html=True)
        st.markdown('<p class="ab-section-sub">Upload batch revenue, validate, and generate billing runs</p>',
                    unsafe_allow_html=True)

        st.markdown(
            import_status_html("", "ab-section-title", "ab-section-sub"),
            unsafe_allow_html=True,
        )

        if st.button("Process Files", key="btn_process", use_container_width=True):
            if get_shared_import_meta():
                with st.spinner("Memproses file..."):
                    import time; time.sleep(1)
                st.success("Data dari Import Manager berhasil diproses.")
            else:
                st.warning("Upload file terlebih dahulu di halaman Import Manager.")

        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="ab-card">', unsafe_allow_html=True)
        st.markdown('<p class="ab-section-title">Invoice Status Breakdown</p>',
                    unsafe_allow_html=True)
        st.markdown('<p class="ab-section-sub">Sent, overdue, and paid invoices by value</p>',
                    unsafe_allow_html=True)

        fig_bar = go.Figure(go.Bar(
            x=["Sent", "Overdue", "Paid"],
            y=[66, 120, 30],
            marker_color=["#6366f1", "#f43f5e", "#10b981"],
            marker_line_color="rgba(255,255,255,0.86)",
            marker_line_width=1.5,
            text=["66M", "120M", "30M"],
            textposition="outside",
            textfont=dict(size=11, color="#475569"),
        ))
        fig_bar.update_layout(
            height=220, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20,b=0,l=0,r=0),
            xaxis=dict(showgrid=False, tickfont=dict(size=12, color="#64748b")),
            yaxis=dict(showgrid=False, visible=False),
            bargap=0.45,
        )
        st.plotly_chart(fig_bar, use_container_width=True,
                        config={"displayModeBar": False})

        for label, value in [("Sent","Rp 18.5B"),("Overdue","Rp 3.8B"),("Paid","Rp 15.2B")]:
            st.markdown(f"""
            <div class="ab-invoice-row">
                <span class="ab-invoice-label">{label}</span>
                <span class="ab-invoice-value">{value}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 3: Recent Activities ──
    st.markdown('<div class="ab-card">', unsafe_allow_html=True)
    st.markdown('<p class="ab-section-title">Recent Activities</p>', unsafe_allow_html=True)
    st.markdown('<p class="ab-section-sub">Latest batch processing status by terminal</p>',
                unsafe_allow_html=True)

    fc1, fc2, fc3 = st.columns([2, 2, 2])
    with fc1:
        f_tenant = st.selectbox("", ["Semua Terminal","Terminal 1","Terminal 2"],
                                key="ab_tenant", label_visibility="collapsed")
    with fc2:
        f_status = st.selectbox("", ["Semua Status","SUCCESS","RESERVED","FAILED"],
                                key="ab_status", label_visibility="collapsed")
    with fc3:
        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
        st.button("Refresh", key="btn_refresh", use_container_width=True)

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    df_act = get_recent_activities()
    if f_tenant != "Semua Terminal": df_act = df_act[df_act["Tenant/SBU"] == f_tenant]
    if f_status != "Semua Status":   df_act = df_act[df_act["Status"]     == f_status]

    st.markdown("""
    <div class="ab-tbl-header">
        <span>File Name</span><span>Tenant/SBU</span>
        <span>Date</span><span>Status</span><span>Action</span>
    </div>""", unsafe_allow_html=True)

    for _, row in df_act.iterrows():
        badge = fmt_status_badge(row["Status"])
        st.markdown(f"""
        <div class="ab-tbl-row">
            <span>{row['File Name']}</span>
            <span style="color:#5f6368;">{row['Tenant/SBU']}</span>
            <span style="color:#5f6368;">{row['Date']}</span>
            <span>{badge}</span>
            <span style="display:flex;gap:10px;font-size:15px;">
                <span title="View"  style="cursor:pointer;">👁️</span>
                <span title="Edit"  style="cursor:pointer;">✏️</span>
                <span title="Check" style="cursor:pointer;color:#1e7e34;">✔️</span>
            </span>
        </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # ── ROW 4: Detail Invoice + Overdue Tracker ──
    col_inv, col_ov = st.columns([1, 1])

    with col_inv:
        st.markdown('<div class="ab-card">', unsafe_allow_html=True)
        st.markdown('<p class="ab-section-title">Detail Invoice</p>', unsafe_allow_html=True)
        st.markdown('<p class="ab-section-sub">Open billing items by tenant and due date</p>',
                    unsafe_allow_html=True)

        invoices = pd.DataFrame({
            "Invoice ID": ["INV-2026-001","INV-2026-002","INV-2026-003","INV-2026-004","INV-2026-005"],
            "Tenant":     ["Ground Handling","PSC","VIP Services","Commercial Area","Cargo Area"],
            "Amount":     ["Rp 8.47B","Rp 6.4B","Rp 2.73B","Rp 1.95B","Rp 8.47B"],
            "Due Date":   ["15 Jul 2026","20 Jul 2026","25 Jul 2026","30 Jul 2026","05 Aug 2026"],
            "Status":     ["PAID","PAID","OVERDUE","PENDING","PENDING"],
        })

        st.markdown("""
        <div class="ab-detail-header">
            <span>Invoice ID</span><span>Tenant</span>
            <span>Amount</span><span>Due Date</span><span>Status</span>
        </div>""", unsafe_allow_html=True)

        for _, row in invoices.iterrows():
            badge = fmt_status_badge(row["Status"])
            st.markdown(f"""
            <div class="ab-detail-row">
                <span style="color:#4f46e5;font-weight:700;">{row['Invoice ID']}</span>
                <span>{row['Tenant']}</span><span>{row['Amount']}</span>
                <span style="color:#64748b;">{row['Due Date']}</span>
                <span>{badge}</span>
            </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with col_ov:
        st.markdown('<div class="ab-card">', unsafe_allow_html=True)
        st.markdown('<p class="ab-section-title">Overdue Tracker</p>', unsafe_allow_html=True)
        st.markdown('<p class="ab-section-sub">Aging risk by tenant with collection progress</p>',
                    unsafe_allow_html=True)

        for name, amount, due, days in [
            ("PT BUDI PUTRA BOGAJAYA", "Rp 1.2B", "15 Jun 2026", 13),
            ("PT DEWATAAGUNG WIBAWA",  "Rp 0.8B", "20 Jun 2026",  8),
            ("PT PERTAMINA PATRA",     "Rp 1.3B", "10 Jun 2026", 18),
        ]:
            pct   = min(days / 30 * 100, 100)
            color = "#e11d48" if days > 15 else "#f59e0b"
            st.markdown(f"""
            <div class="ab-alert-item">
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                    <span style="font-size:12px;font-weight:700;color:#1e293b;">{name[:28]}</span>
                    <span style="font-size:13px;font-weight:800;color:#e11d48;">{amount}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                    <span style="font-size:11px;color:#94a3b8;">Due: {due}</span>
                    <span style="font-size:11px;font-weight:700;color:{color};">
                        {days} hari terlambat</span>
                </div>
                <div class="ab-progress-track">
                    <div class="ab-progress-bar" style="background:{color};width:{pct}%;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div class="ab-alert-total">
            <span style="font-size:13px;font-weight:800;color:#e11d48;">Total Overdue</span>
            <span style="font-size:16px;font-weight:850;color:#e11d48;">Rp 3.3B</span>
        </div>""", unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    if "user_name"  not in st.session_state: st.session_state.user_name  = "Admin"
    if "user_email" not in st.session_state: st.session_state.user_email = "injourneyairports@mail.com"
    if "user_role"  not in st.session_state: st.session_state.user_role  = "Admin"
    page_accrual_billing()
