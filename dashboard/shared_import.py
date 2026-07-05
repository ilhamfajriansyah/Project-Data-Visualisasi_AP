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
    "pendapatanrs": "pendapatan_rs",
    "rs": "rs_percent",
    "rs_persen": "rs_percent",
    "persen_rs": "rs_percent",
    "rs_percent": "rs_percent",
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
    "acv": "acv",
    "achievement": "acv",
    "start_kontrak": "start_kontrak",
    "tanggal_mulai": "start_kontrak",
    "mulai_kontrak": "start_kontrak",
    "tgl_mulai": "start_kontrak",
    "start_contract": "start_kontrak",
    "end_kontrak": "end_kontrak",
    "tanggal_selesai": "end_kontrak",
    "akhir_kontrak": "end_kontrak",
    "tgl_selesai": "end_kontrak",
    "tgl_akhir": "end_kontrak",
    "end_contract": "end_kontrak",
    "kerja_sama": "kerja_sama",
    "jenis_kerjasama": "kerja_sama",
    "jenis_kerja_sama": "kerja_sama",
    "skema": "kerja_sama",
    "nomor_kontrak_sistem": "nomor_kontrak_sistem",
    "no_kontrak_sistem": "nomor_kontrak_sistem",
    "nomor_kontrak_legal": "nomor_kontrak_legal",
    "no_kontrak_legal": "nomor_kontrak_legal",
    "csp_non_csp": "csp_non_csp",
    "csp": "csp_non_csp",
    "pemilihan_mitra_usaha": "pemilihan_mitra_usaha",
    "mgrs_per_pax": "mgrs_per_pax",
    "mgrs_pax": "mgrs_per_pax",
    "mgrs": "mgrs_per_pax",
    "real_pax": "real_pax",

    # Remaining 50 columns
    "document_date": "document_date",
    "pic": "pic",
    "ro_number": "ro_number",
    "area": "area",
    "lokasi": "lokasi",
    "lantai": "lantai",
    "gate": "gate",
    "smoking_status": "smoking_status",
    "sub_bidang_usaha_original": "sub_bidang_usaha",
    "coa": "coa",
    "doc_number_rs": "doc_number_rs",
    "doc_number_sewa": "doc_number_sewa",
    "variant_no": "variant_no",
    "catatan": "catatan",
    "trafik_int_arr": "trafik_int_arr",
    "trafik_int_dep": "trafik_int_dep",
    "subtotal_trafik_int": "subtotal_trafik_int",
    "trafik_dom_arr": "trafik_dom_arr",
    "trafik_dom_dep": "trafik_dom_dep",
    "subtotal_trafik_dom": "subtotal_trafik_dom",
    "perimeter_spending_pax": "perimeter_spending_pax",
    "rev_sqm": "rev_per_sqm",
    "spending": "spending_per_pax",
    "spending_per_pax": "spending_per_pax",
    "spending_pax": "spending_per_pax",
    "spp": "spending_per_pax",
    "spending_per_passenger": "spending_per_pax",
}

NUMERIC_STANDARD_COLUMNS = {
    "tahun",
    "min_omzet",
    "real_omzet",
    "pendapatan_sewa",
    "pendapatan_rs",
    "total_kontribusi",
    "luas_sqm",
    "total_trafik",
    "rs_percent",
    "mgrs_per_pax",
    "real_pax",
    "acv",
    "rev_per_sqm",
    "spending_per_pax",
    "trafik_int_arr",
    "trafik_int_dep",
    "subtotal_trafik_int",
    "trafik_dom_arr",
    "trafik_dom_dep",
    "subtotal_trafik_dom",
}

DATE_STANDARD_COLUMNS = {"document_date", "start_kontrak", "end_kontrak"}

_NULL_PLACEHOLDERS = {"nan", "none", "nat", "-", "n/a", "na"}


def _clean_column_name(column) -> str:
    name = str(column).strip().lower()
    # Header asli sering punya keterangan format/instruksi nempel, mis.
    # "END KONTRAK\n(mm/dd/yyyy)" atau "NOMOR KONTRAK SISTEM (SAP)" — buang
    # isi dalam tanda kurung supaya nama intinya tetap cocok dengan alias
    # ("end_kontrak", bukan "end_kontrak_mm_dd_yyyy").
    name = re.sub(r"\([^)]*\)", " ", name)
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


def normalize_imported_data(df: pd.DataFrame) -> pd.DataFrame:
    """Bersihkan data mentah hasil upload sebelum disimpan: trim whitespace,
    samakan placeholder kosong ("nan"/"-"/dst) jadi NaN yang konsisten, dan
    koersi tipe kolom numerik/tanggal yang dikenal. `masa_jasa` dinormalisasi
    ke tanggal awal bulan supaya key deduplikasi (kode_ruang + masa_jasa +
    tahun) di import_manager.py bisa diandalkan meski format asal di Excel
    berbeda-beda antar file.
    """
    df = df.copy()

    for col in df.columns:
        if df[col].dtype != object:
            continue
        stripped = df[col].apply(lambda v: v.strip() if isinstance(v, str) else v)
        df[col] = stripped.apply(
            lambda v: pd.NA if isinstance(v, str) and v.lower() in _NULL_PLACEHOLDERS else v
        )

    mapping = get_column_mapping(df)

    for std_name in NUMERIC_STANDARD_COLUMNS:
        orig_col = mapping.get(std_name)
        if not orig_col or orig_col not in df.columns:
            continue
        cleaned = df[orig_col].astype(str).str.replace(r"[^\d.\-]", "", regex=True)
        df[orig_col] = pd.to_numeric(cleaned, errors="coerce")

    for std_name in DATE_STANDARD_COLUMNS:
        orig_col = mapping.get(std_name)
        if orig_col and orig_col in df.columns:
            df[orig_col] = pd.to_datetime(df[orig_col], errors="coerce")

    masa_jasa_col = mapping.get("masa_jasa")
    if masa_jasa_col and masa_jasa_col in df.columns:
        parsed = pd.to_datetime(df[masa_jasa_col], errors="coerce")
        df[masa_jasa_col] = parsed.dt.to_period("M").dt.to_timestamp()

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
    df = normalize_imported_data(raw_df)

    mapping = get_column_mapping(df)
    missing = get_missing_dashboard_columns(df)
    
    # Extract period from the Masa Jasa column if available
    period_str = "-"
    masa_jasa_col = mapping.get("masa_jasa")
    if masa_jasa_col and masa_jasa_col in df.columns:
        valid_vals = df[masa_jasa_col].dropna()
        if not valid_vals.empty:
            first_val = valid_vals.iloc[0]
            if isinstance(first_val, (pd.Timestamp, datetime)):
                period_str = first_val.strftime("%b-%y")
            else:
                parsed_date = pd.to_datetime(first_val, errors="coerce")
                if pd.notna(parsed_date):
                    period_str = parsed_date.strftime("%b-%y")
                else:
                    period_str = str(first_val).strip()

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
        "column_types": {col: str(df[col].dtype) for col in df.columns},
        "period": period_str,
        "periode": period_str
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
