from .accrual_billing import page_accrual_billing
from .revenue_sharing import page_revenue_sharing
from .room_database import render_room_database
from .lease_contract import render_lease_contract
from .import_manager import render_import_manager
from .Data_verification import render_data_verification
from .dashboard_style import DASHBOARD_CSS
from login.access_control import Role, get_current_role, init_auth_state, is_authenticated, logout_user
from .shared_import import get_shared_import_data, has_dashboard_ready_import, import_status_html
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
from html import escape
from textwrap import dedent
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

# ─────────────────────────────────────────────
# LOAD CSS
# ─────────────────────────────────────────────
def inject_dashboard_css():
    st.markdown(f"<style>{DASHBOARD_CSS}</style>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    .ap-top-actions {
        display: flex;
        align-items: flex-start;
        justify-content: flex-end;
        gap: 14px;
        padding-top: 2px;
        position: relative;
        overflow: visible;
    }
    .ap-top-bell {
        width: 34px;
        height: 34px;
        margin-top: 7px;
        border-radius: 50%;
        background: rgba(255,255,255,0.78);
        border: 1px solid rgba(255,255,255,0.96);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        box-shadow: 0 2px 8px rgba(99,102,241,0.08);
    }
    .ap-profile-details {
        position: relative;
        overflow: visible;
    }
    .ap-profile-details > summary {
        list-style: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        user-select: none;
        outline: none;
    }
    .ap-profile-details > summary::-webkit-details-marker {
        display: none;
    }
    .ap-profile-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: #d6d6d6;
        border: 1px solid rgba(203,213,225,0.95);
        box-shadow: 0 4px 14px rgba(15,23,42,0.08);
        flex: 0 0 auto;
        display: block;
        overflow: hidden;
        position: relative;
    }
    .ap-profile-avatar::before {
        content: "";
        position: absolute;
        left: 50%;
        top: 9px;
        width: 19px;
        height: 19px;
        border-radius: 50%;
        background: #9f9f9f;
        transform: translateX(-50%);
    }
    .ap-profile-avatar::after {
        content: "";
        position: absolute;
        left: 50%;
        top: 29px;
        width: 35px;
        height: 25px;
        border-radius: 50% 50% 42% 42% / 62% 62% 38% 38%;
        background: #9f9f9f;
        transform: translateX(-50%);
    }
    .ap-profile-menu {
        position: absolute;
        right: 0;
        top: 54px;
        z-index: 9999;
        width: 210px;
        padding: 8px 0;
        border-radius: 10px;
        background: rgba(255,255,255,0.98);
        border: 1px solid rgba(226,232,240,0.96);
        box-shadow: 0 16px 34px rgba(15,23,42,0.14);
        overflow: hidden;
    }
    .ap-profile-menu-item {
        height: 46px;
        padding: 0 20px;
        color: #334155 !important;
        text-decoration: none !important;
        display: flex;
        align-items: center;
        gap: 15px;
        font-size: 14px;
        font-weight: 600;
        white-space: nowrap;
    }
    .ap-profile-menu-item:hover {
        background: rgba(99,102,241,0.08);
        color: #4f46e5 !important;
    }
    .ap-profile-menu-icon {
        width: 18px;
        color: #64748b;
        text-align: center;
        font-size: 16px;
    }
    #MainMenu,
    footer,
    header,
    [data-testid="stHeader"] {
        display: none !important;
        height: 0 !important;
        visibility: hidden !important;
    }
    .block-container {
        padding-top: 2px !important;
    }
    [data-testid="stSidebarContent"] {
        padding: 0 !important;
    }
    [data-testid="stSidebarContent"] > div,
    [data-testid="stSidebarContent"] > div:first-child,
    [data-testid="stSidebarContent"] [data-testid="stVerticalBlock"],
    [data-testid="stSidebarContent"] [data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    [data-testid="stSidebar"] .element-container:first-child {
        margin-top: 0 !important;
    }
    .ap-brand {
        margin-top: -2px !important;
        padding: 6px 14px 10px !important;
    }
    .ap-brand-mini {
        margin-top: -2px !important;
        padding: 6px 0 8px !important;
    }
    .ap-logo {
        width: 34px !important;
        height: 34px !important;
        border-radius: 11px !important;
    }
    .ap-brand-name {
        font-size: 10.2px !important;
        line-height: 1.2 !important;
    }
    .ap-brand-sub {
        font-size: 8.6px !important;
        margin-top: 2px !important;
    }
    .nad-top-divider {
        margin: 6px 0 12px !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .overview-main-card-marker) {
        position: relative;
        height: auto;
        min-height: 0;
        overflow: visible;
        padding: 22px 24px 24px;
        margin-bottom: 18px;
        border-radius: 28px;
        background:
            radial-gradient(circle at 10% 0%, rgba(139, 92, 246, 0.09), transparent 34%),
            radial-gradient(circle at 92% 100%, rgba(6, 182, 212, 0.08), transparent 38%),
            rgba(255, 255, 255, 0.66);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border: 1px solid rgba(255, 255, 255, 0.96);
        box-shadow:
            0 18px 50px rgba(76, 81, 191, 0.10),
            0 4px 14px rgba(15, 23, 42, 0.035),
            inset 0 1px 0 rgba(255, 255, 255, 1);
    }
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .overview-main-card-marker)
    > div[data-testid="stElementContainer"]:has(.overview-main-card-marker) {
        display: none;
    }
    button[kind="secondary"][data-testid="baseButton-secondary"] {
        border: none !important;
    }

    div[data-testid="stButton"] > button {
        background: transparent !important;
        color: #6366f1 !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        min-height: 18px !important;
        height: 18px !important;
        line-height: 18px !important;
        font-size: 10.5px !important;
        font-weight: 700 !important;
        text-align: right !important;
    }
    div[data-testid="stButton"] > button p {
        font-size: 10.5px !important;
        margin: 0 !important;
        line-height: 18px !important;
        white-space: nowrap !important;
    }
    div[data-testid="stButton"] {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
    }
    div[data-testid="stButton"] > button:hover {
        color: #4f46e5 !important;
        background: transparent !important;
    }
    
    .overview-main-card-marker {
        display: none;
    }
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .overview-section-card-strip) {
        position: relative;
        height: auto;
        min-height: 0;
        overflow: visible;
        background: rgba(255, 255, 255, 0.56);
        backdrop-filter: blur(26px);
        -webkit-backdrop-filter: blur(26px);
        border-radius: 20px;
        padding: 16px 20px 20px;
        border: 1px solid rgba(255, 255, 255, 0.90);
        box-shadow:
            0 8px 32px rgba(99, 102, 241, 0.07),
            0 2px 8px rgba(0, 0, 0, 0.025),
            inset 0 1px 0 rgba(255, 255, 255, 1),
            inset 0 -1px 0 rgba(99, 102, 241, 0.025);
        margin-bottom: 14px;
        transition: box-shadow 0.2s, transform 0.2s;
    }
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .overview-section-card-strip):hover {
        box-shadow:
            0 14px 42px rgba(99, 102, 241, 0.11),
            0 2px 8px rgba(0, 0, 0, 0.03),
            inset 0 1px 0 rgba(255, 255, 255, 1);
        transform: translateY(-1px);
    }
    .overview-section-card-strip {
        position: relative;
        height: 5px;
        margin: -2px 0 14px;
        border-radius: 999px;
        background: linear-gradient(90deg, rgba(99,102,241,0.00), rgba(99,102,241,0.50), rgba(6,182,212,0.58), rgba(16,185,129,0.52), rgba(16,185,129,0.00));
        box-shadow: 0 8px 24px rgba(6, 182, 212, 0.12);
    }
    .overview-section-card-strip::after {
        content: "";
        position: absolute;
        left: 8%;
        right: 8%;
        top: 1px;
        height: 1px;
        border-radius: inherit;
        background: rgba(255, 255, 255, 0.72);
    }
    .overview-card-action {
        font-size: 11px;
        color: #6366f1;
        text-align: right;
        margin: 2px 0;
        font-weight: 600;
        cursor: pointer;
    }
    .overview-card-action.is-detail {
        margin-top: 4px;
    }
    
    .overview-light-table-wrap {
    width: 100%;
    overflow: hidden;
    border-radius: 16px;
    border: 1px solid rgba(226, 232, 240, 0.9);
    background: rgba(255, 255, 255, 0.68);
    box-shadow:
        0 8px 24px rgba(99, 102, 241, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.95);
    }

    .overview-light-table-wrap.is-summary {
        min-height: 265px;
    }

    .overview-light-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        color: #1e293b;
    }

    .overview-light-table thead {
        background: rgba(248, 250, 252, 0.92);
    }

    .overview-light-table th {
        padding: 12px 14px;
        text-align: left;
        font-size: 12px;
        font-weight: 700;
        color: #64748b;
        border-bottom: 1px solid rgba(226, 232, 240, 0.95);
    }

    .overview-light-table td {
        padding: 12px 14px;
        font-size: 12.5px;
        font-weight: 600;
        color: #0f172a;
        border-bottom: 1px solid rgba(226, 232, 240, 0.72);
    }

    .overview-light-table tbody tr:last-child td {
        border-bottom: none;
    }

    .overview-light-table tbody tr:hover {
        background: rgba(99, 102, 241, 0.045);
    }
                
    h2[style*="padding-top:6px"],
    .lc-header-title,
    .page-header,
    .im-manager-surface {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    .ap-top-actions {
        align-items: center;
        padding-top: 0;
        min-height: 40px;
    }
    .ap-top-bell {
        margin-top: 0;
    }
    @media (max-width: 900px) {
        .block-container {
            padding-top: 2px !important;
        }
        .ap-brand {
            padding-top: 5px !important;
        }
    }

    /* Enterprise dashboard redesign */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #F8FAFC !important;
    }

    .block-container {
        max-width: 100% !important;
        padding: 18px 28px 34px !important;
    }

    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #E5E7EB !important;
        box-shadow: none !important;
        min-width: 250px !important;
        width: 250px !important;
        max-width: 250px !important;
    }

    [data-testid="stSidebarContent"] {
        background: #ffffff !important;
    }

    .ap-brand {
        margin: 0 !important;
        padding: 20px 24px 22px !important;
        border-bottom: 1px solid #E5E7EB !important;
    }

    .ap-logo {
        width: 42px !important;
        height: 42px !important;
        border-radius: 10px !important;
        background: #2563EB !important;
        box-shadow: none !important;
        font-size: 13px !important;
    }

    .ap-brand-name {
        color: #0F172A !important;
        font-size: 12px !important;
        font-weight: 800 !important;
        letter-spacing: 0 !important;
    }

    .ap-brand-sub {
        color: #64748B !important;
        font-size: 10px !important;
        font-weight: 700 !important;
        letter-spacing: 1.6px !important;
    }

    .nav-group {
        padding: 22px 24px 8px !important;
        color: #94A3B8 !important;
        font-size: 10px !important;
        letter-spacing: 1.2px !important;
    }

    .nav-active {
        margin: 4px 16px !important;
        padding: 12px 14px !important;
        border-radius: 10px !important;
        background: #EFF6FF !important;
        border: 1px solid #DBEAFE !important;
        box-shadow: none !important;
        color: #2563EB !important;
        font-size: 13px !important;
        font-weight: 700 !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] {
        padding: 0 16px !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] > button {
        height: 44px !important;
        min-height: 44px !important;
        padding: 0 14px !important;
        border-radius: 10px !important;
        color: #475569 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        background: transparent !important;
        justify-content: flex-start !important;
        text-align: left !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: #F1F5F9 !important;
        color: #2563EB !important;
    }

    .nad-top-divider {
        height: 1px !important;
        margin: 14px 0 18px !important;
        background: #E5E7EB !important;
        box-shadow: none !important;
    }

    .nad-top-divider::after {
        display: none !important;
    }

    .ap-top-actions {
        align-items: center !important;
        gap: 14px !important;
        min-height: 44px !important;
    }

    .ap-top-bell {
        width: 38px !important;
        height: 38px !important;
        margin: 0 !important;
        border-radius: 999px !important;
        background: #ffffff !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: none !important;
        color: #334155 !important;
    }

    .ap-profile-avatar {
        width: 42px !important;
        height: 42px !important;
        background: #E2E8F0 !important;
        border: 1px solid #CBD5E1 !important;
        box-shadow: none !important;
    }

    .ap-user-meta {
        text-align: left;
        color: #0F172A;
        font-size: 12px;
        font-weight: 800;
        line-height: 1.2;
    }

    .ap-user-meta span {
        display: block;
    }

    .ap-profile-details > summary {
        gap: 10px !important;
    }

    .ap-user-role {
        margin-top: 2px;
        color: #64748B;
        font-size: 11px;
        font-weight: 600;
    }

    .overview-shell {
        width: 100%;
    }

    .overview-filter-label {
        margin: 0 0 6px 2px;
        color: #64748B;
        font-size: 11px;
        font-weight: 700;
    }

    .overview-filter-spacer {
        height: 2px;
    }

    .overview-kpi-card {
        min-height: 118px;
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        background: #ffffff;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }

    .overview-kpi-icon {
        width: 52px;
        height: 52px;
        flex: 0 0 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        font-size: 18px;
        font-weight: 900;
    }

    .overview-kpi-copy {
        min-width: 0;
    }

    .overview-kpi-label {
        color: #475569;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 0.3px;
        text-transform: uppercase;
    }

    .overview-kpi-value {
        margin-top: 7px;
        color: #0F172A;
        font-size: 27px;
        font-weight: 900;
        line-height: 1.05;
        letter-spacing: 0 !important;
    }

    .overview-kpi-delta {
        margin-top: 10px;
        color: #64748B;
        font-size: 11px;
        font-weight: 700;
    }

    .overview-kpi-delta strong {
        display: inline-flex;
        align-items: center;
        padding: 3px 8px;
        margin-right: 6px;
        border-radius: 999px;
        background: #DCFCE7;
        color: #059669;
        font-size: 11px;
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) {
        position: relative;
        overflow: hidden;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        background: #ffffff;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker)
    > div[data-testid="stElementContainer"]:has(.ed-card-marker) {
        display: none;
    }

    .ed-card-marker {
        display: none;
    }

    .ed-section-title {
        margin: 0;
        color: #0F172A;
        font-size: 16px;
        font-weight: 900;
    }

    .ed-section-sub {
        margin: 3px 0 0;
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
    }

    .ed-card-action {
        text-align: right;
        color: #2563EB;
        font-size: 12px;
        font-weight: 800;
    }

    .ed-alert-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 12px;
    }

    .ed-alert-item {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        background: #ffffff;
    }

    .ed-alert-icon {
        width: 40px;
        height: 40px;
        flex: 0 0 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        font-weight: 900;
    }

    .ed-alert-title {
        margin: 0;
        color: #0F172A;
        font-size: 12.5px;
        font-weight: 850;
        line-height: 1.35;
    }

    .ed-alert-sub {
        margin: 4px 0 0;
        color: #64748B;
        font-size: 11.5px;
        font-weight: 600;
    }

    .ed-table-card {
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        background: #ffffff;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
        overflow: hidden;
    }

    .ed-table-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 16px 18px 8px;
    }

    .ed-table-title {
        margin: 0;
        color: #0F172A;
        font-size: 16px;
        font-weight: 900;
    }

    .ed-table-link {
        color: #2563EB;
        font-size: 12px;
        font-weight: 800;
    }

    .ed-table-scroll {
        width: 100%;
        overflow-x: auto;
    }

    .ed-table {
        width: 100%;
        border-collapse: collapse;
        color: #0F172A;
        font-size: 12px;
    }

    .ed-table th {
        padding: 10px 18px;
        background: #F8FAFC;
        border-top: 1px solid #F1F5F9;
        border-bottom: 1px solid #E2E8F0;
        color: #475569;
        font-size: 11px;
        font-weight: 850;
        text-align: left;
        white-space: nowrap;
    }

    .ed-table td {
        padding: 12px 18px;
        border-bottom: 1px solid #F1F5F9;
        color: #0F172A;
        font-size: 12px;
        font-weight: 650;
        white-space: nowrap;
    }

    .ed-table tbody tr:hover {
        background: #F8FAFC;
    }

    .ed-table tbody tr:last-child td {
        border-bottom: none;
    }

    .ed-positive {
        color: #059669;
        font-weight: 850;
    }

    .ed-negative {
        color: #DC2626;
        font-weight: 850;
    }

    .ed-pagination {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 13px 18px 16px;
        border-top: 1px solid #F1F5F9;
        color: #64748B;
        font-size: 12px;
        font-weight: 650;
    }

    .ed-chip-row {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 8px;
    }

    [data-testid="stSelectbox"] > div > div,
    .stTextInput > div > div > input {
        min-height: 40px !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background: #ffffff !important;
        box-shadow: none !important;
        color: #0F172A !important;
        font-size: 13px !important;
        font-weight: 650 !important;
    }

    .stTextInput > div > div > input::placeholder {
        color: #94A3B8 !important;
    }

    div[data-testid="stButton"] > button,
    div[data-testid="stDownloadButton"] > button {
        min-height: 38px !important;
        height: 38px !important;
        padding: 0 14px !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background: #ffffff !important;
        color: #334155 !important;
        box-shadow: none !important;
        font-size: 12px !important;
        font-weight: 800 !important;
    }

    div[data-testid="stButton"] > button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        border-color: #94A3B8 !important;
        background: #F8FAFC !important;
        color: #0F172A !important;
        transform: none !important;
    }

    @media (max-width: 1100px) {
        .overview-kpi-card {
            min-height: 104px;
        }

        .overview-kpi-value {
            font-size: 23px;
        }
    }
    </style>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
ROLE_MENUS = {
    Role.USER: [
        "Overview",
        "Revenue Sharing",
        "Accrual & Billing",
        "Room Database",
        "Lease Contract",
        "Import Manager",
        "Data Verification",
    ],
    Role.ADMIN: [
        "Overview",
        "Revenue Sharing",
        "Accrual & Billing",
        "Room Database",
        "Lease Contract",
        "Import Manager",
        "Data Verification",
    ],
}


def get_allowed_menus():
    return ROLE_MENUS.get(get_current_role(), ["Overview"])


def can_access_menu(menu_name):
    return menu_name in get_allowed_menus()


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
    return dedent(f"""
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
    </div>""").strip()

def _light_table_html(df, extra_class=""):
    header_html = "".join([f"<th>{escape(str(col))}</th>" for col in df.columns])

    rows_html = ""
    for _, row in df.iterrows():
        cells = "".join([f"<td>{escape(str(value))}</td>" for value in row])
        rows_html += f"<tr>{cells}</tr>"

    return dedent(f"""
    <div class="overview-light-table-wrap {extra_class}">
        <table class="overview-light-table">
            <thead>
                <tr>{header_html}</tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
    </div>
    """).strip()


def _ed_card_marker(container):
    container.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)


def _fmt_rp_compact(value):
    if pd.isna(value):
        value = 0
    if value >= 1_000_000_000_000:
        return f"Rp {value / 1_000_000_000_000:.2f}T"
    if value >= 1_000_000_000:
        return f"Rp {value / 1_000_000_000:.2f}B"
    if value >= 1_000_000:
        return f"Rp {value / 1_000_000:.2f}M"
    return f"Rp {value:,.0f}"


def _fmt_rp_full(value):
    if pd.isna(value):
        value = 0
    return f"Rp {value:,.0f}"


def _format_mom(value):
    sign = "up" if value >= 0 else "down"
    cls = "ed-positive" if value >= 0 else "ed-negative"
    arrow = "↑" if value >= 0 else "↓"
    return f'<span class="{cls}">{arrow} {abs(value):.1f}%</span>'


def _overview_kpi_card(label, value, delta, accent, icon):
    return dedent(f"""
    <div class="overview-kpi-card">
        <div class="overview-kpi-icon" style="background:{accent}14;color:{accent};">{escape(icon)}</div>
        <div class="overview-kpi-copy">
            <div class="overview-kpi-label">{escape(label)}</div>
            <div class="overview-kpi-value">{escape(value)}</div>
            <div class="overview-kpi-delta"><strong>↑ {escape(delta)}</strong> vs periode sebelumnya</div>
        </div>
    </div>
    """).strip()


def _alert_item_html(icon, accent, title, subtitle):
    return dedent(f"""
    <div class="ed-alert-item">
        <div class="ed-alert-icon" style="background:{accent}14;color:{accent};">{escape(icon)}</div>
        <div style="flex:1;min-width:0;">
            <p class="ed-alert-title">{escape(title)}</p>
            <p class="ed-alert-sub">{escape(subtitle)}</p>
        </div>
        <div style="color:#94A3B8;font-weight:900;">&gt;</div>
    </div>
    """).strip()


def _enterprise_table_html(df, title=None, link_label=None, table_class=""):
    header_html = "".join(f"<th>{escape(str(col))}</th>" for col in df.columns)
    rows_html = ""
    for _, row in df.iterrows():
        cells = []
        for value in row:
            text = str(value)
            if text.startswith("<span "):
                cells.append(f"<td>{text}</td>")
            else:
                cells.append(f"<td>{escape(text)}</td>")
        rows_html += f"<tr>{''.join(cells)}</tr>"

    head_html = ""
    if title:
        link_html = f'<span class="ed-table-link">{escape(link_label)}</span>' if link_label else ""
        head_html = dedent(f"""
        <div class="ed-table-head">
            <p class="ed-table-title">{escape(title)}</p>
            {link_html}
        </div>
        """).strip()

    return dedent(f"""
    <div class="ed-table-card {table_class}">
        {head_html}
        <div class="ed-table-scroll">
            <table class="ed-table">
                <thead><tr>{header_html}</tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
        </div>
    </div>
    """).strip()


def _enterprise_table_inner_html(df):
    header_html = "".join(f"<th>{escape(str(col))}</th>" for col in df.columns)
    rows_html = ""
    for _, row in df.iterrows():
        cells = []
        for value in row:
            text = str(value)
            if text.startswith("<span "):
                cells.append(f"<td>{text}</td>")
            else:
                cells.append(f"<td>{escape(text)}</td>")
        rows_html += f"<tr>{''.join(cells)}</tr>"
    return dedent(f"""
    <div class="ed-table-scroll">
        <table class="ed-table">
            <thead><tr>{header_html}</tr></thead>
            <tbody>{rows_html}</tbody>
        </table>
    </div>
    """).strip()


# ══════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════
def _overview_main_card_marker(container):
    container.markdown('<div class="overview-main-card-marker"></div>', unsafe_allow_html=True)


def _overview_section_strip():
    st.markdown('<div class="overview-section-card-strip"></div>', unsafe_allow_html=True)


NAV_ICONS = {
    "Overview": "📊",
    "Revenue Sharing": "💰",
    "Accrual & Billing": "🧾",
    "Room Database": "🏢",
    "Lease Contract": "📄",
    "Import Manager": "📤",
    "Data Verification": "✓",
}


def _go_to_menu(menu_name):
    if not can_access_menu(menu_name):
        st.session_state.active_menu = "Overview"
        return
    st.session_state.active_menu = menu_name


if not hasattr(st, "_ap_original_button"):
    st._ap_original_button = st.button


def _ap_button(*args, **kwargs):
    key = kwargs.get("key")

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


def _nav_group(label):
    if st.session_state.sidebar_minimized:
        st.markdown('<div class="nav-group-mini"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="nav-group">{label}</div>', unsafe_allow_html=True)


def show_sidebar():
    with st.sidebar:

        _sidebar_brand()

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


def _nav_item(icon, label):
    if not can_access_menu(label):
        return

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
    if not can_access_menu(label):
        return

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
            f'padding-top:0;">{title}</h2>',
            unsafe_allow_html=True
        )
    if show_search:
        with n2:
            st.text_input("search", placeholder="🔍  Searching anything...",
                          label_visibility="collapsed", key="search_bar")
    with n3:
        user_name = escape(st.session_state.user_name or "User")
        role_label = "Admin" if get_current_role() == Role.ADMIN else "Analyst"
        st.markdown(f"""
        <div class="ap-top-actions">
            <div class="ap-top-bell">🔔</div>
            <details class="ap-profile-details">
                <summary aria-label="Profile menu">
                    <span class="ap-profile-avatar" title="{user_name}"></span>
                    <span class="ap-user-meta">
                        <span>{user_name}</span>
                        <span class="ap-user-role">{role_label}</span>
                    </span>
                </summary>
                <div class="ap-profile-menu">
                    <a class="ap-profile-menu-item" href="#settings">
                        <span class="ap-profile-menu-icon">⚙</span>
                        <span>Settings</span>
                    </a>
                    <a class="ap-profile-menu-item" href="?ap_logout=1">
                        <span class="ap-profile-menu-icon">↪</span>
                        <span>Logout</span>
                    </a>
                </div>
            </details>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('<div class="nad-top-divider"></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════
def page_overview(df_raw):
    show_topnav("Overview", show_search=False)

    for key in ["show_all_rev", "show_all_best", "show_all_detail", "overview_detail_page"]:
        if key not in st.session_state:
            st.session_state[key] = 1 if key == "overview_detail_page" else False

    terminal_options = ["All Terminal"] + sorted(df_raw["terminal"].dropna().unique().tolist())
    year_options = ["Semua Tahun"] + sorted(df_raw["tahun"].dropna().unique().tolist(), reverse=True)
    month_options = ["Semua Bulan"] + BULAN

    if st.session_state.get("f_terminal") not in terminal_options:
        st.session_state.f_terminal = terminal_options[0]
    if st.session_state.get("f_tahun") not in year_options:
        st.session_state.f_tahun = year_options[0]
    if st.session_state.get("f_masa") not in month_options:
        st.session_state.f_masa = month_options[0]

    f1, f2, f3, f4 = st.columns([1.35, 1.05, 1.45, 3.3])
    with f1:
        sel_terminal = st.selectbox("Terminal", terminal_options, key="f_terminal")
    with f2:
        sel_tahun = st.selectbox("Tahun", year_options, key="f_tahun")
    with f3:
        sel_masa = st.selectbox("Bulan", month_options, key="f_masa")
    with f4:
        st.markdown(
            '<div style="height:52px;display:flex;align-items:end;justify-content:flex-end;'
            'color:#64748B;font-size:12px;font-weight:650;">Data terakhir diperbarui: 02 Jun 2025 10:30 WIB</div>',
            unsafe_allow_html=True,
        )

    df = df_raw.copy()
    if sel_terminal != "All Terminal": df = df[df["terminal"]  == sel_terminal]
    if sel_tahun    != "Semua Tahun":  df = df[df["tahun"]     == int(sel_tahun)]
    if sel_masa     != "Semua Bulan":  df = df[df["masa_jasa"] == sel_masa]

    real_revenue = df["real_omzet"].sum()
    revenue_sharing = df["pendapatan_rs"].sum()
    total_contribution = df["kontribusi"].sum()
    acv_value = df["acv"].mean() if not df.empty else 0

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(_overview_kpi_card("Real Revenue (Omzet)", _fmt_rp_compact(real_revenue), "5.2%", "#2563EB", "Rp"), unsafe_allow_html=True)
    with k2:
        st.markdown(_overview_kpi_card("Revenue Sharing", _fmt_rp_compact(revenue_sharing), "2.3%", "#7C3AED", "%"), unsafe_allow_html=True)
    with k3:
        st.markdown(_overview_kpi_card("Total Contribution", _fmt_rp_compact(total_contribution), "4.2%", "#059669", "+"), unsafe_allow_html=True)
    with k4:
        st.markdown(_overview_kpi_card("ACV", f"{acv_value:.2f}%", "8.4%", "#EA580C", "ACV"), unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    main_left, main_right = st.columns([65, 35])
    with main_left:
        trend_card = st.container()
        with trend_card:
            _ed_card_marker(trend_card)
            th1, th2 = st.columns([4, 1])
            with th1:
                st.markdown('<p class="ed-section-title">Revenue Trend</p><p class="ed-section-sub">Monthly revenue, sharing, and contribution in Rp billion</p>', unsafe_allow_html=True)
            with th2:
                st.selectbox("Trend period", ["Monthly"], key="overview_trend_period", label_visibility="collapsed")

            trend = (
                df.groupby("masa_jasa")
                .agg(
                    real_revenue=("real_omzet", "sum"),
                    revenue_sharing=("pendapatan_rs", "sum"),
                    contribution=("kontribusi", "sum"),
                )
                .reindex(BULAN, fill_value=0)
                .reset_index()
                .rename(columns={"index": "masa_jasa"})
            )
            trend["month"] = trend["masa_jasa"].astype(str).str[:3]
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=trend["month"], y=trend["real_revenue"] / 1_000_000_000,
                mode="lines+markers", name="Real Revenue",
                line=dict(color="#2563EB", width=2.5), marker=dict(size=6),
            ))
            fig.add_trace(go.Scatter(
                x=trend["month"], y=trend["revenue_sharing"] / 1_000_000_000,
                mode="lines+markers", name="Revenue Sharing",
                line=dict(color="#7C3AED", width=2.5), marker=dict(size=6),
            ))
            fig.add_trace(go.Scatter(
                x=trend["month"], y=trend["contribution"] / 1_000_000_000,
                mode="lines+markers", name="Contribution",
                line=dict(color="#059669", width=2.5), marker=dict(size=6),
            ))
            fig.update_layout(
                height=320,
                margin=dict(t=20, b=8, l=8, r=8),
                plot_bgcolor="#ffffff",
                paper_bgcolor="#ffffff",
                hovermode="x unified",
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(size=11, color="#475569"),
                ),
                xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#64748B"), fixedrange=True),
                yaxis=dict(
                    title=dict(text="Rp Miliar", font=dict(size=11, color="#64748B")),
                    showgrid=True,
                    gridcolor="#E2E8F0",
                    zeroline=False,
                    tickfont=dict(size=11, color="#64748B"),
                    fixedrange=True,
                ),
            )
            st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with main_right:
        alert_card = st.container()
        with alert_card:
            _ed_card_marker(alert_card)
            ah1, ah2 = st.columns([3, 1])
            with ah1:
                st.markdown('<p class="ed-section-title">Alert & Insight</p><p class="ed-section-sub">Highlights requiring analyst attention</p>', unsafe_allow_html=True)
            with ah2:
                st.markdown('<div class="ed-card-action">Lihat semua</div>', unsafe_allow_html=True)

            trend_nonzero = trend[trend["real_revenue"] > 0]
            if len(trend_nonzero) >= 2:
                current_rev = trend_nonzero.iloc[-1]["real_revenue"]
                prev_rev = trend_nonzero.iloc[-2]["real_revenue"]
                rev_change = ((current_rev - prev_rev) / prev_rev * 100) if prev_rev else 0
            else:
                rev_change = 0
            low_acv = int((df["acv"] < 80).sum()) if not df.empty else 0
            terminal_sum = df.groupby("terminal")["kontribusi"].sum()
            top_terminal = terminal_sum.idxmax() if len(terminal_sum) else "Terminal 1"
            top_terminal_share = int((terminal_sum.max() / terminal_sum.sum()) * 100) if terminal_sum.sum() else 0
            alerts = [
                _alert_item_html("!", "#DC2626", f"Revenue {'turun' if rev_change < 0 else 'naik'} {abs(rev_change):.1f}% dibanding periode lalu", f"Realisasi periode aktif: {_fmt_rp_compact(real_revenue)}"),
                _alert_item_html("A", "#EA580C", f"{low_acv} tenant memiliki ACV < 80%", "Perlu perhatian untuk potensi risiko"),
                _alert_item_html("i", "#2563EB", f"{top_terminal} menyumbang {top_terminal_share}% kontribusi", "Monitor perubahan komposisi terminal"),
            ]
            st.markdown(f'<div class="ed-alert-list">{"".join(alerts)}</div>', unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    top_rev, top_acv = st.columns(2)
    tenant_summary = (
        df.groupby(["perusahaan", "brand"])
        .agg(real_revenue=("real_omzet", "sum"), acv=("acv", "mean"), contribution=("kontribusi", "sum"))
        .reset_index()
    )
    if tenant_summary.empty:
        tenant_summary = pd.DataFrame(columns=["perusahaan", "brand", "real_revenue", "acv", "contribution"])

    with top_rev:
        df_top_rev = tenant_summary.sort_values("real_revenue", ascending=False).head(5).copy()
        df_top_rev.insert(0, "#", range(1, len(df_top_rev) + 1))
        df_top_rev["Real Revenue"] = df_top_rev["real_revenue"].apply(_fmt_rp_compact)
        df_top_rev["ACV"] = df_top_rev["acv"].apply(lambda x: f"{x:.1f}%")
        df_top_rev = df_top_rev[["#", "perusahaan", "brand", "Real Revenue", "ACV"]]
        df_top_rev.columns = ["#", "Tenant", "Brand", "Real Revenue", "ACV"]
        st.markdown(_enterprise_table_html(df_top_rev, "Top Revenue Tenant", "Lihat semua"), unsafe_allow_html=True)

    with top_acv:
        df_top_acv = tenant_summary.sort_values("acv", ascending=False).head(5).copy()
        df_top_acv.insert(0, "#", range(1, len(df_top_acv) + 1))
        df_top_acv["ACV"] = df_top_acv["acv"].apply(lambda x: f"{x:.1f}%")
        df_top_acv["Contribution"] = df_top_acv["contribution"].apply(_fmt_rp_compact)
        df_top_acv = df_top_acv[["#", "perusahaan", "brand", "ACV", "Contribution"]]
        df_top_acv.columns = ["#", "Tenant", "Brand", "ACV", "Contribution"]
        st.markdown(_enterprise_table_html(df_top_acv, "Top ACV Tenant", "Lihat semua"), unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    detail_card = st.container()
    with detail_card:
        _ed_card_marker(detail_card)
        dh1, ds, dfb, dex, dpp = st.columns([4.2, 1.9, 0.8, 0.8, 0.9])
        with dh1:
            st.markdown('<p class="ed-section-title">Detail Revenue Tenant</p><p class="ed-section-sub">Detailed tenant performance for the active filter context</p>', unsafe_allow_html=True)
        with ds:
            search_query = st.text_input("Search tenant", placeholder="Cari tenant atau brand...", key="overview_detail_search", label_visibility="collapsed")
        with dfb:
            if st.button("Filter", key="overview_detail_filter", width="stretch"):
                st.session_state.overview_detail_page = 1
                st.rerun()

        detail_df = df[["perusahaan", "brand", "kode_ruang", "min_omzet", "real_omzet", "kontribusi", "acv"]].copy()
        if search_query:
            q = search_query.lower().strip()
            detail_df = detail_df[
                detail_df["perusahaan"].astype(str).str.lower().str.contains(q, na=False)
                | detail_df["brand"].astype(str).str.lower().str.contains(q, na=False)
                | detail_df["kode_ruang"].astype(str).str.lower().str.contains(q, na=False)
            ]

        export_df = detail_df.copy()
        with dex:
            st.download_button(
                "Export",
                data=export_df.to_csv(index=False).encode("utf-8"),
                file_name="detail_revenue_tenant.csv",
                mime="text/csv",
                key="overview_detail_export",
                width="stretch",
            )
        with dpp:
            rows_per_page = st.selectbox("Rows per page", [10, 25, 50], key="overview_rows_per_page", label_visibility="collapsed")

        detail_df["Ach %"] = np.where(detail_df["min_omzet"] > 0, detail_df["real_omzet"] / detail_df["min_omzet"] * 100, 0)
        total_rows = len(detail_df)
        total_pages = max(1, int(np.ceil(total_rows / rows_per_page)))
        if st.session_state.overview_detail_page > total_pages:
            st.session_state.overview_detail_page = total_pages
        if st.session_state.overview_detail_page < 1:
            st.session_state.overview_detail_page = 1

        start_idx = (st.session_state.overview_detail_page - 1) * rows_per_page
        end_idx = start_idx + rows_per_page
        detail_view = detail_df.iloc[start_idx:end_idx].copy()
        detail_view["Min Omzet"] = detail_view["min_omzet"].apply(_fmt_rp_full)
        detail_view["Real Omzet"] = detail_view["real_omzet"].apply(_fmt_rp_full)
        detail_view["Kontribusi"] = detail_view["kontribusi"].apply(_fmt_rp_full)
        detail_view["Ach %"] = detail_view["Ach %"].apply(lambda x: f"{x:.1f}%")
        detail_view["ACV"] = detail_view["acv"].apply(lambda x: f"{x:.1f}%")
        detail_view = detail_view[["perusahaan", "brand", "kode_ruang", "Min Omzet", "Real Omzet", "Kontribusi", "Ach %", "ACV"]]
        detail_view.columns = ["Tenant", "Brand", "Kode Ruang", "Min Omzet", "Real Omzet", "Kontribusi", "Ach %", "ACV"]
        st.markdown(_enterprise_table_inner_html(detail_view), unsafe_allow_html=True)

        p1, p2, p3, p4 = st.columns([4, 0.7, 0.9, 0.7])
        with p1:
            first_item = 0 if total_rows == 0 else start_idx + 1
            last_item = min(end_idx, total_rows)
            st.markdown(f'<div class="ed-pagination">{first_item} - {last_item} dari {total_rows} data</div>', unsafe_allow_html=True)
        with p2:
            if st.button("<", key="overview_prev_page", width="stretch", disabled=st.session_state.overview_detail_page <= 1):
                st.session_state.overview_detail_page -= 1
                st.rerun()
        with p3:
            st.markdown(f'<div class="ed-pagination" style="justify-content:center;">Page {st.session_state.overview_detail_page} / {total_pages}</div>', unsafe_allow_html=True)
        with p4:
            if st.button(">", key="overview_next_page", width="stretch", disabled=st.session_state.overview_detail_page >= total_pages):
                st.session_state.overview_detail_page += 1
                st.rerun()


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
def init_dashboard_state():
    init_auth_state()
    defaults = {
        "active_menu": "Overview",
        "sidebar_minimized": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    st.session_state.sidebar_minimized = False

    if not can_access_menu(st.session_state.active_menu):
        st.session_state.active_menu = "Overview"


def handle_logout_query():
    if st.query_params.get("ap_logout") != "1":
        return
    st.query_params.clear()
    logout_user()
    st.rerun()


def render_dashboard_app():
    init_dashboard_state()
    handle_logout_query()
    inject_dashboard_css()

    st.markdown(
        f'<div class="ap-sidebar-state {"is-mini" if st.session_state.sidebar_minimized else "is-expanded"}"></div>',
        unsafe_allow_html=True,
    )

    df_raw = get_active_dashboard_data()
    show_sidebar()

    menu = st.session_state.active_menu

    if menu == "Overview":
        page_overview(df_raw)
    elif menu == "Revenue Sharing":
        page_revenue_sharing()
    elif menu == "Accrual & Billing":
        page_accrual_billing()
    elif menu == "Import Manager":
        render_import_manager()
    elif menu == "Room Database":
        render_room_database()
    elif menu == "Lease Contract":
        render_lease_contract()
    elif menu == "Data Verification":
        render_data_verification()
    else:
        page_overview(df_raw)


def main():
    st.set_page_config(
        page_title="Non Aeronautical Dashboard",
        page_icon="A",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    init_auth_state()

    if os.getenv("DEV_BYPASS_LOGIN", "false").lower() == "true":
        st.session_state.authenticated = True
        st.session_state.user_name = st.session_state.get("user_name", "Developer")
        st.session_state.user_role = st.session_state.get("user_role", Role.ADMIN)

    if not is_authenticated():
        from login.app import render_current_page as render_login_page

        render_login_page()
        st.stop()

    render_dashboard_app()


if __name__ == "__main__":
    main()
