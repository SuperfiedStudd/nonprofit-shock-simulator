# Distress Modeling Audit

## Repo discovery

- Workspace audit found one source artifact only: `irs990_cohort_features.csv`.
- No scripts, labels, notebooks, or prior model outputs were present.
- Raw table size: **540,860 rows**, **122,392 EINs**, tax years **2017-2024**.
- Form mix: `990=540,404`, `990PF=456`.
- `cohort_1m_80m` is always 1, so the full file already reflects the retained cohort universe; **15.8%** of rows sit outside the current-year `in_1m_80m` band to preserve continuity.

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
- Reliable feature years retained for labels: **2017, 2018, 2021, 2022**.
- Core rows retained: **145,852**.

## 990 vs 990-PF test

|   roc_auc |   pr_auc |    brier |   prevalence |   precision_at_0_20 |   predicted_positive_at_0_20 |   precision_at_top_5pct |   precision_at_top_10pct |   precision_at_top_20pct | model_name             |   train_rows |   test_rows | scope_name             |   pf_share_train |   pf_share_test |
|----------:|---------:|---------:|-------------:|--------------------:|-----------------------------:|------------------------:|-------------------------:|-------------------------:|:-----------------------|-------------:|------------:|:-----------------------|-----------------:|----------------:|
|  0.720874 | 0.474473 | 0.13139  |     0.192701 |            0.350898 |                     0.305384 |                0.752577 |                 0.603829 |                 0.430596 | 990_only               |       118696 |       27156 | 990_only               |      0           |     0           |
|  0.720941 | 0.474656 | 0.131308 |     0.192605 |            0.350645 |                     0.305335 |                0.752024 |                 0.603753 |                 0.430648 | combined_990_and_990PF |       118745 |       27180 | combined_990_and_990PF |      0.000412649 |     0.000883002 |

Interpretation: private-foundation support is too thin for stable judge-facing claims, so the recommended presentation backbone is **Form 990 only**.

## Imputation handling

|   roc_auc |   pr_auc |    brier |   prevalence |   precision_at_0_20 |   predicted_positive_at_0_20 |   precision_at_top_5pct |   precision_at_top_10pct |   precision_at_top_20pct | model_name            |   train_rows |   test_rows | spec_name             |   train_imputed_share |   test_imputed_share |
|----------:|---------:|---------:|-------------:|--------------------:|-----------------------------:|------------------------:|-------------------------:|-------------------------:|:----------------------|-------------:|------------:|:----------------------|----------------------:|---------------------:|
|  0.720874 | 0.474473 | 0.13139  |     0.192701 |            0.350898 |                     0.305384 |                0.752577 |                 0.603829 |                 0.430596 | observed_only         |       118696 |       27156 | observed_only         |              0        |             0        |
|  0.740765 | 0.515276 | 0.130294 |     0.19892  |            0.353164 |                     0.356393 |                0.800294 |                 0.650798 |                 0.467485 | observed_plus_imputed |       148950 |       40750 | observed_plus_imputed |              0.203115 |             0.333595 |

Interpretation: the main model excludes imputed current-year rows and keeps them only for sensitivity work.
