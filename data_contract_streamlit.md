# Data Contract For The Streamlit Demo

## Resolution order

The app loads files in this priority order so it stays aligned with the upgraded rerun story first and only falls back when required.

## Run summary

Resolution order:

1. `new results/run_summary.json`
2. `distress_outputs/run_summary.json`

Required fields:

- `selected_label`
- `selected_features`
- `final_model`

## Peer benchmark universe

Resolution order:

1. `new results/peer_benchmark_cards.csv`
2. `distress_outputs/fairlight_package/peer_benchmark_cards.csv`
3. `distress_outputs/fairlight_package/tables/peer_benchmark_cards.csv`

Required columns:

- `ein`
- `business_name`
- `feature_year`
- `state`
- `peer_group`
- `funding_bucket`
- `size_bucket`
- `sector_group`
- `predicted_distress_probability`
- `risk_bucket`
- `peer_reserve_percentile`
- `peer_margin_percentile`
- `peer_liability_percentile`
- `concentration_percentile`
- `overall_risk_percentile`
- `overall_risk_rank_bucket`
- `reserve_gap_vs_peer_median`
- `margin_gap_vs_peer_median`
- `leverage_gap_vs_peer_median`
- `concentration_gap_vs_peer_median`
- `key_gaps`
- `strength_flags`

## Latest-year structural fields

Resolution order:

1. `distress_outputs/intermediate/latest_2023_scores_full.csv`

Used to enrich the lookup, benchmarking, and portfolio tabs with raw financial context.

Required columns:

- `ein`
- `tax_year`
- `total_revenue`
- `total_expenses`
- `contributions_grants`
- `program_service_revenue`
- `net_assets_eoy`
- `total_assets_eoy`
- `total_liabilities_eoy`
- `operating_margin_clean`
- `reserve_months_proxy`
- `liability_ratio_clean`
- `net_asset_ratio_clean`
- `revenue_growth_clean`
- `expense_growth_gap`
- `asset_growth_clean`
- `donation_share_clean`
- `program_share_clean`
- `fundraising_share_clean`
- `grants_share_clean`
- `revenue_hhi_clean`

Fallback logic:

- If this file is missing, the app still runs from peer benchmark cards alone.
- The lookup narrative becomes thinner.
- The portfolio tab still renders, but selected-row detail and rationale become thinner.

## Org-level shock results

Resolution order:

1. `streamlit_demo_data/upgraded_shock_simulation_results.csv`
2. `new results/upgraded_shock_simulation_results.csv`
3. `distress_outputs/fairlight_package/shock_simulation_results.csv`

Required columns:

- `ein`
- `scenario_name`
- `scenario_family`
- `shock_size`
- `baseline_risk`
- `shocked_risk`
- `absolute_increase`
- `relative_increase`
- `baseline_bucket`
- `shocked_bucket`
- `bucket_shift`
- `risk_bucket_transition`
- `main_drivers`

Useful optional columns:

- `feature_year`
- `state`
- `peer_group`
- `funding_bucket`
- `size_bucket`
- `sector_group`
- `shock_exposure_revenue_loss`
- `shock_exposure_expense_increase`
- `shocked_total_revenue`
- `shocked_total_expenses`
- `shocked_net_assets_eoy`
- `operating_margin_clean`
- `reserve_months_proxy`
- `liability_ratio_clean`
- `net_asset_ratio_clean`
- `revenue_growth_clean`
- `expense_growth_gap`
- `donation_share_clean`
- `revenue_hhi_clean`

Fallback logic:

- If the exact upgraded org-level file exists, the simulator uses it.
- If only the packaged older org-level file exists, the simulator still renders but labels itself as a fallback.
- If no org-level rows exist, the simulator and portfolio tab fall back to worst-case fields from shortlists or summary-only messaging where possible.

## Shock summary

Resolution order:

1. `new results/shock_scenario_summary.csv`
2. `streamlit_demo_data/upgraded_shock_scenario_summary.csv`
3. `distress_outputs/fairlight_package/tables/shock_scenario_summary.csv`

Required columns:

- `scenario_name`
- `org_count`
- `avg_baseline_risk`
- `avg_shocked_risk`
- `avg_absolute_increase`
- `median_absolute_increase`
- `bucket_upshift_share`

## Shortlists

Resolution order:

1. `new results/fairlight_shortlists_table.csv`
2. `distress_outputs/fairlight_package/tables/fairlight_shortlists_table.csv`

Required columns:

- `ein`
- `business_name`
- `peer_group`
- `predicted_distress_probability`
- `shortlist_category`
- `plain_english_recommendation`

Useful optional columns:

- `feature_year`
- `state`
- `funding_bucket`
- `size_bucket`
- `sector_group`
- `worst_case_scenario`
- `worst_case_risk`
- `worst_case_delta`
- `worst_case_relative_increase`
- `worst_case_bucket_transition`
- `worst_case_drivers`
- `bucket_shift`
- `benchmark_position_summary`
- `shock_sensitivity_summary`
- `shortlist_score`

Fallback logic:

- If shortlist rows exist, the `Portfolio Rankings` tab can rank directly inside shortlist classes.
- If shortlist fields are missing, the app still renders baseline, peer, and scenario rankings without shortlist-specific modes.

## Threshold evidence

Resolution order:

1. `new results/threshold_scan.csv`
2. `distress_outputs/fairlight_package/tables/threshold_evidence_table.csv`
3. `distress_outputs/threshold_table.csv`

Required columns:

- `variable`
- `segment`
- `threshold_rule`
- `lift_or_odds_ratio`
- `support_count`

Accepted naming patterns:

- upgraded style: `distress_rate_a`, `distress_rate_b`
- packaged style: `distress_rate_below`, `distress_rate_above`

## Insight evidence

Resolution order:

1. `new results/insight_evidence_table.csv`

Required columns:

- `insight_key`
- `plain_english_statement`
- `evidence`
- `value`
- `confidence`

## Portfolio Rankings derived layer

The `Portfolio Rankings` tab does not introduce a new model. It builds a cached merged table from the existing downstream outputs above.

Primary inputs:

- peer benchmark universe
- latest-year structural fields
- shortlist rows
- org-level shock results

Derived fields used by the tab:

- `peer_strength_score`
- `peer_weakness_score`
- `top_scenario`
- `worst_case_risk`
- `worst_case_delta`
- `worst_case_relative_increase`
- `worst_case_bucket_shift`
- `worst_case_main_drivers`
- `donation_worst_delta`
- `donation_worst_bucket_jump`
- `expense_worst_delta`
- `expense_worst_bucket_jump`
- `observed_data_flag`
- scenario-view columns for the currently selected scenario:
  - `scenario_name_view`
  - `scenario_absolute_delta`
  - `scenario_relative_delta`
  - `scenario_bucket_jump`
  - `scenario_shocked_risk`
  - `scenario_drivers`

Ranking-mode dependencies:

- baseline risk modes require `predicted_distress_probability`
- reserve and leverage modes require peer percentile columns
- concentration mode requires `concentration_percentile`
- shortlist modes require `shortlist_category` and preferably `shortlist_score`
- scenario modes require org-level shock rows or fallback worst-case fields

Portfolio fallback logic:

- If a required column for a ranking mode is unavailable, the tab shows a note instead of crashing.
- If scenario rows are partially missing, the tab keeps baseline and peer rankings available and leaves scenario-specific cells blank.
- If shortlist narrative text is missing, the rationale column falls back to benchmark or shock summary text.
- If observed-row support cannot be inferred, the observed-only checkbox is shown as unavailable rather than filtering incorrectly.
