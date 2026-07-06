import streamlit as st
import streamlit.components.v1 as components
import pandas as pd

from .export_utils import EXCEL_MIME, dataframe_to_excel_bytes
from datetime import date
from textwrap import dedent
import time

from .shared_import import (
    KETENTUAN_RULES,
    get_shared_import_meta,
    store_shared_import,
    validate_import_upload,
    SHARED_DATA_KEY,
    SHARED_META_KEY,
    normalize_imported_data,
    normalize_identity_key,
    read_import_file,
    get_missing_dashboard_columns,
    get_column_mapping,
    REQUIRED_DASHBOARD_COLUMNS,
)
from .navigation import topnav_actions_html
from .pagination import render_pagination

IM_PAGE_ICON_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
    'width="18" height="18" fill="none" stroke="currentColor" '
    'stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round" '
    'aria-hidden="true">'
    '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
    '<polyline points="17 8 12 3 7 8"/>'
    '<line x1="12" y1="3" x2="12" y2="15"/>'
    '</svg>'
)


def _im_page_header_html():
    return dedent(f"""
    <div class="ov-page-header">
        <div class="ov-page-header-left">
            <div class="ov-page-icon" aria-hidden="true">{IM_PAGE_ICON_SVG}</div>
            <div class="ov-page-header-copy">
                <div class="ov-page-title-row">
                    <h2 class="ov-page-title">Import Manager</h2>
                </div>
                <p class="ov-page-sub">Unggah file performa komersial Anda untuk memperbarui analytics engine.</p>
            </div>
        </div>
        {topnav_actions_html()}
    </div>
    """).strip()


def _mount_im_fixed_header():
    components.html(
        """
        <script>
        (function () {
            const doc = window.parent.document;

            function findHeaderHost(marker) {
                return (
                    marker.closest('[data-testid="stVerticalBlockBorderWrapper"]')
                    || marker.closest('[data-testid="stVerticalBlock"]')
                );
            }

            function applyFixedHeader() {
                const marker = doc.querySelector('.ov-sticky-header-marker');
                if (!marker) return;

                const host = findHeaderHost(marker);
                if (!host) return;

                host.classList.add('ov-fixed-header-active');

                const sidebar = doc.querySelector('[data-testid="stSidebar"]');
                const left = sidebar ? sidebar.getBoundingClientRect().width : 258;
                host.style.left = left + 'px';
            }

            applyFixedHeader();
            window.parent.addEventListener('resize', applyFixedHeader);
            setTimeout(applyFixedHeader, 120);
            setTimeout(applyFixedHeader, 450);
            setTimeout(applyFixedHeader, 900);
        })();
        </script>
        """,
        height=0,
    )

# ─────────────────────────────────────────────
# DUMMY DATA
# ─────────────────────────────────────────────
PERIOD_ACTIVE = "April 2026"
DEADLINE      = date(2026, 4, 30)

SBU_LIST = ["Cikarang", "Bali", "Ginung", "Lombok", "Manado", "Kupang", "Jayapura", "Sorong"]

def _load_import_history() -> pd.DataFrame:
    try:
        from .connection import get_engine
        from sqlalchemy import text

        engine = get_engine()
        try:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE import_history ADD COLUMN IF NOT EXISTS deleted_by VARCHAR(255)"))
        except Exception:
            pass

        with engine.connect() as conn:
            return pd.read_sql(
                text("""
                    SELECT import_id, periode, filename, uploaded_by, uploaded_at,
                           total_records, valid_records, rs_total, file_size, status,
                           deleted_by
                    FROM import_history ih
                    ORDER BY uploaded_at DESC NULLS LAST, import_id DESC
                """),
                conn,
            )
    except Exception:
        return pd.DataFrame()


def _get_refined_history_data() -> list[dict]:
    history = _load_import_history()
    if history.empty:
        return []

    items = []
    for _, row in history.iterrows():
        uploaded_at = pd.to_datetime(row.get("uploaded_at"), errors="coerce")
        uploader = str(row.get("uploaded_by") or "User")
        initials = "".join(part[:1] for part in uploader.split()[:2]).upper() or "U"
        rs_total = float(row.get("rs_total") or 0)
        items.append({
            "import_id": row.get("import_id"),
            "period": row.get("periode") or "-",
            "upload_date": uploaded_at.strftime("%d %b %Y") if pd.notna(uploaded_at) else "-",
            "upload_time": uploaded_at.strftime("%H:%M WIB") if pd.notna(uploaded_at) else "-",
            "uploader": uploader,
            "role": "User",
            "initials": initials,
            "color": "#6366f1",
            "total_records": int(row.get("total_records") or 0),
            "tenants": int(row.get("valid_records") or 0),
            "file_size": row.get("file_size") or "-",
            "rs_total": f"Rp {rs_total:,.0f}".replace(",", "."),
            "status": row.get("status") or "Success",
            "deleted_by": row.get("deleted_by"),
        })
    return items


# ─────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────
from .import_manager_styles import _PAGE_CSS, _REFINED_IMPORT_CSS, _NEW_DESIGN_CSS


# ─────────────────────────────────────────────
# INIT STATE
# ─────────────────────────────────────────────
def _init_state():
    defaults = {
        "im_view":        "PIC",       # "PIC" | "Admin"
        "im_step":        1,           # 1-4
        "im_file":        None,
        "im_preview_ok":  False,
        "im_submitted":   False,
        "im_confirmed":   False,
        "im_sbu":         SBU_LIST[0],
        "im_deadline":    str(DEADLINE),
        "im_validation":  {key: False for key, _ in KETENTUAN_RULES},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


_IM_NOTICE_ICONS = {
    "error": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    "warning": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    "success": '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>',
}


def _render_save_result_notice(result: dict) -> None:
    """Kartu notifikasi terstruktur untuk hasil `_save_to_database()`: ikon +
    judul singkat berbahasa awam + penjelasan, dengan detail teknis (mis.
    kode ruang yang bentrok) dipisah di baris sendiri — bukan satu paragraf
    teks polos ala st.error/st.warning bawaan."""
    from html import escape

    severity = result.get("severity", "error")
    icon = _IM_NOTICE_ICONS.get(severity, _IM_NOTICE_ICONS["error"])

    detail_html = ""
    detail_items = result.get("detail_items")
    if detail_items:
        tags = "".join(f'<span class="im-notice-tag">{escape(str(v))}</span>' for v in detail_items)
        detail_html = (
            '<div class="im-notice-detail">'
            f'<span class="im-notice-detail-label">{escape(result.get("detail_label", "Detail"))}</span>'
            f'<div class="im-notice-tags">{tags}</div>'
            '</div>'
        )

    st.markdown(
        f'<div class="im-notice im-notice-{severity}">'
        f'<div class="im-notice-icon">{icon}</div>'
        '<div class="im-notice-body">'
        f'<div class="im-notice-title">{escape(result.get("title", ""))}</div>'
        f'<div class="im-notice-desc">{escape(result.get("message", ""))}</div>'
        f'{detail_html}'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def _save_to_database():
    """Simpan data ke transaction_revenue. Selalu mengembalikan
    (success, result) dengan `result` sebagai dict {severity, title,
    message, detail_label, detail_items} — bukan string polos — supaya
    UI bisa menampilkan kartu notifikasi terstruktur (lihat
    _render_save_result_notice) alih-alih satu paragraf teks teknis."""
    from .shared_import import SHARED_DATA_KEY
    df = st.session_state.get(SHARED_DATA_KEY)
    if df is None or df.empty:
        return False, {
            "severity": "error",
            "title": "Tidak Ada Data untuk Disimpan",
            "message": "File yang diunggah tidak berisi data yang bisa diproses.",
        }
    
    mapping = st.session_state.get("shared_import_mapping", {})
    df_to_save = df.rename(columns={v: k for k, v in mapping.items()})

    # Nama kolom standar Import Manager berbeda dari nama kolom asli di tabel
    # transaction_revenue (lihat alias "produksi_m2 AS luas_sqm" di
    # load_dashboard_data), jadi disamakan dulu supaya tidak ikut dibuang
    # saat filter save_cols di bawah.
    DB_COLUMN_OVERRIDES = {"luas_sqm": "produksi_m2"}
    df_to_save = df_to_save.rename(columns={
        k: v for k, v in DB_COLUMN_OVERRIDES.items() if k in df_to_save.columns
    })

    from .connection import get_engine
    from sqlalchemy import inspect, text
    from sqlalchemy.exc import IntegrityError
    import time

    NATURAL_KEY = ["kode_ruang", "masa_jasa", "tahun"]

    try:
        engine = get_engine()
        import_id = int(time.time())
        inspector = inspect(engine)
        db_columns = [col['name'] for col in inspector.get_columns('transaction_revenue')]

        if 'import_id' in db_columns:
            df_to_save['import_id'] = import_id

        save_cols = [c for c in df_to_save.columns if c in db_columns]
        df_final = df_to_save[save_cols].copy()
        df_final = df_final.loc[:, ~df_final.columns.duplicated()]

        if 'id' in df_final.columns:
            df_final = df_final.drop(columns=['id'])

        skipped_count = 0
        skipped_items = []
        if all(c in df_final.columns for c in NATURAL_KEY):
            # Safety net di level database: kombinasi kode_ruang + masa_jasa +
            # tahun harus unik, supaya baris yang sama tidak pernah bisa dobel
            # tersimpan walau ada bug di pengecekan aplikasi di bawah.
            try:
                with engine.begin() as ddl_conn:
                    ddl_conn.execute(text(
                        "ALTER TABLE transaction_revenue ADD CONSTRAINT "
                        "uq_transaction_revenue_natural_key UNIQUE (kode_ruang, masa_jasa, tahun)"
                    ))
            except Exception:
                pass

            dup_mask = df_final.duplicated(subset=NATURAL_KEY, keep=False)
            if dup_mask.any():
                dup_items = []
                for kode, group in df_final.loc[dup_mask].groupby("kode_ruang", dropna=False):
                    rows = _format_row_list([int(i) + 2 for i in group.index], limit=8)
                    dup_items.append(f"{kode} — baris {rows}")
                return False, {
                    "severity": "error",
                    "title": "Data Duplikat Ditemukan",
                    "message": (
                        f"File ini punya {int(dup_mask.sum())} baris dengan kode ruang dan periode "
                        "yang sama persis. Hapus atau perbaiki salah satu baris yang bentrok, "
                        "lalu unggah ulang."
                    ),
                    "detail_label": "Kode Ruang yang Bentrok",
                    "detail_items": dup_items[:15],
                }

            tahun_values = [
                int(t) for t in pd.to_numeric(df_final["tahun"], errors="coerce").dropna().unique()
            ]
            existing = pd.DataFrame(columns=["kode_ruang", "masa_jasa", "tahun"])
            if tahun_values:
                with engine.connect() as conn:
                    existing = pd.read_sql(
                        text(
                            "SELECT kode_ruang, masa_jasa, tahun FROM transaction_revenue "
                            "WHERE kode_ruang = ANY(:kode_ruang) AND tahun = ANY(:tahun)"
                        ),
                        conn,
                        params={
                            "kode_ruang": df_final["kode_ruang"].astype(str).tolist(),
                            "tahun": tahun_values,
                        },
                    )

            if not existing.empty:
                existing_keys = set(
                    zip(
                        existing["kode_ruang"].astype(str),
                        pd.to_datetime(existing["masa_jasa"], errors="coerce"),
                        existing["tahun"],
                    )
                )
                is_dup = df_final.apply(
                    lambda r: (
                        str(r["kode_ruang"]),
                        pd.to_datetime(r["masa_jasa"], errors="coerce"),
                        r["tahun"],
                    ) in existing_keys,
                    axis=1,
                )
                skipped_count = int(is_dup.sum())
                skipped_items = [
                    f"{row['kode_ruang']} — baris {int(idx) + 2}"
                    for idx, row in df_final.loc[is_dup].iterrows()
                ][:15]
                df_final = df_final.loc[~is_dup].copy()

            if df_final.empty:
                return False, {
                    "severity": "error",
                    "title": "Semua Data Sudah Pernah Diimpor",
                    "message": (
                        f"Seluruh {skipped_count} baris pada file ini sudah ada di database "
                        "(kode ruang dan periode yang sama). Tidak ada data baru yang ditambahkan."
                    ),
                    "detail_label": "Baris yang Sudah Pernah Diimpor",
                    "detail_items": skipped_items,
                }

        # Normalisasi tenant: tenant_master adalah satu-satunya sumber
        # kebenaran untuk identitas tenant (dedup berdasarkan perusahaan +
        # brand + terminal). transaction_revenue tetap menyimpan kolom
        # tenant apa adanya (kompatibel dengan halaman lain), tapi sekarang
        # juga terhubung lewat tenant_id yang benar-benar merujuk ke sana.
        if (
            'tenant_id' in db_columns
            and all(c in df_final.columns for c in ["perusahaan", "brand", "terminal"])
        ):
            try:
                with engine.begin() as ddl_conn:
                    ddl_conn.execute(text(
                        "ALTER TABLE tenant_master ADD CONSTRAINT "
                        "uq_tenant_master_key UNIQUE (perusahaan, brand, terminal)"
                    ))
            except Exception:
                pass

            tenant_cols = [c for c in ["perusahaan", "brand", "terminal", "bidang_usaha", "lokasi"] if c in df_final.columns]
            tenant_rows = df_final[tenant_cols].dropna(subset=["perusahaan", "brand", "terminal"]).copy()
            tenant_rows["_tenant_key"] = list(zip(
                tenant_rows["perusahaan"].map(normalize_identity_key),
                tenant_rows["brand"].map(normalize_identity_key),
                tenant_rows["terminal"].map(normalize_identity_key),
            ))
            # Dedup pakai kunci case/spasi-insensitive, bukan kecocokan
            # string persis — supaya "PT ABC" dan "pt  abc" dalam file yang
            # sama tidak dianggap dua tenant berbeda.
            tenant_rows = tenant_rows.drop_duplicates(subset=["_tenant_key"])

            if not tenant_rows.empty:
                with engine.begin() as tconn:
                    existing_tenants = pd.read_sql(
                        text("SELECT id, perusahaan, brand, terminal FROM tenant_master"), tconn
                    )
                    key_to_id = {
                        (
                            normalize_identity_key(r.perusahaan),
                            normalize_identity_key(r.brand),
                            normalize_identity_key(r.terminal),
                        ): r.id
                        for r in existing_tenants.itertuples()
                    }

                    for _, row in tenant_rows.iterrows():
                        tkey = row["_tenant_key"]
                        if tkey in key_to_id:
                            continue  # tenant sudah ada (mungkin beda huruf besar/kecil atau spasi)
                        inserted_id = tconn.execute(
                            text("""
                                INSERT INTO tenant_master (perusahaan, brand, terminal, bidang_usaha, lokasi)
                                VALUES (:perusahaan, :brand, :terminal, :bidang_usaha, :lokasi)
                                ON CONFLICT (perusahaan, brand, terminal) DO NOTHING
                                RETURNING id
                            """),
                            {
                                "perusahaan": row["perusahaan"],
                                "brand": row["brand"],
                                "terminal": row["terminal"],
                                "bidang_usaha": row.get("bidang_usaha"),
                                "lokasi": row.get("lokasi"),
                            },
                        ).scalar()
                        if inserted_id is None:
                            # Konflik exact-match (kasus langka: kunci ternormalisasi
                            # baru dilihat di batch ini tapi string persisnya sudah
                            # ada) — ambil id yang sudah ada.
                            inserted_id = tconn.execute(
                                text(
                                    "SELECT id FROM tenant_master "
                                    "WHERE perusahaan = :perusahaan AND brand = :brand AND terminal = :terminal"
                                ),
                                {
                                    "perusahaan": row["perusahaan"],
                                    "brand": row["brand"],
                                    "terminal": row["terminal"],
                                },
                            ).scalar()
                        key_to_id[tkey] = inserted_id

                df_final["_tenant_key"] = list(zip(
                    df_final["perusahaan"].map(normalize_identity_key),
                    df_final["brand"].map(normalize_identity_key),
                    df_final["terminal"].map(normalize_identity_key),
                ))
                df_final["tenant_id"] = df_final["_tenant_key"].map(key_to_id)
                df_final = df_final.drop(columns=["_tenant_key"])

        # Normalisasi kontrak: satu baris kontrak per nomor_kontrak_sistem
        # (nomor SAP), disimpan terpisah dari transaction_revenue dan
        # terhubung ke tenant_master. Hanya baris yang benar-benar punya
        # nomor kontrak sistem yang diproses di sini. Baris kontrak.import_id
        # merujuk ke import_history, jadi penyiapan datanya di sini, tapi
        # eksekusi INSERT-nya harus menunggu sampai import_history baris ini
        # sudah benar-benar ada (lihat di bawah) — kalau tidak, FK gagal
        # persis seperti bug transaction_revenue vs import_history sebelumnya.
        kontrak_rows = pd.DataFrame()
        kontrak_available = {}
        if "nomor_kontrak_sistem" in df_final.columns:
            try:
                with engine.begin() as ddl_conn:
                    ddl_conn.execute(text(
                        "ALTER TABLE kontrak ADD CONSTRAINT "
                        "uq_kontrak_nomor_sistem UNIQUE (nomor_kontrak_sistem)"
                    ))
            except Exception:
                pass

            kontrak_col_map = {
                "nomor_kontrak_sistem": "nomor_kontrak_sistem",
                "nomor_kontrak_legal": "nomor_kontrak_legal",
                "kerja_sama": "jenis_kontrak",
                "rs_percent": "sharing_percent",
                "min_omzet": "minimal_omzet",
                "mgrs_per_pax": "mgrs_per_pax",
                "start_kontrak": "start_kontrak",
                "end_kontrak": "end_kontrak",
            }
            kontrak_available = {src: dst for src, dst in kontrak_col_map.items() if src in df_final.columns}
            kontrak_rows = (
                df_final[list(kontrak_available.keys()) + (["tenant_id"] if "tenant_id" in df_final.columns else [])]
                .dropna(subset=["nomor_kontrak_sistem"])
                .drop_duplicates(subset=["nomor_kontrak_sistem"])
            )

        with engine.begin() as conn:
            if 'import_history' in inspector.get_table_names():
                meta = get_shared_import_meta()
                rs_total = 0.0
                if 'pendapatan_rs' in df_final.columns:
                    rs_total = float(pd.to_numeric(df_final['pendapatan_rs'], errors='coerce').fillna(0).sum())
                conn.execute(
                    text("""
                        INSERT INTO import_history
                            (import_id, periode, filename, uploaded_by, uploaded_at, is_active,
                             total_records, valid_records, rs_total, file_size, status)
                        VALUES
                            (:import_id, :periode, :filename, :uploaded_by, CURRENT_TIMESTAMP, true,
                             :total_records, :valid_records, :rs_total, :file_size, 'Success')
                    """),
                    {
                        'import_id': import_id,
                        'periode': meta.get('period') or meta.get('periode') or PERIOD_ACTIVE,
                        'filename': meta.get('file_name') or st.session_state.get('im_file') or '-',
                        'uploaded_by': st.session_state.get('user_name', 'Operational User'),
                        'total_records': int(len(df_final)) + skipped_count,
                        'valid_records': int(len(df_final)),
                        'rs_total': rs_total,
                        'file_size': meta.get('file_size') or '-',
                    },
                )

            if not kontrak_rows.empty:
                for _, row in kontrak_rows.iterrows():
                    params = {dst: row.get(src) for src, dst in kontrak_available.items()}
                    params["tenant_id"] = row.get("tenant_id")
                    params["import_id"] = import_id
                    cols = list(params.keys())
                    conn.execute(
                        text(
                            f"INSERT INTO kontrak ({', '.join(cols)}) "
                            f"VALUES ({', '.join(':' + c for c in cols)}) "
                            "ON CONFLICT (nomor_kontrak_sistem) DO NOTHING"
                        ),
                        params,
                    )

            df_final.to_sql("transaction_revenue", con=conn, if_exists="append", index=False)

            # Normalisasi trafik: berbeda dari tenant_master/kontrak (yang
            # berbasis identitas), traffic adalah AGREGAT per
            # tahun+bulan+terminal yang dijumlahkan dari banyak baris tenant
            # sekaligus. Jadi bukan sekadar insert baris baru — tiap kali ada
            # baris baru masuk ke transaction_revenue untuk suatu
            # tahun+bulan+terminal, agregatnya dihitung ULANG dari seluruh
            # transaction_revenue (bukan cuma batch ini), supaya tetap akurat
            # walau datanya datang dari beberapa kali import terpisah.
            if all(c in df_final.columns for c in ["tahun", "masa_jasa", "terminal"]):
                try:
                    with engine.begin() as ddl_conn:
                        ddl_conn.execute(text(
                            "ALTER TABLE traffic ADD CONSTRAINT "
                            "uq_traffic_key UNIQUE (tahun, bulan, terminal)"
                        ))
                except Exception:
                    pass

                periods = (
                    df_final[["tahun", "masa_jasa", "terminal"]]
                    .dropna()
                    .drop_duplicates()
                )
                for _, p in periods.iterrows():
                    conn.execute(
                        text("""
                            INSERT INTO traffic (tahun, bulan, terminal, pax_domestik, pax_internasional, total_pax, import_id)
                            SELECT
                                tahun,
                                TO_CHAR(MAX(masa_jasa::date), 'FMMonth'),
                                terminal,
                                SUM(COALESCE(subtotal_trafik_dom, 0)),
                                SUM(COALESCE(subtotal_trafik_int, 0)),
                                SUM(COALESCE(total_trafik, 0)),
                                :import_id
                            FROM transaction_revenue
                            WHERE tahun = :tahun AND masa_jasa::date = CAST(:masa_jasa AS date) AND terminal = :terminal
                            GROUP BY tahun, terminal
                            ON CONFLICT (tahun, bulan, terminal) DO UPDATE SET
                                pax_domestik = EXCLUDED.pax_domestik,
                                pax_internasional = EXCLUDED.pax_internasional,
                                total_pax = EXCLUDED.total_pax,
                                import_id = EXCLUDED.import_id
                        """),
                        {
                            "tahun": p["tahun"],
                            "masa_jasa": p["masa_jasa"],
                            "terminal": p["terminal"],
                            "import_id": import_id,
                        },
                    )

        st.cache_data.clear()

        if skipped_count:
            return True, {
                "severity": "warning",
                "title": "Sebagian Data Berhasil Disimpan",
                "message": (
                    f"{len(df_final)} baris baru berhasil disimpan. {skipped_count} baris "
                    "dilewati karena sudah pernah diimpor sebelumnya."
                ),
                "detail_label": "Baris yang Dilewati",
                "detail_items": skipped_items,
            }
        return True, {"severity": "success", "title": "Data Berhasil Disimpan", "message": "Seluruh baris pada file ini berhasil disimpan ke database."}
    except IntegrityError:
        return False, {
            "severity": "error",
            "title": "Data Sudah Ada di Database",
            "message": "Sebagian atau seluruh data pada file ini sudah ada di database. Tidak ada data baru yang disimpan.",
        }
    except Exception as e:
        return False, {
            "severity": "error",
            "title": "Gagal Menyimpan ke Database",
            "message": f"Terjadi kesalahan teknis saat menyimpan data: {str(e)}",
        }


_REQUIRED_COLUMN_LABELS = {
    "perusahaan": "Perusahaan",
    "brand": "Brand",
    "terminal": "Terminal",
    "kode_ruang": "Kode Ruang",
    "bidang_usaha": "Bidang Usaha",
    "masa_jasa": "Masa Jasa",
    "tahun": "Tahun",
    "min_omzet": "Min Omzet",
    "real_omzet": "Real Omzet",
    "pendapatan_sewa": "Pendapatan Sewa",
    "pendapatan_rs": "Pendapatan RS",
    "total_kontribusi": "Total Kontribusi",
    "luas_sqm": "Luas (m2)",
}


def _format_row_list(rows, limit=6) -> str:
    """Format daftar nomor baris Excel jadi teks ringkas, mis. '5, 8, 12, ...'."""
    rows = sorted(int(r) for r in rows)
    shown = ", ".join(str(r) for r in rows[:limit])
    return shown + (f", +{len(rows) - limit} lainnya" if len(rows) > limit else "")


def _get_merge_cell_detail(uploaded) -> str:
    try:
        uploaded.seek(0)
        filename = uploaded.name.lower()
        if filename.endswith(".xlsx"):
            from openpyxl import load_workbook
            workbook = load_workbook(uploaded, read_only=True)
            try:
                for ws in workbook.worksheets:
                    if ws.merged_cells.ranges:
                        ranges = [str(r) for r in list(ws.merged_cells.ranges)[:2]]
                        return f"Merge cells ditemukan pada sheet '{ws.title}', cell {', '.join(ranges)}. Silakan pisahkan."
            finally:
                workbook.close()
        elif filename.endswith(".xls"):
            import xlrd
            uploaded.seek(0)
            workbook = xlrd.open_workbook(file_contents=uploaded.read())
            for sheet in workbook.sheets():
                if sheet.merged_cells:
                    ranges = [f"{xlrd.formula.cellname(r[0], r[2])}:{xlrd.formula.cellname(r[1]-1, r[3]-1)}" for r in sheet.merged_cells[:2]]
                    return f"Merge cells ditemukan pada sheet '{sheet.name}', cell {', '.join(ranges)}. Silakan pisahkan."
    except Exception as exc:
        return f"Gagal membaca file: {exc}"
    return "Merge cells ditemukan pada file Excel Anda. Silakan pisahkan."


def _get_structure_detail(uploaded) -> list[str]:
    try:
        uploaded.seek(0)
        df = read_import_file(uploaded)
        df_norm = normalize_imported_data(df)
        missing = get_missing_dashboard_columns(df_norm)
        if missing:
            labels = [_REQUIRED_COLUMN_LABELS.get(col, col.upper()) for col in sorted(missing)]
            return [f"Header kolom berikut tidak ditemukan: {', '.join(labels)}."]
    except Exception as exc:
        return [f"Gagal membaca file: {exc}"]
    return ["Struktur kolom tidak sesuai template. Hindari perubahan struktur kolom."]


def _get_required_filled_detail(uploaded) -> list[str]:
    """Untuk tiap kolom wajib yang punya data kosong: sebutkan nama kolomnya
    dan nomor baris Excel-nya, sekaligus bedakan baris yang memang kosong di
    file asli dari baris yang datanya ada tapi tidak terbaca oleh proses
    pembersihan data (mis. teks di kolom angka, format tanggal yang tidak
    dikenali) — supaya user tahu harus mengisi atau memperbaiki format."""
    try:
        uploaded.seek(0)
        raw_df = read_import_file(uploaded)
        df_norm = normalize_imported_data(raw_df)
        mapping = get_column_mapping(df_norm)

        lines = []
        for col in sorted(REQUIRED_DASHBOARD_COLUMNS):
            orig_col = mapping.get(col)
            if not orig_col or orig_col not in df_norm.columns:
                continue

            series = df_norm[orig_col]
            empty_mask = series.isna()
            if series.dtype == object:
                cleaned = series.astype(str).str.strip()
                empty_mask = empty_mask | cleaned.eq("") | cleaned.str.lower().isin({"nan", "none", "nat"})
            if not empty_mask.any():
                continue

            raw_series = raw_df[orig_col] if orig_col in raw_df.columns else None
            blank_rows, invalid_rows = [], []
            for idx in df_norm.index[empty_mask]:
                excel_row = int(idx) + 2  # +1 untuk header, +1 karena index mulai dari 0
                raw_val = raw_series.loc[idx] if raw_series is not None else None
                raw_is_blank = pd.isna(raw_val) or str(raw_val).strip() == ""
                (blank_rows if raw_is_blank else invalid_rows).append(excel_row)

            label = _REQUIRED_COLUMN_LABELS.get(col, col.upper())
            parts = []
            if blank_rows:
                parts.append(f"kosong (baris {_format_row_list(blank_rows)})")
            if invalid_rows:
                parts.append(f"format tidak terbaca (baris {_format_row_list(invalid_rows)})")
            lines.append(f"{label}: {'; '.join(parts)}")

        if lines:
            return lines
    except Exception as exc:
        return [f"Gagal membaca file: {exc}"]
    return ["Kolom wajib harus terisi penuh. Pastikan tidak ada data kosong."]


def _render_ketentuan_import(validation: dict[str, bool] | None = None, is_uploaded: bool = False):
    validation = validation or {key: False for key, _ in KETENTUAN_RULES}
    uploaded = None
    if is_uploaded:
        uploader_key = f"im_uploader_refined_{st.session_state.uploader_version}"
        uploaded = st.session_state.get(uploader_key)

    items_html = ""
    from html import escape
    for key, label in KETENTUAN_RULES:
        if not is_uploaded:
            icon_class = "im-ketentuan-neutral"
            item_class = "is-neutral"
            icon = ""
            warning_html = ""
        else:
            passed = validation.get(key, False)
            if passed:
                icon_class = "im-ketentuan-check"
                item_class = "is-pass"
                icon = "✓"
                warning_html = ""
            else:
                icon_class = "im-ketentuan-fail"
                item_class = "is-fail"
                icon = "✗"
                detail_lines = []
                if uploaded:
                    if key == "format":
                        detail_lines = ["Format file tidak didukung. Gunakan .xlsx atau .xls."]
                    elif key == "size":
                        detail_lines = ["Ukuran file melebihi batas maksimal 20 MB."]
                    elif key == "merge_cell":
                        detail_lines = [_get_merge_cell_detail(uploaded)]
                    elif key == "structure":
                        detail_lines = _get_structure_detail(uploaded)
                    elif key == "required_filled":
                        detail_lines = _get_required_filled_detail(uploaded)
                if not detail_lines:
                    fallback_msgs = {
                        "format": "Format file tidak didukung. Gunakan .xlsx atau .xls.",
                        "size": "Ukuran file melebihi batas maksimal 20 MB.",
                        "merge_cell": "Merge cells ditemukan pada file Excel Anda.",
                        "structure": "Struktur kolom tidak sesuai template.",
                        "required_filled": "Kolom wajib harus terisi penuh."
                    }
                    detail_lines = [fallback_msgs.get(key, "Validasi gagal.")]

                if len(detail_lines) > 1:
                    items = "".join(f"<li>{escape(line)}</li>" for line in detail_lines)
                    warning_html = f'<div class="im-ketentuan-warning-box"><ul class="im-ketentuan-warning-list">{items}</ul></div>'
                else:
                    warning_html = f'<div class="im-ketentuan-warning-box">{escape(detail_lines[0])}</div>'

        items_html += dedent(f"""
        <div class="im-ketentuan-item {item_class}">
            <div class="im-ketentuan-row">
                <span class="{icon_class}">{icon}</span>
                <span class="im-ketentuan-text">{label}</span>
            </div>
            {warning_html}
        </div>
        """).strip()

    st.markdown(dedent(f"""
    <div class="im-panel im-ketentuan-card">
        <div class="im-ketentuan-head">
            <div class="im-section-title">Ketentuan Import</div>
        </div>
        <div class="im-ketentuan-body">{items_html}</div>
    </div>
    """).strip(), unsafe_allow_html=True)


def _render_import_history_refined():
    data = _get_refined_history_data()

    per_page = 7
    total = len(data)
    total_pages = max(1, (total + per_page - 1) // per_page)

    if "im_hist_page" not in st.session_state:
        st.session_state.im_hist_page = 1

    page = st.session_state.im_hist_page
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page
    end_idx = min(start_idx + per_page, total)
    page_data = data[start_idx:end_idx]

    # Build status badge helper
    def _hist_status(status):
        s = status.lower()
        if s == "success":
            return '<span class="im-status-badge im-status-success"><span class="status-dot"></span>Success</span>'
        elif s == "warning":
            return '<span class="im-status-badge im-status-warning"><span class="status-dot"></span>Warning</span>'
        elif s == "failed":
            return '<span class="im-status-badge im-status-failed"><span class="status-dot"></span>Failed</span>'
        elif s == "deleted":
            return '<span class="im-status-badge im-status-deleted"><span class="status-dot"></span>Deleted</span>'
        return '<span class="im-status-badge im-status-success"><span class="status-dot"></span>' + status + '</span>'

    # Build dot class
    def _dot_class(status):
        s = status.lower()
        if s == "success": return "dot-success"
        if s == "warning": return "dot-warning"
        if s == "failed": return "dot-failed"
        if s == "deleted": return "dot-deleted"
        return "dot-success"

    # Build rows
    rows_html = ""
    for r in page_data:
        rs_html = f'<span class="im-rs-total">{r["rs_total"]}</span>' if r["rs_total"] else '<span class="im-rs-empty">—</span>'
        if r["status"].lower() == "deleted":
            action_content = '<span style="color:#94a3b8;font-size:11.5px;font-weight:500;padding-left:8px;">—</span>'
        else:
            icon_view = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>'
            icon_reload = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>'
            icon_download = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>'
            icon_delete = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path><line x1="10" y1="11" x2="10" y2="17"></line><line x1="14" y1="11" x2="14" y2="17"></line></svg>'
            action_content = (
                f'<button data-im-action="view_import" data-im-id="{r["import_id"]}" class="im-action-btn" title="View">{icon_view}</button>'
                f'<button data-im-action="download_import" data-im-id="{r["import_id"]}" class="im-action-btn" title="Download">{icon_download}</button>'
                f'<button data-im-action="reload_import" data-im-id="{r["import_id"]}" class="im-action-btn" title="Reload">{icon_reload}</button>'
                f'<button data-im-action="delete_import" data-im-id="{r["import_id"]}" class="im-action-btn btn-delete" title="Delete">{icon_delete}</button>'
            )

        uploader_role_html = f'<div class="im-uploader-role">{r["role"]}</div>'
        if r["status"].lower() == "deleted" and r.get("deleted_by"):
            uploader_role_html += f'<div style="font-size:10px;color:#ef4444;font-weight:600;margin-top:1px;">Dihapus oleh: {r["deleted_by"]}</div>'

        rows_html += (
            '<tr>'
            '<td>'
            f'<div class="im-period-cell">'
            f'<span class="im-period-dot {_dot_class(r["status"])}"></span>'
            f'<span class="im-period-name">{r["period"]}</span>'
            '</div>'
            '</td>'
            '<td>'
            f'<div class="im-date-cell">'
            f'<div class="im-date-main">{r["upload_date"]}</div>'
            f'<div class="im-date-time">{r["upload_time"]}</div>'
            '</div>'
            '</td>'
            '<td>'
            f'<div class="im-uploader-cell">'
            f'<div class="im-uploader-avatar" style="background:{r["color"]};">{r["initials"]}</div>'
            '<div>'
            f'<div class="im-uploader-name">{r["uploader"]}</div>'
            f'{uploader_role_html}'
            '</div>'
            '</div>'
            '</td>'
            '<td>'
            f'<div class="im-records-val">{f"{r["total_records"]:,}".replace(",", ".")}</div>'
            '<div class="im-records-sub">rows</div>'
            '</td>'
            f'<td><span class="im-tenants-link">{f"{r["tenants"]:,}".replace(",", ".")}</span></td>'
            f'<td><span class="im-filesize">{r["file_size"]}</span></td>'
            f'<td>{rs_html}</td>'
            f'<td>{_hist_status(r["status"])}</td>'
            '<td>'
            f'<div class="im-action-btns">{action_content}</div>'
            '</td>'
            '</tr>'
        )

    if not rows_html:
        rows_html = '<tr><td colspan="9" style="text-align:center;color:#94a3b8;padding:30px;">Belum ada data import yang tersedia.</td></tr>'

    history_html = (
        '<div class="im-panel im-history">'
        '<div class="im-history-head">'
        '<div class="im-history-head-left">'
        '<div class="im-section-title">Upload History</div>'
        '<div class="im-section-sub">All import sessions — most recent first</div>'
        '</div>'
        '<div class="im-history-actions">'
        '<button data-im-action="refresh" class="im-btn-refresh">Refresh</button>'
        '<button data-im-action="clear_trash" class="im-btn-export btn-clear-trash">Clear Trash</button>'
        '</div>'
        '</div>'
        '<div style="overflow-x:auto; margin-bottom: 0px !important;">'
        '<table class="im-hist-table">'
        '<thead><tr>'
        '<th>Period</th>'
        '<th>Upload Date</th>'
        '<th>Uploaded By</th>'
        '<th>Total Records</th>'
        '<th>Tenants</th>'
        '<th>File Size</th>'
        '<th>RS Total</th>'
        '<th>Status</th>'
        '<th>Actions</th>'
        '</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        '</table>'
        '</div>'
        '</div>'
    )
    st.markdown(history_html, unsafe_allow_html=True)

    # Render standardized pagination below the table card
    st.markdown('<div class="overview-detail-pagination-footer-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    im_page_input = render_pagination(
        current_page=st.session_state.im_hist_page,
        total_pages=total_pages,
        first_item=start_idx + 1,
        last_item=end_idx,
        total_rows=total,
        sync_key="im_hist_page_sync",
    )

    if im_page_input and im_page_input.isdigit():
        new_page = int(im_page_input)
        if new_page != st.session_state.im_hist_page:
            st.session_state.im_hist_page = new_page
            st.rerun()


def _render_new_workspace():
    if "uploader_version" not in st.session_state:
        st.session_state.uploader_version = 0
    uploader_key = f"im_uploader_refined_{st.session_state.uploader_version}"

    left, right = st.columns([6, 4], gap="medium")

    # ── LEFT: three-section upload card ──
    # Section 1: HTML heading card  (border-bottom: none, top-only radius)
    # Section 2: native file uploader styled as lavender dashed drop zone
    # Section 3: hint row (negative margin-top closes the Streamlit flex gap)
    with left:
        st.markdown("""
        <div class="im-panel im-upload-shell">
            <div class="im-upload-heading">
                <div>
                    <div class="im-section-title">Upload Data File</div>
                    <div class="im-section-sub">Format yang didukung: .xlsx dan .xls (Excel).</div>
                </div>
                <button data-im-action="top_refresh" class="im-top-refresh-btn" title="Reset/Upload Another">↻</button>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Let's get the uploaded file from st.file_uploader
        # If we use a key that depends on version to reset it
        # We check if file is uploaded or not
        uploaded = st.session_state.get(uploader_key)

        if not uploaded:
            st.markdown(f"""
            <div class="im-dropzone-wrapper">
                <div class="im-dropzone-visual">
                    <div class="im-dropzone-icon-box">
                        <div class="im-dropzone-icon">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                                <line x1="12" y1="19" x2="12" y2="5"></line>
                                <polyline points="5 12 12 5 19 12"></polyline>
                            </svg>
                        </div>
                    </div>
                    <div class="im-dropzone-title">Drag & Drop Excel File</div>
                    <div class="im-dropzone-subtitle">or <span class="im-dropzone-browse">browse files</span> from your computer</div>
                    <div class="im-dropzone-badges">
                        <div class="im-dropzone-badge">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="badge-icon"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line></svg>
                            <span style="margin-left: 4px;">.xlsx / .xls supported</span>
                        </div>
                        <div class="im-dropzone-badge">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="badge-icon"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
                            <span style="margin-left: 4px;">Auto validation</span>
                        </div>
                        <div class="im-dropzone-badge">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="badge-icon"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"></path></svg>
                            <span style="margin-left: 4px;">Max file size 20 MB</span>
                        </div>
                    </div>
                </div>
                <div class="im-uploader-overlay">
            """, unsafe_allow_html=True)

            # Render uploader inside the overlay.
            # No `type=` restriction here on purpose: Streamlit silently
            # rejects mismatched files at the picker/drop level when `type`
            # is set, leaving `uploaded` as None with no visible feedback
            # (its own rejection message renders behind our invisible
            # overlay). Accepting anything and validating it ourselves below
            # lets the existing "Format file tidak didukung" error actually
            # surface to the user.
            uploaded = st.file_uploader(
                "Browse Files",
                label_visibility="collapsed",
                key=uploader_key,
            )

            st.markdown("""
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
                <div class="im-info-banner">
                    Pastikan struktur file sesuai template untuk menghindari error pada proses import.
                </div>
            """, unsafe_allow_html=True)
        else:
            validation = validate_import_upload(uploaded)
            st.session_state.im_validation = validation
            all_valid = all(validation.values())
            st.session_state.im_import_ready = all_valid

            if all_valid:
                current_sbu = st.session_state.get("im_sbu", SBU_LIST[0])
                try:
                    df_imported, missing_columns = store_shared_import(uploaded, current_sbu)
                    st.session_state.im_file = uploaded.name
                    st.session_state.im_import_ready = len(missing_columns) == 0

                    # Setiap file yang benar-benar baru dipilih di browser (bahkan
                    # kalau nama & isinya identik dengan upload sebelumnya) dapat
                    # `file_id` baru dari Streamlit — beda dengan rerun biasa saat
                    # file yang sama masih "duduk" di uploader, yang mengembalikan
                    # objek UploadedFile yang sama persis. Memakai file_id (bukan
                    # nama file) supaya re-upload file yang identik tetap memicu
                    # pengecekan duplikat ke database, bukan diam-diam dilewati.
                    current_file_id = getattr(uploaded, "file_id", uploaded.name)
                    if st.session_state.im_import_ready and st.session_state.get("im_file_attempt_id") != current_file_id:
                        success, result = _save_to_database()
                        st.session_state.im_file_attempt_id = current_file_id
                        st.session_state.im_last_save_ok = success
                        st.session_state.im_last_save_result = result
                        if result.get("severity") != "success":
                            _render_save_result_notice(result)
                    elif st.session_state.get("im_last_save_ok") is False:
                        # File yang sama masih terpilih dan percobaan simpan
                        # sebelumnya gagal (duplikat) — tampilkan lagi errornya
                        # secara konsisten, bukannya diam saja seolah berhasil.
                        last_result = st.session_state.get("im_last_save_result")
                        if last_result:
                            _render_save_result_notice(last_result)

                    total_records = len(df_imported)
                    
                    # Calculate dynamic warnings based on logic:
                    # check for 0 or negative real_omzet and empty cells
                    warnings = 0
                    if "real_omzet" in df_imported.columns:
                        warnings += int((df_imported["real_omzet"] <= 0).sum())
                    
                    null_counts = df_imported.isnull().sum().sum()
                    warnings += int(null_counts)
                    
                    # Capping warnings if they exceed record count for safety
                    warnings = min(warnings, total_records)
                    valid_records = max(0, total_records - warnings)
                    score = int((valid_records / total_records) * 100) if total_records > 0 else 100

                    success_html = (
                        '<div class="im-success-visual">'
                        '<div class="im-success-icon-box">'
                        '<div class="im-success-icon">✓</div>'
                        '</div>'
                        '<div class="im-success-title">Upload Successful!</div>'
                        f'<div class="im-success-subtitle">{uploaded.name} · {total_records:,} records processed</div>'
                        '<div class="im-progress-bar-container">'
                        '<div class="im-progress-bar-fill"></div>'
                        '</div>'
                        '<div class="im-success-details">'
                        '<div class="im-stats-row">'
                        f'<div class="im-stat-card stat-records"><div class="stat-value">{total_records:,}</div><div class="stat-label">Records</div></div>'
                        f'<div class="im-stat-card stat-valid"><div class="stat-value">{valid_records:,}</div><div class="stat-label">Valid</div></div>'
                        f'<div class="im-stat-card stat-warnings"><div class="stat-value">{warnings:,}</div><div class="stat-label">Warnings</div></div>'
                        f'<div class="im-stat-card stat-score"><div class="stat-value">{score}%</div><div class="stat-label">Score</div></div>'
                        '</div>'
                        '</div>'
                        '</div>'
                    )

                    # Jangan tampilkan kartu "Upload Successful" kalau file ini
                    # justru gagal/tidak tersimpan ke database (mis. duplikat) —
                    # kartu hijau ini dulu selalu muncul terlepas dari hasil
                    # simpan yang sebenarnya, jadi tampak seolah upload berhasil
                    # padahal datanya tidak masuk.
                    if st.session_state.get("im_last_save_ok") is not False:
                        st.markdown(success_html, unsafe_allow_html=True)

                except Exception as exc:
                    st.error(f"Gagal memproses file: {exc}")
                    all_valid = False

            if not all_valid:
                # Render the drag & drop zone in failed visual state, keeping it interactive
                st.markdown(f"""
                <div class="im-dropzone-wrapper">
                    <div class="im-dropzone-visual">
                        <div class="im-dropzone-icon-box">
                            <div class="im-dropzone-icon">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
                                    <line x1="12" y1="19" x2="12" y2="5"></line>
                                    <polyline points="5 12 12 5 19 12"></polyline>
                                </svg>
                            </div>
                        </div>
                        <div class="im-dropzone-title">Drag & Drop Excel File</div>
                        <div class="im-dropzone-subtitle" style="margin-bottom: 12px;">File Terunggah: <strong>{uploaded.name}</strong></div>
                        <div class="im-validation-error-card">
                            <div class="im-validation-error-title">Kesalahan Validasi File</div>
                            <div class="im-validation-error-desc">Silakan perbaiki kesalahan di bawah ini sebelum mengunggah kembali.</div>
                        </div>
                    </div>
                    <div class="im-uploader-overlay">
                """, unsafe_allow_html=True)

                # Render the overlay file uploader so they can drop a new file.
                # No `type=` restriction — see comment on the other
                # file_uploader call above for why.
                st.file_uploader(
                    "Browse Files",
                    label_visibility="collapsed",
                    key=uploader_key,
                )

                st.markdown("""
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("""
                    <div class="im-info-banner">
                        Pastikan struktur file sesuai template untuk menghindari error pada proses import.
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── RIGHT: Ketentuan Import (white card) ──
    with right:
        is_uploaded = st.session_state.get(uploader_key) is not None
        _render_ketentuan_import(st.session_state.get("im_validation"), is_uploaded=is_uploaded)

    # ── Riwayat Import table ──
    _render_import_history_refined()


def _patch_upload_limit_text():
    components.html(
        """
        <script>
        (function () {
            try {
                const doc = window.parent.document;
                const win = window.parent;

                // Suppress browser default navigation on real OS file drag-and-drop
                if (!win.__imDragGuardInstalled) {
                    win.__imDragGuardInstalled = true;
                    ["dragover", "drop"].forEach((evtName) => {
                        win.addEventListener(evtName, (e) => {
                            if (!e.target.closest('[data-testid="stFileUploaderDropzone"]')) {
                                e.preventDefault();
                            }
                        }, false);
                    });
                }

                function patchUploadLimit() {
                    try {
                        doc.querySelectorAll('[data-testid="stFileUploader"]').forEach((uploader) => {
                            uploader.classList.add('im-refined-uploader');

                            const walker = doc.createTreeWalker(uploader, NodeFilter.SHOW_TEXT);
                            let node = walker.nextNode();
                            while (node) {
                                if (/200\\s*MB/i.test(node.nodeValue || '')) {
                                    node.nodeValue = (node.nodeValue || '').replace(/200\\s*MB/gi, '20MB');
                                }
                                node = walker.nextNode();
                            }
                        });
                    } catch (err) {
                        console.error("[ImportManager] Error in patchUploadLimit:", err);
                    }
                }



                function triggerAction(actionName) {
                    try {
                        const input = doc.querySelector('input[placeholder="__im_action_trigger__"]');
                        if (!input) return;

                        input.focus();

                        let prototype = Object.getPrototypeOf(input);
                        let nativeSetter = null;
                        while (prototype) {
                            const desc = Object.getOwnPropertyDescriptor(prototype, 'value');
                            if (desc && desc.set) {
                                nativeSetter = desc.set;
                                break;
                            }
                            prototype = Object.getPrototypeOf(prototype);
                        }

                        if (nativeSetter) {
                            nativeSetter.call(input, actionName);
                        } else {
                            input.value = actionName;
                        }

                        const tracker = input._valueTracker;
                        if (tracker) {
                            tracker.setValue('');
                        }

                        input.dispatchEvent(new Event('input', { bubbles: true }));
                        input.dispatchEvent(new Event('change', { bubbles: true }));

                        input.dispatchEvent(new KeyboardEvent('keydown', {
                            key: 'Enter',
                            code: 'Enter',
                            keyCode: 13,
                            which: 13,
                            bubbles: true
                        }));

                        input.blur();
                    } catch (err) {
                        console.error("[ImportManager] Error sending action to Python:", err);
                    }
                }

                function handleActionClick(e) {
                    try {
                        const btn = e.target.closest('[data-im-action]');
                        if (!btn) return;

                        e.preventDefault();
                        e.stopPropagation();

                        const action = btn.getAttribute('data-im-action');
                        const id = btn.getAttribute('data-im-id') || '';
                        const triggerValue = id ? (action + ':' + id) : action;

                        console.log("[ImportManager] Action intercepted:", triggerValue);
                        triggerAction(triggerValue);
                    } catch (err) {
                        console.error("[ImportManager] Error during action click interception:", err);
                    }
                }

                // Safely install/re-install the click listener to prevent duplicate / stale handlers
                if (win.__imActionHandler) {
                    doc.removeEventListener('click', win.__imActionHandler, true);
                }
                win.__imActionHandler = handleActionClick;
                doc.addEventListener('click', win.__imActionHandler, true);

                function hideActionTriggerInput() {
                    try {
                        const input = doc.querySelector('input[placeholder="__im_action_trigger__"]');
                        if (input) {
                            const container = input.closest('[data-testid="stElementContainer"]');
                            if (container) {
                                container.style.position = 'fixed';
                                container.style.top = '-9999px';
                                container.style.left = '-9999px';
                                container.style.width = '1px';
                                container.style.height = '1px';
                                container.style.overflow = 'hidden';
                                container.style.opacity = '0';
                                container.style.pointerEvents = 'none';
                            }
                        }
                    } catch (err) {
                        console.error("[ImportManager] Error in hideActionTriggerInput:", err);
                    }
                }

                function checkModalClosure() {
                    try {
                        const modal = doc.querySelector('[data-testid="stModal"]');
                        if (modal) {
                            win.__imModalWasOpen = true;
                        } else if (win.__imModalWasOpen) {
                            win.__imModalWasOpen = false;
                            console.log("[ImportManager] Modal closure detected.");
                            triggerAction("close_dialog");
                        }
                    } catch (err) {
                        console.error("[ImportManager] Error checking modal closure:", err);
                    }
                }

                patchUploadLimit();
                hideActionTriggerInput();

                const observer = new MutationObserver(() => {
                    patchUploadLimit();
                    hideActionTriggerInput();
                    checkModalClosure();
                });

                observer.observe(doc.body, {
                    childList: true,
                    subtree: true,
                    characterData: true,
                });
            } catch (globalErr) {
                console.error("[ImportManager] Global initialization error:", globalErr);
            }
        })();
        </script>
        """,
        height=0,
        width=0,
    )


_DIALOG_ACTIONS = {"view_import", "download_import", "delete_import", "clear_trash"}


def render_import_manager():
    _init_state()

    # ── Route actions ──────────────────────────────────────────────────────────
    # Prefer JS-triggered pending action (no page reload); fall back to query params
    # (kept for backward compatibility with direct URL navigation).
    _pending = st.session_state.get("_im_action_pending", "")
    if _pending:
        del st.session_state["_im_action_pending"]
        action, _, import_id = _pending.partition(":")
    else:
        action = st.query_params.get("action", "")
        import_id = st.query_params.get("import_id", "")

    if action == "refresh":
        if "action" in st.query_params:
            del st.query_params["action"]
        st.rerun()
    elif action == "top_refresh":
        st.session_state.uploader_version = st.session_state.get("uploader_version", 0) + 1
        if SHARED_DATA_KEY in st.session_state:
            del st.session_state[SHARED_DATA_KEY]
        if SHARED_META_KEY in st.session_state:
            del st.session_state[SHARED_META_KEY]
        st.session_state.im_file = None
        st.session_state.im_import_ready = False
        st.session_state.im_validation = {key: False for key, _ in KETENTUAN_RULES}
        st.session_state.pop("im_file_attempt_id", None)
        st.session_state.pop("im_last_save_ok", None)
        st.session_state.pop("im_last_save_result", None)
        st.rerun()
    elif action == "close_dialog":
        st.session_state["_im_open_dialog"] = None
        st.rerun()
    elif action == "reload_import" and import_id:
        try:
            execute_reload_import(int(import_id))
        except Exception:
            pass
        if "action" in st.query_params:
            del st.query_params["action"]
        if "import_id" in st.query_params:
            del st.query_params["import_id"]
    elif action in _DIALOG_ACTIONS:
        # Dialogs must be re-invoked on every rerun to stay open (Streamlit
        # closes a dialog the moment its opening call is skipped on a rerun,
        # which is exactly what happened when this was a one-shot trigger:
        # the very next rerun — e.g. clicking a button inside the dialog —
        # didn't call the dialog function again, so it vanished instantly).
        st.session_state["_im_open_dialog"] = (action, import_id)
        if "action" in st.query_params:
            del st.query_params["action"]
        if "import_id" in st.query_params:
            del st.query_params["import_id"]

    # Re-open whichever dialog is currently active on every rerun, until a
    # dialog handler explicitly clears "_im_open_dialog".
    _open = st.session_state.get("_im_open_dialog")
    if _open:
        d_action, d_id = _open
        try:
            if d_action == "view_import":
                show_import_details_dialog(int(d_id))
            elif d_action == "download_import":
                show_download_dialog(int(d_id))
            elif d_action == "delete_import":
                show_delete_confirm_dialog(int(d_id))
            elif d_action == "clear_trash":
                show_clear_trash_dialog()
        except Exception:
            st.session_state["_im_open_dialog"] = None

    st.markdown('<div class="overview-page-marker im-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    st.markdown(_PAGE_CSS, unsafe_allow_html=True)
    st.markdown(_REFINED_IMPORT_CSS, unsafe_allow_html=True)
    st.markdown(_NEW_DESIGN_CSS, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="ov-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_im_page_header_html(), unsafe_allow_html=True)
        st.markdown('<div class="ov-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="ov-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)
    _mount_im_fixed_header()

    st.markdown('<div class="im-manager-surface">', unsafe_allow_html=True)
    _render_new_workspace()
    st.markdown('</div>', unsafe_allow_html=True)
    _patch_upload_limit_text()

    # ── JS-action bridge ──────────────────────────────────────────────────────
    # Hidden text input placed LAST so it renders after all CSS (no flash).
    # The CSS rule in _REFINED_IMPORT_CSS and the JS in _patch_upload_limit_text
    # both hide it. The callback is called inline when st.text_input runs and
    # the widget value changed; it then calls st.rerun() so the NEXT run routes
    # the action (via _im_action_pending) without any extra elements at the top
    # of the page that would disturb the layout.
    def _on_action_trigger_change():
        val = st.session_state.get("im_js_action_trigger", "")
        if val:
            st.session_state["_im_action_pending"] = val
            st.session_state["im_js_action_trigger"] = ""
            st.rerun()

    st.text_input(
        "im_action",
        key="im_js_action_trigger",
        label_visibility="collapsed",
        placeholder="__im_action_trigger__",
        on_change=_on_action_trigger_change,
    )


@st.dialog("Detail Data Import", width="large")
def show_import_details_dialog(import_id):
    from .connection import get_engine
    from sqlalchemy import text
    import pandas as pd
    
    st.write(f"Menampilkan data transaksi untuk **Import ID: {import_id}**")
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            meta = pd.read_sql(
                text("SELECT filename, periode, uploaded_by, uploaded_at FROM import_history WHERE import_id = :import_id"),
                conn,
                params={"import_id": import_id}
            )
            df = pd.read_sql(
                text("""
                    SELECT document_date, masa_jasa, tahun, perusahaan, brand, perimeter_spending_pax,
                           kode_ruang, pic, ro_number, terminal, sub_terminal, area, lokasi, lantai, gate,
                           smoking_status, sub_bidang_usaha, bidang_usaha, coa, nomor_kontrak_sistem,
                           nomor_kontrak_legal, start_kontrak, end_kontrak, csp_non_csp, kerja_sama,
                           pemilihan_mitra_usaha, produksi_m2, tarif_sewa_ruang_m2, rs_percent, min_omzet,
                           real_omzet, mgrs_per_pax, real_pax, pendapatan_rs, pendapatan_sewa, total_kontribusi,
                           acv, rev_per_sqm, spending_per_pax, doc_number_rs, doc_number_sewa, variant_no,
                           catatan, trafik_int_arr, trafik_int_dep, subtotal_trafik_int, trafik_dom_arr,
                           trafik_dom_dep, subtotal_trafik_dom, total_trafik
                    FROM transaction_revenue
                    WHERE import_id = :import_id
                """),
                conn,
                params={"import_id": import_id}
            )
            
        if meta.empty:
            st.error("Data riwayat import tidak ditemukan.")
            return
            
        row = meta.iloc[0]
        st.markdown(f"""
        **File:** `{row.get('filename')}` | **Uploader:** `{row.get('uploaded_by')}` | **Tanggal:** `{row.get('uploaded_at')}`
        """)
        
        if df.empty:
            st.warning("Tidak ada transaksi untuk import ini.")
        else:
            for col in ["document_date", "start_kontrak", "end_kontrak"]:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: pd.to_datetime(x).strftime("%Y-%m-%d") if pd.notna(x) else "-")
            if "masa_jasa" in df.columns:
                df["masa_jasa"] = df["masa_jasa"].apply(lambda x: pd.to_datetime(x).strftime("%b-%y") if pd.notna(x) else "-")
            df = df.fillna("-").replace({None: "-", "None": "-", "nan": "-", "NaN": "-"})
            
            rename_map = {
                "document_date": "DOCUMENT DATE",
                "masa_jasa": "MASA",
                "tahun": "TAHUN",
                "perusahaan": "PERUSAHAAN",
                "brand": "BRAND",
                "perimeter_spending_pax": "PERIMETER / SPENDING / PAX",
                "kode_ruang": "KODE RUANG",
                "pic": "PIC",
                "ro_number": "RO NUMBER",
                "terminal": "TERMINAL",
                "sub_terminal": "SUB TERMINAL",
                "area": "AREA",
                "lokasi": "LOKASI",
                "lantai": "LANTAI",
                "gate": "GATE",
                "smoking_status": "SMOKING STATUS",
                "sub_bidang_usaha": "SUB BIDANG USAHA",
                "bidang_usaha": "BIDANG USAHA",
                "coa": "COA",
                "nomor_kontrak_sistem": "NOMOR KONTRAK SISTEM (SAP)",
                "nomor_kontrak_legal": "NOMOR KONTRAK LEGAL",
                "start_kontrak": "START KONTRAK",
                "end_kontrak": "END KONTRAK",
                "csp_non_csp": "CSP / NON-CSP",
                "kerja_sama": "KERJA SAMA",
                "pemilihan_mitra_usaha": "PEMILIHAN MITRA USAHA",
                "produksi_m2": "PRODUKSI (M2)",
                "tarif_sewa_ruang_m2": "TARIF SEWA RUANG / M2",
                "rs_percent": "% RS",
                "min_omzet": "MIN OMZET",
                "real_omzet": "REAL OMZET",
                "mgrs_per_pax": "MGRS / PAX",
                "real_pax": "REAL PAX",
                "pendapatan_rs": "PENDAPATAN RS",
                "pendapatan_sewa": "PENDAPATAN SEWA",
                "total_kontribusi": "TOTAL KONTRIBUSI",
                "acv": "ACV",
                "rev_per_sqm": "REV / SQM",
                "spending_per_pax": "SPENDING / PAX",
                "doc_number_rs": "DOC. NUMBER RS",
                "doc_number_sewa": "DOC. NUMBER SEWA",
                "variant_no": "VARIANT NO",
                "catatan": "CATATAN",
                "trafik_int_arr": "TRAFIK INT ARR",
                "trafik_int_dep": "TRAFIK INT DEP",
                "subtotal_trafik_int": "SUBTOTAL TRAFIK INT",
                "trafik_dom_arr": "TRAFIK DOM ARR",
                "trafik_dom_dep": "TRAFIK DOM DEP",
                "subtotal_trafik_dom": "SUBTOTAL TRAFIK DOM",
                "total_trafik": "TOTAL TRAFIK",
            }
            df = df.rename(columns=rename_map)
            
            template_order = [
                "DOCUMENT DATE", "MASA", "TAHUN", "PERUSAHAAN", "BRAND", "PERIMETER / SPENDING / PAX",
                "KODE RUANG", "PIC", "RO NUMBER", "TERMINAL", "SUB TERMINAL", "AREA", "LOKASI", "LANTAI",
                "GATE", "SMOKING STATUS", "SUB BIDANG USAHA", "BIDANG USAHA", "COA",
                "NOMOR KONTRAK SISTEM (SAP)", "NOMOR KONTRAK LEGAL", "START KONTRAK", "END KONTRAK",
                "CSP / NON-CSP", "KERJA SAMA", "PEMILIHAN MITRA USAHA", "PRODUKSI (M2)", "TARIF SEWA RUANG / M2",
                "% RS", "MIN OMZET", "REAL OMZET", "MGRS / PAX", "REAL PAX", "PENDAPATAN RS", "PENDAPATAN SEWA",
                "TOTAL KONTRIBUSI", "ACV", "REV / SQM", "SPENDING / PAX", "DOC. NUMBER RS", "DOC. NUMBER SEWA",
                "VARIANT NO", "CATATAN", "TRAFIK INT ARR", "TRAFIK INT DEP", "SUBTOTAL TRAFIK INT",
                "TRAFIK DOM ARR", "TRAFIK DOM DEP", "SUBTOTAL TRAFIK DOM", "TOTAL TRAFIK"
            ]
            df = df[[col for col in template_order if col in df.columns]]
            st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error(f"Gagal mengambil detail data: {e}")


@st.dialog("Unduh Data Import")
def show_download_dialog(import_id):
    from .connection import get_engine
    from sqlalchemy import text
    import pandas as pd
    import io
    
    st.write(f"Mempersiapkan unduhan untuk **Import ID: {import_id}**...")
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            meta = pd.read_sql(
                text("SELECT filename FROM import_history WHERE import_id = :import_id"),
                conn,
                params={"import_id": import_id}
            )
            df = pd.read_sql(
                text("""
                    SELECT document_date, masa_jasa, tahun, perusahaan, brand, perimeter_spending_pax,
                           kode_ruang, pic, ro_number, terminal, sub_terminal, area, lokasi, lantai, gate,
                           smoking_status, sub_bidang_usaha, bidang_usaha, coa, nomor_kontrak_sistem,
                           nomor_kontrak_legal, start_kontrak, end_kontrak, csp_non_csp, kerja_sama,
                           pemilihan_mitra_usaha, produksi_m2, tarif_sewa_ruang_m2, rs_percent, min_omzet,
                           real_omzet, mgrs_per_pax, real_pax, pendapatan_rs, pendapatan_sewa, total_kontribusi,
                           acv, rev_per_sqm, spending_per_pax, doc_number_rs, doc_number_sewa, variant_no,
                           catatan, trafik_int_arr, trafik_int_dep, subtotal_trafik_int, trafik_dom_arr,
                           trafik_dom_dep, subtotal_trafik_dom, total_trafik
                    FROM transaction_revenue
                    WHERE import_id = :import_id
                """),
                conn,
                params={"import_id": import_id}
            )
            
        if df.empty:
            st.error("Data tidak ditemukan atau kosong.")
            return
            
        filename = meta.iloc[0]["filename"] if not meta.empty else f"import_{import_id}.xlsx"
        if not filename.endswith((".xlsx", ".xls")):
            filename = f"{filename}.xlsx"
            
        for col in ["document_date", "start_kontrak", "end_kontrak"]:
            if col in df.columns:
                df[col] = df[col].apply(lambda x: pd.to_datetime(x).strftime("%Y-%m-%d") if pd.notna(x) else "-")
        if "masa_jasa" in df.columns:
            df["masa_jasa"] = df["masa_jasa"].apply(lambda x: pd.to_datetime(x).strftime("%b-%y") if pd.notna(x) else "-")
        df = df.fillna("-").replace({None: "-", "None": "-", "nan": "-", "NaN": "-"})
        
        rename_map = {
            "document_date": "DOCUMENT DATE",
            "masa_jasa": "MASA",
            "tahun": "TAHUN",
            "perusahaan": "PERUSAHAAN",
            "brand": "BRAND",
            "perimeter_spending_pax": "PERIMETER / SPENDING / PAX",
            "kode_ruang": "KODE RUANG",
            "pic": "PIC",
            "ro_number": "RO NUMBER",
            "terminal": "TERMINAL",
            "sub_terminal": "SUB TERMINAL",
            "area": "AREA",
            "lokasi": "LOKASI",
            "lantai": "LANTAI",
            "gate": "GATE",
            "smoking_status": "SMOKING STATUS",
            "sub_bidang_usaha": "SUB BIDANG USAHA",
            "bidang_usaha": "BIDANG USAHA",
            "coa": "COA",
            "nomor_kontrak_sistem": "NOMOR KONTRAK SISTEM (SAP)",
            "nomor_kontrak_legal": "NOMOR KONTRAK LEGAL",
            "start_kontrak": "START KONTRAK",
            "end_kontrak": "END KONTRAK",
            "csp_non_csp": "CSP / NON-CSP",
            "kerja_sama": "KERJA SAMA",
            "pemilihan_mitra_usaha": "PEMILIHAN MITRA USAHA",
            "produksi_m2": "PRODUKSI (M2)",
            "tarif_sewa_ruang_m2": "TARIF SEWA RUANG / M2",
            "rs_percent": "% RS",
            "min_omzet": "MIN OMZET",
            "real_omzet": "REAL OMZET",
            "mgrs_per_pax": "MGRS / PAX",
            "real_pax": "REAL PAX",
            "pendapatan_rs": "PENDAPATAN RS",
            "pendapatan_sewa": "PENDAPATAN SEWA",
            "total_kontribusi": "TOTAL KONTRIBUSI",
            "acv": "ACV",
            "rev_per_sqm": "REV / SQM",
            "spending_per_pax": "SPENDING / PAX",
            "doc_number_rs": "DOC. NUMBER RS",
            "doc_number_sewa": "DOC. NUMBER SEWA",
            "variant_no": "VARIANT NO",
            "catatan": "CATATAN",
            "trafik_int_arr": "TRAFIK INT ARR",
            "trafik_int_dep": "TRAFIK INT DEP",
            "subtotal_trafik_int": "SUBTOTAL TRAFIK INT",
            "trafik_dom_arr": "TRAFIK DOM ARR",
            "trafik_dom_dep": "TRAFIK DOM DEP",
            "subtotal_trafik_dom": "SUBTOTAL TRAFIK DOM",
            "total_trafik": "TOTAL TRAFIK",
        }
        df = df.rename(columns=rename_map)
        
        template_order = [
            "DOCUMENT DATE", "MASA", "TAHUN", "PERUSAHAAN", "BRAND", "PERIMETER / SPENDING / PAX",
            "KODE RUANG", "PIC", "RO NUMBER", "TERMINAL", "SUB TERMINAL", "AREA", "LOKASI", "LANTAI",
            "GATE", "SMOKING STATUS", "SUB BIDANG USAHA", "BIDANG USAHA", "COA",
            "NOMOR KONTRAK SISTEM (SAP)", "NOMOR KONTRAK LEGAL", "START KONTRAK", "END KONTRAK",
            "CSP / NON-CSP", "KERJA SAMA", "PEMILIHAN MITRA USAHA", "PRODUKSI (M2)", "TARIF SEWA RUANG / M2",
            "% RS", "MIN OMZET", "REAL OMZET", "MGRS / PAX", "REAL PAX", "PENDAPATAN RS", "PENDAPATAN SEWA",
            "TOTAL KONTRIBUSI", "ACV", "REV / SQM", "SPENDING / PAX", "DOC. NUMBER RS", "DOC. NUMBER SEWA",
            "VARIANT NO", "CATATAN", "TRAFIK INT ARR", "TRAFIK INT DEP", "SUBTOTAL TRAFIK INT",
            "TRAFIK DOM ARR", "TRAFIK DOM DEP", "SUBTOTAL TRAFIK DOM", "TOTAL TRAFIK"
        ]
        df = df[[col for col in template_order if col in df.columns]]
        
        towrite = io.BytesIO()
        with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Data Revenue")
        towrite.seek(0)
        
        st.markdown(f"""
        <div class="im-dl-success">
            <div class="im-dl-success-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
            </div>
            <div class="im-dl-success-text">
                <div class="im-dl-success-title">File Excel berhasil dibuat!</div>
                <div class="im-dl-success-sub">{filename} &middot; {len(df)} baris data</div>
            </div>
        </div>
        <style>
        .im-dl-success {{
            display: flex;
            align-items: center;
            gap: 12px;
            background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.08) 100%);
            border: 1px solid rgba(99,102,241,0.18);
            border-radius: 12px;
            padding: 14px 16px;
            margin: 4px 0 18px 0;
        }}
        .im-dl-success-icon {{
            flex: 0 0 auto;
            width: 36px;
            height: 36px;
            border-radius: 50%;
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            color: #fff;
            box-shadow: 0 3px 10px rgba(99,102,241,0.35);
        }}
        .im-dl-success-icon svg {{ width: 18px; height: 18px; }}
        .im-dl-success-title {{
            font-size: 13.5px;
            font-weight: 700;
            color: #1e1b4b;
        }}
        .im-dl-success-sub {{
            font-size: 12px;
            color: #64748b;
            margin-top: 2px;
        }}
        div[data-testid="stDialog"] div[data-testid="stDownloadButton"] > button {{
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 8px !important;
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 10px !important;
            height: 42px !important;
            font-size: 14px !important;
            font-weight: 600 !important;
            box-shadow: 0 4px 14px rgba(99,102,241,0.30) !important;
            transition: all 0.15s ease-in-out !important;
        }}
        div[data-testid="stDialog"] div[data-testid="stDownloadButton"] > button:hover {{
            box-shadow: 0 6px 18px rgba(99,102,241,0.42) !important;
            transform: translateY(-1px) !important;
        }}
        div[data-testid="stDialog"] div[data-testid="stDownloadButton"] > button::before {{
            content: "" !important;
            display: inline-block !important;
            width: 16px !important;
            height: 16px !important;
            background-color: #ffffff !important;
            -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 384 512'%3E%3Cpath d='M0 64C0 28.7 28.7 0 64 0H224V128c0 17.7 14.3 32 32 32H384V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zM384 128H256V0L384 128zM216 232c0-13.3-10.7-24-24-24s-24 10.7-24 24v99.9l-31-31c-9.4-9.4-24.6-9.4-33.9 0s-9.4 24.6 0 33.9l72 72c9.4 9.4 24.6 9.4 33.9 0l72-72c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-31 31V232z'/%3E%3C/svg%3E") no-repeat center / contain !important;
            mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 384 512'%3E%3Cpath d='M0 64C0 28.7 28.7 0 64 0H224V128c0 17.7 14.3 32 32 32H384V448c0 35.3-28.7 64-64 64H64c-35.3 0-64-28.7-64-64V64zM384 128H256V0L384 128zM216 232c0-13.3-10.7-24-24-24s-24 10.7-24 24v99.9l-31-31c-9.4-9.4-24.6-9.4-33.9 0s-9.4 24.6 0 33.9l72 72c9.4 9.4 24.6 9.4 33.9 0l72-72c9.4-9.4 9.4-24.6 0-33.9s-24.6-9.4-33.9 0l-31 31V232z'/%3E%3C/svg%3E") no-repeat center / contain !important;
        }}
        </style>
        """, unsafe_allow_html=True)

        st.download_button(
            label="Download File Excel",
            data=towrite,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Gagal memproses unduhan: {e}")


@st.dialog("Hapus Data Import")
def show_delete_confirm_dialog(import_id):
    from .connection import get_engine
    from sqlalchemy import text
    import pandas as pd
    import time
    
    try:
        engine = get_engine()
        with engine.connect() as conn:
            meta = pd.read_sql(
                text("SELECT filename FROM import_history WHERE import_id = :import_id"),
                conn,
                params={"import_id": import_id}
            )
        filename = meta.iloc[0]["filename"] if not meta.empty else f"ID {import_id}"
        
        st.warning(f"Apakah Anda yakin ingin menghapus data import dari file **{filename}**?")
        st.write("Tindakan ini akan menghapus semua data transaksi yang terkait dan tidak dapat dibatalkan.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Ya, Hapus Data", use_container_width=True, type="primary"):
                with engine.begin() as trans_conn:
                    try:
                        trans_conn.execute(text("ALTER TABLE import_history ADD COLUMN IF NOT EXISTS deleted_by VARCHAR(255)"))
                    except Exception:
                        pass
                    trans_conn.execute(
                        text("DELETE FROM transaction_revenue WHERE import_id = :import_id"),
                        {"import_id": import_id}
                    )
                    trans_conn.execute(
                        text("UPDATE import_history SET is_active = false, status = 'Deleted', deleted_by = :deleted_by WHERE import_id = :import_id"),
                        {
                            "import_id": import_id,
                            "deleted_by": st.session_state.get("user_name", "Operational User")
                        }
                    )
                st.cache_data.clear()
                st.session_state.pop("shared_import_df", None)
                st.session_state.pop("shared_import_meta", None)
                st.session_state.pop("shared_import_mapping", None)
                st.session_state["_im_open_dialog"] = None
                st.success("Data berhasil dihapus!")
                time.sleep(1)
                st.rerun()
        with col2:
            if st.button("Batal", use_container_width=True):
                st.session_state["_im_open_dialog"] = None
                st.rerun()
    except Exception as e:
        st.error(f"Gagal menghapus data: {e}")


def execute_reload_import(import_id):
    from .connection import get_engine
    from sqlalchemy import text
    import time
    
    st.toast(f"Memulai memuat ulang data untuk Import ID: {import_id}...", icon="🔄")
    try:
        engine = get_engine()
        with engine.begin() as conn:
            conn.execute(
                text("UPDATE import_history SET status = 'Success' WHERE import_id = :import_id"),
                {"import_id": import_id}
            )
        st.cache_data.clear()
        st.success("Data berhasil dimuat ulang!")
        time.sleep(0.5)
        st.rerun()
    except Exception as e:
        st.error(f"Gagal memuat ulang data: {e}")


@st.dialog("Hapus Semua Riwayat Deleted")
def show_clear_trash_dialog():
    from .connection import get_engine
    from sqlalchemy import text
    import time
    
    st.warning("Apakah Anda yakin ingin menghapus permanen semua riwayat file yang sudah di-delete?")
    st.write("Tindakan ini akan membersihkan log riwayat 'Deleted' dari database secara permanen.")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Ya, Bersihkan", use_container_width=True, type="primary"):
            try:
                engine = get_engine()
                with engine.begin() as conn:
                    conn.execute(
                        text("DELETE FROM import_history WHERE status = 'Deleted' OR COALESCE(is_active, true) = false")
                    )
                st.cache_data.clear()
                st.session_state["_im_open_dialog"] = None
                st.success("Riwayat berhasil dibersihkan!")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Gagal membersihkan: {e}")
    with col2:
        if st.button("Batal", use_container_width=True):
            st.session_state["_im_open_dialog"] = None
            st.rerun()


if __name__ == "__main__":
    st.set_page_config(page_title="Data Import Manager", layout="wide")
    render_import_manager()
