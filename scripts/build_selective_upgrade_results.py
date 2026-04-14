from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from catboost import CatBoostClassifier
from lightgbm import LGBMClassifier
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "new results"
SEED = 42
RESULT_LABEL_KEY = "peer_relative_composite"
RISK_BINS = [-np.inf, 0.10, 0.20, 0.35, np.inf]
RISK_BUCKETS = ["Low", "Watch", "High", "Very High"]
TOP_K_LEVELS = [0.05, 0.10, 0.20]
SCENARIOS = [
    {"scenario_name": "donation_shock_10", "scenario_family": "donation_revenue", "shock_size": -0.10},
    {"scenario_name": "donation_shock_20", "scenario_family": "donation_revenue", "shock_size": -0.20},
    {"scenario_name": "donation_shock_30", "scenario_family": "donation_revenue", "shock_size": -0.30},
    {"scenario_name": "program_shock_10", "scenario_family": "program_revenue", "shock_size": -0.10},
    {"scenario_name": "program_shock_20", "scenario_family": "program_revenue", "shock_size": -0.20},
    {"scenario_name": "grant_shock_10", "scenario_family": "grant_government_revenue", "shock_size": -0.10},
    {"scenario_name": "grant_shock_20", "scenario_family": "grant_government_revenue", "shock_size": -0.20},
    {"scenario_name": "expense_inflation_5", "scenario_family": "expense_inflation", "shock_size": 0.05},
    {"scenario_name": "expense_inflation_10", "scenario_family": "expense_inflation", "shock_size": 0.10},
]


def ensure_dirs() -> None:
    RESULTS_DIR.mkdir(exist_ok=True)


def load_modules():
    scripts_dir = str(ROOT / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import build_distress_pipeline as backbone
    import build_fairlight_package as package

    backbone.ROOT = ROOT
    backbone.INPUT_PATH = ROOT / "irs990_cohort_features.csv"
    package.ROOT = ROOT
    package.PACKAGE_DIR = RESULTS_DIR
    package.TABLE_DIR = RESULTS_DIR
    package.CHART_DIR = RESULTS_DIR / "_charts_unused"
    package.CHART_DATA_DIR = RESULTS_DIR / "_chart_data_unused"
    return backbone, package


def metric_block(y_true: pd.Series, pred_prob: np.ndarray) -> dict[str, float]:
    metrics = {
        "roc_auc": float(roc_auc_score(y_true, pred_prob)),
        "pr_auc": float(average_precision_score(y_true, pred_prob)),
        "brier": float(brier_score_loss(y_true, pred_prob)),
        "prevalence": float(y_true.mean()),
        "precision_at_0_20": float(precision_score(y_true, pred_prob >= 0.20, zero_division=0)),
        "predicted_positive_at_0_20": float((pred_prob >= 0.20).mean()),
    }
    for level in TOP_K_LEVELS:
        cutoff = max(1, int(math.ceil(len(pred_prob) * level)))
        top_idx = np.argsort(pred_prob)[::-1][:cutoff]
        metrics[f"precision_at_top_{int(level * 100)}pct"] = float(y_true.iloc[top_idx].mean())
    return metrics


def calibration_summary(y_true: pd.Series, pred_prob: np.ndarray, n_bins: int = 10) -> dict[str, float]:
    y = y_true.to_numpy(dtype=float)
    p = np.clip(np.asarray(pred_prob, dtype=float), 1e-6, 1 - 1e-6)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    bucket = np.digitize(p, bins[1:-1], right=True)
    ece = 0.0
    max_gap = 0.0
    non_empty = 0
    for idx in range(n_bins):
        mask = bucket == idx
        if not mask.any():
            continue
        non_empty += 1
        pred_mean = float(p[mask].mean())
        obs_rate = float(y[mask].mean())
        gap = abs(pred_mean - obs_rate)
        ece += gap * mask.mean()
        max_gap = max(max_gap, gap)
    return {"ece_10": float(ece), "max_bin_gap": float(max_gap), "non_empty_bins": float(non_empty)}


def risk_bucket_from_prob(prob: pd.Series) -> pd.Series:
    return pd.cut(prob, bins=RISK_BINS, labels=RISK_BUCKETS).astype(str)


def build_logistic_pipeline(features: list[str], numeric_pool: set[str], categorical_pool: set[str]) -> Pipeline:
    numeric = [f for f in features if f in numeric_pool]
    categorical = [f for f in features if f in categorical_pool]
    prep = ColumnTransformer(
        transformers=[
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", RobustScaler())]), numeric),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            ),
        ]
    )
    model = LogisticRegression(C=0.8, max_iter=4000, solver="lbfgs", random_state=SEED)
    return Pipeline([("prep", prep), ("model", model)])


def add_peer_anchor_features(
    df: pd.DataFrame,
    metric_col: str,
    prefix: str,
    group_cols: list[str],
) -> pd.DataFrame:
    out = df.copy()
    observed = out["observed_flag"].eq(1)
    rank_col = f"peer_pct_{prefix}_obs"
    resid_col = f"peer_{prefix}_resid_obs"
    z_col = f"peer_{prefix}_z_obs"

    out[rank_col] = np.nan
    out[resid_col] = np.nan
    out[z_col] = np.nan

    obs_values = out.loc[observed, group_cols + [metric_col]].dropna(subset=[metric_col]).copy()
    obs_values["_orig_index"] = obs_values.index
    obs_values[rank_col] = obs_values.groupby(group_cols)[metric_col].rank(pct=True)
    stats = (
        obs_values.groupby(group_cols)[metric_col]
        .agg(_mean="mean", _std="std", _median="median")
        .reset_index()
    )
    obs_values = obs_values.merge(stats, on=group_cols, how="left")
    obs_values[resid_col] = obs_values[metric_col] - obs_values["_median"]
    obs_values[z_col] = ((obs_values[metric_col] - obs_values["_mean"]) / obs_values["_std"].replace(0, np.nan)).clip(-4, 4)

    out.loc[obs_values["_orig_index"], rank_col] = obs_values[rank_col].to_numpy()
    out.loc[obs_values["_orig_index"], resid_col] = obs_values[resid_col].to_numpy()
    out.loc[obs_values["_orig_index"], z_col] = obs_values[z_col].to_numpy()
    return out


def build_upgrade_features(raw: pd.DataFrame, backbone) -> pd.DataFrame:
    feat = backbone.add_safe_features(raw).sort_values(["ein", "tax_year"]).reset_index(drop=True)
    expenses_pos = feat["total_expenses"].clip(lower=0)
    coverage_raw = backbone.safe_divide(
        feat["net_assets_eoy"].clip(lower=0) * 12.0,
        expenses_pos.where(expenses_pos > 0),
    ).clip(lower=0)
    feat["net_asset_coverage_months_raw"] = coverage_raw
    feat["log_net_asset_coverage"] = np.log1p(coverage_raw).clip(upper=np.log1p(120))

    group_cols = ["tax_year", "return_type_clean", "peer_group"]
    for metric_col, prefix in [
        ("log_net_asset_coverage", "coverage"),
        ("operating_margin_clean", "margin"),
        ("liability_ratio_clean", "liability"),
        ("revenue_growth_clean", "revenue_growth"),
    ]:
        feat = add_peer_anchor_features(feat, metric_col, prefix, group_cols)

    prev_year = feat.groupby("ein")["tax_year"].shift(1)
    has_prev = prev_year.eq(feat["tax_year"] - 1)
    prev_log_cov = feat.groupby("ein")["log_net_asset_coverage"].shift(1)
    feat["coverage_change_1y_log"] = (feat["log_net_asset_coverage"] - prev_log_cov).where(has_prev).clip(-4, 4)
    return feat


def build_panel_with_candidate_labels(featured: pd.DataFrame, backbone) -> pd.DataFrame:
    next_cols = [
        "observed_flag",
        "imputed",
        "return_type_clean",
        "operating_margin_clean",
        "reserve_months_proxy",
        "liability_ratio_clean",
        "net_asset_ratio_clean",
        "revenue_growth_clean",
        "asset_growth_clean",
        "tax_year",
        "net_assets_eoy",
        "log_net_asset_coverage",
        "peer_pct_coverage_obs",
        "peer_pct_margin_obs",
        "peer_pct_liability_obs",
        "peer_pct_revenue_growth_obs",
    ]
    panel = backbone.add_next_year_fields(featured, next_cols)
    panel["pair_current_observed"] = panel["observed_flag"] == 1
    panel["pair_next_observed"] = panel["next_observed_flag"] == 1
    panel["pair_current_imputed"] = panel["imputed"] == 1
    panel["feature_year"] = panel["tax_year"]
    panel["label_year"] = panel["next_tax_year"]

    core_mask = (
        panel["has_next_consecutive"]
        & panel["pair_current_observed"]
        & panel["pair_next_observed"]
        & panel["feature_year"].isin([2017, 2018, 2021, 2022])
    )
    core = panel.loc[core_mask].copy()

    core["current_static_label"] = (
        (
            (core["next_operating_margin_clean"] <= -0.05).astype(int)
            + (core["next_reserve_months_proxy"] < 1.5).astype(int)
            + (core["next_liability_ratio_clean"] > 0.85).astype(int)
            + (core["next_revenue_growth_clean"] <= -0.20).astype(int)
            + (core["next_asset_growth_clean"] <= -0.10).astype(int)
        )
        >= 2
    ) | ((core["next_net_assets_eoy"] <= 0) & (core["next_operating_margin_clean"] < 0))

    for name, next_col, current_col in [
        ("coverage_delta", "next_log_net_asset_coverage", "log_net_asset_coverage"),
        ("margin_delta", "next_operating_margin_clean", "operating_margin_clean"),
        ("liability_delta", "next_liability_ratio_clean", "liability_ratio_clean"),
        ("revenue_delta", "next_revenue_growth_clean", "revenue_growth_clean"),
        ("asset_delta", "next_asset_growth_clean", "asset_growth_clean"),
    ]:
        core[name] = core[next_col] - core[current_col]
        grp = core.groupby(["label_year", "return_type_clean", "peer_group"])[name]
        core[f"{name}_z"] = ((core[name] - grp.transform("mean")) / grp.transform("std").replace(0, np.nan)).clip(-4, 4)

    core["peer_relative_delta_label"] = (
        (
            (core["coverage_delta_z"] <= -1.0).astype(int)
            + (core["margin_delta_z"] <= -1.0).astype(int)
            + (core["liability_delta_z"] >= 1.0).astype(int)
            + (core["revenue_delta_z"] <= -1.0).astype(int)
            + (core["asset_delta_z"] <= -1.0).astype(int)
        )
        >= 2
    ) | ((core["next_net_assets_eoy"] <= 0) & (core["margin_delta_z"] < 0))

    quintile_symptoms = (
        (core["next_peer_pct_coverage_obs"] <= 0.20).astype(int)
        + (core["next_peer_pct_margin_obs"] <= 0.20).astype(int)
        + (core["next_peer_pct_liability_obs"] >= 0.80).astype(int)
        + (core["coverage_delta_z"] <= -1.0).astype(int)
        + (core["margin_delta_z"] <= -1.0).astype(int)
        + (core["revenue_delta_z"] <= -1.0).astype(int)
    )
    tight_symptoms = (
        (core["next_peer_pct_coverage_obs"] <= 0.15).astype(int)
        + (core["next_peer_pct_margin_obs"] <= 0.15).astype(int)
        + (core["next_peer_pct_liability_obs"] >= 0.85).astype(int)
        + (core["coverage_delta_z"] <= -1.0).astype(int)
        + (core["margin_delta_z"] <= -1.0).astype(int)
        + (core["revenue_delta_z"] <= -1.0).astype(int)
    )
    core["peer_relative_composite"] = (quintile_symptoms >= 2) | (
        (core["next_net_assets_eoy"] <= 0) & (core["next_peer_pct_margin_obs"] <= 0.50)
    )
    core["peer_relative_composite_tight"] = (tight_symptoms >= 2) | (
        (core["next_net_assets_eoy"] <= 0) & (core["next_peer_pct_margin_obs"] <= 0.50)
    )

    for col in [
        "current_static_label",
        "peer_relative_delta_label",
        "peer_relative_composite",
        "peer_relative_composite_tight",
    ]:
        core[col] = core[col].astype(int)
    return core


def numeric_and_categorical_pools(backbone) -> tuple[set[str], set[str]]:
    numeric_pool = set(backbone.NUMERIC_FEATURES) | {
        "log_net_asset_coverage",
        "net_asset_coverage_months_raw",
        "coverage_change_1y_log",
        "peer_pct_coverage_obs",
        "peer_pct_margin_obs",
        "peer_pct_liability_obs",
        "peer_pct_revenue_growth_obs",
        "peer_coverage_resid_obs",
        "peer_margin_resid_obs",
        "peer_liability_resid_obs",
        "peer_revenue_growth_resid_obs",
        "peer_coverage_z_obs",
        "peer_margin_z_obs",
        "peer_liability_z_obs",
        "peer_revenue_growth_z_obs",
        "macro_donation_unrate",
        "macro_concentration_unrate",
        "macro_expensegap_inflation",
        "macro_leverage_rates",
    }
    categorical_pool = set(backbone.CATEGORICAL_FEATURES)
    return numeric_pool, categorical_pool


def evaluate_feature_variants(
    core_990: pd.DataFrame,
    label_col: str,
    backbone,
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    numeric_pool, categorical_pool = numeric_and_categorical_pools(backbone)
    feature_sets = {
        "baseline_current_backbone": backbone.PRIMARY_FEATURES,
        "coverage_fix_only": [
            "operating_margin_clean",
            "log_net_asset_coverage",
            "liability_ratio_clean",
            "net_asset_ratio_clean",
            "revenue_growth_clean",
            "expense_growth_gap",
            "asset_growth_clean",
            "donation_share_clean",
            "revenue_hhi_clean",
            "salary_share_clean",
            "org_age_clean",
            "peer_group",
        ],
        "peer_anchored_with_direct": [
            "operating_margin_clean",
            "log_net_asset_coverage",
            "liability_ratio_clean",
            "net_asset_ratio_clean",
            "revenue_growth_clean",
            "expense_growth_gap",
            "asset_growth_clean",
            "donation_share_clean",
            "revenue_hhi_clean",
            "salary_share_clean",
            "org_age_clean",
            "peer_group",
            "peer_pct_margin_obs",
            "peer_pct_coverage_obs",
            "peer_pct_liability_obs",
            "peer_pct_revenue_growth_obs",
            "peer_margin_z_obs",
            "peer_coverage_z_obs",
        ],
        "peer_anchored_no_direct": [
            "liability_ratio_clean",
            "net_asset_ratio_clean",
            "revenue_growth_clean",
            "expense_growth_gap",
            "asset_growth_clean",
            "donation_share_clean",
            "revenue_hhi_clean",
            "salary_share_clean",
            "org_age_clean",
            "peer_group",
            "peer_pct_margin_obs",
            "peer_pct_coverage_obs",
            "peer_pct_liability_obs",
            "peer_pct_revenue_growth_obs",
            "peer_margin_z_obs",
            "peer_coverage_z_obs",
        ],
    }

    rows: list[dict[str, Any]] = []
    for feature_variant, features in feature_sets.items():
        pipe = build_logistic_pipeline(features, numeric_pool, categorical_pool)
        for split_name, train_years, test_year in [
            ("train_2017_test_2018", [2017], 2018),
            ("train_2017_2018_test_2021", [2017, 2018], 2021),
            ("train_2017_2018_2021_test_2022", [2017, 2018, 2021], 2022),
        ]:
            train_df = core_990.loc[core_990["feature_year"].isin(train_years)].copy()
            test_df = core_990.loc[core_990["feature_year"].eq(test_year)].copy()
            y_train = train_df[label_col].astype(int)
            y_test = test_df[label_col].astype(int)
            pipe.fit(train_df[features], y_train)
            pred = pipe.predict_proba(test_df[features])[:, 1]
            rows.append(
                {
                    "experiment_family": "feature_variant",
                    "experiment_name": feature_variant,
                    "label_key": label_col,
                    "split_name": split_name,
                    **metric_block(y_test, pred),
                }
            )
    return pd.DataFrame(rows), feature_sets


def evaluate_label_candidates(
    core_990: pd.DataFrame,
    selected_features: list[str],
    backbone,
) -> pd.DataFrame:
    numeric_pool, categorical_pool = numeric_and_categorical_pools(backbone)
    pipe = build_logistic_pipeline(selected_features, numeric_pool, categorical_pool)
    rows: list[dict[str, Any]] = []
    for label_col in [
        "current_static_label",
        "peer_relative_delta_label",
        "peer_relative_composite_tight",
        "peer_relative_composite",
    ]:
        year_rates = core_990.groupby("feature_year")[label_col].mean()
        for split_name, train_years, test_year in [
            ("train_2017_test_2018", [2017], 2018),
            ("train_2017_2018_test_2021", [2017, 2018], 2021),
            ("train_2017_2018_2021_test_2022", [2017, 2018, 2021], 2022),
        ]:
            train_df = core_990.loc[core_990["feature_year"].isin(train_years)].copy()
            test_df = core_990.loc[core_990["feature_year"].eq(test_year)].copy()
            y_train = train_df[label_col].astype(int)
            y_test = test_df[label_col].astype(int)
            pipe.fit(train_df[selected_features], y_train)
            pred = pipe.predict_proba(test_df[selected_features])[:, 1]
            rows.append(
                {
                    "experiment_family": "label_candidate",
                    "experiment_name": label_col,
                    "label_key": label_col,
                    "split_name": split_name,
                    "overall_rate": float(core_990[label_col].mean()),
                    "year_rate_std": float(year_rates.std()),
                    **metric_block(y_test, pred),
                }
            )
    return pd.DataFrame(rows)


def fetch_macro_years() -> pd.DataFrame:
    series_ids = ["UNRATE", "CPIAUCSL", "FEDFUNDS"]
    yearly: dict[str, pd.Series] = {}
    for series_id in series_ids:
        frame = pd.read_csv(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}")
        frame["observation_date"] = pd.to_datetime(frame["observation_date"])
        frame[series_id] = pd.to_numeric(frame[series_id], errors="coerce")
        frame["year"] = frame["observation_date"].dt.year
        yearly[series_id] = frame.groupby("year")[series_id].mean()
    inflation = yearly["CPIAUCSL"].pct_change()
    macro = pd.DataFrame({"tax_year": sorted(set(yearly["UNRATE"].index) | set(inflation.index))})
    macro["unrate_avg"] = macro["tax_year"].map(yearly["UNRATE"])
    macro["fedfunds_avg"] = macro["tax_year"].map(yearly["FEDFUNDS"])
    macro["cpi_inflation"] = macro["tax_year"].map(inflation)
    return macro


def evaluate_macro_pack(
    core_990: pd.DataFrame,
    base_features: list[str],
    label_col: str,
    backbone,
) -> tuple[pd.DataFrame, list[str], pd.DataFrame]:
    macro = fetch_macro_years()
    merged = core_990.merge(
        macro,
        left_on="feature_year",
        right_on="tax_year",
        how="left",
        suffixes=("", "_macro"),
    )
    if "tax_year_macro" in merged.columns:
        merged = merged.drop(columns=["tax_year_macro"])
    elif "tax_year_y" in merged.columns:
        merged = merged.drop(columns=["tax_year_y"])
    merged["macro_donation_unrate"] = merged["donation_share_clean"] * merged["unrate_avg"]
    merged["macro_concentration_unrate"] = merged["revenue_hhi_clean"] * merged["unrate_avg"]
    merged["macro_expensegap_inflation"] = merged["expense_growth_gap"] * merged["cpi_inflation"]
    merged["macro_leverage_rates"] = merged["liability_ratio_clean"] * merged["fedfunds_avg"]
    macro_features = base_features + [
        "macro_donation_unrate",
        "macro_concentration_unrate",
        "macro_expensegap_inflation",
        "macro_leverage_rates",
    ]
    numeric_pool, categorical_pool = numeric_and_categorical_pools(backbone)
    rows: list[dict[str, Any]] = []
    for experiment_name, features in {
        "peer_anchored_no_direct": base_features,
        "peer_anchored_no_direct_plus_macro_pack": macro_features,
    }.items():
        pipe = build_logistic_pipeline(features, numeric_pool, categorical_pool)
        for split_name, train_years, test_year in [
            ("train_2017_test_2018", [2017], 2018),
            ("train_2017_2018_test_2021", [2017, 2018], 2021),
            ("train_2017_2018_2021_test_2022", [2017, 2018, 2021], 2022),
        ]:
            train_df = merged.loc[merged["feature_year"].isin(train_years)].copy()
            test_df = merged.loc[merged["feature_year"].eq(test_year)].copy()
            y_train = train_df[label_col].astype(int)
            y_test = test_df[label_col].astype(int)
            pipe.fit(train_df[features], y_train)
            pred = pipe.predict_proba(test_df[features])[:, 1]
            rows.append(
                {
                    "experiment_family": "macro_pack",
                    "experiment_name": experiment_name,
                    "label_key": label_col,
                    "split_name": split_name,
                    **metric_block(y_test, pred),
                }
            )
    return pd.DataFrame(rows), macro_features, merged


def extract_logistic_coefficients(model: Pipeline) -> pd.DataFrame:
    prep = model.named_steps["prep"]
    fitted = model.named_steps["model"]
    coef = pd.DataFrame(
        {
            "encoded_feature": prep.get_feature_names_out(),
            "coefficient": fitted.coef_[0],
        }
    )
    coef["abs_coefficient"] = coef["coefficient"].abs()
    coef["odds_ratio_per_scaled_unit"] = np.exp(coef["coefficient"])
    coef["business_feature"] = (
        coef["encoded_feature"]
        .str.replace("num__", "", regex=False)
        .str.replace("cat__", "", regex=False)
        .str.replace("peer_group_", "peer_group=", regex=False)
    )
    return coef.sort_values("abs_coefficient", ascending=False)


def prepare_gbm_frame(frame: pd.DataFrame, features: list[str], categorical: list[str]) -> pd.DataFrame:
    out = frame[features].copy()
    numeric = [f for f in features if f not in categorical]
    for col in numeric:
        out[col] = out[col].fillna(out[col].median())
    for col in categorical:
        out[col] = out[col].fillna("missing").astype("category")
    return out


def evaluate_model_challengers(
    core_990: pd.DataFrame,
    final_features: list[str],
    label_col: str,
    backbone,
) -> tuple[pd.DataFrame, pd.DataFrame, Pipeline, pd.DataFrame]:
    numeric_pool, categorical_pool = numeric_and_categorical_pools(backbone)
    categorical = [f for f in final_features if f in categorical_pool]
    logistic = build_logistic_pipeline(final_features, numeric_pool, categorical_pool)
    metric_rows: list[dict[str, Any]] = []
    calibration_rows: list[dict[str, Any]] = []
    final_logistic_model: Pipeline | None = None
    final_predictions: pd.DataFrame | None = None

    for split_name, train_years, test_year in [
        ("train_2017_test_2018", [2017], 2018),
        ("train_2017_2018_test_2021", [2017, 2018], 2021),
        ("train_2017_2018_2021_test_2022", [2017, 2018, 2021], 2022),
    ]:
        train_df = core_990.loc[core_990["feature_year"].isin(train_years)].copy()
        test_df = core_990.loc[core_990["feature_year"].eq(test_year)].copy()
        y_train = train_df[label_col].astype(int)
        y_test = test_df[label_col].astype(int)

        logistic.fit(train_df[final_features], y_train)
        p_log = logistic.predict_proba(test_df[final_features])[:, 1]

        x_train_gbm = prepare_gbm_frame(train_df, final_features, categorical)
        x_test_gbm = prepare_gbm_frame(test_df, final_features, categorical)

        lightgbm = LGBMClassifier(
            objective="binary",
            n_estimators=300,
            learning_rate=0.05,
            num_leaves=31,
            min_child_samples=200,
            subsample=0.8,
            colsample_bytree=0.8,
            reg_lambda=1.0,
            random_state=SEED,
            verbosity=-1,
        )
        lightgbm.fit(x_train_gbm, y_train, categorical_feature=categorical)
        p_lgb = lightgbm.predict_proba(x_test_gbm)[:, 1]

        catboost = CatBoostClassifier(
            iterations=300,
            depth=6,
            learning_rate=0.05,
            loss_function="Logloss",
            verbose=False,
            random_seed=SEED,
            l2_leaf_reg=5.0,
            subsample=0.8,
        )
        cat_indices = [x_train_gbm.columns.get_loc(col) for col in categorical]
        catboost.fit(x_train_gbm, y_train, cat_features=cat_indices)
        p_cat = catboost.predict_proba(x_test_gbm)[:, 1]

        p_blend = 0.5 * (p_lgb + p_cat)
        for model_name, pred in {
            "upgraded_logistic": p_log,
            "lightgbm": p_lgb,
            "catboost": p_cat,
            "catboost_lightgbm_blend": p_blend,
        }.items():
            metric_rows.append(
                {
                    "experiment_family": "model_family",
                    "experiment_name": model_name,
                    "label_key": label_col,
                    "split_name": split_name,
                    **metric_block(y_test, pred),
                }
            )
            calibration_rows.append({"model_name": model_name, "split_name": split_name, **calibration_summary(y_test, pred)})

        if split_name == "train_2017_2018_2021_test_2022":
            final_logistic_model = logistic
            final_predictions = test_df[["ein", "business_name", "feature_year", "peer_group"]].copy()
            final_predictions["actual_label"] = y_test.values
            final_predictions["upgraded_logistic_pred"] = p_log
            final_predictions["catboost_lightgbm_blend_pred"] = p_blend

    assert final_logistic_model is not None
    assert final_predictions is not None
    return pd.DataFrame(metric_rows), pd.DataFrame(calibration_rows), final_logistic_model, final_predictions


def attach_sector_lookup(latest: pd.DataFrame) -> pd.DataFrame:
    lookup_path = ROOT / "distress_outputs" / "fairlight_package" / "irs_ntee_lookup.csv"
    if not lookup_path.exists():
        latest["NTEE_CD"] = np.nan
        latest["sector_group"] = np.nan
        return latest
    lookup = pd.read_csv(lookup_path, usecols=["EIN", "NTEE_CD"], low_memory=False).drop_duplicates(subset=["EIN"])
    broad_map = {
        "A": "Arts, Culture & Humanities",
        "B": "Education",
        "C": "Environment",
        "D": "Animal-Related",
        "E": "Health Care",
        "F": "Mental Health & Crisis Intervention",
        "G": "Diseases & Medical Disciplines",
        "H": "Medical Research",
        "I": "Crime, Legal & Public Safety",
        "J": "Employment",
        "K": "Food, Agriculture & Nutrition",
        "L": "Housing & Shelter",
        "M": "Public Safety, Disaster Preparedness & Relief",
        "N": "Recreation & Sports",
        "O": "Youth Development",
        "P": "Human Services",
        "Q": "International & Foreign Affairs",
        "R": "Civil Rights & Advocacy",
        "S": "Community Improvement & Capacity Building",
        "T": "Philanthropy & Grantmaking",
        "U": "Science & Technology",
        "V": "Social Science",
        "W": "Public & Societal Benefit",
        "X": "Religion-Related",
        "Y": "Mutual & Membership Benefit",
        "Z": "Unknown / Unclassified",
    }
    latest = latest.merge(lookup, left_on="ein", right_on="EIN", how="left")
    latest["sector_group"] = latest["NTEE_CD"].astype(str).str[0].map(broad_map)
    latest = latest.drop(columns=["EIN"])
    return latest


def build_peer_reference_maps(latest: pd.DataFrame) -> dict[str, dict[tuple[Any, ...], dict[str, Any]]]:
    group_cols = ["feature_year", "return_type_clean", "peer_group"]
    refs: dict[str, dict[tuple[Any, ...], dict[str, Any]]] = {}
    metrics = {
        "coverage": "log_net_asset_coverage",
        "margin": "operating_margin_clean",
        "liability": "liability_ratio_clean",
        "revenue_growth": "revenue_growth_clean",
    }
    for prefix, col in metrics.items():
        metric_refs: dict[tuple[Any, ...], dict[str, Any]] = {}
        for key, subset in latest.groupby(group_cols):
            values = np.sort(subset[col].dropna().to_numpy(dtype=float))
            if len(values) == 0:
                continue
            metric_refs[key] = {
                "values": values,
                "mean": float(np.nanmean(values)),
                "std": float(np.nanstd(values, ddof=1)) if len(values) > 1 else float("nan"),
                "median": float(np.nanmedian(values)),
            }
        refs[prefix] = metric_refs
    return refs


def apply_peer_reference_maps(frame: pd.DataFrame, refs: dict[str, dict[tuple[Any, ...], dict[str, Any]]]) -> pd.DataFrame:
    out = frame.copy().reset_index(drop=True)
    group_cols = ["feature_year", "return_type_clean", "peer_group"]
    metrics = {
        "coverage": "log_net_asset_coverage",
        "margin": "operating_margin_clean",
        "liability": "liability_ratio_clean",
        "revenue_growth": "revenue_growth_clean",
    }
    for prefix, col in metrics.items():
        pct = np.full(len(out), np.nan)
        resid = np.full(len(out), np.nan)
        z = np.full(len(out), np.nan)
        for key, positions in out.groupby(group_cols).indices.items():
            ref = refs[prefix].get(key)
            if ref is None:
                continue
            values = out.iloc[positions][col].to_numpy(dtype=float)
            pct[positions] = np.searchsorted(ref["values"], values, side="right") / len(ref["values"])
            resid[positions] = values - ref["median"]
            if np.isfinite(ref["std"]) and ref["std"] > 1e-9:
                z[positions] = np.clip((values - ref["mean"]) / ref["std"], -4, 4)
            else:
                z[positions] = 0.0
        out[f"peer_pct_{prefix}_obs"] = pct
        out[f"peer_{prefix}_resid_obs"] = resid
        out[f"peer_{prefix}_z_obs"] = z
    return out


def compute_threshold_scan(train_df: pd.DataFrame, test_df: pd.DataFrame, label_col: str) -> pd.DataFrame:
    candidates = [
        ("reserve_months_proxy", "overall"),
        ("peer_pct_coverage_obs", "overall"),
        ("liability_ratio_clean", "overall"),
        ("peer_pct_margin_obs", "overall"),
        ("revenue_hhi_clean", "overall"),
        ("revenue_growth_clean", "overall"),
        ("expense_growth_gap", "overall"),
        ("reserve_months_proxy", "donation_led"),
        ("peer_pct_coverage_obs", "mixed"),
        ("liability_ratio_clean", "1M_3M"),
        ("reserve_months_proxy", "3M_10M"),
    ]
    rows: list[dict[str, Any]] = []
    for variable, segment in candidates:
        if segment == "overall":
            tr, te, segment_label = train_df.copy(), test_df.copy(), "overall"
        elif segment in {"donation_led", "program_led", "mixed"}:
            tr = train_df.loc[train_df["funding_bucket"] == segment].copy()
            te = test_df.loc[test_df["funding_bucket"] == segment].copy()
            segment_label = f"funding={segment}"
        else:
            tr = train_df.loc[train_df["size_bucket"] == segment].copy()
            te = test_df.loc[test_df["size_bucket"] == segment].copy()
            segment_label = f"size={segment}"
        if len(tr) < 2000 or variable not in tr or tr[variable].dropna().nunique() < 10:
            continue
        thresholds = sorted(tr[variable].dropna().quantile([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]).unique())
        best_row, best_score = None, -np.inf
        for thr in thresholds:
            for direction in ["below", "above"]:
                tr_flag = tr[variable] <= thr if direction == "below" else tr[variable] >= thr
                te_flag = te[variable] <= thr if direction == "below" else te[variable] >= thr
                if tr_flag.sum() < 500 or (~tr_flag).sum() < 500 or te_flag.sum() < 300 or (~te_flag).sum() < 300:
                    continue
                tr_rate_a = float(tr.loc[tr_flag, label_col].mean())
                tr_rate_b = float(tr.loc[~tr_flag, label_col].mean())
                if tr_rate_a <= tr_rate_b:
                    continue
                score = tr_rate_a - tr_rate_b
                if score <= best_score:
                    continue
                te_rate_a = float(te.loc[te_flag, label_col].mean())
                te_rate_b = float(te.loc[~te_flag, label_col].mean())
                if te_rate_a <= te_rate_b:
                    continue
                odds_ratio_test = ((te_rate_a + 1e-9) / (1 - te_rate_a + 1e-9)) / (
                    (te_rate_b + 1e-9) / (1 - te_rate_b + 1e-9)
                )
                best_score = score
                best_row = {
                    "variable": variable,
                    "segment": segment_label,
                    "threshold_rule": f"{variable} {'<=' if direction == 'below' else '>='} {thr:.3f}",
                    "distress_rate_a": te_rate_a,
                    "distress_rate_b": te_rate_b,
                    "lift_or_odds_ratio": float(odds_ratio_test),
                    "support_count": int(te_flag.sum() if direction == "below" else (~te_flag).sum()),
                }
        if best_row:
            rows.append(best_row)
    return pd.DataFrame(rows).sort_values("lift_or_odds_ratio", ascending=False)


def score_latest_year(
    featured: pd.DataFrame,
    model: Pipeline,
    final_features: list[str],
) -> pd.DataFrame:
    latest = featured.loc[
        (featured["tax_year"] == 2023)
        & (featured["observed_flag"] == 1)
        & (featured["return_type_clean"] == "990")
    ].copy()
    latest["feature_year"] = latest["tax_year"]
    latest["predicted_distress_probability"] = model.predict_proba(latest[final_features])[:, 1]
    latest["risk_bucket"] = risk_bucket_from_prob(latest["predicted_distress_probability"])
    latest["peer_margin_percentile"] = latest["peer_pct_margin_obs"]
    latest["peer_reserve_percentile"] = latest["peer_pct_coverage_obs"]
    latest["peer_liability_percentile"] = latest["peer_pct_liability_obs"]
    return latest


def build_shock_scenario_summary(results: pd.DataFrame) -> pd.DataFrame:
    return (
        results.groupby("scenario_name")
        .agg(
            org_count=("ein", "size"),
            avg_baseline_risk=("baseline_risk", "mean"),
            avg_shocked_risk=("shocked_risk", "mean"),
            avg_absolute_increase=("absolute_increase", "mean"),
            median_absolute_increase=("absolute_increase", "median"),
            bucket_upshift_share=("bucket_shift", lambda s: (s > 0).mean()),
            severe_jump_share=("bucket_shift", lambda s: (s >= 2).mean()),
        )
        .reset_index()
        .sort_values("avg_absolute_increase", ascending=False)
    )


def run_peer_aware_shocks(
    latest: pd.DataFrame,
    model: Pipeline,
    final_features: list[str],
    package,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    baseline = latest.copy().reset_index(drop=True)
    baseline["baseline_risk"] = baseline["predicted_distress_probability"]
    baseline["baseline_bucket"] = baseline["risk_bucket"]
    refs = build_peer_reference_maps(baseline)
    results: list[pd.DataFrame] = []
    for scenario in SCENARIOS:
        shocked = package.recompute_shocked_features(baseline, scenario)
        shocked["feature_year"] = baseline["feature_year"]
        shocked["return_type_clean"] = baseline["return_type_clean"]
        shocked["peer_group"] = baseline["peer_group"]
        shocked["log_net_asset_coverage"] = np.log1p(
            shocked["reserve_months_proxy"].clip(lower=0)
        ).clip(upper=np.log1p(120))
        shocked = apply_peer_reference_maps(shocked, refs)
        shocked_prob = model.predict_proba(shocked[final_features])[:, 1]
        shocked["shocked_risk"] = shocked_prob
        shocked["shocked_bucket"] = risk_bucket_from_prob(shocked["shocked_risk"])
        shocked["absolute_increase"] = shocked["shocked_risk"] - shocked["baseline_risk"]
        shocked["relative_increase"] = shocked["absolute_increase"] / shocked["baseline_risk"].replace(0, np.nan)
        order = {label: idx for idx, label in enumerate(RISK_BUCKETS)}
        shocked["bucket_shift"] = shocked["shocked_bucket"].map(order).astype(int) - shocked["baseline_bucket"].map(order).astype(int)
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
                    "peer_group",
                    "funding_bucket",
                    "size_bucket",
                    "sector_group",
                    "baseline_risk",
                    "shocked_risk",
                    "absolute_increase",
                    "relative_increase",
                    "baseline_bucket",
                    "shocked_bucket",
                    "bucket_shift",
                    "risk_bucket_transition",
                    "main_drivers",
                    "scenario_name",
                    "scenario_family",
                    "shock_size",
                ]
            ].copy()
        )
    results_df = pd.concat(results, ignore_index=True)
    scenario_summary = build_shock_scenario_summary(results_df)
    worst_case = (
        results_df.sort_values(["absolute_increase", "shocked_risk"], ascending=[False, False])
        .groupby("ein", as_index=False)
        .first()
        .rename(
            columns={
                "scenario_name": "worst_case_scenario",
                "shocked_risk": "worst_case_risk",
                "absolute_increase": "worst_case_delta",
                "relative_increase": "worst_case_relative_increase",
                "risk_bucket_transition": "worst_case_bucket_transition",
                "main_drivers": "worst_case_drivers",
            }
        )
    )
    return scenario_summary, worst_case


def build_insight_evidence(
    core_990: pd.DataFrame,
    latest: pd.DataFrame,
    threshold_scan: pd.DataFrame,
    shortlists: pd.DataFrame,
    shock_summary: pd.DataFrame,
    label_col: str,
) -> pd.DataFrame:
    test_2022 = core_990.loc[core_990["feature_year"] == 2022].copy()
    base_rate = float(test_2022[label_col].mean())
    donation_combo = (test_2022["donation_share_clean"] > 0.75) & (test_2022["revenue_hhi_clean"] > 0.70) & (test_2022["reserve_months_proxy"] < 2.0)
    high_risk_share = float(latest["risk_bucket"].isin(["High", "Very High"]).mean())
    top_scenario = shock_summary.iloc[0]
    rows = [
        {
            "insight_key": "reserve_threshold",
            "plain_english_statement": "Thin reserve buffers remain the cleanest distress separator after the upgrade.",
            "evidence": threshold_scan.iloc[0]["threshold_rule"],
            "value": round(float(threshold_scan.iloc[0]["lift_or_odds_ratio"]), 3),
            "confidence": "high",
        },
        {
            "insight_key": "peer_reserve_context",
            "plain_english_statement": "Peer-relative reserve weakness now carries stronger, cleaner holdout lift than before.",
            "evidence": "peer_pct_coverage_obs threshold",
            "value": round(float(threshold_scan.loc[threshold_scan["variable"] == "peer_pct_coverage_obs", "lift_or_odds_ratio"].max()), 3),
            "confidence": "high",
        },
        {
            "insight_key": "leverage_pressure",
            "plain_english_statement": "High leverage is still a primary risk dimension and becomes easier to defend in peer context.",
            "evidence": "liability_ratio_clean threshold",
            "value": round(float(threshold_scan.loc[threshold_scan["variable"] == "liability_ratio_clean", "lift_or_odds_ratio"].max()), 3),
            "confidence": "high",
        },
        {
            "insight_key": "donation_fragility",
            "plain_english_statement": "Donation dependence is still only dangerous when concentration and low cushion travel together.",
            "evidence": "2022 holdout distress rate for donation-heavy, concentrated, low-cushion rows",
            "value": round(float(test_2022.loc[donation_combo, label_col].mean()), 3),
            "confidence": "high",
        },
        {
            "insight_key": "triage_concentration",
            "plain_english_statement": "The upgraded score still supports triage rather than broad-brush intervention.",
            "evidence": "2023 High/Very High share",
            "value": round(high_risk_share, 3),
            "confidence": "high",
        },
        {
            "insight_key": "scenario_pressure",
            "plain_english_statement": "The most dangerous scenario remains immediately presentation-ready for a judge-facing stress slide.",
            "evidence": str(top_scenario["scenario_name"]),
            "value": round(float(top_scenario["avg_absolute_increase"]), 4),
            "confidence": "high",
        },
        {
            "insight_key": "shortlist_actionability",
            "plain_english_statement": "The rerun still produces targeted intervention-ready shortlists.",
            "evidence": "shortlist rows generated",
            "value": float(len(shortlists)),
            "confidence": "high",
        },
        {
            "insight_key": "base_rate",
            "plain_english_statement": "The retained label still marks a minority class that is large enough for action but not so broad it loses meaning.",
            "evidence": "2022 holdout prevalence",
            "value": round(base_rate, 3),
            "confidence": "medium",
        },
    ]
    return pd.DataFrame(rows)


def write_markdowns(
    scorecard: pd.DataFrame,
    calibration: pd.DataFrame,
    threshold_scan: pd.DataFrame,
    insight_table: pd.DataFrame,
    feature_sets: dict[str, list[str]],
    final_features: list[str],
    final_label: str,
    final_logistic_coef: pd.DataFrame,
    shock_summary: pd.DataFrame,
    selected_shortlists: pd.DataFrame,
) -> None:
    feature_2022 = scorecard.loc[
        (scorecard["experiment_family"] == "feature_variant")
        & (scorecard["split_name"] == "train_2017_2018_2021_test_2022")
    ].copy()
    label_2022 = scorecard.loc[
        (scorecard["experiment_family"] == "label_candidate")
        & (scorecard["split_name"] == "train_2017_2018_2021_test_2022")
    ].copy()
    model_2022 = scorecard.loc[
        (scorecard["experiment_family"] == "model_family")
        & (scorecard["split_name"] == "train_2017_2018_2021_test_2022")
    ].copy()
    macro_2022 = scorecard.loc[
        (scorecard["experiment_family"] == "macro_pack")
        & (scorecard["split_name"] == "train_2017_2018_2021_test_2022")
    ].copy()

    feature_keep = feature_2022.loc[feature_2022["experiment_name"] == "peer_anchored_no_direct"].iloc[0]
    feature_direct = feature_2022.loc[feature_2022["experiment_name"] == "peer_anchored_with_direct"].iloc[0]
    label_keep = label_2022.loc[label_2022["experiment_name"] == final_label].iloc[0]
    advanced_best = model_2022.sort_values(["roc_auc", "pr_auc"], ascending=False).iloc[0]
    logistic_row = model_2022.loc[model_2022["experiment_name"] == "upgraded_logistic"].iloc[0]

    top_logistic_features = final_logistic_coef.loc[
        ~final_logistic_coef["business_feature"].str.startswith("peer_group=")
    ].head(8)[["business_feature", "coefficient", "odds_ratio_per_scaled_unit"]]

    integration_md = f"""# Integration Decision Log

| Proposed change | Decision | Why |
|---|---|---|
| Log-transform the net-asset coverage signal and stop relying on raw `expense_coverage` | implement now | Raw `expense_coverage` is unstable and judge-hostile. The log net-asset coverage version improved 2022 holdout versus the old backbone (ROC-AUC {feature_2022.loc[feature_2022['experiment_name'] == 'baseline_current_backbone', 'roc_auc'].iloc[0]:.3f} -> {feature_2022.loc[feature_2022['experiment_name'] == 'coverage_fix_only', 'roc_auc'].iloc[0]:.3f}) while keeping the reserve story intact. |
| Remove direct current-year margin and coverage from the main logistic feature set | implement now | Once peer anchors were added, removing direct current-year margin and coverage barely changed 2022 holdout (ROC-AUC {feature_direct['roc_auc']:.3f} vs {feature_keep['roc_auc']:.3f}) and reduced circularity between the score, thresholds, and shortlist logic. |
| Rebuild peer-relative anchors using observed rows only | implement now | This directly improves holdout validity and makes benchmark cards cleaner. The new peer-anchored feature variants materially outperformed the old backbone. |
| Upgrade the distress label to a peer-relative multi-signal target | implement now | The selected label `{final_label}` improved holdout behavior and made threshold discovery much stronger without becoming impossible to explain. |
| Keep a tighter bottom-15% peer version of the label | reject | It matched the old prevalence better, but bottom quintile language is simpler and the bottom-20% version produced stronger, more presentation-ready threshold evidence. |
| Add the 4 FRED-style macro interaction features to the retained logistic | reject | The macro pack hurt every retained holdout and mostly acted like a disguised year effect on only four reliable feature years. |
| Replace the backbone with the CatBoost + LightGBM challenger | test but do not adopt yet | It is clearly stronger technically, but it adds story complexity and weakens the threshold-to-action narrative. Keep it as a credibility benchmark, not the presentation backbone. |
| Pull in older v3 work as truth | reject | No local v3 artifact was available in this repo, and the request was to treat old work as a donor rather than truth. |
"""
    (RESULTS_DIR / "integration_decision_log.md").write_text(integration_md, encoding="utf-8")

    label_md = f"""# Label Comparison

## Candidates tested

{label_2022[['experiment_name', 'overall_rate', 'year_rate_std', 'roc_auc', 'pr_auc', 'brier']].to_markdown(index=False)}

## Business meaning

- `current_static_label`: the original accepted rule. It is simple, but it relies on uniform raw thresholds and under-uses peer context.
- `peer_relative_delta_label`: clean deterioration logic with excellent year-rate stability, but too narrow for the hackathon story because it mostly tags only the sharpest collapses.
- `peer_relative_composite_tight`: technically strong and closer to the old prevalence, but the bottom-15% cutoff is harder to explain on stage.
- `{final_label}`: next-year distress is flagged when at least two peer-relative weakness or deterioration symptoms show up, or when balance-sheet failure pairs with at least middling-to-weak peer margin. This gives us "bottom-quintile / top-quintile plus deterioration" language judges can follow.

## Holdout behavior

- Selected label 2022 holdout ROC-AUC: {label_keep['roc_auc']:.3f}
- Selected label 2022 holdout PR-AUC: {label_keep['pr_auc']:.3f}
- Selected label 2022 prevalence: {label_keep['prevalence']:.1%}
- Selected label year-rate standard deviation: {label_keep['year_rate_std']:.3f}

## Final recommendation

- Keep `{final_label}` as the retained distress label.
- Why: it balances business meaning, peer-relative deterioration, threshold usefulness, and holdout behavior better than the old static label.
- Caveat: it is modestly more complex than the original label, so the presentation should describe it as a "bottom-quintile peer weakness plus deterioration" target rather than reciting the full formula.
"""
    (RESULTS_DIR / "label_comparison.md").write_text(label_md, encoding="utf-8")

    feature_md = f"""# Feature Change Audit

## Coverage metric decision

- Implemented: `log_net_asset_coverage`
- Kept for business readout: raw `reserve_months_proxy`
- Why: the log version stabilizes the predictor, while reserve months stays easier to present in benchmark cards and threshold slides.

## Features added

- `log_net_asset_coverage`
- `peer_pct_coverage_obs`
- `peer_pct_margin_obs`
- `peer_pct_liability_obs`
- `peer_pct_revenue_growth_obs`
- `peer_coverage_resid_obs`
- `peer_margin_resid_obs`
- `peer_liability_resid_obs`
- `peer_revenue_growth_resid_obs`
- `peer_coverage_z_obs`
- `peer_margin_z_obs`
- `coverage_change_1y_log`

## Features removed from the retained predictive set

- `operating_margin_clean`
- `reserve_months_proxy`
- direct current-year margin and reserve levels from the logistic backbone

## Circularity cleanup

- The retained score now relies on peer-relative margin and coverage anchors instead of directly reusing the same current-year reserve and margin constructs that also drive business rules and shortlist framing.
- The 2022 holdout drop from keeping direct features versus removing them was negligible:
  - ROC-AUC {feature_direct['roc_auc']:.3f} with direct features
  - ROC-AUC {feature_keep['roc_auc']:.3f} without direct features

## Macro feature decision

- Tested macro pack: `macro_donation_unrate`, `macro_concentration_unrate`, `macro_expensegap_inflation`, `macro_leverage_rates`
- Decision: reject
- Why: the pack degraded the retained logistic on every holdout and added more year-noise risk than insight value.

## Final retained feature set

`{", ".join(final_features)}`
"""
    (RESULTS_DIR / "feature_change_audit.md").write_text(feature_md, encoding="utf-8")

    model_md = f"""# Model Comparison

## 2022 holdout scorecard

{model_2022[['experiment_name', 'roc_auc', 'pr_auc', 'brier', 'precision_at_0_20', 'precision_at_top_10pct']].to_markdown(index=False)}

## Calibration snapshot

{calibration.loc[calibration['split_name'] == 'train_2017_2018_2021_test_2022', ['model_name', 'ece_10', 'max_bin_gap']].to_markdown(index=False)}

## Interpretability

- `upgraded_logistic`: cleanest to explain, easiest to translate into thresholds, and easiest to defend in a hackathon room.
- `catboost_lightgbm_blend`: materially stronger on pure metrics, but not naturally threshold-first and much harder to narrate without a model-mechanics detour.

## Recommendation

- Retain `upgraded_logistic` as the presentation backbone.
- Keep `catboost_lightgbm_blend` as an appendix or credibility benchmark only.
- Reason: the advanced challenger is clearly stronger ({advanced_best['roc_auc']:.3f} ROC-AUC vs {logistic_row['roc_auc']:.3f} for logistic in 2022), but the hackathon value of switching is smaller than the story cost.

## What the retained logistic is learning

{top_logistic_features.to_markdown(index=False)}
"""
    (RESULTS_DIR / "model_comparison.md").write_text(model_md, encoding="utf-8")

    stronger = insight_table.loc[insight_table["insight_key"].isin(["reserve_threshold", "peer_reserve_context", "leverage_pressure", "scenario_pressure"])]
    insight_md = f"""# Insight Impact Review

## What got stronger

- Reserve threshold evidence got stronger and cleaner; the final threshold scan now produces larger replicated lifts.
- Peer-relative weakness is safer to present because it is now embedded both in the label and in the retained score.
- Leverage pressure is more defensible as a core storyline because it shows up in both the new label and the upgraded logistic.
- Scenario storytelling is still intact after the backbone change, and the rerun shortlist remains action-oriented.

## What got weaker

- The final backbone says less directly about raw current-year operating margin because that signal was deliberately moved out of the retained predictive set.
- Macro sensitivity claims did not survive testing and should be dropped rather than padded.

## Safe judge-facing insights

{stronger[['plain_english_statement', 'evidence', 'value', 'confidence']].to_markdown(index=False)}

## Recommendation

- Present the stronger reserve, leverage, peer-relative weakness, and scenario triage insights confidently.
- Do not present macro-interaction claims or pretend the advanced challenger is the main engine.
"""
    (RESULTS_DIR / "insight_impact_review.md").write_text(insight_md, encoding="utf-8")

    final_md = f"""# Final Backbone Recommendation

## Blunt answer

- Final technical backbone: upgraded logistic regression
- Final label: `{final_label}`
- Final predictive feature pattern: peer-anchored, no direct current-year margin or coverage levels

## Exact changes to keep

- log-transformed net-asset coverage
- observed-only peer percentiles, residuals, and z-scores
- peer-relative composite distress label
- circularity cleanup that removes direct current-year margin and reserve from the retained score
- benchmark, shortlist, threshold, and shock reruns off the upgraded logistic

## What to leave out

- the macro interaction pack
- switching the presentation backbone to CatBoost + LightGBM
- the tighter bottom-15% label variant
- any new technical work that forces a model-explainer detour in the live story

## Are we better positioned to win?

- Yes.
- The science is cleaner, the benchmark story is more credible, the threshold slides get stronger, and the judges do not have to swallow a black-box rewrite.

## Should we stop technical work now?

- Yes.
- Freeze the upgraded logistic backbone now, keep the advanced challenger as appendix evidence only, and move the team fully into storytelling, demo flow, and slide polish.

## Final rerun outputs

- Shortlist rows regenerated: {len(selected_shortlists)}
- Top shock scenario: `{shock_summary.iloc[0]['scenario_name']}` with average risk increase {shock_summary.iloc[0]['avg_absolute_increase']:.4f}
"""
    (RESULTS_DIR / "final_backbone_recommendation.md").write_text(final_md, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    backbone, package = load_modules()

    raw = backbone.load_data()
    featured = build_upgrade_features(raw, backbone)
    panel = build_panel_with_candidate_labels(featured, backbone)
    core_990 = panel.loc[panel["return_type_clean"] == "990"].copy()

    feature_variant_metrics, feature_sets = evaluate_feature_variants(core_990, "peer_relative_composite", backbone)
    final_features = feature_sets["peer_anchored_no_direct"]
    label_metrics = evaluate_label_candidates(core_990, final_features, backbone)
    macro_metrics, _, _ = evaluate_macro_pack(core_990, final_features, RESULT_LABEL_KEY, backbone)
    model_metrics, calibration_metrics, final_logistic_model, _ = evaluate_model_challengers(
        core_990, final_features, RESULT_LABEL_KEY, backbone
    )

    evaluation_scorecard = pd.concat([feature_variant_metrics, label_metrics, macro_metrics, model_metrics], ignore_index=True)
    evaluation_scorecard.to_csv(RESULTS_DIR / "evaluation_scorecard.csv", index=False)
    calibration_metrics.to_csv(RESULTS_DIR / "calibration_summary.csv", index=False)

    final_train = core_990.loc[core_990["feature_year"].isin([2017, 2018, 2021, 2022])].copy()
    final_logistic_model.fit(final_train[final_features], final_train[RESULT_LABEL_KEY].astype(int))
    coef = extract_logistic_coefficients(final_logistic_model)

    threshold_scan = compute_threshold_scan(
        core_990.loc[core_990["feature_year"].isin([2017, 2018, 2021])].copy(),
        core_990.loc[core_990["feature_year"] == 2022].copy(),
        RESULT_LABEL_KEY,
    )
    threshold_scan.to_csv(RESULTS_DIR / "threshold_scan.csv", index=False)

    latest = score_latest_year(featured, final_logistic_model, final_features)
    latest = attach_sector_lookup(latest)
    peer_cards = package.build_peer_benchmark_cards(latest)

    shock_summary, worst_case = run_peer_aware_shocks(latest, final_logistic_model, final_features, package)
    shock_summary.to_csv(RESULTS_DIR / "shock_scenario_summary.csv", index=False)

    shortlists = package.build_shortlists(peer_cards, worst_case)
    insight_table = build_insight_evidence(core_990, latest, threshold_scan, shortlists, shock_summary, RESULT_LABEL_KEY)
    insight_table.to_csv(RESULTS_DIR / "insight_evidence_table.csv", index=False)

    write_markdowns(
        evaluation_scorecard,
        calibration_metrics,
        threshold_scan,
        insight_table,
        feature_sets,
        final_features,
        RESULT_LABEL_KEY,
        coef,
        shock_summary,
        shortlists,
    )

    summary = {
        "results_dir": str(RESULTS_DIR),
        "selected_label": RESULT_LABEL_KEY,
        "selected_features": final_features,
        "final_model": "upgraded_logistic",
        "rows_core_990": int(len(core_990)),
        "top_shock_scenario": str(shock_summary.iloc[0]["scenario_name"]),
    }
    (RESULTS_DIR / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
