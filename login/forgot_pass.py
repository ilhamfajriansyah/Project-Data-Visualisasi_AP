import re
import streamlit as st
from ui_shared import render_auth_header, show_error


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def go_to(page_name: str) -> None:
    st.session_state.auth_page = page_name
    st.query_params["page"] = page_name
    st.rerun()


def render_forgot_panel() -> None:
    if "reset_email_sent" not in st.session_state:
        st.session_state.reset_email_sent = False

    render_auth_header(
        "Reset Password",
        "Masukkan email Anda untuk menerima link reset password",
    )

    st.markdown(
        """
        <div class="info-box">
            <div class="info-box-icon">ⓘ</div>
            <div class="info-box-text">
                Masukkan email yang terdaftar. Jika akun ditemukan, kami akan mengirimkan
                link reset password ke email Anda.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="forgot-form-top-gap"></div>', unsafe_allow_html=True)

    with st.form("forgot_password_form", clear_on_submit=False):
        st.markdown('<div class="field-label">Email</div>', unsafe_allow_html=True)
        email = st.text_input(
            "Email",
            placeholder="user@airport.com",
            label_visibility="collapsed",
            key="forgot_email_input",
        )

        submitted = st.form_submit_button("Kirim Link Reset", use_container_width=True)

    if submitted:
        if not email:
            show_error("Email wajib diisi.")
        elif not validate_email(email):
            show_error("Format email tidak valid.")
        else:
            st.session_state.reset_email_sent = True

    if st.session_state.reset_email_sent:
        st.markdown(
            """
            <div class="success-box">
                Jika email terdaftar, link reset password telah dikirim.
                Silakan cek inbox atau folder spam Anda.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="forgot-bottom-gap"></div>', unsafe_allow_html=True)

    left_spacer, center_col, right_spacer = st.columns([1, 1, 1])
    with center_col:
        back_clicked = st.button(
            "Kembali ke Login",
            key="forgot_back_to_login_btn",
            type="tertiary",
            use_container_width=True,
        )

    if back_clicked:
        st.session_state.reset_email_sent = False
        go_to("login")