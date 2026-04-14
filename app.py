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
    brief_meta_card_html,
    brief_summary_card_html,
    flag_chip_html,
    hero_html,
    insight_card_html,
    metric_card_html,
    note_card_html,
    risk_pill_html,
    selector_note_html,
    section_card_html,
    sidebar_note_card_html,
    sidebar_stat_card_html,
)


PAGE_TITLE = "Fairlight Resilience Demo"
TAB_TITLES = [
    "1. Risk Score Lookup",
    "2. Peer Benchmarking",
    "3. Shock Simulator",
    "4. High-Impact Discovery",
    "5. Portfolio Rankings",
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


def dataframe_height(frame: pd.DataFrame, max_height: int = 440) -> int:
    rows = max(1, len(frame))
    return min(max_height, 46 + rows * 36)


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
    fig.update_xaxes(title="Percentile within peer group", range=[0, 112])
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
    fig.update_xaxes(title="Risk increase under shock (points)")
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
    fig.update_yaxes(title="Worst-case shock delta (points)")
    return apply_chart_style(fig, height=440, margin_left=48, margin_right=24, margin_bottom=50, showlegend=True)


def render_metric_cards(cards: list[tuple[str, str, str]]) -> None:
    if not cards:
        return
    columns = st.columns(len(cards))
    for column, (title, value, subtitle) in zip(columns, cards):
        with column:
            st.markdown(metric_card_html(title, value, subtitle), unsafe_allow_html=True)


def render_method_note(bundle: dict) -> None:
    run_summary = bundle.get("run_summary", {})
    with st.expander("Method note / about this score", expanded=False):
        st.markdown(
            "\n".join(
                [
                    "- Retained label: `peer_relative_composite`",
                    "- Retained model: `upgraded logistic regression`",
                    "- Simulator is deterministic, not causal",
                    "- Donor vs grant / government exposure may be approximated from IRS filing structure",
                    "- Peer-relative signals are computed on observed rows only",
                    f"- Current run summary points to model `{run_summary.get('final_model', 'unknown')}`",
                ]
            )
        )


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
                "Observed 2023 nonprofit rows available in the scored universe.",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            sidebar_stat_card_html(
                "Stress scenarios",
                f"{shock_results['scenario_name'].nunique() if not shock_results.empty else len(SCENARIO_LABELS)}",
                "Deterministic downside tests available in the simulator.",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            sidebar_stat_card_html(
                "Shortlisted",
                f"{len(shortlists):,}",
                "Financial resilience and intervention-readiness shortlist rows.",
            ),
            unsafe_allow_html=True,
        )
        st.markdown(
            sidebar_note_card_html(
                f"Broadest stressor: {scenario_label(top_scenario)}."
            ),
            unsafe_allow_html=True,
        )
        with st.expander("Method note / about this score", expanded=False):
            st.markdown(
                "\n".join(
                    [
                        "- Retained label: `peer_relative_composite`",
                        "- Retained model: `upgraded logistic regression`",
                        "- Simulator is deterministic, not causal",
                        "- Peer-relative signals are computed on observed rows only",
                    ]
                )
            )


def render_selector(orgs: pd.DataFrame) -> str:
    st.markdown('<div class="section-header">Company selector</div>', unsafe_allow_html=True)
    st.markdown(
        selector_note_html("Choose a nonprofit from the dropdown to update every tab on the page."),
        unsafe_allow_html=True,
    )
    option_map = {row["org_label"]: row["ein"] for _, row in orgs.iterrows()}
    option_labels = list(option_map.keys())
    current_label = next(
        (label for label, ein in option_map.items() if ein == st.session_state["selected_ein"]),
        option_labels[0],
    )
    selected_label = st.selectbox(
        "Choose nonprofit",
        options=option_labels,
        index=option_labels.index(current_label),
        label_visibility="collapsed",
    )
    chosen_ein = option_map[selected_label]
    if chosen_ein != st.session_state["selected_ein"]:
        st.session_state["selected_ein"] = chosen_ein
        rerun()
    return st.session_state["selected_ein"]


def build_company_summary(selected_row: pd.Series, selected_shocks: pd.DataFrame, shortlists: pd.DataFrame) -> tuple[str, list[tuple[str, str]]]:
    worst_case = most_sensitive_scenario(selected_shocks)
    shortlist_match = shortlist_row(shortlists, clean_text(selected_row.get("ein"), fallback=""))
    reserve_pct = format_percentile(selected_row.get("peer_reserve_percentile"))
    leverage_pct = format_percentile(selected_row.get("peer_liability_percentile"))
    summary = (
        f"{clean_text(selected_row.get('business_name'))} is a {clean_text(selected_row.get('sector_group'))} organization in "
        f"{clean_text(selected_row.get('state'))}, grouped with {humanize_peer_group(selected_row.get('peer_group'))} peers. "
        f"Baseline distress probability is {format_probability(selected_row.get('predicted_distress_probability'))}; reserve position is {reserve_pct} "
        f"and leverage sits at {leverage_pct} versus peers."
    )
    if shortlist_match is not None:
        summary += f" It is currently flagged as {clean_text(shortlist_match.get('shortlist_category')).lower()}."
    if worst_case is not None:
        summary += f" The most sensitive deterministic scenario is {scenario_label(worst_case.get('scenario_name'))}."

    details = [
        ("EIN", format_ein(selected_row.get("ein"))),
        ("Latest filing", clean_text(selected_row.get("feature_year"))),
        ("Peer group", humanize_peer_group(selected_row.get("peer_group"))),
        ("Sector / state", f"{clean_text(selected_row.get('sector_group'))} | {clean_text(selected_row.get('state'))}"),
        ("Funding model", humanize_funding_bucket(selected_row.get("funding_bucket"))),
        ("Most sensitive scenario", scenario_label(worst_case.get("scenario_name")) if worst_case is not None else "See Shock Simulator"),
    ]
    return summary, details


def render_company_brief(selected_row: pd.Series, selected_shocks: pd.DataFrame, shortlists: pd.DataFrame) -> None:
    summary, details = build_company_summary(selected_row, selected_shocks, shortlists)
    left, right = st.columns([0.9, 0.1])
    with left:
        st.markdown(
            brief_summary_card_html(
                clean_text(selected_row.get("business_name")),
                summary,
            ),
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(risk_pill_html(clean_text(selected_row.get("risk_bucket"))), unsafe_allow_html=True)

    detail_columns = st.columns(len(details))
    for column, (label, value) in zip(detail_columns, details):
        with column:
            st.markdown(brief_meta_card_html(label, value), unsafe_allow_html=True)


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


def render_insight_cards(items: list[tuple[str, str]]) -> None:
    st.markdown('<div class="section-header">Insights</div>', unsafe_allow_html=True)
    columns = st.columns(len(items))
    for column, (title, body) in zip(columns, items):
        with column:
            st.markdown(insight_card_html(title, body), unsafe_allow_html=True)


def render_dataframe(frame: pd.DataFrame, max_height: int = 440) -> None:
    display = frame.copy()
    if display.empty:
        st.markdown(note_card_html("No rows to display."), unsafe_allow_html=True)
        return
    display = display.where(pd.notna(display), "—")
    html = display.to_html(index=False, classes="theme-table", border=0, escape=False)
    height = dataframe_height(display, max_height=max_height)
    st.markdown(
        f'<div class="theme-table-wrap" style="max-height:{height}px;">{html}</div>',
        unsafe_allow_html=True,
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
    table["Top scenario"] = coalesce_series(table, ["scenario_name_view", "top_scenario"], default="-").apply(scenario_label)
    table["Shock delta"] = coalesce_series(table, ["scenario_absolute_delta", "worst_case_delta"]).apply(format_points)
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
            "Top scenario",
            "Shock delta",
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
        f"Top scenario: {scenario_label(row.get('scenario_name_view') if pd.notna(row.get('scenario_name_view')) else row.get('top_scenario'))}<br>"
        f"Shock delta: {format_points(row.get('scenario_absolute_delta') if pd.notna(row.get('scenario_absolute_delta')) else row.get('worst_case_delta'))}"
    )


def tab_risk_lookup(selected_row: pd.Series, threshold_scan: pd.DataFrame) -> None:
    drivers = derive_driver_list(selected_row, top_n=5)
    threshold_flags = derive_threshold_flags(selected_row, threshold_scan)
    interpretation = build_interpretation(selected_row, drivers, threshold_flags)

    render_metric_cards(
        [
            ("Baseline risk", format_probability(selected_row.get("predicted_distress_probability")), "Retained upgraded logistic output"),
            ("Risk bucket", clean_text(selected_row.get("risk_bucket")), clean_text(selected_row.get("overall_risk_rank_bucket"))),
            ("Reserve percentile", format_percentile(selected_row.get("peer_reserve_percentile")), "Lower means weaker reserve position"),
            ("Leverage percentile", format_percentile(selected_row.get("peer_liability_percentile")), "Higher means more leverage pressure"),
        ]
    )

    left, right = st.columns([1.15, 0.85])
    with left:
        st.markdown('<div class="section-header">Driver graph</div>', unsafe_allow_html=True)
        st.plotly_chart(make_driver_chart(drivers), width="stretch")
    with right:
        st.markdown('<div class="section-header">Key financial markers</div>', unsafe_allow_html=True)
        render_dataframe(key_financial_markers(selected_row))

    st.markdown('<div class="section-header">Triggered threshold flags</div>', unsafe_allow_html=True)
    if threshold_flags:
        st.markdown("".join(flag_chip_html(flag["label"]) for flag in threshold_flags[:5]), unsafe_allow_html=True)
    else:
        st.markdown(note_card_html("No retained threshold flags are triggered for this organization in the available data."), unsafe_allow_html=True)

    driver_text = ", ".join(driver["label"] for driver in drivers[:3]) if drivers else "driver detail is limited in the stored artifacts"
    threshold_text = ", ".join(flag["label"].lower() for flag in threshold_flags[:3]) if threshold_flags else "no retained threshold cutoffs are currently triggered"
    render_insight_cards(
        [
            ("Bottom line", interpretation),
            ("Top drivers", f"The strongest visible risk drivers are {driver_text}."),
            ("Threshold read", f"The retained threshold scan indicates {threshold_text}."),
        ]
    )


def tab_peer_benchmarking(orgs: pd.DataFrame, selected_row: pd.Series) -> None:
    weakness_text, strength_text = benchmark_callouts(selected_row)
    render_metric_cards(
        [
            ("Reserve percentile", format_percentile(selected_row.get("peer_reserve_percentile")), "Higher is stronger"),
            ("Margin percentile", format_percentile(selected_row.get("peer_margin_percentile")), "Higher is stronger"),
            ("Leverage percentile", format_percentile(selected_row.get("peer_liability_percentile")), "Higher is riskier"),
            ("Concentration percentile", format_percentile(selected_row.get("concentration_percentile")), "Higher is riskier"),
            ("Overall peer risk", clean_text(selected_row.get("overall_risk_rank_bucket")), format_probability(selected_row.get("predicted_distress_probability"))),
        ]
    )

    left, right = st.columns([1.08, 0.92])
    with left:
        st.markdown('<div class="section-header">Peer-relative chart</div>', unsafe_allow_html=True)
        st.plotly_chart(make_benchmark_chart(selected_row), width="stretch")
    with right:
        st.markdown('<div class="section-header">Peer comparison table</div>', unsafe_allow_html=True)
        render_dataframe(build_benchmark_table(selected_row))

    render_insight_cards(
        [
            ("Strongest weakness", weakness_text + " This should shape the first intervention conversation."),
            ("Relative strength", strength_text + " It helps frame what not to disrupt during intervention."),
            ("Peer context", peer_context_text(orgs, selected_row)),
        ]
    )


def tab_shock_simulator(
    selected_row: pd.Series,
    shock_results: pd.DataFrame,
    shock_summary: pd.DataFrame,
    shock_source_mode: str,
    shock_source_note: str,
) -> None:
    st.markdown(
        note_card_html("Deterministic scenario engine for demo purposes. This is a stress test, not a causal forecast."),
        unsafe_allow_html=True,
    )
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

    st.markdown('<div class="section-header">Scenario selector</div>', unsafe_allow_html=True)
    selected_scenario = st.selectbox(
        "Scenario",
        options=scenario_names,
        format_func=scenario_label,
        key="selected_scenario",
        label_visibility="collapsed",
    )

    if shock_source_mode != "exact_upgraded_org_level":
        st.markdown(note_card_html(shock_source_note), unsafe_allow_html=True)

    if selected_shocks.empty:
        scenario_row = shock_summary.loc[shock_summary["scenario_name"] == selected_scenario].iloc[0]
        render_metric_cards(
            [
                ("Avg baseline risk", format_probability(scenario_row.get("avg_baseline_risk")), "Summary-level fallback"),
                ("Avg shocked risk", format_probability(scenario_row.get("avg_shocked_risk")), "Summary-level fallback"),
                ("Avg absolute change", format_points(scenario_row.get("avg_absolute_increase")), format_points(scenario_row.get("median_absolute_increase")) + " median"),
                ("Bucket upshift share", format_relative(scenario_row.get("bucket_upshift_share")), "Share of orgs moving up a bucket"),
            ]
        )
        st.warning("Only summary-level scenario output is available for this organization.")
        render_dataframe(shock_summary.copy())
        return

    scenario_row = selected_shocks.loc[selected_shocks["scenario_name"] == selected_scenario].iloc[0]
    render_metric_cards(
        [
            ("Baseline risk", format_probability(scenario_row.get("baseline_risk")), clean_text(scenario_row.get("baseline_bucket"))),
            ("Shocked risk", format_probability(scenario_row.get("shocked_risk")), clean_text(scenario_row.get("shocked_bucket"))),
            ("Absolute change", format_points(scenario_row.get("absolute_increase")), format_relative(scenario_row.get("relative_increase"))),
            ("Bucket transition", clean_text(scenario_row.get("risk_bucket_transition")), scenario_label(selected_scenario)),
        ]
    )

    left, right = st.columns([1.08, 0.92])
    with left:
        st.markdown('<div class="section-header">Scenario sensitivity graph</div>', unsafe_allow_html=True)
        st.plotly_chart(make_scenario_delta_chart(selected_shocks, selected_scenario), width="stretch")
    with right:
        st.markdown('<div class="section-header">Scenario results table</div>', unsafe_allow_html=True)
        render_dataframe(scenario_summary_table(selected_shocks))

    top_scenario = most_sensitive_scenario(selected_shocks)
    top_scenario_text = (
        f"{scenario_label(top_scenario.get('scenario_name'))} produces the largest increase for this organization: "
        f"{format_points(top_scenario.get('absolute_increase'))} to {format_probability(top_scenario.get('shocked_risk'))}."
        if top_scenario is not None
        else "No top scenario was available."
    )
    render_insight_cards(
        [
            ("What changed", shock_explanation(selected_row, scenario_row, shock_source_mode)),
            ("Most sensitive scenario", top_scenario_text),
            ("How to read this", "Use the simulator for triage and prioritization, not as a causal forecast of what will definitely happen."),
        ]
    )


def render_shortlist_section(title: str, shortlists: pd.DataFrame) -> None:
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)
    section_table = shortlist_table_for_section(shortlists, title)
    if section_table.empty:
        st.markdown(note_card_html("No shortlist rows were available for this section."), unsafe_allow_html=True)
        return

    display = section_table.drop(columns=["ein"]).copy().rename(
        columns={"business_name": "Organization", "peer_group": "Peer group"}
    )
    render_dataframe(display)

    chooser = {f"{row['business_name']} | {row['Baseline risk']}": row["ein"] for _, row in section_table.iterrows()}
    selected_option = st.selectbox(
        f"Focus an organization from {title}",
        options=list(chooser.keys()),
        key=f"chooser_{title}",
    )
    if st.button(f"Set focus to selected {title.lower()} organization", key=f"button_{title}"):
        st.session_state["selected_ein"] = chooser[selected_option]
        rerun()


def tab_high_impact_discovery(shortlists: pd.DataFrame) -> None:
    if shortlists.empty:
        st.warning("No shortlist artifact was found.")
        return

    render_metric_cards(
        [
            ("Fragile but investable", str((shortlists["shortlist_category"] == "Fragile but investable").sum()), "Intervention-ready cases"),
            ("Resilient outperformers", str((shortlists["shortlist_category"] == "Resilient outperformer").sum()), "Peer-learning examples"),
            ("Shock-sensitive watchlist", str((shortlists["shortlist_category"] == "Shock-sensitive priority watchlist").sum()), "Stress-monitor candidates"),
        ]
    )

    left, right = st.columns([1.08, 0.92])
    with left:
        st.markdown('<div class="section-header">Shortlist landscape</div>', unsafe_allow_html=True)
        st.plotly_chart(make_discovery_chart(shortlists), width="stretch")
    with right:
        st.markdown('<div class="section-header">Category summary</div>', unsafe_allow_html=True)
        render_dataframe(shortlist_overview_table(shortlists))

    fragile = shortlists.loc[shortlists["shortlist_category"] == "Fragile but investable"].sort_values("predicted_distress_probability", ascending=False).iloc[0]
    resilient = shortlists.loc[shortlists["shortlist_category"] == "Resilient outperformer"].sort_values("predicted_distress_probability", ascending=True).iloc[0]
    watch = shortlists.loc[shortlists["shortlist_category"] == "Shock-sensitive priority watchlist"].sort_values("worst_case_delta", ascending=False).iloc[0]
    render_insight_cards(
        [
            ("Fragile but investable", f"{clean_text(fragile.get('business_name'))} is a strong intervention-ready example with {format_probability(fragile.get('predicted_distress_probability'))} baseline risk."),
            ("Resilient outperformers", f"{clean_text(resilient.get('business_name'))} shows what strong reserve, margin, and leverage positioning looks like among peers."),
            ("Shock-sensitive watchlist", f"{clean_text(watch.get('business_name'))} shows the sharpest shock jump at {format_points(watch.get('worst_case_delta'))}."),
        ]
    )

    st.markdown(
        note_card_html("These lists are framed around financial resilience and intervention-readiness, not mission or social impact ranking."),
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

    st.markdown(
        note_card_html(
            "Portfolio Rankings is the macro control room: use it to scan the full portfolio, compare ranking lenses, and push one organization back into the shared main-dashboard selection."
        ),
        unsafe_allow_html=True,
    )

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

    controls_row_1 = st.columns([1.35, 1.1, 1.0, 0.7, 0.8])
    with controls_row_1[0]:
        ranking_mode = st.selectbox("Ranking mode", options=RANKING_MODES, key="portfolio_ranking_mode")
    with controls_row_1[1]:
        scenario_control = st.selectbox(
            "Scenario type",
            options=scenario_options,
            index=scenario_options.index(current_scenario_control),
            format_func=scenario_label,
            key="portfolio_scenario_control",
        )
    with controls_row_1[2]:
        scenario_metric = st.selectbox(
            "Scenario ranking metric",
            options=scenario_metric_options,
            key="portfolio_scenario_metric",
        )
    with controls_row_1[3]:
        top_n = st.selectbox("Top N", options=[10, 25, 50, 100], index=1, key="portfolio_top_n")
    with controls_row_1[4]:
        sort_direction = st.selectbox("Sort direction", options=["Descending", "Ascending"], key="portfolio_sort_direction")

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

    summary_cards = [("Filtered nonprofits", f"{summary['count']:,}", "Current filtered set")]
    if value_is_available(summary["avg_baseline_risk"]):
        summary_cards.append(("Average baseline risk", format_probability(summary["avg_baseline_risk"]), "Across the current slice"))
    if value_is_available(summary["high_risk_share"]):
        summary_cards.append(("High-risk share", format_relative(summary["high_risk_share"]), "High or Very High"))
    if summary.get("most_common_peer_group"):
        summary_cards.append(
            (
                "Most common peer group",
                humanize_peer_group(summary["most_common_peer_group"]),
                "Dominant peer cluster",
            )
        )
    if summary.get("most_dangerous_scenario"):
        summary_cards.append(
            (
                "Most dangerous scenario",
                scenario_label(summary["most_dangerous_scenario"]),
                "Average delta leader",
            )
        )
    if "shortlist_category" in filtered.columns:
        summary_cards.append(("Shortlisted in slice", f"{summary['shortlist_count']:,}", "Rows with a shortlist tag"))
    render_metric_cards(summary_cards)

    ranked, note = rank_frame(
        scenario_view,
        mode=ranking_mode,
        scenario_metric=scenario_metric,
        sort_direction=sort_direction,
        top_n=int(top_n),
    )
    if note:
        st.markdown(note_card_html(note), unsafe_allow_html=True)

    table_left, table_right = st.columns([1.45, 0.55])
    with table_left:
        st.markdown('<div class="section-header">Portfolio ranking table</div>', unsafe_allow_html=True)
        render_dataframe(ranking_table_from_frame(ranked, ranking_mode), max_height=720)
    with table_right:
        top_row = ranked.iloc[0] if not ranked.empty else None
        interpretation = "No organizations matched the current filters."
        if top_row is not None:
            interpretation = (
                f"Current leader: {clean_text(top_row.get('business_name'))}. "
                f"This row ranks first for '{ranking_mode.lower()}' with baseline risk "
                f"{format_probability(top_row.get('predicted_distress_probability'))}."
            )
        st.markdown(insight_card_html("Quick interpretation", interpretation), unsafe_allow_html=True)

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
                "Selected row detail",
                options=list(selected_option_map.keys()),
                index=list(selected_option_map.keys()).index(selected_key),
                key="portfolio_selected_row",
            )
            selected_rank_ein = selected_option_map[selected_rank_label]
            st.session_state["portfolio_selected_ein"] = selected_rank_ein
            selected_rank_row = ranked.loc[ranked["ein"] == selected_rank_ein].iloc[0]
            st.markdown(
                section_card_html("Selected-row summary", ranking_detail_card(selected_rank_row)),
                unsafe_allow_html=True,
            )
            if st.button("Use selected org in main dashboard", key="portfolio_sync_button"):
                st.session_state["selected_ein"] = selected_rank_ein
                rerun()

    render_insight_cards(
        [
            (
                "Ranking lens",
                f"The current lens is '{ranking_mode}'. Use it to compare portfolio-wide patterns before drilling into a single organization.",
            ),
            (
                "Scenario experiment",
                f"Scenario control is set to {scenario_label(scenario_control)} and ranks by {scenario_metric.lower()}.",
            ),
            (
                "Workflow",
                "Use the table to identify a candidate, review the selected-row summary, and push that organization into the main tabs with the sync button.",
            ),
        ]
    )


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
    st.markdown(hero_html(), unsafe_allow_html=True)
    selected_ein = render_selector(orgs)
    selected_row = current_org_row(orgs, selected_ein)
    selected_shocks = org_shocks(bundle["shock_results"], selected_ein)
    render_company_brief(selected_row, selected_shocks, bundle["shortlists"])

    tab1, tab2, tab3, tab4, tab5 = st.tabs(TAB_TITLES)
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


if __name__ == "__main__":
    main()
