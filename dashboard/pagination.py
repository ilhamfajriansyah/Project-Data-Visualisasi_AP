import streamlit as st
import streamlit.components.v1 as components

# ‹ dan › (U+2039/U+203A) — visual identik dengan < dan >
# AMAN di Markdown Streamlit: ">" saja = blockquote = label invisible
_PREV = "‹"
_NEXT = "›"


def _state_key_from_sync_key(sync_key):
    return sync_key[:-5] if sync_key.endswith("_sync") else sync_key


def _set_page(state_key, page):
    st.session_state[state_key] = page


# CSS murni — tanpa JavaScript sama sekali.
# Scoped via .overview-detail-pagination-footer-marker agar tidak mengganggu
# button lain di halaman yang sama.
_CSS = """<style>
.ed-pg-info {
    font-size: 12.5px;
    color: #6b7280;
    line-height: 38px;
    white-space: nowrap;
}

/* ── Base pill — semua tombol pagination ── */
body:has(.overview-detail-pagination-footer-marker)
div[data-testid="stElementContainer"]:has(.overview-detail-pagination-footer-marker)
~ div[data-testid="stHorizontalBlock"]
div[data-testid="stButton"] button {
    min-width: 38px !important;
    width:      38px !important;
    height:     38px !important;
    padding:    0    !important;
    border-radius: 999px               !important;
    border:        1.5px solid #d1d5db !important;
    background:    #ffffff             !important;
    color:         #374151             !important;
    font-size:     14px                !important;
    font-weight:   600                 !important;
    box-shadow:    none                !important;
    transition: background 0.15s, border-color 0.15s !important;
}

body:has(.overview-detail-pagination-footer-marker)
div[data-testid="stElementContainer"]:has(.overview-detail-pagination-footer-marker)
~ div[data-testid="stHorizontalBlock"]
div[data-testid="stButton"] button:hover:not(:disabled) {
    background:   #f3f4f6 !important;
    border-color: #9ca3af !important;
}

body:has(.overview-detail-pagination-footer-marker)
div[data-testid="stElementContainer"]:has(.overview-detail-pagination-footer-marker)
~ div[data-testid="stHorizontalBlock"]
div[data-testid="stButton"] button:disabled {
    opacity: 0.35        !important;
    cursor:  not-allowed !important;
}

/* ── Halaman aktif — biru ── */
body:has(.overview-detail-pagination-footer-marker)
div[data-testid="stElementContainer"]:has(.overview-detail-pagination-footer-marker)
~ div[data-testid="stHorizontalBlock"]
[data-testid="baseButton-primary"],
body:has(.overview-detail-pagination-footer-marker)
div[data-testid="stElementContainer"]:has(.overview-detail-pagination-footer-marker)
~ div[data-testid="stHorizontalBlock"]
[data-testid="stBaseButton-primary"],
body:has(.overview-detail-pagination-footer-marker)
div[data-testid="stElementContainer"]:has(.overview-detail-pagination-footer-marker)
~ div[data-testid="stHorizontalBlock"]
button[kind="primary"] {
    background:   #1d4ed8 !important;
    border-color: #1d4ed8 !important;
    color:        #ffffff  !important;
    font-weight:  700      !important;
    opacity:      1        !important;
    cursor:       default  !important;
    box-shadow: 0 2px 8px rgba(29, 78, 216, 0.35) !important;
}
</style>"""


def render_pagination(current_page, total_pages, first_item, last_item, total_rows, sync_key):
    """
    Render pagination bar: info text (kiri) + pill buttons (kanan).
    Murni CSS — tanpa JavaScript. Pastikan marker
    .overview-detail-pagination-footer-marker dirender tepat sebelum
    memanggil fungsi ini, dan pagination berada DI LUAR container yang
    punya CSS override button (seperti blok ed-card-marker di DV).
    """
    state_key = _state_key_from_sync_key(sync_key)
    current_page = max(1, min(int(current_page), int(total_pages or 1)))
    total_pages  = max(1, int(total_pages or 1))

    # Inject CSS setiap render agar selalu muncul SETELAH page-specific CSS
    st.markdown(_CSS, unsafe_allow_html=True)

    # Hitung halaman yang ditampilkan (maks 5)
    max_visible = 5
    start_p = max(1, current_page - max_visible // 2)
    end_p   = min(total_pages, start_p + max_visible - 1)
    start_p = max(1, end_p - max_visible + 1)
    visible_pages = list(range(start_p, end_p + 1))

    # Layout: [info_text | spacer besar | ‹ | page... | ›]
    n_page = len(visible_pages)
    widths = [12, 35] + [3] * (2 + n_page)
    cols   = st.columns(widths, gap="small")

    # Info text (kiri)
    with cols[0]:
        st.markdown(
            f'<div class="ed-pg-info">Showing {first_item}–{last_item} of {total_rows}</div>',
            unsafe_allow_html=True,
        )

    # ‹ (prev)
    with cols[2]:
        st.button(
            _PREV, key=f"{sync_key}_prev",
            disabled=current_page <= 1,
            on_click=_set_page, args=(state_key, current_page - 1),
        )

    # Angka halaman
    for i, p in enumerate(visible_pages, start=3):
        with cols[i]:
            is_active = p == current_page
            st.button(
                str(p), key=f"{sync_key}_page_{p}",
                type="primary" if is_active else "secondary",
                disabled=is_active,
                on_click=_set_page, args=(state_key, p),
            )

    # › (next)
    with cols[-1]:
        st.button(
            _NEXT, key=f"{sync_key}_next",
            disabled=current_page >= total_pages,
            on_click=_set_page, args=(state_key, current_page + 1),
        )

    return str(st.session_state.get(state_key, current_page))


def patch_pagination():
    """Kept for compatibility with existing callers."""
    components.html("", height=0, width=0)
