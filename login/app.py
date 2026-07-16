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
    from ui_shared import app_shell, render_auth_header, render_role_selector, show_error


def init_login_page_state() -> None:
    init_auth_state()
    st.session_state.setdefault("auth_page", "login")


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

    # Tampilkan pesan error hanya jika sesi benar-benar kedaluwarsa.
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
        email = st.text_input(
            "Email",
            placeholder=role_email,
            label_visibility="visible",
            key="email_input",
        )

        password = st.text_input(
            "Password",
            placeholder="••••••••",
            type="password",
            label_visibility="visible",
            key="password_input",
        )

        remember = st.checkbox(
            "Remember Me",
            value=st.session_state.remember_me,
            key="remember_me_checkbox",
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
    render_login_panel()


def main() -> None:
    st.set_page_config(
        page_title="Airport Monitoring Dashboard Login",
        page_icon="A",
        layout="wide",
        initial_sidebar_state="collapsed",
    )

    init_auth_state()

    # Tangani proses logout secara langsung.
    if st.query_params.get("ap_logout") == "1":
        if not handle_logout_request():
            st.stop()
        st.query_params.clear()
        st.rerun()

    # Tangani proses keepalive untuk mempertahankan sesi.
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
        st.stop()

    app_shell(render_current_page)


if __name__ == "__main__":
    main()
