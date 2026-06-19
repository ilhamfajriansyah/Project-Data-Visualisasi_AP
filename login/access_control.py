from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from html import escape
from typing import Any

import extra_streamlit_components as stx
import streamlit as st

AUTH_COOKIE_NAME = "ap_auth_session"
AUTH_COOKIE_MAX_AGE_DAYS = 30


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

    demo_account = DEMO_ACCOUNTS.get(normalized_email)

    if demo_account:
        if password != demo_account["password"]:
            return None, "Password tidak sesuai."

        role = normalize_role(demo_account["role"])
        requested_role = normalize_role(selected_role)
        if role != requested_role:
            return None, (
                f"Akun ini terdaftar sebagai {role.value}, bukan {requested_role.value}. "
                f"Silakan pilih role {role.value}."
            )

        name = demo_account["name"]
    else:
        # Prototype fallback. For production, replace this with a database lookup
        # and never trust role data submitted from the UI.
        role = normalize_role(selected_role)
        name = make_display_name(normalized_email)

    return AuthUser(email=normalized_email, name=name, role=role), ""


def login_user(user: AuthUser, remember: bool = False) -> None:
    init_auth_state()
    st.session_state.is_authenticated = True
    st.session_state.auth_user = user.to_session()
    st.session_state.user_name = user.name
    st.session_state.user_email = user.email
    st.session_state.user_role = user.role.value
    st.session_state.login_role = user.role.value
    st.session_state.remember_me = remember

    if remember:
        persist_session(user)
    else:
        clear_persisted_session()


def logout_user() -> None:
    st.session_state.is_authenticated = False
    st.session_state.auth_user = None
    st.session_state.user_name = ""
    st.session_state.user_email = ""
    st.session_state.user_role = ""
    st.session_state.login_role = Role.USER.value
    clear_persisted_session()


def get_cookie_manager() -> stx.CookieManager:
    """Singleton CookieManager — must reuse the same instance/key across
    reruns, otherwise extra_streamlit_components re-mounts the underlying
    component and cookie reads become unreliable.

    Note: the manager's own __init__ only snapshots the browser's cookies
    once, at construction time. Don't rely on that snapshot (via .get()) —
    always call .get_all() explicitly when you need a fresh read, since
    that's the only method that actually re-queries the browser."""
    if "_ap_cookie_manager" not in st.session_state:
        st.session_state["_ap_cookie_manager"] = stx.CookieManager(key="ap_cookie_manager")
    return st.session_state["_ap_cookie_manager"]


def ensure_session_persisted() -> None:
    """Re-assert the remember-me cookie on every authenticated render.

    Setting the cookie once, right before the st.rerun() that follows a
    successful login, is unreliable: the cookie-writing component is an
    iframe that needs a round-trip to the browser to actually execute its
    JS, and the immediate rerun can cut that short before it finishes.
    Calling this on every dashboard render (it's a cheap no-op once the
    cookie already matches) gives it many more chances to actually stick
    before the user ever hits refresh."""
    if not st.session_state.get("is_authenticated"):
        return
    if not st.session_state.get("remember_me"):
        return

    user = get_current_user()
    if user:
        persist_session(user)


def persist_session(user: AuthUser) -> None:
    """Only called when the user ticks "Remember Me" at login — writes the
    session to a browser cookie so a page refresh (or new browser session,
    within the cookie's lifetime) doesn't bounce back to the login page."""
    cookie_manager = get_cookie_manager()
    expires_at = datetime.now() + timedelta(days=AUTH_COOKIE_MAX_AGE_DAYS)
    cookie_manager.set(
        AUTH_COOKIE_NAME,
        json.dumps(user.to_session()),
        expires_at=expires_at,
        key="ap_set_auth_cookie",
    )


def clear_persisted_session() -> None:
    cookie_manager = get_cookie_manager()
    cookies = cookie_manager.get_all(key="ap_cookie_refresh_clear")
    if AUTH_COOKIE_NAME in cookies:
        cookie_manager.delete(AUTH_COOKIE_NAME, key="ap_delete_auth_cookie")


def restore_session_from_cookie() -> bool:
    """Call once near the top of the app, before any login check. If the
    user isn't already authenticated in this session but a valid "Remember
    Me" cookie exists from a previous session, transparently log them back
    in instead of showing the login page after a refresh."""
    init_auth_state()
    if st.session_state.is_authenticated:
        return True

    cookie_manager = get_cookie_manager()
    # Force a fresh read from the browser — the snapshot taken when the
    # manager was constructed is frequently stale/empty on the very first
    # rerun after the underlying component finishes loading.
    cookies = cookie_manager.get_all(key="ap_cookie_refresh_restore")
    raw_value = cookies.get(AUTH_COOKIE_NAME)
    if not raw_value:
        return False

    try:
        data = json.loads(raw_value)
        user = AuthUser.from_session(data)
    except (ValueError, TypeError):
        user = None

    if not user:
        cookie_manager.delete(AUTH_COOKIE_NAME, key="ap_delete_invalid_cookie")
        return False

    # Re-validate against the demo account table so a stale/edited cookie
    # can't grant a role the account no longer has.
    demo_account = DEMO_ACCOUNTS.get(user.email)
    if demo_account and normalize_role(demo_account["role"]) != user.role:
        cookie_manager.delete(AUTH_COOKIE_NAME, key="ap_delete_mismatched_cookie")
        return False

    login_user(user, remember=True)
    return True


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
