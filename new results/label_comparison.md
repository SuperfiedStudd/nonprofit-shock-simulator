# Label Comparison

## Candidates tested

| experiment_name               |   overall_rate |   year_rate_std |   roc_auc |   pr_auc |     brier |
|:------------------------------|---------------:|----------------:|----------:|---------:|----------:|
| current_static_label          |       0.208554 |      0.0172663  |  0.741845 | 0.509676 | 0.126234  |
| peer_relative_delta_label     |       0.108226 |      0.00302002 |  0.830512 | 0.509039 | 0.0690403 |
| peer_relative_composite_tight |       0.203377 |      0.0184051  |  0.807503 | 0.625265 | 0.105125  |
| peer_relative_composite       |       0.243301 |      0.0208627  |  0.809803 | 0.65814  | 0.12106   |

## Business meaning

- `current_static_label`: the original accepted rule. It is simple, but it relies on uniform raw thresholds and under-uses peer context.
- `peer_relative_delta_label`: clean deterioration logic with excellent year-rate stability, but too narrow for the hackathon story because it mostly tags only the sharpest collapses.
- `peer_relative_composite_tight`: technically strong and closer to the old prevalence, but the bottom-15% cutoff is harder to explain on stage.
- `peer_relative_composite`: next-year distress is flagged when at least two peer-relative weakness or deterioration symptoms show up, or when balance-sheet failure pairs with at least middling-to-weak peer margin. This gives us "bottom-quintile / top-quintile plus deterioration" language judges can follow.

## Holdout behavior

- Selected label 2022 holdout ROC-AUC: 0.810
- Selected label 2022 holdout PR-AUC: 0.658
- Selected label 2022 prevalence: 22.7%
- Selected label year-rate standard deviation: 0.021

## Final recommendation

- Keep `peer_relative_composite` as the retained distress label.
- Why: it balances business meaning, peer-relative deterioration, threshold usefulness, and holdout behavior better than the old static label.
- Caveat: it is modestly more complex than the original label, so the presentation should describe it as a "bottom-quintile peer weakness plus deterioration" target rather than reciting the full formula.
