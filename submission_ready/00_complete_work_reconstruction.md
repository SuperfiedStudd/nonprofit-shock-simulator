# Complete Work Reconstruction

This document reconstructs what happened in `E:\distressed` from the files that exist here now: script contents, output artifacts, filenames, and filesystem timestamps. There is no saved terminal transcript in this folder, so this is a best-evidence reconstruction rather than a literal command-by-command shell history.

## Executive summary

The work happened in two major passes:

1. A nonprofit distress modeling backbone was built from a single IRS cohort CSV.
2. That backbone was turned into a Fairlight-oriented solution package with benchmarking, shock simulation, shortlists, charts, and presentation materials.

By the end of the work, the folder contained:

- a complete modeling pipeline script
- a complete Fairlight packaging script
- scored outputs, audits, and threshold tables
- presentation-ready charts and summary documents
- a final deck brief for ChatGPT / slide production

## Starting point

The visible starting artifact is:

- `irs990_cohort_features.csv` at `2026-04-13 17:44:56`

That file appears to be the single source dataset used to build everything else.

## High-level timeline

| Time on 2026-04-13 | What appears to have happened |
|---|---|
| 17:44:56 | Source cohort CSV is present in the workspace. |
| 21:17:26 | `scripts/build_distress_pipeline.py` was saved. |
| 21:17:44 to 21:18:11 | The distress pipeline ran and generated intermediate files, model outputs, Markdown writeups, a scored sample, and `run_summary.json`. |
| 21:27:17 | `presentation_outline.md` was added as a presentation planning document. |
| 21:39:55 | `fairlight_package/irs_ntee_lookup.csv` appeared, showing that sector enrichment / packaging work had started. |
| 21:44:55 | `scripts/build_fairlight_package.py` was saved in its current form. |
| 21:45:09 to 21:45:33 | The Fairlight package run produced benchmark cards, shock simulation outputs, summary tables, charts, Markdown summaries, and `package_summary.json`. |
| 22:09:32 | `final_presentation_prompt_for_chatgpt.md` was added as a final deck-generation brief. |

## Important reconstruction note

The Fairlight package timestamps suggest at least one edit-and-rerun cycle. Some package outputs were written before the current `build_fairlight_package.py` file's last saved timestamp. The safest interpretation is:

- the package script existed and was run
- it was then refined and saved again
- the final artifacts in the folder represent the completed package state

## What the first major script did

The first backbone script is `scripts/build_distress_pipeline.py`.

Its `main()` function shows the intended workflow:

1. load the IRS cohort data
2. add cleaned and clipped financial features
3. build a labeled observed-pairs panel
4. compare multiple label options
5. choose `composite_distress`
6. test form scope and imputation sensitivity
7. restrict the primary model to Form 990 observations
8. backtest logistic regression and a shallow decision tree on time-based holdouts
9. extract interpretable coefficients
10. scan threshold rules
11. train the final retained model and score the latest year
12. write CSV outputs, Markdown audits, business summaries, and a run summary JSON

## What was built in the first pass

### Data and panel outputs

These files indicate the panel-building and validation work:

- `intermediate/pair_coverage_by_year.csv`
- `intermediate/modeling_panel_observed_pairs.csv`
- `intermediate/label_candidate_summary.csv`
- `intermediate/form_scope_comparison.csv`
- `intermediate/imputation_sensitivity.csv`

### Model outputs

These files show the actual model evaluation and interpretation pass:

- `intermediate/model_backtest_metrics.csv`
- `intermediate/model_backtest_predictions.csv`
- `intermediate/final_logistic_coefficients.csv`
- `intermediate/logistic_coefficients_tidy.csv`
- `threshold_table.csv`
- `intermediate/latest_2023_scores_full.csv`
- `distress_scored_sample.csv`
- `intermediate/risk_archetypes.csv`

### Documentation outputs

These files show that the pipeline was not just run technically; it was translated into a business-facing narrative:

- `distress_feature_review.csv`
- `distress_modeling_audit.md`
- `distress_label_options.md`
- `distress_model_results.md`
- `distress_insight_candidates.md`
- `fairlight_bridge.md`
- `for_chatgpt_review.md`
- `run_summary.json`

## Key results from the first pass

From `run_summary.json` and `distress_model_results.md`, the main accepted backbone appears to be:

- raw rows: 540,860
- core observed-pair rows across forms: 145,925
- primary Form 990 model rows: 145,852
- selected label: `composite_distress`
- retained model: logistic regression

The accepted 2022 holdout row in the summary is:

- ROC-AUC: 0.7209
- PR-AUC: 0.4745
- Brier: 0.1314
- prevalence: 19.27%
- precision at top 5%: 75.26%
- precision at top 10%: 60.38%
- precision at top 20%: 43.06%

The strongest business findings written into the outputs were:

- thin reserves are the clearest separator
- leverage and weak net assets are major risk signals
- peer-relative reserve weakness matters almost as much as absolute reserve weakness
- donation dependence is most dangerous when concentration is high and cushion is low

## What happened after the first pass

At `21:27:17`, `presentation_outline.md` was created. That file translates the backbone into an 8-slide story:

- problem framing
- practical distress definition
- model credibility
- threshold evidence
- funding fragility nuance
- peer benchmarking
- intervention archetypes
- Fairlight productization path

This appears to be the bridge between "the model works" and "the presentation can now be built."

## What the second major script did

The second backbone script is `scripts/build_fairlight_package.py`.

Its `main()` function shows the packaging workflow:

1. load the latest scored universe and modeling panel
2. retrain the retained model used for downstream scenario work
3. attempt IRS NTEE enrichment for sector context
4. build peer benchmark cards
5. summarize peer segments
6. run deterministic shock simulations
7. summarize scenarios, peer-group shock sensitivity, and shock drivers
8. build Fairlight shortlists
9. write method notes, audits, charts, evidence files, and a final package summary JSON

## What was built in the second pass

### Sector enrichment

The package attempted an official IRS Business Master File join and cached:

- `fairlight_package/irs_ntee_lookup.csv`

It also wrote:

- `fairlight_package/sector_enrichment_audit.md`

This is the evidence that sector context was added instead of left as a future idea.

### Benchmarking and stress testing

The core Fairlight outputs are:

- `fairlight_package/peer_benchmark_cards.csv`
- `fairlight_package/shock_simulation_results.csv`
- `fairlight_package/tables/peer_segment_summary.csv`
- `fairlight_package/tables/shock_scenario_summary.csv`
- `fairlight_package/tables/shock_peer_group_summary.csv`
- `fairlight_package/tables/shock_driver_frequency.csv`
- `fairlight_package/tables/fairlight_shortlists_table.csv`
- `fairlight_package/tables/shortlist_overview_table.csv`
- `fairlight_package/tables/model_backtest_scorecard.csv`
- `fairlight_package/tables/threshold_evidence_table.csv`

### Narrative and packaging documents

The packaging pass also wrote:

- `fairlight_package/shock_simulator_method.md`
- `fairlight_package/peer_segment_summary.md`
- `fairlight_package/shock_segment_summary.md`
- `fairlight_package/fairlight_shortlists.md`
- `fairlight_package/presentation_evidence.md`
- `fairlight_package/slide_chart_specs.md`
- `fairlight_package/for_chatgpt_final_review.md`
- `fairlight_package/package_summary.json`

### Chart assets

Five final charts and their supporting CSVs were created:

- reserve buffer chart
- leverage bucket chart
- peer reserve decile chart
- concentration and low-cushion interaction heatmap
- shock delta by peer group chart

These live under:

- `fairlight_package/charts`
- `fairlight_package/chart_data`

## Key results from the second pass

From `package_summary.json`, the finished package reports:

- benchmark cards: 42,751
- org-scenario shock rows: 384,759
- shortlist rows: 30
- broad sector enrichment coverage: 71.16%

The top average shock scenario was:

- `expense_inflation_10`
- average absolute risk increase: 0.01818
- bucket upshift share: 10.30%

From the review files, the intended final business story became:

1. build a transparent distress backbone
2. convert it into thresholds
3. turn thresholds into peer benchmarking and stress testing
4. create intervention-ready shortlists
5. present the whole system as a resilience decision system, not just a model

## Final-stage presentation artifacts

Two late-stage artifacts indicate the work moved fully into submission / deck preparation mode:

- `presentation_outline.md`
- `fairlight_package/final_presentation_prompt_for_chatgpt.md`

The final prompt is especially important because it is effectively the handoff brief for generating the judge-facing presentation. It locks:

- audience
- tone
- narrative arc
- exact numbers to cite
- chart priorities
- slide-by-slide structure
- constraints on how to frame the scenario engine and the model

## What was likely done manually vs scripted

### Clearly scripted

- core data cleaning and feature engineering
- label construction
- holdout backtests
- coefficient extraction and threshold scans
- latest-year scoring
- benchmark card construction
- scenario simulation
- table and chart generation
- most Markdown summary generation directly from script

### Likely manual or semi-manual follow-on work

- `presentation_outline.md`
- `fairlight_package/final_presentation_prompt_for_chatgpt.md`

Those two files look like later-stage communication / presentation packaging artifacts rather than first-pass model outputs.

## Final project state

By the end of the work, this folder had progressed from one raw CSV to a complete solution stack:

- reproducible code
- validated distress backbone
- latest-year scoring
- peer benchmarking
- deterministic shock simulation
- segment summaries
- intervention shortlists
- final charts
- final deck instructions

In practical terms, the work was no longer "an experiment." It had already become a submission-ready analytics package.

## What should be submitted

The best submission set is not the raw repo dump. It should be the curated materials that communicate the result:

1. the final presentation prompt / deck brief
2. presentation evidence and chart specs
3. the key model-results summary
4. shortlist and segment summaries
5. threshold and backtest evidence tables
6. the five final charts
7. the two pipeline scripts for reproducibility

## What should not be submitted unless specifically requested

These files are useful internally but are probably too heavy or too raw for a normal submission package:

- `irs990_cohort_features.csv`
- `intermediate/latest_2023_scores_full.csv`
- `intermediate/modeling_panel_observed_pairs.csv`
- `fairlight_package/shock_simulation_results.csv`
- `fairlight_package/peer_benchmark_cards.csv`

Those are better treated as supporting evidence or backup data.

## Bottom line

The workspace shows a clear progression:

- build the distress backbone
- validate it
- translate it into business thresholds and narratives
- extend it into Fairlight benchmarking and scenario tools
- package it into charts, shortlists, and a final presentation brief

That is the full story of what happened here, based on the files that were produced.
