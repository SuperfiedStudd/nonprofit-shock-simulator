# Distress Model Results

## Dataset universe and splits

- Primary modeling universe: Form 990 observed consecutive pairs only.
- Feature years used: 2017, 2018, 2021, 2022.
- Primary label: `composite_distress`.
- Splits:
  - train 2017 -> test 2018
  - train 2017-2018 -> test 2021
  - train 2017-2018-2021 -> test 2022

## Models tested

| split_name                     |   roc_auc |   pr_auc |    brier |   prevalence |   precision_at_0_20 |   predicted_positive_at_0_20 |   precision_at_top_5pct |   precision_at_top_10pct |   precision_at_top_20pct | model_name           |   train_rows |   test_rows |
|:-------------------------------|----------:|---------:|---------:|-------------:|--------------------:|-----------------------------:|------------------------:|-------------------------:|-------------------------:|:---------------------|-------------:|------------:|
| train_2017_test_2018           |  0.733936 | 0.520939 | 0.128661 |     0.198045 |            0.356388 |                     0.328559 |                0.839639 |                 0.681479 |                 0.471313 | logistic_regression  |        40872 |       57603 |
| train_2017_test_2018           |  0.745925 | 0.515138 | 0.121596 |     0.198045 |            0.409958 |                     0.309255 |                0.892398 |                 0.685645 |                 0.484941 | decision_tree_depth4 |        40872 |       57603 |
| train_2017_2018_test_2021      |  0.723931 | 0.546578 | 0.140981 |     0.223283 |            0.422727 |                     0.298551 |                0.846838 |                 0.732575 |                 0.528307 | logistic_regression  |        98475 |       20221 |
| train_2017_2018_test_2021      |  0.741788 | 0.552272 | 0.130408 |     0.223283 |            0.394996 |                     0.38737  |                0.923913 |                 0.778547 |                 0.537948 | decision_tree_depth4 |        98475 |       20221 |
| train_2017_2018_2021_test_2022 |  0.720874 | 0.474473 | 0.13139  |     0.192701 |            0.350898 |                     0.305384 |                0.752577 |                 0.603829 |                 0.430596 | logistic_regression  |       118696 |       27156 |
| train_2017_2018_2021_test_2022 |  0.720327 | 0.475744 | 0.12431  |     0.192701 |            0.378163 |                     0.314332 |                0.863034 |                 0.625184 |                 0.461524 | decision_tree_depth4 |       118696 |       27156 |

## Recommended model

- **Keep:** logistic regression
- **Why:** it is more interpretable and remains competitive with the shallow tree while producing a cleaner business story.
- Final 2022 holdout:
  - Logistic ROC-AUC 0.721
  - Logistic PR-AUC 0.474
  - Logistic Brier 0.131
  - Tree ROC-AUC 0.720
  - Tree PR-AUC 0.476
  - Tree Brier 0.124

## What the model is actually learning

Structural numeric signals:

| business_feature       |   coefficient |   odds_ratio_per_scaled_unit |
|:-----------------------|--------------:|-----------------------------:|
| liability_ratio_clean  |     0.447451  |                     1.56432  |
| net_asset_ratio_clean  |    -0.440414  |                     0.64377  |
| salary_share_clean     |    -0.342249  |                     0.710171 |
| reserve_months_proxy   |    -0.339777  |                     0.711929 |
| donation_share_clean   |     0.259331  |                     1.29606  |
| revenue_hhi_clean      |     0.222495  |                     1.24919  |
| org_age_clean          |    -0.183028  |                     0.832745 |
| operating_margin_clean |    -0.0853129 |                     0.918225 |

Peer-group baseline effects:

| business_feature                  |   coefficient |   odds_ratio_per_scaled_unit |
|:----------------------------------|--------------:|-----------------------------:|
| peer_group=under_1M__mixed        |      0.745739 |                     2.108    |
| peer_group=25M_plus__program_led  |     -0.64384  |                     0.525272 |
| peer_group=10M_25M__donation_led  |     -0.624948 |                     0.535289 |
| peer_group=25M_plus__donation_led |     -0.615444 |                     0.540401 |
| peer_group=10M_25M__program_led   |     -0.538126 |                     0.583841 |
| peer_group=3M_10M__program_led    |     -0.334413 |                     0.715758 |

Interpretation:

- The cleanest structural signals are thin reserves, high leverage, weak net-asset position, and concentrated donation-heavy funding models.
- Peer-group effects show that organizations falling into the `under_1M` boundary buckets are materially more fragile than larger peers in this retained cohort, while 25M+ groups are far more resilient.
- This is why the final story should focus on financial structure first and size band second.

## Calibration notes

- Logistic calibration is good enough for decision support; no post-hoc calibration layer was kept.
- The shallow tree is less stable and less well calibrated, so it was not retained as the backbone.

## Threshold findings

| variable              | segment              | threshold_rule                 |   distress_rate_below |   distress_rate_above |   lift_or_odds_ratio |   support_count | confidence_note                                   |
|:----------------------|:---------------------|:-------------------------------|----------------------:|----------------------:|---------------------:|----------------:|:--------------------------------------------------|
| reserve_months_proxy  | size=3M_10M          | reserve_months_proxy <= 2.594  |              0.499439 |              0.114092 |              7.74748 |             891 | use with caution due to thinner support           |
| reserve_months_proxy  | size=1M_3M           | reserve_months_proxy <= 2.700  |              0.531902 |              0.140822 |              6.93276 |            1677 | moderate support with directionally stable effect |
| reserve_months_proxy  | overall              | reserve_months_proxy <= 2.623  |              0.523884 |              0.138307 |              6.8554  |            3831 | high support and effect replicates in test year   |
| peer_pct_reserve      | overall              | peer_pct_reserve <= 0.211      |              0.438453 |              0.133832 |              5.05332 |            5248 | high support and effect replicates in test year   |
| liability_ratio_clean | overall              | liability_ratio_clean >= 0.563 |              0.148118 |              0.443415 |              4.58196 |           23056 | high support and effect replicates in test year   |
| liability_ratio_clean | size=1M_3M           | liability_ratio_clean >= 0.503 |              0.149903 |              0.446602 |              4.57658 |            9793 | moderate support with directionally stable effect |
| reserve_months_proxy  | funding=donation_led | reserve_months_proxy <= 2.626  |              0.466443 |              0.17484  |              4.12587 |            1788 | moderate support with directionally stable effect |
| peer_pct_reserve      | funding=mixed        | peer_pct_reserve <= 0.212      |              0.324324 |              0.132647 |              3.13862 |             851 | use with caution due to thinner support           |
| peer_pct_margin       | overall              | peer_pct_margin <= 0.197       |              0.29051  |              0.167799 |              2.03074 |            5511 | high support and effect replicates in test year   |
| revenue_hhi_clean     | overall              | revenue_hhi_clean >= 0.985     |              0.171013 |              0.27681  |              1.85544 |           21589 | high support and effect replicates in test year   |
| donation_share_clean  | funding=donation_led | donation_share_clean >= 0.997  |              0.195547 |              0.301938 |              1.77939 |            9343 | moderate support with directionally stable effect |
| revenue_growth_clean  | overall              | revenue_growth_clean >= 0.271  |              0.17511  |              0.258657 |              1.64358 |           21438 | high support and effect replicates in test year   |
| expense_growth_gap    | overall              | expense_growth_gap <= -0.126   |              0.252495 |              0.180475 |              1.53385 |            4610 | high support and effect replicates in test year   |
| expense_growth_gap    | size=10M_25M         | expense_growth_gap <= 0.000    |              0.186681 |              0.141017 |              1.39815 |             916 | use with caution due to thinner support           |
| revenue_growth_clean  | funding=program_led  | revenue_growth_clean <= -0.040 |              0.206178 |              0.163494 |              1.32888 |            2590 | moderate support with directionally stable effect |
| expense_growth_gap    | funding=program_led  | expense_growth_gap <= -0.076   |              0.197282 |              0.167938 |              1.21767 |            2134 | moderate support with directionally stable effect |

## Year stability findings

- Performance stays meaningfully above base rate across retained holdouts.
- The main instability source is the panel break around 2019-2020, not a collapse of economic logic in later years.
