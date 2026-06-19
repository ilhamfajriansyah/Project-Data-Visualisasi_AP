"""Client-side idle/expiry watchdog for the dashboard.

This complements (never replaces) the server-side checks in
login.access_control.validate_active_session(). The backend is the
authority on whether a session is actually still valid; this module only
provides the UX layer: a live countdown and a warning modal so the user
isn't silently logged out, plus a couple of triggers that route back to
the existing `?ap_logout=1` / `?ap_keepalive=1` query-param handlers in
dashboard/app.py.

Streamlit has no first-class way to push events from the browser to
Python outside of widget interactions, so:
  - Real-time idle/mouse/keyboard/scroll tracking and the visible
    countdown are pure client-side JS (no Python round trip needed for
    the ticking itself).
  - Detected activity is synced back to the *server* record at most once
    every SERVER_SYNC_MIN_INTERVAL_SECONDS, via a full navigation to
    `?ap_keepalive=1` (the same mechanism the existing logout link
    already uses for `?ap_logout=1`). This keeps the authoritative
    server-side idle timer reasonably in sync without reloading the page
    on every mouse wiggle.
  - The "Stay Logged In" button always syncs immediately (a single
    deliberate click, not a background loop).
  - localStorage (not a plain JS variable) backs the idle clock so
    activity in any tab of this app resets every other open tab's timer
    too — this is what keeps multiple tabs from showing independent,
    out-of-sync "you're about to be logged out" modals.
"""

import streamlit.components.v1 as components


def inject_session_watchdog(
    idle_elapsed_seconds: float,
    idle_timeout_seconds: float,
    warning_lead_seconds: float,
) -> None:
    components.html(
        f"""
        <script>
        (function () {{
            const doc = window.parent.document;

            const IDLE_TIMEOUT_MS = {idle_timeout_seconds * 1000};
            const WARNING_LEAD_MS = {warning_lead_seconds * 1000};
            const SERVER_SYNC_MIN_INTERVAL_MS = 5 * 60 * 1000;
            const STORAGE_KEY = 'ap_last_activity_ms';

            // Seed the idle clock from the *server's* notion of last
            // activity, so a brand-new tab (or one that just restored a
            // session from a remember-me cookie) doesn't start as if the
            // user had just been active right now.
            const serverIdleMs = {idle_elapsed_seconds * 1000};
            const serverBaseline = Date.now() - serverIdleMs;

            function getLastActivity() {{
                const stored = parseInt(localStorage.getItem(STORAGE_KEY) || '0', 10);
                return Math.max(stored, serverBaseline);
            }}
            function setLastActivity(ts) {{
                localStorage.setItem(STORAGE_KEY, String(ts));
            }}
            if (!localStorage.getItem(STORAGE_KEY)) {{
                setLastActivity(serverBaseline);
            }}

            let lastServerSync = Date.now();
            function syncServer(force) {{
                const now = Date.now();
                if (!force && (now - lastServerSync) < SERVER_SYNC_MIN_INTERVAL_MS) {{
                    return;
                }}
                lastServerSync = now;
                window.parent.location.search = '?ap_keepalive=1';
            }}

            function onActivity() {{
                setLastActivity(Date.now());
                hideModal();
                syncServer(false);
            }}
            ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart', 'wheel'].forEach(function (evt) {{
                doc.addEventListener(evt, onActivity, {{ passive: true }});
            }});

            function injectStyle() {{
                if (doc.getElementById('ap-session-modal-style')) return;
                const style = doc.createElement('style');
                style.id = 'ap-session-modal-style';
                style.textContent = `
                    .ap-session-modal-overlay {{
                        position: fixed; inset: 0; z-index: 100000;
                        background: rgba(15, 23, 42, 0.45);
                        display: flex; align-items: center; justify-content: center;
                        font-family: 'Poppins', sans-serif;
                    }}
                    .ap-session-modal-card {{
                        width: 360px; max-width: calc(100vw - 32px);
                        background: #ffffff; border-radius: 16px;
                        padding: 26px 26px 22px;
                        box-shadow: 0 24px 60px rgba(15, 23, 42, 0.25);
                        text-align: center;
                    }}
                    .ap-session-modal-icon {{
                        width: 44px; height: 44px; margin: 0 auto 14px;
                        border-radius: 50%; background: #FEF3C7; color: #D97706;
                        display: flex; align-items: center; justify-content: center;
                        font-size: 20px; font-weight: 800;
                    }}
                    .ap-session-modal-title {{
                        font-size: 17px; font-weight: 800; color: #0F172A; margin-bottom: 8px;
                    }}
                    .ap-session-modal-message {{
                        font-size: 13.5px; color: #475569; line-height: 1.55; margin: 0 0 20px;
                    }}
                    .ap-session-modal-countdown {{
                        font-weight: 800; color: #DC2626;
                    }}
                    .ap-session-modal-actions {{
                        display: flex; gap: 10px;
                    }}
                    .ap-session-modal-btn {{
                        flex: 1; height: 40px; border-radius: 10px; border: none;
                        font-size: 13px; font-weight: 700; cursor: pointer;
                        font-family: 'Poppins', sans-serif;
                    }}
                    .ap-session-modal-btn-primary {{
                        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
                        color: #ffffff;
                    }}
                    .ap-session-modal-btn-ghost {{
                        background: #F1F5F9; color: #334155;
                    }}
                `;
                doc.head.appendChild(style);
            }}

            function ensureModal() {{
                let modal = doc.getElementById('ap-session-modal');
                if (modal) return modal;

                injectStyle();
                modal = doc.createElement('div');
                modal.id = 'ap-session-modal';
                modal.style.display = 'none';
                modal.innerHTML = `
                    <div class="ap-session-modal-overlay">
                        <div class="ap-session-modal-card" role="alertdialog" aria-modal="true" aria-labelledby="ap-session-modal-title">
                            <div class="ap-session-modal-icon" aria-hidden="true">!</div>
                            <div id="ap-session-modal-title" class="ap-session-modal-title">Session Expiring</div>
                            <p class="ap-session-modal-message">
                                Your session will expire in
                                <span id="ap-session-modal-countdown" class="ap-session-modal-countdown">5:00</span>
                                due to inactivity.
                            </p>
                            <div class="ap-session-modal-actions">
                                <button type="button" id="ap-session-modal-logout" class="ap-session-modal-btn ap-session-modal-btn-ghost">Logout</button>
                                <button type="button" id="ap-session-modal-stay" class="ap-session-modal-btn ap-session-modal-btn-primary">Stay Logged In</button>
                            </div>
                        </div>
                    </div>
                `;
                doc.body.appendChild(modal);

                doc.getElementById('ap-session-modal-stay').addEventListener('click', function () {{
                    setLastActivity(Date.now());
                    hideModal();
                    syncServer(true);
                }});
                doc.getElementById('ap-session-modal-logout').addEventListener('click', function () {{
                    window.parent.location.search = '?ap_logout=1';
                }});

                return modal;
            }}

            function showModal() {{
                ensureModal().style.display = 'block';
            }}
            function hideModal() {{
                const modal = doc.getElementById('ap-session-modal');
                if (modal) modal.style.display = 'none';
            }}
            function formatCountdown(ms) {{
                const totalSeconds = Math.max(0, Math.ceil(ms / 1000));
                const m = Math.floor(totalSeconds / 60);
                const s = totalSeconds % 60;
                return m + ':' + (s < 10 ? '0' : '') + s;
            }}

            function tick() {{
                const now = Date.now();
                const idleMs = now - getLastActivity();
                const remainingMs = IDLE_TIMEOUT_MS - idleMs;

                if (remainingMs <= 0) {{
                    window.parent.location.search = '?ap_logout=1';
                    return;
                }}

                if (idleMs >= IDLE_TIMEOUT_MS - WARNING_LEAD_MS) {{
                    showModal();
                    const el = doc.getElementById('ap-session-modal-countdown');
                    if (el) el.textContent = formatCountdown(remainingMs);
                }} else {{
                    hideModal();
                }}
            }}

            // Re-running this script on every Streamlit rerun would stack a
            // new interval each time without this guard.
            if (window.parent.__apSessionWatchdogInterval) {{
                clearInterval(window.parent.__apSessionWatchdogInterval);
            }}
            window.parent.__apSessionWatchdogInterval = setInterval(tick, 1000);
            tick();
        }})();
        </script>
        """,
        height=0,
    )
