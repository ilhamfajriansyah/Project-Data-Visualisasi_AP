import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import numpy as np

from .enterprise_ui import (
    ED_FONT,
    alert_card_html,
    alert_grid_html,
    donut_legend_html,
    filter_label,
    fmt_rp_compact,
    fmt_rp_full,
    fmt_status_badge,
    inject_enterprise_page_css,
    kpi_card_html,
    kpi_grid_html,
    paginate_dataframe,
    progress_bar_html,
    section_title_html,
    table_inner_html,
)
from .navigation import show_topnav
from .export_utils import EXCEL_MIME, dataframe_to_excel_bytes

AB_MONTH_OPTIONS = ["June 2026", "May 2026", "April 2026"]
AB_TERMINAL_OPTIONS = ["Terminal 1", "Terminal 2", "All Terminal"]
AB_STATUS_FILTER = ["All", "PAID", "SENT", "PENDING", "OVERDUE"]
AB_DONUT_COLORS = ["#10B981", "#2563EB", "#F59E0B", "#EF4444"]
AB_DETAIL_SORT = {
    "Invoice ID": "Invoice ID",
    "Due Date": "Due Date",
    "Outstanding Balance": "Outstanding Balance",
    "Accrual Amount": "Accrual Amount",
}


# ─────────────────────────────────────────────
# DATA (existing business sources preserved)
# ─────────────────────────────────────────────
def get_recent_activities():
    return pd.DataFrame({
        "File Name": [
            "Accrual_Jun_Ground.xlsx", "Accrual_Jun_VIP.xlsx",
            "Accrual_Jun_Ground.xlsx", "Accrual_Jun_Ground.xlsx",
            "Accrual_Jun_VIP.xlsx", "Accrual_Jun_VIP.xlsx",
        ],
        "Tenant/SBU": [
            "Terminal 1", "Terminal 2", "Terminal 1",
            "Terminal 1", "Terminal 2", "Terminal 2",
        ],
        "Date": [
            "28 Jun 2026", "28 Jun 2026", "28 Jun 2026",
            "28 Jun 2026", "28 Jun 2026", "28 Jun 2026",
        ],
        "Status": [
            "SUCCESS", "RESERVED", "SUCCESS",
            "SUCCESS", "RESERVED", "RESERVED",
        ],
    })


def get_billing_kpis():
    return {
        "total_accrual": 21_100_000_000,
        "invoice_issued": 18_500_000_000,
        "amount_collected": 15_200_000_000,
        "outstanding": 3_300_000_000,
        "accrual_mom": 8.4,
        "invoice_mom": 6.1,
        "collected_mom": 12.5,
        "outstanding_mom": -4.2,
        "invoice_count": 90,
    }


def get_accrual_trend_data():
    return pd.DataFrame({
        "Bulan": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Accrual Amount": [14.2, 15.8, 16.5, 17.9, 19.4, 21.1],
        "Invoice Amount": [12.5, 13.6, 14.8, 15.9, 17.2, 18.5],
        "Collected Amount": [10.2, 11.4, 12.1, 13.5, 14.0, 15.2],
    })


def get_invoice_status_distribution():
    return pd.DataFrame({
        "Status": ["Paid", "Sent", "Pending", "Overdue"],
        "Amount": [9_600_000_000, 3_700_000_000, 3_300_000_000, 1_900_000_000],
    })


def _base_invoices():
    return pd.DataFrame({
        "Invoice ID": ["INV-2026-001", "INV-2026-002", "INV-2026-003", "INV-2026-004", "INV-2026-005"],
        "Tenant": ["Ground Handling", "PSC", "VIP Services", "Commercial Area", "Cargo Area"],
        "Invoice Date": ["01 Jun 2026", "03 Jun 2026", "05 Jun 2026", "08 Jun 2026", "10 Jun 2026"],
        "Due Date": ["15 Jul 2026", "20 Jul 2026", "25 Jul 2026", "30 Jul 2026", "05 Aug 2026"],
        "Amount": [8_470_000_000, 6_400_000_000, 2_730_000_000, 1_950_000_000, 8_470_000_000],
        "Status": ["PAID", "SENT", "OVERDUE", "PENDING", "PENDING"],
    })


@st.cache_data(show_spinner=False)
def get_recent_billing_activities():
    df = _base_invoices().copy()
    extras = []
    tenants = ["Ground Handling", "PSC", "VIP Services", "Commercial Area", "Cargo Area", "Parking Area"]
    statuses = ["PAID", "SENT", "PENDING", "OVERDUE"]
    for i in range(6, 21):
        extras.append({
            "Invoice ID": f"INV-2026-{i:03d}",
            "Tenant": tenants[i % len(tenants)],
            "Invoice Date": f"{(i % 28) + 1:02d} Jun 2026",
            "Due Date": f"{(i % 28) + 1:02d} Jul 2026",
            "Amount": np.random.default_rng(i).integers(500_000_000, 4_000_000_000),
            "Status": statuses[i % len(statuses)],
        })
    return pd.concat([df, pd.DataFrame(extras)], ignore_index=True)


def get_top_outstanding_tenants():
    return [
        {"tenant": "PT BUDI PUTRA BOGAJAYA", "amount": 1_200_000_000, "aging": "> 90 days", "progress": 18, "color": "#DC2626"},
        {"tenant": "PT DEWATAAGUNG WIBAWA", "amount": 800_000_000, "aging": "61–90 days", "progress": 42, "color": "#EA580C"},
        {"tenant": "PT PERTAMINA PATRA", "amount": 1_300_000_000, "aging": "> 90 days", "progress": 12, "color": "#DC2626"},
        {"tenant": "PT MAPAN SEJAHTERA", "amount": 620_000_000, "aging": "31–60 days", "progress": 58, "color": "#F59E0B"},
        {"tenant": "PT NUSANTARA RETAIL", "amount": 480_000_000, "aging": "0–30 days", "progress": 76, "color": "#059669"},
    ]


@st.cache_data(show_spinner=False)
def get_accrual_billing_detail():
    rng = np.random.default_rng(24)
    base = _base_invoices()
    contracts = ["LC-2024-001", "LC-2024-014", "LC-2025-008", "LC-2025-019", "LC-2026-003"]
    rows = []
    for i in range(128):
        ref = base.iloc[i % len(base)]
        accrual = float(ref["Amount"])
        invoice = accrual * rng.uniform(0.92, 1.0)
        status = ref["Status"]
        if status == "PAID":
            collected = invoice
        elif status == "OVERDUE":
            collected = invoice * rng.uniform(0.1, 0.4)
        else:
            collected = invoice * rng.uniform(0.45, 0.85)
        outstanding = max(invoice - collected, 0)
        rows.append({
            "Invoice ID": f"INV-2026-{i + 1:03d}",
            "Tenant": ref["Tenant"],
            "Contract No.": contracts[i % len(contracts)],
            "Accrual Amount": accrual,
            "Invoice Amount": invoice,
            "Amount Collected": collected,
            "Outstanding Balance": outstanding,
            "Due Date": ref["Due Date"],
            "Billing Status": status,
        })
    return pd.DataFrame(rows)


def _filter_select_label(value):
    return "Filter" if value == "All" else value


def _trend_figure(df_trend):
    fig = go.Figure()
    series = [
        ("Accrual Amount", "#7C3AED"),
        ("Invoice Amount", "#2563EB"),
        ("Collected Amount", "#059669"),
    ]
    for col, color in series:
        fig.add_trace(go.Scatter(
            x=df_trend["Bulan"],
            y=df_trend[col],
            mode="lines+markers",
            name=col,
            line=dict(color=color, width=2.5),
            marker=dict(size=6, color="#ffffff", line=dict(color=color, width=2)),
        ))
    fig.update_layout(
        autosize=True,
        height=320,
        margin=dict(t=16, b=8, l=8, r=8),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        hovermode="x unified",
        font=dict(family=ED_FONT, size=11, color="#475569"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, tickfont=dict(size=11, color="#64748B"), fixedrange=True),
        yaxis=dict(
            title=dict(text="Rp Miliar", font=dict(size=11, color="#64748B")),
            showgrid=True,
            gridcolor="#E2E8F0",
            zeroline=False,
            tickfont=dict(size=11, color="#64748B"),
            fixedrange=True,
        ),
    )
    return fig


def _donut_figure(dist_df, total):
    fig = go.Figure(data=[go.Pie(
        labels=dist_df["Status"],
        values=dist_df["Amount"],
        hole=0.62,
        sort=False,
        marker=dict(colors=AB_DONUT_COLORS, line=dict(color="#ffffff", width=2)),
        textinfo="none",
        hovertemplate="%{label}<br>%{value:,.0f}<extra></extra>",
    )])
    fig.update_layout(
        height=280,
        margin=dict(t=10, b=10, l=10, r=10),
        plot_bgcolor="#ffffff",
        paper_bgcolor="#ffffff",
        showlegend=False,
        annotations=[dict(
            text=f"<b>{fmt_rp_compact(total)}</b><br><span style='font-size:11px;color:#64748B'>Total Invoice</span>",
            x=0.5, y=0.5, font=dict(size=13, color="#0F172A", family=ED_FONT), showarrow=False,
        )],
    )
    return fig


def _outstanding_list_html(items):
    rows = []
    for item in items:
        rows.append(
            f'<div class="ed-outstanding-row">'
            f'<div class="ed-outstanding-head">'
            f'<p class="ed-outstanding-name">{item["tenant"][:32]}</p>'
            f'<span class="ed-outstanding-amt">{fmt_rp_compact(item["amount"])}</span>'
            f"</div>"
            f'<div class="ed-outstanding-meta">'
            f'<span>{item["aging"]}</span>'
            f'<span>Collection progress</span>'
            f"</div>"
            f'{progress_bar_html(item["progress"], item["color"])}'
            f"</div>"
        )
    return "".join(rows)


def _apply_detail_formatting(df):
    view = df.copy()
    view["Accrual Amount"] = view["Accrual Amount"].apply(fmt_rp_full)
    view["Invoice Amount"] = view["Invoice Amount"].apply(fmt_rp_full)
    view["Amount Collected"] = view["Amount Collected"].apply(
        lambda v: f'<span class="ed-positive">{fmt_rp_full(v)}</span>'
    )
    view["Outstanding Balance"] = view.apply(
        lambda r: (
            f'<span class="ed-negative">{fmt_rp_full(r["Outstanding Balance"])}</span>'
            if r["_outstanding_raw"] > 0
            else f'<span style="color:#64748B;">{fmt_rp_full(r["Outstanding Balance"])}</span>'
        ),
        axis=1,
    )
    view["Billing Status"] = view["Billing Status"].apply(fmt_status_badge)
    view = view.drop(columns=["_outstanding_raw"])
    view["Invoice ID"] = view["Invoice ID"].apply(
        lambda v: f'<span style="color:#2563EB;font-weight:700;">{v}</span>'
    )
    return view


# ══════════════════════════════════════════════
# PAGE: ACCRUAL & BILLING
# ══════════════════════════════════════════════
def page_accrual_billing():
    st.markdown('<div class="overview-page-marker ab-page-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
    inject_enterprise_page_css("ab-page-marker", extra_css="""
    body:has(.ab-page-marker) div[data-testid="stHorizontalBlock"]:has(.ab-trend-card):has(.ab-donut-card) {
        align-items: stretch !important;
    }
    body:has(.ab-page-marker) div[data-testid="stVerticalBlock"]:has(.ab-trend-card),
    body:has(.ab-page-marker) div[data-testid="stVerticalBlock"]:has(.ab-donut-card) {
        min-height: 100% !important;
    }
    body:has(.ab-page-marker) .ed-positive { color: #059669; font-weight: 700; }
    body:has(.ab-page-marker) .ed-negative { color: #DC2626; font-weight: 700; }
    """)
    show_topnav(
        "Accrual & Billing",
        subtitle="Monitor accrual, invoice, and collection performance",
        show_search=False,
    )

    for key in ["ab_detail_page", "ab_recent_page", "ab_filter_status", "ab_detail_sort"]:
        if key not in st.session_state:
            st.session_state[key] = 1 if key.endswith("_page") else ("All" if key == "ab_filter_status" else "Due Date")

    pf1, pf2, pf3 = st.columns([1.35, 1.35, 3.3])
    with pf1:
        st.markdown(filter_label("Month"), unsafe_allow_html=True)
        st.selectbox("Month", AB_MONTH_OPTIONS, key="ab_month", label_visibility="collapsed")
    with pf2:
        st.markdown(filter_label("Terminal"), unsafe_allow_html=True)
        st.selectbox("Terminal", AB_TERMINAL_OPTIONS, key="ab_terminal", label_visibility="collapsed")
    with pf3:
        st.markdown(
            '<div style="height:52px;display:flex;align-items:end;justify-content:flex-end;'
            f'color:#64748B;font-size:12px;font-weight:500;font-family:{ED_FONT};">'
            "Data terakhir diperbarui: 12 Jun 2026 10:42 WIB</div>",
            unsafe_allow_html=True,
        )

    kpis = get_billing_kpis()
    st.markdown(
        kpi_grid_html(
            kpi_card_html("Total Accrual", fmt_rp_compact(kpis["total_accrual"]), f"{kpis['accrual_mom']:.1f}%", True, "#7C3AED", "Σ"),
            kpi_card_html("Invoice Issued", fmt_rp_compact(kpis["invoice_issued"]), f"{kpis['invoice_mom']:.1f}%", True, "#2563EB", "▤"),
            kpi_card_html("Amount Collected", fmt_rp_compact(kpis["amount_collected"]), f"{kpis['collected_mom']:.1f}%", True, "#059669", "₵"),
            kpi_card_html("Outstanding Amount", fmt_rp_compact(kpis["outstanding"]), f"{abs(kpis['outstanding_mom']):.1f}%", False, "#DC2626", "!"),
        ),
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    trend_col, donut_col = st.columns([3, 2], gap="small")
    trend_df = get_accrual_trend_data()
    dist_df = get_invoice_status_distribution()
    total_invoice = dist_df["Amount"].sum()

    with trend_col:
        st.markdown('<div class="ed-card-marker ab-trend-card"></div>', unsafe_allow_html=True)
        th1, th2 = st.columns([3.2, 1])
        with th1:
            st.markdown(section_title_html("Accrual vs Collection Trend", "Monthly accrual, invoice, and collection in Rp billion"), unsafe_allow_html=True)
        with th2:
            st.selectbox("Trend period", ["Monthly"], key="ab_trend_period", label_visibility="collapsed")
        st.plotly_chart(_trend_figure(trend_df), width="stretch", config={"displayModeBar": False})

    with donut_col:
        st.markdown('<div class="ed-card-marker ab-donut-card"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html("Invoice Status Distribution", "Breakdown of invoice value by status"), unsafe_allow_html=True)
        chart_slot, legend_slot = st.columns([1.05, 1], gap="small")
        with chart_slot:
            st.plotly_chart(_donut_figure(dist_df, total_invoice), width="stretch", config={"displayModeBar": False})
        with legend_slot:
            st.markdown(
                donut_legend_html(dist_df["Status"].tolist(), dist_df["Amount"].tolist(), AB_DONUT_COLORS),
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="ed-card-marker ab-alerts-card"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html("Billing Alerts", "Actionable billing and collection exceptions"), unsafe_allow_html=True)
        st.markdown(
            alert_grid_html(
                alert_card_html("critical", "!", "12 invoice jatuh tempo", "Total outstanding Rp 1,9 M memerlukan tindakan segera"),
                alert_card_html("warning", "₵", "Outstanding balance Rp 3,3 M", "16 tenant dengan piutang terbuka"),
                alert_card_html("info", "◷", "5 invoice jatuh tempo minggu ini", "Total Rp 780 Jt diharapkan terkumpul"),
                alert_card_html("positive", "↑", "Tingkat penagihan naik 8%", "Jumlah yang terkumpul melampaui bulan sebelumnya"),
            ),
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    recent_col, outstanding_col = st.columns([13, 7], gap="small")

    with recent_col:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        rh1, rh2 = st.columns([3.2, 1])
        with rh1:
            st.markdown(section_title_html("Recent Billing Activities", "Latest invoice activity and status updates"), unsafe_allow_html=True)
        with rh2:
            st.markdown('<div class="ed-card-action">View All</div>', unsafe_allow_html=True)

        recent_df = get_recent_billing_activities()

        recent_view, recent_total, recent_pages, r_first, r_last = paginate_dataframe(
            recent_df, st.session_state.ab_recent_page, 5
        )
        recent_display = recent_view.copy()
        recent_display["Amount"] = recent_display["Amount"].apply(fmt_rp_compact)
        recent_display["Status"] = recent_display["Status"].apply(fmt_status_badge)
        recent_display["Invoice ID"] = recent_display["Invoice ID"].apply(
            lambda v: f'<span style="color:#2563EB;font-weight:700;">{v}</span>'
        )
        recent_align = {"Amount": "right", "Status": "center"}
        st.markdown(table_inner_html(recent_display, col_align=recent_align), unsafe_allow_html=True)

        st.markdown('<div class="overview-detail-pagination-footer-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        rpa, rpb, rpc, rpd = st.columns([6.6, 0.28, 0.68, 0.28], gap="small")
        with rpa:
            st.markdown(f'<div class="ed-pagination-info">{r_first}–{r_last} dari {recent_total} data</div>', unsafe_allow_html=True)
        with rpb:
            if st.button("‹", key="ab_recent_prev", disabled=st.session_state.ab_recent_page <= 1):
                st.session_state.ab_recent_page -= 1
                st.rerun()
        with rpc:
            st.markdown(f'<div class="ed-pagination-label">Page {st.session_state.ab_recent_page} / {recent_pages}</div>', unsafe_allow_html=True)
        with rpd:
            if st.button("›", key="ab_recent_next", disabled=st.session_state.ab_recent_page >= recent_pages):
                st.session_state.ab_recent_page += 1
                st.rerun()

    with outstanding_col:
        st.markdown('<div class="ed-card-marker"></div>', unsafe_allow_html=True)
        st.markdown(section_title_html("Top Outstanding Tenant", "Highest open balances with aging and collection progress"), unsafe_allow_html=True)
        st.markdown(_outstanding_list_html(get_top_outstanding_tenants()), unsafe_allow_html=True)

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="ed-card-marker ab-detail-card"></div>', unsafe_allow_html=True)
        dh1, ds, df_btn, dsrt, dex, dpp = st.columns([2.4, 2.1, 0.95, 1.05, 0.78, 0.72], vertical_alignment="center")
        with dh1:
            st.markdown(section_title_html("Accrual & Billing Detail", "Complete accrual, invoice, and collection records"), unsafe_allow_html=True)
        with ds:
            search_query = st.text_input(
                "Search",
                placeholder="Search invoice ID, tenant...",
                key="ab_detail_search",
                label_visibility="collapsed",
                on_change=lambda: st.session_state.update({"ab_detail_page": 1}),
            )
        with df_btn:
            st.selectbox(
                "Billing Status",
                AB_STATUS_FILTER,
                key="ab_filter_status",
                label_visibility="collapsed",
                format_func=_filter_select_label,
                on_change=lambda: st.session_state.update({"ab_detail_page": 1}),
            )
        with dsrt:
            st.selectbox(
                "Sort by",
                list(AB_DETAIL_SORT.keys()),
                key="ab_detail_sort",
                label_visibility="collapsed",
                on_change=lambda: st.session_state.update({"ab_detail_page": 1}),
            )

        detail_df = get_accrual_billing_detail()
        if search_query:
            q = search_query.lower().strip()
            detail_df = detail_df[
                detail_df["Invoice ID"].astype(str).str.lower().str.contains(q, na=False)
                | detail_df["Tenant"].astype(str).str.lower().str.contains(q, na=False)
                | detail_df["Contract No."].astype(str).str.lower().str.contains(q, na=False)
            ]
        if st.session_state.ab_filter_status != "All":
            detail_df = detail_df[detail_df["Billing Status"] == st.session_state.ab_filter_status]

        sort_col = AB_DETAIL_SORT[st.session_state.ab_detail_sort]
        ascending = sort_col in ("Invoice ID", "Due Date")
        detail_df = detail_df.sort_values(sort_col, ascending=ascending)

        export_df = detail_df.copy()
        export_df["Accrual Amount"] = export_df["Accrual Amount"].apply(fmt_rp_full)
        export_df["Invoice Amount"] = export_df["Invoice Amount"].apply(fmt_rp_full)
        export_df["Amount Collected"] = export_df["Amount Collected"].apply(fmt_rp_full)
        export_df["Outstanding Balance"] = export_df["Outstanding Balance"].apply(fmt_rp_full)
        with dex:
            st.download_button(
                "Export",
                data=dataframe_to_excel_bytes(export_df, "Accrual Billing Detail"),
                file_name="accrual_billing_detail.xlsx",
                mime=EXCEL_MIME,
                key="ab_detail_export",
                width="stretch",
            )
        with dpp:
            rows_per_page = st.selectbox("Rows per page", [5, 10, 25, 50], index=1, key="ab_rows_per_page", label_visibility="collapsed")

        detail_slice, total_rows, total_pages, first_item, last_item = paginate_dataframe(
            detail_df, st.session_state.ab_detail_page, rows_per_page
        )
        detail_slice = detail_slice.copy()
        detail_slice["_outstanding_raw"] = detail_slice["Outstanding Balance"]
        detail_view = _apply_detail_formatting(detail_slice)
        detail_align = {
            "Accrual Amount": "right",
            "Invoice Amount": "right",
            "Amount Collected": "right",
            "Outstanding Balance": "right",
            "Billing Status": "center",
        }
        st.markdown(table_inner_html(detail_view, col_align=detail_align), unsafe_allow_html=True)

        st.markdown('<div class="overview-detail-pagination-footer-marker" aria-hidden="true"></div>', unsafe_allow_html=True)
        pa, pb, pc, pd_ = st.columns([6.6, 0.28, 0.68, 0.28], gap="small")
        with pa:
            st.markdown(f'<div class="ed-pagination-info">{first_item}–{last_item} dari {total_rows} data</div>', unsafe_allow_html=True)
        with pb:
            if st.button("‹", key="ab_detail_prev", disabled=st.session_state.ab_detail_page <= 1):
                st.session_state.ab_detail_page -= 1
                st.rerun()
        with pc:
            st.markdown(f'<div class="ed-pagination-label">Page {st.session_state.ab_detail_page} / {total_pages}</div>', unsafe_allow_html=True)
        with pd_:
            if st.button("›", key="ab_detail_next", disabled=st.session_state.ab_detail_page >= total_pages):
                st.session_state.ab_detail_page += 1
                st.rerun()


if __name__ == "__main__":
    if "user_name" not in st.session_state:
        st.session_state.user_name = "Admin"
    if "user_email" not in st.session_state:
        st.session_state.user_email = "injourneyairports@mail.com"
    if "user_role" not in st.session_state:
        st.session_state.user_role = "Admin"
    page_accrual_billing()
