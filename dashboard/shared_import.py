from datetime import datetime
import re

import pandas as pd
import streamlit as st


SHARED_DATA_KEY = "shared_import_df"
SHARED_META_KEY = "shared_import_meta"
MAX_IMPORT_FILE_BYTES = 20 * 1024 * 1024

KETENTUAN_RULES = [
    ("extension", "Format file harus Excel (.xlsx / .xls)"),
    ("size", "Ukuran file maksimal 20 MB"),
    ("readable", "File dapat dibaca"),
    ("not_empty", "File memiliki data"),
]

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
    "kontribusi",
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
    "sub_terminal": "terminal",
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
    "total_kontribusi": "kontribusi",
    "contribution": "kontribusi",
    "luas": "luas_sqm",
    "sqm": "luas_sqm",
    "area_sqm": "luas_sqm",
    "traffic": "jumlah_pax",
    "total_pax": "jumlah_pax",
    "passenger": "jumlah_pax",
    "passengers": "jumlah_pax",
    "penumpang": "jumlah_pax",
    "jumlah_penumpang": "jumlah_pax",
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
    "jumlah_pax",
]


def _clean_column_name(column) -> str:
    name = str(column).strip().lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def normalize_imported_data(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [
        COLUMN_ALIASES.get(_clean_column_name(col), _clean_column_name(col))
        for col in normalized.columns
    ]
    normalized = normalized.loc[:, ~normalized.columns.duplicated()]

    for col in NUMERIC_COLUMNS:
        if col in normalized.columns:
            normalized[col] = pd.to_numeric(normalized[col], errors="coerce")

    if "tahun" in normalized.columns:
        normalized["tahun"] = normalized["tahun"].fillna(0).astype(int)
    if {"real_omzet", "luas_sqm"}.issubset(normalized.columns):
        normalized["rev_sqm"] = normalized["real_omzet"] / normalized["luas_sqm"].replace(0, pd.NA)
    if {"real_omzet", "min_omzet"}.issubset(normalized.columns):
        normalized["acv"] = (normalized["real_omzet"] / normalized["min_omzet"].replace(0, pd.NA) * 100).round(2)

    return normalized


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
    for col in REQUIRED_DASHBOARD_COLUMNS:
        if col not in df.columns:
            return False
        series = df[col]
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

    filename = uploaded.name.lower()
    results["format"] = filename.endswith(ALLOWED_IMPORT_EXTENSIONS)
    results["size"] = uploaded.size <= MAX_IMPORT_FILE_BYTES

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

    return results


def read_import_file(uploaded) -> pd.DataFrame:
    uploaded.seek(0)
    filename = uploaded.name.lower()
    if not filename.endswith(ALLOWED_IMPORT_EXTENSIONS):
        raise ValueError("Format file tidak didukung. Gunakan .xlsx atau .xls.")
    return pd.read_excel(uploaded)


def validate_import_upload(uploaded) -> dict[str, bool]:
    if uploaded is None:
        return {key: False for key, _ in KETENTUAN_RULES}

    filename = str(getattr(uploaded, "name", "")).lower()
    size = int(getattr(uploaded, "size", 0) or 0)
    validation = {
        "extension": filename.endswith((".xlsx", ".xls")),
        "size": size <= MAX_IMPORT_FILE_BYTES,
        "readable": False,
        "not_empty": False,
    }

    if validation["extension"] and validation["size"]:
        try:
            df = read_import_file(uploaded)
            validation["readable"] = True
            validation["not_empty"] = not df.empty
        except Exception:
            validation["readable"] = False
            validation["not_empty"] = False
        finally:
            uploaded.seek(0)

    return validation


def store_shared_import(uploaded, sbu: str = "") -> tuple[pd.DataFrame, list[str]]:
    raw_df = read_import_file(uploaded)
    df = normalize_imported_data(raw_df)
    missing = get_missing_dashboard_columns(df)
    st.session_state[SHARED_DATA_KEY] = df
    st.session_state[SHARED_META_KEY] = {
        "file_name": uploaded.name,
        "rows": len(df),
        "columns": len(df.columns),
        "uploaded_at": datetime.now().strftime("%d %b %Y - %H:%M"),
        "sbu": sbu,
        "ready_for_dashboard": len(missing) == 0,
        "missing_columns": missing,
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
    return sorted(REQUIRED_DASHBOARD_COLUMNS.difference(df.columns))


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
