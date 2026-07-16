from __future__ import annotations

import re
import secrets
import threading
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from html import escape
from typing import Any

import extra_streamlit_components as stx
import streamlit as st

# Penyimpanan sesi backend berjalan di memori proses server (_SESSION_STORE).
# Berbeda dengan st.session_state, penyimpanan ini tetap ada meskipun halaman dimuat ulang secara penuh (hard refresh).
AUTH_COOKIE_NAME = "ap_session_token"

IDLE_TIMEOUT = timedelta(minutes=60)
IDLE_WARNING_LEAD = timedelta(minutes=5)  # Tampilkan modal "sesi segera berakhir" beberapa menit sebelumnya
ABSOLUTE_TIMEOUT_NORMAL = timedelta(hours=8)
ABSOLUTE_TIMEOUT_REMEMBER = timedelta(days=3)

IDLE_TIMEOUT_SECONDS = IDLE_TIMEOUT.total_seconds()
IDLE_WARNING_LEAD_SECONDS = IDLE_WARNING_LEAD.total_seconds()

# Secure cookies akan ditolak pada protokol HTTP (seperti local dev); biarkan False untuk pengembangan.
COOKIE_SECURE = False


class Role(str, Enum):
    USER = "User"
    ADMIN = "Admin"


def _lookup_user_record(email: str) -> dict[str, str] | None:
    """DB-backed account lookup — replaces the old hardcoded DEMO_ACCOUNTS
    dict. Lazy-imports dashboard.connection since this module is loaded
    before the project root is guaranteed to be on sys.path (see login/app.py)."""
    from dashboard.connection import get_engine
    from sqlalchemy import text

    engine = get_engine()
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT username, password, role, pic_name FROM users WHERE username = :username"),
            {"username": email},
        ).mappings().first()
    return dict(row) if row else None


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


# Skema Sesi: token (PK), email, name, role, remember, login_at, last_activity_at, absolute_expires_at.
_SESSION_STORE: dict[str, dict[str, Any]] = {}
_SESSION_STORE_LOCK = threading.Lock()


def _now() -> datetime:
    return datetime.now()


def _new_token() -> str:
    return secrets.token_urlsafe(32)


def create_session(user: AuthUser, remember: bool) -> str:
    """Create server session record and return opaque token for browser cookie."""
    token = _new_token()
    now = _now()
    lifetime = ABSOLUTE_TIMEOUT_REMEMBER if remember else ABSOLUTE_TIMEOUT_NORMAL

    record = {
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "remember": remember,
        "login_at": now,
        "last_activity_at": now,
        "absolute_expires_at": now + lifetime,
    }
    with _SESSION_STORE_LOCK:
        _SESSION_STORE[token] = record
    return token


def invalidate_token(token: str | None) -> None:
    if not token:
        return
    with _SESSION_STORE_LOCK:
        _SESSION_STORE.pop(token, None)


def touch_session(token: str | None) -> bool:
    """Refresh session last_activity_at timestamp."""
    if not token:
        return False
    with _SESSION_STORE_LOCK:
        record = _SESSION_STORE.get(token)
        if not record:
            return False
        record["last_activity_at"] = _now()
        return True


def validate_token(token: str | None) -> tuple[AuthUser | None, bool, str | None]:
    """Validate token expiry, touch activity timestamp, and return user info."""
    if not token:
        return None, False, "invalid"

    with _SESSION_STORE_LOCK:
        record = _SESSION_STORE.get(token)
        if not record:
            return None, False, "invalid"

        now = _now()
        if now >= record["absolute_expires_at"]:
            del _SESSION_STORE[token]
            return None, False, "absolute_timeout"

        if now - record["last_activity_at"] >= IDLE_TIMEOUT:
            del _SESSION_STORE[token]
            return None, False, "idle_timeout"

        # Permintaan valid — memperbarui timestamp aktivitas dengan aman:
        # Setiap permintaan yang tervalidasi akan memperpanjang masa berlaku sesi aktif.
        record["last_activity_at"] = now
        remember = bool(record["remember"])
        try:
            user = AuthUser(
                email=record["email"],
                name=record["name"],
                role=normalize_role(record["role"]),
            )
        except ValueError:
            del _SESSION_STORE[token]
            return None, False, "invalid"

    return user, remember, None


def session_time_remaining(token: str | None) -> dict[str, float] | None:
    """Get remaining session lifetime details."""
    if not token:
        return None
    with _SESSION_STORE_LOCK:
        record = _SESSION_STORE.get(token)
        if not record:
            return None
        now = _now()
        idle_deadline = record["last_activity_at"] + IDLE_TIMEOUT
        deadline = min(idle_deadline, record["absolute_expires_at"])
        idle_elapsed = (now - record["last_activity_at"]).total_seconds()
        seconds_until_expiry = max(0.0, (deadline - now).total_seconds())

    return {
        "idle_elapsed_seconds": max(0.0, idle_elapsed),
        "idle_timeout_seconds": IDLE_TIMEOUT_SECONDS,
        "seconds_until_expiry": seconds_until_expiry,
    }


def init_auth_state() -> None:
    st.session_state.setdefault("is_authenticated", False)
    st.session_state.setdefault("auth_user", None)
    st.session_state.setdefault("user_name", "")
    st.session_state.setdefault("user_email", "")
    st.session_state.setdefault("user_role", "")
    st.session_state.setdefault("login_role", Role.USER.value)
    st.session_state.setdefault("remember_me", False)
    st.session_state.setdefault("session_token", None)
    st.session_state.setdefault("session_expired_reason", None)


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

    user_record = _lookup_user_record(normalized_email)
    if not user_record:
        return None, "Akun tidak ditemukan."

    import bcrypt
    if not bcrypt.checkpw(password.encode("utf-8"), user_record["password"].encode("utf-8")):
        return None, "Password tidak sesuai."

    role = normalize_role(user_record["role"])
    requested_role = normalize_role(selected_role)
    if role != requested_role:
        return None, (
            f"Akun ini terdaftar sebagai {role.value}, bukan {requested_role.value}. "
            f"Silakan pilih role {role.value}."
        )

    name = user_record.get("pic_name") or make_display_name(normalized_email)
    return AuthUser(email=normalized_email, name=name, role=role), ""


def login_user(user: AuthUser, remember: bool = False) -> None:
    init_auth_state()
    token = create_session(user, remember)

    st.session_state.is_authenticated = True
    st.session_state.auth_user = user.to_session()
    st.session_state.user_name = user.name
    st.session_state.user_email = user.email
    st.session_state.user_role = user.role.value
    st.session_state.login_role = user.role.value
    st.session_state.remember_me = remember
    st.session_state.session_token = token
    st.session_state.session_expired_reason = None

    _write_session_cookie(token, remember)


def logout_user() -> None:
    invalidate_token(st.session_state.get("session_token"))

    st.session_state.is_authenticated = False
    st.session_state.auth_user = None
    st.session_state.user_name = ""
    st.session_state.user_email = ""
    st.session_state.user_role = ""
    # Simpan state login_role agar pilihan user tidak hilang selama operasi cookie asinkron.
    st.session_state.session_token = None
    _clear_session_cookie()


def get_cookie_manager() -> stx.CookieManager:
    """Singleton CookieManager to maintain stable keys across reruns."""
    if "_ap_cookie_manager" not in st.session_state:
        st.session_state["_ap_cookie_manager"] = stx.CookieManager(key="ap_cookie_manager")
    return st.session_state["_ap_cookie_manager"]


def _get_cookies_or_none(cookie_manager: stx.CookieManager, key: str) -> dict[str, Any] | None:
    """Get cookies from manager, preserving None state if it hasn't resolved."""
    return cookie_manager.cookie_manager(method="getAll", key=key, default=None)


def is_session_check_pending() -> bool:
    """Check if session cookie detection is still in progress."""
    return bool(st.session_state.get("_ap_session_check_pending"))


def handle_logout_request() -> bool:
    """Handle query parameter logout request using session cookie."""
    cookie_manager = get_cookie_manager()
    cookies = _get_cookies_or_none(cookie_manager, "ap_logout_cookie_read")
    if cookies is None:
        return False

    token = st.session_state.get("session_token") or cookies.get(AUTH_COOKIE_NAME)
    invalidate_token(token)
    logout_user()
    return True


def _write_session_cookie(token: str, remember: bool) -> None:
    """Write token to client cookie with strict constraints."""
    cookie_manager = get_cookie_manager()
    lifetime = ABSOLUTE_TIMEOUT_REMEMBER if remember else ABSOLUTE_TIMEOUT_NORMAL
    cookie_manager.set(
        AUTH_COOKIE_NAME,
        token,
        expires_at=datetime.now() + lifetime,
        key="ap_set_auth_cookie",
        secure=COOKIE_SECURE,
        same_site="strict",
    )


def _clear_session_cookie() -> None:
    cookie_manager = get_cookie_manager()
    cookies = cookie_manager.get_all(key="ap_cookie_refresh_clear")
    if AUTH_COOKIE_NAME in cookies:
        cookie_manager.delete(AUTH_COOKIE_NAME, key="ap_delete_auth_cookie")


def validate_active_session() -> bool:
    """Validate the session on each render and recover from cookie if needed."""
    init_auth_state()

    import os
    if os.getenv("DEV_BYPASS_LOGIN", "false").lower() == "true" and not st.session_state.get("is_authenticated"):
        st.session_state["_ap_session_check_pending"] = False
        st.session_state.is_authenticated = True
        st.session_state.auth_user = {
            "email": "admin@airport.com",
            "name": "Developer",
            "role": "Admin"
        }
        st.session_state.user_name = "Developer"
        st.session_state.user_email = "admin@airport.com"
        st.session_state.user_role = "Admin"
        st.session_state.login_role = "Admin"
        return True

    cookie_manager = get_cookie_manager()
    cookies = _get_cookies_or_none(cookie_manager, "ap_cookie_refresh_validate")

    if cookies is None:
        # Tunggu validasi cookie selesai sebelum menampilkan antarmuka.
        st.session_state["_ap_session_check_pending"] = not st.session_state.is_authenticated
        return bool(st.session_state.is_authenticated)

    st.session_state["_ap_session_check_pending"] = False
    cookie_token = cookies.get(AUTH_COOKIE_NAME)

    token = st.session_state.get("session_token") or cookie_token
    if not token:
        if st.session_state.is_authenticated:
            logout_user()
        return False

    user, remember, reason = validate_token(token)
    if not user:
        # Hanya keluarkan (logout) sesi yang aktif untuk menghindari reset state pada UI login.
        if st.session_state.is_authenticated:
            st.session_state.session_expired_reason = reason
            logout_user()
        return False

    if not st.session_state.is_authenticated or st.session_state.get("session_token") != token:
        st.session_state.is_authenticated = True
        st.session_state.auth_user = user.to_session()
        st.session_state.user_name = user.name
        st.session_state.user_email = user.email
        st.session_state.user_role = user.role.value
        st.session_state.login_role = user.role.value
        st.session_state.session_token = token
        st.session_state.remember_me = remember
        st.session_state.session_expired_reason = None

    # Perbarui cookie secara berkala untuk memastikan sinkronisasi browser tetap terjaga.
    if cookie_token != token:
        _write_session_cookie(token, remember)

    return True


def is_authenticated() -> bool:
    """Perform quick session check for UI routing."""
    init_auth_state()
    return bool(st.session_state.is_authenticated and get_current_user())


def get_current_user() -> AuthUser | None:
    init_auth_state()
    return AuthUser.from_session(st.session_state.auth_user)


def get_current_role() -> Role | None:
    user = get_current_user()
    return user.role if user else None
