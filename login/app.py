import sys
from pathlib import Path

import streamlit as st

LOGIN_DIR = Path(__file__).resolve().parent
PROJECT_DIR = LOGIN_DIR.parent

for path in (PROJECT_DIR, LOGIN_DIR):
    path_text = str(path)
    if path_text not in sys.path:
        sys.path.insert(0, path_text)

if __package__:
    from .access_control import (
        authenticate_user,
        available_roles,
        handle_logout_request,
        init_auth_state,
        is_authenticated,
        is_session_check_pending,
        login_user,
        touch_session,
        validate_active_session,
    )
    from .forgot_pass import render_forgot_panel
    from .reset_pass import render_reset_panel
    from .ui_shared import app_shell, render_auth_header, render_role_selector, show_error
else:
    from access_control import (
        authenticate_user,
        available_roles,
        handle_logout_request,
        init_auth_state,
        is_authenticated,
        is_session_check_pending,
        login_user,
        touch_session,
        validate_active_session,
    )
    from forgot_pass import render_forgot_panel
    from reset_pass import render_reset_panel
    from ui_shared import app_shell, render_auth_header, render_role_selector, show_error


def init_login_page_state() -> None:
    init_auth_state()
    st.session_state.setdefault("auth_page", "login")

    page_param = st.query_params.get("page", "login")
    if page_param in ["login", "forgot_password", "reset_password"]:
        st.session_state.auth_page = page_param


SESSION_EXPIRED_MESSAGES = {
    "idle_timeout": "Sesi Anda berakhir karena tidak ada aktivitas selama 60 menit.",
    "absolute_timeout": "Sesi Anda berakhir. Silakan login kembali.",
}


def render_login_panel() -> None:
    if is_authenticated():
        return

    render_auth_header(
        "Airport Monitoring",
        "Sign in to access your dashboard",
    )

    # "invalid" (token unrecognized — e.g. right after a normal logout, or
    # a first-ever visit with a stale/foreign cookie) is intentionally NOT
    # shown here: it isn't an unexpected expiry, just "not logged in", and
    # alarming the user about it on every fresh visit/logout would be
    # noise. Only genuine idle/absolute timeouts warrant the notice.
    expired_reason = st.session_state.pop("session_expired_reason", None)
    expired_message = SESSION_EXPIRED_MESSAGES.get(expired_reason)
    if expired_message:
        show_error(expired_message)

    role_options = available_roles()
    if "login_role_initialized" not in st.session_state:
        st.session_state.login_role = role_options[0]
        st.session_state.email_input = ""
        st.session_state.login_role_initialized = True

    if st.session_state.login_role not in role_options:
        st.session_state.login_role = role_options[0]
        st.session_state.email_input = ""

    if (
        "login_role_selector" not in st.session_state
        or st.session_state.login_role_selector not in role_options
    ):
        st.session_state.login_role_selector = st.session_state.login_role

    selected_role = render_role_selector(role_options, st.session_state.login_role)

    if selected_role != st.session_state.login_role:
        st.session_state.login_role = selected_role
        st.rerun()

    role_email = "admin@airport.com" if st.session_state.login_role == "Admin" else "user@airport.com"

    with st.form("login_form", clear_on_submit=False):
        st.markdown('<div class="field-label">Email</div>', unsafe_allow_html=True)
        email = st.text_input(
            "Email",
            placeholder=role_email,
            label_visibility="collapsed",
            key="email_input",
        )

        st.markdown('<div class="field-label">Password</div>', unsafe_allow_html=True)
        password = st.text_input(
            "Password",
            placeholder="••••••••",
            type="password",
            label_visibility="collapsed",
            key="password_input",
        )

        helper_left, helper_right = st.columns([1, 1], vertical_alignment="center")

        with helper_left:
            remember = st.checkbox(
                "Remember Me",
                value=st.session_state.remember_me,
                key="remember_me_checkbox",
            )

        with helper_right:
            st.markdown(
                """
                <div class="forgot-password-link-wrap">
                    <a class="forgot-password-link" href="?page=forgot_password" target="_self">
                        Lupa Password?
                    </a>
                </div>
                """,
                unsafe_allow_html=True,
            )

        sign_in_clicked = st.form_submit_button(
            "Sign In",
            use_container_width=True,
            type="primary",
        )

    if sign_in_clicked:
        st.session_state.remember_me = remember
        with st.spinner("Memproses login..."):
            user, error_message = authenticate_user(
                email=email,
                password=password,
                selected_role=st.session_state.login_role,
            )

        if not user:
            show_error(error_message)
            return

        login_user(user, remember=remember)
        st.session_state.auth_page = "login"
        st.query_params.clear()
        st.rerun()


def render_current_page() -> None:
    init_login_page_state()
    page = st.session_state.auth_page

    if page == "login":
        render_login_panel()
    elif page == "forgot_password":
        render_forgot_panel()
    elif page == "reset_password":
        render_reset_panel()
    else:
        st.session_state.auth_page = "login"
        render_login_panel()


def main() -> None:
    st.set_page_config(
        page_title="Airport Monitoring Dashboard Login",
        page_icon="A",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    init_auth_state()

    # Handle ?ap_logout=1 unconditionally, before any other session logic.
    # The Logout link is a real page navigation (target="_self"), which
    # starts a brand-new Streamlit session — st.session_state has no token
    # to invalidate yet, only the (async) cookie does. handle_logout_request
    # waits for that cookie read to resolve before acting, so we don't risk
    # invalidating nothing and having the old session quietly restore
    # itself right back.
    if st.query_params.get("ap_logout") == "1":
        if not handle_logout_request():
            st.stop()
        st.query_params.clear()
        st.rerun()

    # Same reasoning as logout above — this is a real page navigation
    # (window.parent.location.search = '?ap_keepalive=1' from the session
    # watchdog's JS), so handle it before any cookie/pending gate so an
    # activity ping is never silently dropped behind that race.
    if st.query_params.get("ap_keepalive") == "1":
        st.query_params.clear()
        touch_session(st.session_state.get("session_token"))
        st.rerun()

    validate_active_session()

    if is_authenticated():
        from dashboard import render_dashboard_app

        render_dashboard_app()
        return

    if is_session_check_pending():
        # We genuinely don't know yet whether a remember-me cookie exists
        # (the cookie component hasn't reported back this run) — render
        # nothing rather than flashing the login page; Streamlit reruns
        # automatically the moment the component resolves.
        st.stop()

    app_shell(render_current_page)


if __name__ == "__main__":
    main()
