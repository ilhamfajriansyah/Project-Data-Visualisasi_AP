import streamlit as st

try:
    from .ui_shared import render_auth_header, show_error
except ImportError:
    from ui_shared import render_auth_header, show_error


def validate_new_password(password: str, confirm_password: str) -> tuple[bool, str]:
    if not password and not confirm_password:
        return False, "Masukkan password baru dan konfirmasi password."
    if not password:
        return False, "Password baru wajib diisi."
    if not confirm_password:
        return False, "Konfirmasi password wajib diisi."
    if len(password) < 8:
        return False, "Password minimal 8 karakter."
    if password != confirm_password:
        return False, "Konfirmasi password tidak cocok."
    return True, ""


def go_to(page_name: str) -> None:
    st.session_state.auth_page = page_name
    st.query_params["page"] = page_name
    st.rerun()


def render_reset_panel() -> None:
    if "password_reset_success" not in st.session_state:
        st.session_state.password_reset_success = False

    render_auth_header(
        "Set Password Baru",
        "Masukkan password baru untuk akun Anda",
    )

    st.markdown(
        """
        <div class="info-box">
            <div class="info-box-icon">ⓘ</div>
            <div class="info-box-text">
                Gunakan minimal 8 karakter. Disarankan menggabungkan huruf besar,
                huruf kecil, angka, dan simbol.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.form("reset_password_form", clear_on_submit=False):
        st.markdown('<div class="field-label">Password Baru</div>', unsafe_allow_html=True)
        password = st.text_input(
            "Password Baru",
            placeholder="••••••••",
            type="password",
            label_visibility="collapsed",
            key="new_password_input",
        )

        st.markdown('<div class="field-label">Konfirmasi Password</div>', unsafe_allow_html=True)
        confirm_password = st.text_input(
            "Konfirmasi Password",
            placeholder="••••••••",
            type="password",
            label_visibility="collapsed",
            key="confirm_password_input",
        )

        submitted = st.form_submit_button("Simpan Password Baru", use_container_width=True)

    if submitted:
        is_valid, error_message = validate_new_password(password, confirm_password)
        if is_valid:
            st.session_state.password_reset_success = True
        else:
            show_error(error_message)

    if st.session_state.password_reset_success:
        st.markdown(
            """
            <div class="success-box">
                Password berhasil diperbarui.
                Silakan kembali ke halaman login untuk masuk ke sistem.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="bottom-link-button-wrap">', unsafe_allow_html=True)
    back_clicked = st.button(
        "Kembali ke Login",
        key="reset_back_to_login_btn",   # atau reset_back_to_login_btn
        use_container_width=False,
        type="secondary",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if back_clicked:
        st.session_state.password_reset_success = False
        go_to("login")
