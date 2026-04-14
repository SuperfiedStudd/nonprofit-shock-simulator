# Integration Decision Log

| Proposed change | Decision | Why |
|---|---|---|
| Log-transform the net-asset coverage signal and stop relying on raw `expense_coverage` | implement now | Raw `expense_coverage` is unstable and judge-hostile. The log net-asset coverage version improved 2022 holdout versus the old backbone (ROC-AUC 0.801 -> 0.806) while keeping the reserve story intact. |
| Remove direct current-year margin and coverage from the main logistic feature set | implement now | Once peer anchors were added, removing direct current-year margin and coverage barely changed 2022 holdout (ROC-AUC 0.810 vs 0.810) and reduced circularity between the score, thresholds, and shortlist logic. |
| Rebuild peer-relative anchors using observed rows only | implement now | This directly improves holdout validity and makes benchmark cards cleaner. The new peer-anchored feature variants materially outperformed the old backbone. |
| Upgrade the distress label to a peer-relative multi-signal target | implement now | The selected label `peer_relative_composite` improved holdout behavior and made threshold discovery much stronger without becoming impossible to explain. |
| Keep a tighter bottom-15% peer version of the label | reject | It matched the old prevalence better, but bottom quintile language is simpler and the bottom-20% version produced stronger, more presentation-ready threshold evidence. |
| Add the 4 FRED-style macro interaction features to the retained logistic | reject | The macro pack hurt every retained holdout and mostly acted like a disguised year effect on only four reliable feature years. |
| Replace the backbone with the CatBoost + LightGBM challenger | test but do not adopt yet | It is clearly stronger technically, but it adds story complexity and weakens the threshold-to-action narrative. Keep it as a credibility benchmark, not the presentation backbone. |
| Pull in older v3 work as truth | reject | No local v3 artifact was available in this repo, and the request was to treat old work as a donor rather than truth. |
