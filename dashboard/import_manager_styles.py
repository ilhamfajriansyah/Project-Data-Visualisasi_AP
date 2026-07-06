"""CSS constants for the Import Manager page, relocated out of import_manager.py
to keep that file focused on logic. Content is unchanged from before — this is a
pure code-organization split, not a styling change."""

_PAGE_CSS = """
<style>
/* Pull the workspace surface up to close the default Streamlit gap left
   after the fixed header's spacer (mirrors the same fix used elsewhere)
   — keeps it compact/close to the header. */
body:has(.im-page-marker) div[data-testid="stElementContainer"]:has(.im-manager-surface) {
    margin-top: -85px !important;
}

/* Nudge the pagination row down 10px on this page only. */
body:has(.im-page-marker) div[data-testid="stElementContainer"]:has(.overview-detail-pagination-footer-marker) ~ div[data-testid="stLayoutWrapper"] {
    margin-top: 10px !important;
}

/* ── STEPPER ── */
.stepper-wrap {
    display: flex; align-items: center; gap: 0;
    margin-bottom: 24px; position: relative;
}
.step-item {
    display: flex; flex-direction: column; align-items: center; flex: 1;
    position: relative; z-index: 1;
}
.step-circle {
    width: 36px; height: 36px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; font-weight: 800;
    transition: all 0.3s;
}
.step-circle.done   { background: linear-gradient(135deg,#059669,#10b981); color:#fff; box-shadow:0 4px 12px rgba(16,185,129,0.35); }
.step-circle.active { background: linear-gradient(135deg,#6366f1,#06b6d4); color:#fff; box-shadow:0 4px 12px rgba(99,102,241,0.40); }
.step-circle.idle   { background: rgba(148,163,184,0.18); color:#94a3b8; border:2px solid rgba(148,163,184,0.30); }
.step-label { font-size:10.5px; font-weight:700; margin-top:6px; text-align:center; line-height:1.3; }
.step-label.done   { color:#059669; }
.step-label.active { color:#4f46e5; }
.step-label.idle   { color:#94a3b8; }
.step-line {
    flex: 1; height: 2px; margin-top:-18px; position: relative; z-index: 0;
    border-radius: 999px;
}
.step-line.done { background: linear-gradient(90deg,#059669,#10b981); }
.step-line.idle { background: rgba(148,163,184,0.22); }

/* ── UPLOAD DROP ── */
.lc-dropzone {
    border: 2px dashed rgba(99,102,241,0.30);
    border-radius: 18px;
    background: rgba(255,255,255,0.62);
    backdrop-filter: blur(12px);
    padding: 40px 24px;
    text-align: center;
    transition: all 0.2s;
}
.lc-dropzone:hover { border-color: rgba(99,102,241,0.55); background: rgba(99,102,241,0.03); }
.lc-drop-icon { font-size: 40px; margin-bottom: 10px; }
.lc-drop-title { font-size: 15px; font-weight: 700; color: #1e293b; margin-bottom: 4px; }
.lc-drop-sub   { font-size: 11.5px; color: #94a3b8; margin-bottom: 16px; line-height: 1.6; }

/* ── FILE ITEM ── */
.lc-file-item {
    display: flex; align-items: center; gap: 14px;
    background: rgba(255,255,255,0.68);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.92);
    border-radius: 14px;
    padding: 14px 16px;
    margin-top: 10px;
    box-shadow: 0 3px 12px rgba(99,102,241,0.06);
}
.lc-file-icon {
    width: 40px; height: 40px; border-radius: 10px;
    background: rgba(16,185,129,0.12);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
}
.lc-file-name { font-size: 13px; font-weight: 700; color: #1e293b; }
.lc-file-sub  { font-size: 11px; color: #94a3b8; margin-top: 2px; }

/* ── PREVIEW CARD ── */
.preview-kpi-row { display: flex; gap: 12px; margin-bottom: 16px; flex-wrap: wrap; }
.preview-kpi {
    flex: 1; min-width: 120px;
    background: rgba(255,255,255,0.68);
    border: 1px solid rgba(255,255,255,0.92);
    border-radius: 14px; padding: 14px 16px;
    box-shadow: 0 3px 12px rgba(99,102,241,0.05);
    text-align: center;
}
.preview-kpi-label { font-size:10px; font-weight:700; color:#94a3b8; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:5px; }
.preview-kpi-val   { font-size:20px; font-weight:800; color:#1e293b; }
.preview-kpi-val.err { color:#dc2626; }

/* ── PERIOD BANNER ── */
.period-banner {
    background: linear-gradient(135deg, rgba(99,102,241,0.09), rgba(6,182,212,0.07));
    border: 1px solid rgba(99,102,241,0.18);
    border-radius: 14px; padding: 14px 18px;
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 18px; flex-wrap: wrap; gap: 8px;
}
.period-title { font-size:13px; font-weight:800; color:#4f46e5; }
.period-sub   { font-size:11.5px; color:#64748b; margin-top:2px; }
.period-badge {
    background: rgba(245,158,11,0.12); color:#d97706;
    border:1px solid rgba(245,158,11,0.26);
    padding:5px 14px; border-radius:999px;
    font-size:11.5px; font-weight:700;
}

/* ── KPI CARDS (Admin) ── */
.adm-kpi {
    background: rgba(255,255,255,0.62); backdrop-filter: blur(22px);
    border: 1px solid rgba(255,255,255,0.94); border-radius: 18px;
    padding: 18px 16px; position:relative; overflow:hidden;
    box-shadow: 0 6px 24px rgba(99,102,241,0.07), inset 0 1px 0 rgba(255,255,255,1);
    transition: transform .2s;
}
.adm-kpi:hover { transform: translateY(-2px); }
.adm-kpi::before {
    content:""; position:absolute; left:16px; right:16px; top:0; height:3px;
    border-radius:0 0 999px 999px;
    background: var(--accent, linear-gradient(135deg,#6366f1,#06b6d4)); opacity:.9;
}
.adm-kpi-label { font-size:9.5px; font-weight:800; color:#94a3b8; text-transform:uppercase; letter-spacing:.6px; margin-bottom:6px; }
.adm-kpi-val   { font-size:26px; font-weight:800; background:var(--accent,linear-gradient(135deg,#4f46e5,#0891b2)); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; margin-bottom:4px; }
.adm-kpi-sub   { font-size:10.5px; color:#64748b; font-weight:600; }

/* ── REMINDER BANNER ── */
.reminder-banner {
    background: linear-gradient(135deg,rgba(245,158,11,0.09),rgba(251,146,60,0.07));
    border:1px solid rgba(245,158,11,0.26); border-radius:14px;
    padding:14px 18px; margin-bottom:14px;
    display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;
}
.reminder-txt { font-size:12.5px; color:#92400e; font-weight:500; line-height:1.5; }
.reminder-txt strong { color:#b45309; font-weight:800; }

/* ── TABLE ── */
.im-table { width:100%; border-collapse:collapse; }
.im-table thead tr { background: rgba(99, 102, 241, 0.05); border-bottom: none; }
.im-table th { padding: 11px 13px; text-align: left; font-size: 11px; font-weight: 700; color: #4F46E5; text-transform: uppercase; letter-spacing: .5px; white-space: nowrap; }
.im-table td { padding:12px 13px; font-size:12.5px; color:#334155; border-bottom:1px solid rgba(99,102,241,0.05); vertical-align:middle; }
.im-table tbody tr:hover { background:rgba(99,102,241,0.025); }
.im-table tbody tr:last-child td { border-bottom:none; }

/* ── STATUS BADGES ── */
.b-approve  { background:rgba(16,185,129,0.12); color:#059669; border:1px solid rgba(16,185,129,0.25); padding:3px 11px; border-radius:999px; font-size:11px; font-weight:700; }
.b-rejected { background:rgba(239,68,68,0.10);  color:#dc2626; border:1px solid rgba(239,68,68,0.22); padding:3px 11px; border-radius:999px; font-size:11px; font-weight:700; }
.b-pending  { background:rgba(245,158,11,0.12); color:#d97706; border:1px solid rgba(245,158,11,0.25); padding:3px 11px; border-radius:999px; font-size:11px; font-weight:700; }
.b-success  { background:rgba(16,185,129,0.12); color:#059669; border:1px solid rgba(16,185,129,0.25); padding:3px 11px; border-radius:999px; font-size:11px; font-weight:700; }
.b-failed   { background:rgba(239,68,68,0.10);  color:#dc2626; border:1px solid rgba(239,68,68,0.22); padding:3px 11px; border-radius:999px; font-size:11px; font-weight:700; }

/* ── ADMIN CONTROL CARDS ── */
.admin-ctrl {
    background:rgba(255,255,255,0.56); backdrop-filter:blur(20px);
    border:1px solid rgba(255,255,255,0.90); border-radius:16px;
    padding:16px 18px; margin-bottom:10px;
    box-shadow:0 4px 16px rgba(99,102,241,0.06);
}
.admin-ctrl-title { font-size:12.5px; font-weight:800; color:#1e293b; margin-bottom:3px; }
.admin-ctrl-sub   { font-size:11px; color:#94a3b8; margin-bottom:10px; }

/* ── SCHEME MAPPING ── */
.scheme-row {
    display:flex; align-items:center; gap:10px;
    background:rgba(255,255,255,0.56); border:1px solid rgba(255,255,255,0.88);
    border-radius:12px; padding:10px 14px; margin-bottom:8px;
    box-shadow:0 2px 8px rgba(99,102,241,0.04);
}
.scheme-col { flex:1; font-size:11.5px; font-weight:600; color:#475569; }
.scheme-arrow { color:#94a3b8; font-size:14px; flex-shrink:0; }
.scheme-master { flex:1; font-size:11.5px; color:#94a3b8; font-weight:500; }

.im-footer { display:flex; align-items:center; justify-content:space-between; padding:12px 16px; border-top:1px solid rgba(99,102,241,0.07); }
.im-footer-info { font-size:11.5px; color:#94a3b8; font-weight:500; }
</style>
"""

_REFINED_IMPORT_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800;900&display=swap');

.stApp, .stApp * {
    font-family: 'Inter', sans-serif !important;
}
.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
.stApp [class*="-title"], .stApp [class*="-header"], .stApp [class*="title-"] {
    font-family: 'Montserrat', sans-serif !important;
}
.im-manager-surface {
    margin-top: -8px !important;
}
.im-page-head {
    display: grid;
    grid-template-columns: minmax(220px, 1.25fr) minmax(260px, 0.95fr) minmax(210px, 0.7fr);
    gap: 18px;
    align-items: center;
    margin-bottom: 10px;
}
.im-page-title {
    font-size: 19px;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
}
.im-page-subtitle {
    margin-top: 2px;
    font-size: 11px;
    color: #64748b;
    font-weight: 500;
}
.im-userbar {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 12px;
}
.im-bell {
    width: 34px;
    height: 34px;
    border-radius: 50%;
    background: rgba(255,255,255,0.62);
    border: 1px solid rgba(255,255,255,0.94);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #4f46e5;
    font-size: 15px;
    font-weight: 900;
    box-shadow: 0 4px 18px rgba(99,102,241,0.08);
}
.im-user {
    display: flex;
    align-items: center;
    gap: 9px;
    min-width: 0;
}
.im-avatar {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 13px;
    font-weight: 800;
    background: linear-gradient(135deg,#6366f1,#06b6d4);
    box-shadow: 0 5px 16px rgba(99,102,241,0.28);
}
.im-user-name {
    font-size: 12.5px;
    font-weight: 800;
    color: #1e293b;
    line-height: 1.2;
}
.im-user-mail {
    font-size: 10.5px;
    color: #94a3b8;
    max-width: 170px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.im-workspace {
    display: grid;
    grid-template-columns: minmax(0, 1.72fr) minmax(300px, 0.78fr);
    gap: 22px;
    align-items: start;
}
.im-panel {
    background: rgba(255,255,255,0.56);
    backdrop-filter: blur(26px);
    -webkit-backdrop-filter: blur(26px);
    border: 1px solid rgba(255,255,255,0.90);
    border-radius: 18px;
    box-shadow:
        0 8px 32px rgba(99,102,241,0.07),
        0 2px 8px rgba(0,0,0,0.025),
        inset 0 1px 0 rgba(255,255,255,1);
}
.im-upload-shell {
    padding: 18px 18px 16px;
}
.im-upload-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 12px;
}
.im-section-title {
    font-size: 13px;
    font-weight: 800;
    color: #1e293b;
}
.im-section-sub {
    margin-top: 3px;
    font-size: 11px;
    color: #94a3b8;
}
.im-period-chip {
    flex-shrink: 0;
    padding: 6px 12px;
    border-radius: 999px;
    background: linear-gradient(135deg,rgba(99,102,241,0.13),rgba(6,182,212,0.10));
    border: 1px solid rgba(99,102,241,0.20);
    color: #4f46e5;
    font-size: 11px;
    font-weight: 800;
}
.im-top-refresh-btn {
    background: #eff6ff !important;
    border: 1px solid rgba(37, 99, 235, 0.18) !important;
    border-radius: 50% !important;
    width: 32px !important;
    height: 32px !important;
    min-width: 32px !important;
    min-height: 32px !important;
    max-width: 32px !important;
    max-height: 32px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.05) !important;
    margin: 0 !important;
    color: #2563eb !important;
    font-size: 15px !important;
    font-weight: 800 !important;
    cursor: pointer !important;
    line-height: 1 !important;
    outline: none !important;
}
.im-top-refresh-btn:hover {
    background: #dbeafe !important;
    border-color: rgba(37, 99, 235, 0.4) !important;
    transform: rotate(30deg) !important;
}

/* Custom Drag & Drop visual styles */
.im-dropzone-wrapper {
    position: relative;
    width: 100%;
    margin-bottom: 14px;
}
.im-dropzone-visual {
    border: 2px dashed rgba(99, 102, 241, 0.25);
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.72), rgba(245, 243, 255, 0.45));
    padding: 40px 24px;
    text-align: center;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    box-shadow: 0 8px 32px rgba(99, 102, 241, 0.04);
    height: 254px !important;
    box-sizing: border-box !important;
}
.im-dropzone-wrapper:hover .im-dropzone-visual {
    border-color: rgba(99, 102, 241, 0.6);
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.8), rgba(245, 243, 255, 0.6));
    box-shadow: 0 12px 40px rgba(99, 102, 241, 0.08);
}
.im-dropzone-icon-box {
    width: 64px;
    height: 64px;
    border-radius: 18px;
    background: #f3f0ff;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.08);
}
.im-dropzone-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #a78bfa;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(167, 139, 250, 0.35);
    font-size: 18px;
    font-weight: 700;
}
.im-dropzone-title {
    font-size: 16.5px;
    font-weight: 800;
    color: #1e293b;
    margin-bottom: 4px;
}
.im-dropzone-subtitle {
    font-size: 12.5px;
    color: #64748b;
    margin-bottom: 22px;
}
.im-dropzone-browse {
    color: #6366f1;
    font-weight: 800;
    text-decoration: none;
    cursor: pointer;
}
.im-dropzone-browse:hover {
    text-decoration: underline;
}
.im-dropzone-badges {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}
.im-dropzone-badge {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    background: #f5f3ff;
    border: 1px solid rgba(99, 102, 241, 0.18);
    border-radius: 999px;
    color: #6366f1;
    font-size: 10.5px;
    font-weight: 700;
}
.badge-icon {
    stroke: #6366f1;
    stroke-width: 2.2;
}

/* Transparent Sibling and Class Overlay Uploader */
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) {
    position: relative !important;
    margin-top: -268px !important;
    height: 254px !important;
    z-index: 1000 !important;
    cursor: pointer !important;
}
.im-refined-uploader {
    opacity: 0 !important;
    cursor: pointer !important;
    width: 100% !important;
    height: 100% !important;
}
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) *,
.im-refined-uploader * {
    cursor: pointer !important;
    width: 100% !important;
    height: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
}
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploadDropzone"],
.im-refined-uploader [data-testid="stFileUploadDropzone"],
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzone"],
.im-refined-uploader [data-testid="stFileUploaderDropzone"] {
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    background: transparent !important;
}

/* The decorative "Browse files" button/icon/instructions get blown up to
   100% x 100% by the rule above, which makes them sit on top of (and
   intercept all pointer/drag events meant for) the real, invisible
   <input type="file">. That's why clicking worked (the button's own
   click handler opens the file dialog) but dragging a file onto the
   zone did not (the drop landed on the button, not the input). Make
   the decorative layer click/drop-through so the input underneath is
   what actually receives both clicks and native drag-and-drop. */
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzone"] > span,
.im-refined-uploader [data-testid="stFileUploaderDropzone"] > span,
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzone"] > span *,
.im-refined-uploader [data-testid="stFileUploaderDropzone"] > span *,
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzoneInstructions"],
.im-refined-uploader [data-testid="stFileUploaderDropzoneInstructions"],
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzoneInstructions"] *,
.im-refined-uploader [data-testid="stFileUploaderDropzoneInstructions"] * {
    pointer-events: none !important;
}
/* The dropzone <section> lays out its <input> and the decorative <span>
   as side-by-side flex children (each ~50% width), not stacked/overlapping.
   Forcing width:100% above doesn't escape that — the input still only
   covers the LEFT half. Anywhere on the right half, pointer/drag events
   fall through the (pointer-events:none) span straight past the real
   uploader to our decorative background card behind it, which has no
   upload handlers at all. Taking the input out of flow with absolute
   positioning makes it cover the *entire* dropzone regardless of the
   sibling's flex sizing. */
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzone"],
.im-refined-uploader [data-testid="stFileUploaderDropzone"] {
    position: relative !important;
}
div:has(.im-dropzone-wrapper) + div:has([data-testid="stFileUploader"]) [data-testid="stFileUploaderDropzoneInput"],
.im-refined-uploader [data-testid="stFileUploaderDropzoneInput"] {
    pointer-events: auto !important;
    position: absolute !important;
    inset: 0 !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    z-index: 1 !important;
}

/* Pure-CSS equivalent of ".im-refined-uploader" above. That class is added
   by JS (a MutationObserver in a components.html iframe) which needs a
   moment to load/run — navigate here quickly and the raw Streamlit uploader
   (visible "Drag and drop"/"Browse files") flashes on top of the decorative
   dropzone before the JS hides it. Streamlit auto-applies "st-key-<key>" as
   a class on the widget's own container, so this targets the exact same
   widget with no JS dependency and no flash. */
[class*="st-key-im_uploader_refined_"] {
    opacity: 0 !important;
    position: relative !important;
    margin-top: -268px !important;
    height: 254px !important;
    z-index: 1000 !important;
    cursor: pointer !important;
}
[class*="st-key-im_uploader_refined_"] * {
    cursor: pointer !important;
    width: 100% !important;
    height: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    box-sizing: border-box !important;
}
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploadDropzone"],
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploaderDropzone"] {
    padding: 0 !important;
    margin: 0 !important;
    border: none !important;
    background: transparent !important;
    position: relative !important;
}
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploaderDropzone"] > span,
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploaderDropzone"] > span *,
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploaderDropzoneInstructions"],
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploaderDropzoneInstructions"] * {
    pointer-events: none !important;
}
[class*="st-key-im_uploader_refined_"] [data-testid="stFileUploaderDropzoneInput"] {
    pointer-events: auto !important;
    position: absolute !important;
    inset: 0 !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    z-index: 1 !important;
}


/* Success State styling */
.im-success-visual {
    border: 1.5px solid rgba(99, 102, 241, 0.20) !important;
    border-radius: 24px !important;
    background: rgba(255, 255, 255, 0.45) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    padding: 30px 24px 24px !important;
    text-align: center !important;
    box-shadow: 0 8px 32px 0 rgba(99, 102, 241, 0.05), inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    margin-bottom: 14px !important;
    animation: cardPopIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
.im-success-icon-box {
    width: 68px !important;
    height: 68px !important;
    border-radius: 50% !important;
    background: rgba(99, 102, 241, 0.08) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin-bottom: 14px !important;
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.12) !important;
    border: 1px solid rgba(255, 255, 255, 0.5) !important;
    backdrop-filter: blur(4px) !important;
}
.im-success-icon {
    width: 44px !important;
    height: 44px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    color: #ffffff !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35) !important;
    font-size: 20px !important;
    font-weight: bold !important;
}
.im-success-title {
    font-size: 22px !important;
    font-weight: 850 !important;
    background: linear-gradient(135deg, #6366F1, #8B5CF6) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
    margin-bottom: 4px !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
    letter-spacing: -0.5px !important;
}
.im-success-subtitle {
    font-size: 12px !important;
    color: #64748b !important;
    margin-bottom: 20px !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* Progress bar container and animations */
.im-progress-bar-container {
    width: 100% !important;
    max-width: 440px !important;
    height: 6px !important;
    background: rgba(226, 232, 240, 0.5) !important;
    border-radius: 999px !important;
    overflow: hidden !important;
    margin-bottom: 20px !important;
    border: 1px solid rgba(255, 255, 255, 0.4) !important;
}
@keyframes progressBarWidth {
    0% { width: 0%; }
    100% { width: 100%; }
}
@keyframes progressBarColor {
    0% { background-color: #2563eb; } /* Blue */
    45% { background-color: #2563eb; }
    75% { background-color: #f97316; } /* Orange */
    100% { background-color: #10b981; } /* Green */
}
.im-progress-bar-fill {
    height: 100% !important;
    border-radius: 999px !important;
    width: 0%;
    background-color: #2563eb;
    animation-name: progressBarWidth, progressBarColor !important;
    animation-duration: 2.5s, 2.5s !important;
    animation-timing-function: cubic-bezier(0.4, 0, 0.2, 1), cubic-bezier(0.4, 0, 0.2, 1) !important;
    animation-fill-mode: forwards, forwards !important;
}

/* Success details and buttons slide up/fade in */
@keyframes successDetailsFadeIn {
    0% {
        opacity: 0;
        transform: translateY(16px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}
@keyframes cardPopIn {
    0% {
        opacity: 0;
        transform: scale(0.96) translateY(12px);
    }
    100% {
        opacity: 1;
        transform: scale(1) translateY(0);
    }
}
@keyframes failureDetailsSlideUp {
    0% {
        opacity: 0;
        transform: translateY(12px);
    }
    100% {
        opacity: 1;
        transform: translateY(0);
    }
}
.im-success-details {
    width: 100% !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    animation: successDetailsFadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1) 2s both !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

/* Stats Cards container and cards */
.im-stats-row {
    display: flex !important;
    justify-content: center !important;
    gap: 12px !important;
    width: 100% !important;
    margin-bottom: 20px !important;
    flex-wrap: wrap !important;
}
.im-stat-card {
    flex: 1 !important;
    min-width: 90px !important;
    border-radius: 14px !important;
    padding: 12px 8px !important;
    text-align: center !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.02), inset 0 1px 0 rgba(255, 255, 255, 0.5) !important;
    transition: transform 0.2s, box-shadow 0.2s, background 0.2s !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
.im-stat-card:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 16px rgba(99, 102, 241, 0.06) !important;
}
/* Purple Stat Card: Records */
.stat-records {
    background: rgba(99, 102, 241, 0.08) !important;
    border: 1.5px solid rgba(99, 102, 241, 0.30) !important;
}
.stat-records .stat-value {
    color: #6366f1 !important;
    background: linear-gradient(135deg, #6366F1, #4F46E5) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}
/* Green Stat Card: Valid */
.stat-valid {
    background: rgba(16, 185, 129, 0.08) !important;
    border: 1.5px solid rgba(16, 185, 129, 0.30) !important;
}
.stat-valid .stat-value {
    color: #10b981 !important;
    background: linear-gradient(135deg, #10B981, #059669) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}
/* Yellow Stat Card: Warnings */
.stat-warnings {
    background: rgba(245, 158, 11, 0.08) !important;
    border: 1.5px solid rgba(245, 158, 11, 0.30) !important;
}
.stat-warnings .stat-value {
    color: #d97706 !important;
    background: linear-gradient(135deg, #F59E0B, #D97706) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}
/* Teal Stat Card: Score */
.stat-score {
    background: rgba(20, 184, 166, 0.08) !important;
    border: 1.5px solid rgba(20, 184, 166, 0.30) !important;
}
.stat-score .stat-value {
    color: #14b8a6 !important;
    background: linear-gradient(135deg, #14B8A6, #0D9488) !important;
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
    background-clip: text !important;
}

.stat-value {
    font-size: 22px !important;
    font-weight: 850 !important;
    margin-bottom: 2px !important;
    line-height: 1.2 !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
.stat-label {
    font-size: 11px !important;
    color: #64748b !important;
    font-weight: 600 !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}

div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] {
    max-width: 380px !important;
    margin: 16px 0 0 0 !important;
    width: 100% !important;
}
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stButton"] button {
    width: 100% !important;
    height: 42px !important;
    border-radius: 24px !important; /* Pill style matching mockup */
    font-size: 13.5px !important;
    font-weight: 700 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
    font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
}
/* Style for Col 1 button (Upload Another) */
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button,
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:first-child button {
    background: #ffffff !important;
    color: #1e293b !important;
    border: 1.5px solid #cbd5e1 !important;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05) !important;
}
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button::before,
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:first-child button::before {
    content: "";
    display: inline-block;
    width: 14px;
    height: 14px;
    margin-right: 8px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2364748b' stroke-width='2.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/%3E%3Cpolyline points='17 8 12 3 7 8'/%3E%3Cline x1='12' y1='3' x2='12' y2='15'/%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    flex-shrink: 0;
}
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="column"]:first-child button:hover,
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:first-child button:hover {
    background: #f8fafc !important;
    border-color: #94a3b8 !important;
    color: #0f172a !important;
    transform: translateY(-1px) !important;
}
/* Style for Col 2 button (View Data) */
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button,
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child button {
    background: #2563eb !important; /* Solid blue background */
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2) !important;
}
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button::before,
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child button::before {
    content: "";
    display: inline-block;
    width: 14px;
    height: 14px;
    margin-right: 8px;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%23ffffff' stroke-width='2.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='3' width='18' height='18' rx='2'/%3E%3Cline x1='3' y1='9' x2='21' y2='9'/%3E%3Cline x1='9' y1='21' x2='9' y2='9'/%3E%3C/svg%3E");
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    flex-shrink: 0;
}
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="column"]:last-child button:hover,
div:has(> .im-success-visual) ~ div [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:last-child button:hover {
    background: #1d4ed8 !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.35) !important;
    transform: translateY(-1px) !important;
}

/* Failure State styling */
.im-failure-visual {
    border: 2px solid rgba(239, 68, 68, 0.2);
    border-radius: 24px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.72), rgba(254, 242, 242, 0.45));
    padding: 40px 24px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(239, 68, 68, 0.04);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin-bottom: 14px;
    animation: cardPopIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}
.im-failure-icon-box {
    width: 64px;
    height: 64px;
    border-radius: 18px;
    background: #fef2f2;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    box-shadow: 0 8px 24px rgba(239, 68, 68, 0.08);
}
.im-failure-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: #ef4444;
    color: #ffffff;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.35);
    font-size: 20px;
    font-weight: bold;
}
.im-failure-title {
    font-size: 19px;
    font-weight: 850;
    color: #dc2626;
    margin-bottom: 4px;
}
.im-failure-subtitle {
    font-size: 12.5px;
    color: #64748b;
    margin-bottom: 24px;
}
.im-failure-details {
    width: 100%;
    max-width: 460px;
    background: rgba(255, 255, 255, 0.68);
    border: 1px solid rgba(239, 68, 68, 0.15);
    border-radius: 16px;
    padding: 16px;
    margin-bottom: 24px;
    text-align: left;
    animation: failureDetailsSlideUp 0.5s cubic-bezier(0.16, 1, 0.3, 1) 0.15s both;
}
.im-failure-detail-item {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 8px;
    font-size: 12.5px;
    color: #475569;
}
.im-failure-detail-item:last-child {
    margin-bottom: 0;
}

.im-side-stack {
    display: flex;
    flex-direction: column;
    gap: 12px;
}
.im-side-control {
    padding: 14px 14px 13px;
}
.im-side-control-grid {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(130px, 1fr);
    gap: 10px;
    align-items: end;
}
.im-control-title {
    font-size: 12px;
    color: #64748b;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
}
.im-map-card {
    padding: 0;
    overflow: hidden;
}
.im-card-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 15px 16px 11px;
    border-bottom: 1px solid rgba(99,102,241,0.08);
}
.im-auto-badge {
    padding: 5px 10px;
    border-radius: 999px;
    color: #047857;
    background: rgba(16,185,129,0.13);
    border: 1px solid rgba(16,185,129,0.20);
    font-size: 10px;
    font-weight: 850;
    letter-spacing: 0.4px;
    white-space: nowrap;
    box-shadow: none;
}
.im-map-body {
    padding: 12px 16px 15px;
    max-height: 238px;
    overflow-y: auto;
}
.im-map-row {
    display: block;
    margin-bottom: 9px;
}
.im-map-box {
    min-height: 66px;
    border-radius: 12px;
    background: rgba(255,255,255,0.68);
    border: 1px solid rgba(255,255,255,0.92);
    box-shadow: 0 2px 10px rgba(99,102,241,0.05);
    padding: 10px 12px;
    border-left: 5px solid rgba(99,102,241,0.62);
}
.im-map-label {
    font-size: 10px;
    font-weight: 800;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin-bottom: 4px;
}
.im-map-value {
    font-size: 12px;
    font-weight: 800;
    color: #1e293b;
    line-height: 1.35;
}
.im-map-arrow {
    color: #64748b;
    font-size: 15px;
    font-weight: 900;
    line-height: 1;
    margin: 2px 0;
}
.im-execute-wrap {
    padding: 0 16px 15px;
}
.im-ketentuan-card {
    padding: 0;
    overflow: hidden;
}
.im-ketentuan-head {
    padding: 15px 16px 11px;
    border-bottom: 1px solid rgba(99,102,241,0.08);
}
.im-ketentuan-body {
    padding: 14px 16px 18px;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.im-ketentuan-item {
    display: flex;
    flex-direction: column;
    gap: 0;
    font-size: 12px;
    font-weight: 600;
    color: #334155;
    line-height: 1.45;
    width: 100%;
    transition: all 0.2s ease;
}
.im-ketentuan-row {
    display: flex;
    align-items: center;
    gap: 10px;
    width: 100%;
}
.im-ketentuan-text {
    font-weight: 600;
}
.im-ketentuan-neutral {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: transparent;
    border: 2px solid #cbd5e1;
    margin-top: 1px;
    box-sizing: border-box;
}
.im-ketentuan-check {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #ffffff !important;
    font-size: 11px;
    font-weight: 900;
    background: #10b981 !important; /* Solid emerald green */
    border: 1px solid #10b981 !important;
    margin-top: 1px;
}
.im-ketentuan-fail {
    flex-shrink: 0;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: #ffffff !important;
    font-size: 10px;
    font-weight: 900;
    background: #ef4444 !important; /* Solid red */
    border: 1px solid #ef4444 !important;
    margin-top: 1px;
}
.im-ketentuan-item.is-neutral .im-ketentuan-text {
    color: #64748b;
    font-weight: 500;
}
.im-ketentuan-item.is-pass .im-ketentuan-text {
    color: #1e293b;
    font-weight: 600;
}
.im-ketentuan-item.is-fail .im-ketentuan-text {
    color: #991b1b;
    font-weight: 600;
}
.im-ketentuan-item.is-fail {
    background: rgba(239, 68, 68, 0.05) !important;
    border: 1px solid rgba(239, 68, 68, 0.12) !important;
    border-radius: 12px;
    padding: 10px 12px !important;
    margin-bottom: 2px;
    box-shadow: 0 2px 8px rgba(239, 68, 68, 0.04);
}
.im-ketentuan-warning-box {
    background: #fef2f2;
    border: 1px solid #fca5a5;
    border-radius: 8px;
    padding: 8px 12px;
    margin-top: 8px;
    margin-left: 30px; /* Aligns under text, offset by icon width (20px) + gap (10px) */
    font-size: 11px;
    color: #991b1b;
    font-weight: 500;
    line-height: 1.45;
}
.im-ketentuan-warning-list {
    margin: 0;
    padding-left: 16px;
    list-style: disc;
}
.im-ketentuan-warning-list li {
    margin: 2px 0;
}
.im-ketentuan-warning-list li::marker {
    color: #dc2626;
}
.im-info-banner {
    margin-top: -25px;
    padding: 12px 14px;
    border-radius: 12px;
    background: rgba(99,102,241,0.08);
    border: 1px solid rgba(99,102,241,0.18);
    color: #4338ca;
    font-size: 11.5px;
    font-weight: 650;
    line-height: 1.5;
}
.im-history {
    margin-top: 1px;
    padding: 0;
    overflow: hidden;
}
.im-history-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 20px 24px 16px;
    border-bottom: 1px solid rgba(99,102,241,0.08);
}
.im-history-head-left .im-section-title {
    font-size: 15px;
    font-weight: 850;
}
.im-history-head-left .im-section-sub {
    margin-top: 2px;
    font-size: 11.5px;
}
.im-history-actions {
    display: flex;
    align-items: center;
    gap: 10px;
}
.im-btn-refresh, .im-btn-export {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 10px;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    border: none;
}
.im-btn-refresh, .im-btn-export {
    background: rgba(255,255,255,0.72);
    border: 1px solid rgba(99,102,241,0.15);
    color: #4f46e5;
}
.im-btn-refresh:hover {
    background: #f5f3ff;
    border-color: rgba(99,102,241,0.3);
    transform: none;
    box-shadow: none;
}
.im-btn-export.btn-clear-trash {
    color: #ef4444 !important;
    border-color: rgba(239, 68, 68, 0.20) !important;
}
.im-btn-export.btn-clear-trash:hover {
    background: #fef2f2 !important;
    border-color: rgba(239, 68, 68, 0.40) !important;
}
/* History Table Row Design */
.im-hist-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
}
.im-hist-table thead tr {
    background: rgba(99, 102, 241, 0.05);
    border-radius: 10px;
    overflow: hidden;
}
.im-hist-table th {
    padding: 11px 14px;
    background: transparent;
    border: none;
    color: #4F46E5;
    font-size: 11px;
    font-weight: 700;
    text-align: left;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
}
.im-hist-table th:first-child {
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
}
.im-hist-table th:last-child {
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
}
.im-hist-table td {
    padding: 16px 16px;
    font-size: 12.5px;
    color: #334155;
    border-bottom: 1px solid #f8fafc;
    vertical-align: middle;
}
.im-hist-table tbody tr {
    transition: background 0.15s;
}
.im-hist-table tbody tr:hover {
    background: rgba(99,102,241,0.02);
}
.im-hist-table tbody tr:last-child td {
    border-bottom: none;
}
/* Period cell with colored dot */
.im-period-cell {
    display: flex;
    align-items: center;
    gap: 10px;
}
.im-period-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}
.im-period-dot.dot-success { background: #10b981; }
.im-period-dot.dot-warning { background: #f59e0b; }
.im-period-dot.dot-failed  { background: #ef4444; }
.im-period-dot.dot-deleted { background: #64748b; }
.im-period-name {
    font-size: 13px;
    font-weight: 800;
    color: #1e293b;
}
/* Upload date with sub-time */
.im-date-cell {
    line-height: 1.3;
}
.im-date-main {
    font-size: 13px;
    font-weight: 700;
    color: #1e293b;
}
.im-date-time {
    font-size: 10.5px;
    color: #94a3b8;
    font-weight: 500;
}
/* Uploader cell with avatar */
.im-uploader-cell {
    display: flex;
    align-items: center;
    gap: 10px;
}
.im-uploader-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
    font-size: 11px;
    font-weight: 800;
    flex-shrink: 0;
    box-shadow: 0 3px 8px rgba(0,0,0,0.12);
}
.im-uploader-name {
    font-size: 12.5px;
    font-weight: 700;
    color: #1e293b;
    line-height: 1.2;
}
.im-uploader-role {
    font-size: 10.5px;
    color: #94a3b8;
    font-weight: 500;
}
/* Records cell */
.im-records-val {
    font-size: 16px;
    font-weight: 850;
    color: #1e293b;
    line-height: 1.2;
}
.im-records-sub {
    font-size: 10px;
    color: #94a3b8;
    font-weight: 600;
    text-transform: lowercase;
}
/* Tenants link */
.im-tenants-link {
    font-size: 13px;
    font-weight: 700;
    color: #6366f1;
    cursor: pointer;
}
.im-tenants-link:hover {
    text-decoration: underline;
}
/* File size */
.im-filesize {
    font-size: 12.5px;
    color: #64748b;
    font-weight: 600;
}
/* RS Total */
.im-rs-total {
    font-size: 12.5px;
    font-weight: 700;
    color: #1e293b;
}
.im-rs-empty {
    font-size: 12.5px;
    color: #cbd5e1;
    font-weight: 500;
}
/* Status badges with dot */
.im-status-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 11.5px;
    font-weight: 700;
    white-space: nowrap;
}
.im-status-badge .status-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
}
.im-status-success {
    background: rgba(16,185,129,0.10);
    color: #059669;
    border: 1px solid rgba(16,185,129,0.20);
}
.im-status-success .status-dot { background: #10b981; }
.im-status-warning {
    background: rgba(245,158,11,0.10);
    color: #d97706;
    border: 1px solid rgba(245,158,11,0.20);
}
.im-status-warning .status-dot { background: #f59e0b; }
.im-status-failed {
    background: rgba(239,68,68,0.08);
    color: #dc2626;
    border: 1px solid rgba(239,68,68,0.18);
}
.im-status-failed .status-dot { background: #ef4444; }
.im-status-deleted {
    background: rgba(100, 116, 139, 0.10);
    color: #475569;
    border: 1px solid rgba(100, 116, 139, 0.20);
}
.im-status-deleted .status-dot { background: #64748b; }
/* Action buttons */
.im-action-btns {
    display: flex;
    align-items: center;
    gap: 6px;
}
.im-action-btn {
    width: 30px;
    height: 30px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid rgba(99,102,241,0.15);
    background: #fff;
    color: #6366F1;
    cursor: pointer;
    transition: all 0.15s;
    font-size: 13px;
}
.im-action-btn svg {
    width: 16px;
    height: 16px;
    stroke: currentColor;
}
.im-action-btn:hover {
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    color: #fff;
    border-color: transparent;
}
.im-action-btn.btn-delete:hover {
    background: #fef2f2;
    color: #ef4444;
    border-color: rgba(239,68,68,0.2);
}
/* Reset native <button> appearance for action + header buttons */
button.im-action-btn {
    appearance: none;
    -webkit-appearance: none;
    padding: 0;
    outline: none;
    box-sizing: border-box;
    line-height: 1;
}
button.im-btn-refresh,
button.im-btn-export {
    appearance: none;
    -webkit-appearance: none;
    outline: none;
    font-family: inherit;
}
/* JS-action bridge input — offscreen (not display:none) so React events fire normally */
[data-testid="stElementContainer"]:has(input[placeholder="__im_action_trigger__"]) {
    position: fixed !important;
    top: -9999px !important;
    left: -9999px !important;
    width: 1px !important;
    height: 1px !important;
    overflow: hidden !important;
    opacity: 0 !important;
    pointer-events: none !important;
    z-index: -1 !important;
}
/* Pagination */
.im-pagination-wrap {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 24px;
    border-top: 1px solid #f1f5f9;
}
.im-pagination-info {
    font-size: 12px;
    color: #94a3b8;
    font-weight: 500;
}
.im-pagination-btns {
    display: flex;
    align-items: center;
    gap: 4px;
}
.im-pg-btn {
    padding: 6px 12px;
    border-radius: 8px;
    font-size: 12px;
    font-weight: 600;
    border: 1px solid #e2e8f0;
    background: #fff;
    color: #64748b;
    cursor: pointer;
    transition: all 0.15s;
}
.im-pg-btn:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
}
.im-pg-btn.active {
    background: #fff;
    color: #1e293b;
    border-color: #6366f1;
    box-shadow: 0 0 10px rgba(99,102,241,0.28);
}
.im-pg-btn.active:hover {
    background: #fff;
    color: #1e293b;
    border-color: #6366f1;
}
.im-pg-btn.disabled {
    opacity: 0.4;
    cursor: not-allowed;
}
.im-refresh {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    background: rgba(255,255,255,0.62);
    border: 1px solid rgba(255,255,255,0.92);
    color: #4f46e5;
    font-size: 13px;
    font-weight: 900;
}
.im-table thead tr {
    background: rgba(99, 102, 241, 0.05);
}
.im-table th {
    color: #4F46E5;
    font-size: 11px;
}
.im-table td {
    padding: 12px 20px;
    font-size: 12px;
}
[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.68) !important;
    color: #4f46e5 !important;
    border: 1px solid rgba(99,102,241,0.20) !important;
    border-radius: 12px !important;
    font-size: 12.5px !important;
    font-weight: 800 !important;
    box-shadow: 0 4px 16px rgba(99,102,241,0.08) !important;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: rgba(99,102,241,0.36) !important;
    box-shadow: 0 7px 22px rgba(99,102,241,0.13) !important;
}
@media (max-width: 1050px) {
    .im-page-head {
        grid-template-columns: 1fr;
    }
    .im-userbar {
        justify-content: flex-start;
    }
    .im-workspace {
        grid-template-columns: 1fr;
    }
}
@media (max-width: 640px) {
    .im-page-title {
        font-size: 19px;
    }
    .im-upload-heading,
    .im-card-head,
    .im-history-head {
        align-items: flex-start;
        flex-direction: column;
    }
    .im-map-row {
        grid-template-columns: 1fr;
    }
    .im-map-arrow {
        transform: rotate(90deg);
    }
}
</style>
"""

_NEW_DESIGN_CSS = """
<style>
/* ── Page title ── */
.im-page-title-v2 {
    font-size: 20px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.2;
}
.im-page-sub-v2 {
    margin-top: 4px;
    font-size: 12px;
    color: #64748B;
    font-weight: 400;
}
.im-page-sub-v2 a, .im-page-sub-v2 span {
    color: #4F46E5;
    font-weight: 600;
    text-decoration: none;
}

/* ── Upload card: three-section visual card ──
   Heading (HTML card-top) + drop zone (stFileUploadDropzone) + hint row
   all appear as one card via matching borders and zero-margin CSS. */
.im-upload-card-v2 {
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-bottom: none;
    border-radius: 14px 14px 0 0;
    padding: 18px 20px 14px;
}
.im-upload-title-v2 {
    font-size: 15px;
    font-weight: 800;
    color: #0F172A;
    line-height: 1.2;
}
.im-upload-sub-v2 {
    font-size: 12px;
    color: #94A3B8;
    margin-top: 3px;
}
/* ── File uploader: MINIMAL overrides only — do not touch layout props ──
   Only section cleanup; card appearance is handled by HTML im-upload-card-v2.
   The drop zone (stFileUploadDropzone) IS the visual dashed inner box. */
[data-testid="stFileUploader"] > section {
    gap: 0 !important;
    padding: 0 !important;
}
[data-testid="stFileUploader"] > section > small { display: none !important; }

/* ── Drop zone: lavender dashed box, flex column, cloud icon via ::before ── */
[data-testid="stFileUploadDropzone"] {
    border: 1.5px dashed #C4C9F4 !important;
    border-radius: 0 0 12px 12px !important;
    background: #F5F3FF !important;
    padding: 36px 20px 24px !important;
    min-height: 200px !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 0 !important;
    cursor: pointer !important;
    transition: border-color 0.18s, background 0.18s !important;
    box-shadow: none !important;
}
[data-testid="stFileUploadDropzone"]:hover {
    border-color: #818CF8 !important;
    background: #EEF2FF !important;
}
/* Cloud upload icon as first flex item */
[data-testid="stFileUploadDropzone"]::before {
    content: '' !important;
    display: block !important;
    width: 52px !important;
    height: 52px !important;
    border-radius: 13px !important;
    background-color: #EEF2FF !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%234F46E5' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='16 16 12 12 8 16'%3E%3C/polyline%3E%3Cline x1='12' y1='12' x2='12' y2='21'%3E%3C/line%3E%3Cpath d='M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3'%3E%3C/path%3E%3C/svg%3E") !important;
    background-repeat: no-repeat !important;
    background-position: center !important;
    background-size: 22px 22px !important;
    flex-shrink: 0 !important;
    margin-bottom: 14px !important;
}
/* Instruction text container */
[data-testid="stFileUploadDropzoneInstructions"] {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    text-align: center !important;
    margin-bottom: 18px !important;
}
[data-testid="stFileUploadDropzoneInstructions"] > div {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    gap: 5px !important;
}
[data-testid="stFileUploadDropzoneInstructions"] svg { display: none !important; }
[data-testid="stFileUploadDropzoneInstructions"] > div > span {
    font-size: 15px !important;
    font-weight: 700 !important;
    color: #1E293B !important;
    font-family: 'Inter', sans-serif !important;
}
[data-testid="stFileUploadDropzoneInstructions"] small,
[data-testid="stFileUploadDropzoneInstructions"] > div > small {
    font-size: 12px !important;
    color: #94A3B8 !important;
    font-weight: 400 !important;
}
/* Browse Files button inside the drop zone */
[data-testid="stFileUploadDropzone"] button {
    background: #4F46E5 !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 700 !important;
    min-height: 40px !important;
    padding: 0 32px !important;
    letter-spacing: 0.2px !important;
    box-shadow: 0 4px 14px rgba(79,70,229,0.28) !important;
    width: auto !important;
}
[data-testid="stFileUploadDropzone"] button:hover { background: #4338CA !important; }

/* Hint row below — negative margin-top closes the Streamlit ~1rem vertical gap
   so it appears flush against the drop zone bottom border. */
.im-upload-hint {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #ffffff;
    border: 1px solid #E2E8F0;
    border-top: 1px solid #F0EEFF;
    border-radius: 0 0 14px 14px;
    padding: 11px 18px 13px;
    margin-top: -1rem;
    position: relative;
    z-index: 2;
}
.im-upload-hint-icon {
    width: 34px;
    height: 34px;
    border-radius: 10px;
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    color: #ffffff;
    font-size: 9px;
    font-weight: 800;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    letter-spacing: 0.3px;
}
.im-upload-hint-text {
    font-size: 12px;
    color: #64748B;
    line-height: 1.5;
}

/* ── Ketentuan Import (white card) ── */
.im-ketentuan-card {
    background: #ffffff !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    padding: 0 !important;
    box-shadow: 0 1px 4px rgba(15,23,42,0.05) !important;
    overflow: hidden !important;
}
.im-ketentuan-head {
    padding: 20px 22px 14px !important;
    border-bottom: 1px solid #F1F5F9 !important;
}
.im-ketentuan-head .im-section-title {
    font-size: 14px !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    letter-spacing: 0.1px !important;
    margin: 0 !important;
}
.im-ketentuan-body {
    padding: 20px 22px 22px !important;
    display: flex !important;
    flex-direction: column !important;
    gap: 12px !important;
}
.im-ketentuan-item {
    display: flex !important;
    flex-direction: column !important;
    align-items: flex-start !important;
    width: 100% !important;
    margin-bottom: 4px !important;
    gap: 0 !important;
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}
.im-ketentuan-item.is-neutral {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}
.im-ketentuan-item.is-pass {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}
.im-ketentuan-item.is-fail {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
    box-shadow: none !important;
}
.im-ketentuan-row {
    display: flex !important;
    flex-direction: row !important;
    align-items: center !important;
    gap: 10px !important;
    width: 100% !important;
}
.im-ketentuan-neutral,
.im-ketentuan-check,
.im-ketentuan-fail {
    width: 20px !important;
    height: 20px !important;
    min-width: 20px !important;
    min-height: 20px !important;
    max-width: 20px !important;
    max-height: 20px !important;
    border-radius: 50% !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    flex-shrink: 0 !important;
    box-sizing: border-box !important;
    line-height: 1 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    text-align: center !important;
}
.im-ketentuan-neutral {
    background: transparent !important;
    border: 2px solid #cbd5e1 !important;
}
.im-ketentuan-check {
    background: #10b981 !important;
    border: 1px solid #10b981 !important;
    color: #ffffff !important;
    font-size: 11px !important;
    font-weight: 900 !important;
}
.im-ketentuan-fail {
    background: #ef4444 !important;
    border: 1px solid #ef4444 !important;
    color: #ffffff !important;
    font-size: 11px !important;
    font-weight: 900 !important;
    box-shadow: 0 0 10px rgba(239, 68, 68, 0.5) !important;
}
.im-ketentuan-text {
    font-size: 12.5px !important;
    color: #1e293b !important;
    font-weight: 600 !important;
    line-height: 1.45 !important;
}
.im-ketentuan-item.is-neutral .im-ketentuan-text {
    color: #64748b !important;
    font-weight: 500 !important;
}
.im-ketentuan-item.is-pass .im-ketentuan-text {
    color: #1e293b !important;
    font-weight: 600 !important;
}
.im-ketentuan-item.is-fail .im-ketentuan-text {
    color: #1e293b !important;
    font-weight: 600 !important;
}
.im-ketentuan-warning-box {
    background: #fef2f2 !important;
    border: 1px solid #fca5a5 !important;
    border-radius: 8px !important;
    padding: 8px 12px !important;
    margin-top: 8px !important;
    margin-left: 30px !important;
    font-size: 11px !important;
    color: #991b1b !important;
    font-weight: 500 !important;
    line-height: 1.45 !important;
    width: calc(100% - 30px) !important;
    box-sizing: border-box !important;
}
.im-validation-error-card {
    background: #fef2f2 !important;
    border: 1px solid #fca5a5 !important;
    border-radius: 12px !important;
    padding: 12px 20px !important;
    margin-top: 5px !important;
    width: 85% !important;
    max-width: 420px !important;
    box-sizing: border-box !important;
    text-align: center !important;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.05) !important;
}
.im-validation-error-title {
    font-size: 13px !important;
    font-weight: 750 !important;
    color: #b91c1c !important;
    margin-bottom: 3px !important;
}
.im-validation-error-desc {
    font-size: 11.5px !important;
    font-weight: 450 !important;
    color: #991b1b !important;
    line-height: 1.4 !important;
}
/* Kartu notifikasi hasil simpan (lihat _render_save_result_notice) — ikon +
   judul singkat + penjelasan bahasa awam, dengan detail teknis (mis. kode
   ruang yang bentrok) dipisah di bawah, bukan digabung jadi satu paragraf. */
.im-notice {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    border-radius: 12px;
    border: 1px solid;
    border-left-width: 4px;
    padding: 14px 16px;
    margin-top: 8px;
}
.im-notice-icon {
    flex: 0 0 auto;
    width: 32px;
    height: 32px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.im-notice-icon svg { width: 17px; height: 17px; }
.im-notice-body { flex: 1; min-width: 0; }
.im-notice-title {
    font-size: 13.5px;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 3px;
}
.im-notice-desc {
    font-size: 12.5px;
    font-weight: 450;
    color: #475569;
    line-height: 1.5;
}
.im-notice-detail {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid rgba(15, 23, 42, 0.06);
}
.im-notice-detail-label {
    display: block;
    font-size: 9.5px;
    font-weight: 700;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 6px;
}
.im-notice-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
}
.im-notice-tag {
    font-size: 11.5px;
    font-weight: 600;
    font-family: ui-monospace, "SF Mono", Menlo, Consolas, monospace;
    padding: 3px 9px;
    border-radius: 6px;
    background: rgba(15, 23, 42, 0.045);
    color: #334155;
    border: 1px solid rgba(15, 23, 42, 0.07);
}
.im-notice-error {
    background: #fef2f2;
    border-color: #fecaca;
}
.im-notice-error .im-notice-icon {
    background: rgba(220, 38, 38, 0.12);
    color: #dc2626;
}
.im-notice-warning {
    background: #fffbeb;
    border-color: #fde68a;
}
.im-notice-warning .im-notice-icon {
    background: rgba(217, 119, 6, 0.14);
    color: #d97706;
}
.im-notice-success {
    background: #f0fdf4;
    border-color: #bbf7d0;
}
.im-notice-success .im-notice-icon {
    background: rgba(22, 163, 74, 0.14);
    color: #16a34a;
}
.im-ketentuan-footer {
    margin-top: 18px;
    padding-top: 14px;
    border-top: 1px solid #F1F5F9;
}
.im-ketentuan-footer-label {
    font-size: 9px;
    font-weight: 800;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.9px;
    margin-bottom: 3px;
}
.im-ketentuan-footer-val {
    font-size: 11.5px;
    font-weight: 700;
    color: #475569;
}

/* ── Riwayat Import table card ── */
.im-riwayat-card {
    background: #ffffff;
    border-radius: 16px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(15,23,42,0.05);
    overflow: hidden;
    margin-top: 20px;
}
.im-riwayat-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 10px;
    padding: 18px 20px 14px;
    border-bottom: 1px solid #F1F5F9;
}
.im-riwayat-title-v2 {
    font-size: 14px;
    font-weight: 800;
    color: #0F172A;
}
.im-riwayat-search-box {
    display: flex;
    align-items: center;
    gap: 7px;
    padding: 7px 12px;
    border-radius: 8px;
    border: 1px solid #E2E8F0;
    background: #F8FAFC;
    min-width: 220px;
}
.im-riwayat-search-icon { color: #94A3B8; font-size: 13px; }
.im-riwayat-btns { display: flex; gap: 7px; flex-shrink: 0; }
.im-riwayat-btn-v2 {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 7px 14px; border-radius: 8px;
    border: 1px solid #E2E8F0; background: #ffffff;
    font-size: 12px; font-weight: 600; color: #475569;
    cursor: pointer; white-space: nowrap;
}
.im-riwayat-btn-export {
    background: #4F46E5; color: #ffffff; border-color: #4F46E5;
}
/* table */
.im-table-v2 { width:100%; border-collapse:collapse; }
.im-table-v2 thead tr { background: rgba(99, 102, 241, 0.05); }
.im-table-v2 th { padding:11px 16px; text-align:left; font-size:11px; font-weight:700; color:#4F46E5; text-transform:uppercase; letter-spacing:.5px; white-space:nowrap; border-bottom:none; }
.im-table-v2 td { padding:13px 16px; font-size:12.5px; color:#334155; border-bottom:1px solid #F8FAFC; vertical-align:middle; }
.im-table-v2 tbody tr:hover { background:#FAFBFF; }
.im-table-v2 tbody tr:last-child td { border-bottom:none; }
.im-file-ext-icon {
    display: inline-flex; align-items: center; gap: 8px;
}
.im-file-badge {
    width: 28px; height: 28px; border-radius: 6px;
    background: #DCFCE7; color: #16A34A;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 9.5px; font-weight: 800; flex-shrink: 0;
}
.im-file-badge.xls { background: #D1FAE5; color: #059669; }
.im-file-badge.csv { background: #DBEAFE; color: #2563EB; }
.im-file-badge.err { background: #FEE2E2; color: #DC2626; }
/* status badges v2 */
.bv2-sukses  { background:#DCFCE7; color:#16A34A; padding:4px 12px; border-radius:999px; font-size:11.5px; font-weight:700; display:inline-block; }
.bv2-gagal   { background:#FEE2E2; color:#DC2626; padding:4px 12px; border-radius:999px; font-size:11.5px; font-weight:700; display:inline-block; }
.bv2-pending { background:#FEF9C3; color:#92400E; padding:4px 12px; border-radius:999px; font-size:11.5px; font-weight:700; display:inline-block; }
/* eye action icon */
.im-eye-btn {
    width: 30px; height: 30px; border-radius: 8px;
    background: #F1F5F9; display: inline-flex;
    align-items: center; justify-content: center;
    color: #64748B; font-size: 14px; cursor: pointer;
}
/* pagination */
.im-pagination-row {
    display: flex; align-items: center;
    justify-content: space-between;
    padding: 13px 20px; border-top: 1px solid #F1F5F9;
    flex-wrap: wrap; gap: 8px;
}
.im-pagination-info { font-size: 12px; color: #94A3B8; font-weight: 500; }
.im-page-btns { display: flex; gap: 4px; align-items: center; }
.im-page-btn-v2 {
    min-width: 30px; height: 30px; padding: 0 6px;
    border-radius: 6px; border: 1px solid #E2E8F0;
    background: #ffffff; font-size: 12px; font-weight: 600;
    color: #64748B; display: inline-flex; align-items: center;
    justify-content: center; cursor: pointer;
}
.im-page-btn-v2.active { background: #4F46E5; color: #ffffff; border-color: #4F46E5; }
.im-page-btn-v2.dots { border: none; background: transparent; color: #94A3B8; }

/* ── Bottom info cards ── */
.im-info-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-top: 18px;
}
.im-info-card-v2 {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 1px 3px rgba(15,23,42,0.04);
    padding: 18px 20px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
}
.im-info-icon-v2 {
    width: 40px; height: 40px; border-radius: 10px;
    background: #F1F5F9; display: flex;
    align-items: center; justify-content: center;
    font-size: 18px; flex-shrink: 0;
}
.im-info-title-v2 { font-size: 13px; font-weight: 800; color: #1E293B; margin-bottom: 5px; }
.im-info-text-v2 { font-size: 11.5px; color: #64748B; line-height: 1.55; font-weight: 400; }
</style>
"""
