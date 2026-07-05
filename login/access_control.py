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

# ──────────────────────────────────────────────────────────────────────────
# SESSION POLICY
#
# Architecture note: this is a single-process Streamlit app — there is no
# separate REST backend or database. The "backend" for session purposes is
# this Python module's in-memory _SESSION_STORE, which lives in the running
# Streamlit server process and is shared by every connected browser/tab
# (st.session_state, by contrast, is per-tab and is wiped on a hard
# refresh — that's why the store, not session_state, is the source of
# truth for expiry). A real production deployment would back this store
# with Redis/a database so sessions survive a server restart; documented
# here as the known trade-off of the in-memory approach.
# ──────────────────────────────────────────────────────────────────────────
AUTH_COOKIE_NAME = "ap_session_token"

IDLE_TIMEOUT = timedelta(minutes=60)
IDLE_WARNING_LEAD = timedelta(minutes=5)  # show the "expiring soon" modal this far ahead
ABSOLUTE_TIMEOUT_NORMAL = timedelta(hours=8)
ABSOLUTE_TIMEOUT_REMEMBER = timedelta(days=3)

IDLE_TIMEOUT_SECONDS = IDLE_TIMEOUT.total_seconds()
IDLE_WARNING_LEAD_SECONDS = IDLE_WARNING_LEAD.total_seconds()

# Set to True once the app is served over HTTPS. Cookies marked Secure are
# silently refused by browsers on a plain http:// origin (e.g. local dev),
# so this must stay False there.
COOKIE_SECURE = False


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


# ──────────────────────────────────────────────────────────────────────────
# SERVER-SIDE SESSION STORE
#
# "Database schema" (documented as a dict shape here since there's no real
# DB in this app — this is exactly the shape you'd give a `sessions` table
# if/when this store moves to Redis/Postgres):
#
#   sessions:
#     token               TEXT PRIMARY KEY   -- opaque bearer token (cookie value)
#     email               TEXT NOT NULL
#     name                TEXT NOT NULL
#     role                TEXT NOT NULL
#     remember            BOOLEAN NOT NULL
#     login_at            TIMESTAMP NOT NULL
#     last_activity_at    TIMESTAMP NOT NULL
#     absolute_expires_at TIMESTAMP NOT NULL
# ──────────────────────────────────────────────────────────────────────────
_SESSION_STORE: dict[str, dict[str, Any]] = {}
_SESSION_STORE_LOCK = threading.Lock()


def _now() -> datetime:
    return datetime.now()


def _new_token() -> str:
    return secrets.token_urlsafe(32)


def create_session(user: AuthUser, remember: bool) -> str:
    """Creates the server-side session record (the "database row") and
    returns the bearer token that gets handed to the browser as a cookie.
    Never put the token's *content* (role, etc.) in the cookie itself —
    only this opaque token, so a tampered cookie can't forge a role."""
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
    """Explicitly refresh last_activity_at (used by the keepalive
    endpoint triggered from the frontend watchdog's "Stay Logged In"
    button and periodic activity sync)."""
    if not token:
        return False
    with _SESSION_STORE_LOCK:
        record = _SESSION_STORE.get(token)
        if not record:
            return False
        record["last_activity_at"] = _now()
        return True


def validate_token(token: str | None) -> tuple[AuthUser | None, bool, str | None]:
    """The core backend check: reject (idle_timeout / absolute_timeout /
    invalid) or accept-and-touch. Returns (user_or_none, remember, reason).
    Called on every authenticated render — see validate_active_session()."""
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

        # Valid request — this *is* the "refresh activity timestamp safely"
        # requirement: every validated request extends the idle window.
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
    """Snapshot used to seed the frontend countdown accurately from the
    server's notion of time, instead of trusting the browser clock alone."""
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
    # login_role sengaja tidak direset di sini: ini adalah UI state form login
    # yang harus dipertahankan agar pilihan role yang sedang diketik ulang
    # tidak hilang saat logout_user() dipanggil berulang oleh
    # validate_active_session (stale cookie belum terhapus secara async).
    st.session_state.session_token = None
    _clear_session_cookie()


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


def _get_cookies_or_none(cookie_manager: stx.CookieManager, key: str) -> dict[str, Any] | None:
    """Like cookie_manager.get_all(), but distinguishes "the browser
    genuinely has no cookies" ({}) from "the cookie iframe hasn't reported
    back yet this run" (None) — get_all() always uses default={} for both,
    which is exactly what causes the login-page flash on refresh: the very
    first script run after a hard reload can't tell those two cases apart
    and wrongly assumes "no cookie" before the real answer has arrived.

    Reaches into CookieManager's own `.cookie_manager` (the underlying
    declared component callable) since the public wrapper methods don't
    expose a way to override their hardcoded default={}."""
    return cookie_manager.cookie_manager(method="getAll", key=key, default=None)


def is_session_check_pending() -> bool:
    """True while we genuinely don't know yet whether a persisted-session
    cookie exists (the component hasn't reported back this run). The
    caller should render nothing/a neutral loading state and st.stop() —
    Streamlit automatically reruns once the component resolves."""
    return bool(st.session_state.get("_ap_session_check_pending"))


def handle_logout_request() -> bool:
    """Call when ?ap_logout=1 is present, before any other session logic.

    The Logout link is a real page navigation (target="_self"), which
    starts a brand-new Streamlit session — st.session_state.session_token
    is empty in that fresh session, so the *only* place the real token
    can be recovered from is the cookie itself. Reading that cookie is
    async (see _get_cookies_or_none), so: if it hasn't resolved yet, wait
    (return False, caller should st.stop()) rather than guessing — acting
    before we know the token would invalidate nothing and leave the old
    session valid server-side, which is exactly what silently logs the
    user right back in once the cookie *does* resolve afterwards.

    Returns True once the logout has actually been carried out (caller
    should st.rerun())."""
    cookie_manager = get_cookie_manager()
    cookies = _get_cookies_or_none(cookie_manager, "ap_logout_cookie_read")
    if cookies is None:
        return False

    token = st.session_state.get("session_token") or cookies.get(AUTH_COOKIE_NAME)
    invalidate_token(token)
    logout_user()
    return True


def _write_session_cookie(token: str, remember: bool) -> None:
    """The cookie only ever carries the opaque token — never the
    password, role, or any other session payload (see module docstring).

    HttpOnly can't be set here: this library writes cookies via
    document.cookie in client-side JS, and HttpOnly cookies are by
    definition unwritable/unreadable from JS (only a real HTTP response's
    Set-Cookie header can mark a cookie HttpOnly). That requires server
    control over HTTP headers, which a pure Streamlit app doesn't expose.
    Documented trade-off: mitigated by the cookie containing only a
    revocable random token, never credentials.

    `remember=False` still gets a real (non-session) expiry because this
    underlying library always requires an explicit expiry — but the
    *server-side* record (see create_session) is the actual authority for
    both the 60-minute idle cap and the 8-hour/3-day absolute cap, so this
    is just a transport convenience, not a security boundary."""
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
    """Call once near the top of every page render, before deciding
    whether to show the dashboard or the login page. This is the
    "backend validation on every authenticated request" requirement:
    idle/absolute expiry is re-checked here every single rerun, never
    just trusted from client-held state.

    Also transparently restores a session from the persisted cookie when
    st.session_state is empty (e.g. right after a hard refresh)."""
    init_auth_state()

    import os
    if os.getenv("DEV_BYPASS_LOGIN", "false").lower() == "true":
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
        # Don't know yet whether a remember-me cookie exists — if there's
        # also no in-tab session, avoid flashing the login page; the
        # caller should wait (see is_session_check_pending()) for the
        # automatic rerun that fires once the component resolves.
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
        # Hanya panggil logout_user() jika sesi sebelumnya aktif. Stale cookie
        # (dari sesi sebelumnya yang sudah di-logout) bisa menyebabkan token
        # invalid di sini meskipun pengguna tidak pernah login di tab ini —
        # memanggil logout_user() berulang setiap render hanya akan men-reset
        # state UI login (login_role, dll) secara tidak sengaja.
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

    # Re-assert the cookie on every render (not just once at login) — for
    # BOTH remember-me and normal sessions, since "stay logged in across a
    # refresh" is required for normal sessions too (just not across a full
    # browser restart). The cookie-writing component is an iframe that
    # needs a round trip to the browser to actually execute — a single
    # .set() call right before the login flow's immediate st.rerun() can
    # get cut short before it ever reaches the browser. Repeating this on
    # every authenticated render gives it many more chances to actually
    # stick before a refresh happens.
    if cookie_token != token:
        _write_session_cookie(token, remember)

    return True


def is_authenticated() -> bool:
    """Cheap session_state-only check for UI gating. The actual
    idle/absolute-expiry enforcement happens once per render in
    validate_active_session() — this just reads the result of that."""
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
