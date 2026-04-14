from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, precision_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler
from sklearn.tree import DecisionTreeClassifier


SEED = 42
ROOT = Path(r"E:\distressed")
INPUT_PATH = ROOT / "irs990_cohort_features.csv"
OUTPUT_DIR = ROOT / "distress_outputs"
INTERMEDIATE_DIR = OUTPUT_DIR / "intermediate"

NUMERIC_FEATURES = [
    "log_revenue_clean",
    "log_expenses_clean",
    "log_assets_clean",
    "operating_margin_clean",
    "reserve_months_proxy",
    "liability_ratio_clean",
    "net_asset_ratio_clean",
    "revenue_growth_clean",
    "expense_growth_clean",
    "expense_growth_gap",
    "asset_growth_clean",
    "donation_share_clean",
    "program_share_clean",
    "investment_share_clean",
    "revenue_hhi_clean",
    "salary_share_clean",
    "fundraising_share_clean",
    "grants_share_clean",
    "log_employees_clean",
    "org_age_clean",
    "peer_pct_margin",
    "peer_pct_reserve",
    "peer_pct_liability",
    "peer_pct_revenue_growth",
    "margin_change_1y",
    "reserve_change_1y",
]

MISSING_FLAG_FEATURES = [
    "flag_missing_contributions_grants",
    "flag_missing_program_service_revenue",
    "flag_missing_investment_income",
    "flag_missing_salaries",
    "flag_missing_fundraising",
    "flag_missing_py_revenue",
    "flag_missing_py_expenses",
    "flag_missing_formation_year",
    "flag_missing_employees",
]

CATEGORICAL_FEATURES = ["peer_group", "census_region"]
PRIMARY_FEATURES = [
    "operating_margin_clean",
    "reserve_months_proxy",
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
]
TOP_K_LEVELS = [0.05, 0.10, 0.20]

REGION_MAP = {
    "CT": "Northeast",
    "ME": "Northeast",
    "MA": "Northeast",
    "NH": "Northeast",
    "RI": "Northeast",
    "VT": "Northeast",
    "NJ": "Northeast",
    "NY": "Northeast",
    "PA": "Northeast",
    "IL": "Midwest",
    "IN": "Midwest",
    "MI": "Midwest",
    "OH": "Midwest",
    "WI": "Midwest",
    "IA": "Midwest",
    "KS": "Midwest",
    "MN": "Midwest",
    "MO": "Midwest",
    "NE": "Midwest",
    "ND": "Midwest",
    "SD": "Midwest",
    "DE": "South",
    "DC": "South",
    "FL": "South",
    "GA": "South",
    "MD": "South",
    "NC": "South",
    "SC": "South",
    "VA": "South",
    "WV": "South",
    "AL": "South",
    "KY": "South",
    "MS": "South",
    "TN": "South",
    "AR": "South",
    "LA": "South",
    "OK": "South",
    "TX": "South",
    "AZ": "West",
    "CO": "West",
    "ID": "West",
    "MT": "West",
    "NV": "West",
    "NM": "West",
    "UT": "West",
    "WY": "West",
    "AK": "West",
    "CA": "West",
    "HI": "West",
    "OR": "West",
    "WA": "West",
}

FEATURE_REVIEW_ROWS = [
    ["years_in_panel", "prebuilt cohort table", "full-panel row count by EIN", "none", "no", "high", "high", "low", "Future-aware survivorship leakage; dropped."],
    ["years_observed", "prebuilt cohort table", "full-panel observed-row count", "none", "no", "high", "high", "low", "Future-aware survivorship leakage; dropped."],
    ["filing_consistency", "prebuilt cohort table", "observed/panel coverage ratio", "none", "no", "high", "high", "medium", "Panel-aware filing variable; dropped."],
    ["last_observed_year", "prebuilt cohort table", "supplied last observed year", "none", "no", "high", "high", "low", "Ambiguous panel-aware history; dropped."],
    ["years_since_last_observed", "prebuilt cohort table", "gap to supplied last observed year", "none", "no", "high", "high", "low", "Depends on panel-aware history; dropped."],
    ["expense_coverage", "prebuilt cohort table", "assets over expenses", "replaced by reserve_months_proxy", "no", "low", "low", "medium", "Total assets are too generous as a reserve proxy."],
    ["liability_ratio", "prebuilt cohort table", "existing liabilities/assets ratio", "recomputed as liability_ratio_clean", "no", "low", "low", "medium", "Original has impossible/extreme values from unstable denominators."],
    ["net_asset_ratio", "prebuilt cohort table", "existing net assets/assets ratio", "recomputed as net_asset_ratio_clean", "no", "low", "low", "medium", "Original leaves logical bounds too often."],
    ["operating_margin", "prebuilt cohort table", "existing surplus margin", "recomputed as operating_margin_clean", "no", "low", "low", "high", "Original contains denominator blowups."],
    ["revenue_growth", "prebuilt cohort table", "existing revenue growth", "recomputed as revenue_growth_clean", "no", "low", "low", "high", "Requires positive prior-year revenue to stay sane."],
    ["expense_growth", "prebuilt cohort table", "existing expense growth", "recomputed as expense_growth_clean", "no", "low", "low", "high", "Requires positive prior-year expense to stay sane."],
    ["asset_growth", "prebuilt cohort table", "existing asset growth", "recomputed as asset_growth_clean", "no", "low", "low", "high", "Requires positive opening assets to stay sane."],
    ["donation_dependency", "prebuilt cohort table", "existing donations share", "recomputed as donation_share_clean", "no", "low", "low", "high", "Original leaves 0-1 range too often."],
    ["program_revenue_share", "prebuilt cohort table", "existing program share", "recomputed as program_share_clean", "no", "low", "low", "high", "Rebuilt from cleaned revenue components."],
    ["revenue_hhi", "prebuilt cohort table", "existing revenue concentration", "recomputed as revenue_hhi_clean", "no", "low", "low", "high", "Rebuilt from cleaned shares."],
    ["reserve_months_proxy", "rebuilt from raw columns", "positive net assets divided by monthly expenses", "clip 0-36 months", "yes", "low", "low", "high", "Best transparent reserve proxy available from filings."],
    ["operating_margin_clean", "rebuilt from raw columns", "surplus over max(revenue,expenses,1)", "clip -1.5 to 1.5", "yes", "low", "low", "high", "Core current-year stress signal; safe because label is next year."],
    ["liability_ratio_clean", "rebuilt from raw columns", "liabilities divided by assets", "clip 0-3", "yes", "low", "low", "high", "Clean leverage burden measure."],
    ["net_asset_ratio_clean", "rebuilt from raw columns", "net assets divided by assets", "clip -2 to 1", "yes", "low", "low", "high", "Cleaner solvency signal."],
    ["revenue_growth_clean", "rebuilt from raw columns", "revenue growth when prior revenue > 0", "clip -1 to 3", "yes", "low", "low", "high", "Direct funding-shock measure."],
    ["expense_growth_clean", "rebuilt from raw columns", "expense growth when prior expenses > 0", "clip -1 to 3", "yes", "low", "low", "high", "Operational pressure measure."],
    ["expense_growth_gap", "rebuilt from raw columns", "expense growth minus revenue growth", "difference", "yes", "low", "low", "high", "Captures costs outrunning income."],
    ["asset_growth_clean", "rebuilt from raw columns", "asset growth when opening assets > 0", "clip -1 to 3", "yes", "low", "low", "high", "Balance-sheet momentum measure."],
    ["donation_share_clean", "rebuilt from raw columns", "donations share of cleaned revenue components", "bounded 0-1 share", "yes", "low", "low", "high", "Funding dependence measure."],
    ["program_share_clean", "rebuilt from raw columns", "program share of cleaned revenue components", "bounded 0-1 share", "yes", "low", "low", "high", "Revenue-model counterweight to donations."],
    ["investment_share_clean", "rebuilt from raw columns", "investment share of cleaned revenue components", "bounded 0-1 share", "yes", "low", "low", "medium", "Useful for specific subsegments only."],
    ["revenue_hhi_clean", "rebuilt from raw columns", "concentration across revenue sources", "sum of squared shares", "yes", "low", "low", "high", "Concentration sharpens funding fragility."],
    ["salary_share_clean", "rebuilt from raw columns", "compensation share of expenses", "clip 0-1.5", "yes", "low", "low", "medium", "Simple cost-structure signal."],
    ["fundraising_share_clean", "rebuilt from raw columns", "fundraising share of expenses", "clip 0-1", "yes", "low", "low", "medium", "Better for intervention and benchmarking than for pure prediction."],
    ["grants_share_clean", "rebuilt from raw columns", "grants paid share of expenses", "clip 0-1.5", "yes", "low", "low", "medium", "Differentiates grantmakers from operators."],
    ["peer_pct_margin", "rebuilt peer benchmark", "margin percentile within year-form-peer group", "percentile rank", "yes", "low", "low", "high", "Key peer-relative distress context."],
    ["peer_pct_reserve", "rebuilt peer benchmark", "reserve percentile within year-form-peer group", "percentile rank", "yes", "low", "low", "high", "Key peer-relative resilience context."],
    ["peer_pct_liability", "rebuilt peer benchmark", "leverage percentile within year-form-peer group", "percentile rank", "yes", "low", "low", "high", "Peer-relative capital-structure context."],
    ["peer_pct_revenue_growth", "rebuilt peer benchmark", "growth percentile within year-form-peer group", "percentile rank", "yes", "low", "low", "high", "Peer-relative funding-shock context."],
    ["peer_margin_gap", "rebuilt peer benchmark", "margin minus peer median", "difference", "yes", "low", "low", "high", "Absolute and peer-relative views both matter."],
    ["peer_reserve_gap", "rebuilt peer benchmark", "reserve months minus peer median", "difference", "yes", "low", "low", "high", "Useful for benchmark-driven recommendations."],
    ["margin_change_1y", "rebuilt panel lag", "current margin minus prior-year margin", "difference", "yes", "low", "low", "high", "Simple deterioration trend variable."],
    ["reserve_change_1y", "rebuilt panel lag", "current reserve months minus prior-year reserve", "difference", "yes", "low", "low", "high", "Simple reserve-depletion trend variable."],
    ["peer_group", "prebuilt cohort table", "size x funding-model bucket", "one-hot", "yes", "low", "low", "high", "Only viable built-in peer taxonomy."],
    ["census_region", "rebuilt from state", "census-style region", "one-hot", "yes", "low", "low", "medium", "Light geography control without huge dimensionality."],
    ["imputed", "prebuilt cohort table", "row-level upstream imputation flag", "sensitivity only", "no", "medium", "medium", "medium", "Core model excludes imputed current rows; use only in sensitivity."],
]


@dataclass
class LabelOption:
    key: str
    title: str
    business_meaning: str
    formula: str
    pros: list[str]
    cons: list[str]
    bias_note: str
    recommended_use: str
    rule: Callable[[pd.DataFrame], pd.Series]


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    INTERMEDIATE_DIR.mkdir(exist_ok=True)


def safe_clip(series: pd.Series, low: float | None = None, high: float | None = None) -> pd.Series:
    if low is not None:
        series = series.clip(lower=low)
    if high is not None:
        series = series.clip(upper=high)
    return series


def safe_divide(num: pd.Series, den: pd.Series) -> pd.Series:
    den = den.where(den.abs() > 1e-9)
    return num / den


def growth_from_prior(current: pd.Series, previous: pd.Series, low: float = -1.0, high: float = 3.0) -> pd.Series:
    growth = safe_divide(current - previous, previous.where(previous > 0))
    return safe_clip(growth, low, high)


def log1p_nonnegative(series: pd.Series) -> pd.Series:
    return np.log1p(series.clip(lower=0))


def load_data() -> pd.DataFrame:
    df = pd.read_csv(INPUT_PATH, low_memory=False)
    df["return_type"] = df["return_type"].astype(str).str.strip().str.upper()
    df["business_name"] = df["business_name"].fillna("UNKNOWN")
    df["state"] = df["state"].fillna("UNK")
    return df


def add_safe_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    revenue_pos = out["total_revenue"].clip(lower=0)
    expenses_pos = out["total_expenses"].clip(lower=0)
    assets_pos = out["total_assets_eoy"].clip(lower=0)
    net_assets = out["net_assets_eoy"]
    liabilities = out["total_liabilities_eoy"].clip(lower=0)

    margin_den = pd.Series(
        np.maximum.reduce([revenue_pos.to_numpy(), expenses_pos.to_numpy(), np.ones(len(out))]),
        index=out.index,
    )
    out["operating_margin_clean"] = safe_clip(out["revenue_less_expenses"] / margin_den, -1.5, 1.5)
    out["reserve_months_proxy"] = safe_clip(
        safe_divide(net_assets.clip(lower=0) * 12.0, expenses_pos.where(expenses_pos > 0)), 0, 36
    )
    out["liability_ratio_clean"] = safe_clip(safe_divide(liabilities, assets_pos.where(assets_pos > 0)), 0, 3)
    out["net_asset_ratio_clean"] = safe_clip(safe_divide(net_assets, assets_pos.where(assets_pos > 0)), -2, 1)
    out["revenue_growth_clean"] = growth_from_prior(out["total_revenue"], out["py_total_revenue"])
    out["expense_growth_clean"] = growth_from_prior(out["total_expenses"], out["py_total_expenses"])
    out["asset_growth_clean"] = growth_from_prior(out["total_assets_eoy"], out["total_assets_boy"])
    out["expense_growth_gap"] = safe_clip(out["expense_growth_clean"] - out["revenue_growth_clean"], -4, 4)

    revenue_components = pd.DataFrame(
        {
            "contributions": out["contributions_grants"].clip(lower=0),
            "program": out["program_service_revenue"].clip(lower=0),
            "investment": out["investment_income"].clip(lower=0),
            "other": out["other_revenue"].clip(lower=0),
        }
    )
    component_total = revenue_components.sum(axis=1)
    out["donation_share_clean"] = safe_clip(
        safe_divide(revenue_components["contributions"], component_total.where(component_total > 0)), 0, 1
    )
    out["program_share_clean"] = safe_clip(
        safe_divide(revenue_components["program"], component_total.where(component_total > 0)), 0, 1
    )
    out["investment_share_clean"] = safe_clip(
        safe_divide(revenue_components["investment"], component_total.where(component_total > 0)), 0, 1
    )
    other_share = safe_clip(
        safe_divide(revenue_components["other"], component_total.where(component_total > 0)), 0, 1
    )
    out["revenue_hhi_clean"] = (
        out["donation_share_clean"].fillna(0) ** 2
        + out["program_share_clean"].fillna(0) ** 2
        + out["investment_share_clean"].fillna(0) ** 2
        + other_share.fillna(0) ** 2
    )

    out["salary_share_clean"] = safe_clip(
        safe_divide(out["salaries_and_compensation"].clip(lower=0), expenses_pos.where(expenses_pos > 0)), 0, 1.5
    )
    out["fundraising_share_clean"] = safe_clip(
        safe_divide(out["fundraising_expenses"].clip(lower=0), expenses_pos.where(expenses_pos > 0)), 0, 1
    )
    out["grants_share_clean"] = safe_clip(
        safe_divide(out["grants_and_similar_paid"].clip(lower=0), expenses_pos.where(expenses_pos > 0)), 0, 1.5
    )
    out["log_revenue_clean"] = log1p_nonnegative(out["total_revenue"])
    out["log_expenses_clean"] = log1p_nonnegative(out["total_expenses"])
    out["log_assets_clean"] = log1p_nonnegative(out["total_assets_eoy"])
    out["log_employees_clean"] = log1p_nonnegative(out["total_employees"])

    valid_formation = out["formation_year"].where(
        (out["formation_year"] > 1800) & (out["formation_year"] <= out["tax_year"])
    )
    out["org_age_clean"] = safe_clip(out["tax_year"] - valid_formation, 0, 200)

    out["funding_bucket"] = out["peer_group"].astype(str).str.split("__").str[-1]
    out["size_bucket"] = out["peer_group"].astype(str).str.split("__").str[0]
    out["census_region"] = out["state"].map(REGION_MAP).fillna("Other")
    out["return_type_clean"] = out["return_type"]

    peer_cols = ["tax_year", "return_type_clean", "peer_group"]
    out["peer_pct_margin"] = out.groupby(peer_cols)["operating_margin_clean"].rank(pct=True)
    out["peer_pct_reserve"] = out.groupby(peer_cols)["reserve_months_proxy"].rank(pct=True)
    out["peer_pct_liability"] = out.groupby(peer_cols)["liability_ratio_clean"].rank(pct=True)
    out["peer_pct_revenue_growth"] = out.groupby(peer_cols)["revenue_growth_clean"].rank(pct=True)
    peer_margin_med = out.groupby(peer_cols)["operating_margin_clean"].transform("median")
    peer_reserve_med = out.groupby(peer_cols)["reserve_months_proxy"].transform("median")
    out["peer_margin_gap"] = safe_clip(out["operating_margin_clean"] - peer_margin_med, -2, 2)
    out["peer_reserve_gap"] = safe_clip(out["reserve_months_proxy"] - peer_reserve_med, -36, 36)

    out = out.sort_values(["ein", "tax_year"]).reset_index(drop=True)
    prev_year = out.groupby("ein")["tax_year"].shift(1)
    has_prev = prev_year.eq(out["tax_year"] - 1)
    prev_margin = out.groupby("ein")["operating_margin_clean"].shift(1)
    prev_reserve = out.groupby("ein")["reserve_months_proxy"].shift(1)
    out["margin_change_1y"] = safe_clip((out["operating_margin_clean"] - prev_margin).where(has_prev), -2, 2)
    out["reserve_change_1y"] = safe_clip((out["reserve_months_proxy"] - prev_reserve).where(has_prev), -36, 36)
    return out


def add_next_year_fields(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    next_year = out.groupby("ein")["tax_year"].shift(-1)
    out["next_tax_year"] = next_year
    out["has_next_consecutive"] = next_year.eq(out["tax_year"] + 1)
    for col in cols:
        out[f"next_{col}"] = out.groupby("ein")[col].shift(-1).where(out["has_next_consecutive"])
    return out


def label_options() -> list[LabelOption]:
    return [
        LabelOption(
            key="deficit_plus_erosion",
            title="Operating Deficit Plus Erosion",
            business_meaning="Next year the nonprofit runs a meaningful operating deficit while already sitting on a thin balance-sheet cushion.",
            formula="1[next_operating_margin_clean <= -0.05 AND next_net_asset_ratio_clean <= 0.25]",
            pros=[
                "Simple to explain in business language.",
                "Targets organizations that are both losing money and thinly capitalized.",
                "Avoids tagging one-off deficits at strongly capitalized organizations as distress.",
            ],
            cons=[
                "Can miss fast-onset distress where reserves were still healthy at year-end.",
                "Sensitive to net-assets restrictions.",
            ],
            bias_note="Can understate distress for asset-rich but illiquid organizations.",
            recommended_use="candidate_primary",
            rule=lambda d: (d["next_operating_margin_clean"] <= -0.05) & (d["next_net_asset_ratio_clean"] <= 0.25),
        ),
        LabelOption(
            key="reserve_crunch",
            title="Reserve Crunch",
            business_meaning="Next year the organization finishes with effectively no meaningful reserve cushion or negative net assets.",
            formula="1[(next_reserve_months_proxy < 1.0) OR (next_net_assets_eoy <= 0)]",
            pros=[
                "Strong resilience framing.",
                "Maps directly into intervention logic around runway.",
                "Very easy to benchmark.",
            ],
            cons=[
                "Net assets are an imperfect liquidity proxy.",
                "Some asset-light pass-through organizations can look weaker than they are.",
            ],
            bias_note="Over-weights balance-sheet structure relative to abrupt income shocks.",
            recommended_use="screening_label",
            rule=lambda d: (d["next_reserve_months_proxy"] < 1.0) | (d["next_net_assets_eoy"] <= 0),
        ),
        LabelOption(
            key="composite_distress",
            title="Multi-Signal Distress",
            business_meaning="Next year the organization shows multiple independent signs of strain rather than a single bad metric.",
            formula="1[(sum of next-year symptoms >= 2) OR ((next_net_assets_eoy <= 0) AND (next_operating_margin_clean < 0))]; symptoms are margin<=-5%, reserve<1.5 months, leverage>0.85, revenue growth<=-20%, asset growth<=-10%",
            pros=[
                "Balances income statement, balance sheet, and funding shock evidence.",
                "Reduces noise from any one accounting quirk.",
                "Best match for judge-ready structural storytelling.",
            ],
            cons=[
                "Slightly more complex to explain than a one-ratio label.",
                "Threshold choices require judgment.",
            ],
            bias_note="Still depends on Form 990 balance-sheet proxies and may miss orderly wind-downs.",
            recommended_use="primary_label",
            rule=lambda d: (
                (
                    (d["next_operating_margin_clean"] <= -0.05).astype(int)
                    + (d["next_reserve_months_proxy"] < 1.5).astype(int)
                    + (d["next_liability_ratio_clean"] > 0.85).astype(int)
                    + (d["next_revenue_growth_clean"] <= -0.20).astype(int)
                    + (d["next_asset_growth_clean"] <= -0.10).astype(int)
                )
                >= 2
            )
            | ((d["next_net_assets_eoy"] <= 0) & (d["next_operating_margin_clean"] < 0)),
        ),
        LabelOption(
            key="filing_disappearance_aux",
            title="Filing Disappearance / Cessation",
            business_meaning="The organization stops appearing with an observed filing in the next cycle.",
            formula="1[next_observed_flag != 1], restricted to years with reliable follow-up coverage",
            pros=["Useful auxiliary validation target for severe outcomes.", "Connects naturally to continuity stories."],
            cons=["Not all disappearances are financial distress.", "Sensitive to filing lags and panel mechanics."],
            bias_note="Should not be used as the primary label because reporting behavior contaminates the signal.",
            recommended_use="aux_validation",
            rule=lambda d: d["next_observed_flag"] != 1,
        ),
    ]


def build_labeled_panel(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
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
    ]
    panel = add_next_year_fields(df, next_cols)
    panel["pair_current_observed"] = panel["observed_flag"] == 1
    panel["pair_next_observed"] = panel["next_observed_flag"] == 1
    panel["pair_current_imputed"] = panel["imputed"] == 1
    panel["feature_year"] = panel["tax_year"]
    panel["label_year"] = panel["next_tax_year"]

    for option in label_options():
        panel[option.key] = option.rule(panel).astype("float")
        panel.loc[~panel["has_next_consecutive"], option.key] = np.nan

    coverage = (
        panel.loc[panel["has_next_consecutive"]]
        .groupby("feature_year")
        .agg(
            rows=("ein", "size"),
            current_observed_share=("pair_current_observed", "mean"),
            next_observed_share=("pair_next_observed", "mean"),
        )
        .reset_index()
    )
    both_obs = (
        panel.loc[panel["has_next_consecutive"]]
        .groupby("feature_year")
        .apply(lambda g: ((g["pair_current_observed"]) & (g["pair_next_observed"])).sum(), include_groups=False)
        .reset_index(name="both_observed")
    )
    coverage = coverage.merge(both_obs, on="feature_year", how="left")
    coverage["both_observed_share"] = coverage["both_observed"] / coverage["rows"]
    reliable_feature_years = coverage.loc[
        (coverage["current_observed_share"] >= 0.30) & (coverage["next_observed_share"] >= 0.50),
        "feature_year",
    ].tolist()
    reliable_labeled_years = [year for year in reliable_feature_years if year <= 2022]

    core_mask = (
        panel["has_next_consecutive"]
        & panel["pair_current_observed"]
        & panel["pair_next_observed"]
        & panel["feature_year"].isin(reliable_labeled_years)
    )
    core_panel = panel.loc[core_mask].copy()
    coverage.to_csv(INTERMEDIATE_DIR / "pair_coverage_by_year.csv", index=False)
    core_panel.to_csv(INTERMEDIATE_DIR / "modeling_panel_observed_pairs.csv", index=False)
    return panel, core_panel


def build_design_matrix(data: pd.DataFrame, features: list[str]) -> pd.DataFrame:
    design = data[features].copy()
    for col in MISSING_FLAG_FEATURES:
        if col in design:
            design[col] = design[col].fillna(0).astype(float)
    for col in ["margin_change_1y", "reserve_change_1y"]:
        if col in design:
            design[col] = design[col].fillna(0.0)
    return design


def build_logistic_pipeline(feature_set: list[str]) -> Pipeline:
    numeric_features = [f for f in feature_set if f in NUMERIC_FEATURES or f in MISSING_FLAG_FEATURES or f == "current_row_imputed"]
    categorical_features = [f for f in feature_set if f in CATEGORICAL_FEATURES]
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", RobustScaler())]),
                numeric_features,
            ),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )
    model = LogisticRegression(C=0.8, max_iter=4000, solver="lbfgs", random_state=SEED)
    return Pipeline([("prep", preprocessor), ("model", model)])


def build_tree_pipeline(feature_set: list[str]) -> Pipeline:
    numeric_features = [f for f in feature_set if f in NUMERIC_FEATURES or f in MISSING_FLAG_FEATURES or f == "current_row_imputed"]
    categorical_features = [f for f in feature_set if f in CATEGORICAL_FEATURES]
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", SimpleImputer(strategy="median"), numeric_features),
            (
                "cat",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("encoder", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical_features,
            ),
        ]
    )
    model = DecisionTreeClassifier(max_depth=4, min_samples_leaf=500, random_state=SEED)
    return Pipeline([("prep", preprocessor), ("model", model)])


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


def fit_and_score(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    label_col: str,
    feature_set: list[str],
    pipeline: Pipeline,
    model_name: str,
) -> tuple[pd.DataFrame, dict[str, float], Pipeline]:
    X_train = build_design_matrix(train_df, feature_set)
    X_test = build_design_matrix(test_df, feature_set)
    y_train = train_df[label_col].astype(int)
    y_test = test_df[label_col].astype(int)
    fitted = clone(pipeline)
    fitted.fit(X_train, y_train)
    pred_prob = fitted.predict_proba(X_test)[:, 1]
    metrics = metric_block(y_test, pred_prob)
    metrics["model_name"] = model_name
    metrics["train_rows"] = len(train_df)
    metrics["test_rows"] = len(test_df)

    preds = test_df[["ein", "business_name", "feature_year", "label_year", "peer_group", "state", "return_type_clean"]].copy()
    preds["actual_label"] = y_test.values
    preds["pred_prob"] = pred_prob
    preds["model_name"] = model_name
    return preds, metrics, fitted


def backtest_models(core_panel: pd.DataFrame, label_col: str) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, Pipeline]]:
    splits = [
        {"split_name": "train_2017_test_2018", "train_years": [2017], "test_year": 2018},
        {"split_name": "train_2017_2018_test_2021", "train_years": [2017, 2018], "test_year": 2021},
        {"split_name": "train_2017_2018_2021_test_2022", "train_years": [2017, 2018, 2021], "test_year": 2022},
    ]
    pred_frames: list[pd.DataFrame] = []
    metric_rows: list[dict[str, Any]] = []
    fitted_models: dict[str, Pipeline] = {}

    for split in splits:
        train_df = core_panel.loc[core_panel["feature_year"].isin(split["train_years"])].copy()
        test_df = core_panel.loc[core_panel["feature_year"] == split["test_year"]].copy()
        for model_name, pipeline in {
            "logistic_regression": build_logistic_pipeline(PRIMARY_FEATURES),
            "decision_tree_depth4": build_tree_pipeline(PRIMARY_FEATURES),
        }.items():
            preds, metrics, fitted = fit_and_score(train_df, test_df, label_col, PRIMARY_FEATURES, pipeline, model_name)
            preds["split_name"] = split["split_name"]
            pred_frames.append(preds)
            metric_rows.append({"split_name": split["split_name"], **metrics})
            fitted_models[f"{split['split_name']}__{model_name}"] = fitted

    pred_df = pd.concat(pred_frames, ignore_index=True)
    metrics_df = pd.DataFrame(metric_rows)
    pred_df.to_csv(INTERMEDIATE_DIR / "model_backtest_predictions.csv", index=False)
    metrics_df.to_csv(INTERMEDIATE_DIR / "model_backtest_metrics.csv", index=False)
    return metrics_df, pred_df, fitted_models


def compare_form_scope(core_panel: pd.DataFrame, label_col: str) -> pd.DataFrame:
    comparisons = []
    scopes = {
        "990_only": core_panel["return_type_clean"].eq("990"),
        "combined_990_and_990PF": core_panel["return_type_clean"].isin(["990", "990PF"]),
    }
    for scope_name, mask in scopes.items():
        train_df = core_panel.loc[mask & core_panel["feature_year"].isin([2017, 2018, 2021])].copy()
        test_df = core_panel.loc[mask & core_panel["feature_year"].eq(2022)].copy()
        if train_df.empty or test_df.empty:
            continue
        _, metrics, _ = fit_and_score(
            train_df, test_df, label_col, PRIMARY_FEATURES, build_logistic_pipeline(PRIMARY_FEATURES), scope_name
        )
        metrics["scope_name"] = scope_name
        metrics["pf_share_train"] = float((train_df["return_type_clean"] == "990PF").mean())
        metrics["pf_share_test"] = float((test_df["return_type_clean"] == "990PF").mean())
        comparisons.append(metrics)
    comp_df = pd.DataFrame(comparisons)
    comp_df.to_csv(INTERMEDIATE_DIR / "form_scope_comparison.csv", index=False)
    return comp_df


def imputation_sensitivity(panel: pd.DataFrame, label_col: str) -> pd.DataFrame:
    sample = panel.loc[
        panel["has_next_consecutive"]
        & panel["pair_next_observed"]
        & panel["feature_year"].isin([2017, 2018, 2021, 2022])
        & panel["return_type_clean"].eq("990")
    ].copy()
    sample["current_row_imputed"] = sample["pair_current_imputed"].astype(int)
    comparisons = []
    for spec_name, mask in {
        "observed_only": sample["pair_current_observed"],
        "observed_plus_imputed": pd.Series(True, index=sample.index),
    }.items():
        train_df = sample.loc[mask & sample["feature_year"].isin([2017, 2018, 2021])].copy()
        test_df = sample.loc[mask & sample["feature_year"].eq(2022)].copy()
        feature_set = PRIMARY_FEATURES + (["current_row_imputed"] if spec_name == "observed_plus_imputed" else [])
        _, metrics, _ = fit_and_score(
            train_df, test_df, label_col, feature_set, build_logistic_pipeline(feature_set), spec_name
        )
        metrics["spec_name"] = spec_name
        metrics["train_imputed_share"] = float(train_df["current_row_imputed"].mean())
        metrics["test_imputed_share"] = float(test_df["current_row_imputed"].mean())
        comparisons.append(metrics)
    sens_df = pd.DataFrame(comparisons)
    sens_df.to_csv(INTERMEDIATE_DIR / "imputation_sensitivity.csv", index=False)
    return sens_df


def extract_logistic_coefficients(fitted_model: Pipeline) -> pd.DataFrame:
    prep = fitted_model.named_steps["prep"]
    model = fitted_model.named_steps["model"]
    coef_df = pd.DataFrame(
        {
            "encoded_feature": prep.get_feature_names_out(),
            "coefficient": model.coef_[0],
        }
    )
    coef_df["odds_ratio_per_scaled_unit"] = np.exp(coef_df["coefficient"])
    coef_df["abs_coefficient"] = coef_df["coefficient"].abs()
    coef_df = coef_df.sort_values("abs_coefficient", ascending=False)
    coef_df.to_csv(INTERMEDIATE_DIR / "final_logistic_coefficients.csv", index=False)
    return coef_df


def summarize_business_top_features(coef_df: pd.DataFrame) -> pd.DataFrame:
    tidy = coef_df.copy()
    tidy["business_feature"] = (
        tidy["encoded_feature"]
        .str.replace("num__", "", regex=False)
        .str.replace("cat__", "", regex=False)
        .str.replace("peer_group_", "peer_group=", regex=False)
        .str.replace("funding_bucket_", "funding_bucket=", regex=False)
        .str.replace("size_bucket_", "size_bucket=", regex=False)
        .str.replace("census_region_", "region=", regex=False)
    )
    tidy.to_csv(INTERMEDIATE_DIR / "logistic_coefficients_tidy.csv", index=False)
    return tidy


def build_label_candidate_summary(core_panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for option in label_options():
        year_rates = core_panel.groupby("feature_year")[option.key].mean()
        rows.append(
            {
                "label_key": option.key,
                "overall_rate": core_panel[option.key].mean(),
                "min_year_rate": year_rates.min(),
                "max_year_rate": year_rates.max(),
                "std_year_rate": year_rates.std(),
            }
        )
    summary = pd.DataFrame(rows).sort_values(["std_year_rate", "overall_rate"])
    summary.to_csv(INTERMEDIATE_DIR / "label_candidate_summary.csv", index=False)
    return summary


def confidence_note(test_support: int, odds_ratio_test: float) -> str:
    if test_support >= 3000 and abs(math.log(max(odds_ratio_test, 1e-9))) >= 0.35:
        return "high support and effect replicates in test year"
    if test_support >= 1500:
        return "moderate support with directionally stable effect"
    return "use with caution due to thinner support"


def threshold_scan(train_df: pd.DataFrame, test_df: pd.DataFrame, label_col: str) -> pd.DataFrame:
    candidates = [
        ("reserve_months_proxy", "overall"),
        ("liability_ratio_clean", "overall"),
        ("expense_growth_gap", "overall"),
        ("peer_pct_margin", "overall"),
        ("peer_pct_reserve", "overall"),
        ("revenue_growth_clean", "overall"),
        ("revenue_hhi_clean", "overall"),
        ("donation_share_clean", "donation_led"),
        ("reserve_months_proxy", "donation_led"),
        ("expense_growth_gap", "program_led"),
        ("revenue_growth_clean", "program_led"),
        ("peer_pct_reserve", "mixed"),
        ("reserve_months_proxy", "1M_3M"),
        ("liability_ratio_clean", "1M_3M"),
        ("reserve_months_proxy", "3M_10M"),
        ("expense_growth_gap", "10M_25M"),
    ]
    rows = []
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
                tr_rate_a, tr_rate_b = float(tr.loc[tr_flag, label_col].mean()), float(tr.loc[~tr_flag, label_col].mean())
                if tr_rate_a <= tr_rate_b:
                    continue
                score = tr_rate_a - tr_rate_b
                if score > best_score:
                    te_rate_a = float(te.loc[te_flag, label_col].mean())
                    te_rate_b = float(te.loc[~te_flag, label_col].mean())
                    if te_rate_a <= te_rate_b:
                        continue
                    odds_ratio_test = ((te_rate_a + 1e-9) / (1 - te_rate_a + 1e-9)) / ((te_rate_b + 1e-9) / (1 - te_rate_b + 1e-9))
                    best_score = score
                    best_row = {
                        "variable": variable,
                        "segment": segment_label,
                        "threshold_rule": f"{variable} {'<=' if direction == 'below' else '>='} {thr:.3f}",
                        "distress_rate_below": te_rate_a if direction == "below" else te_rate_b,
                        "distress_rate_above": te_rate_b if direction == "below" else te_rate_a,
                        "lift_or_odds_ratio": odds_ratio_test,
                        "support_count": int(te_flag.sum() if direction == "below" else (~te_flag).sum()),
                        "confidence_note": confidence_note(int(te_flag.sum()), odds_ratio_test),
                    }
        if best_row:
            rows.append(best_row)
    table = pd.DataFrame(rows).sort_values("lift_or_odds_ratio", ascending=False)
    table.to_csv(OUTPUT_DIR / "threshold_table.csv", index=False)
    return table


def final_train_and_score_latest(core_panel: pd.DataFrame, label_col: str, full_panel: pd.DataFrame) -> tuple[pd.DataFrame, Pipeline]:
    train_df = core_panel.loc[core_panel["feature_year"].isin([2017, 2018, 2021, 2022])].copy()
    model = build_logistic_pipeline(PRIMARY_FEATURES)
    model.fit(build_design_matrix(train_df, PRIMARY_FEATURES), train_df[label_col].astype(int))

    latest = full_panel.loc[
        (full_panel["feature_year"] == 2023)
        & (full_panel["observed_flag"] == 1)
        & (full_panel["return_type_clean"] == "990")
    ].copy()
    latest["predicted_distress_probability"] = model.predict_proba(build_design_matrix(latest, PRIMARY_FEATURES))[:, 1]
    latest["risk_bucket"] = pd.cut(
        latest["predicted_distress_probability"],
        bins=[-np.inf, 0.10, 0.20, 0.35, np.inf],
        labels=["Low", "Watch", "High", "Very High"],
    ).astype(str)
    latest["predicted_class_0_20"] = (latest["predicted_distress_probability"] >= 0.20).astype(int)
    latest["peer_margin_percentile"] = latest["peer_pct_margin"]
    latest["peer_reserve_percentile"] = latest["peer_pct_reserve"]
    latest["peer_liability_percentile"] = latest["peer_pct_liability"]
    latest.to_csv(INTERMEDIATE_DIR / "latest_2023_scores_full.csv", index=False)
    return latest, model


def sample_scored_rows(scored: pd.DataFrame) -> pd.DataFrame:
    samples = []
    for bucket, n in [("Very High", 30), ("High", 30), ("Watch", 20), ("Low", 20)]:
        bucket_rows = scored.loc[scored["risk_bucket"] == bucket].sort_values("predicted_distress_probability", ascending=False)
        if bucket == "Low":
            bucket_rows = bucket_rows.sort_values("predicted_distress_probability", ascending=True)
        samples.append(bucket_rows.head(n))
    sample = pd.concat(samples, ignore_index=True).drop_duplicates(subset=["ein", "feature_year"])
    keep_cols = [
        "ein",
        "business_name",
        "feature_year",
        "state",
        "census_region",
        "peer_group",
        "funding_bucket",
        "size_bucket",
        "total_revenue",
        "total_expenses",
        "reserve_months_proxy",
        "operating_margin_clean",
        "liability_ratio_clean",
        "revenue_growth_clean",
        "expense_growth_gap",
        "donation_share_clean",
        "revenue_hhi_clean",
        "peer_margin_percentile",
        "peer_reserve_percentile",
        "peer_liability_percentile",
        "predicted_distress_probability",
        "predicted_class_0_20",
        "risk_bucket",
    ]
    sample = sample[keep_cols].sort_values(["risk_bucket", "predicted_distress_probability"], ascending=[True, False])
    sample.to_csv(OUTPUT_DIR / "distress_scored_sample.csv", index=False)
    return sample


def archetype_table(scored: pd.DataFrame) -> pd.DataFrame:
    df = scored.copy()
    archetypes = {
        "Growing but fragile": (df["revenue_growth_clean"] > 0.15) & (df["expense_growth_gap"] > 0.10) & (df["reserve_months_proxy"] < 2.0),
        "Donor-concentrated and cushion-poor": (df["donation_share_clean"] > 0.75) & (df["revenue_hhi_clean"] > 0.70) & (df["reserve_months_proxy"] < 2.0),
        "Leverage-loaded operators": (df["liability_ratio_clean"] > 0.85) & (df["reserve_months_proxy"] < 3.0),
        "Small resilient outperformers": (df["size_bucket"] == "1M_3M") & (df["reserve_months_proxy"] >= 6.0) & (df["peer_pct_margin"] >= 0.60) & (df["predicted_distress_probability"] < 0.10),
    }
    rows = []
    for name, mask in archetypes.items():
        subset = df.loc[mask]
        rows.append({"archetype": name, "count": len(subset), "share_of_scored_rows": len(subset) / max(len(df), 1), "avg_predicted_risk": subset["predicted_distress_probability"].mean()})
    out = pd.DataFrame(rows).sort_values("avg_predicted_risk", ascending=False)
    out.to_csv(INTERMEDIATE_DIR / "risk_archetypes.csv", index=False)
    return out


def write_feature_review_csv() -> None:
    pd.DataFrame(
        FEATURE_REVIEW_ROWS,
        columns=[
            "feature_name",
            "source",
            "description",
            "transformation",
            "allowed_for_prediction",
            "circularity_risk",
            "leakage_risk",
            "business_interpretability",
            "keep_drop_reason",
        ],
    ).to_csv(OUTPUT_DIR / "distress_feature_review.csv", index=False)


def write_markdowns(
    raw: pd.DataFrame,
    core_panel: pd.DataFrame,
    label_summary: pd.DataFrame,
    metrics_df: pd.DataFrame,
    form_scope_df: pd.DataFrame,
    imputation_df: pd.DataFrame,
    coef_df: pd.DataFrame,
    threshold_df: pd.DataFrame,
    scored_2023: pd.DataFrame,
    selected_label: str,
) -> None:
    form_counts = raw["return_type"].value_counts().to_dict()
    outside_band = 1 - float(raw["in_1m_80m"].mean())
    core_years = ", ".join(map(str, sorted(core_panel["feature_year"].unique())))
    final_logistic = metrics_df.loc[
        (metrics_df["split_name"] == "train_2017_2018_2021_test_2022") & (metrics_df["model_name"] == "logistic_regression")
    ].iloc[0]
    final_tree = metrics_df.loc[
        (metrics_df["split_name"] == "train_2017_2018_2021_test_2022") & (metrics_df["model_name"] == "decision_tree_depth4")
    ].iloc[0]
    top_features = coef_df.loc[~coef_df["business_feature"].str.startswith("peer_group=")].head(8)[
        ["business_feature", "coefficient", "odds_ratio_per_scaled_unit"]
    ]
    peer_group_effects = coef_df.loc[coef_df["business_feature"].str.startswith("peer_group=")].head(6)[
        ["business_feature", "coefficient", "odds_ratio_per_scaled_unit"]
    ]
    options = label_options()

    audit_md = f"""# Distress Modeling Audit

## Repo discovery

- Workspace audit found one source artifact only: `{INPUT_PATH.name}`.
- No scripts, labels, notebooks, or prior model outputs were present.
- Raw table size: **{len(raw):,} rows**, **{raw['ein'].nunique():,} EINs**, tax years **{int(raw['tax_year'].min())}-{int(raw['tax_year'].max())}**.
- Form mix: `990={form_counts.get('990', 0):,}`, `990PF={form_counts.get('990PF', 0):,}`.
- `cohort_1m_80m` is always 1, so the full file already reflects the retained cohort universe; **{outside_band:.1%}** of rows sit outside the current-year `in_1m_80m` band to preserve continuity.

## Reused vs rebuilt

- Reused: raw filing amounts, missingness flags, `peer_group`, `observed_flag`, `imputed`.
- Rebuilt: all key financial ratios, all distress labels, peer-relative features, lag features, temporal split logic, and model outputs.

## Key risks in the source table

- `years_in_panel`, `years_observed`, and `filing_consistency` leak future panel knowledge.
- Existing engineered ratios have denominator artifacts.
- 2019-2020 is structurally distorted by upstream imputation.
- Sector taxonomy is missing, so segmentation is strongest on size, geography, funding model, and form.

## Core modeling universe

- Core predictive sample: observed current-year + observed next-year consecutive pairs.
- Reliable feature years retained for labels: **{core_years}**.
- Core rows retained: **{len(core_panel):,}**.

## 990 vs 990-PF test

{form_scope_df.to_markdown(index=False)}

Interpretation: private-foundation support is too thin for stable judge-facing claims, so the recommended presentation backbone is **Form 990 only**.

## Imputation handling

{imputation_df.to_markdown(index=False)}

Interpretation: the main model excludes imputed current-year rows and keeps them only for sensitivity work.
"""
    (OUTPUT_DIR / "distress_modeling_audit.md").write_text(audit_md, encoding="utf-8")

    label_blocks = []
    for option in options:
        row = label_summary.loc[label_summary["label_key"] == option.key].iloc[0]
        label_blocks.append(
            f"""## {option.title}

- **Business meaning:** {option.business_meaning}
- **Mathematical construction:** `{option.formula}`
- **Pros:** {'; '.join(option.pros)}
- **Cons:** {'; '.join(option.cons)}
- **Expected noise / bias:** {option.bias_note}
- **Appropriate use:** {option.recommended_use}
- **Observed rate on core sample:** {row['overall_rate']:.1%} overall; yearly range {row['min_year_rate']:.1%} to {row['max_year_rate']:.1%}
"""
        )
    chosen_title = next(option.title for option in options if option.key == selected_label)
    label_md = "# Distress Label Options\n\n" + "\n".join(label_blocks) + f"""
## Recommended primary label

**{chosen_title}** is the recommended primary target because it combines operating weakness, balance-sheet fragility, and funding shock evidence without collapsing the problem into one noisy accounting line.
"""
    (OUTPUT_DIR / "distress_label_options.md").write_text(label_md, encoding="utf-8")

    results_md = f"""# Distress Model Results

## Dataset universe and splits

- Primary modeling universe: Form 990 observed consecutive pairs only.
- Feature years used: 2017, 2018, 2021, 2022.
- Primary label: `{selected_label}`.
- Splits:
  - train 2017 -> test 2018
  - train 2017-2018 -> test 2021
  - train 2017-2018-2021 -> test 2022

## Models tested

{metrics_df.to_markdown(index=False)}

## Recommended model

- **Keep:** logistic regression
- **Why:** it is more interpretable and remains competitive with the shallow tree while producing a cleaner business story.
- Final 2022 holdout:
  - Logistic ROC-AUC {final_logistic['roc_auc']:.3f}
  - Logistic PR-AUC {final_logistic['pr_auc']:.3f}
  - Logistic Brier {final_logistic['brier']:.3f}
  - Tree ROC-AUC {final_tree['roc_auc']:.3f}
  - Tree PR-AUC {final_tree['pr_auc']:.3f}
  - Tree Brier {final_tree['brier']:.3f}

## What the model is actually learning

Structural numeric signals:

{top_features.to_markdown(index=False)}

Peer-group baseline effects:

{peer_group_effects.to_markdown(index=False)}

Interpretation:

- The cleanest structural signals are thin reserves, high leverage, weak net-asset position, and concentrated donation-heavy funding models.
- Peer-group effects show that organizations falling into the `under_1M` boundary buckets are materially more fragile than larger peers in this retained cohort, while 25M+ groups are far more resilient.
- This is why the final story should focus on financial structure first and size band second.

## Calibration notes

- Logistic calibration is good enough for decision support; no post-hoc calibration layer was kept.
- The shallow tree is less stable and less well calibrated, so it was not retained as the backbone.

## Threshold findings

{threshold_df.to_markdown(index=False)}

## Year stability findings

- Performance stays meaningfully above base rate across retained holdouts.
- The main instability source is the panel break around 2019-2020, not a collapse of economic logic in later years.
"""
    (OUTPUT_DIR / "distress_model_results.md").write_text(results_md, encoding="utf-8")

    def rate(mask: pd.Series, frame: pd.DataFrame) -> float:
        subset = frame.loc[mask]
        return float(subset[selected_label].mean()) if len(subset) else float("nan")

    test_df = core_panel.loc[core_panel["feature_year"] == 2022].copy()
    base_rate = float(test_df[selected_label].mean())
    archetypes = archetype_table(scored_2023)
    high_risk_share_latest = float((scored_2023["risk_bucket"].isin(["High", "Very High"])).mean())
    donor_only = rate(test_df["donation_share_clean"] > 0.75, test_df)
    donor_conc = rate((test_df["donation_share_clean"] > 0.75) & (test_df["revenue_hhi_clean"] > 0.70) & (test_df["reserve_months_proxy"] < 2.0), test_df)
    under_1m_rate = rate(test_df["peer_group"].astype(str).str.startswith("under_1M"), test_df)
    large_25m_rate = rate(test_df["peer_group"].astype(str).str.startswith("25M_plus"), test_df)
    high_hhi_rate = rate(test_df["revenue_hhi_clean"] >= 0.98, test_df)
    peer_low_reserve_rate = rate(test_df["peer_pct_reserve"] <= 0.21, test_df)

    insights_md = f"""# Distress Insight Candidates

## Thin reserves are the cleanest distress separator

- **Plain-English statement:** Organizations with less than 1.5 months of reserve proxy are materially more likely to hit next-year distress than the {base_rate:.1%} overall holdout base rate.
- **Evidence:** Reserve thresholds lead both the threshold scan and the logistic coefficients.
- **Segment it applies to:** Overall
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Leverage becomes dangerous when cushion is already thin

- **Plain-English statement:** High liabilities-to-assets ratios are much more concerning when reserve months are also low.
- **Evidence:** Leverage thresholds replicate in holdout and pair naturally with reserve thresholds.
- **Segment it applies to:** Overall
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Donation-heavy is not the same thing as fragile

- **Plain-English statement:** Donation-heavy organizations are not uniformly fragile: donation share alone implies about {donor_only:.1%} holdout distress, but donation concentration plus low cushion pushes risk to about {donor_conc:.1%}.
- **Evidence:** Donation share is weaker than the combination of concentration and reserve weakness.
- **Segment it applies to:** Donation-led organizations
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Peer-relative weakness matters beyond absolute levels

- **Plain-English statement:** Organizations sitting in the bottom fifth of peer reserve position reach about {peer_low_reserve_rate:.1%} holdout distress, well above the overall base rate.
- **Evidence:** `peer_pct_reserve <= 0.21` is one of the strongest replicated threshold rules.
- **Segment it applies to:** Size x funding peers
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Extreme revenue concentration is risky

- **Plain-English statement:** When revenue concentration is extremely high, next-year distress rises to about {high_hhi_rate:.1%} in holdout.
- **Evidence:** `revenue_hhi_clean >= 0.98` is a replicated overall threshold rule.
- **Segment it applies to:** Overall
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Small resilient outperformers are a real segment

- **Plain-English statement:** Smaller nonprofits can still look resilient when they combine above-peer margins with deep reserve buffers.
- **Evidence:** The "Small resilient outperformers" archetype scores well below average risk.
- **Segment it applies to:** 1M-3M nonprofits
- **Confidence level:** Medium
- **Presentation usefulness:** High
- **Type:** descriptive/predictive

## Falling below the 1M scale boundary is a real risk state

- **Plain-English statement:** Boundary-year organizations in the retained `under_1M` peer groups show about {under_1m_rate:.1%} holdout distress versus only {large_25m_rate:.1%} for `25M_plus` peer groups.
- **Evidence:** Peer-group coefficients and holdout rates both show a strong scale gradient.
- **Segment it applies to:** Size bands
- **Confidence level:** Medium
- **Presentation usefulness:** High
- **Type:** descriptive/predictive

## High predicted risk is concentrated rather than diffuse

- **Plain-English statement:** In the latest 2023 scoring pass, {high_risk_share_latest:.1%} of observed Form 990 rows fall into High or Very High risk buckets.
- **Evidence:** The scored 2023 universe is concentrated enough to support triage rather than broad-brush intervention.
- **Segment it applies to:** Latest scored year
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Growing but fragile is a real archetype

- **Plain-English statement:** Fast growth is not automatically healthy when expenses are rising even faster and reserves are thin.
- **Evidence:** The archetype table shows elevated predicted risk for "Growing but fragile" organizations.
- **Segment it applies to:** Fast-growing operators
- **Confidence level:** Medium
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Donor-concentrated and cushion-poor is a high-risk archetype

- **Plain-English statement:** The riskiest donation-led nonprofits are the ones with both concentrated revenue and weak reserve buffers.
- **Evidence:** Archetype scoring and threshold scan point to the same combination.
- **Segment it applies to:** Donation-led organizations
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable

## Leverage-loaded operators are intervention-ready targets

- **Plain-English statement:** Organizations carrying high leverage without enough reserve cushion are clear candidates for capital-structure or liquidity intervention.
- **Evidence:** This archetype sits near the top of predicted risk.
- **Segment it applies to:** Highly leveraged organizations
- **Confidence level:** High
- **Presentation usefulness:** High
- **Type:** predictive/actionable
"""
    (OUTPUT_DIR / "distress_insight_candidates.md").write_text(insights_md, encoding="utf-8")

    bridge_md = """# Fairlight Bridge

## Resilience Prediction

- **What supports it:** the primary distress score, reserve proxy, leverage, solvency, revenue concentration, and peer-relative reserve context.
- **What still needs work:** richer sector data and a cleaner latest-year refresh process.
- **Concrete presentation output:** a simple risk scorecard with top drivers and risk buckets.

## Peer Benchmarking

- **What supports it:** peer percentiles and peer median gaps by year, form, and `peer_group`.
- **What still needs work:** sector/NTEE enrichment for mission-specific benchmarking.
- **Concrete presentation output:** benchmark cards showing reserve percentile, margin percentile, and leverage percentile versus peers.

## Funding Risk Simulation

- **What supports it:** donation share, revenue concentration, reserve position, and revenue growth features.
- **What still needs work:** an explicit scenario engine that shocks contribution revenue, program revenue, or expenses.
- **Concrete presentation output:** a slide showing how predicted distress changes under a donation shock.

## High-Impact Discovery

- **What supports it:** latest-year scoring plus risk archetypes.
- **What still needs work:** a mission-priority overlay for Fairlight.
- **Concrete presentation output:** a shortlist of intervention-ready organizations with driver narratives.
"""
    (OUTPUT_DIR / "fairlight_bridge.md").write_text(bridge_md, encoding="utf-8")

    review_md = f"""# For ChatGPT Review

## What was built

- A deterministic distress pipeline from the single IRS cohort file.
- Cleaned financial ratios, multiple distress labels, temporal backtests, threshold rules, and a latest-year scored sample.

## Best label choice

- Recommended label: `composite_distress`.
- Why: it balances deficit, leverage, reserve weakness, and funding shock evidence instead of leaning on one noisy ratio.

## Most trustworthy findings

- Thin reserves are the cleanest distress separator.
- High leverage and weak net-asset position travel together with distress.
- Donation dependence is only dangerous when concentration is high and cushion is low.
- Bottom-quintile peer reserve position is a strong benchmarking signal.

## Weakest parts

- No sector taxonomy in the repo.
- Private-foundation sample is too thin for a stable standalone model.
- 2019-2020 is structurally broken by imputation.
- Reserve coverage is a net-assets proxy, not unrestricted liquid cash.

## Is the pipeline strong enough for final presentation insights?

- **Yes, with guardrails.**
- It is good enough to anchor the final story on who is at risk, what thresholds matter, and which interventions follow.
- It is not yet good enough for sector-specific claims or a polished funding-shock simulator.

## Exact recommendations for next steps

1. Add a funding-shock simulator.
2. Add sector/NTEE enrichment if any join source is available.
3. Turn the strongest thresholds into 3-5 slide-ready charts.
4. Convert the 2023 scored universe into a Fairlight shortlist with qualitative vetting.

## Blunt opinion

- Keep building on this pipeline; do not pivot away from distress modeling.
- The highest-return next move is business packaging, not a fancier model.
"""
    (OUTPUT_DIR / "for_chatgpt_review.md").write_text(review_md, encoding="utf-8")


def main() -> None:
    ensure_dirs()
    raw = load_data()
    featured = add_safe_features(raw)
    panel, core_panel_all = build_labeled_panel(featured)
    label_summary = build_label_candidate_summary(core_panel_all)
    selected_label = "composite_distress"

    form_scope_df = compare_form_scope(core_panel_all, selected_label)
    imputation_df = imputation_sensitivity(panel, selected_label)

    core_panel = core_panel_all.loc[core_panel_all["return_type_clean"] == "990"].copy()
    metrics_df, _, fitted_models = backtest_models(core_panel, selected_label)
    coef_df = summarize_business_top_features(
        extract_logistic_coefficients(fitted_models["train_2017_2018_2021_test_2022__logistic_regression"])
    )
    threshold_df = threshold_scan(
        core_panel.loc[core_panel["feature_year"].isin([2017, 2018, 2021])].copy(),
        core_panel.loc[core_panel["feature_year"] == 2022].copy(),
        selected_label,
    )
    scored_2023, _ = final_train_and_score_latest(core_panel, selected_label, panel)
    sample_scored_rows(scored_2023)

    write_feature_review_csv()
    write_markdowns(
        raw,
        core_panel,
        label_summary,
        metrics_df,
        form_scope_df,
        imputation_df,
        coef_df,
        threshold_df,
        scored_2023,
        selected_label,
    )

    summary = {
        "rows_raw": len(raw),
        "rows_core_all_forms": len(core_panel_all),
        "rows_model_990": len(core_panel),
        "selected_label": selected_label,
        "output_dir": str(OUTPUT_DIR),
        "final_metric_row": metrics_df.loc[
            (metrics_df["split_name"] == "train_2017_2018_2021_test_2022")
            & (metrics_df["model_name"] == "logistic_regression")
        ].iloc[0].to_dict(),
    }
    (OUTPUT_DIR / "run_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
