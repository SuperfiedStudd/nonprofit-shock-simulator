from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd


RANKING_MODES = [
    "Highest baseline risk",
    "Lowest baseline risk / most resilient",
    "Worst peer-relative reserve weakness",
    "Worst leverage pressure",
    "Highest shock sensitivity",
    "Largest bucket jump under scenario stress",
    "Fragile but investable",
    "Resilient outperformers",
    "Shock-sensitive watchlist",
    "Strongest reserve position",
    "Strongest peer-relative strength",
    "Highest concentration risk",
    "Biggest donation-shock sensitivity",
    "Biggest expense-inflation sensitivity",
]

SCENARIO_CONTROL_ALL = "Worst case across scenarios"
SCENARIO_METRICS = {
    "Absolute risk delta": "scenario_absolute_delta",
    "Relative risk delta": "scenario_relative_delta",
    "Bucket jump": "scenario_bucket_jump",
    "Scenario vulnerability (shocked risk)": "scenario_shocked_risk",
}
SHORTLIST_MODE_TO_CATEGORY = {
    "Fragile but investable": "Fragile but investable",
    "Resilient outperformers": "Resilient outperformer",
    "Shock-sensitive watchlist": "Shock-sensitive priority watchlist",
}


@dataclass(frozen=True)
class RankingInstruction:
    column: str
    ascending: bool
    secondary: list[str]
    note: str = ""


def _series_or_default(frame: pd.DataFrame, column: str, default: Any = np.nan) -> pd.Series:
    if column in frame.columns:
        return frame[column]
    return pd.Series(default, index=frame.index)


def _coalesce_series(frame: pd.DataFrame, columns: list[str], default: Any = np.nan) -> pd.Series:
    out = pd.Series(default, index=frame.index)
    for column in columns:
        if column in frame.columns:
            out = out.where(out.notna(), frame[column])
    return out


def _has_columns(frame: pd.DataFrame, columns: list[str]) -> bool:
    return all(column in frame.columns for column in columns)


def _safe_mode(series: pd.Series) -> str | None:
    if series.empty:
        return None
    counts = series.dropna().astype(str).value_counts()
    return None if counts.empty else str(counts.index[0])


def _shock_summary_by_ein(shock_results: pd.DataFrame) -> pd.DataFrame:
    if shock_results.empty or not _has_columns(shock_results, ["ein", "absolute_increase"]):
        return pd.DataFrame(columns=["ein"])

    sort_columns = [column for column in ["absolute_increase", "shocked_risk"] if column in shock_results.columns]
    worst_source = shock_results.sort_values(sort_columns, ascending=[False] * len(sort_columns)) if sort_columns else shock_results.copy()
    worst = worst_source.groupby("ein", as_index=False).first().rename(
        columns={
            "scenario_name": "top_scenario",
            "shocked_risk": "worst_case_risk",
            "absolute_increase": "worst_case_delta",
            "relative_increase": "worst_case_relative_increase",
            "bucket_shift": "worst_case_bucket_shift",
            "main_drivers": "worst_case_main_drivers",
            "risk_bucket_transition": "worst_case_bucket_transition",
        }
    )
    worst_columns = [
        "ein",
        "top_scenario",
        "worst_case_risk",
        "worst_case_delta",
        "worst_case_relative_increase",
        "worst_case_bucket_shift",
        "worst_case_main_drivers",
        "worst_case_bucket_transition",
    ]
    for column in worst_columns:
        if column not in worst.columns:
            worst[column] = np.nan
    worst = worst[worst_columns]

    def family_aggregate(family: str, prefix: str) -> pd.DataFrame:
        if not _has_columns(shock_results, ["ein", "scenario_family", "absolute_increase"]):
            return pd.DataFrame(columns=["ein"])
        subset = shock_results.loc[shock_results["scenario_family"].eq(family)].copy()
        if subset.empty:
            return pd.DataFrame(columns=["ein"])
        agg_map: dict[str, tuple[str, str]] = {f"{prefix}_worst_delta": ("absolute_increase", "max")}
        if "bucket_shift" in subset.columns:
            agg_map[f"{prefix}_worst_bucket_jump"] = ("bucket_shift", "max")
        return subset.groupby("ein").agg(**agg_map).reset_index()

    donation = family_aggregate("donation_revenue", "donation")
    expense = family_aggregate("expense_inflation", "expense")
    out = worst.copy()
    if not donation.empty:
        out = out.merge(donation, on="ein", how="left")
    if not expense.empty:
        out = out.merge(expense, on="ein", how="left")
    return out


def build_portfolio_frame(orgs: pd.DataFrame, shortlists: pd.DataFrame, shock_results: pd.DataFrame) -> pd.DataFrame:
    base = orgs.copy()
    if "ein" not in base.columns:
        return base

    if not shortlists.empty and "ein" in shortlists.columns:
        shortlist_keep = [
            "ein",
            "shortlist_category",
            "plain_english_recommendation",
            "shortlist_score",
            "worst_case_scenario",
            "worst_case_risk",
            "worst_case_delta",
            "worst_case_relative_increase",
            "worst_case_bucket_transition",
            "worst_case_drivers",
            "bucket_shift",
        ]
        shortlist_present = [column for column in shortlist_keep if column in shortlists.columns]
        if shortlist_present:
            base = base.merge(shortlists[shortlist_present].drop_duplicates(subset=["ein"]), on="ein", how="left")

    shock_summary = _shock_summary_by_ein(shock_results)
    if not shock_summary.empty:
        base = base.merge(shock_summary, on="ein", how="left", suffixes=("", "_shock"))

    for destination, sources in [
        ("worst_case_delta", ["worst_case_delta", "worst_case_delta_shock"]),
        ("worst_case_relative_increase", ["worst_case_relative_increase", "worst_case_relative_increase_shock"]),
        ("worst_case_risk", ["worst_case_risk", "worst_case_risk_shock"]),
        ("top_scenario", ["top_scenario", "top_scenario_shock", "worst_case_scenario"]),
        ("worst_case_bucket_shift", ["worst_case_bucket_shift", "worst_case_bucket_shift_shock", "bucket_shift"]),
        ("worst_case_main_drivers", ["worst_case_main_drivers", "worst_case_main_drivers_shock", "worst_case_drivers"]),
        (
            "worst_case_bucket_transition",
            ["worst_case_bucket_transition", "worst_case_bucket_transition_shock"],
        ),
    ]:
        merged = _coalesce_series(base, sources)
        if merged.notna().any():
            base[destination] = merged

    observed_inputs = [
        column
        for column in ["feature_year", "latest_year_raw", "predicted_distress_probability", "peer_reserve_percentile"]
        if column in base.columns
    ]
    if observed_inputs:
        observed_flag = pd.Series(False, index=base.index)
        for column in observed_inputs:
            observed_flag = observed_flag | base[column].notna()
        base["observed_data_flag"] = observed_flag
    else:
        base["observed_data_flag"] = True

    base["peer_strength_score"] = (
        _series_or_default(base, "peer_reserve_percentile", 0).fillna(0)
        + _series_or_default(base, "peer_margin_percentile", 0).fillna(0)
        + (1 - _series_or_default(base, "peer_liability_percentile", 0).fillna(0))
        + (1 - _series_or_default(base, "concentration_percentile", 0).fillna(0))
    ) / 4.0
    base["peer_weakness_score"] = 1 - base["peer_strength_score"]
    return base


def scenario_control_options(shock_results: pd.DataFrame) -> list[str]:
    if shock_results.empty or "scenario_name" not in shock_results.columns:
        return [SCENARIO_CONTROL_ALL]
    options = sorted(shock_results["scenario_name"].dropna().astype(str).unique().tolist())
    return [SCENARIO_CONTROL_ALL] + options


def apply_filters(
    frame: pd.DataFrame,
    *,
    peer_groups: list[str],
    size_bands: list[str],
    funding_models: list[str],
    states: list[str],
    sectors: list[str],
    risk_buckets: list[str],
    shortlist_categories: list[str],
    observed_only: bool = False,
) -> pd.DataFrame:
    filtered = frame.copy()
    filter_map = {
        "peer_group": peer_groups,
        "size_bucket": size_bands,
        "funding_bucket": funding_models,
        "state": states,
        "sector_group": sectors,
        "risk_bucket": risk_buckets,
        "shortlist_category": shortlist_categories,
    }
    for column, values in filter_map.items():
        if values and column in filtered.columns:
            filtered = filtered.loc[filtered[column].isin(values)].copy()
    if observed_only and "observed_data_flag" in filtered.columns:
        filtered = filtered.loc[_series_or_default(filtered, "observed_data_flag", False).fillna(False)].copy()
    return filtered


def with_scenario_view(frame: pd.DataFrame, shock_results: pd.DataFrame, scenario_name: str) -> pd.DataFrame:
    out = frame.copy()
    if shock_results.empty or not _has_columns(shock_results, ["ein", "scenario_name"]):
        out["scenario_name_view"] = SCENARIO_CONTROL_ALL
        out["scenario_absolute_delta"] = _coalesce_series(out, ["worst_case_delta"])
        out["scenario_relative_delta"] = _coalesce_series(out, ["worst_case_relative_increase"])
        out["scenario_bucket_jump"] = _coalesce_series(out, ["worst_case_bucket_shift", "bucket_shift"])
        out["scenario_shocked_risk"] = _coalesce_series(out, ["worst_case_risk"])
        out["scenario_drivers"] = _coalesce_series(out, ["worst_case_main_drivers", "worst_case_drivers"])
        return out

    if scenario_name == SCENARIO_CONTROL_ALL:
        out["scenario_name_view"] = _coalesce_series(out, ["top_scenario", "worst_case_scenario"], default=SCENARIO_CONTROL_ALL)
        out["scenario_absolute_delta"] = _coalesce_series(out, ["worst_case_delta"])
        out["scenario_relative_delta"] = _coalesce_series(out, ["worst_case_relative_increase"])
        out["scenario_bucket_jump"] = _coalesce_series(out, ["worst_case_bucket_shift", "bucket_shift"])
        out["scenario_shocked_risk"] = _coalesce_series(out, ["worst_case_risk"])
        out["scenario_drivers"] = _coalesce_series(out, ["worst_case_main_drivers", "worst_case_drivers"])
        return out

    selected = shock_results.loc[shock_results["scenario_name"] == scenario_name].copy()
    if selected.empty:
        out["scenario_name_view"] = scenario_name
        out["scenario_absolute_delta"] = np.nan
        out["scenario_relative_delta"] = np.nan
        out["scenario_bucket_jump"] = np.nan
        out["scenario_shocked_risk"] = np.nan
        out["scenario_drivers"] = np.nan
        return out

    scenario_columns = [
        column
        for column in [
            "ein",
            "scenario_name",
            "absolute_increase",
            "relative_increase",
            "bucket_shift",
            "shocked_risk",
            "main_drivers",
        ]
        if column in selected.columns
    ]
    scenario_keep = selected[scenario_columns].rename(
        columns={
            "scenario_name": "scenario_name_view",
            "absolute_increase": "scenario_absolute_delta",
            "relative_increase": "scenario_relative_delta",
            "bucket_shift": "scenario_bucket_jump",
            "shocked_risk": "scenario_shocked_risk",
            "main_drivers": "scenario_drivers",
        }
    )
    for column in [
        "scenario_name_view",
        "scenario_absolute_delta",
        "scenario_relative_delta",
        "scenario_bucket_jump",
        "scenario_shocked_risk",
        "scenario_drivers",
    ]:
        if column not in scenario_keep.columns:
            scenario_keep[column] = np.nan
    return out.merge(scenario_keep, on="ein", how="left")


def _instruction_for_mode(mode: str, scenario_metric: str) -> RankingInstruction:
    scenario_col = SCENARIO_METRICS.get(scenario_metric, "scenario_absolute_delta")
    instructions = {
        "Highest baseline risk": RankingInstruction("predicted_distress_probability", False, ["overall_risk_percentile"]),
        "Lowest baseline risk / most resilient": RankingInstruction("predicted_distress_probability", True, ["peer_strength_score"]),
        "Worst peer-relative reserve weakness": RankingInstruction("peer_reserve_percentile", True, ["reserve_gap_vs_peer_median"]),
        "Worst leverage pressure": RankingInstruction("peer_liability_percentile", False, ["leverage_gap_vs_peer_median"]),
        "Highest shock sensitivity": RankingInstruction(scenario_col, False, ["scenario_shocked_risk"]),
        "Largest bucket jump under scenario stress": RankingInstruction("scenario_bucket_jump", False, ["scenario_absolute_delta"]),
        "Fragile but investable": RankingInstruction("shortlist_score", False, ["predicted_distress_probability"]),
        "Resilient outperformers": RankingInstruction("shortlist_score", False, ["peer_strength_score"]),
        "Shock-sensitive watchlist": RankingInstruction("shortlist_score", False, ["worst_case_delta"]),
        "Strongest reserve position": RankingInstruction("peer_reserve_percentile", False, ["reserve_gap_vs_peer_median"]),
        "Strongest peer-relative strength": RankingInstruction("peer_strength_score", False, ["predicted_distress_probability"]),
        "Highest concentration risk": RankingInstruction("concentration_percentile", False, ["revenue_hhi_clean"]),
        "Biggest donation-shock sensitivity": RankingInstruction("donation_worst_delta", False, ["donation_worst_bucket_jump"]),
        "Biggest expense-inflation sensitivity": RankingInstruction("expense_worst_delta", False, ["expense_worst_bucket_jump"]),
    }
    return instructions[mode]


def apply_mode_subset(frame: pd.DataFrame, mode: str) -> pd.DataFrame:
    if mode in SHORTLIST_MODE_TO_CATEGORY:
        category = SHORTLIST_MODE_TO_CATEGORY[mode]
        if "shortlist_category" not in frame.columns:
            return frame.iloc[0:0].copy()
        return frame.loc[frame["shortlist_category"].eq(category)].copy()
    return frame


def rank_frame(
    frame: pd.DataFrame,
    *,
    mode: str,
    scenario_metric: str,
    sort_direction: str,
    top_n: int,
) -> tuple[pd.DataFrame, str]:
    working = apply_mode_subset(frame, mode)
    instruction = _instruction_for_mode(mode, scenario_metric)
    if instruction.column not in working.columns:
        return pd.DataFrame(), f"The ranking mode '{mode}' is not available from the current artifact set."

    working = working.loc[working[instruction.column].notna()].copy()
    if working.empty:
        return pd.DataFrame(), f"No organizations matched the current filters for '{mode}'."

    ascending = instruction.ascending
    if sort_direction == "Ascending":
        ascending = True
    elif sort_direction == "Descending":
        ascending = False

    sort_columns = [instruction.column] + [column for column in instruction.secondary if column in working.columns]
    sort_orders = [ascending] + [ascending] * (len(sort_columns) - 1)
    ranked = working.sort_values(sort_columns, ascending=sort_orders).head(top_n).copy()
    return ranked, instruction.note


def most_dangerous_scenario(frame: pd.DataFrame, shock_results: pd.DataFrame) -> str | None:
    if frame.empty or shock_results.empty or not _has_columns(shock_results, ["ein", "scenario_name", "absolute_increase"]):
        return None
    subset = shock_results.loc[shock_results["ein"].isin(frame["ein"])]
    if subset.empty:
        return None
    grouped = subset.groupby("scenario_name")["absolute_increase"].mean().sort_values(ascending=False)
    return None if grouped.empty else str(grouped.index[0])


def build_summary_metrics(frame: pd.DataFrame, shock_results: pd.DataFrame) -> dict[str, Any]:
    count = int(len(frame))
    avg_baseline = (
        float(frame["predicted_distress_probability"].mean())
        if count and "predicted_distress_probability" in frame.columns
        else np.nan
    )
    high_risk_share = (
        float(frame["risk_bucket"].isin(["High", "Very High"]).mean())
        if count and "risk_bucket" in frame.columns
        else np.nan
    )
    shortlist_count = int(frame["shortlist_category"].notna().sum()) if count and "shortlist_category" in frame.columns else 0
    return {
        "count": count,
        "avg_baseline_risk": avg_baseline,
        "high_risk_share": high_risk_share,
        "most_common_peer_group": _safe_mode(_series_or_default(frame, "peer_group", default=np.nan)),
        "most_dangerous_scenario": most_dangerous_scenario(frame, shock_results),
        "shortlist_count": shortlist_count,
    }


def build_rationale(row: pd.Series, mode: str) -> str:
    if pd.notna(row.get("plain_english_recommendation")):
        return str(row.get("plain_english_recommendation"))
    if mode in {"Fragile but investable", "Resilient outperformers"} and pd.notna(row.get("benchmark_position_summary")):
        return str(row.get("benchmark_position_summary"))
    if mode in {"Highest shock sensitivity", "Largest bucket jump under scenario stress", "Shock-sensitive watchlist"} and pd.notna(
        row.get("shock_sensitivity_summary")
    ):
        return str(row.get("shock_sensitivity_summary"))
    if mode in {"Highest shock sensitivity", "Largest bucket jump under scenario stress", "Biggest donation-shock sensitivity", "Biggest expense-inflation sensitivity"}:
        drivers = row.get("scenario_drivers") or row.get("worst_case_main_drivers") or row.get("worst_case_drivers")
        if pd.notna(drivers):
            return str(drivers)
    if mode == "Strongest peer-relative strength" and pd.notna(row.get("strength_flags")):
        return str(row.get("strength_flags"))
    if pd.notna(row.get("key_gaps")):
        return str(row.get("key_gaps"))
    return "No rationale available from the current artifact set."
