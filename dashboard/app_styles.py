"""CSS constants for app.py, relocated out of that file to keep it focused on
logic/routing. Content is unchanged from before — this is a pure code-
organization split, not a styling change."""

from textwrap import dedent

_APP_MAIN_CSS = """
    <style>
    /* Hide the invisible iframes used by the session watchdog / cookie
       manager components (session persistence + idle-timeout tracking) —
       without this they leave a thin blank gap that pushes page content
       down, since they're still a normal (non-collapsed) flex item even
       though there's nothing visible inside. */
    div[data-testid="stElementContainer"]:has(iframe[height="0"]) {
        display: none !important;
    }
    .ap-top-actions {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 8px; /* reduced gap */
        padding-top: 0;
        position: relative;
        overflow: visible;
    }
    .ap-top-bell {
        width: 34px;
        height: 34px;
        margin-top: 7px;
        border-radius: 50%;
        background: rgba(255,255,255,0.78);
        border: 1px solid rgba(255,255,255,0.96);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 16px;
        box-shadow: 0 2px 8px rgba(99,102,241,0.08);
    }
    .ap-profile-details {
        position: relative;
        overflow: visible;
    }
    .ap-profile-details > summary {
        list-style: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        user-select: none;
        outline: none;
    }
    .ap-profile-details > summary::-webkit-details-marker {
        display: none;
    }
    .ap-profile-avatar {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: #d6d6d6;
        border: 1px solid rgba(203,213,225,0.95);
        box-shadow: 0 4px 14px rgba(15,23,42,0.08);
        flex: 0 0 auto;
        display: block;
        overflow: hidden;
        position: relative;
    }
    .ap-profile-avatar::before {
        content: "";
        position: absolute;
        left: 50%;
        top: 9px;
        width: 19px;
        height: 19px;
        border-radius: 50%;
        background: #ffffff;
        transform: translateX(-50%);
    }
    .ap-profile-avatar::after {
        content: "";
        position: absolute;
        left: 50%;
        top: 29px;
        width: 35px;
        height: 25px;
        border-radius: 50% 50% 42% 42% / 62% 62% 38% 38%;
        background: #ffffff;
        transform: translateX(-50%);
    }
    .ap-profile-menu {
        position: absolute;
        right: 0;
        top: 48px;
        z-index: 9999;
        width: 132px;
        padding: 4px 0;
        border-radius: 10px;
        background: linear-gradient(135deg, rgba(244,114,182,0.10), rgba(255,255,255,0.32));
        backdrop-filter: blur(18px);
        -webkit-backdrop-filter: blur(18px);
        border: 1px solid rgba(255,255,255,0.35);
        box-shadow: 0 8px 18px rgba(15,23,42,0.10);
        overflow: hidden;
    }
    .ap-profile-menu-item {
        height: 32px;
        padding: 0 12px;
        color: #334155 !important;
        text-decoration: none !important;
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        font-weight: 600;
        white-space: nowrap;
        background: transparent;
        transition: background 0.15s ease;
    }
    .ap-profile-menu-item:hover {
        background: rgba(99,102,241,0.08);
        color: #4f46e5 !important;
    }
    .ap-profile-menu-item.is-danger {
        color: #DC2626 !important;
    }
    .ap-profile-menu-item.is-danger:hover {
        background: linear-gradient(135deg, rgba(244,63,94,0.10), rgba(168,85,247,0.10));
        color: #DC2626 !important;
    }
    .ap-profile-menu-icon {
        width: 14px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        color: inherit;
        text-align: center;
        font-size: 13px;
    }
    #MainMenu,
    footer,
    header,
    [data-testid="stHeader"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebarHeader"],
    [data-testid="collapsedControl"] {
        display: none !important;
        height: 0 !important;
        visibility: hidden !important;
    }
    .block-container {
        padding-top: 0rem !important;
        margin-top: 0 !important;
    }
    [data-testid="stSidebarContent"] {
        padding: 0 !important;
    }
    [data-testid="stSidebarContent"] > div,
    [data-testid="stSidebarContent"] > div:first-child,
    [data-testid="stSidebarContent"] [data-testid="stVerticalBlock"],
    [data-testid="stSidebarContent"] [data-testid="stVerticalBlock"] > div:first-child {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    [data-testid="stSidebar"] .element-container:first-child {
        margin-top: 0 !important;
    }
    .ap-brand {
        margin-top: 20px !important;
        padding: 10px 14px 16px !important;
        margin-bottom: 35px !important;
    }
    .ap-brand-mini {
        margin-top: 20px !important;
        padding: 10px 0 12px !important;
        margin-bottom: 35px !important;
    }
    .ap-logo {
        width: 34px !important;
        height: 34px !important;
        border-radius: 11px !important;
    }
    .ap-brand-name {
        font-size: 10.2px !important;
        line-height: 1.2 !important;
    }
    .ap-brand-sub {
        font-size: 8.6px !important;
        margin-top: 2px !important;
    }
    .nad-top-divider {
        margin: 6px 0 12px !important;
    }
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .overview-main-card-marker) {
        position: relative;
        height: auto;
        min-height: 0;
        overflow: visible;
        padding: 22px 24px 24px;
        margin-bottom: 18px;
        border-radius: 28px;
        background:
            radial-gradient(circle at 10% 0%, rgba(139, 92, 246, 0.09), transparent 34%),
            radial-gradient(circle at 92% 100%, rgba(6, 182, 212, 0.08), transparent 38%),
            rgba(255, 255, 255, 0.66);
        backdrop-filter: blur(30px);
        -webkit-backdrop-filter: blur(30px);
        border: 1px solid rgba(255, 255, 255, 0.96);
        box-shadow:
            0 18px 50px rgba(76, 81, 191, 0.10),
            0 4px 14px rgba(15, 23, 42, 0.035),
            inset 0 1px 0 rgba(255, 255, 255, 1);
    }
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .overview-main-card-marker)
    > div[data-testid="stElementContainer"]:has(.overview-main-card-marker) {
        display: none;
    }
    button[kind="secondary"][data-testid="baseButton-secondary"] {
        border: none !important;
    }

    div[data-testid="stButton"] > button {
        background: transparent !important;
        color: #6366f1 !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        min-height: 18px !important;
        height: 18px !important;
        line-height: 18px !important;
        font-size: 10.5px !important;
        font-weight: 700 !important;
        text-align: right !important;
    }
    div[data-testid="stButton"] > button p {
        font-size: 10.5px !important;
        margin: 0 !important;
        line-height: 18px !important;
        white-space: nowrap !important;
    }
    div[data-testid="stButton"] {
        display: flex !important;
        justify-content: flex-end !important;
        align-items: center !important;
    }
    div[data-testid="stButton"] > button:hover {
        color: #4f46e5 !important;
        background: transparent !important;
    }
    
    .overview-main-card-marker {
        display: none;
    }
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .overview-section-card-strip) {
        position: relative;
        height: auto;
        min-height: 0;
        overflow: visible;
        background: rgba(255, 255, 255, 0.56);
        backdrop-filter: blur(26px);
        -webkit-backdrop-filter: blur(26px);
        border-radius: 20px;
        padding: 16px 20px 20px;
        border: 1px solid rgba(255, 255, 255, 0.90);
        box-shadow:
            0 8px 32px rgba(99, 102, 241, 0.07),
            0 2px 8px rgba(0, 0, 0, 0.025),
            inset 0 1px 0 rgba(255, 255, 255, 1),
            inset 0 -1px 0 rgba(99, 102, 241, 0.025);
        margin-bottom: 14px;
        transition: box-shadow 0.2s, transform 0.2s;
    }
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .overview-section-card-strip):hover {
        box-shadow:
            0 14px 42px rgba(99, 102, 241, 0.11),
            0 2px 8px rgba(0, 0, 0, 0.03),
            inset 0 1px 0 rgba(255, 255, 255, 1);
        transform: translateY(-1px);
    }
    .overview-section-card-strip {
        position: relative;
        height: 5px;
        margin: -2px 0 14px;
        border-radius: 999px;
        background: linear-gradient(90deg, rgba(99,102,241,0.00), rgba(99,102,241,0.50), rgba(6,182,212,0.58), rgba(16,185,129,0.52), rgba(16,185,129,0.00));
        box-shadow: 0 8px 24px rgba(6, 182, 212, 0.12);
    }
    .overview-section-card-strip::after {
        content: "";
        position: absolute;
        left: 8%;
        right: 8%;
        top: 1px;
        height: 1px;
        border-radius: inherit;
        background: rgba(255, 255, 255, 0.72);
    }
    .overview-card-action {
        font-size: 11px;
        color: #6366f1;
        text-align: right;
        margin: 2px 0;
        font-weight: 600;
        cursor: pointer;
    }
    .overview-card-action.is-detail {
        margin-top: 4px;
    }
    
    .overview-light-table-wrap {
    width: 100%;
    overflow: hidden;
    border-radius: 16px;
    border: 1px solid rgba(226, 232, 240, 0.9);
    background: rgba(255, 255, 255, 0.68);
    box-shadow:
        0 8px 24px rgba(99, 102, 241, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.95);
    }

    .overview-light-table-wrap.is-summary {
        min-height: 265px;
    }

    .overview-light-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        color: #1e293b;
        font-family: 'Inter', sans-serif !important;
    }

    .overview-light-table thead {
        background: rgba(99, 102, 241, 0.06);
    }

    .overview-light-table th {
        padding: 12px 16px;
        text-align: left;
        font-size: 11px;
        font-weight: 700;
        color: #4F46E5;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        border-bottom: none;
    }

    .overview-light-table td {
        padding: 12px 14px;
        font-size: 12.5px;
        font-weight: 600;
        color: #0f172a;
        border-bottom: 1px solid rgba(226, 232, 240, 0.72);
    }

    .overview-light-table tbody tr:last-child td {
        border-bottom: none;
    }

    .overview-light-table tbody tr:hover {
        background: rgba(99, 102, 241, 0.045);
    }
                
    h2[style*="padding-top:6px"],
    .lc-header-title,
    .page-header,
    .im-manager-surface {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }
    .ap-top-actions {
        align-items: center;
        gap: 8px; /* reduced gap */
        padding-top: 0;
        min-height: 38px;
    }
    .ap-top-bell {
        margin-top: 0;
    }
    @media (max-width: 900px) {
        .block-container {
            padding-top: 2px !important;
        }
        .ap-brand {
            padding-top: 5px !important;
        }
    }

    /* Enterprise dashboard redesign */
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"] {
        background: #F8FAFC !important;
    }

    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .main,
    section.main {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    .block-container {
        max-width: 100% !important;
        padding: 0 28px 34px !important;
        margin-top: 0 !important;
    }

    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewContainer"] .block-container,
    section.main > div,
    .main > div {
        padding-top: 0 !important;
        padding-bottom: 34px !important;
        margin-top: 0 !important;
    }

    .dashboard-container,
    .page-container,
    .content-wrapper,
    .main-content,
    .overview-container {
        margin-top: 0 !important;
        padding-top: 0 !important;
    }

    [data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #E5E7EB !important;
        box-shadow: none !important;
        min-width: 258px !important;
        width: 258px !important;
        max-width: 258px !important;
    }

    [data-testid="stSidebarContent"] {
        background: #ffffff !important;
        padding-top: 24px !important;
    }

    [data-testid="stSidebarUserContent"],
    [data-testid="stSidebarContent"] > div,
    [data-testid="stSidebarContent"] [data-testid="stVerticalBlock"] {
        padding-top: 0 !important;
        margin-top: 0 !important;
    }

    /* Pin only the footer to the bottom of the sidebar — position:absolute
       takes it completely out of normal flow, so it cannot affect (or be
       affected by) the layout of the brand/nav items above it. */
    [data-testid="stSidebar"] {
        position: relative !important;
    }
    [data-testid="stSidebarContent"] div[data-testid="stElementContainer"]:has(.ap-sidebar-footer) {
        position: absolute !important;
        left: 0 !important;
        right: 0 !important;
        bottom: 18px !important;
        margin: 0 !important;
    }
    .ap-brand {
        margin: 0 !important;
        padding: 16px 24px 16px !important;
        display: flex !important;
        align-items: center !important;
        border-bottom: 1px solid #E5E7EB !important;
    }

    .ap-logo {
        width: 36px !important;
        height: 36px !important;
        border-radius: 10px !important;
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%) !important;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }

    .ap-brand-name {
        color: #0F172A !important;
        font-size: 18px !important;
        font-weight: 800 !important;
        letter-spacing: -0.2px !important;
        font-family: 'Montserrat', sans-serif !important;
        white-space: nowrap !important;
        line-height: 1 !important;
    }

    .ap-brand-copy {
        min-width: 0 !important;
        flex: 1 1 auto !important;
    }

    .ap-brand-sub {
        color: #6366F1 !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        letter-spacing: 0px !important;
        line-height: 1 !important;
        margin-top: 4px !important;
        font-family: 'Inter', sans-serif !important;
    }

    .ap-toolbar-title {
        padding: 22px 24px 8px !important;
        color: #94A3B8 !important;
        font-size: 10px !important;
        letter-spacing: 1.2px !important;
    }

    .nav-category-header {
        font-size: 10px !important;
        font-weight: 800 !important;
        color: #94A3B8 !important;
        letter-spacing: 1.2px !important;
        text-transform: uppercase !important;
        margin: 20px 24px 28px !important;
        font-family: 'Montserrat', sans-serif !important;
    }

    .nav-group {
        display: none !important;
    }

    .nav-row,
    .nav-active {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0 14px 2px !important;
        padding: 5px 12px;
        border-radius: 10px;
        color: #64748B;
        font-size: 13px;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
        line-height: 1.2;
        box-sizing: border-box !important;
        width: calc(100% - 28px) !important;
        max-width: calc(100% - 28px) !important;
        height: 36px !important;
        position: relative;
    }

    .nav-icon-box {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 28px;
        height: 28px;
        border-radius: 7px;
        flex-shrink: 0;
        box-sizing: border-box !important;
        transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease !important;
    }

    .nav-icon-box svg {
        width: 16px;
        height: 16px;
        display: block;
    }

    .nav-label {
        flex-shrink: 0;
        overflow: visible;
        white-space: nowrap;
        letter-spacing: -0.15px;
        color: inherit;
        font-family: 'Inter', sans-serif !important;
    }

    .nav-overlay {
        pointer-events: none;
        position: relative;
        z-index: 1;
        background: transparent !important;
        border: 1px solid transparent !important;
    }

    .nav-active {
        margin: 0 14px 2px !important;
        padding: 5px 14px 5px 10px !important;
        border-radius: 12px !important;
        background: #F5F3FF !important;
        border: 1px solid #DDD6FE !important;
        box-shadow: none !important;
        color: #7C3AED !important;
        font-weight: 700 !important;
        height: 36px !important;
        width: calc(100% - 28px) !important;
        max-width: calc(100% - 28px) !important;
    }

    .nav-active .nav-icon-box {
        background-color: #EDE9FE !important;
        color: #7C3AED !important;
    }

    .nav-row .nav-icon-box {
        background-color: #F8FAFC !important;
        color: #64748B !important;
        border: 1px solid #F1F5F9 !important;
    }

    .nav-indicator-pill {
        position: absolute;
        left: 0;
        top: 5px;
        bottom: 5px;
        width: 3.5px;
        background: linear-gradient(180deg, #A78BFA 0%, #7C3AED 100%);
        border-radius: 0 4px 4px 0;
    }

    .nav-badge {
        margin-left: auto;
        background: linear-gradient(135deg, #06B6D4 0%, #3B82F6 100%);
        color: #ffffff;
        font-size: 10.5px;
        font-weight: 700;
        padding: 2.5px 8.5px;
        border-radius: 20px;
        box-shadow: 0 2.5px 7px rgba(6, 182, 212, 0.25);
    }

    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(.nav-overlay) {
        padding-left: 0 !important;
        padding-right: 0 !important;
        margin-left: 0 !important;
        margin-right: 0 !important;
    }

    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(.nav-overlay) [data-testid="stMarkdownContainer"],
    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(.nav-overlay) [data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        padding: 0 !important;
    }

    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(div[data-testid="stButton"]) {
        margin-bottom: -36px !important;
        position: relative;
        z-index: 2;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] {
        margin: 0 14px 2px !important;
        padding: 0 !important;
        height: 36px !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] > button {
        height: 36px !important;
        min-height: 36px !important;
        opacity: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        cursor: pointer !important;
        transition: none !important;
        width: 100% !important;
    }

    /* Hover effects */
    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(div[data-testid="stButton"]):hover + div[data-testid="stElementContainer"] .nav-row.nav-overlay {
        background: rgba(241, 245, 249, 0.5) !important;
        color: #1E293B !important;
        border-radius: 12px !important;
    }

    [data-testid="stSidebar"] div[data-testid="stElementContainer"]:has(div[data-testid="stButton"]):hover + div[data-testid="stElementContainer"] .nav-row.nav-overlay .nav-icon-box {
        background-color: #E2E8F0 !important;
        color: #1E293B !important;
    }

    .ap-sidebar-footer {
        margin: 0 16px 18px !important;
        padding: 0 !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        text-align: center !important;
        font-size: 11px !important;
        font-weight: 500 !important;
        color: #94A3B8 !important;
        font-family: 'Inter', sans-serif !important;
        letter-spacing: 0.2px !important;
        line-height: 1.5 !important;
        white-space: normal !important;
    }

    .ap-sidebar-spacer {
        height: 20px !important;
        min-height: 20px !important;
    }

    .ap-sidebar-status {
        display: flex;
        align-items: center;
        gap: 8px;
        color: #475569;
        font-size: 11px;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
    }

    .ap-status-dot {
        width: 8px;
        height: 8px;
        border-radius: 999px;
        background: #10B981;
        flex: 0 0 8px;
        box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.18);
    }

    .ap-sidebar-sync {
        margin-top: 6px;
        color: #94A3B8;
        font-size: 10px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
    }

    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        min-height: 100% !important;
        gap: 0px !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] {
        padding: 0 16px !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] > button {
        height: 36px !important;
        min-height: 36px !important;
        padding: 0 14px !important;
        border-radius: 12px !important;
        color: #475569 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        background: transparent !important;
        justify-content: flex-start !important;
        text-align: left !important;
        box-shadow: none !important;
    }

    [data-testid="stSidebar"] div[data-testid="stButton"] > button:hover {
        background: transparent !important;
        background-color: transparent !important;
        color: transparent !important;
        opacity: 0 !important;
        box-shadow: none !important;
        border: none !important;
    }

    .nad-top-divider {
        height: 1px !important;
        margin: 8px 0 14px !important;
        background: #E5E7EB !important;
        box-shadow: none !important;
    }

    .nad-top-divider::after {
        display: none !important;
    }

    .ap-top-actions {
        align-items: center !important;
        gap: 14px !important;
        min-height: 44px !important;
    }

    .ap-top-bell {
        width: 38px !important;
        height: 38px !important;
        margin: 0 !important;
        border-radius: 999px !important;
        background: #ffffff !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: none !important;
        color: #334155 !important;
    }

    .ap-profile-avatar {
        width: 42px !important;
        height: 42px !important;
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
        border: none !important;
        box-shadow: 0 3px 10px rgba(99, 102, 241, 0.30) !important;
    }

    .ap-user-meta {
        text-align: left;
        color: #0F172A;
        font-size: 12px;
        font-weight: 800;
        line-height: 1.2;
    }

    .ap-user-meta span {
        display: block;
    }

    .ap-profile-details > summary {
        gap: 10px !important;
    }

    .ap-user-role {
        margin-top: 2px;
        color: #64748B;
        font-size: 11px;
        font-weight: 600;
    }

    .overview-shell {
        width: 100%;
    }

    .overview-filter-label {
        margin: 0 0 6px 2px;
        color: #64748B;
        font-size: 11px;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
    }

    .overview-filter-spacer {
        height: 2px;
    }

    .overview-page-marker {
        display: none;
    }

    /* The marker's own wrapper still occupies a flex slot in Streamlit's
       vertical block (contributing a default "gap" before the next element)
       even though its content is display:none. Remove the wrapper itself
       from flow so it doesn't add unwanted spacing. */
    div[data-testid="stElementContainer"]:has(.overview-page-marker) {
        display: none !important;
    }

    /* ── Overview header — identical mechanism to Traffic Monitor's header:
       position:fixed (pinned to the viewport, immune to normal-flow gaps),
       sized to land its bottom border on the sidebar's divider line:
       stSidebarContent padding-top (24px) + .ap-brand box
       (13px + 42px logo + 13px padding + 1px border) = 93px. */
    body:has(.overview-page-marker) .ov-fixed-header-active {
        position: fixed !important;
        top: 0 !important;
        right: 0 !important;
        z-index: 200 !important;
        background: #F8FAFC !important;
        border-bottom: 1px solid #E5E7EB !important;
        box-shadow: 0 4px 20px rgba(15, 23, 42, 0.08) !important;
        height: 93px !important;
        min-height: 93px !important;
        max-height: 93px !important;
        padding: 0 28px !important;
        margin: 0 !important;
        width: auto !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
        overflow: visible !important;
    }
    body:has(.overview-page-marker) .ov-fixed-header-spacer {
        display: block !important;
        height: 93px !important;
        min-height: 93px !important;
        max-height: 93px !important;
        margin: 0 !important;
        padding: 0 !important;
        width: 100%;
        flex-shrink: 0;
    }
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-fixed-header-spacer) {
        margin: 0 !important;
        padding: 0 !important;
        height: 93px !important;
        min-height: 93px !important;
        max-height: 93px !important;
    }
    /* Collapse the invisible JS-mount component (iframe) so it doesn't add
       its own default element spacing between the spacer and the filters. */
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(> iframe) {
        margin: 0 !important;
        padding: 0 !important;
        height: 0 !important;
        min-height: 0 !important;
    }
    /* Pull the filter card up to close the remaining default Streamlit gap
       after the (mandatory, fixed-height) spacer — keeps it compact/close
       to the header without overlapping the fixed header itself. */
    body:has(.overview-page-marker) div[data-testid="stHorizontalBlock"]:has(.ov-filtercard-marker) {
        margin-top: -24px !important;
    }
    body:has(.overview-page-marker) div[data-testid="stHorizontalBlock"]:has(.overview-kpi-card) {
        margin-top: 0 !important;
    }
    body:has(.overview-page-marker) .ov-sticky-header-marker,
    body:has(.overview-page-marker) .ov-sticky-header-end {
        display: none;
    }
    body:has(.overview-page-marker) [data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ov-sticky-header-marker) {
        gap: 0 !important;
        height: 100% !important;
        justify-content: center !important;
    }
    body:has(.overview-page-marker) [data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ov-sticky-header-marker) > div[data-testid="stElementContainer"] {
        margin: 0 !important;
        padding: 0 !important;
    }
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-sticky-header-marker) {
        height: 100% !important;
        display: flex !important;
        align-items: center !important;
    }
    body:has(.overview-page-marker) .ov-page-header {
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        width: 100%;
        gap: 16px;
        height: 100%;
    }
    body:has(.overview-page-marker) .ov-page-header-left {
        display: flex; align-items: center; gap: 12px; min-width: 0;
    }
    body:has(.overview-page-marker) .ov-page-icon {
        width: 36px; height: 36px; flex: 0 0 36px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        background: linear-gradient(135deg, #4F46E5 0%, #3B82F6 100%);
        color: #ffffff; box-shadow: 0 4px 12px rgba(37, 99, 235, 0.18);
    }
    body:has(.overview-page-marker) .ov-page-icon svg {
        width: 18px; height: 18px;
    }
    body:has(.overview-page-marker) .ov-page-header-copy {
        display: flex; flex-direction: column; justify-content: center; gap: 4px !important;
        min-height: 36px; min-width: 0;
    }
    body:has(.overview-page-marker) .ov-page-title-row {
        display: flex; align-items: center; gap: 10px; min-height: 0 !important;
        margin: 0 !important; padding: 0 !important;
    }
    body:has(.overview-page-marker) h2.ov-page-title {
        margin: 0 !important; padding: 0 !important;
        font-size: 18px; line-height: 1 !important; font-weight: 800;
        color: #0F172A; font-family: 'Montserrat', sans-serif !important;
    }
    body:has(.overview-page-marker) p.ov-page-sub {
        margin: 0 !important; padding: 0 !important;
        color: #64748B; font-size: 12px; line-height: 1 !important;
        font-weight: 500; font-family: 'Inter', sans-serif !important;
    }
    /* Beda ukuran judul/sub-judul tiap card di halaman ini, mengikuti
       kontras yang dipakai pada header halaman (h2.ov-page-title vs
       p.ov-page-sub). */
    body:has(.overview-page-marker) .ed-section-title {
        font-size: 16px !important;
        font-weight: 800 !important;
    }
    body:has(.overview-page-marker) .ed-section-sub {
        font-size: 11px !important;
        font-weight: 500 !important;
    }
    body:has(.overview-page-marker) .ap-top-actions {
        flex-shrink: 0;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] > div > div {
        position: relative !important;
        display: flex !important;
        align-items: center !important;
        padding-right: 10px !important;
        min-height: 40px !important;
        overflow: visible !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] > div > div::after {
        content: none !important;
        display: none !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] div[data-baseweb="select"] {
        width: 100% !important;
        min-width: 0 !important;
        overflow: visible !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        gap: 8px !important;
        padding: 0 4px 0 10px !important;
        min-height: 38px !important;
        box-sizing: border-box !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
        display: flex !important;
        align-items: center !important;
        line-height: 1.25 !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div:first-child {
        flex: 1 1 auto !important;
        min-width: 0 !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"],
    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        display: flex !important;
        align-items: center !important;
        margin: 0 !important;
        line-height: 1.25 !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] svg {
        opacity: 1 !important;
        color: #64748B !important;
        fill: #64748B !important;
        width: 14px !important;
        height: 14px !important;
        flex: 0 0 14px !important;
        align-self: center !important;
        margin: 0 !important;
        position: static !important;
        transform: none !important;
    }

    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] div[data-baseweb="select"] span,
    body:has(.overview-page-marker) [data-testid="stMain"] [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        overflow: visible !important;
        text-overflow: clip !important;
        white-space: nowrap !important;
        max-width: none !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) {
        align-items: stretch !important;
        display: flex !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] {
        display: flex !important;
        flex-direction: column !important;
        align-self: stretch !important;
        margin: 0 !important;
        padding: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"] {
        width: 100% !important;
        flex: 1 1 auto !important;
        display: flex !important;
        flex-direction: column !important;
        margin: 0 !important;
        padding: 0 !important;
        min-height: 100% !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .overview-trend-card),
    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .overview-alert-card) {
        display: flex !important;
        flex-direction: column !important;
        flex: 1 1 auto !important;
        height: 100% !important;
        min-height: 100% !important;
        box-sizing: border-box !important;
        overflow: hidden !important;
        padding: 16px !important;
        margin: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) > div[data-testid="stElementContainer"] {
        margin-bottom: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker) > div[data-testid="stElementContainer"]:last-child {
        margin-bottom: 0 !important;
        padding-bottom: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(.overview-trend-card) > div[data-testid="stElementContainer"]:has([data-testid="stPlotlyChart"]) {
        flex: 1 1 auto !important;
        display: flex !important;
        flex-direction: column !important;
        min-height: 0 !important;
        overflow: hidden !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(.overview-trend-card) [data-testid="stPlotlyChart"] {
        flex: 1 1 auto !important;
        min-height: 0 !important;
        height: 100% !important;
        overflow: hidden !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(.overview-trend-card) [data-testid="stPlotlyChart"] > div,
    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(.overview-trend-card) [data-testid="stPlotlyChart"] .js-plotly-plot {
        height: 100% !important;
        min-height: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-trend-card):has(.overview-alert-card) > div[data-testid="column"] > div[data-testid="stVerticalBlock"]:has(.overview-alert-card) .ed-alert-list {
        flex: 1 1 auto !important;
        margin-bottom: 0 !important;
        min-height: 0 !important;
    }
    
    /* Ratakan selectbox rows ke tengah vertikal baris header detail */
    div[data-testid="stHorizontalBlock"]:has(.ed-table-card) 
    [data-testid="stSelectbox"] {
        margin-top: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.ed-table-card) 
    [data-testid="stSelectbox"] > label {
        display: none !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.ed-table-card) 
    [data-testid="stSelectbox"] > div {
        margin-top: 0 !important;
    }

    .overview-kpi-card {
        min-height: 118px;
        display: flex;
        align-items: center;
        gap: 16px;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        background: #ffffff;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }

    .overview-kpi-icon {
        width: 52px;
        height: 52px;
        flex: 0 0 52px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        font-size: 18px;
        font-weight: 800;
        font-family: 'Inter', sans-serif !important;
    }

    .overview-kpi-copy {
        min-width: 0;
    }

    .overview-kpi-label {
        color: #475569;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.3px;
        text-transform: uppercase;
        font-family: 'Inter', sans-serif !important;
    }

    .overview-kpi-value {
        margin-top: 7px;
        color: #0F172A;
        font-size: 26px;
        font-weight: 800;
        line-height: 1.05;
        letter-spacing: 0 !important;
        font-family: 'Inter', sans-serif !important;
    }

    .overview-kpi-delta {
        margin-top: 10px;
        color: #64748B;
        font-size: 11px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
    }

    .overview-kpi-delta strong {
        display: inline-flex;
        align-items: center;
        padding: 3px 8px;
        margin-right: 6px;
        border-radius: 999px;
        background: #DCFCE7;
        color: #059669;
        font-size: 11px;
    }

    .kpi-pro-card {
        display: flex;
        flex-direction: column;
        gap: 11px;
        min-height: 170px;
        padding: 18px 20px;
        border-radius: 14px;
        border: 1px solid #E2E8F0;
        background: #ffffff;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
        transition: all 0.3s ease;
    }

    .kpi-pro-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05), 0 4px 6px -2px rgba(0,0,0,0.025);
    }

    .kpi-pro-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .kpi-pro-icon {
        width: 40px;
        height: 40px;
        flex: 0 0 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 10px;
    }

    .kpi-pro-icon svg {
        width: 20px;
        height: 20px;
    }

    .kpi-pro-badge {
        display: inline-flex;
        align-items: center;
        gap: 3px;
        padding: 3px 9px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        background: #DCFCE7;
        color: #16A34A;
        white-space: nowrap;
    }

    .kpi-pro-badge.is-down {
        background: #FEE2E2;
        color: #DC2626;
    }

    .kpi-pro-body {
        min-width: 0;
    }

    .kpi-pro-label {
        color: #64748B;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.4px;
        text-transform: uppercase;
    }

    .kpi-pro-value-row {
        display: flex;
        align-items: baseline;
        gap: 6px;
        margin-top: 7px;
    }

    .kpi-pro-value {
        color: #0F172A;
        font-size: 25px;
        font-weight: 800;
        line-height: 1.1;
    }

    .kpi-pro-unit {
        color: #94A3B8;
        font-size: 12px;
        font-weight: 600;
    }

    .kpi-pro-sub {
        margin-top: 6px;
        color: #94A3B8;
        font-size: 11.5px;
        font-weight: 500;
    }

    .kpi-pro-foot {
        margin-top: auto;
    }

    .kpi-pro-bar-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        font-size: 11px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .kpi-pro-bar-row span:first-child {
        color: #94A3B8;
        font-weight: 500;
    }

    .kpi-pro-bar-track {
        height: 5px;
        border-radius: 999px;
        background: #F1F5F9;
        overflow: hidden;
    }

    .kpi-pro-bar-fill {
        height: 100%;
        border-radius: 999px;
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker):not(
        :has(div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] .ed-card-marker)
    ) {
        position: relative;
        overflow: hidden;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        background: #ffffff;
        box-shadow: 0 1px 2px rgba(15,23,42,0.04);
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] .ed-card-marker):not(
        :has(div[data-testid="stVerticalBlock"] > div[data-testid="stElementContainer"] .ed-card-marker)
    )
    > div[data-testid="stElementContainer"]:has(.ed-card-marker) {
        display: none;
    }

    .ed-card-marker {
        display: none;
    }

    .ed-section-title {
        margin: 0;
        color: #0F172A;
        font-size: 15px;
        font-weight: 700;
        font-family: 'Montserrat', sans-serif !important;
    }

    .ed-section-sub {
        margin: 3px 0 0;
        color: #64748B;
        font-size: 11px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-card-action {
        text-align: right;
        color: #2563EB;
        font-size: 12px;
        font-weight: 700;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-alert-list {
        display: flex;
        flex-direction: column;
        gap: 10px;
        margin-top: 12px;
        margin-bottom: 14px;
        flex: 1 1 auto;
        max-height: 360px;
        overflow-y: auto;
        padding-right: 4px;
    }

    .ed-alert-item {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 14px;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        background: #ffffff;
    }

    .ed-alert-icon {
        width: 40px;
        height: 40px;
        flex: 0 0 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: 999px;
        font-weight: 900;
    }

    .ed-alert-icon svg {
        width: 18px;
        height: 18px;
    }

    .ed-alert-title {
        margin: 0;
        color: #0F172A;
        font-size: 12.5px;
        font-weight: 700;
        line-height: 1.35;
        font-family: 'Montserrat', sans-serif !important;
    }

    .ed-alert-sub {
        margin: 4px 0 0;
        color: #64748B;
        font-size: 11.5px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-table-card {
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        background: #ffffff;
        box-shadow: 0 4px 18px rgba(15, 23, 42, 0.05);
        overflow: hidden;
    }

    .ed-table-head {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 18px 18px 14px;
    }

    .ed-table-head-stack {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
        padding: 18px 18px 12px;
    }

    .ed-table-head-copy {
        min-width: 0;
    }

    .ed-table-title {
        margin: 0;
        color: #0F172A;
        font-size: 15px;
        font-weight: 700;
        font-family: 'Montserrat', sans-serif !important;
    }

    .ed-table-subtitle {
        margin: 4px 0 0;
        color: #64748B;
        font-size: 11px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-table-link {
        color: #2563EB;
        font-size: 12px;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
        text-decoration: none;
        white-space: nowrap;
    }

    .ed-table-link-with-icon {
        display: inline-flex;
        align-items: center;
        justify-content: flex-end;
        gap: 6px;
        padding-top: 2px;
    }

    .ed-view-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 16px;
        height: 16px;
        color: #2563EB;
        font-size: 13px;
        line-height: 1;
    }

    .ed-table-scroll {
        width: 100%;
        overflow-x: auto;
        padding: 0 14px 14px;
        box-sizing: border-box;
    }

    .ed-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        color: #0F172A;
        font-size: 12px;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-table thead tr {
        background: rgba(99, 102, 241, 0.06);
        border-radius: 10px;
        overflow: hidden;
    }

    .ed-table th {
        padding: 11px 16px;
        background: transparent;
        border: none;
        color: #4F46E5;
        font-size: 11px;
        font-weight: 700;
        text-align: left;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-table th:first-child {
        border-top-left-radius: 10px;
        border-bottom-left-radius: 10px;
    }

    .ed-table th:last-child {
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
    }

    .ed-table th.ed-th-right,
    .ed-table td.ed-td-right {
        text-align: right;
    }

    .ed-table th.ed-th-center,
    .ed-table td.ed-td-center {
        text-align: center;
    }

    .ed-table td {
        padding: 11px 14px;
        border-bottom: 1px solid #F1F5F9;
        color: #0F172A;
        font-size: 12px;
        font-weight: 500;
        white-space: nowrap;
        font-family: 'Inter', sans-serif !important;
        background: #ffffff;
    }

    .ed-table tbody tr:hover td {
        background: #FAFAFF;
    }

    .ed-table tbody tr:last-child td {
        border-bottom: none;
    }

    .ed-value-blue {
        color: #2563EB;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-rank-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 22px;
        height: 22px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
        margin-right: 8px;
        vertical-align: middle;
        flex: 0 0 22px;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-rank-badge.rank-1 {
        background: #F97316;
        color: #ffffff;
    }

    .ed-rank-badge.rank-2 {
        background: #94A3B8;
        color: #ffffff;
    }

    .ed-rank-badge.rank-3 {
        background: #B45309;
        color: #ffffff;
    }

    .ed-tenant-with-rank {
        display: inline-flex;
        align-items: center;
        gap: 0;
    }

    .ed-table-card.ed-table-best3 .ed-table tbody td {
        padding-top: 25px;
        padding-bottom: 25px;
        vertical-align: middle;
    }

    .ed-table-card.ed-table-best3 .ed-table tbody tr:hover td {
        background: #FAFAFF;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-top-tables-marker) .ed-table-scroll {
        flex: 1 1 auto !important;
        display: flex !important;
        flex-direction: column !important;
        min-height: 0 !important;
    }

    div[data-testid="stHorizontalBlock"]:has(.overview-top-tables-marker) .ed-table tbody {
        vertical-align: top;
    }

    .ed-positive {
        color: #059669;
        font-weight: 700;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-negative {
        color: #DC2626;
        font-weight: 700;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-pagination {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 12px;
        padding: 13px 18px 16px;
        border-top: 1px solid #F1F5F9;
        color: #64748B;
        font-size: 12px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
    }

    .ed-chip-row {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 8px;
    }

    body:has(.dv-page-marker) [data-testid="stSelectbox"] > div > div {
        min-height: 40px !important;
        height: 40px !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background: #ffffff !important;
        box-shadow: none !important;
        outline: none !important;
        transition: border-color 0.15s ease, background-color 0.15s ease !important;
    }

    body:has(.dv-page-marker) [data-testid="stSelectbox"] div[data-baseweb="select"],
    body:has(.dv-page-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] span,
    body:has(.dv-page-marker) [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"],
    body:has(.dv-page-marker) [data-testid="stSelectbox"] [data-baseweb="select"] [data-testid="stMarkdownContainer"] p {
        font-size: 13px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        color: #0F172A !important;
    }

    body:has(.dv-page-marker) [data-testid="stTextInput"] [data-baseweb="input"] {
        min-height: 40px !important;
        height: 40px !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background: #ffffff !important;
        box-shadow: none !important;
        outline: none !important;
        overflow: hidden !important;
        display: flex !important;
        align-items: center !important;
        transition: border-color 0.15s ease, background-color 0.15s ease !important;
    }

    body:has(.dv-page-marker) [data-testid="stTextInput"] [data-baseweb="input"] > div {
        width: 100% !important;
        height: 100% !important;
        display: flex !important;
        align-items: center !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }

    body:has(.dv-page-marker) .stTextInput > div > div > input,
    body:has(.dv-page-marker) [data-testid="stTextInput"] input {
        min-height: 38px !important;
        height: 38px !important;
        border: none !important;
        border-radius: 8px !important;
        background: transparent !important;
        box-shadow: none !important;
        outline: none !important;
        color: #0F172A !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0 12px !important;
    }

    body:has(.dv-page-marker) [data-testid="stSelectbox"] > div > div:hover,
    body:has(.dv-page-marker) [data-testid="stSelectbox"] > div > div:focus-within,
    body:has(.dv-page-marker) [data-testid="stTextInput"] [data-baseweb="input"]:hover,
    body:has(.dv-page-marker) [data-testid="stTextInput"] [data-baseweb="input"]:focus-within {
        border-color: #94A3B8 !important;
        background: #F8FAFC !important;
        box-shadow: none !important;
        outline: none !important;
    }

    body:has(.dv-page-marker) .stTextInput > div > div > input:focus,
    body:has(.dv-page-marker) .stTextInput > div > div > input:hover,
    body:has(.dv-page-marker) [data-testid="stTextInput"] input:focus,
    body:has(.dv-page-marker) [data-testid="stTextInput"] input:hover {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
        background: transparent !important;
    }

    body:has(.dv-page-marker) .stTextInput > div > div > input::placeholder,
    body:has(.dv-page-marker) [data-testid="stTextInput"] input::placeholder {
        color: #94A3B8 !important;
    }

    div[data-baseweb="popover"],
    div[data-baseweb="menu"],
    div[data-baseweb="popover"] div[data-baseweb="menu"],
    div[data-baseweb="popover"] ul[role="listbox"] {
        z-index: 999999 !important;
    }

    div[data-baseweb="menu"],
    div[data-baseweb="menu"] > div,
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] div[data-baseweb="menu"],
    div[data-baseweb="popover"] div[data-baseweb="menu"] > div,
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] ul[role="listbox"] {
        background: #ffffff !important;
        border: 1px solid #CBD5E1 !important;
        border-radius: 8px !important;
        box-shadow: 0 10px 26px rgba(15, 23, 42, 0.12) !important;
        overflow: hidden !important;
    }

    div[data-baseweb="menu"] ul,
    div[data-baseweb="menu"] [role="listbox"],
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] [role="listbox"] {
        margin: 0 !important;
        padding: 4px !important;
        background: #ffffff !important;
        border-radius: 8px !important;
        border: 0 !important;
        box-shadow: none !important;
    }

    div[data-baseweb="menu"] li,
    div[data-baseweb="menu"] [role="option"],
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] [role="option"],
    div[data-baseweb="popover"] [data-baseweb="menu"] li {
        min-height: 48px !important;
        height: 48px !important;
        padding: 0 20px !important;
        margin: 0 !important;
        border-radius: 6px !important;
        background: #ffffff !important;
        color: #0F172A !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        line-height: 1.25 !important;
        display: flex !important;
        align-items: center !important;
    }

    div[data-baseweb="menu"] li *,
    div[data-baseweb="menu"] [role="option"] *,
    div[data-baseweb="popover"] li *,
    div[data-baseweb="popover"] [role="option"] * {
        background: transparent !important;
        color: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        line-height: inherit !important;
    }

    div[data-baseweb="menu"] li > div,
    div[data-baseweb="menu"] [role="option"] > div,
    div[data-baseweb="popover"] li > div,
    div[data-baseweb="popover"] [role="option"] > div {
        min-height: 0 !important;
        height: 100% !important;
        margin: 0 !important;
        padding: 0 !important;
        display: flex !important;
        align-items: center !important;
        width: 100% !important;
    }

    div[data-baseweb="menu"] li > div > div,
    div[data-baseweb="menu"] [role="option"] > div > div,
    div[data-baseweb="popover"] li > div > div,
    div[data-baseweb="popover"] [role="option"] > div > div,
    div[data-baseweb="menu"] [data-testid="stMarkdownContainer"],
    div[data-baseweb="popover"] [data-testid="stMarkdownContainer"],
    div[data-baseweb="menu"] [data-testid="stMarkdownContainer"] p,
    div[data-baseweb="popover"] [data-testid="stMarkdownContainer"] p {
        margin: 0 !important;
        padding: 0 !important;
        min-height: 0 !important;
        height: auto !important;
        display: flex !important;
        align-items: center !important;
        line-height: 1.25 !important;
    }

    div[data-baseweb="menu"] li:hover,
    div[data-baseweb="menu"] [role="option"]:hover,
    div[data-baseweb="menu"] [role="option"][aria-selected="true"],
    div[data-baseweb="menu"] [aria-selected="true"],
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] [role="option"]:hover,
    div[data-baseweb="popover"] [role="option"][aria-selected="true"],
    div[data-baseweb="popover"] [aria-selected="true"] {
        background: #EFF6FF !important;
        color: #1D4ED8 !important;
    }

    div[data-testid="stButton"] > button,
    div[data-testid="stDownloadButton"] > button {
        min-height: 40px !important;
        height: 40px !important;
        padding: 0 14px !important;
        border-radius: 8px !important;
        border: 1px solid #CBD5E1 !important;
        background: #ffffff !important;
        color: #0F172A !important;
        box-shadow: none !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        transition: border-color 0.15s ease, background-color 0.15s ease, color 0.15s ease !important;
    }

    div[data-testid="stDownloadButton"] > button p,
    div[data-testid="stButton"] > button p {
        font-size: 13px !important;
        font-weight: 500 !important;
        font-family: 'Inter', sans-serif !important;
        color: #0F172A !important;
    }

    .ed-pagination-info {
        display: flex;
        align-items: center;
        height: 44px;
        padding: 0 4px;
        color: #64748B;
        font-size: 12px;
        font-weight: 500;
        font-family: 'Inter', sans-serif !important;
        border-top: 1px solid #F1F5F9;
    }

    .overview-detail-pagination-footer-marker {
        display: none;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stElementContainer"]:has(.overview-detail-pagination-footer-marker) {
        display: none;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type {
        align-items: center !important;
        gap: 2px !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(2),
    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(3),
    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(4) {
        flex: 0 0 auto !important;
        width: auto !important;
        min-width: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(2) {
        width: 32px !important;
        max-width: 32px !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(4) {
        width: 32px !important;
        max-width: 32px !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(3) {
        width: max-content !important;
        max-width: max-content !important;
        flex: 0 0 max-content !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    > div[data-testid="column"]:nth-child(3) .ed-pagination-label {
        justify-content: center;
        padding: 0 2px;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
        border-top: 1px solid #F1F5F9 !important;
        height: 44px !important;
        width: 32px !important;
        min-width: 32px !important;
        max-width: 32px !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] > button {
        height: 30px !important;
        min-height: 30px !important;
        width: 30px !important;
        min-width: 30px !important;
        max-width: 30px !important;
        padding: 0 !important;
        margin: 0 !important;
        border-radius: 6px !important;
        border: 1px solid #E2E8F0 !important;
        background: #ffffff !important;
        color: #334155 !important;
        font-size: 18px !important;
        font-weight: 400 !important;
        line-height: 1 !important;
        box-shadow: none !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] > button:hover:not(:disabled) {
        background: #F1F5F9 !important;
        border-color: #CBD5E1 !important;
        color: #0F172A !important;
    }

    div[data-testid="stVerticalBlock"]:has(.overview-detail-pagination-footer-marker)
    > div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] > button:disabled {
        opacity: 0.3 !important;
    }


    .ed-pagination-label {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 44px;
        padding: 0 2px;
        color: #0F172A;
        font-size: 12px;
        font-weight: 600;
        font-family: 'Inter', sans-serif !important;
        white-space: nowrap;
        border-top: 1px solid #F1F5F9;
    }

    /* Reset semua button dulu */
    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] > .ed-card-marker)
    div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] {
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 0 !important;
        border-top: 1px solid #F1F5F9 !important;
        height: 44px !important;
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] > .ed-card-marker)
    div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] > button {
        height: 30px !important;
        min-height: 30px !important;
        width: 30px !important;
        min-width: 0 !important;
        max-width: 30px !important;
        padding: 0 !important;
        margin: 0 auto !important;
        border-radius: 6px !important;
        border: 1px solid #E2E8F0 !important;
        background: #ffffff !important;
        color: #334155 !important;
        font-size: 18px !important;
        font-weight: 400 !important;
        line-height: 1 !important;
        box-shadow: none !important;
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] > .ed-card-marker)
    div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] > button:hover:not(:disabled) {
        background: #F1F5F9 !important;
        border-color: #CBD5E1 !important;
        color: #0F172A !important;
    }

    div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] > .ed-card-marker)
    div[data-testid="stHorizontalBlock"]:last-of-type
    div[data-testid="stButton"] > button:disabled {
        opacity: 0.3 !important;
    }

                
    .overview-kpi-card,
    .overview-kpi-card *,
    .kpi-pro-card,
    .kpi-pro-card *,
    .overview-light-table-wrap,
    .overview-light-table-wrap *,
    .ed-table-card,
    .ed-table-card *,
    div[data-testid="stVerticalBlock"]:has(.ed-card-marker),
    div[data-testid="stVerticalBlock"]:has(.ed-card-marker) * {
        font-family: 'Inter', sans-serif !important;
    }

    div[data-testid="stButton"] > button:hover,
    div[data-testid="stDownloadButton"] > button:hover {
        border-color: #94A3B8 !important;
        background: #F8FAFC !important;
        color: #0F172A !important;
        transform: none !important;
    }

    @media (max-width: 1100px) {
        .overview-kpi-card {
            min-height: 104px;
        }

        .overview-kpi-value {
            font-size: 23px;
        }

        .kpi-pro-card {
            min-height: 150px;
            padding: 14px 16px;
        }

        .kpi-pro-value {
            font-size: 21px;
        }
    }
    </style>
    """


_OVERVIEW_EXTRA_CSS = dedent(f"""
    <style>
    /* Same header-to-filter gap as the Lease Contract page. */
    body:has(.overview-page-marker) .ov-fixed-header-spacer,
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-fixed-header-spacer) {{
        height: 56px !important;
        min-height: 56px !important;
        max-height: 56px !important;
    }}
    /* ── Filter Data card (same design as Lease Contract) ──────────── */
    body:has(.overview-page-marker) div[data-testid="stHorizontalBlock"]:has(.ov-filtercard-marker),
    body:has(.overview-page-marker) div[data-testid="stLayoutWrapper"]:has(.ov-filtercard-marker) {{
        margin-top: -24px !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"] {{
        background: #FFFFFF !important;
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 20px !important;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.03), 0 2px 4px -1px rgba(0,0,0,0.015) !important;
        padding: 18px 20px 14px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stHorizontalBlock"]:has(.ov-filtercard-marker) ~ div[data-testid="stHorizontalBlock"]:has(.kpi-pro-card),
    body:has(.overview-page-marker) div[data-testid="stLayoutWrapper"]:has(.ov-filtercard-marker) ~ div[data-testid="stLayoutWrapper"]:has(.kpi-pro-card) {{
        margin-top: 1px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stLayoutWrapper"]:has(.kpi-pro-card) + div[data-testid="stLayoutWrapper"]:has(.kpi-pro-card) {{
        margin-top: 10px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-vertical-spacer) {{
        margin-top: 0px !important;
        margin-bottom: 0px !important;
        height: 10px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-vertical-spacer) + div[data-testid="stElementContainer"] {{
        margin-top: -24px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-vertical-spacer) + div:has(.ed-card-marker) {{
        margin-top: -24px !important;
    }}
    /* Jarak Vertikal antara KPI Cards baris kedua dengan Revenue Trend dan Alert & Insight */
    body:has(.overview-page-marker) [data-testid="stHorizontalBlock"]:has(.overview-trend-card),
    body:has(.overview-page-marker) [data-testid="stLayoutWrapper"]:has(.overview-trend-card) {{
        margin-top: 10px !important;
    }}
    .ov-filtercard-head {{
        display: flex; align-items: center; gap: 12px;
    }}
    .ov-filtercard-icon {{
        width: 34px; height: 34px; border-radius: 10px; flex: 0 0 34px;
        background: #EEF2FF; color: #4338CA;
        display: flex; align-items: center; justify-content: center;
    }}
    .ov-filtercard-title {{
        margin: 0 !important; color: #0F172A; font-size: 18px !important; font-weight: 700 !important;
        font-family: 'Montserrat', sans-serif !important; line-height: 1 !important;
    }}
    .ov-filtercard-badge {{
        display: inline-flex; align-items: center; margin-left: 8px;
        padding: 2px 8px; border-radius: 999px; vertical-align: middle;
        background: #F0FDF4; border: 1px solid #BBF7D0;
        font-size: 10.5px !important; font-weight: 700 !important; color: #16A34A;
        white-space: nowrap;
    }}
    .ov-filtercard-sub {{
        margin: 5px 0 0 !important; color: #64748B; font-size: 11px !important; font-weight: 400 !important;
        line-height: 1 !important;
        font-family: 'Inter', sans-serif !important;
    }}
    .ov-filter-label {{
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        gap: 6px !important;
        color: #475569 !important;
        font-size: 11.5px !important;
        font-weight: 700 !important;
        font-family: Inter, sans-serif !important;
        margin: 0 0 6px 4px !important;
        height: 16px !important;
        line-height: 16px !important;
    }}
    .ov-filter-label svg {{
        display: block !important;
        flex-shrink: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    .ov-filter-label span {{
        line-height: 1 !important;
        display: inline-block !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-filter-label) {{
        margin-bottom: -4px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-filterrow-marker) {{
        margin: 0 !important; padding: 0 !important; height: 0 !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-filterrow-marker) + div[data-testid="stHorizontalBlock"],
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-filterrow-marker) + div[data-testid="stLayoutWrapper"] {{
        margin-top: -4px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-filtercard-footer-marker) {{
        margin: 6px 0 -10px !important;
        height: 1px !important;
        border-top: 1px solid #F1F5F9 !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="baseButton-secondary"] {{
        border: 1px solid #E2E8F0 !important; border-radius: 8px !important;
        background: #ffffff !important; color: #475569 !important;
        font-size: 11.5px !important; font-weight: 700 !important;
        font-family: Inter, sans-serif !important;
        height: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        width: 145px !important;
        min-width: 145px !important;
        max-width: 145px !important;
        padding: 0 !important;
        margin-left: auto !important; margin-right: 0 !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-reset-top-marker) + div[data-testid="stElementContainer"] [data-testid="baseButton-secondary"],
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-reset-top-marker) + div[data-testid="stElementContainer"] [data-testid="stBaseButton-secondary"] {{
        border-radius: 999px !important;
        width: auto !important;
        min-width: 0 !important;
        max-width: none !important;
        height: 36px !important;
        min-height: 36px !important;
        max-height: 36px !important;
        padding: 0 18px !important;
        font-size: 13px !important;
    }}
    body:has(.overview-page-marker) div[data-testid="stElementContainer"]:has(.ov-reset-top-marker) + div[data-testid="stElementContainer"] [data-testid="stIconMaterial"] {{
        font-family: 'Material Symbols Rounded' !important;
        font-size: 15px !important;
    }}
    body:has(.overview-page-marker) [data-testid="baseButton-primary"],
    body:has(.overview-page-marker) [data-testid="stBaseButton-primary"] {{
        border-radius: 999px !important;
        font-size: 12.5px !important; font-weight: 700 !important;
        font-family: Inter, sans-serif !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        border: none !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35) !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="baseButton-primary"],
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stBaseButton-primary"] {{
        border-radius: 8px !important;
        font-size: 11.5px !important; font-weight: 700 !important;
        font-family: Inter, sans-serif !important;
        color: #ffffff !important;
        background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%) !important;
        border: none !important;
        box-shadow: 0 3px 10px rgba(99, 102, 241, 0.2) !important;
        height: 32px !important;
        min-height: 32px !important;
        max-height: 32px !important;
        width: 145px !important;
        min-width: 145px !important;
        max-width: 145px !important;
        padding: 0 !important;
        margin-left: auto !important; margin-right: 0 !important;
    }}
    body:has(.overview-page-marker) [data-testid="baseButton-primary"]:hover,
    body:has(.overview-page-marker) [data-testid="stBaseButton-primary"]:hover {{
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.45) !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="baseButton-primary"]:hover,
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stBaseButton-primary"]:hover {{
        background: linear-gradient(135deg, #4F46E5 0%, #4338CA 100%) !important;
        box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3) !important;
    }}
    body:has(.overview-page-marker) [data-testid="baseButton-primary"] svg,
    body:has(.overview-page-marker) [data-testid="stBaseButton-primary"] [data-testid="stIconMaterial"] {{
        color: #ffffff !important;
        fill: #ffffff !important;
        font-family: 'Material Symbols Rounded' !important;
    }}
    body:has(.overview-page-marker) [data-testid="baseButton-primary"] p,
    body:has(.overview-page-marker) [data-testid="stBaseButton-primary"] p {{
        color: #ffffff !important;
    }}
    /* ── Selectbox Dropdowns in Filter Card ────────────────────────── */
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] {{
        margin-bottom: 0 !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] > div {{
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] > div > div {{
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        backdrop-filter: none !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] {{
        border: 1px solid #E2E8F0 !important;
        border-radius: 999px !important;
        background-color: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(99, 102, 241, 0.04) !important;
        transition: all 0.2s ease !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"]:hover {{
        border-color: #CBD5E1 !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {{
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.1) !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        min-height: 32px !important;
        height: 32px !important;
        max-height: 32px !important;
        padding: 0 4px 0 12px !important;
        display: flex !important;
        align-items: center !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] [data-testid="stSelectboxSelectedValue"] {{
        font-size: 11.5px !important;
        font-weight: 600 !important;
        color: #334155 !important;
    }}
    body:has(.overview-page-marker) [data-testid="stVerticalBlockBorderWrapper"]:has(.ov-filtercard-marker) [data-testid="stSelectbox"] svg {{
        color: #64748B !important;
    }}

    /* Export button on overview detail tenant table */
    div[data-testid="stElementContainer"]:has(.ov-btn-export-marker) {{
        position: absolute !important;
        width: 0 !important;
        height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }}
    div[data-testid="stElementContainer"]:has(.ov-btn-export-marker) + div[data-testid="stElementContainer"] button {{
        background: rgba(255, 255, 255, 0.72) !important;
        border: 1px solid rgba(99, 102, 241, 0.25) !important;
        color: #4F46E5 !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 6px !important;
        padding: 0 16px !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 12px !important;
        min-height: 38px !important;
        height: 38px !important;
        box-shadow: none !important;
        transition: all 0.2s ease !important;
    }}
    div[data-testid="stElementContainer"]:has(.ov-btn-export-marker) + div[data-testid="stElementContainer"] button:hover {{
        background: #f5f3ff !important;
        border-color: rgba(99, 102, 241, 0.45) !important;
    }}
    div[data-testid="stElementContainer"]:has(.ov-btn-export-marker) + div[data-testid="stElementContainer"] button p {{
        color: #4F46E5 !important;
        font-size: 12px !important;
        font-weight: 700 !important;
        font-family: 'Inter', sans-serif !important;
        margin: 0 !important;
        padding: 0 !important;
    }}
    div[data-testid="stElementContainer"]:has(.ov-btn-export-marker) + div[data-testid="stElementContainer"] button::before {{
        content: "" !important;
        display: inline-block !important;
        width: 14px !important;
        height: 14px !important;
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="%234F46E5" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>') !important;
        background-size: contain !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        flex-shrink: 0 !important;
    }}
    </style>
    """)
