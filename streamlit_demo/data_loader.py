from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]


def normalize_ein_value(value: Any) -> str:
    if pd.isna(value):
        return ""
    digits = "".join(ch for ch in str(value).strip() if ch.isdigit())
    if not digits:
        return ""
    return digits.zfill(9)


def normalize_ein_series(series: pd.Series) -> pd.Series:
    return series.apply(normalize_ein_value)


def _existing_path(candidates: list[Path]) -> Path | None:
    for path in candidates:
        if path.exists():
            return path
    return None


def _load_csv(path: Path | None) -> pd.DataFrame:
    if path is None:
        return pd.DataFrame()
    return pd.read_csv(path, low_memory=False)


def _load_json(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _build_source_map() -> dict[str, Path | None]:
    return {
        "run_summary": _existing_path(
            [
                ROOT / "new results" / "run_summary.json",
                ROOT / "distress_outputs" / "run_summary.json",
            ]
        ),
        "peer_cards": _existing_path(
            [
                ROOT / "new results" / "peer_benchmark_cards.csv",
                ROOT / "distress_outputs" / "fairlight_package" / "peer_benchmark_cards.csv",
                ROOT / "distress_outputs" / "fairlight_package" / "tables" / "peer_benchmark_cards.csv",
            ]
        ),
        "raw_latest": _existing_path(
            [
                ROOT / "distress_outputs" / "intermediate" / "latest_2023_scores_full.csv",
            ]
        ),
        "shortlists": _existing_path(
            [
                ROOT / "new results" / "fairlight_shortlists_table.csv",
                ROOT / "distress_outputs" / "fairlight_package" / "tables" / "fairlight_shortlists_table.csv",
            ]
        ),
        "shock_results": _existing_path(
            [
                ROOT / "streamlit_demo_data" / "upgraded_shock_simulation_results.csv",
                ROOT / "new results" / "upgraded_shock_simulation_results.csv",
                ROOT / "distress_outputs" / "fairlight_package" / "shock_simulation_results.csv",
            ]
        ),
        "shock_summary": _existing_path(
            [
                ROOT / "new results" / "shock_scenario_summary.csv",
                ROOT / "streamlit_demo_data" / "upgraded_shock_scenario_summary.csv",
                ROOT / "distress_outputs" / "fairlight_package" / "tables" / "shock_scenario_summary.csv",
            ]
        ),
        "threshold_scan": _existing_path(
            [
                ROOT / "new results" / "threshold_scan.csv",
                ROOT / "distress_outputs" / "fairlight_package" / "tables" / "threshold_evidence_table.csv",
                ROOT / "distress_outputs" / "threshold_table.csv",
            ]
        ),
        "insights": _existing_path(
            [
                ROOT / "new results" / "insight_evidence_table.csv",
            ]
        ),
    }


def _coerce_numeric(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    out = df.copy()
    for column in columns:
        if column in out.columns:
            out[column] = pd.to_numeric(out[column], errors="coerce")
    return out


def _merge_org_universe(peer_cards: pd.DataFrame, raw_latest: pd.DataFrame) -> pd.DataFrame:
    orgs = peer_cards.copy()
    if "ein" not in orgs.columns:
        return orgs

    orgs["ein"] = normalize_ein_series(orgs["ein"])
    orgs = _coerce_numeric(
        orgs,
        [
            "feature_year",
            "predicted_distress_probability",
            "peer_reserve_percentile",
            "peer_margin_percentile",
            "peer_liability_percentile",
            "concentration_percentile",
            "overall_risk_percentile",
            "reserve_gap_vs_peer_median",
            "margin_gap_vs_peer_median",
            "leverage_gap_vs_peer_median",
            "concentration_gap_vs_peer_median",
        ],
    )

    if raw_latest.empty or "ein" not in raw_latest.columns:
        orgs["org_label"] = orgs["business_name"].fillna("Unknown Organization") + " | EIN " + orgs["ein"]
        return orgs

    raw_keep = [
        "ein",
        "tax_year",
        "total_revenue",
        "total_expenses",
        "contributions_grants",
        "program_service_revenue",
        "investment_income",
        "other_revenue",
        "net_assets_eoy",
        "total_assets_eoy",
        "total_liabilities_eoy",
        "operating_margin_clean",
        "reserve_months_proxy",
        "liability_ratio_clean",
        "net_asset_ratio_clean",
        "revenue_growth_clean",
        "expense_growth_gap",
        "asset_growth_clean",
        "donation_share_clean",
        "program_share_clean",
        "fundraising_share_clean",
        "grants_share_clean",
        "revenue_hhi_clean",
    ]
    raw = raw_latest.copy()
    raw["ein"] = normalize_ein_series(raw["ein"])
    raw = raw[[column for column in raw_keep if column in raw.columns]].copy()
    if "tax_year" in raw.columns:
        raw = raw.rename(columns={"tax_year": "latest_year_raw"})
    raw = _coerce_numeric(
        raw,
        [column for column in raw.columns if column not in {"ein"}],
    )
    orgs = orgs.merge(raw, on="ein", how="left")

    if "feature_year" not in orgs.columns and "latest_year_raw" in orgs.columns:
        orgs["feature_year"] = orgs["latest_year_raw"]

    orgs["org_label"] = orgs["business_name"].fillna("Unknown Organization") + " | EIN " + orgs["ein"]
    return orgs


def _assess_shock_source(
    shock_results: pd.DataFrame,
    orgs: pd.DataFrame,
    path: Path | None,
) -> tuple[str, str]:
    if shock_results.empty or path is None or "baseline_risk" not in shock_results.columns:
        return (
            "summary_only",
            "Only scenario summary rows were found, so the simulator falls back to summary-level messaging.",
        )

    if "ein" not in shock_results.columns or "predicted_distress_probability" not in orgs.columns:
        return (
            "org_level_unknown",
            f"Org-level shock rows loaded from {path.name}, but the app could not validate them against baseline probabilities.",
        )

    compare = orgs[["ein", "predicted_distress_probability"]].merge(
        shock_results[["ein", "baseline_risk"]].drop_duplicates(subset=["ein"]),
        on="ein",
        how="inner",
    )
    if compare.empty:
        return (
            "org_level_unknown",
            f"Org-level shock rows loaded from {path.name}, but no EIN overlap was available for validation.",
        )

    mean_abs_gap = (compare["predicted_distress_probability"] - compare["baseline_risk"]).abs().mean()
    if "upgraded" in path.name.lower() or mean_abs_gap <= 0.005:
        return (
            "exact_upgraded_org_level",
            "Org-level scenario rows are aligned to the upgraded logistic rerun.",
        )

    return (
        "fallback_packaged_org_level",
        (
            "Org-level scenario rows came from the older packaged simulator because the upgraded rerun only saved summary "
            f"tables. Baseline gap versus upgraded lookup averages {mean_abs_gap:.3f}, so the tab is labeled as a fallback."
        ),
    )


def load_demo_bundle() -> dict[str, Any]:
    sources = _build_source_map()

    run_summary = _load_json(sources["run_summary"])
    peer_cards = _load_csv(sources["peer_cards"])
    raw_latest = _load_csv(sources["raw_latest"])
    shortlists = _load_csv(sources["shortlists"])
    shock_results = _load_csv(sources["shock_results"])
    shock_summary = _load_csv(sources["shock_summary"])
    threshold_scan = _load_csv(sources["threshold_scan"])
    insights = _load_csv(sources["insights"])

    orgs = _merge_org_universe(peer_cards, raw_latest)

    for frame in [shortlists, shock_results]:
        if not frame.empty and "ein" in frame.columns:
            frame["ein"] = normalize_ein_series(frame["ein"])

    if not shortlists.empty:
        shortlists = _coerce_numeric(
            shortlists,
            [
                "predicted_distress_probability",
                "worst_case_risk",
                "worst_case_delta",
                "worst_case_relative_increase",
                "shortlist_score",
            ],
        )

    if not shock_results.empty:
        shock_results = _coerce_numeric(
            shock_results,
            [
                "feature_year",
                "shock_size",
                "baseline_risk",
                "shocked_risk",
                "absolute_increase",
                "relative_increase",
                "bucket_shift",
                "shock_exposure_revenue_loss",
                "shock_exposure_expense_increase",
                "shocked_total_revenue",
                "shocked_total_expenses",
                "shocked_net_assets_eoy",
                "shocked_total_assets_eoy",
                "operating_margin_clean",
                "reserve_months_proxy",
                "liability_ratio_clean",
                "net_asset_ratio_clean",
                "revenue_growth_clean",
                "expense_growth_gap",
                "donation_share_clean",
                "revenue_hhi_clean",
            ],
        )

    if not threshold_scan.empty:
        threshold_scan = _coerce_numeric(
            threshold_scan,
            ["distress_rate_a", "distress_rate_b", "distress_rate_below", "distress_rate_above", "lift_or_odds_ratio", "support_count"],
        )

    shock_source_mode, shock_source_note = _assess_shock_source(shock_results, orgs, sources["shock_results"])

    default_ein = ""
    if not shortlists.empty and "ein" in shortlists.columns:
        default_ein = shortlists.iloc[0]["ein"]
    elif not orgs.empty and "ein" in orgs.columns:
        default_ein = orgs.sort_values("business_name").iloc[0]["ein"]

    return {
        "orgs": orgs.sort_values(["business_name", "ein"]).reset_index(drop=True),
        "peer_cards": peer_cards,
        "shortlists": shortlists,
        "shock_results": shock_results,
        "shock_summary": shock_summary,
        "threshold_scan": threshold_scan,
        "insights": insights,
        "run_summary": run_summary,
        "sources": {key: str(path) if path else None for key, path in sources.items()},
        "shock_source_mode": shock_source_mode,
        "shock_source_note": shock_source_note,
        "default_ein": default_ein,
    }
