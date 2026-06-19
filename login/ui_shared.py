from base64 import b64encode
from html import escape
from pathlib import Path
import streamlit as st

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
LOGO_PATHS = [
    PROJECT_DIR / "asset" / "logo.png",
    PROJECT_DIR / "asset" / "logo(2).png",
]

LEFT_PANEL_IMAGE_CANDIDATES = [
    PROJECT_DIR / "asset" / "background.jpeg",
    PROJECT_DIR / "background.jpeg",
]

IMAGE_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def image_to_data_url(path: Path) -> str:
    encoded_image = b64encode(path.read_bytes()).decode("ascii")
    mime_type = IMAGE_MIME_TYPES.get(path.suffix.lower(), "image/png")
    return f"data:{mime_type};base64,{encoded_image}"


def get_left_panel_background_css() -> str:
    for path in LEFT_PANEL_IMAGE_CANDIDATES:
        if path.exists():
            return (
                "background: "
                "linear-gradient(90deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 28%, rgba(255,255,255,0.08) 100%), "
                f'url("{image_to_data_url(path)}") center center / cover no-repeat;'
            )

    return (
        "background: "
        "linear-gradient(180deg, rgba(230,241,255,0.95), rgba(247,251,255,0.98));"
    )


def get_logo_markup() -> str:
    logo_images = []

    for index, path in enumerate(LOGO_PATHS):
        if path.exists():
            logo_images.append(
                f'<img class="brand-logo brand-logo-{index + 1}" '
                f'src="{image_to_data_url(path)}" alt="Logo {index + 1}" />'
            )

    if logo_images:
        return (
            '<div class="brand-logo-row">'
            + "".join(logo_images)
            + "</div>"
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
            transform-origin: center;
            animation: auth-form-enter 560ms cubic-bezier(0.22, 1, 0.36, 1) both;
            will-change: transform, opacity;
        }}

        @keyframes auth-form-enter {{
            0% {{
                opacity: 0;
                transform: translateY(18px);
            }}
            100% {{
                opacity: 1;
                transform: translateY(0);
            }}
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
            animation: airport-image-enter 680ms cubic-bezier(0.22, 1, 0.36, 1) both;
            will-change: transform, opacity;
        }}

        @keyframes airport-image-enter {{
            0% {{
                opacity: 0;
                transform: translateX(-28px);
            }}
            100% {{
                opacity: 1;
                transform: translateX(0);
            }}
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

        .brand-logo-row {{
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 18px;
            width: 100%;
            margin: 14px auto 12px;
            flex-wrap: wrap;
            transform: translateY(10px);
        }}

        .brand-logo {{
            width: auto;
            max-width: 190px;
            max-height: 74px;
            height: auto;
            display: block;
            object-fit: contain;
        }}

        .brand-logo-2 {{
            max-width: 150px;
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
            margin: 15px 0 15px;
        }}

        div[data-testid="stForm"] {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            padding: 0 !important;
            margin-top: 4px !important;
        }}

        [data-testid="stTextInput"] {{
            margin-bottom: 6px;
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
            transition:
                box-shadow 180ms ease,
                transform 180ms ease !important;
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
            box-shadow:
                inset 0 0 0 1.5px #068585,
                0 0 0 4px rgba(6, 133, 133, 0.14),
                0 10px 24px rgba(6, 133, 133, 0.16) !important;
        }}

        div[data-testid="column"]:nth-child(2) [data-baseweb="input"]:focus-within {{
            transform: translateY(-2px);
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
            caret-color: #111827 !important;
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
            color: #94a3b8 !important;
            transition:
                color 160ms ease,
                opacity 160ms ease,
                transform 180ms ease !important;
        }}

        [data-baseweb="input"] button:hover {{
            color: #068585 !important;
            transform: scale(1.08);
        }}

        [data-baseweb="input"] button:active {{
            transform: scale(0.94);
        }}

        [data-baseweb="input"] button svg {{
            transition:
                opacity 160ms ease,
                transform 180ms ease !important;
        }}

        [data-baseweb="input"] button:hover svg {{
            opacity: 0.92;
            transform: rotate(-6deg);
        }}

        [data-baseweb="input"] *,
        [data-baseweb="input"] *:focus {{
            outline: none !important;
        }}

        div[data-testid="stButton"] {{
            margin-bottom: 0 !important;
        }}

        [data-testid="stElementContainer"]:has([data-testid="stRadio"]),
        [data-testid="stVerticalBlock"] > div:has(> [data-testid="stElementContainer"] [data-testid="stRadio"]) {{
            width: 100% !important;
        }}

        [data-testid="stRadio"] {{
            display: block !important;
            width: 100% !important;
            max-width: none !important;
            min-height: 56px !important;
            margin: 8px 0 10px !important;
            padding: 0 !important;
            border-radius: 20px !important;
            background: linear-gradient(135deg, #e2e5ec 0%, #eaedf4 100%) !important;
            box-shadow:
                inset 0 1px 3px rgba(0,0,0,0.10),
                inset 0 -1px 0 rgba(255,255,255,0.70),
                0 1px 0 rgba(255,255,255,0.85) !important;
            box-sizing: border-box !important;
            overflow: hidden !important;
        }}

        [data-testid="stRadio"] > div,
        [data-testid="stRadio"] > div > div,
        [data-testid="stRadio"] [role="radiogroup"] {{
            width: 100% !important;
            max-width: none !important;
        }}

        [data-testid="stRadio"] [role="radiogroup"] {{
            height: 56px !important;
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 0 !important;
            align-items: stretch !important;
            position: relative !important;
            overflow: hidden !important;
            border-radius: 20px !important;
        }}

        [data-testid="stRadio"] [role="radiogroup"]::before {{
            content: "" !important;
            position: absolute !important;
            inset: 0 auto 0 0 !important;
            width: 50% !important;
            height: 100% !important;
            border-radius: 20px 0 0 20px !important;
            background: linear-gradient(180deg, #0c8b8f 0%, #056a71 100%) !important;
            border: none !important;
            box-shadow:
                inset 0 1px 0 rgba(255,255,255,0.20),
                inset 0 -1px 0 rgba(0,0,0,0.08) !important;
            box-sizing: border-box !important;
            contain: paint !important;
            pointer-events: none !important;
            transform: translateX(0) !important;
            transition:
                transform 340ms cubic-bezier(0.22, 1, 0.36, 1),
                border-radius 340ms cubic-bezier(0.22, 1, 0.36, 1),
                box-shadow 220ms ease,
                background 220ms ease !important;
            z-index: 0 !important;
        }}

        [data-testid="stRadio"] [role="radiogroup"]:has(label:last-child input[type="radio"]:checked)::before {{
            border-radius: 0 20px 20px 0 !important;
            transform: translateX(100%) !important;
        }}

        [data-testid="stRadio"] label:has(input[type="radio"]) {{
            width: 100% !important;
            max-width: none !important;
            flex: 1 1 0 !important;
            height: 56px !important;
            min-height: 56px !important;
            margin: 0 !important;
            padding: 0 !important;
            border: 1.5px solid transparent !important;
            border-radius: 0 !important;
            color: #6b7280 !important;
            background: transparent !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            line-height: 1 !important;
            letter-spacing: 0.01em !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            position: relative !important;
            overflow: hidden !important;
            box-sizing: border-box !important;
            cursor: pointer !important;
            transition:
                color 240ms cubic-bezier(0.22, 1, 0.36, 1),
                transform 200ms cubic-bezier(0.22, 1, 0.36, 1),
                box-shadow 200ms ease,
                background 240ms ease !important;
            z-index: 1 !important;
        }}

        [data-testid="stRadio"] label:has(input[type="radio"])::after {{
            content: "" !important;
            position: absolute !important;
            top: 0 !important;
            left: -100% !important;
            width: 60% !important;
            height: 100% !important;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(255,255,255,0.32) 50%,
                transparent 100%
            ) !important;
            transition: left 500ms ease !important;
            pointer-events: none !important;
            z-index: -1 !important;
        }}

        [data-testid="stRadio"] label:has(input[type="radio"]):hover {{
            color: #1f2937 !important;
            background: rgba(255, 255, 255, 0.40) !important;
            box-shadow:
                0 1px 4px rgba(0,0,0,0.06),
                0 4px 8px rgba(0,0,0,0.04) !important;
            transform: none !important;
            border-color: rgba(255,255,255,0.60) !important;
        }}

        [data-testid="stRadio"] label:has(input[type="radio"]):hover::after {{
            left: 140% !important;
        }}

        [data-testid="stRadio"] label:has(input[type="radio"]:checked),
        [data-testid="stRadio"] label:has(input[type="radio"]:checked):hover {{
            background: transparent !important;
            border-color: transparent !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            box-shadow: none !important;
            transform: none !important;
            animation: none !important;
        }}

        [data-testid="stRadio"] label:first-child:has(input[type="radio"]:checked) {{
            border-radius: 20px 0 0 20px !important;
        }}

        [data-testid="stRadio"] label:last-child:has(input[type="radio"]:checked) {{
            border-radius: 0 20px 20px 0 !important;
        }}

        [data-testid="stRadio"] label:has(input[type="radio"]:checked):hover {{
            background: transparent !important;
            border-color: transparent !important;
            box-shadow: none !important;
            transform: none !important;
        }}

        @keyframes tab-pill-settle {{
            0%   {{ filter: brightness(1.08); }}
            100% {{ filter: brightness(1); }}
        }}

        [data-testid="stRadio"] label:has(input[type="radio"]:checked)::after {{
            inset: 0 !important;
            left: auto !important;
            width: 100% !important;
            border-radius: inherit !important;
            background: transparent !important;
            box-shadow: none !important;
            animation: none !important;
            z-index: -1 !important;
        }}

        [data-testid="stRadio"] input[type="radio"] {{
            position: absolute !important;
            opacity: 0 !important;
            width: 0 !important;
            height: 0 !important;
            margin: 0 !important;
            padding: 0 !important;
            pointer-events: none !important;
        }}

        [data-testid="stRadio"] label:has(input[type="radio"]) > div:first-child {{
            display: none !important;
        }}

        [data-testid="stRadio"] label:has(input[type="radio"]) p,
        [data-testid="stRadio"] label:has(input[type="radio"]) span,
        [data-testid="stRadio"] label:has(input[type="radio"]) div {{
            color: inherit !important;
            font-size: 14px !important;
            font-weight: inherit !important;
            line-height: 1 !important;
            margin: 0 !important;
        }}

        /* ── Role Tab Switch ── */
        [data-testid="stButtonGroup"] {{
            width: 100% !important;
            min-height: 52px !important;
            margin: 8px 0 22px !important;
            padding: 4px !important;
            border-radius: 20px !important;
            background: linear-gradient(135deg, #e2e5ec 0%, #eaedf4 100%) !important;
            box-shadow:
                inset 0 1px 3px rgba(0,0,0,0.10),
                inset 0 -1px 0 rgba(255,255,255,0.70),
                0 1px 0 rgba(255,255,255,0.85) !important;
            box-sizing: border-box !important;
            position: relative !important;
            overflow: hidden !important;
        }}

        [data-testid="stButtonGroup"] [data-baseweb="button-group"] {{
            width: 100% !important;
            height: 44px !important;
            display: grid !important;
            grid-template-columns: 1fr 1fr !important;
            gap: 0 !important;
            position: relative !important;
        }}

        /* base button style */
        [data-testid="stButtonGroup"] button {{
            width: 100% !important;
            height: 44px !important;
            min-height: 44px !important;
            margin: 0 !important;
            border: 1.5px solid transparent !important;
            border-radius: 16px !important;
            background: transparent !important;
            box-shadow: none !important;
            color: #6b7280 !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            line-height: 1 !important;
            letter-spacing: 0.01em !important;
            cursor: pointer !important;
            position: relative !important;
            overflow: hidden !important;
            transition:
                color 240ms cubic-bezier(0.22, 1, 0.36, 1),
                transform 200ms cubic-bezier(0.22, 1, 0.36, 1),
                box-shadow 200ms ease,
                background 240ms ease !important;
            transform: scale(1) !important;
            z-index: 1 !important;
        }}

        /* ripple pseudo-element */
        [data-testid="stButtonGroup"] button::before {{
            content: "" !important;
            position: absolute !important;
            inset: 50% !important;
            width: 0 !important;
            height: 0 !important;
            border-radius: 50% !important;
            background: rgba(6, 133, 133, 0.18) !important;
            transform: translate(-50%, -50%) !important;
            transition:
                width 400ms ease,
                height 400ms ease,
                opacity 400ms ease !important;
            opacity: 0 !important;
            z-index: 0 !important;
        }}

        [data-testid="stButtonGroup"] button:active::before {{
            width: 220px !important;
            height: 220px !important;
            opacity: 1 !important;
            transition:
                width 0ms,
                height 0ms,
                opacity 0ms !important;
        }}

        /* shimmer sweep on hover (inactive) */
        [data-testid="stButtonGroup"] button::after {{
            content: "" !important;
            position: absolute !important;
            top: 0 !important;
            left: -100% !important;
            width: 60% !important;
            height: 100% !important;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(255,255,255,0.32) 50%,
                transparent 100%
            ) !important;
            transition: left 500ms ease !important;
            pointer-events: none !important;
            z-index: 0 !important;
        }}

        [data-testid="stButtonGroup"] button:hover::after {{
            left: 140% !important;
        }}

        /* hover state (inactive) */
        [data-testid="stButtonGroup"] button:hover {{
            color: #1f2937 !important;
            background: rgba(255, 255, 255, 0.40) !important;
            box-shadow:
                0 1px 4px rgba(0,0,0,0.06),
                0 4px 8px rgba(0,0,0,0.04) !important;
            transform: scale(1.02) !important;
            border-color: rgba(255,255,255,0.60) !important;
        }}

        [data-testid="stButtonGroup"] button:active {{
            transform: scale(0.97) !important;
        }}

        /* ACTIVE / SELECTED button */
        [data-testid="stButtonGroup"] button[aria-checked="true"],
        [data-testid="stButtonGroup"] button[aria-pressed="true"],
        [data-testid="stButtonGroup"] button[aria-selected="true"] {{
            background: linear-gradient(180deg, #0c8b8f 0%, #056a71 100%) !important;
            border-color: #068585 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            box-shadow:
                0 2px 8px rgba(6, 133, 133, 0.18),
                0 8px 22px rgba(6, 133, 133, 0.16),
                0 1px 2px rgba(0,0,0,0.08),
                inset 0 1px 0 rgba(255,255,255,0.22) !important;
            transform: scale(1.03) translateY(-1px) !important;
            animation: tab-pill-pop 320ms cubic-bezier(0.22, 1, 0.36, 1) both !important;
            z-index: 2 !important;
        }}

        @keyframes tab-pill-pop {{
            0%   {{ opacity: 0.6; transform: scale(0.95) translateY(2px); }}
            55%  {{ transform: scale(1.05) translateY(-2px); }}
            100% {{ opacity: 1;  transform: scale(1.03) translateY(-1px); }}
        }}

        /* glow pulse on active */
        [data-testid="stButtonGroup"] button[aria-checked="true"]::after,
        [data-testid="stButtonGroup"] button[aria-pressed="true"]::after,
        [data-testid="stButtonGroup"] button[aria-selected="true"]::after {{
            content: "" !important;
            position: absolute !important;
            inset: 0 !important;
            left: auto !important;
            width: 100% !important;
            border-radius: 16px !important;
            background: transparent !important;
            box-shadow: 0 0 0 0 rgba(6, 133, 133, 0.30) !important;
            animation: tab-glow-pulse 2.4s ease-in-out infinite !important;
            pointer-events: none !important;
            z-index: -1 !important;
        }}

        @keyframes tab-glow-pulse {{
            0%   {{ box-shadow: 0 0 0 0   rgba(6, 133, 133, 0.28); }}
            50%  {{ box-shadow: 0 0 0 6px rgba(6, 133, 133, 0.00); }}
            100% {{ box-shadow: 0 0 0 0   rgba(6, 133, 133, 0.28); }}
        }}

        /* active + hover: stay lifted, add extra glow */
        [data-testid="stButtonGroup"] button[aria-checked="true"]:hover,
        [data-testid="stButtonGroup"] button[aria-pressed="true"]:hover,
        [data-testid="stButtonGroup"] button[aria-selected="true"]:hover {{
            background: linear-gradient(180deg, #12a3a6 0%, #066f76 100%) !important;
            color: #ffffff !important;
            box-shadow:
                0 4px 14px rgba(6, 133, 133, 0.28),
                0 12px 30px rgba(6, 133, 133, 0.22),
                inset 0 1px 0 rgba(255,255,255,0.26) !important;
            transform: scale(1.04) translateY(-2px) !important;
            border-color: #04747a !important;
        }}

        /* Strong override for Streamlit/BaseWeb segmented controls. */
        [data-testid="stButtonGroup"] label:has(input:checked),
        [data-testid="stButtonGroup"] [role="radio"][aria-checked="true"],
        [data-testid="stButtonGroup"] [role="tab"][aria-selected="true"],
        [data-testid="stButtonGroup"] button[aria-checked="true"],
        [data-testid="stButtonGroup"] button[aria-pressed="true"],
        [data-testid="stButtonGroup"] button[aria-selected="true"],
        [data-testid="stSegmentedControl"] label:has(input:checked),
        [data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"],
        [data-testid="stSegmentedControl"] [role="tab"][aria-selected="true"],
        [data-testid="stSegmentedControl"] button[aria-checked="true"],
        [data-testid="stSegmentedControl"] button[aria-pressed="true"],
        [data-testid="stSegmentedControl"] button[aria-selected="true"] {{
            background: linear-gradient(180deg, #0c8b8f 0%, #056a71 100%) !important;
            border-color: #068585 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            box-shadow:
                0 2px 8px rgba(6, 133, 133, 0.18),
                0 8px 22px rgba(6, 133, 133, 0.16),
                0 1px 2px rgba(0,0,0,0.08),
                inset 0 1px 0 rgba(255,255,255,0.22) !important;
            transform: scale(1.03) translateY(-1px) !important;
        }}

        [data-testid="stButtonGroup"] label:has(input:checked) *,
        [data-testid="stButtonGroup"] [role="radio"][aria-checked="true"] *,
        [data-testid="stButtonGroup"] [role="tab"][aria-selected="true"] *,
        [data-testid="stButtonGroup"] button[aria-checked="true"] *,
        [data-testid="stButtonGroup"] button[aria-pressed="true"] *,
        [data-testid="stButtonGroup"] button[aria-selected="true"] *,
        [data-testid="stSegmentedControl"] label:has(input:checked) *,
        [data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"] *,
        [data-testid="stSegmentedControl"] [role="tab"][aria-selected="true"] *,
        [data-testid="stSegmentedControl"] button[aria-checked="true"] *,
        [data-testid="stSegmentedControl"] button[aria-pressed="true"] *,
        [data-testid="stSegmentedControl"] button[aria-selected="true"] * {{
            color: #ffffff !important;
        }}

        [data-testid="stButtonGroup"] label:has(input:checked) > div,
        [data-testid="stButtonGroup"] label:has(input:checked) > span,
        [data-testid="stButtonGroup"] label:has(input:checked) [data-baseweb],
        [data-testid="stButtonGroup"] [role="radio"][aria-checked="true"] > div,
        [data-testid="stButtonGroup"] [role="radio"][aria-checked="true"] > span,
        [data-testid="stButtonGroup"] [role="tab"][aria-selected="true"] > div,
        [data-testid="stButtonGroup"] [role="tab"][aria-selected="true"] > span,
        [data-testid="stSegmentedControl"] label:has(input:checked) > div,
        [data-testid="stSegmentedControl"] label:has(input:checked) > span,
        [data-testid="stSegmentedControl"] label:has(input:checked) [data-baseweb],
        [data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"] > div,
        [data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"] > span,
        [data-testid="stSegmentedControl"] [role="tab"][aria-selected="true"] > div,
        [data-testid="stSegmentedControl"] [role="tab"][aria-selected="true"] > span {{
            background: transparent !important;
            color: #ffffff !important;
            border-color: transparent !important;
            box-shadow: none !important;
        }}

        [data-testid="stButtonGroup"] label:has(input:checked):hover,
        [data-testid="stButtonGroup"] [role="radio"][aria-checked="true"]:hover,
        [data-testid="stButtonGroup"] [role="tab"][aria-selected="true"]:hover,
        [data-testid="stSegmentedControl"] label:has(input:checked):hover,
        [data-testid="stSegmentedControl"] [role="radio"][aria-checked="true"]:hover,
        [data-testid="stSegmentedControl"] [role="tab"][aria-selected="true"]:hover {{
            background: linear-gradient(180deg, #12a3a6 0%, #066f76 100%) !important;
            border-color: #04747a !important;
            color: #ffffff !important;
            box-shadow:
                0 4px 14px rgba(6, 133, 133, 0.28),
                0 12px 30px rgba(6, 133, 133, 0.22),
                inset 0 1px 0 rgba(255,255,255,0.26) !important;
            transform: scale(1.04) translateY(-2px) !important;
        }}

        div[data-testid="stButton"] > button {{
            height: 52px;
            width: 100%;
            border-radius: 16px;
            font-size: 14px;
            font-weight: 700;
            transition:
                background 180ms ease,
                border-color 180ms ease,
                box-shadow 180ms ease,
                transform 180ms ease !important;
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
            transition:
                color 160ms ease,
                transform 160ms ease,
                text-decoration-color 160ms ease !important;
        }}

        .forgot-password-link:hover {{
            color: #068585 !important;
            text-decoration: underline !important;
            transform: translateY(-1px);
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
            margin-top: 12px !important;
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
            position: relative !important;
            overflow: hidden !important;
            transform-origin: center !important;
            transition:
                background 180ms ease,
                border-color 180ms ease,
                box-shadow 220ms ease,
                transform 180ms cubic-bezier(0.22, 1, 0.36, 1) !important;
        }}

        div[data-testid="stFormSubmitButton"] > button::before {{
            content: "" !important;
            position: absolute !important;
            inset: 0 auto 0 -70% !important;
            width: 48% !important;
            height: 100% !important;
            background: linear-gradient(
                90deg,
                transparent 0%,
                rgba(255,255,255,0.34) 48%,
                transparent 100%
            ) !important;
            transform: skewX(-18deg) !important;
            transition: left 540ms cubic-bezier(0.22, 1, 0.36, 1) !important;
            pointer-events: none !important;
        }}

        div[data-testid="stFormSubmitButton"] > button:hover {{
            background: linear-gradient(180deg, #12a3a6 0%, #066f76 100%) !important;
            border-color: #04747a !important;
            box-shadow:
                0 2px 6px rgba(6, 133, 133, 0.14),
                0 18px 32px rgba(6, 133, 133, 0.28) !important;
            transform: translateY(-2px) scale(1.012) !important;
        }}

        div[data-testid="stFormSubmitButton"] > button:hover::before {{
            left: 120% !important;
        }}

        div[data-testid="stFormSubmitButton"] > button:active {{
            transform: translateY(0) scale(0.985) !important;
            box-shadow: 0 8px 18px rgba(6, 133, 133, 0.18) !important;
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
            position: fixed !important;
            top: 18px !important;
            right: 18px !important;
            left: auto !important;
            width: auto !important;
            max-width: min(420px, calc(100vw - 36px)) !important;
            z-index: 99999 !important;
            display: flex !important;
            align-items: center !important;
            justify-content: space-between !important;
            gap: 14px !important;
            margin: 0 !important;
            padding: 14px 16px !important;
            background: #DC2626 !important;
            border: none !important;
            border-radius: 12px !important;
            box-shadow:
                0 8px 16px rgba(220, 38, 38, 0.20),
                0 16px 32px rgba(15, 23, 42, 0.14) !important;
            box-sizing: border-box !important;
            transform-origin: top right;
            animation: error-alert-trigger 420ms cubic-bezier(0.22, 1, 0.36, 1) both;
            will-change: transform, opacity;
        }}

        @keyframes error-alert-trigger {{
            0% {{
                opacity: 0;
                transform: translateY(-10px) scale(0.97);
            }}
            100% {{
                opacity: 1;
                transform: translateY(0) scale(1);
            }}
        }}

        .error-alert-title {{
            display: none;
        }}

        .error-alert-content {{
            color: #ffffff !important;
            font-size: 14px;
            font-weight: 700;
            line-height: 1.4;
            margin: 0;
            text-align: left !important;
        }}

        .error-alert-close {{
            flex-shrink: 0;
            width: 22px;
            height: 22px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border: none;
            background: transparent;
            color: #ffffff;
            opacity: 0.85;
            font-size: 18px;
            line-height: 1;
            cursor: pointer;
            padding: 0;
        }}

        .error-alert-close:hover {{
            opacity: 1;
        }}

        div[data-testid="stSpinner"] {{
            margin: 12px 0 0 !important;
        }}

        div[data-testid="stSpinner"] > div {{
            color: #068585 !important;
            font-size: 13px !important;
            font-weight: 600 !important;
        }}

        div[data-testid="stSpinner"] svg {{
            animation: auth-spinner-spin 780ms linear infinite !important;
            color: #068585 !important;
        }}

        @keyframes auth-spinner-spin {{
            100% {{
                transform: rotate(360deg);
            }}
        }}

        @media (prefers-reduced-motion: reduce) {{
            .error-alert,
            .left-panel,
            div[data-testid="column"]:nth-child(2) [data-testid="stVerticalBlockBorderWrapper"],
            div[data-testid="column"]:nth-child(2) [data-baseweb="input"],
            div[data-testid="column"]:nth-child(2) div[data-testid="stButton"] > button:not(:hover),
            [data-baseweb="input"] button,
            [data-baseweb="input"] button svg,
            div[data-testid="stSpinner"] svg {{
                animation: none !important;
                transition: none !important;
                transform: none !important;
                will-change: auto;
            }}
        }}

        div[data-testid="stButton"] {{
            transform-origin: center center !important;
            transition:
                transform 180ms cubic-bezier(0.22, 1, 0.36, 1),
                filter 180ms ease !important;
            will-change: transform;
        }}

        div[data-testid="stButton"]:hover {{
            transform: translateY(-4px) scale(1.025) !important;
            filter: brightness(1.03);
        }}

        div[data-testid="stButton"]:active {{
            transform: translateY(0) scale(0.975) !important;
        }}

        div[data-testid="stButton"]:hover > button {{
            box-shadow:
                0 2px 6px rgba(15, 23, 42, 0.08),
                0 16px 30px rgba(15, 23, 42, 0.14) !important;
        }}

        div[data-testid="stButton"]:hover > button[kind="primary"] {{
            background: linear-gradient(180deg, #12a3a6 0%, #066f76 100%) !important;
            border-color: #04747a !important;
            box-shadow:
                0 2px 6px rgba(6, 133, 133, 0.14),
                0 18px 32px rgba(6, 133, 133, 0.28) !important;
        }}

        div[data-testid="stButton"] > button[kind="tertiary"]:hover,
        div[data-testid="stButton"]:has(> button[kind="tertiary"]):hover {{
            transform: none !important;
            filter: none !important;
            box-shadow: none !important;
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


def render_role_selector(role_options: list[str], selected_role: str) -> str:
    selected_index = role_options.index(selected_role)

    return st.radio(
        "Role",
        role_options,
        index=selected_index,
        key="login_role_selector",
        label_visibility="collapsed",
        horizontal=True,
    )


def show_error(message: str, title: str = "Periksa kembali") -> None:
    safe_message = escape(message.lstrip("*").strip())

    st.markdown(
        f"""
        <div class="error-alert" role="alert" aria-live="polite">
            <div class="error-alert-content">{safe_message}</div>
            <button type="button" class="error-alert-close" aria-label="Tutup"
                    onclick="this.closest('.error-alert').style.display='none';">&times;</button>
        </div>
        """,
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
