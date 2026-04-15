from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from .data_loader import normalize_ein_series


ROOT = Path(__file__).resolve().parents[1]
COHORT_PATH = ROOT / "irs990_cohort_features.csv"
SCORE_PATHS = [
    ROOT / "new results" / "peer_benchmark_cards.csv",
    ROOT / "distress_outputs" / "fairlight_package" / "peer_benchmark_cards.csv",
    ROOT / "distress_outputs" / "fairlight_package" / "tables" / "peer_benchmark_cards.csv",
    ROOT / "streamlit_demo_data" / "upgraded_shock_simulation_results.csv",
]

MAP_YEARS = list(range(2017, 2024))
CHOROPLETH_SCALE = ["#EFF6FF", "#004E7C", "#00263A"]
DOT_COLOR_MAP = {
    "Low": "#2D6A4F",
    "Watch": "#007B7F",
    "High": "#C41E3A",
    "Very High": "#8C1C13",
    "Unscored": "#7B8794",
}
FADING_DOT_COLOR = "#B0BEC5"
STATE_BORDER_COLOR = "#E2E6EA"
VALID_STATE_CODES = {
    "AL",
    "AK",
    "AZ",
    "AR",
    "CA",
    "CO",
    "CT",
    "DE",
    "FL",
    "GA",
    "HI",
    "ID",
    "IL",
    "IN",
    "IA",
    "KS",
    "KY",
    "LA",
    "ME",
    "MD",
    "MA",
    "MI",
    "MN",
    "MS",
    "MO",
    "MT",
    "NE",
    "NV",
    "NH",
    "NJ",
    "NM",
    "NY",
    "NC",
    "ND",
    "OH",
    "OK",
    "OR",
    "PA",
    "RI",
    "SC",
    "SD",
    "TN",
    "TX",
    "UT",
    "VT",
    "VA",
    "WA",
    "WV",
    "WI",
    "WY",
    "DC",
}
STATE_NAME_MAP = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
    "DC": "District of Columbia",
}
STATE_CENTROIDS = {
    "AL": (32.806671, -86.791130),
    "AK": (61.370716, -152.404419),
    "AZ": (33.729759, -111.431221),
    "AR": (34.969704, -92.373123),
    "CA": (36.116203, -119.681564),
    "CO": (39.059811, -105.311104),
    "CT": (41.597782, -72.755371),
    "DE": (39.318523, -75.507141),
    "DC": (38.897438, -77.026817),
    "FL": (27.766279, -81.686783),
    "GA": (33.040619, -83.643074),
    "HI": (21.094318, -157.498337),
    "ID": (44.240459, -114.478828),
    "IL": (40.349457, -88.986137),
    "IN": (39.849426, -86.258278),
    "IA": (42.011539, -93.210526),
    "KS": (38.526600, -96.726486),
    "KY": (37.668140, -84.670067),
    "LA": (31.169546, -91.867805),
    "ME": (44.693947, -69.381927),
    "MD": (39.063946, -76.802101),
    "MA": (42.230171, -71.530106),
    "MI": (43.326618, -84.536095),
    "MN": (45.694454, -93.900192),
    "MS": (32.741646, -89.678696),
    "MO": (38.456085, -92.288368),
    "MT": (46.921925, -110.454353),
    "NE": (41.125370, -98.268082),
    "NV": (38.313515, -117.055374),
    "NH": (43.452492, -71.563896),
    "NJ": (40.298904, -74.521011),
    "NM": (34.840515, -106.248482),
    "NY": (42.165726, -74.948051),
    "NC": (35.630066, -79.806419),
    "ND": (47.528912, -99.784012),
    "OH": (40.388783, -82.764915),
    "OK": (35.565342, -96.928917),
    "OR": (44.572021, -122.070938),
    "PA": (40.590752, -77.209755),
    "RI": (41.680893, -71.511780),
    "SC": (33.856892, -80.945007),
    "SD": (44.299782, -99.438828),
    "TN": (35.747845, -86.692345),
    "TX": (31.054487, -97.563461),
    "UT": (40.150032, -111.862434),
    "VT": (44.045876, -72.710686),
    "VA": (37.769337, -78.169968),
    "WA": (47.400902, -121.490494),
    "WV": (38.491226, -80.954453),
    "WI": (44.268543, -89.616508),
    "WY": (42.755966, -107.302490),
}
STATE_JITTER_SCALE = {
    "AK": 1.2,
    "CA": 1.1,
    "CO": 0.75,
    "CT": 0.30,
    "DC": 0.15,
    "DE": 0.20,
    "FL": 0.8,
    "HI": 0.25,
    "MA": 0.25,
    "MD": 0.25,
    "ME": 0.6,
    "MT": 1.1,
    "NH": 0.25,
    "NJ": 0.22,
    "NV": 0.8,
    "NY": 0.55,
    "RI": 0.18,
    "TX": 1.2,
    "UT": 0.6,
    "VA": 0.55,
    "VT": 0.22,
    "WA": 0.7,
    "WY": 0.8,
}


@dataclass(frozen=True)
class GeoMetricSpec:
    key: str
    column: str
    label: str
    colorbar_title: str
    formatter: str
    help_text: str


GEO_METRICS = {
    "Median total revenue": GeoMetricSpec(
        key="Median total revenue",
        column="median_revenue",
        label="Median total revenue",
        colorbar_title="Median revenue",
        formatter="currency",
        help_text="Median total revenue among active filers in the selected year.",
    ),
    "Active org count": GeoMetricSpec(
        key="Active org count",
        column="org_count",
        label="Active org count",
        colorbar_title="Active orgs",
        formatter="integer",
        help_text="Count of observed filers in the selected year.",
    ),
    "Median distress probability": GeoMetricSpec(
        key="Median distress probability",
        column="median_distress_probability",
        label="Median distress probability",
        colorbar_title="Median distress",
        formatter="percent",
        help_text="Median current scored-universe distress probability among active mapped organizations.",
    ),
    "Median operating margin": GeoMetricSpec(
        key="Median operating margin",
        column="median_operating_margin",
        label="Median operating margin",
        colorbar_title="Median margin",
        formatter="percent_signed",
        help_text="Median operating margin among active filers in the selected year.",
    ),
    "High-risk share": GeoMetricSpec(
        key="High-risk share",
        column="high_risk_share",
        label="High-risk share",
        colorbar_title="High-risk share",
        formatter="percent",
        help_text="Share of scored active organizations in High or Very High risk buckets.",
    ),
}


def _existing_path(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.exists():
            return path
    return None


def _format_value(value: Any, formatter: str) -> str:
    if value is None or pd.isna(value):
        return "NA"
    number = float(value)
    if formatter == "currency":
        return f"${number:,.0f}"
    if formatter == "integer":
        return f"{int(round(number)):,}"
    if formatter == "percent":
        return f"{number * 100:.1f}%"
    if formatter == "percent_signed":
        sign = "+" if number >= 0 else ""
        return f"{sign}{number * 100:.1f}%"
    return f"{number:,.2f}"


def _format_compact(value: Any, formatter: str) -> str:
    if value is None or pd.isna(value):
        return "NA"
    number = float(value)
    if formatter == "currency":
        absolute = abs(number)
        if absolute >= 1_000_000_000:
            return f"${number / 1_000_000_000:.1f}B"
        if absolute >= 1_000_000:
            return f"${number / 1_000_000:.1f}M"
        if absolute >= 1_000:
            return f"${number / 1_000:.0f}K"
        return f"${number:,.0f}"
    if formatter == "integer":
        return f"{int(round(number)):,}"
    if formatter == "percent":
        return f"{number * 100:.1f}%"
    if formatter == "percent_signed":
        sign = "+" if number >= 0 else ""
        return f"{sign}{number * 100:.1f}%"
    return f"{number:,.2f}"


def _load_score_lookup() -> tuple[pd.DataFrame, str | None]:
    required_columns = {"ein", "predicted_distress_probability", "risk_bucket"}
    fallback_columns = {"ein", "baseline_risk", "baseline_bucket"}
    for score_path in SCORE_PATHS:
        if not score_path.exists():
            continue

        header = pd.read_csv(score_path, nrows=0).columns.tolist()
        header_set = set(header)
        if required_columns.issubset(header_set):
            scores = pd.read_csv(
                score_path,
                usecols=["ein", "predicted_distress_probability", "risk_bucket"],
                dtype={
                    "ein": "string",
                    "predicted_distress_probability": "float64",
                    "risk_bucket": "string",
                },
                low_memory=False,
            )
        elif fallback_columns.issubset(header_set):
            scores = pd.read_csv(
                score_path,
                usecols=["ein", "baseline_risk", "baseline_bucket"],
                dtype={
                    "ein": "string",
                    "baseline_risk": "float64",
                    "baseline_bucket": "string",
                },
                low_memory=False,
            ).rename(
                columns={
                    "baseline_risk": "predicted_distress_probability",
                    "baseline_bucket": "risk_bucket",
                }
            )
        else:
            continue

        scores["ein"] = normalize_ein_series(scores["ein"])
        scores["risk_bucket"] = scores["risk_bucket"].fillna("Unscored")
        scores = scores.drop_duplicates(subset=["ein"]).reset_index(drop=True)
        return scores, str(score_path)

    return pd.DataFrame(columns=["ein", "predicted_distress_probability", "risk_bucket"]), None


@st.cache_resource(show_spinner=False)
def load_geographic_bundle() -> dict[str, Any]:
    usecols = [
        "ein",
        "business_name",
        "tax_year",
        "state",
        "total_revenue",
        "operating_margin",
        "liability_ratio",
        "observed_flag",
        "years_since_last_observed",
        "imputed",
    ]
    dtypes = {
        "ein": "string",
        "business_name": "string",
        "tax_year": "Int16",
        "state": "string",
        "total_revenue": "float64",
        "operating_margin": "float64",
        "liability_ratio": "float64",
        "observed_flag": "Int8",
        "years_since_last_observed": "float64",
        "imputed": "Int8",
    }
    panel = pd.read_csv(COHORT_PATH, usecols=usecols, dtype=dtypes)
    panel["ein"] = normalize_ein_series(panel["ein"])
    panel["state"] = panel["state"].fillna("").str.upper().str.strip()
    panel = panel.loc[panel["tax_year"].isin(MAP_YEARS)].copy()
    panel = panel.loc[panel["state"].isin(VALID_STATE_CODES)].copy()

    scores, score_path = _load_score_lookup()
    if not scores.empty:
        panel = panel.merge(scores, on="ein", how="left")
    else:
        panel["predicted_distress_probability"] = np.nan
        panel["risk_bucket"] = "Unscored"

    panel["risk_bucket"] = panel["risk_bucket"].fillna("Unscored")
    panel["state_name"] = panel["state"].map(STATE_NAME_MAP).fillna(panel["state"])

    panel["years_since_last_observed"] = pd.to_numeric(panel["years_since_last_observed"], errors="coerce")
    panel["observed_flag"] = pd.to_numeric(panel["observed_flag"], errors="coerce").fillna(0).astype(int)
    panel["imputed"] = pd.to_numeric(panel["imputed"], errors="coerce").fillna(0).astype(int)

    centroids = pd.DataFrame(
        [{"state": code, "base_lat": coords[0], "base_lon": coords[1]} for code, coords in STATE_CENTROIDS.items()]
    )
    panel = panel.merge(centroids, on="state", how="left")

    seed = pd.to_numeric(panel["ein"].str[-6:], errors="coerce").fillna(0).astype("int64")
    angle = (seed % 360).astype("float64") * np.pi / 180.0
    radius = 0.15 + ((seed // 360) % 9).astype("float64") / 10.0
    scale = panel["state"].map(STATE_JITTER_SCALE).fillna(0.45).astype("float64")
    panel["lat"] = panel["base_lat"] + np.sin(angle) * scale * radius * 0.75
    panel["lon"] = panel["base_lon"] + np.cos(angle) * scale * radius

    positive_revenue = panel["total_revenue"].where(panel["total_revenue"] > 0, 1.0).fillna(1.0)
    panel["dot_size"] = np.clip(np.log10(positive_revenue) * 1.85, 3.0, 17.0)
    panel["ghost_opacity"] = np.select(
        [
            panel["observed_flag"].eq(1),
            panel["years_since_last_observed"].eq(1),
            panel["years_since_last_observed"].eq(2),
        ],
        [0.95, 0.40, 0.15],
        default=0.0,
    )
    panel["dot_status"] = np.select(
        [
            panel["observed_flag"].eq(1),
            panel["years_since_last_observed"].eq(1),
            panel["years_since_last_observed"].eq(2),
        ],
        ["Active", "Fading", "Fading"],
        default="Hidden",
    )
    panel["dot_color"] = np.where(
        panel["observed_flag"].eq(1),
        panel["risk_bucket"].map(DOT_COLOR_MAP).fillna(DOT_COLOR_MAP["Unscored"]),
        FADING_DOT_COLOR,
    )
    panel["high_risk_flag"] = np.where(
        panel["predicted_distress_probability"].notna(),
        panel["risk_bucket"].isin(["High", "Very High"]).astype(float),
        np.nan,
    )

    active = panel.loc[panel["observed_flag"].eq(1)].copy()
    state_year_agg = (
        active.groupby(["tax_year", "state", "state_name"], as_index=False)
        .agg(
            org_count=("ein", "nunique"),
            median_revenue=("total_revenue", "median"),
            median_operating_margin=("operating_margin", "median"),
            median_distress_probability=("predicted_distress_probability", "median"),
            high_risk_share=("high_risk_flag", "mean"),
            scored_org_count=("predicted_distress_probability", lambda values: int(values.notna().sum())),
        )
        .sort_values(["tax_year", "org_count", "state"], ascending=[True, False, True])
        .reset_index(drop=True)
    )
    state_year_agg["prev_org_count"] = state_year_agg.sort_values(["state", "tax_year"]).groupby("state")["org_count"].shift(1)
    state_year_agg["org_count_delta"] = state_year_agg["org_count"] - state_year_agg["prev_org_count"].fillna(0)

    scored_unique = int(panel.loc[panel["predicted_distress_probability"].notna(), "ein"].nunique())
    cohort_unique = int(panel["ein"].nunique())
    return {
        "panel": panel.reset_index(drop=True),
        "state_year_agg": state_year_agg,
        "score_path": score_path,
        "score_coverage_overall": (scored_unique / cohort_unique) if cohort_unique else 0.0,
        "scored_unique_eins": scored_unique,
        "cohort_unique_eins": cohort_unique,
    }


@st.cache_data(show_spinner=False)
def build_geographic_snapshot(year: int) -> dict[str, Any]:
    bundle = load_geographic_bundle()
    panel = bundle["panel"]
    state_year_agg = bundle["state_year_agg"]

    year_frame = panel.loc[panel["tax_year"].eq(year)].copy()
    active_rows = year_frame.loc[year_frame["observed_flag"].eq(1)].copy()
    dots = year_frame.loc[year_frame["ghost_opacity"] > 0].copy()
    state_agg = state_year_agg.loc[state_year_agg["tax_year"].eq(year)].copy()
    previous_state_agg = state_year_agg.loc[state_year_agg["tax_year"].eq(year - 1)].copy()

    active_count = int(active_rows["ein"].nunique()) if not active_rows.empty else 0
    fading_count = int(dots.loc[dots["observed_flag"].eq(0), "ein"].nunique()) if not dots.empty else 0
    scored_count = int(active_rows["predicted_distress_probability"].notna().sum()) if not active_rows.empty else 0
    coverage = (scored_count / active_count) if active_count else 0.0

    return {
        "state_agg": state_agg.reset_index(drop=True),
        "previous_state_agg": previous_state_agg.reset_index(drop=True),
        "dots": dots.reset_index(drop=True),
        "active_count": active_count,
        "fading_count": fading_count,
        "state_count": int(state_agg["state"].nunique()) if not state_agg.empty else 0,
        "scored_coverage": coverage,
        "risk_metric_note": (
            f"Risk-based map views reuse the current scored universe from {Path(bundle['score_path']).name} and cover "
            f"{coverage * 100:.1f}% of active mapped organizations in {year}."
            if bundle["score_path"]
            else "Risk-based map views are unavailable because no scored-universe file was found."
        ),
    }


def make_geographic_map(state_agg: pd.DataFrame, dots: pd.DataFrame, metric_key: str, show_dots: bool) -> go.Figure:
    spec = GEO_METRICS[metric_key]
    figure = go.Figure()

    color_values = state_agg[spec.column] if spec.column in state_agg.columns else pd.Series(dtype=float)
    non_null = color_values.dropna()
    if not non_null.empty:
        q_low = float(non_null.quantile(0.05))
        q_high = float(non_null.quantile(0.95))
        zmin = min(float(non_null.min()), q_low)
        zmax = max(float(non_null.max()), q_high)
    else:
        zmin = None
        zmax = None

    hover_metric = state_agg.get(spec.column, pd.Series(index=state_agg.index, dtype=float)).apply(lambda value: _format_value(value, spec.formatter))
    hover_revenue = state_agg.get("median_revenue", pd.Series(index=state_agg.index, dtype=float)).apply(lambda value: _format_value(value, "currency"))
    hover_margin = state_agg.get("median_operating_margin", pd.Series(index=state_agg.index, dtype=float)).apply(
        lambda value: _format_value(value, "percent_signed")
    )
    hover_risk = state_agg.get("high_risk_share", pd.Series(index=state_agg.index, dtype=float)).apply(lambda value: _format_value(value, "percent"))
    customdata = np.column_stack(
        [
            state_agg.get("state_name", pd.Series(index=state_agg.index, dtype=str)).fillna(state_agg.get("state", "")),
            hover_metric,
            state_agg.get("org_count", pd.Series(index=state_agg.index, dtype=float)).fillna(0).astype(int).astype(str),
            hover_revenue,
            hover_margin,
            hover_risk,
        ]
    )

    figure.add_trace(
        go.Choropleth(
            locations=state_agg.get("state", pd.Series(dtype=str)),
            locationmode="USA-states",
            z=state_agg.get(spec.column, pd.Series(dtype=float)),
            colorscale=CHOROPLETH_SCALE,
            zmin=zmin,
            zmax=zmax,
            marker_line_color=STATE_BORDER_COLOR,
            marker_line_width=0.9,
            colorbar=dict(title=spec.colorbar_title),
            customdata=customdata,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                + f"{spec.label}: "
                + "%{customdata[1]}<br>"
                + "Active orgs: %{customdata[2]}<br>"
                + "Median revenue: %{customdata[3]}<br>"
                + "Median margin: %{customdata[4]}<br>"
                + "High-risk share: %{customdata[5]}<extra></extra>"
            ),
        )
    )

    if show_dots and not dots.empty:
        dot_customdata = np.column_stack(
            [
                dots.get("state_name", pd.Series(index=dots.index, dtype=str)).fillna(dots.get("state", "")),
                dots.get("dot_status", pd.Series(index=dots.index, dtype=str)).fillna("Hidden"),
                dots.get("risk_bucket", pd.Series(index=dots.index, dtype=str)).fillna("Unscored"),
                dots.get("total_revenue", pd.Series(index=dots.index, dtype=float)).apply(lambda value: _format_value(value, "currency")),
                dots.get("operating_margin", pd.Series(index=dots.index, dtype=float)).apply(
                    lambda value: _format_value(value, "percent_signed")
                ),
            ]
        )
        figure.add_trace(
            go.Scattergeo(
                lon=dots.get("lon", pd.Series(dtype=float)),
                lat=dots.get("lat", pd.Series(dtype=float)),
                mode="markers",
                text=dots.get("business_name", pd.Series(index=dots.index, dtype=str)).fillna("Unknown organization"),
                customdata=dot_customdata,
                marker=dict(
                    size=dots.get("dot_size", pd.Series(index=dots.index, dtype=float)).fillna(4.0),
                    color=dots.get("dot_color", pd.Series(index=dots.index, dtype=str)).fillna(FADING_DOT_COLOR),
                    opacity=dots.get("ghost_opacity", pd.Series(index=dots.index, dtype=float)).fillna(0.0),
                    line=dict(width=0),
                ),
                hovertemplate=(
                    "<b>%{text}</b><br>"
                    + "State: %{customdata[0]}<br>"
                    + "Status: %{customdata[1]}<br>"
                    + "Risk bucket: %{customdata[2]}<br>"
                    + "Revenue: %{customdata[3]}<br>"
                    + "Operating margin: %{customdata[4]}<extra></extra>"
                ),
                showlegend=False,
            )
        )

    figure.update_layout(
        height=660,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        geo=dict(
            scope="usa",
            projection_type="albers usa",
            showland=True,
            landcolor="#FFFFFF",
            bgcolor="rgba(0,0,0,0)",
            showlakes=True,
            lakecolor="#FFFFFF",
            subunitcolor=STATE_BORDER_COLOR,
        ),
    )
    return figure


def make_top_states_chart(state_agg: pd.DataFrame, metric_key: str) -> go.Figure:
    spec = GEO_METRICS[metric_key]
    if state_agg.empty or spec.column not in state_agg.columns:
        return go.Figure()

    frame = state_agg.loc[state_agg[spec.column].notna(), ["state_name", spec.column]].copy()
    frame = frame.sort_values(spec.column, ascending=False).head(10).sort_values(spec.column, ascending=True)
    frame["text_label"] = frame[spec.column].apply(lambda value: _format_compact(value, spec.formatter))

    figure = go.Figure(
        go.Bar(
            x=frame[spec.column],
            y=frame["state_name"],
            orientation="h",
            marker=dict(color="#12395B", line=dict(color="#12395B", width=1)),
            text=frame["text_label"],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>" + f"{spec.label}: " + "%{text}<extra></extra>",
        )
    )
    figure.update_layout(
        height=420,
        margin=dict(l=18, r=24, t=20, b=36),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#102A43", family="Segoe UI, Helvetica Neue, Arial, sans-serif"),
    )
    figure.update_xaxes(showgrid=True, gridcolor="#E8EDF3", zeroline=False, title=spec.label, tickfont=dict(color="#486581"))
    figure.update_yaxes(showgrid=False, title="", tickfont=dict(color="#334E68"))
    return figure


def make_yoy_delta_chart(state_agg: pd.DataFrame, year: int) -> go.Figure:
    if state_agg.empty or year == MAP_YEARS[0]:
        return go.Figure()

    frame = state_agg[["state_name", "org_count_delta"]].copy()
    frame = frame.sort_values("org_count_delta", key=lambda values: values.abs(), ascending=False).head(10)
    frame = frame.sort_values("org_count_delta", ascending=True)
    frame["color"] = np.where(frame["org_count_delta"] >= 0, "#12395B", "#A64743")
    frame["text_label"] = frame["org_count_delta"].apply(lambda value: f"{int(value):+d}")

    figure = go.Figure(
        go.Bar(
            x=frame["org_count_delta"],
            y=frame["state_name"],
            orientation="h",
            marker=dict(color=frame["color"], line=dict(color=frame["color"], width=1)),
            text=frame["text_label"],
            textposition="outside",
            cliponaxis=False,
            hovertemplate="%{y}<br>Active org change: %{text}<extra></extra>",
        )
    )
    figure.add_vline(x=0, line_dash="dot", line_color="#9FB3C8", line_width=1.1)
    figure.update_layout(
        height=420,
        margin=dict(l=18, r=24, t=20, b=36),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(color="#102A43", family="Segoe UI, Helvetica Neue, Arial, sans-serif"),
    )
    figure.update_xaxes(showgrid=True, gridcolor="#E8EDF3", zeroline=False, title=f"Change vs {year - 1}", tickfont=dict(color="#486581"))
    figure.update_yaxes(showgrid=False, title="", tickfont=dict(color="#334E68"))
    return figure
