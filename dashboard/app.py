from .navigation import show_topnav, topnav_actions_html
from .accrual_billing import page_accrual_billing
from .revenue_sharing import page_revenue_sharing
from .room_database import render_room_database
from .lease_contract import render_lease_contract
from .import_manager import render_import_manager
from .Data_verification import render_data_verification
from .traffic_monitor import page_traffic_monitor
from .dashboard_style import DASHBOARD_CSS
from .pagination import render_pagination, patch_pagination
from login.access_control import (
    IDLE_TIMEOUT_SECONDS,
    IDLE_WARNING_LEAD_SECONDS,
    Role,
    get_current_role,
    init_auth_state,
    is_authenticated,
    session_time_remaining,
)
from .session_watchdog import inject_session_watchdog
from .shared_import import get_shared_import_data, has_dashboard_ready_import, import_status_html
import streamlit as st
import streamlit.components.v1 as components
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

OVERVIEW_FONT_FAMILY = "Inter, sans-serif"

# ─────────────────────────────────────────────
# LOAD CSS
# ─────────────────────────────────────────────
def inject_dashboard_css():
    st.markdown(f"<style>{DASHBOARD_CSS}</style>", unsafe_allow_html=True)
    st.markdown("""
    <style>
    /* Hide the invisible iframes used by the session watchdog / cookie
       manager components (session persistence + idle-timeout tracking) —
       without this they leave a thin blank gap that pushes page content
       down, since they're still a normal (non-collapsed) flex item even
       though there's nothing visible inside. */
    div[data-testid="stElementContainer"]:has(iframe[height="0"]) {
        display: none !important;
    }
    .ap-top-actions {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 8px; /* reduced gap */
        padding-top: 0;
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
        background: #ffffff;
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
        background: #ffffff;
        transform: translateX(-50%);
    }
    .ap-profile-menu {
        position: absolute;
        right: 0;
        top: 48px;
        z-index: 9999;
        width: 132px;
        padding: 4px 0;
        border-radius: 10px;
        background: linear-gradient(135deg, rgba(244,114,182,0.10), rgba(255,255,255,0.32));
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(255,255,255,0.35);
        box-shadow: 0 8px 18px rgba(15,23,42,0.10);
        overflow: hidden;
    }
    .ap-profile-menu-item {
        height: 32px;
        padding: 0 12px;
        color: #334155 !important;
        text-decoration: none !important;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        font-weight: 600;
        white-space: nowrap;
        background: transparent;
        transition: background 0.15s ease;
    }
    .ap-profile-menu-item:hover {
        background: rgba(99,102,241,0.08);
        color: #4f46e5 !important;
    }
    .ap-profile-menu-item.is-danger {
        color: #DC2626 !important;
    }
    .ap-profile-menu-item.is-danger:hover {
        background: linear-gradient(135deg, rgba(244,63,94,0.10), rgba(168,85,247,0.10));
        color: #DC2626 !important;
    }
    .ap-profile-menu-icon {
        width: 14px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: inherit;
        text-align: center;
        font-size: 13px;
    }
    #MainMenu,
    footer,
    header,
    [data-testid="stHeader"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarHeader"],
    [data-testid="collapsedControl"] {
        display: none !important;
        height: 0 !important;
        visibility: hidden !important;
    }
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0 !important;
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
        margin-top: 20px !important;
        padding: 10px 14px 16px !important;
        margin-bottom: 35px !important;
    }
    .ap-brand-mini {
        margin-top: 20px !important;
        padding: 10px 0 12px !important;
        margin-bottom: 35px !important;
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
        font-family: 'Inter', sans-serif !important;
    }

    .overview-light-table thead {
        background: rgba(99, 102, 241, 0.06);
    }

    .overview-light-table th {
        padding: 12px 16px;
        text-align: left;
        font-size: 11px;
        font-weight: 700;
        color: #4F46E5;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: none;
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
        gap: 8px; /* reduced gap */
        padding-top: 0;
        min-height: 38px;
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

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .main,
    section.main {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    .block-container {
        max-width: 100% !important;
        padding: 0 28px 34px !important;
        margin-top: 0 !important;
    }

    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewContainer"] .block-container,
    section.main > div,
    .main > div {
        padding-top: 0 !important;
        padding-bottom: 34px !important;
        margin-top: 0 !important;
    }

    .dashboard-container,
    .page-container,
    .content-wrapper,
    .main-content,
    .overview-container {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #E5E7EB !important;
        box-shadow: none !important;
        min-width: 258px !important;
        width: 258px !important;
        max-width: 258px !important;
    }

    [data-testid="stSidebarContent"] {
        background: #ffffff !important;
        padding-top: 24px !important;
    }

    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebarContent"] > div,
    [data-testid="stSidebarContent"] [data-testid="stVerticalBlock"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Pin only the footer to the bottom of the sidebar — position:absolute
       takes it completely out of normal flow, so it cannot affect (or be
       affected by) the layout of the brand/nav items above it. */
    [data-testid="stSidebar"] {
        position: relative !important;
    }
    [data-testid="stSidebarContent"] div[data-testid="stElementContainer"]:has(.ap-sidebar-footer) {
        position: absolute !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 18px !important;
        margin: 0 !important;
    }
    .ap-brand {
        margin: 0 !important;
        padding: 16px 24px 16px !important;
        display: flex !important;
        align-items: center !important;
        border-bottom: 1px solid #E5E7EB !important;
    }

    .ap-logo {
        width: 36px !important;
        height: 36px !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .ap-brand-name {
        color: #0F172A !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        letter-spacing: -0.2px !important;
        font-family: 'Montserrat', sans-serif !important;
        white-space: nowrap !important;
        line-height: 1 !important;
    }

    .ap-brand-copy {
        min-width: 0 !important;
        flex: 1 1 auto !important;
    }

    .ap-brand-sub {
        color: #6366F1 !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        letter-spacing: 0px !important;
        line-height: 1 !important;
        margin-top: 4px !important;
        font-family: 'Inter', sans-serif !important;
    }

    .ap-toolbar-title {
        padding: 22px 24px 8px !important;
        color: #94A3B8 !important;
        font-size: 10px !important;
        letter-spacing: 1.2px !important;
    }

    .nav-category-header {
        font-size: 10px !important;
        font-weight: 800 !important;
        color: #94A3B8 !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
        margin: 20px 24px 28px !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    .nav-group {
        display: none !important;
    }

    .nav-row,
    .nav-active {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0 14px 2px !important;
        padding: 5px 12px;
        border-radius: 10px;
        color: #64748B;
        font-size: 13px;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
        line-height: 1.2;
        box-sizing: border-box !important;
        width: calc(100% - 28px) !important;
        max-width: calc(100% - 28px) !important;
        height: 36px !important;
        position: relative;
    }

    .nav-icon-box {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 7px;
        flex-shrink: 0;
        box-sizing: border-box !important;
        transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease !important;
    }

    .nav-icon-box svg {
        width: 16px;
        height: 16px;
        display: block;
    }

    .nav-label {
        flex-shrink: 0;
        overflow: visible;
        white-space: nowrap;
        letter-spacing: -0.15px;
        color: inherit;
        font-family: 'Inter', sans-serif !important;
    }

    .nav-overlay {
        pointer-events: none;
        position: relative;
        z-index: 1;
        background: transparent !important;
        border: 1px solid transparent !important;
    }

    .nav-active {
        margin: 0 14px 2px !important;
        padding: 5px 14px 5px 10px !important;
        border-radius: 12px !important;
        background: #F5F3FF !important;
        border: 1px solid #DDD6FE !important;
        box-shadow: none !important;
        color: #7C3AED !important;
        font-weight: 700 !important;
        height: 36px !important;
        width: calc(100% - 28px) !important;
        max-width: calc(100% - 28px) !important;
    }

    .nav-active .nav-icon-box {
        background-color: #EDE9FE !important;
        color: #7C3AED !important;
    }

    .nav-row .nav-icon-box {
        background-color: #F8FAFC !important;
        color: #64748B !important;
        border: 1px solid #F1F5F9 !important;
    }

    .nav-indicator-pill {
        position: absolute;
        left: 0;
        top: 5px;
        bottom: 5px;
        width: 3.5px;
        background: linear-gradient(180deg, #A78BFA 0%, #7C3AED 100%);
        border-radius: 0 4px 4px 0;
    }

    .nav-badge {
        margin-left: auto;
        background: linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%);
        color: #ffffff;
        font-size: 10.5px;
        font-weight: 700;
        padding: 2.5px 8.5px;
        border-radius: 20px;
        box-shadow: 0 2.5px 7px rgba(6, 182, 212, 0.25);
    }

    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(.nav-overlay) {
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(.nav-overlay) [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(.nav-overlay) [data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(div[data-testid="stButton"]) {
        margin-bottom: -36px !important;
        position: relative;
        z-index: 2;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] {
        margin: 0 14px 2px !important;
        padding: 0 !important;
        height: 36px !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] > button {
        height: 36px !important;
        min-height: 36px !important;
        opacity: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        cursor: pointer !important;
        transition: none !important;
        width: 100% !important;
    }

    /* Hover effects */
    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(div[data-testid="stButton"]):hover + div[data-testid="stElementContainer"] .nav-row.nav-overlay {
        background: rgba(241, 245, 249, 0.5) !important;
        color: #1E293B !important;
        border-radius: 12px !important;
    }

    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(div[data-testid="stButton"]):hover + div[data-testid="stElementContainer"] .nav-row.nav-overlay .nav-icon-box {
        background-color: #E2E8F0 !important;
        color: #1E293B !important;
    }

    .ap-sidebar-footer {
        margin: 0 16px 18px !important;
        padding: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        text-align: center !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        color: #94A3B8 !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.2px !important;
        line-height: 1.5 !important;
        white-space: normal !important;
    }

    .ap-sidebar-spacer {
        height: 20px !important;
        min-height: 20px !important;
    }

    .ap-sidebar-status {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #475569;
        font-size: 11px;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
    }

    .ap-status-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: #10B981;
        flex: 0 0 8px;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.18);
    }

    .ap-sidebar-sync {
        margin-top: 6px;
        color: #94A3B8;
        font-size: 10px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        min-height: 100% !important;
        gap: 0px !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] {
        padding: 0 16px !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] > button {
        height: 36px !important;
        min-height: 36px !important;
        padding: 0 14px !important;
        border-radius: 12px !important;
        color: #475569 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        background: transparent !important;
        justify-content: flex-start !important;
        text-align: left !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: transparent !important;
        background-color: transparent !important;
        color: transparent !important;
        opacity: 0 !important;
        box-shadow: none !important;
        border: none !important;
    }

    .nad-top-divider {
        height: 1px !important;
        margin: 8px 0 14px !important;
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
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        border: none !important;
        box-shadow: 0 3px 10px rgba(99, 102, 241, 0.30) !important;
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
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
    }

    .overview-filter-spacer {
        height: 2px;
    }

    .overview-page-marker {
        display: none;
    }

    /* The marker's own wrapper still occupies a flex slot in Streamlit's
       vertical block (contributing a default "gap" before the next element)
       even though its content is display:none. Remove the wrapper itself
       from flow so it doesn't add unwanted spacing. */
    div[data-testid="stElementContainer"]:has(.overview-page-marker) {
        display: none !important;
    }

    /* ── Overview header — identical mechanism to Traffic Monitor's header:
       position:fixed (pinned to the viewport, immune to normal-flow gaps),
       sized to land its bottom border on the sidebar's divider line:
       stSidebarContent padding-top (24px) + .ap-brand box
       (13px + 42px logo + 13px padding + 1px border) = 93px. */
    body:has(.overview-page-marker) .ov-fixed-header-active {
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
    body:has(.overview-page-marker) .ov-fixed-header-spacer {
        display: block !important;
        height: 93px !important;
        min-height: 93px !important;
        max-height: 93px !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100%;
        flex-shrink: 0;
    }
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-fixed-header-spacer) {
        margin: 0 !important;
        padding: 0 !important;
        height: 93px !important;
        min-height: 93px !important;
        max-height: 93px !important;
    }
    /* Collapse the invisible JS-mount component (iframe) so it doesn't add
       its own default element spacing between the spacer and the filters. */
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(> iframe) {
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
    }
    /* Pull the filter card up to close the remaining default Streamlit gap
       after the (mandatory, fixed-height) spacer — keeps it compact/close
       to the header without overlapping the fixed header itself. */
    body:has(.overview-page-marker) div[data-testid="stHorizontalBlock"]:has(.ov-filtercard-marker) {
        margin-top: -24px !important;
    }
    body:has(.overview-page-marker) div[data-testid="stHorizontalBlock"]:has(.overview-kpi-card) {
        margin-top: 0 !important;
    }
    body:has(.overview-page-marker) .ov-sticky-header-marker,
    body:has(.overview-page-marker) .ov-sticky-header-end {
        display: none;
    }
    body:has(.overview-page-marker) [data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ov-sticky-header-marker) {
        gap: 0 !important;
        height: 100% !important;
        justify-content: center !important;
    }
    body:has(.overview-page-marker) [data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ov-sticky-header-marker) > div[data-testid="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-sticky-header-marker) {
        height: 100% !important;
        display: flex !important;
        align-items: center !important;
    }
    body:has(.overview-page-marker) .ov-page-header {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100%;
        gap: 16px;
        height: 100%;
    }
    body:has(.overview-page-marker) .ov-page-header-left {
        display: flex; align-items: center; gap: 12px; min-width: 0;
    }
    body:has(.overview-page-marker) .ov-page-icon {
        width: 36px; height: 36px; flex: 0 0 36px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
        color: #ffffff; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.18);
    }
    body:has(.overview-page-marker) .ov-page-icon svg {
        width: 18px; height: 18px;
    }
    body:has(.overview-page-marker) .ov-page-header-copy {
        display: flex; flex-direction: column; justify-content: center; gap: 4px !important;
        min-height: 36px; min-width: 0;
    }
    body:has(.overview-page-marker) .ov-page-title-row {
        display: flex; align-items: center; gap: 10px; min-height: 0 !important;
        margin: 0 !important; padding: 0 !important;
    }
    body:has(.overview-page-marker) h2.ov-page-title {
        margin: 0 !important; padding: 0 !important;
        font-size: 18px; line-height: 1 !important; font-weight: 800;
        color: #0F172A; font-family: 'Montserrat', sans-serif !important;
    }
    body:has(.overview-page-marker) p.ov-page-sub {
        margin: 0 !important; padding: 0 !important;
        color: #64748B; font-size: 12px; line-height: 1 !important;
        font-weight: 500; font-family: 'Inter', sans-serif !important;
    }
    /* Beda ukuran judul/sub-judul tiap card di halaman ini, mengikuti
       kontras yang dipakai pada header halaman (h2.ov-page-title vs
       p.ov-page-sub). */
    body:has(.overview-page-marker) .ed-section-title {
        font-size: 16px !important;
        font-weight: 800 !important;
    }
    body:has(.overview-page-marker) .ed-section-sub {
        font-size: 11px !important;
        font-weight: 500 !important;
    }
    body:has(.overview-page-marker) .ap-top-actions {
        flex-shrink: 0;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] > div > div {
        position: relative !important;
        display: flex !important;
        align-items: center !important;
        padding-right: 10px !important;
        min-height: 40px !important;
        overflow: visible !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] > div > div::after {
        content: none !important;
        display: none !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] div[data-baseweb="select"] {
        width: 100% !important;
        min-width: 0 !important;
        overflow: visible !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 8px !important;
        padding: 0 4px 0 10px !important;
        min-height: 38px !important;
        box-sizing: border-box !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        display: flex !important;
        align-items: center !important;
        line-height: 1.25 !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child {
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"],
    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
        line-height: 1.25 !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] svg {
        opacity: 1 !important;
        color: #64748B !important;
        fill: #64748B !important;
        width: 14px !important;
        height: 14px !important;
        flex: 0 0 14px !important;
        align-self: center !important;
        margin: 0 !important;
        position: static !important;
        transform: none !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] div[data-baseweb="select"] span,
    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: nowrap !important;
        max-width: none !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) {
        align-items: stretch !important;
        display: flex !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-self: stretch !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
        width: 100% !important;
        flex: 1 1 auto !important;
        display: flex !important;
        flex-direction: column !important;
        margin: 0 !important;
        padding: 0 !important;
        min-height: 100% !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .overview-trend-card),
    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .overview-alert-card) {
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 auto !important;
        height: 100% !important;
        min-height: 100% !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
        padding: 16px !important;
        margin: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) > div[data-testid="stElementContainer"] {
        margin-bottom: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) > div[data-testid="stElementContainer"]:last-child {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(.overview-trend-card) > div[data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]) {
        flex: 1 1 auto !important;
        display: flex !important;
        flex-direction: column !important;
        min-height: 0 !important;
        overflow: hidden !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(.overview-trend-card) [data-testid="stPlotlyChart"] {
        flex: 1 1 auto !important;
        min-height: 0 !important;
        height: 100% !important;
        overflow: hidden !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(.overview-trend-card) [data-testid="stPlotlyChart"] > div,
    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(.overview-trend-card) [data-testid="stPlotlyChart"] .js-plotly-plot {
        height: 100% !important;
        min-height: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(.overview-alert-card) .ed-alert-list {
        flex: 1 1 auto !important;
        margin-bottom: 0 !important;
        min-height: 0 !important;
    }
    
    /* Ratakan selectbox rows ke tengah vertikal baris header detail */
    div[data-testid="stHorizontalBlock"]:has(.ed-table-card) 
    [data-testid="stSelectbox"] {
        margin-top: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.ed-table-card) 
    [data-testid="stSelectbox"] > label {
        display: none !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.ed-table-card) 
    [data-testid="stSelectbox"] > div {
        margin-top: 0 !important;
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
        font-weight: 800;
        font-family: 'Inter', sans-serif !important;
    }

    .overview-kpi-copy {
        min-width: 0;
    }

    .overview-kpi-label {
        color: #475569;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        font-family: 'Inter', sans-serif !important;
    }

    .overview-kpi-value {
        margin-top: 7px;
        color: #0F172A;
        font-size: 26px;
        font-weight: 800;
        line-height: 1.05;
        letter-spacing: 0 !important;
        font-family: 'Inter', sans-serif !important;
    }

    .overview-kpi-delta {
        margin-top: 10px;
        color: #64748B;
        font-size: 11px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
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

    .kpi-pro-card {
        display: flex;
        flex-direction: column;
        gap: 11px;
        min-height: 170px;
        padding: 18px 20px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        background: #ffffff;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }

    .kpi-pro-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .kpi-pro-icon {
        width: 40px;
        height: 40px;
        flex: 0 0 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
    }

    .kpi-pro-icon svg {
        width: 20px;
        height: 20px;
    }

    .kpi-pro-badge {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        background: #DCFCE7;
        color: #16A34A;
        white-space: nowrap;
    }

    .kpi-pro-badge.is-down {
        background: #FEE2E2;
        color: #DC2626;
    }

    .kpi-pro-body {
        min-width: 0;
    }

    .kpi-pro-label {
        color: #64748B;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }

    .kpi-pro-value-row {
        display: flex;
        align-items: baseline;
        gap: 6px;
        margin-top: 7px;
    }

    .kpi-pro-value {
        color: #0F172A;
        font-size: 25px;
        font-weight: 800;
        line-height: 1.1;
    }

    .kpi-pro-unit {
        color: #94A3B8;
        font-size: 12px;
        font-weight: 600;
    }

    .kpi-pro-sub {
        margin-top: 6px;
        color: #94A3B8;
        font-size: 11.5px;
        font-weight: 500;
    }

    .kpi-pro-foot {
        margin-top: auto;
    }

    .kpi-pro-bar-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .kpi-pro-bar-row span:first-child {
        color: #94A3B8;
        font-weight: 500;
    }

    .kpi-pro-bar-track {
        height: 5px;
        border-radius: 999px;
        background: #F1F5F9;
        overflow: hidden;
    }

    .kpi-pro-bar-fill {
        height: 100%;
        border-radius: 999px;
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker):not(
        :has(div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] .ed-card-marker)
    ) {
        position: relative;
        overflow: hidden;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        background: #ffffff;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker):not(
        :has(div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] .ed-card-marker)
    )
    > div[data-testid="stElementContainer"]:has(.ed-card-marker) {
        display: none;
    }

    .ed-card-marker {
        display: none;
    }

    .ed-section-title {
        margin: 0;
        color: #0F172A;
        font-size: 15px;
        font-weight: 700;
        font-family: 'Montserrat', sans-serif !important;
    }

    .ed-section-sub {
        margin: 3px 0 0;
        color: #64748B;
        font-size: 11px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-card-action {
        text-align: right;
        color: #2563EB;
        font-size: 12px;
        font-weight: 700;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-alert-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 12px;
        margin-bottom: 14px;
        flex: 1 1 auto;
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
        font-weight: 700;
        line-height: 1.35;
        font-family: 'Montserrat', sans-serif !important;
    }

    .ed-alert-sub {
        margin: 4px 0 0;
        color: #64748B;
        font-size: 11.5px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-table-card {
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        background: #ffffff;
        box-shadow: 0 4px 18px rgba(15, 23, 42, 0.05);
        overflow: hidden;
    }

    .ed-table-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 18px 18px 14px;
    }

    .ed-table-head-stack {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
        padding: 18px 18px 12px;
    }

    .ed-table-head-copy {
        min-width: 0;
    }

    .ed-table-title {
        margin: 0;
        color: #0F172A;
        font-size: 15px;
        font-weight: 700;
        font-family: 'Montserrat', sans-serif !important;
    }

    .ed-table-subtitle {
        margin: 4px 0 0;
        color: #64748B;
        font-size: 11px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-table-link {
        color: #2563EB;
        font-size: 12px;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
        text-decoration: none;
        white-space: nowrap;
    }

    .ed-table-link-with-icon {
        display: inline-flex;
        align-items: center;
        justify-content: flex-end;
        gap: 6px;
        padding-top: 2px;
    }

    .ed-view-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 16px;
        height: 16px;
        color: #2563EB;
        font-size: 13px;
        line-height: 1;
    }

    .ed-table-scroll {
        width: 100%;
        overflow-x: auto;
        padding: 0 14px 14px;
        box-sizing: border-box;
    }

    .ed-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        color: #0F172A;
        font-size: 12px;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-table thead tr {
        background: rgba(99, 102, 241, 0.06);
        border-radius: 10px;
        overflow: hidden;
    }

    .ed-table th {
        padding: 11px 16px;
        background: transparent;
        border: none;
        color: #4F46E5;
        font-size: 11px;
        font-weight: 700;
        text-align: left;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-table th:first-child {
        border-top-left-radius: 10px;
        border-bottom-left-radius: 10px;
    }

    .ed-table th:last-child {
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
    }

    .ed-table th.ed-th-right,
    .ed-table td.ed-td-right {
        text-align: right;
    }

    .ed-table th.ed-th-center,
    .ed-table td.ed-td-center {
        text-align: center;
    }

    .ed-table td {
        padding: 11px 14px;
        border-bottom: 1px solid #F1F5F9;
        color: #0F172A;
        font-size: 12px;
        font-weight: 500;
        white-space: nowrap;
        font-family: 'Inter', sans-serif !important;
        background: #ffffff;
    }

    .ed-table tbody tr:hover td {
        background: #FAFAFF;
    }

    .ed-table tbody tr:last-child td {
        border-bottom: none;
    }

    .ed-value-blue {
        color: #2563EB;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-rank-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        margin-right: 8px;
        vertical-align: middle;
        flex: 0 0 22px;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-rank-badge.rank-1 {
        background: #F97316;
        color: #ffffff;
    }

    .ed-rank-badge.rank-2 {
        background: #94A3B8;
        color: #ffffff;
    }

    .ed-rank-badge.rank-3 {
        background: #B45309;
        color: #ffffff;
    }

    .ed-tenant-with-rank {
        display: inline-flex;
        align-items: center;
        gap: 0;
    }

    .ed-table-card.ed-table-best3 .ed-table tbody td {
        padding-top: 25px;
        padding-bottom: 25px;
        vertical-align: middle;
    }

    .ed-table-card.ed-table-best3 .ed-table tbody tr:hover td {
        background: #FAFAFF;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-top-tables-marker) .ed-table-scroll {
        flex: 1 1 auto !important;
        display: flex !important;
        flex-direction: column !important;
        min-height: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-top-tables-marker) .ed-table tbody {
        vertical-align: top;
    }

    .ed-positive {
        color: #059669;
        font-weight: 700;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-negative {
        color: #DC2626;
        font-weight: 700;
        font-family: 'Inter', sans-serif !important;
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
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-chip-row {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 8px;
    }

    body:has(.dv-page-marker) [data-testid="stSelectbox"] > div > div {
        min-height: 40px !important;
        height: 40px !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background: #ffffff !important;
        box-shadow: none !important;
        outline: none !important;
        transition: border-color 0.15s ease, background-color 0.15s ease !important;
    }

    body:has(.dv-page-marker) [data-testid="stSelectbox"] div[data-baseweb="select"],
    body:has(.dv-page-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] span,
    body:has(.dv-page-marker) [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"],
    body:has(.dv-page-marker) [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        font-size: 13px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        color: #0F172A !important;
    }

    body:has(.dv-page-marker) [data-testid="stTextInput"] [data-baseweb="input"] {
        min-height: 40px !important;
        height: 40px !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background: #ffffff !important;
        box-shadow: none !important;
        outline: none !important;
        overflow: hidden !important;
        display: flex !important;
        align-items: center !important;
        transition: border-color 0.15s ease, background-color 0.15s ease !important;
    }

    body:has(.dv-page-marker) [data-testid="stTextInput"] [data-baseweb="input"] > div {
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        align-items: center !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    body:has(.dv-page-marker) .stTextInput > div > div > input,
    body:has(.dv-page-marker) [data-testid="stTextInput"] input {
        min-height: 38px !important;
        height: 38px !important;
        border: none !important;
        border-radius: 8px !important;
        background: transparent !important;
        box-shadow: none !important;
        outline: none !important;
        color: #0F172A !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0 12px !important;
    }

    body:has(.dv-page-marker) [data-testid="stSelectbox"] > div > div:hover,
    body:has(.dv-page-marker) [data-testid="stSelectbox"] > div > div:focus-within,
    body:has(.dv-page-marker) [data-testid="stTextInput"] [data-baseweb="input"]:hover,
    body:has(.dv-page-marker) [data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
        border-color: #94A3B8 !important;
        background: #F8FAFC !important;
        box-shadow: none !important;
        outline: none !important;
    }

    body:has(.dv-page-marker) .stTextInput > div > div > input:focus,
    body:has(.dv-page-marker) .stTextInput > div > div > input:hover,
    body:has(.dv-page-marker) [data-testid="stTextInput"] input:focus,
    body:has(.dv-page-marker) [data-testid="stTextInput"] input:hover {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        background: transparent !important;
    }

    body:has(.dv-page-marker) .stTextInput > div > div > input::placeholder,
    body:has(.dv-page-marker) [data-testid="stTextInput"] input::placeholder {
        color: #94A3B8 !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    div[data-baseweb="popover"] div[data-baseweb="menu"],
    div[data-baseweb="popover"] ul[role="listbox"] {
        z-index: 999999 !important;
    }

    div[data-baseweb="menu"],
    div[data-baseweb="menu"] > div,
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] div[data-baseweb="menu"],
    div[data-baseweb="popover"] div[data-baseweb="menu"] > div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] ul[role="listbox"] {
        background: #ffffff !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.12) !important;
        overflow: hidden !important;
    }

    div[data-baseweb="menu"] ul,
    div[data-baseweb="menu"] [role="listbox"],
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] [role="listbox"] {
        margin: 0 !important;
        padding: 4px !important;
        background: #ffffff !important;
        border-radius: 8px !important;
        border: 0 !important;
        box-shadow: none !important;
    }

    div[data-baseweb="menu"] li,
    div[data-baseweb="menu"] [role="option"],
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] [role="option"],
    div[data-baseweb="popover"] [data-baseweb="menu"] li {
        min-height: 48px !important;
        height: 48px !important;
        padding: 0 20px !important;
        margin: 0 !important;
        border-radius: 6px !important;
        background: #ffffff !important;
        color: #0F172A !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        line-height: 1.25 !important;
        display: flex !important;
        align-items: center !important;
    }

    div[data-baseweb="menu"] li *,
    div[data-baseweb="menu"] [role="option"] *,
    div[data-baseweb="popover"] li *,
    div[data-baseweb="popover"] [role="option"] * {
        background: transparent !important;
        color: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
    }

    div[data-baseweb="menu"] li > div,
    div[data-baseweb="menu"] [role="option"] > div,
    div[data-baseweb="popover"] li > div,
    div[data-baseweb="popover"] [role="option"] > div {
        min-height: 0 !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
    }

    div[data-baseweb="menu"] li > div > div,
    div[data-baseweb="menu"] [role="option"] > div > div,
    div[data-baseweb="popover"] li > div > div,
    div[data-baseweb="popover"] [role="option"] > div > div,
    div[data-baseweb="menu"] [data-testid="stMarkdownContainer"],
    div[data-baseweb="popover"] [data-testid="stMarkdownContainer"],
    div[data-baseweb="menu"] [data-testid="stMarkdownContainer"] p,
    div[data-baseweb="popover"] [data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        padding: 0 !important;
        min-height: 0 !important;
        height: auto !important;
        display: flex !important;
        align-items: center !important;
        line-height: 1.25 !important;
    }

    div[data-baseweb="menu"] li:hover,
    div[data-baseweb="menu"] [role="option"]:hover,
    div[data-baseweb="menu"] [role="option"][aria-selected="true"],
    div[data-baseweb="menu"] [aria-selected="true"],
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] [role="option"]:hover,
    div[data-baseweb="popover"] [role="option"][aria-selected="true"],
    div[data-baseweb="popover"] [aria-selected="true"] {
        background: #EFF6FF !important;
        color: #1D4ED8 !important;
    }

    div[data-testid="stButton"] > button,
    div[data-testid="stDownloadButton"] > button {
        min-height: 40px !important;
        height: 40px !important;
        padding: 0 14px !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background: #ffffff !important;
        color: #0F172A !important;
        box-shadow: none !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.15s ease, background-color 0.15s ease, color 0.15s ease !important;
    }

    div[data-testid="stDownloadButton"] > button p,
    div[data-testid="stButton"] > button p {
        font-size: 13px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        color: #0F172A !important;
    }

    .ed-pagination-info {
        display: flex;
        align-items: center;
        height: 44px;
        padding: 0 4px;
        color: #64748B;
        font-size: 12px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
        border-top: 1px solid #F1F5F9;
    }

    .overview-detail-pagination-footer-marker {
        display: none;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stElementContainer"]:has(.overview-detail-pagination-footer-marker) {
        display: none;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type {
        align-items: center !important;
        gap: 2px !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(2),
    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(3),
    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(4) {
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(2) {
        width: 32px !important;
        max-width: 32px !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(4) {
        width: 32px !important;
        max-width: 32px !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(3) {
        width: max-content !important;
        max-width: max-content !important;
        flex: 0 0 max-content !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(3) .ed-pagination-label {
        justify-content: center;
        padding: 0 2px;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
        border-top: 1px solid #F1F5F9 !important;
        height: 44px !important;
        width: 32px !important;
        min-width: 32px !important;
        max-width: 32px !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] > button {
        height: 30px !important;
        min-height: 30px !important;
        width: 30px !important;
        min-width: 30px !important;
        max-width: 30px !important;
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 6px !important;
        border: 1px solid #E2E8F0 !important;
        background: #ffffff !important;
        color: #334155 !important;
        font-size: 18px !important;
        font-weight: 400 !important;
        line-height: 1 !important;
        box-shadow: none !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] > button:hover:not(:disabled) {
        background: #F1F5F9 !important;
        border-color: #CBD5E1 !important;
        color: #0F172A !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] > button:disabled {
        opacity: 0.3 !important;
    }


    .ed-pagination-label {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 44px;
        padding: 0 2px;
        color: #0F172A;
        font-size: 12px;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
        white-space: nowrap;
        border-top: 1px solid #F1F5F9;
    }

    /* Reset semua button dulu */
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] > .ed-card-marker)
    div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
        border-top: 1px solid #F1F5F9 !important;
        height: 44px !important;
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] > .ed-card-marker)
    div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] > button {
        height: 30px !important;
        min-height: 30px !important;
        width: 30px !important;
        min-width: 0 !important;
        max-width: 30px !important;
        padding: 0 !important;
        margin: 0 auto !important;
        border-radius: 6px !important;
        border: 1px solid #E2E8F0 !important;
        background: #ffffff !important;
        color: #334155 !important;
        font-size: 18px !important;
        font-weight: 400 !important;
        line-height: 1 !important;
        box-shadow: none !important;
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] > .ed-card-marker)
    div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] > button:hover:not(:disabled) {
        background: #F1F5F9 !important;
        border-color: #CBD5E1 !important;
        color: #0F172A !important;
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] > .ed-card-marker)
    div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] > button:disabled {
        opacity: 0.3 !important;
    }

                
    .overview-kpi-card,
    .overview-kpi-card *,
    .kpi-pro-card,
    .kpi-pro-card *,
    .overview-light-table-wrap,
    .overview-light-table-wrap *,
    .ed-table-card,
    .ed-table-card *,
    div[data-testid="stVerticalBlock"]:has(.ed-card-marker),
    div[data-testid="stVerticalBlock"]:has(.ed-card-marker) * {
        font-family: 'Inter', sans-serif !important;
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

        .kpi-pro-card {
            min-height: 150px;
            padding: 14px 16px;
        }

        .kpi-pro-value {
            font-size: 21px;
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
        "Lease Contract",
        "Traffic Monitor",
        "Import Manager",
        "Data Verification",
    ],
    Role.ADMIN: [
        "Overview",
        "Revenue Sharing",
        "Lease Contract",
        "Traffic Monitor",
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
            "jumlah_pax":      np.random.randint(500, 3000),
        })
    df = pd.DataFrame(rows)
    df["rev_sqm"] = df["real_omzet"] / df["luas_sqm"]
    df["acv"]     = (df["real_omzet"] / df["min_omzet"] * 100).round(2)
    return df

def fmt_rp(v):
    if v >= 1_000_000_000_000: return f"Rp {v/1_000_000_000_000:.2f}T"
    if v >= 1_000_000_000:     return f"Rp {v/1_000_000_000:.2f}M"
    if v >= 1_000_000:         return f"Rp {v/1_000_000:.2f}Jt"
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


def _ed_card_marker(container, extra_class: str = "") -> None:
    marker_class = "ed-card-marker"
    if extra_class:
        marker_class = f"{marker_class} {extra_class}"
    container.markdown(f'<div class="{marker_class}"></div>', unsafe_allow_html=True)


def _overview_filter_label(label: str) -> str:
    return f'<p class="overview-filter-label">{escape(label)}</p>'


def _fmt_rp_compact(value):
    if pd.isna(value):
        value = 0
    if value >= 1_000_000_000_000:
        val_str = f"{value / 1_000_000_000_000:.2f}"
        return f"Rp {val_str.replace('.', ',')} T"
    if value >= 1_000_000_000:
        val_str = f"{value / 1_000_000_000:.2f}"
        return f"Rp {val_str.replace('.', ',')} M"
    if value >= 1_000_000:
        val_str = f"{value / 1_000_000:.2f}"
        return f"Rp {val_str.replace('.', ',')} Jt"
    val_str = f"{value:,.0f}"
    return f"Rp {val_str.replace(',', '.')}"


def _fmt_rp_full(value):
    if pd.isna(value):
        value = 0
    val_str = f"{value:,.0f}"
    return f"Rp {val_str.replace(',', '.')}"


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


# ══════════════════════════════════════════════
# HELPER: KPI cards "pro" (icon + badge + progress bar)
# ══════════════════════════════════════════════
KPI_PRO_ICON_PATHS = {
    "omzet":  '<line x1="12" y1="2" x2="12" y2="22"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>',
    "layers": '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"></path><path d="M22 12A10 10 0 0 0 12 2v10z"></path>',
    "file":   '<path d="m3 9 9-7 9 7"></path><path d="M4 10v10a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1v-4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v4a1 1 0 0 0 1 1h3a1 1 0 0 0 1-1V10"></path>',
    "bars":   '<line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line>',
    "users":  '<rect width="20" height="14" x="2" y="5" rx="2"></rect><line x1="2" y1="10" x2="22" y2="10"></line>',
    "expand": '<rect width="18" height="18" x="3" y="3" rx="2"></rect>',
    "award":  '<circle cx="12" cy="8" r="6"></circle><path d="M15.477 12.89 17 22l-5-3-5 3 1.523-9.11"></path>',
    "plane":  '<path d="M17.8 19.2 16 11l3.5-3.5C21 6 21.5 4 21 3c-1-.5-3 0-4.5 1.5L13 8 4.8 6.2c-.5-.1-.9.1-1.1.5l-.3.5c-.2.5-.1 1 .3 1.3L9 12l-2 3H4l-1 1 3 2 2 3 1-1v-3l3-2 3.5 5.3c.3.4.8.5 1.3.3l.5-.2c.4-.3.6-.7.5-1.2z"></path>',
}


def _kpi_pro_icon_svg(icon_key: str) -> str:
    paths = KPI_PRO_ICON_PATHS[icon_key]
    return (
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
    )


def _compact_number(value, decimals=1):
    if value is None or pd.isna(value):
        value = 0
    value = float(value)
    abs_value = abs(value)
    if abs_value >= 1_000_000_000_000:
        val_str = f"{value / 1_000_000_000_000:.{decimals}f}"
        return val_str.replace(".", ","), "T"
    if abs_value >= 1_000_000_000:
        val_str = f"{value / 1_000_000_000:.{decimals}f}"
        return val_str.replace(".", ","), "M"
    if abs_value >= 1_000_000:
        val_str = f"{value / 1_000_000:.{decimals}f}"
        return val_str.replace(".", ","), "Jt"
    if abs_value >= 1_000:
        val_str = f"{value:,.0f}"
        return val_str.replace(",", "."), ""
    val_str = f"{value:.{decimals}f}"
    return val_str.replace(".", ","), ""


def _pct_change(current, base):
    if not base:
        return 0.0
    return (current - base) / base * 100


def _kpi_pro_card(label, value, unit, subtitle, delta_pct, accent, icon_key, bar_label):
    is_down = delta_pct < 0
    badge_cls = "is-down" if is_down else ""
    arrow = "↘" if is_down else "↗"
    bar_width = min(100, max(6, 50 + delta_pct * 2.2))
    
    # Process unit to extract prefix (like "Rp") and suffix (like "M", "Jt", or empty)
    prefix = ""
    display_unit = unit
    if unit.startswith("Rp"):
        prefix = "Rp "
        display_unit = unit[2:].strip()
        
    unit_span = f'<span class="kpi-pro-unit"> {escape(display_unit)}</span>' if display_unit else ""
    
    # Format percentage display to Indonesian decimal format
    formatted_pct = f"{arrow} {abs(delta_pct):.1f}%".replace(".", ",")
    
    html = (
        f'<div class="kpi-pro-card">'
        f'<div class="kpi-pro-head">'
        f'<div class="kpi-pro-icon" style="background:{accent}1A;color:{accent};">{_kpi_pro_icon_svg(icon_key)}</div>'
        f'<div class="kpi-pro-badge {badge_cls}">{formatted_pct}</div>'
        f'</div>'
        f'<div class="kpi-pro-body">'
        f'<div class="kpi-pro-label">{escape(label)}</div>'
        f'<div class="kpi-pro-value-row">'
        f'<span class="kpi-pro-value">{escape(prefix)}{escape(value)}</span>'
        f'{unit_span}'
        f'</div>'
        f'<div class="kpi-pro-sub">{escape(subtitle)}</div>'
        f'</div>'
        f'<div class="kpi-pro-foot">'
        f'<div class="kpi-pro-bar-row">'
        f'<span>{escape(bar_label)}</span>'
        f'<span style="color:{accent};">{formatted_pct}</span>'
        f'</div>'
        f'<div class="kpi-pro-bar-track">'
        f'<div class="kpi-pro-bar-fill" style="width:{bar_width:.0f}%;background:{accent};"></div>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    return html


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


def _rank_badge_html(rank: int) -> str:
    return f'<span class="ed-rank-badge rank-{rank}">{rank}</span>'


def _table_col_class(col_name: str, col_align: dict | None, prefix: str = "ed-th") -> str:
    align = (col_align or {}).get(str(col_name), "left")
    return f'{prefix}-{align}'


def _enterprise_table_html(df, title=None, link_label=None, table_class="", col_align=None, subtitle=None, show_eye_icon=False):
    col_align = col_align or {}
    header_html = "".join(
        f'<th class="{_table_col_class(col, col_align, "ed-th")}">{escape(str(col))}</th>'
        for col in df.columns
    )
    rows_html = ""
    for _, row in df.iterrows():
        cells = []
        for col, value in zip(df.columns, row):
            text = str(value)
            td_class = _table_col_class(col, col_align, "ed-td")
            if text.startswith("<span ") or text.startswith('<span class="ed-rank-badge'):
                cells.append(f'<td class="{td_class}">{text}</td>')
            elif text.startswith('<span class="ed-tenant-with-rank"') or text.startswith("<div "):
                cells.append(f'<td class="{td_class}">{text}</td>')
            else:
                cells.append(f'<td class="{td_class}">{escape(text)}</td>')
        rows_html += f"<tr>{''.join(cells)}</tr>"

    head_html = ""
    if title:
        link_html = ""
        if link_label:
            eye_html = '<span class="ed-view-icon">👁</span>' if show_eye_icon else ""
            link_html = f'<span class="ed-table-link ed-table-link-with-icon">{eye_html}{escape(link_label)}</span>'
        if subtitle:
            head_html = dedent(f"""
            <div class="ed-table-head-stack">
                <div class="ed-table-head-copy">
                    <p class="ed-table-title">{escape(title)}</p>
                    <p class="ed-table-subtitle">{escape(subtitle)}</p>
                </div>
                {link_html}
            </div>
            """).strip()
        else:
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


def _enterprise_table_inner_html(df, col_align=None):
    col_align = col_align or {}
    header_html = "".join(
        f'<th class="{_table_col_class(col, col_align, "ed-th")}">{escape(str(col))}</th>'
        for col in df.columns
    )
    rows_html = ""
    for _, row in df.iterrows():
        cells = []
        for col, value in zip(df.columns, row):
            text = str(value)
            td_class = _table_col_class(col, col_align, "ed-td")
            if text.startswith("<span "):
                cells.append(f'<td class="{td_class}">{text}</td>')
            else:
                cells.append(f'<td class="{td_class}">{escape(text)}</td>')
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


def _nav_icon(*paths: str) -> str:
    inner = "".join(paths)
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'width="18" height="18" fill="none" stroke="currentColor" '
        'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
        f'aria-hidden="true">{inner}</svg>'
    )


NAV_ICONS = {
    "Overview": _nav_icon(
        '<rect x="3" y="3" width="7" height="7" rx="1.5"/>',
        '<rect x="14" y="3" width="7" height="7" rx="1.5"/>',
        '<rect x="3" y="14" width="7" height="7" rx="1.5"/>',  
        '<rect x="14" y="14" width="7" height="7" rx="1.5"/>',
    ),
    "Revenue Sharing": _nav_icon(
        '<circle cx="18" cy="5" r="3"/>',
        '<circle cx="6" cy="12" r="3"/>',
        '<circle cx="18" cy="19" r="3"/>',
        '<line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>',
        '<line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>',
    ),
    "Lease Contract": _nav_icon(
        '<path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"/>',
        '<polyline points="14 2 14 8 20 8"/>',
        '<path d="M10 16h4"/>',
        '<path d="m8 12.5 4-4a1.5 1.5 0 0 1 2 2l-4 4-2 0z"/>',
    ),
    "Traffic Monitor": _nav_icon(
        '<polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>',
    ),
    "Import Manager": _nav_icon(
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>',
        '<polyline points="17 8 12 3 7 8"/>',
        '<line x1="12" y1="3" x2="12" y2="15"/>',
    ),
    "Data Verification": _nav_icon(
        '<path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>',
        '<path d="m9 12 2 2 4-4"/>',
    ),
}


def _overview_page_header_html():
    return dedent(f"""
    <div class="ov-page-header">
        <div class="ov-page-header-left">
            <div class="ov-page-icon" aria-hidden="true">{NAV_ICONS["Overview"]}</div>
            <div class="ov-page-header-copy">
                <div class="ov-page-title-row">
                    <h2 class="ov-page-title">Overview</h2>
                </div>
                <p class="ov-page-sub">Monitor commercial revenue and operational performance.</p>
            </div>
        </div>
        {topnav_actions_html()}
    </div>
    """).strip()


def _mount_overview_fixed_header():
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


def _sidebar_brand_logo_svg():
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
        'width="18" height="18" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round" '
        'style="color: #ffffff;">'
        '<path d="M17.8 19.2 16 11l3.5-3.5a2.1 2.1 0 1 0-3-3L13 8 4.8 6.2c-.5-.1-1 .1-1.2.5l-.3.3c-.2.3-.2.7 0 1l6.7 4.1L6 16.2c-.3.3-.4.8-.2 1.1l.3.3c.3.2.8.1 1.1-.2l4.1-4.1 4.1 6.7c.3.2.7.2 1 0l.3-.3c.4-.2.6-.7.5-1.2z"/>'
        '</svg>'
    )


def _sidebar_brand():
    if st.session_state.get("sidebar_minimized", False):
        st.markdown(f"""
        <div class="ap-brand ap-brand-mini">
            <div class="ap-logo">{_sidebar_brand_logo_svg()}</div>
        </div>""", unsafe_allow_html=True)
        return

    st.markdown(f"""
    <div class="ap-brand">
        <div style="display:flex;align-items:center;gap:12px;">
            <div class="ap-logo">{_sidebar_brand_logo_svg()}</div>
            <div class="ap-brand-copy">
                <div class="ap-brand-name">AirportBI</div>
                <div class="ap-brand-sub">Commercial Suite</div>
            </div>
        </div>
    </div>""", unsafe_allow_html=True)


def _nav_group(label):
    if st.session_state.get("sidebar_minimized", False):
        st.markdown('<div class="nav-group-mini"></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="nav-group">{label}</div>', unsafe_allow_html=True)


def _sidebar_footer():
    if st.session_state.get("sidebar_minimized", False):
        st.markdown(
            '<div class="ap-sidebar-footer" style="font-size: 12px !important;">'
            '© 2026</div>',
            unsafe_allow_html=True,
        )
        return
    st.markdown("""
    <div class="ap-sidebar-footer">
        © 2026 INJOURNEY AIRPORTS. ALL RIGHTS RESERVED.
    </div>
    """, unsafe_allow_html=True)


def show_sidebar():
    with st.sidebar:

        _sidebar_brand()

        st.markdown('<div class="nav-category-header">NAVIGATION</div>', unsafe_allow_html=True)

        menu_items = [
            "Overview",
            "Revenue Sharing",
            "Lease Contract",
            "Traffic Monitor",
            "Import Manager",
            "Data Verification",
        ]
        for label in menu_items:
            _nav_row(NAV_ICONS[label], label)

        st.markdown('<div class="ap-sidebar-spacer"></div>', unsafe_allow_html=True)
        _sidebar_footer()


def _nav_row(icon, label):
    if not can_access_menu(label):
        return

    mini = st.session_state.get("sidebar_minimized", False)
    is_active = st.session_state.active_menu == label
    label_html = "" if mini else f'<span class="nav-label">{escape(label)}</span>'

    st.button(" ", key=f"nav_{label}", help=label if mini else None, use_container_width=True)

    if is_active:
        st.markdown(
            f"""
            <div class="nav-active nav-overlay" title="{escape(label)}">
                <span class="nav-indicator-pill"></span>
                <span class="nav-icon-box">{icon}</span>
                {label_html}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div class="nav-row nav-overlay" title="{escape(label)}">
                <span class="nav-icon-box">{icon}</span>
                {label_html}
            </div>
            """,
            unsafe_allow_html=True,
        )


def _nav_item(icon, label):
    _nav_row(icon, label)


def _nav_sub(icon, label):
    _nav_row(icon, label)


# ══════════════════════════════════════════════
# PAGE: OVERVIEW
# ══════════════════════════════════════════════
_OV_FILTER_DEFAULTS = {
    "f_terminal": "All Terminal", "f_tahun": "All Year", "f_masa": "All Month",
    "f_perusahaan": "All Perusahaan", "f_kode_ruang": "All Kode Ruang",
}


def clear_overview_filters():
    """Reset both the applied filters and the pending (draft) widget values."""
    for applied_key, default in _OV_FILTER_DEFAULTS.items():
        st.session_state[applied_key] = default
        st.session_state[f"f_pend_{applied_key[2:]}"] = default


def _apply_overview_filters():
    """Copy the pending (draft) widget values into the applied filter keys."""
    for applied_key in _OV_FILTER_DEFAULTS:
        st.session_state[applied_key] = st.session_state[f"f_pend_{applied_key[2:]}"]


_OV_FILTER_ICONS = {
    "building": '<path d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"></path><path d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"></path><path d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"></path><path d="M10 6h4"></path><path d="M10 10h4"></path><path d="M10 14h4"></path><path d="M10 18h4"></path>',
    "grid":     '<rect width="7" height="7" x="3" y="3" rx="1"></rect><rect width="7" height="7" x="14" y="3" rx="1"></rect><rect width="7" height="7" x="14" y="14" rx="1"></rect><rect width="7" height="7" x="3" y="14" rx="1"></rect>',
    "monitor":  '<rect width="20" height="14" x="2" y="3" rx="2"></rect><line x1="8" y1="21" x2="16" y2="21"></line><line x1="12" y1="17" x2="12" y2="21"></line>',
    "calendar": '<path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path>',
    "filter":   '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"></polygon>',
}


def _ov_filter_icon_svg(icon_key: str, size: int = 14) -> str:
    paths = _OV_FILTER_ICONS.get(icon_key, "")
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
    )


def _render_overview_filter_card(
    active_count, terminal_options, year_options, month_options,
    perusahaan_options, kode_ruang_options,
) -> None:
    """"Filter Data" card matching the Lease Contract page — filters are
    staged in f_pend_* widget keys and only take effect once the user
    clicks "Terapkan Filter" / "Bersihkan Semua" / the header "Reset Filter"."""
    st.markdown('<div class="ov-filtercard-marker"></div>', unsafe_allow_html=True)

    badge = (
        f'<span class="ov-filtercard-badge">{active_count} aktif</span>'
        if active_count > 0 else ""
    )
    head_l, head_r = st.columns([4, 1.2], vertical_alignment="center")
    with head_l:
        st.markdown(
            '<div class="ov-filtercard-head">'
            f'<span class="ov-filtercard-icon">{_ov_filter_icon_svg("filter", 18)}</span>'
            '<div>'
            f'<p class="ov-filtercard-title">Filter Data{badge}</p>'
            '<p class="ov-filtercard-sub">Pilih kriteria untuk memfilter data yang ditampilkan</p>'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    with head_r:
        st.button(
            "↺  Reset Filter", key="ov_btn_reset_top", use_container_width=True,
            on_click=clear_overview_filters,
        )

    st.markdown('<div class="ov-filterrow-marker"></div>', unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5, gap="small")
    field_defs = [
        (c1, "building", "Nama Perusahaan", perusahaan_options, "f_pend_perusahaan"),
        (c2, "grid", "Kode Ruangan", kode_ruang_options, "f_pend_kode_ruang"),
        (c3, "monitor", "Terminal", terminal_options, "f_pend_terminal"),
        (c4, "calendar", "Tahun", year_options, "f_pend_tahun"),
        (c5, "calendar", "Bulan", month_options, "f_pend_masa"),
    ]
    for col, icon_key, label, options, widget_key in field_defs:
        with col:
            st.markdown(
                f'<div class="ov-filter-label">{_ov_filter_icon_svg(icon_key, 12)}<span>{label}</span></div>',
                unsafe_allow_html=True,
            )
            st.selectbox(label, options, key=widget_key, label_visibility="collapsed")

    st.markdown('<div class="ov-filtercard-footer-marker"></div>', unsafe_allow_html=True)
    _foot_spacer, foot_r1, foot_r2 = st.columns([3.2, 1.3, 1.3], vertical_alignment="center")
    with foot_r1:
        st.button("✕  Bersihkan Semua", key="ov_btn_reset_bottom", use_container_width=True, on_click=clear_overview_filters)
    with foot_r2:
        st.button(
            "Terapkan Filter", key="ov_btn_apply", use_container_width=True,
            type="primary", icon=":material/filter_alt:", on_click=_apply_overview_filters,
        )


def _get_overview_extra_css():
    return dedent(f"""
    <style>
    /* Same header-to-filter gap as the Lease Contract page. */
    body:has(.overview-page-marker) .ov-fixed-header-spacer,
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-fixed-header-spacer) {{
        height: 56px !important;
        min-height: 56px !important;
        max-height: 56px !important;
    }}
    /* ── Filter Data card (same design as Lease Contract) ──────────── */
    body:has(.overview-page-marker) div[data-testid="stHorizontalBlock"]:has(.ov-filtercard-marker),
    body:has(.overview-page-marker) div[data-testid="stLayoutWrapper"]:has(.ov-filtercard-marker) {{
        margin-top: -24px !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -1px rgba(0,0,0,0.015) !important;
        padding: 18px 20px 14px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stHorizontalBlock"]:has(.ov-filtercard-marker) ~ div[data-testid="stHorizontalBlock"]:has(.kpi-pro-card),
    body:has(.overview-page-marker) div[data-testid="stLayoutWrapper"]:has(.ov-filtercard-marker) ~ div[data-testid="stLayoutWrapper"]:has(.kpi-pro-card) {{
        margin-top: 1px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stLayoutWrapper"]:has(.kpi-pro-card) + div[data-testid="stLayoutWrapper"]:has(.kpi-pro-card) {{
        margin-top: 10px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-vertical-spacer) {{
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        height: 10px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-vertical-spacer) + div[data-testid="stElementContainer"] {{
        margin-top: -24px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-vertical-spacer) + div:has(.ed-card-marker) {{
        margin-top: -24px !important;
    }}
    /* Jarak Vertikal antara KPI Cards baris kedua dengan Revenue Trend dan Alert & Insight */
    body:has(.overview-page-marker) [data-testid="stHorizontalBlock"]:has(.overview-trend-card),
    body:has(.overview-page-marker) [data-testid="stLayoutWrapper"]:has(.overview-trend-card) {{
        margin-top: 10px !important;
    }}
    .ov-filtercard-head {{
        display: flex; align-items: center; gap: 12px;
    }}
    .ov-filtercard-icon {{
        width: 34px; height: 34px; border-radius: 10px; flex: 0 0 34px;
        background: #EEF2FF; color: #4338CA;
        display: flex; align-items: center; justify-content: center;
    }}
    .ov-filtercard-title {{
        margin: 0 !important; color: #0F172A; font-size: 18px !important; font-weight: 700 !important;
        font-family: 'Montserrat', sans-serif !important; line-height: 1 !important;
    }}
    .ov-filtercard-badge {{
        display: inline-flex; align-items: center; margin-left: 8px;
        padding: 2px 8px; border-radius: 999px; vertical-align: middle;
        background: #F0FDF4; border: 1px solid #BBF7D0;
        font-size: 10.5px !important; font-weight: 700 !important; color: #16A34A;
        white-space: nowrap;
    }}
    .ov-filtercard-sub {{
        margin: 5px 0 0 !important; color: #64748B; font-size: 11px !important; font-weight: 400 !important;
        line-height: 1 !important;
        font-family: 'Inter', sans-serif !important;
    }}
    .ov-filter-label {{
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
    }}
    .ov-filter-label svg {{
        display: block !important;
        flex-shrink: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    .ov-filter-label span {{
        line-height: 1 !important;
        display: inline-block !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-filter-label) {{
        margin-bottom: -4px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-filterrow-marker) {{
        margin: 0 !important; padding: 0 !important; height: 0 !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-filterrow-marker) + div[data-testid="stHorizontalBlock"],
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-filterrow-marker) + div[data-testid="stLayoutWrapper"] {{
        margin-top: -4px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-filtercard-footer-marker) {{
        margin: 6px 0 -10px !important;
        height: 1px !important;
        border-top: 1px solid #F1F5F9 !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="baseButton-secondary"] {{
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
    }}
    body:has(.overview-page-marker) [data-testid="baseButton-primary"],
    body:has(.overview-page-marker) [data-testid="stBaseButton-primary"] {{
        border-radius: 999px !important;
        font-size: 12.5px !important; font-weight: 700 !important;
        font-family: Inter, sans-serif !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="baseButton-primary"],
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stBaseButton-primary"] {{
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
    }}
    body:has(.overview-page-marker) [data-testid="baseButton-primary"]:hover,
    body:has(.overview-page-marker) [data-testid="stBaseButton-primary"]:hover {{
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.45) !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="baseButton-primary"]:hover,
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stBaseButton-primary"]:hover {{
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    }}
    body:has(.overview-page-marker) [data-testid="baseButton-primary"] svg,
    body:has(.overview-page-marker) [data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"] {{
        color: #ffffff !important;
        fill: #ffffff !important;
        font-family: 'Material Symbols Rounded' !important;
    }}
    body:has(.overview-page-marker) [data-testid="baseButton-primary"] p,
    body:has(.overview-page-marker) [data-testid="stBaseButton-primary"] p {{
        color: #ffffff !important;
    }}
    /* ── Selectbox Dropdowns in Filter Card ────────────────────────── */
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] {{
        margin-bottom: 0 !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] > div {{
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] > div > div {{
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        backdrop-filter: none !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] {{
        border: 1px solid #E2E8F0 !important;
        border-radius: 999px !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(99, 102, 241, 0.04) !important;
        transition: all 0.2s ease !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"]:hover {{
        border-color: #CBD5E1 !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {{
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1) !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        min-height: 32px !important;
        height: 32px !important;
        max-height: 32px !important;
        padding: 0 4px 0 12px !important;
        display: flex !important;
        align-items: center !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"] {{
        font-size: 11.5px !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] svg {{
        color: #64748B !important;
    }}

    /* Export button on overview detail tenant table */
    div[data-testid="stElementContainer"]:has(.ov-btn-export-marker) {{
        position: absolute !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }}
    div[data-testid="stElementContainer"]:has(.ov-btn-export-marker) + div[data-testid="stElementContainer"] button {{
        background: rgba(255, 255, 255, 0.72) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        color: #4F46E5 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        padding: 0 16px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        min-height: 38px !important;
        height: 38px !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }}
    div[data-testid="stElementContainer"]:has(.ov-btn-export-marker) + div[data-testid="stElementContainer"] button:hover {{
        background: #f5f3ff !important;
        border-color: rgba(99, 102, 241, 0.45) !important;
    }}
    div[data-testid="stElementContainer"]:has(.ov-btn-export-marker) + div[data-testid="stElementContainer"] button p {{
        color: #4F46E5 !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    div[data-testid="stElementContainer"]:has(.ov-btn-export-marker) + div[data-testid="stElementContainer"] button::before {{
        content: "" !important;
        display: inline-block !important;
        width: 14px !important;
        height: 14px !important;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%234F46E5" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>') !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        flex-shrink: 0 !important;
    }}
    </style>
    """)


def page_overview(df_raw):
    for key in ["show_all_rev", "show_all_best", "show_all_detail", "overview_detail_page"]:
        if key not in st.session_state:
            st.session_state[key] = 1 if key == "overview_detail_page" else False

    terminal_options = ["All Terminal"] + sorted(df_raw["terminal"].dropna().unique().tolist())
    db_years = [int(y) for y in df_raw["tahun"].dropna().unique()]
    all_years = sorted(list(set(db_years + [2023, 2024, 2025, 2026, 2027, 2028, 2029, 2030])), reverse=True)
    year_options = ["All Year"] + all_years
    month_options = ["All Month"] + BULAN
    perusahaan_options = ["All Perusahaan"] + sorted(df_raw["perusahaan"].dropna().unique().tolist())
    kode_ruang_options = ["All Kode Ruang"] + sorted(df_raw["kode_ruang"].dropna().unique().tolist())

    if st.session_state.get("f_terminal") not in terminal_options:
        st.session_state.f_terminal = terminal_options[0]
    if st.session_state.get("f_tahun") not in year_options:
        st.session_state.f_tahun = year_options[0]
    if st.session_state.get("f_masa") not in month_options:
        st.session_state.f_masa = month_options[0]
    if st.session_state.get("f_perusahaan") not in perusahaan_options:
        st.session_state.f_perusahaan = perusahaan_options[0]
    if st.session_state.get("f_kode_ruang") not in kode_ruang_options:
        st.session_state.f_kode_ruang = kode_ruang_options[0]

    for pend_key, applied_key, options in (
        ("f_pend_terminal", "f_terminal", terminal_options),
        ("f_pend_tahun", "f_tahun", year_options),
        ("f_pend_masa", "f_masa", month_options),
        ("f_pend_perusahaan", "f_perusahaan", perusahaan_options),
        ("f_pend_kode_ruang", "f_kode_ruang", kode_ruang_options),
    ):
        if st.session_state.get(pend_key) not in options:
            st.session_state[pend_key] = st.session_state[applied_key]

    active_count = sum([
        st.session_state.get("f_terminal", "All Terminal") != "All Terminal",
        st.session_state.get("f_tahun", "All Year") != "All Year",
        st.session_state.get("f_masa", "All Month") != "All Month",
        st.session_state.get("f_perusahaan", "All Perusahaan") != "All Perusahaan",
        st.session_state.get("f_kode_ruang", "All Kode Ruang") != "All Kode Ruang",
    ])

    st.markdown('<div class="overview-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown(_get_overview_extra_css(), unsafe_allow_html=True)
    _mount_overview_fixed_header()

    with st.container():
        st.markdown('<div class="ov-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_overview_page_header_html(), unsafe_allow_html=True)
        st.markdown('<div class="ov-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="ov-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)

    with st.container(border=True):
        _render_overview_filter_card(
            active_count, terminal_options, year_options, month_options,
            perusahaan_options, kode_ruang_options,
        )

    sel_terminal = st.session_state.f_terminal
    sel_tahun = st.session_state.f_tahun
    sel_masa = st.session_state.f_masa
    sel_perusahaan = st.session_state.f_perusahaan
    sel_kode_ruang = st.session_state.f_kode_ruang

    df = df_raw.copy()
    if sel_terminal   != "All Terminal":   df = df[df["terminal"]    == sel_terminal]
    if sel_tahun      != "All Year":       df = df[df["tahun"]       == int(sel_tahun)]
    if sel_masa       != "All Month":      df = df[df["masa_jasa"]   == sel_masa]
    if sel_perusahaan != "All Perusahaan": df = df[df["perusahaan"]  == sel_perusahaan]
    if sel_kode_ruang != "All Kode Ruang": df = df[df["kode_ruang"]  == sel_kode_ruang]

    real_revenue = df["real_omzet"].sum()
    revenue_sharing = df["pendapatan_rs"].sum()
    rental_revenue = df["pendapatan_sewa"].sum()
    total_contribution = df["kontribusi"].sum()
    total_sqm = df["luas_sqm"].sum()
    total_pax = df["jumlah_pax"].sum() if "jumlah_pax" in df.columns else 0
    target_omzet = df["min_omzet"].sum()
    avg_contract_value = df["min_omzet"].mean() if not df.empty else 0
    rev_per_sqm = (real_revenue / total_sqm) if total_sqm else 0
    spending_per_pax = (real_revenue / total_pax) if total_pax else 0

    # Periode pembanding (tahun sebelumnya, dengan filter terminal & bulan yang sama)
    current_year = int(sel_tahun) if sel_tahun != "All Year" else (int(df["tahun"].max()) if not df.empty else None)
    prior_df = df_raw.iloc[0:0]
    if current_year is not None:
        prior_df = df_raw[df_raw["tahun"] == current_year - 1]
        if sel_terminal   != "All Terminal":   prior_df = prior_df[prior_df["terminal"]   == sel_terminal]
        if sel_masa       != "All Month":      prior_df = prior_df[prior_df["masa_jasa"]  == sel_masa]
        if sel_perusahaan != "All Perusahaan": prior_df = prior_df[prior_df["perusahaan"] == sel_perusahaan]
        if sel_kode_ruang != "All Kode Ruang": prior_df = prior_df[prior_df["kode_ruang"] == sel_kode_ruang]

    prior_real_revenue = prior_df["real_omzet"].sum()
    prior_revenue_sharing = prior_df["pendapatan_rs"].sum()
    prior_rental_revenue = prior_df["pendapatan_sewa"].sum()
    prior_contribution = prior_df["kontribusi"].sum()
    prior_sqm = prior_df["luas_sqm"].sum()
    prior_pax = prior_df["jumlah_pax"].sum() if "jumlah_pax" in prior_df.columns else 0
    prior_avg_contract = prior_df["min_omzet"].mean() if not prior_df.empty else 0
    prior_rev_per_sqm = (prior_real_revenue / prior_sqm) if prior_sqm else 0
    prior_spending_per_pax = (prior_real_revenue / prior_pax) if prior_pax else 0

    omzet_val, omzet_scale = _compact_number(real_revenue)
    rs_val, rs_scale = _compact_number(revenue_sharing)
    rental_val, rental_scale = _compact_number(rental_revenue)
    contrib_val, contrib_scale = _compact_number(total_contribution)
    spend_val, spend_scale = _compact_number(spending_per_pax, decimals=0)
    revsqm_val, revsqm_scale = _compact_number(rev_per_sqm, decimals=2)
    acv_val, acv_scale = _compact_number(avg_contract_value)
    traffic_val, traffic_scale = _compact_number(total_pax)

    contribution_delta = _pct_change(total_contribution, prior_contribution)
    spending_delta = _pct_change(spending_per_pax, prior_spending_per_pax)
    traffic_subtitle = f"Tahun {current_year}" if sel_tahun != "Semua Tahun" else "Seluruh periode"

    kpi_cards = [
        _kpi_pro_card("Real Omzet", omzet_val, f"Rp {omzet_scale}".strip(),
                       f"Target: {_fmt_rp_compact(target_omzet)}",
                       _pct_change(real_revenue, target_omzet), "#4F46E5", "omzet", "vs target"),
        _kpi_pro_card("Revenue Sharing", rs_val, f"Rp {rs_scale}".strip(),
                       f"YoY {_pct_change(revenue_sharing, prior_revenue_sharing):+.1f}%".replace(".", ","),
                       _pct_change(revenue_sharing, prior_revenue_sharing), "#0891B2", "layers", "YoY growth"),
        _kpi_pro_card("Rental Revenue", rental_val, f"Rp {rental_scale}".strip(),
                       f"vs {_fmt_rp_compact(prior_rental_revenue)} prior",
                       _pct_change(rental_revenue, prior_rental_revenue), "#2563EB", "file", "vs prior yr"),
        _kpi_pro_card("Total Contribution", contrib_val, f"Rp {contrib_scale}".strip(),
                       f"{contribution_delta:+.1f}% vs prior period".replace(".", ","),
                       contribution_delta, "#059669", "bars", "vs prior yr"),
        _kpi_pro_card("Spending per Pax", spend_val, f"Rp {spend_scale}".strip(),
                       f"{spending_delta:+.1f}% vs prior period".replace(".", ","),
                       spending_delta, "#D97706", "users", "vs prior yr"),
        _kpi_pro_card("Rev / SQM", revsqm_val, f"Rp {revsqm_scale}".strip(),
                       "per sqm · annual",
                       _pct_change(rev_per_sqm, prior_rev_per_sqm), "#E11D48", "expand", "YoY"),
        _kpi_pro_card("ACV", acv_val, f"Rp {acv_scale}".strip(),
                       "Avg Contract Value",
                       _pct_change(avg_contract_value, prior_avg_contract), "#7C3AED", "award", "vs prior yr"),
        _kpi_pro_card("Total Traffic", traffic_val, f"{traffic_scale} pax".strip(),
                       traffic_subtitle,
                       _pct_change(total_pax, prior_pax), "#2563EB", "plane", "YoY growth"),
    ]

    kpi_row1 = st.columns(4)
    for col, card_html in zip(kpi_row1, kpi_cards[:4]):
        with col:
            st.markdown(card_html, unsafe_allow_html=True)

    kpi_row2 = st.columns(4)
    for col, card_html in zip(kpi_row2, kpi_cards[4:]):
        with col:
            st.markdown(card_html, unsafe_allow_html=True)

    st.markdown('<div class="ov-vertical-spacer"></div>', unsafe_allow_html=True)

    main_left, main_right = st.columns([65, 35], gap="small")
    with main_left:
        st.markdown('<div class="ed-card-marker overview-trend-card"></div>', unsafe_allow_html=True)
        st.markdown('<p class="ed-section-title">Revenue Trend</p><p class="ed-section-sub">Monthly revenue, sharing, and contribution in Rp billion</p>', unsafe_allow_html=True)

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
            autosize=True,
            height=388,
            margin=dict(t=20, b=8, l=8, r=8),
            plot_bgcolor="#ffffff",
            paper_bgcolor="#ffffff",
            hovermode="x unified",
            font=dict(family=OVERVIEW_FONT_FAMILY, size=11, color="#475569"),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
                font=dict(family=OVERVIEW_FONT_FAMILY, size=11, color="#475569"),
            ),
            xaxis=dict(
                showgrid=False,
                tickfont=dict(family=OVERVIEW_FONT_FAMILY, size=11, color="#64748B"),
                fixedrange=True,
            ),
            yaxis=dict(
                title=dict(
                    text="Rp Miliar",
                    font=dict(family=OVERVIEW_FONT_FAMILY, size=11, color="#64748B"),
                ),
                showgrid=True,
                gridcolor="#E2E8F0",
                zeroline=False,
                tickfont=dict(family=OVERVIEW_FONT_FAMILY, size=11, color="#64748B"),
                fixedrange=True,
            ),
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})

    with main_right:
        st.markdown('<div class="ed-card-marker overview-alert-card"></div>', unsafe_allow_html=True)
        st.markdown('<p class="ed-section-title">Alert & Insight</p><p class="ed-section-sub">Highlights requiring analyst attention</p>', unsafe_allow_html=True)

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
            _alert_item_html("!", "#DC2626", f"Revenue {'turun' if rev_change < 0 else 'naik'} {abs(rev_change):.1f}% dibanding periode lalu".replace(".", ","), f"Realisasi periode aktif: {_fmt_rp_compact(real_revenue)}"),
            _alert_item_html("A", "#EA580C", f"{low_acv} tenant memiliki ACV < 80%", "Perlu perhatian untuk potensi risiko"),
            _alert_item_html("i", "#2563EB", f"{top_terminal} menyumbang {top_terminal_share}% kontribusi", "Monitor perubahan komposisi terminal"),
        ]
        st.markdown(f'<div class="ed-alert-list">{"".join(alerts)}</div>', unsafe_allow_html=True)

    st.markdown('<div class="ov-vertical-spacer"></div>', unsafe_allow_html=True)

    detail_card = st.container()
    with detail_card:
        _ed_card_marker(detail_card)
        dh1, ds, dex, dpp = st.columns([3.85, 2.85, 0.78, 0.72], vertical_alignment="center")
        with dh1:
            st.markdown(
                '<p class="ed-section-title">Detail Revenue Tenant</p>'
                '<p class="ed-section-sub">Data lengkap seluruh tenant aktif</p>',
                unsafe_allow_html=True,
            )
        with ds:
            search_query = st.text_input(
                "Search tenant",
                placeholder="Cari tenant atau brand...",
                key="overview_detail_search",
                label_visibility="collapsed",
                on_change=lambda: st.session_state.update({"overview_detail_page": 1}),
            )

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
            st.markdown('<div class="ov-btn-export-marker"></div>', unsafe_allow_html=True)
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
        detail_view["Ach %"] = detail_view["Ach %"].apply(lambda x: f"{x:.1f}%".replace(".", ","))
        detail_view["ACV"] = detail_view["acv"].apply(lambda x: f"{x:.1f}%".replace(".", ","))
        detail_view = detail_view[["perusahaan", "brand", "kode_ruang", "Min Omzet", "Real Omzet", "Kontribusi", "Ach %", "ACV"]]
        detail_view.columns = ["Tenant", "Brand", "Kode Ruang", "Min Omzet", "Real Omzet", "Kontribusi", "Ach %", "ACV"]
        detail_col_align = {
            "Min Omzet": "right",
            "Real Omzet": "right",
            "Kontribusi": "right",
            "Ach %": "right",
            "ACV": "right",
        }
        st.markdown(_enterprise_table_inner_html(detail_view, col_align=detail_col_align), unsafe_allow_html=True)

        first_item = 0 if total_rows == 0 else start_idx + 1
        last_item = min(end_idx, total_rows)

        # Use new generic pagination module
        st.markdown('<div class="overview-detail-pagination-footer-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        ov_page_input = render_pagination(
            current_page=st.session_state.overview_detail_page,
            total_pages=total_pages,
            first_item=first_item,
            last_item=last_item,
            total_rows=total_rows,
            sync_key="overview_detail_page_sync"
        )
        if ov_page_input and ov_page_input.isdigit():
            new_page = int(ov_page_input)
            if new_page != st.session_state.overview_detail_page:
                st.session_state.overview_detail_page = new_page
                st.rerun()

        # Mount Javascript listener
        patch_pagination()


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


def render_dashboard_app():
    # ?ap_logout=1 / ?ap_keepalive=1 are handled earlier, in login/app.py's
    # main(), before this function is ever reached — see the comment there
    # for why (it must run before the cookie/pending-session gate).
    init_dashboard_state()
    inject_dashboard_css()

    session_status = session_time_remaining(st.session_state.get("session_token"))
    if session_status:
        inject_session_watchdog(
            idle_elapsed_seconds=session_status["idle_elapsed_seconds"],
            idle_timeout_seconds=IDLE_TIMEOUT_SECONDS,
            warning_lead_seconds=IDLE_WARNING_LEAD_SECONDS,
        )

    st.markdown(
        f'<div class="ap-sidebar-state {"is-mini" if st.session_state.get("sidebar_minimized", False) else "is-expanded"}"></div>',
        unsafe_allow_html=True,
    )

    df_raw = get_active_dashboard_data()
    show_sidebar()

    menu = st.session_state.active_menu

    if menu == "Overview":
        page_overview(df_raw)
    elif menu == "Revenue Sharing":
        page_revenue_sharing()
    elif menu == "Lease Contract":
        render_lease_contract()
    elif menu == "Traffic Monitor":
        page_traffic_monitor()
    elif menu == "Import Manager":
        render_import_manager()
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
