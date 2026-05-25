import streamlit as st
from access_control import (
    authenticate_user,
    available_roles,
    get_access_mode_label,
    get_current_user,
    init_auth_state,
    is_authenticated,
    login_user,
    logout_user,
)
from ui_shared import app_shell, render_auth_header, show_error
from forgot_pass import render_forgot_panel
from reset_pass import render_reset_panel

st.set_page_config(
    page_title="Airport Monitoring Dashboard Login",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="collapsed",
)

init_auth_state()

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"

page_param = st.query_params.get("page", "login")
if page_param in ["login", "forgot_password", "reset_password"]:
    st.session_state.auth_page = page_param


def render_login_panel() -> None:
    render_auth_header(
        "Airport Monitoring",
        "Sign in to access your dashboard",
    )

    if is_authenticated():
        current_user = get_current_user()
        if current_user:
            st.markdown(
                f"""
                <div class="success-box">
                    Login aktif sebagai <b>{current_user.name}</b>
                    ({current_user.role.value}) - {get_access_mode_label(current_user.role)}.
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown('<div class="auth-bottom-gap"></div>', unsafe_allow_html=True)
            if st.button("Logout", key="logout_btn", use_container_width=True):
                logout_user()
                st.rerun()

            return

    role_options = available_roles()
    selected_role = st.segmented_control(
        "Role",
        role_options,
        default=st.session_state.login_role,
        key="login_role_selector",
        label_visibility="collapsed",
        width="stretch",
    )

    if selected_role and selected_role != st.session_state.login_role:
        st.session_state.login_role = selected_role
        st.rerun()

    st.markdown('<div class="field-label">Email</div>', unsafe_allow_html=True)
    email = st.text_input(
        "Email",
        placeholder="user@airport.com",
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

    sign_in_clicked = st.button(
        "Sign In",
        use_container_width=True,
        key="sign_in_btn",
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

        login_user(user)
        st.success(
            f"Login berhasil sebagai {user.role.value}. Email yang digunakan: {user.email}"
        )
        st.rerun()


def render_current_page() -> None:
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
    app_shell(render_current_page)


if __name__ == "__main__":
    main()
