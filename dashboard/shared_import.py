from datetime import datetime
import re

import pandas as pd
import streamlit as st


SHARED_DATA_KEY = "shared_import_df"
SHARED_META_KEY = "shared_import_meta"
MAX_IMPORT_FILE_BYTES = 20 * 1024 * 1024

# KETENTUAN_RULES is defined below with correct keys (format, size, merge_cell, required_filled, structure)

REQUIRED_DASHBOARD_COLUMNS = {
    "perusahaan",
    "brand",
    "terminal",
    "kode_ruang",
    "bidang_usaha",
    "masa_jasa",
    "tahun",
    "min_omzet",
    "real_omzet",
    "pendapatan_sewa",
    "pendapatan_rs",
    "total_kontribusi",
    "luas_sqm",
}

COLUMN_ALIASES = {
    "tenant": "perusahaan",
    "tenant_name": "perusahaan",
    "nama_tenant": "perusahaan",
    "nama_perusahaan": "perusahaan",
    "company": "perusahaan",
    "brand_name": "brand",
    "kode_ruangan": "kode_ruang",
    "unit": "kode_ruang",
    "unit_name": "kode_ruang",
    "sbu": "terminal",
    "office_sbu": "terminal",
    "terminal_sbu": "terminal",
    "sub_terminal": "sub_terminal",
    "business_category": "bidang_usaha",
    "kategori": "bidang_usaha",
    "sub_bidang_usaha": "bidang_usaha",
    "periode": "masa_jasa",
    "bulan": "masa_jasa",
    "month": "masa_jasa",
    "year": "tahun",
    "minimum_omzet": "min_omzet",
    "target_omzet": "min_omzet",
    "omzet": "real_omzet",
    "nilai_omzet": "real_omzet",
    "monthly_revenue": "real_omzet",
    "revenue": "real_omzet",
    "sewa": "pendapatan_sewa",
    "pendapatan": "pendapatan_sewa",
    "revenue_sharing": "pendapatan_rs",
    "rs": "pendapatan_rs",
    "pendapatanrs": "pendapatan_rs",
    "total_kontribusi": "total_kontribusi",
    "contribution": "total_kontribusi",
    "luas": "luas_sqm",
    "sqm": "luas_sqm",
    "area_sqm": "luas_sqm",
    "total_trafik": "total_trafik",
    "traffic": "total_trafik",
    "total_pax": "total_trafik",
    "passenger": "total_trafik",
    "passengers": "total_trafik",
    "penumpang": "total_trafik",
    "jumlah_penumpang": "total_trafik",
    "trafik": "total_trafik",
    "total_traffic": "total_trafik",
    "trafik_total": "total_trafik",
    "jumlah_trafik": "total_trafik",
    "produksi_m2": "luas_sqm",
    "produksi": "luas_sqm",
}

NUMERIC_COLUMNS = [
    "tahun",
    "min_omzet",
    "real_omzet",
    "pendapatan_sewa",
    "pendapatan_rs",
    "kontribusi",
    "luas_sqm",
    "total_trafik",
]


def _clean_column_name(column) -> str:
    name = str(column).strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def normalize_imported_data(df: pd.DataFrame) -> pd.DataFrame:
    # Preserve original columns exactly as requested
    return df


def get_column_mapping(df: pd.DataFrame) -> dict[str, str]:
    mapping = {}
    for col in df.columns:
        cleaned = _clean_column_name(col)
        if cleaned in COLUMN_ALIASES:
            mapping[COLUMN_ALIASES[cleaned]] = col
        elif cleaned in REQUIRED_DASHBOARD_COLUMNS:
            mapping[cleaned] = col
    return mapping


def get_mapped_column(required_col: str) -> str | None:
    mapping = st.session_state.get("shared_import_mapping", {})
    return mapping.get(required_col)


MAX_IMPORT_FILE_BYTES = 20 * 1024 * 1024
ALLOWED_IMPORT_EXTENSIONS = (".xlsx", ".xls")

KETENTUAN_RULES = [
    ("format", "Format file: .xlsx, .xls"),
    ("size", "Maksimal ukuran file: 20 MB"),
    ("merge_cell", "Pastikan data tidak mengandung merge cell"),
    ("required_filled", "Kolom wajib harus terisi"),
    ("structure", "Hindari perubahan struktur kolom"),
]


def _file_has_merged_cells(uploaded) -> bool:
    uploaded.seek(0)
    filename = uploaded.name.lower()

    if filename.endswith(".xlsx"):
        try:
            from openpyxl import load_workbook

            workbook = load_workbook(uploaded, read_only=True, data_only=True)
            try:
                for worksheet in workbook.worksheets:
                    if worksheet.merged_cells.ranges:
                        return True
            finally:
                workbook.close()
            return False
        except Exception:
            preview = pd.read_excel(uploaded, nrows=0)
            uploaded.seek(0)
            return any(str(col).startswith("Unnamed") for col in preview.columns)

    if filename.endswith(".xls"):
        try:
            import xlrd

            uploaded.seek(0)
            workbook = xlrd.open_workbook(file_contents=uploaded.read())
            for sheet in workbook.sheets():
                if sheet.merged_cells:
                    return True
            return False
        except ImportError:
            preview = pd.read_excel(uploaded, nrows=0)
            uploaded.seek(0)
            return any(str(col).startswith("Unnamed") for col in preview.columns)
        except Exception:
            return True

    return False


def _required_columns_filled(df: pd.DataFrame) -> bool:
    mapping = get_column_mapping(df)
    for col_req in REQUIRED_DASHBOARD_COLUMNS:
        orig_col = mapping.get(col_req)
        if not orig_col:
            return False
        series = df[orig_col]
        if series.isna().any():
            return False
        if series.dtype == object:
            cleaned = series.astype(str).str.strip()
            if cleaned.eq("").any() or cleaned.str.lower().isin({"nan", "none", "nat"}).any():
                return False
    return True


def validate_import_upload(uploaded) -> dict[str, bool]:
    results = {key: False for key, _ in KETENTUAN_RULES}
    if uploaded is None:
        return results

    filename = str(getattr(uploaded, "name", "")).lower()
    results["format"] = filename.endswith(ALLOWED_IMPORT_EXTENSIONS)
    results["size"] = int(getattr(uploaded, "size", 0) or 0) <= MAX_IMPORT_FILE_BYTES

    if not (results["format"] and results["size"]):
        return results

    try:
        results["merge_cell"] = not _file_has_merged_cells(uploaded)
        uploaded.seek(0)
        raw_df = read_import_file(uploaded)
        df = normalize_imported_data(raw_df)
        missing = get_missing_dashboard_columns(df)
        results["structure"] = len(missing) == 0
        results["required_filled"] = _required_columns_filled(df) if results["structure"] else False
    except Exception:
        pass
    finally:
        uploaded.seek(0)

    return results


def read_import_file(uploaded) -> pd.DataFrame:
    uploaded.seek(0)
    filename = str(getattr(uploaded, "name", "")).lower()
    if not filename.endswith(ALLOWED_IMPORT_EXTENSIONS):
        raise ValueError("Format file tidak didukung. Gunakan .xlsx atau .xls.")
    return pd.read_excel(uploaded)


def store_shared_import(uploaded, sbu: str = "") -> tuple[pd.DataFrame, list[str]]:
    raw_df = read_import_file(uploaded)
    df = raw_df.copy()
    
    mapping = get_column_mapping(df)
    missing = get_missing_dashboard_columns(df)
    
    st.session_state[SHARED_DATA_KEY] = df
    st.session_state["shared_import_mapping"] = mapping
    st.session_state[SHARED_META_KEY] = {
        "file_name": uploaded.name,
        "rows": len(df),
        "columns": len(df.columns),
        "uploaded_at": datetime.now().strftime("%d %b %Y - %H:%M"),
        "sbu": sbu,
        "ready_for_dashboard": len(missing) == 0,
        "missing_columns": missing,
        "original_columns": list(df.columns),
        "column_types": {col: str(df[col].dtype) for col in df.columns}
    }
    return df, missing


def get_shared_import_data() -> pd.DataFrame | None:
    df = st.session_state.get(SHARED_DATA_KEY)
    if isinstance(df, pd.DataFrame) and not df.empty:
        return df.copy()
    return None


def get_shared_import_meta() -> dict:
    return st.session_state.get(SHARED_META_KEY, {})


def get_missing_dashboard_columns(df: pd.DataFrame) -> list[str]:
    mapping = get_column_mapping(df)
    return sorted(REQUIRED_DASHBOARD_COLUMNS.difference(mapping.keys()))


def has_dashboard_ready_import() -> bool:
    df = get_shared_import_data()
    return df is not None and not get_missing_dashboard_columns(df)


def import_status_html(card_class: str, title_class: str, sub_class: str) -> str:
    meta = get_shared_import_meta()
    if not meta:
        return f"""
        <div class="{card_class}">
            <p class="{title_class}">Central Import Source</p>
            <p class="{sub_class}">Belum ada file dari Import Manager. Data halaman masih memakai database atau dummy data.</p>
        </div>
        """

    status = "Ready for dashboard" if meta.get("ready_for_dashboard") else "Uploaded, but schema incomplete"
    detail = f"{meta.get('file_name', '-')} - {meta.get('rows', 0):,} rows - {meta.get('uploaded_at', '-')}"
    missing = meta.get("missing_columns") or []
    warning = ""
    if missing:
        warning = f'<p class="{sub_class}">Kolom kurang: {", ".join(missing[:6])}</p>'

    return f"""
    <div class="{card_class}">
        <p class="{title_class}">Central Import Source</p>
        <p class="{sub_class}">{status}</p>
        <p class="{sub_class}">{detail}</p>
        {warning}
    </div>
    """
