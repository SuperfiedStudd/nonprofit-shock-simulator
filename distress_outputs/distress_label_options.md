# Distress Label Options

## Operating Deficit Plus Erosion

- **Business meaning:** Next year the nonprofit runs a meaningful operating deficit while already sitting on a thin balance-sheet cushion.
- **Mathematical construction:** `1[next_operating_margin_clean <= -0.05 AND next_net_asset_ratio_clean <= 0.25]`
- **Pros:** Simple to explain in business language.; Targets organizations that are both losing money and thinly capitalized.; Avoids tagging one-off deficits at strongly capitalized organizations as distress.
- **Cons:** Can miss fast-onset distress where reserves were still healthy at year-end.; Sensitive to net-assets restrictions.
- **Expected noise / bias:** Can understate distress for asset-rich but illiquid organizations.
- **Appropriate use:** candidate_primary
- **Observed rate on core sample:** 3.9% overall; yearly range 2.9% to 4.6%

## Reserve Crunch

- **Business meaning:** Next year the organization finishes with effectively no meaningful reserve cushion or negative net assets.
- **Mathematical construction:** `1[(next_reserve_months_proxy < 1.0) OR (next_net_assets_eoy <= 0)]`
- **Pros:** Strong resilience framing.; Maps directly into intervention logic around runway.; Very easy to benchmark.
- **Cons:** Net assets are an imperfect liquidity proxy.; Some asset-light pass-through organizations can look weaker than they are.
- **Expected noise / bias:** Over-weights balance-sheet structure relative to abrupt income shocks.
- **Appropriate use:** screening_label
- **Observed rate on core sample:** 11.3% overall; yearly range 8.3% to 14.4%

## Multi-Signal Distress

- **Business meaning:** Next year the organization shows multiple independent signs of strain rather than a single bad metric.
- **Mathematical construction:** `1[(sum of next-year symptoms >= 2) OR ((next_net_assets_eoy <= 0) AND (next_operating_margin_clean < 0))]; symptoms are margin<=-5%, reserve<1.5 months, leverage>0.85, revenue growth<=-20%, asset growth<=-10%`
- **Pros:** Balances income statement, balance sheet, and funding shock evidence.; Reduces noise from any one accounting quirk.; Best match for judge-ready structural storytelling.
- **Cons:** Slightly more complex to explain than a one-ratio label.; Threshold choices require judgment.
- **Expected noise / bias:** Still depends on Form 990 balance-sheet proxies and may miss orderly wind-downs.
- **Appropriate use:** primary_label
- **Observed rate on core sample:** 20.8% overall; yearly range 19.3% to 22.7%

## Filing Disappearance / Cessation

- **Business meaning:** The organization stops appearing with an observed filing in the next cycle.
- **Mathematical construction:** `1[next_observed_flag != 1], restricted to years with reliable follow-up coverage`
- **Pros:** Useful auxiliary validation target for severe outcomes.; Connects naturally to continuity stories.
- **Cons:** Not all disappearances are financial distress.; Sensitive to filing lags and panel mechanics.
- **Expected noise / bias:** Should not be used as the primary label because reporting behavior contaminates the signal.
- **Appropriate use:** aux_validation
- **Observed rate on core sample:** 0.0% overall; yearly range 0.0% to 0.0%

## Recommended primary label

**Multi-Signal Distress** is the recommended primary target because it combines operating weakness, balance-sheet fragility, and funding shock evidence without collapsing the problem into one noisy accounting line.
