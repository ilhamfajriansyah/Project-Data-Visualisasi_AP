import re
import streamlit as st
from ui_shared import app_shell, render_auth_header, show_error
from forgot_pass import render_forgot_panel
from reset_pass import render_reset_panel

st.set_page_config(
    page_title="Airport Monitoring Dashboard Login",
    page_icon="A",
    layout="wide",
    initial_sidebar_state="collapsed",
)

if "role" not in st.session_state:
    st.session_state.role = "User"

if "remember_me" not in st.session_state:
    st.session_state.remember_me = False

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "login"

page_param = st.query_params.get("page", "login")
if page_param in ["login", "forgot_password", "reset_password"]:
    st.session_state.auth_page = page_param


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def account_exists(email: str) -> bool:
    known_domains = ["@airport.com", "@example.com", "@injourney.com"]
    return any(email.endswith(domain) for domain in known_domains)


def validate_login(email: str, password: str) -> tuple[bool, str]:
    if not email and not password:
        return False, "Masukkan email dan password Anda."
    if not email:
        return False, "Email wajib diisi."
    if not password:
        return False, "Password wajib diisi."
    if not validate_email(email):
        return False, "Format email tidak valid."
    if not account_exists(email):
        return False, "Akun tidak ditemukan."
    return True, ""


def go_to(page_name: str) -> None:
    st.session_state.auth_page = page_name
    st.query_params["page"] = page_name
    st.rerun()


def render_login_panel() -> None:
    render_auth_header(
        "Airport Monitoring",
        "Silahkan masuk ke sistem",
    )

    role_left, role_right = st.columns(2)

    with role_left:
        user_btn = st.button(
            "User",
            use_container_width=True,
            key="role_user_btn",
            type="primary" if st.session_state.role == "User" else "secondary",
        )

    with role_right:
        admin_btn = st.button(
            "Admin",
            use_container_width=True,
            key="role_admin_btn",
            type="primary" if st.session_state.role == "Admin" else "secondary",
        )

    if user_btn:
        st.session_state.role = "User"
        st.rerun()

    if admin_btn:
        st.session_state.role = "Admin"
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
        is_valid, error_message = validate_login(email, password)

        if is_valid:
            st.success(
                f"Login berhasil sebagai {st.session_state.role}. Email yang digunakan: {email}"
            )
        else:
            show_error(error_message)


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
