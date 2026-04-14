from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "streamlit_demo_data"
SHOCK_OUTPUT_PATH = OUTPUT_DIR / "upgraded_shock_simulation_results.csv"
SHOCK_SUMMARY_OUTPUT_PATH = OUTPUT_DIR / "upgraded_shock_scenario_summary.csv"
METADATA_PATH = OUTPUT_DIR / "streamlit_demo_artifacts.json"


def load_modules():
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)

    import build_distress_pipeline as backbone
    import build_fairlight_package as package
    import build_selective_upgrade_results as upgrade

    backbone.ROOT = ROOT
    backbone.INPUT_PATH = ROOT / "irs990_cohort_features.csv"
    upgrade.ROOT = ROOT
    upgrade.RESULTS_DIR = ROOT / "new results"
    return backbone, package, upgrade


def load_run_summary() -> dict[str, object]:
    path = ROOT / "new results" / "run_summary.json"
    return json.loads(path.read_text(encoding="utf-8"))


def build_model(
    backbone,
    upgrade,
    final_features: list[str],
    label_col: str,
) -> tuple[Pipeline, pd.DataFrame]:
    raw = backbone.load_data()
    featured = upgrade.build_upgrade_features(raw, backbone)
    panel = upgrade.build_panel_with_candidate_labels(featured, backbone)
    core_990 = panel.loc[panel["return_type_clean"] == "990"].copy()
    final_train = core_990.loc[core_990["feature_year"].isin([2017, 2018, 2021, 2022])].copy()
    numeric_pool, categorical_pool = upgrade.numeric_and_categorical_pools(backbone)
    model = upgrade.build_logistic_pipeline(final_features, numeric_pool, categorical_pool)
    model.fit(final_train[final_features], final_train[label_col].astype(int))
    return model, featured


def build_org_level_shocks(
    latest: pd.DataFrame,
    model: Pipeline,
    final_features: list[str],
    package,
    upgrade,
) -> pd.DataFrame:
    baseline = latest.copy().reset_index(drop=True)
    baseline["baseline_risk"] = baseline["predicted_distress_probability"]
    baseline["baseline_bucket"] = baseline["risk_bucket"]
    refs = upgrade.build_peer_reference_maps(baseline)

    results: list[pd.DataFrame] = []
    for scenario in upgrade.SCENARIOS:
        shocked = package.recompute_shocked_features(baseline, scenario)
        shocked["feature_year"] = baseline["feature_year"]
        shocked["return_type_clean"] = baseline["return_type_clean"]
        shocked["peer_group"] = baseline["peer_group"]
        shocked["log_net_asset_coverage"] = np.log1p(shocked["reserve_months_proxy"].clip(lower=0)).clip(upper=np.log1p(120))
        shocked = upgrade.apply_peer_reference_maps(shocked, refs)

        shocked_prob = model.predict_proba(shocked[final_features])[:, 1]
        shocked["shocked_risk"] = shocked_prob
        shocked["shocked_bucket"] = upgrade.risk_bucket_from_prob(shocked["shocked_risk"])
        shocked["absolute_increase"] = shocked["shocked_risk"] - shocked["baseline_risk"]
        shocked["relative_increase"] = shocked["absolute_increase"] / shocked["baseline_risk"].replace(0, np.nan)
        bucket_order = {label: idx for idx, label in enumerate(upgrade.RISK_BUCKETS)}
        shocked["bucket_shift"] = shocked["shocked_bucket"].map(bucket_order).astype(int) - shocked["baseline_bucket"].map(bucket_order).astype(int)
        shocked["risk_bucket_transition"] = np.where(
            shocked["bucket_shift"] == 0,
            "No change",
            shocked["baseline_bucket"] + " -> " + shocked["shocked_bucket"],
        )
        shocked["main_drivers"] = package.build_driver_text(baseline, shocked)
        shocked["scenario_name"] = scenario["scenario_name"]
        shocked["scenario_family"] = scenario["scenario_family"]
        shocked["shock_size"] = scenario["shock_size"]

        results.append(
            shocked[
                [
                    "ein",
                    "business_name",
                    "feature_year",
                    "state",
                    "census_region",
                    "peer_group",
                    "funding_bucket",
                    "size_bucket",
                    "NTEE_CD",
                    "sector_group",
                    "scenario_name",
                    "scenario_family",
                    "shock_size",
                    "baseline_risk",
                    "shocked_risk",
                    "absolute_increase",
                    "relative_increase",
                    "baseline_bucket",
                    "shocked_bucket",
                    "bucket_shift",
                    "risk_bucket_transition",
                    "main_drivers",
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
                ]
            ].copy()
        )

    return pd.concat(results, ignore_index=True)


def main(force: bool = False) -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    if SHOCK_OUTPUT_PATH.exists() and not force:
        print(f"Existing artifact found at {SHOCK_OUTPUT_PATH}. Use --force to rebuild.")
        return

    run_summary = load_run_summary()
    final_features = list(run_summary["selected_features"])
    label_col = str(run_summary["selected_label"])

    backbone, package, upgrade = load_modules()
    model, featured = build_model(backbone, upgrade, final_features, label_col)
    latest = upgrade.score_latest_year(featured, model, final_features)
    latest = upgrade.attach_sector_lookup(latest)

    org_level_shocks = build_org_level_shocks(latest, model, final_features, package, upgrade)
    scenario_summary = upgrade.build_shock_scenario_summary(org_level_shocks)

    org_level_shocks.to_csv(SHOCK_OUTPUT_PATH, index=False)
    scenario_summary.to_csv(SHOCK_SUMMARY_OUTPUT_PATH, index=False)

    metadata = {
        "label": label_col,
        "model": "upgraded_logistic",
        "rows_latest": int(len(latest)),
        "rows_org_level_shocks": int(len(org_level_shocks)),
        "scenarios": sorted(org_level_shocks["scenario_name"].dropna().unique().tolist()),
        "top_scenario": scenario_summary.iloc[0]["scenario_name"] if not scenario_summary.empty else None,
        "shock_output_path": str(SHOCK_OUTPUT_PATH),
    }
    METADATA_PATH.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build supplemental Streamlit demo artifacts.")
    parser.add_argument("--force", action="store_true", help="Rebuild even if the artifact already exists.")
    args = parser.parse_args()
    main(force=args.force)
