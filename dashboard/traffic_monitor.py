"""Dasbor Pemantau Trafik — Modul Orkestrator."""

import streamlit as st
import pandas as pd
from .export_utils import EXCEL_MIME, dataframe_to_excel_bytes
from .enterprise_ui import section_title_html, table_inner_html

# Impor logika pemrosesan data
from .traffic_data import (
    get_traffic_monitor_data,
    _aggregate_metrics,
    get_monthly_traffic_trend,
    get_domestic_intl_monthly,
    get_spp_monthly,
    get_terminal_table_df,
    _fmt_millions,
    _fmt_pax_short,
    _fmt_rp_k,
    TM_YEAR_OPTIONS,
    TM_MONTH_OPTIONS,
    TM_TERMINAL_OPTIONS,
)

# Impor logika presentasi antarmuka (UI)
from .traffic_ui import (
    _inject_tm_css,
    _tm_page_header,
    _render_tm_filter_card,
    _mount_tm_fixed_header,
    _tm_kpi_card,
    _mini_metric_box,
    _traffic_trend_figure,
    _dom_intl_figure,
    _spp_trend_figure,
    _terminal_card_html,
    _donut_figure,
    _yoy_bar_figure,
    _insight_card_html,
    donut_legend_html,
    TM_DONUT_COLORS,
    _month_short,
)

def page_traffic_monitor(df_raw=None):
    # Ambil data trafik bersih yang ternormalisasi dari sumber
    data_df = get_traffic_monitor_data(df_raw)

    # Inisialisasi state filter terapan jika belum ada
    for key, default in [
        ("tm_year", "All Year"),
        ("tm_month", "All Month"),
        ("tm_terminal", "All Terminal"),
    ]:
        if key not in st.session_state:
            st.session_state[key] = default

    # Inisialisasi state filter sementara (draf) jika belum ada
    for pend_key, applied_key in (
        ("tm_pend_terminal", "tm_terminal"), ("tm_pend_year", "tm_year"), ("tm_pend_month", "tm_month"),
    ):
        if pend_key not in st.session_state:
            st.session_state[pend_key] = st.session_state[applied_key]

    # Validasi agar pilihan state sesuai dengan daftar opsi yang tersedia
    if st.session_state.tm_year not in TM_YEAR_OPTIONS:
        st.session_state.tm_year = "All Year"
    if st.session_state.tm_month not in TM_MONTH_OPTIONS:
        st.session_state.tm_month = "All Month"
    if st.session_state.tm_terminal not in TM_TERMINAL_OPTIONS:
        st.session_state.tm_terminal = "All Terminal"

    # Ambil statistik agregat dan tren waktu berdasarkan filter
    metrics = _aggregate_metrics(
        data_df,
        st.session_state.tm_year,
        st.session_state.tm_month,
        st.session_state.tm_terminal,
    )
    trend_df = get_monthly_traffic_trend(data_df, st.session_state.tm_year, st.session_state.tm_terminal)
    dom_intl_df = get_domestic_intl_monthly(data_df, st.session_state.tm_year, st.session_state.tm_terminal)
    spp_df = get_spp_monthly(data_df, st.session_state.tm_year, st.session_state.tm_terminal)

    current_year_label = f"FY {metrics['current_year']}" if metrics["current_year"] else "Current"
    prior_year_label = f"FY {metrics['prior_year']}" if metrics["prior_year"] else "Prior"
    scope_label = metrics["terminal_label"]

    # Hitung jumlah filter aktif untuk ditampilkan di badge UI
    active_count = sum([
        st.session_state.get("tm_year", "All Year") != "All Year",
        st.session_state.get("tm_month", "All Month") != "All Month",
        st.session_state.get("tm_terminal", "All Terminal") != "All Terminal",
    ])

    # Sisipkan penanda halaman dan gaya CSS
    st.markdown('<div class="overview-page-marker tm-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    _inject_tm_css()

    # Tampilkan tata letak header
    with st.container():
        st.markdown('<div class="tm-sticky-header-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        st.markdown(_tm_page_header(), unsafe_allow_html=True)
        st.markdown('<div class="tm-sticky-header-end" aria-hidden="true"></div>', unsafe_allow_html=True)

    st.markdown('<div class="tm-fixed-header-spacer" aria-hidden="true"></div>', unsafe_allow_html=True)

    # Tampilkan widget Kartu Filter
    with st.container(border=True):
        _render_tm_filter_card(
            active_count,
            TM_TERMINAL_OPTIONS,
            TM_YEAR_OPTIONS,
            TM_MONTH_OPTIONS,
        )

    _mount_tm_fixed_header()

    # Susun grid Metrik KPI
    yoy_val_str = f"{metrics['yoy']:.1f}".replace(".", ",")
    growth_val_str = f"{abs(metrics['growth_pct']):.1f}".replace(".", ",")
    growth_sign = "+" if metrics["growth_pct"] >= 0 else "-"
    growth_display = f"{growth_sign}{growth_val_str}%" if metrics["growth_available"] else "N/A"
    domestic_pct_str = f"{metrics['domestic_pct']:.1f}".replace(".", ",")
    intl_pct_str = f"{metrics['intl_pct']:.1f}".replace(".", ",")

    spark_total = trend_df["Current"].tolist()
    spark_dom = dom_intl_df["Domestic"].tolist()
    spark_intl = dom_intl_df["International"].tolist()
    spark_spp = spp_df["SPP"].tolist()

    kpi_html = "".join([
        _tm_kpi_card("Total Traffic", _fmt_millions(metrics["total"]),
                     f"{current_year_label} · {scope_label}", metrics["yoy"], "#7C3AED", "users", spark_total),
        _tm_kpi_card("Domestic Traffic", _fmt_millions(metrics["domestic"]),
                     f"{domestic_pct_str}% of total traffic", metrics["domestic_yoy"],
                     "#2563EB", "map-pin", spark_dom),
        _tm_kpi_card("International Traffic", _fmt_millions(metrics["international"]),
                     f"{intl_pct_str}% of total traffic", metrics["international_yoy"],
                     "#06B6D4", "globe", spark_intl),
        _tm_kpi_card("Spending Per Pax", _fmt_rp_k(metrics["spp"]),
                     "Weighted terminal average", metrics["spp_yoy"], "#D97706", "credit-card", spark_spp),
        _tm_kpi_card("Traffic Growth", growth_display,
                     metrics["growth_label"], metrics["growth_pct"], "#059669", "trending-up", spark_total),
    ])
    st.markdown(f'<div class="tm-kpi-grid">{kpi_html}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Tampilkan Baris Grafik (Tren dan perbandingan Domestik/Internasional)
    row1_left, row1_right = st.columns([1.55, 1], gap="small")
    peak_month = trend_df.loc[trend_df["Current"].idxmax(), "Month"] if not trend_df.empty else "-"
    peak_value = trend_df["Current"].max() if not trend_df.empty else 0

    with row1_left:
        st.markdown('<div class="ed-card-marker tm-trend-card"></div>', unsafe_allow_html=True)
        h1, h2 = st.columns([3.2, 1])
        with h1:
            st.markdown(section_title_html(
                "Total Traffic Trend",
                f"Monthly passengers — {current_year_label} vs {prior_year_label} · {scope_label}",
            ), unsafe_allow_html=True)
        yoy_display = f"+{yoy_val_str}%" if metrics["prior_total"] else "N/A"
        st.markdown(f'<span class="tm-yoy-pill">YoY {yoy_display}</span>', unsafe_allow_html=True)
        st.markdown(
            '<div class="tm-mini-metrics">'
            + _mini_metric_box(current_year_label, _fmt_millions(metrics["total"]), accent="#7C3AED")
            + _mini_metric_box(prior_year_label, _fmt_millions(metrics["prior_total"]), accent="#94A3B8")
            + _mini_metric_box("Peak Month", f"{peak_month} · {_fmt_pax_short(peak_value * 1_000_000)}", accent="#2563EB")
            + _mini_metric_box("Growth", yoy_display, accent="#059669")
            + "</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(_traffic_trend_figure(trend_df, current_year_label, prior_year_label), use_container_width=True,
                        config={"displayModeBar": False})

    with row1_right:
        st.markdown('<div class="ed-card-marker tm-split-card"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Domestic vs International",
            f"Monthly split — {current_year_label} · {scope_label}",
        ), unsafe_allow_html=True)
        st.markdown(
            '<div class="tm-mini-metrics" style="grid-template-columns:repeat(2,minmax(0,1fr));">'
            + _mini_metric_box("Domestic", _fmt_millions(metrics["domestic"]),
                               f"{domestic_pct_str}% share", "#2563EB")
            + _mini_metric_box("International", _fmt_millions(metrics["international"]),
                               f"{intl_pct_str}% share", "#06B6D4")
            + "</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(_dom_intl_figure(dom_intl_df), use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f'<div class="tm-split-bar">'
            f'<div class="tm-split-dom" style="width:{metrics["domestic_pct"]:.1f}%;"></div>'
            f'<div class="tm-split-intl" style="width:{metrics["intl_pct"]:.1f}%;"></div>'
            f"</div>"
            f'<div class="tm-split-legend">'
            f'<span>Domestic {domestic_pct_str}%</span>'
            f'<span>International {intl_pct_str}%</span>'
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:11px'></div>", unsafe_allow_html=True)

    # Tampilkan Baris Bawah (Tren SPP, Kartu Terminal, dan grafik Distribusi)
    row2_a, row2_b, row2_c = st.columns([1.15, 1.05, 0.95], gap="small")
    spp_peak = spp_df["SPP"].max()
    spp_peak_month = spp_df.loc[spp_df["SPP"].idxmax(), "Month"] if (not pd.isna(spp_peak) and spp_peak != 0) else ""
    spp_value_k = metrics["spp"] / 1000.0 if metrics["spp"] else 0.0
    achievement = (spp_value_k / 90.0 - 1) * 100 if spp_value_k else 0.0

    with row2_a:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Spending per Pax Trend",
            f"Monthly Rp '000 per passenger vs Rp 90K target · {scope_label}",
        ), unsafe_allow_html=True)
        
        ach_sign = "+" if achievement >= 0 else ""
        ach_color = "#059669" if achievement >= 0 else "#DC2626"
        ach_str = f"{ach_sign}{achievement:.1f}%".replace(".", ",")
        peak_month_label = f"{_month_short(spp_peak_month)} Peak" if spp_peak_month else "Peak SPP"
        
        st.markdown(
            '<div class="tm-mini-metrics" style="grid-template-columns:repeat(4,minmax(0,1fr));">'
            + _mini_metric_box(f"{current_year_label} Avg", _fmt_rp_k(metrics["spp"]), accent="#D97706")
            + _mini_metric_box(peak_month_label, _fmt_rp_k(spp_peak * 1000), spp_peak_month, "#EA580C")
            + _mini_metric_box("Target", "Rp 90,0 K", accent="#64748B")
            + _mini_metric_box("Achievement", ach_str, accent=ach_color)
            + "</div>",
            unsafe_allow_html=True,
        )
        st.plotly_chart(_spp_trend_figure(spp_df), use_container_width=True, config={"displayModeBar": False})

    with row2_b:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Traffic by Terminal",
            f"Annual passengers — {current_year_label}",
        ), unsafe_allow_html=True)
        cards = []
        all_metrics = _aggregate_metrics(data_df, st.session_state.tm_year, st.session_state.tm_month, "All Terminal")
        for row in all_metrics["rows"]:
            cards.append(_terminal_card_html(row, all_metrics["shares"][row["name"]]))
        st.markdown(f'<div class="tm-terminal-stack">{"".join(cards)}</div>', unsafe_allow_html=True)

    with row2_c:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Traffic Distribution",
            f"Contribution by terminal — {current_year_label} · All Terminals",
        ), unsafe_allow_html=True)
        labels = [r["name"] for r in all_metrics["rows"]]
        values = [r["total"] for r in all_metrics["rows"]]
        chart_slot, legend_slot = st.columns([1.05, 1], gap="small")
        with chart_slot:
            st.plotly_chart(
                _donut_figure(labels, values, _fmt_millions(all_metrics["total"])),
                use_container_width=True,
                config={"displayModeBar": False},
            )
        with legend_slot:
            st.markdown(
                donut_legend_html(labels, values, TM_DONUT_COLORS, _fmt_millions),
                unsafe_allow_html=True,
            )
        st.markdown(section_title_html("YoY Growth by Terminal", ""), unsafe_allow_html=True)
        st.plotly_chart(_yoy_bar_figure(all_metrics["rows"]), use_container_width=True,
                        config={"displayModeBar": False})

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Tampilkan Kartu Insight Eksekutif
    top_row = max(all_metrics["rows"], key=lambda row: row["total"], default=None)
    top_name = top_row["name"] if top_row else "No terminal"
    top_total = top_row["total"] if top_row else 0
    top_share = all_metrics["shares"].get(top_name, 0) if top_row else 0
    top_spp = top_row["spp"] if top_row else 0
    intl_mix = (metrics["international"] / metrics["total"] * 100) if metrics["total"] else 0

    top_share_str = f"{top_share:.1f}".replace(".", ",")
    intl_mix_str = f"{intl_mix:.1f}".replace(".", ",")
    target_diff = (metrics['spp'] / 90_000 - 1) * 100
    target_diff_str = f"{target_diff:+.1f}".replace(".", ",")
    yoy_str = f"{metrics['yoy']:+.1f}".replace(".", ",")

    with st.container():
        st.markdown('<div class="ed-card-marker tm-insights-card"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html(
            "Executive Insights",
            f"Traffic & spending analysis · {current_year_label} · {scope_label}",
        ), unsafe_allow_html=True)
        st.markdown(
            '<div class="tm-insight-grid">'
            + _insight_card_html(
                f"{top_name} memimpin dengan {_fmt_millions(top_total)} ({top_share_str}%)",
                "Terminal dengan volume pergerakan penumpang tertinggi berdasarkan data saat ini.",
                f"Porsi {top_share_str}%",
                "#0891B2", "#ECFEFF",
            )
            + (
                _insight_card_html(
                    f"Pertumbuhan penumpang {yoy_str}% YoY",
                    f"Total pergerakan penumpang mencapai {_fmt_millions(metrics['total'])} dibandingkan {_fmt_millions(metrics['prior_total'])} pada tahun {metrics['prior_year']}.",
                    f"{yoy_str}% YoY",
                    "#059669", "#F0FDF4",
                )
                if metrics["prior_total"] else
                _insight_card_html(
                    "Data Tahun Lalu Belum Ada",
                    f"Saat ini total pergerakan penumpang adalah {_fmt_millions(metrics['total'])}. Angka pertumbuhan tahunan (YoY) akan muncul setelah file data tahun {prior_year_label} diunggah.",
                    "N/A",
                    "#94A3B8", "#F8FAFC",
                )
            )
            + _insight_card_html(
                f"Rata-rata SPP {_fmt_rp_k(metrics['spp'])}",
                "Rata-rata nilai belanja per penumpang di bandara, dihitung dari total kontribusi dibagi volume penumpang.",
                f"{target_diff_str}% vs target",
                "#D97706", "#FFF7ED",
            )
            + _insight_card_html(
                f"Porsi Penerbangan Internasional {intl_mix_str}%",
                "Persentase penumpang rute luar negeri. Nilai belanja (SPP) tertinggi di antara seluruh terminal saat ini adalah " + _fmt_rp_k(top_spp) + ".",
                f"SPP Tertinggi {_fmt_rp_k(top_spp)}",
                "#7C3AED", "#F5F3FF",
            )
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

    # Tampilkan Ringkasan Tabel dan tombol Unduh Excel
    table_df = get_terminal_table_df(all_metrics)
    display_df = table_df.drop(columns=["_share", "_total"]).copy()
    col_align = {
        "Domestic Traffic": "right",
        "International Traffic": "right",
        "Total Traffic": "right",
        "Traffic Share": "right",
        "Spending Per Pax": "right",
        "YoY Growth": "right",
    }

    with st.container():
        st.markdown('<div class="ed-card-marker tm-performance-card"></div>', unsafe_allow_html=True)
        th1, th2 = st.columns([3.5, 1])
        with th1:
            st.markdown(section_title_html(
                "Traffic Performance by Terminal",
                f"Annual traffic and spending summary — {current_year_label} · {scope_label}",
            ), unsafe_allow_html=True)
        with th2:
            st.markdown('<div class="tm-btn-export-marker"></div>', unsafe_allow_html=True)
            st.download_button(
                "Export",
                data=dataframe_to_excel_bytes(display_df, "Traffic Performance"),
                file_name="traffic_performance_by_terminal.xlsx",
                mime=EXCEL_MIME,
                key="tm_performance_export",
                use_container_width=True,
            )
        st.markdown(
            f'<div class="tm-table-wrap">{table_inner_html(display_df, col_align=col_align)}</div>',
            unsafe_allow_html=True,
        )
