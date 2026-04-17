from __future__ import annotations

import textwrap

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from streamlit_demo.data_loader import load_demo_bundle
from streamlit_demo.logic import (
    SCENARIO_LABELS,
    benchmark_callouts,
    build_benchmark_table,
    build_interpretation,
    clean_text,
    derive_driver_list,
    derive_threshold_flags,
    format_currency_compact,
    format_ein,
    format_months,
    format_percentile,
    format_points,
    format_probability,
    format_ratio,
    format_relative,
    format_signed_percent,
    humanize_funding_bucket,
    humanize_peer_group,
    humanize_size_bucket,
    most_sensitive_scenario,
    peer_context_text,
    scenario_label,
    scenario_summary_table,
    shock_explanation,
    shortlist_table_for_section,
)
from streamlit_demo.portfolio_rankings import (
    RANKING_MODES,
    SCENARIO_CONTROL_ALL,
    SCENARIO_METRICS,
    apply_filters,
    build_portfolio_frame,
    build_rationale,
    build_summary_metrics,
    rank_frame,
    scenario_control_options,
    with_scenario_view,
)
from streamlit_demo.ui import (
    GLOBAL_CSS,
    activity_panel_html,
    brief_meta_card_html,
    brief_summary_card_html,
    compact_filter_bar_html,
    executive_header_html,
    filter_lenses_html,
    flag_chip_html,
    html_table_html,
    insight_bento_html,
    kpi_strip_html,
    landing_header_strip_html,
    landing_headline_html,
    live_feed_html,
    module_header_html,
    narrative_panel_html,
    note_card_html,
    overview_bento_html,
    pagination_footer_html,
    rank_table_html,
    risk_pill_html,
    sidebar_note_card_html,
    sidebar_stat_card_html,
    sim_observation_html,
    status_chip_html,
    status_dot_html,
)


PAGE_TITLE = "Fairlight Resilience Decision System"
TAB_TITLES = [
    "1. Resilience Prediction",
    "2. Peer Benchmarking",
    "3. Deterministic Stress Testing",
    "4. Attention Prioritization",
    "5. Portfolio Prioritization",
    "6. Data Explorer",
]

NAVY = "#12395b"
BLUE = "#3e6b90"
TEAL = "#4f7f80"
SLATE = "#7b8794"
GOLD = "#b98d41"
RUST = "#a64743"
LIGHT_GRID = "#e8edf3"
CATEGORY_COLORS = {
    "Fragile but investable": NAVY,
    "Resilient outperformer": TEAL,
    "Shock-sensitive priority watchlist": RUST,
}


st.set_page_config(page_title=PAGE_TITLE, layout="wide", initial_sidebar_state="expanded")


def rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()


@st.cache_data(show_spinner=False)
def get_bundle() -> dict:
    return load_demo_bundle()


@st.cache_data(show_spinner=False)
def get_portfolio_frame_cached(orgs: pd.DataFrame, shortlists: pd.DataFrame, shock_results: pd.DataFrame) -> pd.DataFrame:
    return build_portfolio_frame(orgs, shortlists, shock_results)


def current_org_row(orgs: pd.DataFrame, ein: str) -> pd.Series:
    match = orgs.loc[orgs["ein"] == ein]
    if match.empty:
        return orgs.iloc[0]
    return match.iloc[0]


def org_shocks(shock_results: pd.DataFrame, ein: str) -> pd.DataFrame:
    if shock_results.empty or "ein" not in shock_results.columns:
        return pd.DataFrame()
    return shock_results.loc[shock_results["ein"] == ein].copy()


def shortlist_row(shortlists: pd.DataFrame, ein: str) -> pd.Series | None:
    if shortlists.empty or "ein" not in shortlists.columns:
        return None
    subset = shortlists.loc[shortlists["ein"] == ein]
    if subset.empty:
        return None
    return subset.iloc[0]


def num_or_zero(value: object) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if pd.isna(number) else number


def series_or_default(frame: pd.DataFrame, column: str, default: object = pd.NA) -> pd.Series:
    if column in frame.columns:
        return frame[column]
    return pd.Series(default, index=frame.index)


def coalesce_series(frame: pd.DataFrame, columns: list[str], default: object = pd.NA) -> pd.Series:
    output = pd.Series(default, index=frame.index)
    for column in columns:
        if column in frame.columns:
            output = output.where(output.notna(), frame[column])
    return output


def format_year_value(value: object) -> str:
    if value is None or pd.isna(value):
        return "-"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return clean_text(value, fallback="-")
    return str(int(number)) if number.is_integer() else f"{number:.0f}"


def value_is_available(value: object) -> bool:
    if value is None:
        return False
    try:
        return not pd.isna(value)
    except TypeError:
        return True


def wrap_label(text: str, width: int = 18) -> str:
    return "<br>".join(textwrap.wrap(text, width=width, break_long_words=False)) or text


def apply_chart_style(
    fig: go.Figure,
    *,
    height: int,
    margin_left: int = 24,
    margin_right: int = 28,
    margin_top: int = 22,
    margin_bottom: int = 48,
    showlegend: bool = False,
) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=margin_left, r=margin_right, t=margin_top, b=margin_bottom),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        showlegend=showlegend,
        font=dict(family="Segoe UI, Helvetica Neue, Arial, sans-serif", size=14, color="#102a43"),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.04,
            xanchor="left",
            x=0.0,
            bgcolor="rgba(255,255,255,0.0)",
        ),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=LIGHT_GRID,
        zeroline=False,
        automargin=True,
        ticks="outside",
        tickfont=dict(size=12, color="#486581"),
        title_font=dict(size=13, color="#334e68"),
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        automargin=True,
        tickfont=dict(size=12, color="#334e68"),
        title_font=dict(size=13, color="#334e68"),
    )
    return fig


def make_driver_chart(drivers: list[dict]) -> go.Figure:
    frame = pd.DataFrame(drivers)
    if frame.empty:
        return go.Figure()
    frame = frame.sort_values("score", ascending=True)
    frame["label_display"] = frame["label"].apply(lambda value: wrap_label(value, width=24))
    fig = go.Figure(
        go.Bar(
            x=frame["score"],
            y=frame["label_display"],
            orientation="h",
            marker=dict(color=NAVY, line=dict(color=NAVY, width=1)),
            text=[f"{value:.1f}" for value in frame["score"]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>Driver weight: %{x:.1f}<extra></extra>",
        )
    )
    fig.update_xaxes(title="Relative driver weight")
    fig.update_yaxes(title="")
    return apply_chart_style(
        fig,
        height=max(360, 76 * len(frame)),
        margin_left=240,
        margin_right=68,
        margin_bottom=32,
    )


def make_benchmark_chart(row: pd.Series) -> go.Figure:
    frame = pd.DataFrame(
        [
            {"Metric": "Reserve percentile", "Percentile": num_or_zero(row.get("peer_reserve_percentile")) * 100, "Color": TEAL},
            {"Metric": "Margin percentile", "Percentile": num_or_zero(row.get("peer_margin_percentile")) * 100, "Color": BLUE},
            {"Metric": "Leverage percentile", "Percentile": num_or_zero(row.get("peer_liability_percentile")) * 100, "Color": GOLD},
            {"Metric": "Concentration percentile", "Percentile": num_or_zero(row.get("concentration_percentile")) * 100, "Color": RUST},
            {"Metric": "Overall risk percentile", "Percentile": num_or_zero(row.get("overall_risk_percentile")) * 100, "Color": NAVY},
        ]
    )
    fig = go.Figure(
        go.Bar(
            x=frame["Percentile"],
            y=frame["Metric"],
            orientation="h",
            marker=dict(color=frame["Color"], line=dict(color=frame["Color"], width=1)),
            text=[f"{value:.0f}th pct" for value in frame["Percentile"]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>%{x:.0f}th percentile<extra></extra>",
        )
    )
    fig.add_vline(x=50, line_dash="dot", line_color="#9fb3c8", line_width=1.2)
    fig.update_xaxes(title="Percentile within peer frame", range=[0, 112])
    fig.update_yaxes(title="")
    return apply_chart_style(fig, height=420, margin_left=155, margin_right=82, margin_bottom=40)


def make_scenario_delta_chart(shocks: pd.DataFrame, selected_scenario: str) -> go.Figure:
    if shocks.empty:
        return go.Figure()
    frame = shocks.copy()
    frame["Scenario"] = frame["scenario_name"].map(SCENARIO_LABELS).fillna(frame["scenario_name"])
    frame["Delta"] = frame["absolute_increase"] * 100
    frame = frame.sort_values("Delta", ascending=True)
    frame["Color"] = frame["scenario_name"].apply(lambda value: RUST if value == selected_scenario else NAVY)
    fig = go.Figure(
        go.Bar(
            x=frame["Delta"],
            y=frame["Scenario"].apply(lambda value: wrap_label(value, width=24)),
            orientation="h",
            marker=dict(color=frame["Color"], line=dict(color=frame["Color"], width=1)),
            text=[f"{value:.1f} pts" for value in frame["Delta"]],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>%{x:.1f} point increase<extra></extra>",
        )
    )
    fig.update_xaxes(title="Risk increase under deterministic shock (points)")
    fig.update_yaxes(title="")
    return apply_chart_style(fig, height=460, margin_left=235, margin_right=84, margin_bottom=36)


def make_discovery_chart(shortlists: pd.DataFrame) -> go.Figure:
    if shortlists.empty:
        return go.Figure()
    frame = shortlists.copy()
    frame["Baseline risk"] = frame["predicted_distress_probability"] * 100
    frame["Worst-case delta"] = frame["worst_case_delta"] * 100
    frame["Category"] = frame["shortlist_category"]
    fig = px.scatter(
        frame,
        x="Baseline risk",
        y="Worst-case delta",
        color="Category",
        hover_name="business_name",
        hover_data={
            "peer_group": True,
            "Baseline risk": ":.1f",
            "Worst-case delta": ":.1f",
            "Category": True,
            "business_name": False,
        },
        color_discrete_map=CATEGORY_COLORS,
    )
    fig.update_traces(marker=dict(size=13, line=dict(color="#ffffff", width=1.3), opacity=0.9))
    fig.update_xaxes(title="Baseline risk (%)")
    fig.update_yaxes(title="Worst-case deterministic stress delta (points)")
    return apply_chart_style(fig, height=440, margin_left=48, margin_right=24, margin_bottom=50, showlegend=True)


def render_sidebar(bundle: dict) -> None:
    orgs = bundle["orgs"]
    shortlists = bundle["shortlists"]
    shock_results = bundle["shock_results"]
    top_scenario = bundle.get("run_summary", {}).get("top_shock_scenario") or "expense_inflation_10"
    with st.sidebar:
        st.markdown('<div class="sidebar-rail-title">Coverage</div>', unsafe_allow_html=True)
        st.markdown(
            sidebar_stat_card_html(
                "Organizations scored",
                f"{len(orgs):,}",
                "Observed nonprofit rows available in the current scored universe.",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            sidebar_stat_card_html(
                "Stress scenarios",
                f"{shock_results['scenario_name'].nunique() if not shock_results.empty else len(SCENARIO_LABELS)}",
                "Deterministic planning shocks available in the simulator.",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            sidebar_stat_card_html(
                "Shortlisted",
                f"{len(shortlists):,}",
                "Organizations tagged for financially actionable prioritization.",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            sidebar_note_card_html(
                f"Largest average downside scenario: {scenario_label(top_scenario)}."
            ),
            unsafe_allow_html=True,
        )
        with st.expander("Method note / about this score", expanded=False):
            st.markdown(
                "\n".join(
                    [
                        "- Distress triage is based on the retained `peer_relative_composite` label",
                        "- The backbone is a conservative, interpretable logistic model",
                        "- Scenario shocks are deterministic planning tools, not causal forecasts",
                        "- Peer-relative signals are computed on observed rows only",
                    ]
                )
            )


def build_company_summary(selected_row: pd.Series, selected_shocks: pd.DataFrame, shortlists: pd.DataFrame) -> tuple[str, list[tuple[str, str]]]:
    worst_case = most_sensitive_scenario(selected_shocks)
    shortlist_match = shortlist_row(shortlists, clean_text(selected_row.get("ein"), fallback=""))
    reserve_pct = format_percentile(selected_row.get("peer_reserve_percentile"))
    leverage_pct = format_percentile(selected_row.get("peer_liability_percentile"))
    summary = (
        f"{clean_text(selected_row.get('business_name'))} is a {clean_text(selected_row.get('sector_group'))} organization in "
        f"{clean_text(selected_row.get('state'))}, compared within the app's {humanize_peer_group(selected_row.get('peer_group'))} peer frame. "
        f"Baseline distress probability is {format_probability(selected_row.get('predicted_distress_probability'))}; reserve position is {reserve_pct} "
        f"and leverage sits at {leverage_pct} versus peers."
    )
    if shortlist_match is not None:
        summary += f" It currently sits in the {clean_text(shortlist_match.get('shortlist_category')).lower()} prioritization category."
    if worst_case is not None:
        summary += f" Its largest deterministic stress-test move comes under {scenario_label(worst_case.get('scenario_name'))}."

    details = [
        ("EIN", format_ein(selected_row.get("ein"))),
        ("Latest filing", clean_text(selected_row.get("feature_year"))),
        ("Peer group", humanize_peer_group(selected_row.get("peer_group"))),
        ("Sector / state", f"{clean_text(selected_row.get('sector_group'))} | {clean_text(selected_row.get('state'))}"),
        ("Funding model", humanize_funding_bucket(selected_row.get("funding_bucket"))),
        ("Largest stress-test move", scenario_label(worst_case.get("scenario_name")) if worst_case is not None else "See Stress Testing"),
    ]
    return summary, details


def render_company_brief(selected_row: pd.Series, selected_shocks: pd.DataFrame, shortlists: pd.DataFrame) -> None:
    summary, _details = build_company_summary(selected_row, selected_shocks, shortlists)

    biz_name = clean_text(selected_row.get("business_name"))
    risk_bucket = clean_text(selected_row.get("risk_bucket"))
    peer_group = humanize_peer_group(selected_row.get("peer_group"))
    filing_year = clean_text(selected_row.get("feature_year"))
    ein_display = format_ein(selected_row.get("ein"))

    # ------- Executive Header -------
    exec_html = executive_header_html(
        title=f"Executive Briefing &mdash; {biz_name}",
        body=summary,
        meta_lines=[
            f"EIN <strong>{ein_display}</strong>",
            f"Filing Year <strong>{filing_year}</strong>",
            f"Peer Frame <strong>{peer_group}</strong>",
            f"Risk Bucket <strong>{risk_bucket}</strong>",
        ],
    )

    # ------- KPI Strip -------
    rev_growth = selected_row.get("revenue_growth_clean")
    try:
        rev_growth_val = float(rev_growth) if rev_growth is not None else None
    except (TypeError, ValueError):
        rev_growth_val = None
    rev_is_positive = rev_growth_val is not None and rev_growth_val >= 0

    kpi_items = [
        {
            "label": "Total Revenue",
            "value": format_currency_compact(selected_row.get("total_revenue")),
            "icon": "account_balance",
            "delta": f"{format_signed_percent(rev_growth)} vs prior year" if rev_growth_val is not None else "Growth not reported",
            "delta_icon": "trending_up" if rev_is_positive else "trending_down",
            "delta_tone": "ok" if rev_is_positive else "warn",
        },
        {
            "label": "Reserve Runway",
            "value": format_months(selected_row.get("reserve_months_proxy")),
            "icon": "savings",
            "delta": f"{format_percentile(selected_row.get('peer_reserve_percentile'))} reserve percentile",
            "delta_icon": "group",
        },
        {
            "label": "Distress Probability",
            "value": format_probability(selected_row.get("predicted_distress_probability")),
            "icon": "security",
            "delta": f"{risk_bucket} &mdash; {format_percentile(selected_row.get('peer_liability_percentile'))} leverage percentile",
            "inverse": True,
        },
    ]
    kpi_html = kpi_strip_html(kpi_items)

    # ------- Narrative + Live Feed + Activity Table -------
    narrative = narrative_panel_html(
        title="Financial Climate Assessment",
        body=summary,
    )

    feed_items: list[dict] = []
    if isinstance(selected_shocks, pd.DataFrame) and not selected_shocks.empty and "absolute_increase" in selected_shocks.columns:
        ranked = selected_shocks.dropna(subset=["absolute_increase"]).copy()
        ranked["absolute_increase"] = pd.to_numeric(ranked["absolute_increase"], errors="coerce").fillna(0.0)
        ranked = ranked.sort_values("absolute_increase", ascending=False).head(3)
        for _, row in ranked.iterrows():
            baseline = clean_text(row.get("baseline_bucket"))
            shocked = clean_text(row.get("shocked_bucket"))
            delta = format_points(row.get("absolute_increase"))
            scen_name = scenario_label(row.get("scenario_name"))
            family = clean_text(row.get("scenario_family")).upper()
            shift = row.get("bucket_shift")
            try:
                shift_val = float(shift) if shift is not None else 0
            except (TypeError, ValueError):
                shift_val = 0
            meta_line = f"{family} &middot; {scen_name}" if family else scen_name.upper()
            body_line = f"Shifts risk from <strong>{baseline}</strong> to <strong>{shocked}</strong> ({delta} absolute)." if baseline and shocked else f"Projected absolute increase of {delta}."
            feed_items.append({"meta": meta_line, "body": body_line, "alert": shift_val > 0})
    if not feed_items:
        feed_items = [{"meta": "NO SCENARIO DATA", "body": "Run the deterministic stress test to populate scenario signals for this organization."}]

    feed = live_feed_html("Scenario Signals", feed_items, live=True)

    markers = key_financial_markers(selected_row)
    rows: list[list[str]] = []
    for _, marker in markers.iterrows():
        rows.append([
            clean_text(marker.get("Metric")),
            clean_text(marker.get("Current value")),
            clean_text(marker.get("Why it matters")),
        ])
    table = html_table_html(
        headers=["Metric", "Current Value", "Interpretation"],
        rows=rows,
        column_classes=["strong", "", "meta"],
    )

    # Shortlist membership chip in the activity header
    shortlist_match = shortlists[shortlists["ein"] == clean_text(selected_row.get("ein"), fallback="")] if isinstance(shortlists, pd.DataFrame) and "ein" in getattr(shortlists, "columns", []) else pd.DataFrame()
    if not shortlist_match.empty:
        category = clean_text(shortlist_match.iloc[0].get("shortlist_category"))
        link_label = f"Shortlist &middot; {category}"
    else:
        link_label = "Not on prioritization shortlist"

    activity = activity_panel_html("Key Financial Markers", table, link_label=link_label)

    bento = overview_bento_html(narrative, feed, activity)

    st.markdown(exec_html + kpi_html + bento, unsafe_allow_html=True)


def key_financial_markers(selected_row: pd.Series) -> pd.DataFrame:
    rows = [
        ("Reserve buffer", format_months(selected_row.get("reserve_months_proxy")), "Liquidity cushion visible to operators"),
        ("Operating margin", format_signed_percent(selected_row.get("operating_margin_clean")), "Annual earnings pressure"),
        ("Leverage", format_ratio(selected_row.get("liability_ratio_clean")), "Balance-sheet strain"),
        ("Net asset ratio", format_signed_percent(selected_row.get("net_asset_ratio_clean")), "Capital cushion"),
        ("Donation share", format_signed_percent(selected_row.get("donation_share_clean")), "Revenue mix dependence"),
        ("Revenue concentration", format_ratio(selected_row.get("revenue_hhi_clean"), digits=3, suffix=""), "Single-source fragility"),
    ]
    return pd.DataFrame(rows, columns=["Metric", "Current value", "Why it matters"])


def shortlist_overview_table(shortlists: pd.DataFrame) -> pd.DataFrame:
    if shortlists.empty:
        return pd.DataFrame()
    overview = (
        shortlists.groupby("shortlist_category")
        .agg(
            Organizations=("ein", "count"),
            Median_baseline_risk=("predicted_distress_probability", "median"),
            Median_worst_case_delta=("worst_case_delta", "median"),
        )
        .reset_index()
    )
    overview["Median baseline risk"] = overview["Median_baseline_risk"].apply(format_probability)
    overview["Median worst-case delta"] = overview["Median_worst_case_delta"].apply(format_points)
    return overview[["shortlist_category", "Organizations", "Median baseline risk", "Median worst-case delta"]].rename(
        columns={"shortlist_category": "Category"}
    )


def safe_options(frame: pd.DataFrame, column: str) -> list[str]:
    if column not in frame.columns:
        return []
    values = frame[column].dropna().astype(str)
    return sorted((value for value in values.unique().tolist() if value), key=str.lower)


def ranking_table_from_frame(ranked: pd.DataFrame, mode: str) -> pd.DataFrame:
    if ranked.empty:
        return pd.DataFrame()
    table = ranked.copy()
    table["Organization"] = series_or_default(table, "business_name", "Unknown organization").fillna("Unknown organization")
    table["EIN"] = series_or_default(table, "ein", "").apply(format_ein)
    table["Latest year"] = coalesce_series(table, ["feature_year", "latest_year_raw"], default="-").apply(format_year_value)
    table["Peer group"] = series_or_default(table, "peer_group", "-").apply(humanize_peer_group)
    table["State"] = series_or_default(table, "state", "-").fillna("-")
    table["Sector"] = series_or_default(table, "sector_group", "-").fillna("-")
    table["Baseline risk"] = series_or_default(table, "predicted_distress_probability").apply(format_probability)
    table["Risk bucket"] = series_or_default(table, "risk_bucket", "-").fillna("-")
    table["Reserve percentile"] = series_or_default(table, "peer_reserve_percentile").apply(format_percentile)
    table["Leverage percentile"] = series_or_default(table, "peer_liability_percentile").apply(format_percentile)
    table["Concentration percentile"] = series_or_default(table, "concentration_percentile").apply(format_percentile)
    table["Top stress scenario"] = coalesce_series(table, ["scenario_name_view", "top_scenario"], default="-").apply(scenario_label)
    table["Stress delta"] = coalesce_series(table, ["scenario_absolute_delta", "worst_case_delta"]).apply(format_points)
    table["Shortlist category"] = series_or_default(table, "shortlist_category", "-").fillna("-")
    table["Rationale"] = table.apply(lambda row: build_rationale(row, mode), axis=1)
    return table[
        [
            "Organization",
            "EIN",
            "Latest year",
            "Peer group",
            "State",
            "Sector",
            "Baseline risk",
            "Risk bucket",
            "Reserve percentile",
            "Leverage percentile",
            "Concentration percentile",
            "Top stress scenario",
            "Stress delta",
            "Shortlist category",
            "Rationale",
        ]
    ]


def ranking_detail_card(row: pd.Series) -> str:
    return (
        f"<strong>{clean_text(row.get('business_name'))}</strong><br>"
        f"EIN: {format_ein(row.get('ein'))}<br>"
        f"Peer group: {humanize_peer_group(row.get('peer_group'))}<br>"
        f"Baseline risk: {format_probability(row.get('predicted_distress_probability'))}<br>"
        f"Reserve percentile: {format_percentile(row.get('peer_reserve_percentile'))}<br>"
        f"Leverage percentile: {format_percentile(row.get('peer_liability_percentile'))}<br>"
        f"Top stress scenario: {scenario_label(row.get('scenario_name_view') if pd.notna(row.get('scenario_name_view')) else row.get('top_scenario'))}<br>"
        f"Stress delta: {format_points(row.get('scenario_absolute_delta') if pd.notna(row.get('scenario_absolute_delta')) else row.get('worst_case_delta'))}"
    )


def tab_risk_lookup(selected_row: pd.Series, threshold_scan: pd.DataFrame) -> None:
    drivers = derive_driver_list(selected_row, top_n=5)
    threshold_flags = derive_threshold_flags(selected_row, threshold_scan)
    interpretation = build_interpretation(selected_row, drivers, threshold_flags)

    org_name = clean_text(selected_row.get("business_name"))
    ein_txt = clean_text(selected_row.get("ein"))
    bucket = clean_text(selected_row.get("risk_bucket"))
    filing_year = clean_text(selected_row.get("filing_year"))
    peer_frame = clean_text(selected_row.get("peer_size_bucket"))

    st.markdown(
        executive_header_html(
            title=f"Resilience Prediction &mdash; {org_name}",
            body=(
                "The resilience model produces a conservative baseline distress probability by combining "
                "reserve strength, leverage, operating margin, revenue mix, and peer frame signals. "
                "Use it as a triage starting point &mdash; not a causal verdict."
            ),
            meta_lines=[
                f"EIN <strong>{ein_txt}</strong>",
                f"Filing Year <strong>{filing_year}</strong>",
                f"Peer Frame <strong>{peer_frame}</strong>",
                f"Risk Bucket <strong>{bucket}</strong>",
            ],
        ),
        unsafe_allow_html=True,
    )

    reserve_pct = selected_row.get("peer_reserve_percentile")
    leverage_pct = selected_row.get("peer_liability_percentile")
    reserve_tone = "ok" if (isinstance(reserve_pct, (int, float)) and reserve_pct >= 50) else "warn"
    leverage_tone = "warn" if (isinstance(leverage_pct, (int, float)) and leverage_pct >= 50) else "ok"

    kpi_items = [
        {
            "label": "Baseline Risk",
            "value": format_probability(selected_row.get("predicted_distress_probability")),
            "icon": "monitoring",
            "delta": f"Risk bucket &mdash; <strong>{bucket}</strong>",
            "delta_icon": "label",
        },
        {
            "label": "Reserve Percentile",
            "value": format_percentile(reserve_pct),
            "icon": "savings",
            "delta": "Higher percentile = stronger reserve buffer",
            "delta_icon": "arrow_upward" if reserve_tone == "ok" else "arrow_downward",
            "delta_tone": reserve_tone,
        },
        {
            "label": "Leverage Percentile",
            "value": format_percentile(leverage_pct),
            "icon": "scale",
            "delta": "Higher percentile = more balance-sheet pressure",
            "delta_icon": "arrow_upward" if leverage_tone == "warn" else "arrow_downward",
            "delta_tone": leverage_tone,
            "inverse": True,
        },
    ]
    st.markdown(kpi_strip_html(kpi_items), unsafe_allow_html=True)

    left, right = st.columns([1.15, 0.85])
    with left:
        st.markdown(
            module_header_html(
                "Main Drivers",
                legend=[
                    {"label": "Risk Contribution", "color": "#000613"},
                    {"label": "Top Signal",        "color": "#fdb69a"},
                ],
            ),
            unsafe_allow_html=True,
        )
        st.plotly_chart(make_driver_chart(drivers), width="stretch")
    with right:
        markers = key_financial_markers(selected_row)
        marker_rows = [
            [clean_text(markers.iloc[i][col]) for col in markers.columns]
            for i in range(len(markers))
        ]
        markers_table = html_table_html(
            headers=list(markers.columns),
            rows=marker_rows,
            column_classes=["strong", "", "meta"],
        )
        st.markdown(
            activity_panel_html("Key Financial Markers", markers_table),
            unsafe_allow_html=True,
        )

    if threshold_flags:
        th_rows = []
        for flag in threshold_flags[:6]:
            lift_val = flag.get("lift") or 0.0
            lift_txt = f"{lift_val:.2f}x" if lift_val else "&mdash;"
            th_rows.append([
                clean_text(flag.get("label")),
                clean_text(flag.get("segment")),
                lift_txt,
                status_chip_html("Triggered", tone="alert"),
            ])
        th_table = html_table_html(
            headers=["Threshold rule", "Segment frame", "Relative lift", "Status"],
            rows=th_rows,
            column_classes=["strong", "", "meta", ""],
        )
        st.markdown(
            activity_panel_html("Threshold Checks That Fired", th_table),
            unsafe_allow_html=True,
        )
    else:
        empty_table = html_table_html(
            headers=["Status"],
            rows=[[status_chip_html("No retained threshold cutoffs are currently triggered", tone="ok")]],
        )
        st.markdown(
            activity_panel_html("Threshold Checks That Fired", empty_table),
            unsafe_allow_html=True,
        )

    st.markdown(
        sim_observation_html(interpretation, kicker="Bottom Line"),
        unsafe_allow_html=True,
    )

    driver_text = ", ".join(driver["label"] for driver in drivers[:3]) if drivers else "driver detail is limited in the stored artifacts"
    threshold_text = ", ".join(flag["label"].lower() for flag in threshold_flags[:3]) if threshold_flags else "no retained threshold cutoffs are currently triggered"
    st.markdown(
        insight_bento_html(
            [
                {
                    "kicker": "Main Drivers",
                    "title": "Strongest signals",
                    "body": f"The strongest visible risk drivers are {driver_text}.",
                },
                {
                    "kicker": "Threshold Takeaway",
                    "title": "Retained scan",
                    "body": f"The retained threshold scan indicates {threshold_text}.",
                },
                {
                    "kicker": "How To Use This",
                    "title": "Triage Compass",
                    "body": "Treat this as a conservative starting point for a case conversation &mdash; the baseline is directional, not causal.",
                },
            ]
        ),
        unsafe_allow_html=True,
    )


def tab_peer_benchmarking(orgs: pd.DataFrame, selected_row: pd.Series) -> None:
    weakness_text, strength_text = benchmark_callouts(selected_row)

    org_name = clean_text(selected_row.get("business_name"))
    peer_size = clean_text(selected_row.get("peer_size_bucket"))
    peer_fund = clean_text(selected_row.get("peer_funding_type"))
    overall_peer = clean_text(selected_row.get("overall_risk_rank_bucket"))
    concentration_pct = selected_row.get("concentration_percentile")

    st.markdown(
        executive_header_html(
            title=f"Peer Benchmarking &mdash; {org_name}",
            body=(
                "Percentiles locate this organization within its size-and-funding peer frame. "
                "They are directional benchmarking signals &mdash; not a full sector-and-geography normalization."
            ),
            meta_lines=[
                f"Peer Size Bucket <strong>{peer_size}</strong>",
                f"Funding Frame <strong>{peer_fund}</strong>",
                f"Concentration Percentile <strong>{format_percentile(concentration_pct)}</strong>",
                f"Overall Peer Risk <strong>{overall_peer}</strong>",
            ],
        ),
        unsafe_allow_html=True,
    )

    reserve_pct = selected_row.get("peer_reserve_percentile")
    margin_pct = selected_row.get("peer_margin_percentile")
    leverage_pct = selected_row.get("peer_liability_percentile")
    reserve_tone = "ok" if (isinstance(reserve_pct, (int, float)) and reserve_pct >= 0.5) else "warn"
    margin_tone = "ok" if (isinstance(margin_pct, (int, float)) and margin_pct >= 0.5) else "warn"
    leverage_tone = "warn" if (isinstance(leverage_pct, (int, float)) and leverage_pct >= 0.5) else "ok"

    kpi_items = [
        {
            "label": "Reserve Percentile",
            "value": format_percentile(reserve_pct),
            "icon": "savings",
            "delta": "Higher = stronger reserve buffer",
            "delta_icon": "arrow_upward" if reserve_tone == "ok" else "arrow_downward",
            "delta_tone": reserve_tone,
        },
        {
            "label": "Margin Percentile",
            "value": format_percentile(margin_pct),
            "icon": "trending_up",
            "delta": "Higher = stronger operating margin",
            "delta_icon": "arrow_upward" if margin_tone == "ok" else "arrow_downward",
            "delta_tone": margin_tone,
        },
        {
            "label": "Leverage Percentile",
            "value": format_percentile(leverage_pct),
            "icon": "scale",
            "delta": "Higher = more balance-sheet pressure",
            "delta_icon": "arrow_upward" if leverage_tone == "warn" else "arrow_downward",
            "delta_tone": leverage_tone,
            "inverse": True,
        },
    ]
    st.markdown(kpi_strip_html(kpi_items), unsafe_allow_html=True)

    left, right = st.columns([1.08, 0.92])
    with left:
        st.markdown(
            module_header_html(
                "Peer-Relative Percentiles",
                legend=[
                    {"label": "Selected Organization", "color": "#000613"},
                    {"label": "Peer Median",           "color": "#fdb69a"},
                ],
            ),
            unsafe_allow_html=True,
        )
        st.plotly_chart(make_benchmark_chart(selected_row), width="stretch")
    with right:
        benchmark_df = build_benchmark_table(selected_row)
        bench_headers = list(benchmark_df.columns)
        bench_rows = []
        for i in range(len(benchmark_df)):
            row_cells = []
            for col in bench_headers:
                cell = clean_text(benchmark_df.iloc[i][col])
                if col == "Read":
                    tone = "ok" if "strength" in cell.lower() else ("warn" if "weakness" in cell.lower() else "")
                    cell = status_chip_html(cell, tone=tone)
                row_cells.append(cell)
            bench_rows.append(row_cells)
        bench_classes = ["strong", "", "meta", "", ""]
        bench_table = html_table_html(
            headers=bench_headers,
            rows=bench_rows,
            column_classes=bench_classes[: len(bench_headers)],
        )
        st.markdown(
            activity_panel_html("Metric-by-Metric Comparison", bench_table),
            unsafe_allow_html=True,
        )

    obs_body = (
        f"<strong>{weakness_text}</strong> This is the cleanest place to start an intervention conversation &mdash; "
        f"while protecting the relative strength: <em>{strength_text.lower()}</em>"
    )
    st.markdown(
        sim_observation_html(obs_body, kicker="Peer Read"),
        unsafe_allow_html=True,
    )

    st.markdown(
        insight_bento_html(
            [
                {
                    "kicker": "Primary Gap",
                    "title": "Where to intervene",
                    "body": weakness_text + " This is the cleanest place to start an intervention conversation.",
                },
                {
                    "kicker": "Primary Strength",
                    "title": "What to protect",
                    "body": strength_text + " It helps frame what should be protected while intervening elsewhere.",
                },
                {
                    "kicker": "Comparison Frame",
                    "title": "Peer Context",
                    "body": peer_context_text(orgs, selected_row) + " Peer comparisons here are directional within size and funding buckets.",
                },
            ]
        ),
        unsafe_allow_html=True,
    )


def tab_shock_simulator(
    selected_row: pd.Series,
    shock_results: pd.DataFrame,
    shock_summary: pd.DataFrame,
    shock_source_mode: str,
    shock_source_note: str,
) -> None:
    selected_shocks = org_shocks(shock_results, clean_text(selected_row.get("ein"), fallback=""))

    scenario_names = [name for name in SCENARIO_LABELS if selected_shocks.empty or name in set(selected_shocks["scenario_name"].dropna())]
    if not scenario_names and not shock_summary.empty:
        scenario_names = shock_summary["scenario_name"].dropna().tolist()
    if not scenario_names:
        st.warning("No scenario artifacts were found for the simulator.")
        return

    if st.session_state.get("selected_scenario") not in scenario_names:
        top_org_scenario = most_sensitive_scenario(selected_shocks)
        st.session_state["selected_scenario"] = top_org_scenario["scenario_name"] if top_org_scenario is not None else scenario_names[0]

    # ------- Executive Header for the simulator module -------
    org_name = clean_text(selected_row.get("business_name"))
    st.markdown(
        executive_header_html(
            title="Simulation Control Center",
            body=(
                "Adjust the scenario to project institutional resilience for "
                f"<strong>{org_name}</strong>. Results are deterministic planning shocks applied to the current "
                "financial profile &mdash; use them for downside planning, not prediction or causal inference."
            ),
            meta_lines=[
                f"Source Mode <strong>{shock_source_mode.replace('_', ' ').title()}</strong>",
                f"Scenarios Available <strong>{len(scenario_names)}</strong>",
            ],
        ),
        unsafe_allow_html=True,
    )

    # ------- Scenario selector -------
    selected_scenario = st.selectbox(
        "Stress scenario",
        options=scenario_names,
        format_func=scenario_label,
        key="selected_scenario",
        label_visibility="visible",
    )

    if shock_source_mode != "exact_upgraded_org_level":
        st.markdown(note_card_html(shock_source_note), unsafe_allow_html=True)

    # ------- Summary-only fallback -------
    if selected_shocks.empty:
        scenario_row = shock_summary.loc[shock_summary["scenario_name"] == selected_scenario].iloc[0]
        kpi_items = [
            {
                "label": "Average Baseline Risk",
                "value": format_probability(scenario_row.get("avg_baseline_risk")),
                "icon": "monitoring",
                "delta": "Summary-level fallback",
            },
            {
                "label": "Average Stressed Risk",
                "value": format_probability(scenario_row.get("avg_shocked_risk")),
                "icon": "trending_up",
                "delta": "Summary-level fallback",
                "delta_tone": "warn",
            },
            {
                "label": "Bucket Upshift Share",
                "value": format_relative(scenario_row.get("bucket_upshift_share")),
                "icon": "insights",
                "delta": f"{format_points(scenario_row.get('avg_absolute_increase'))} avg increase",
                "inverse": True,
            },
        ]
        st.markdown(kpi_strip_html(kpi_items), unsafe_allow_html=True)
        st.warning("Only summary-level stress-test output is available for this organization.")

        summary_rows = []
        for _, row in shock_summary.iterrows():
            summary_rows.append([
                scenario_label(row.get("scenario_name")),
                format_probability(row.get("avg_baseline_risk")),
                format_probability(row.get("avg_shocked_risk")),
                format_points(row.get("avg_absolute_increase")),
                format_relative(row.get("bucket_upshift_share")),
            ])
        table_html = html_table_html(
            headers=["Scenario", "Baseline Risk", "Stressed Risk", "Avg Increase", "Bucket Upshift"],
            rows=summary_rows,
            column_classes=["strong", "", "", "", "meta"],
        )
        st.markdown(
            activity_panel_html("Summary Shock Results", table_html),
            unsafe_allow_html=True,
        )
        return

    # ------- Full org-level output -------
    scenario_row = selected_shocks.loc[selected_shocks["scenario_name"] == selected_scenario].iloc[0]
    baseline_risk = scenario_row.get("baseline_risk")
    shocked_risk = scenario_row.get("shocked_risk")
    try:
        baseline_val = float(baseline_risk) if baseline_risk is not None else None
        shocked_val = float(shocked_risk) if shocked_risk is not None else None
    except (TypeError, ValueError):
        baseline_val = shocked_val = None
    risk_rising = (baseline_val is not None and shocked_val is not None and shocked_val > baseline_val)

    kpi_items = [
        {
            "label": "Baseline Risk",
            "value": format_probability(baseline_risk),
            "icon": "monitoring",
            "delta": clean_text(scenario_row.get("baseline_bucket")),
            "delta_icon": "label",
        },
        {
            "label": "Stressed Risk",
            "value": format_probability(shocked_risk),
            "icon": "warning",
            "delta": clean_text(scenario_row.get("shocked_bucket")),
            "delta_icon": "arrow_upward" if risk_rising else "arrow_downward",
            "delta_tone": "warn" if risk_rising else "ok",
        },
        {
            "label": "Risk Increase",
            "value": format_points(scenario_row.get("absolute_increase")),
            "icon": "insights",
            "delta": f"{format_relative(scenario_row.get('relative_increase'))} relative &mdash; {clean_text(scenario_row.get('risk_bucket_transition'))}",
            "inverse": True,
        },
    ]
    st.markdown(kpi_strip_html(kpi_items), unsafe_allow_html=True)

    # ------- Chart + Scenario Outcomes Table -------
    chart_col, table_col = st.columns([1.08, 0.92])
    with chart_col:
        st.markdown(
            module_header_html(
                "Scenario Sensitivity",
                legend=[
                    {"label": "Absolute Risk Delta", "color": "#000613"},
                    {"label": "Selected Scenario",   "color": "#fdb69a"},
                ],
            ),
            unsafe_allow_html=True,
        )
        st.plotly_chart(make_scenario_delta_chart(selected_shocks, selected_scenario), width="stretch")
    with table_col:
        outcomes = scenario_summary_table(selected_shocks)
        if outcomes.empty:
            st.markdown(
                activity_panel_html("Scenario Outcomes", html_table_html(headers=["No rows"], rows=[])),
                unsafe_allow_html=True,
            )
        else:
            table_headers = list(outcomes.columns)
            table_rows = [
                [clean_text(outcomes.iloc[i][col]) for col in table_headers]
                for i in range(len(outcomes))
            ]
            classes = ["strong"] + [""] * (len(table_headers) - 1)
            table_html = html_table_html(
                headers=table_headers,
                rows=table_rows,
                column_classes=classes,
            )
            st.markdown(
                activity_panel_html("Scenario Outcomes", table_html),
                unsafe_allow_html=True,
            )

    # ------- Observation narrative -------
    top_scenario = most_sensitive_scenario(selected_shocks)
    if top_scenario is not None:
        top_body = (
            f"<strong>{scenario_label(top_scenario.get('scenario_name'))}</strong> produces the largest modeled increase "
            f"for {clean_text(selected_row.get('business_name'))}: "
            f"<strong>{format_points(top_scenario.get('absolute_increase'))}</strong> to "
            f"<strong>{format_probability(top_scenario.get('shocked_risk'))}</strong>. "
            "Immediate contingency conversations are recommended before the next fiscal planning cycle."
        )
    else:
        top_body = "No dominant scenario was identified."
    st.markdown(sim_observation_html(top_body), unsafe_allow_html=True)

    # ------- Insight bento (3-up, last tile inverse) -------
    st.markdown(
        insight_bento_html(
            [
                {
                    "kicker": "Scenario Readout",
                    "title": scenario_label(selected_scenario),
                    "body": shock_explanation(selected_row, scenario_row, shock_source_mode),
                },
                {
                    "kicker": "Largest Downside Move",
                    "title": scenario_label(top_scenario.get("scenario_name")) if top_scenario is not None else "&mdash;",
                    "body": (
                        f"{format_points(top_scenario.get('absolute_increase'))} to "
                        f"{format_probability(top_scenario.get('shocked_risk'))}."
                    ) if top_scenario is not None else "No top scenario was available.",
                },
                {
                    "kicker": "How To Use This",
                    "title": "Contingency Compass",
                    "body": "This view compares downside sensitivity across scenarios to support contingency planning. It does not forecast what will happen in practice.",
                },
            ]
        ),
        unsafe_allow_html=True,
    )


def render_shortlist_section(title: str, shortlists: pd.DataFrame) -> None:
    section_table = shortlist_table_for_section(shortlists, title)
    if section_table.empty:
        empty_table = html_table_html(
            headers=["Status"],
            rows=[[status_chip_html("No organizations in this category", tone="warn")]],
        )
        st.markdown(
            activity_panel_html(title, empty_table),
            unsafe_allow_html=True,
        )
        return

    display = section_table.drop(columns=["ein"]).copy().rename(
        columns={"business_name": "Organization", "peer_group": "Peer group"}
    )
    display_headers = list(display.columns)
    display_rows = [
        [clean_text(display.iloc[i][col]) for col in display_headers]
        for i in range(len(display))
    ]
    display_classes = ["strong", "meta", "", "", ""]
    table_html_section = html_table_html(
        headers=display_headers,
        rows=display_rows,
        column_classes=display_classes[: len(display_headers)],
    )
    st.markdown(
        activity_panel_html(title, table_html_section),
        unsafe_allow_html=True,
    )

    chooser = {f"{row['business_name']} | {row['Baseline risk']}": row["ein"] for _, row in section_table.iterrows()}
    selected_option = st.selectbox(
        f"Choose an organization from {title}",
        options=list(chooser.keys()),
        key=f"chooser_{title}",
    )
    if st.button("Use selected organization in main view", key=f"button_{title}"):
        st.session_state["selected_ein"] = chooser[selected_option]
        rerun()


def tab_high_impact_discovery(shortlists: pd.DataFrame) -> None:
    if shortlists.empty:
        st.warning("No prioritization shortlist artifact was found.")
        return

    fragile_count = int((shortlists["shortlist_category"] == "Fragile but investable").sum())
    resilient_count = int((shortlists["shortlist_category"] == "Resilient outperformer").sum())
    watch_count = int((shortlists["shortlist_category"] == "Shock-sensitive priority watchlist").sum())
    total_count = fragile_count + resilient_count + watch_count

    st.markdown(
        executive_header_html(
            title="Attention Prioritization",
            body=(
                "Three financially actionable lenses sit on top of the baseline model: "
                "<strong>Fragile but investable</strong> surfaces elevated-risk cases with plausible intervention leverage; "
                "<strong>Resilient outperformers</strong> are peer-relative examples worth learning from; "
                "<strong>Shock-sensitive watchlist</strong> flags organizations with the sharpest deterministic downside. "
                "These are not mission-impact rankings."
            ),
            meta_lines=[
                f"Shortlisted Organizations <strong>{total_count}</strong>",
                f"Category Count <strong>3</strong>",
                "Source <strong>Retained Prioritization Artifact</strong>",
            ],
        ),
        unsafe_allow_html=True,
    )

    kpi_items = [
        {
            "label": "Fragile But Investable",
            "value": str(fragile_count),
            "icon": "medical_services",
            "delta": "Elevated-risk, intervention leverage",
            "delta_icon": "priority_high",
            "delta_tone": "warn",
        },
        {
            "label": "Resilient Outperformers",
            "value": str(resilient_count),
            "icon": "trending_up",
            "delta": "Peer-relative stronger positioning",
            "delta_icon": "check",
            "delta_tone": "ok",
        },
        {
            "label": "Shock-Sensitive Watchlist",
            "value": str(watch_count),
            "icon": "warning",
            "delta": "Sharpest downside sensitivity",
            "inverse": True,
        },
    ]
    st.markdown(kpi_strip_html(kpi_items), unsafe_allow_html=True)

    left, right = st.columns([1.08, 0.92])
    with left:
        st.markdown(
            module_header_html(
                "Prioritization Map",
                legend=[
                    {"label": "Fragile But Investable",    "color": "#12395b"},
                    {"label": "Resilient Outperformer",    "color": "#4f7f80"},
                    {"label": "Shock-Sensitive Watchlist", "color": "#a64743"},
                ],
            ),
            unsafe_allow_html=True,
        )
        st.plotly_chart(make_discovery_chart(shortlists), width="stretch")
    with right:
        overview = shortlist_overview_table(shortlists)
        if overview.empty:
            overview_table = html_table_html(headers=["No rows"], rows=[])
        else:
            overview_headers = list(overview.columns)
            overview_rows = [
                [clean_text(overview.iloc[i][col]) for col in overview_headers]
                for i in range(len(overview))
            ]
            overview_classes = ["strong", "meta", "", ""]
            overview_table = html_table_html(
                headers=overview_headers,
                rows=overview_rows,
                column_classes=overview_classes[: len(overview_headers)],
            )
        st.markdown(
            activity_panel_html("Category Summary", overview_table),
            unsafe_allow_html=True,
        )

    fragile = shortlists.loc[shortlists["shortlist_category"] == "Fragile but investable"].sort_values("predicted_distress_probability", ascending=False).iloc[0]
    resilient = shortlists.loc[shortlists["shortlist_category"] == "Resilient outperformer"].sort_values("predicted_distress_probability", ascending=True).iloc[0]
    watch = shortlists.loc[shortlists["shortlist_category"] == "Shock-sensitive priority watchlist"].sort_values("worst_case_delta", ascending=False).iloc[0]

    observation_body = (
        f"<strong>{clean_text(fragile.get('business_name'))}</strong> anchors the intervention pool at "
        f"<strong>{format_probability(fragile.get('predicted_distress_probability'))}</strong> baseline risk, "
        f"while <strong>{clean_text(watch.get('business_name'))}</strong> carries the sharpest modeled downside at "
        f"<strong>{format_points(watch.get('worst_case_delta'))}</strong>. "
        "Use these lists to decide where attention may matter most financially &mdash; they do not measure mission impact."
    )
    st.markdown(
        sim_observation_html(observation_body, kicker="Prioritization Read"),
        unsafe_allow_html=True,
    )

    st.markdown(
        insight_bento_html(
            [
                {
                    "kicker": "Fragile But Investable",
                    "title": clean_text(fragile.get("business_name")),
                    "body": f"Representative intervention candidate with {format_probability(fragile.get('predicted_distress_probability'))} baseline risk.",
                },
                {
                    "kicker": "Resilient Outperformers",
                    "title": clean_text(resilient.get("business_name")),
                    "body": "Shows what stronger reserve, margin, and leverage positioning looks like within its peer frame.",
                },
                {
                    "kicker": "Shock-Sensitive Watchlist",
                    "title": clean_text(watch.get("business_name")),
                    "body": f"Sharpest deterministic downside move at {format_points(watch.get('worst_case_delta'))}.",
                },
            ]
        ),
        unsafe_allow_html=True,
    )

    for title in ["Fragile but investable", "Resilient outperformers", "Shock-sensitive watchlist"]:
        render_shortlist_section(title, shortlists)


def tab_portfolio_rankings(bundle: dict) -> None:
    orgs = bundle["orgs"]
    shortlists = bundle["shortlists"]
    shock_results = bundle["shock_results"]
    portfolio = get_portfolio_frame_cached(orgs, shortlists, shock_results)
    if portfolio.empty:
        st.warning("Portfolio ranking inputs are missing.")
        return

    scenario_options = scenario_control_options(shock_results)
    current_scenario_control = st.session_state.get("portfolio_scenario_control", SCENARIO_CONTROL_ALL)
    if current_scenario_control not in scenario_options:
        current_scenario_control = SCENARIO_CONTROL_ALL
        st.session_state["portfolio_scenario_control"] = current_scenario_control
    scenario_metric_options = list(SCENARIO_METRICS.keys())
    if st.session_state.get("portfolio_scenario_metric") not in scenario_metric_options:
        st.session_state["portfolio_scenario_metric"] = scenario_metric_options[0]
    observed_only_supported = "observed_data_flag" in portfolio.columns
    observed_only_already_full = (
        bool(series_or_default(portfolio, "observed_data_flag", True).fillna(True).all())
        if observed_only_supported
        else False
    )

    st.markdown(
        executive_header_html(
            title="Portfolio Prioritization",
            body=(
                "Refine institutional datasets across prioritization lenses, peer frames, and stress scenarios. "
                "Use the primary controls to pick a lens, then push an organization into the shared main view with the sync action."
            ),
            meta_lines=[
                f"Total Rows <strong>{len(portfolio):,}</strong>",
                f"Observed-Only Available <strong>{'Yes' if observed_only_supported and not observed_only_already_full else 'No'}</strong>",
                f"Stress Scenarios <strong>{len(scenario_options)}</strong>",
            ],
        ),
        unsafe_allow_html=True,
    )

    # ---- Primary controls (compact row; always visible) ----
    controls_row_1 = st.columns([1.35, 1.1, 1.0, 0.7, 0.8])
    with controls_row_1[0]:
        ranking_mode = st.selectbox("Prioritization lens", options=RANKING_MODES, key="portfolio_ranking_mode")
    with controls_row_1[1]:
        scenario_control = st.selectbox(
            "Stress scenario",
            options=scenario_options,
            index=scenario_options.index(current_scenario_control),
            format_func=scenario_label,
            key="portfolio_scenario_control",
        )
    with controls_row_1[2]:
        scenario_metric = st.selectbox(
            "Stress ranking metric",
            options=scenario_metric_options,
            key="portfolio_scenario_metric",
        )
    with controls_row_1[3]:
        top_n = st.selectbox("Top N", options=[10, 25, 50, 100], index=1, key="portfolio_top_n")
    with controls_row_1[4]:
        sort_direction = st.selectbox("Sort direction", options=["Descending", "Ascending"], key="portfolio_sort_direction")

    # ---- Advanced filter drawer ----
    with st.expander("Advanced Filters", expanded=False):
        controls_row_2 = st.columns(4)
        with controls_row_2[0]:
            peer_group_filter = st.multiselect(
                "Peer group",
                options=safe_options(portfolio, "peer_group"),
                format_func=humanize_peer_group,
                key="portfolio_peer_group",
            )
        with controls_row_2[1]:
            size_filter = st.multiselect(
                "Size band",
                options=safe_options(portfolio, "size_bucket"),
                format_func=humanize_size_bucket,
                key="portfolio_size_band",
            )
        with controls_row_2[2]:
            funding_filter = st.multiselect(
                "Funding model",
                options=safe_options(portfolio, "funding_bucket"),
                format_func=humanize_funding_bucket,
                key="portfolio_funding_model",
            )
        with controls_row_2[3]:
            risk_bucket_filter = st.multiselect("Risk bucket", options=safe_options(portfolio, "risk_bucket"), key="portfolio_risk_bucket")

        controls_row_3 = st.columns(4)
        with controls_row_3[0]:
            state_filter = st.multiselect("State", options=safe_options(portfolio, "state"), key="portfolio_state")
        with controls_row_3[1]:
            sector_filter = st.multiselect("Sector", options=safe_options(portfolio, "sector_group"), key="portfolio_sector")
        with controls_row_3[2]:
            shortlist_filter = st.multiselect("Shortlist category", options=safe_options(portfolio, "shortlist_category"), key="portfolio_shortlist")
        with controls_row_3[3]:
            observed_only = st.checkbox(
                "Observed-only clean-data rows",
                value=True,
                disabled=not observed_only_supported or observed_only_already_full,
                key="portfolio_observed_only",
            )
            if observed_only_supported and observed_only_already_full:
                st.caption("Current bundle already consists of observed scored rows.")
            elif not observed_only_supported:
                st.caption("Observed-only filtering is not available from the current artifact set.")

    # ---- Visual compact filter bar (reflects primary widget state) ----
    entity_label = "All peer frames"
    if peer_group_filter:
        first = humanize_peer_group(peer_group_filter[0])
        entity_label = first if len(peer_group_filter) == 1 else f"{first} +{len(peer_group_filter) - 1} more"
    output_label = f"Top {top_n}, {sort_direction}"
    st.markdown(
        compact_filter_bar_html(
            groups=[
                {"label": "Core Analysis", "value": ranking_mode},
                {"label": "Entity Profile", "value": entity_label},
                {"label": "Output", "value": output_label},
            ],
            actions=[
                {"label": "Clear Filters", "icon": "close"},
                {"label": "Advanced", "icon": "tune", "primary": True},
            ],
        ),
        unsafe_allow_html=True,
    )

    # ---- Active lens chips ----
    lenses: list[dict] = [
        {"category": "Lens", "value": ranking_mode},
        {"category": "Stress", "value": scenario_label(scenario_control)},
    ]
    for val in peer_group_filter:
        lenses.append({"category": "Peer", "value": humanize_peer_group(val)})
    for val in size_filter:
        lenses.append({"category": "Size", "value": humanize_size_bucket(val)})
    for val in funding_filter:
        lenses.append({"category": "Funding", "value": humanize_funding_bucket(val)})
    for val in state_filter:
        lenses.append({"category": "State", "value": clean_text(val)})
    for val in sector_filter:
        lenses.append({"category": "Sector", "value": clean_text(val)})
    for val in risk_bucket_filter:
        lenses.append({"category": "Risk Bucket", "value": clean_text(val)})
    for val in shortlist_filter:
        lenses.append({"category": "Shortlist", "value": clean_text(val)})
    if observed_only_supported and observed_only and not observed_only_already_full:
        lenses.append({"category": "Data", "value": "Observed-only"})
    st.markdown(filter_lenses_html(lenses), unsafe_allow_html=True)

    filtered = apply_filters(
        portfolio,
        peer_groups=peer_group_filter,
        size_bands=size_filter,
        funding_models=funding_filter,
        states=state_filter,
        sectors=sector_filter,
        risk_buckets=risk_bucket_filter,
        shortlist_categories=shortlist_filter,
        observed_only=observed_only if observed_only_supported else False,
    )
    scenario_view = with_scenario_view(filtered, shock_results, scenario_control)
    summary = build_summary_metrics(filtered, shock_results)

    # ---- KPI strip (3-up, last inverse) ----
    high_risk_val = summary["high_risk_share"] if value_is_available(summary["high_risk_share"]) else None
    baseline_val = summary["avg_baseline_risk"] if value_is_available(summary["avg_baseline_risk"]) else None
    most_common_peer = humanize_peer_group(summary["most_common_peer_group"]) if summary.get("most_common_peer_group") else "&mdash;"
    kpi_items = [
        {
            "label": "Filtered Rows",
            "value": f"{summary['count']:,}",
            "icon": "database",
            "delta": f"Most common peer &mdash; <strong>{most_common_peer}</strong>",
            "delta_icon": "groups",
        },
        {
            "label": "Average Baseline Risk",
            "value": format_probability(baseline_val) if baseline_val is not None else "&mdash;",
            "icon": "monitoring",
            "delta": "Across the current slice",
            "delta_icon": "insights",
        },
        {
            "label": "High-Risk Share",
            "value": format_relative(high_risk_val) if high_risk_val is not None else "&mdash;",
            "icon": "priority_high",
            "delta": "High or Very High buckets",
            "delta_icon": "warning",
            "inverse": True,
        },
    ]
    st.markdown(kpi_strip_html(kpi_items), unsafe_allow_html=True)

    ranked, note = rank_frame(
        scenario_view,
        mode=ranking_mode,
        scenario_metric=scenario_metric,
        sort_direction=sort_direction,
        top_n=int(top_n),
    )
    if note:
        st.markdown(note_card_html(note), unsafe_allow_html=True)

    # ---- Ranked table + side panel ----
    table_left, table_right = st.columns([1.55, 0.45])
    with table_left:
        st.markdown(
            module_header_html(
                "Portfolio Prioritization Table",
                legend=[
                    {"label": "Elevated risk", "color": "#a64743"},
                    {"label": "Watch",         "color": "#fdb69a"},
                    {"label": "Stable",        "color": "#4f7f80"},
                ],
            ),
            unsafe_allow_html=True,
        )
        if ranked.empty:
            empty_table = rank_table_html(
                headers=["Status"],
                rows=[[status_chip_html("No organizations matched the current filters", tone="warn")]],
            )
            st.markdown(
                activity_panel_html("Prioritization Output", empty_table),
                unsafe_allow_html=True,
            )
        else:
            def _risk_tone(bucket: str) -> str:
                b = (bucket or "").lower()
                if "very high" in b or b == "high":
                    return "alert"
                if "watch" in b:
                    return "warn"
                if "low" in b:
                    return "ok"
                return "neutral"

            rank_rows = []
            for i, (_, row) in enumerate(ranked.iterrows(), start=1):
                bucket_raw = clean_text(row.get("risk_bucket"))
                tone = _risk_tone(bucket_raw)
                baseline_txt = format_probability(row.get("predicted_distress_probability"))
                stress_src = row.get("scenario_absolute_delta")
                if pd.isna(stress_src):
                    stress_src = row.get("worst_case_delta")
                stress_txt = format_points(stress_src)
                peer_txt = humanize_peer_group(row.get("peer_group"))
                rank_rows.append([
                    f"{i:02d}",
                    clean_text(row.get("business_name")),
                    peer_txt,
                    clean_text(row.get("state"), fallback="-"),
                    baseline_txt,
                    stress_txt,
                    status_dot_html(tone),
                ])
            rank_table = rank_table_html(
                headers=["Rank", "Organization", "Peer Group", "State", "Baseline Risk", "Stress Delta", "Status"],
                rows=rank_rows,
                column_classes=["rank", "strong", "meta", "meta", "num", "num", "center"],
                column_aligns=["", "", "", "", "right", "right", "center"],
            )
            st.markdown(
                activity_panel_html("Prioritization Output", rank_table),
                unsafe_allow_html=True,
            )
            st.markdown(
                pagination_footer_html(
                    showing=f"Showing 1-{len(ranked)} of {len(filtered):,} prioritized entities."
                ),
                unsafe_allow_html=True,
            )

    with table_right:
        top_row = ranked.iloc[0] if not ranked.empty else None
        interpretation = "No organizations matched the current filters."
        if top_row is not None:
            interpretation = (
                f"Current leader: <strong>{clean_text(top_row.get('business_name'))}</strong>. "
                f"Ranks first for &ldquo;{ranking_mode.lower()}&rdquo; with baseline risk "
                f"<strong>{format_probability(top_row.get('predicted_distress_probability'))}</strong>."
            )
        st.markdown(
            sim_observation_html(interpretation, kicker="Quick Read"),
            unsafe_allow_html=True,
        )

        if not ranked.empty:
            selected_option_map = {
                f"{clean_text(row['business_name'])} | {format_probability(row.get('predicted_distress_probability'))} | {format_ein(row['ein'])}": row["ein"]
                for _, row in ranked.iterrows()
            }
            current_portfolio_focus = st.session_state.get("portfolio_selected_ein")
            if current_portfolio_focus not in ranked["ein"].tolist():
                current_portfolio_focus = ranked.iloc[0]["ein"]
                st.session_state["portfolio_selected_ein"] = current_portfolio_focus

            selected_key = next(
                (label for label, ein in selected_option_map.items() if ein == current_portfolio_focus),
                list(selected_option_map.keys())[0],
            )
            selected_rank_label = st.selectbox(
                "Selected organization",
                options=list(selected_option_map.keys()),
                index=list(selected_option_map.keys()).index(selected_key),
                key="portfolio_selected_row",
            )
            selected_rank_ein = selected_option_map[selected_rank_label]
            st.session_state["portfolio_selected_ein"] = selected_rank_ein
            selected_rank_row = ranked.loc[ranked["ein"] == selected_rank_ein].iloc[0]
            detail_table = html_table_html(
                headers=["Field", "Value"],
                rows=[
                    ["EIN", format_ein(selected_rank_row.get("ein"))],
                    ["Peer group", humanize_peer_group(selected_rank_row.get("peer_group"))],
                    ["Baseline risk", format_probability(selected_rank_row.get("predicted_distress_probability"))],
                    ["Reserve percentile", format_percentile(selected_rank_row.get("peer_reserve_percentile"))],
                    ["Leverage percentile", format_percentile(selected_rank_row.get("peer_liability_percentile"))],
                    ["Top stress scenario", scenario_label(
                        selected_rank_row.get("scenario_name_view")
                        if pd.notna(selected_rank_row.get("scenario_name_view"))
                        else selected_rank_row.get("top_scenario")
                    )],
                    ["Stress delta", format_points(
                        selected_rank_row.get("scenario_absolute_delta")
                        if pd.notna(selected_rank_row.get("scenario_absolute_delta"))
                        else selected_rank_row.get("worst_case_delta")
                    )],
                ],
                column_classes=["meta", "strong"],
            )
            st.markdown(
                activity_panel_html(
                    clean_text(selected_rank_row.get("business_name")) or "Selected organization",
                    detail_table,
                ),
                unsafe_allow_html=True,
            )
            if st.button("Use selected organization in main view", key="portfolio_sync_button"):
                st.session_state["selected_ein"] = selected_rank_ein
                rerun()

    # ---- Insight bento (3-up, last inverse) ----
    st.markdown(
        insight_bento_html(
            [
                {
                    "kicker": "Prioritization Lens",
                    "title": ranking_mode,
                    "body": "Use it to compare portfolio-wide patterns before drilling into a single organization.",
                },
                {
                    "kicker": "Stress Setting",
                    "title": scenario_label(scenario_control),
                    "body": f"Ranks by {scenario_metric.lower()} within the selected scenario control.",
                },
                {
                    "kicker": "Workflow",
                    "title": "Scan → Select → Sync",
                    "body": "Use the table to identify a candidate, review the selected-organization panel, and push that organization into the main tabs with the sync button.",
                },
            ]
        ),
        unsafe_allow_html=True,
    )


def tab_data_explorer(bundle: dict) -> None:
    orgs = bundle["orgs"]
    shortlists = bundle["shortlists"]
    if orgs.empty:
        st.warning("The scored universe is unavailable.")
        return

    if not shortlists.empty and "shortlist_category" in shortlists.columns and "ein" in shortlists.columns:
        base = orgs.merge(
            shortlists[["ein", "shortlist_category"]].drop_duplicates("ein"),
            on="ein",
            how="left",
        )
    else:
        base = orgs.copy()

    st.markdown(
        executive_header_html(
            title="Scored Universe Explorer",
            body=(
                "Search, filter, and export the full scored universe of nonprofit entities. This view is for ad-hoc "
                "discovery &mdash; for curated triage, switch back to Portfolio Prioritization or Attention Prioritization."
            ),
            meta_lines=[
                f"Total Rows <strong>{len(orgs):,}</strong>",
                f"Columns Indexed <strong>{len(orgs.columns)}</strong>",
                f"Shortlisted <strong>{len(shortlists):,}</strong>",
            ],
        ),
        unsafe_allow_html=True,
    )

    ctrls = st.columns([1.8, 1.0, 1.0, 0.8])
    with ctrls[0]:
        search = st.text_input(
            "Search by name or EIN",
            key="explorer_search",
            placeholder="e.g. United Way or 13-0000000",
        )
    with ctrls[1]:
        rows_per_page = int(st.selectbox(
            "Rows per page",
            options=[10, 25, 50, 100],
            index=1,
            key="explorer_rows_per_page",
        ))
    with ctrls[2]:
        sort_column = st.selectbox(
            "Sort by",
            options=["Baseline risk", "Reserve percentile", "Leverage percentile", "Total revenue"],
            key="explorer_sort_column",
        )
    with ctrls[3]:
        sort_direction = st.selectbox(
            "Direction",
            options=["Descending", "Ascending"],
            key="explorer_sort_direction",
        )

    with st.expander("Advanced Filters", expanded=False):
        row_a = st.columns(4)
        with row_a[0]:
            state_filter = st.multiselect("State", options=safe_options(base, "state"), key="explorer_state")
        with row_a[1]:
            sector_filter = st.multiselect("Sector", options=safe_options(base, "sector_group"), key="explorer_sector")
        with row_a[2]:
            peer_filter = st.multiselect(
                "Peer group",
                options=safe_options(base, "peer_group"),
                format_func=humanize_peer_group,
                key="explorer_peer",
            )
        with row_a[3]:
            risk_filter = st.multiselect("Risk bucket", options=safe_options(base, "risk_bucket"), key="explorer_risk")
        row_b = st.columns(4)
        with row_b[0]:
            funding_filter = st.multiselect(
                "Funding model",
                options=safe_options(base, "funding_bucket"),
                format_func=humanize_funding_bucket,
                key="explorer_funding",
            )
        with row_b[1]:
            shortlist_filter = st.multiselect(
                "Shortlist category",
                options=safe_options(base, "shortlist_category"),
                key="explorer_shortlist",
            )

    filtered = base.copy()
    if search and search.strip():
        pattern = search.strip().lower()
        name_series = series_or_default(filtered, "business_name", "").fillna("").astype(str).str.lower()
        ein_series = series_or_default(filtered, "ein", "").fillna("").astype(str).str.lower()
        mask = name_series.str.contains(pattern, regex=False, na=False) | ein_series.str.contains(pattern, regex=False, na=False)
        filtered = filtered.loc[mask]
    if state_filter and "state" in filtered.columns:
        filtered = filtered.loc[filtered["state"].astype(str).isin(state_filter)]
    if sector_filter and "sector_group" in filtered.columns:
        filtered = filtered.loc[filtered["sector_group"].astype(str).isin(sector_filter)]
    if peer_filter and "peer_group" in filtered.columns:
        filtered = filtered.loc[filtered["peer_group"].astype(str).isin(peer_filter)]
    if risk_filter and "risk_bucket" in filtered.columns:
        filtered = filtered.loc[filtered["risk_bucket"].astype(str).isin(risk_filter)]
    if funding_filter and "funding_bucket" in filtered.columns:
        filtered = filtered.loc[filtered["funding_bucket"].astype(str).isin(funding_filter)]
    if shortlist_filter and "shortlist_category" in filtered.columns:
        filtered = filtered.loc[filtered["shortlist_category"].astype(str).isin(shortlist_filter)]

    sort_map = {
        "Baseline risk": "predicted_distress_probability",
        "Reserve percentile": "peer_reserve_percentile",
        "Leverage percentile": "peer_liability_percentile",
        "Total revenue": "total_revenue",
    }
    sort_col = sort_map[sort_column]
    if sort_col in filtered.columns:
        sort_values = pd.to_numeric(filtered[sort_col], errors="coerce")
        sorted_df = filtered.assign(__sort=sort_values).sort_values(
            "__sort", ascending=(sort_direction == "Ascending"), na_position="last"
        ).drop(columns="__sort")
    else:
        sorted_df = filtered

    cohort_bits: list[str] = []
    if state_filter:
        cohort_bits.append(clean_text(state_filter[0]) + (f" +{len(state_filter) - 1}" if len(state_filter) > 1 else ""))
    if sector_filter:
        cohort_bits.append(clean_text(sector_filter[0]) + (f" +{len(sector_filter) - 1}" if len(sector_filter) > 1 else ""))
    cohort_label = " / ".join(cohort_bits) if cohort_bits else "All cohorts"
    st.markdown(
        compact_filter_bar_html(
            groups=[
                {"label": "Slice", "value": f"{len(sorted_df):,} rows"},
                {"label": "Cohort", "value": cohort_label},
                {"label": "Output", "value": f"{sort_column}, {sort_direction}"},
            ],
            actions=[
                {"label": "Clear Search", "icon": "close"},
                {"label": "Advanced", "icon": "tune", "primary": True},
            ],
        ),
        unsafe_allow_html=True,
    )

    lenses: list[dict] = []
    if search and search.strip():
        lenses.append({"category": "Search", "value": search.strip()})
    for v in state_filter:
        lenses.append({"category": "State", "value": clean_text(v)})
    for v in sector_filter:
        lenses.append({"category": "Sector", "value": clean_text(v)})
    for v in peer_filter:
        lenses.append({"category": "Peer", "value": humanize_peer_group(v)})
    for v in risk_filter:
        lenses.append({"category": "Risk", "value": clean_text(v)})
    for v in funding_filter:
        lenses.append({"category": "Funding", "value": humanize_funding_bucket(v)})
    for v in shortlist_filter:
        lenses.append({"category": "Shortlist", "value": clean_text(v)})
    st.markdown(filter_lenses_html(lenses), unsafe_allow_html=True)

    median_risk = None
    high_share = None
    if not sorted_df.empty:
        risk_series = pd.to_numeric(
            series_or_default(sorted_df, "predicted_distress_probability"),
            errors="coerce",
        )
        if not risk_series.dropna().empty:
            median_risk = float(risk_series.median())
        if "risk_bucket" in sorted_df.columns:
            high_mask = sorted_df["risk_bucket"].astype(str).str.lower().isin(["high", "very high"])
            high_share = float(high_mask.sum()) / float(len(sorted_df))

    kpi_items = [
        {
            "label": "Matching Rows",
            "value": f"{len(sorted_df):,}",
            "icon": "database",
            "delta": f"of {len(orgs):,} scored",
            "delta_icon": "percent",
        },
        {
            "label": "Median Baseline Risk",
            "value": format_probability(median_risk) if median_risk is not None else "&mdash;",
            "icon": "monitoring",
            "delta": "Across the current slice",
            "delta_icon": "insights",
        },
        {
            "label": "High-Risk Share",
            "value": format_relative(high_share) if high_share is not None else "&mdash;",
            "icon": "priority_high",
            "delta": "High or Very High buckets",
            "delta_icon": "warning",
            "inverse": True,
        },
    ]
    st.markdown(kpi_strip_html(kpi_items), unsafe_allow_html=True)

    total_rows = len(sorted_df)
    total_pages = max(1, -(-total_rows // rows_per_page)) if rows_per_page else 1
    current_page = int(st.session_state.get("explorer_page", 1))
    current_page = min(max(1, current_page), total_pages)
    st.session_state["explorer_page"] = current_page
    start_idx = (current_page - 1) * rows_per_page
    end_idx = min(start_idx + rows_per_page, total_rows)
    page_df = sorted_df.iloc[start_idx:end_idx]

    header_col, csv_col = st.columns([0.78, 0.22])
    with header_col:
        st.markdown(
            module_header_html(
                "Scored Universe",
                legend=[
                    {"label": "Elevated", "color": "#a64743"},
                    {"label": "Watch", "color": "#fdb69a"},
                    {"label": "Stable", "color": "#4f7f80"},
                ],
            ),
            unsafe_allow_html=True,
        )
    with csv_col:
        csv_bytes = sorted_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download CSV",
            data=csv_bytes,
            file_name=f"fairlight_scored_universe_{total_rows}_rows.csv",
            mime="text/csv",
            key="explorer_csv",
            width="stretch",
        )

    def _tone(bucket: str) -> str:
        b = (bucket or "").lower()
        if "very high" in b or b == "high":
            return "alert"
        if "watch" in b:
            return "warn"
        if "low" in b:
            return "ok"
        return "neutral"

    if page_df.empty:
        empty_table = rank_table_html(
            headers=["Status"],
            rows=[[status_chip_html("No organizations matched the current filters", tone="warn")]],
        )
        st.markdown(activity_panel_html("Scored Universe", empty_table), unsafe_allow_html=True)
    else:
        rank_rows = []
        for i, (_, row) in enumerate(page_df.iterrows(), start=start_idx + 1):
            rank_rows.append([
                f"{i:03d}",
                clean_text(row.get("business_name")),
                format_ein(row.get("ein")),
                clean_text(row.get("state"), fallback="-"),
                clean_text(row.get("sector_group"), fallback="-"),
                humanize_peer_group(row.get("peer_group")),
                format_probability(row.get("predicted_distress_probability")),
                format_percentile(row.get("peer_reserve_percentile")),
                format_percentile(row.get("peer_liability_percentile")),
                status_dot_html(_tone(clean_text(row.get("risk_bucket")))),
            ])
        rank_table = rank_table_html(
            headers=[
                "#", "Organization", "EIN", "State", "Sector", "Peer Group",
                "Baseline Risk", "Reserve %ile", "Leverage %ile", "Risk",
            ],
            rows=rank_rows,
            column_classes=[
                "rank", "strong", "meta", "meta", "", "meta",
                "num", "num", "num", "center",
            ],
            column_aligns=[
                "", "", "", "", "", "",
                "right", "right", "right", "center",
            ],
        )
        st.markdown(activity_panel_html("Scored Universe", rank_table), unsafe_allow_html=True)

        showing = (
            f"Showing <strong>{start_idx + 1:,}</strong>&ndash;<strong>{end_idx:,}</strong> "
            f"of <strong>{total_rows:,}</strong> entities &middot; "
            f"Page {current_page:,} of {total_pages:,}"
        )
        st.markdown(pagination_footer_html(showing=showing), unsafe_allow_html=True)

        pager_cols = st.columns([0.15, 0.7, 0.15])
        with pager_cols[0]:
            if st.button("← Prev", key="explorer_prev", disabled=(current_page <= 1), width="stretch"):
                st.session_state["explorer_page"] = current_page - 1
                rerun()
        with pager_cols[2]:
            if st.button("Next →", key="explorer_next", disabled=(current_page >= total_pages), width="stretch"):
                st.session_state["explorer_page"] = current_page + 1
                rerun()

    if total_rows == 0:
        obs_body = "No rows matched the current slice. Broaden the filters to see more entities."
    else:
        first_row = sorted_df.iloc[0]
        obs_body = (
            f"The current slice leads with <strong>{clean_text(first_row.get('business_name'))}</strong> "
            f"at baseline risk <strong>{format_probability(first_row.get('predicted_distress_probability'))}</strong>. "
            f"Export the active slice with the CSV action &mdash; the download mirrors every filter and sort applied here."
        )
    st.markdown(sim_observation_html(obs_body, kicker="Slice Summary"), unsafe_allow_html=True)

    st.markdown(
        insight_bento_html(
            [
                {
                    "kicker": "Universe Coverage",
                    "title": f"{len(orgs):,} Scored Entities",
                    "body": "Every row here was scored against the retained peer-relative composite label. Apply cohort filters to zoom into a sector, state, or peer frame before exporting.",
                },
                {
                    "kicker": "Export Discipline",
                    "title": "CSV Mirrors The Slice",
                    "body": "Downloads reflect active filters and sort order &mdash; not only the paginated window &mdash; so you can hand off exactly the slice you inspected.",
                },
                {
                    "kicker": "How To Use This",
                    "title": "Discovery Before Decision",
                    "body": "Treat the Explorer as a discovery tool; graduate candidates into Portfolio Prioritization or Attention Prioritization to build a triage narrative.",
                },
            ]
        ),
        unsafe_allow_html=True,
    )


def resolve_search_to_ein(orgs: pd.DataFrame, query: str) -> str | None:
    """Resolve a free-text query to an EIN. Accepts 9-digit EIN (with or without
    hyphens/spaces) or a business-name substring. Returns None on miss."""
    if not query:
        return None
    q = query.strip()
    if not q:
        return None
    digits = "".join(ch for ch in q if ch.isdigit())
    if len(digits) == 9 and "ein" in orgs.columns:
        hit = orgs.loc[orgs["ein"].astype(str).str.replace(r"\D", "", regex=True) == digits]
        if not hit.empty:
            return str(hit.iloc[0]["ein"])
    if "business_name" in orgs.columns:
        names = orgs["business_name"].astype(str).str.lower()
        mask = names.str.contains(q.lower(), na=False, regex=False)
        if mask.any():
            return str(orgs.loc[mask].iloc[0]["ein"])
    return None


def render_landing(bundle: dict) -> None:
    """Fairlight Resilience Decision System landing page.

    Clean search + selection interface: slim product-name strip →
    rounded-pill search bar with orange accent → centered
    "Select Entity Context" dropdown (primary focal point).
    """
    orgs = bundle["orgs"]

    st.markdown(
        landing_header_strip_html(
            title="Fairlight Resilience Decision System",
            eyebrow="Intelligence &middot; Institutional Terminal",
        ),
        unsafe_allow_html=True,
    )

    with st.container(key="landing_search"):
        with st.form("landing_search_form", clear_on_submit=False):
            query = st.text_input(
                "Search",
                placeholder="Search Company/EIN",
                label_visibility="collapsed",
                key="landing_search_query",
            )
            submitted = st.form_submit_button("Submit")
        if submitted:
            hit = resolve_search_to_ein(orgs, query)
            if hit:
                st.session_state["selected_ein"] = hit
                st.toast(f"Routed to EIN {format_ein(hit)}", icon=":material/verified:")
                rerun()
            elif query.strip():
                st.warning(f"No match for “{query}”. Try an EIN or refine the name.")

    st.markdown(
        landing_headline_html(
            title_html="Select Entity Context",
            subtitle="Establish operational parameters before initiating institutional analysis.",
        ),
        unsafe_allow_html=True,
    )

    option_map = {row["ein"]: row["org_label"] for _, row in orgs.iterrows()}
    option_eins = list(option_map.keys())
    if st.session_state["selected_ein"] not in option_map:
        st.session_state["selected_ein"] = option_eins[0]
    last_synced_ein = st.session_state.get("landing_org_select_synced")
    if "landing_org_select" not in st.session_state:
        st.session_state["landing_org_select"] = st.session_state["selected_ein"]
    elif st.session_state["selected_ein"] != last_synced_ein:
        st.session_state["landing_org_select"] = st.session_state["selected_ein"]
    st.session_state["landing_org_select_synced"] = st.session_state["selected_ein"]
    with st.container(key="landing_directory"):
        selected_ein = st.selectbox(
            "Organization",
            options=option_eins,
            format_func=lambda ein: option_map.get(ein, ein),
            label_visibility="collapsed",
            key="landing_org_select",
        )
    if selected_ein != st.session_state["selected_ein"]:
        st.session_state["selected_ein"] = selected_ein
        st.session_state["landing_org_select_synced"] = selected_ein
        rerun()


def main() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
    bundle = get_bundle()
    orgs = bundle["orgs"]
    if orgs.empty:
        st.error("No scored organization universe was found. Check the rerun artifact paths in `data_contract_streamlit.md`.")
        return

    if "selected_ein" not in st.session_state:
        st.session_state["selected_ein"] = bundle.get("default_ein") or orgs.iloc[0]["ein"]

    render_sidebar(bundle)
    render_landing(bundle)
    selected_ein = st.session_state["selected_ein"]
    selected_row = current_org_row(orgs, selected_ein)
    selected_shocks = org_shocks(bundle["shock_results"], selected_ein)
    render_company_brief(selected_row, selected_shocks, bundle["shortlists"])

    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(TAB_TITLES)
    with tab1:
        tab_risk_lookup(selected_row, bundle["threshold_scan"])
    with tab2:
        tab_peer_benchmarking(orgs, selected_row)
    with tab3:
        tab_shock_simulator(
            selected_row,
            bundle["shock_results"],
            bundle["shock_summary"],
            bundle["shock_source_mode"],
            bundle["shock_source_note"],
        )
    with tab4:
        tab_high_impact_discovery(bundle["shortlists"])
    with tab5:
        tab_portfolio_rankings(bundle)
    with tab6:
        tab_data_explorer(bundle)


if __name__ == "__main__":
    main()
