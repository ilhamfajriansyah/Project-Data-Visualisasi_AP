from base64 import b64encode
from pathlib import Path
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
LOGO_PATH = PROJECT_DIR / "asset" / "logo.png"

LEFT_PANEL_IMAGE_CANDIDATES = [
    PROJECT_DIR / "airport-terminal 1.png",
    PROJECT_DIR / "asset" / "airport-terminal 1.png",
]


def get_left_panel_background_css() -> str:
    for path in LEFT_PANEL_IMAGE_CANDIDATES:
        if path.exists():
            encoded_image = b64encode(path.read_bytes()).decode("ascii")
            return (
                "background: "
                "linear-gradient(90deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 28%, rgba(255,255,255,0.08) 100%), "
                f'url("data:image/png;base64,{encoded_image}") center center / cover no-repeat;'
            )

    return (
        "background: "
        "linear-gradient(180deg, rgba(230,241,255,0.95), rgba(247,251,255,0.98));"
    )


def get_logo_markup() -> str:
    if LOGO_PATH.exists():
        encoded_logo = b64encode(LOGO_PATH.read_bytes()).decode("ascii")
        return (
            f'<img class="brand-logo" src="data:image/png;base64,{encoded_logo}" '
            'alt="InJourney logo" />'
        )

    return """
        <div class="brand-logo-fallback" aria-label="InJourney logo fallback">
            <span class="brand-logo-main">injourney</span>
        </div>
    """


def inject_shared_css() -> None:
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Poppins', sans-serif;
        }}

        html, body {{
            margin: 0;
            min-height: 100%;
            overflow-x: hidden !important;
        }}

        body,
        [data-testid="stApp"],
        [data-testid="stAppViewContainer"],
        [data-testid="stMain"] {{
            min-height: 100vh;
            background: linear-gradient(
                90deg,
                #e6f1ff 0%,
                #f7fbff 49.7%,
                #f2f5fa 49.7%,
                #f2f5fa 100%
            ) !important;
        }}

        #MainMenu, header, footer {{
            visibility: hidden;
        }}

        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stDecoration"] {{
            display: none !important;
        }}

        .block-container {{
            padding: 0 !important;
            max-width: 100vw !important;
        }}

        [data-testid="column"] {{
            padding: 0 !important;
        }}

        [data-testid="stVerticalBlock"] {{
            gap: 0 !important;
        }}

        [data-testid="stMain"] .block-container > [data-testid="stVerticalBlock"] > div > [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1),
        [data-testid="stMain"] .block-container > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] > div > [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1),
        [data-testid="stMain"] .block-container > div > [data-testid="stVerticalBlock"] > div > [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) {{
            display: flex;
            align-items: stretch;
            justify-content: stretch;
            min-height: 100vh;
            padding: 0 !important;
            margin: 0 !important;
            overflow: hidden !important;
        }}

        [data-testid="stMain"] .block-container > [data-testid="stVerticalBlock"] > div > [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) > div,
        [data-testid="stMain"] .block-container > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] > div > [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) > div,
        [data-testid="stMain"] .block-container > div > [data-testid="stVerticalBlock"] > div > [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(1) > div {{
            width: 100%;
            min-height: 100vh;
            margin: 0 !important;
            padding: 0 !important;
        }}

        /* ── Right panel column ── */
        div[data-testid="column"]:nth-child(2) {{
            min-height: 100vh;
            background: #f2f5fa !important;
            padding: 44px 56px !important;
            box-sizing: border-box !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        div[data-testid="column"]:nth-child(2) > div:first-child {{
            width: 100% !important;
            min-height: 100vh;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}


        /* ── Form card: target the border-wrapper Streamlit creates for container(border=True) ── */
        div[data-testid="column"]:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] {{
            width: 100% !important;
            max-width: 520px !important;
            margin: 0 auto !important;
            background: #ffffff !important;
            border: 2px solid #d8dee8 !important;
            outline: 1px solid #e9edf3 !important;
            outline-offset: 0;
            border-radius: 28px !important;
            box-shadow:
                0 2px 6px rgba(15, 23, 42, 0.04),
                0 12px 28px rgba(15, 23, 42, 0.10),
                0 28px 56px rgba(15, 23, 42, 0.07) !important;
            padding: 36px 36px 34px !important;
            box-sizing: border-box !important;
        }}

        /* ── Reset Streamlit's default border inside our card ── */
        div[data-testid="column"]:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"] > div[data-testid="stVerticalBlock"] {{
            gap: 0 !important;
        }}

        .left-panel {{
            position: relative;
            width: 100%;
            height: 100%;
            min-height: 100vh;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden;
            {get_left_panel_background_css()}
            border-right: 1px solid rgba(255, 255, 255, 0.72);
            box-shadow: inset -1px 0 0 rgba(203, 220, 245, 0.28);
        }}

        .left-panel::before {{
            content: "";
            position: absolute;
            inset: 0;
            background: linear-gradient(
                180deg,
                rgba(255,255,255,0.10),
                rgba(255,255,255,0.02) 40%,
                rgba(255,255,255,0.22) 100%
            );
            pointer-events: none;
        }}

        .left-panel::after {{
            content: "";
            position: absolute;
            top: 0;
            right: 0;
            width: 24px;
            height: 100%;
            background: linear-gradient(
                90deg,
                rgba(255,255,255,0) 0%,
                rgba(255,255,255,0.55) 100%
            );
            pointer-events: none;
        }}

        .login-top {{
            text-align: center;
            margin: 0 0 26px;
        }}

        .brand-mark {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            gap: 4px;
            margin: 0 0 10px;
        }}

        .brand-logo {{
            width: 200px;
            max-height: 90px;
            height: auto;
            display: block;
            margin: 14px auto 10px;
            object-fit: contain;
        }}

        .hero-title {{
            margin: 0;
            color: #000000 !important;
            font-size: 28px;
            line-height: 1.15;
            font-weight: 700;
        }}

        .hero-subtitle {{
            margin: 10px 0 0;
            color: #64748b;
            font-size: 14px;
        }}

        .forgot-form-top-gap {{
            height: 14px;
        }}

        .forgot-bottom-gap {{
            height: 8px;
        }}

        .field-label {{
            color: #334155;
            font-size: 13px;
            font-weight: 600;
            margin: 18px 0 14px;
        }}

        div[data-testid="stForm"] {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin-top: 24px !important;
        }}

        [data-testid="stTextInput"] {{
            margin-bottom: 10px;
        }}

        [data-baseweb="input"] {{
            min-height: 56px !important;
            height: 56px !important;
            border-radius: 16px !important;
            background: #ffffff !important;
            box-shadow: inset 0 0 0 1px #d1d5db !important;
            border: none !important;
            overflow: hidden !important;
            display: flex !important;
            align-items: center !important;
        }}

        [data-baseweb="input"] > div {{
            width: 100% !important;
            height: 100% !important;
            display: flex !important;
            align-items: center !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: 0 !important;
        }}

        [data-baseweb="input"]:focus-within {{
            box-shadow: inset 0 0 0 1px #068585 !important, 0 0 0 3px rgba(6, 133, 133, 0.12) !important;
        }}

        [data-baseweb="input"] input {{
            width: 100% !important;
            height: 56px !important;
            min-height: 56px !important;
            padding: 0 16px !important;
            margin: 0 !important;
            border: none !important;
            outline: none !important;
            background: transparent !important;
            color: #334155 !important;
            font-size: 15px !important;
            box-sizing: border-box !important;
            appearance: none !important;
            -webkit-appearance: none !important;
        }}

        [data-baseweb="input"] input::placeholder {{
            color: #94a3b8 !important;
            opacity: 1 !important;
        }}

        [data-baseweb="input"] button {{
            height: 56px !important;
            min-height: 56px !important;
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            background: transparent !important;
            padding: 0 14px !important;
            margin: 0 !important;
        }}

        [data-baseweb="input"] *,
        [data-baseweb="input"] *:focus {{
            outline: none !important;
        }}

        div[data-testid="stButton"] {{
            margin-bottom: 0 !important;
        }}

        div[data-testid="stButton"] > button {{
            height: 52px;
            width: 100%;
            border-radius: 16px;
            font-size: 14px;
            font-weight: 700;
        }}

        div[data-testid="stButton"] > button[kind="secondary"] {{
            border: 1px solid #e5e7eb !important;
            background: #f3f4f6 !important;
            color: #334155 !important;
            box-shadow: none !important;
        }}

        div[data-testid="stButton"] > button[kind="primary"] {{
            border: 1px solid #068585 !important;
            background: linear-gradient(180deg, #0c8b8f 0%, #056a71 100%) !important;
            color: #ffffff !important;
            box-shadow: 0 12px 24px rgba(6, 133, 133, 0.18) !important;
        }}

        .auth-form-top-gap {{
            height: 18px;
        }}

        .auth-bottom-gap {{
            height: 10px;
        }}

        div[data-testid="stCheckbox"] {{
            margin: 0 !important;
            padding: 0 !important;
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
        }}

        div[data-testid="stCheckbox"] > label {{
            display: flex !important;
            align-items: center !important;
            gap: 6px !important;
            width: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
            cursor: pointer;
        }}

        div[data-testid="stCheckbox"] > label > div:first-child:not(:has(input[type="checkbox"])),
        div[data-testid="stCheckbox"] > label > span:first-child:not(:has(input[type="checkbox"])) {{
            display: none !important;
            width: 0 !important;
            min-width: 0 !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            overflow: hidden !important;
        }}

        div[data-testid="stCheckbox"] label > :has(input[type="checkbox"]) {{
            flex: 0 0 18px !important;
            width: 18px !important;
            height: 18px !important;
            min-width: 18px !important;
            margin: 0 !important;
            padding: 0 !important;
            position: relative !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        div[data-testid="stCheckbox"] input[type="checkbox"] {{
            appearance: none !important;
            -webkit-appearance: none !important;
            position: relative !important;
            inset: auto !important;
            z-index: 2 !important;
            width: 18px !important;
            height: 18px !important;
            min-width: 18px !important;
            margin: 0 !important;
            padding: 0 !important;
            border: 2px solid #cbd5e1 !important;
            border-radius: 5px !important;
            background: #ffffff !important;
            box-shadow: none !important;
            box-sizing: border-box !important;
            clip: auto !important;
            clip-path: none !important;
            opacity: 1 !important;
            cursor: pointer !important;
            display: grid !important;
            place-content: center !important;
            transition:
                background 180ms ease,
                border-color 180ms ease,
                box-shadow 180ms ease,
                transform 180ms ease !important;
        }}

        div[data-testid="stCheckbox"] input[type="checkbox"]::after {{
            content: "";
            width: 5px;
            height: 9px;
            margin-top: -1px;
            border: solid #ffffff;
            border-width: 0 2px 2px 0;
            opacity: 0;
            transform: rotate(45deg) scale(0.45);
            transform-origin: center;
            transition:
                opacity 130ms ease,
                transform 180ms cubic-bezier(0.2, 0.9, 0.25, 1.35);
        }}

        div[data-testid="stCheckbox"] input[type="checkbox"]:checked {{
            border-color: #068585 !important;
            background: linear-gradient(180deg, #0c8b8f 0%, #056a71 100%) !important;
            box-shadow: 0 0 0 3px rgba(6, 133, 133, 0.12) !important;
            animation: checkbox-pop 180ms ease-out;
        }}

        div[data-testid="stCheckbox"] input[type="checkbox"]:checked::after {{
            opacity: 1;
            transform: rotate(45deg) scale(1);
        }}

        div[data-testid="stCheckbox"] label > :has(input[type="checkbox"]) > div,
        div[data-testid="stCheckbox"] label > :has(input[type="checkbox"]) svg {{
            display: none !important;
        }}

        @keyframes checkbox-pop {{
            0% {{
                transform: scale(0.88);
            }}
            65% {{
                transform: scale(1.08);
            }}
            100% {{
                transform: scale(1);
            }}
        }}

        div[data-testid="stCheckbox"] > label p,
        div[data-testid="stCheckbox"] > label > div:not(:has(input[type="checkbox"])),
        div[data-testid="stCheckbox"] > label > span:not(:has(input[type="checkbox"])) {{
            margin: 0 !important;
            color: #111827 !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            line-height: 1.1 !important;
        }}

        [data-testid="stElementContainer"]:has(.forgot-password-link-wrap),
        [data-testid="stMarkdownContainer"]:has(.forgot-password-link-wrap) {{
            width: 100% !important;
            height: 44px !important;
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            margin: 0 !important;
            padding: 0 !important;
        }}

        .forgot-password-link-wrap {{
            width: 100% !important;
            height: 44px !important;
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            margin: 0 !important;
            padding: 0 !important;
            text-align: right !important;
        }}

        .forgot-password-link {{
            display: inline-flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            margin: 0 !important;
            padding: 0 !important;
            color: #64748b !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            line-height: 1.1 !important;
            text-align: right !important;
            text-decoration: none !important;
            white-space: nowrap !important;
        }}

        .forgot-password-link:hover {{
            color: #068585 !important;
            text-decoration: underline !important;
        }}

        div[data-testid="stButton"] > button[kind="tertiary"] {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin: -1px 0 0 0 !important;
            min-height: 44px !important;
            height: 44px !important;
            width: 100% !important;
            border-radius: 0 !important;
            color: #64748b !important;
            font-size: 12px !important;
            font-weight: 500 !important;
            line-height: 1.1 !important;
            text-decoration: none !important;
            display: flex !important;
            align-items: center !important;
            justify-content: flex-end !important;
            text-align: right !important;
            white-space: nowrap !important;
        }}

div[data-testid="stButton"] > button[kind="tertiary"] [data-testid="stMarkdownContainer"],
div[data-testid="stButton"] > button[kind="tertiary"] [data-testid="stMarkdownContainer"] p {{
    width: 100% !important;
    text-align: right !important;
    margin: 0 !important;
    white-space: nowrap !important;
}}

        div[data-testid="stButton"] > button[kind="tertiary"]:hover {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #068585 !important;
            text-decoration: underline !important;
            transform: none !important;
        }}

        div[data-testid="stButton"] > button[kind="tertiary"]:focus,
        div[data-testid="stButton"] > button[kind="tertiary"]:focus-visible {{
            outline: none !important;
            box-shadow: none !important;
        }}

        div[data-testid="column"]:nth-child(2) > div[data-testid="stButton"] {{
            width: 100% !important;
            margin: 0 !important;
            display: flex !important;
            align-items: center !important;
        }}

        div[data-testid="stFormSubmitButton"] {{
            width: 100% !important;
            display: block !important;
            margin-top: 18px !important;
        }}

        div[data-testid="stFormSubmitButton"] > button {{
            width: 100% !important;
            display: block !important;
            height: 58px !important;
            border-radius: 18px !important;
            border: 1px solid #068585 !important;
            background: linear-gradient(180deg, #0c8b8f 0%, #056a71 100%) !important;
            color: #ffffff !important;
            font-size: 16px !important;
            font-weight: 700 !important;
            box-shadow: 0 12px 24px rgba(6, 133, 133, 0.18) !important;
        }}

        .info-box {{
            display: flex !important;
            align-items: flex-start !important;
            gap: 14px !important;
            background: #f3f6f8;
            border: 1px solid #e5eaef;
            color: #475569;
            border-radius: 16px;
            padding: 16px 18px;
            font-size: 13px;
            line-height: 1.7;
            margin: 18px 0 22px 0;
        }}

        .info-box-icon {{
            flex-shrink: 0;
            width: 26px;
            height: 26px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            color: #475569;
            font-size: 18px;
            line-height: 1;
            margin-top: 1px;
        }}

        .info-box-text {{
            flex: 1;
        }}

        .success-box {{
            background: #ecfdf5;
            border: 1px solid #a7f3d0;
            color: #065f46;
            border-radius: 14px;
            padding: 14px 16px;
            font-size: 13px;
            line-height: 1.6;
            margin-top: 18px;
        }}

        .error-alert {{
            display: flex !important;
            align-items: center !important;
            gap: 12px;
            background-color: #fee5e3 !important;
            border: 1px solid #f39590 !important;
            border-radius: 12px !important;
            padding: 14px 16px !important;
            margin-top: 16px !important;
            width: 100%;
        }}

        .error-alert-icon {{
            flex-shrink: 0;
            font-size: 20px;
            color: #e8634f;
        }}

        .error-alert-content {{
            flex: 1;
            color: #cc3d2d !important;
            font-size: 14px;
            font-weight: 500;
            line-height: 1.4;
            margin: 0;
            text-align: left !important;
        }}

        bottom-link-wrap {{
            margin-top: 22px;
            text-align: center;
        }}

        .bottom-link {{
            color: #068585 !important;
            text-decoration: none !important;
            font-size: 13px !important;
            font-weight: 600 !important;
        }}

        .bottom-link:hover {{
            color: #0a7e85 !important;
            text-decoration: none !important;
        }}

        .bottom-login-link-wrap {{
            margin-top: 14px;
            display: flex;
            justify-content: center;
            align-items: center;
        }}

        .bottom-login-link-wrap [data-testid="stButton"] {{
            margin: 0 !important;
            width: auto !important;
        }}

        .bottom-login-link-wrap [data-testid="stButton"] > button[kind="tertiary"] {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            color: #068585 !important;
            font-size: 13px !important;
            font-weight: 600 !important;
            padding: 0 !important;
            margin: 0 !important;
            min-height: auto !important;
            height: auto !important;
            width: auto !important;
            line-height: 1.2 !important;
            text-decoration: none !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
        }}

        .bottom-login-link-wrap [data-testid="stButton"] > button[kind="tertiary"]:hover {{
            background: transparent !important;
            order: none !important;
            box-shadow: none !important;
            color: #0a7e85 !important;
            text-decoration: underline !important;
            transform: none !important;
        }}

        @media (max-width: 840px) {{
            .left-panel {{
                display: none;
            }}

            [data-testid="stMain"] .block-container > [data-testid="stVerticalBlock"] > div > [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2),
            [data-testid="stMain"] .block-container > [data-testid="stVerticalBlockBorderWrapper"] > [data-testid="stVerticalBlock"] > div > [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2),
            [data-testid="stMain"] .block-container > div > [data-testid="stVerticalBlock"] > div > [data-testid="stHorizontalBlock"] > div[data-testid="column"]:nth-child(2) {{
                padding: 18px 20px !important;
            }}

            .hero-title {{
                font-size: 24px;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_left_panel() -> None:
    st.markdown('<div class="left-panel"></div>', unsafe_allow_html=True)


def render_auth_header(title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="login-top">
            <div class="brand-mark">
                {get_logo_markup()}
            </div>
            <h2 class="hero-title">{title}</h2>
            <p class="hero-subtitle">{subtitle}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def show_error(message: str) -> None:
    st.markdown(
        f'''
        <div class="error-alert">
            <div class="error-alert-icon">⚠️</div>
            <div class="error-alert-content">{message}</div>
        </div>
        ''',
        unsafe_allow_html=True,
    )


def app_shell(render_right_panel, col_ratio=(1.4, 0.8)) -> None:
    inject_shared_css()

    left_col, right_col = st.columns(col_ratio, gap="small")

    with left_col:
        render_left_panel()

    with right_col:
        # border=True membuat Streamlit membungkus konten dalam
        # [data-testid="stVerticalBlockBorderWrapper"] yang bisa kita style via CSS
        with st.container(border=True):
            render_right_panel()
