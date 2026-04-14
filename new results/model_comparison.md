# Model Comparison

## 2022 holdout scorecard

| experiment_name         |   roc_auc |   pr_auc |    brier |   precision_at_0_20 |   precision_at_top_10pct |
|:------------------------|----------:|---------:|---------:|--------------------:|-------------------------:|
| upgraded_logistic       |  0.809803 | 0.65814  | 0.12106  |            0.49203  |                 0.82732  |
| lightgbm                |  0.863727 | 0.725519 | 0.10737  |            0.530807 |                 0.866716 |
| catboost                |  0.861569 | 0.721598 | 0.108036 |            0.532034 |                 0.866716 |
| catboost_lightgbm_blend |  0.863713 | 0.725704 | 0.107357 |            0.531627 |                 0.868189 |

## Calibration snapshot

| model_name              |     ece_10 |   max_bin_gap |
|:------------------------|-----------:|--------------:|
| upgraded_logistic       | 0.0196158  |     0.0786112 |
| lightgbm                | 0.00535493 |     0.0237019 |
| catboost                | 0.00811766 |     0.0324982 |
| catboost_lightgbm_blend | 0.00676887 |     0.0298496 |

## Interpretability

- `upgraded_logistic`: cleanest to explain, easiest to translate into thresholds, and easiest to defend in a hackathon room.
- `catboost_lightgbm_blend`: materially stronger on pure metrics, but not naturally threshold-first and much harder to narrate without a model-mechanics detour.

## Recommendation

- Retain `upgraded_logistic` as the presentation backbone.
- Keep `catboost_lightgbm_blend` as an appendix or credibility benchmark only.
- Reason: the advanced challenger is clearly stronger (0.864 ROC-AUC vs 0.810 for logistic in 2022), but the hackathon value of switching is smaller than the story cost.

## What the retained logistic is learning

| business_feature       |   coefficient |   odds_ratio_per_scaled_unit |
|:-----------------------|--------------:|-----------------------------:|
| peer_coverage_z_obs    |     -1.85355  |                     0.15668  |
| peer_pct_coverage_obs  |      1.35628  |                     3.88172  |
| peer_pct_margin_obs    |     -0.812485 |                     0.443754 |
| peer_margin_z_obs      |      0.596396 |                     1.81556  |
| liability_ratio_clean  |      0.595809 |                     1.8145   |
| net_asset_ratio_clean  |     -0.590241 |                     0.554194 |
| donation_share_clean   |      0.544693 |                     1.72408  |
| peer_pct_liability_obs |     -0.290973 |                     0.747536 |
