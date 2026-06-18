"""Shared top navigation — avoids circular imports from page modules."""

from html import escape

import streamlit as st

from login.access_control import Role, get_current_role


def topnav_actions_html():
    """Bell + profile/logout menu — shared so any custom header layout can reuse it
    without duplicating (and risking breaking) the logout link."""
    user_name = escape(st.session_state.user_name or "User")
    role_label = "Admin" if get_current_role() == Role.ADMIN else "Analyst"
    return f"""
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
                <a class="ap-profile-menu-item" href="?ap_logout=1" target="_self">
                    <span class="ap-profile-menu-icon">↪</span>
                    <span>Logout</span>
                </a>
            </div>
        </details>
    </div>
    """


def show_topnav(title="Non Aeronautical Dashboard", subtitle=None, show_search=True):
    if show_search:
        n1, n2, n3 = st.columns([3, 4, 3])
    else:
        n1, n3 = st.columns([4, 6])
        n2 = None
    with n1:
        subtitle_html = ""
        if subtitle:
            subtitle_html = (
                f'<p style="margin:4px 0 0;color:#64748B;font-size:12px;font-weight:500;'
                f'font-family:Poppins,sans-serif;">{escape(subtitle)}</p>'
            )
        st.markdown(
            f'<h2 style="margin:0;font-size:19px;font-weight:800;color:#0f172a;'
            f'padding-top:0;">{escape(title)}</h2>{subtitle_html}',
            unsafe_allow_html=True,
        )
    if show_search:
        with n2:
            st.text_input(
                "Search",
                placeholder="🔍  Searching anything...",
                label_visibility="collapsed",
                key="search_bar",
            )
    with n3:
        st.markdown(topnav_actions_html(), unsafe_allow_html=True)
    st.markdown('<div class="nad-top-divider"></div>', unsafe_allow_html=True)
