# Feature Change Audit

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
  - ROC-AUC 0.810 with direct features
  - ROC-AUC 0.810 without direct features

## Macro feature decision

- Tested macro pack: `macro_donation_unrate`, `macro_concentration_unrate`, `macro_expensegap_inflation`, `macro_leverage_rates`
- Decision: reject
- Why: the pack degraded the retained logistic on every holdout and added more year-noise risk than insight value.

## Final retained feature set

`liability_ratio_clean, net_asset_ratio_clean, revenue_growth_clean, expense_growth_gap, asset_growth_clean, donation_share_clean, revenue_hhi_clean, salary_share_clean, org_age_clean, peer_group, peer_pct_margin_obs, peer_pct_coverage_obs, peer_pct_liability_obs, peer_pct_revenue_growth_obs, peer_margin_z_obs, peer_coverage_z_obs`
