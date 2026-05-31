from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from html import escape
from typing import Any

import streamlit as st


class Role(str, Enum):
    USER = "User"
    ADMIN = "Admin"


class Permission(str, Enum):
    VIEW_DATA = "view_data"
    EDIT_DATA = "edit_data"
    IMPORT_DATA = "import_data"


ROLE_PERMISSIONS: dict[Role, set[Permission]] = {
    Role.USER: {
        Permission.VIEW_DATA,
        Permission.EDIT_DATA,
        Permission.IMPORT_DATA,
    },
    Role.ADMIN: {
        Permission.VIEW_DATA,
    },
}


DEMO_ACCOUNTS: dict[str, dict[str, str]] = {
    "user@airport.com": {
        "name": "Operational User",
        "password": "user12345",
        "role": Role.USER.value,
    },
    "admin@airport.com": {
        "name": "Administrator",
        "password": "admin12345",
        "role": Role.ADMIN.value,
    },
}

KNOWN_DOMAINS = ("@airport.com", "@example.com", "@injourney.com")


@dataclass(frozen=True)
class AuthUser:
    email: str
    name: str
    role: Role

    def to_session(self) -> dict[str, str]:
        return {
            "email": self.email,
            "name": self.name,
            "role": self.role.value,
        }

    @classmethod
    def from_session(cls, data: dict[str, Any] | None) -> "AuthUser | None":
        if not data:
            return None

        try:
            return cls(
                email=str(data["email"]),
                name=str(data["name"]),
                role=normalize_role(data["role"]),
            )
        except (KeyError, ValueError):
            return None


def init_auth_state() -> None:
    st.session_state.setdefault("is_authenticated", False)
    st.session_state.setdefault("auth_user", None)
    st.session_state.setdefault("user_name", "")
    st.session_state.setdefault("user_email", "")
    st.session_state.setdefault("user_role", "")
    st.session_state.setdefault("login_role", Role.USER.value)
    st.session_state.setdefault("remember_me", False)


def normalize_role(role: str | Role) -> Role:
    if isinstance(role, Role):
        return role

    for available_role in Role:
        if str(role).strip().lower() == available_role.value.lower():
            return available_role

    raise ValueError(f"Unknown role: {role}")


def available_roles() -> list[str]:
    return [role.value for role in Role]


def demo_email_for_role(role: str | Role) -> str:
    normalized_role = normalize_role(role)
    for email, account in DEMO_ACCOUNTS.items():
        if normalize_role(account["role"]) == normalized_role:
            return email

    raise ValueError(f"No demo email configured for role: {role}")


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(pattern, email) is not None


def account_exists(email: str) -> bool:
    normalized_email = email.strip().lower()
    return normalized_email in DEMO_ACCOUNTS or normalized_email.endswith(KNOWN_DOMAINS)


def make_display_name(email: str) -> str:
    username = email.split("@", 1)[0].replace(".", " ").replace("_", " ")
    return username.title() or "User"


def authenticate_user(
    email: str,
    password: str,
    selected_role: str | Role = Role.USER,
) -> tuple[AuthUser | None, str]:
    normalized_email = email.strip().lower()

    if not normalized_email and not password:
        return None, "Masukkan email dan password Anda."
    if not normalized_email:
        return None, "Email wajib diisi."
    if not password:
        return None, "Password wajib diisi."
    if not validate_email(normalized_email):
        return None, "Format email tidak valid."
    if not account_exists(normalized_email):
        return None, "Akun tidak ditemukan."

    try:
        requested_role = normalize_role(selected_role)
    except ValueError:
        return None, "Role tidak valid."

    demo_account = DEMO_ACCOUNTS.get(normalized_email)

    if demo_account:
        if password != demo_account["password"]:
            return None, "Password tidak sesuai."

        account_role = normalize_role(demo_account["role"])
        if account_role != requested_role:
            return None, (
                "Akun tidak ditemukan. Periksa email, password, dan role yang Anda pilih."
            )

        role = account_role
        name = demo_account["name"]
    else:
        # Prototype fallback. For production, replace this with a database lookup
        # and never trust role data submitted from the UI.
        role = requested_role
        name = make_display_name(normalized_email)

    return AuthUser(email=normalized_email, name=name, role=role), ""


def login_user(user: AuthUser) -> None:
    init_auth_state()
    st.session_state.is_authenticated = True
    st.session_state.auth_user = user.to_session()
    st.session_state.user_name = user.name
    st.session_state.user_email = user.email
    st.session_state.user_role = user.role.value
    st.session_state.login_role = user.role.value


def logout_user() -> None:
    st.session_state.is_authenticated = False
    st.session_state.auth_user = None
    st.session_state.user_name = ""
    st.session_state.user_email = ""
    st.session_state.user_role = ""
    st.session_state.login_role = Role.USER.value
    st.session_state.email_input = ""


def is_authenticated() -> bool:
    init_auth_state()
    return bool(st.session_state.is_authenticated and get_current_user())


def get_current_user() -> AuthUser | None:
    init_auth_state()
    return AuthUser.from_session(st.session_state.auth_user)


def get_current_role() -> Role | None:
    user = get_current_user()
    return user.role if user else None


def has_permission(permission: Permission, role: Role | None = None) -> bool:
    current_role = role or get_current_role()
    if current_role is None:
        return False

    return permission in ROLE_PERMISSIONS.get(current_role, set())


def can_view(role: Role | None = None) -> bool:
    return has_permission(Permission.VIEW_DATA, role)


def can_edit(role: Role | None = None) -> bool:
    return has_permission(Permission.EDIT_DATA, role)


def get_access_mode_label(role: Role | None = None) -> str:
    current_role = role or get_current_role()
    if current_role == Role.USER:
        return "Edit mode"
    if current_role == Role.ADMIN:
        return "Read-only mode"
    return "Guest"


def require_login() -> None:
    if is_authenticated():
        return

    st.markdown(
        """
        <div style="
            max-width: 560px;
            margin: 80px auto;
            padding: 28px;
            border: 1px solid #e5e7eb;
            border-radius: 18px;
            background: #ffffff;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
        ">
            <div style="font-size:18px;font-weight:700;color:#111827;margin-bottom:8px;">
                Login diperlukan
            </div>
            <div style="font-size:14px;line-height:1.7;color:#64748b;">
                Silakan masuk melalui halaman login sebelum membuka dashboard.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()


def require_permission(permission: Permission, feature_name: str = "fitur ini") -> bool:
    if has_permission(permission):
        return True

    render_read_only_notice(feature_name)
    return False


def render_read_only_notice(feature_name: str = "fitur ini") -> None:
    safe_feature_name = escape(feature_name)
    st.markdown(
        f"""
        <div style="
            margin: 10px 0 18px;
            padding: 14px 16px;
            border: 1px solid #d7e7e5;
            border-left: 4px solid #068585;
            border-radius: 14px;
            background: linear-gradient(180deg, #ffffff 0%, #f5fbfa 100%);
            color: #334155;
            font-size: 13px;
            line-height: 1.6;
        ">
            Anda masuk sebagai <b>Admin</b>. {safe_feature_name} tersedia dalam mode lihat saja.
        </div>
        """,
        unsafe_allow_html=True,
    )
