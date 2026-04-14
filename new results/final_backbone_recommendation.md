# Final Backbone Recommendation

## Blunt answer

- Final technical backbone: upgraded logistic regression
- Final label: `peer_relative_composite`
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

- Shortlist rows regenerated: 30
- Top shock scenario: `expense_inflation_10` with average risk increase 0.0320
